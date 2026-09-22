#!/usr/bin/env python3
"""Rebuild livestock-loss CSVs, charts and bilingual pages from saved NSO data.

Run fetch_livestock_losses.py first for a fresh source extract. This step is
offline and preserves missing values. Download workbooks use the documented
wide, page-language layout; rebuild_downloads.py is the normal repository writer.
"""

import csv
import hashlib
import itertools
import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "data.mn/public"
VERSION_NUMBER = 2
VERSION = ROOT / f"tools/versions/nso-livestock-losses/v{VERSION_NUMBER}"
RAW = VERSION / "raw"
START, END = 1971, 2025
PUBLISHED = date(2026, 9, 20)
NSO_PAGE = "https://data.1212.mn/pxweb/{lang}/NSO/NSO__Industry,%20service__Livestock/{table}/"
SCHEMA = "https://vega.github.io/schema/vega-lite/v5.json"
CONFIG = {"axis": {"labelFontSize": 14, "titleFontSize": 16, "labelColor": "#64748b", "titleColor": "#334155"},
          "legend": {"labelFontSize": 13, "titleFontSize": 14}, "view": {"stroke": "transparent"}}
DATASETS = {
    "livestock-losses-by-aimag": {
        "measure": "losses_thousand", "category": "region", "unit_en": "Losses (thousand head)", "unit_mn": "Хорогдол (мянган толгой)",
        "title_en": f"Mongolia Livestock Losses by Aimag, Thousand Head ({START}–{END})",
        "title_mn": f"Монгол Улсын том малын зүй бус хорогдол аймгаар, мянган толгой ({START}–{END})",
        "excerpt_en": f"Annual losses of adult livestock across Mongolia’s 21 aimags and Ulaanbaatar, in thousand head, from {START} to {END}; includes natural disasters, disease and other causes.",
        "excerpt_mn": f"Монгол Улсын 21 аймаг, Улаанбаатар хотын {START}–{END} оны том малын зүй бус хорогдол, мянган толгойгоор; байгалийн аюулт үзэгдэл, өвчин болон бусад шалтгааныг хамарна.",
    },
    "livestock-loss-rate-by-aimag": {
        "measure": "loss_rate_percent", "category": "region", "unit_en": "Loss rate (%)", "unit_mn": "Хорогдлын хувь (%)",
        "title_en": f"Mongolia Livestock Loss Rate by Aimag, Percent ({START}–{END})",
        "title_mn": f"Монгол Улсын малын зүй бус хорогдлын хувь аймгаар ({START}–{END})",
        "excerpt_en": f"Annual adult livestock losses as a percentage of the previous year’s closing herd across Mongolia’s 21 aimags and Ulaanbaatar, {START}–{END}; calculated from NSO census tables.",
        "excerpt_mn": f"Монгол Улсын 21 аймаг, Улаанбаатар хотын {START}–{END} оны том малын зүй бус хорогдлыг өмнөх оны эцсийн малын тоонд харьцуулсан хувь; ҮСХ-ны тооллогын хүснэгтүүдээс тооцов.",
    },
    "livestock-losses-by-type": {
        "measure": "losses_thousand", "category": "animal", "unit_en": "Losses (thousand head)", "unit_mn": "Хорогдол (мянган толгой)",
        "title_en": f"Mongolia Livestock Losses by Animal Type, Thousand Head ({START}–{END})",
        "title_mn": f"Монгол Улсын том малын зүй бус хорогдол малын төрлөөр, мянган толгой ({START}–{END})",
        "excerpt_en": f"Annual national losses of horses, cattle, camels, sheep and goats in Mongolia, in thousand head, from {START} to {END}; excludes young animals born during the reporting year.",
        "excerpt_mn": f"Монгол Улсын {START}–{END} оны адуу, үхэр, тэмээ, хонь, ямааны зүй бус хорогдол, мянган толгойгоор; тайлант онд төрсөн төл малын хорогдлыг оруулаагүй.",
    },
}


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def decode(kind, lang):
    data = read_json(RAW / f"{kind}-{lang}-data.json")
    assert data["id"] == ["Малын төрөл", "Бүс", "Он"], data["id"]
    dimensions = [data["dimension"][key]["category"] for key in data["id"]]
    codes = [sorted(d["index"], key=d["index"].get) for d in dimensions]
    assert math.prod(data["size"]) == math.prod(map(len, codes))
    units = data["dimension"]["ContentsCode"]["category"]["unit"]
    unit = next(iter(units.values()))["base"].strip().lower()
    assert unit in {"thousand heads", "thousand head", "мянган толгой"}, unit
    records = {}
    for i, (animal, region, year_code) in enumerate(itertools.product(*codes)):
        year = int(dimensions[2]["label"][year_code])
        value = data["value"][i] if isinstance(data["value"], list) else data["value"].get(str(i))
        status = data.get("status", {}).get(str(i))
        if value is not None:
            assert isinstance(value, (int, float)) and math.isfinite(value) and value >= 0
        records[(year, region, animal)] = {"value": value, "status": status,
                                          "region": dimensions[1]["label"][region].strip(),
                                          "animal": dimensions[0]["label"][animal].strip()}
    return records


