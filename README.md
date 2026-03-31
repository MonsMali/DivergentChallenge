# RevOps Copilot

A Python CLI application that acts as a RevOps Copilot for Private Equity portfolio companies. It ingests fragmented operational data (CSVs, text files), structures it, and lets users ask natural language business questions like *"Which deals should I focus on?"*, *"What looks at risk?"*, or *"What actions should we take this week?"*. The system produces actionable recommendations with specific next steps, not generic summaries.

Built as a technical challenge for the Agentic AI Engineer role at Divergent Investments.

---

## Table of Contents

1. [Setup Instructions](#setup-instructions)
2. [System Architecture](#system-architecture)
3. [AI Tools and Frameworks Used](#ai-tools-and-frameworks-used)
4. [Orchestration](#orchestration)
5. [Deterministic Logic vs LLMs](#deterministic-logic-vs-llms)
6. [External Data Source Integration](#external-data-source-integration)
7. [Token Usage and Cost Optimization](#token-usage-and-cost-optimization)
8. [Example Inputs and Outputs](#example-inputs-and-outputs)
9. [Future Feature Ideas](#future-feature-ideas)

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- An Anthropic API key ([get one here](https://console.anthropic.com/))

### Quick Start

```bash
# Clone the repo
git clone https://github.com/MonsMali/DivergentChallenge.git
cd DivergentChallenge

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e .

# Configure API key and credentials
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# Single query mode
python -m src.cli ask "Which deals should I focus on this week?"

# Interactive copilot mode (ingests once, ask multiple questions)
python -m src.cli chat

# Health check (no API key needed)
python -m src.cli status
```

### Google Drive Setup

The system connects to Google Drive as its external data source. To configure:

1. **Create a GCP project** at [console.cloud.google.com](https://console.cloud.google.com)
2. **Enable the Google Drive API** (APIs & Services > Library > search "Google Drive API")
3. **Create a service account** (IAM & Admin > Service Accounts > Create)
4. **Download the JSON credentials** file and save as `credentials.json` in the project root
5. **Share the Drive folder** with the service account email (e.g., `revops@project.iam.gserviceaccount.com`)

The CLI defaults to the challenge dataset folder. To use a different folder:

```bash
python -m src.cli ask "What looks at risk?" \
  --folder-id YOUR_FOLDER_ID
```

Alternatively, set the `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable to the JSON string content.

---

## Project Structure

```
DivergentChallenge/
├── pyproject.toml
├── .env.example
├── data/                        # Local fallback data for dev/testing
│   ├── accounts.csv
│   ├── deals.csv
│   ├── activities.csv
│   └── call_notes.txt
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py                   # CLI entry point (click)
│   ├── config.py                # Settings, API keys via env vars
│   ├── llm.py                   # Thin wrapper around anthropic SDK, token tracking
│   ├── models.py                # Pydantic models for inter-step data
│   ├── orchestrator.py          # Runs pipeline steps in sequence
│   ├── sources/
│   │   └── gdrive.py            # Google Drive: auth, list, download
│   └── pipeline/
│       ├── ingester.py          # Deterministic: load, parse, normalize, join
│       ├── planner.py           # LLM: query understanding, plan generation
│       ├── analyzer.py          # Hybrid: deterministic scoring + LLM classification
│       └── synthesizer.py       # LLM: actionable output generation
├── tests/
│   ├── test_models.py
│   ├── test_ingester.py
│   └── test_analyzer.py
└── examples/
    ├── example_1_focus.md
    ├── example_2_risk.md
    └── example_3_weekly.md
```

---

## System Architecture

The system is a **multi-step agentic pipeline** with four distinct stages. Each stage has a clear responsibility and a deliberate choice between deterministic logic and LLM reasoning.

```
User Query
    |
    v
+----------+    Deterministic: Google Drive download (or local fallback),
| INGESTER |    file I/O, parsing, normalization,
+----+-----+    join call_notes to deals via company name matching.
     |          Outputs: structured DataFrames + data quality metadata.
     v
+----------+    LLM (Claude Sonnet): receives user query + data schema summary
| PLANNER  |    (column names, row counts, sample values, quality flags).
+----+-----+    Outputs: structured JSON analysis plan.
     |
     v
+----------+    Hybrid: deterministic for filtering, aggregation, scoring,
| ANALYZER |    joins. LLM for interpreting free-text notes, classifying
+----+-----+    deal sentiment, extracting insights from unstructured fields.
     |          Outputs: enriched deal data with risk scores and classifications.
     v
+-------------+  LLM (Claude Sonnet): takes structured analysis output and
| SYNTHESIZER |  generates prioritized, actionable recommendations with
+-------------+  specific next steps, not generic summaries.
```

### Step Details

- **Ingester** (deterministic): Loads CSVs and text files, merges deals with accounts and activities via joins, attaches call notes by company name matching, flags data quality issues. No LLM involved.

- **Planner** (LLM): Receives the user's natural language query plus a concise schema summary (not raw data). Produces a structured JSON analysis plan indicating which deals to focus on and what type of analysis to perform.

- **Analyzer** (hybrid): Computes deterministic risk scores using a weighted formula (contact recency, meeting count, email engagement, probability, data quality). Separately, sends all call notes to the LLM in a single batched call for sentiment classification.

- **Synthesizer** (LLM): Takes the full enriched deal data with scores and sentiment, plus the original query, and generates specific, actionable recommendations with named deals, dollar amounts, and concrete next steps.

---

## AI Tools and Frameworks Used

| Tool | Purpose | Why This Choice |
|------|---------|-----------------|
| **anthropic SDK** | Direct API access to Claude Sonnet 4 | The workflow has exactly 3 LLM calls per query. A thin wrapper is cleaner and more transparent than LangChain/LlamaIndex, which add framework overhead without value for this use case. |
| **pandas** | Data manipulation and merging | Standard, battle-tested library for tabular data. Handles CSV parsing, joins, and null value handling out of the box. |
| **pydantic** | Typed data contracts between pipeline steps | Ensures data integrity at each boundary. Makes the orchestration self-documenting and catches schema violations early. |
| **click** | CLI framework | Lightweight, well-documented, no magic. Supports commands, options, and flags with minimal boilerplate. |
| **rich** | Terminal formatting | Colored output, tables, panels, and progress spinners. Makes pipeline output readable and the demo experience sharper, with minimal code. |
| **google-api-python-client** | Google Drive integration | Official Google SDK for Drive API access. Uses service account auth for CLI/automation suitability. |

### Deliberately Not Used

- **No vector databases, no embeddings, no RAG.** The dataset is 5 deals. It fits entirely in an LLM context window. Using vector search here would be over-engineering and would demonstrate poor judgment about when to apply complex architectures.
- **No LangChain / LlamaIndex.** For 3 LLM calls with clear input/output contracts, a 40-line wrapper module (`llm.py`) is simpler, more debuggable, and has zero framework lock-in.
- **No agents framework.** The pipeline is linear and predictable. A ReAct loop or tool-use agent would add non-determinism without benefit.

---

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

---

## Deterministic Logic vs LLMs

This is the most important architectural decision in the system. The principle: **use deterministic logic wherever the task has clear rules and structured inputs. Use LLMs where the task requires interpretation, reasoning over ambiguity, or natural language generation.**

| Step | Type | Why |
|------|------|-----|
| File I/O, parsing, CSV loading | Deterministic | Structured data, no ambiguity. LLM adds cost and latency for zero benefit. |
| Data merging and joins | Deterministic | Exact-match joins on known keys (deal_id, company name). No interpretation needed. |
| Company name matching (call notes) | Deterministic | Case-insensitive string matching is sufficient for this dataset. At scale with fuzzy company names, an LLM or fuzzy matcher would be warranted. |
| Data quality flagging | Deterministic | Rule-based checks (null fields, missing matches). 100% reliable, zero cost, reproducible. |
| Risk scoring | Deterministic | Weighted numeric formula based on defined business rules. Reproducible, auditable, and explainable. |
| Query understanding / planning | **LLM** | Natural language intent classification requires semantic understanding. "What should I focus on?" vs "What's at risk?" require different analysis approaches. |
| Call note sentiment analysis | **LLM** | Free-text interpretation. "Interested but budget concerns" requires nuanced classification that no rule-based approach handles reliably. |
| Final synthesis / recommendations | **LLM** | Requires reasoning across multiple data points (scores, sentiment, quality flags, amounts, dates) and generating natural language advice tailored to the specific question. |

The boundary is not about difficulty but about whether the task has a **single correct answer derivable from rules** (deterministic) or requires **interpretation and judgment** (LLM).

---

## External Data Source Integration

### Architecture

The source layer is **abstracted from the pipeline**. The ingester receives a directory path regardless of where files originated. The `sources/gdrive.py` module authenticates with Google Drive, downloads files to a temp directory, and returns the path. The ingester never knows (or needs to know) it's working with Drive data.

### Google Drive Integration

- Uses a **service account** (no browser OAuth flow) for CLI/automation suitability
- Files are downloaded to a `tempfile.mkdtemp()` directory, then passed to the ingester as a local path
- Error handling: graceful failures for auth issues, missing folders, empty folders

### Extensibility

This pattern extends easily to other sources by adding new modules:
- `sources/s3.py` for AWS S3 buckets
- `sources/sftp.py` for SFTP servers
- `sources/hubspot.py` for direct CRM API exports

Each module only needs to implement a function that returns a directory path containing the expected files.

---

## Token Usage and Cost Optimization

### Actual Token Usage (from example runs)

Each query costs approximately **$0.015-0.017** with Claude Sonnet 4:

| Step | Avg Input Tokens | Avg Output Tokens | Avg Cost |
|------|-----------------|-------------------|----------|
| Planner | ~347 | ~71 | $0.0021 |
| Analyzer (sentiment) | ~136 | ~55 | $0.0012 |
| Synthesizer | ~836 | ~660 | $0.0124 |
| **Total per query** | **~1,319** | **~786** | **~$0.016** |

The synthesizer dominates cost (78%) because it produces the longest output. The planner and analyzer are highly efficient.

### Optimization Strategies Implemented

1. **Schema summaries, not raw data.** The planner receives column names, value ranges, and deal counts rather than full DataFrames. For 5 rows this saves ~200 tokens; at 10,000 rows this is the difference between $0.01 and $5.00 per query.

2. **Batched sentiment classification.** All 5 call notes are sent in a single LLM call (~136 input tokens) rather than 5 separate calls (which would cost ~5x in per-request overhead and system prompt repetition).

3. **Concise, role-specific system prompts.** Each pipeline step gets a minimal system prompt scoped to its job. The planner prompt is 80 tokens; the synthesizer prompt is 120 tokens. No "you are a helpful assistant" padding.

4. **Deterministic pre-filtering.** Risk scores and data quality flags are computed before any LLM call. The LLM reasons over pre-scored, pre-filtered data rather than raw numbers.

### Production-Scale Strategies (Not Implemented)

- **Route classification to Claude Haiku**: Sentiment classification is a simple task. At scale, routing it to Haiku ($0.25/MTok input vs $3/MTok for Sonnet) would reduce analyzer cost by 12x.
- **Prompt caching**: System prompts are identical across queries. Anthropic's prompt caching feature would eliminate re-processing ~200 tokens of system prompt per call.
- **Batch API**: For non-interactive runs (e.g., daily scheduled analysis), the Anthropic Batch API offers 50% cost reduction with 24-hour turnaround.

---

## Example Inputs and Outputs

Full examples with pipeline output are in the `examples/` directory:

- [`example_1_focus.md`](examples/example_1_focus.md) - "Which deals should I focus on this week?"
- [`example_2_risk.md`](examples/example_2_risk.md) - "What deals look at risk?"
- [`example_3_weekly.md`](examples/example_3_weekly.md) - "What actions should we take this week?"
- [`example_4_chat.md`](examples/example_4_chat.md) - Interactive chat session with two queries (demonstrates cached ingestion)

### Sample Output (abbreviated)

**Query:** *"Which deals should I focus on this week?"*

```
Priority 1: Beta Ltd ($120K) - Sarah
Schedule final contract review meeting by Wednesday. 80% probability, positive
sentiment, closes April 10th. Confirm pricing, get legal review started,
prepare DocuSign package.

Priority 2: Acme Corp ($50K) - John
Address budget concerns with ROI presentation by Thursday. 10-day silence on
deal with budget hesitation needs immediate attention.

Priority 5: Unknown Co ($45K) - Sarah
Data cleanup required before any sales action. Missing critical data (stage,
close date, account info). Spend 30 minutes updating CRM or mark as dead deal.
```

---

## Future Feature Ideas

### 1. Scheduled Monitoring and Alerts

Run the pipeline daily on a cron job, diff against previous state, and push alerts via Slack or email when:
- Deals go cold (contact gap exceeds threshold)
- Pipeline velocity drops below historical average
- Close dates approach with low probability

**Business value:** Proactive risk management instead of reactive querying. Sales managers get notified of problems before they become critical, reducing deal slippage.

### 2. CRM Write-back via MCP (Model Context Protocol)

Extend the system from read-only to bidirectional. Connect to Salesforce/HubSpot via MCP to:
- Auto-create follow-up tasks based on recommendations
- Update deal stages when analysis suggests progression or regression
- Log recommended actions directly in the CRM activity feed

**Business value:** Closes the loop between insight and action. Reduces manual data entry and ensures recommendations are acted on, not just read.
