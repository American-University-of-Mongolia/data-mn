#!/usr/bin/env python3
"""Rebuild hay-harvest-by-aimag CSVs and charts from the saved NSO v1 extract.

Source: DT_NSO_1002_007V1.px (unit: thousand tonnes). Keeps the 22 leaf units
(21 aimags + Ulaanbaatar, code 511); region groups, the national total and the
duplicate capital group (code 5) are excluded. Missing source cells stay empty.
"""

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATASET_ID = "hay-harvest-by-aimag"
VERSION = ROOT / f"tools/versions/{DATASET_ID}/v1"
RAW = VERSION / "raw"
PUBLIC = ROOT / "data.mn/public"
GROUPS = {"0", "1", "2", "3", "4", "5"}
CONFIG = {"axis": {"labelFontSize": 14, "titleFontSize": 16, "labelColor": "#64748b", "titleColor": "#334155"},
          "view": {"stroke": "transparent"}, "legend": {"labelFontSize": 13, "titleFontSize": 14}}
SCHEMA = "https://vega.github.io/schema/vega-lite/v5.json"
UNIT = {"en": "Hay and fodder (thousand tonnes)", "mn": "Өвс, тэжээл (мянган тонн)"}
DESC = {"en": "Hay cut and fodder laid in for winter across Mongolia's 21 aimags and Ulaanbaatar, in thousand tonnes, 1960 to 2025. Boundaries: geoBoundaries (ODbL) / OpenStreetMap contributors.",
        "mn": "Монгол Улсын 21 аймаг, Улаанбаатар хотын 1960-2025 оны хадсан өвс, бэлтгэсэн тэжээл, мянган тонноор. Хил хязгаар: geoBoundaries (ODbL) / OpenStreetMap contributors."}


def decode(lang):
    data = json.loads((RAW / f"data-{lang}.json").read_text(encoding="utf-8"))
    assert data["id"] == ["Бүс", "он"]
    reg, yr = (data["dimension"][k]["category"] for k in data["id"])
    rc = sorted(reg["index"], key=reg["index"].get)
    yc = sorted(yr["index"], key=yr["index"].get)
    assert len(data["value"]) == len(rc) * len(yc)
    out = {}
    for i, (r, y) in enumerate(itertools.product(rc, yc)):
        v = data["value"][i]
        if v is not None:
            assert isinstance(v, (int, float)) and math.isfinite(v) and v >= 0
        out[int(yr["label"][y]), r] = (v, reg["label"][r].strip())
    return out, rc


def write_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:  # plain UTF-8, no BOM
        w = csv.writer(f, lineterminator="\n")
        w.writerow(headers)
        w.writerows(rows)


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def csv_data(name, lang):
    num = ["year", "value"] if lang == "en" else ["он", "утга"]
    return {"url": f"/datasets/{name}", "format": {"type": "csv", "parse": {k: "number" for k in num}}}


