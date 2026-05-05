#!/usr/bin/env python3
"""
gather_snap_patch_notices.py
──────────────────────────────
Collect every commit that has landed on each stable k8s snap track since the
last patch-notice update, and write them to pending_patch_notices_snap.txt
so the doc author can review and draft the next "Patch notices" section.

Prerequisites
─────────────
  • git         – run from the root of the k8s-snap git repository
  • Python 3.10+ (stdlib only, no extra packages needed)
  • unsquashfs  – to extract BOM from downloaded snap files (apt: squashfs-tools)

No snapcraft login is required.  Revision data is fetched from the public
Snapstore REST API.  Optionally set GH_TOKEN or GITHUB_TOKEN in your
environment to raise the GitHub API rate limit from 60 to 5000 requests/hour.

The script downloads snap files (~150 MB each) and extracts bom.json from them
to find the commit SHA.  Downloaded snaps are stored in a temporary directory
and cleaned up automatically.

Usage
─────
  1.  Update SNAP_NAME, SNAP_REPO, and LAST_DOCUMENTED_HASHES below.
  2.  cd /path/to/k8s-snap   (root of the snap git repository)
  3.  python3 docs/tools/gather_snap_patch_notices.py

After publishing a patch-notice PR, update LAST_DOCUMENTED_HASHES with the
latest commit hash that was included in that PR so the next run only reports
genuinely new work.
"""

import json
import os
import platform
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

# The snap name as it appears on the Snap Store.
SNAP_NAME = "k8s"

# The GitHub repository that hosts the snap source code.
SNAP_REPO = "canonical/k8s-snap"

# For each active track, record the last commit hash that was already included
# in the published patch notices.  Update these values after each patch-notice
# PR is merged.
LAST_DOCUMENTED_HASHES: dict[str, str] = {
    "1.32": "12ed7570a64c5bc4fe38f5463ffe94f6aeda99e3",
    "1.33": "7dfb42ff943a8de01e6e326855024bd5944d1efd",
    "1.34": "46d9f8328e4537115c5475bb7b9182983b9c931a",
    "1.35": "c471e7a4947a5f46f92e9410df4e65d1d35be3b5",
}

# Where to write the output.
OUTPUT_FILE = Path("pending_patch_notices_snap.txt")

# ─────────────────────────────────────────────────────────────────────────────


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    """Run *cmd* and return the completed-process object (never raises)."""
    return subprocess.run(cmd, capture_output=True, text=True)


# ── Step 1: current stable revision from Snap Store ────────────────────────

_SNAPSTORE_API = "https://api.snapcraft.io/v2/snaps/info/{name}"


def _normalise_arch(arch: str) -> str:
    """Map common architecture names to Snap Store architecture strings."""
    mapped = {
        "x86_64": "amd64",
        "aarch64": "arm64",
        "armv7l": "armhf",
    }
    return mapped.get(arch, arch)


def get_target_architecture() -> str:
    """
    Return the architecture to query from stable channel-map entries.

    The value can be overridden with SNAP_TARGET_ARCH, otherwise local machine
    architecture is used (normalized to Snap Store naming).
    """
    override = os.getenv("SNAP_TARGET_ARCH", "").strip()
    if override:
        return _normalise_arch(override)
    return _normalise_arch(platform.machine())


