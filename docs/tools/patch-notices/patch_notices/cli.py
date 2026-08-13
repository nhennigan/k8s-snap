# Copyright 2026 Canonical, Ltd.
# See LICENSE file for licensing details.

"""Entry point for the patch-notices CLI."""

import json
from datetime import date as _date
from pathlib import Path

import click
from rich.console import Console

from patch_notices import fetcher, ai, workbook, state

console = Console()


def _expand_track(version: str, source: str) -> str:
    """Expand a short version like '1.32' to the full channel string."""
    if "/" in version:
        return version  # already a full channel
    if source == "charm":
        return f"{version}/stable"
    return f"{version}-classic/stable"


@click.group()
def main():
    """Patch-notices updater for Canonical Kubernetes."""


@main.command()
@click.option(
    "--track",
    required=True,
    help="Release version to process, e.g. '1.32'.",
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
    track = _expand_track(track, source)
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
    help="Release version to process, e.g. '1.32'.",
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
    default="patch_notices_review.md",
    show_default=True,
    help="Path to write the workbook.",
)
def review(track: str, source: str, output: str):
    """Run AI triage and write the Markdown workbook.

    Reads the delta produced by `fetch`, processes each commit through the AI
    (diff > body > title), and writes the workbook with Included,
    Verification, and Discarded sections.
    """
    track = _expand_track(track, source)
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
    help="Release version to finalize, e.g. '1.32'.",
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
    default="patch_notices_review.md",
    show_default=True,
    help="Path to the edited workbook.",
)
@click.option(
    "--export",
    default="patch_notices_output.md",
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
    track = _expand_track(track, source)
    console.print(f"[bold]Finalizing track:[/bold] {track} [dim](source: {source})[/dim]")
    state_key = f"charm:{track}" if source == "charm" else f"snap:{track}"

    included_shas = workbook.parse_included_shas(workbook_path)
    if included_shas:
        latest_sha = included_shas[-1]
        workbook.export_clean(workbook_path, export)
        console.print(f"[green]Clean export written:[/green] {export}")
    else:
        # No included items — either all commits were discarded, or fetch found nothing.
        try:
            delta = fetcher.load_delta(state_key)
        except FileNotFoundError:
            console.print("[red]No delta found. Run `fetch` first.[/red]")
            raise SystemExit(1)
        if delta:
            # Commits were fetched but all discarded — advance to the delta head.
            latest_sha = delta[-1]["sha"]
            console.print("[yellow]No included items — advancing bookmark to delta head (nothing exported).[/yellow]")
        else:
            # fetch ran but found no new commits — update the date with the existing SHA.
            existing = state.load().get("tracks", {}).get(state_key, {})
            latest_sha = existing.get("last_documented_sha")
            if not latest_sha:
                console.print("[red]No existing state for this track.[/red]")
                raise SystemExit(1)
            console.print("[dim]No new commits — updating date only.[/dim]")

    state.update(state_key, latest_sha)
    console.print(f"[green]State updated.[/green] Latest SHA: {latest_sha}")


@main.command()
@click.option(
    "--track",
    required=True,
    help="Release version to process, e.g. '1.35'.",
)
@click.option(
    "--source",
    default="snap",
    show_default=True,
    type=click.Choice(["snap", "charm"]),
    help="Source to process: 'snap' (default) or 'charm'.",
)
@click.option(
    "--release-notes",
    required=True,
    help="Path to the release notes file to update, e.g. docs/canonicalk8s/releases/snap/1.35.md.",
)
@click.option(
    "--summary-out",
    required=True,
    help="Path to write the per-track summary JSON (for use by pr-body).",
)
@click.option(
    "--workbook",
    "workbook_out",
    default=None,
    show_default=True,
    help="Optional path to also write the full review workbook (Included/Discarded/Verification). "
         "Useful for local inspection. Does not affect the release notes or state.",
)
def generate(track: str, source: str, release_notes: str, summary_out: str, workbook_out: str | None):
    """Fetch, triage, and write directly to the release notes file.

    The CI entry point for the automated workflow. Combines fetch + review +
    insert into one command. On success, advances the state bookmark.

    Writes a summary JSON to --summary-out regardless of outcome so that
    pr-body can include all tracks in the PR body table.
    """
    track = _expand_track(track, source)
    today_dt = _date.today()
    today = f"{today_dt.strftime('%b')} {today_dt.day}, {today_dt.year}"
    state_key = f"charm:{track}" if source == "charm" else f"snap:{track}"

    console.print(f"[bold]Generating patch notice:[/bold] {track} [dim](source: {source})[/dim]")

    # --- Fetch ---
    if source == "charm":
        delta = fetcher.fetch_charm_delta(state_key)
    else:
        delta = fetcher.fetch_delta(track)

    if not delta:
        summary = {
            "track": state_key,
            "status": "up-to-date",
            "date": today,
            "included": [],
            "discarded": [],
            "limited_context": [],
        }
        Path(summary_out).parent.mkdir(parents=True, exist_ok=True)
        Path(summary_out).write_text(json.dumps(summary, indent=2))
        console.print(f"[dim]Up to date — no new commits.[/dim]")
        return

    # --- AI triage ---
    triage_result = ai.triage(delta, source=source)

    included = [r for r in triage_result if r["triage"]["action"] == "include"]
    discarded = [r for r in triage_result if r["triage"]["action"] == "discard"]

    if not included:
        summary = workbook.build_track_summary(triage_result, state_key, today)
        summary["status"] = "all-discarded"
        Path(summary_out).parent.mkdir(parents=True, exist_ok=True)
        Path(summary_out).write_text(json.dumps(summary, indent=2))
        if workbook_out:
            workbook.write(triage_result, output_path=workbook_out)
            console.print(f"[green]Workbook written:[/green] {workbook_out}")
        latest_sha = delta[-1]["sha"]
        state.update(state_key, latest_sha)
        console.print(
            f"[yellow]All {len(discarded)} commits discarded — bookmark advanced, "
            "release notes unchanged.[/yellow]"
        )
        return

    # --- Insert into release notes (before updating state, so a failure is retryable) ---
    workbook.insert_patch_notice(release_notes, triage_result, today, source)

    # --- Update state ---
    latest_sha = delta[-1]["sha"]
    state.update(state_key, latest_sha)

    # --- Write summary ---
    summary = workbook.build_track_summary(triage_result, state_key, today)
    Path(summary_out).parent.mkdir(parents=True, exist_ok=True)
    Path(summary_out).write_text(json.dumps(summary, indent=2))

    if workbook_out:
        workbook.write(triage_result, output_path=workbook_out)
        console.print(f"[green]Workbook written:[/green] {workbook_out}")

    console.print(
        f"[green]✓[/green] {track} — "
        f"[green]{len(included)} included[/green], "
        f"[dim]{len(discarded)} discarded[/dim]"
        + (f", [yellow]{len(summary['limited_context'])} ⚠️[/yellow]"
           if summary["limited_context"] else "")
    )


@main.command()
@click.option(
    "--summaries-dir",
    required=True,
    help="Directory containing per-track summary JSON files written by generate.",
)
@click.option(
    "--output",
    default="-",
    show_default=True,
    help="Output file path. Use '-' to print to stdout (default).",
)
def pr_body(summaries_dir: str, output: str):
    """Generate the PR body markdown from per-track summary JSON files.

    Reads all *.json files in --summaries-dir (produced by generate) and
    prints a formatted PR body with a summary table and per-track collapsible
    detail sections.
    """
    summary_dir = Path(summaries_dir)
    if not summary_dir.is_dir():
        console.print(f"[red]Directory not found:[/red] {summaries_dir}")
        raise SystemExit(1)

    summaries = [
        json.loads(f.read_text())
        for f in sorted(summary_dir.glob("*.json"))
    ]
    if not summaries:
        console.print(f"[red]No summary JSON files found in[/red] {summaries_dir}")
        raise SystemExit(1)

    body = workbook.build_pr_body(summaries)

    if output == "-":
        click.echo(body)
    else:
        Path(output).write_text(body)
        console.print(f"[green]PR body written:[/green] {output}")
