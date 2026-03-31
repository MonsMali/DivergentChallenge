# Example 1: Deal Focus Prioritization

**Query:** `"Which deals should I focus on this week?"`

**Command:** `python -m src.cli ask "Which deals should I focus on this week?" --verbose`

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
  Analysis type: priority
  Relevant deals: all
  Reasoning: To determine which deals to focus on this week, I need to analyze all
  deals by priority considering factors like close dates, deal amounts, probabilities,
  and stages.

--- Analyzer ---
  Deal #1 (Acme Corp): risk=0.25, sentiment=cautious
  Deal #2 (Beta Ltd): risk=0.067, sentiment=positive
  Deal #3 (Delta Inc): risk=0.707, sentiment=unclear
  Deal #4 (Omega SA): risk=0.61, sentiment=neutral
  Deal #5 (Unknown Co): risk=1.0, sentiment=neutral
```

---

## System Output

### Priority Ranking for This Week

**Focus Order (by business impact & urgency):**

1. **Beta Ltd** - $120K deal (Expected Value: $96K)
2. **Acme Corp** - $50K deal (Expected Value: $30K)
3. **Omega SA** - $75K deal (Expected Value: $37.5K)
4. **Delta Inc** - $30K deal (Expected Value: $9K)
5. **Unknown Co** - $45K deal (Expected Value: $18K)

### Specific Actions Required

#### IMMEDIATE (This Week)

**Beta Ltd ($120,000)** - Sarah
- **Action**: Schedule final contract review meeting by Wednesday
- **Why**: 80% probability, positive sentiment, closes April 10th (6 days)
- **Risk**: Minimal (0.067 score) but fast close timeline creates execution risk
- **Next steps**: Confirm pricing, get legal review started, prepare DocuSign package

**Acme Corp ($50,000)** - John
- **Action**: Address budget concerns with ROI presentation by Thursday
- **Why**: 10-day silence on $50K deal with budget hesitation needs immediate attention
- **Risk**: Moderate (0.25 score), cautious sentiment suggests price sensitivity
- **Next steps**: Prepare cost-benefit analysis, explore payment terms options

#### SECONDARY PRIORITY

**Omega SA ($75,000)** - Mike
- **Action**: Mike must schedule discovery call this week (15-day gap is critical)
- **Why**: High value but zero meetings completed, stale contact flagged
- **Risk**: High (0.61 score) due to no face-to-face engagement

#### LOWER PRIORITY

**Delta Inc ($30,000)** - John
- **Action**: Re-engage with specific use case examples by Friday
- **Why**: 25-day silence has killed momentum on early-stage deal

**Unknown Co ($45,000)** - Sarah
- **Action**: Data cleanup required before any sales action
- **Why**: Missing critical data (stage, close date, account info) makes this unworkable
- **Recommendation**: Spend 30 minutes updating CRM or mark as dead deal

### Weekly Revenue Forecast

- **High confidence**: Beta Ltd ($96K expected)
- **Medium confidence**: Acme Corp ($30K expected)
- **Total realistic pipeline**: $126K for next 30 days

---

## Token Usage Summary

| Step | Input Tokens | Output Tokens | Cost |
|------|-------------|---------------|------|
| Planner | 348 | 75 | $0.002169 |
| Analyzer | 136 | 55 | $0.001233 |
| Synthesizer | 841 | 644 | $0.012183 |
| **Total** | **1,325** | **774** | **$0.015585** |

Model: `claude-sonnet-4-20250514`
