# Copyright 2026 Canonical, Ltd.
# See LICENSE file for licensing details.

"""Fetch the PR delta between the last documented SHA and the current stable SHA.

Pipeline:
  1. Query Snap Store API  -> current revision number for the track
  2. Query Launchpad API   -> git SHA for that revision's build
  3. Query GitHub API      -> list of PRs merged between the two SHAs
"""

from __future__ import annotations

import json
import os
import pathlib
import re
from typing import Any

import requests

from patch_notices import state

SNAP_STORE_API = "https://api.snapcraft.io/v2/snaps/info/k8s"
LAUNCHPAD_API = "https://api.launchpad.net/devel"
GITHUB_API = "https://api.github.com"
GITHUB_REPO = "canonical/k8s-snap"

# Launchpad snap owner/project path — builds live at ~containers/k8s/+snap/<name>
LP_SNAP_OWNER = "~containers"
LP_SNAP_PROJECT = "k8s"

METADATA_DIR = pathlib.Path(__file__).parent.parent / "metadata"

# PR number embedded in squash-merge commit subject, e.g. "fix: something (#2131)"
_PR_IN_SUBJECT_RE = re.compile(r"\(#(\d+)\)$")


def _snap_store_revision(track: str) -> int:
    """Return the current amd64 revision number published on *track*.

    The track argument should be the full channel name, e.g. '1.32-classic/stable'.
    The Snap Store channel-map uses '<track>/<risk>' in channel.name, where
    track contains the version + flavor (e.g. '1.32-classic').
    """
    resp = requests.get(
        SNAP_STORE_API,
        headers={"Snap-Device-Series": "16"},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    # Normalise: accept both '1.32-classic/stable' and '1.32-classic' + risk split
    if "/" in track:
        track_name, risk = track.split("/", 1)
    else:
        raise ValueError(
            f"track must be in '<version>/<risk>' format, e.g. '1.32-classic/stable'. Got: {track!r}"
        )

    for entry in data.get("channel-map", []):
        ch = entry["channel"]
        if ch["track"] == track_name and ch["risk"] == risk and ch["architecture"] == "amd64":
            return int(entry["revision"])

    raise ValueError(
        f"Track '{track}' not found in Snap Store channel-map for 'k8s'. "
        f"Available stable tracks: {sorted({e['channel']['track'] for e in data.get('channel-map', []) if e['channel']['risk'] == 'stable'})}"
    )


def _launchpad_sha(track: str, revision: int) -> str:
    """Return the git SHA that produced *revision* for *track* via Launchpad builds.

    Launchpad snap builds live at:
      /devel/~containers/k8s/+snap/k8s-snap-<track>/builds

    Each build entry has:
      - store_upload_revision: the snap store revision number (int)
      - revision_id: the VCS commit SHA used for the build
    """
    # Derive the Launchpad snap name from the track, e.g. '1.32-classic/stable' -> 'k8s-snap-1.32-classic'
    track_name = track.split("/")[0]
    snap_name = f"k8s-snap-{track_name}"
    # URL pattern: /devel/~containers/k8s/+snap/<name>/builds
    builds_url = (
        f"{LAUNCHPAD_API}/{LP_SNAP_OWNER}/{LP_SNAP_PROJECT}/+snap/{snap_name}/builds"
    )

    # Paginate through builds (newest first) until we find the matching store revision
    url: str | None = f"{builds_url}?ws.size=75"
    while url:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for build in data.get("entries", []):
            if build.get("store_upload_revision") == revision:
                sha = build.get("revision_id")
                if sha:
                    return sha
                raise ValueError(
                    f"Launchpad build for revision {revision} found but 'revision_id' is empty. "
                    f"Build keys: {list(build.keys())}"
                )
        url = data.get("next_collection_link")

    raise ValueError(
        f"No Launchpad build found for snap '{snap_name}' with store revision {revision}. "
        "The build may still be in progress, or the snap name may have changed."
    )


def _github_commits(base_sha: str, head_sha: str) -> list[dict[str, Any]]:
    """Return one entry per commit between *base_sha* and *head_sha*.

    Uses a single GitHub compare request. The compare response contains both
    the commit list and the aggregate file patches for the whole range.
    PR numbers are extracted from commit message subjects where GitHub embeds
    them (e.g. "fix: something (#2131)"). No per-commit API calls are made.
    The aggregate diff is attached to every entry so the AI has full context.
    """
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    headers["Accept"] = "application/vnd.github+json"
    headers["X-GitHub-Api-Version"] = "2022-11-28"

    resp = requests.get(
        f"{GITHUB_API}/repos/{GITHUB_REPO}/compare/{base_sha}...{head_sha}?per_page=250",
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    # Build aggregate diff string from all changed files in the range (one request, free)
    aggregate_diff = "\n\n".join(
        f"--- {f['filename']} ---\n{f.get('patch', '(binary or no diff)')}"
        for f in data.get("files", [])
    )

    entries: list[dict[str, Any]] = []
    for commit in data.get("commits", []):
        msg_lines = commit["commit"]["message"].splitlines()
        title = msg_lines[0]
        body = "\n".join(msg_lines[1:]).strip()

        m = _PR_IN_SUBJECT_RE.search(title)
        pr_number = int(m.group(1)) if m else None
        pr_url = (
            f"https://github.com/{GITHUB_REPO}/pull/{pr_number}"
            if pr_number else None
        )

        entries.append({
            "sha": commit["sha"],
            "title": title,
            "body": body,
            "html_url": commit.get("html_url", ""),
            "author": (commit.get("author") or {}).get("login")
                      or commit["commit"]["author"]["name"],
            "date": commit["commit"]["author"]["date"][:10],
            "pr_number": pr_number,
            "pr_url": pr_url,
            "diff": aggregate_diff,
        })

    return entries


def fetch_delta(track: str) -> list[dict[str, Any]]:
    """Full pipeline: Snap Store -> Launchpad -> GitHub. Returns PR list."""
    track_state = state.load().get("tracks", {}).get(track, {})
    base_sha = track_state.get("last_documented_sha")
    if not base_sha:
        raise ValueError(
            f"No last_documented_sha for track '{track}' in patch-metadata.json. "
            "Add an initial entry before running fetch."
        )
    revision = _snap_store_revision(track)
    head_sha = _launchpad_sha(track, revision)
    prs = _github_commits(base_sha, head_sha)
    _save_delta(track, prs)
    return prs


def _save_delta(track: str, prs: list[dict[str, Any]]) -> None:
    """Persist delta to metadata/delta-<safe-track>.json."""
    METADATA_DIR.mkdir(exist_ok=True)
    safe = track.replace("/", "-")
    path = METADATA_DIR / f"delta-{safe}.json"
    path.write_text(json.dumps(prs, indent=2))


def load_delta(track: str) -> list[dict[str, Any]]:
    """Load a previously saved delta from disk."""
    safe = track.replace("/", "-")
    path = METADATA_DIR / f"delta-{safe}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"No delta file found for track '{track}'. Run `fetch` first."
        )
    return json.loads(path.read_text())
