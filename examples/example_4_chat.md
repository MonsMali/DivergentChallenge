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

## Weekly Deal Focus Priority Ranking

Based on weighted business impact (deal size x probability / risk score) and urgency:

**1. Beta Ltd - $120k (IMMEDIATE ACTION REQUIRED)**
**2. Acme Corp - $50k**
**3. Omega SA - $75k**
**4. Delta Inc - $30k**
**5. Unknown Co - $45k (DATA CLEANUP NEEDED)**

### PRIORITY 1: Beta Ltd ($120,000) - Sarah
- **Expected value:** $96,000 with 80% close probability
- **Critical timeline:** Close date April 10th (THIS WEEK)
- **Action:** Schedule contract review meeting by Wednesday 4/2
- **Risk mitigation:** Their "fast close" pressure could indicate budget deadline - confirm decision timeline and get legal/procurement contacts immediately
- **Next 48 hours:** Send final proposal terms and pricing confirmation

### PRIORITY 2: Acme Corp ($50,000) - John
- **Expected value:** $30,000 with 60% close probability
- **Budget concern resolution:** Schedule budget/ROI discussion call by Thursday 4/3
- **10-day communication gap:** John needs to re-engage immediately with cost-benefit analysis
- **Specific action:** Prepare scaled-down proposal option (potentially $35k) to address budget constraints
- **Timeline:** Aim to advance to negotiation stage by Friday 4/4

### PRIORITY 3: Omega SA ($75,000) - Mike
- **Data quality issue:** 15-day stale contact with zero meetings scheduled
- **Immediate action:** Mike must schedule discovery call within 2 business days
- **Risk factor:** High risk score (0.61) suggests deal may stall - need concrete next steps commitment
- **Manufacturing cycle consideration:** Confirm their Q2 budget allocation deadline

### PRIORITY 4: Delta Inc ($30,000) - John
- **Critical data gap:** 25-day stale contact flags this as near-dead
- **John's action:** Send "break-up" email by Tuesday 4/1 - either re-engage or disqualify
- **Use case clarity:** If they respond, schedule 30-min use case definition call
- **Resource allocation:** Don't invest more than 2 hours without clear buying signals

### PRIORITY 5: Unknown Co ($45,000) - Sarah
- **Data cleanup required:** Missing stage, close date, and account details
- **Sarah's immediate task:** Spend 30 minutes researching company and updating CRM data
- **Decision point:** If no response to outreach by Friday 4/4, mark as "Closed Lost - No Response"
- **40-day gap:** This deal is likely dead but needs formal disposition

### Resource Allocation Recommendation
- **Sarah:** 80% time on Beta Ltd negotiation, 20% on Unknown Co cleanup
- **John:** 70% time on Acme Corp budget discussion, 30% on Delta Inc re-qualification
- **Mike:** 100% focus on Omega SA discovery and relationship building

```
  planner 348→77 | analyzer 136→55 | synthesizer 843→767 | $0.0175
```

---

### Query 2: "What's the total pipeline value at risk?"

```
> What's the total pipeline value at risk?
```

**Output:**

## Pipeline Risk Analysis: $172,000 in Immediate Jeopardy

**Total Pipeline Value at Risk: $172,000** (54% of $320,000 total pipeline)

### CRITICAL RISK - Immediate Action Required

**1. Omega SA - $75,000 (Risk Score: 0.61)**
- **Risk Factor**: 15 days no contact + zero meetings despite Proposal stage
- **Action**: Mike must schedule face-to-face meeting within 48 hours. Deal is stalling with only 25 days to close date (4/20).
- **Specific Next Step**: Book on-site visit by Thursday 1/16 to re-engage Manufacturing decision makers.

**2. Delta Inc - $30,000 (Risk Score: 0.707)**
- **Risk Factor**: 25 days stale contact + unclear use case in Discovery
- **Action**: John needs to qualify out or re-engage immediately. Discovery stage deals shouldn't go cold this long.
- **Specific Next Step**: Send breakup email by COB today - either they respond with meeting availability or remove from pipeline.

### HIGH RISK - Address This Week

**3. Unknown Co - $45,000 (Risk Score: 1.0)**
- **Risk Factor**: Missing critical data + 40 days stale + zero meetings
- **Action**: Sarah must clean this record within 24 hours or remove from pipeline entirely.
- **Specific Next Step**: If legitimate opportunity, update stage/close date and book discovery call by Friday. Otherwise, mark as lost.

**4. Acme Corp - $50,000 (Risk Score: 0.25)**
- **Risk Factor**: Budget concerns + 10 days since last contact approaching close date
- **Action**: John needs budget qualification call this week to address pricing objections.
- **Specific Next Step**: Schedule CFO inclusion call by January 20th to discuss budget approval process.

### Data Quality Impact on Risk
- **$75,000 at risk** due to stale contact patterns (Omega SA + Delta Inc)
- **$45,000 at risk** due to missing critical deal data (Unknown Co)
- **Clean deals** (Beta Ltd) show 6.7% risk score - use as benchmark

### Immediate Actions - Next 48 Hours
1. **Mike**: Call Omega SA Manufacturing contact directly - don't email
2. **Sarah**: Audit Unknown Co record completely or remove from pipeline
3. **John**: Send Delta Inc breakup email sequence starting today
4. **John**: Schedule Acme Corp budget qualification before weekend

**Expected Impact**: Addressing these 4 deals could secure or properly qualify $200,000 in pipeline value within one week.

```
  planner 348→70 | analyzer 136→55 | synthesizer 836→639 | $0.0154
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

**Cost for this session:**

| | Query 1 | Query 2 | Session Total |
|---|---------|---------|---------------|
| Input tokens | 1,327 | 1,320 | 2,647 |
| Output tokens | 899 | 764 | 1,663 |
| Cost | $0.0175 | $0.0154 | $0.0329 |

Two queries for ~$0.03 with zero redundant data loading. In the single-query `ask` mode, this would have required two separate Drive downloads and ingestion passes.

Model: `claude-sonnet-4-20250514`
