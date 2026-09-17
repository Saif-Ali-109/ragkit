# ragkit

Reusable RAG framework extracted from DocPilot
(<https://github.com/Saif-Ali-109/DocPilot>).

**Status — Stage 1 (core chain), in progress.** The loader → parser → chunker →
embeddings → vector store → retriever → generator → citations components are
being moved out of DocPilot into this package, and DocPilot consumes ragkit
(dogfood) so the extraction is validated by DocPilot's existing test suite
staying green — not by new claims.

- Scope: core chain first (Stage 1); agentic layer, eval harness, and codegen
  follow as later stages (DocPilot PLAN §8).
- No CI or PyPI publishing yet.