"""Tests for the analyzer pipeline step (deterministic scoring only)."""

from datetime import date

from src.models import AnalysisPlan, EnrichedDeal
from src.pipeline.analyzer import _compute_risk_score
from src.pipeline.metrics import compute_scope_metrics
from tests.conftest import requires_gdrive


def _make_deal(**overrides) -> EnrichedDeal:
    """Build an EnrichedDeal with sensible defaults, overridable per-field."""
    defaults = dict(
        deal_id=1,
        company="Test Co",
        stage="Discovery",
        amount=10000.0,
        owner="Alice",
        close_date=date(2026, 6, 1),
        probability=0.5,
        risk_score=0.5,
        last_contact_days=10,
        meetings=2,
        email_threads=3,
    )
    defaults.update(overrides)
    return EnrichedDeal(**defaults)


def test_sort_deals_risk_highest_first():
    from src.pipeline.analyzer import _sort_deals

    deals = [
        _make_deal(deal_id=1, risk_score=0.3),
        _make_deal(deal_id=2, risk_score=0.9),
        _make_deal(deal_id=3, risk_score=0.6),
    ]
    plan = AnalysisPlan(analysis_type="risk")
    sorted_deals = _sort_deals(deals, plan)
    assert [d.deal_id for d in sorted_deals] == [2, 3, 1]


def test_sort_deals_priority_by_weighted_value():
    from src.pipeline.analyzer import _sort_deals

    deals = [
        _make_deal(deal_id=1, amount=100000, probability=0.3, risk_score=0.5),  # value=30000
        _make_deal(deal_id=2, amount=50000, probability=0.8, risk_score=0.2),   # value=40000
        _make_deal(deal_id=3, amount=200000, probability=0.1, risk_score=0.9),  # value=20000
    ]
    plan = AnalysisPlan(analysis_type="priority")
    sorted_deals = _sort_deals(deals, plan)
    assert [d.deal_id for d in sorted_deals] == [2, 1, 3]


def test_sort_deals_priority_tiebreaker_risk():
    from src.pipeline.analyzer import _sort_deals

    deals = [
        _make_deal(deal_id=1, amount=50000, probability=0.8, risk_score=0.7),  # value=40000
        _make_deal(deal_id=2, amount=40000, probability=1.0, risk_score=0.2),  # value=40000
    ]
    plan = AnalysisPlan(analysis_type="priority")
    sorted_deals = _sort_deals(deals, plan)
    # Same weighted value, lower risk wins
    assert [d.deal_id for d in sorted_deals] == [2, 1]


def test_sort_deals_actions_by_close_date_then_staleness():
    from src.pipeline.analyzer import _sort_deals

    deals = [
        _make_deal(deal_id=1, close_date=date(2026, 6, 30), last_contact_days=25),
        _make_deal(deal_id=2, close_date=date(2026, 4, 10), last_contact_days=2),
        _make_deal(deal_id=3, close_date=None, last_contact_days=15),
    ]
    plan = AnalysisPlan(analysis_type="actions")
    sorted_deals = _sort_deals(deals, plan)
    # April 10 first, June 30 second, None last
    assert [d.deal_id for d in sorted_deals] == [2, 1, 3]


def test_sort_deals_actions_none_dates_sorted_by_staleness():
    from src.pipeline.analyzer import _sort_deals

    deals = [
        _make_deal(deal_id=1, close_date=None, last_contact_days=5),
        _make_deal(deal_id=2, close_date=None, last_contact_days=20),
    ]
    plan = AnalysisPlan(analysis_type="actions")
    sorted_deals = _sort_deals(deals, plan)
    # Both None dates, higher staleness first
    assert [d.deal_id for d in sorted_deals] == [2, 1]


def test_sort_deals_general_same_as_risk():
    from src.pipeline.analyzer import _sort_deals

    deals = [
        _make_deal(deal_id=1, risk_score=0.2),
        _make_deal(deal_id=2, risk_score=0.8),
    ]
    plan = AnalysisPlan(analysis_type="general")
    sorted_deals = _sort_deals(deals, plan)
    assert [d.deal_id for d in sorted_deals] == [2, 1]


