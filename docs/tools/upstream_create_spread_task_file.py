# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

#!/usr/bin/env python3
"""
Extract commands from Markdown and reStructuredText files.

This script reads a Markdown or reStructuredText file and extracts all commands from code blocks.

For Markdown:
- Code blocks are defined by triple backticks (```).
- Blocks starting with {note} or {tip} are excluded.
- "SPREAD" HTML comment blocks are included.
- "SPREAD SKIP" markers in HTML comment blocks mark ranges to exclude.
- "SPREAD SUITE" markers in HTML comments route output to suite-specific directories when provided.

For reStructuredText:
- Code blocks are defined by .. code-block:: directive.
- SPREAD comment blocks (.. SPREAD\n...\n.. SPREAD END) are included.
- SPREAD SKIP markers (.. SPREAD SKIP\n...\n.. SPREAD SKIP END) mark ranges to exclude.
- SPREAD SUITE markers (.. SPREAD SUITE: suite_name) route output to suite-specific directories when provided.

All command blocks (both code blocks and SPREAD blocks) within SPREAD SKIP ranges are excluded
from the output.
"""

import sys
import re
import argparse
import logging
from pathlib import Path


def validate_paired_markers(content, start_pattern, end_pattern, marker_name, flags=0):
    """
    Validate that markers are properly paired and ordered using a stack-based approach.

    Args:
        content: Content to validate
        start_pattern: Regex pattern for start marker
        end_pattern: Regex pattern for end marker
        marker_name: Name of marker for error messages
        flags: Optional regex flags (e.g., re.MULTILINE)

    Returns:
        List of tuples (start_pos, end_pos) for valid marker pairs

    Raises:
        ValueError: If markers are not properly paired or ordered
    """
    starts = [(m.start(), "start") for m in re.finditer(start_pattern, content, flags)]
    ends = [(m.start(), "end") for m in re.finditer(end_pattern, content, flags)]

    # Merge and sort by position
    all_markers = sorted(starts + ends, key=lambda x: x[0])

    # Use stack to validate pairing
    stack = []
    pairs = []

    for pos, marker_type in all_markers:
        if marker_type == "start":
            stack.append(pos)
        else:  # marker_type == 'end'
            if not stack:
                raise ValueError(
                    f"Found closing {marker_name} marker without corresponding opening marker at position {pos}"
                )
            start_pos = stack.pop()
            pairs.append((start_pos, pos))

    if stack:
        raise ValueError(f"Unclosed {marker_name} marker found at position {stack[0]}")

    return pairs


def extract_markdown_spread_comments(content):
    """
    Extract all SPREAD comment blocks from markdown content.

    Args:
        content: Markdown content as string

    Returns:
        List of tuples (position, command_string) for SPREAD blocks

    Raises:
        ValueError: If a SPREAD comment block is not properly closed
    """
    spread_blocks = []
    # Pattern that matches <!-- SPREAD but not <!-- SPREAD SKIP
    pattern = r"<!-- SPREAD(?! SKIP)\s*\n(.*?)-->"

    # Find all <!-- SPREAD (not SPREAD SKIP) and verify each has a closing -->
    spread_starts = [
        m.start() for m in re.finditer(r"<!-- SPREAD(?! SKIP)\s*", content)
    ]
    for start_pos in spread_starts:
        # Look for --> after this position
        remaining_content = content[start_pos:]
        if "-->" not in remaining_content:
            raise ValueError(
                f"Unclosed SPREAD comment block found at position {start_pos}"
            )
        # Check if --> appears before the next <!-- SPREAD (if any)
        next_spread = remaining_content.find("<!-- SPREAD", 1)
        closing_pos = remaining_content.find("-->")
        if next_spread != -1 and closing_pos > next_spread:
            raise ValueError(
                f"Unclosed SPREAD comment block found at position {start_pos}"
            )

    for match in re.finditer(pattern, content, re.DOTALL):
        command_content = match.group(1).strip()
        if command_content:
            spread_blocks.append((match.start(), command_content))

    return spread_blocks


