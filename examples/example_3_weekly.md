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
  Reasoning: To determine this week's priorities, I need to evaluate all deals
  across urgency signals including close dates, data quality issues, stage
  progression, and probability to surface concrete owner actions.

--- Analyzer ---
  #1 Acme Corp: risk=0.25 sentiment=cautious
  #2 Beta Ltd: risk=0.067 sentiment=positive
  #3 Delta Inc: risk=0.707 sentiment=unclear
  #4 Omega SA: risk=0.61 sentiment=neutral
  #5 Unknown Co: risk=1.0 sentiment=neutral
```

---

## System Output

# This Week's RevOps Action Plan -- April 1, 2026

## Priority Ranking (by Expected Value, Risk-Adjusted)

| Rank | Deal | Owner | EV (Amount x Prob) | Risk Score | Close Date | Action Urgency |
|------|------|-------|--------------------|------------|------------|----------------|
| 1 | Beta Ltd | Sarah | **$96,000** | 0.067 (Low) | Apr 10 | Critical -- closes in 9 days |
| 2 | Acme Corp | John | **$30,000** | 0.25 (Low-Med) | Apr 15 | High -- closes in 14 days, gone silent |
| 3 | Omega SA | Mike | **$37,500** | 0.61 (High) | Apr 20 | High -- high risk, no meetings held |
| 4 | Unknown Co | Sarah | **$18,000** | 1.0 (Critical) | MISSING | Medium -- data triage required first |
| 5 | Delta Inc | John | **$9,000** | 0.707 (High) | May 1 | Lower -- early stage, more runway |

### #1 -- Beta Ltd | $120,000 | Sarah | Close: April 10

**Situation:** Highest EV deal in the pipeline at $96K. Lowest risk score (0.067). Buyer is actively pushing for a fast close. Nine days to the deadline.

**The risk here is execution, not interest.** A deal this size can still slip on contract redlines, legal review, or procurement delays.

**Actions this week:**
1. **Today (Apr 1):** Sarah to confirm with the Beta Ltd contact whether a signed agreement by April 10 is still achievable -- specifically ask: *"Is your procurement/legal team looped in and is April 10 still realistic on your side?"*
2. **By Apr 2:** If contract hasn't been sent, send it today. If it has, confirm they've received it and identify who internally owns signature authority.
3. **By Apr 3:** Escalate internally -- Sarah should brief her manager that this deal needs legal/finance support on standby to turn around any redlines within 24 hours.
4. **By Apr 7 (3 days before close):** If no signed agreement, Sarah schedules a call to resolve any final blockers. Do not let this drift to Apr 10 without a concrete signature path confirmed.

> **Manager action:** Flag this deal for daily status updates. A $120K deal at 80% probability is your most important asset this week.

### #2 -- Acme Corp | $50,000 | John | Close: April 15

**Situation:** 14 days to close. Last contact was **10 days ago** -- that's too long given the timeline. Sentiment is cautious with documented budget concerns. Two meetings and five email threads suggest genuine engagement, but the silence is a warning sign.

**The risk:** Budget objection is unresolved and John has let it sit for 10 days. If unaddressed, this deal will push to Q2 or die.

**Actions this week:**
1. **Today (Apr 1):** John calls (not emails) Acme Corp. The goal is a single, direct conversation to address the budget concern head-on. Suggested framing: *"I want to make sure we find a path forward that works for your budget before April 15 -- can we talk through the numbers today?"*
2. **By Apr 2:** Based on that call, John prepares one of two responses:
   - If budget is the real blocker: Present a phased payment option, reduced scope at $35-40K, or a Q2 start with contract signed now. Get manager approval on any pricing flexibility before the call.
   - If the deal is stalling for another reason: Identify the true objection and escalate to manager for coaching.
3. **By Apr 7:** If no positive signal after outreach, John formally reassesses probability (consider dropping to 0.4) and updates CRM notes. Do not carry this at 0.6 if the buyer has gone cold.

> **Data note:** No data quality flags on this deal -- the CRM data is clean. The risk is purely commercial.

### #3 -- Omega SA | $75,000 | Mike | Close: April 20

**Situation:** $37,500 EV, but risk score of 0.61 indicates significant concern. **Zero meetings held.** Last contact was 15 days ago. The buyer's own note says "long sales cycle expected" -- yet the close date is April 20, just 19 days away. These two facts are in direct contradiction.

**The risk:** This deal has a fictitious close date. A deal with zero meetings and a long sales cycle does not close in 19 days. Either the close date is wrong, or there are undocumented conversations not captured in the CRM.

**Actions this week:**
1. **By Apr 2:** Mike contacts Omega SA to schedule a first live meeting (video or in-person given EU region) this week or early next. Without a meeting, this deal cannot progress.
2. **By Apr 2:** Mike updates the CRM with an honest close date. If the sales cycle is genuinely long, this deal is likely a June or July close -- reflecting that now is critical for accurate forecasting. Manager should review and approve the update.
3. **By Apr 3:** Mike and his manager align on what "Proposal" stage actually means here -- if there's been no meeting, this deal may need to be moved back to Discovery.
4. **Data flag:** `stale_contact` on a deal with zero meetings is a serious data hygiene issue. RevOps should flag this for pipeline review -- a $75K deal at Proposal with no meetings is a forecast risk.

> **Manager action:** Do not count this deal in April forecast until a meeting is confirmed and the close date is validated.

### #4 -- Unknown Co | $45,000 | Sarah | Close: MISSING

**Situation:** This deal is a data emergency. Risk score is 1.0 (maximum). Four data quality flags: `missing_stage`, `missing_close_date`, `no_account_match`, `stale_contact`. Last contact was **40 days ago**. Zero meetings, one email thread, no recent updates.

**This deal cannot be forecasted or actioned until the data is fixed.** The $18K expected value is notional.

**Actions this week (Internal -- Sarah + RevOps):**
1. **By Apr 2 (hard deadline):** Sarah answers five questions and updates the CRM:
   - Who is the actual contact at this company, and what is the company's real name?
   - What stage is this deal in (if Sarah doesn't know, it's Discovery or Dead)?
   - What is a realistic close date based on actual buyer signals?
   - Why has there been no contact for 40 days?
   - Is this deal alive at all?
2. **By Apr 2:** RevOps/manager reviews Sarah's update. If Sarah cannot answer the questions above, this deal should be **marked as stalled/dead** and removed from the active pipeline until re-engaged.
3. **By Apr 3:** If the deal is real and active, Sarah makes contact with the prospect and documents the outcome in CRM same day.

> **Note to Sarah:** Given you are also owning the highest-priority deal (Beta Ltd) this week, flag to your manager if bandwidth is a constraint. Beta Ltd must take precedence.

> **Systemic note for RevOps:** A deal reaching 40 days without contact and carrying 4 data quality flags indicates a gap in your pipeline hygiene process. Consider implementing an automated CRM alert if any deal goes 14+ days without a contact log entry.

### #5 -- Delta Inc | $30,000 | John | Close: May 1

**Situation:** Lowest EV at $9K. High risk score (0.707). Last contact was **25 days ago** (`stale_contact` flagged). Discovery stage, unclear use case, only one meeting held.

**This is a lower priority this week given the May 1 close date and John's heavier obligations on Acme Corp.** However, 25 days of silence in Discovery with an unclear use case puts this deal on a path to dying quietly.

**Actions this week (time-boxed to 30 minutes):**
1. **By Apr 3:** John sends a single, low-pressure re-engagement email. Suggested angle: share a relevant SaaS case study or ROI benchmark for their likely use case and ask one qualifying question: *"Is solving [X] still a priority for your team in Q2?"* This tests if the deal is alive without over-investing.
2. **By Apr 4:** CRM flag cleared or escalated. If John gets no response by Apr 8, mark contact as stale, move close date to June at the earliest, and reduce probability to 20%. The May 1 close date at Discovery stage is not credible and should not appear in April/May forecasting.

**Do not:** Have John spend more than 1 hour on Delta Inc this week. Beta Ltd and Acme Corp represent 7x the adjusted value.

> **Note:** John is carrying both #2 (Acme Corp) and #5 (Delta Inc) this week. Manager should confirm John is not overloaded and that Acme Corp is his primary focus.

## This Week's Summary Checklist

| By When | Who | Action |
|---------|-----|--------|
| **Apr 1 (today)** | Sarah | Confirm Beta Ltd signature path -- call the buyer |
| **Apr 1 (today)** | John | Call Acme Corp, address budget objection directly |
| **Apr 2** | Sarah | Complete all data fields for Unknown Co or mark as stalled |
| **Apr 2** | Mike | Contact Omega SA, book first meeting, update close date |
| **Apr 2** | Manager | Review Omega SA close date; remove from April forecast if unvalidated |
| **Apr 2** | Manager | Brief legal/finance on Beta Ltd standby support |
| **Apr 3** | John | Send Delta Inc re-engagement email |
| **Apr 3** | RevOps | Review pipeline hygiene process for Unknown Co-type scenarios |
| **Apr 7** | Sarah | Final push on Beta Ltd if not yet signed |
| **Apr 7** | John | Re-assess Acme Corp probability if no positive signal received |

*Forecast note: Of your ~$320K in pipeline, only Beta Ltd ($96K EV) and Acme Corp ($30K EV) represent credible April closes. Omega SA's April close date should be treated as unvalidated until a meeting is confirmed. Total validated April EV: **~$126K.***

---

## Token Usage Summary

| Step | Model | Input Tokens | Output Tokens | Cost |
|------|-------|-------------|---------------|------|
| Planner | Sonnet 4.6 | 348 | 69 | $0.002079 |
| Analyzer | Haiku 4.5 | 136 | 60 | $0.000349 |
| Synthesizer | Sonnet 4.6 | 856 | 2,560 | $0.040968 |
| **Total** | | **1,340** | **2,689** | **$0.043396** |
