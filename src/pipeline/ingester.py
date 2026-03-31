"""Deterministic ingestion: load, parse, normalize, merge, and flag data quality."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.models import DataQualityReport, EnrichedDeal

logger = logging.getLogger(__name__)


def _read_csv_safe(path: Path) -> pd.DataFrame | None:
    """Read a CSV file, returning None if it does not exist."""
    if not path.exists():
        logger.warning("File not found, skipping: %s", path.name)
        return None
    return pd.read_csv(path)


def _parse_call_notes(path: Path) -> dict[str, str]:
    """Parse call_notes.txt into {company: note} mapping."""
    notes: dict[str, str] = {}
    if not path.exists():
        logger.warning("call_notes.txt not found, skipping")
        return notes
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            company, note = line.split(":", 1)
            notes[company.strip().lower()] = note.strip()
    return notes


def ingest(data_dir: str) -> tuple[list[EnrichedDeal], DataQualityReport]:
    """Run the full ingestion pipeline on a data directory.

    Returns enriched deals and a data quality report.
    """
    base = Path(data_dir)

    # 1. Load CSVs
    deals_df = _read_csv_safe(base / "deals.csv")
    accounts_df = _read_csv_safe(base / "accounts.csv")
    activities_df = _read_csv_safe(base / "activities.csv")
    call_notes = _parse_call_notes(base / "call_notes.txt")

    if deals_df is None or deals_df.empty:
        logger.error("No deals data available")
        return [], DataQualityReport(total_deals=0, complete_deals=0, incomplete_deals=0)

    # 2. Merge deals + activities on deal_id (left join)
    if activities_df is not None:
        merged = deals_df.merge(activities_df, on="deal_id", how="left")
    else:
        merged = deals_df.copy()

    # 3. Merge with accounts on company name (left join)
    account_map: dict[str, dict] = {}
    if accounts_df is not None:
        for _, row in accounts_df.iterrows():
            account_map[row["company"].strip().lower()] = {
                "industry": row["industry"],
                "employees": row.get("employees"),
                "region": row["region"],
            }

    # 4. Build EnrichedDeal objects
    enriched_deals: list[EnrichedDeal] = []
    missing_fields_summary: dict[str, int] = {}
    orphaned: list[str] = []

    for _, row in merged.iterrows():
        company_key = str(row["company"]).strip().lower()
        account = account_map.get(company_key)
        note = call_notes.get(company_key)

        flags: list[str] = []
        if pd.isna(row.get("stage")) or row.get("stage") == "":
            flags.append("missing_stage")
            missing_fields_summary["stage"] = missing_fields_summary.get("stage", 0) + 1
        if pd.isna(row.get("close_date")) or row.get("close_date") == "":
            flags.append("missing_close_date")
            missing_fields_summary["close_date"] = missing_fields_summary.get("close_date", 0) + 1
        if account is None:
            flags.append("no_account_match")
            if row["company"] not in orphaned:
                orphaned.append(row["company"])
        if pd.isna(row.get("last_contact_days")):
            flags.append("no_activity_data")
        if note is None:
            flags.append("no_call_note")

        last_contact = None if pd.isna(row.get("last_contact_days")) else int(row["last_contact_days"])
        if last_contact is not None and last_contact > 14:
            flags.append("stale_contact")

        close_date = None
        raw_cd = row.get("close_date")
        if pd.notna(raw_cd) and raw_cd != "":
            close_date = pd.to_datetime(raw_cd).date()

        stage = None
        raw_stage = row.get("stage")
        if pd.notna(raw_stage) and raw_stage != "":
            stage = str(raw_stage)

        ed = EnrichedDeal(
            deal_id=int(row["deal_id"]),
            company=row["company"],
            stage=stage,
            amount=float(row["amount"]),
            owner=row["owner"],
            close_date=close_date,
            probability=float(row["probability"]),
            call_note=note,
            industry=account["industry"] if account else None,
            employees=int(account["employees"]) if account and pd.notna(account.get("employees")) else None,
            region=account["region"] if account else None,
            last_contact_days=last_contact,
            meetings=None if pd.isna(row.get("meetings")) else int(row["meetings"]),
            email_threads=None if pd.isna(row.get("email_threads")) else int(row["email_threads"]),
            has_account_match=account is not None,
            data_quality_flags=flags,
        )
        enriched_deals.append(ed)

    complete = sum(1 for d in enriched_deals if not d.data_quality_flags)
    incomplete = len(enriched_deals) - complete

    report = DataQualityReport(
        total_deals=len(enriched_deals),
        complete_deals=complete,
        incomplete_deals=incomplete,
        missing_fields_summary=missing_fields_summary,
        orphaned_companies=orphaned,
    )
    logger.info(
        "Ingested %d deals (%d complete, %d with issues)",
        report.total_deals, report.complete_deals, report.incomplete_deals,
    )
    return enriched_deals, report
