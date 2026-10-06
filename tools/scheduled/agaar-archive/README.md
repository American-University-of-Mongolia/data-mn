# agaar archive job

Monthly run of `fetch_data.py --update` for agaar.gov.mn (see
`.claude/skills/datamn-source-agaar/SKILL.md` for why the archive must be
refreshed). Claude Code runs it headless so that anything unusual is written up
for a human instead of decided by a script.

| File | Purpose |
|------|---------|
| `prompt.md` | Instructions for the headless run (read from `origin/main` at run time) |
| `run.sh` | Creates a throwaway worktree, runs `claude -p`, cleans up |
| `datamn-agaar-archive.{service,timer}` | systemd user units: 2nd of each month, 10:00 |

Each run opens a PR "agaar archive run YYYY-MM-DD" with a before/after table and
a **Decisions needed** section, or a GitHub issue if archived values would be
lost. It never merges or deploys. Review and merge the PR as usual.

## Install (ritz server)

```bash
claude setup-token   # then: echo "CLAUDE_CODE_OAUTH_TOKEN=..." > ~/.config/datamn/claude.env; chmod 600 it
systemctl --user link ~/projects/data/tools/scheduled/agaar-archive/datamn-agaar-archive.{service,timer}
systemctl --user enable --now datamn-agaar-archive.timer
loginctl enable-linger "$USER"   # run without an active login
```

Run once now: `systemctl --user start datamn-agaar-archive.service`.
Logs: `~/.local/state/datamn/agaar-archive-YYYY-MM-DD.log`.
