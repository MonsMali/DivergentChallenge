"""CLI entry point for the RevOps Copilot."""

from __future__ import annotations

import logging
import sys
from contextlib import contextmanager

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

from src.models import DataQualityReport, EnrichedDeal, PipelineResult, ScopeMetrics
from src.orchestrator import load_data, run_analysis

console = Console()

_STEP_LABELS = {
    "planner": "Planning analysis...",
    "analyzer": "Analyzing deals...",
    "synthesizer": "Generating recommendations...",
}


@contextmanager
def _step_spinner(step: str):
    """Show a Rich spinner for each pipeline step."""
    with console.status(f"[bold cyan]{_STEP_LABELS.get(step, step)}"):
        yield


# ── Display helpers ──────────────────────────────────────────────────

def _print_token_usage(result: PipelineResult) -> None:
    parts = []
    for name, step in result.token_usage.steps.items():
        parts.append(f"{name} {step.input_tokens}\u2192{step.output_tokens}")
    console.print(
        f"  {' | '.join(parts)} | ${result.token_usage.total_cost:.4f}",
        style="dim",
    )


def _print_scope_metrics(metrics: ScopeMetrics) -> None:
    """Render headline numbers deterministically, above the LLM panel."""
    table = Table(
        title=f"[bold]{metrics.scope_description}[/bold]",
        show_header=False,
        box=None,
        padding=(0, 1),
        title_justify="left",
    )
    table.add_column(style="dim")
    table.add_column(justify="right")
    table.add_row("Total pipeline", f"${metrics.total_pipeline:,.0f}")
    table.add_row("Weighted pipeline", f"${metrics.weighted_pipeline:,.0f}")
    table.add_row("Deals in scope", str(metrics.deal_count))
    table.add_row("Overdue close dates", str(metrics.overdue_count))
    table.add_row("Stale contacts (>14d)", str(metrics.stale_count))
    table.add_row("Records with data gaps", str(metrics.incomplete_data_count))
    if metrics.owners:
        table.add_row("Owners in scope", ", ".join(metrics.owners))

    console.print()
    console.print(Panel(
        table,
        title="[bold]Headline Metrics (deterministic)[/bold]",
        border_style="cyan",
        padding=(0, 1),
    ))


def _print_recommendation(result: PipelineResult) -> None:
    _print_scope_metrics(result.scope_metrics)
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
    filters = result.plan.filters_to_apply or {}
    if filters:
        filter_str = ", ".join(f"{k}={v}" for k, v in filters.items())
        console.print(f"  Filters: {filter_str}")
    else:
        console.print(f"  Filters: [dim]none[/dim]")
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
    with console.status("[bold cyan]Downloading data from Google Drive..."):
        deals, report = load_data(folder_id, credentials)
    console.print(f"  [green]\u2713[/green] {report.total_deals} deals loaded from Google Drive")

    result = run_analysis(query, deals, report, on_step=_step_spinner)
    if verbose:
        _print_verbose(result)
    _print_recommendation(result)


@cli.command()
@click.option("--folder-id", default=None, help="Google Drive folder ID (defaults to challenge dataset)")
@click.option("--credentials", default="credentials.json", help="Path to GCP credentials JSON")
def status(
    folder_id: str | None,
    credentials: str,
) -> None:
    """Show data health check \u2014 no LLM calls, no cost."""
    with console.status("[bold cyan]Downloading data from Google Drive..."):
        deals, report = load_data(folder_id, credentials)
    console.print(f"  [green]\u2713[/green] {report.total_deals} deals loaded from Google Drive")
    _print_deals_table(deals, report)


@cli.command()
@click.option("--folder-id", default=None, help="Google Drive folder ID (defaults to challenge dataset)")
@click.option("--credentials", default="credentials.json", help="Path to GCP credentials JSON")
def chat(
    folder_id: str | None,
    credentials: str,
) -> None:
    """Interactive copilot mode \u2014 ask multiple questions without re-loading data."""
    with console.status("[bold cyan]Downloading data from Google Drive..."):
        deals, report = load_data(folder_id, credentials)
    console.print(f"  [green]\u2713[/green] {report.total_deals} deals loaded from Google Drive")

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
            result = run_analysis(query, deals, report, on_step=_step_spinner)
            _print_recommendation(result)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    cli()
