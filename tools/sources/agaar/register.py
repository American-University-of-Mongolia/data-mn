#!/usr/bin/env python3
"""Register the agaar source and its parent dataset (cleaned daily PM2.5 station means)."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1]
sys.path.insert(0, str(TOOLS))

from registry import Dataset, Registry, Source  # noqa: E402

PARENT_ID = "agaar-daily-station-means"
DATA_FILE = "sources/agaar/derived/agaar-daily-station-means.csv"


# The page datasets: aggregations of the parent, one derived table each
# (see datasets/agaar-daily-station-means.md, "Splits").
SPLITS = [
    ("pm25-monthly-ulaanbaatar-aimags",
     "PM2.5 in Ulaanbaatar and Aimag Centres by Month",
     "Улаанбаатар болон аймгийн төвүүдийн PM2.5, сараар",
     {"table": "pm25-monthly-ulaanbaatar-aimags", "from": "2025-10", "aggregate": "monthly mean by area"}),
    ("pm25-unhealthy-days-ulaanbaatar",
     "Days Above Mongolia's PM2.5 Limit in Ulaanbaatar by Month",
     "Улаанбаатарт PM2.5-ын зөвшөөрөгдөх хэмжээг давсан өдрийн тоо, сараар",
     {"table": "pm25-unhealthy-days-ulaanbaatar", "from": "2025-10", "limit": 50, "min_stations": 8}),
    ("pm25-winter-by-aimag-centre",
     "Winter PM2.5 by Aimag Centre",
     "Аймгийн төвүүдийн өвлийн PM2.5",
     {"table": "pm25-winter-by-aimag-centre", "season": "2025-12/2026-02", "min_station_days": 60}),
    ("pm25-winter-by-station-ulaanbaatar",
     "Winter PM2.5 by Monitoring Station in Ulaanbaatar",
     "Улаанбаатарын агаар хяналтын станцуудын өвлийн PM2.5",
     {"table": "pm25-winter-by-station-ulaanbaatar", "season": "2025-12/2026-02", "min_days": 60}),
]


def register_splits(registry: Registry, meta: dict) -> None:
    for split_id, name_en, name_mn, split_filter in SPLITS:
        if registry.get_dataset(split_id) is not None:
            print(f"Split already registered: {split_id}")
            continue
        registry.add_dataset(
            Dataset(
                id=split_id,
                source_id="agaar",
                name_en=name_en,
                name_mn=name_mn,
                category_en="Environment",
                category_mn="Байгаль орчин",
                definition_path=f"sources/agaar/datasets/{split_id}.md",
                parent_id=PARENT_ID,
                is_parent=False,
                split_filter=split_filter,
                tags=["air quality", "PM2.5", "pollution"],
                source_ref="https://agaar.gov.mn",
                source_path=f"sources/agaar/derived/{split_id}.csv",
                data_file=f"data.mn/public/datasets/{split_id}-en.csv",
                mdx_file_en=f"data.mn/src/data/data/en/{split_id}.mdx",
                mdx_file_mn=f"data.mn/src/data/data/mn/{split_id}.mdx",
                chart_spec=f"data.mn/public/charts/{split_id}-en.json",
                data_as_of=meta["last_date"],
                status="active",
                auto_update=True,
                auto_publish=False,
            )
        )
        print(f"Added split: {split_id}")


def main() -> None:
    meta = json.loads((HERE / "derived" / "agaar-daily-station-means.meta.json").read_text(encoding="utf-8"))
    registry = Registry()

    if registry.get_source("agaar") is None:
        registry.add_source(
            Source(
                id="agaar",
                name="Air Quality Portal (NAMEM)",
                name_mn="Агаарын чанарын мэдээллийн сан (ЦУОШГ)",
                type="api",
                base_url="https://agaar.gov.mn",
                definition_path="sources/agaar/source.md",
                update_frequency="monthly",
                priority=40,
                config={"archive": "sources/agaar/raw", "fetcher": ".claude/skills/datamn-source-agaar/fetch_data.py"},
            )
        )
        print("Added source: agaar")
    else:
        print("Source already registered: agaar")

    if registry.get_dataset(PARENT_ID) is None:
        registry.add_dataset(
            Dataset(
                id=PARENT_ID,
                source_id="agaar",
                name_en="Daily PM2.5 by Monitoring Station (cleaned)",
                name_mn="Агаар хяналтын станц тус бүрийн өдрийн PM2.5 (цэвэрлэсэн)",
                description_en=(
                    "Daily mean PM2.5 per agaar.gov.mn station with cleaning rules applied "
                    "(negatives, PM2.5 above PM10, spikes, stuck sensors); parent for the PM2.5 pages."
                ),
                description_mn=(
                    "agaar.gov.mn-ийн станц тус бүрийн өдрийн дундаж PM2.5, цэвэрлэх дүрэм "
                    "хэрэглэсэн; PM2.5 хуудсуудын эх өгөгдөл."
                ),
                category_en="Environment",
                category_mn="Байгаль орчин",
                definition_path=f"sources/agaar/datasets/{PARENT_ID}.md",
                is_parent=True,
                tags=["air quality", "PM2.5", "pollution", "ulaanbaatar", "aimag"],
                keywords_en=["Mongolia", "air pollution", "PM2.5", "smog"],
                keywords_mn=["Монгол", "агаарын бохирдол", "PM2.5", "утаа"],
                source_ref="https://agaar.gov.mn",
                source_path=DATA_FILE,
                source_metadata=meta,
                status="active",
                auto_update=True,
                auto_publish=False,
            )
        )
        print(f"Added parent dataset: {PARENT_ID}")
    else:
        print(f"Parent dataset already registered: {PARENT_ID}")

    register_splits(registry, meta)

    con = sqlite3.connect(registry.db_path)
    con.execute(
        """UPDATE datasets SET source_metadata = ?, data_file = ?, data_as_of = ?,
               last_fetched_at = ?, updated_at = datetime('now') WHERE id = ?""",
        (json.dumps(meta, ensure_ascii=False), DATA_FILE, meta["last_date"], meta["built_at"], PARENT_ID),
    )
    con.commit()
    con.close()
    print(f"Refreshed parent metadata: data to {meta['last_date']}")


if __name__ == "__main__":
    main()
