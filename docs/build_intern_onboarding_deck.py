#!/usr/bin/env python3
"""Build the Data.mn intern onboarding deck (regenerable from live repo data).

Usage:
    .venv/bin/python docs/build_intern_onboarding_deck.py

Output:
    docs/data-mn-intern-onboarding.pptx

Numbers (registry stats, ebarilga counts) are read live from tools/registry
and tools/sources/ebarilga, so re-running refreshes the deck. All other
examples are fixed excerpts from real repo files (see SOURCES below).
"""
import csv
import os
import sqlite3
from datetime import date

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "data-mn-intern-onboarding.pptx")

BLUE = RGBColor(0x1F, 0x77, 0xB4)
DARK = RGBColor(0x1F, 0x29, 0x37)
GRAY = RGBColor(0x6B, 0x72, 0x80)
LIGHT = RGBColor(0xF3, 0xF4, 0xF6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x16, 0x65, 0x2B)
RED = RGBColor(0xB9, 0x1C, 0x1C)


def live_stats():
    c = sqlite3.connect(os.path.join(ROOT, "tools", "registry", "data.db"))
    n_src = c.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    n_ds = c.execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
    n_pub = c.execute("SELECT COUNT(*) FROM datasets WHERE is_published=1").fetchone()[0]
    n_par = c.execute("SELECT COUNT(*) FROM datasets WHERE is_parent=1").fetchone()[0]
    n_eb = c.execute("SELECT COUNT(*) FROM datasets WHERE source_id='ebarilga'").fetchone()[0]
    eb_feats = 0
    for code in ("built_building",):
        import json as _j
        m = _j.load(open(os.path.join(
            ROOT, "tools", "sources", "ebarilga", "raw",
            f"ebarilga-{code}.meta.json"), encoding="utf-8"))
        eb_feats = m.get("features", 0)
    return {"sources": n_src, "datasets": n_ds, "published": n_pub,
            "parents": n_par, "ebarilga": n_eb, "footprints": eb_feats,
            "date": date.today().isoformat()}


# ---------------------------------------------------------------- helpers

def new_slide(prs, title, subtitle=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                                 prs.slide_width, Inches(1.05))
    bar.fill.solid()
    bar.fill.fore_color.rgb = BLUE
    bar.line.fill.background()
    tf = bar.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title
    r.font.size = Pt(30)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = "Calibri"
    tf.margin_left = Inches(0.4)
    tf.vertical_anchor = 1  # middle
    if subtitle:
        tb = slide.shapes.add_textbox(Inches(0.5), Inches(1.15),
                                      Inches(12.3), Inches(0.5))
        p = tb.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = subtitle
        r.font.size = Pt(16)
        r.font.italic = True
        r.font.color.rgb = GRAY
        r.font.name = "Calibri"
    foot = slide.shapes.add_textbox(Inches(0.5), Inches(7.05),
                                    Inches(12.3), Inches(0.35))
    p = foot.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    r = p.add_run()
    r.text = "Data.mn intern onboarding"
    r.font.size = Pt(10)
    r.font.color.rgb = GRAY
    r.font.name = "Calibri"
    return slide


def bullets(slide, left, top, width, height, items, size=18, gap=6):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        if isinstance(item, str):
            item = [(item, {})]
        p.level = 0
        first = True
        for text, fmt in item:
            r = p.add_run() if not first else p.add_run()
            first = False
            r.text = text
            r.font.size = Pt(fmt.get("size", size))
            r.font.bold = fmt.get("bold", False)
            r.font.italic = fmt.get("italic", False)
            r.font.color.rgb = fmt.get("color", DARK)
            r.font.name = fmt.get("font", "Calibri")
    return tb


def code_box(slide, left, top, width, height, text, size=11):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                 left, top, width, height)
    box.fill.solid()
    box.fill.fore_color.rgb = LIGHT
    box.line.fill.background()
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.15)
    tf.margin_right = Inches(0.15)
    tf.margin_top = Inches(0.08)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.name = "Consolas"
    r.font.color.rgb = DARK
    return box


def style_cell(cell, text, size=13, bold=False, color=DARK, fill=None,
               align=PP_ALIGN.LEFT):
    cell.fill.background()
    if fill is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
    cell.margin_left = Inches(0.08)
    cell.margin_right = Inches(0.08)
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = str(text)
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = "Calibri"


