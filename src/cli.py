"""CLI entry point for the RevOps Copilot."""

from __future__ import annotations

import logging
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

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

console = Console()


# ── Display helpers ──────────────────────────────────────────────────

def _print_token_usage(result: PipelineResult) -> None:
    parts = []
    for name, step in result.token_usage.steps.items():
        parts.append(f"{name} {step.input_tokens}\u2192{step.output_tokens}")
    console.print(
        f"  {' | '.join(parts)} | ${result.token_usage.total_cost:.4f}",
        style="dim",
    )


def _print_recommendation(result: PipelineResult) -> None:
    console.print()
    console.print(Panel(
        result.synthesis,
        title="[bold]Recommendation[/bold]",
        border_style="green",
        padding=(1, 2),
    ))
    _print_token_usage(result)


def _print_deals_table(deals: list[EnrichedDeal], report: DataQualityReport) -> None:
    console.print(
        f"\n  [bold]{report.total_deals}[/bold] deals | "
        f"{report.complete_deals} complete | "
        f"[yellow]{report.incomplete_deals} with gaps[/yellow]"
    )

    if report.missing_fields_summary:
        parts = [f"{f}: {c}" for f, c in report.missing_fields_summary.items()]
        console.print(f"  [yellow]Missing: {', '.join(parts)}[/yellow]")

    if report.orphaned_companies:
        console.print(
            f"  [yellow]No account match: {', '.join(report.orphaned_companies)}[/yellow]"
        )

    table = Table(show_header=True, header_style="bold", padding=(0, 1))
    table.add_column("#", style="dim", width=3)
    table.add_column("Company", min_width=12)
    table.add_column("Stage", min_width=10)
    table.add_column("Amount", justify="right")
    table.add_column("Prob", justify="right")
    table.add_column("Owner")
    table.add_column("Quality")

    for d in deals:
        if d.data_quality_flags:
            quality = ", ".join(d.data_quality_flags)
            quality_markup = f"[yellow]{quality}[/yellow]"
        else:
            quality_markup = "[green]OK[/green]"

        table.add_row(
            str(d.deal_id),
            d.company,
            d.stage or "[dim]N/A[/dim]",
            f"${d.amount:,.0f}",
            f"{d.probability:.0%}",
            d.owner,
            quality_markup,
        )

    console.print()
    console.print(table)


def _print_verbose(result: PipelineResult) -> None:
    console.print(f"\n[bold cyan]--- Planner ---[/bold cyan]")
    console.print(f"  Type: {result.plan.analysis_type}")
    console.print(f"  Deals: {result.plan.relevant_deals}")
    console.print(f"  Reasoning: [italic]{result.plan.reasoning}[/italic]")

    console.print(f"\n[bold cyan]--- Analyzer ---[/bold cyan]")
    for d in result.enriched_deals:
        score = d.risk_score or 0
        if score > 0.6:
            risk_style = "red"
        elif score > 0.4:
            risk_style = "yellow"
        else:
            risk_style = "green"
        console.print(
            f"  #{d.deal_id} {d.company}: "
            f"risk=[{risk_style}]{d.risk_score}[/{risk_style}] "
            f"sentiment={d.sentiment}"
        )


# ── Pipeline helpers ─────────────────────────────────────────────────

def _load_data(
    folder_id: str | None,
    credentials: str,
) -> tuple[list[EnrichedDeal], DataQualityReport]:
    with console.status("[bold cyan]Downloading data from Google Drive..."):
        drive_folder = folder_id or DEFAULT_GDRIVE_FOLDER_ID
        data_path = load_from_gdrive(drive_folder, credentials)
        deals, report = ingest(data_path)
    console.print(f"  [green]\u2713[/green] {report.total_deals} deals loaded from Google Drive")
    return deals, report


def _run_analysis(
    query: str,
    deals: list[EnrichedDeal],
    report: DataQualityReport,
    verbose: bool = False,
) -> PipelineResult:
    token_usage = TokenUsage()

    if not deals:
        return PipelineResult(
            query=query,
            plan=AnalysisPlan(),
            enriched_deals=[],
            synthesis="No deals available to analyze.",
            data_quality=report,
            token_usage=token_usage,
        )

    with console.status("[bold cyan]Planning analysis..."):
        analysis_plan, plan_usage = plan(query, deals)
    token_usage.add_step("planner", **plan_usage)

    with console.status("[bold cyan]Analyzing deals..."):
        analyzed_deals, analyzer_usage = analyze(deals, analysis_plan)
    token_usage.add_step("analyzer", **analyzer_usage)

    with console.status("[bold cyan]Generating recommendations..."):
        synthesis, synth_usage = synthesize(analyzed_deals, query, analysis_plan)
    token_usage.add_step("synthesizer", **synth_usage)

    result = PipelineResult(
        query=query,
        plan=analysis_plan,
        enriched_deals=analyzed_deals,
        synthesis=synthesis,
        data_quality=report,
        token_usage=token_usage,
    )

    if verbose:
        _print_verbose(result)

    return result


# ── CLI commands ─────────────────────────────────────────────────────

@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def cli(debug: bool) -> None:
    """RevOps Copilot \u2014 an agentic CLI for deal management."""
    level = logging.DEBUG if debug else logging.WARNING
    logging.basicConfig(level=level, format="%(name)s %(levelname)s: %(message)s")


@cli.command()
@click.argument("query")
@click.option("--folder-id", default=None, help="Google Drive folder ID (defaults to challenge dataset)")
@click.option("--credentials", default="credentials.json", help="Path to GCP credentials JSON")
@click.option("--verbose", is_flag=True, help="Show intermediate pipeline steps")
def ask(
    query: str,
    folder_id: str | None,
    credentials: str,
    verbose: bool,
) -> None:
    """Ask a natural language business question about your deals."""
    deals, report = _load_data(folder_id, credentials)
    result = _run_analysis(query, deals, report, verbose)
    _print_recommendation(result)


@cli.command()
@click.option("--folder-id", default=None, help="Google Drive folder ID (defaults to challenge dataset)")
@click.option("--credentials", default="credentials.json", help="Path to GCP credentials JSON")
def status(
    folder_id: str | None,
    credentials: str,
) -> None:
    """Show data health check \u2014 no LLM calls, no cost."""
    deals, report = _load_data(folder_id, credentials)
    _print_deals_table(deals, report)


@cli.command()
@click.option("--folder-id", default=None, help="Google Drive folder ID (defaults to challenge dataset)")
@click.option("--credentials", default="credentials.json", help="Path to GCP credentials JSON")
def chat(
    folder_id: str | None,
    credentials: str,
) -> None:
    """Interactive copilot mode \u2014 ask multiple questions without re-loading data."""
    deals, report = _load_data(folder_id, credentials)

    console.print(Panel(
        f"[bold]{report.total_deals}[/bold] deals loaded \u2014 "
        f"{report.complete_deals} complete, {report.incomplete_deals} with gaps\n"
        f"Type [bold]exit[/bold] to quit",
        title="[bold]RevOps Copilot[/bold]",
        border_style="cyan",
    ))

    while True:
        try:
            query = console.input("\n[bold green]> [/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit"):
            console.print("[dim]Goodbye.[/dim]")
            break

        try:
            result = _run_analysis(query, deals, report)
            _print_recommendation(result)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    cli()
