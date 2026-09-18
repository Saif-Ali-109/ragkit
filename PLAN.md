# ragkit — PLAN (working state, derived from SPEC.md)

role: the HOW — stages, tasks, exit checklists, execution order
authority: derived — SPEC.md wins on conflict

## 1. status

- origin: extracted from DocPilot (Phases 1–6 COMPLETE, 2026-09-12)
- current: Stage 1 — core chain, ACTIVE (started 2026-09-17)
- source-of-truth extraction plan: DocPilot PLAN §8
  (<https://github.com/Saif-Ali-109/DocPilot/blob/main/PLAN.md>)

## 2. Stage 1 — core chain (ACTIVE)

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
- [ ] S1-T8 exit sweep: READMEs honest, tag `v0.1.0`, DocPilot pin ↔ tag
      recorded

### 2.3 exit criteria (checked at stage close)

- [ ] installable from git; `import ragkit` works in a clean venv
- [x] DocPilot has zero copies of the moved modules (grep-verified, no shims)
- [x] ragkit standalone test suite green (S1-T5: 181 passed, 10 hermetic skips)
- [x] combined DocPilot + ragkit suite green (≥ 552; unit tests live in
      ragkit only) — S1-T6: ragkit 191 + DocPilot 361 = 552
- [x] retrieval parity evidence committed (`parity/`, 30/30 top-k identical)
- [ ] version pairing recorded; both repos pushed; no secrets

## 3. Stage 2 — agentic (planned)

- `agent/*`, `tools/*` (GitHub Tool), langgraph dep → ragkit
- gate: DocPilot full suite green + agentic parity sample

## 4. Stage 3 — eval harness (planned)

- `eval/{benchmark,triples,__main__,judge_ab,tool_necessity}.py` →
  `ragkit.eval` (Evaluator + checkpointed/TPD-aware harness)

## 5. Stage 4 — codegen (planned)

- `codegen/*`, `validation/*`, `agent/code_route.py` (Generator +
  CodeValidator)

## 6. git workflow

- repo: https://github.com/Saif-Ali-109/ragkit.git, branch main
- Conventional Commits; commit per task; tag stages (`v0.1.0` at Stage-1 end)
- DocPilot pins the exact ragkit commit/tag it consumes (version pairing)
- never commit secrets or `.env`