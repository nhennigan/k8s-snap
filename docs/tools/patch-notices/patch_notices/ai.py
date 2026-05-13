# Copyright 2026 Canonical, Ltd.
# See LICENSE file for licensing details.

"""AI triage: categorise and summarise each PR in the delta.

Truth hierarchy (per spec): file diffs > PR body > PR title.
"""

from __future__ import annotations

import os
from typing import Any

import openai

SYSTEM_PROMPT = """\
You are a technical writer producing monthly patch notices for Canonical Kubernetes.
You will be given a git commit: its title, body, and the aggregate file diff for the release.

## Editorial strategy

- **Focus on impact.** Do not repeat the commit subject. Describe the user-facing
  benefit, operational impact, or reason the change matters.
- **Filter for user action.** Include: bug fixes, features, security-relevant
  dependency updates, deprecation warnings, operational improvements, and significant
  upgrade or rollback behaviour changes.
- **Major docs only.** Include documentation changes only when they introduce a new
  guide, a new supported workflow, a deprecation notice, or a material change in how
  an operator uses or manages the product.
- **Exclude noise.** Discard: copyright changes, linting-only changes, CI-only
  changes, test-only changes, release preparation, and other low-signal maintenance
  unless they directly affect shipped behaviour.
- **Strict revision exclusion.** Discard commits that only update
  architecture-specific snap revision numbers, e.g.
  `Update K8s revisions ["amd64-xxxx", "arm64-xxxx"]`.

## Snap-specific rules

- **Include `Update component versions` commits.** These represent real shipped
  changes and must never be excluded.
- **Distinguish component bumps from revision bookkeeping:**
  - *Include*: packaged component updates — Kubernetes, CNI, containerd, runc, Helm,
    k8s-dqlite, Cilium, CoreDNS, MetalLB, metrics-server, and similar shipped deps.
  - *Exclude*: commits that only move track-specific amd64/arm64 snap revision numbers.
- **Version bumps formatting.** When component updates are present, group them under
  a `Version bumps` bullet at the top of the included items:
  - If exact component names and versions are visible in the input, list each as a
    nested bullet: `- containerd 1.7.x → 1.7.y`
  - If versions changed but exact values are not visible, use a single
    `- Version bumps` bullet without inventing details.

## Related commits

When a commit is clearly part of the same feature story or bug fix as other commits
you have already seen in this batch, set `group_hint` to a short label (e.g.
`"CoreDNS HA"`, `"CoreDNS late-joiner fix"`, `"ServiceArgsController"`). The
workbook will render all commits sharing a `group_hint` as one collapsed entry,
with every SHA listed so the human reviewer can see exactly which commits are
covered. Use `null` for standalone commits.

## Tone

Professional, concise, and focused on stability, upgrade safety, security, and
operator experience.

## Output format

Respond with valid JSON only — no markdown fences:
{
  "action": "include" | "discard",
  "category": "Major Feature" | "Deprecation" | "Bug Fix" | "Security" |
              "Component Bump" | "Performance" | "Documentation" | null,
  "summary": "<benefit-centric sentence, max 120 chars, starts with a verb, or null>",
  "reason": "<one sentence reason if discarded, else null>",
  "group_hint": "<short feature/fix story label shared across related commits, or null>"
}
"""


def triage(prs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run each PR through the LLM. Returns an enriched list of PR records.

    Supports OpenAI directly or any OpenAI-compatible endpoint (e.g. OpenRouter).
    Set OPENAI_BASE_URL to override, e.g.:
      export OPENAI_BASE_URL=https://openrouter.ai/api/v1
      export OPENAI_API_KEY=sk-or-...
    """
    client = openai.OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ.get("OPENAI_BASE_URL"),  # None = use OpenAI default
    )
    results = []
    for pr in prs:
        result = _triage_one(client, pr)
        results.append({**pr, "triage": result})
    return results


def _triage_one(client: openai.OpenAI, pr: dict[str, Any]) -> dict[str, Any]:
    """Triage a single PR. Returns the parsed JSON response."""
    user_content = (
        f"Commit {pr.get('sha', '')[:8]}"
        + (f" (PR #{pr.get('pr_number')})" if pr.get('pr_number') else "")
        + f": {pr.get('title')}\n\n"
        f"Author: {pr.get('author')}\n"
        f"Date: {pr.get('date')}\n\n"
        f"Body:\n{pr.get('body') or '(none)'}\n\n"
        f"Diff:\n{pr.get('diff') or '(not available)'}"
    )
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "openai/gpt-4o"),
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )
    import json

    return json.loads(response.choices[0].message.content)
