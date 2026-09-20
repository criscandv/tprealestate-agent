#!/usr/bin/env bash
# UserPromptSubmit hook: routes /opsx:archive to the spec-archive-agent subagent.
# Lives outside openspec's generated files, so `openspec update` cannot overwrite it.

prompt="$(python3 -c 'import json, sys; print(json.load(sys.stdin).get("prompt", ""))' 2>/dev/null)"

case "$prompt" in
  /opsx:archive*)
    cat <<'EOF'
Project rule for /opsx:archive: do NOT run the archive steps yourself. Launch the `spec-archive-agent` subagent (Agent tool, subagent_type "spec-archive-agent"; it runs on Sonnet) from the repository root, passing the change name given after /opsx:archive (or the one inferred from the conversation) and any decision the user has already stated (proceed_with_incomplete_artifacts: yes|no, proceed_with_incomplete_tasks: yes|no, sync: now|skip|cancel, store: <id>). Wait for it synchronously. If it returns an "Archive paused — decision needed" report, ask the user with AskUserQuestion using the options it lists and launch it again with the answer. Relay its final report to the user unchanged.
EOF
    ;;
esac

exit 0
