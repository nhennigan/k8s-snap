# patch-notices

Automates the monthly patch-notices update for Canonical Kubernetes.

It pulls the delta of PRs since the last documented commit, runs AI triage,
and produces a human-editable Markdown workbook. Once approved, `finalize`
strips the internal tags and writes a clean snippet ready to paste into a PR.

## Prerequisites

- Python 3.11+
- An OpenAI API key (or compatible endpoint)
- Network access to the Snap Store, Launchpad, and GitHub APIs

## Setup

```bash
cd docs/tools/patch-notices
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Set the required environment variable:

```bash
# OpenAI directly:
export OPENAI_API_KEY=sk-...

# Or OpenRouter (recommended — supports spend limits):
export OPENAI_API_KEY=sk-or-...
export OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

Optionally, set a GitHub token to raise the API rate limit from 60 to 5000
requests/hour (useful if you process a large delta):

```bash
export GITHUB_TOKEN=ghp_...  # optional, read-only public_repo scope
```

## The three commands

### 1. fetch — pull the PR delta

```bash
patch-notices fetch --track 1.30/stable
```

Queries the Snap Store for the current stable revision, resolves the build SHA
via Launchpad, then fetches all PRs between `last_documented_sha`
(from `metadata/patch-metadata.json`) and that SHA.
Writes a raw delta to `metadata/delta-<track>.json`.

### 2. review — run AI triage and open the workbook

```bash
patch-notices review --track 1.30/stable
```

Reads the delta, processes each PR through the AI (diff > body > title),
and writes `monthly_review.md` in the current directory.
Prints a clickable link to the file.

The workbook has three sections:
- **Included** — benefit-centric summaries tagged `<!-- sha:... -->`
- **Verification** — original PR titles and numbers for fact-checking
- **Discarded** — noise items with a one-sentence reason

Edit the workbook freely: delete lines, rewrite summaries, move items between
sections. The `<!-- sha:... -->` tags are the only thing `finalize` reads.

### 3. finalize — close the loop

```bash
patch-notices finalize --track 1.30/stable
```

Parses the workbook for `<!-- sha:... -->` tags, updates
`metadata/patch-metadata.json` with the latest included SHA and today's date,
then writes `patch-notice-export.md` — a clean snippet with all internal tags
and verification noise removed.

## State file

`metadata/patch-metadata.json` is git-tracked. Commit it after each monthly
run so the next person who runs `fetch` starts from the right place.

## See also

[PLAN.md](PLAN.md) — full system specification.
