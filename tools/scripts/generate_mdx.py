#!/usr/bin/env python3
"""Generate matching English and Mongolian data pages.

The chart and downloadable CSVs are language-specific. One XLSX workbook is
shared by both pages.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import yaml


SOURCE_DEFAULTS = {
    "nso-1212": (
        "National Statistics Office of Mongolia",
        "Үндэсний Статистикийн Хороо",
        "https://data.1212.mn",
    ),
    "mongolbank": ("Bank of Mongolia", "Монголбанк", "https://www.mongolbank.mn"),
    "mrpam": (
        "Mineral Resources and Petroleum Authority",
        "Ашигт малтмал, газрын тосны газар",
        "https://mrpam.gov.mn",
    ),
}


def format_size(path: Path) -> str:
    size = path.stat().st_size
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{round(size / 1024)} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def render_frontmatter(values: dict) -> str:
    return yaml.safe_dump(
        values,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=1000,
    ).strip()


def generate_mdx_pages(
    *,
    dataset_id: str,
    title_en: str,
    title_mn: str,
    excerpt_en: str,
    excerpt_mn: str,
    category_en: str,
    category_mn: str,
    tags_en: list[str],
    tags_mn: list[str],
    keywords_en: list[str],
    keywords_mn: list[str],
    source_id: str,
    source_table_id: str,
    base_dir: Path,
    publish_date: str,
    data_date: str,
    version: int,
    chart_title_en: str | None = None,
    chart_title_mn: str | None = None,
) -> tuple[Path, Path]:
    if len(excerpt_en) < 50 or len(excerpt_mn) < 50:
        raise ValueError("Both excerpts must be at least 50 characters")
    if len(keywords_en) < 2 or len(keywords_mn) < 2:
        raise ValueError("Both languages require at least two keywords")
    if source_id not in SOURCE_DEFAULTS:
        raise ValueError(f"Unknown source ID: {source_id}")

    source_name_en, source_name_mn, source_url = SOURCE_DEFAULTS[source_id]
    dataset_dir = base_dir / "public" / "datasets"
    full_en = dataset_dir / f"{dataset_id}-all-en.csv"
    full_mn = dataset_dir / f"{dataset_id}-all-mn.csv"
    xlsx = dataset_dir / f"{dataset_id}.xlsx"
    for path in (full_en, full_mn, xlsx):
        if not path.exists():
            raise FileNotFoundError(path)

    common = {
        "publishDate": date.fromisoformat(publish_date),
        "author": "Data.mn",
        "dataVersion": version,
        "dataDate": date.fromisoformat(data_date),
    }
    en = {
        "title": title_en,
        **common,
        "excerpt": excerpt_en,
        "category": category_en,
        "tags": tags_en,
        "keywords": keywords_en,
        "dataFiles": [
            {
                "path": f"/datasets/{dataset_id}-all-en.csv",
                "format": "csv",
                "size": format_size(full_en),
                "description": "Download as CSV (all data)",
            },
            {
                "path": f"/datasets/{dataset_id}.xlsx",
                "format": "xlsx",
                "size": format_size(xlsx),
                "description": "Open in Excel",
            },
        ],
        "source": {
            "name": source_name_en,
            "url": source_url,
            "tableId": source_table_id,
        },
    }
    mn = {
        "title": title_mn,
        **common,
        "excerpt": excerpt_mn,
        "category": category_mn,
        "tags": tags_mn,
        "keywords": keywords_mn,
        "dataFiles": [
            {
                "path": f"/datasets/{dataset_id}-all-mn.csv",
                "format": "csv",
                "size": format_size(full_mn),
                "description": "CSV татах (бүх өгөгдөл)",
            },
            {
                "path": f"/datasets/{dataset_id}.xlsx",
                "format": "xlsx",
                "size": format_size(xlsx),
                "description": "Excel татах",
            },
        ],
        "source": {
            "name": source_name_mn,
            "url": source_url,
            "tableId": source_table_id,
        },
    }

    body_template = """---
{frontmatter}
---

import VegaChart from '~/components/ui/VegaChart.astro';

{excerpt}

<VegaChart
  spec="/charts/{dataset_id}-{lang}.json"
  title="{chart_title}"
/>
"""
    en_path = base_dir / "src" / "data" / "data" / "en" / f"{dataset_id}.mdx"
    mn_path = base_dir / "src" / "data" / "data" / "mn" / f"{dataset_id}.mdx"
    en_path.parent.mkdir(parents=True, exist_ok=True)
    mn_path.parent.mkdir(parents=True, exist_ok=True)
    en_path.write_text(
        body_template.format(
            frontmatter=render_frontmatter(en),
            excerpt=excerpt_en,
            dataset_id=dataset_id,
            lang="en",
            chart_title=chart_title_en or title_en,
        ),
        encoding="utf-8",
    )
    mn_path.write_text(
        body_template.format(
            frontmatter=render_frontmatter(mn),
            excerpt=excerpt_mn,
            dataset_id=dataset_id,
            lang="mn",
            chart_title=chart_title_mn or title_mn,
        ),
        encoding="utf-8",
    )
    return en_path, mn_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--title-en", required=True)
    parser.add_argument("--title-mn", required=True)
    parser.add_argument("--excerpt-en", required=True)
    parser.add_argument("--excerpt-mn", required=True)
    parser.add_argument("--category-en", required=True)
    parser.add_argument("--category-mn", required=True)
    parser.add_argument("--tags-en", "--tags", nargs="+", required=True)
    parser.add_argument("--tags-mn", nargs="+", required=True)
    parser.add_argument("--keywords-en", nargs="+", required=True)
    parser.add_argument("--keywords-mn", nargs="+", required=True)
    parser.add_argument("--source-id", default="nso-1212")
    parser.add_argument("--source-table-id", required=True)
    parser.add_argument("--base-dir", type=Path, required=True)
    parser.add_argument("--publish-date", default=date.today().isoformat())
    parser.add_argument("--data-date", required=True)
    parser.add_argument("--version", type=int, default=1)
    parser.add_argument("--chart-title-en")
    parser.add_argument("--chart-title-mn")
    return parser.parse_args()


if __name__ == "__main__":
    paths = generate_mdx_pages(**vars(parse_args()))
    for path in paths:
        print(path)
