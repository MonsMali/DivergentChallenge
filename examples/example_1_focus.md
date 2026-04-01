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
  Reasoning: To identify which deals to focus on this week, I will prioritize
  deals by proximity of close date, deal stage advancement, and probability,
  while flagging data quality issues that may need resolution before action can
  be taken.

--- Analyzer ---
  #1 Acme Corp: risk=0.25 sentiment=cautious
  #2 Beta Ltd: risk=0.067 sentiment=positive
  #3 Delta Inc: risk=0.707 sentiment=unclear
  #4 Omega SA: risk=0.61 sentiment=neutral
  #5 Unknown Co: risk=1.0 sentiment=neutral
```

---

## System Output

# Weekly Deal Focus Recommendations
**As of April 1, 2026**

## Priority Ranking (by Expected Value, Risk-Adjusted)

| Rank | Deal | EV (Amount x Prob) | Risk Score | Close Date | Days to Close |
|------|------|-------------------|------------|------------|---------------|
| 1 | Beta Ltd | **$96,000** | 0.067 (Low) | Apr 10 | **9 days** |
| 2 | Acme Corp | **$30,000** | 0.25 (Low-Med) | Apr 15 | 14 days |
| 3 | Omega SA | **$37,500** | 0.61 (High) | Apr 20 | 19 days |
| 4 | Delta Inc | **$9,000** | 0.707 (High) | May 1 | 30 days |
| 5 | Unknown Co | **$18,000*** | 1.0 (Critical) | MISSING | Unknown |

*\*EV is unreliable due to critical data quality issues*

### PRIORITY 1 -- Beta Ltd | $120,000 | Owner: Sarah
**Action Required: Close this deal by April 10 -- 9 days remaining.**

This is your highest-confidence, highest-value deal this week. A risk score of 0.067, positive sentiment, and a champion actively pushing for a fast close makes this the closest thing to a certain win in your pipeline.

**Specific actions this week:**
- **Today (Apr 1):** Sarah to send a finalized redlined contract to Beta Ltd with a clear signature deadline of **April 7** -- giving 3 business days buffer before the April 10 close date. Do not wait for them to request it.
- **By Apr 3:** Confirm legal/procurement contacts on Beta Ltd's side are looped in. With 12 email threads and 5 meetings, relationships are established -- identify who has signature authority if not already confirmed.
- **By Apr 5:** If no signature or response by Apr 3, Sarah schedules a 20-minute live call (not email) to address any final blockers. The buyer is motivated; friction is likely process, not intent.
- **Risk watch:** The fast-close momentum is an asset -- don't let internal delays (legal review, contract generation) be the reason this slips to May. Escalate to RevOps or deal desk today if any internal bottlenecks exist.

### PRIORITY 2 -- Acme Corp | $50,000 | Owner: John
**Action Required: Re-engage immediately -- last contact was 10 days ago with a closing deadline of April 15.**

This deal has clean data, a reasonable probability (0.6), and low risk (0.25), but the "budget concerns" flag combined with 10 days of silence is a yellow light that could turn red fast. At 14 days to close, this week is the decisive window.

**Specific actions this week:**
- **By Apr 2:** John sends a targeted email -- NOT a generic check-in. Address the budget concern head-on. Options to consider: phased payment structure, a reduced scope pilot at ~$30,000 with expansion language baked in, or a time-limited discount (e.g., 10% if signed by April 10). Choose one and lead with it.
- **By Apr 3:** If no response to the email within 24 hours, John calls directly. Two meetings completed means there's an established relationship -- use it.
- **By Apr 7:** If still no commitment signal, escalate internally. Reassess probability downward to 0.4 and flag for pipeline review. Do not let this drift silently past April 15.

### PRIORITY 3 -- Omega SA | $75,000 | Owner: Mike
**Action Required: Break the silence and qualify urgency -- 0 meetings and 15 days of no contact is a serious warning sign for an April 20 close.**

Despite having the second-largest deal size, Omega SA has a high risk score (0.61), neutral sentiment, zero meetings held, and a "long sales cycle expected" note. This deal is unlikely to close April 20 as currently positioned, but it's worth fighting for this week to either accelerate it or reset the close date to a credible forecast.

**Specific actions this week:**
- **By Apr 2:** Mike re-engages via phone (not email given the stale contact flag). Goal of the call: get a first meeting booked for the week of April 6-10 and identify the internal decision-maker.
- **By Apr 3:** If contact is made, Mike proposes a structured next step -- a 45-minute discovery-to-proposal walkthrough with the key stakeholder(s). No meeting means no deal by April 20.
- **By Apr 4:** Mike updates the CRM with honest probability and close date. If a meeting cannot be secured this week, the April 20 close date should be pushed to **June 1** minimum, given the "long sales cycle" note. A false close date distorts forecast -- flag this for your pipeline review.

### PRIORITY 4 -- Delta Inc | $30,000 | Owner: John
**This week: Qualify or kill -- do not let this linger.**

Delta Inc has a 25-day contact gap, an unclear use case, only 1 meeting, and a high risk score (0.707). At 30 days to a May 1 close, there's still time -- but only if John re-engages immediately and uncovers whether there is a real opportunity here.

**Specific actions this week:**
- **By Apr 3:** John sends a direct re-engagement email with a specific question: *"We'd like to understand your core use case better before proposing a path forward -- can we set up 30 minutes this week?"* This tests responsiveness and seriousness simultaneously.
- **By Apr 5:** If no response, this deal should be moved to "At Risk" status in the CRM. The combination of stale contact, unclear use case, and low probability (0.3) does not justify significant time investment until re-engagement is confirmed.
- **Note for John:** John already owns Acme Corp (Priority 2). Given Acme's April 15 deadline, Acme must take precedence this week if time is constrained. Delta Inc can be deprioritized to mid-week or delegated for initial re-engagement.

### PRIORITY 5 -- Unknown Co | $45,000 | Owner: Sarah
**Immediate CRM cleanup required before any sales action. This deal should not be in active pipeline in its current state.**

This record has **four simultaneous data quality flags**: missing stage, missing close date, no account match, and stale contact (40 days). The risk score is 1.0 -- maximum. No meaningful sales decision can be made on this deal until the data is cleaned.

**Specific actions this week:**
- **By Apr 2 (Sarah + RevOps):** Identify who "Unknown Co" actually is. Run the email domain, deal owner history, and any CRM activity logs to match to a real account. This is a data hygiene task, not a sales task.
- **By Apr 3:** Once the account is identified: populate stage, close date, and industry/region. If the account cannot be identified, **archive the deal** and remove it from the active pipeline. A $45,000 phantom record inflates your forecast by ~$18,000 in expected value.
- **Note:** Sarah also owns Beta Ltd (Priority 1). Beta Ltd must remain Sarah's primary focus this week. Unknown Co cleanup should be handled in under 30 minutes and can be done async or delegated to a RevOps admin.

## This Week's Pipeline Health Summary

| Issue | Deal(s) Affected | Action Owner | Deadline |
|-------|-----------------|--------------|----------|
| Stale contact re-engagement | Delta Inc, Omega SA, Unknown Co | John, Mike, Sarah | Apr 2-3 |
| Immediate close push | Beta Ltd | Sarah | Apr 1 |
| Budget objection resolution | Acme Corp | John | Apr 2 |
| CRM data cleanup | Unknown Co | Sarah + RevOps | Apr 2-3 |
| Forecast accuracy audit | Omega SA (wrong close date) | Mike + Manager | Apr 4 |

> **Bottom line this week:** Beta Ltd is your must-win. Acme Corp is your must-defend. Omega SA and Delta Inc need re-engagement to determine if they belong in this month's forecast at all. Unknown Co is a data problem before it's a sales problem.

---

## Token Usage Summary

| Step | Model | Input Tokens | Output Tokens | Cost |
|------|-------|-------------|---------------|------|
| Planner | Sonnet 4.6 | 349 | 129 | $0.002982 |
| Analyzer | Haiku 4.5 | 136 | 60 | $0.000349 |
| Synthesizer | Sonnet 4.6 | 865 | 2,180 | $0.035295 |
| **Total** | | **1,350** | **2,369** | **$0.038626** |
