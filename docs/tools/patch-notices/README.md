# patch-notices

Automates the monthly patch-notices update for Canonical Kubernetes.

For manual use, it pulls the PR delta, runs AI triage, and produces a
human-editable Markdown workbook. Once approved, `finalize` strips the internal
tags and writes a clean snippet. For CI use, `generate` combines all three steps
and writes directly into the release notes file.

## Prerequisites

- Python 3.11+
- An OpenAI API key (or compatible endpoint)
- Network access to the Snap Store, Launchpad, Charmhub, and GitHub APIs

## Setup

```bash
cd docs/tools/patch-notices
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Set the required environment variable:

```bash
# GitHub Models (uses your Copilot licence — no additional spend):
# Create a PAT at https://github.com/settings/tokens (no scopes required)
export OPENAI_API_KEY=ghp_...
export OPENAI_BASE_URL=https://models.inference.ai.azure.com
export OPENAI_MODEL=gpt-4o

# Or OpenAI directly:
export OPENAI_API_KEY=sk-...

# Or OpenRouter (supports spend limits):
export OPENAI_API_KEY=sk-or-...
export OPENAI_BASE_URL=https://openrouter.ai/api/v1
export OPENAI_MODEL=openai/gpt-4o
```

Optionally, set a GitHub token to raise the API rate limit from 60 to 5000
requests/hour (useful if you process a large delta):

```bash
export GITHUB_TOKEN=ghp_...  # optional, read-only public_repo scope
```

The grouping pass (Pass 2 of `review`) uses a separate, lighter model. To override the
default:

```bash
export OPENAI_GROUP_MODEL=gpt-4o-mini   # default; change if your endpoint lacks this model
```

## Manual workflow

Pass `--track` as a short version number, e.g. `1.32`. The tool expands this
to `1.32-classic/stable` for snap (the default) or `1.32/stable` for charm.
State is stored under the key `snap:1.32-classic/stable` in `patch-metadata.json`.

### 1. fetch — pull the PR delta

```bash
patch-notices fetch --track 1.32
```

Queries the Snap Store for the current stable revision, resolves the build SHA
via Launchpad, then fetches all PRs between `last_documented_sha`
(from `metadata/patch-metadata.json`) and that SHA.
Writes a raw delta to `metadata/delta-<track>.json`.

### 2. review — run AI triage and open the workbook

```bash
patch-notices review --track 1.32
```

Reads the delta, processes each PR through the AI (diff > body > title),
and writes `patch_notices_review.md` in the current directory.
Prints the path to the written file.

The workbook has three sections:
- **Included** — benefit-centric summaries tagged `<!-- sha:... -->`
- **Verification** — original PR titles and numbers for fact-checking
- **Discarded** — noise items with a one-sentence reason

Edit the workbook freely: delete lines, rewrite summaries, move items between
sections. The `<!-- sha:... -->` tags are the only thing `finalize` reads.

### 3. finalize — close the loop

```bash
patch-notices finalize --track 1.32
```

Parses the workbook for `<!-- sha:... -->` tags, updates
`metadata/patch-metadata.json` with the latest included SHA and today's date,
then writes `patch_notices_output.md` — a clean snippet with all internal tags
and verification noise removed.

If all commits were discarded (no included items), the export file is not
written but the bookmark is still advanced to the latest delta SHA so the
next run does not re-process the same commits.

If `fetch` found no new commits at all (empty delta), only the
`last_documented_date` is updated — the SHA is left unchanged.

## State file

`metadata/patch-metadata.json` is git-tracked. Commit it after each monthly
run so the next person who runs `fetch` starts from the right place.

## Charm patch notices

The same three commands work for Canonical Kubernetes charm releases
(`canonical/k8s-operator`) by adding `--source charm`.

### How it works

Instead of the Snap Store + Launchpad pipeline, the charm path:

1. Queries **Charmhub** for the current stable revision of the `k8s` charm.
2. Maps that revision to a **git SHA** via its GitHub tag (`k8s-rev<N>` in
   `canonical/k8s-operator`).
3. Fetches all commits between `last_documented_sha` and that SHA.

### Charm track format

Charm tracks use `<version>/stable` internally (no `-classic` suffix). Passing
`--source charm --track 1.32` expands to `1.32/stable`. State is stored under
the key `charm:1.32/stable` so snap and charm entries never collide in
`patch-metadata.json`.

### Initial setup

Before the first run, set the `last_documented_sha` for each charm track in
`metadata/patch-metadata.json`. Find the right SHA by looking up the
`k8s-rev<N>` tag on GitHub that corresponds to the charm revision that was
stable at your last patch notice date:

```
https://github.com/canonical/k8s-operator/releases/tag/k8s-rev<N>
```

### Manual workflow commands

```bash
# 1. Pull the commit delta from canonical/k8s-operator
patch-notices fetch --source charm --track 1.32

# 2. Run AI triage with the charm-specific prompt; write the workbook
patch-notices review --source charm --track 1.32 --output charm_review.md

# 3. Update state and export the clean patch notice
patch-notices finalize --source charm --track 1.32 \
  --workbook-path charm_review.md --export charm-export.md
```

Use `--output` and `--export` to avoid overwriting your snap workbook files
when processing both snap and charm tracks in the same session.

## Automated workflow (CI)

The `generate` and `pr-body` commands are used by the GitHub Actions workflow
to process all tracks automatically. See [ARCHITECTURE.md](ARCHITECTURE.md) for the
full architecture.

### generate — fetch, triage, and insert in one step

```bash
patch-notices generate \
  --track 1.32 \
  --release-notes docs/canonicalk8s/releases/snap/1.32.md \
  --summary-out summaries/snap-1.32.json
```

Combines `fetch` + AI triage + direct insertion into the release notes file.
Advances the state bookmark on success. Writes a summary JSON to `--summary-out`
(used by `pr-body`) regardless of outcome.

Use `--workbook <path>` to also write the full Included/Discarded/Verification
workbook for local inspection — this does not affect the release notes or state.

Works for both snap and charm tracks via `--source charm`.

### pr-body — generate the PR body

```bash
patch-notices pr-body --summaries-dir summaries/ --output pr-body.md
```

Reads all `*.json` files in `--summaries-dir` (written by `generate`) and
produces a formatted PR body with a summary table and per-track collapsible
detail sections. Use `--output -` (default) to print to stdout.

## See also

[PLAN.md](PLAN.md) — original system specification (snap pipeline only; predates charm support).

[ARCHITECTURE.md](ARCHITECTURE.md) — architecture and PR flow for the automated monthly workflow.
