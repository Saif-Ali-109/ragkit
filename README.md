# ragkit

Reusable RAG framework extracted from DocPilot
(<https://github.com/Saif-Ali-109/DocPilot>) and consumed by it (dogfood).

**Status — Stage 4 (codegen) complete, `v0.4.0` — extraction complete.** Stage 1
moved the core chain (loader → parser → chunker → embeddings → vector store →
retriever → generator → citations); Stage 2 moved the agentic layer
(`ragkit.agent`: gate, LangGraph loop, sufficiency judge, pipeline),
`ragkit.tools`, and `ragkit.testing` (single copy of the canned test fakes);
Stage 3 moved the eval harness (`ragkit.eval`: `benchmark`, `triples`,
`judge_ab`, `tool_necessity`, CLI `python -m ragkit.eval` + committed
datasets); Stage 4 (final) moved the codegen stack (`ragkit.codegen`,
`ragkit.validation`, `ragkit.agent.code_route`, plus the code benchmark in
`ragkit.eval` with its `code_benchmark.json` dataset). Every bundle in the
extraction plan (DocPilot PLAN §8.4) is now in ragkit. DocPilot imports all
of it and its suite stays green (combined 552, unchanged across all stages —
tests relocated, zero loss).

- Install: `uv pip install "ragkit @ git+https://github.com/Saif-Ali-109/ragkit.git@v0.4.0"` — `import ragkit` works in a clean venv (`langgraph>=1.2.11` is a declared dep, lazily imported by `graph.py`).
- Framework config is owned by `ragkit.config` (env-read, safe defaults; a
  host app loads its `.env` before importing ragkit — DocPilot does this,
  and may register its own pipeline hooks via `ragkit.agent.host_wiring`).
- Parity evidence lives in `parity/`: Stage-1 retrieval top-k 30/30
  identical (live same-process run), Stage-2 hermetic agentic parity 6/6
  scenarios identical (direct/agentic routing, judge retry, needs-tool) +
  one live CLI smoke, Stage-3 hermetic eval report parity (judge_ab /
  tool_necessity / benchmark report JSONs identical field-for-field pre vs
  post) + one live TPD-aware eval smoke, and Stage-4 hermetic codegen parity
  (validation verdicts + emitted code + code_route + code_benchmark
  payloads identical pre vs post) + one live TPD-aware codegen smoke.
- Scope: all deferred bundles moved (Stages 1–4) — extraction complete, per
  DocPilot PLAN §8. No CI or PyPI publishing yet.

## Docs (framework self-documentation)

- **SPEC.md** — source of truth: purpose, stages, locked decisions
- **PLAN.md** — working state: tasks, exit checklists
- **ACTIVE.md** — current view: stage, what happened, load index