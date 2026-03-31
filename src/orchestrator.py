"""Pipeline orchestrator: data loading and analysis execution."""

from __future__ import annotations

import logging

from src.config import DEFAULT_GDRIVE_FOLDER_ID
from src.models import (
    AnalysisPlan,
    DataQualityReport,
    EnrichedDeal,
    PipelineResult,
    TokenUsage,
)
from src.pipeline.analyzer import analyze
from src.pipeline.ingester import ingest
from src.pipeline.planner import plan
from src.pipeline.synthesizer import synthesize
from src.sources.gdrive import load_from_gdrive

logger = logging.getLogger(__name__)


def load_data(
    folder_id: str | None = None,
    credentials: str = "credentials.json",
) -> tuple[list[EnrichedDeal], DataQualityReport]:
    """Download data from Google Drive and ingest it."""
    drive_folder = folder_id or DEFAULT_GDRIVE_FOLDER_ID
    data_path = load_from_gdrive(drive_folder, credentials)
    return ingest(data_path)


def run_analysis(
    query: str,
    enriched_deals: list[EnrichedDeal],
    quality_report: DataQualityReport,
) -> PipelineResult:
    """Run planner -> analyzer -> synthesizer on pre-ingested deals."""
    token_usage = TokenUsage()

    if not enriched_deals:
        return PipelineResult(
            query=query,
            plan=AnalysisPlan(),
            enriched_deals=[],
            synthesis="No deals available to analyze.",
            data_quality=quality_report,
            token_usage=token_usage,
        )

    analysis_plan, plan_usage = plan(query, enriched_deals)
    token_usage.add_step("planner", **plan_usage)

    analyzed_deals, analyzer_usage = analyze(enriched_deals, analysis_plan)
    token_usage.add_step("analyzer", **analyzer_usage)

    synthesis, synth_usage = synthesize(analyzed_deals, query, analysis_plan)
    token_usage.add_step("synthesizer", **synth_usage)

    return PipelineResult(
        query=query,
        plan=analysis_plan,
        enriched_deals=analyzed_deals,
        synthesis=synthesis,
        data_quality=quality_report,
        token_usage=token_usage,
    )
