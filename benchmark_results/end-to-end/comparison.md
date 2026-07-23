# End-to-end RAG comparison

Dataset: `synthetic-policy-end-to-end-v1` · Environment: development

| Backend | Pass | ACL | Refusal | Citations | Grounded | Answer | E2E p50 | E2E p95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| azure_ai_search | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 61872.60 ms | 62210.97 ms |
| pgvector | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 61594.13 ms | 62299.90 ms |
| qdrant | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 61745.85 ms | 61970.89 ms |

Latency phase distributions (mean, median, standard deviation, p50 and p95) are retained
in `comparison.json`. Per-question outcomes and timings are in each backend artifact.

## Interpretation guardrails

- Results use a synthetic policy corpus and a development-scale Azure deployment.
- Generation is non-deterministic; this run is evidence, not a universal quality claim.
- Backends ran sequentially to remain within the development model quota.
- Generation and end-to-end latency include quota retry/queue time in this development deployment.
