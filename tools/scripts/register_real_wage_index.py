#!/usr/bin/env python3
"""Register the real wage draft as pending, without publishing or enabling refreshes."""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

from build_real_wage_index import ROOT, SLUG, SOURCE_PATH, TABLE, VERSION

sys.path.insert(0, str(ROOT / "tools"))
from registry.registry import Dataset, Registry, Version


def register(db):
    registry = Registry(db)
    snapshot = VERSION / f"{SLUG}-en.csv"
    digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    existing = registry.get_dataset(SLUG)
    if existing:
        versions = registry.get_versions(SLUG)
        if (existing.status != "pending" or existing.is_published or existing.auto_publish
                or existing.auto_update or existing.current_version not in (0, 1)
                or len(versions) != 1 or versions[0].version != 1
                or versions[0].data_hash != digest):
            raise ValueError("Existing dataset differs or is published; review instead of overwriting")
    manifest = json.loads((VERSION / "raw/manifest.json").read_text())
    for name, expected in manifest["files"].items():
        if hashlib.sha256((VERSION / "raw" / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Source snapshot checksum mismatch: {name}")
    responses = [json.loads((VERSION / f"raw/response-{lang}.json").read_text())
                 for lang in ("en", "mn")]
    if responses[0]["updated"] != responses[1]["updated"]:
        raise ValueError("Bilingual source update dates differ")
    source_updated = responses[0]["updated"]
    source_metadata = {"retrieved_at": manifest["retrieved_at"], "index_base": "2023=100",
                       "source_change_years": [2014], "non_comparable_years": [2025]}
    dataset = Dataset(
        id=SLUG, source_id="nso-1212", name_en="Mongolia Real Wage Index (1992–2025)",
        name_mn="Монгол Улсын бодит цалингийн индекс (1992–2025)",
        description_en="Annual national real wage index, 2023=100; source changed in 2014; 2025 is not comparable with earlier years.",
        description_mn="Улсын дундаж бодит цалингийн жилийн индекс, 2023=100; 2014 онд эх үүсвэр өөрчлөгдсөн; 2025 оныг өмнөх онуудтай харьцуулах боломжгүй.",
        category_en="Labor Market", category_mn="Хөдөлмөрийн зах зээл",
        definition_path=f"tools/sources/nso-1212/datasets/{SLUG}.md",
        tags=["mongolia", "real wages", "purchasing power", "inflation"],
        keywords_en=["real wage index", "inflation-adjusted wages"],
        keywords_mn=["бодит цалингийн индекс", "худалдан авах чадвар"],
        source_ref=TABLE, source_path=SOURCE_PATH,
        split_filter={"sector_code": "0", "years": [1992, 2025]},
        source_metadata=source_metadata,
        status="pending", auto_update=False, auto_publish=False,
    )
    if not existing:
        registry.add_dataset(dataset)
    # add_dataset intentionally persists only core fields. Save generated-file
    # and coverage metadata through update_dataset, including on matching reruns.
    registry.update_dataset(SLUG, current_version=1,
        description_en=dataset.description_en, description_mn=dataset.description_mn,
        source_metadata=source_metadata,
        data_file=f"data.mn/public/datasets/{SLUG}-en.csv",
        mdx_file_en=f"data.mn/src/data/data/en/{SLUG}.mdx",
        mdx_file_mn=f"data.mn/src/data/data/mn/{SLUG}.mdx",
        chart_spec=f"data.mn/public/charts/{SLUG}-en.json",
        data_as_of="2025-12-31", last_fetched_at=manifest["retrieved_at"],
        last_checked_at=manifest["retrieved_at"], source_updated_at=source_updated,
        created_at=(existing.created_at if existing else None) or datetime.now(timezone.utc).isoformat(),
        coverage_geography=json.dumps(["national"]), coverage_granularity="national",
        coverage_time_start="1992", coverage_time_end="2025", coverage_frequency="annual",
        coverage_dimensions=json.dumps({"economic_sector": False}),
        coverage_notes="Official national annual index; 2014 source transition unconfirmed for comparability; 2025 explicitly non-comparable.",
    )
    if existing:
        print("Matching pending snapshot metadata repaired; no version or activity added")
        return
    registry.add_version(Version(
        id=0, dataset_id=SLUG, version=1, data_hash=digest,
        data_path=str(snapshot.relative_to(ROOT)), row_count=34, column_count=2,
        change_type="initial", change_summary="National official real wage index, 1992–2025; pending review",
        source_updated_at=source_updated,
        source_raw_files=[str(p.relative_to(ROOT)) for p in sorted((VERSION / "raw").iterdir())],
    ))
    registry.log_activity("add", "success", "Prepared national real wage draft; not published",
                          dataset_id=SLUG, source_id="nso-1212")
    print("Registered one pending dataset with one version")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=ROOT / "tools/registry/data.db")
    register(parser.parse_args().db)
