## S3-T4 eval parity — hermetic, deterministic pre/post eval reports

- pre  : docpilot `6122c8c` (`docpilot.eval` @ Stage-3 start), timestamp 2026-09-19T08:49:25.923823+00:00
- post : docpilot `1d9bda2` + ragkit `68b7790` (`ragkit.eval`), timestamp 2026-09-19T08:49:31.228037+00:00
- hermetic: True — scripted judges + scripted benchmark runner; GITHUB_PAT zeroed; no network / DB / LLM
- datasets: {'benchmark': 30, 'judge_triples': 24, 'tool_necessity': 15} (judge_triples / tool_necessity / benchmark — sha256-identical pre/post)
- normalized: generated_at, dataset_path (generated_at pinned; judge_ab dataset_path fixed label)
- compared sections: judge_ab, tool_necessity, benchmark (benchmark = classic + agentic reports + §6.1 comparison)
- verdict: **IDENTICAL**

Every report JSON matches field-for-field on both sides (judge_ab A/B calibration, tool-necessity tri-class metrics, benchmark classic/agentic reports + comparison).

## Live eval smoke (post-extraction, one invocation)

```
Judge two-prompt A/B — dataset: /home/ain/Desktop/framework/ragkit/src/ragkit/eval/dataset/judge_triples.json (24 triples)
winner: tie (calibration-only outcome; adoption is the client's call)

metric                         A         B
------------------------------------------
verdict_accuracy           1.000     1.000
adversarial_accuracy       1.000     1.000
parse_failure_rate         0.000     0.000
------------------------------------------
Per-category accuracy (A / B):
  sufficient-direct        1.000 / 1.000    (n=6)
  sufficient-partial       1.000 / 1.000    (n=6)
  insufficient-missing     1.000 / 1.000    (n=6)
  adversarial              1.000 / 1.000    (n=6)

Confusion (gold → predicted): A / B
  sufficient   sufficient: 15/15  insufficient: 0/0
  insufficient sufficient: 0/0  insufficient: 9/9

  prompt A parse failures: none
  prompt B parse failures: none
```

_report generated 2026-09-19T09:01:23.071653+00:00 by compare_s3_eval.py_
