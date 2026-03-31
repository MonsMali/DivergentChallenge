"""Tests for the ingester pipeline step."""

from src.pipeline.ingester import ingest


def test_ingest_all_deals_produced():
    deals, report = ingest("./data")
    assert len(deals) == 5
    assert report.total_deals == 5


def test_unknown_co_flagged():
    deals, report = ingest("./data")
    unknown = [d for d in deals if d.company == "Unknown Co"][0]
    assert "missing_stage" in unknown.data_quality_flags
    assert "missing_close_date" in unknown.data_quality_flags
    assert "no_account_match" in unknown.data_quality_flags
    assert unknown.has_account_match is False
    assert "Unknown Co" in report.orphaned_companies


def test_beta_ltd_fully_enriched():
    deals, _ = ingest("./data")
    beta = [d for d in deals if d.company == "Beta Ltd"][0]
    assert beta.has_account_match is True
    assert beta.call_note is not None
    assert "strong interest" in beta.call_note.lower()
    assert beta.meetings == 5
    assert beta.last_contact_days == 2


def test_delta_inc_stale_contact():
    deals, _ = ingest("./data")
    delta = [d for d in deals if d.company == "Delta Inc"][0]
    assert "stale_contact" in delta.data_quality_flags
    assert delta.last_contact_days == 25


def test_data_quality_report():
    _, report = ingest("./data")
    assert report.incomplete_deals > 0
    assert "stage" in report.missing_fields_summary
    assert "close_date" in report.missing_fields_summary