def extract_markdown_spread_skip_comments(content):
    """
    Extract all SPREAD SKIP comment blocks from markdown content.

    Args:
        content: Markdown content as string

    Returns:
        List of tuples (start_pos, end_pos) for SPREAD SKIP exclusion ranges

    Raises:
        ValueError: If a SPREAD SKIP comment block is not properly closed
    """
    # Validate pairing using stack-based validation
    start_pattern = r"<!-- SPREAD SKIP -->"
    end_pattern = r"<!-- SPREAD SKIP END -->"
    pairs = validate_paired_markers(content, start_pattern, end_pattern, "SPREAD SKIP")

    # Convert pairs to ranges (end position should include the end marker)
    spread_skip_ranges = []
    for start_pos, end_pos in pairs:
        # end_pos is the start of the end marker, so we add its length
        end_marker_match = re.search(end_pattern, content[end_pos:])
        if end_marker_match:
            full_end_pos = end_pos + end_marker_match.end()
            spread_skip_ranges.append((start_pos, full_end_pos))

    return spread_skip_ranges


def extract_rst_spread_comments(content):
    """
    Extract all SPREAD comment blocks from reStructuredText content.

    Args:
        content: reStructuredText content as string

    Returns:
        List of tuples (position, command_string) for SPREAD blocks

    Raises:
        ValueError: If a SPREAD block is not properly closed
    """
    # Validate pairing using stack-based validation
    start_pattern = r"^\.\. SPREAD\s*$"
    end_pattern = r"^\.\. SPREAD END\s*$"
    validate_paired_markers(content, start_pattern, end_pattern, "SPREAD", re.MULTILINE)

    spread_blocks = []

    # Pattern to match .. SPREAD\n content \n.. SPREAD END
    pattern = r"^\.\. SPREAD\s*\n(.*?)^\.\. SPREAD END\s*$"

    # Extract content from SPREAD blocks
    for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
        raw_content = match.group(1)
        match_start = match.start()

        # Split into lines and strip .. prefix from each line
        lines = raw_content.split("\n")
        stripped_lines = []
        for line in lines:
            # Strip leading .. and optional space
            if line.startswith(".. "):
                stripped_lines.append(line[3:])
            elif line.startswith(".."):
                stripped_lines.append(line[2:])
            else:
                stripped_lines.append(line)

        # Dedent the content (remove common leading whitespace)
        non_empty_lines = [line for line in stripped_lines if line.strip()]

        if not non_empty_lines:
            continue

        # Find minimum indentation
        min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)

        # Remove the common indentation
        dedented_lines = []
        for line in stripped_lines:
            if line.strip():  # Non-empty line
                dedented_lines.append(line[min_indent:])
            else:  # Empty line
                dedented_lines.append("")

        command_content = "\n".join(dedented_lines).strip()

        if command_content:
            spread_blocks.append((match_start, command_content))

    return spread_blocks


def extract_rst_spread_skip_comments(content):
    """
    Extract all SPREAD SKIP comment blocks from reStructuredText content.

    Args:
        content: reStructuredText content as string

    Returns:
        List of tuples (start_pos, end_pos) for SPREAD SKIP exclusion ranges

    Raises:
        ValueError: If a SPREAD SKIP block is not properly closed
    """
    # Validate pairing using stack-based validation
    start_pattern = r"^\.\. SPREAD SKIP\s*$"
    end_pattern = r"^\.\. SPREAD SKIP END\s*$"
    validate_paired_markers(
        content, start_pattern, end_pattern, "SPREAD SKIP", re.MULTILINE
    )

    spread_skip_ranges = []

    # Pattern to match .. SPREAD SKIP\n content \n.. SPREAD SKIP END
    pattern = r"^\.\. SPREAD SKIP\s*\n(.*?)^\.\. SPREAD SKIP END\s*$"

    # Extract ranges from SPREAD SKIP blocks
    for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
        start_pos = match.start()
        end_pos = match.end()
        spread_skip_ranges.append((start_pos, end_pos))

    return spread_skip_ranges

