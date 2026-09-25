"""Hermetic codegen-parity recorder (PLAN §5 S4-T4 / DocPilot §8.9 S4-T4).

Drives the SAME deterministic, component-injected codegen stack against the
pre-move codegen bundle (DocPilot ``docpilot.codegen`` / ``docpilot.validation``
/ ``docpilot.agent.code_route`` / ``docpilot.eval.code_benchmark`` @ the
Stage-4-start worktree) and the post-move framework package (``ragkit.*``)
and records four payload sections:

  - codegen        — ``ask_code`` over the committed fixture corpus with a
                     scripted retriever + scripted generator
  - validation     — ``RetrieveThenValidate`` verdicts over the fixture
                     corpus (parse / imports / symbols paths + empty-evidence
                     SKIP path)
  - code_route     — ``run_code_route``: standard-ask fallback, validated
                     code path, and the T4 loop that refuses unvalidatable
                     code after the reformulation budget
  - code_benchmark — ``run_code_benchmark`` with a scripted runner over the
                     committed ``code_benchmark.json`` dataset

    # pre  — docpilot.* from the Stage-4-start worktree (PYTHONPATH shadows
    #        the editable install; the venv's ragkit core is used by both
    #        sides; env vars come from --env-file so docpilot.config can import)
    PYTHONPATH=/tmp/opencode/s4_parity_pre/src <venv>/python s4_codegen_parity.py \
        --side pre --out parity/s4_codegen_pre.json \
        --docpilot-repo /tmp/opencode/s4_parity_pre \
        --env-file /home/ain/Desktop/framework/DocPilot/.env

    # post — ragkit.* standalone (ragkit.config has safe defaults)
    <venv>/python s4_codegen_parity.py --side post \
        --out parity/s4_codegen_post.json --docpilot-repo <DocPilot>

Hermetic: every payload is computed over committed, byte-identical fixture /
dataset files with scripted retriever, generator and code-benchmark runner —
no network / DB / LLM call happens on either side, and this module zeroes
``GITHUB_PAT`` before ANY docpilot/ragkit import.

Determinism: ``time.perf_counter`` latencies inside ``ask_code`` /
``run_code_route`` are wall-clock by design, so the harness normalises both
latency fields to 0.0 before serialising; ``run_code_benchmark`` accepts
``generated_at`` explicitly and the scripted runner pins its own latencies.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Hermeticity FIRST — before any docpilot/ragkit import freezes config.
os.environ["GITHUB_PAT"] = ""

_HERE = Path(__file__).resolve().parent
_RAGKIT_REPO = _HERE.parents[0]

FIXED_GENERATED_AT = "2026-09-23T00:00:00"  # pinned for report parity
_DATASET_SHA = "ecc1975a1914c27ab6f7f1ce394f86b81e580b379af2b6fc7024760a649373dc"

_FIXTURES = _RAGKIT_REPO / "tests" / "fixtures" / "codegen" / "fastapi_basic"
_REFUSAL_SENTENCE = (
    "I don't know — the available documentation does not cover this question."
)
_FALLBACK_QA = ("What are the validation rules for FastAPI path parameters?",)
_CODE_QA = "Write a minimal FastAPI application with a GET endpoint."


def _short_sha(cwd: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=cwd,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:  # pragma: no cover
        return "unknown"


# ---------------------------------------------------------------------------
# Scripted components (same construction rule on both sides — byte-identical).
# ---------------------------------------------------------------------------


class _FakeRetriever:
    """Returns the fixed fixture corpus as retrieval results."""

    def __init__(self, results: list) -> None:
        self.results = results
        self.calls: list[tuple] = []

    def retrieve(self, question: str, *, top_k: int, language: str | None):
        self.calls.append((question, top_k, language))
        return self.results


class _FakeGenerator:
    """Understands both the answer path (generate_answer) and code path
    (generate) — mirrors the app-level fake used by the moved hermetic tests."""

    def __init__(self, answer_text="", code_text=""):
        self.answer_text = answer_text
        self.code_text = code_text
        self.answer_calls = 0
        self.code_calls = 0

    def generate_answer(self, context_text, sources_text, question):
        self.answer_calls += 1
        return self.answer_text

    def generate(self, prompt):
        self.code_calls += 1
        return self.code_text


def _chunk(content: str, file: str, heading: str, cid: str):
    from ragkit.core.models import Chunk, RetrieverResult

    return RetrieverResult(
        chunk=Chunk(id=cid, content=content, heading_path=heading, source_file=file),
        score=0.9,
    )


def _fixture_results() -> list:
    """api_spec.md + valid_example.py as the retrieved evidence corpus."""
    spec = (_FIXTURES / "api_spec.md").read_text(encoding="utf-8")
    valid = (_FIXTURES / "valid_example.py").read_text(encoding="utf-8")
    return [
        _chunk(spec, "en/docs/tutorial/first-steps.md", "First Steps", "c1"),
        _chunk(valid, "en/docs/tutorial/first-steps.md", "First Steps", "c2"),
    ]


VALID_CODE = """\
Here is a minimal FastAPI app from the tutorial [1]:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

