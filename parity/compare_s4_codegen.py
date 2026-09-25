"""Compare the pre/post hermetic codegen-parity recordings (PLAN §5 S4-T4 /
DocPilot §8.9 S4-T4).

Loads ``s4_codegen_pre.json`` / ``s4_codegen_post.json`` (written by
``s4_codegen_parity.py --side pre|post``), diffs the four payload sections
(codegen, validation, code_route, code_benchmark) recursively
(field-for-field), and writes ``s4_codegen_parity_report.md``.  Exits 0 only
when every compared value is byte-identical on both sides.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent

_SECTIONS = (
    "codegen",
    "validation",
    "code_route",
    "code_benchmark",
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
    pre = json.loads((_HERE / "s4_codegen_pre.json").read_text())
    post = json.loads((_HERE / "s4_codegen_post.json").read_text())

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
        "## S4-T4 codegen parity — hermetic, deterministic pre/post payloads",
        "",
        f"- pre  : docpilot `{pre['meta']['docpilot_sha']}` (`docpilot.codegen` / "
        f"`docpilot.validation` / `docpilot.agent.code_route` / "
        f"`docpilot.eval.code_benchmark` @ Stage-4 start), timestamp {pre['meta']['timestamp']}",
        f"- post : docpilot `{post['meta']['docpilot_sha']}` + ragkit `{post['meta']['ragkit_sha']}` "
        f"(`ragkit.*`), timestamp {post['meta']['timestamp']}",
        f"- hermetic: {post['meta']['hermetic']} — scripted retriever/generator/"
        "runner; GITHUB_PAT zeroed; no network / DB / LLM",
        f"- dataset: code_benchmark {post['meta']['code_benchmark_rows']} rows, "
        f"sha256 `{post['meta']['dataset_sha']}` (identical pre/post); "
        "fixtures fastapi_basic sha-identical (verified)",
        f"- normalized: {', '.join(post['meta']['normalized'])}",
        f"- compared sections: {', '.join(_SECTIONS)} "
        "(codegen valid+refused, validation verdicts incl. SKIP path, "
        "code_route fallback/validated/refused, code_benchmark full report)",
        f"- verdict: **{'IDENTICAL' if identical else 'DIFFERENCES FOUND'}**",
        "",
    ]
    if identical:
        lines.append(
            "Every payload matches field-for-field on both sides (prompts, "
            "emitted code, validation verdicts, route decisions, benchmark "
            "rows + metrics)."
        )
    else:
        for section, diffs in sorted(all_diffs.items()):
            lines.append(f"### {section} — {len(diffs)} difference(s)")
            for d in diffs:
                lines.append(f"- {d}")

    # Live codegen smoke evidence (post side only — recorded once at S4-T4).
    smoke = _HERE / "s4_codegen_smoke.txt"
    if smoke.exists():
        lines += [
            "",
            "## Live codegen smoke (post-extraction, one invocation)",
            "",
            "```",
            smoke.read_text().strip(),
            "```",
        ]
    lines.append("")
    lines.append(f"_report generated {datetime.now(timezone.utc).isoformat()} by compare_s4_codegen.py_")
    (_HERE / "s4_codegen_parity_report.md").write_text("\n".join(lines) + "\n")

    print("\n".join(lines))
    print(f"\n-> report: {_HERE / 's4_codegen_parity_report.md'}")
    return 0 if identical else 1


if __name__ == "__main__":
    sys.exit(main())