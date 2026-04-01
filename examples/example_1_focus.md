# Example 1: Deal Focus Prioritization

**Query:** `"Which deals should I focus on this week?"`

**Command:** `python -m src.cli ask "Which deals should I focus on this week?" --verbose`

*Output captured on April 1, 2026.*

---

## Pipeline Steps (Verbose Output)

```
  ✓ 5 deals loaded from Google Drive

--- Planner ---
  Type: priority
  Deals: all
  Reasoning: Need to analyze all deals to prioritize based on close dates,
  stages, probabilities, and data quality issues to determine weekly focus.

--- Analyzer ---
  #1 Acme Corp: risk=0.25 sentiment=cautious
  #2 Beta Ltd: risk=0.067 sentiment=positive
  #3 Delta Inc: risk=0.707 sentiment=unclear
  #4 Omega SA: risk=0.61 sentiment=neutral
  #5 Unknown Co: risk=1.0 sentiment=neutral
```

---

## System Output

# Weekly Deal Focus Prioritization

## Priority Ranking by Business Impact

1. **Beta Ltd - $120,000** (Expected value: $96K)
2. **Acme Corp - $50,000** (Expected value: $30K)
3. **Omega SA - $75,000** (Expected value: $37.5K)
4. **Delta Inc - $30,000** (Expected value: $9K)
5. **Unknown Co - $45,000** (Expected value: $18K)

## Specific Actions by Deal

### IMMEDIATE PRIORITY: Beta Ltd ($120,000)
**Owner: Sarah | Close: April 10 (5 days out)**
- **This Week Actions:**
  - Schedule contract review meeting by Wednesday 4/5
  - Prepare final pricing concessions (budget max 5% discount = $6K)
  - Get legal review started Monday 4/3
  - Daily check-ins with Sarah through close date
- **Why Critical:** 80% probability, positive sentiment, closes in 5 days, highest revenue impact

### HIGH PRIORITY: Acme Corp ($50,000)
**Owner: John | Close: April 15 (10 days out)**
- **This Week Actions:**
  - John must reconnect by Tuesday 4/4 (10-day gap is dangerous)
  - Address budget concerns with ROI calculator/case study
  - Propose payment plan options to overcome budget objection
  - Schedule stakeholder meeting to advance from Proposal stage
- **Why Important:** Decent probability (60%), manageable risk, closes soon

### RECOVERY NEEDED: Omega SA ($75,000)
**Owner: Mike | Data Quality Issues**
- **This Week Actions:**
  - Mike needs immediate outreach - 15 days silent is critical
  - **Red flag:** Zero meetings scheduled despite $75K opportunity
  - Book discovery call by Thursday 4/6 or risk losing deal
  - Update CRM with proper contact cadence plan
- **Data Issue:** High risk score (0.61) + no meetings = process breakdown

### RE-ENGAGEMENT: Delta Inc ($30,000)
**Owner: John | 25 Days Stale**
- **This Week Actions:**
  - John must call by Wednesday 4/5 (stale_contact flag critical)
  - Qualify use case properly - "unclear use case" needs resolution
  - Either advance to Proposal or disqualify by Friday 4/7
  - Don't let this drift further into May

### DATA CLEANUP: Unknown Co ($45,000)
**Owner: Sarah | Multiple Missing Fields**
- **This Week Actions:**
  - Sarah must update: Stage, Close Date, Industry, Region by Tuesday 4/4
  - 40-day contact gap requires immediate phone call Monday 4/3
  - If no response by Friday 4/7, move to "Lost" status
  - **Critical:** 1.0 risk score indicates deal may already be dead

## Weekly Revenue at Risk
- **High Confidence Close:** $96K (Beta Ltd)
- **Medium Risk:** $67.5K (Acme + Omega combined expected value)
- **Data Quality Issues:** $63K (Unknown Co + Delta Inc)

**Recommendation:** Focus 60% of time on Beta Ltd close, 30% on Acme budget resolution, 10% on data cleanup for the remaining deals.

---

## Token Usage Summary

| Step | Input Tokens | Output Tokens | Cost |
|------|-------------|---------------|------|
| Planner | 348 | 69 | $0.002079 |
| Analyzer | 136 | 55 | $0.001233 |
| Synthesizer | 835 | 813 | $0.014700 |
| **Total** | **1,319** | **937** | **$0.018012** |

Model: `claude-sonnet-4-20250514`
