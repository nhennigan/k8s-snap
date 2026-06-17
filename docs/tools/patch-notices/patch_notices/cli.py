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
@click.option(
    "--source",
    default="snap",
    show_default=True,
    type=click.Choice(["snap", "charm"]),
    help="Source to fetch: 'snap' (default) or 'charm'.",
)
def fetch(track: str, source: str):
    """Pull the PR delta since the last documented commit.

    For snap: resolves the current stable SHA via the Snap Store + Launchpad APIs,
    then fetches all PRs between that SHA and last_documented_sha.

    For charm: resolves the current stable revision via Charmhub, maps it to a
    git SHA via the GitHub tag (k8s-rev<N>), then fetches all commits between
    that SHA and last_documented_sha in canonical/k8s-operator.

    Writes the raw delta to metadata/delta-<track>.json.
    """
    console.print(f"[bold]Fetching delta for track:[/bold] {track} [dim](source: {source})[/dim]")
    if source == "charm":
        state_key = f"charm:{track}"
        delta = fetcher.fetch_charm_delta(state_key)
    else:
        delta = fetcher.fetch_delta(track)
        state_key = f"snap:{track}"
    console.print(f"[green]Found {len(delta)} commits.[/green]")


@main.command()
@click.option(
    "--track",
    required=True,
    help="Snap track to process, e.g. '1.30/stable'.",
)
@click.option(
    "--source",
    default="snap",
    show_default=True,
    type=click.Choice(["snap", "charm"]),
    help="Source to triage: 'snap' (default) or 'charm'.",
)
@click.option(
    "--output",
    default="monthly_review.md",
    show_default=True,
    help="Path to write the workbook.",
)
def review(track: str, source: str, output: str):
    """Run AI triage and write the Markdown workbook.

    Reads the delta produced by `fetch`, processes each commit through the AI
    (diff > body > title), and writes the workbook with Included,
    Verification, and Discarded sections.
    """
    console.print(f"[bold]Running AI triage for track:[/bold] {track} [dim](source: {source})[/dim]")
    load_key = f"charm:{track}" if source == "charm" else f"snap:{track}"
    delta = fetcher.load_delta(load_key)
    triage_result = ai.triage(delta, source=source)
    workbook.write(triage_result, output_path=output)
    console.print(f"[green]Workbook written:[/green] {output}")


@main.command()
@click.option(
    "--track",
    required=True,
    help="Snap track to finalize, e.g. '1.30/stable'.",
)
@click.option(
    "--source",
    default="snap",
    show_default=True,
    type=click.Choice(["snap", "charm"]),
    help="Source to finalize: 'snap' (default) or 'charm'.",
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
def finalize(track: str, source: str, workbook_path: str, export: str):
    """Close the loop: update state and write the clean export.

    Parses the workbook for <!-- sha:... --> tags, updates
    metadata/patch-metadata.json with the latest included SHA, and writes
    a clean export ready to paste into a PR.

    If all commits were intentionally discarded (no included items), the
    bookmark is still advanced to the last commit in the fetched delta so
    future runs start from the right place.
    """
    console.print(f"[bold]Finalizing track:[/bold] {track} [dim](source: {source})[/dim]")
    state_key = f"charm:{track}" if source == "charm" else f"snap:{track}"

    included_shas = workbook.parse_included_shas(workbook_path)
    if included_shas:
        latest_sha = included_shas[-1]
        workbook.export_clean(workbook_path, export)
        console.print(f"[green]Clean export written:[/green] {export}")
    else:
        # All commits were discarded — advance the bookmark to the head of the delta
        # so the next run doesn't re-process the same commits.
        delta = fetcher.load_delta(state_key)
        if not delta:
            console.print("[red]No delta found. Run `fetch` first.[/red]")
            raise SystemExit(1)
        latest_sha = delta[-1]["sha"]
        console.print("[yellow]No included items — advancing bookmark to delta head (nothing exported).[/yellow]")

    state.update(state_key, latest_sha)
    console.print(f"[green]State updated.[/green] Latest SHA: {latest_sha}")
