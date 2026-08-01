#!/usr/bin/env python3
"""Run a transactional headless Codex update of all data.mn datasets."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE_ROOT = Path.home() / ".local" / "state" / "data.mn" / "dataset-audits"
DEFAULT_CODEX = Path("/usr/local/bin/codex")
DEFAULT_MODEL = "gpt-5.6-terra"
PROMPT_RELATIVE_PATH = Path("tools/automation/biweekly-dataset-audit.prompt.md")
TIMEOUT_SECONDS = 8 * 60 * 60


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--state-root", type=Path, default=DEFAULT_STATE_ROOT)
    parser.add_argument("--codex", type=Path, default=DEFAULT_CODEX)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate prerequisites and print the release stages without running them.",
    )
    return parser.parse_args()


def run(command: list[str], *, cwd: Path, **kwargs: object) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, text=True, check=True, **kwargs)


def git(project_root: Path, *args: str, capture: bool = False) -> str:
    completed = run(
        ["git", *args], cwd=project_root, capture_output=capture,
    )
    return completed.stdout.strip() if capture else ""


def verify_release(worktree: Path, python: Path) -> None:
    changed = set(git(worktree, "status", "--porcelain", capture=True).splitlines())
    protected = (
        "AGENTS.md", "CLAUDE.md", ".github/", "config/deploy", "data.mn/config/deploy",
        "systemd/", "tools/automation/", "tools/scripts/run_scheduled_dataset_audit.py",
    )
    changed_paths = [line[3:] for line in changed if len(line) > 3]
    forbidden = [path for path in changed_paths if path.startswith(protected)]
    if forbidden:
        raise RuntimeError(f"Scheduled update touched protected paths: {forbidden}")

    checks = [
        (["git", "diff", "--check"], worktree),
        ([str(python), "tools/scripts/validate_mdx_datafiles.py"], worktree),
        ([str(python), "../tools/scripts/validate_vega.py", "--all"], worktree / "data.mn"),
        ([str(python), "-c", (
            "import sqlite3; c=sqlite3.connect('tools/registry/data.db'); "
            "v=c.execute('PRAGMA foreign_key_check').fetchall(); "
            "assert not v, v"
        )], worktree),
        (["npm", "ci", "--no-audit", "--no-fund"], worktree / "data.mn"),
        (["npm", "run", "categories"], worktree / "data.mn"),
        (["npm", "exec", "--", "astro", "check"], worktree / "data.mn"),
        (["npm", "exec", "--", "astro", "build"], worktree / "data.mn"),
    ]
    environment = {
        **os.environ,
        "HOME": str(worktree / ".automation-home"),
        "XDG_CACHE_HOME": str(worktree / ".automation-cache"),
        "npm_config_cache": str(worktree / ".npm-cache"),
    }
    for command, cwd in checks:
        run(command, cwd=cwd, env=environment)


def deploy(project_root: Path) -> None:
    deploy_root = project_root / "data.mn"
    source = (deploy_root / "config/deploy.yml").read_text(encoding="utf-8")
    local = source.replace("local: false", "local: true").replace(
        "  remote: ssh://ritz@ritz-cmd\n", ""
    )
    descriptor, name = tempfile.mkstemp(prefix="datamn-scheduled-", suffix=".yml")
    config = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(local)
        environment = {**os.environ, "LANG": "en_US.UTF-8", "LC_ALL": "en_US.UTF-8"}
        run(["kamal", "deploy", "-c", str(config)], cwd=deploy_root, env=environment)
    finally:
        config.unlink(missing_ok=True)


def write_result(path: Path, **values: object) -> None:
    path.write_text(json.dumps(values, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)


def main() -> int:
    args = parse_args()
    project_root = args.project_root.expanduser().resolve()
    state_root = args.state_root.expanduser().resolve()
    codex = args.codex.expanduser().resolve()
    prompt_path = project_root / PROMPT_RELATIVE_PATH
    validation_python = state_root / ".venv/bin/python"
    state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(state_root, 0o700)
    required = [project_root / ".git", prompt_path, codex, validation_python]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError(f"Missing scheduled-update prerequisites: {missing}")

    with (state_root / "audit.lock").open("w", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("A dataset update is already running; exiting.", file=sys.stderr)
            return 75

        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = state_root / run_id
        worktree = run_dir / "worktree"
        report_path = run_dir / "report.md"
        events_path = run_dir / "events.jsonl"
        result_path = run_dir / "result.json"
        run_dir.mkdir(mode=0o700)

        if args.dry_run:
            print("stages: preflight -> isolated Codex update -> validation -> commit -> "
                  "fast-forward main -> push -> Kamal deploy")
            run_dir.rmdir()
            return 0

        base = git(project_root, "rev-parse", "HEAD", capture=True)
        if git(project_root, "status", "--porcelain", capture=True):
            raise RuntimeError("Canonical checkout is not clean")
        git(project_root, "fetch", "origin", "main")
        if base != git(project_root, "rev-parse", "origin/main", capture=True):
            raise RuntimeError("Canonical main is not synchronized with origin/main")

        branch = f"automation/dataset-update-{run_id.lower()}"
        git(project_root, "worktree", "add", "-b", branch, str(worktree), base)
        released = False
        try:
            command = [
                str(codex), "exec", "--ephemeral", "--sandbox", "workspace-write",
                "--model", args.model, "-c", 'model_reasoning_effort="medium"',
                "--cd", str(worktree), "--json", "--output-last-message",
                str(report_path), "-",
            ]
            with events_path.open("w", encoding="utf-8") as events:
                completed = subprocess.run(
                    command,
                    cwd=worktree,
                    input=prompt_path.read_text(encoding="utf-8"),
                    text=True,
                    stdout=events,
                    stderr=subprocess.STDOUT,
                    timeout=TIMEOUT_SECONDS,
                    check=False,
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                )
            os.chmod(events_path, 0o600)
            if report_path.exists():
                os.chmod(report_path, 0o600)
            if completed.returncode != 0:
                raise RuntimeError(f"Codex update failed with exit {completed.returncode}")
            if git(worktree, "rev-parse", "HEAD", capture=True) != base:
                raise RuntimeError("Codex committed unexpectedly; refusing release")
            if not git(worktree, "status", "--porcelain", capture=True):
                write_result(result_path, status="current", base=base, report=str(report_path))
                return 0

            verify_release(worktree, validation_python)
            # Validation caches and build output are never release content.
            for generated in (".automation-home", ".automation-cache", ".npm-cache", "data.mn/dist"):
                shutil.rmtree(worktree / generated, ignore_errors=True)
            git(worktree, "add", "--all")
            git(worktree, "commit", "-m", f"Automated dataset refresh {run_id[:8]}")
            update_commit = git(worktree, "rev-parse", "HEAD", capture=True)

            if git(project_root, "rev-parse", "HEAD", capture=True) != base:
                raise RuntimeError("Main changed during validation; refusing release")
            if git(project_root, "status", "--porcelain", capture=True):
                raise RuntimeError("Canonical checkout changed during validation")
            git(project_root, "merge", "--ff-only", branch)
            git(project_root, "push", "origin", "main")
            deploy(project_root)
            released = True
            write_result(
                result_path,
                status="deployed",
                base=base,
                commit=update_commit,
                report=str(report_path),
            )
            return 0
        except Exception as error:
            write_result(
                result_path,
                status="failed",
                base=base,
                error_type=type(error).__name__,
                error=str(error),
                production_changed=released,
                worktree=str(worktree),
            )
            raise
        finally:
            latest = state_root / "latest-report.md"
            if report_path.exists():
                latest.unlink(missing_ok=True)
                latest.symlink_to(report_path.relative_to(state_root))
            if released or not worktree.exists() or not git(worktree, "status", "--porcelain", capture=True):
                git(project_root, "worktree", "remove", "--force", str(worktree))
                git(project_root, "branch", "-D", branch)


if __name__ == "__main__":
    raise SystemExit(main())
