#!/usr/bin/env python3
"""Run the shared Parliament attendance collector from the Codex skill."""

from pathlib import Path
import runpy


REPOSITORY = Path(__file__).resolve().parents[4]
COLLECTOR = (
    REPOSITORY
    / ".claude"
    / "skills"
    / "datamn-source-parliament"
    / "fetch_data.py"
)

if not COLLECTOR.exists():
    raise SystemExit(f"Shared Parliament collector not found: {COLLECTOR}")

runpy.run_path(str(COLLECTOR), run_name="__main__")
