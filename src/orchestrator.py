"""Pipeline orchestrator: runs ingester -> planner -> analyzer -> synthesizer."""

from __future__ import annotations

import logging

import click

from src.models import AnalysisPlan, PipelineResult, TokenUsage
from src.pipeline.analyzer import analyze
from src.pipeline.ingester import ingest
from src.pipeline.planner import plan
from src.pipeline.synthesizer import synthesize
from src.sources.gdrive import load_from_gdrive
from src.sources.local import load_from_local

logger = logging.getLogger(__name__)


def run_pipeline(
    query: str,
    source: str = "local",
    data_dir: str = "./data",
    folder_id: str | None = None,
    credentials: str = "credentials.json",
    verbose: bool = False,
) -> PipelineResult:
    """Execute the full RevOps pipeline and return structured results."""
    token_usage = TokenUsage()

    # Step 1: Resolve data source
    if source == "gdrive":
        if not folder_id:
            raise click.UsageError("--folder-id is required when using --source gdrive")
        data_path = load_from_gdrive(folder_id, credentials)
    else:
        data_path = load_from_local(data_dir)

    if verbose:
        click.echo(f"\n--- Data source: {source} ({data_path}) ---")

    # Step 2: Ingest
    enriched_deals, quality_report = ingest(data_path)

    if verbose:
        click.echo(f"\n--- Ingester: {quality_report.total_deals} deals loaded ---")
        click.echo(f"  Complete: {quality_report.complete_deals}")
        click.echo(f"  Incomplete: {quality_report.incomplete_deals}")
        if quality_report.orphaned_companies:
            click.echo(f"  Orphaned companies: {quality_report.orphaned_companies}")
        if quality_report.missing_fields_summary:
            click.echo(f"  Missing fields: {quality_report.missing_fields_summary}")

    if not enriched_deals:
        return PipelineResult(
            query=query,
            plan=AnalysisPlan(),
            enriched_deals=[],
            synthesis="No deals available to analyze.",
            data_quality=quality_report,
            token_usage=token_usage,
        )

    # Step 3: Plan
    analysis_plan, plan_usage = plan(query, enriched_deals)
    token_usage.add_step("planner", **plan_usage)

    if verbose:
        click.echo(f"\n--- Planner ---")
        click.echo(f"  Analysis type: {analysis_plan.analysis_type}")
        click.echo(f"  Relevant deals: {analysis_plan.relevant_deals}")
        click.echo(f"  Reasoning: {analysis_plan.reasoning}")

    # Step 4: Analyze
    analyzed_deals, analyzer_usage = analyze(enriched_deals, analysis_plan)
    token_usage.add_step("analyzer", **analyzer_usage)

    if verbose:
        click.echo(f"\n--- Analyzer ---")
        for d in analyzed_deals:
            click.echo(
                f"  Deal #{d.deal_id} ({d.company}): "
                f"risk={d.risk_score}, sentiment={d.sentiment}"
            )

    # Step 5: Synthesize
    synthesis, synth_usage = synthesize(analyzed_deals, query, analysis_plan)
    token_usage.add_step("synthesizer", **synth_usage)

    if verbose:
        click.echo(f"\n--- Token Usage ---")
        for step_name, step_usage in token_usage.steps.items():
            click.echo(
                f"  {step_name}: {step_usage.input_tokens} in / "
                f"{step_usage.output_tokens} out / ${step_usage.cost:.6f}"
            )
        click.echo(
            f"  TOTAL: {token_usage.total_input_tokens} in / "
            f"{token_usage.total_output_tokens} out / ${token_usage.total_cost:.6f}"
        )

    return PipelineResult(
        query=query,
        plan=analysis_plan,
        enriched_deals=analyzed_deals,
        synthesis=synthesis,
        data_quality=quality_report,
        token_usage=token_usage,
    )
