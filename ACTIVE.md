# ragkit — ACTIVE current view (derived, never authoritative)

role: current view — stage, what happened, load index
authority: lowest — fix ACTIVE if it contradicts SPEC/PLAN
load: read whole

## 1. Status

- current_stage: Stage 1 — core chain, ACTIVE (entered 2026-09-17)
- last_updated: 2026-09-17
- test baseline: none yet — the ragkit suite lands with S1-T5
- gate reference: DocPilot full suite 552 passing (pre-extraction)

## 2. What happened (work state)

- 2026-09-17: DocPilot Phase 7 signed off → this repo created (public).
  DocPilot PLAN §8 is the source-of-truth extraction plan.
- 2026-09-17 S1-T1: scaffolded (`src/ragkit/`, pyproject uv_build +
  CPU-torch index, README, .gitignore); `chore: scaffold ragkit` pushed to
  main; editable-installed into the DocPilot venv; `import ragkit` verified.
- 2026-09-17 S1-T1b: self-docs trio added (SPEC.md + PLAN.md + this file) +
  README pointer.
- 2026-09-17 S1-T2: moved the §2.1 core-chain modules into `src/ragkit/`
  (`docpilot.` → `ragkit.` mechanical prefix swap; `docpilot.config` and
  DocPilot app-glue docstring refs kept DocPilot-side) + the 11 unit-test
  files (+conftest) into `tests/`; reverse-swap diff proves byte-mechanical.
  Fixed stale venv `.pth` editable paths (→ current repo locations) so the
  DocPilot venv resolves both packages; moved suite green there (182 passed,
  1 skipped — model/PostgreSQL hermetic skips).
- Next: S1-T3 — DocPilot rewire to `ragkit` imports, delete moved modules
  from `src/docpilot/`, grep-verify zero moved-prefix imports left.

## 3. Load index

| File | Section | Load when |
|---|---|---|
| SPEC.md | all | always (short, read whole) |
| PLAN.md | §2 Stage 1 | stage-1 work |
| PLAN.md | §3–§5 | later stages |
| DocPilot PLAN §8 | 1231–1323 | always — source-of-truth extraction plan |

## 4. Refresh rules

- After SPEC/PLAN edits → update §3 line ranges + `last_updated`.
- After stage/task/decision changes → update §1–§2 in the same commit.
- Contradicts SPEC/PLAN → fix this file, never the other way.