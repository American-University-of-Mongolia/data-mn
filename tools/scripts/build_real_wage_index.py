#!/usr/bin/env python3
"""Build the national real-wage draft from an immutable bilingual NSO snapshot.

Run --fetch once to create v1/raw. Later runs rebuild CSVs, charts and pages
offline. Refreshes require a new reviewed version, never overwriting v1.
Excel downloads use the repository's rebuild_downloads.py contract.
"""

import argparse
import csv
import hashlib
import json
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SLUG = "real-wage-index-national"
VERSION = ROOT / "tools/versions" / SLUG / "v1"
GROUP = "REAL WAGE INDEX (2023=100), by divisions of economic activities"
SOURCE_PATH = f"Labour, business/Wages/{GROUP}/DT_NSO_0400_036V4.px"
TABLE = "DT_NSO_0400_036V4.px"
YEARBOOK = "https://downloads.1212.mn/YEARBOOK_2018.pdf"


def source_url(lang):
    group = urllib.parse.quote(f"NSO__Labour, business__Wages__{GROUP}", safe="")
    return f"https://data.1212.mn/pxweb/{lang}/NSO/{group}/{TABLE}/"


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def fetch():
    raw = VERSION / "raw"
    if raw.exists():
        raise RuntimeError("Snapshot already exists. Use a new version for a refresh.")
    raw.mkdir(parents=True)
    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "table": TABLE,
                "source_path": SOURCE_PATH, "files": {}}
    for lang in ("en", "mn"):
        url = f"https://data.1212.mn/api/v1/{lang}/NSO/" + urllib.parse.quote(SOURCE_PATH, safe="/")
        with urllib.request.urlopen(url, timeout=45) as response:
            metadata = json.load(response)
        dump(raw / f"metadata-{lang}.json", metadata)
        query = {"query": [{"code": v["code"], "selection": {
            "filter": "item", "values": v["values"]}} for v in metadata["variables"]],
            "response": {"format": "json-stat2"}}
        dump(raw / f"query-{lang}.json", query)
        request = urllib.request.Request(url, data=json.dumps(query).encode(),
                                         headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=45) as response:
            dump(raw / f"response-{lang}.json", json.load(response))
        with urllib.request.urlopen(source_url(lang), timeout=45) as response:
            (raw / f"source-page-{lang}.html").write_bytes(response.read())
    for path in sorted(raw.iterdir()):
        manifest["files"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    dump(raw / "manifest.json", manifest)


def national_rows(lang):
    data = json.loads((VERSION / f"raw/response-{lang}.json").read_text())
    sector, year = data["id"]
    sector_index = data["dimension"][sector]["category"]["index"]
    years = data["dimension"][year]["category"]
    assert "0" in sector_index, "National aggregate source code missing"
    offset = sector_index["0"] * data["size"][1]
    return sorted((int(years["label"][code]), data["value"][offset + index])
                  for code, index in years["index"].items())


def build():
    manifest = json.loads((VERSION / "raw/manifest.json").read_text())
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((VERSION / "raw" / name).read_bytes()).hexdigest() == digest
    en, mn = national_rows("en"), national_rows("mn")
    assert en == mn, "Bilingual numeric mismatch"
    assert [y for y, _ in en] == list(range(1992, 2026))
    assert all(isinstance(v, (int, float)) and v > 0 for _, v in en)
    assert dict(en)[2023] == 100, "Source base changed: review before building"
    captions = {
        "en": "Index: 2023 = 100. Dashed lines mark a source change in 2014 and a methodology change in 2025. Comparability across 2014 has not been confirmed; NSO explicitly states that 2025 (orange point) is not comparable with earlier years.",
        "mn": "Индекс: 2023 = 100. Тасархай шугам нь 2014 оны эх үүсвэрийн болон 2025 оны аргачлалын өөрчлөлтийг тэмдэглэнэ. 2014 оны өмнөх ба дараах утгуудын харьцуулагдах байдлыг баталгаажуулаагүй. ҮСХ 2025 оныг (улбар шар цэг) өмнөх онуудтай харьцуулах боломжгүй гэж тодорхой тайлбарласан.",
    }
    for lang, rows in (("en", en), ("mn", mn)):
        is_en = lang == "en"
        year = "Year" if is_en else "Он"
        value = "Real wage index (2023=100)" if is_en else "Бодит цалингийн индекс (2023=100)"
        title = "Mongolia Real Wage Index (1992–2025)" if is_en else "Монгол Улсын бодит цалингийн индекс (1992–2025)"
        excerpt = ("Average wages adjusted for consumer prices, showing changes in purchasing power. Source and methodology changes are marked; this is not a measure of each worker's income."
                   if is_en else "Хэрэглээний үнийн өөрчлөлтөөр засварласан дундаж цалингийн индекс нь худалдан авах чадварын өөрчлөлтийг харуулна. Эх үүсвэр болон аргачлалын өөрчлөлтийг тэмдэглэв; ажилтан бүрийн орлогыг хэмжихгүй.")
        csv_path = ROOT / f"data.mn/public/datasets/{SLUG}-{lang}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow([year, value])
            writer.writerows(rows)
        (VERSION / f"{SLUG}-{lang}.csv").write_bytes(csv_path.read_bytes())
        x = {"field": year, "type": "quantitative", "title": year,
             "scale": {"domain": [1992, 2026], "nice": False},
             "axis": {"format": "d", "tickCount": 6, "grid": False, "labelAngle": 0,
                      "labelOverlap": "greedy", "labelSeparation": 8}}
        y = {"field": value, "type": "quantitative",
             "title": "Index (2023=100)" if is_en else "Индекс (2023=100)",
             "scale": {"zero": True, "domainMax": 140}, "axis": {"format": ".0f", "gridOpacity": 0.25}}
        tooltip = [{"field": year, "title": year, "type": "quantitative", "format": "d"},
                   {"field": value, "title": value, "type": "quantitative", "format": ".1f"}]
        line = {"type": "line", "strokeWidth": 2.5, "color": "#1f77b4", "interpolate": "linear"}
        spec = {"$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "description": title + ". " + captions[lang],
                "data": {"url": f"/datasets/{SLUG}-{lang}.csv", "format": {"type": "csv"}},
                "encoding": {"x": x, "y": y},
                "layer": [
                    {"transform": [{"filter": f"datum['{year}'] < 2014"}], "mark": line,
                     "encoding": {"x": x, "y": y}},
                    {"transform": [{"filter": f"datum['{year}'] >= 2014 && datum['{year}'] < 2025"}],
                     "mark": line, "encoding": {"x": x, "y": y}},
                    {"transform": [{"filter": f"datum['{year}'] >= 2013 && datum['{year}'] <= 2014"}],
                     "mark": {**line, "strokeDash": [5, 4]}, "encoding": {"x": x, "y": y}},
                    {"transform": [{"filter": f"datum['{year}'] >= 2024 && datum['{year}'] <= 2025"}],
                     "mark": {**line, "strokeDash": [5, 4], "color": "#d97706"},
                     "encoding": {"x": x, "y": y}},
                    {"params": [{"name": "hover", "select": {"type": "point", "nearest": True,
                        "on": "pointerover", "clear": "pointerout"}}],
                     "mark": {"type": "point", "filled": True, "size": 70, "color": "#1f77b4"},
                     "encoding": {"x": x, "y": y, "tooltip": tooltip,
                                  "opacity": {"condition": {"param": "hover", "empty": False, "value": 1}, "value": 0}}},
                    {"transform": [{"filter": f"datum['{year}'] == 2025"}],
                     "mark": {"type": "circle", "size": 110, "color": "#d97706"},
                     "encoding": {"x": x, "y": y, "tooltip": tooltip}},
                ],
                "config": {"view": {"stroke": "transparent"},
                           "axis": {"labelFontSize": 14, "titleFontSize": 16, "titlePadding": 10,
                                    "labelColor": "#64748b", "titleColor": "#334155"}}}
        dump(ROOT / f"data.mn/public/charts/{SLUG}-{lang}.json", spec)
        source = "National Statistics Office of Mongolia" if is_en else "Үндэсний Статистикийн Хороо"
        tags = ["mongolia", "real wages", "purchasing power", "inflation", "labor"] if is_en else ["монгол", "бодит цалин", "худалдан авах чадвар", "инфляц", "хөдөлмөр"]
        metadata = {"title": title, "publishDate": date(2026, 9, 30), "excerpt": excerpt,
                    "category": "Labor Market" if is_en else "Хөдөлмөрийн зах зээл",
                    "tags": tags, "keywords": tags, "author": "Data.mn", "dataVersion": 1,
                    "dataDate": date(2025, 12, 31), "excelLanguage": "page", "dataFiles": [
                        {"path": f"/datasets/{SLUG}-{lang}.csv", "format": "csv", "size": "1 KB",
                         "description": "Download as CSV" if is_en else "CSV татах"},
                        {"path": f"/datasets/{SLUG}-{lang}.xlsx", "format": "xlsx", "size": "9 KB",
                         "description": "Open in Excel" if is_en else "Excel татах"}],
                    "source": {"name": source, "url": source_url(lang), "tableId": TABLE}}
        page = "---\n" + yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False) + "---\n\n"
        page += "import VegaChart from '~/components/ui/VegaChart.astro';\n\n"
        page += f'<VegaChart spec="/charts/{SLUG}-{lang}.json" title={json.dumps(title, ensure_ascii=False)} caption={json.dumps(captions[lang], ensure_ascii=False)} />\n'
        (ROOT / f"data.mn/src/data/data/{lang}/{SLUG}.mdx").write_text(page)
    dump(VERSION / "validation.json", {"rows_per_language": len(en), "years": [1992, 2025],
         "bilingual_numeric_parity": True, "missing_values": 0, "base_2023": 100,
         "source_hashes_verified": True, "dashed_connectors_before": [2014, 2025]})
    print(f"Built {SLUG}: {len(en)} annual observations per language; source values preserved")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    if args.fetch:
        fetch()
    build()
