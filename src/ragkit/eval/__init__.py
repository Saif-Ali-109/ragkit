"""Evaluation tooling (SPEC §6; Phase 6 code benchmark SPEC §8).

Judge two-prompt A/B calibration is the first slice (SPEC §6.2).  The
labeled datasets live under ``src/ragkit/eval/dataset/`` — the root
``data/`` directory is git-ignored, but SPEC §6.4 requires the benchmark
dataset to be *committed*, so it ships inside the package.  Stage 4 added
the code benchmark (``code_benchmark.py`` + its dataset) here alongside
``ragkit.validation``.
"""