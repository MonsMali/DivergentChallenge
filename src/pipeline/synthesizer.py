"""LLM-powered synthesis: generate actionable recommendations from enriched deals."""

from __future__ import annotations

import logging
from datetime import date

from src.llm import call_llm
from src.models import AnalysisPlan, EnrichedDeal, ScopeMetrics

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a RevOps advisor at a Private Equity fund. Your audience is the fund's "
    "operating team and portfolio company sales leadership.\n\n"
    "Given enriched deal data with risk scores, sentiment, data quality flags, risk "
    "flags, and authoritative scope metrics, produce actionable recommendations.\n\n"
    "Rules:\n"
    "- Name deals, cite dollar amounts, assign owners, and give concrete next steps with dates.\n"
    "- Do NOT produce generic advice like 'follow up with leads'.\n"
    "- Use the provided Scope metrics verbatim. Do NOT recompute totals, weighted "
    "values, overdue counts, or stale counts. If you reference these numbers in your "
    "narrative, copy them from the Scope metrics block exactly.\n"
    "- Keep `data_quality_flags` (record completeness) and `risk_flags` (sales risk "
    "signals like stale_contact) distinct in your reasoning. A stale contact is a "
    "sales-risk problem, not a data-quality problem.\n"
    "- If data is incomplete, acknowledge it explicitly and still provide the best recommendation.\n"
    "- Prioritize by business impact (deal size * probability, adjusted for risk).\n"
    "- Structure: priority ranking, then specific actions per deal.\n"
    "- Professional tone.\n"
    "- Respond in the same language as the user's question."
)


def _format_deals_for_llm(deals: list[EnrichedDeal]) -> str:
    """Format enriched deals as readable text for the LLM."""
    lines = []
    for d in deals:
        quality_str = ", ".join(d.data_quality_flags) if d.data_quality_flags else "none"
        risk_str = ", ".join(d.risk_flags) if d.risk_flags else "none"
        lines.append(
            f"Deal #{d.deal_id} — {d.company}\n"
            f"  Stage: {d.stage or 'MISSING'}  |  Amount: ${d.amount:,.0f}  |  "
            f"Probability: {d.probability}  |  Owner: {d.owner}\n"
            f"  Close date: {d.close_date or 'MISSING'}  |  "
            f"Industry: {d.industry or 'unknown'}  |  Region: {d.region or 'unknown'}\n"
            f"  Last contact: {d.last_contact_days or 'N/A'} days ago  |  "
            f"Meetings: {d.meetings or 0}  |  Email threads: {d.email_threads or 0}\n"
            f"  Call note: {d.call_note or 'none'}\n"
            f"  Risk score: {d.risk_score or 'N/A'}  |  Sentiment: {d.sentiment or 'N/A'}\n"
            f"  Data quality flags: {quality_str}\n"
            f"  Risk flags: {risk_str}"
        )
    return "\n\n".join(lines)


def _format_scope_metrics(metrics: ScopeMetrics) -> str:
    """Render the deterministic scope metrics block sent to the LLM."""
    return (
        f"Scope: {metrics.scope_description}\n"
        f"  Total pipeline:    ${metrics.total_pipeline:,.0f}\n"
        f"  Weighted pipeline: ${metrics.weighted_pipeline:,.0f}\n"
        f"  Deals in scope: {metrics.deal_count}\n"
        f"  Overdue close dates: {metrics.overdue_count}\n"
        f"  Stale contact (>14d): {metrics.stale_count}\n"
        f"  Records with data gaps: {metrics.incomplete_data_count}\n"
        f"  Owners in scope: {', '.join(metrics.owners) if metrics.owners else 'none'}"
    )


def synthesize(
    deals: list[EnrichedDeal],
    query: str,
    analysis_plan: AnalysisPlan,
    scope_metrics: ScopeMetrics,
    today: date | None = None,
) -> tuple[str, dict]:
    """Generate the final actionable response.

    `today` is injectable so tests can pin the synthesizer's date awareness.
    """
    today = today or date.today()
    deals_text = _format_deals_for_llm(deals)
    scope_text = _format_scope_metrics(scope_metrics)
    user_prompt = (
        f"Today's date: {today.isoformat()}\n\n"
        f"User question: {query}\n\n"
        f"Analysis approach: {analysis_plan.analysis_type} — {analysis_plan.reasoning}\n\n"
        f"Scope metrics (authoritative — do not recompute):\n{scope_text}\n\n"
        f"Deal data ({len(deals)} deals):\n\n{deals_text}"
    )

    text, usage = call_llm(SYSTEM_PROMPT, user_prompt)
    logger.info("Synthesis complete (%d tokens)", usage["output_tokens"])
    return text, usage
