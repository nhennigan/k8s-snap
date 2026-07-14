# Patch Notices — Automation Plan

## Goal

Automate the current manual process of:

1. Running the patch-notices tool for all 8 tracks (4 snap + 4 charm)
2. Creating a PR to `main` with updated release notes
3. Manually backporting the docs changes to all active release branches

The automation produces the same output — a human-reviewed PR — but eliminates the
archaeology, AI triage, and backport orchestration steps.

---

## Architecture

### Workflow trigger

A new GitHub Actions workflow (`.github/workflows/update-patch-notices.yaml`) runs:

- **Scheduled**: 1st of every month (`cron: "0 10 1 * *"`)
- **On demand**: `workflow_dispatch`

The workflow runs on **`main` only** (not on release branches). This mirrors the current
manual process and avoids the problem of needing to remove CI from release branches when
a new release is cut.

### Full PR flow

```
Workflow runs on main
       │
       ▼
ONE PR to main
  ├── docs/canonicalk8s/releases/snap/1.32.md  (if changes)
  ├── docs/canonicalk8s/releases/snap/1.33.md  (if changes)
  ├── docs/canonicalk8s/releases/snap/1.34.md  (if changes)
  ├── docs/canonicalk8s/releases/snap/1.35.md  (if changes)
  ├── docs/canonicalk8s/releases/charm/1.32.md (if changes)
  ├── docs/canonicalk8s/releases/charm/1.33.md (if changes)
  ├── docs/canonicalk8s/releases/charm/1.34.md (if changes)
  ├── docs/canonicalk8s/releases/charm/1.35.md (if changes)
  └── docs/tools/patch-notices/metadata/patch-metadata.json
  + labels: backport release-1.32, release-1.33, release-1.34, release-1.35
       │
       ▼
Human reviews PR body (included / discarded / ⚠️ summary per track)
       │
       ▼ (merge)
backport.yaml auto-creates 4 backport PRs
  ├── → release-1.32  (1.32 release notes + any older versions present in the commit)
  ├── → release-1.33  (same commit — carries 1.32 + 1.33 file changes)
  ├── → release-1.34  (same commit — carries 1.32 + 1.33 + 1.34 file changes)
  └── → release-1.35  (same commit — carries all changed release notes files)
       │
       ├─ Note: a release-X.YY branch receives the backport even if version X.YY
       │  had no new notices, because it still needs the older version file updates.
       │
       ▼
Each backport PR has a small patch-metadata.json conflict
(reviewer accepts "ours" — keeps the release branch's own state)
       │
       ▼
Backport PRs reviewed and merged

Total PRs per fortnight: 5  (1 main + 4 backports)
```

---

## Release notes file insertion

Each track's patch notice entry is inserted as a new dated section at the **top** of the
`## Patch notices` block in the relevant release notes file. If the section does not yet
exist, it is created at the correct location:

- **Snap** release notes: after `## Upgrade notes`
- **Charm** release notes: after `## Also in this release`

Before inserting, the content passes through the same clean pipeline used by `finalize`:

- `<!-- sha:... -->` tags removed
- `**Category**` labels stripped from bullet lines (same as `export_clean` in `workbook.py`)
- `⚠️` blockquote callouts removed (reviewer warnings, not for publication)
- Group hint lines removed

Format of each inserted entry (clean — no internal tags or category labels):

```markdown
## Patch notices

Jul 15, 2026

- Version bumps
    - Kubernetes v1.35.3
    - containerd v1.7.30
    - runc v1.3.4
- Fixes ConfigMap watch recovery after resource version expiration,
  preventing stalled controllers on compacted clusters.
```

Component bumps are always grouped into a single nested "Version bumps" entry.
All other items are flat bullets beneath it. This matches the existing format in
`docs/canonicalk8s/releases/snap/1.35.md`.

---

## Track → release notes file mapping

| Track | File |
|---|---|
| `snap:1.35-classic/stable` | `docs/canonicalk8s/releases/snap/1.35.md` |
| `snap:1.34-classic/stable` | `docs/canonicalk8s/releases/snap/1.34.md` |
| `snap:1.33-classic/stable` | `docs/canonicalk8s/releases/snap/1.33.md` |
| `snap:1.32-classic/stable` | `docs/canonicalk8s/releases/snap/1.32.md` |
| `charm:1.35/stable` | `docs/canonicalk8s/releases/charm/1.35.md` |
| `charm:1.34/stable` | `docs/canonicalk8s/releases/charm/1.34.md` |
| `charm:1.33/stable` | `docs/canonicalk8s/releases/charm/1.33.md` |
| `charm:1.32/stable` | `docs/canonicalk8s/releases/charm/1.32.md` |

---

## PR body structure

The table uses the human-readable release version so it's immediately clear which release
each row corresponds to. The `source` column distinguishes snap from charm.

