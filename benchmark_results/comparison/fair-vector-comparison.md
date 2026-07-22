# Fair vector-only retrieval comparison

Dataset: `synthetic-policy-fair-vector-v1` · Cases: 52 · Top k: 5

Environment: development · Measured runs per backend: 1

| Backend | Recall@5 | MRR | Mean retrieval latency (ms) |
|---|---:|---:|---:|
| azure_ai_search | 1.0000 | 0.9904 | 48.63 |
| pgvector | 1.0000 | 0.9904 | 114.97 |
| qdrant | 1.0000 | 0.9904 | 45.78 |

## Interpretation guardrails

- Development-scale results are workload-specific and do not establish a universal winner.
- Latency includes one client-side retrieval call but excludes query embedding generation.
- Platform-optimised hybrid, sparse and semantic features are outside this comparison.
- Each backend has one measured run; latency has no warm-up exclusion or confidence interval.
