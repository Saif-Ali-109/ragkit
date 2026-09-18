"""Hermetic agentic parity recorder (PLAN §8.7b S2-T4).

Runs the SAME deterministic, component-injected agentic scenarios against the
pre-extraction app layer (DocPilot ``docpilot.agent``) and the post-extraction
framework layer (``ragkit.agent``) and records normalized results as JSON.

    # pre  — docpilot.agent from the Stage-2-start worktree (PYTHONPATH shadows
    #        the editable install; the venv's ragkit core is used by both sides)
    PYTHONPATH=/tmp/opencode/s2_parity_pre/src <venv>/python s2_agentic_parity.py \
        --side pre --out parity/s2_agentic_pre.json --docpilot-repo /tmp/opencode/s2_parity_pre

    # post — ragkit.agent via DocPilot dogfooding (import docpilot registers
    #        the host wiring, so the direct fast path runs the app's ask())
    <venv>/python s2_agentic_parity.py --side post \
        --out parity/s2_agentic_post.json --docpilot-repo <DocPilot>

Hermetic: every scenario injects canned retriever / generator / judge / tool
and this module zeroes ``GITHUB_PAT`` before ANY ragkit/docpilot import, so
no process makes a network, DB or LLM call and no live env value can change
behaviour.  Scenarios cover the three loop branches (sufficient, retry via
reformulated query, needs-tool) plus the direct fast path under auto and
forced strategies.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Hermeticity FIRST — before any ragkit/docpilot import freezes config.
os.environ["GITHUB_PAT"] = ""

_HERE = Path(__file__).resolve().parent
_RAGKIT_REPO = _HERE.parents[0]

SIMPLE_Q = "How do I install FastAPI?"
GATE_Q = (
    "Combine path, query, and body parameters in one endpoint — what are the "
    "validation rules for each kind?"
)
RETRY_Q = "reformulated validation rules"


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
# Scenario seed data (fixed and identical for both sides)
# ---------------------------------------------------------------------------

SCENARIOS = [
    {
        "id": "direct_auto",
        "question": SIMPLE_Q,
        "strategy": "auto",
        "gen_response": "Run `pip install fastapi` [1].",
        "results": {
            SIMPLE_Q: [{"content": "Install FastAPI with pip.", "score": 0.9, "chunk_id": "d1"}]
        },
        "judge_verdicts": [],
        "tool_results": None,
        "expect_direct": True,
    },
    {
        "id": "direct_forced",
        "question": GATE_Q,
        "strategy": "direct",
        "gen_response": "Path, query and body parameters each validate separately [1].",
        "results": {
            GATE_Q: [
                {"content": "[1] Path, [2] query, [3] body validation rules.", "score": 0.91, "chunk_id": "c1"},
                {"content": "Validation rules differ per kind.", "score": 0.72, "chunk_id": "c2"},
            ]
        },
        "judge_verdicts": [],
        "tool_results": None,
        "expect_direct": True,
    },
    {
        "id": "agentic_sufficient",
        "question": GATE_Q,
        "strategy": "auto",
        "gen_response": "Each parameter kind has its own validation rules [1].",
        "results": {
            GATE_Q: [
                {"content": "[1] Path, [2] query, [3] body validation rules.", "score": 0.91, "chunk_id": "c1"},
                {"content": "Validation rules differ per kind.", "score": 0.72, "chunk_id": "c2"},
            ]
        },
        "judge_verdicts": [{"verdict": "sufficient", "reason": "evidence present"}],
        "tool_results": None,
        "expect_direct": False,
    },
    {
        "id": "agentic_forced_simple",
        "question": SIMPLE_Q,
        "strategy": "agentic",
        "gen_response": "Install via pip [1].",
        "results": {
            SIMPLE_Q: [{"content": "Install FastAPI with pip.", "score": 0.9, "chunk_id": "d1"}]
        },
        "judge_verdicts": [{"verdict": "sufficient", "reason": "simple answered"}],
        "tool_results": None,
        "expect_direct": False,
    },
    {
        "id": "agentic_retry",
        "question": GATE_Q,
        "strategy": "agentic",
        "gen_response": "Validation differs per parameter kind [1].",
        "results": {
            GATE_Q: [
                {"content": "[1] Path, [2] query, [3] body validation rules.", "score": 0.61, "chunk_id": "c1"},
            ],
            RETRY_Q: [
                {"content": "Each parameter kind has its own validation rules.", "score": 0.88, "chunk_id": "c3"},
            ],
        },
        "judge_verdicts": [
            {"verdict": "insufficient", "reason": "thin evidence", "reformulated_query": RETRY_Q},
            {"verdict": "sufficient", "reason": "better evidence"},
        ],
        "tool_results": None,
        "expect_direct": False,
    },
    {
        "id": "agentic_tool",
        "question": GATE_Q,
        "strategy": "agentic",
        "gen_response": "OAuth tokens expire — see the live issue [1].",
        "results": {
            GATE_Q: [
                {"content": "[1] Path, [2] query, [3] body validation rules.", "score": 0.61, "chunk_id": "c1"},
            ],
        },
        "judge_verdicts": [
            {
                "verdict": "insufficient",
                "reason": "needs live issue state",
                "needs_tool": True,
                "tool_request": {"name": "github.search_issues", "params": {"query": "oauth token expiration"}},
            }
        ],
        "tool_results": {"github.search_issues": {"ok": True, "summary": "1 matching issue(s)", "n": 1}},
        "expect_direct": False,
    },
]


def _run_side(side: str, docpilot_repo: str) -> dict:
    # Fakes come from ragkit.testing (the single canonical copy, venv 3ded3fb)
    # and are injected identically into both sides.
    from ragkit.agent.types import Judgment
    from ragkit.citations.engine import StandardCitationEngine
    from ragkit.testing import FakeGenerator, FakeRetriever, StubJudge, StubTool, github_issue_result, make_result

    if side == "pre":
        sys.stderr.write("pre side: importing docpilot.agent (worktree)\n")
        # The pre-extraction app layer — the worktree's own docpilot.
        from docpilot.agent.pipeline_agentic import agentic_ask
    else:
        sys.stderr.write("post side: importing docpilot (host wiring) + ragkit.agent\n")
        import docpilot  # noqa: F401  — registers host wiring (S2-T3)

        from ragkit.agent.pipeline_agentic import agentic_ask

    results: list[dict] = []
    for sc in SCENARIOS:
        results_by_query = {
            q: [make_result(content=r["content"], score=r["score"], chunk_id=r["chunk_id"]) for r in rs]
            for q, rs in sc["results"].items()
        }
        retriever = FakeRetriever(results_by_query)
        generator = FakeGenerator(sc["gen_response"])
        judge = StubJudge([Judgment(**v) for v in sc["judge_verdicts"]])
        tool = None
        if sc["tool_results"] is not None:
            tool_results = {
                name: github_issue_result() if data["ok"] else data for name, data in sc["tool_results"].items()
            }
            tool = StubTool(tool_results)

        res = agentic_ask(
            sc["question"],
            strategy=sc["strategy"],
            retriever=retriever,
            generator=generator,
            judge=judge,
            citation_engine=StandardCitationEngine(),
            tool=tool,
        )
        results.append(
            {
                "id": sc["id"],
                "answer": res.answer,
                "direct": res.direct,
                "refused": res.refused,
                "max_retries": res.max_retries,
                "sources": [dataclasses.asdict(s) for s in res.sources],
                "trace": [
                    {"step": t.step, "query": t.query, "decision": t.decision, "detail": t.detail}
                    for t in res.trace
                ],
                "retriever_calls": [list(c) for c in retriever.calls],
                "judge_calls": judge.calls,
                "judge_tools_seen": list(judge.tools_seen),
                "tool_calls": [{"name": c.name, "params": c.params} for c in (tool.calls if tool else [])],
            }
        )
    return {
        "meta": {
            "side": side,
            "docpilot_sha": _short_sha(docpilot_repo),
            "ragkit_sha": _short_sha(_RAGKIT_REPO),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hermetic": True,
            "scenario_count": len(SCENARIOS),
        },
        "scenarios": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--side", choices=("pre", "post"), required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--docpilot-repo", required=True)
    args = parser.parse_args()

    payload = _run_side(args.side, args.docpilot_repo)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    sys.stderr.write(
        f"wrote {args.out} — docpilot@{payload['meta']['docpilot_sha']} "
        f"ragkit@{payload['meta']['ragkit_sha']} ({len(payload['scenarios'])} scenarios)\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())