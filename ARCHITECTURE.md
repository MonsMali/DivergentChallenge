# Architecture

## Overview

RevOps Copilot is a Python CLI that connects to Google Drive, ingests fragmented operational data (CSVs, text files), runs it through a four-stage agentic pipeline, and produces actionable deal recommendations in response to natural language questions. Each stage deliberately chooses between deterministic logic and LLM reasoning based on whether the task requires interpretation.

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

- **anthropic SDK** - Direct API access to Claude Sonnet 4.6 (planning + synthesis) and Haiku 4.5 (sentiment classification); thin wrapper, no framework needed for 3 LLM calls per query
- **pandas** - CSV parsing, DataFrame merges, null handling for tabular deal data
- **pydantic** - Typed data contracts between pipeline steps; schema validation at each boundary
- **click** - CLI framework for commands (`ask`, `chat`, `status`), options, and flags
- **rich** - Terminal formatting: colored output, tables, panels, progress spinners
- **google-api-python-client** - Google Drive file download via service account authentication
- **python-dotenv** - Environment variable loading for API keys and credentials

## Orchestration

Linear sequential pipeline: Ingester -> Planner -> Analyzer -> Synthesizer. Each step has typed pydantic input/output. The orchestrator exposes `load_data()` (Drive download + ingestion) and `run_analysis()` (planner + analyzer + synthesizer) as separate functions. This split enables the `chat` command to cache ingested data and only re-run the LLM steps per query. A verbose mode prints intermediate results after each step for debugging.

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

The source layer is abstracted from the pipeline. `sources/gdrive.py` authenticates via service account, downloads all files from a Drive folder to a temp directory, and returns the path. The ingester receives a directory path regardless of origin, making it source-agnostic. This pattern extends to other sources (S3, SFTP, CRM API exports) by adding new modules that return a directory path.

## Token Usage & Cost

Measured across 3 example queries (Sonnet 4.6 for planner/synthesizer, Haiku 4.5 for analyzer):

| Step | Model | Avg Input | Avg Output | Avg Cost |
|------|-------|-----------|------------|----------|
| Planner | Sonnet 4.6 | 348 | 104 | $0.0026 |
| Analyzer | Haiku 4.5 | 136 | 60 | $0.0003 |
| Synthesizer | Sonnet 4.6 | 857 | 2,329 | $0.0375 |
| **Total** | | **1,341** | **2,493** | **$0.040** |

Key optimizations: schema summaries (not raw data) sent to LLM, batched sentiment classification routed to Haiku 4.5 (1 call for all notes, ~4x cheaper than Sonnet), concise role-specific system prompts, deterministic pre-filtering before LLM reasoning. At production scale: enable prompt caching, use Batch API for scheduled runs.
