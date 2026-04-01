# Example 3: Weekly Action Plan

**Query:** `"What actions should we take this week?"`

**Command:** `python -m src.cli ask "What actions should we take this week?" --verbose`

*Output captured on April 1, 2026.*

---

## Pipeline Steps (Verbose Output)

```
  ✓ 5 deals loaded from Google Drive

--- Planner ---
  Type: actions
  Deals: all
  Reasoning: To determine weekly actions, I need to analyze all deals to
  identify urgent tasks, data quality issues to fix, and deals requiring
  immediate attention based on close dates and stages.

--- Analyzer ---
  #1 Acme Corp: risk=0.25 sentiment=cautious
  #2 Beta Ltd: risk=0.067 sentiment=positive
  #3 Delta Inc: risk=0.707 sentiment=unclear
  #4 Omega SA: risk=0.61 sentiment=neutral
  #5 Unknown Co: risk=1.0 sentiment=neutral
```

---

## System Output

# Weekly Action Plan - Priority Ranking

## URGENT (This Week - Days 1-3)

**#1 PRIORITY: Beta Ltd - $120,000** (Expected Value: $96K)
- **Action**: Sarah must schedule contract review meeting by Wednesday
- **Why**: Close date April 10th (5 days away), 80% probability, positive sentiment
- **Risk**: Minimal (0.067 score) but time-sensitive

**#2 PRIORITY: Acme Corp - $50,000** (Expected Value: $30K)
- **Action**: John needs to address budget concerns with financial proposal by Thursday
- **Why**: 10 days since contact, cautious sentiment on $50K deal
- **Next Step**: Schedule budget discussion call with decision maker this week

## MEDIUM PRIORITY (This Week - Days 4-7)

**#3: Omega SA - $75,000** (Expected Value: $37.5K)
- **Action**: Mike must make contact immediately - 15 days stale
- **Critical Issue**: Zero meetings scheduled despite proposal stage
- **Next Step**: Phone outreach Tuesday, schedule demo by Friday

## DATA CLEANUP REQUIRED (Immediate)

**#4: Unknown Co - $45,000** (Expected Value: $18K)
- **Action**: Sarah needs to complete deal record by Wednesday
- **Missing**: Stage, close date, company details (40 days stale)
- **Decision Point**: Qualify viability or mark as lost

**#5: Delta Inc - $30,000** (Expected Value: $9K)
- **Action**: John should re-engage or disqualify by Friday
- **Issue**: 25 days without contact, unclear use case
- **High Risk**: 0.707 risk score indicates likely stall

## SPECIFIC NEXT STEPS BY REP

**Sarah (2 deals)**:
- Beta Ltd: Contract review meeting by Wednesday
- Unknown Co: Complete missing data fields by Wednesday

**John (2 deals)**:
- Acme Corp: Budget discussion call by Thursday
- Delta Inc: Re-engagement call or disqualification by Friday

**Mike (1 deal)**:
- Omega SA: Immediate phone outreach Tuesday, demo by Friday

## REVENUE IMPACT
- **At Risk**: $96K (Beta Ltd) if not closed this week
- **Recoverable**: $67.5K (Acme + Omega) with immediate action
- **Pipeline Health**: 2 deals need data cleanup affecting forecast accuracy

**Data Quality Issue**: 40% of deals have stale contact flags - implement weekly contact requirements immediately.

---

## Token Usage Summary

| Step | Input Tokens | Output Tokens | Cost |
|------|-------------|---------------|------|
| Planner | 347 | 76 | $0.002181 |
| Analyzer | 136 | 55 | $0.001233 |
| Synthesizer | 841 | 600 | $0.011523 |
| **Total** | **1,324** | **731** | **$0.014937** |

Model: `claude-sonnet-4-20250514`