def table_slide(prs, title, subtitle, headers, rows, widths=None, size=13):
    slide = new_slide(prs, title, subtitle)
    nrows, ncols = len(rows) + 1, len(headers)
    left, top, width = Inches(0.5), Inches(1.8), Inches(12.33)
    height = Inches(min(0.45 + 0.45 * len(rows), 5.0))
    gf = slide.shapes.add_table(nrows, ncols, left, top, width, height)
    table = gf.table
    if widths:
        for i, w in enumerate(widths):
            table.columns[i].width = Inches(w)
    for j, h in enumerate(headers):
        style_cell(table.cell(0, j), h, size=size, bold=True,
                   color=WHITE, fill=BLUE)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            fill = RGBColor(0xE8, 0xF1, 0xFA) if i % 2 == 0 else WHITE
            style_cell(table.cell(i + 1, j), val, size=size, fill=fill)
    return slide


def flow_box(slide, left, top, width, height, text, size=12, fill=WHITE,
             border=BLUE, bold=False):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                 left, top, width, height)
    box.fill.solid()
    box.fill.fore_color.rgb = fill
    box.line.color.rgb = border
    box.line.width = Pt(2)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = 1
    for para, first in ((tf.paragraphs[0], True),):
        para.alignment = PP_ALIGN.CENTER
        r = para.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = DARK
        r.font.name = "Calibri"
    return box


def arrow_right(slide, left, top, width=Inches(0.35), height=Inches(0.3)):
    a = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, left, top, width, height)
    a.fill.solid()
    a.fill.fore_color.rgb = BLUE
    a.line.fill.background()
    return a


def arrow_down(slide, left, top, width=Inches(0.3), height=Inches(0.35)):
    a = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, left, top, width, height)
    a.fill.solid()
    a.fill.fore_color.rgb = BLUE
    a.line.fill.background()
    return a


# ---------------------------------------------------------------- slides 1-8

