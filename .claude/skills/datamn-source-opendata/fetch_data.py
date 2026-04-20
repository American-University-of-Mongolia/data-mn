#!/usr/bin/env python3
"""
Download a dataset from opendata.gov.mn by ID and convert to CSV.

Usage:
    python3 fetch_data.py 6686                    # Download dataset 6686 (auto-detect format)
    python3 fetch_data.py 6686 --format csv       # Prefer CSV if available
    python3 fetch_data.py 6686 --format json      # Prefer JSON
    python3 fetch_data.py 6686 --list-files       # List available files without downloading
    python3 fetch_data.py 6686 --file-id 18132    # Download specific file by file ID
    python3 fetch_data.py 6686 --output /tmp/out  # Custom output directory

Output directory: tools/temp/opendata/{dataset_id}/
Output files:
    {dataset_id}-raw.{ext}   -- raw downloaded file
    {dataset_id}-mn.csv      -- cleaned Mongolian CSV (ready for translate_csv.py)
"""

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

# ─── Constants ────────────────────────────────────────────────────────────────

BASE_URL = "https://opendata.gov.mn/api/v1"
MEDIA_URL = f"{BASE_URL}/media"

_REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = _REPO_ROOT / "tools" / "temp" / "opendata"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Referer": "https://opendata.gov.mn/",
}

# Preferred format order for auto-selection
FORMAT_PRIORITY = ["csv", "xlsx", "json", "xml", "geojson"]


# ─── API Helpers ──────────────────────────────────────────────────────────────


def post(endpoint: str, payload: dict) -> dict | None:
    url = f"{BASE_URL}{endpoint}"
    r = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("code") == 200:
        return data["result"]
    print(f"API error: {data.get('message')}", file=sys.stderr)
    return None


def get_detail(dataset_id: int) -> dict | None:
    return post("/front/detail/view", {"id": dataset_id})


def build_download_url(file_obj: dict) -> str:
    path = file_obj["path"]
    return f"{MEDIA_URL}/{path}"


# ─── Download Logic ───────────────────────────────────────────────────────────


def select_file(files: list[dict], preferred_format: str | None) -> dict | None:
    """Select the best file from a dataset's file list."""
    if not files:
        return None

    # Filter by preferred format if specified
    if preferred_format:
        matches = [f for f in files if f["ext"].lower() == preferred_format.lower()]
        if matches:
            return matches[0]
        print(f"  No {preferred_format.upper()} file found, falling back to auto-select.")

    # Auto-select by priority
    for fmt in FORMAT_PRIORITY:
        for f in files:
            if f["ext"].lower() == fmt:
                return f

    return files[0]


