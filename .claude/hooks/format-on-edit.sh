#!/usr/bin/env bash
# PostToolUse hook for Claude Code.
# Formats the file just edited/written using ruff. Single-package project: everything
# under app/ and tests/ is Python.
# Reads JSON payload from stdin and extracts tool_input.file_path.
# Always exits 0 — formatting failures must not block tool execution.

set +e

payload="$(cat)"
file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // empty' 2>/dev/null)"

if [ -z "$file" ] || [ ! -f "$file" ]; then
  exit 0
fi

project_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"

case "$file" in
  "$project_dir"/*.py)
    (cd "$project_dir" && uv run ruff check --fix --quiet "$file" >/dev/null 2>&1)
    (cd "$project_dir" && uv run ruff format --quiet "$file" >/dev/null 2>&1)
    ;;
esac

exit 0