```markdown
## Patch notices — 2026-07-15

| Release | Source | Status | Included | Discarded | ⚠️ |
|---|---|---|---|---|---|
| 1.35 | snap | ✅ Updated | 3 | 4 | 1 |
| 1.35 | charm | ✅ Updated | 2 | 5 | 0 |
| 1.34 | snap | — Up to date | | | |
| 1.34 | charm | ✅ Updated | 1 | 6 | 0 |
| 1.33 | snap | ✅ Updated | 2 | 3 | 0 |
| ... | | | | | |

<details><summary>Snap 1.35 — 3 included, 4 discarded, 1 ⚠️</summary>

### Included
- Fixes ConfigMap watch recovery after resource version expiration,
  preventing stalled controllers on compacted clusters.
- Updates containerd to v1.7.30 and runc to v1.3.4.

### ⚠️ Large diff — verify manually before approving
- `abc1234` (PR #2616) — docs: Upgrade sphinx stack to v2
  _(triaged from PR title and description only)_

### Discarded
- `def5678` PR #2595 — fix(test): validate previous_track
  _internal test change, no operator impact_

</details>

<details><summary>Charm 1.35 — 2 included, 5 discarded</summary>
...
</details>
```

---

## The `patch-metadata.json` conflict

The `patch-metadata.json` state file will conflict in every backport PR because each
release branch maintains its own tracking state. Two options:

**Option A — `.gitattributes` merge driver (recommended for zero-touch backports)**

