# Platform-optimised retrieval comparison

Dataset: `synthetic-policy-fair-vector-v1` · Cases: 52 · Top k: 5

Environment: development · Measured repetitions per backend: 3

| Backend | Recall@5 | Precision@5 | MRR | nDCG@5 | p50 (ms) | p95 (ms) |
|---|---:|---:|---:|---:|---:|---:|
| azure_ai_search | 1.0000 | 0.2000 | 1.0000 | 1.0000 | 75.69 | 181.34 |
| pgvector | 1.0000 | 0.2000 | 0.9776 | 0.9833 | 95.54 | 117.43 |
| qdrant | 1.0000 | 0.2000 | 0.9679 | 0.9763 | 55.87 | 60.04 |

## Interpretation guardrails

- Development-scale results are workload-specific and do not establish a universal winner.
- Latency includes one client-side retrieval call but excludes query embedding generation.
- Platform-optimised features differ by backend and are intentionally not a controlled vector-only comparison.
