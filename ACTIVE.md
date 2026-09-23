# ragkit — ACTIVE current view (derived, never authoritative)

role: current view — stage, what happened, load index
authority: lowest — fix ACTIVE if it contradicts SPEC/PLAN
load: read whole

## 1. Status

- current_stage: **Stage 4 — codegen, ACTIVE 2026-09-23** (Stage 3 — eval
  harness COMPLETE 2026-09-19 `v0.3.0`; Stage 2 — agentic COMPLETE 2026-09-18
  `v0.2.0`; Stage 1 — core chain COMPLETE 2026-09-18 `v0.1.0` — each tagged
  and pushed, DocPilot pinned). Stage 4 = **final** extraction stage (§5).
- last_updated: 2026-09-23
- test baseline: combined 552 (pre-extraction); current split ragkit 410 +
  DocPilot 142 (unit tests relocated zero loss; live-PG integration tests run
  when the gitignored repo-root `.env` is present, else hermetic-skip:
  totals unchanged)
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
- 2026-09-18 S2-T1: docs — Stage 2 (agentic) task list written into ragkit
  PLAN §3 and DocPilot PLAN §8.7 (S2-T1..T5 + exit criteria); ACTIVE
  refreshed in both repos. Bundle: `agent/*` (except `code_route.py` →
  Stage 4) + `tools/*` + langgraph dep move; ragkit.config gains 10 keys
  (AGENT_*, GITHUB_*, RETRIEVAL_LANGUAGE); parity gate = hermetic harness +
  one live smoke (locked). Next: S2-T2 — mechanical move.
- 2026-09-18 S2-T2: mechanical move — `docpilot.agent` → `ragkit.agent`,
  `docpilot.tools` → `ragkit.tools` (prefix swap); `ragkit.config` extended
  with 10 keys; langgraph dep added; 6 hermetic agent/tool test files moved.
  `3ded3fb` — ragkit 299 passed/1 skipped, 290/10 hermetic.
- 2026-09-18 S2-T3: DocPilot dogfood — `src/docpilot/` + `tests/` imports
  rewired to `ragkit.agent.*` / `ragkit.tools.*`; moved modules + 6 test
  files deleted; DocPilot config re-exports the 10 keys; pin → `@3ded3fb`.
  DocPilot 252 + ragkit 300 = 552.
- 2026-09-18 S2-T4: agentic parity evidence — hermetic determinism harness
  (fakes, fixed queries: routing, judge-retry, fake-tool live path): full
  trace identical pre (`docpilot.agent` @ Stage-2 start `391ebc8`) vs post
  (`ragkit.agent`). 6/6 scenarios IDENTICAL + one live CLI smoke (`docpilot
  ask --strategy agentic`, exit 0). Evidence: `parity/s2_*`.
- 2026-09-18 S2-T5: exit sweep — READMEs honest, clean-venv install from git
  `@v0.2.0` (deps incl. langgraph 1.2.11 resolved; imports OK; `docpilot`
  not importable), tag `v0.2.0` (`500717d`), DocPilot pin → `@v0.2.0`,
  §3.3 / §8.7b all `[x]`, both repos pushed. **Stage 2 COMPLETE.**
- 2026-09-19 S3-T1: docs — Stage 3 (eval) scope + task list in ragkit PLAN
  §4 + DocPilot PLAN §8.8, Stage 4 (§5/§8.9) pre-planned in the same commit;
  ACTIVE refreshed both repos (`b8f35b5` / DocPilot `6122c8c`).
- 2026-09-19 S3-T2: mechanical move — `docpilot.eval` → `ragkit.eval`
  (`benchmark/triples/judge_ab/tool_necessity` + `__main__`/`__init__` + 3
  dataset JSONs); 3 hermetic eval test files moved; `code_benchmark.py` + its
  test stay DocPilot-side until Stage 4. `309037b` — ragkit 410.
- 2026-09-19 S3-T3: DocPilot dogfood — moved eval modules + 3 tests deleted;
  `python -m docpilot.eval` workflow → `python -m ragkit.eval` (code-benchmark
  dispatcher lazy-guarded "moves in Stage 4"); pin → `@309037b`; DocPilot 142
  + ragkit 410 = 552.
- 2026-09-19 S3-T4: eval parity evidence — hermetic report-JSON harness
  (stubbed retriever/generator/judge; fixed dataset rows): pre
  `docpilot.eval`@`6122c8c` vs post (`ragkit.eval`) — **IDENTICAL
  field-for-field** (judge_ab 24, tool_necessity 15, benchmark 30);
  + one live TPD-aware smoke (`python -m ragkit.eval judge-ab`, 48 live
  Groq calls, transcript `parity/s3_eval_smoke.txt`). Evidence:
  `parity/s3_eval_parity.py` + `compare_s3_eval.py` + report.
- 2026-09-19 S3-T5: exit sweep — READMEs honest (ragkit Stage 3 `v0.3.0`),
  clean-venv install from git `@v0.3.0` (deps unchanged vs `v0.2.0`;
  `docpilot` not importable), tag `v0.3.0` (`f03c2e7`), DocPilot pin →
  `@v0.3.0`, §4.3 / §8.8b all `[x]`, both repos pushed. **Stage 3 COMPLETE.**
- 2026-09-23 S4-T1: Stage 4 (codegen) kicked off — §5/§8.9 scope+tasks were
  pre-written (`b8f35b5`/`6122c8c`); this refresh: stage headers honest
  (Stage 4 ACTIVE), both ACTIVEs updated, and the Stage-4-start pre-side
  worktree created (`/tmp/opencode/s4_parity_pre` @ DocPilot `34dea0d`).
  Next: S4-T2 — mechanical move.
- Stage 4 (final, §5) moves `codegen/*`, `validation/*`,
  `agent/code_route.py`, `eval/code_benchmark.py` + `code_benchmark.json` →
  `ragkit.codegen` / `ragkit.validation` / `ragkit.agent.code_route` /
  `ragkit.eval` (activates the code-benchmark `__main__` lazy-guard); 3
  CODE_* config keys; 5 hermetic test files move. Gate: full parity harness
  + 1 live codegen smoke. After S4-T5: extraction complete.

## 3. Load index

| File | Section | Load when |
|---|---|---|
| SPEC.md | all | always (short, read whole) |
| PLAN.md | §2 Stage 1 | stage-1 work |
| PLAN.md | §3 Stage 2 | stage-2 work (agentic) |
| PLAN.md | §4 Stage 3 | stage-3 work (eval, done) |
| PLAN.md | §5 Stage 4 | stage-4 work (codegen, ACTIVE) |
| DocPilot PLAN §8 | 1231–1536 | always — source-of-truth extraction plan (Stages 1–4) |
| DocPilot PLAN §8.8 | 1440–1495 | stage-3 work (eval, done) |
| DocPilot PLAN §8.9 | 1496–1536 | stage-4 work (codegen, ACTIVE) |

## 4. Refresh rules

- After SPEC/PLAN edits → update §3 line ranges + `last_updated`.
- After stage/task/decision changes → update §1–§2 in the same commit.
- Contradicts SPEC/PLAN → fix this file, never the other way.