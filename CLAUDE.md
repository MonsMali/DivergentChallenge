# CLAUDE.md - RevOps Copilot | Divergent Investments Technical Challenge

## Project Overview

A Python CLI application that acts as a **RevOps Copilot** for a Private Equity portfolio company. It ingests fragmented operational data (CSVs, text files), structures it, and allows users to ask natural language business questions like "which deals should I focus on?", "what looks at risk?", or "what actions should we take this week?". The system produces **actionable outputs**, not just summaries.

This is a technical challenge for the Agentic AI Engineer role at Divergent Investments.

## Architecture

The system is a **multi-step agentic pipeline** with four distinct stages. Each stage has a clear responsibility and a deliberate choice between deterministic logic and LLM reasoning.

```
User Query
    │
    ▼
┌──────────┐    Deterministic: Google Drive download (or local fallback),
│ INGESTER │    file I/O, parsing, normalization,
└────┬─────┘    join call_notes to deals via company name matching.
└────┬─────┘    Outputs: structured DataFrames + data quality metadata.
     │
     ▼
┌──────────┐    LLM (Claude Sonnet): receives user query + data schema summary
│ PLANNER  │    (column names, row counts, sample values, quality flags).
└────┬─────┘    Outputs: structured JSON analysis plan.
     │
     ▼
┌──────────┐    Hybrid: deterministic for filtering, aggregation, scoring,
│ ANALYZER │    joins. LLM for interpreting free-text notes, classifying
└────┬─────┘    deal sentiment, extracting insights from unstructured fields.
     │          Outputs: enriched deal data with risk scores and classifications.
     ▼
┌─────────────┐  LLM (Claude Sonnet): takes structured analysis output and
│ SYNTHESIZER │  generates prioritized, actionable recommendations with
└─────────────┘  specific next steps, not generic summaries.
```

## Tech Stack

- **Python 3.11+**
- **click** or **typer** for CLI
- **pandas** for data manipulation
- **anthropic** SDK (Claude Sonnet 4 for planning/synthesis)
- **pydantic** for data models between pipeline steps
- **google-api-python-client** + **google-auth** for Google Drive integration (primary data source)
- Local file fallback for development/testing

## Project Structure

```
revops-copilot/
├── CLAUDE.md
├── README.md
├── pyproject.toml          # or requirements.txt
├── data/                   # local fallback for dev/testing only (NOT the primary source)
│   ├── accounts.csv
│   ├── deals.csv
│   ├── activities.csv
│   └── call_notes.txt
├── src/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point (click/typer)
│   ├── config.py           # settings, API keys via env vars
│   ├── models.py           # pydantic models for inter-step data
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── gdrive.py       # Google Drive: auth, list files, download to temp dir
│   │   └── local.py        # local directory loader (dev fallback)
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── ingester.py     # deterministic: load, parse, normalize, join
│   │   ├── planner.py      # LLM: query understanding, plan generation
│   │   ├── analyzer.py     # hybrid: deterministic scoring + LLM classification
│   │   └── synthesizer.py  # LLM: actionable output generation
│   ├── orchestrator.py     # runs the pipeline steps in sequence
│   └── llm.py              # thin wrapper around anthropic SDK, token tracking
├── tests/
│   ├── test_ingester.py
│   ├── test_analyzer.py
│   └── test_pipeline.py
└── examples/               # 2-3 example inputs/outputs (required deliverable)
    ├── example_1_focus.md
    ├── example_2_risk.md
    └── example_3_weekly.md
```

## Data Context

The dataset is intentionally small (5 deals, 4 accounts, 5 activity rows, 5 call notes). This is NOT a scale test. The evaluators will focus on architecture quality, orchestration clarity, and output usefulness.

### Key data characteristics to handle:

- **Deal 5 (Unknown Co)**: missing stage, missing close_date, no matching account in accounts.csv. Handle gracefully -- flag as incomplete, do not crash or silently ignore.
- **Deal 3 (Delta Inc)**: 25 days since last contact, 1 meeting only, call note says "early stage, unclear use case". This is the obvious at-risk deal.
- **Deal 2 (Beta Ltd)**: 2 days since contact, 5 meetings, 12 email threads, 0.8 probability, call note says "strong interest, pushing for fast close". This is the top priority.
- **call_notes.txt**: unstructured, no deal_id. Must join to deals via company name matching. This is a deliberate design choice to highlight in the README.

### Data files:

**accounts.csv**: company, industry, employees, region
**deals.csv**: deal_id, company, stage, amount, owner, close_date, probability
**activities.csv**: deal_id, last_contact_days, meetings, email_threads
**call_notes.txt**: one-liner notes per company, format "Company: note text"

## Design Principles

1. **Deterministic where possible, LLM where necessary.** File parsing, joins, numeric scoring, filtering = deterministic. Interpreting free-text notes, understanding user intent, generating recommendations = LLM. Always justify the boundary.

