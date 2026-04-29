"""Deterministic aggregate metrics over the analyzer's filtered deal slice.

These numbers are authoritative. The CLI renders them in a fixed preamble; the
synthesizer receives them as inputs with a "do not recompute" instruction. This
keeps headline figures (weighted pipeline, overdue counts, etc.) out of the
LLM's arithmetic responsibility.
"""

from __future__ import annotations

from datetime import date

from src.models import AnalysisPlan, EnrichedDeal, ScopeMetrics

_INCOMPLETE_RECORD_FLAGS = {"missing_stage", "missing_close_date", "no_account_match"}


def _build_scope_description(
    plan: AnalysisPlan,
    scoped_count: int,
    total_in_dataset: int,
) -> str:
    """Label the slice the user is being shown.

    A filter that didn't actually reduce the deal count (or fell back to the
    full list inside the analyzer) is treated as portfolio scope, since the
    user is in fact seeing the whole portfolio.
    """
    if scoped_count == total_in_dataset:
        return f"Portfolio ({scoped_count} deals)"

    if plan.filters_to_apply:
        # Render scalar filters cleanly; skip nested/list values that come from
        # malformed planner output and would otherwise produce noisy labels.
        scalar_parts = [
            f"{k}={v}"
            for k, v in plan.filters_to_apply.items()
            if not isinstance(v, (list, dict))
        ]
        if scalar_parts:
            return (
                f"Filtered: {', '.join(scalar_parts)} "
                f"({scoped_count} of {total_in_dataset} deals)"
            )

    if isinstance(plan.relevant_deals, list):
        return f"Selected deals ({scoped_count} of {total_in_dataset})"

    return f"{scoped_count} of {total_in_dataset} deals"


def compute_scope_metrics(
    deals: list[EnrichedDeal],
    plan: AnalysisPlan,
    total_in_dataset: int,
    today: date | None = None,
) -> ScopeMetrics:
    """Compute deterministic aggregates over the exact deal slice the user sees.

    Scope is whatever the analyzer produced after planner-driven filtering. For
    "Summarize everything" this is the full portfolio; for "What should John
    focus on?" this is John's subset only.
    """
    today = today or date.today()

    return ScopeMetrics(
        scope_description=_build_scope_description(plan, len(deals), total_in_dataset),
        deal_count=len(deals),
        total_pipeline=sum(d.amount for d in deals),
        weighted_pipeline=sum(d.amount * d.probability for d in deals),
        overdue_count=sum(
            1 for d in deals if d.close_date is not None and d.close_date < today
        ),
        stale_count=sum(1 for d in deals if "stale_contact" in d.risk_flags),
        incomplete_data_count=sum(
            1 for d in deals
            if any(f in d.data_quality_flags for f in _INCOMPLETE_RECORD_FLAGS)
        ),
        owners=sorted({d.owner for d in deals}),
    )