def write_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Vega's CSV loader retains a BOM in the first field name. Use plain UTF-8
    # so year/он is addressable in chart expressions as well as in downloads.
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)


def build_records():
    manifest = read_json(RAW / "manifest.json")
    assert (manifest["loss_year_start"], manifest["loss_year_end"]) == (START, END)
    for kind, table in manifest["tables"].items():
        for lang, info in table["languages"].items():
            source = RAW / f"{kind}-{lang}-data.json"
            assert hashlib.sha256(source.read_bytes()).hexdigest() == info["sha256"], source
    sources = {(kind, lang): decode(kind, lang) for kind in ("losses", "herds") for lang in ("en", "mn")}
    for kind in ("losses", "herds"):
        en, mn = sources[kind, "en"], sources[kind, "mn"]
        assert en.keys() == mn.keys(), f"{kind}: bilingual keys differ"
        assert all(en[k]["value"] == mn[k]["value"] for k in en), f"{kind}: bilingual numbers differ"
    rows = []
    for (year, region, animal), record in sorted(sources["losses", "en"].items()):
        mn = sources["losses", "mn"][year, region, animal]
        herd = sources["herds", "en"].get((year - 1, region, animal), {"value": None, "status": "missing year"})
        loss, opening = record["value"], herd["value"]
        rate = None if loss is None or opening is None or opening <= 0 else round(loss / opening * 100, 6)
        rows.append({"year": year, "region_code": region, "region_en": record["region"], "region_mn": mn["region"],
                     "animal_code": animal, "animal_en": record["animal"], "animal_mn": mn["animal"],
                     "losses_thousand": loss, "starting_herd_thousand": opening, "loss_rate_percent": rate,
                     "loss_status": record["status"], "herd_status": herd["status"]})
    # National totals are independent controls; do not sum mixed hierarchy levels.
    residuals = []
    for year in range(START, END + 1):
        total = next(r["losses_thousand"] for r in rows if r["year"] == year and r["region_code"] == "0" and r["animal_code"] == "0")
        provinces = [r["losses_thousand"] for r in rows if r["year"] == year and r["region_code"] != "0" and r["animal_code"] == "0"]
        assert len(provinces) == 22
        observed = [v for v in provinces if v is not None]
        residuals.append({"year": year, "national_thousand": total, "available_regions": len(observed),
                          "regional_sum_thousand": round(sum(observed), 6),
                          "difference_thousand": None if total is None else round(sum(observed) - total, 6)})
    # Older source rows have only one decimal in thousand head. Rounding of 22
    # regions can differ from the independently rounded national control by 1.15.
    comparable = [r for r in residuals if r["difference_thousand"] is not None]
    assert all(abs(r["difference_thousand"]) <= 1.15 for r in comparable), comparable
    type_residuals = []
    for year in range(START, END + 1):
        national = [r for r in rows if r["year"] == year and r["region_code"] == "0"]
        total = next(r["losses_thousand"] for r in national if r["animal_code"] == "0")
        values = [r["losses_thousand"] for r in national if r["animal_code"] != "0"]
        assert len(values) == 5 and all(v is not None for v in values)
        difference = round(sum(values) - total, 6)
        type_residuals.append({"year": year, "national_thousand": total,
                               "type_sum_thousand": round(sum(values), 6), "difference_thousand": difference,
                               "exceeds_one_decimal_rounding": abs(difference) > 0.3})
    assert len(rows) == (END - START + 1) * 23 * 6
    write_csv(VERSION / "observations.csv", list(rows[0]), [list(r.values()) for r in rows])
    write_json(VERSION / "validation.json", {"observations": len(rows), "bilingual_exact_match": True,
                "missing_losses": sum(r["losses_thousand"] is None for r in rows),
                "missing_starting_herds": sum(r["starting_herd_thousand"] is None for r in rows),
                "missing_rates": sum(r["loss_rate_percent"] is None for r in rows),
                "national_type_reconciliation": type_residuals,
                "national_reconciliation": residuals})
    return rows