2. **Structured data between steps.** Use pydantic models so each pipeline step has typed inputs/outputs. This makes the orchestration explicit and testable.

3. **Graceful degradation with incomplete data.** Never crash on missing fields. Flag data quality issues and still produce useful output. The system should tell the user "Deal 5 has incomplete data (missing stage, close date, no account match)" rather than dropping it.

4. **Actionable outputs, not summaries.** Bad: "Deal 3 is at risk." Good: "Deal 3 (Delta Inc, $30k) has had no contact in 25 days and only 1 meeting. The call note indicates an unclear use case. Recommended action: schedule a discovery call this week to clarify their needs and assess whether to continue pursuing."

5. **Token efficiency.** Send schema summaries to the LLM, not raw data dumps. Log token usage per step. Mention in README that at production scale you would route classification to Haiku and reserve Sonnet for complex reasoning.

## Token Usage & Cost Optimization

This is an explicit deliverable. The README must include a dedicated section, and the code must support it with real numbers.

### In the code:
- Wrap every Anthropic API call in a helper (`llm.py`) that logs `input_tokens`, `output_tokens`, and estimated cost per call.
- At the end of each query, print a **token usage summary**: total tokens per pipeline step, total cost, model used per step.
- Store usage data in a structured format (dict/pydantic model) so it can be included in verbose output.

### Optimization strategies to implement and document:
1. **Schema summaries, not raw data.** Send column names, row counts, dtypes, and a 2-row sample to the LLM, not the full DataFrame. For 5 rows this does not matter, but explain that at 10k+ rows this is the difference between pennies and dollars.
2. **Concise, role-specific system prompts.** Each pipeline step gets a minimal system prompt scoped to its job. No bloated "you are a helpful assistant" preamble.
3. **Deterministic pre-filtering.** The analyzer does numeric filtering/scoring before calling the LLM, so the LLM only reasons over relevant deals, not the full dataset.
4. **Mention (in README) production-scale strategies:** routing classification tasks to Haiku, prompt caching for repeated system prompts, batching multiple deal analyses into a single LLM call.

- Use `anthropic` Python SDK directly
- Model: `claude-sonnet-4-20250514` for planning and synthesis
- API key via `ANTHROPIC_API_KEY` environment variable
- **Token tracking**: wrap every API call to log input/output tokens and cost. Print a summary at the end of each query.
- System prompts should be concise and role-specific per step (planner system prompt != synthesizer system prompt)

## CLI Interface

```bash
# Primary: fetch from Google Drive (folder ID from the challenge dataset)
python -m src.cli ask "Which deals should I focus on this week?" --source gdrive --folder-id 1CjyUQgtfl0AKEXBhkS7pxuEEs1UWn1ud

# Fallback: local files for dev/testing
python -m src.cli ask "What looks at risk?" --source local --data-dir ./data

# Show pipeline details (verbose mode)
python -m src.cli ask "What actions should we take?" --verbose

# Data summary / health check
python -m src.cli status
```

## Google Drive Integration

- Use `google-api-python-client` with a **service account** (simpler for CLI tools, no browser OAuth flow needed).
- The ingester downloads all files from the specified Drive folder to a temp directory, then processes them.
- The ingester itself is source-agnostic: it receives a directory path regardless of whether files came from Drive or local disk.
- Credentials via `GOOGLE_SERVICE_ACCOUNT_JSON` env var or a `credentials.json` file.
- README must include clear setup instructions for creating a GCP project, enabling Drive API, and creating a service account.

## Deliverables Checklist

- [ ] Working Python CLI application
- [ ] README.md with:
  - [ ] Setup instructions
  - [ ] Architecture description
  - [ ] AI tools/frameworks used and why
  - [ ] System structure explanation
  - [ ] Orchestration approach
  - [ ] Deterministic vs LLM boundary decisions (with reasoning)
  - [ ] External data source integration (Google Drive as primary, local fallback)
  - [ ] Token usage and cost considerations
- [ ] 2-3 example inputs/outputs in examples/ directory
- [ ] 2 ideas for new features

## Feature Ideas (for README)

1. **Scheduled Monitoring & Alerts**: run the pipeline daily on a cron, diff against previous state, push alerts (Slack/email) when deals go cold, pipeline velocity drops, or close dates approach with low probability.

2. **CRM Write-back via MCP**: instead of just reading data, use MCP (Model Context Protocol) to connect bidirectionally with the CRM. The copilot could auto-create follow-up tasks, update deal stages, or log recommended actions directly back into Salesforce/HubSpot.

## Code Style

- Type hints everywhere
- Docstrings on public functions
- No print statements for user output -- use click.echo or a logger
- Keep functions small and single-purpose
- No over-engineering: no embeddings, no vector DB, no RAG for 5 rows of data