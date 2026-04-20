#!/usr/bin/env python3
"""
Search and browse datasets on opendata.gov.mn.

The portal is a Nuxt SPA backed by a REST API at https://opendata.gov.mn/api/v1.
All endpoints use POST with JSON body.

Usage:
    python3 query_api.py хүн ам           # Search by Mongolian keyword
    python3 query_api.py population        # Search by English keyword
    python3 query_api.py --list            # List all datasets (page 1)
    python3 query_api.py --list --page 3   # List page 3
    python3 query_api.py --detail 6686     # Get dataset detail by ID
    python3 query_api.py --org 5296722     # List datasets from an org
    python3 query_api.py --count           # Print total dataset count
"""

import argparse
import json
import sys
import time

import requests

# ─── Constants ────────────────────────────────────────────────────────────────

BASE_URL = "https://opendata.gov.mn/api/v1"
PAGE_SIZE = 20

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

# Update frequency UUID → name mapping (from /front/reference)
FREQ_NAMES = {
    "ec3cabe1-c37c-489c-929c-da3e5c109dbd": "Daily / Өдөр бүр",
    "b5b3b3b3-b3b3-b3b3-b3b3-b3b3b3b3b3b3": "Weekly / 7 хоног тутам",
    "monthly": "Monthly / Сар тутам",
}


# ─── API Helpers ──────────────────────────────────────────────────────────────


def post(endpoint: str, payload: dict) -> dict | None:
    """POST to API endpoint; return result dict or None on error."""
    url = f"{BASE_URL}{endpoint}"
    try:
        r = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("code") == 200:
            return data["result"]
        print(f"API error: {data.get('message')}", file=sys.stderr)
        return None
    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return None


def search(query: str = "", page: int = 1, page_size: int = PAGE_SIZE,
           org_reg_num: str = "", sort: str = "created_at DESC") -> dict | None:
    """Search datasets. Returns {items, total_rows, total_pages}."""
    payload = {
        "page": {"page": page, "page_size": page_size, "sort": sort},
        "org_reg_num": org_reg_num,
        "data_uuid": "",
        "frequency_uuid": "",
        "start_term": "",
        "end_term": "",
        "query": query,
    }
    result = post("/front/search", payload)
    if not result:
        return None
    details = result["details"]
    return {
        "items": details["items"],
        "total_rows": details["total_rows"],
        "total_pages": details["total_pages"],
        "page": page,
        "org_list": result.get("org_list", []),
    }


def get_detail(dataset_id: int) -> dict | None:
    """Get full metadata and file list for a dataset."""
    return post("/front/detail/view", {"id": dataset_id})


def get_references() -> dict | None:
    """Get data formats and update frequencies."""
    return post("/front/reference", {})


# ─── Display Helpers ──────────────────────────────────────────────────────────


def print_item(item: dict, idx: int | None = None):
    """Print one dataset item in a human-readable format."""
    prefix = f"[{idx}] " if idx is not None else ""
    freq = item.get("frequency") or {}
    freq_name = freq.get("name", "")
    print(f"{prefix}ID: {item['id']}  |  {freq_name}")
    print(f"  Name: {item['name']}")
    print(f"  Org:  {item.get('org', {}).get('name', '')}")
    term = item.get("term", "")
    if term:
        print(f"  Updated: {term}")
    files = item.get("files") or []
    if files:
        fmts = ", ".join(f"{f['ext'].upper()}" for f in files)
        print(f"  Files: {fmts}")
    print()


def print_detail(detail: dict):
    """Print full dataset detail."""
    print(f"ID:          {detail['id']}")
    print(f"Name:        {detail['name']}")
    org = detail.get("org") or {}
    print(f"Org:         {org.get('name', '')} (reg: {org.get('reg_num', '')})")
    freq = detail.get("frequency") or {}
    print(f"Frequency:   {freq.get('name', 'N/A')}")
    print(f"Updated:     {detail.get('term', 'N/A')}")
    print(f"Status:      {detail.get('status', 'N/A')}")
    print()

    files = detail.get("files") or []
    if files:
        print(f"Files ({len(files)}):")
        for f in files:
            size_mb = f.get("size", 0) / 1024 / 1024
            path = f.get("path", "")
            ext = f.get("ext", "")
            download_url = f"https://opendata.gov.mn/storage/{path}.{ext}"
            print(f"  [{f['id']}] {ext.upper()}  {size_mb:.1f} MB")
            print(f"       {download_url}")
    print()

    desc = detail.get("description", "")
    if desc:
        import re
        clean = re.sub(r"<[^>]+>", "", desc).strip()
        if clean:
            print("Description (schema):")
            print(clean[:800])


# ─── CLI Commands ─────────────────────────────────────────────────────────────


def cmd_search(query: str, page: int, org: str):
    print(f"Searching: '{query}' (page {page}) ...\n")
    result = search(query=query, page=page, org_reg_num=org)
    if not result:
        print("No results.")
        return

    items = result["items"]
    total = result["total_rows"]
    pages = result["total_pages"]

    print(f"Results: {total} datasets ({pages} pages)\n")
    if not items:
        print("No items on this page.")
        return

    for i, item in enumerate(items, 1):
        print_item(item, idx=(page - 1) * PAGE_SIZE + i)

    print(f"Showing page {page}/{pages} ({len(items)} items)")


def cmd_detail(dataset_id: int):
    detail = get_detail(dataset_id)
    if not detail:
        print(f"Dataset {dataset_id} not found.")
        return
    print_detail(detail)


def cmd_count():
    result = search(query="", page=1, page_size=1)
    if result:
        print(f"Total datasets: {result['total_rows']}")


def cmd_list_orgs():
    result = search(query="", page=1, page_size=1)
    if not result:
        return
    for org in sorted(result.get("org_list", []), key=lambda o: o.get("org_name", "")):
        print(f"  {org.get('reg_num', ''):15}  {org.get('org_name', '')}")


# ─── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Search and browse opendata.gov.mn datasets"
    )
    parser.add_argument("query", nargs="*", help="Search keywords")
    parser.add_argument("--list", action="store_true", help="List all datasets")
    parser.add_argument("--detail", type=int, metavar="ID", help="Show dataset detail")
    parser.add_argument("--org", default="", metavar="REG_NUM", help="Filter by org reg_num")
    parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    parser.add_argument("--count", action="store_true", help="Print total dataset count")
    parser.add_argument("--orgs", action="store_true", help="List all organizations")
    args = parser.parse_args()

    if args.count:
        cmd_count()
    elif args.orgs:
        cmd_list_orgs()
    elif args.detail:
        cmd_detail(args.detail)
    elif args.list or args.org:
        cmd_search(query=" ".join(args.query), page=args.page, org=args.org)
    elif args.query:
        cmd_search(query=" ".join(args.query), page=args.page, org=args.org)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
