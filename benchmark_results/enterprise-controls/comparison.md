# Enterprise control comparison

Dataset: `synthetic-policy-enterprise-controls-v1` · Environment: development

| Backend | Pass | ACL | Refusal | Citations | Grounded | Answer | E2E p50 | E2E p95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| azure_ai_search | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 61547.12 ms | 62242.34 ms |
| pgvector | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 61538.65 ms | 61876.30 ms |
| qdrant | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 46501.04 ms | 62786.99 ms |

Latency phase distributions (mean, median, standard deviation, p50 and p95) are retained
in `comparison.json`. Per-question outcomes and timings are in each backend artifact.

## Interpretation guardrails

- Results use a synthetic policy corpus and a development-scale Azure deployment.
- Generation is non-deterministic; this run is evidence, not a universal quality claim.
- Backends ran sequentially to remain within the development model quota.
- Generation and end-to-end latency include quota retry/queue time in this development deployment.
