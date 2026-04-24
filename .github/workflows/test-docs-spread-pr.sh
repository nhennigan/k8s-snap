#!/bin/bash

set -euo pipefail

# Use a local env file when running outside GitHub Actions.
: "${GITHUB_ENV:=/tmp/docs-spread.github.env}"
: > "$GITHUB_ENV"

rm -rf tests/spread-generated
mkdir -p tests/spread-generated
# Create all suite directories so spread doesn't fail reading spread.yaml
mkdir -p tests/spread-generated/{snap_clean,snap_bootstrapped,charm_clean,charm_bootstrapped}

BASE_SHA=$(git merge-base origin/main HEAD) && HEAD_SHA=$(git rev-parse HEAD)

mapfile -t changed_files < <(
  git diff --name-only "${BASE_SHA}" "${HEAD_SHA}" \
  | grep -E '^docs/canonicalk8s/(snap|charm)/(tutorial|howto)/.*\.(md|markdown)$' \
  || true
  )

if [[ ${#changed_files[@]} -eq 0 ]]; then
  echo "No docs files needing spread tests changed in this PR."
  echo "NO_SUITES=true" >> "$GITHUB_ENV"
  exit 0
fi

declare -A suites_seen=()
generated_any=false

for file in "${changed_files[@]}"; do

  # If there is no suite marker, skip the file. This allows us to have docs files that don't trigger spread tests.
  marker_suite="$(grep -Eo 'SPREAD SUITE:\s*[a-z_]+' "$file" | head -n1 | sed -E 's/.*:\s*//' || true)"
  if [[ -z "$marker_suite" ]]; then
    echo "Skipping $file (no SPREAD SUITE marker)"
    continue
  fi

  # Validate the suite value is one of the expected ones to catch typos early
  # This validation will be moved to the create_spread_task_file.py script in the future
  suite="$marker_suite"
  case "$suite" in
    snap_clean|snap_bootstrapped|charm_clean|charm_bootstrapped) ;;
    *)
      echo "Unsupported SPREAD SUITE marker '$suite' in $file"
      exit 1
      ;;
  esac

  rel="${file#docs/canonicalk8s/}"
  rel="${rel%.*}"
  # Flatten: use sanitized path with slashes replaced to avoid intermediate dirs
  task_name=$(echo "$rel" | sed 's|/|-|g')
  out_dir="tests/spread-generated/${suite}/${task_name}"
  mkdir -p "$out_dir"

  # Generate the spread task file for this docs file
  python3 docs/tools/create_spread_task_file.py \
    "$file" \
    "$out_dir/task.yaml"
  suites_seen["$suite"]=1
  generated_any=true
done

if [[ "$generated_any" != true ]]; then
  echo "No docs files with SPREAD SUITE markers changed in this PR."
  echo "NO_SUITES=true" >> "$GITHUB_ENV"
  exit 0
fi

printf "%s\n" "${!suites_seen[@]}" | sort > /tmp/spread_suites.txt

{
  echo "SPREAD_SUITES<<EOF"
  cat /tmp/spread_suites.txt
  echo "EOF"
} >> "$GITHUB_ENV"

# Also export locally so we can run the spread suites step in this script.
SPREAD_SUITES="$(cat /tmp/spread_suites.txt)"

# while IFS= read -r suite; do
#   [[ -z "$suite" ]] && continue
#   echo "Running docs suite: $suite"
#   ~/Documents/k8s/spread/cmd/spread/main -vv "multipass:ubuntu-24.04-64:tests/spread-generated/${suite}/"
# done <<< "$SPREAD_SUITES"

