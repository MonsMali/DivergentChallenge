"""Tests for the analyzer pipeline step (deterministic scoring only)."""

from src.pipeline.analyzer import _compute_risk_score
from src.pipeline.ingester import ingest


def test_beta_ltd_lowest_risk():
    deals, _ = ingest("./data")
    scores = {d.company: _compute_risk_score(d) for d in deals}
    assert scores["Beta Ltd"] == min(scores.values()), "Beta Ltd should have lowest risk"


def test_unknown_co_highest_risk():
    deals, _ = ingest("./data")
    scores = {d.company: _compute_risk_score(d) for d in deals}
    # Unknown Co or Delta Inc should be highest risk
    top_risk = max(scores, key=scores.get)
    assert top_risk in ("Unknown Co", "Delta Inc"), f"Expected high-risk deal, got {top_risk}"


def test_risk_scores_bounded():
    deals, _ = ingest("./data")
    for d in deals:
        score = _compute_risk_score(d)
        assert 0.0 <= score <= 1.0, f"Deal {d.deal_id} score {score} out of bounds"


def test_delta_inc_higher_risk_than_acme():
    deals, _ = ingest("./data")
    scores = {d.company: _compute_risk_score(d) for d in deals}
    assert scores["Delta Inc"] > scores["Acme Corp"]
