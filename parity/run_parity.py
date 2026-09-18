"""Same-process retrieval top-k parity recorder (PLAN §8.3 S1-T7).

Runs the exact app retriever construction and retrieval against live PG and
writes the top-k results as JSON.  Run once per side::

    PARITY_MODE=pre  PYTHONPATH=<pre-extraction src> python run_parity.py /tmp/outdir
    PARITY_MODE=post python run_parity.py /tmp/outdir

Both sides call the *same* call site —
``docpilot.pipeline_ask._build_default_retriever()`` — so the only variable
is which ``docpilot`` package is importable (worktree monolith vs
ragkit-backed).

Requires: DocPilot's ``.env`` (POSTGRES_* + BGE model available).  In the
pre run ``docpilot.config`` loads ``.env`` from the worktree root; copy it
there first.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve()
_QUERIES_PATH = _HERE.parent / "queries.json"


def _short_sha(cwd: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=cwd,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _chunks_count(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM chunks")
        (n,) = cur.fetchone()
    return int(n)


def run_par(mode: str, outdir: str) -> None:
    # --- imports ------------------------------------------------------------
    from docpilot import config
    from docpilot.pipeline_ask import _build_default_retriever

    # --- build retriever (loads BGE model once) -----------------------------
    t0 = time.perf_counter()
    retriever, conn = _build_default_retriever()
    build_s = time.perf_counter() - t0

    top_k = config.RETRIEVAL_TOP_K
    chunks_count = _chunks_count(conn)

    # Mirror pipeline_ask.ask(): explicit language → config default; the
    # literal "any" disables the filter at the retrieval layer.
    resolved_language = config.RETRIEVAL_LANGUAGE
    filter_language = None if resolved_language == "any" else resolved_language

    # --- retrieve -----------------------------------------------------------
    queries_path = _QUERIES_PATH
    qs = json.loads(queries_path.read_text())["queries"]

    results: dict[str, list[dict]] = {}
    t0 = time.perf_counter()
    for q in qs:
        retrieved = retriever.retrieve(
            q["question"], top_k=top_k, language=filter_language
        )
        results[q["id"]] = [
            {
                "id": r.chunk.id,
                "source_file": r.chunk.source_file,
                "chunk_index": r.chunk.chunk_index,
                "score": r.score,
            }
            for r in retrieved
        ]
    retrieve_s = time.perf_counter() - t0

    conn.close()

    # --- meta ---------------------------------------------------------------
    if mode == "pre":
        dp_sha = _short_sha("/tmp/opencode/dp-pre")
        rk_sha = ""
    else:
        dp_sha = _short_sha(str(Path.cwd()))
        rk_sha = _short_sha("/home/ain/Desktop/framework/ragkit")

    meta = {
        "mode": mode,
        "docpilot_commit": dp_sha,
        "ragkit_commit": rk_sha,
        "chunks_count": chunks_count,
        "top_k": top_k,
        "retrieval_language": config.RETRIEVAL_LANGUAGE,
        "rerank_enabled": config.RERANK_ENABLED,
        "hybrid_enabled": config.HYBRID_ENABLED,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "build_elapsed_s": round(build_s, 2),
        "retrieve_elapsed_s": round(retrieve_s, 3),
        "queries_count": len(qs),
    }

    payload = {"meta": meta, "results": results}

    out_path = Path(outdir) / f"retrieval_topk_{mode}.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        f"mode={mode}  queries={len(qs)}  top_k={top_k}  "
        f"build={build_s:.1f}s  retrieve={retrieve_s:.3f}s  → {out_path}"
    )


if __name__ == "__main__":
    mode = os.environ.get("PARITY_MODE", "")
    if mode not in ("pre", "post"):
        sys.exit(f"PARITY_MODE must be 'pre' or 'post', got '{mode}'")
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    run_par(mode, outdir)
