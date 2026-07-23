# Benchmark evidence

This directory contains the schema-validated evidence for the live Azure development benchmark
executed on 22–23 July 2026. All content uses synthetic company policies and fictional access
groups.

## Execution manifest

| Track | Questions / cases | Repetitions | Backends | Measured executions |
|---|---:|---:|---:|---:|
| Fair vector-only | 52 | 3 | 3 | 468 |
| Platform-optimised | 52 | 3 | 3 | 468 |
| Enterprise controls | 8 | 1 | 3 | 24 |
| End-to-end RAG | 12 | 1 | 3 | 36 |
| **Total** | | | | **996** |

Each retrieval backend also received three unmeasured warm-up requests per retrieval track.
Retrieval-only tracks used precomputed query embeddings. Answer-generation tracks ran sequentially
to stay within the development Foundry quota.

## Evidence layout

- `raw/`: fair vector-only per-backend JSON, CSV and Markdown.
- `comparison/`: fair vector-only comparison and interpretation guardrails.
- `platform-optimized/`: platform-specific raw evidence and a separate comparison.
- `enterprise-controls/`: ACL, department/group, effective-date, version, refusal, citation,
  groundedness and correctness evidence.
- `end-to-end/`: representative grounded-answer evidence with embedding, retrieval, generation and
  end-to-end timings.

JSON is the canonical machine-readable evidence. CSV provides per-question analysis. Markdown is
the publishable summary. `scripts/validate_benchmark_artifacts.py` validates backend completeness,
dataset comparability, track isolation, companion formats and the exact measured-execution count.

## Interpretation

These results describe one synthetic workload on a development-scale Azure deployment. They do
not establish a universal database winner. Fair vector-only results support controlled retrieval
comparison; platform-optimised results describe different vendor-specific feature sets and must
not be mixed with the fair baseline. Generation latency includes model-quota retry/queue time.
