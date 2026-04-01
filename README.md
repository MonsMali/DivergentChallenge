# RevOps Copilot

A Python CLI application that acts as a RevOps Copilot for Private Equity portfolio companies. It ingests fragmented operational data (CSVs, text files), structures it, and lets users ask natural language business questions like *"Which deals should I focus on?"*, *"What looks at risk?"*, or *"What actions should we take this week?"*. The system produces actionable recommendations with specific next steps, not generic summaries.

Built as a technical challenge for the Agentic AI Engineer role at Divergent Investments.

---

For a detailed explanation of the architecture, workflow, tools used, and cost optimization, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Setup Instructions

### Prerequisites

- Python 3.11+ (tested on 3.12)
- An Anthropic API key ([get one here](https://console.anthropic.com/))
- Google Cloud service account with Drive API access (see step 2 below)

### 1. Install

```bash
git clone https://github.com/MonsMali/DivergentChallenge.git
cd DivergentChallenge

python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

pip install -e .
```

### 2. Configure Google Drive Credentials

The app connects to Google Drive to ingest the challenge dataset. To set this up:

1. Create a GCP project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable the **Google Drive API** (APIs & Services > Library > search "Google Drive API")
3. Create a **service account** (IAM & Admin > Service Accounts > Create)
4. Download the JSON credentials file and save it as `credentials.json` in the project root
5. Share the [challenge Drive folder](https://drive.google.com/drive/folders/1CjyUQgtfl0AKEXBhkS7pxuEEs1UWn1ud) with the service account email (e.g., `revops@your-project.iam.gserviceaccount.com`)

Alternatively, paste the full JSON content into the `GOOGLE_SERVICE_ACCOUNT_JSON` variable in `.env` (useful for CI/CD).

### 3. Set API Key and Run

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# Interactive mode (recommended) -- loads data once, ask multiple questions
python -m src.cli chat

# Single query
python -m src.cli ask "Which deals should I focus on this week?"

# Health check -- no API key needed, shows data quality summary
python -m src.cli status
```

To use a different Drive folder: `python -m src.cli ask "..." --folder-id YOUR_FOLDER_ID`

---

## Project Structure

```
DivergentChallenge/
├── pyproject.toml
├── .env.example
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
    ├── example_3_weekly.md
    └── example_4_interactive_session.md
```

---

## Example Inputs and Outputs

Full examples with pipeline output are in the `examples/` directory:

- [`example_4_interactive_session.md`](examples/example_4_interactive_session.md) - **Interactive chat session with 10 queries (recommended starting point)**
- [`example_1_focus.md`](examples/example_1_focus.md) - "Which deals should I focus on this week?"
- [`example_2_risk.md`](examples/example_2_risk.md) - "What deals look at risk?"
- [`example_3_weekly.md`](examples/example_3_weekly.md) - "What actions should we take this week?"

### Quick Demo

The fastest way to see the system in action is `python -m src.cli chat`. Data loads once from Google Drive, then you can ask multiple questions:

```
  ✓ 5 deals loaded from Google Drive
╭──────────────── RevOps Copilot ─────────────────╮
│ 5 deals loaded — 2 complete, 3 with gaps        │
│ Type exit to quit                               │
╰─────────────────────────────────────────────────╯

> Which deals should I focus on this week?

╭──────────────── Recommendation ─────────────────╮
│                                                 │
│  PRIORITY 1 — Beta Ltd ($120K) - Sarah          │
│  Close date April 10 (9 days). Send redlined    │
│  contract today, schedule live call by Apr 3,   │
│  confirm signature path by Apr 7.               │
│                                                 │
│  PRIORITY 2 — Acme Corp ($50K) - John           │
│  Budget concerns + 10-day silence. Call today,  │
│  address budget head-on with phased payment or  │
│  reduced scope option.                          │
│                                                 │
│  ...                                            │
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
