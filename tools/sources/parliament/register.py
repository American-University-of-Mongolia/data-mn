#!/usr/bin/env python3
"""Register the Parliament source and its normalized parent dataset."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1]
sys.path.insert(0, str(TOOLS))

from registry import Dataset, Registry, Source  # noqa: E402


def main() -> None:
    metadata_path = HERE / "raw" / "parliament-pull.meta.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    registry = Registry()

    source = registry.get_source("parliament")
    if source is None:
        registry.add_source(
            Source(
                id="parliament",
                name="State Great Khural of Mongolia",
                name_mn="Монгол Улсын Их Хурал",
                type="mixed",
                base_url="https://www.parliament.mn/nc/635/",
                definition_path="sources/parliament/source.md",
                update_frequency="per sitting",
                priority=40,
                config={"structured_dashboard": "https://att.parliament.mn/"},
            )
        )
        print("Added source: parliament")
    elif source.definition_path != "sources/parliament/source.md":
        raise SystemExit(
            f"Existing parliament source has unexpected definition: {source.definition_path}"
        )
    else:
        print("Source already registered: parliament")

    dataset_id = "parliament-attendance-records"
    dataset = registry.get_dataset(dataset_id)
    if dataset is None:
        registry.add_dataset(
            Dataset(
                id=dataset_id,
                source_id="parliament",
                name_en="Mongolian Parliament Plenary Attendance Records",
                name_mn="Монгол Улсын Их Хурлын нэгдсэн хуралдааны ирцийн бүртгэл",
                description_en=(
                    "Normalized MP-by-sitting attendance, arrival, and plenary "
                    "start-time records; parent for user-facing attendance views."
                ),
                description_mn=(
                    "Гишүүн-хуралдаан бүрийн ирц, ирсэн цаг, нэгдсэн хуралдааны "
                    "эхлэх цагийн нормчилсон бүртгэл."
                ),
                category_en="Government & Politics",
                category_mn="Засаглал ба улс төр",
                definition_path=(
                    "sources/parliament/datasets/parliament-attendance-records.md"
                ),
                is_parent=True,
                tags=["parliament", "attendance", "punctuality", "MPs", "plenary"],
                keywords_en=["Mongolia", "parliament", "attendance", "lateness"],
                keywords_mn=["Монгол", "УИХ", "ирц", "хоцролт"],
                source_ref="https://att.parliament.mn/",
                source_path="sources/parliament/raw/parliament-attendance.csv",
                source_metadata=metadata,
                status="active",
                auto_update=True,
                auto_publish=False,
            )
        )
        print(f"Added parent dataset: {dataset_id}")
    elif dataset.source_id != "parliament" or not dataset.is_parent:
        raise SystemExit(f"Unexpected existing dataset row: {dataset_id}")
    else:
        print(f"Parent dataset already registered: {dataset_id}")

    connection = sqlite3.connect(registry.db_path)
    connection.execute(
        """
        UPDATE datasets
        SET source_metadata = ?, source_path = ?, data_file = ?, data_as_of = ?,
            last_checked_at = ?, last_fetched_at = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (
            json.dumps(metadata, ensure_ascii=False),
            "sources/parliament/raw/parliament-attendance.csv",
            "sources/parliament/raw/parliament-attendance.csv",
            metadata["coverage"]["last_sitting"],
            metadata["fetched_at"],
            metadata["fetched_at"],
            dataset_id,
        ),
    )
    connection.commit()
    connection.close()
    print(f"Refreshed parent metadata: {metadata['coverage']['last_sitting']}")


if __name__ == "__main__":
    main()
