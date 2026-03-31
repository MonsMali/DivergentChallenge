# Architecture

## Overview

RevOps Copilot is a Python CLI that ingests fragmented operational data (CSVs, text files) from Google Drive or local disk, runs it through a four-stage agentic pipeline, and produces actionable deal recommendations in response to natural language questions. Each stage deliberately chooses between deterministic logic and LLM reasoning based on whether the task requires interpretation.

## Workflow

```
User Query
    |
    v
+----------+    Deterministic: file I/O, CSV parsing, data merging,
| INGESTER |    company name matching, data quality flagging.
+----+-----+    Output: list[EnrichedDeal] + DataQualityReport
     |
     v
+----------+    LLM: receives query + schema summary (not raw data).
| PLANNER  |    Output: AnalysisPlan (JSON) with analysis type + reasoning.
+----+-----+
     |
     v
+----------+    Hybrid: deterministic risk scoring (weighted formula) +
| ANALYZER |    LLM sentiment classification (batched, single call).
+----+-----+    Output: deals with risk_score + sentiment attached.
     |
     v
+-------------+  LLM: generates prioritized, actionable recommendations
| SYNTHESIZER |  with specific deals, dollar amounts, and next steps.
+-------------+  Output: natural language advisory text.
```

## Tools Used

- **anthropic SDK** - Direct Claude Sonnet 4 API access; thin wrapper over framework for 3 LLM calls per query
- **pandas** - CSV parsing, DataFrame merges, null handling for tabular deal data
- **pydantic** - Typed data contracts between pipeline steps; schema validation at each boundary
- **click** - CLI framework for commands (`ask`, `status`), options, and flags
- **google-api-python-client** - Google Drive file download via service account authentication
- **python-dotenv** - Environment variable loading for API keys and credentials

## Orchestration

Linear sequential pipeline: Ingester -> Planner -> Analyzer -> Synthesizer. Each step has typed pydantic input/output. The orchestrator runs steps in sequence, collects token usage from each LLM call, and returns a structured `PipelineResult`. This is intentionally not a DAG — the workflow is linear with each step depending on the previous. A verbose mode prints intermediate results after each step for debugging.

## Deterministic vs LLM Decisions

| Step | Type | Why |
|------|------|-----|
| File I/O, CSV parsing | Deterministic | Structured data, no ambiguity |
| Data merging (joins on deal_id, company) | Deterministic | Exact-match keys, no interpretation |
| Data quality flagging | Deterministic | Rule-based null checks, 100% reliable |
| Risk scoring | Deterministic | Weighted formula: reproducible, auditable |
| Query understanding / planning | **LLM** | Natural language intent classification |
| Call note sentiment analysis | **LLM** | Free-text interpretation, no reliable rules |
| Final synthesis / recommendations | **LLM** | Cross-data reasoning + NL generation |

## Google Drive Integration

The source layer is abstracted from the pipeline. `sources/gdrive.py` authenticates via service account, downloads all files from a Drive folder to a temp directory, and returns the path. The ingester receives a directory path regardless of origin, making it source-agnostic. The same pattern extends to S3, SFTP, or CRM API exports by adding new source modules.

## Token Usage & Cost

Measured across 3 example queries (Claude Sonnet 4, `claude-sonnet-4-20250514`):

| Step | Avg Input | Avg Output | Avg Cost |
|------|-----------|------------|----------|
| Planner | 347 | 71 | $0.0021 |
| Analyzer | 136 | 55 | $0.0012 |
| Synthesizer | 836 | 660 | $0.0124 |
| **Total** | **1,319** | **786** | **$0.016** |

Key optimizations: schema summaries (not raw data) sent to LLM, batched sentiment classification (1 call for all notes), concise role-specific system prompts, deterministic pre-filtering before LLM reasoning. At production scale: route classification to Haiku (12x cheaper), enable prompt caching, use Batch API for scheduled runs.
