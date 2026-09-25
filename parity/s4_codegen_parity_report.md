## S4-T4 codegen parity — hermetic, deterministic pre/post payloads

- pre  : docpilot `34dea0d` (`docpilot.codegen` / `docpilot.validation` / `docpilot.agent.code_route` / `docpilot.eval.code_benchmark` @ Stage-4 start), timestamp 2026-09-23T16:59:17.372398+00:00
- post : docpilot `c1d3664` + ragkit `127cfb0` (`ragkit.*`), timestamp 2026-09-23T16:59:20.158484+00:00
- hermetic: True — scripted retriever/generator/runner; GITHUB_PAT zeroed; no network / DB / LLM
- dataset: code_benchmark 6 rows, sha256 `ecc1975a1914c27ab6f7f1ce394f86b81e580b379af2b6fc7024760a649373dc` (identical pre/post); fixtures fastapi_basic sha-identical (verified)
- normalized: latency_ms (ask_code/code_route set to 0.0), generated_at (code_benchmark pinned)
- compared sections: codegen, validation, code_route, code_benchmark (codegen valid+refused, validation verdicts incl. SKIP path, code_route fallback/validated/refused, code_benchmark full report)
- verdict: **IDENTICAL**

Every payload matches field-for-field on both sides (prompts, emitted code, validation verdicts, route decisions, benchmark rows + metrics).

## Live codegen smoke (post-extraction, one invocation)

```
$ python /tmp/opencode/s4_smoke.py  (one live codegen invocation — S4-T4 "one live smoke" budget)
(post-extraction stack: DocPilot c1d3664 + ragkit 127cfb0; host wiring registered by
 docpilot; live PG corpus 15.3k chunks; Groq generator; explicit code opt-in)

question      : Write a minimal FastAPI application with a GET endpoint that returns 'Hello, World'.
decision      : True (explicit code opt-in)
code emitted  : 1 block(s)
validated     : PASS (3 checks)
validation    : passed=True failed=False
sources       : 5 source(s)
attempts      : 1
--- answer ---
```Python
# [1]
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return "Hello, World"
```

This minimal FastAPI application creates an `app` instance, defines a single GET endpoint at the root path (`/`), and returns the string `"Hello, World"` when the endpoint is accessed. The code follows the pattern shown in the documentation examples for creating a FastAPI app and defining a route.
```

_report generated 2026-09-23T17:00:27.764636+00:00 by compare_s4_codegen.py_
