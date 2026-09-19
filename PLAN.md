# ragkit — PLAN (working state, derived from SPEC.md)

role: the HOW — stages, tasks, exit checklists, execution order
authority: derived — SPEC.md wins on conflict

## 1. status

- origin: extracted from DocPilot (Phases 1–6 COMPLETE, 2026-09-12)
- current: **Stage 2 — agentic, COMPLETE 2026-09-18 (`v0.2.0`; both repos
  pushed). Next: Stage 3 — eval harness (planned §4), then Stage 4 — codegen
  (§5) — both start on user go.**
- source-of-truth extraction plan: DocPilot PLAN §8
  (<https://github.com/Saif-Ali-109/DocPilot/blob/main/PLAN.md>)

## 2. Stage 1 — core chain (COMPLETE 2026-09-18, v0.1.0)

### 2.1 scope (move set, from DocPilot `src/docpilot/`)

- `ingestion/{loader,parser,chunker,fastapi_loader}.py` → `ragkit.ingestion`
- `embeddings/provider.py` → `ragkit.embeddings`
- `retrieval/{vector_store,lexical,retriever,hybrid}.py` → `ragkit.retrieval`
- `reranking/reranker.py` → `ragkit.reranking`
- `generation/{generator,prompts}.py` → `ragkit.generation`
- `citations/engine.py` → `ragkit.citations`
- `core/{models,direct}.py` → `ragkit.core`
- `db/connection.py` → `ragkit.db`

Deps: psycopg[binary], pgvector, sentence-transformers, groq, requests.
App/agent deps (fastapi, chainlit, langgraph) stay DocPilot-side for now.

### 2.2 tasks (execution order)

- [x] S1-T1 scaffold — DONE 2026-09-17 (repo, `src/ragkit/`, pyproject
      uv_build + CPU-torch index, README, .gitignore; `chore: scaffold
      ragkit` pushed to main; editable-installed into the DocPilot venv;
      `import ragkit` verified)
- [x] S1-T1b self-docs — DONE 2026-09-17 (this SPEC/PLAN/ACTIVE trio +
      README pointer, so the framework repo is self-explanatory)
- [x] S1-T2 move the §2.1 modules (mechanical `docpilot.` → `ragkit.` prefix
      swap) + move their unit tests into `tests/` — DONE 2026-09-17
      (moved 16 modules + `db/schema.sql` + 11 unit tests; prefix swap
      verified byte-mechanical; moved suite green in the DocPilot venv:
      182 passed, 1 skipped — model/DB hermetic skips)
- [x] S1-T3 DocPilot rewire (imports → ragkit; delete moved modules from
      `src/docpilot/`; grep-verify zero moved-prefix imports left) — DONE
      2026-09-18 (src + tests rewired; 11 moved unit tests deleted from
      DocPilot; pyproject git pin `@ed0f908`; DocPilot suite green 369,
      ragkit 183 → combined 552)
- [x] S1-T4 connection semantics ownership (ragkit owns DSN→conn; decide
      `db/maintenance.py` home) — DONE 2026-09-18: `ragkit/config.py` owns the
      framework keys (POSTGRES_*, EMBEDDING_MODEL, GROQ_*, RERANKER_MODEL,
      RERANK_CANDIDATES, RETRIEVAL_TOP_K) — env-read with safe defaults, no
      import hard-fail; core-chain modules read `ragkit.config` (reverse
      docpilot dependency gone); DocPilot re-exports the non-secret keys and
      loads `.env` before ragkit.config (`docpilot/__init__.py`);
      `db/maintenance.py` + its SQL/integration tests moved into `ragkit.db`;
      DocPilot dedupe CLI uses `ragkit.db.maintenance`. Combined 552 green
      (ragkit 191 = 181 passed, 10 skipped / DocPilot 361). Restores
      hermeticity: ragkit's live-PG integration tests skip under a bare
      environment instead of borrowing DocPilot's `.env`.
- [x] S1-T5 ragkit standalone test suite green (hermetic — no model/network)
      — DONE 2026-09-18: ragkit suite 181 passed, 10 skipped from its own
      root; every skip is a hermetic availability skip (1 real-corpus-not-
      cloned, 6 live-PG retriever/hybrid, 3 maintenance integration) — no
      model/network access needed
- [x] S1-T6 combined DocPilot + ragkit suite green on ragkit imports
      (≥ baseline 552; unit tests live in ragkit only) — DONE 2026-09-18:
      re-verified after S1-T4 at the committed state — ragkit 191 (181
      passed, 10 skipped) + DocPilot 361 = 552
- [x] S1-T7 retrieval parity evidence (same-process top-k identical pre/post)
      — DONE 2026-09-18: live same-process run — pre-extraction monolith
      `docpilot@69f91dc` (git worktree) vs post-extraction
      `docpilot@ebbdefa` + `ragkit@34686e2`, both against the same live PG
      corpus (15,319 chunks), same call site
      (`pipeline_ask._build_default_retriever()`), BGE-small, top_k=5,
      language=en, levers off. 30 benchmark queries →
      **30/30 top-k IDENTICAL** (harness + evidence in `parity/`). CLI/API
      smoke: `python -m docpilot ask ...` exit 0 with a cited answer
- [x] S1-T8 exit sweep: READMEs honest, tag `v0.1.0`, DocPilot pin ↔ tag
      recorded — DONE 2026-09-18: READMEs updated (both repos); clean-venv
      install from git `@v0.1.0` verified (`import ragkit` + `ragkit.config`
      safe defaults in a deps-free venv); `git tag -a v0.1.0` pushed; DocPilot
      pyproject pin → `@v0.1.0`; §8.5 all `[x]`; no secrets; both repos
      pushed. **Stage 1 COMPLETE — paused for review.**

### 2.3 exit criteria (checked at stage close)

- [x] installable from git; `import ragkit` works in a clean venv — DONE
      (S1-T8: deps-free clean venv from `@v0.1.0`; `import ragkit`,
      `from ragkit import config` succeed)
- [x] DocPilot has zero copies of the moved modules (grep-verified, no shims)
- [x] ragkit standalone test suite green (S1-T5: 181 passed, 10 hermetic skips)
- [x] combined DocPilot + ragkit suite green (≥ 552; unit tests live in
      ragkit only) — S1-T6: ragkit 191 + DocPilot 361 = 552
- [x] retrieval parity evidence committed (`parity/`, 30/30 top-k identical)
- [x] version pairing recorded (DocPilot pin `@v0.1.0` ↔ ragkit tag
      `v0.1.0`); both repos pushed; no secrets

## 3. Stage 2 — agentic (ACTIVE 2026-09-18)

### 3.1 scope (move set, from DocPilot `src/docpilot/`)
- `agent/__init__.py`, `agent/gate.py`, `agent/graph.py`, `agent/interface.py`,
  `agent/judge.py`, `agent/pipeline_agentic.py`, `agent/prompts.py`,
  `agent/questions.py`, `agent/types.py` → `ragkit.agent`
- `tools/__init__.py`, `tools/base.py`, `tools/github.py` → `ragkit.tools`
- NOT moving: `agent/code_route.py`, `codegen/*`, `validation/*` (Stage 4)
- config: `ragkit.config` now owns the `AGENT_*`, `GITHUB_*` and
  `RETRIEVAL_LANGUAGE` keys (env-read, safe defaults identical to DocPilot's
  today; `GITHUB_PAT` optional, default "")
- deps: `langgraph>=1.2.11` moves to ragkit (lazy — only `graph.py` imports
  it, so `ragkit.agent` stays importable without langgraph installed)
- gate: DocPilot full suite green + agentic parity sample (hermetic harness
  + one live smoke — locked 2026-09-18)

### 3.2 tasks (execution order)
- [x] S2-T1: docs — scope + task list + ACTIVE refresh, committed in both
      repos — DONE 2026-09-18 (ragkit PLAN §3 / DocPilot PLAN §8.7)
- [x] S2-T2: move mechanically (prefix swap) into `ragkit.agent` /
      `ragkit.tools`; extend `ragkit.config` with the 10 keys; graph.py
      `_NO_CONTEXT_NOTE` from `ragkit.core.direct`; langgraph dep; 6
      hermetic agent/tool test files move — DONE 2026-09-18
      (`3ded3fb`; ragkit 299 passed/1 skipped, 290/10 hermetic)
- [x] S2-T3: DocPilot dogfood — rewire cli/api/eval/code_route + staying
      tests to `ragkit.agent.*` / `ragkit.tools.*`; delete moved modules +
      tests; DocPilot config re-exports the 10 keys; pin bump; combined
      suite green — DONE 2026-09-18 (DocPilot `b2983de` → ragkit
      `@3ded3fb`; DocPilot 252 + ragkit 300 = 552 ≥ baseline)
- [x] S2-T4: agentic parity evidence — hermetic determinism harness (fakes,
      fixed queries: routing, judge-retry, fake-tool live path): full trace
      identical pre (`docpilot.agent` @ Stage-2 start) vs post
      (`ragkit.agent`); + one live CLI/API smoke — DONE 2026-09-18
      (`ed58c54`; 6/6 scenarios IDENTICAL; live CLI smoke exit 0)
- [x] S2-T5: exit sweep — READMEs honest, clean-venv install from git
      (langgraph), tag `v0.2.0`, DocPilot pin ↔ tag recorded, §3.3 all
      `[x]`, both repos pushed — DONE 2026-09-18 (tag `v0.2.0` =
      `500717d`; clean venv from `git+…ragkit.git@v0.2.0` — deps incl.
      langgraph 1.2.11 resolved, imports OK, `docpilot` not importable;
      DocPilot pin → `@v0.2.0`; both repos pushed)

### 3.3 exit criteria (checked at stage close)
- [x] ragkit standalone test suite green (agent/tools tests included,
      hermetic) — DONE: 299 passed/1 skipped with dev `.env`; 290
      passed/10 skipped bare (all skips hermetic availability)
- [x] combined DocPilot + ragkit suite green; moved unit tests live in
      ragkit only — DONE: DocPilot 252 + ragkit 300 = 552 (= Stage-1
      baseline, 109 tests relocated, zero loss); zero `docpilot.agent` /
      `docpilot.tools` refs left in DocPilot src/tests, no shims
- [x] agentic parity evidence committed (hermetic harness + live smoke)
      — DONE: `parity/s2_agentic_parity_report.md` 6/6 scenarios
      IDENTICAL + `s2_cli_smoke.txt` (exit 0)
- [x] version pairing recorded (DocPilot pin ↔ ragkit tag `v0.2.0`);
      READMEs honest; both repos pushed; no secrets — DONE: DocPilot
      pin → `@v0.2.0` ↔ tag `v0.2.0` (`500717d`); clean-venv install
      from the tag verified; dirty eval reports + `opencode.jsonc`
      remain uncommitted on the DocPilot side

## 4. Stage 3 — eval harness (PLANNED 2026-09-18 — start on user go)

### 4.1 scope (move set, from DocPilot `src/docpilot/`)

- `eval/benchmark.py`, `eval/triples.py`, `eval/judge_ab.py`,
  `eval/tool_necessity.py` → `ragkit.eval` (Evaluator + checkpointed /
  TPD-aware harness; mechanical `docpilot.eval` → `ragkit.eval` prefix swap)
- `eval/__init__.py`, `eval/__main__.py` → `ragkit.eval` (`python -m
  ragkit.eval` dispatcher). The `__main__` `code-benchmark` branch is
  lazy-guarded until Stage 4 (`ragkit.eval.code_benchmark` lands then —
  ImportError → clear "moves in Stage 4" message)
- `eval/dataset/{benchmark,judge_triples,tool_necessity}.json` ship inside
  `ragkit.eval` (committed labeled datasets — SPEC §6.4 rule). NOT moving now:
  `dataset/code_benchmark.json` (rides with `code_benchmark.py`, Stage 4)
- NOT moving: `eval/code_benchmark.py` (imports `validation` — a Stage-4
  module; moving it now would create a `ragkit.eval → docpilot.validation`
  reverse dep and break clean-venv imports), `eval/reports/` (runtime output
  stays DocPilot-side; new JSONs never-commit)
- tests move: `test_eval_benchmark.py`, `test_eval_judge_ab.py`,
  `test_eval_tool_necessity.py` (hermetic — stubbed judge/generator; patch
  sites → `ragkit.config`). `test_eval_code_benchmark.py` stays (Stage 4)
- config: NO new framework keys — eval reads only keys already owned
  (`AGENT_JUDGE_MODEL`, `GROQ_MODEL`, `RETRIEVAL_LANGUAGE`,
  `RETRIEVAL_TOP_K`). Deps: no new — eval reuses ragkit core/agent + existing
  deps
- gate (mirror §3.1): DocPilot full suite green + eval parity sample —
  hermetic determinism harness (fixed dataset rows + stubbed
  retriever/generator/judge → report JSON identical pre/post) + one live
  TPD-aware eval smoke (locked 2026-09-18)

### 4.2 tasks (execution order)

- [x] S3-T1: docs — this section (ragkit PLAN §4 / DocPilot PLAN §8.8) +
      ACTIVE refresh, committed in both repos. Bundle: `eval/*` minus
      `code_benchmark.py` + `reports/`. — DONE 2026-09-18 (ragkit `b8f35b5` /
      DocPilot `6122c8c`; both PLANs + ACTIVE committed and pushed)
- [x] S3-T2: move mechanically (prefix swap `docpilot.eval` → `ragkit.eval`)
      into `ragkit.eval`: benchmark/triples/judge_ab/tool_necessity +
      `__main__`/`__init__` + 3 committed dataset JSONs; `__main__`
      code-benchmark lazy-guard; 3 hermetic eval test files move (patch
      sites → `ragkit.config`); no new config keys or deps. — DONE
      2026-09-19 (ragkit `309037b`; `_classic_run` resolves direct_ask via
      `ragkit.agent.host_wiring`, zero docpilot refs in ragkit src)
- [x] S3-T3: DocPilot dogfood — delete moved modules + tests from
      `src/docpilot/`; rewire any staying consumers to `ragkit.eval`;
      `python -m docpilot.eval` workflow → `python -m ragkit.eval`;
      pyproject pin bump; combined suite green. — DONE 2026-09-19
      (eval modules + 3 tests deleted from `src/docpilot/`; staying
      `code_benchmark.py` + `test_eval_code_benchmark.py` rewire to
      `ragkit.eval.benchmark`; `python -m docpilot.eval` → `python -m
      ragkit.eval` (code-benchmark dispatcher lazy-guarded until Stage 4,
      module still runnable as `python -m docpilot.eval.code_benchmark`);
      pin → `@309037b` (S3-T2 commit; `v0.3.0` tag at S3-T5); DocPilot 142
      + ragkit 410 = 552 baseline held)
- [x] S3-T4: eval parity evidence — hermetic determinism harness: fixed
      dataset rows + stubbed retriever/generator/judge drive the eval
      pipeline pre (`docpilot.eval` @ Stage-3 start worktree) vs post
      (`ragkit.eval`) — report JSON identical field-for-field; + one live
      TPD-aware eval smoke (one invocation). — DONE 2026-09-19
      (`parity/s3_eval_parity.py` + `compare_s3_eval.py`: scripted judges +
      scripted benchmark runner over the committed datasets — judge_ab 24,
      tool_necessity 15, benchmark 30 — `generated_at`/`dataset_path`
      normalised; pre=`docpilot.eval`@`6122c8c` vs post=`ragkit.eval`@
      `68b7790`: every report JSON IDENTICAL field-for-field, exit 0;
      `s3_eval_parity_report.md` committed. Live TPD-aware smoke: one
      invocation `python -m ragkit.eval judge-ab --out /tmp/opencode/
      s3_smoke` — exit 0, 24 triples × 2 prompts (48 live Groq judge calls,
      no TPD abort), report written only to the never-commit dir;
      `parity/s3_eval_smoke.txt` committed)
- [x] S3-T5: exit sweep — READMEs honest (ragkit status Stage 3; DocPilot
      callout eval moved), clean-venv install from git (regression — no new
      deps), tag `v0.3.0`, DocPilot pin → `@v0.3.0`, §4.3 / §8.8b all `[x]`,
      both repos pushed, no secrets. — DONE 2026-09-19 (READMEs both repos
      Stage-3 honest; clean venv from `git+…ragkit.git@v0.3.0` — deps
      unchanged vs `v0.2.0` (empty pyproject diff), imports OK; ragkit 409/1
      + DocPilot 142 = 552; tag `v0.3.0` = `15e2aa1`; DocPilot pin
      `@v0.3.0`; both pushed)

### 4.3 exit criteria (checked at stage close)

- [x] ragkit standalone test suite green (eval tests included, hermetic — no
      model/network; live-PG skips as before) — DONE: 409 passed/1 skipped
- [x] combined DocPilot + ragkit suite green; moved eval tests live in
      ragkit only, no duplicated test files — DONE: DocPilot 142 + ragkit
      410 = 552
- [x] eval parity evidence committed (hermetic report-JSON harness verdict +
      live smoke output) — DONE: S3-T4, `parity/s3_eval_*`
- [x] version pairing recorded (DocPilot pin ↔ ragkit tag `v0.3.0`);
      READMEs honest; both repos pushed; no secrets — DONE: S3-T5

## 5. Stage 4 — codegen (PLANNED 2026-09-18 — start after Stage 3 closes)

### 5.1 scope (move set, from DocPilot `src/docpilot/`)

- `codegen/__init__.py`, `codegen/pipeline_ask_code.py`, `codegen/prompts.py`
  → `ragkit.codegen` (Generator)
- `validation/__init__.py`, `validation/validator.py`, `validation/verdict.py`
  → `ragkit.validation` (CodeValidator)
- `agent/code_route.py` → `ragkit.agent.code_route` (the agent router Stage 2
  deferred; already wired to `ragkit.agent.*` APIs in S2-T3)
- `eval/code_benchmark.py` + `eval/dataset/code_benchmark.json` →
  `ragkit.eval` now importable (validation is in ragkit by then); the §4
  `__main__` lazy-guard activates
- config: `CODE_INTENT_PHRASES`, `CODE_ROUTE_ENABLED`,
  `CODE_VALIDATE_MAX_TURNS` → `ragkit.config` (env-read, safe defaults
  identical to DocPilot's today; DocPilot re-exports). No new deps — groq
  already owned
- tests move: `test_validation.py`, `test_codegen_pipeline.py`,
  `test_code_route.py`, `test_code_route_loop.py`,
  `test_eval_code_benchmark.py` (hermetic; patch sites → `ragkit.config`).
  `test_api_code.py` stays DocPilot-side (API-level, app-facing)
- NOT moving: `api/service.py` code endpoint (`POST /api/v1/code`), CLI code
  wiring — DocPilot app surface stays app-side
- gate: DocPilot full suite green + codegen parity sample — hermetic
  determinism harness (stubbed generator/judge: identical validation verdicts
  + emitted code pre/post) + one live codegen smoke (locked 2026-09-18)

### 5.2 tasks (execution order)

- [ ] S4-T1: docs — this section (ragkit PLAN §5 / DocPilot PLAN §8.9) +
      ACTIVE refresh, committed in both repos.
- [ ] S4-T2: move mechanically (prefix swap) into `ragkit.codegen` /
      `ragkit.validation` / `ragkit.agent.code_route`; `ragkit.eval` gains
      `code_benchmark` + `code_benchmark.json` (activate `__main__` branch);
      `ragkit.config` gains the 3 `CODE_*` keys; 5 hermetic test files move.
- [ ] S4-T3: DocPilot dogfood — rewire `api/service.py` code endpoint + CLI
      code paths + staying app-level test (`test_api_code.py`) to
      `ragkit.codegen` / `ragkit.validation` / `ragkit.agent.code_route`;
      delete moved modules + tests; config re-exports the 3 `CODE_*` keys;
      pin bump; combined suite green.
- [ ] S4-T4: codegen parity evidence — hermetic determinism harness: stubbed
      generator/judge — validation verdicts + emitted code identical pre
      (`docpilot.*` @ Stage-4 start worktree) vs post (`ragkit.*`); + one
      live codegen smoke (TPD-aware, one invocation).
- [ ] S4-T5: exit sweep — READMEs honest, clean-venv install from git
      (regression), tag `v0.4.0`, DocPilot pin → `@v0.4.0`, §5.3 / §8.9b all
      `[x]`, both repos pushed, no secrets; **all §8.4 bundles moved →
      extraction complete**.

### 5.3 exit criteria (checked at stage close)

- [ ] ragkit standalone test suite green (codegen/validation/code_route tests
      included, hermetic)
- [ ] combined DocPilot + ragkit suite green; moved tests live in ragkit only
- [ ] codegen parity evidence committed (hermetic harness verdict + live
      smoke output)
- [ ] version pairing recorded (DocPilot pin ↔ ragkit tag `v0.4.0`);
      READMEs honest; both repos pushed; no secrets; all deferred bundles
      moved

## 6. git workflow

- repo: https://github.com/Saif-Ali-109/ragkit.git, branch main
- Conventional Commits; commit per task; tag stages (`v0.1.0` at Stage-1 end)
- DocPilot pins the exact ragkit commit/tag it consumes (version pairing)
- never commit secrets or `.env`