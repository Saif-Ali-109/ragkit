"""Compare the pre/post hermetic eval-parity recordings (PLAN §4 S3-T4 /
DocPilot §8.8 S3-T4).

Loads ``s3_eval_pre.json`` / ``s3_eval_post.json`` (written by
``s3_eval_parity.py --side pre|post``), diffs the three report JSON payloads
(judge_ab, tool_necessity, benchmark.classic|agentic|comparison) recursively
(field-for-field), and writes ``s3_eval_parity_report.md``.  Exits 0 only when
every compared value is byte-identical on both sides.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent

_SECTIONS = (
    "judge_ab",
    "tool_necessity",
    "benchmark",
)


def _flat_diff(pre_obj, post_obj, path: str = "") -> list[str]:
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
    pre = json.loads((_HERE / "s3_eval_pre.json").read_text())
    post = json.loads((_HERE / "s3_eval_post.json").read_text())

    all_diffs: dict[str, list[str]] = {}
    for section in _SECTIONS:
        if section not in pre or section not in post:
            all_diffs[section] = ["missing on one side"]
            continue
        diffs = _flat_diff(pre[section], post[section], section)
        if diffs:
            all_diffs[section] = diffs

    identical = not all_diffs
    lines = [
        "## S3-T4 eval parity — hermetic, deterministic pre/post eval reports",
        "",
        f"- pre  : docpilot `{pre['meta']['docpilot_sha']}` (`docpilot.eval` @ Stage-3 start), "
        f"timestamp {pre['meta']['timestamp']}",
        f"- post : docpilot `{post['meta']['docpilot_sha']}` + ragkit `{post['meta']['ragkit_sha']}` "
        f"(`ragkit.eval`), timestamp {post['meta']['timestamp']}",
        f"- hermetic: {post['meta']['hermetic']} — scripted judges + scripted benchmark runner; "
        "GITHUB_PAT zeroed; no network / DB / LLM",
        f"- datasets: {post['meta']['dataset_sizes']} "
        "(judge_triples / tool_necessity / benchmark — sha256-identical pre/post)",
        f"- normalized: {', '.join(post['meta']['normalized'])} "
        "(generated_at pinned; judge_ab dataset_path fixed label)",
        f"- compared sections: {', '.join(_SECTIONS)} "
        "(benchmark = classic + agentic reports + §6.1 comparison)",
        f"- verdict: **{'IDENTICAL' if identical else 'DIFFERENCES FOUND'}**",
        "",
    ]
    if identical:
        lines.append(
            "Every report JSON matches field-for-field on both sides "
            "(judge_ab A/B calibration, tool-necessity tri-class metrics, "
            "benchmark classic/agentic reports + comparison)."
        )
    else:
        for section, diffs in sorted(all_diffs.items()):
            lines.append(f"### {section} — {len(diffs)} difference(s)")
            for d in diffs:
                lines.append(f"- {d}")

    # Live eval smoke evidence (post side only — recorded once at S3-T4).
    smoke = _HERE / "s3_eval_smoke.txt"
    if smoke.exists():
        lines += [
            "",
            "## Live eval smoke (post-extraction, one invocation)",
            "",
            "```",
            smoke.read_text().strip(),
            "```",
        ]
    lines.append("")
    lines.append(f"_report generated {datetime.now(timezone.utc).isoformat()} by compare_s3_eval.py_")
    (_HERE / "s3_eval_parity_report.md").write_text("\n".join(lines) + "\n")

    print("\n".join(lines))
    print(f"\n-> report: {_HERE / 's3_eval_parity_report.md'}")
    return 0 if identical else 1


if __name__ == "__main__":
    sys.exit(main())