def get_stable_revisions(snap_name: str, track: str, target_arch: str) -> list[dict]:
    """
    Return all available revisions for ``<track>-classic/stable`` on the Snap Store.

    K8s snaps use the "-classic" confinement, so track "1.32" becomes "1.32-classic".

    Each revision entry includes the channel info, revision number, release date,
    and a download URL. The result is filtered to the requested architecture and
    only revisions from the most recent stable promotion are returned.

    Returns a list of dicts; empty list on any error.
    """
    url = _SNAPSTORE_API.format(name=snap_name)
    print(f"    GET {url} (with Snap-Device-Series header) …")

    # The Snap Store v2 API requires a device series header.
    req = urllib.request.Request(
        url,
        headers={"Snap-Device-Series": "16"},  # series 16 = Ubuntu Core 16+ (current standard)
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        print(f"    ERROR: Snap Store API returned HTTP {exc.code}: {exc.reason}",
              file=sys.stderr)
        return []
    except Exception as exc:
        print(f"    ERROR: could not reach Snap Store API: {exc}", file=sys.stderr)
        return []

    # K8s snaps use "-classic" track naming: "1.32" → "1.32-classic/stable"
    target_track = f"{track}-classic"
    target_risk = "stable"
    revisions: list[dict] = []

    for channel_entry in data.get("channel-map", []):
        channel_info = channel_entry.get("channel", {})
        channel_name = channel_info.get("name", "")  # e.g., "1.32-classic/stable"
        channel_track = channel_info.get("track", "")
        channel_risk = channel_info.get("risk", "")

        if channel_track == target_track and channel_risk == target_risk:
            rev_info = {
                "revision": channel_entry.get("revision"),
                "architecture": channel_info.get("architecture", ""),
                "version": channel_entry.get("version", ""),
                "channel": channel_name,
                "released_at": channel_info.get("released-at", ""),
                "download_url": channel_entry.get("download", {}).get("url", ""),
            }
            revisions.append(rev_info)

    if not revisions:
        print(f"    WARNING: '{target_track}/stable' not found in Snap Store",
              file=sys.stderr)
        return []

    arch_revisions = [revision for revision in revisions if revision["architecture"] == target_arch]
    if not arch_revisions:
        available = ", ".join(sorted({revision["architecture"] for revision in revisions}))
        print(
            f"    WARNING: '{target_track}/stable' has no '{target_arch}' build. "
            f"Available architectures: {available}",
            file=sys.stderr,
        )
        return []

    latest_release = max(revision["released_at"] for revision in arch_revisions)
    latest_revisions = [
        revision for revision in arch_revisions if revision["released_at"] == latest_release
    ]

    print(f"    → {len(latest_revisions)} revision(s) for {target_track}/stable/{target_arch} "
          f"(promoted {latest_release[:10]}: "
          f"{', '.join(str(r['revision']) for r in latest_revisions)})")
    return latest_revisions


# ── Step 2: extract commit SHA from snap BOM ─────────────────────────────────

def extract_bom_commit_hash(snap_name: str, revision: int, arch: str,
                             download_url: str) -> str | None:
    """
    Download a snap from the Snap Store, extract its bom.json, and return the
    commit SHA of the k8s component.

    The BOM (Bill of Materials) is embedded in the snap and contains commit
    hashes for each component.  We use unsquashfs to extract it.
    """
    if not download_url:
        print(f"    WARNING: no download URL available for revision {revision}",
              file=sys.stderr)
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        snap_path = Path(tmpdir) / f"k8s_{arch}_{revision}.snap"
        squashfs_root = Path(tmpdir) / "squashfs-root"

        # Download the snap
        print(f"    Downloading snap revision {revision} ({arch}) …")
        try:
            urllib.request.urlretrieve(download_url, snap_path)  # noqa: S310
        except Exception as exc:
            print(f"    ERROR: could not download snap: {exc}", file=sys.stderr)
            return None

        # Extract bom.json using unsquashfs
        print(f"    Extracting bom.json from snap …")
        result = _run([
            "unsquashfs", "-d", str(squashfs_root), str(snap_path), "bom.json",
        ])
        if result.returncode == 0:
            extracted = squashfs_root / "bom.json"
            if extracted.exists():
                try:
                    bom_data = json.loads(extracted.read_text())
                    commit_hash = bom_data.get("k8s", {}).get("revision")
                    if commit_hash:
                        print(f"    BOM extracted: k8s revision → {commit_hash[:12]}")
                        return commit_hash
                except Exception as exc:
                    print(f"    ERROR: could not parse bom.json: {exc}", file=sys.stderr)
        else:
            print(f"    ERROR running unsquashfs: {result.stderr[:200]}", file=sys.stderr)

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
    target_arch = get_target_architecture()
    print(f"Using target architecture: {target_arch}")

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

        # 1. Get stable revisions from Snap Store
        revisions = get_stable_revisions(SNAP_NAME, track, target_arch)
        if not revisions:
            sections.append(
                f"### Version {track} ###\n"
                "  [SKIPPED] Could not determine current stable revisions.\n"
            )
            continue

        # 2. Try to extract or resolve commit SHA from the first available revision
        current_hash: str | None = None
        for rev_info in revisions:
            revision = rev_info["revision"]
            arch = rev_info["architecture"]
            download_url = rev_info["download_url"]
            print(f"    Resolving revision {revision} ({arch}) …")
            current_hash = extract_bom_commit_hash(SNAP_NAME, revision, arch, download_url)
            if current_hash:
                break

        if current_hash is None:
            tried = ", ".join(str(r["revision"]) for r in revisions)
            sections.append(
                f"### Version {track} ###\n"
                f"  [SKIPPED] Could not extract commit hash from snap revisions ({tried}).\n"
                f"  (Consider providing LAST_DOCUMENTED_HASHES or running from a deployed snap.)\n"
            )
            continue

        print(f"    → current hash:    {current_hash}")

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
        f"# Pending Patch Notices (Snap)\n"
        f"# Generated : {today}\n"
        f"# Snap      : {SNAP_NAME}  ({SNAP_REPO})\n"
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
