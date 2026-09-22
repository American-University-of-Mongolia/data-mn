#!/usr/bin/env python3
"""Fetch a bounded, bilingual NSO extract for the livestock-loss project.

Uses stable region/animal codes and discovers year codes from labels on every
refresh. The NSO year codes are positions, not literal calendar years.
"""

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "tools/versions/nso-livestock-losses/v2/raw"
TABLES = {"losses": "DT_NSO_1001_029V1.px", "herds": "DT_NSO_1001_021V1.px"}
API = "https://data.1212.mn/api/v1/{lang}/NSO/Industry,%20service/Livestock/"


def request_json(url, query=None):
    data = None if query is None else json.dumps(query).encode()
    req = Request(url, data=data, headers={
        "Accept": "application/json", "Content-Type": "application/json",
        "User-Agent": "data.mn livestock-losses contributor",
    })
    with urlopen(req, timeout=60) as response:
        return json.load(response)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def fetch(start, end, output):
    years = next(v for v in request_json(API.format(lang="en") + TABLES["losses"])["variables"] if v["code"] == "Он")
    available = sorted(map(int, years["valueTexts"]))
    start = min(available) if start is None else start
    end = max(available) if end is None else end
    if start > end:
        raise ValueError("Start year must not exceed end year")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Preserve saved versions; choose a new --output directory: {output}")
    catalog = request_json(API.format(lang="en"))
    updates = {t["id"]: t.get("updated") for t in catalog}
    save_json(output / "catalog.json", catalog)
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(),
                "loss_year_start": start, "loss_year_end": end, "tables": {}}
    for kind, table in TABLES.items():
        manifest["tables"][kind] = {"id": table, "updated": updates[table], "languages": {}}
        for lang in ("en", "mn"):
            time.sleep(1)
            url = API.format(lang=lang) + quote(table)
            metadata = request_json(url)
            selection = {}
            for variable in metadata["variables"]:
                code = variable["code"]
                pairs = list(zip(variable["values"], variable["valueTexts"]))
                if code == "Бүс":
                    # National total plus 21 aimags and the capital. Excludes
                    # the duplicate UB regional total (5), soums and bags.
                    values = [v for v, _ in pairs if v == "0" or len(v) == 3]
                    assert len(values) == 23, values
                elif code == "Он":
                    minimum = start if kind == "losses" else start - 1
                    maximum = end if kind == "losses" else end - 1
                    values = [v for v, label in pairs if minimum <= int(label) <= maximum]
                    assert len(values) == end - start + 1, (table, lang, values)
                else:
                    assert code == "Малын төрөл", code
                    values = variable["values"]
                    assert values == ["0", "1", "2", "3", "4", "5"]
                selection[code] = values
            query = {"query": [{"code": code, "selection": {"filter": "item", "values": values}}
                               for code, values in selection.items()],
                     "response": {"format": "json-stat2"}}
            result = request_json(url, query)
            for suffix, payload in (("metadata", metadata), ("query", query), ("data", result)):
                save_json(output / f"{kind}-{lang}-{suffix}.json", payload)
            data_path = output / f"{kind}-{lang}-data.json"
            manifest["tables"][kind]["languages"][lang] = {
                "api_url": url, "sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
                "rows": len(result["value"]),
            }
            print(kind, lang, result.get("size"), "observations:", len(result["value"]), flush=True)
    save_json(output / "manifest.json", manifest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, help="Defaults to the earliest available loss year")
    parser.add_argument("--end", type=int, help="Defaults to the latest available loss year")
    parser.add_argument("--output", type=Path, default=RAW)
    args = parser.parse_args()
    fetch(args.start, args.end, args.output)
