"""Tests for the planner's deterministic schema-summary builder.

The schema summary is what the LLM sees instead of raw deal data; we test it
deterministically without invoking Claude.
"""

from datetime import date

from src.models import EnrichedDeal
from src.pipeline.planner import _build_schema_summary


def _make_deal(**overrides) -> EnrichedDeal:
    defaults = dict(
        deal_id=1,
        company="Test Co",
        stage="Discovery",
        amount=10000.0,
        owner="Alice",
        close_date=date(2026, 6, 1),
        probability=0.5,
    )
    defaults.update(overrides)
    return EnrichedDeal(**defaults)


def test_schema_summary_surfaces_both_flag_families():
    deals = [
        _make_deal(
            deal_id=5,
            company="Unknown Co",
            data_quality_flags=["missing_stage", "no_account_match"],
            risk_flags=[],
        ),
        _make_deal(
            deal_id=3,
            company="Delta Inc",
            data_quality_flags=[],
            risk_flags=["stale_contact"],
        ),
    ]
    summary = _build_schema_summary(deals)

    # Both flag families must be visible to the planner so it can route
    # risk-oriented vs data-quality-oriented queries correctly.
    assert "Data quality flags present" in summary
    assert "missing_stage" in summary
    assert "no_account_match" in summary
    assert "Risk flags present" in summary
    assert "stale_contact" in summary


def test_schema_summary_handles_empty_flag_families():
    deals = [_make_deal(data_quality_flags=[], risk_flags=[])]
    summary = _build_schema_summary(deals)
    assert "Data quality flags present: none" in summary
    assert "Risk flags present: none" in summary
