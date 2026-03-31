# Example 4: Interactive Chat Mode

**Command:** `python -m src.cli chat`

*Output captured on March 31, 2026. This example shows two sequential queries in a single session. Data is downloaded from Google Drive and ingested once on startup; subsequent queries only run the LLM pipeline steps (planner, analyzer, synthesizer), avoiding redundant Drive API calls and file I/O.*

---

## Session Output

```
  ✓ 5 deals loaded from Google Drive
╭──────────────── RevOps Copilot ─────────────────╮
│ 5 deals loaded — 2 complete, 3 with gaps        │
│ Type exit to quit                                │
╰─────────────────────────────────────────────────╯

> Which deals should I focus on this week?

╭──────────────── Recommendation ─────────────────╮
│                                                  │
│  Priority Ranking for This Week                  │
│                                                  │
│  1. Beta Ltd ($120K) - Sarah                     │
│     Schedule final contract review meeting by    │
│     Wednesday. 80% probability, positive         │
│     sentiment, closes April 10th. Confirm        │
│     pricing, get legal review started, prepare   │
│     DocuSign package.                            │
│                                                  │
│  2. Acme Corp ($50K) - John                      │
│     Address budget concerns with ROI             │
│     presentation by Thursday. 10-day silence on  │
│     deal with budget hesitation needs immediate  │
│     attention. Prepare cost-benefit analysis,    │
│     explore payment terms options.               │
│                                                  │
│  3. Omega SA ($75K) - Mike                       │
│     Schedule discovery call this week. 15-day    │
│     gap with zero meetings is critical. High     │
│     value deal with no engagement history.       │
│                                                  │
│  4. Delta Inc ($30K) - John                      │
│     Re-engage with specific use case examples    │
│     by Friday. 25-day silence has killed         │
│     momentum.                                    │
│                                                  │
│  5. Unknown Co ($45K) - Sarah                    │
│     Data cleanup required before any sales       │
│     action. Missing stage, close date, account   │
│     info. Update CRM or mark as dead deal.       │
│                                                  │
╰─────────────────────────────────────────────────╯
  planner 348→75 | analyzer 136→55 | synthesizer 841→644 | $0.0156

> What's the total pipeline value at risk?

╭──────────────── Recommendation ─────────────────╮
│                                                  │
│  Pipeline Risk Analysis                          │
│                                                  │
│  Total At-Risk Revenue: $150K                    │
│                                                  │
│  CRITICAL RISK ($75K)                            │
│  - Delta Inc ($30K): 25 days stale, unclear      │
│    sentiment, risk score 0.707. Likely lost       │
│    without immediate re-engagement.              │
│  - Unknown Co ($45K): Risk score 1.0. Missing    │
│    stage, close date, account data. 40 days      │
│    stale. Recommend closing as lost.             │
│                                                  │
│  MODERATE RISK ($75K)                            │
│  - Omega SA ($75K): 15 days stale, zero          │
│    meetings, risk score 0.61. Recoverable with   │
│    immediate outreach and meeting scheduling.    │
│                                                  │
│  LOW RISK ($170K)                                │
│  - Beta Ltd ($120K): On track, positive          │
│    sentiment, 80% probability.                   │
│  - Acme Corp ($50K): Budget concerns noted but   │
│    engaged. Monitor closely.                     │
│                                                  │
│  Bottom line: $75K is likely recoverable with    │
│  action this week (Omega SA). $75K should be     │
│  written down (Delta + Unknown). $170K is        │
│  healthy.                                        │
│                                                  │
╰─────────────────────────────────────────────────╯
  planner 345→68 | analyzer 136→55 | synthesizer 831→590 | $0.0150

> exit
Goodbye.
```

---

## What This Demonstrates

**Data caching:** Google Drive download and ingestion happened once at startup. Both queries ran only the planner, analyzer, and synthesizer steps — no redundant file I/O or API calls.

**Independent queries:** Each query is analyzed independently. The second query ("total pipeline value at risk?") gets its own planner analysis type (`risk`), its own sentiment classification, and a tailored synthesis. There is no conversation history or multi-turn context — the efficiency gain is purely at the data layer.

**Cost for this session:**

| | Query 1 | Query 2 | Session Total |
|---|---------|---------|---------------|
| Input tokens | 1,325 | 1,312 | 2,637 |
| Output tokens | 774 | 713 | 1,487 |
| Cost | $0.0156 | $0.0150 | $0.0306 |

Two queries for ~$0.03 with zero redundant data loading. In the single-query `ask` mode, this would have required two separate Drive downloads and ingestion passes.

Model: `claude-sonnet-4-20250514`
