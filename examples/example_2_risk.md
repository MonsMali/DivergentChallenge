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
  Reasoning: Analyze all deals for risk signals including low probability
  scores, early pipeline stages, upcoming close dates, and data quality issues
  such as missing fields and stale contacts.

--- Analyzer ---
  #1 Acme Corp: risk=0.25 sentiment=cautious
  #2 Beta Ltd: risk=0.067 sentiment=positive
  #3 Delta Inc: risk=0.707 sentiment=unclear
  #4 Omega SA: risk=0.61 sentiment=neutral
  #5 Unknown Co: risk=1.0 sentiment=neutral
```

---

## System Output

# At-Risk Deal Analysis -- April 1, 2026

## Risk Priority Ranking

Ranked by **adjusted risk impact** (deal size x probability x risk score):

| Rank | Deal | Amount | Prob | Risk Score | Adj. Risk Exposure | Owner |
|------|------|--------|------|------------|-------------------|-------|
| 1 | Unknown Co | $45,000 | 0.40 | 1.00 | **$18,000** | Sarah |
| 2 | Omega SA | $75,000 | 0.50 | 0.61 | **$22,875** | Mike |
| 3 | Delta Inc | $30,000 | 0.30 | 0.707 | **$6,363** | John |
| 4 | Acme Corp | $50,000 | 0.60 | 0.25 | **$7,500** | John |
| 5 | Beta Ltd | $120,000 | 0.80 | 0.067 | **$6,432** | Sarah |

> **Note:** Omega SA ranks higher than Delta Inc in business priority despite a lower risk score, because its dollar exposure is 2.5x larger and close date is sooner.

### CRITICAL -- Unknown Co | $45,000 | Sarah | Risk Score: 1.0

**Why it's at risk:**
- **Maximum risk score (1.0)** -- worst in portfolio
- Stage and close date are **completely missing** -- this deal cannot be properly managed or forecasted
- Last contact was **40 days ago** -- likely gone dark
- Zero meetings held; only 1 email thread
- No account match in CRM, industry and region unknown
- 4 simultaneous data quality flags: `missing_stage`, `missing_close_date`, `no_account_match`, `stale_contact`

**Recommended Actions:**
1. **By April 3 (48 hours):** Sarah to attempt direct outreach -- phone call preferred over email given the 40-day silence. If no response, escalate to manager to assess whether this deal should be disqualified.
2. **By April 3:** Sarah to manually populate Stage, Close Date, Industry, and Region in CRM -- even with best estimates -- so forecasting is not distorted.
3. **By April 5:** RevOps to run account matching logic and resolve `no_account_match` flag; if no company record can be found, flag for disqualification and remove from pipeline.
4. **If no response by April 8:** Mark as Closed Lost or move to nurture sequence. Do not let a $45K ghost deal pollute Q2 forecast.

### HIGH -- Omega SA | $75,000 | Mike | Risk Score: 0.61

**Why it's at risk:**
- **Zero meetings held** despite being at Proposal stage -- a critical engagement gap
- Last contact **15 days ago** on a deal closing April 20 -- only **19 days away**
- Sentiment is neutral; call note flags "long sales cycle expected," which directly contradicts the April 20 close date
- `stale_contact` flag suggests the contact record may be outdated
- EU region adds potential timezone/compliance friction

**Recommended Actions:**
1. **By April 3:** Mike to schedule a live video call with the Omega SA decision-maker. A Proposal-stage deal with zero meetings and 19 days to close is structurally broken -- the relationship needs a real conversation, not just emails.
2. **By April 3:** Verify contact information to resolve `stale_contact` flag. Confirm you are engaged with the actual budget owner, not a gatekeeper.
3. **By April 5:** Mike and manager to have a pipeline review on Omega SA specifically. If a meeting cannot be booked by April 7, the close date needs to be pushed to May/June and probability reduced from 0.5 to 0.3 or lower.
4. **By April 7:** If the call note says "long sales cycle," document what that means -- is it 3 months? 6 months? Set a realistic close date and adjust forecast accordingly.

### ELEVATED -- Delta Inc | $30,000 | John | Risk Score: 0.707

**Why it's at risk:**
- Last contact **25 days ago** -- stale for an active deal
- Only 1 meeting and 2 email threads; minimal engagement depth
- Still in Discovery with a May 1 close -- **30 days away** with no defined use case
- Probability at 0.30, risk score at 0.707 -- both independently signal this deal is shaky
- `stale_contact` flag; sentiment is unclear

**Recommended Actions:**
1. **By April 3:** John to reach out to Delta Inc with a specific, targeted message -- not a check-in. Frame around a concrete use case hypothesis: *"Based on our last conversation, I believe you're trying to solve [X]. I'd like to show you how we've done this for similar SaaS companies in 30 minutes."* Force a response.
2. **By April 7:** If John gets a meeting, run a structured Discovery call to define the use case and identify a budget owner. Without both, this deal has no path to May 1 close.
3. **By April 8:** If no response, move probability to 0.15 and push close date to June 1. Do not hold May 1 as realistic.
4. **For John's manager:** John owns both Delta Inc and Acme Corp (see below), both with activity gaps. Review John's total pipeline load -- if he's carrying too many deals, prioritize Acme Corp (higher probability, closer date) and consider re-assigning or deprioritizing Delta.

### WATCH -- Acme Corp | $50,000 | John | Risk Score: 0.25

**Why it's worth watching:**
- Close date is **April 15 -- only 14 days away**
- Last contact **10 days ago** -- not critical yet, but requires immediate re-engagement given the timeline
- Budget concerns flagged explicitly in call notes
- Probability at 0.60 and sentiment cautious -- this deal is winnable but not secure
- EU region may introduce procurement or legal review delays before April 15

**Recommended Actions:**
1. **By April 3:** John to re-engage Acme Corp directly to address the budget concern head-on. Come prepared with a specific option: a phased payment structure, a reduced initial scope at $35K with expansion, or a business case document quantifying ROI. Don't let "budget concerns" sit unaddressed with 14 days left.
2. **By April 7:** Confirm whether Acme Corp has any internal approval process (legal, procurement, finance sign-off) that could push past April 15. If yes, get the paperwork moving immediately.
3. **By April 10:** If no concrete buying signals (verbal commit, legal review started, or PO process initiated), adjust probability to 0.4 and flag for April forecast revision.

### LOW RISK -- Beta Ltd | $120,000 | Sarah | Risk Score: 0.067

**Why it's largely healthy:**
- Active engagement: 5 meetings, 12 email threads, last contact 2 days ago
- Positive sentiment, strong interest, buyer is pushing for fast close
- Probability at 0.80, risk score at 0.067 -- lowest risk in portfolio
- Close date April 10 -- **9 days away**

**One risk to monitor:**
- "Pushing for fast close" from the buyer side can sometimes indicate they want concessions baked into urgency. Ensure Sarah is not over-discounting to match their timeline pressure.

**Recommended Actions:**
1. **By April 3:** Sarah to confirm all legal/procurement steps are initiated on Beta Ltd's side -- MSA, security review, PO approval. A 9-day close is tight for a $120K Fintech deal in the UK.
2. **By April 5:** If any contract redlines are expected, get Legal involved today. Do not let a $120K deal slip past April 10 due to a late legal handoff.
3. **Note for Sarah's manager:** Sarah is simultaneously owning Beta Ltd (healthy) and Unknown Co (critical). Ensure Unknown Co cleanup does not consume bandwidth that slows down the $120K close this week.

## Summary Action Board

| Deal | Owner | Next Action | Deadline |
|------|-------|-------------|----------|
| Unknown Co | Sarah | Phone outreach + CRM data cleanup | April 3 |
| Omega SA | Mike | Book live meeting with decision-maker | April 3 |
| Delta Inc | John | Targeted re-engagement with use case hypothesis | April 3 |
| Acme Corp | John | Address budget objection with concrete options | April 3 |
| Beta Ltd | Sarah | Confirm legal/procurement steps initiated | April 3 |

> **Manager flag:** John owns the two next-most-at-risk deals (Delta Inc + Acme Corp) simultaneously. A 15-minute pipeline coaching call with John by **April 2** is recommended to prioritize effort given the compressed timelines.

---

## Token Usage Summary

| Step | Model | Input Tokens | Output Tokens | Cost |
|------|-------|-------------|---------------|------|
| Planner | Sonnet 4.6 | 346 | 113 | $0.002733 |
| Analyzer | Haiku 4.5 | 136 | 60 | $0.000349 |
| Synthesizer | Sonnet 4.6 | 851 | 2,247 | $0.036258 |
| **Total** | | **1,333** | **2,420** | **$0.039340** |
