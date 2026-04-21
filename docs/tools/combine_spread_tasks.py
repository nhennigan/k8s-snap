#!/usr/bin/env python3
"""Combine multiple generated spread task files into one ordered scenario task."""

from __future__ import annotations

import argparse
from pathlib import Path


def extract_execute_block(task_file: Path) -> list[str]:
    """Return execute block lines (without two-space YAML indentation)."""
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
            # Stop if we hit another top-level key.
            break

    if not block:
        raise ValueError(f"Empty execute block in {task_file}")

    return block


def write_combined_task(output_file: Path, summary: str, kill_timeout: str, sections: list[tuple[str, list[str]]]) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        f.write(f"summary: {summary}\n\n")
        f.write(f"kill-timeout: {kill_timeout}\n\n")
        f.write("execute: |\n")

        for title, commands in sections:
            f.write(f"  echo \"=== {title} ===\"\n")
            for command_line in commands:
                f.write(f"  {command_line}\n")
            f.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine generated spread task.yaml files into one ordered scenario task.yaml"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output combined task.yaml",
    )
    parser.add_argument(
        "--summary",
        default="DISA STIG chain scenario",
        help="Summary value for the combined task",
    )
    parser.add_argument(
        "--kill-timeout",
        default="30m",
        help="kill-timeout value for the combined task",
    )
    parser.add_argument(
        "task_files",
        nargs="+",
        help="Ordered list of generated task.yaml files to combine",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    ordered_files = [Path(p) for p in args.task_files]
    sections: list[tuple[str, list[str]]] = []

    for task_file in ordered_files:
        if not task_file.is_file():
            raise FileNotFoundError(f"Task file not found: {task_file}")
        title = task_file.stem
        commands = extract_execute_block(task_file)
        sections.append((title, commands))

    write_combined_task(
        output_file=Path(args.output),
        summary=args.summary,
        kill_timeout=args.kill_timeout,
        sections=sections,
    )


if __name__ == "__main__":
    main()
