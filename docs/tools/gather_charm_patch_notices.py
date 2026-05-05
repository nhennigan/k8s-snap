#!/usr/bin/env python3
"""
gather_charm_patch_notices.py
─────────────────────────────
Collect every commit that has landed on each stable charm track since the last
patch-notice update, and write them to pending_patch_notices.txt so the doc
author can review and draft the next "Patch notices" section.

Prerequisites
─────────────
  • git  – run from the root of the charm's git repository
  • Python 3.10+ (stdlib only, no extra packages needed)

No charmcraft or gh CLI installation is required.  Revision data is fetched
from the public Charmhub REST API and release/commit data from the public
GitHub REST API.  Optionally set GH_TOKEN or GITHUB_TOKEN in your environment
to raise the GitHub API rate limit from 60 to 5000 requests/hour.

Usage
─────
  1.  Update CHARM_NAME, CHARM_REPO, and LAST_DOCUMENTED_HASHES below.
  2.  cd /path/to/k8s-operator   (root of the charm git repository)
  3.  python3 docs/tools/gather_charm_patch_notices.py

After publishing a patch-notice PR, update LAST_DOCUMENTED_HASHES with the
latest commit hash that was included in that PR so the next run only reports
genuinely new work.
"""

import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

# The charm name as it appears on Charmhub.
CHARM_NAME = "k8s"

# The GitHub repository that hosts releases / tags for this charm.
CHARM_REPO = "canonical/k8s-operator"

# Git tag prefix used when tagging charm revisions in the repository.
# Tags are expected in the form  <TAG_PREFIX>-rev<N>  (e.g. "k8s-rev1838").
TAG_PREFIX = "k8s"

# For each active track, record the last commit hash that was already included
# in the published patch notices.  Update these values after each patch-notice
# PR is merged.
LAST_DOCUMENTED_HASHES: dict[str, str] = {
    "1.32": "5cda3128de2a65c5efc3f33bdb3ca7dc9dde5781",
    "1.33": "b2e5d36305e267ac96f1179c807744df6ca43ef0",
    "1.34": "54dd4d316b75def8bf40a49fa7099fe179e67da7",
    "1.35": "02ef6762c621729414b83490d26ab0769ac52ba3",
}

# Where to write the output.
OUTPUT_FILE = Path("pending_patch_notices.txt")

# ─────────────────────────────────────────────────────────────────────────────


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    """Run *cmd* and return the completed-process object (never raises)."""
    return subprocess.run(cmd, capture_output=True, text=True)


# ── Step 1: current stable revision from Charmhub (public API) ──────────────

# Public Charmhub API — no authentication required.
_CHARMHUB_INFO_URL = "https://api.charmhub.io/v2/charms/info/{name}?fields=channel-map"


def get_stable_revisions(charm_name: str, track: str) -> list[str]:
    """
    Return all revision numbers currently published to ``<track>/stable``.

    A single stable promotion publishes one revision per (architecture, base)
    combination, so there are typically 4–8 entries that all share the same
    ``released-at`` timestamp but carry different revision numbers.  All of
    those revisions were built from the same source commit, so we collect the
    full set and let the caller try each one until a matching GitHub release
    is found.

    Returns an empty list on any error.
    """
    url = _CHARMHUB_INFO_URL.format(name=charm_name)
    print(f"    GET {url} …")
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        print(f"    ERROR: Charmhub API returned HTTP {exc.code}: {exc.reason}",
              file=sys.stderr)
        return []
    except Exception as exc:  # network errors, JSON errors, …
        print(f"    ERROR: could not reach Charmhub API: {exc}", file=sys.stderr)
        return []

    target_channel = f"{track}/stable"

    # Collect all (released-at, revision) pairs for this channel.
    candidates: list[tuple[str, str]] = []
    for entry in data.get("channel-map", []):
        channel_info = entry.get("channel", {})
        if channel_info.get("name") != target_channel:
            continue
        rev = entry.get("revision", {}).get("revision")
        released_at = channel_info.get("released-at", "")
        if rev is not None:
            candidates.append((released_at, str(rev)))

    if not candidates:
        print(f"    WARNING: '{target_channel}' not found in Charmhub channel-map",
              file=sys.stderr)
        return []

    # Keep only entries from the most recent promotion (highest released-at).
    latest_date = max(c[0] for c in candidates)
    revisions = [rev for released_at, rev in candidates if released_at == latest_date]
    print(f"    → {len(revisions)} revision(s) for {target_channel} "
          f"(promoted {latest_date[:10]}): {', '.join(sorted(revisions))}")
    return revisions


# ── Step 2: map revision → commit hash ──────────────────────────────────────

# Optional GitHub token for higher API rate limits when the local-tag
# resolution path is unavailable.
import os as _os

_GITHUB_TOKEN: str = _os.environ.get("GH_TOKEN") or _os.environ.get("GITHUB_TOKEN") or ""
_GITHUB_API = "https://api.github.com"


