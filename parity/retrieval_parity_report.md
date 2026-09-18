## S1-T7 retrieval parity — same-process top-k, pre/post extraction

- pre  : docpilot `69f91dc` (monolith), chunks=15319, timestamp 2026-09-18T15:50:27.628054+00:00
- post : docpilot `ebbdefa` + ragkit `34686e2`, chunks=15319, timestamp 2026-09-18T15:50:55.958001+00:00
- settings: top_k=5, language=en, rerank_enabled=False, hybrid_enabled=False
- queries: 30
- verdict: **IDENTICAL** — 30/30 queries top-k identical (none differ)

## CLI smoke (post-extraction, live)

`python -m docpilot ask "How do I declare a query parameter with a default value in FastAPI?"` from DocPilot `ebbdefa` + ragkit `34686e2`:

- exit code 0; cited answer produced (sources `en/docs/tutorial/query-params*.md`), Groq generation default path — live end-to-end on ragkit imports.