def chart_base(description):
    return {"$schema": SCHEMA, "description": description, "config": CONFIG}


def fields(lang, category):
    return ("year", category, "value") if lang == "en" else ("он", "бүс" if category == "region" else "малын_төрөл", "утга")


def csv_data(filename):
    numeric = ["он", "утга"] if filename.endswith("-mn.csv") else ["year", "value"]
    return {"url": f"/datasets/{filename}", "format": {"type": "csv", "parse": {field: "number" for field in numeric}}}


def write_charts(dataset_id, config, lang, year_end, categories, maximum):
    year, category, value = fields(lang, config["category"])
    unit = config[f"unit_{lang}"]
    year_title = "Year" if lang == "en" else "Он"
    region_title = "Aimag / capital" if lang == "en" else "Аймаг, нийслэл"
    chart = chart_base(config[f"excerpt_{lang}"])
    if config["category"] == "region":
        name = "name" if lang == "en" else "name_mn"
        chart.update({"data": csv_data(f"{dataset_id}-{lang}.csv"),
            "description": chart["description"] + " Boundaries: geoBoundaries (ODbL) / OpenStreetMap contributors.",
            "params": [{"name": "selectedYear", "value": year_end, "bind": {"input": "range", "min": START, "max": year_end, "step": 1, "name": year_title + ": "}}],
            "transform": [{"filter": f"datum['{year}'] == selectedYear"},
                {"lookup": category, "from": {"data": {"url": "/maps/mongolia-aimags.json", "format": {"type": "json", "property": "features"}},
                    "key": f"properties.{name}"}, "as": "boundary"},
                {"calculate": f"isValid(datum['{value}']) ? format(datum['{value}'], ',.3f') : " + ("'Unavailable'" if lang == "en" else "'Мэдээлэлгүй'"), "as": "display_value"}],
            "projection": {"type": "mercator"}, "mark": {"type": "geoshape", "stroke": "white", "strokeWidth": 1, "invalid": None},
            "encoding": {"shape": {"field": "boundary", "type": "geojson"},
                "color": {"field": value, "type": "quantitative", "scale": {"scheme": "oranges", "domain": [0, maximum]},
                "condition": {"test": f"!isValid(datum['{value}'])", "value": "#cbd5e1"},
                "legend": {"orient": "top", "title": unit, "format": ",.1f", "titleLimit": 350, "gradientLength": 250}},
                "tooltip": [{"field": category, "type": "nominal", "title": region_title},
                    {"field": year, "type": "quantitative", "title": year_title, "format": "d"},
                    {"field": "display_value", "type": "nominal", "title": unit}]}})
        rank = chart_base(("Six aimags/capital with the highest value in the selected year. All 22 regions are in the downloads."
                           if lang == "en" else "Сонгосон онд хамгийн өндөр үзүүлэлттэй зургаан аймаг, нийслэл. Бүх 22 нутаг дэвсгэрийн мэдээллийг татаж авна."))
        rank.update({"data": csv_data(f"{dataset_id}-{lang}.csv"),
            "params": [{"name": "selectedYear", "value": year_end}],
            "transform": [{"filter": f"datum['{year}'] == selectedYear"},
                          {"filter": f"isValid(datum['{value}'])"},
                          {"window": [{"op": "row_number", "as": "rank"}], "sort": [{"field": value, "order": "descending"}, {"field": category, "order": "ascending"}]},
                          {"filter": "datum.rank <= 6"}],
            "mark": {"type": "bar", "cornerRadiusEnd": 3},
            "encoding": {"y": {"field": category, "type": "nominal", "sort": "-x", "title": None, "axis": {"labelLimit": 150}},
                "x": {"field": value, "type": "quantitative", "title": unit, "scale": {"zero": True}, "axis": {"format": ",.1f"}},
                "tooltip": [{"field": category, "type": "nominal", "title": region_title}, {"field": year, "type": "quantitative", "title": year_title, "format": "d"},
                            {"field": value, "type": "quantitative", "title": unit, "format": ",.3f"}]}})
        write_json(PUBLIC / f"charts/{dataset_id}-ranking-{lang}.json", rank)
    else:
        cat_title = "Animal type" if lang == "en" else "Малын төрөл"
        chart.update({"data": csv_data(f"{dataset_id}-{lang}.csv"),
            "encoding": {"x": {"field": year, "type": "quantitative", "title": year_title,
                "axis": {"format": "d", "grid": False, "values": sorted({START, END, *range(((START + 9) // 10) * 10, END, 10)})},
                "scale": {"zero": False, "nice": False}},
                "y": {"field": value, "type": "quantitative", "title": unit, "scale": {"zero": True}, "axis": {"format": ",.0f"}},
                "color": {"field": category, "type": "nominal", "legend": {"orient": "top", "title": cat_title},
                          "scale": {"domain": categories, "range": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]}}},
            "layer": [{"mark": {"type": "line", "strokeWidth": 2.5}},
                {"params": [{"name": "hover", "select": {"type": "point", "nearest": True, "on": "pointerover", "clear": "pointerout"}}],
                 "mark": {"type": "point", "filled": True, "size": 80},
                 "encoding": {"opacity": {"condition": {"param": "hover", "empty": False, "value": 1}, "value": 0},
                    "tooltip": [{"field": category, "type": "nominal", "title": cat_title}, {"field": year, "type": "quantitative", "title": year_title, "format": "d"},
                                {"field": value, "type": "quantitative", "title": unit, "format": ",.3f"}]}}]})
    write_json(PUBLIC / f"charts/{dataset_id}-{lang}.json", chart)


def write_page(dataset_id, config, lang):
    import yaml
    csv_path = PUBLIC / f"datasets/{dataset_id}-{lang}.csv"
    xlsx_path = PUBLIC / f"datasets/{dataset_id}-{lang}.xlsx"
    def size(path):
        return f"{max(1, math.ceil(path.stat().st_size / 1024))} KB" if path.exists() else "pending"
    table = "DT_NSO_1001_029V1.px"
    fm = {"title": config[f"title_{lang}"], "publishDate": PUBLISHED, "excerpt": config[f"excerpt_{lang}"],
          "category": "Agriculture" if lang == "en" else "Хөдөө аж ахуй",
          "tags": ["mongolia", "livestock", "agriculture", "livestock losses"] if lang == "en" else ["монгол", "мал аж ахуй", "хөдөө аж ахуй", "малын хорогдол"],
          "keywords": ["Mongolia livestock losses", "livestock mortality by aimag", "adult animal losses"] if lang == "en" else ["малын зүй бус хорогдол", "малын хорогдол аймгаар", "том малын хорогдол"],
          "author": "Data.mn", "dataVersion": VERSION_NUMBER, "dataDate": date(END, 12, 31), "excelLanguage": "page",
          "dataFiles": [{"path": f"/datasets/{csv_path.name}", "format": "csv", "size": size(csv_path),
                         "label": "CSV (English)" if lang == "en" else "CSV (Монгол)",
                         "description": "All data, one observation per row. For Excel, import as UTF-8 with a comma delimiter." if lang == "en" else "Бүх өгөгдөл, нэг мөрөнд нэг ажиглалт. Excel-д оруулахдаа UTF-8 кодчилол, таслал тусгаарлагчийг сонгоно уу."},
                        {"path": f"/datasets/{xlsx_path.name}", "format": "xlsx", "size": size(xlsx_path),
                         "label": "Excel (English)" if lang == "en" else "Excel (Монгол)",
                         "description": f"Formatted tables for {START}–{END}, in English." if lang == "en" else f"{START}–{END} оны бүх өгөгдөл, монгол хэлээр."}],
          "source": {"name": "National Statistics Office of Mongolia" if lang == "en" else "Үндэсний Статистикийн Хороо",
                     "url": NSO_PAGE.format(lang=lang, table=table),
                     "tableId": table if config["measure"] != "loss_rate_percent" else table + "; DT_NSO_1001_021V1.px"}}
    is_region = config["category"] == "region"
    caption = ("Adult livestock losses include natural disasters, disease and other causes, and exclude young animals born during the reporting year."
               if lang == "en" else "Том малын зүй бус хорогдолд байгалийн аюулт үзэгдэл, өвчин болон бусад шалтгаан орно. Тайлант онд төрсөн төл малын хорогдлыг оруулаагүй.")
    if config["measure"] == "loss_rate_percent":
        caption = ("Rate = annual adult animal losses ÷ previous year-end livestock × 100. Calculated by Data.mn; all causes combined."
                   if lang == "en" else "Хувь = жилийн том малын зүй бус хорогдол ÷ өмнөх оны эцсийн малын тоо × 100. Data.mn-ээс тооцсон, бүх шалтгааныг хамарсан үзүүлэлт.")
    title = ("Losses across Mongolia" if lang == "en" else "Монгол Улсын малын зүй бус хорогдол") if is_region else config[f"title_{lang}"]
    if config["measure"] == "loss_rate_percent":
        title = "Share of the starting herd lost" if lang == "en" else "Оны эхний малд эзлэх хорогдлын хувь"
    if is_region:
        caption += (" Historical coverage follows NSO region labels; administrative boundaries changed over time. Blank values mean unavailable, not zero."
                    if lang == "en" else " Түүхэн хамрах хүрээ нь ҮСХ-ны нутаг дэвсгэрийн нэршлийг дагана. Засаг захиргааны хил хязгаар хугацааны явцад өөрчлөгдсөн. Хоосон утга нь тэг бус, мэдээлэл байхгүйг илэрхийлнэ.")
        caption += (" Move the year slider to update both charts. Grey means unavailable. The same colour scale is used for every year; the map uses present-day boundaries."
                    if lang == "en" else " Он сонгох гулсагчийг хөдөлгөхөд хоёр график зэрэг шинэчлэгдэнэ. Саарал өнгө нь мэдээлэлгүйг илэрхийлнэ. Бүх онд ижил өнгөний хуваарь, газрын зурагт өнөөгийн хил хязгаарыг ашигласан.")
    else:
        caption += (" In some historical years, the sum of animal types differs from the separately reported national total; source values are preserved."
                    if lang == "en" else " Зарим өмнөх онд малын төрлүүдийн нийлбэр нь тусад нь мэдээлсэн улсын нийт дүнгээс зөрдөг. Эх сурвалжийн утгуудыг хэвээр хадгалсан.")
    body = f"import VegaChart from '~/components/ui/VegaChart.astro';\n\n{config[f'excerpt_{lang}']}\n\n"
    group = f' yearGroup="{dataset_id}"' if is_region else ''
    body += f'<VegaChart spec="/charts/{dataset_id}-{lang}.json" title="{title}" caption="{caption}" aspectRatio={{0.625}}{group} />\n'
    if is_region:
        title = "Highest losses by year" if lang == "en" else "Оноор хамгийн их хорогдолтой нутаг дэвсгэр"
        if config["measure"] == "loss_rate_percent":
            title = "Highest loss rates by year" if lang == "en" else "Оноор хамгийн өндөр хорогдлын хувьтай нутаг дэвсгэр"
        caption = "Use the year slider under the map to compare the top six regions. Downloads contain all 22." if lang == "en" else "Газрын зургийн доорх он сонгох гулсагчаар хамгийн өндөр үзүүлэлттэй зургаан нутаг дэвсгэрийг харьцуулна. Татах файлд бүх 22 нутаг дэвсгэр орсон."
        caption += (" Orkhon losses start in 1976 and Govisumber in 1991; rates also require an available previous-year herd. Unavailable values are omitted from rankings."
                    if lang == "en" else " Орхоны хорогдлын мэдээлэл 1976, Говьсүмбэрийнх 1991 оноос эхэлнэ. Хувийг тооцоход өмнөх оны малын тоо шаардлагатай. Мэдээлэлгүй утгыг эрэмбэд оруулахгүй.")
        body += f'\n<VegaChart spec="/charts/{dataset_id}-ranking-{lang}.json" title="{title}" caption="{caption}" aspectRatio={{0.6}}{group} />\n'
    (ROOT / f"data.mn/src/data/data/{lang}/{dataset_id}.mdx").write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n\n" + body)


def build():
    rows = build_records()
    workbook_payload = []
    for dataset_id, config in DATASETS.items():
        if config["category"] == "region":
            selected = [r for r in rows if r["animal_code"] == "0" and r["region_code"] != "0"]
        else:
            selected = [r for r in rows if r["region_code"] == "0" and r["animal_code"] != "0"]
        payload = {"id": dataset_id, "unit_en": config["unit_en"], "unit_mn": config["unit_mn"], "sheets": []}
        for lang in ("en", "mn"):
            headers = fields(lang, config["category"])
            output = [[r["year"], r[f'{config["category"]}_{lang}'], r[config["measure"]]] for r in selected]
            # Preserve source-code order so bilingual numeric rows align exactly.
            write_csv(PUBLIC / f"datasets/{dataset_id}-{lang}.csv", headers, output)
            if config["category"] == "region":
                write_csv(PUBLIC / f"datasets/{dataset_id}-latest-{lang}.csv", headers, [r for r in output if r[0] == END])
            write_charts(dataset_id, config, lang, END, list(dict.fromkeys(r[1] for r in output)), max(r[2] for r in output if r[2] is not None))
            write_page(dataset_id, config, lang)
            categories = sorted({r[1] for r in output})
            lookup = {(r[0], r[1]): r[2] for r in output}
            matrix = [[headers[0], *categories]] + [[year, *[lookup[year, cat] for cat in categories]] for year in range(START, END + 1)]
            payload["sheets"].append({"name": "English" if lang == "en" else "Монгол", "matrix": matrix})
        workbook_payload.append(payload)
        version = ROOT / f"tools/versions/{dataset_id}/v{VERSION_NUMBER}"
        version.mkdir(parents=True, exist_ok=True)
        for lang in ("en", "mn"):
            (version / f"data-{lang}.csv").write_bytes((PUBLIC / f"datasets/{dataset_id}-{lang}.csv").read_bytes())
        print(dataset_id, len(selected), "rows per language")
    write_json(VERSION / "workbook-input.json", workbook_payload)


if __name__ == "__main__":
    build()
