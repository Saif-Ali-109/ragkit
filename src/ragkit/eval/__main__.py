"""``python -m ragkit.eval`` — Phase 4 eval entry point.

Subcommands (SPEC §6.2 slices):
  - ``judge-ab``        (default) judge two-prompt A/B calibration
  - ``tool-necessity``  tri-class tool-trigger necessity measurement
  - ``benchmark``       §6.1 classic-vs-agentic comparison over the benchmark
  - ``code-benchmark``  Phase 6 code eval — moves into `ragkit.eval` in
                        Stage 4; dispatching it here raises a clear error
                        until then
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    args = list(argv) if argv is not None else sys.argv[1:]
    if args and args[0] == "tool-necessity":
        from ragkit.eval.tool_necessity import main as tool_necessity_main

        return tool_necessity_main(args[1:])
    if args and args[0] == "benchmark":
        from ragkit.eval.benchmark import main as benchmark_main

        return benchmark_main(args[1:])
    if args and args[0] == "code-benchmark":
        print(
            "ragkit.eval: `code-benchmark` moves to this package in Stage 4; "
            "it is not available yet. Nothing ran.",
            file=sys.stderr,
        )
        return 2
    from ragkit.eval.judge_ab import main as judge_ab_main

    return judge_ab_main(args)


if __name__ == "__main__":
    raise SystemExit(main())