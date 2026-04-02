# Architecture, Workflow and Tools

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
+----------+    LLM (Haiku 4.5): receives query + schema summary (not raw data).
| PLANNER  |    Output: AnalysisPlan (JSON) with analysis type + reasoning.
+----+-----+
     |
     v
+----------+    Hybrid: deterministic risk scoring (weighted formula) +
| ANALYZER |    LLM sentiment classification (batched, single call).
+----+-----+    Output: deals scored, sorted by analysis_type, filtered
     |          by filters_to_apply from the planner.
     |
     v
+-------------+  LLM (Sonnet 4.6): generates prioritized, actionable recommendations
| SYNTHESIZER |  with specific deals, dollar amounts, and next steps.
+-------------+  Output: natural language advisory text.
```

## AI Tools and Frameworks Used

| Tool | Purpose | Why This Choice |
|------|---------|-----------------|
| **anthropic SDK** | Direct API access to Claude Sonnet 4.6 and Haiku 4.5 | The workflow has exactly 3 LLM calls per query. A thin wrapper is cleaner and more transparent than LangChain/LlamaIndex, which add framework overhead without value for this use case. Sonnet handles synthesis (complex reasoning + NL generation); Haiku handles planning and sentiment classification (structured JSON output, simple classification). |
| **pandas** | Data manipulation and merging | Standard, battle-tested library for tabular data. Handles CSV parsing, joins, and null value handling out of the box. |
| **pydantic** | Typed data contracts between pipeline steps | Ensures data integrity at each boundary. Makes the orchestration self-documenting and catches schema violations early. |
| **click** | CLI framework | Lightweight, well-documented, no magic. Supports commands, options, and flags with minimal boilerplate. |
| **rich** | Terminal formatting | Colored output, tables, panels, and progress spinners. Makes pipeline output readable and the demo experience sharper, with minimal code. |
| **google-api-python-client** | Google Drive integration | Official Google SDK for Drive API access. Uses service account auth for CLI/automation suitability. |

### Deliberately Not Used

- **No vector databases, no embeddings, no RAG.** The dataset is 5 deals. It fits entirely in an LLM context window. Using vector search here would be over-engineering and would demonstrate poor judgment about when to apply complex architectures.
- **No LangChain / LlamaIndex.** For 3 LLM calls with clear input/output contracts, a 40-line wrapper module (`llm.py`) is simpler, more debuggable, and has zero framework lock-in.
- **No agents framework.** The pipeline is linear and predictable. A ReAct loop or tool-use agent would add non-determinism without benefit.

## Orchestration

The pipeline follows a **linear sequential flow**: Ingester -> Planner -> Analyzer -> Synthesizer. Each step has typed input/output via pydantic models. The orchestrator (`orchestrator.py`) is a simple sequential runner that:

1. Resolves the data source (local directory or Google Drive download)
2. Runs the ingester to produce enriched deals and a quality report
3. Sends the query + schema summary to the planner for analysis planning
4. Runs the analyzer for deterministic scoring + LLM sentiment classification
5. Passes everything to the synthesizer for final recommendation generation
6. Collects token usage from all LLM steps into a structured summary

This is intentionally **not** a DAG or event-driven system. The workflow is linear: each step depends on the previous step's output. For a production system with multiple data sources, parallel analysis paths, or conditional branching, a DAG-based orchestrator (e.g., Prefect, Airflow) would be appropriate. For this use case, sequential execution is the simplest correct solution.

### Interactive Mode (chat command)

The `chat` command runs ingestion once on startup and caches the enriched deals in memory. Subsequent queries only execute the planner, analyzer, and synthesizer steps, avoiding redundant Drive API calls and file I/O. This means the first query pays the full cost (download + ingestion + 3 LLM calls), but every subsequent query only costs the 3 LLM calls (~$0.016 each) with no data loading overhead.

## Deterministic Logic vs LLMs

This is the most important architectural decision in the system. The principle: **use deterministic logic wherever the task has clear rules and structured inputs. Use LLMs where the task requires interpretation, reasoning over ambiguity, or natural language generation.**

| Step | Type | Why |
|------|------|-----|
| File I/O, CSV parsing | Deterministic | Structured data, no ambiguity. LLM adds cost and latency for zero benefit. |
| Data merging (joins on deal_id, company) | Deterministic | Exact-match keys, no interpretation needed. |
| Company name matching (call notes) | Deterministic | Case-insensitive string matching is sufficient for this dataset. At scale with fuzzy company names, an LLM or fuzzy matcher would be warranted. |
| Data quality flagging | Deterministic | Rule-based null checks, 100% reliable, zero cost, reproducible. |
| Risk scoring, sorting, filtering | Deterministic | Weighted numeric formula based on defined business rules. After scoring, deals are sorted by the planner's `analysis_type` (risk, priority, actions, general) and filtered by `filters_to_apply`. This is where the planner's output becomes load-bearing, it controls what the synthesizer sees. |
| Query understanding / planning | **LLM (Haiku)** | Natural language intent classification requires semantic understanding, but the output is structured JSON with 4 possible types. Simple enough for Haiku. |
| Call note sentiment analysis | **LLM (Haiku)** | Free-text interpretation. "Interested but budget concerns" requires nuanced classification that no rule-based approach handles reliably. |
| Final synthesis / recommendations | **LLM (Sonnet)** | Requires reasoning across multiple data points (scores, sentiment, quality flags, amounts, dates) and generating natural language advice tailored to the specific question. This is the only step that justifies a frontier model. |

The boundary is not about difficulty but about whether the task has a **single correct answer derivable from rules** (deterministic) or requires **interpretation and judgment** (LLM).

## External Data Source Integration

The source layer is **abstracted from the pipeline**. The ingester receives a directory path regardless of where files originated. The `sources/gdrive.py` module authenticates with Google Drive, downloads files to a temp directory, and returns the path. The ingester never knows (or needs to know) it's working with Drive data.

- Uses a **service account** (no browser OAuth flow) for CLI/automation suitability
- Files are downloaded to a `tempfile.mkdtemp()` directory, then passed to the ingester as a local path
- Error handling: graceful failures for auth issues, missing folders, empty folders

This pattern extends easily to other sources by adding new modules (`sources/s3.py`, `sources/sftp.py`, `sources/hubspot.py`). Each module only needs to implement a function that returns a directory path containing the expected files.

## Token Usage and Cost Optimization

### Actual Token Usage (from a 10-query interactive session)

Cost per query ranges from **$0.014 to $0.044** depending on output length, averaging **$0.029 per query**:

| Step | Model | Avg Input Tokens | Avg Output Tokens | Avg Cost |
|------|-------|-----------------|-------------------|----------|
| Planner | Haiku 4.5 | ~347 | ~77 | $0.0006 |
| Analyzer (sentiment) | Haiku 4.5 | ~132 | ~56 | $0.0003 |
| Synthesizer | Sonnet 4.6 | ~848 | ~1,550 | $0.0264 |
| **Total per query** | | **~1,327** | **~1,683** | **~$0.029** |

A full 10-query session cost **$0.29 total**. The synthesizer dominates cost (~91%) because it produces the longest, most detailed output. Broad queries ("Summarize everything") cost ~$0.04; focused queries ("Tell me about Delta Inc") cost ~$0.014. The analyzer uses Haiku 4.5 for sentiment classification -- a simple task that doesn't require a frontier model, reducing its cost by ~4x compared to routing through Sonnet.

### Optimization Strategies Implemented

1. **Schema summaries, not raw data.** The planner receives column names, value ranges, and deal counts rather than full DataFrames. For 5 rows this saves ~200 tokens; at 10,000 rows this is the difference between $0.01 and $5.00 per query.

2. **Batched sentiment classification.** All 5 call notes are sent in a single LLM call (~136 input tokens) rather than 5 separate calls (which would cost ~5x in per-request overhead and system prompt repetition).

3. **Concise, role-specific system prompts.** Each pipeline step gets a minimal system prompt scoped to its job. The planner prompt is 80 tokens; the synthesizer prompt is 120 tokens. No "you are a helpful assistant" padding.

4. **Deterministic pre-filtering.** Risk scores and data quality flags are computed before any LLM call. The LLM reasons over pre-scored, pre-filtered data rather than raw numbers.

### Production-Scale Strategies (Not Implemented)

- **Prompt caching**: System prompts are identical across queries. Anthropic's prompt caching feature would eliminate re-processing ~200 tokens of system prompt per call.
- **Batch API**: For non-interactive runs (e.g., daily scheduled analysis), the Anthropic Batch API offers 50% cost reduction with 24-hour turnaround.

### Data Considerations

The synthesizer receives today's date and reasons about close dates relative to when the system is run (e.g., flagging overdue deals). Contact recency (`last_contact_days`) is a static integer field in the dataset, not computed from activity timestamps. In a production system, this would be derived from actual CRM activity dates so it stays current automatically.
