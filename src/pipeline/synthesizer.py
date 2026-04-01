"""LLM-powered synthesis: generate actionable recommendations from enriched deals."""

from __future__ import annotations

import logging
from datetime import date

from src.llm import call_llm
from src.models import AnalysisPlan, EnrichedDeal

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a RevOps advisor for a sales team at a Private Equity portfolio company. "
    "Given enriched deal data with risk scores, sentiment analysis, and data quality "
    "flags, produce actionable recommendations.\n\n"
    "Rules:\n"
    "- Be specific: name deals, cite dollar amounts, mention concrete next steps with timeframes.\n"
    "- Do NOT produce generic advice like 'follow up with leads'.\n"
    "- If data is incomplete, acknowledge it explicitly and still provide the best recommendation.\n"
    "- Prioritize by business impact (deal size * probability, adjusted for risk).\n"
    "- Use a clear structure: priority ranking, then specific actions per deal."
)


def _format_deals_for_llm(deals: list[EnrichedDeal]) -> str:
    """Format enriched deals as readable text for the LLM."""
    lines = []
    for d in deals:
        flags_str = ", ".join(d.data_quality_flags) if d.data_quality_flags else "none"
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
            f"  Data quality flags: {flags_str}"
        )
    return "\n\n".join(lines)


def synthesize(
    deals: list[EnrichedDeal],
    query: str,
    analysis_plan: AnalysisPlan,
) -> tuple[str, dict]:
    """Generate the final actionable response.

    Returns (synthesis_text, usage_dict).
    """
    deals_text = _format_deals_for_llm(deals)
    user_prompt = (
        f"Today's date: {date.today().isoformat()}\n\n"
        f"User question: {query}\n\n"
        f"Analysis approach: {analysis_plan.analysis_type} — {analysis_plan.reasoning}\n\n"
        f"Deal data ({len(deals)} deals):\n\n{deals_text}"
    )

    text, usage = call_llm(SYSTEM_PROMPT, user_prompt)
    logger.info("Synthesis complete (%d tokens)", usage["output_tokens"])
    return text, usage