Serve it locally with uvicorn [2]:

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
"""

INVALID_CODE = """\
Here is the app [1]:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "hello"
```
"""


# ---------------------------------------------------------------------------
# Scripted code-benchmark runner (same rule on both sides; exercises the
# scoring paths — PASS rows, an imports-FAIL row, and the refusal row).
# ---------------------------------------------------------------------------


def _make_code_runner(mod, questions: list, verdict_cls, check_cls, status_cls):
    """Build ``run(request) -> mod.CodeRunOutput`` keyed by the dataset.

    PASS verdicts carry the exact check names the scorer reads
    (``parse`` / ``imports_evidence`` / ``symbols_evidence``); every 3rd
    answerable row gets an imports FAIL so both pass and fail metrics are
    exercised; the ``refusal_expected`` row refuses with no code.
    """
    RunOutput = mod.CodeRunOutput

    def _pass_verdict() -> verdict_cls:
        return verdict_cls(
            passed=True,
            checks=(
                check_cls("parse", status_cls.PASS, "parses cleanly"),
                check_cls(
                    "imports_evidence", status_cls.PASS, "all imports grounded"
                ),
                check_cls(
                    "symbols_evidence", status_cls.PASS, "all symbols grounded"
                ),
            ),
        )

    def _fail_imports_verdict() -> verdict_cls:
        return verdict_cls(
            passed=False,
            checks=(
                check_cls("parse", status_cls.PASS, "parses cleanly"),
                check_cls(
                    "imports_evidence",
                    status_cls.FAIL,
                    "import 'flask' not found in the retrieved documentation",
                ),
                check_cls(
                    "symbols_evidence", status_cls.SKIP, "skipped on FAIL"
                ),
            ),
        )

    out_by_request: dict[str, mod.CodeRunOutput] = {}
    for i, q in enumerate(questions):
        if q.refusal_expected:
            out_by_request[q.request] = RunOutput(
                question=q.request,
                answer=_REFUSAL_SENTENCE,
                source_files=[],
                code_blocks=[],
                block_verdicts=[],
                verdict=None,
                validation_failed=False,
                refused=True,
                validation_turns=1,
                latency_ms=50.0 + i,
            )
            continue
        imports = ", ".join(q.gold_imports) if q.gold_imports else "fastapi"
        code = f"import {imports}\n\napp = None\n"
        checks_fail = i % 3 == 0
        verdict = _fail_imports_verdict() if checks_fail else _pass_verdict()
        marker = "[1]" if q.gold_sources else ""
        out_by_request[q.request] = RunOutput(
            question=q.request,
            answer=f"Here is the code {marker}:\n\n```python\n{code}\n```",
            source_files=list(q.gold_sources),
            code_blocks=[code],
            block_verdicts=[verdict],
            verdict=verdict,
            validation_failed=checks_fail,
            refused=False,
            validation_turns=1 if not checks_fail else 2,
            latency_ms=100.0 + i,
        )

    def run(request: str):
        if request not in out_by_request:
            raise KeyError(f"scripted code runner: unknown request {request!r}")
        return out_by_request[request]

    return run


# ---------------------------------------------------------------------------
# Serialization (latency fields normalised — see module docstring)
# ---------------------------------------------------------------------------


def _verdict_dict(v) -> dict | None:
    if v is None:
        return None
    return {
        "passed": v.passed,
        "checks": [[c.name, c.status.value, c.detail] for c in v.checks],
    }


def _request_dict(r) -> dict:
    return {
        "question": r.question,
        "raw_response": r.raw_response,
        "code_blocks": list(r.code_blocks),
        "answer": r.answer,
        "footer": r.footer,
        "sources": [
            {
                "ref": s.ref,
                "file": s.file,
                "heading": s.heading,
                "kind": s.kind,
            }
            for s in r.sources
        ],
        "results": [
            {
                "id": res.chunk.id,
                "score": round(res.score, 6),
                "file": res.chunk.source_file,
                "heading": res.chunk.heading_path,
            }
            for res in r.results
        ],
        "raw_prompt": r.raw_prompt,
        "retrieval_latency_ms": 0.0,
        "latency_ms": 0.0,
        "refused": r.refused,
        "verdict": _verdict_dict(r.verdict),
        "block_verdicts": [_verdict_dict(v) for v in r.block_verdicts],
        "validation_failed": r.validation_failed,
        "validation_reasons": list(r.validation_reasons),
        "generation_attempts": r.generation_attempts,
    }


def _route_dict(res) -> dict:
    return {
        "decision": {"code": res.decision.code, "reason": res.decision.reason},
        "answer": res.answer,
        "ask": (
            {
                "display": res.ask.display,
                "sources": [
                    {
                        "ref": s.ref,
                        "file": s.file,
                        "heading": s.heading,
                        "kind": s.kind,
                    }
                    for s in res.ask.sources
                ],
            }
            if res.ask is not None
            else None
        ),
        "code": _request_dict(res.code) if res.code is not None else None,
    }


# ---------------------------------------------------------------------------
# Side driver
# ---------------------------------------------------------------------------


def _load_side_module(side: str) -> dict:
    """Return the codegen submodule bundle for the requested side."""
    if side == "pre":
        sys.stderr.write("pre side: importing docpilot codegen stack (Stage-4-start worktree)\n")
        from docpilot.agent.code_route import run_code_route
        from docpilot.codegen import ask_code
        from docpilot.eval import code_benchmark
        from docpilot.validation import (
            CheckStatus,
            RetrieveThenValidate,
            ValidationCheck,
            ValidationVerdict,
            combine_verdicts,
        )
    else:
        sys.stderr.write("post side: importing ragkit codegen stack (standalone)\n")
        from ragkit.agent.code_route import run_code_route
        from ragkit.codegen import ask_code
        from ragkit.eval import code_benchmark
        from ragkit.validation import (
            CheckStatus,
            RetrieveThenValidate,
            ValidationCheck,
            ValidationVerdict,
            combine_verdicts,
        )

    ds = Path(code_benchmark.__file__).resolve().parent / "dataset"
    return {
        "ask_code": ask_code,
        "run_code_route": run_code_route,
        "code_benchmark": code_benchmark,
        "RetrieveThenValidate": RetrieveThenValidate,
        "CheckStatus": CheckStatus,
        "ValidationCheck": ValidationCheck,
        "ValidationVerdict": ValidationVerdict,
        "combine_verdicts": combine_verdicts,
        "dataset_dir": ds,
    }


def _run_side(side: str, docpilot_repo: str) -> dict:
    mod = _load_side_module(side)
    cb = mod["code_benchmark"]

    # --- codegen (ask_code) -------------------------------------------------
    generator = _FakeGenerator(code_text=VALID_CODE)
    retriever = _FakeRetriever(_fixture_results())
    req = mod["ask_code"](
        _CODE_QA,
        retriever=retriever,
        generator=generator,
        top_k=5,
        language="en",
    )
    codegen_valid = _request_dict(req)

    # codegen — uncovered request ⇒ SPEC §3.9 refusal, no code.
    refusal_retriever = _FakeRetriever([])
    refusal_generator = _FakeGenerator(code_text=_REFUSAL_SENTENCE)
    req_refused = mod["ask_code"](
        "Write code for a Django model.",
        retriever=refusal_retriever,
        generator=refusal_generator,
        top_k=5,
        language="en",
    )
    codegen_refused = _request_dict(req_refused)

    # --- validation (RetrieveThenValidate over the fixture corpus) ----------
    spec = (_FIXTURES / "api_spec.md").read_text(encoding="utf-8")
    evidence = [spec]
    validator = mod["RetrieveThenValidate"]()
    verdicts = {}
    for name in (
        "valid_example",
        "invalid_syntax",
        "invalid_unknown_import",
        "invalid_undefined_symbol",
    ):
        text = (_FIXTURES / f"{name}.py").read_text(encoding="utf-8")
        verdicts[name] = _verdict_dict(validator.validate(text, evidence))
    # empty evidence ⇒ SKIP path (no evidence to ground against)
    verdicts["valid_example_no_evidence"] = _verdict_dict(
        validator.validate((_FIXTURES / "valid_example.py").read_text(), [])
    )

    # --- code_route ---------------------------------------------------------
    from ragkit.citations.engine import StandardCitationEngine

    cit = StandardCitationEngine()

    # fallback: standard ask path, byte-identical to a plain ask() call.
    fallback_gen = _FakeGenerator(answer_text="FastAPI validates path parameters by type.")
    fallback_ret = _FakeRetriever(_fixture_results())
    fb = mod["run_code_route"](
        _FALLBACK_QA[0],
        enabled=False,
        retriever=fallback_ret,
        generator=fallback_gen,
        citation_engine=cit,
        top_k=5,
        language="en",
    )
    route_fallback = _route_dict(fb)
    route_fallback["retriever_calls"] = list(fallback_ret.calls)
    route_fallback["generator_answer_calls"] = fallback_gen.answer_calls

    # validated code path: explicit opt-in; generated code must validate.
    valid_gen = _FakeGenerator(code_text=VALID_CODE)
    valid_ret = _FakeRetriever(_fixture_results())
    ok = mod["run_code_route"](
        _CODE_QA,
        explicit_code=True,
        retriever=valid_ret,
        generator=valid_gen,
        citation_engine=cit,
        max_validation_turns=2,
        top_k=5,
        language="en",
    )
    route_validated = _route_dict(ok)

    # T4 loop exhaustion: code never validates → refuse after budget.
    bad_gen = _FakeGenerator(code_text=INVALID_CODE)
    bad_ret = _FakeRetriever(_fixture_results())
    refused = mod["run_code_route"](
        _CODE_QA,
        explicit_code=True,
        retriever=bad_ret,
        generator=bad_gen,
        citation_engine=cit,
        max_validation_turns=2,
        top_k=5,
        language="en",
    )
    route_refused = _route_dict(refused)

    # --- code_benchmark -----------------------------------------------------
    questions = cb.load_code_benchmark(mod["dataset_dir"] / "code_benchmark.json")
    runner = _make_code_runner(
        cb,
        questions,
        mod["ValidationVerdict"],
        mod["ValidationCheck"],
        mod["CheckStatus"],
    )
    report = cb.run_code_benchmark(
        questions, runner, generated_at=FIXED_GENERATED_AT
    )
    bench_payload = cb.report_to_dict(report)

    return {
        "meta": {
            "side": side,
            "docpilot_sha": _short_sha(docpilot_repo),
            "ragkit_sha": _short_sha(_RAGKIT_REPO),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hermetic": True,
            "normalized": [
                "latency_ms (ask_code/code_route set to 0.0)",
                "generated_at (code_benchmark pinned)",
            ],
            "dataset_sha": _DATASET_SHA,
            "code_benchmark_rows": len(questions),
        },
        "codegen": {"valid": codegen_valid, "refused": codegen_refused},
        "validation": verdicts,
        "code_route": {
            "fallback": route_fallback,
            "validated": route_validated,
            "refused": route_refused,
        },
        "code_benchmark": bench_payload,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--side", choices=("pre", "post"), required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--docpilot-repo", required=True)
    parser.add_argument(
        "--env-file", type=Path, default=None, help=".env to load before imports (needed for pre side)"
    )
    args = parser.parse_args()

    if args.env_file is not None:
        from dotenv import load_dotenv

        load_dotenv(args.env_file)

    payload = _run_side(args.side, args.docpilot_repo)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    sys.stderr.write(
        f"wrote {args.out} — docpilot@{payload['meta']['docpilot_sha']} "
        f"ragkit@{payload['meta']['ragkit_sha']} "
        f"code_benchmark_rows={payload['meta']['code_benchmark_rows']}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())