"""Compare pre/post retrieval top-k parity JSONs (PLAN §8.3 S1-T7).

Loads the two ``retrieval_topk_{mode}.json`` outputs, asserts the top-k
sequence is byte-equal per query (chunk id + source file + chunk index +
exact score), and writes the verdict report:

    python compare_parity.py /tmp/outdir/pre.json /tmp/outdir/post.json

Exit 0 when every query is identical, 1 otherwise.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main(pre_path: str, post_path: str) -> int:
    pre = json.loads(Path(pre_path).read_text())
    post = json.loads(Path(post_path).read_text())

    assert pre["meta"]["mode"] == "pre" and post["meta"]["mode"] == "post"

    pre_res, post_res = pre["results"], post["results"]
    assert pre_res.keys() == post_res.keys(), "query id sets differ"

    identical = True
    differs: list[str] = []
    for qid in pre_res:
        if pre_res[qid] != post_res[qid]:
            identical = False
            differs.append(qid)

    pre_meta, post_meta = pre["meta"], post["meta"]
    report = (
        "## S1-T7 retrieval parity — same-process top-k, pre/post extraction\n\n"
        f"- pre  : docpilot `{pre_meta['docpilot_commit']}` "
        f"(monolith), chunks={pre_meta['chunks_count']}, "
        f"timestamp {pre_meta['timestamp']}\n"
        f"- post : docpilot `{post_meta['docpilot_commit']}` + "
        f"ragkit `{post_meta['ragkit_commit']}`, "
        f"chunks={post_meta['chunks_count']}, timestamp {post_meta['timestamp']}\n"
        f"- settings: top_k={pre_meta['top_k']}, "
        f"language={pre_meta['retrieval_language']}, "
        f"rerank_enabled={pre_meta['rerank_enabled']}, "
        f"hybrid_enabled={pre_meta['hybrid_enabled']}\n"
        f"- queries: {len(pre_res)}\n"
        f"- verdict: **{'IDENTICAL' if identical else 'MISMATCH'}"
        f"** — {len(pre_res) - len(differs)}/{len(pre_res)} queries "
        f"top-k identical ({', '.join(differs) or 'none'} differ)\n"
    )

    out = Path(pre_path).parent / "retrieval_parity_report.md"
    out.write_text(report)
    print(report)
    return 0 if identical else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: compare_parity.py <pre.json> <post.json>")
    sys.exit(main(sys.argv[1], sys.argv[2]))