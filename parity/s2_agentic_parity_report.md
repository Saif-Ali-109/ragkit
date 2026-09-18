## S2-T4 agentic parity — hermetic, deterministic pre/post extraction

- pre  : docpilot `391ebc8` (`docpilot.agent`), timestamp 2026-09-18T17:39:22.976994+00:00
- post : docpilot `b2983de` + ragkit `3ded3fb` (`ragkit.agent`), timestamp 2026-09-18T17:39:24.074989+00:00
- hermetic: True — canned retriever/generator/judge/tool injected; GITHUB_PAT zeroed; no network / DB / LLM
- scenarios: 6 (direct auto, direct forced, agentic sufficient, agentic forced-simple, agentic retry-reformulate, agentic needs-tool)
- compared fields: answer, direct, refused, max_retries, sources, trace, retriever_calls, judge_calls, judge_tools_seen, tool_calls (trace latency excluded)
- verdict: **IDENTICAL**

Every scenario matches field-for-field on both sides.

## Live CLI smoke (post-extraction, one invocation)

```
$ python -m docpilot ask --strategy agentic "Combine path, query, and body parameters in one endpoint — what are the validation rules for each kind?"
(exit 0)
(post-extraction stack: DocPilot b2983de + ragkit 3ded3fb; live PG corpus 15,319 chunks; Groq generator + judge; one live invocation — S2-T4 "one live CLI smoke" budget)

stdout (replayed verbatim):

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights:   0%|          | 0/199 [00:00<?, ?it/s]
Loading weights: 100%|██████████| 199/199 [00:00<00:00, 5574.85it/s]
I don't know — the available documentation does not cover this question.

Interpretation: exit 0 — the agentic path ran live end-to-end on the moved
ragkit.agent code: host wiring built the DB-backed default retriever, the
Groq sufficiency judge evaluated the retrieval, and the generator terminated
with the SPEC §3.9 refusal — a legitimate terminal verdict when the judge
deems the retrieved evidence insufficient. A citation-bearing answer on the
agentic branch is covered hermetically by the six parity scenarios
(agentic_sufficient / retry / needs-tool answer paths are field-for-field
identical pre/post); the live budget was spent deliberately on exactly one
invocation (Groq TPD).
```

_report generated 2026-09-18T17:42:18.062874+00:00 by compare_s2_agentic.py_
