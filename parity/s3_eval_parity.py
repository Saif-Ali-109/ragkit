"""Hermetic eval-parity recorder (PLAN §4 S3-T4 / DocPilot §8.8 S3-T4).

Drives the SAME deterministic, component-injected eval pipeline against the
pre-move eval package (DocPilot ``docpilot.eval`` @ Stage-3-start worktree)
and the post-move framework package (``ragkit.eval``) and records the three
report JSON payloads:

  - judge_ab      — ``evaluate_prompt`` A/B → ``build_ab_report`` → ``ab_report_to_dict``
  - tool_necessity — ``evaluate_tool_necessity`` → ``report_to_dict``
  - benchmark     — ``run_pipeline`` classic + agentic → ``build_comparison``
                    → ``report_to_dict`` × 2 + ``comparison_to_dict``

    # pre  — docpilot.eval from the Stage-3-start worktree (PYTHONPATH shadows
    #        the editable install; the venv's ragkit core is used by both
    #        sides; env vars come from --env-file so docpilot.config can import)
    PYTHONPATH=/tmp/opencode/s3_parity_pre/src <venv>/python s3_eval_parity.py \
        --side pre --out parity/s3_eval_pre.json \
        --docpilot-repo /tmp/opencode/s3_parity_pre \
        --env-file /home/ain/Desktop/framework/DocPilot/.env

    # post — ragkit.eval standalone (ragkit.config has safe defaults)
    <venv>/python s3_eval_parity.py --side post \
        --out parity/s3_eval_post.json --docpilot-repo <DocPilot>

Hermetic: every report is computed over the committed, byte-identical dataset
files (sha256-verified) with scripted judges and a scripted benchmark runner
injected — no network / DB / LLM call happens on either side, and this module
zeroes ``GITHUB_PAT`` before ANY docpilot/ragkit import.

Determinism: ``time.strftime`` is the only wall-clock source in the report
builders (``generated_at``).  ``run_pipeline`` accepts ``generated_at``
explicitly; for ``build_ab_report`` / ``evaluate_tool_necessity`` the harness
pins ``generated_at`` on the returned report object before serialization.
``dataset_path`` is normalised to a fixed label for judge_ab (the pre/post
repositories live at different absolute paths; contents are sha-identical).
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Hermeticity FIRST — before any docpilot/ragkit import freezes config.
os.environ["GITHUB_PAT"] = ""

_HERE = Path(__file__).resolve().parent
_RAGKIT_REPO = _HERE.parents[0]

FIXED_GENERATED_AT = "2026-09-19T00:00:00"  # pinned for report parity
_DATASET_LABEL = "dataset/judge_triples.json"  # normalised path label


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
# Scripted judge (same construction rule on both sides; verdicts derive from
# the fixed triple contents, so pre and post compute identical queues).
# ---------------------------------------------------------------------------


def _judgments_for_judge_ab(triples) -> list:
    """Verdict queue: predict the gold, flipping every 5th triple so the
    per-category / confusion paths are exercised deterministically."""
    from ragkit.agent.types import Judgment

    out: list = []
    for i, t in enumerate(triples):
        verdict = t.gold
        if i % 5 == 0:  # deliberate misprediction (both sides agree)
            verdict = "insufficient" if t.gold == "sufficient" else "sufficient"
        out.append(Judgment(verdict=verdict, reason=f"parity-judge {i}"))
    return out


def _judgments_for_tool_necessity(triples) -> list:
    """Verdict + needs_tool + tool_request queue derived from the triples."""
    from ragkit.agent.types import Judgment

    out: list = []
    for i, t in enumerate(triples):
        verdict = t.gold_verdict
        if i % 5 == 0:
            verdict = "insufficient" if t.gold_verdict == "sufficient" else "sufficient"
        needs_tool = t.gold_needs_tool
        if i % 7 == 0:  # flip FP/FN coverage deterministically
            needs_tool = not needs_tool
        tool_request = None
        if needs_tool:
            tool_request = {
                "name": t.gold_tool_action or "github.search_issues",
                "params": {"query": t.question.lower().replace(" ", "-")[:40]},
            }
        out.append(
            Judgment(verdict=verdict, reason=f"parity-tn {i}", needs_tool=needs_tool, tool_request=tool_request)
        )
    return out


# ---------------------------------------------------------------------------
# Scripted benchmark runner (same rule on both sides; runs from the side's
# own RunOutput/LoopTraceStep dataclasses, which are byte-identical).
# ---------------------------------------------------------------------------


def _make_runner(mod, bench: list, *, agentic: bool):
    """Build ``run(question) -> mod.RunOutput`` keyed by the fixed benchmark.

    classic   — one search step (retrieval_calls == 1), never calls a tool;
                live-state answers stay at the 0.5 partial-correct score.
    agentic   — adds a ``tool_call`` trace step for live-state rows, so those
                score 1.0 and avg_tool_calls differs — exercises the
                comparison builder on both sides identically.
    """
    from ragkit.agent.types import LoopTraceStep

    RunOutput = mod.RunOutput

    def _output(q, i: int) -> dataclasses.dataclass:
        if q.category == "neither":
            answer = "I don't know."
            refused = True
        else:
            facts = " ".join(q.gold_key_facts) if q.gold_key_facts else "Answer text."
            answer = facts + (" [1]" if q.gold_sources else "")
            refused = False
        trace = [LoopTraceStep.new("search", q.question, "direct", detail="parity")]
        if agentic and q.category == "live-state-answerable":
            trace.append(
                LoopTraceStep.new(
                    "tool_call", q.question, "github.search_issues", detail="parity"
                )
            )
        return RunOutput(
            answer=answer,
            source_files=list(q.gold_sources),
            refused=refused,
            trace_steps=trace,
            latency_ms=100.0 + i,
        )

    by_question = {q.question: _output(q, i) for i, q in enumerate(bench)}

    def run(question: str):
        if question not in by_question:
            raise KeyError(f"scripted runner: unknown question {question!r}")
        return by_question[question]

    return run


# ---------------------------------------------------------------------------
# Side driver
# ---------------------------------------------------------------------------


def _load_side_module(side: str):
    """Return the eval submodule bundle for the requested side."""
    if side == "pre":
        sys.stderr.write("pre side: importing docpilot.eval (Stage-3-start worktree)\n")
        from docpilot.eval import benchmark, judge_ab, tool_necessity
        from docpilot.eval.triples import load_judge_triples
    else:
        sys.stderr.write("post side: importing ragkit.eval (standalone)\n")
        from ragkit.eval import benchmark, judge_ab, tool_necessity
        from ragkit.eval.triples import load_judge_triples

    from ragkit.testing import StubJudge

    return {
        "benchmark": benchmark,
        "judge_ab": judge_ab,
        "tool_necessity": tool_necessity,
        "load_judge_triples": load_judge_triples,
        "StubJudge": StubJudge,
        "dataset_dir": Path(judge_ab.__file__).resolve().parent / "dataset",
    }


def _run_side(side: str, docpilot_repo: str) -> dict:
    mod = _load_side_module(side)
    ds = mod["dataset_dir"]
    StubJudge = mod["StubJudge"]

    # --- judge_ab ---------------------------------------------------------
    judge_triples_path = ds / "judge_triples.json"
    judge_triples = mod["load_judge_triples"](judge_triples_path)

    judge_a = StubJudge(_judgments_for_judge_ab(judge_triples))
    report_a = mod["judge_ab"].evaluate_prompt(
        judge_triples, judge_a, prompt_name="A"
    )
    judge_b = StubJudge(_judgments_for_judge_ab(judge_triples))
    report_b = mod["judge_ab"].evaluate_prompt(
        judge_triples, judge_b, prompt_name="B"
    )
    ab = mod["judge_ab"].build_ab_report(_DATASET_LABEL, report_a, report_b)
    ab.generated_at = FIXED_GENERATED_AT
    judge_ab_payload = mod["judge_ab"].ab_report_to_dict(ab)

    # --- tool_necessity ---------------------------------------------------
    tn_path = ds / "tool_necessity.json"
    tn_triples = mod["tool_necessity"].load_tool_necessity_triples(tn_path)
    tn_judge = StubJudge(_judgments_for_tool_necessity(tn_triples))
    tn_report = mod["tool_necessity"].evaluate_tool_necessity(tn_triples, tn_judge)
    tn_report.generated_at = FIXED_GENERATED_AT
    tn_payload = mod["tool_necessity"].report_to_dict(tn_report)

    # --- benchmark --------------------------------------------------------
    bench_path = ds / "benchmark.json"
    bench = mod["benchmark"].load_benchmark(bench_path)
    checker = lambda answer, source_files: True  # deterministic grounding stub

    classic = mod["benchmark"].run_pipeline(
        bench,
        "classic",
        _make_runner(mod["benchmark"], bench, agentic=False),
        grounding_checker=checker,
        generated_at=FIXED_GENERATED_AT,
    )
    agentic = mod["benchmark"].run_pipeline(
        bench,
        "agentic",
        _make_runner(mod["benchmark"], bench, agentic=True),
        grounding_checker=checker,
        generated_at=FIXED_GENERATED_AT,
    )
    comparison = mod["benchmark"].build_comparison(classic, agentic)

    return {
        "meta": {
            "side": side,
            "docpilot_sha": _short_sha(docpilot_repo),
            "ragkit_sha": _short_sha(_RAGKIT_REPO),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hermetic": True,
            "normalized": ["generated_at", "dataset_path"],
            "dataset_sizes": {
                "judge_triples": len(judge_triples),
                "tool_necessity": len(tn_triples),
                "benchmark": len(bench),
            },
        },
        "judge_ab": judge_ab_payload,
        "tool_necessity": tn_payload,
        "benchmark": {
            "classic": mod["benchmark"].report_to_dict(classic),
            "agentic": mod["benchmark"].report_to_dict(agentic),
            "comparison": mod["benchmark"].comparison_to_dict(comparison),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--side", choices=("pre", "post"), required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--docpilot-repo", required=True)
    parser.add_argument("--env-file", type=Path, default=None, help=".env to load before imports (needed for pre side)")
    args = parser.parse_args()

    if args.env_file is not None:
        from dotenv import load_dotenv

        load_dotenv(args.env_file)

    payload = _run_side(args.side, args.docpilot_repo)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    sys.stderr.write(
        f"wrote {args.out} — docpilot@{payload['meta']['docpilot_sha']} "
        f"ragkit@{payload['meta']['ragkit_sha']} "
        f"datasets={payload['meta']['dataset_sizes']}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())