def download_file(url: str, dest: Path, file_size_bytes: int = 0) -> Path:
    """Download a file with progress indication, skipping if cached."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"  Cached: {dest.name}")
        return dest

    size_mb = file_size_bytes / 1024 / 1024 if file_size_bytes else 0
    size_str = f" ({size_mb:.0f} MB)" if size_mb > 0 else ""
    print(f"  Downloading{size_str}: {url}")

    dl_headers = {k: v for k, v in HEADERS.items() if k != "Content-Type"}
    dl_headers["Accept"] = "*/*"

    r = requests.get(url, headers=dl_headers, timeout=300, stream=True)
    r.raise_for_status()

    downloaded = 0
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=65536):
            f.write(chunk)
            downloaded += len(chunk)
            if size_mb > 10:
                mb = downloaded / 1024 / 1024
                print(f"\r  Progress: {mb:.1f}/{size_mb:.0f} MB", end="", flush=True)

    if size_mb > 10:
        print()

    actual_mb = dest.stat().st_size / 1024 / 1024
    print(f"  Saved: {dest.name} ({actual_mb:.1f} MB)")
    return dest


# ─── Conversion Logic ─────────────────────────────────────────────────────────


def json_to_csv(json_path: Path, csv_path: Path) -> pd.DataFrame | None:
    """Convert a JSON dataset file to a flat CSV."""
    print(f"  Converting JSON → CSV ...")

    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"  Warning: JSON parse error: {e}")
        # Try streaming with lines=True (NDJSON)
        try:
            df = pd.read_json(json_path, lines=True)
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            print(f"  Converted (NDJSON): {csv_path.name} ({len(df)} rows)")
            return df
        except Exception:
            print(f"  Error: Could not parse JSON file.")
            return None

    # Handle different JSON shapes
    if isinstance(data, list):
        df = pd.json_normalize(data)
    elif isinstance(data, dict):
        # Try common wrapper keys
        for key in ["data", "result", "items", "records", "rows"]:
            if key in data and isinstance(data[key], list):
                df = pd.json_normalize(data[key])
                break
        else:
            df = pd.json_normalize([data])
    else:
        print(f"  Error: unexpected JSON type {type(data)}")
        return None

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"  Converted: {csv_path.name} ({len(df)} rows, {len(df.columns)} columns)")
    return df


def xlsx_to_csv(xlsx_path: Path, csv_path: Path) -> pd.DataFrame | None:
    """Convert XLSX to CSV."""
    print(f"  Converting XLSX → CSV ...")
    df = pd.read_excel(xlsx_path, engine="openpyxl")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"  Converted: {csv_path.name} ({len(df)} rows, {len(df.columns)} columns)")
    return df


def convert_to_csv(raw_path: Path, csv_path: Path, ext: str) -> pd.DataFrame | None:
    """Convert downloaded file to CSV based on extension."""
    ext = ext.lower()
    if ext == "csv":
        # Already CSV — just copy and return
        import shutil
        shutil.copy(raw_path, csv_path)
        df = pd.read_csv(csv_path, encoding="utf-8-sig", nrows=5)
        total = sum(1 for _ in open(csv_path)) - 1
        print(f"  Copied: {csv_path.name} (~{total} rows, {len(df.columns)} columns)")
        return df
    elif ext == "json":
        return json_to_csv(raw_path, csv_path)
    elif ext in ("xlsx", "xls"):
        return xlsx_to_csv(raw_path, csv_path)
    else:
        print(f"  Warning: no converter for .{ext} — raw file saved only.")
        return None


# ─── Main Logic ───────────────────────────────────────────────────────────────


def cmd_list_files(dataset_id: int):
    """List available files for a dataset."""
    detail = get_detail(dataset_id)
    if not detail:
        print(f"Dataset {dataset_id} not found.")
        return

    print(f"\nDataset: {detail['name']}")
    print(f"Org:     {detail.get('org', {}).get('name', '')}")
    print(f"Updated: {detail.get('term', 'N/A')}\n")

    files = detail.get("files") or []
    if not files:
        print("No files available.")
        return

    print(f"Files ({len(files)}):")
    for f in files:
        size_mb = f.get("size", 0) / 1024 / 1024
        url = build_download_url(f)
        print(f"  [{f['id']}] {f['ext'].upper():8} {size_mb:8.1f} MB  {url} (.{f['ext']})")


def cmd_download(dataset_id: int, preferred_format: str | None,
                 file_id: int | None, output_dir: Path):
    """Download dataset and convert to CSV."""
    detail = get_detail(dataset_id)
    if not detail:
        print(f"Dataset {dataset_id} not found.")
        sys.exit(1)

    print(f"\nDataset: {detail['name']}")
    print(f"Org:     {detail.get('org', {}).get('name', '')}")
    print(f"Updated: {detail.get('term', 'N/A')}\n")

    files = detail.get("files") or []
    if not files:
        print("Error: No files available for this dataset.")
        sys.exit(1)

    # Select file
    if file_id is not None:
        matches = [f for f in files if f["id"] == file_id]
        if not matches:
            print(f"Error: File ID {file_id} not found in dataset {dataset_id}.")
            sys.exit(1)
        selected = matches[0]
    else:
        selected = select_file(files, preferred_format)

    if not selected:
        print("Error: Could not select a file.")
        sys.exit(1)

    ext = selected["ext"].lower()
    size_mb = selected.get("size", 0) / 1024 / 1024
    print(f"Selected: [{selected['id']}] {ext.upper()} ({size_mb:.1f} MB)")

    # Determine output paths
    out_dir = output_dir / str(dataset_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_name = f"{dataset_id}-raw.{ext}"
    csv_name = f"{dataset_id}-mn.csv"
    raw_path = out_dir / raw_name
    csv_path = out_dir / csv_name

    # Download
    url = build_download_url(selected)
    download_file(url, raw_path, file_size_bytes=selected.get("size", 0))

    # Convert to CSV
    if ext != csv_name.split(".")[-1]:
        df = convert_to_csv(raw_path, csv_path, ext)
    else:
        df = convert_to_csv(raw_path, csv_path, ext)

    print(f"\nOutput directory: {out_dir}")
    print(f"Raw file:   {raw_name}")
    if csv_path.exists():
        print(f"CSV file:   {csv_name}")
        print(f"\nNext step: translate to English:")
        print(f"  conda run -n datamn python3 tools/scripts/translate_csv.py \\")
        print(f"    {csv_path} --from mn --to en \\")
        print(f"    -o {out_dir / csv_name.replace('-mn.csv', '-en.csv')}")


# ─── CLI ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Download datasets from opendata.gov.mn"
    )
    parser.add_argument("dataset_id", type=int, help="Dataset ID (e.g. 6686)")
    parser.add_argument(
        "--format", choices=["csv", "json", "xlsx", "xml"],
        help="Preferred file format (default: auto-select best)"
    )
    parser.add_argument(
        "--file-id", type=int, metavar="ID",
        help="Download specific file by file ID"
    )
    parser.add_argument(
        "--list-files", action="store_true",
        help="List available files without downloading"
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help=f"Output directory (default: {DEFAULT_OUTPUT})"
    )
    args = parser.parse_args()

    if args.list_files:
        cmd_list_files(args.dataset_id)
    else:
        cmd_download(args.dataset_id, args.format, args.file_id, args.output)


if __name__ == "__main__":
    main()
