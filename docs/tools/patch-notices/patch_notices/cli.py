# Copyright 2026 Canonical, Ltd.
# See LICENSE file for licensing details.

"""Entry point for the patch-notices CLI."""

import click
from rich.console import Console

from patch_notices import fetcher, ai, workbook, state

console = Console()


@click.group()
def main():
    """Patch-notices updater for Canonical Kubernetes."""


@main.command()
@click.option(
    "--track",
    required=True,
    help="Snap track to process, e.g. '1.30/stable'.",
)
def fetch(track: str):
    """Pull the PR delta since the last documented commit.

    Resolves the current stable SHA via the Snap Store + Launchpad APIs,
    then fetches all PRs between that SHA and last_documented_sha.
    Writes the raw delta to metadata/delta-<track>.json.
    """
    console.print(f"[bold]Fetching delta for track:[/bold] {track}")
    delta = fetcher.fetch_delta(track)
    console.print(f"[green]Found {len(delta)} PRs.[/green]")


@main.command()
@click.option(
    "--track",
    required=True,
    help="Snap track to process, e.g. '1.30/stable'.",
)
@click.option(
    "--output",
    default="monthly_review.md",
    show_default=True,
    help="Path to write the workbook.",
)
def review(track: str, output: str):
    """Run AI triage and write the Markdown workbook.

    Reads the delta produced by `fetch`, processes each PR through the AI
    (diff > body > title), and writes the workbook with Included,
    Verification, and Discarded sections.
    """
    console.print(f"[bold]Running AI triage for track:[/bold] {track}")
    delta = fetcher.load_delta(track)
    triage_result = ai.triage(delta)
    workbook.write(triage_result, output_path=output)
    console.print(f"[green]Workbook written:[/green] {output}")


@main.command()
@click.option(
    "--track",
    required=True,
    help="Snap track to finalize, e.g. '1.30/stable'.",
)
@click.option(
    "--workbook-path",
    default="monthly_review.md",
    show_default=True,
    help="Path to the edited workbook.",
)
@click.option(
    "--export",
    default="patch-notice-export.md",
    show_default=True,
    help="Path for the clean export snippet.",
)
def finalize(track: str, workbook_path: str, export: str):
    """Close the loop: update state and write the clean export.

    Parses the workbook for <!-- sha:... --> tags, updates
    metadata/patch-metadata.json with the latest included SHA, and writes
    a clean export ready to paste into a PR.
    """
    console.print(f"[bold]Finalizing track:[/bold] {track}")
    included_shas = workbook.parse_included_shas(workbook_path)
    if not included_shas:
        console.print("[red]No included SHAs found in workbook. Aborting.[/red]")
        raise SystemExit(1)
    latest_sha = included_shas[-1]
    state.update(track, latest_sha)
    workbook.export_clean(workbook_path, export)
    console.print(f"[green]State updated.[/green] Latest SHA: {latest_sha}")
    console.print(f"[green]Clean export written:[/green] {export}")
