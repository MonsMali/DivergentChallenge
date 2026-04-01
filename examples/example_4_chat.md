# Example 4: Interactive Chat Mode

**Command:** `python -m src.cli chat`

*Output captured on April 1, 2026. This example shows two sequential queries in a single session. Data is downloaded from Google Drive and ingested once on startup; subsequent queries only run the LLM pipeline steps (planner, analyzer, synthesizer), avoiding redundant Drive API calls and file I/O.*

---

## Session Output

```
  ✓ 5 deals loaded from Google Drive
╭──────────────────────────── RevOps Copilot ─────────────────────────────────╮
│ 5 deals loaded — 2 complete, 3 with gaps                                    │
│ Type exit to quit                                                           │
╰─────────────────────────────────────────────────────────────────────────────╯
```

### Query 1: "Which deals should I focus on this week?"

```
> Which deals should I focus on this week?
```

**Output:**

## Weekly Deal Focus Report
**As of April 1, 2026 | Prepared for Sales Leadership**

### Priority Rankings (Expected Value Adjusted for Risk)

| Rank | Deal | Raw EV | Risk Score | Adjusted Priority | Close Date | Owner |
|------|------|--------|------------|-------------------|------------|-------|
| 1 | Beta Ltd | $96,000 | 0.067 (Low) | Critical | Apr 10 | Sarah |
| 2 | Acme Corp | $30,000 | 0.25 (Low-Med) | High | Apr 15 | John |
| 3 | Omega SA | $37,500 | 0.61 (High) | Medium | Apr 20 | Mike |
| 4 | Unknown Co | $18,000 | 1.0 (Max) | Data Blocker | MISSING | Sarah |
| 5 | Delta Inc | $9,000 | 0.707 (High) | Low/Nurture | May 1 | John |

**PRIORITY 1 -- Beta Ltd | $120,000 | Close: April 10 | Owner: Sarah**

Why it's #1: Highest adjusted expected value at $96K, lowest risk score in the portfolio (0.067), positive sentiment, and a prospect explicitly pushing for a fast close. You have **9 calendar days** to get this signed.

The risk here is execution delay, not deal quality.

Actions this week:
1. **Today (Apr 1) -- Sarah to send redlined contract draft.** If legal review hasn't started, escalate internally *today*. At $120K with a Fintech buyer in the UK, compliance and contract review typically need 3-5 business days minimum.
2. **By Apr 3 -- Schedule a live call to walk through final terms.** Confirm: payment terms, start date, and any outstanding procurement requirements (especially relevant for UK Fintech -- check for FCA-related vendor approval steps).
3. **By Apr 7 -- Verbal confirmation of signed intent.** If Sarah hasn't received a clear "yes, we're signing by Apr 10," flag immediately to management for executive sponsor outreach from your side.

**PRIORITY 2 -- Acme Corp | $50,000 | Close: April 15 | Owner: John**

Budget concerns combined with a cautious sentiment and 10 days of silence is a yellow flag that needs to be resolved *this week* -- not next.

Actions this week:
1. **Today (Apr 1) -- John to send a targeted re-engagement email** addressing budget directly. Suggested angle: offer a revised proposal with a phased payment structure or a stripped-down Tier 1 scope at $35K to remove the budget objection.
2. **By Apr 3 -- Secure a 30-minute call.** Force a binary answer: *"Is budget approval in place for a decision before April 15, or do we need to adjust scope/timeline?"*
3. **By Apr 8 -- Decision checkpoint.** If budget is confirmed: push for signed agreement by Apr 13. If NOT confirmed: immediately re-forecast close date to May.

**PRIORITY 3 -- Omega SA | $75,000 | Close: April 20 | Owner: Mike**

This close date needs immediate re-evaluation. Zero meetings held. 15 days since last contact. "Long sales cycle expected" note directly contradicts the April 20 close date.

Actions this week:
1. **By Apr 2 -- Mike to re-engage with a specific meeting request.** Manufacturing buyers in EU often have formal procurement cycles -- Mike needs to understand *where Omega SA is in their internal process*.
2. **By Apr 4 -- CRM update required.** After re-engagement, Mike must update the close date to reflect reality. If Omega SA confirms a long sales cycle, move close date to June-July and adjust probability to 30-35%.
3. **By Apr 7 -- First meeting must be booked.** Zero meetings at Proposal stage in manufacturing with a long-cycle note is a data contradiction.

**PRIORITY 4 -- Unknown Co | $45,000 | Close: MISSING | Owner: Sarah**

This deal cannot be worked until data is remediated. Maximum risk score (1.0), four data quality flags, 40 days of silence. This is a CRM liability.

**PRIORITY 5 -- Delta Inc | $30,000 | Close: May 1 | Owner: John**

Low-pressure re-engagement only. John sends a single email by Apr 3 with a qualifying question. Do not invest more than 1 hour. Beta Ltd and Acme Corp represent 7x the adjusted value.

### Forecast Integrity Note

**Current active pipeline (April closes): ~$188K nominal.**
Realistically, approximately **$55K-$70K** is credible for April close based on deal health:
- Beta Ltd ($96K EV) is the only high-confidence April close.
- Acme Corp ($30K EV) is possible but budget-dependent.
- Omega SA ($37.5K EV) should likely be **removed from April forecast** entirely pending Mike's engagement this week.

```
  planner 349→88 | analyzer 136→60 | synthesizer 854→2603 | $0.0443
```

---

### Query 2: "What's the total pipeline value at risk?"

```
> What's the total pipeline value at risk?
```

**Output:**

## Pipeline Value at Risk -- April 1, 2026

### Executive Summary

