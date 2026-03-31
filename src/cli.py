"""CLI entry point for the RevOps Copilot."""

from __future__ import annotations

import logging
import sys

import click

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

from src.orchestrator import run_pipeline
from src.pipeline.ingester import ingest
from src.sources.local import load_from_local


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def cli(debug: bool) -> None:
    """RevOps Copilot — an agentic CLI for deal management."""
    level = logging.DEBUG if debug else logging.WARNING
    logging.basicConfig(level=level, format="%(name)s %(levelname)s: %(message)s")


@cli.command()
@click.argument("query")
@click.option("--source", default="local", type=click.Choice(["local", "gdrive"]), help="Data source")
@click.option("--data-dir", default="./data", help="Path to local data directory")
@click.option("--folder-id", default=None, help="Google Drive folder ID")
@click.option("--credentials", default="credentials.json", help="Path to GCP credentials JSON")
@click.option("--verbose", is_flag=True, help="Show intermediate pipeline steps")
def ask(
    query: str,
    source: str,
    data_dir: str,
    folder_id: str | None,
    credentials: str,
    verbose: bool,
) -> None:
    """Ask a natural language business question about your deals."""
    result = run_pipeline(
        query=query,
        source=source,
        data_dir=data_dir,
        folder_id=folder_id,
        credentials=credentials,
        verbose=verbose,
    )

    click.echo("\n" + "=" * 60)
    click.echo(result.synthesis)
    click.echo("=" * 60)

    # Always print token usage summary
    click.echo("\nToken Usage Summary:")
    for step_name, step_usage in result.token_usage.steps.items():
        click.echo(
            f"  {step_name:>12}: {step_usage.input_tokens:>6} in / "
            f"{step_usage.output_tokens:>6} out / ${step_usage.cost:.6f}"
        )
    click.echo(
        f"  {'TOTAL':>12}: {result.token_usage.total_input_tokens:>6} in / "
        f"{result.token_usage.total_output_tokens:>6} out / "
        f"${result.token_usage.total_cost:.6f}"
    )


@cli.command()
@click.option("--source", default="local", type=click.Choice(["local", "gdrive"]), help="Data source")
@click.option("--data-dir", default="./data", help="Path to local data directory")
@click.option("--folder-id", default=None, help="Google Drive folder ID")
@click.option("--credentials", default="credentials.json", help="Path to GCP credentials JSON")
def status(
    source: str,
    data_dir: str,
    folder_id: str | None,
    credentials: str,
) -> None:
    """Show data health check — no LLM calls, no cost."""
    if source == "gdrive":
        from src.sources.gdrive import load_from_gdrive

        if not folder_id:
            raise click.UsageError("--folder-id required with --source gdrive")
        data_path = load_from_gdrive(folder_id, credentials)
    else:
        data_path = load_from_local(data_dir)

    deals, report = ingest(data_path)

    click.echo("RevOps Copilot — Data Quality Report")
    click.echo("=" * 40)
    click.echo(f"Total deals:      {report.total_deals}")
    click.echo(f"Complete:         {report.complete_deals}")
    click.echo(f"Incomplete:       {report.incomplete_deals}")

    if report.missing_fields_summary:
        click.echo("\nMissing Fields:")
        for field, count in report.missing_fields_summary.items():
            click.echo(f"  {field}: {count} deal(s)")

    if report.orphaned_companies:
        click.echo(f"\nOrphaned (no account match): {', '.join(report.orphaned_companies)}")

    click.echo("\nDeals:")
    for d in deals:
        flags = ", ".join(d.data_quality_flags) if d.data_quality_flags else "OK"
        click.echo(
            f"  #{d.deal_id} {d.company:<12} | "
            f"{d.stage or 'N/A':<12} | "
            f"${d.amount:>9,.0f} | "
            f"p={d.probability} | "
            f"{flags}"
        )


if __name__ == "__main__":
    cli()
