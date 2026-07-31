#!/usr/bin/env python3
"""Run a locked, headless Codex audit of all data.mn datasets."""

from __future__ import annotations

import argparse
import fcntl
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE_ROOT = Path.home() / ".local" / "state" / "data.mn" / "dataset-audits"
DEFAULT_CODEX = Path("/usr/local/bin/codex")
DEFAULT_MODEL = "gpt-5.6-terra"
PROMPT_PATH = PROJECT_ROOT / "tools" / "automation" / "biweekly-dataset-audit.prompt.md"
TIMEOUT_SECONDS = 4 * 60 * 60


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--state-root", type=Path, default=DEFAULT_STATE_ROOT)
    parser.add_argument("--codex", type=Path, default=DEFAULT_CODEX)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate prerequisites and print the command without running Codex.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = args.project_root.expanduser().resolve()
    state_root = args.state_root.expanduser().resolve()
    codex = args.codex.expanduser().resolve()
    prompt_path = project_root / PROMPT_PATH.relative_to(PROJECT_ROOT)

    missing = [
        str(path)
        for path in (project_root / ".git", prompt_path, codex)
        if not path.exists()
    ]
    if missing:
        raise RuntimeError(f"Missing scheduled-audit prerequisites: {missing}")

    state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(state_root, 0o700)
    lock_path = state_root / "audit.lock"

    with lock_path.open("w", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("A dataset audit is already running; exiting.", file=sys.stderr)
            return 75

        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = state_root / run_id
        report_path = run_dir / "report.md"
        events_path = run_dir / "events.jsonl"
        run_dir.mkdir(mode=0o700)

        command = [
            str(codex),
            "exec",
            "--ephemeral",
            "--sandbox",
            "read-only",
            "--model",
            args.model,
            "-c",
            'model_reasoning_effort="medium"',
            "--cd",
            str(project_root),
            "--json",
            "--output-last-message",
            str(report_path),
            "-",
        ]
        if args.dry_run:
            print(" ".join(command))
            run_dir.rmdir()
            return 0

        prompt = prompt_path.read_text(encoding="utf-8")
        with events_path.open("w", encoding="utf-8") as events:
            completed = subprocess.run(
                command,
                input=prompt,
                text=True,
                stdout=events,
                stderr=subprocess.STDOUT,
                timeout=TIMEOUT_SECONDS,
                check=False,
                env={
                    **os.environ,
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
            )
        os.chmod(events_path, 0o600)
        if report_path.exists():
            os.chmod(report_path, 0o600)
        if completed.returncode != 0:
            raise RuntimeError(
                f"Codex dataset audit failed with exit {completed.returncode}; "
                f"events={events_path}"
            )

        latest_path = state_root / "latest-report.md"
        latest_path.unlink(missing_ok=True)
        latest_path.symlink_to(report_path.relative_to(state_root))
        print(f"Dataset audit completed: {report_path}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
