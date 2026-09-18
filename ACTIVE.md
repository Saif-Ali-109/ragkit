# ragkit — ACTIVE current view (derived, never authoritative)

role: current view — stage, what happened, load index
authority: lowest — fix ACTIVE if it contradicts SPEC/PLAN
load: read whole

## 1. Status

- current_stage: Stage 1 — core chain, **COMPLETE** (2026-09-18, `v0.1.0`
  tagged + pushed); paused for review before Stage 2 (agentic)
- last_updated: 2026-09-18
- test baseline: combined 552 (pre-extraction); current split ragkit 191
  (190 passed, 1 skipped with a dev `.env`; 181 passed, 10 skipped hermetic)
  + DocPilot 361
- gate reference: combined DocPilot + ragkit suite ≥ 552 (locked 2026-09-18;
  unit tests live in ragkit only; the ragkit conftest optionally loads the
  repo-root `.env` — gitignored — so live-PG integration tests run when
  credentials are present, else hermetic-skip: totals unchanged)

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
- 2026-09-18 S1-T4: connection semantics ownership — added `ragkit/config.py`
  owning the framework keys the core chain reads (POSTGRES_*, EMBEDDING_MODEL,
  GROQ_API_KEY/MODEL/MAX_RETRIES, RERANKER_MODEL, RERANK_CANDIDATES,
  RETRIEVAL_TOP_K): env-read with safe defaults, no import hard-fail, so
  `import ragkit` works standalone. Core-chain modules switched from
  `from docpilot import config` → `from ragkit import config` (reverse
  dependency gone; grep-verified). DocPilot config re-exports the non-secret
  keys; `docpilot/__init__.py` loads `.env` before any ragkit.config read.
  Moved `db/maintenance.py` + its SQL/integration tests into `ragkit.db`;
  DocPilot's dedupe CLI uses `ragkit.db.maintenance` (dry-run wiring tests
  stay DocPilot-side). Combined gate green: ragkit 191 (181 passed, 10
  skipped) + DocPilot 361 = 552. Hermeticity restored: ragkit's live-PG
  integration tests skip under a bare environment (were passing only by
  borrowing DocPilot's `.env` via the old reverse import).
- 2026-09-18 S1-T5/T6/T7: Stage-1 verification passes — standalone hermetic
  suite green (181 passed, 10 availability skips); combined 552 re-verified
  at the committed state (ragkit 191 + DocPilot 361); retrieval parity
  evidence — live same-process run, pre-extraction monolith
  `docpilot@69f91dc` (git worktree) vs post `docpilot@ebbdefa` +
  `ragkit@34686e2` against the same live PG corpus (15,319 chunks, BGE-small,
  top_k=5, language=en, levers off): 30 benchmark queries → **30/30 top-k
  IDENTICAL**; CLI/API smoke exit 0 with cited answer. Harness + evidence in
  `parity/`.
- 2026-09-18 S1-T8: exit sweep — READMEs honest (both repos), clean-venv
  install from git `@v0.1.0` verified (deps-free venv: `import ragkit` +
  `ragkit.config` safe defaults), `v0.1.0` annotated tag pushed on ragkit,
  DocPilot pyproject pin → `@v0.1.0`, §8.5 all `[x]`, no secrets, both repos
  pushed. **Stage 1 COMPLETE — paused for review before Stage 2 (agentic).**
- 2026-09-18 post-close follow-up (independent Stage-1 audit): verdict
  merge-ready — no blockers, no major code findings. Applied fixes: DocPilot
  PLAN §8.3 S1-T5/T6/T7 checkboxes (were stale `[ ]`); ragkit skip-string
  + load-index nits. ragkit test conftest now optionally loads the
  repo-root `.env` (gitignored) so the 9 live-PG integration tests run on
  dev machines with credentials — suite 190 passed, 1 skipped there;
  hermetic baseline (no `.env`) 181 passed, 10 skipped; totals identical.

## 3. Load index

| File | Section | Load when |
|---|---|---|
| SPEC.md | all | always (short, read whole) |
| PLAN.md | §2 Stage 1 | stage-1 work |
| PLAN.md | §3–§5 | later stages |
| DocPilot PLAN §8 | 1231–1364 | always — source-of-truth extraction plan |

## 4. Refresh rules

- After SPEC/PLAN edits → update §3 line ranges + `last_updated`.
- After stage/task/decision changes → update §1–§2 in the same commit.
- Contradicts SPEC/PLAN → fix this file, never the other way.