#!/usr/bin/env bash
# PostToolUse hook: after a human-readable document (.md/.html/.pptx) is written,
# advise the main loop to run the korean-reviewer agent on it. Advisory only —
# never blocks. When several docs are produced, each Write fires this hook, so
# the advice tells the main loop it may review them in parallel.
set -euo pipefail

# Degrade silently (allow the action) if jq isn't installed — never fail the hook.
command -v jq >/dev/null 2>&1 || exit 0

# Read the hook payload from stdin.
payload="$(cat)"

# Extract the written file path. Write/Edit/MultiEdit all expose file_path on
# tool_input; fall back to a top-level path key just in case. jq stays silent on
# missing keys, so non-file tools yield an empty string.
file_path="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty')"

# Nothing actionable without a path.
[ -n "$file_path" ] || exit 0

# Only act on human-readable document extensions (case-insensitive).
ext="${file_path##*.}"
ext="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"
case "$ext" in
  md|markdown|html|htm|pptx) ;;
  *) exit 0 ;;
esac

# Skip plugin/agent/internal files — we only want reader-facing docs, not the
# plugin's own .md scaffolding or anything under a dotfile dir.
case "$file_path" in
  */.claude/*|*/.claude-plugin/*|*/agents/*|*/skills/*|*/node_modules/*) exit 0 ;;
esac

base="$(basename "$file_path")"

# Emit a non-blocking advisory. additionalContext is surfaced to the main loop;
# we explicitly authorize parallel dispatch when multiple docs were just written.
cat <<JSON
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "A Korean document '$base' ($file_path) was just written. Invoke the korean-reviewer agent (Agent tool, subagent_type: \"korean-reviewer\") to proofread and fix unnatural Korean in this file. If several such documents were written this turn, dispatch one korean-reviewer call per file concurrently (in parallel) in a single message. Skip if the document is in English or the user does not want proofreading."
  }
}
JSON

exit 0
