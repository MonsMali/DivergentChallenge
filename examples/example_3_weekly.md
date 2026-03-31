# Example 3: Weekly Action Plan

**Query:** `"What actions should we take this week?"`

**Command:** `python -m src.cli ask "What actions should we take this week?" --verbose`

*Output captured on March 31, 2026. Date-relative language in the synthesis reflects that run date.*

---

## Pipeline Steps (Verbose Output)

```
  ✓ 5 deals loaded from Google Drive

--- Planner ---
  Type: actions
  Deals: all
  Reasoning: Need to analyze all deals to identify actionable items for this week
  including data quality issues, upcoming close dates, and stage-appropriate next steps.

--- Analyzer ---
  #1 Acme Corp: risk=0.25 sentiment=cautious
  #2 Beta Ltd: risk=0.067 sentiment=positive
  #3 Delta Inc: risk=0.707 sentiment=unclear
  #4 Omega SA: risk=0.61 sentiment=neutral
  #5 Unknown Co: risk=1.0 sentiment=neutral
```

---

## System Output

### Priority Ranking (By Adjusted Business Impact)

1. **Beta Ltd** - $96K adjusted value ($120K x 0.8 prob)
2. **Acme Corp** - $30K adjusted value ($50K x 0.6 prob)
3. **Omega SA** - $37.5K adjusted value ($75K x 0.5 prob)
4. **Delta Inc** - $9K adjusted value ($30K x 0.3 prob)
5. **Unknown Co** - $18K adjusted value ($45K x 0.4 prob)

### Immediate Actions This Week

#### PRIORITY 1: Beta Ltd ($120K) - Sarah
**Action:** Schedule contract review meeting by Wednesday
- **Why:** Closes April 10th with 80% probability and positive sentiment
- **Next steps:** Sarah should send contract draft today and propose 2 meeting slots for stakeholder review
- **Risk mitigation:** With only 8 days to close, any delays kill the deal

#### PRIORITY 2: Acme Corp ($50K) - John
**Action:** Address budget concerns with ROI presentation by Thursday
- **Why:** 10 days since last contact with "budget concerns" noted
- **Next steps:** John should prepare cost-benefit analysis showing 6-month payback and schedule decision-maker call
- **Timeline:** If no positive response by April 4th, this deal likely slips to Q2

#### PRIORITY 3: Omega SA ($75K) - Mike
**Action:** Mike must make contact this Tuesday
- **Why:** 15 days stale contact with NO meetings held yet - highest relationship risk
- **Next steps:** Schedule discovery call immediately, or reassign if Mike is unavailable
- **Data issue:** Zero meetings after 15 days indicates poor qualification

#### PRIORITY 4: Unknown Co ($45K) - Sarah
**Action:** Sarah should audit and update deal by Wednesday
- **Why:** Missing critical data (stage, close date, industry) makes this unworkable
- **Next steps:** Either complete deal profile or mark as dead/inactive
- **40-day stale contact:** If no response to outreach, archive the deal

#### PRIORITY 5: Delta Inc ($30K) - John
**Action:** Re-engage by Friday or deprioritize
- **Why:** 25 days stale with unclear use case and high risk score (0.707)
- **Next steps:** One final value-focused email; if no response, move to nurture sequence

### Critical Data Quality Actions
- **Mike:** Needs CRM hygiene training - zero meetings on active $75K deal
- **Sarah:** Must resolve Unknown Co data gaps immediately
- **John:** Should update Delta Inc contact frequency or adjust probability down

**Key insight:** Beta Ltd represents 43% of this week's potential revenue and needs immediate attention to ensure April 10th close.

---

## Token Usage Summary

| Step | Input Tokens | Output Tokens | Cost |
|------|-------------|---------------|------|
| Planner | 347 | 71 | $0.002106 |
| Analyzer | 136 | 55 | $0.001233 |
| Synthesizer | 836 | 681 | $0.012723 |
| **Total** | **1,319** | **807** | **$0.016062** |

Model: `claude-sonnet-4-20250514`
