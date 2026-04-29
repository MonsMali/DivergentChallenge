"""Tests for pydantic data models."""

from datetime import date

import pytest

from src.models import (
    Account,
    Activity,
    AnalysisPlan,
    DataQualityReport,
    Deal,
    EnrichedDeal,
    PipelineResult,
    ScopeMetrics,
    TokenUsage,
)


def test_account():
    acc = Account(company="Acme Corp", industry="SaaS", employees=200, region="EU")
    assert acc.company == "Acme Corp"

    acc_no_emp = Account(company="X", industry="Y", region="Z")
    assert acc_no_emp.employees is None


def test_deal_with_all_fields():
    deal = Deal(
        deal_id=1, company="Acme", stage="Proposal", amount=50000,
        owner="John", close_date=date(2026, 4, 15), probability=0.6,
    )
    assert deal.stage == "Proposal"


def test_deal_with_optional_none():
    deal = Deal(
        deal_id=5, company="Unknown Co", amount=45000,
        owner="Sarah", probability=0.4,
    )
    assert deal.stage is None
    assert deal.close_date is None
    assert deal.call_note is None


def test_deal_probability_validation():
    with pytest.raises(ValueError):
        Deal(deal_id=1, company="X", amount=1, owner="A", probability=1.5)


def test_activity():
    act = Activity(deal_id=1, last_contact_days=10, meetings=2, email_threads=5)
    assert act.meetings == 2


def test_enriched_deal_defaults():
    ed = EnrichedDeal(
        deal_id=5, company="Unknown Co", amount=45000,
        owner="Sarah", probability=0.4,
    )
    assert ed.has_account_match is False
    assert ed.data_quality_flags == []
    assert ed.risk_flags == []
    assert ed.risk_score is None
    assert ed.sentiment is None


def test_data_quality_report():
    dqr = DataQualityReport(
        total_deals=5, complete_deals=3, incomplete_deals=2,
        missing_fields_summary={"stage": 1, "close_date": 1},
        orphaned_companies=["Unknown Co"],
    )
    assert dqr.orphaned_companies == ["Unknown Co"]


def test_analysis_plan_defaults():
    plan = AnalysisPlan()
    assert plan.relevant_deals == "all"
    assert plan.analysis_type == "general"


def test_token_usage_add_step():
    usage = TokenUsage()
    usage.add_step("planner", input_tokens=500, output_tokens=100, cost=0.003)
    usage.add_step("synthesizer", input_tokens=800, output_tokens=300, cost=0.007)
    assert usage.total_input_tokens == 1300
    assert usage.total_output_tokens == 400
    assert len(usage.steps) == 2


def test_pipeline_result():
    result = PipelineResult(
        query="test",
        plan=AnalysisPlan(),
        enriched_deals=[],
        synthesis="No deals.",
        data_quality=DataQualityReport(total_deals=0, complete_deals=0, incomplete_deals=0),
        token_usage=TokenUsage(),
    )
    assert result.query == "test"
    # scope_metrics has a sensible default so existing call sites don't break.
    assert result.scope_metrics.deal_count == 0


def test_scope_metrics_defaults():
    m = ScopeMetrics()
    assert m.scope_description == "Portfolio"
    assert m.deal_count == 0
    assert m.total_pipeline == 0.0
    assert m.weighted_pipeline == 0.0
    assert m.overdue_count == 0
    assert m.stale_count == 0
    assert m.incomplete_data_count == 0
    assert m.owners == []
