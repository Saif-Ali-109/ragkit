"""Compare the pre/post hermetic agentic parity recordings (PLAN §8.7b S2-T4).

Loads ``s2_agentic_pre.json`` / ``s2_agentic_post.json`` (written by
``s2_agentic_parity.py --side pre|post``), diffs every normalized field per
scenario, and writes ``s2_agentic_parity_report.md``.  Exits 0 only when every
scenario is byte-identical in every compared field.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent

_FIELDS = (
    "answer",
    "direct",
    "refused",
    "max_retries",
    "sources",
    "trace",
    "retriever_calls",
    "judge_calls",
    "judge_tools_seen",
    "tool_calls",
)


def _flat_diff(pre_obj: dict, post_obj: dict, path: str = "") -> list[str]:
    diffs: list[str] = []
    if isinstance(pre_obj, dict) and isinstance(post_obj, dict):
        for key in sorted(set(pre_obj) | set(post_obj)):
            diffs += _flat_diff(pre_obj.get(key), post_obj.get(key), f"{path}.{key}")
    elif isinstance(pre_obj, list) and isinstance(post_obj, list):
        if len(pre_obj) != len(post_obj):
            diffs.append(f"{path}: list length {len(pre_obj)} != {len(post_obj)}")
        for i, (a, b) in enumerate(zip(pre_obj, post_obj)):
            diffs += _flat_diff(a, b, f"{path}[{i}]")
    elif pre_obj != post_obj:
        diffs.append(f"{path}: {pre_obj!r} != {post_obj!r}")
    return diffs


def main() -> int:
    pre = json.loads((_HERE / "s2_agentic_pre.json").read_text())
    post = json.loads((_HERE / "s2_agentic_post.json").read_text())

    pre_by_id = {s["id"]: s for s in pre["scenarios"]}
    post_by_id = {s["id"]: s for s in post["scenarios"]}

    all_diffs: dict[str, list[str]] = {}
    for sid in sorted(pre_by_id):
        if sid not in post_by_id:
            all_diffs[sid] = ["missing on post side"]
            continue
        diffs = []
        for f in _FIELDS:
            diffs += _flat_diff(pre_by_id[sid][f], post_by_id[sid][f], f)
        if diffs:
            all_diffs[sid] = diffs

    identical = not all_diffs
    lines = [
        "## S2-T4 agentic parity — hermetic, deterministic pre/post extraction",
        "",
        f"- pre  : docpilot `{pre['meta']['docpilot_sha']}` (`docpilot.agent`), "
        f"timestamp {pre['meta']['timestamp']}",
        f"- post : docpilot `{post['meta']['docpilot_sha']}` + ragkit `{post['meta']['ragkit_sha']}` "
        f"(`ragkit.agent`), timestamp {post['meta']['timestamp']}",
        f"- hermetic: {post['meta']['hermetic']} — canned retriever/generator/judge/tool injected; "
        "GITHUB_PAT zeroed; no network / DB / LLM",
        f"- scenarios: {len(pre_by_id)} (direct auto, direct forced, agentic sufficient, "
        "agentic forced-simple, agentic retry-reformulate, agentic needs-tool)",
        f"- compared fields: {', '.join(_FIELDS)} (trace latency excluded)",
        f"- verdict: **{'IDENTICAL' if identical else 'DIFFERENCES FOUND'}**",
        "",
    ]
    if identical:
        lines.append("Every scenario matches field-for-field on both sides.")
    else:
        for sid, diffs in sorted(all_diffs.items()):
            lines.append(f"### {sid} — {len(diffs)} difference(s)")
            for d in diffs:
                lines.append(f"- {d}")

    # Live CLI smoke evidence (post side only — recorded once at S2-T4).
    smoke = _HERE / "s2_cli_smoke.txt"
    if smoke.exists():
        lines += [
            "",
            "## Live CLI smoke (post-extraction, one invocation)",
            "",
            "```",
            smoke.read_text().strip(),
            "```",
        ]
    lines.append("")
    lines.append(f"_report generated {datetime.now(timezone.utc).isoformat()} by compare_s2_agentic.py_")
    (_HERE / "s2_agentic_parity_report.md").write_text("\n".join(lines) + "\n")

    print("\n".join(lines))
    print(f"\n-> report: {_HERE / 's2_agentic_parity_report.md'}")
    return 0 if identical else 1


if __name__ == "__main__":
    sys.exit(main())