def charts(lang, maximum, end, start):
    year, region, value = ("year", "region", "value") if lang == "en" else ("он", "бүс", "утга")
    en = lang == "en"
    ytitle, rtitle = ("Year", "Aimag / capital") if en else ("Он", "Аймаг, нийслэл")
    unit = UNIT[lang]
    name = "name" if en else "name_mn"
    unavailable = "'Unavailable'" if en else "'Мэдээлэлгүй'"
    csvname = f"{DATASET_ID}-{lang}.csv"
    m = {"$schema": SCHEMA, "description": DESC[lang], "config": CONFIG, "data": csv_data(csvname, lang),
         "params": [{"name": "selectedYear", "value": end, "bind": {"input": "range", "min": start, "max": end, "step": 1, "name": ytitle + ": "}}],
         "transform": [{"filter": f"datum['{year}'] == selectedYear"},
                       {"lookup": region, "from": {"data": {"url": "/maps/mongolia-aimags.json", "format": {"type": "json", "property": "features"}},
                                                  "key": f"properties.{name}"}, "as": "boundary"},
                       {"calculate": f"isValid(datum['{value}']) ? format(datum['{value}'], ',.2f') : {unavailable}", "as": "display_value"}],
         "projection": {"type": "mercator"},
         "mark": {"type": "geoshape", "stroke": "white", "strokeWidth": 1, "invalid": None},
         "encoding": {"shape": {"field": "boundary", "type": "geojson"},
                      "color": {"field": value, "type": "quantitative", "scale": {"scheme": "greens", "domain": [0, maximum]},
                                "condition": {"test": f"!isValid(datum['{value}'])", "value": "#cbd5e1"},
                                "legend": {"orient": "top", "title": unit, "format": ",.0f", "titleLimit": 350, "gradientLength": 250}},
                      "tooltip": [{"field": region, "type": "nominal", "title": rtitle},
                                  {"field": year, "type": "quantitative", "title": ytitle, "format": "d"},
                                  {"field": "display_value", "type": "nominal", "title": unit}]}}
    write_json(PUBLIC / f"charts/{DATASET_ID}-{lang}.json", m)
    r = {"$schema": SCHEMA,
         "description": "Six aimags/capital with the highest value in the selected year. All 22 regions are in the downloads." if en
         else "Сонгосон онд хамгийн өндөр үзүүлэлттэй зургаан аймаг, нийслэл. Бүх 22 нутаг дэвсгэрийн мэдээллийг татаж авна.",
         "config": CONFIG, "data": csv_data(csvname, lang), "params": [{"name": "selectedYear", "value": end}],
         "transform": [{"filter": f"datum['{year}'] == selectedYear"}, {"filter": f"isValid(datum['{value}'])"},
                       {"window": [{"op": "row_number", "as": "rank"}],
                        "sort": [{"field": value, "order": "descending"}, {"field": region, "order": "ascending"}]},
                       {"filter": "datum.rank <= 6"}],
         "mark": {"type": "bar", "color": "#54a24b", "cornerRadiusEnd": 3},
         "encoding": {"y": {"field": region, "type": "nominal", "sort": "-x", "title": None, "axis": {"labelLimit": 150}},
                      "x": {"field": value, "type": "quantitative", "title": unit, "scale": {"zero": True}, "axis": {"format": ",.0f"}},
                      "tooltip": [{"field": region, "type": "nominal", "title": rtitle},
                                  {"field": year, "type": "quantitative", "title": ytitle, "format": "d"},
                                  {"field": value, "type": "quantitative", "title": unit, "format": ",.2f"}]}}
    write_json(PUBLIC / f"charts/{DATASET_ID}-ranking-{lang}.json", r)


def build():
    en, codes = decode("en")
    mn, codes_mn = decode("mn")
    assert codes == codes_mn and en.keys() == mn.keys()
    assert all(en[k][0] == mn[k][0] for k in en)
    leaves = [c for c in codes if c not in GROUPS]
    assert len(leaves) == 22
    years = sorted({y for y, _ in en})
    rows = {"en": [], "mn": []}
    for y in years:
        for c in leaves:
            v = en[y, c][0]
            for lang, src in (("en", en), ("mn", mn)):
                rows[lang].append([y, src[y, c][1], "" if v is None else v])
    for lang, h in (("en", ["year", "region", "value"]), ("mn", ["он", "бүс", "утга"])):
        write_csv(PUBLIC / f"datasets/{DATASET_ID}-{lang}.csv", h, rows[lang])
        (VERSION / f"data-{lang}.csv").write_bytes((PUBLIC / f"datasets/{DATASET_ID}-{lang}.csv").read_bytes())
    maximum = max(r[2] for r in rows["en"] if r[2] != "")
    for lang in ("en", "mn"):
        charts(lang, maximum, years[-1], years[0])
    manifest = {"table": "DT_NSO_1002_007V1.px", "unit_en": "thousand tonnes", "unit_mn": "мян.тн",
                "years": [years[0], years[-1]], "source_updated": "2026-01-15",
                "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(RAW.glob("*.json"))}}
    write_json(VERSION / "manifest.json", manifest)
    print(len(rows["en"]), "rows per language;", sum(r[2] == "" for r in rows["en"]), "missing; max", maximum)


if __name__ == "__main__":
    build()