def extract_markdown_spread_suite(content):
    """
    Extract SPREAD SUITE marker values from markdown content.

    Args:
        content: Markdown content as string

    Returns:
        List of suite marker values found in markdown markers
    """
    markdown_pattern = r'<!--\s*SPREAD SUITE:\s*([a-z_]+)\s*-->'
    return [m.group(1).strip() for m in re.finditer(markdown_pattern, content)]


def extract_rst_spread_suite(content):
    """
    Extract SPREAD SUITE marker values from reStructuredText content.

    Args:
        content: reStructuredText content as string

    Returns:
        List of suite marker values found in RST markers
    """
    rst_pattern = r'^\.\.\s*SPREAD SUITE:\s*([a-z_]+)\s*$'
    return [m.group(1).strip() for m in re.finditer(rst_pattern, content, re.MULTILINE)]

def get_allowed_spread_suites(spread_config_path="spread.yaml"):
    """
    Load allowed suite markers from spread.yaml.

    Args:
        spread_config_path: Path to spread.yaml

    Returns:
        List of allowed suite names

    Raises:
        FileNotFoundError: If spread.yaml is missing
        ValueError: If no suites are defined in spread.yaml
    """
    config_file = Path(spread_config_path)
    if not config_file.is_file():
        raise FileNotFoundError(
            f"Required spread config file not found: {config_file}. "
            "Run this script from the repository root or provide spread.yaml there."
        )

    content = config_file.read_text(encoding='utf-8')
    lines = content.splitlines()

    suites_indent = None
    in_suites = False
    detected = set()

    for raw_line in lines:
        if not raw_line.strip() or raw_line.lstrip().startswith('#'):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(' '))
        stripped = raw_line.strip()

        if not in_suites:
            if stripped == 'suites:':
                in_suites = True
                suites_indent = indent
            continue

        if indent <= suites_indent:
            break

        if indent != suites_indent + 2 or not stripped.endswith(':'):
            continue

        suite_key = stripped[:-1].strip().strip('"\'')
        suite_key = suite_key.rstrip('/')
        if not suite_key:
            continue

        suite_name = Path(suite_key).name or suite_key
        detected.add(suite_name)

    suites = sorted(detected)
    if not suites:
        raise ValueError(f"No suites found in spread config: {config_file}")

    return suites


def extract_commands_from_rst(file_path):
    """
    Extract all commands from code blocks and SPREAD comments in a reStructuredText file.

    Args:
        file_path: Path to the reStructuredText file

    Returns:
        List of command strings found in code blocks and SPREAD comments, in document order
    """
    content = Path(file_path).read_text(encoding='utf-8')

    # Extract SPREAD comment blocks
    spread_blocks = extract_rst_spread_comments(content)

    # Extract SPREAD SKIP ranges
    spread_skip_ranges = extract_rst_spread_skip_comments(content)

    # Find all code blocks in RST:
    # - Match a ".. code-block::" directive line (with any trailing options),
    # - Allow a single optional blank line immediately after the directive,
    # - Then capture (in group 1) all subsequent indented content lines as the code block body.
    pattern = r"^\.\. code-block::[^\n]*\n(?:\n)?((?:[ \t]+.+(?:\n|$))+)"
    matches = re.finditer(pattern, content, re.MULTILINE)

    code_blocks = []
    for match in matches:
        indented_content = match.group(1)
        match_start = match.start()
        match_end = match.end()

        # Skip blocks that are within excluded ranges
        is_excluded = any(
            start <= match_start < end for start, end in spread_skip_ranges
        )
        if is_excluded:
            continue

        # Dedent the content (remove common leading whitespace)
        lines = indented_content.split("\n")
        # Filter out empty lines for indentation calculation
        non_empty_lines = [line for line in lines if line.strip()]

        if not non_empty_lines:
            continue

        # Find minimum indentation
        min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)

        # Remove the common indentation
        dedented_lines = []
        for line in lines:
            if line.strip():  # Non-empty line
                dedented_lines.append(line[min_indent:])
            else:  # Empty line
                dedented_lines.append("")

        code_content = "\n".join(dedented_lines).strip()

        if code_content:
            code_blocks.append((match_start, code_content))

    # Filter SPREAD blocks to exclude those within SPREAD SKIP ranges
    filtered_spread_blocks = []
    for pos, content in spread_blocks:
        is_excluded = any(start <= pos < end for start, end in spread_skip_ranges)
        if not is_excluded:
            filtered_spread_blocks.append((pos, content))

    # Combine code blocks and filtered SPREAD blocks, then sort by position
    all_blocks = code_blocks + filtered_spread_blocks
    all_blocks.sort(key=lambda x: x[0])

    # Extract just the command content, maintaining order
    commands = [content for position, content in all_blocks]

    return commands


