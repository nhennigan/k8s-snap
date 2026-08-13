# Patch Notices — Automation Plan

## Goal

Automate the current manual process of:

1. Running the patch-notices tool for all active tracks (one snap + one charm per supported release)
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
  ├── docs/canonicalk8s/releases/snap/<version>.md  (one per active snap track, if changes)
  ├── docs/canonicalk8s/releases/charm/<version>.md (one per active charm track, if changes)
  └── docs/tools/patch-notices/metadata/patch-metadata.json
       │
       ▼
Human reviews PR body (included / discarded / ⚠️ summary per track)
       │
       ▼ (merge)
patch-notices-backport.yaml triggers — creates one backport PR per active release branch
  Each cherry-pick auto-removes files that don't exist on the target branch
  (e.g. 1.35.md is dropped when backporting to release-1.32)
       │
       ▼
Backport PRs reviewed and merged

Total PRs per run: 1 main + one backport per active release
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
- Fix ConfigMap watch recovery after resource version expiration,
  preventing stalled controllers on compacted clusters.
```

Component bumps are always grouped into a single nested "Version bumps" entry.
All other items are flat bullets beneath it. This matches the existing format in
`docs/canonicalk8s/releases/snap/1.35.md`.

---

## Track → release notes file mapping

The mapping is explicit in the `TRACKS` env block in the workflow — there is no
auto-derivation in the code. The `generate` command receives `--release-notes` as
a required argument, so the workflow is the single source of truth.

The naming convention is:

| Source | Track version | Release notes file |
|---|---|---|
| snap | `X.YY` | `docs/canonicalk8s/releases/snap/X.YY.md` |
| charm | `X.YY` | `docs/canonicalk8s/releases/charm/X.YY.md` |

To add a new release, append two lines to the `TRACKS` block and create the
corresponding release notes file. No other changes are needed.

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
- Fix ConfigMap watch recovery after resource version expiration,
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

Under normal operation — workflow runs on `main`, backports applied in order — the
`patch-metadata.json` cherry-picks cleanly onto each release branch because the file
is only modified by this workflow and the base state matches.

If a backport is ever skipped or a release branch diverges, the file may conflict.
The correct resolution is always **"ours"** (keep the release branch's version).
One-time mitigation: add the following to `.gitattributes` so git resolves it
automatically for all future cherry-picks:

```
docs/tools/patch-notices/metadata/patch-metadata.json merge=ours
```

---

## Rate limits and failure handling

GitHub Models limits `gpt-4o` to ~50 requests/day. A full run with
~8 commits per track uses roughly `(commits × tracks) + tracks` requests,
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
| PR granularity | One PR for all active tracks |
| Merge behaviour | Always require human approval |
| Empty delta | Noted in PR body table; no release notes change |
| `finalize` command | Kept for local/manual use |
| `patch_notices_output.md` | No longer produced by the automated workflow |
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
