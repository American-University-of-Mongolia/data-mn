#!/usr/bin/env python3
"""
Review a data.mn pull request and print a merge-ready report.

Validates only the datasets added/modified in the PR, plus global checks.
The PR is checked out into a temporary worktree, so the current working
tree is never touched.

Usage:
    # From anywhere; runs with the repo .venv python:
    .venv/bin/python tools/scripts/review_pr.py 132
    .venv/bin/python tools/scripts/review_pr.py 132 --fast   # skip slow steps
    .venv/bin/python tools/scripts/review_pr.py 132 --build  # include npm build
    .venv/bin/python tools/scripts/review_pr.py 132 --lint   # include npm check

Requires: gh CLI (authenticated), repo .venv with pytest/pandas/pyyaml.

Exit code 0 if all executed checks pass, 1 otherwise.
"""

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MDX_RE = re.compile(r"data\.mn/src/data/data/(?:en|mn)/(.+)\.mdx$")


@dataclass
class StepResult:
    name: str
    passed: bool | None  # None = skipped
    detail: str = ""


@dataclass
class Report:
    pr: int
    title: str = ""
    head_sha: str = ""
    datasets: list[str] = field(default_factory=list)
    steps: list[StepResult] = field(default_factory=list)
    db_diff: str = ""

    def add(self, name: str, passed: bool | None, detail: str = "") -> None:
        self.steps.append(StepResult(name, passed, detail))

    @property
    def failed(self) -> list[StepResult]:
        return [s for s in self.steps if s.passed is False]

    def print(self) -> None:
        width = 63
        print("+" + "=" * width + "+")
        print(f"| PR #{self.pr} VALIDATION REPORT".ljust(width + 1) + "|")
        if self.title:
            print(f"| {self.title[:width - 2]}".ljust(width + 1) + "|")
        print("+" + "=" * width + "+")
        if self.datasets:
            print(f"| DATASETS ({len(self.datasets)}):".ljust(width + 1) + "|")
            for ds in self.datasets:
                ds_steps = [s for s in self.steps
                            if s.name.startswith(f"{ds}:")]
                ok = all(s.passed for s in ds_steps)
                mark = "PASS" if ok else "FAIL"
                print(f"|   - {ds}: {mark}".ljust(width + 1) + "|")
        else:
            print("| DATASETS: none touched (code-only PR)".ljust(width + 1)
                  + "|")
        print("+" + "=" * width + "+")
        for step in self.steps:
            if step.passed is None:
                mark = "SKIP"
            elif step.passed:
                mark = "PASS"
            else:
                mark = "FAIL"
            print(f"| {mark:4} {step.name[:width - 7]}".ljust(width + 1)
                  + "|")
            if step.passed is False and step.detail:
                for line in step.detail.strip().splitlines()[:8]:
                    print(f"|        {line[:width - 9]}".ljust(width + 1)
                          + "|")
        print("+" + "=" * width + "+")
        verdict = "READY TO MERGE" if not self.failed else "NEEDS FIXES"
        print(f"| RESULT: {verdict}".ljust(width + 1) + "|")
        print("+" + "=" * width + "+")
        if self.db_diff:
            print("\n--- registry data.db diff (base -> PR) ---")
            print(self.db_diff)


def run(cmd: list[str], cwd: Path | None = None,
        timeout: int = 600) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def gh_api(*args: str) -> str:
    # {owner}/{repo} placeholders resolve from REPO_ROOT's git remote.
    code, out = run(["gh", "api", *args], cwd=REPO_ROOT)
    if code != 0:
        raise RuntimeError(f"gh api failed: {out}")
    return out


def pr_files(pr: int) -> list[dict]:
    return json.loads(gh_api(f"repos/{{owner}}/{{repo}}/pulls/{pr}/files",
                             "--paginate"))


def pr_head(pr: int) -> tuple[str, str, str]:
    info = json.loads(gh_api(f"repos/{{owner}}/{{repo}}/pulls/{pr}"))
    return info["head"]["sha"], info["title"], info["base"]["ref"]


def detect_datasets(files: list[dict]) -> list[str]:
    ids: list[str] = []
    for entry in files:
        match = MDX_RE.search(entry["filename"])
        if match and match.group(1) not in ids:
            ids.append(match.group(1))
    return ids


def tail(text: str, lines: int = 8) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])


