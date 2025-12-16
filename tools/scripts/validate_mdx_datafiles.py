#!/usr/bin/env python3
"""
Validate MDX dataFiles frontmatter to ensure CSV/XLSX files exist.

Usage:
    python validate_mdx_datafiles.py                    # Validate all MDX files
    python validate_mdx_datafiles.py path/to/file.mdx   # Validate specific file
    python validate_mdx_datafiles.py --fix              # Auto-fix missing -lang suffixes
"""

import os
import sys
import re
import yaml
from pathlib import Path
from typing import List, Dict, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent.parent.parent
DATA_MN_DIR = SCRIPT_DIR / "data.mn"
MDX_DIRS = [
    DATA_MN_DIR / "src" / "data" / "data" / "en",
    DATA_MN_DIR / "src" / "data" / "data" / "mn",
]
DATASETS_DIR = DATA_MN_DIR / "public" / "datasets"


def extract_frontmatter(mdx_path: Path) -> Dict:
    """Extract YAML frontmatter from MDX file."""
    content = mdx_path.read_text(encoding='utf-8')

    # Match YAML frontmatter between ---
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        print(f"  ⚠️  YAML parse error in {mdx_path.name}: {e}")
        return {}


def validate_datafiles(mdx_path: Path, fix: bool = False) -> List[str]:
    """Validate dataFiles in MDX frontmatter. Returns list of errors."""
    errors = []
    warnings = []

    frontmatter = extract_frontmatter(mdx_path)
    if not frontmatter:
        return []

    data_files = frontmatter.get('dataFiles', [])
    if not data_files:
        return []

    # Determine language from path
    lang = 'en' if '/en/' in str(mdx_path) else 'mn'

    for file_info in data_files:
        file_path = file_info.get('path', '')
        if not file_path:
            continue

        # Remove leading slash and construct full path
        relative_path = file_path.lstrip('/')
        full_path = DATA_MN_DIR / "public" / relative_path

        # Check if file exists
        if not full_path.exists():
            errors.append(f"Missing file: {file_path}")

            # Check for common issues
            if file_path.endswith('.csv'):
                # Check if it's missing the language suffix
                base = file_path[:-4]  # Remove .csv
                lang_version = f"{base}-{lang}.csv"
                lang_path = DATA_MN_DIR / "public" / lang_version.lstrip('/')

                if lang_path.exists():
                    errors[-1] += f"\n      → Suggested fix: Use '{lang_version}' instead"

                    if fix:
                        # TODO: Implement auto-fix
                        pass
        else:
            # File exists - check format
            if file_path.endswith('.csv'):
                # Verify it's the correct language version for this page
                expected_suffix = f"-{lang}.csv"
                if not file_path.endswith(expected_suffix) and '-en.csv' not in file_path and '-mn.csv' not in file_path:
                    warnings.append(f"CSV may not be language-specific: {file_path}")

    return errors, warnings


def validate_all() -> Tuple[int, int]:
    """Validate all MDX files. Returns (error_count, warning_count)."""
    total_errors = 0
    total_warnings = 0
    files_checked = 0

    print("\n🔍 Validating MDX dataFiles...\n")

    for mdx_dir in MDX_DIRS:
        if not mdx_dir.exists():
            print(f"⚠️  Directory not found: {mdx_dir}")
            continue

        for mdx_file in sorted(mdx_dir.glob("*.mdx")):
            files_checked += 1
            errors, warnings = validate_datafiles(mdx_file)

            if errors or warnings:
                print(f"📄 {mdx_file.relative_to(DATA_MN_DIR)}")

                for error in errors:
                    print(f"   ❌ {error}")
                    total_errors += 1

                for warning in warnings:
                    print(f"   ⚠️  {warning}")
                    total_warnings += 1

    print(f"\n{'='*60}")
    print(f"Checked {files_checked} MDX files")

    if total_errors == 0 and total_warnings == 0:
        print("✅ All dataFiles are valid!")
    else:
        if total_errors > 0:
            print(f"❌ {total_errors} error(s) found")
        if total_warnings > 0:
            print(f"⚠️  {total_warnings} warning(s) found")

    return total_errors, total_warnings


def validate_single(mdx_path: str) -> int:
    """Validate a single MDX file. Returns error count."""
    path = Path(mdx_path)
    if not path.exists():
        print(f"❌ File not found: {mdx_path}")
        return 1

    print(f"\n🔍 Validating {path.name}...\n")

    errors, warnings = validate_datafiles(path)

    if errors:
        for error in errors:
            print(f"   ❌ {error}")

    if warnings:
        for warning in warnings:
            print(f"   ⚠️  {warning}")

    if not errors and not warnings:
        print("✅ All dataFiles are valid!")
        return 0

    return len(errors)


def main():
    fix_mode = '--fix' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--fix']

    if args:
        # Validate specific file
        exit_code = validate_single(args[0])
    else:
        # Validate all
        errors, warnings = validate_all()
        exit_code = 1 if errors > 0 else 0

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
