# ragkit

Reusable RAG framework extracted from DocPilot
(<https://github.com/Saif-Ali-109/DocPilot>) and consumed by it (dogfood).

**Status — Stage 3 (eval harness) complete, `v0.3.0`.** Stage 1 moved the
core chain (loader → parser → chunker → embeddings → vector store →
retriever → generator → citations); Stage 2 moved the agentic layer
(`ragkit.agent`: gate, LangGraph loop, sufficiency judge, pipeline),
`ragkit.tools`, and `ragkit.testing` (single copy of the canned test fakes);
Stage 3 moved the eval harness (`ragkit.eval`: `benchmark`, `triples`,
`judge_ab`, `tool_necessity`, CLI `python -m ragkit.eval` + committed
datasets). DocPilot imports all of it and its suite stays green
(combined 552, unchanged across all three stages — tests relocated, zero
loss).

- Install: `uv pip install "ragkit @ git+https://github.com/Saif-Ali-109/ragkit.git@v0.3.0"` — `import ragkit` works in a clean venv (`langgraph>=1.2.11` is a declared dep, lazily imported by `graph.py`).
- Framework config is owned by `ragkit.config` (env-read, safe defaults; a
  host app loads its `.env` before importing ragkit — DocPilot does this,
  and may register its own pipeline hooks via `ragkit.agent.host_wiring`).
- Parity evidence lives in `parity/`: Stage-1 retrieval top-k 30/30
  identical (live same-process run), Stage-2 hermetic agentic parity 6/6
  scenarios identical (direct/agentic routing, judge retry, needs-tool) +
  one live CLI smoke, and Stage-3 hermetic eval report parity (judge_ab /
  tool_necessity / benchmark report JSONs identical field-for-field pre vs
  post) + one live TPD-aware eval smoke.
- Scope: core chain + agentic layer + eval harness done (Stages 1–3);
  codegen follows as a later stage (DocPilot PLAN §8). No CI or PyPI publishing yet.

## Docs (framework self-documentation)

- **SPEC.md** — source of truth: purpose, stages, locked decisions
- **PLAN.md** — working state: tasks, exit checklists
- **ACTIVE.md** — current view: stage, what happened, load index