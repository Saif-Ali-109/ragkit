# ragkit

Reusable RAG framework extracted from DocPilot
(<https://github.com/Saif-Ali-109/DocPilot>) and consumed by it (dogfood).

**Status — Stage 2 (agentic core) complete, `v0.2.0`.** Stage 1 moved the
core chain (loader → parser → chunker → embeddings → vector store →
retriever → generator → citations); Stage 2 moved the agentic layer
(`ragkit.agent`: gate, LangGraph loop, sufficiency judge, pipeline) and the
GitHub tool (`ragkit.tools`), plus `ragkit.testing` (single copy of the
canned test fakes). DocPilot imports all of it and its suite stays green
(combined 552, unchanged across both stages — 109 tests relocated, zero
loss).

- Install: `uv pip install "ragkit @ git+https://github.com/Saif-Ali-109/ragkit.git@v0.2.0"` — `import ragkit` works in a clean venv (`langgraph>=1.2.11` is a declared dep, lazily imported by `graph.py`).
- Framework config is owned by `ragkit.config` (env-read, safe defaults; a
  host app loads its `.env` before importing ragkit — DocPilot does this,
  and may register its own pipeline hooks via `ragkit.agent.host_wiring`).
- Parity evidence lives in `parity/`: Stage-1 retrieval top-k 30/30
  identical (live same-process run) and Stage-2 hermetic agentic parity
  6/6 scenarios identical (direct/agentic routing, judge retry,
  needs-tool) + one live CLI smoke.
- Scope: core chain + agentic layer done (Stages 1–2); eval harness and
  codegen follow as later stages (DocPilot PLAN §8). No CI or PyPI publishing yet.

## Docs (framework self-documentation)

- **SPEC.md** — source of truth: purpose, stages, locked decisions
- **PLAN.md** — working state: tasks, exit checklists
- **ACTIVE.md** — current view: stage, what happened, load index