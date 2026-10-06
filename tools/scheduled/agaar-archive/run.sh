#!/usr/bin/env bash
# Monthly agaar.gov.mn archive run (data.mn). Runs Claude Code headless in a
# throwaway worktree of origin/main; the result is a PR (or an issue) to review.
# Installed as a systemd user timer on the ritz server; see README.md.
set -euo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
STAMP=$(date +%Y-%m-%d)
BRANCH="agaar-archive-$STAMP"
WT="$HOME/.cache/datamn/agaar-archive-$STAMP"
LOG="$HOME/.local/state/datamn/agaar-archive-$STAMP.log"
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
# Long-lived token from `claude setup-token`: CLAUDE_CODE_OAUTH_TOKEN=...
[ -f "$HOME/.config/datamn/claude.env" ] && set -a && . "$HOME/.config/datamn/claude.env" && set +a

mkdir -p "$(dirname "$LOG")" "$(dirname "$WT")"
exec >>"$LOG" 2>&1
echo "== $(date -Is) start"
git -C "$REPO" fetch -q origin main
rm -rf "$WT"; git -C "$REPO" worktree prune
git -C "$REPO" worktree add -q -B "$BRANCH" "$WT" origin/main
cd "$WT"
status=0
# The prompt comes from origin/main, so edits to it take effect once merged.
claude -p "$(cat tools/scheduled/agaar-archive/prompt.md)" \
  --permission-mode acceptEdits \
  --allowedTools "Bash Read Edit Write Glob Grep" \
  --output-format text || status=$?
echo "== $(date -Is) claude exit $status"
cd "$REPO"
git worktree remove --force "$WT" || true
exit $status