| Metric | Value |
|---|---|
| **Total Pipeline (Gross)** | $320,000 |
| **Weighted Pipeline (Probability-Adjusted)** | $178,500 |
| **Pipeline Value at Risk** | **$143,500** (44.8% of gross) |
| **Deals Flagged as High Risk** | 3 of 5 |

### How "Value at Risk" Is Calculated

For each deal: **Amount x Risk Score = Value at Risk**

This reflects dollars exposed to loss based on compounded risk signals (low probability, stale contacts, data quality gaps, sentiment, engagement depth).

### Deal-by-Deal Risk Breakdown

**Priority 1 -- Unknown Co | $45,000 | Risk Score: 1.0**
**Value at Risk: $45,000 (100% of deal value)**

This deal is in complete data failure. Four simultaneous data quality flags, zero meetings, one email thread, and last contact 40 days ago. At probability 0.4, even the base weighted value ($18,000) is likely overstated.

- **By April 3:** Sarah to audit this record in CRM -- determine if a real company exists behind "Unknown Co." If no valid account is identified within 48 hours, move to Dead/Disqualified stage.
- **By April 3:** RevOps to check for duplicate records; suppress from forecast until resolved.

**Priority 2 -- Omega SA | $75,000 | Risk Score: 0.61**
**Value at Risk: $45,750** -- largest single value at risk in the portfolio.

Proposal stage with April 20 close date -- 19 days away -- yet zero meetings and last contact 15 days ago. "Long sales cycle expected" is directly contradicted by the close date.

- **By April 3:** Mike must get a live meeting on the calendar before April 10. If Omega SA won't commit, push close date to June and reduce probability to 0.3.
- **Forecast impact:** Until a meeting is confirmed, recommend treating this as $22,500 (0.3 probability floor) rather than the current $37,500.

**Priority 3 -- Delta Inc | $30,000 | Risk Score: 0.707**
**Value at Risk: $21,210**

25 days stale contact. One meeting, two email threads, "unclear use case." This deal was never properly qualified.

- **By April 3:** John reaches out directly -- phone call preferred. Confirm the use case and assess whether there is a real buying initiative.
- **By April 7:** If no response, move probability to 0.15 and flag for pipeline review.

**Priority 4 -- Acme Corp | $50,000 | Risk Score: 0.25**
**Value at Risk: $12,500**

Moderate risk, but April 15 close date is 14 days away. Budget concerns are the primary signal.

- **By April 4:** John calls Acme Corp to address the budget concern head-on with a concrete option (phased payment, reduced scope, multi-year pricing).
- **By April 8:** If unresolved, adjust probability to 0.4 and push close date to May 15.

**Priority 5 -- Beta Ltd | $120,000 | Risk Score: 0.067**
**Value at Risk: $8,040**

Lowest risk in the portfolio. Strong engagement, positive sentiment. The only threat is process/procurement delay, not deal conviction.

- **By April 4:** Sarah confirms exact contract/signature process. April 10 is 9 days away; any procurement delay could push to May.

### Consolidated Risk Register

| # | Deal | Amount | Risk Score | $ at Risk | Primary Risk Driver | Urgency |
|---|------|--------|------------|-----------|--------------------|----|
| 1 | Unknown Co | $45,000 | 1.00 | **$45,000** | Data integrity failure | Immediate |
| 2 | Omega SA | $75,000 | 0.61 | **$45,750** | Zero meetings, stale contact | This week |
| 3 | Delta Inc | $30,000 | 0.707 | **$21,210** | Stale contact, unclear use case | This week |
| 4 | Acme Corp | $50,000 | 0.25 | **$12,500** | Budget objection, closing soon | By April 4 |
| 5 | Beta Ltd | $120,000 | 0.067 | **$8,040** | Procurement timing only | Monitor |
| | **Total** | **$320,000** | | **$143,500** | | |

### Immediate Actions for RevOps
1. **Pull Unknown Co from April forecast today** until Sarah resolves the account identity by April 3. This deal is currently inflating weighted pipeline by ~$18,000.
2. **Require John to log CRM updates on both Acme Corp and Delta Inc by April 4** -- both deals have the same owner and both are showing engagement gaps at critical stages.
3. **Flag Omega SA for deal review** in the next sales standup: a $75K Proposal with zero meetings and a 19-day close date is a forecast integrity issue, not just a risk signal.
4. **If Beta Ltd closes April 10 as forecasted**, April actual vs. forecast performance will hinge entirely on Acme Corp ($30K expected) with everything else at elevated risk of slipping to Q2.

```
  planner 349→85 | analyzer 136→60 | synthesizer 873→2043 | $0.0359
```

---

```
> exit
Goodbye.
```

---

## What This Demonstrates

**Data caching:** Google Drive download and ingestion happened once at startup. Both queries ran only the planner, analyzer, and synthesizer steps -- no redundant file I/O or API calls.

**Independent queries:** Each query is analyzed independently. The second query ("total pipeline value at risk?") gets its own planner analysis type (`risk`), its own sentiment classification, and a tailored synthesis. There is no conversation history or multi-turn context -- the efficiency gain is purely at the data layer.

**Model tiering:** The planner and synthesizer use Claude Sonnet 4.6 for complex reasoning. The analyzer's sentiment classification uses Claude Haiku 4.5 -- a simpler, cheaper model appropriate for a straightforward classification task.

**Cost for this session:**

| | Query 1 | Query 2 | Session Total |
|---|---------|---------|---------------|
| Input tokens | 1,339 | 1,358 | 2,697 |
| Output tokens | 2,751 | 2,188 | 4,939 |
| Cost | $0.0443 | $0.0359 | $0.0802 |

Two queries for ~$0.08 with zero redundant data loading. In the single-query `ask` mode, this would have required two separate Drive downloads and ingestion passes.