def _github_get(path: str) -> dict | list | None:
    """GET a GitHub REST API path; return parsed JSON or None on error."""
    url = f"{_GITHUB_API}{path}"
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    if _GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {_GITHUB_TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        print(f"    ERROR: GitHub API {url} → HTTP {exc.code}: {exc.reason}",
              file=sys.stderr)
        return None
    except Exception as exc:
        print(f"    ERROR: GitHub API request failed: {exc}", file=sys.stderr)
        return None


def get_commit_for_revision(repo: str, tag_prefix: str, revision: str) -> str | None:
    """
    Return the commit SHA that corresponds to *revision* on Charmhub.

    Strategy (fastest first):
    1. Look up the local git tag ``<tag_prefix>-rev<N>`` with ``git rev-list``.
       This works without any network call if the repo is fully fetched.
    2. Fall back to the GitHub REST API to find a matching release or tag.
    """
    tag = f"{tag_prefix}-rev{revision}"

    # ── 1. Local git tag lookup ───────────────────────────────────────────
    result = _run(["git", "rev-list", "-1", tag])
    if result.returncode == 0 and result.stdout.strip():
        sha = result.stdout.strip()
        print(f"    Local tag {tag} → {sha[:12]}")
        return sha

    # ── 2. GitHub API fallback ────────────────────────────────────────────
    print(f"    Local tag '{tag}' not found; trying GitHub API …", file=sys.stderr)

    # 2a. Try the tag directly via the git-refs endpoint.
    data = _github_get(f"/repos/{repo}/git/ref/tags/{tag}")
    if data and isinstance(data, dict):
        sha = data.get("object", {}).get("sha")
        if sha:
            # A tag object may point to an annotated tag — dereference it.
            if data.get("object", {}).get("type") == "tag":
                tag_data = _github_get(f"/repos/{repo}/git/tags/{sha}")
                if tag_data:
                    sha = tag_data.get("object", {}).get("sha", sha)
            print(f"    GitHub tag {tag} → {sha[:12]}")
            return sha

    # 2b. Scan recent releases as a last resort.
    print(f"    Tag '{tag}' not on GitHub; scanning recent releases …", file=sys.stderr)
    for page in range(1, 5):
        releases = _github_get(f"/repos/{repo}/releases?per_page=50&page={page}")
        if not releases or not isinstance(releases, list):
            break
        for rel in releases:
            if rel.get("tag_name") == tag:
                commitish = rel.get("target_commitish", "")
                return _resolve_branch_to_sha(commitish, repo) or commitish or None
        if len(releases) < 50:
            break

    print(f"    WARNING: could not resolve revision {revision} to a commit SHA",
          file=sys.stderr)
    return None


def _resolve_branch_to_sha(commitish: str, repo: str) -> str | None:
    """Resolve a branch name to a SHA via the GitHub Branches API."""
    if not commitish:
        return None
    if len(commitish) >= 7 and all(c in "0123456789abcdefABCDEF" for c in commitish):
        return commitish  # already a SHA
    data = _github_get(f"/repos/{repo}/branches/{commitish}")
    if data and isinstance(data, dict):
        return data.get("commit", {}).get("sha")
    return None


# ── Step 3: collect commits between the two hashes ───────────────────────────

def get_git_log(base_hash: str, head_hash: str) -> list[str]:
    """
    Return formatted lines for every non-merge commit reachable from
    *head_hash* that is not reachable from *base_hash*.

    Format: ``YYYY-MM-DD | <short-hash> | <subject>``
    """
    result = _run([
        "git", "log",
        f"{base_hash}..{head_hash}",
        "--pretty=format:%as | %h | %s",
        "--no-merges",
    ])
    if result.returncode != 0:
        return [f"ERROR running git log: {result.stderr.strip()}"]
    return [line for line in result.stdout.splitlines() if line.strip()]


# ── Step 4: write the output file ────────────────────────────────────────────

def main() -> None:
    sections: list[str] = []

    for track in sorted(LAST_DOCUMENTED_HASHES):
        last_hash = LAST_DOCUMENTED_HASHES[track]
        print(f"\n── Track {track} ──────────────────────────────────────────")

        if last_hash == "REPLACE_ME":
            print("  SKIPPED: LAST_DOCUMENTED_HASHES not set for this track.", file=sys.stderr)
            sections.append(
                f"### Version {track} ###\n"
                "  [SKIPPED] Update LAST_DOCUMENTED_HASHES in the script for this track.\n"
            )
            continue

        # 1. Current stable revisions on Charmhub (one per arch/base)
        revisions = get_stable_revisions(CHARM_NAME, track)
        if not revisions:
            sections.append(
                f"### Version {track} ###\n"
                "  [SKIPPED] Could not determine current stable revisions.\n"
            )
            continue

        # 2. Map any one revision → commit hash (all share the same source commit)
        current_hash: str | None = None
        for revision in sorted(revisions):
            current_hash = get_commit_for_revision(CHARM_REPO, TAG_PREFIX, revision)
            if current_hash:
                break
        if current_hash is None:
            tried = ", ".join(sorted(revisions))
            sections.append(
                f"### Version {track} ###\n"
                f"  [SKIPPED] Could not map any revision ({tried}) to a commit hash.\n"
            )
            continue

        # 3. Collect new commits
        print(f"    git log {last_hash}..{current_hash} --no-merges …")
        commits = get_git_log(last_hash, current_hash)

        if not commits:
            body = "  (no new commits since last documented hash)\n"
        else:
            body = "\n".join(f"  {c}" for c in commits) + "\n"

        sections.append(f"### Version {track} ###\n{body}")

    # 4. Write output
    today = date.today().strftime("%B %d, %Y")
    file_header = (
        f"# Pending Patch Notices\n"
        f"# Generated : {today}\n"
        f"# Charm     : {CHARM_NAME}  ({CHARM_REPO})\n"
        f"#\n"
        f"# Format    : YYYY-MM-DD | short-hash | commit subject\n"
        f"# Merge commits are excluded.\n"
        f"#\n"
        f"# After publishing patch notices, update LAST_DOCUMENTED_HASHES in\n"
        f"# this script with the most recent hash included in that PR.\n\n"
    )

    OUTPUT_FILE.write_text(file_header + "\n".join(sections), encoding="utf-8")
    print(f"\nResults written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
