# Copyright 2026 Canonical, Ltd.
# See LICENSE file for licensing details.

"""Assemble and parse the Markdown workbook.

Workbook structure
------------------
## Included
<!-- sha:abc1234 -->
- **Major Feature** Adds XYZ support, reducing manual steps by ...

## Verification
- #42 — Original PR title

## Discarded
- #99 — Original title | _Reason: internal refactor, no user impact_
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SHA_TAG_RE = re.compile(r"<!--\s*sha:([0-9a-f]{7,40})\s*-->")


def _group_included(included: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Return a list of groups. Standalone commits are groups of size 1.
    Commits sharing a non-null group_hint are collected together, in first-seen order.
    """
    groups: list[list[dict[str, Any]]] = []
    hint_index: dict[str, int] = {}  # group_hint -> index in groups
    for r in included:
        hint = r["triage"].get("group_hint") or None
        if hint is None:
            groups.append([r])
        elif hint in hint_index:
            groups[hint_index[hint]].append(r)
        else:
            hint_index[hint] = len(groups)
            groups.append([r])
    return groups


CATEGORY_ORDER = [
    "Major Feature",
    "Security",
    "Deprecation",
    "Bug Fix",
    "Performance",
    "Component Bump",
    "Documentation",
]


def write(triage_results: list[dict[str, Any]], output_path: str) -> None:
    """Render triage results into the three-section workbook."""
    included = [r for r in triage_results if r["triage"]["action"] == "include"]
    discarded = [r for r in triage_results if r["triage"]["action"] == "discard"]

    lines: list[str] = ["# Monthly Patch Notice Review\n"]

    # -- Included ----------------------------------------------------------
    lines.append("## Included\n")
    lines.append(
        "> Edit summaries freely. Keep the `<!-- sha:... -->` tags — "
        "`finalize` uses them to update state.\n"
    )
    groups = _group_included(_sort_by_category(included))
    for group in groups:
        if len(group) == 1:
            r = group[0]
            sha = r.get("sha", "unknown")
            category = r["triage"].get("category", "")
            summary = r["triage"].get("summary", "")
            lines.append(f"<!-- sha:{sha} -->")
            lines.append(f"- **{category}** {summary}")
        else:
            # Multi-commit group: one sha tag per commit, one combined bullet
            best = _best_in_group(group)
            category = best["triage"].get("category", "")
            summary = best["triage"].get("summary", "")
            hint = best["triage"].get("group_hint", "")
            for r in group:
                lines.append(f"<!-- sha:{r.get('sha', 'unknown')} -->")
            lines.append(f"- **{category}** {summary}")
            covers = ", ".join(
                f"`{r.get('sha','')[:8]}` {r.get('title', '')}"
                for r in group
            )
            lines.append(f"  _(Group: {hint} — covers: {covers})_")
    lines.append("")

    # -- Verification ------------------------------------------------------
    lines.append("## Verification\n")
    lines.append("> Cross-check summaries against original commit titles.\n")
    for r in included:
        sha = r.get('sha', 'unknown')[:8]
        pr = f" (PR #{r['pr_number']})" if r.get('pr_number') else ""
        url = r.get('pr_url') or r.get('html_url', '')
        lines.append(f"- [`{sha}`]({url}){pr} — {r.get('title')}")
    lines.append("")

    # -- Discarded ---------------------------------------------------------
    lines.append("## Discarded\n")
    lines.append(
        "> Items the AI considers noise. Move to Included (with a sha tag) "
        "if you disagree.\n"
    )
    for r in discarded:
        reason = r["triage"].get("reason", "")
        sha = r.get('sha', 'unknown')[:8]
        pr = f" PR #{r['pr_number']}" if r.get('pr_number') else ""
        lines.append(f"- `{sha}`{pr} — {r.get('title')} | _{reason}_")
    lines.append("")

    Path(output_path).write_text("\n".join(lines))


def parse_included_shas(workbook_path: str) -> list[str]:
    """Return all SHAs found in <!-- sha:... --> tags, in document order."""
    text = Path(workbook_path).read_text()
    # Only parse SHAs that appear before the Verification section
    included_section = text.split("## Verification")[0]
    return SHA_TAG_RE.findall(included_section)


def export_clean(workbook_path: str, export_path: str) -> None:
    """Write a clean copy of the Included section, stripped of all tags."""
    text = Path(workbook_path).read_text()
    included_section = text.split("## Verification")[0]
    # Remove sha tags and blockquote hints
    clean = SHA_TAG_RE.sub("", included_section)
    clean = re.sub(r"^> .*\n", "", clean, flags=re.MULTILINE)
    # Collapse multiple blank lines
    clean = re.sub(r"\n{3,}", "\n\n", clean).strip() + "\n"
    Path(export_path).write_text(clean)


def _best_in_group(group: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the commit from the group with the highest-priority category."""
    return min(
        group,
        key=lambda r: (
            CATEGORY_ORDER.index(r["triage"].get("category", ""))
            if r["triage"].get("category") in CATEGORY_ORDER
            else len(CATEGORY_ORDER)
        ),
    )


def _sort_by_category(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def _key(r: dict[str, Any]) -> int:
        cat = r["triage"].get("category", "")
        try:
            return CATEGORY_ORDER.index(cat)
        except ValueError:
            return len(CATEGORY_ORDER)

    return sorted(items, key=_key)