def extract_commands_from_markdown(file_path):
    """
    Extract all commands from code blocks and SPREAD comments in a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        List of command strings found in code blocks and SPREAD comments, in document order
    """
    content = Path(file_path).read_text(encoding="utf-8")

    # Extract SPREAD comment blocks
    spread_blocks = extract_markdown_spread_comments(content)

    # Extract SPREAD SKIP ranges
    spread_skip_ranges = extract_markdown_spread_skip_comments(content)

    # First, find all blocks with 4+ backticks to identify excluded regions
    excluded_ranges = []
    pattern_4plus = r"````+[^\n]*\n(.*?)````+"
    for match in re.finditer(pattern_4plus, content, re.DOTALL):
        excluded_ranges.append((match.start(), match.end()))

    # Add SPREAD SKIP ranges to excluded ranges
    excluded_ranges.extend(spread_skip_ranges)

    # Find all code blocks: exactly 3 backticks (not more), optional language, content, then exactly 3 backticks
    # Use negative lookbehind and lookahead to ensure exactly 3 backticks
    pattern = r"(?<!`)```(?!`)([^\n]*)\n(.*?)(?<!`)```(?!`)"
    matches = re.finditer(pattern, content, re.DOTALL)

    code_blocks = []
    for match in matches:
        lang_identifier = match.group(1)
        code_content = match.group(2)
        match_start = match.start()
        match_end = match.end()

        # Skip blocks that start with { (like {note}, {tip}, or {terminal})
        if lang_identifier.strip().startswith("{"):
            continue

        # Skip blocks that are nested within 4+ backtick blocks or in excluded sections
        is_nested = any(
            start <= match_start < match_end <= end for start, end in excluded_ranges
        )
        if is_nested:
            continue

        # Add non-empty code content with its position
        if code_content.strip():
            code_blocks.append((match_start, code_content.strip()))

    # Filter SPREAD blocks to exclude those within SPREAD SKIP ranges
    filtered_spread_blocks = []
    for pos, content in spread_blocks:
        is_excluded = any(start <= pos < end for start, end in spread_skip_ranges)
        if not is_excluded:
            filtered_spread_blocks.append((pos, content))

    # Combine code blocks and filtered SPREAD blocks, then sort by position
    all_blocks = code_blocks + filtered_spread_blocks
    all_blocks.sort(key=lambda x: x[0])

    # Extract just the command content, maintaining order
    commands = [content for position, content in all_blocks]

    return commands