def test_apply_filters_string_contains_case_insensitive():
    from src.pipeline.analyzer import _apply_filters

    deals = [
        _make_deal(deal_id=1, stage="Discovery"),
        _make_deal(deal_id=2, stage="Contract Negotiation"),
        _make_deal(deal_id=3, stage="Closed Won"),
    ]
    plan = AnalysisPlan(filters_to_apply={"stage": "negotiation"})
    filtered = _apply_filters(deals, plan)
    assert [d.deal_id for d in filtered] == [2]


def test_apply_filters_min_threshold():
    from src.pipeline.analyzer import _apply_filters

    deals = [
        _make_deal(deal_id=1, amount=30000),
        _make_deal(deal_id=2, amount=75000),
        _make_deal(deal_id=3, amount=120000),
    ]
    plan = AnalysisPlan(filters_to_apply={"min_amount": 50000})
    filtered = _apply_filters(deals, plan)
    assert [d.deal_id for d in filtered] == [2, 3]


def test_apply_filters_unknown_key_ignored():
    from src.pipeline.analyzer import _apply_filters

    deals = [_make_deal(deal_id=1), _make_deal(deal_id=2)]
    plan = AnalysisPlan(filters_to_apply={"nonexistent_field": "value"})
    filtered = _apply_filters(deals, plan)
    assert len(filtered) == 2


def test_apply_filters_empty_result_falls_back():
    from src.pipeline.analyzer import _apply_filters

    deals = [
        _make_deal(deal_id=1, amount=10000),
        _make_deal(deal_id=2, amount=20000),
    ]
    plan = AnalysisPlan(filters_to_apply={"min_amount": 999999})
    filtered = _apply_filters(deals, plan)
    assert len(filtered) == 2


def test_apply_filters_multiple_filters():
    from src.pipeline.analyzer import _apply_filters

    deals = [
        _make_deal(deal_id=1, stage="Discovery", amount=30000),
        _make_deal(deal_id=2, stage="Contract Negotiation", amount=75000),
        _make_deal(deal_id=3, stage="Contract Negotiation", amount=20000),
    ]
    plan = AnalysisPlan(filters_to_apply={"stage": "negotiation", "min_amount": 50000})
    filtered = _apply_filters(deals, plan)
    assert [d.deal_id for d in filtered] == [2]


def test_apply_filters_empty_dict_no_change():
    from src.pipeline.analyzer import _apply_filters

    deals = [_make_deal(deal_id=1), _make_deal(deal_id=2)]
    plan = AnalysisPlan(filters_to_apply={})
    filtered = _apply_filters(deals, plan)
    assert len(filtered) == 2


@requires_gdrive
def test_beta_ltd_lowest_risk(ingested_data):
    deals, _ = ingested_data
    scores = {d.company: _compute_risk_score(d) for d in deals}
    assert scores["Beta Ltd"] == min(scores.values()), "Beta Ltd should have lowest risk"


@requires_gdrive
def test_unknown_co_highest_risk(ingested_data):
    deals, _ = ingested_data
    scores = {d.company: _compute_risk_score(d) for d in deals}
    # Unknown Co or Delta Inc should be highest risk
    top_risk = max(scores, key=scores.get)
    assert top_risk in ("Unknown Co", "Delta Inc"), f"Expected high-risk deal, got {top_risk}"


@requires_gdrive
def test_risk_scores_bounded(ingested_data):
    deals, _ = ingested_data
    for d in deals:
        score = _compute_risk_score(d)
        assert 0.0 <= score <= 1.0, f"Deal {d.deal_id} score {score} out of bounds"


@requires_gdrive
def test_delta_inc_higher_risk_than_acme(ingested_data):
    deals, _ = ingested_data
    scores = {d.company: _compute_risk_score(d) for d in deals}
    assert scores["Delta Inc"] > scores["Acme Corp"]


