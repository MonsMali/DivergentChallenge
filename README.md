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

# Run the copilot (interactive mode -- recommended)
python -m src.cli chat

# Or run a single query
python -m src.cli ask "Which deals should I focus on this week?"

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
+----------+    Deterministic: Google Drive download, CSV parsing,
| INGESTER |    data merging via joins, call note matching by company name,
+----+-----+    data quality flagging. No LLM involved.
     |          Output: list[EnrichedDeal] + DataQualityReport
     v
+----------+    LLM (Sonnet 4.6): receives query + schema summary
| PLANNER  |    (column names, row counts, value ranges -- not raw data).
+----+-----+    Output: AnalysisPlan (JSON) with analysis type + deal filter.
     |
     v
+----------+    Hybrid: deterministic risk scoring via weighted formula
| ANALYZER |    (contact recency, meetings, emails, probability, data quality).
+----+-----+    LLM (Haiku 4.5): batched sentiment classification of call notes.
     |          Output: deals with risk_score + sentiment attached.
     v
+-------------+  LLM (Sonnet 4.6): receives scored deals + query + today's date.
| SYNTHESIZER |  Generates prioritized, actionable recommendations with
+-------------+  named deals, dollar amounts, and concrete next steps.
```

---

## AI Tools and Frameworks Used

| Tool | Purpose | Why This Choice |
|------|---------|-----------------|
| **anthropic SDK** | Direct API access to Claude Sonnet 4.6 and Haiku 4.5 | The workflow has exactly 3 LLM calls per query. A thin wrapper is cleaner and more transparent than LangChain/LlamaIndex, which add framework overhead without value for this use case. Sonnet handles planning and synthesis; Haiku handles sentiment classification. |
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

Each query costs approximately **$0.035-0.045** with Claude Sonnet 4.6 (planner + synthesizer) and Haiku 4.5 (analyzer):

| Step | Model | Avg Input Tokens | Avg Output Tokens | Avg Cost |
|------|-------|-----------------|-------------------|----------|
| Planner | Sonnet 4.6 | ~348 | ~104 | $0.0026 |
| Analyzer (sentiment) | Haiku 4.5 | ~136 | ~60 | $0.0003 |
| Synthesizer | Sonnet 4.6 | ~857 | ~2,329 | $0.0375 |
| **Total per query** | | **~1,341** | **~2,493** | **~$0.040** |

The synthesizer dominates cost (93%) because it produces the longest, most detailed output. The analyzer uses Haiku 4.5 for sentiment classification -- a simple task that doesn't require a frontier model, reducing its cost by ~4x compared to routing through Sonnet.

### Optimization Strategies Implemented

1. **Schema summaries, not raw data.** The planner receives column names, value ranges, and deal counts rather than full DataFrames. For 5 rows this saves ~200 tokens; at 10,000 rows this is the difference between $0.01 and $5.00 per query.

2. **Batched sentiment classification.** All 5 call notes are sent in a single LLM call (~136 input tokens) rather than 5 separate calls (which would cost ~5x in per-request overhead and system prompt repetition).

3. **Concise, role-specific system prompts.** Each pipeline step gets a minimal system prompt scoped to its job. The planner prompt is 80 tokens; the synthesizer prompt is 120 tokens. No "you are a helpful assistant" padding.

4. **Deterministic pre-filtering.** Risk scores and data quality flags are computed before any LLM call. The LLM reasons over pre-scored, pre-filtered data rather than raw numbers.

### Production-Scale Strategies (Not Implemented)

- **Route more tasks to Haiku**: Sentiment classification already uses Haiku 4.5. At scale, query planning could also be routed to Haiku for further cost reduction.
- **Prompt caching**: System prompts are identical across queries. Anthropic's prompt caching feature would eliminate re-processing ~200 tokens of system prompt per call.
- **Batch API**: For non-interactive runs (e.g., daily scheduled analysis), the Anthropic Batch API offers 50% cost reduction with 24-hour turnaround.

### Data Considerations

The synthesizer receives today's date and reasons about close dates relative to when the system is run (e.g., flagging overdue deals). Contact recency (`last_contact_days`) is a static integer field in the dataset, not computed from activity timestamps. In a production system, this would be derived from actual CRM activity dates so it stays current automatically.

---

## Example Inputs and Outputs

Full examples with pipeline output are in the `examples/` directory:

- [`example_4_chat.md`](examples/example_4_chat.md) - **Interactive chat session with two queries (recommended starting point)**
- [`example_1_focus.md`](examples/example_1_focus.md) - "Which deals should I focus on this week?"
- [`example_2_risk.md`](examples/example_2_risk.md) - "What deals look at risk?"
- [`example_3_weekly.md`](examples/example_3_weekly.md) - "What actions should we take this week?"

### Quick Demo

The fastest way to see the system in action is `python -m src.cli chat`. Data loads once from Google Drive, then you can ask multiple questions:

```
  ✓ 5 deals loaded from Google Drive
╭──────────────── RevOps Copilot ─────────────────╮
│ 5 deals loaded — 2 complete, 3 with gaps        │
│ Type exit to quit                                │
╰─────────────────────────────────────────────────╯

> Which deals should I focus on this week?

╭──────────────── Recommendation ─────────────────╮
│                                                  │
│  PRIORITY 1 — Beta Ltd ($120K) - Sarah           │
│  Close date April 10 (9 days). Send redlined     │
│  contract today, schedule live call by Apr 3,    │
│  confirm signature path by Apr 7.                │
│                                                  │
│  PRIORITY 2 — Acme Corp ($50K) - John            │
│  Budget concerns + 10-day silence. Call today,   │
│  address budget head-on with phased payment or   │
│  reduced scope option.                           │
│                                                  │
│  ...                                             │
╰─────────────────────────────────────────────────╯

> What's the total pipeline value at risk?
  ...
```

---

## Future Feature Ideas

### 1. Cross-Portfolio Intelligence

Extend the system to analyze deals across multiple portfolio companies simultaneously, surfacing patterns and benchmarks that no single-company view can reveal:
- "SaaS portfolio companies close 40% faster when they have 3+ meetings before Proposal stage"
- "Your EU deals have a 2x longer sales cycle than US deals -- adjust close date expectations"
- "Three portfolio companies have stale pipelines this week -- here are the common patterns"

**Business value:** Portfolio-level insight is the PE fund's core competitive advantage. Individual company RevOps is useful; cross-company pattern recognition across a fund's holdings is strategic intelligence that informs both operational support and investment decisions.

### 2. CRM Write-back via MCP (Model Context Protocol)

Extend the system from read-only to bidirectional. Connect to Salesforce/HubSpot via MCP to:
- Auto-create follow-up tasks based on recommendations
- Update deal stages when analysis suggests progression or regression
- Log recommended actions directly in the CRM activity feed

**Business value:** Closes the loop between insight and action. Reduces manual data entry and ensures recommendations are acted on, not just read.