def changed_dataset_ids(base_db: Path, head_db: Path) -> list[str]:
    """IDs whose row in the datasets table differs between two DB files."""
    changed: list[str] = []
    base = sqlite3.connect(base_db)
    head = sqlite3.connect(head_db)
    try:
        base_rows = {r[0]: r for r in
                     base.execute("SELECT * FROM datasets ORDER BY id")}
        head_rows = {r[0]: r for r in
                     head.execute("SELECT * FROM datasets ORDER BY id")}
        for dataset_id in sorted(set(base_rows) | set(head_rows)):
            if base_rows.get(dataset_id) != head_rows.get(dataset_id):
                changed.append(dataset_id)
    finally:
        base.close()
        head.close()
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a data.mn PR")
    parser.add_argument("pr", type=int, help="PR number")
    parser.add_argument("--fast", action="store_true",
                        help="Skip slow steps (vega --all, build, lint)")
    parser.add_argument("--build", action="store_true",
                        help="Include npm run build (slow)")
    parser.add_argument("--lint", action="store_true",
                        help="Include npm run check (slow)")
    args = parser.parse_args()

    report = Report(pr=args.pr)
    python = sys.executable
    scripts = REPO_ROOT / "tools" / "scripts"
    tests = REPO_ROOT / "tools" / "tests"

    try:
        head_sha, title, base_ref = pr_head(args.pr)
    except RuntimeError as exc:
        print(f"Cannot load PR #{args.pr}: {exc}")
        return 1
    report.title, report.head_sha = title, head_sha

    files = pr_files(args.pr)
    report.datasets = detect_datasets(files)
    touched = {entry["filename"] for entry in files}
    db_touched = "tools/registry/data.db" in touched

    worktree = Path(tempfile.mkdtemp(prefix=f"pr{args.pr}-review-"))
    shutil.rmtree(worktree)  # git worktree add needs a missing dir
    try:
        code, out = run(["git", "fetch", "origin",
                         f"pull/{args.pr}/head"], cwd=REPO_ROOT)
        if code != 0:
            print(f"Fetch failed:\n{out}")
            return 1
        code, out = run(["git", "worktree", "add", "--detach", str(worktree),
                         "FETCH_HEAD"], cwd=REPO_ROOT)
        if code != 0:
            print(f"Worktree checkout failed:\n{out}")
            return 1

        wt_data_mn = worktree / "data.mn"
        wt_scripts = worktree / "tools" / "scripts"
        wt_tests = worktree / "tools" / "tests"

        # Per-dataset checks.
        for dataset_id in report.datasets:
            code, out = run(
                [python, str(wt_tests / "run_all_checks.py"), dataset_id],
                cwd=worktree)
            # run_all_checks resolves data.mn relative to its own location,
            # so it validates the worktree copy.
            report.add(f"{dataset_id}: run_all_checks", code == 0,
                       "" if code == 0 else tail(out))
            code, out = run(
                [python, str(wt_scripts / "validate_dataset.py"),
                 "--all", dataset_id,
                 "--base-dir", str(wt_data_mn)], cwd=worktree)
            report.add(f"{dataset_id}: validate_dataset", code == 0,
                       "" if code == 0 else tail(out))

        # Global checks (run from the worktree copies).
        code, out = run(
            [python, str(wt_scripts / "validate_mdx_datafiles.py")],
            cwd=worktree)
        report.add("MDX dataFiles", code == 0,
                   "" if code == 0 else tail(out))

        # Registry DB diff (informational, never fails the review).
        db_changed_ids: list[str] = []
        if db_touched:
            base_db = worktree / "base-data.db"
            head_db = worktree / "head-data.db"
            # Binary blobs: capture raw bytes, not text.
            base_blob = subprocess.run(
                ["git", "show", f"{base_ref}:tools/registry/data.db"],
                cwd=REPO_ROOT, capture_output=True, timeout=60).stdout
            head_blob = subprocess.run(
                ["git", "show", f"{head_sha}:tools/registry/data.db"],
                cwd=REPO_ROOT, capture_output=True, timeout=60).stdout
            base_db.write_bytes(base_blob)
            head_db.write_bytes(head_blob)
            _, diff_out = run(
                [python, str(scripts / "diff_registry_db.py"),
                 str(base_db), str(head_db)], cwd=REPO_ROOT)
            report.db_diff = diff_out
            report.add("Registry DB diff", None, "see diff below")
            try:
                db_changed_ids = changed_dataset_ids(base_db, head_db)
            except sqlite3.Error as exc:
                report.add("Registry DB readable", False, str(exc))
        else:
            report.add("Registry DB diff", None, "data.db untouched")

        # Deprecation: only datasets this PR touched (MDX or registry row),
        # so pre-existing issues elsewhere don't block the review.
        depr_ids = sorted(set(report.datasets) | set(db_changed_ids))
        if depr_ids:
            # PRs opened before the deprecation check existed lack it in
            # the worktree; fall back to the local copy pointed at the
            # worktree's DB and pages.
            wt_depr = wt_scripts / "validate_deprecation.py"
            if wt_depr.exists():
                depr_cmd = [python, str(wt_depr)]
            else:
                depr_cmd = [python, str(scripts / "validate_deprecation.py"),
                            "--db", str(worktree / "tools" / "registry"
                                        / "data.db"),
                            "--data-mn", str(wt_data_mn)]
            failures = []
            for dataset_id in depr_ids:
                code, out = run(depr_cmd + [dataset_id], cwd=worktree)
                if code != 0:
                    failures.append(f"{dataset_id}:\n{tail(out)}")
            report.add("Deprecation consistency", not failures,
                       "\n".join(failures))
        else:
            report.add("Deprecation consistency", None, "no candidates")

        if args.fast:
            report.add("Charts (vega --all)", None, "skipped (--fast)")
        else:
            code, out = run(
                [python, str(wt_scripts / "validate_vega.py"), "--all"],
                cwd=wt_data_mn)
            report.add("Charts (vega --all)", code == 0,
                       "" if code == 0 else tail(out))

        if args.build and not args.fast:
            code, out = run(["npm", "run", "build"], cwd=wt_data_mn,
                            timeout=1800)
            report.add("Build (npm)", code == 0,
                       "" if code == 0 else tail(out, 15))
        else:
            report.add("Build (npm)", None, "skipped (pass --build)")

        if args.lint and not args.fast:
            code, out = run(["npm", "run", "check"], cwd=wt_data_mn,
                            timeout=900)
            report.add("Lint (npm)", code == 0,
                       "" if code == 0 else tail(out, 15))
        else:
            report.add("Lint (npm)", None, "skipped (pass --lint)")
    finally:
        run(["git", "worktree", "remove", "--force", str(worktree)],
            cwd=REPO_ROOT)
        run(["git", "worktree", "prune"], cwd=REPO_ROOT)

    report.print()
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
