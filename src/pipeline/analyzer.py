"""Hybrid analyzer: deterministic risk scoring + LLM sentiment classification."""

from __future__ import annotations

import logging

from src.llm import call_llm_json
from src.models import AnalysisPlan, EnrichedDeal

logger = logging.getLogger(__name__)

SENTIMENT_SYSTEM_PROMPT = (
    "You are a sales note analyst. Given a set of call notes, classify the "
    "sentiment of each as one of: positive, cautious, negative, neutral, unclear.\n\n"
    "Respond ONLY with a JSON object mapping company name to sentiment."
)


def _compute_risk_score(deal: EnrichedDeal) -> float:
    """Compute a risk score from 0.0 (safe) to 1.0 (high risk)."""
    score = 0.0

    # Last contact days: 0 at 0 days, 1.0 at 30+ days
    if deal.last_contact_days is not None:
        score += min(deal.last_contact_days / 30.0, 1.0) * 0.25
    else:
        score += 0.25  # no data = assume risk

    # Meetings: 0 = high risk, 3+ = low risk
    if deal.meetings is not None:
        meeting_risk = max(0.0, 1.0 - deal.meetings / 3.0)
        score += meeting_risk * 0.2
    else:
        score += 0.2

    # Email threads: 0-1 = high risk, 5+ = low risk
    if deal.email_threads is not None:
        email_risk = max(0.0, 1.0 - deal.email_threads / 5.0)
        score += email_risk * 0.15
    else:
        score += 0.15

    # Probability: inverted (low prob = high risk)
    score += (1.0 - deal.probability) * 0.25

    # Data quality flags: each adds 0.1
    score += len(deal.data_quality_flags) * 0.1

    return min(round(score, 3), 1.0)


def _classify_sentiment(deals: list[EnrichedDeal]) -> tuple[dict[str, str], dict]:
    """Classify sentiment for all call notes in a single LLM call.

    Returns (company->sentiment mapping, usage_dict).
    """
    notes_with_data = [(d.company, d.call_note) for d in deals if d.call_note]
    if not notes_with_data:
        return {}, {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}

    notes_text = "\n".join(f"- {company}: {note}" for company, note in notes_with_data)
    user_prompt = f"Call notes:\n{notes_text}"

    try:
        data, usage = call_llm_json(SENTIMENT_SYSTEM_PROMPT, user_prompt)
        # Normalize keys to lowercase for matching
        return {k.strip().lower(): v for k, v in data.items()}, usage
    except Exception as e:
        logger.warning("Sentiment classification failed (%s), defaulting to 'unclear'", e)
        fallback = {company.lower(): "unclear" for company, _ in notes_with_data}
        return fallback, {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}


def analyze(
    deals: list[EnrichedDeal],
    analysis_plan: AnalysisPlan,
) -> tuple[list[EnrichedDeal], dict]:
    """Score and classify deals. Returns (updated deals, usage_dict)."""
    # Filter deals based on plan
    if isinstance(analysis_plan.relevant_deals, list):
        relevant_ids = set(analysis_plan.relevant_deals)
        working_deals = [d for d in deals if d.deal_id in relevant_ids]
        # Still score all deals for completeness
        if not working_deals:
            working_deals = deals
    else:
        working_deals = deals

    # Deterministic: risk scoring
    for deal in working_deals:
        deal.risk_score = _compute_risk_score(deal)

    # LLM: sentiment classification (single batched call)
    sentiment_map, usage = _classify_sentiment(working_deals)
    for deal in working_deals:
        deal.sentiment = sentiment_map.get(deal.company.strip().lower(), "unclear")

    logger.info("Analyzed %d deals", len(working_deals))
    return working_deals, usage
