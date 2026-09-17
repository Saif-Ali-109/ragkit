# ragkit — SPEC (source of truth)

role: source of truth for the ragkit framework
authority: highest within this repo — README/PLAN/ACTIVE derive from it
repo: https://github.com/Saif-Ali-109/ragkit.git

## 1. Project Overview

ragkit is a **reusable RAG framework** extracted from DocPilot
(<https://github.com/Saif-Ali-109/DocPilot>). DocPilot is the learning/
validation project; ragkit is the reusable result, extracted only after
DocPilot worked end-to-end and was evaluated (DocPilot Phases 1–6 COMPLETE,
2026-09-12). DocPilot then consumes ragkit (dogfood) so the extraction is
validated by reality, not by claims.

- Swappable interfaces + reference implementations: `DocumentLoader`,
  `Parser`, `Chunker`, `EmbeddingProvider`, `VectorStore`, `Retriever`,
  `Reranker`, `Tool`, `Agent`, `Generator`, `CitationEngine`, `Evaluator`,
  `CodeValidator`.
- No vendor/library calls hard-coded into business logic — BGE, pgvector,
  Groq, LangGraph are implementations behind interfaces.
- Every retrieval and tool decision is inspectable/loggable.

## 2. Extraction stages (build order)

```
Stage 1: Core chain → Stage 2: Agentic layer → Stage 3: Eval harness → Stage 4: Codegen
```

Hard rules:
1. Extraction is a **refactor** — zero behavior change in DocPilot while
   moving code; no "improving" during the move (improvements = follow-ups).
2. DocPilot **dogfoods** ragkit — no copied modules or re-export shims left
   in DocPilot.
3. Every stage gate: DocPilot's full pytest suite green + retrieval parity
   against pre-extraction results.
4. No CI / PyPI publishing until the user explicitly calls for it.

## 3. Stage 1 — Core chain (current)

Scope: loader → parser → chunker → embeddings → vector store → retriever →
generation → citations; the `Reranker` interface moves with it (its gate
lever remains OFF). Tasks and exit criteria → PLAN.md §2.

## 4. Locked decisions

| Date | Decision |
|---|---|
| 2026-09-17 | Separate repo (this one); DocPilot dogfoods ragkit; core chain first; installable, no CI/PyPI |
| 2026-09-17 | Package layout mirrors source: `docpilot.<sub>.<mod>` → `ragkit.<sub>.<mod>` (mechanical prefix swap) |

## 5. Conflict resolution

- feature-during-extraction: refactor-only; feature changes are follow-ups
  after the stage gate.
- skip-evaluation: never — each stage's gate is DocPilot tests + retrieval
  parity.
- unsure-of-stage: ask before restructuring code to fit a stage.