"""LLM-powered query understanding and analysis plan generation."""

from __future__ import annotations

import logging

from src.config import FAST_MODEL
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
    '  "filters_to_apply": {dict of field->scalar value filters},\n'
    '  "reasoning": "one sentence explaining your plan"\n'
    "}\n\n"
    "Critical rules for filters_to_apply:\n"
    "- If the question targets a specific OWNER (e.g. \"What should John focus "
    "on?\"), set filters_to_apply={\"owner\": \"John\"}. The downstream layer "
    "uses this to scope the headline metrics shown to the user.\n"
    "- If the question targets a specific REGION, INDUSTRY, or STAGE, use the "
    "matching field name with a single scalar string value (e.g. "
    "{\"region\": \"EU\"} or {\"stage\": \"Proposal\"}).\n"
    "- For numeric thresholds, use the prefix \"min_\" (e.g. {\"min_amount\": 50000}).\n"
    "- Use ONLY scalar string or numeric values. Do NOT pass lists or dicts as "
    "filter values, and do NOT use field names like data_quality_flags or "
    "risk_flags as filter keys.\n"
    "- For portfolio-wide questions (\"summarize everything\", \"what looks at "
    "risk overall\"), leave filters_to_apply as an empty object {}."
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
    quality_flags_all: list[str] = []
    risk_flags_all: list[str] = []
    for d in deals:
        quality_flags_all.extend(d.data_quality_flags)
        risk_flags_all.extend(d.risk_flags)
    unique_quality_flags = sorted(set(quality_flags_all))
    unique_risk_flags = sorted(set(risk_flags_all))

    return (
        f"Deal count: {len(deals)}\n"
        f"Deal IDs: {deal_ids}\n"
        f"Companies: {companies}\n"
        f"Stages: {stages}\n"
        f"Owners: {owners}\n"
        f"Amount range: ${min(amounts):,.0f} - ${max(amounts):,.0f}\n"
        f"Probability range: {min(probabilities)} - {max(probabilities)}\n"
        f"Close dates: {close_dates if close_dates else 'some missing'}\n"
        f"Data quality flags present: {unique_quality_flags if unique_quality_flags else 'none'}\n"
        f"Risk flags present: {unique_risk_flags if unique_risk_flags else 'none'}"
    )


def plan(query: str, deals: list[EnrichedDeal]) -> tuple[AnalysisPlan, dict]:
    """Generate an analysis plan from a user query and data summary.

    Returns (AnalysisPlan, usage_dict).
    """
    schema_summary = _build_schema_summary(deals)
    user_prompt = f"User question: {query}\n\nAvailable data:\n{schema_summary}"

    try:
        data, usage = call_llm_json(SYSTEM_PROMPT, user_prompt, model=FAST_MODEL)
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
