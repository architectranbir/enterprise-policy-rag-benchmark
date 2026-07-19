# Project Scope

## Overview

This project builds an enterprise policy assistant that answers questions using approved policy documents and returns the source sections used to generate each response.

The implementation focuses on document ingestion, access-aware retrieval, policy versioning, grounded answers, citations, evaluation and operational visibility.

## Use case

Employees often need to search across policies, standards and internal guidance before making a decision. Relevant information may be spread across multiple documents, departments and policy versions.

The assistant is designed to:

* retrieve information from the policies a user is allowed to access;
* select the policy version that is effective for the requested date;
* answer using retrieved evidence rather than model knowledge;
* provide document and section-level citations;
* refuse or escalate questions when there is not enough supporting evidence.

## Retrieval backends

The same application will support three interchangeable retrieval backends:

1. Azure AI Search
2. PostgreSQL with pgvector
3. Qdrant

Only one backend is active during a normal application run.

## Benchmark approach

The project maintains two separate evaluation modes.

### Controlled vector benchmark

The documents, extracted text, chunks, metadata, embedding model, similarity settings, questions and retrieval depth remain consistent across all three backends.

### Platform-specific benchmark

Each backend may use its own search capabilities:

* Azure AI Search: keyword, vector, hybrid and semantic search
* PostgreSQL with pgvector: PostgreSQL full-text search and vector retrieval
* Qdrant: dense and sparse retrieval with metadata filtering

Results from the two modes are reported separately.

## Data

All organisations, users, groups and policy documents in this repository are fictional.

The repository does not contain employer, client or confidential information.

## Current status

The repository is being developed incrementally. Features and benchmark results will only be documented as completed after they have been implemented and verified.