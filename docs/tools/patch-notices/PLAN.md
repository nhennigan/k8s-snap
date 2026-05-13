# System Specification: K8s-Snap Patch Notices Updater

> Source: `docs/tools/hackathon-plan.md` — canonical home for this spec.

## 1. Goal

Automate the "archaeology" of identifying, categorizing, and summarizing
user-facing changes for Canonical Kubernetes snaps/charms. The tool moves the
burden from manual discovery to editorial review.

## 2. State Management

File: `metadata/patch-metadata.json`

```json
{
  "tracks": {
    "1.29/stable": {
      "last_documented_sha": "<git-sha>",
      "last_documented_date": "<ISO-8601>"
    }
  }
}
```

This file is git-tracked so that any contributor starts from the correct
bookmark.

## 3. Data Pipeline ("The Archaeology")

To find the "Stable Reality" (finish line for the delta), the tool must:

1. **Query Snap Store API** — find the current revision for a track
   (e.g. `1.30/stable`).
2. **Query Launchpad API** — look up the build record for that revision to
   extract the specific GitHub commit SHA. This is the **riskiest integration**;
   investigate `lp.snaps` API carefully.
3. **Calculate delta** — fetch all GitHub PRs/commits between
   `last_documented_sha` (state) and `current_stable_sha` (Launchpad).

## 4. AI Triage ("The Assembly Line")

Process the delta PR-by-PR:

- **Context provided**: PR title, PR body, full file diff.
- **Truth hierarchy**: File diffs > PR body > PR title. Ignore misleading
  titles when the diff tells a different story.
- **Categories**: Major Features, Deprecations, Bug Fixes, Security,
  Component Bumps, Performance, Documentation, Internal (discarded).
- **Documentation rule**: only include if the change modifies user-facing
  instructions or help commands.

## 5. User Interface: The Markdown Workbook

The tool generates `monthly_review.md` and prints a clickable terminal link.

Sections:

| Section | Content |
|---|---|
| **Included** | AI "benefit-centric" summaries with hidden `<!-- sha:... -->` tags |
| **Verification** | Original PR titles + numbers for fact-checking |
| **Discarded** | Noise items with a one-sentence reason for exclusion |

## 6. Closing the Loop (Finalization)

When the user runs `patch-notices finalize`:

1. Parse the workbook for `<!-- sha:... -->` tags in the Included section.
2. Update `patch-metadata.json` with the latest included SHA.
3. Write `patch-notice-export.md` — clean snippet, no tags, no verification
   noise — ready to paste into a PR.

## 7. Risks and Notes

| Risk | Mitigation |
|---|---|
| Launchpad API mapping | Spike this first; mock it if needed for the demo |
| LLM output quality | Tune system prompt iteratively; diff-first context helps |
| State corruption | Write state atomically; never overwrite on error |
| Rate limits (GitHub) | Use authenticated requests; cache delta locally |

## 8. Out of scope (for the hackathon)

- Automated PR creation
- Web UI
- Multi-repo support