def write_task_yaml(commands, output_path="task.yaml"):
    """
    Write extracted commands to a task.yaml file.

    Args:
        commands: List of command strings to write
        output_path: Path to the output YAML file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        # Write the header
        f.write("summary: Tutorial test\n")
        f.write("\n")
        f.write("kill-timeout: 30m\n")
        f.write("\n")
        f.write("execute: |\n")

        # Write each command with 2-space indentation
        for command in commands:
            # Split multi-line commands and indent each line
            for line in command.split("\n"):
                f.write(f"  {line}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Extract commands from markdown and reStructuredText files and generate task.yaml for Spread tests.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s docs/tutorial.md
  %(prog)s docs/tutorial.rst
  %(prog)s docs/tutorial.md tests/spread/tutorial/task.yaml
  %(prog)s docs/tutorial.rst tests/spread/tutorial/
  %(prog)s docs/tutorial.md tests/spread-generated/
  %(prog)s docs/tutorial.rst tests/spread-generated/

Behavior:
  - Automatically detects SPREAD SUITE markers in input files
  - If marker present: outputs to <output>/<suite>/task.yaml
  - If no marker: outputs to <output>/task.yaml (or <output> if directory)
    - Always reads spread.yaml and validates marker values against allowed suites
    - In directory output mode, creates all configured suite directories

Special Markers:
  SPREAD blocks (always included):
    Markdown: <!-- SPREAD
              command content
              -->
    RST:      .. SPREAD
              .. command content
              .. SPREAD END
  
  SPREAD SKIP markers (exclude all commands in range):
    Markdown: <!-- SPREAD SKIP -->
              Content to skip (code blocks and SPREAD blocks)
              <!-- SPREAD SKIP END -->
    RST:      .. SPREAD SKIP
              .. Content to skip
              .. SPREAD SKIP END

  SPREAD SUITE marker (optional routing target):
    Markdown: <!-- SPREAD SUITE: snap_clean -->
    RST:      .. SPREAD SUITE: snap_clean
        """
    )

    parser.add_argument(
        "markdown_file",
        help="Path to the markdown or reStructuredText file to extract commands from",
    )

    parser.add_argument(
        "output_path",
        nargs="?",
        default="task.yaml",
        help="Path to the output YAML file or directory (default: task.yaml)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output (DEBUG level)",
    )

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress all output except errors"
    )

    args = parser.parse_args()

    # Configure logging
    log_level = (
        logging.WARNING
        if args.quiet
        else (logging.DEBUG if args.verbose else logging.INFO)
    )
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    file_path = Path(args.markdown_file)
    output_path = Path(args.output_path)

    try:
        # Detect file type once and dispatch to format-specific extractors.
        file_ext = file_path.suffix.lower()
        content = file_path.read_text(encoding='utf-8')

        if file_ext in ['.rst', '.rest']:
            commands = extract_commands_from_rst(file_path)
            suite_matches = extract_rst_spread_suite(content)
        elif file_ext in ['.md', '.markdown']:
            commands = extract_commands_from_markdown(file_path)
            suite_matches = extract_markdown_spread_suite(content)
        else:
            raise ValueError(
                f"Unsupported file type '{file_ext}'. Supported types: .md, .markdown, .rst, .rest"
            )

        logging.info(f"Found {len(commands)} command block(s) in {file_path}")

        for i, command in enumerate(commands, 1):
            logging.debug(f"Command block {i}: {command}")

        # Resolve SPREAD SUITE marker value (if present)
        if not suite_matches:
            marker_suite = None
        else:
            unique_matches = list(dict.fromkeys(suite_matches))
            if len(unique_matches) > 1:
                raise ValueError(
                    f"File '{file_path}' contains multiple different SPREAD SUITE markers: {', '.join(unique_matches)}"
                )
            marker_suite = unique_matches[0]

        # Always read spread.yaml for suite validation and suite directory creation.
        allowed_suites = get_allowed_spread_suites("spread.yaml")

        # Pre-create all suite directories so spread can list suites even if
        # no tasks have been generated for some of them yet.
        # Check for directory-mode output: already a dir, trailing slash, or no file extension.
        is_dir_output = output_path.is_dir() or str(output_path).endswith('/') or not output_path.suffix
        if is_dir_output:
            output_path.mkdir(parents=True, exist_ok=True)
            for suite in allowed_suites:
                (output_path / suite).mkdir(parents=True, exist_ok=True)
                logging.debug(f"Ensured suite directory exists: {output_path / suite}")

        # Determine output file path
        output_file = None
        if marker_suite:
            if marker_suite not in allowed_suites:
                raise ValueError(
                    f"Unsupported SPREAD SUITE marker '{marker_suite}' in {file_path}. "
                    f"Allowed values: {', '.join(allowed_suites)}"
                )

            # Route output under suite directory
            task_stem = file_path.stem
            output_file = output_path / marker_suite / task_stem / "task.yaml"
        else:
            # No marker: use standard output path
            if output_path.is_dir() or str(output_path).endswith('/'):
                output_file = output_path / "task.yaml"
            else:
                output_file = output_path

        # Write commands to task.yaml
        write_task_yaml(commands, output_file)
        logging.info(f"Commands written to {output_file}")

    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()