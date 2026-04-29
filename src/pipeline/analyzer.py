"""Hybrid analyzer: deterministic risk scoring + LLM sentiment classification."""

from __future__ import annotations

import logging
from datetime import date

from src.config import FAST_MODEL
from src.llm import call_llm_json
from src.models import AnalysisPlan, EnrichedDeal, ScopeMetrics
from src.pipeline.metrics import compute_scope_metrics

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

    # Each data-quality and risk flag amplifies the score by 0.1.
    # (stale_contact lives in risk_flags after the data-quality/risk split,
    # so we count both families to preserve the original risk contribution.)
    score += (len(deal.data_quality_flags) + len(deal.risk_flags)) * 0.1

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
        data, usage = call_llm_json(SENTIMENT_SYSTEM_PROMPT, user_prompt, model=FAST_MODEL)
        # Normalize keys to lowercase for matching
        return {k.strip().lower(): v for k, v in data.items()}, usage
    except Exception as e:
        logger.warning("Sentiment classification failed (%s), defaulting to 'unclear'", e)
        fallback = {company.lower(): "unclear" for company, _ in notes_with_data}
        return fallback, {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}


def _sort_deals(deals: list[EnrichedDeal], plan: AnalysisPlan) -> list[EnrichedDeal]:
    """Sort deals based on the planner's analysis_type."""
    analysis_type = plan.analysis_type

    if analysis_type == "priority":
        return sorted(
            deals,
            key=lambda d: (-(d.amount * d.probability), d.risk_score or 0.0),
        )

    if analysis_type == "actions":
        _far_future = date(9999, 12, 31)
        return sorted(
            deals,
            key=lambda d: (
                d.close_date or _far_future,
                -(d.last_contact_days or 0),
            ),
        )

    # "risk" and "general" both sort by risk_score descending
    return sorted(deals, key=lambda d: -(d.risk_score or 0.0))


def _apply_filters(deals: list[EnrichedDeal], plan: AnalysisPlan) -> list[EnrichedDeal]:
    """Apply planner-specified filters. Falls back to full list if nothing matches."""
    if not plan.filters_to_apply:
        return deals

    known_fields = EnrichedDeal.model_fields
    filtered = deals
    for key, value in plan.filters_to_apply.items():
        # min_ prefix: numeric threshold
        if key.startswith("min_"):
            field_name = key[4:]  # strip "min_"
            if field_name not in known_fields:
                continue
            filtered = [
                d for d in filtered
                if getattr(d, field_name, None) is not None
                and getattr(d, field_name) >= value
            ]
        else:
            # String field: case-insensitive contains
            if key not in known_fields:
                continue
            filter_val = str(value).lower()
            filtered = [
                d for d in filtered
                if getattr(d, key, None) is not None
                and filter_val in str(getattr(d, key)).lower()
            ]

    # Fallback: if filtering removed everything, return the original list
    if not filtered:
        return deals

    return filtered


def analyze(
    deals: list[EnrichedDeal],
    analysis_plan: AnalysisPlan,
    today: date | None = None,
) -> tuple[list[EnrichedDeal], ScopeMetrics, dict]:
    """Score, classify, filter, and aggregate.

    Returns (working_deals, scope_metrics, usage_dict). scope_metrics is computed
    over the final filtered slice so it matches what the user sees.
    """
    total_in_dataset = len(deals)

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

    # Sort and filter deals based on analysis plan
    working_deals = _sort_deals(working_deals, analysis_plan)
    working_deals = _apply_filters(working_deals, analysis_plan)

    # Deterministic aggregates over the exact slice the user will see.
    metrics = compute_scope_metrics(
        working_deals, analysis_plan, total_in_dataset, today=today
    )

    logger.info("Analyzed %d deals", len(working_deals))
    return working_deals, metrics, usage
