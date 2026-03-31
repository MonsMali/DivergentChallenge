# Example 2: Risk Assessment

**Query:** `"What deals look at risk?"`

**Command:** `python -m src.cli ask "What deals look at risk?" --verbose`

*Output captured on March 31, 2026. Date-relative language in the synthesis reflects that run date.*

---

## Pipeline Steps (Verbose Output)

```
--- Data source: local ---

--- Ingester: 5 deals loaded ---
  Complete: 2
  Incomplete: 3
  Orphaned companies: ['Unknown Co']
  Missing fields: {'stage': 1, 'close_date': 1}

--- Planner ---
  Analysis type: risk
  Relevant deals: all
  Reasoning: Analyzing all deals to identify risk indicators such as low probability,
  data quality issues, stale contacts, and stage progression concerns.

--- Analyzer ---
  Deal #1 (Acme Corp): risk=0.25, sentiment=cautious
  Deal #2 (Beta Ltd): risk=0.067, sentiment=positive
  Deal #3 (Delta Inc): risk=0.707, sentiment=unclear
  Deal #4 (Omega SA): risk=0.61, sentiment=neutral
  Deal #5 (Unknown Co): risk=1.0, sentiment=neutral
```

---

## System Output

### DEALS AT RISK - PRIORITY RANKING

Based on the data, **3 of 5 deals are at significant risk**, representing $150K in pipeline jeopardy.

---

#### CRITICAL RISK - IMMEDIATE ACTION REQUIRED

**#1: Delta Inc - $30K (Risk Score: 0.707)**
- **Issues:** 25 days since last contact, unclear use case, only 1 meeting
- **Actions for John:**
  - Call Delta Inc **by Friday** to re-engage and clarify their specific use case
  - Schedule discovery call within 7 days or mark deal as dead
  - If they respond, focus on quantifying their pain points with concrete examples

**#2: Unknown Co - $45K (Risk Score: 1.0)**
- **Issues:** Missing stage, missing close date, 40 days stale, zero meetings, no account match
- **Actions for Sarah:**
  - **Close this deal as lost immediately** - it's been abandoned for 40+ days
  - Audit similar deals in your pipeline for data integrity issues
  - If there's genuine opportunity, treat as new lead and restart qualification process

---

#### MODERATE RISK - ACTION WITHIN 1 WEEK

**#3: Omega SA - $75K (Risk Score: 0.61)**
- **Issues:** 15 days since contact, zero meetings scheduled, expecting long sales cycle
- **Actions for Mike:**
  - Schedule face-to-face or video meeting **within 5 business days**
  - Address the "long sales cycle" concern head-on - propose pilot program
  - Set clear next steps with defined timeline before April 20th close date

---

#### MONITORING REQUIRED

**#4: Acme Corp - $50K (Risk Score: 0.25)**
- **Issues:** Budget concerns noted, moderate engagement
- **Actions for John:**
  - Address budget concerns within 2 weeks by presenting ROI calculator
  - Schedule follow-up meeting to discuss budget-friendly options before April 15th

---

### IMMEDIATE PIPELINE ACTIONS (This Week):
1. **Sarah:** Close Unknown Co deal as lost today
2. **John:** Call Delta Inc by Friday or lose the deal
3. **Mike:** Book meeting with Omega SA by next Wednesday
4. **Pipeline cleanup:** Remove stale deals >30 days without clear next steps

**Total at-risk revenue:** $150K (Delta + Unknown + Omega)
**Recoverable with immediate action:** $105K (Delta + Omega)

---

## Token Usage Summary

| Step | Input Tokens | Output Tokens | Cost |
|------|-------------|---------------|------|
| Planner | 345 | 68 | $0.002055 |
| Analyzer | 136 | 55 | $0.001233 |
| Synthesizer | 831 | 656 | $0.012333 |
| **Total** | **1,312** | **779** | **$0.015621** |

Model: `claude-sonnet-4-20250514`
