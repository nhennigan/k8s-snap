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

- **Scheduled**: 1st and 15th of every month (`cron: "0 10 1,15 * *"`)
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
  ├── → release-1.32  (only 1.32 release notes changes)
  ├── → release-1.33  (1.32 + 1.33 changes)
  ├── → release-1.34  (1.32 + 1.33 + 1.34 changes)
  └── → release-1.35  (all changes)
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

Format of each inserted entry:

```markdown
## Patch notices

Jul 15, 2026

- **Bug Fix** Fixes ConfigMap watch recovery after resource version expiration,
  preventing stalled controllers on compacted clusters.
- **Component Bump** Updates containerd to v1.7.30 and runc to v1.3.4.
```

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

```markdown
## Patch notices — 2026-07-15

| Track | Status | Included | Discarded | ⚠️ Large diff |
|---|---|---|---|---|
| snap:1.35-classic/stable | ✅ Updated | 3 | 4 | 1 |
| snap:1.34-classic/stable | — Up to date | | | |
| charm:1.35/stable | ✅ Updated | 2 | 5 | 0 |
| ... | | | | |

<details><summary>snap:1.35-classic/stable — 3 included, 4 discarded</summary>

### Included
- **Bug Fix** Fixes ConfigMap watch recovery after resource version expiration...
- **Component Bump** Updates containerd to v1.7.30 and runc to v1.3.4.

### ⚠️ Large diff — verify manually
- `abc1234` (PR #2616) — docs: Upgrade sphinx stack to v2

### Discarded
- `def5678` PR #2595 — fix(test): validate previous_track | internal test change

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

Key settings:

```yaml
name: Update patch notices

on:
  schedule:
    - cron: "0 10 1,15 * *"
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    env:
      OPENAI_API_KEY: ${{ secrets.PATCH_NOTICES_OPENAI_KEY }}
      OPENAI_BASE_URL: ${{ secrets.PATCH_NOTICES_OPENAI_BASE_URL }}
      OPENAI_MODEL: gpt-4o
      OPENAI_GROUP_MODEL: gpt-4o-mini
      GITHUB_TOKEN: ${{ github.token }}
```

Uses `peter-evans/create-pull-request@v6` (same action as `update-components.yaml`).

PR settings:
- Title: `docs: Update patch notices YYYY-MM-DD`
- Branch: `auto/patch-notices-YYYY-MM-DD`
- Labels: `backport release-1.32`, `backport release-1.33`, `backport release-1.34`,
  `backport release-1.35`

---

## Credentials

Add as repo secrets:

| Secret | Purpose | Value |
|---|---|---|
| `PATCH_NOTICES_OPENAI_KEY` | AI triage API key | GitHub Models PAT (no scopes needed) or OpenRouter key |
| `PATCH_NOTICES_OPENAI_BASE_URL` | API endpoint | `https://models.inference.ai.azure.com` or `https://openrouter.ai/api/v1` |

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
- Mattermost notifications (can be added later via the existing `mattermost.py` pattern)
- Web UI or dashboard for reviewing triage decisions
