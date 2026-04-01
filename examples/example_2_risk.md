# Example 2: Risk Assessment

**Query:** `"What deals look at risk?"`

**Command:** `python -m src.cli ask "What deals look at risk?" --verbose`

*Output captured on April 1, 2026.*

---

## Pipeline Steps (Verbose Output)

```
  ✓ 5 deals loaded from Google Drive

--- Planner ---
  Type: risk
  Deals: all
  Reasoning: Need to analyze all deals to identify risk factors like low
  probability, data quality issues, stale stages, or approaching close dates.

--- Analyzer ---
  #1 Acme Corp: risk=0.25 sentiment=cautious
  #2 Beta Ltd: risk=0.067 sentiment=positive
  #3 Delta Inc: risk=0.707 sentiment=unclear
  #4 Omega SA: risk=0.61 sentiment=neutral
  #5 Unknown Co: risk=1.0 sentiment=neutral
```

---

## System Output

# Deals at Risk Analysis

Based on risk scores, data quality, and business impact, here are the deals requiring immediate attention:

## Priority Ranking (by urgency and potential loss)

**1. CRITICAL: Unknown Co ($45,000)** - Risk Score: 1.0
**2. HIGH: Delta Inc ($30,000)** - Risk Score: 0.707
**3. MEDIUM: Omega SA ($75,000)** - Risk Score: 0.61
**4. LOW: Acme Corp ($50,000)** - Risk Score: 0.25

## Immediate Actions Required

### CRITICAL - Unknown Co ($45,000)
**Issues:** Complete data breakdown - missing stage, close date, account info, 40-day contact gap
**Actions:**
- **Sarah: Immediate outreach by EOD today** - Call + email to re-establish contact
- **Data cleanup by Friday 1/17** - Populate missing stage, close date, industry, region
- **Decision point by 1/24:** If no response after 7 days, move to "Lost" and focus efforts elsewhere

### HIGH RISK - Delta Inc ($30,000)
**Issues:** 25-day silence, unclear use case, early discovery stage with May close date
**Actions:**
- **John: Contact by Thursday 1/16** - Schedule discovery call to clarify use case and budget authority
- **Qualify or disqualify by 1/31** - Either advance to qualified opportunity or deprioritize
- **If re-engaged:** Move probability to 0.5+ or reduce to 0.1 based on findings

### MEDIUM RISK - Omega SA ($75,000)
**Issues:** 15-day contact gap, zero meetings held, long sales cycle warning
**Actions:**
- **Mike: Schedule face-to-face or video meeting by 1/22** - No more email-only engagement
- **Establish project timeline and decision criteria** during first meeting
- **If no meeting acceptance:** Reduce probability to 0.2 and focus on higher-priority deals

### LOW RISK - Acme Corp ($50,000)
**Issues:** Budget concerns but otherwise healthy engagement
**Actions:**
- **John: Address budget concerns by 1/20** - Present ROI analysis or discuss phased implementation
- **Maintain current priority** - 10-day gap is acceptable given strong engagement history

## Revenue Impact Summary
- **Total at-risk revenue:** $200,000 across 4 deals
- **Immediate attention needed:** $120,000 (Unknown Co + Delta Inc + Omega SA)
- **Expected recovery with actions:** ~$85,000 (assuming 50% success rate on interventions)

**Note:** Beta Ltd ($120,000) shows no risk factors - maintain current course with 2-day contact cadence through close on 4/10.

---

## Token Usage Summary

| Step | Input Tokens | Output Tokens | Cost |
|------|-------------|---------------|------|
| Planner | 345 | 68 | $0.002055 |
| Analyzer | 136 | 55 | $0.001233 |
| Synthesizer | 831 | 678 | $0.012663 |
| **Total** | **1,312** | **801** | **$0.015951** |

Model: `claude-sonnet-4-20250514`