# ── ScopeMetrics tests ──────────────────────────────────────────────────


def _fixed_today() -> date:
    return date(2026, 4, 29)


def test_compute_scope_metrics_full_portfolio():
    deals = [
        _make_deal(deal_id=1, owner="John", amount=50000, probability=0.6,
                   close_date=date(2026, 4, 1)),  # overdue vs fixed_today
        _make_deal(deal_id=2, owner="Sarah", amount=120000, probability=0.8,
                   close_date=date(2026, 5, 30)),
        _make_deal(deal_id=3, owner="John", amount=75000, probability=0.5,
                   close_date=date(2026, 6, 30),
                   risk_flags=["stale_contact"], last_contact_days=25),
    ]
    plan = AnalysisPlan()  # relevant_deals="all", no filters
    m = compute_scope_metrics(deals, plan, total_in_dataset=3, today=_fixed_today())

    assert m.scope_description == "Portfolio (3 deals)"
    assert m.deal_count == 3
    assert m.total_pipeline == 245000.0
    # 50000*0.6 + 120000*0.8 + 75000*0.5 = 30000 + 96000 + 37500 = 163500
    assert m.weighted_pipeline == 163500.0
    assert m.overdue_count == 1
    assert m.stale_count == 1
    assert m.incomplete_data_count == 0
    assert m.owners == ["John", "Sarah"]


def test_compute_scope_metrics_filtered_owner():
    deals = [
        _make_deal(deal_id=1, owner="John", amount=50000, probability=0.6),
        _make_deal(deal_id=3, owner="John", amount=75000, probability=0.5),
    ]
    plan = AnalysisPlan(filters_to_apply={"owner": "John"})
    m = compute_scope_metrics(deals, plan, total_in_dataset=5, today=_fixed_today())

    assert "John" in m.scope_description
    assert "2 of 5" in m.scope_description
    assert m.deal_count == 2
    assert m.total_pipeline == 125000.0
    assert m.weighted_pipeline == 67500.0  # 30000 + 37500
    assert m.owners == ["John"]


def test_compute_scope_metrics_counts_data_gaps_separately_from_staleness():
    deals = [
        _make_deal(deal_id=5, owner="Sarah",
                   data_quality_flags=["missing_stage", "no_account_match"],
                   risk_flags=[]),
        _make_deal(deal_id=3, owner="John",
                   data_quality_flags=[],
                   risk_flags=["stale_contact"]),
    ]
    plan = AnalysisPlan()
    m = compute_scope_metrics(deals, plan, total_in_dataset=2, today=_fixed_today())

    # Deal 5 has data gaps; Deal 3 is stale (risk, not data quality).
    assert m.incomplete_data_count == 1
    assert m.stale_count == 1


def test_compute_scope_metrics_filter_that_didnt_reduce_is_portfolio():
    """Planner-supplied filter that fell back to the full list reads as portfolio."""
    deals = [
        _make_deal(deal_id=1, owner="John"),
        _make_deal(deal_id=2, owner="Sarah"),
    ]
    plan = AnalysisPlan(filters_to_apply={"data_quality_flags": ["missing_stage"]})
    m = compute_scope_metrics(deals, plan, total_in_dataset=2, today=_fixed_today())
    assert m.scope_description == "Portfolio (2 deals)"


def test_compute_scope_metrics_today_is_injectable():
    deals = [
        _make_deal(deal_id=1, close_date=date(2026, 5, 1)),
    ]
    plan = AnalysisPlan()
    # On 2026-04-29 the deal is not overdue.
    m_before = compute_scope_metrics(deals, plan, 1, today=date(2026, 4, 29))
    assert m_before.overdue_count == 0
    # On 2026-05-15 it is.
    m_after = compute_scope_metrics(deals, plan, 1, today=date(2026, 5, 15))
    assert m_after.overdue_count == 1
