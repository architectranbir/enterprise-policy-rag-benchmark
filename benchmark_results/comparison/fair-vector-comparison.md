# Fair vector-only retrieval comparison

Dataset: `synthetic-policy-fair-vector-v1` · Cases: 52 · Top k: 5

Environment: development · Measured repetitions per backend: 3

| Backend | Recall@5 | Precision@5 | MRR | nDCG@5 | p50 (ms) | p95 (ms) |
|---|---:|---:|---:|---:|---:|---:|
| azure_ai_search | 1.0000 | 0.2000 | 0.9904 | 0.9929 | 32.57 | 45.33 |
| pgvector | 1.0000 | 0.2000 | 0.9904 | 0.9929 | 94.44 | 121.03 |
| qdrant | 1.0000 | 0.2000 | 0.9904 | 0.9929 | 51.86 | 55.92 |

## Interpretation guardrails

- Development-scale results are workload-specific and do not establish a universal winner.
- Latency includes one client-side retrieval call but excludes query embedding generation.
- Platform-optimised hybrid, sparse and semantic features are outside this comparison.