Add one line to `.gitattributes` so git always keeps "ours" (the release branch's version)
when cherry-picking the metadata file. One-time setup; all future backport conflicts
self-resolve with no reviewer action needed.

**Option B — `draft_commit_conflicts` (minimal change)**

Change `conflict_resolution` in `backport.yaml` from `fail` to `draft_commit_conflicts`.
Backport PRs are created as drafts when there is a conflict. A reviewer accepts "ours"
for the JSON file (~10 seconds) and converts the PR to ready.

---

## Code changes required

### 1. New `generate` command — `patch_notices/cli.py`

The CI entry point. Combines fetch + AI review + write to release notes in one command:

```bash
patch-notices generate \
  --track 1.35-classic/stable \
  --source snap \
  --release-notes docs/canonicalk8s/releases/snap/1.35.md \
  --summary-out /tmp/summary-snap-1.35.json
```

| Delta state | Action |
|---|---|
| Has included commits | Writes dated entry to release notes, updates `patch-metadata.json`, writes summary JSON |
| All commits discarded | Advances bookmark only, writes `{status: "all-discarded"}` summary, no release notes change |
| Empty delta | Writes `{status: "up-to-date"}` summary, no files touched |

The existing `fetch`, `review`, and `finalize` commands are **kept** for local/manual use.

### 2. New `pr-body` command — `patch_notices/cli.py`

Reads all per-track summary JSONs and prints the PR body markdown to stdout:

```bash
patch-notices pr-body --summaries-dir /tmp/summaries/ > pr_body.md
```

Per-track summary JSON structure:

```json
{
  "track": "snap:1.35-classic/stable",
  "status": "updated",
  "date": "2026-07-15",
  "included": [{"category": "Bug Fix", "summary": "..."}],
  "discarded": [{"sha": "...", "title": "...", "reason": "..."}],
  "limited_context": [{"sha": "...", "title": "..."}]
}
```

### 3. New `insert_patch_notice()` — `patch_notices/workbook.py`

Inserts a dated patch notice entry into the release notes file:

- Locates the `## Patch notices` heading, or creates it at the correct location:
  - Snap: after `## Upgrade notes`
  - Charm: after `## Also in this release`
- Prepends the new dated entry at the top of that section (newest first)
- Writes the file atomically

Also adds `build_track_summary(triage_results, track, date)` which returns the
structured dict written to the per-track summary JSON by `generate`.

### 4. New workflow — `.github/workflows/update-patch-notices.yaml`

All 8 tracks are declared in **one place** — the `TRACKS` env block at the top of the
workflow. When a new release is cut, add two lines here and nowhere else:

```yaml
name: Update patch notices

on:
  schedule:
    - cron: "0 10 1 * *"
  workflow_dispatch:

env:
  OPENAI_API_KEY: ${{ secrets.PATCH_NOTICES_OPENAI_KEY }}
  OPENAI_BASE_URL: ${{ secrets.PATCH_NOTICES_OPENAI_BASE_URL }}
  OPENAI_MODEL: gpt-4o
  OPENAI_GROUP_MODEL: gpt-4o-mini
  # Use BOT_TOKEN (not github.token) so the created PR triggers CI checks.
  # github.token-created PRs are blocked from triggering other workflows
  # by GitHub's anti-infinite-loop protection.
  GH_TOKEN: ${{ secrets.BOT_TOKEN }}
  # -----------------------------------------------------------------------
  # TRACKS — one entry per active release, snap then charm.
  # To add 1.36 when it ships: append the two lines marked ADD BELOW.
  # To retire 1.32 at EOL: remove its two lines.
  # -----------------------------------------------------------------------
  TRACKS: |
    snap:1.35-classic/stable docs/canonicalk8s/releases/snap/1.35.md
    snap:1.34-classic/stable docs/canonicalk8s/releases/snap/1.34.md
    snap:1.33-classic/stable docs/canonicalk8s/releases/snap/1.33.md
    snap:1.32-classic/stable docs/canonicalk8s/releases/snap/1.32.md
    charm:1.35/stable        docs/canonicalk8s/releases/charm/1.35.md
    charm:1.34/stable        docs/canonicalk8s/releases/charm/1.34.md
    charm:1.33/stable        docs/canonicalk8s/releases/charm/1.33.md
    charm:1.32/stable        docs/canonicalk8s/releases/charm/1.32.md
    # ADD BELOW when 1.36 ships:
    # snap:1.36-classic/stable docs/canonicalk8s/releases/snap/1.36.md
    # charm:1.36/stable        docs/canonicalk8s/releases/charm/1.36.md

jobs:
  generate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
```

The job iterates `$TRACKS` in a shell loop, running `patch-notices generate` for each
line and collecting the `--summary-out` JSON files. The backport labels are derived
automatically from the track list (every `release-X.YY` present in the tracks list
gets a corresponding `backport release-X.YY` label).

Uses `peter-evans/create-pull-request@v6` (same action as `update-components.yaml`).

PR settings:
- Title: `docs: Update patch notices YYYY-MM-DD`
- Branch: `auto/patch-notices-YYYY-MM-DD`
- Labels: auto-derived — `backport release-1.32`, `backport release-1.33`,
  `backport release-1.34`, `backport release-1.35` (grows automatically as tracks are added)

---

## Rate limits and failure handling

GitHub Models limits `gpt-4o` to ~50 requests/day. A full 8-track run with
~8 commits per track uses ~72 requests (8 commits × 8 tracks + 8 grouping calls),
which can exceed the daily limit on a busy fortnight.

**Automatic notification:** GitHub emails the workflow author whenever a scheduled
workflow fails, so rate limit failures are not silent. No extra setup required.

**Partial failure handling:** If a track fails mid-run, the workflow should collect
the error and include it in the PR body (or skip PR creation and open a GitHub issue
if no tracks succeeded). This prevents a silent partial update.

**Mitigation options:**
- Use OpenRouter instead of GitHub Models — higher rate limits, configurable spend cap
- Add a retry step with exponential backoff for rate-limit errors (HTTP 429)
- Switch `OPENAI_GROUP_MODEL` to `gpt-4o-mini` which has a higher daily limit
  (already the default — ensure the endpoint supports it)

---

## Credentials

Add as repo secrets:

| Secret | Purpose | Value |
|---|---|---|
| `PATCH_NOTICES_OPENAI_KEY` | AI triage API key | GitHub Models PAT (no scopes needed) or OpenRouter key |
| `PATCH_NOTICES_OPENAI_BASE_URL` | API endpoint | `https://models.inference.ai.azure.com` or `https://openrouter.ai/api/v1` |
| `BOT_TOKEN` | PR creation (so CI triggers) | Same bot token used by `update-components.yaml` — no new secret needed |

If using GitHub Models with the repo's built-in `github.token`, no extra secrets are
needed — set `OPENAI_API_KEY: ${{ github.token }}` and
`OPENAI_BASE_URL: https://models.inference.ai.azure.com` directly in the workflow YAML.

---

## Verification steps

1. Run `generate` locally for one track — confirm the dated entry appears at the top
   of the `## Patch notices` section in the correct release notes file
2. Run `pr-body` on the collected summaries — confirm the table and collapsible sections
   render correctly on GitHub
3. Trigger the workflow via `workflow_dispatch` on a test branch — confirm one PR is
   created targeting `main` with all backport labels applied
4. Confirm `patch-metadata.json` is committed in the PR
5. Merge the test PR and confirm `backport.yaml` creates the expected 4 backport PRs

---

## Decisions

| Decision | Choice |
|---|---|
| PR granularity | One PR for all 8 tracks |
| Merge behaviour | Always require human approval |
| Empty delta | Noted in PR body table; no release notes change |
| `finalize` command | Kept for local/manual use |
| `patch-notice-export.md` | No longer produced by the automated workflow |
| Backport mechanism | Existing `backport.yaml` via labels |

---

## Out of scope

- Automated merge of the main PR
- Removing active tracks from the list when a release reaches end-of-life
  (manual update to the workflow YAML matrix)
- Mattermost failure notifications (GitHub's built-in email covers the baseline;
  can add Mattermost via the existing `mattermost.py` pattern if richer alerting
  is needed)
- Web UI or dashboard for reviewing triage decisions
