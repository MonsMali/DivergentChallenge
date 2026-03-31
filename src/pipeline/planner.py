"""LLM-powered query understanding and analysis plan generation."""

from __future__ import annotations

import logging

from src.llm import call_llm_json
from src.models import AnalysisPlan, EnrichedDeal

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a RevOps planning agent. Given a user's business question and a "
    "summary of available deal data, produce an analysis plan.\n\n"
    "Respond ONLY with a JSON object matching this schema:\n"
    "{\n"
    '  "relevant_deals": [list of deal_id integers to analyze, or "all"],\n'
    '  "analysis_type": "risk" | "priority" | "actions" | "general",\n'
    '  "filters_to_apply": {optional dict of field->value filters},\n'
    '  "reasoning": "one sentence explaining your plan"\n'
    "}"
)


def _build_schema_summary(deals: list[EnrichedDeal]) -> str:
    """Build a concise schema summary to send to the LLM instead of raw data."""
    if not deals:
        return "No deals available."

    companies = [d.company for d in deals]
    stages = list({d.stage for d in deals if d.stage})
    owners = list({d.owner for d in deals})
    amounts = [d.amount for d in deals]
    close_dates = [str(d.close_date) for d in deals if d.close_date]
    probabilities = [d.probability for d in deals]
    deal_ids = [d.deal_id for d in deals]
    flags_all = []
    for d in deals:
        flags_all.extend(d.data_quality_flags)
    unique_flags = list(set(flags_all))

    return (
        f"Deal count: {len(deals)}\n"
        f"Deal IDs: {deal_ids}\n"
        f"Companies: {companies}\n"
        f"Stages: {stages}\n"
        f"Owners: {owners}\n"
        f"Amount range: ${min(amounts):,.0f} - ${max(amounts):,.0f}\n"
        f"Probability range: {min(probabilities)} - {max(probabilities)}\n"
        f"Close dates: {close_dates if close_dates else 'some missing'}\n"
        f"Data quality flags present: {unique_flags if unique_flags else 'none'}"
    )


def plan(query: str, deals: list[EnrichedDeal]) -> tuple[AnalysisPlan, dict]:
    """Generate an analysis plan from a user query and data summary.

    Returns (AnalysisPlan, usage_dict).
    """
    schema_summary = _build_schema_summary(deals)
    user_prompt = f"User question: {query}\n\nAvailable data:\n{schema_summary}"

    try:
        data, usage = call_llm_json(SYSTEM_PROMPT, user_prompt)
        analysis_plan = AnalysisPlan(**data)
    except Exception as e:
        logger.warning("Plan parsing failed (%s), using default plan", e)
        analysis_plan = AnalysisPlan(
            relevant_deals="all",
            analysis_type="general",
            reasoning="Fallback: analyzing all deals with general approach.",
        )
        usage = {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}

    logger.info("Plan: type=%s, reasoning=%s", analysis_plan.analysis_type, analysis_plan.reasoning)
    return analysis_plan, usage