def s01_title(prs, st):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                                prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BLUE
    bg.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(3.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Data.mn intern onboarding"
    r.font.size = Pt(54)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = "Calibri"
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(12)
    r = p.add_run()
    r.text = "How the system works, and how you ship your first dataset"
    r.font.size = Pt(24)
    r.font.color.rgb = WHITE
    r.font.name = "Calibri"
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(24)
    r = p.add_run()
    r.text = f"Mongolia's open data platform  •  {st['date']}"
    r.font.size = Pt(18)
    r.font.color.rgb = WHITE
    r.font.name = "Calibri"
    return slide


def s02_what(prs, st):
    slide = new_slide(prs, "What is data.mn?",
                      "Mission: collect all publicly available data on Mongolia "
                      "that is up-to-date and relevant — and make it accessible.")
    bullets(slide, Inches(0.5), Inches(1.8), Inches(5.5), Inches(5.0), [
        [("One focused dataset page per story ", {"bold": True}),
         ("(Statista-style), not raw data dumps.", {})],
        [("Fully bilingual: ", {"bold": True}),
         ("every dataset ships EN + MN data, charts, and pages.", {})],
        [("Citable forever: ", {"bold": True}),
         ("published URLs never break — papers and reports link here.", {})],
        [("Open process: ", {"bold": True}),
         ("you add datasets through GitHub PRs, with AI agents doing the heavy lifting.", {})],
    ], size=19)
    # audience table on the right half
    gf = slide.shapes.add_table(7, 2, Inches(6.5), Inches(1.8),
                                Inches(6.3), Inches(4.9))
    t = gf.table
    t.columns[0].width = Inches(2.2)
    t.columns[1].width = Inches(4.1)
    style_cell(t.cell(0, 0), "Audience", bold=True, color=WHITE, fill=BLUE)
    style_cell(t.cell(0, 1), "What they need", bold=True, color=WHITE, fill=BLUE)
    rows = [("General public", "Easy facts, simple visuals"),
            ("Researchers", "Downloads, methods, history"),
            ("Government", "Current stats, comparisons"),
            ("Intl. orgs", "Standardized data in English"),
            ("Journalists", "Quick facts, citable charts"),
            ("Businesses", "Market and economic trends")]
    for i, (a, b) in enumerate(rows):
        fill = RGBColor(0xE8, 0xF1, 0xFA) if i % 2 == 0 else WHITE
        style_cell(t.cell(i + 1, 0), a, size=14, bold=True, fill=fill)
        style_cell(t.cell(i + 1, 1), b, size=14, fill=fill)
    return slide


def s03_anatomy(prs, st):
    slide = new_slide(prs, "Anatomy of a dataset page",
                      "Example: Ulaanbaatar Apartment Prices (apartment-prices-ulaanbaatar)")
    items = ["Chart at top (interactive Vega-Lite, EN or MN labels)",
             "Download buttons: CSV + Excel, in your language",
             "Methodology + source link (NSO table DT_NSO_0300_00V4.px)",
             "One URL per language, permanent forever",
             "Behind it: 8 files you will create (we'll get there)"]
    bullets(slide, Inches(0.5), Inches(1.8), Inches(6.0), Inches(5.0),
            [[(t, {})] for t in items], size=19)
    code_box(slide, Inches(7.0), Inches(1.8), Inches(5.8), Inches(5.0),
             "data.mn/en/data/apartment-prices-ulaanbaatar\n"
             "data.mn/mn/data/apartment-prices-ulaanbaatar\n\n"
             "Monthly average price per sqm, new vs old\n"
             "apartments, 2022-2026.\n\n"
             "Old apts peaked at 5.06M MNT/sqm\n"
             "in December 2025.\n\n"
             "(excerpt from the live page)", size=13)
    return slide


def s04_numbers(prs, st):
    return table_slide(
        prs, "Data.mn by the numbers", f"Live from the registry ({st['date']})",
        ["Count", "Metric", "What it means"],
        [[str(st["sources"]), "sources", "NSO, MRPAM, MongolBank, eBarilga"],
         [str(st["datasets"]), "datasets tracked", "Registry rows (parents + splits)"],
         [str(st["published"]), "published", "Live pages with permanent URLs"],
         [str(st["parents"]), "parents", "Raw datasets; splits are built from these"],
         ["2", "languages", "Every dataset ships EN + MN"],
         [str(st["ebarilga"]), "ebarilga parents", "UB geoportal layers incl. "
          f"{st['footprints']:,} building footprints"]],
        widths=[2.2, 3.0, 7.1], size=16)


def s05_repomap(prs, st):
    slide = new_slide(prs, "Repo map: where everything lives",
                      "One repo, four neighborhoods (+2 guidebooks)")
    boxes = [(".claude/\nagents, commands,\nskills", "AI playbooks"),
             ("data.mn/\nAstro website", "EN/MN pages,\nCSV/XLSX,\ncharts"),
             ("tools/\nregistry, sources,\nscripts, versions", "Python ops +\nSQLite brain"),
             ("docs/\nvision, principles,\nthis deck", "Why we do\nthings this way")]
    x = Inches(0.5)
    for title, sub in boxes:
        flow_box(slide, x, Inches(2.0), Inches(2.7), Inches(2.2),
                 title + "\n— " + sub, size=14, bold=False)
        x += Inches(3.05)
    flow_box(slide, Inches(0.5), Inches(4.7), Inches(5.9), Inches(1.6),
             "AGENTS.md — instructions every AI agent reads",
             size=15, fill=LIGHT)
    flow_box(slide, Inches(6.9), Inches(4.7), Inches(5.9), Inches(1.6),
             "CONTRIBUTING.md — your human onboarding guide",
             size=15, fill=LIGHT)
    return slide


def s06_lifecycle(prs, st):
    slide = new_slide(prs, "The data lifecycle",
                      "Every dataset travels this pipeline. Your PRs live in the middle.")
    stages = ["1. Source\n(API/PDF/WFS)", "2. Raw pull\ntools/sources/", "3. Parent\nregistry row",
              "4. Splits\nfocused CSVs", "5. Bilingual\nEN + MN"]
    x = Inches(0.4)
    y = Inches(1.9)
    for i, s in enumerate(stages):
        flow_box(slide, x, y, Inches(2.15), Inches(1.5), s, size=13, bold=True)
        if i < 4:
            arrow_right(slide, x + Inches(2.2), y + Inches(0.6))
        x += Inches(2.62)
    stages2 = ["6. Chart + MDX\nVega + pages", "7. Validate\n5 gates must pass",
               "8. PR + review\nGitHub", "9. Publish\npermanent URL"]
    x = Inches(1.7)
    y = Inches(4.2)
    for i, s in enumerate(stages2):
        fill = RGBColor(0xE8, 0xF1, 0xFA) if i < 3 else RGBColor(0xDC, 0xFC, 0xE7)
        flow_box(slide, x, y, Inches(2.15), Inches(1.5), s, size=13,
                 bold=True, fill=fill)
        if i < 3:
            arrow_right(slide, x + Inches(2.2), y + Inches(0.6))
        x += Inches(2.62)
    bullets(slide, Inches(0.5), Inches(6.0), Inches(12.3), Inches(0.9),
            [[("You + your AI agent do stages 2–7. Robert publishes (stage 9).", {})]],
            size=15)
    return slide


def s07_sources(prs, st):
    slide = table_slide(
        prs, "Concept 1 of 7: sources", "Each source = one folder under tools/sources/",
        ["Source", "ID", "Type", "Example content"],
        [["National Statistics Office", "nso-1212", "REST API (1,135 tables)",
          "GDP, poverty, teachers, wages"],
         ["Mineral Resources Authority", "mrpam", "PDF reports (MN-only)",
          "Coal, mining output"],
         ["Bank of Mongolia", "mongolbank", "Mixed EN/MN",
          "Exchange + policy rates, M2"],
         ["eBarilga Geoportal", "ebarilga", "WFS geo API (80 layers)",
          "Buildings, schools, permits"]],
        widths=[3.2, 2.0, 3.3, 3.8], size=14)
    code_box(slide, Inches(0.5), Inches(5.3), Inches(12.33), Inches(1.5),
             "tools/sources/nso-1212/  source.md  (how to use the API)  +  "
             "datasets/*.md  (one recipe per dataset)",
             size=13)
    return slide


def s08_registry(prs, st):
    slide = new_slide(prs, "Concept 2 of 7: the registry (SQLite brain)",
                      "tools/registry/data.db — every dataset's status, versions, and URLs")
    code_box(slide, Inches(0.5), Inches(1.8), Inches(6.0), Inches(4.9),
             "cd tools\n"
             "python -m registry status          # dashboard\n"
             "python -m registry sources         # 4 sources\n"
             "python -m registry list            # all datasets\n"
             "python -m registry list --source ebarilga\n"
             "python -m registry info gdp-nominal\n"
             "python -m registry published       # live URLs",
             size=13)
    code_box(slide, Inches(7.0), Inches(1.8), Inches(5.8), Inches(4.9),
             "Dataset: nso-gdp-by-economic-activity\n"
             "  Status: active / Version: 2\n"
             "  Type: Parent (has splits)\n"
             "  Splits (6): gdp-nominal, gdp-real,\n"
             "    gdp-usd, gdp-growth-rate,\n"
             "    gdp-by-sector, gdp-sector-trends\n\n"
             "(real `registry info` output)",
             size=13)
    return slide

def s09_parentsplit(prs, st):
    slide = new_slide(prs, "Concept 3 of 7: parents and splits",
                      "One messy reality → many clean stories. Real example: GDP.")
    flow_box(slide, Inches(0.5), Inches(3.2), Inches(3.2), Inches(1.6),
             "PARENT (raw, never published)\nnso-gdp-by-economic-activity",
             size=13, bold=True, fill=RGBColor(0xE8, 0xF1, 0xFA))
    splits = ["gdp-nominal", "gdp-real", "gdp-usd",
              "gdp-growth-rate", "gdp-by-sector", "gdp-sector-trends"]
    y = Inches(1.7)
    for s in splits:
        flow_box(slide, Inches(5.6), y, Inches(3.4), Inches(0.62),
                 "SPLIT (published): " + s, size=12)
        y += Inches(0.78)
    code_box(slide, Inches(9.5), Inches(1.8), Inches(3.3), Inches(4.9),
             "Rules:\n\n"
             "- Parent holds ALL\n  dimensions\n"
             "- Each split = ONE story\n"
             "- Splits get parent_id +\n  split_filter in registry\n"
             "- Parent updates → splits\n  regenerate",
             size=13)
    return slide


def s10_bilingual(prs, st):
    slide = new_slide(prs, "Concept 4 of 7: bilingual everything",
                      "Real CSV heads: apartment-prices-ulaanbaatar-en.csv vs -mn.csv")
    code_box(slide, Inches(0.5), Inches(1.8), Inches(5.9), Inches(3.2),
             "indicator,month,price_million_mnt_per_sqm\n"
             "Average price of new apartment,2022-02,3.08\n"
             "Average price of old apartment,2022-02,2.94",
             size=11)
    code_box(slide, Inches(6.9), Inches(1.8), Inches(5.9), Inches(3.2),
             "үзүүлэлт,сар,үнэ_сая_төг_м_кв\n"
             "Шинэ орон сууцны дундаж үнэ,2022-02,3.08\n"
             "Хуучин орон сууцны дундаж үнэ,2022-02,2.94",
             size=11)
    bullets(slide, Inches(0.5), Inches(5.2), Inches(12.3), Inches(1.6), [
        [("Same rows, identical numbers — only labels translate. ", {"bold": True}),
         ("EN/MN numeric mismatch is the #1 PR blocker.", {})],
        [("MN-only source (MRPAM, eBarilga)? Translate with ", {}),
         ("tools/scripts/translate_csv.py.", {"font": "Consolas"})],
    ], size=16)
    return slide


def s11_charts(prs, st):
    slide = new_slide(prs, "Concept 5 of 7: charts (Vega-Lite JSON)",
                      "116 lines for apartments — here's the shape of it")
    code_box(slide, Inches(0.5), Inches(1.8), Inches(6.3), Inches(4.9),
             '{\n'
             '  "$schema": ".../vega-lite/v5.json",\n'
             '  "data": { "url": "/datasets/\n'
             '    apartment-prices-ulaanbaatar-en.csv" },\n'
             '  "encoding": {\n'
             '    "x": { "field": "month",\n'
             '           "type": "temporal" },\n'
             '    "y": { "field": "price_million_mnt_per_sqm",\n'
             '           "type": "quantitative" }\n'
             '  }\n'
             '}',
             size=12)
    bullets(slide, Inches(7.3), Inches(1.8), Inches(5.5), Inches(4.9), [
        [("No width/height ", {"bold": True}), ("— the site handles sizing.", {})],
        [("Time is ", {}), ("temporal or quantitative, never ordinal.", {"bold": True})],
        [("No explicit colors ", {"bold": True}), ("— category10 auto-applies.", {})],
        [("Always validate:", {}), ],
        [("  validate_vega.py --all", {"font": "Consolas"})],
    ], size=17)
    return slide


def s12_mdx(prs, st):
    slide = new_slide(prs, "Concept 6 of 7: MDX pages (one per language)",
                      "Frontmatter = metadata contract. Real apartment frontmatter:")
    code_box(slide, Inches(0.5), Inches(1.8), Inches(7.3), Inches(4.9),
             '---\n'
             'title: "Ulaanbaatar Apartment Prices per sqm ..."\n'
             'category: "Prices & Inflation"\n'
             'dataVersion: 2      # bump on every data change\n'
             'dataFiles:\n'
             '  - path: "/datasets/apartment-...-en.csv"\n'
             '  - path: "/datasets/apartment-....xlsx"\n'
             'source:\n'
             '  name: "National Statistics Office of Mongolia"\n'
             '  tableId: "DT_NSO_0300_00V4.px"\n'
             '---\n'
             '<VegaChart spec="/charts/apartment-...-en.json" />',
             size=11)
    bullets(slide, Inches(8.3), Inches(1.8), Inches(4.5), Inches(4.9), [
        [("dataFiles must exist", {"bold": True}), (" — validator checks.", {})],
        [("EN page → -en files", {"bold": True}), (" only. Same for MN.", {})],
        [("Bump dataVersion", {"bold": True}), (" on every update.", {})],
    ], size=17)
    return slide


def s13_urls(prs, st):
    slide = new_slide(prs, "Concept 7 of 7: versions + frozen URLs",
                      '"Cool URIs don\'t change" — papers and reports cite these links')
    code_box(slide, Inches(0.5), Inches(1.8), Inches(5.5), Inches(2.6),
             "tools/versions/apartment-prices-ulaanbaatar/\n"
             "  v1/   (first release)\n"
             "  v2/   (Sept 2026 refresh)\n\n"
             "Every version kept. Diff on update.",
             size=13)
    bullets(slide, Inches(6.5), Inches(1.8), Inches(6.3), Inches(2.6), [
        [("✅ Add datasets, update data", {"color": GREEN})],
        [("❌ Never delete published data", {"color": RED})],
        [("❌ Never change a URL — ", {"color": RED}),
         ("registry rename ", {"font": "Consolas"}), ("makes a redirect", {})],
        [("Publish = permanent: ", {"bold": True}),
         ("registry publish ", {"font": "Consolas"}), ("assigns the URL.", {})],
    ], size=17)
    bullets(slide, Inches(0.5), Inches(4.8), Inches(12.3), Inches(1.6),
            [[("Rule of thumb: if a URL ever went live, it must work forever. "
               "Deprecate, don't delete.", {"italic": True})]], size=16)
    return slide


def s14_ebarilga(prs, st):
    slide = new_slide(prs, "Worked example: the eBarilga geoportal pulls",
                      "The full pipeline you just learned — executed last week")
    gf = slide.shapes.add_table(6, 3, Inches(0.5), Inches(1.8),
                                Inches(7.3), Inches(4.9))
    t = gf.table
    t.columns[0].width = Inches(2.4)
    t.columns[1].width = Inches(1.7)
    t.columns[2].width = Inches(3.2)
    for j, h in enumerate(["Stage", "Result", "Artifact"]):
        style_cell(t.cell(0, j), h, bold=True, color=WHITE, fill=BLUE, size=13)
    import glob as _g
    import json as _j
    tot = 0
    for m in _g.glob(os.path.join(ROOT, "tools", "sources", "ebarilga",
                                  "raw", "ebarilga-*.meta.json")):
        tot += _j.load(open(m, encoding="utf-8")).get("features", 0)
    rows = [("Skill built", "query + fetch", ".claude/skills/...ebarilga/"),
            ("Raw pulls", "75 layers", "tools/sources/ebarilga/raw/"),
            ("Features", f"{tot:,}", f"{st['footprints']:,} = footprints"),
            ("Derived joins", "3 CSVs", "counts by district/khoroo/ZIP"),
            ("Parents", "76 rows", "registry + datasets/*.md")]
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            fill = RGBColor(0xE8, 0xF1, 0xFA) if i % 2 == 0 else WHITE
            style_cell(t.cell(i + 1, j), val, size=13, fill=fill)
    bullets(slide, Inches(8.3), Inches(1.8), Inches(4.5), Inches(4.9), [
        [("Server quirks found + fixed:", {"bold": True})],
        [("• startIndex ignored → keyset paging", {})],
        [("• 12 poison features → auto-skip", {})],
        [("• 500s on big pages → halve/retry", {})],
        [("Your splits build on the 76 parents.", {"italic": True})],
        [("e.g. ebarilga-secondary-schools", {"font": "Consolas", "size": 12})],
    ], size=15)
    return slide


def s15_task(prs, st):
    slide = new_slide(prs, "Your job: anatomy of an intern task",
                      "Real task format (from docs/intern-tasks-2026-03-02.md)")
    code_box(slide, Inches(0.5), Inches(1.8), Inches(7.3), Inches(4.9),
             "Poverty rate (carryover)\n\n"
             "  Source:   NSO 1212.mn\n"
             "  Task:     Add national poverty rate with\n"
             "            urban/rural split if available\n"
             "  Branch:   add/poverty-rate\n"
             "  Expected: poverty-rate-national,\n"
             "            poverty-rate-urban-rural\n\n"
             "You get: topic + branch + expected IDs.\n"
             "You deliver: a PR per dataset.",
             size=13)
    bullets(slide, Inches(8.3), Inches(1.8), Inches(4.5), Inches(4.9), [
        [("One dataset per PR", {"bold": True}), (" (skills excepted).", {})],
        [("Branch names: ", {}),
         ("add/<dataset>, feat/<skill>", {"font": "Consolas"})],
        [("Sync + rebase", {"bold": True}), (" before final push.", {})],
        [("Coverage note in PR:", {}), (" what + source URL.", {})],
    ], size=16)
    return slide


def s16_prflow(prs, st):
    slide = new_slide(prs, "The PR workflow you'll run every time", "")
    steps = ["1. Sync\nmain", "2. Branch\nadd/...", "3. Work\n+ agent",
             "4. Validate\ngates pass", "5. Commit\nclear msg",
             "6. Push + PR\ngh pr create"]
    x = Inches(0.35)
    y = Inches(2.4)
    for i, s in enumerate(steps):
        flow_box(slide, x, y, Inches(1.75), Inches(1.5), s, size=12, bold=True)
        if i < 5:
            arrow_right(slide, x + Inches(1.78), y + Inches(0.6),
                        width=Inches(0.3))
        x += Inches(2.13)
    flow_box(slide, Inches(4.6), Inches(4.7), Inches(4.1), Inches(1.3),
             "7. Review → address feedback → merged!",
             size=14, bold=True, fill=RGBColor(0xDC, 0xFC, 0xE7))
    return slide

def s17_agents(prs, st):
    slide = new_slide(prs, "Working with AI agents",
                      "The repo teaches your agent. Your job: direct, verify, commit.")
    gf = slide.shapes.add_table(5, 3, Inches(0.5), Inches(1.8),
                                Inches(7.3), Inches(3.6))
    t = gf.table
    t.columns[0].width = Inches(2.2)
    t.columns[1].width = Inches(2.0)
    t.columns[2].width = Inches(3.1)
    for j, h in enumerate(["Command", "Does", "You say"]):
        style_cell(t.cell(0, j), h, bold=True, color=WHITE, fill=BLUE, size=13)
    rows = [("/data-add", "New dataset", '"poverty rate by age, NSO"'),
            ("/data-update", "Refresh data", '"update exchange rates"'),
            ("/data-status", "Dashboard", '"what needs updating?"'),
            ("/data-validate", "Run gates", "before every PR")]
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            fill = RGBColor(0xE8, 0xF1, 0xFA) if i % 2 == 0 else WHITE
            style_cell(t.cell(i + 1, j), val, size=13, fill=fill)
    bullets(slide, Inches(8.3), Inches(1.8), Inches(4.5), Inches(5.0), [
        [("Claude Code: ", {"bold": True}), ("skills + /commands auto-load.", {})],
        [("Codex / Muse: ", {"bold": True}),
         ("same repo, no auto-skills — point them at AGENTS.md + source.md + registry CLI.", {})],
        [("Golden rule: ", {"bold": True}),
         ("be specific, review every diff, never commit blind.", {})],
    ], size=15)
    return slide


def s18_gate(prs, st):
    slide = new_slide(prs, "The validation gate (run before EVERY PR)",
                      "Real gate from docs/intern-tasks-2026-03-02.md — all green or no PR")
    code_box(slide, Inches(0.5), Inches(1.8), Inches(7.6), Inches(4.9),
             "python tools/tests/run_all_checks.py <id>\n"
             "python tools/scripts/validate_dataset.py \\\n"
             "    --all <id> --base-dir data.mn     # 15/15\n"
             "python tools/scripts/validate_vega.py \\\n"
             "    data.mn/public/charts/<id>-en.json\n"
             "... same for -mn.json ...\n"
             "python tools/scripts/validate_mdx_datafiles.py\n"
             "cd data.mn && npm run build && npm run check",
             size=11)
    bullets(slide, Inches(8.6), Inches(1.8), Inches(4.2), Inches(4.9), [
        [("Hard fails:", {"bold": True, "color": RED})],
        [("• EN/MN numeric mismatch", {})],
        [("• XLSX not wide-form", {})],
        [("• Missing EN/MN files", {})],
        [("• Build breaks", {})],
    ], size=16)
    return slide


def s19_done(prs, st):
    return table_slide(
        prs, '"Done" = 8 files + 1 registry row',
        "Apartment example — your PR should look exactly like this",
        ["#", "File", "Purpose"],
        [["1-2", "…-en.csv / …-mn.csv", "Bilingual data (identical numbers)"],
         ["3", "….xlsx", "Generic Excel download (wide-form)"],
         ["4-5", "…-en.json / …-mn.json", "Vega-Lite chart specs"],
         ["6-7", "en/….mdx / mn/….mdx", "Dataset pages"],
         ["8", "registry row", "Status, version, definition link"]],
        widths=[1.0, 5.2, 6.1], size=15)


def s20_mistakes(prs, st):
    return table_slide(
        prs, "Mistakes that blocked real PRs",
        "From the Dec 2024 postmortem + intern history — don't repeat these",
        ["Mistake", "Why it fails", "Fix"],
        [["Whitespace in CSV values", '" Ulaanbaatar" ≠ "Ulaanbaatar"',
          "Strip; validator now errors"],
         ["Chart without -en/-mn suffix", "Language mismatch undetectable",
          "Always <id>-en.json + -mn.json"],
         ["Extra files in datasets/", "Stale/raw files leak to site",
          "Only ship the 8 + xlsx"],
         ["EN/MN numbers differ", "Two truths = no truth",
          "Translate labels, never numbers"],
         ["Stale branch", "Merge conflicts, old data",
          "Sync + rebase before push"]],
        widths=[3.4, 4.2, 4.7], size=13)


def s21_translate(prs, st):
    slide = new_slide(prs, "Translation workflow (MN-only sources)",
                      "MRPAM, eBarilga, and friends arrive in Mongolian only")
    steps = ["1. Fetch MN\nsave -mn.csv", "2. translate_csv.py\n--from mn --to en",
             "3. Validate\nsame shape +\nidentical numbers", "4. Save both\n-mn.csv +\n-en.csv"]
    x = Inches(0.6)
    y = Inches(2.5)
    for i, s in enumerate(steps):
        flow_box(slide, x, y, Inches(2.5), Inches(1.7), s, size=13, bold=True)
        if i < 3:
            arrow_right(slide, x + Inches(2.55), y + Inches(0.7))
        x += Inches(3.05)
    bullets(slide, Inches(0.5), Inches(4.8), Inches(12.3), Inches(1.6),
            [[("Full guide: ", {}), ("tools/TRANSLATION_GUIDE.md",
                                     {"font": "Consolas"})]], size=16)
    return slide


def s22_cheatsheet(prs, st):
    return table_slide(
        prs, "Cheat sheet: where things live", "Tape this to your wall",
        ["Need...", "Go to"],
        [["Dataset definitions", "tools/sources/<id>/datasets/*.md"],
         ["Raw pulls", "tools/sources/<id>/raw/"],
         ["Version history", "tools/versions/<dataset-id>/"],
         ["MDX pages", "data.mn/src/data/data/{en,mn}/"],
         ["CSV/XLSX downloads", "data.mn/public/datasets/"],
         ["Chart specs", "data.mn/public/charts/"],
         ["Validators", "tools/scripts/validate_*.py + tools/tests/"],
         ["Principles", "docs/principles/ (URLs, categories)"]],
        widths=[3.5, 8.8], size=14)


def s23_help(prs, st):
    slide = new_slide(prs, "Getting unstuck", "Read in this order")
    bullets(slide, Inches(0.5), Inches(1.8), Inches(12.3), Inches(5.0), [
        [("1. An existing dataset ", {"bold": True}),
         ("— copy the shape of apartment-prices-ulaanbaatar.", {})],
        [("2. The dataset's source.md + datasets/*.md ", {"bold": True}),
         ("— the recipe.", {})],
        [("3. AGENTS.md + CONTRIBUTING.md ", {"bold": True}),
         ("— process + commands.", {})],
        [("4. Your AI agent ", {"bold": True}),
         ("— paste the error, ask for the fix, review the diff.", {})],
        [("5. Robert ", {"bold": True}),
         ("— when docs + agent disagree, or before anything irreversible (publish/rename).", {})],
    ], size=19)
    return slide


def s24_firstweek(prs, st):
    slide = new_slide(prs, "Your first week", "Definition of done for week one")
    bullets(slide, Inches(0.5), Inches(1.8), Inches(12.3), Inches(4.2), [
        [("☐ Environment green: ", {"bold": True}),
         ("conda env + npm install + registry status + dev server.", {})],
        [("☐ Read one dataset end-to-end: ", {"bold": True}),
         ("MDX + CSVs + chart + registry row for apartments.", {})],
        [("☐ Reproduce one fetch: ", {"bold": True}),
         ("re-pull any ebarilga layer to /tmp with the skill commands.", {})],
        [("☐ Ship a split PR: ", {"bold": True}),
         ("pick an ebarilga parent, build one bilingual split, pass all gates.", {})],
    ], size=19)
    bullets(slide, Inches(0.5), Inches(5.6), Inches(12.3), Inches(1.2),
            [[("Questions? Good — that's the job. Welcome to data.mn. 🇲🇳", {})]],
            size=20)
    return slide


SLIDES = [s01_title, s02_what, s03_anatomy, s04_numbers, s05_repomap,
          s06_lifecycle, s07_sources, s08_registry, s09_parentsplit,
          s10_bilingual, s11_charts, s12_mdx, s13_urls, s14_ebarilga,
          s15_task, s16_prflow, s17_agents, s18_gate, s19_done,
          s20_mistakes, s21_translate, s22_cheatsheet, s23_help,
          s24_firstweek]


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    st = live_stats()
    for fn in SLIDES:
        fn(prs, st)
    prs.save(OUT)
    print(f"saved {OUT} ({len(SLIDES)} slides)")


if __name__ == "__main__":
    main()

