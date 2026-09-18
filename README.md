# ragkit

Reusable RAG framework extracted from DocPilot
(<https://github.com/Saif-Ali-109/DocPilot>) and consumed by it (dogfood).

**Status — Stage 1 (core chain) complete, `v0.1.0`.** The loader → parser →
chunker → embeddings → vector store → retriever → generator → citations
components now live here; DocPilot imports them and its suite stays green
(combined 552). Retrieval parity with the pre-extraction monolith is
evidenced (`parity/`, 30/30 queries top-k identical, live same-process run).

- Install: `uv pip install "ragkit @ git+https://github.com/Saif-Ali-109/ragkit.git@v0.1.0"` — `import ragkit` works in a clean venv.
- Framework config is owned by `ragkit.config` (env-read, safe defaults; a
  host app loads its `.env` before importing ragkit — DocPilot does this).
- Scope: core chain done (Stage 1); agentic layer, eval harness, and codegen
  follow as later stages (DocPilot PLAN §8). No CI or PyPI publishing yet.

## Docs (framework self-documentation)

- **SPEC.md** — source of truth: purpose, stages, locked decisions
- **PLAN.md** — working state: tasks, exit checklists
- **ACTIVE.md** — current view: stage, what happened, load index