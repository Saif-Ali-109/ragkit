# ragkit — ACTIVE current view (derived, never authoritative)

role: current view — stage, what happened, load index
authority: lowest — fix ACTIVE if it contradicts SPEC/PLAN
load: read whole

## 1. Status

- current_stage: Stage 1 — core chain, ACTIVE (entered 2026-09-17)
- last_updated: 2026-09-18
- test baseline: ragkit 183 (182 passed, 1 skipped) + DocPilot 369 = 552
  combined (pre-extraction baseline)
- gate reference: combined DocPilot + ragkit suite ≥ 552 (locked 2026-09-18;
  unit tests live in ragkit only)

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
- 2026-09-18 S1-T3: DocPilot dogfood rewire — `src/docpilot/` + `tests/`
  imports switched to `ragkit.*`, the moved modules and their 11 unit-test
  files deleted (no duplication), pyproject pins ragkit `@ed0f908`. DocPilot
  suite green (369); ragkit 183 → combined 552. Gate interpretation locked
  (SPEC §4): combined count, unit tests in ragkit only.
- Next: S1-T4 — connection semantics (ragkit owns DSN→conn for PgVectorStore,
  DocPilot delegates; decide `db/maintenance.py` home).

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