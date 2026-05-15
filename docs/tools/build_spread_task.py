#!/usr/bin/env python3
"""Smart router: build a spread task.yaml from a scenario or a standalone doc page.

Modes
-----
Scenario mode  (--target matches a name in scenarios.yaml):
    Chains multiple documentation pages into one task.yaml.
    Injects ``set -e`` and ``export SCENARIO_MODE=true`` at the top so
    individual pages can detect they are running inside a chain.

Standalone mode  (--target is a path to a .md file):
    Generates a task.yaml for a single page.
    Injects ``set -e`` but does NOT set SCENARIO_MODE, so conditional
    blocks such as ``sudo k8s bootstrap`` execute normally.

Both modes prepend ``cd "${SPREAD_PATH:-.}"`` before each section so that
path-sensitive commands always start from a known root.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "Error: PyYAML is required. Install with: pip install pyyaml\n"
        "       or: sudo apt-get install python3-yaml",
        file=sys.stderr,
    )
    sys.exit(1)

UPSTREAM_SCRIPT_URL = (
    "https://raw.githubusercontent.com/canonical/operator-workflows"
    "/df449f1e3d1b8babbe9df48bbebcff1e58c9fda9/spread/create_spread_task_file.py"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def find_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def detect_suite(file_path: Path) -> str:
    """Return the SPREAD SUITE value declared in a docs file."""
    content = file_path.read_text(encoding="utf-8")
    for line in content.splitlines():
        match = re.search(r"SPREAD SUITE:\s*([a-z_]+)", line)
        if match:
            return match.group(1)
    raise ValueError(f"No 'SPREAD SUITE:' marker found in {file_path}")


def run_upstream_script(upstream_script: Path, doc_file: Path, output_task: Path) -> None:
    """Invoke the upstream create_spread_task_file.py to extract commands from *doc_file*."""
    subprocess.run(
        [sys.executable, str(upstream_script), str(doc_file), str(output_task)],
        check=True,
    )


def extract_execute_block(task_file: Path) -> list[str]:
    """Return the lines inside ``execute: |`` with the two-space YAML indent removed."""
    lines = task_file.read_text(encoding="utf-8").splitlines()

    execute_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "execute: |":
            execute_idx = i
            break

    if execute_idx is None:
        raise ValueError(f"Missing 'execute: |' block in {task_file}")

    block: list[str] = []
    for line in lines[execute_idx + 1 :]:
        if line.startswith("  "):
            block.append(line[2:])
        elif line.strip() == "":
            block.append("")
        else:
            break  # next top-level YAML key — stop

    if not block:
        raise ValueError(f"Empty execute block in {task_file}")

    return block


# ---------------------------------------------------------------------------
# Task writer
# ---------------------------------------------------------------------------


def write_task(
    output_file: Path,
    summary: str,
    kill_timeout: str,
    sections: list[tuple[str, list[str]]],
    *,
    scenario_mode: bool,
) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        f.write(f"summary: \"{summary}\"\n\n")
        f.write(f"kill-timeout: {kill_timeout}\n\n")
        f.write("execute: |\n")

        # Preamble
        f.write("  set -e\n")
        if scenario_mode:
            f.write("  export SCENARIO_MODE=true\n")
        f.write("\n")

        # Sections
        for title, commands in sections:
            f.write(f'  echo "=== Starting Section: {title} ==="\n')
            f.write('  cd "${SPREAD_PATH:-.}"\n')
            for line in commands:
                f.write(f"  {line}\n")
            f.write("\n")


# ---------------------------------------------------------------------------
# Scenario mode
# ---------------------------------------------------------------------------


def build_scenario(
    scenario_name: str,
    scenarios_file: Path,
    upstream_script: Path,
    repo_root: Path,
    output_dir: Path,
    summary: str,
    kill_timeout: str,
) -> tuple[Path, str]:
    """Generate a combined task.yaml for a named scenario.

    Returns (output_file, suite_name).
    """
    scenarios_data = yaml.safe_load(scenarios_file.read_text(encoding="utf-8"))
    scenario = next(
        (s for s in scenarios_data.get("scenarios", []) if s["name"] == scenario_name),
        None,
    )
    if scenario is None:
        available = [s["name"] for s in scenarios_data.get("scenarios", [])]
        raise ValueError(
            f"Scenario '{scenario_name}' not found in {scenarios_file}.\n"
            f"Available scenarios: {available}"
        )

    suite = scenario["suite"]
    pages = scenario["pages"]
    docs_root = repo_root / "docs" / "canonicalk8s"
    sections: list[tuple[str, list[str]]] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for page in pages:
            doc_file = docs_root / page
            if not doc_file.is_file():
                raise FileNotFoundError(f"Page not found: {doc_file}")
            tmp_task = Path(tmpdir) / page.replace("/", "-")
            run_upstream_script(upstream_script, doc_file, tmp_task)
            commands = extract_execute_block(tmp_task)
            sections.append((Path(page).name, commands))

    output_file = output_dir / suite / f"scenario-{scenario_name}" / "task.yaml"
    write_task(
        output_file,
        summary=summary or f"Scenario: {scenario_name}",
        kill_timeout=kill_timeout,
        sections=sections,
        scenario_mode=True,
    )
    return output_file, suite


# ---------------------------------------------------------------------------
# Standalone mode
# ---------------------------------------------------------------------------


def build_standalone(
    doc_path: Path,
    upstream_script: Path,
    repo_root: Path,
    output_dir: Path,
    summary: str,
    kill_timeout: str,
) -> tuple[Path, str]:
    """Generate a task.yaml for a single documentation page.

    Returns (output_file, suite_name).
    """
    if not doc_path.is_absolute():
        # Accept paths relative to repo root or relative to docs/canonicalk8s/
        candidate = repo_root / doc_path
        if not candidate.is_file():
            candidate = repo_root / "docs" / "canonicalk8s" / doc_path
        doc_path = candidate

    if not doc_path.is_file():
        raise FileNotFoundError(f"File not found: {doc_path}")

    suite = detect_suite(doc_path)

    docs_root = repo_root / "docs" / "canonicalk8s"
    rel = doc_path.relative_to(docs_root)
    task_name = str(rel.with_suffix("")).replace("/", "-")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_task = Path(tmpdir) / "task.yaml"
        run_upstream_script(upstream_script, doc_path, tmp_task)
        commands = extract_execute_block(tmp_task)

    sections = [(doc_path.name, commands)]
    output_file = output_dir / suite / task_name / "task.yaml"
    write_task(
        output_file,
        summary=summary or f"Standalone: {doc_path.name}",
        kill_timeout=kill_timeout,
        sections=sections,
        scenario_mode=False,
    )
    return output_file, suite


# ---------------------------------------------------------------------------
# Detect mode (CI use)
# ---------------------------------------------------------------------------


def run_detect(
    changed_files_input: str,
    scenarios_file: Path,
    upstream_script: Path,
    repo_root: Path,
    output_dir: Path,
    kill_timeout: str,
) -> None:
    """Generate chained task.yaml for every scenario triggered by changed files.

    Called by CI after the standalone task generation loop.  Exits 0 whether
    or not any scenarios were triggered.
    """
    if not scenarios_file.is_file():
        print(f"No scenarios file found at {scenarios_file}, skipping scenario detection.")
        return

    # Build the set of changed files with full relative path from repo root
    changed_set = {
        f"docs/canonicalk8s/{p}"
        for p in changed_files_input.split()
        if p
    }
    if not changed_set:
        print("No changed files provided; skipping scenario detection.")
        return

    data = yaml.safe_load(scenarios_file.read_text(encoding="utf-8"))
    triggered = 0
    for scenario in data.get("scenarios", []):
        pages = {f"docs/canonicalk8s/{p}" for p in scenario["pages"]}
        if not pages.intersection(changed_set):
            continue
        name = scenario["name"]
        print(f"Scenario '{name}' triggered — generating chained task.yaml")
        output_file, suite = build_scenario(
            scenario_name=name,
            scenarios_file=scenarios_file,
            upstream_script=upstream_script,
            repo_root=repo_root,
            output_dir=output_dir,
            summary="",
            kill_timeout=kill_timeout,
        )
        print(f"  Generated: {output_file}")
        triggered += 1

    if triggered == 0:
        print("No scenarios triggered by changed files.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a spread task.yaml from a scenario (chained pages) "
            "or a standalone documentation page."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  # scenario mode
  build_spread_task.py --target fips-disa-stig --upstream-script /path/to/create_spread_task_file.py

  # standalone mode
  build_spread_task.py --target snap/howto/install/fips.md --upstream-script /path/to/create_spread_task_file.py

  # CI detect mode (generates all scenarios triggered by changed files)
  build_spread_task.py --detect --changed-files "snap/howto/install/fips.md" --upstream-script /path/to/create_spread_task_file.py
""",
    )
    parser.add_argument(
        "--target",
        default=None,
        help=(
            "Scenario name from scenarios.yaml, "
            "or path to a .md file (relative to repo root or docs/canonicalk8s/)."
        ),
    )
    parser.add_argument(
        "--detect",
        action="store_true",
        help=(
            "CI detect mode: read --changed-files and generate chained task.yaml "
            "for every scenario whose pages intersect the changed set."
        ),
    )
    parser.add_argument(
        "--changed-files",
        default="",
        help=(
            "Space-delimited docs/canonicalk8s/-relative file list. "
            "Used with --detect."
        ),
    )
    parser.add_argument(
        "--upstream-script",
        required=True,
        type=Path,
        help="Path to the upstream create_spread_task_file.py.",
    )
    parser.add_argument(
        "--scenarios-file",
        type=Path,
        default=None,
        help="Path to scenarios.yaml (default: docs/scenarios.yaml inside repo root).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repo root directory (default: auto-detected via git).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Base output directory (default: tests/spread-generated inside repo root).",
    )
    parser.add_argument(
        "--summary",
        default="",
        help="Override the summary field in the generated task.yaml.",
    )
    parser.add_argument(
        "--kill-timeout",
        default="30m",
        help="kill-timeout value for the generated task (default: 30m).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.detect and not args.target:
        print("Error: one of --target or --detect is required.", file=sys.stderr)
        sys.exit(1)

    # Resolve defaults
    repo_root: Path = args.repo_root or find_repo_root()
    scenarios_file: Path = args.scenarios_file or repo_root / "docs" / "scenarios.yaml"
    output_dir: Path = args.output_dir or repo_root / "tests" / "spread-generated"
    upstream_script: Path = args.upstream_script

    if not upstream_script.is_file():
        print(
            f"Error: upstream script not found at {upstream_script}\n"
            f"  Fetch it with:\n"
            f"    curl -fsSL '{UPSTREAM_SCRIPT_URL}' -o '{upstream_script}'",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- Detect mode (CI) ---
    if args.detect:
        run_detect(
            changed_files_input=args.changed_files,
            scenarios_file=scenarios_file,
            upstream_script=upstream_script,
            repo_root=repo_root,
            output_dir=output_dir,
            kill_timeout=args.kill_timeout,
        )
        return

    target = args.target

    # Detect mode: check if target matches a scenario name
    is_scenario = False
    if scenarios_file.is_file():
        data = yaml.safe_load(scenarios_file.read_text(encoding="utf-8"))
        is_scenario = any(
            s["name"] == target for s in data.get("scenarios", [])
        )

    if is_scenario:
        output_file, suite = build_scenario(
            scenario_name=target,
            scenarios_file=scenarios_file,
            upstream_script=upstream_script,
            repo_root=repo_root,
            output_dir=output_dir,
            summary=args.summary,
            kill_timeout=args.kill_timeout,
        )
    else:
        output_file, suite = build_standalone(
            doc_path=Path(target),
            upstream_script=upstream_script,
            repo_root=repo_root,
            output_dir=output_dir,
            summary=args.summary,
            kill_timeout=args.kill_timeout,
        )

    # Print summary and the spread command
    rel_task_dir = output_file.parent.relative_to(repo_root)
    print(f"\nGenerated: {output_file}")
    print(f"\nTo run the spread test:")
    print(f"  cd {repo_root}/docs")
    print(f"  spread <system>:{rel_task_dir}/")
    print(f"\nFor local testing with multipass:")
    print(f"  cd {repo_root}/docs")
    print(f"  spread multipass:ubuntu-24.04-64:{rel_task_dir}/")


if __name__ == "__main__":
    main()
