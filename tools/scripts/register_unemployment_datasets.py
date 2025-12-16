#!/usr/bin/env python3
"""
Register unemployment datasets in the data.mn registry
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from registry import Registry, Dataset, Version, Source
from datetime import datetime
import hashlib

def main():
    reg = Registry()

    # Check if source exists
    source = reg.get_source('nso-1212')
    if not source:
        print("Creating nso-1212 source...")
        source = Source(
            id='nso-1212',
            name='National Statistics Office of Mongolia',
            name_mn='Үндэсний Статистикийн Хороо',
            type='REST API',
            base_url='https://data.1212.mn',
            definition_path='tools/sources/nso-1212/source.md',
            update_frequency='varies',
            enabled=True,
            priority=100
        )
        reg.add_source(source)
        print("✓ Created nso-1212 source")

    # Dataset 1: Overall unemployment rate
    print("\nRegistering unemployment-rate...")

    existing = reg.get_dataset('unemployment-rate')
    if existing:
        print("  Dataset already exists, updating...")
        reg.update_dataset(
            'unemployment-rate',
            current_version=1,
            status='active',
            data_file='/datasets/unemployment-rate.csv',
            mdx_file_en='src/data/data/en/unemployment-rate.mdx',
            mdx_file_mn='src/data/data/mn/unemployment-rate.mdx',
            chart_spec='/charts/unemployment-rate.json',
            data_as_of='2024-09-29',
            source_updated_at='2025-09-29T09:54:19',
            last_fetched_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    else:
        dataset = Dataset(
            id='unemployment-rate',
            source_id='nso-1212',
            name_en='Mongolia Unemployment Rate',
            name_mn='Монгол Улсын ажилгүйдлийн түвшин',
            category='Economy',
            description_en='Overall unemployment rate in Mongolia (2009-2024)',
            description_mn='Монгол Улсын нийт ажилгүйдлийн түвшин (2009-2024)',
            tags=['unemployment', 'labour', 'economy'],
            keywords_en=['unemployment rate', 'labour market', 'employment'],
            keywords_mn=['ажилгүйдэл', 'хөдөлмөрийн зах зээл', 'ажил эрхлэлт'],
            source_ref='DT_NSO_0400_049V1.px',
            source_path='Labour, business / Decent work',
            definition_path='tools/sources/nso-1212/datasets/unemployment-rate.md',
            is_parent=False,
            current_version=1,
            status='active',
            data_file='/datasets/unemployment-rate.csv',
            mdx_file_en='src/data/data/en/unemployment-rate.mdx',
            mdx_file_mn='src/data/data/mn/unemployment-rate.mdx',
            chart_spec='/charts/unemployment-rate.json',
            data_as_of='2024-09-29',
            source_updated_at='2025-09-29T09:54:19',
            last_fetched_at=datetime.now().isoformat(),
            auto_update=True,
            auto_publish=True
        )
        reg.add_dataset(dataset)
        # Update with file paths
        reg.update_dataset(
            'unemployment-rate',
            current_version=1,
            data_file='/datasets/unemployment-rate.csv',
            mdx_file_en='src/data/data/en/unemployment-rate.mdx',
            mdx_file_mn='src/data/data/mn/unemployment-rate.mdx',
            chart_spec='/charts/unemployment-rate.json',
            data_as_of='2024-09-29',
            source_updated_at='2025-09-29T09:54:19',
            last_fetched_at=datetime.now().isoformat()
        )

    print("✓ Registered unemployment-rate")

    # Dataset 2: Unemployment by sex
    print("\nRegistering unemployment-rate-by-sex...")

    existing = reg.get_dataset('unemployment-rate-by-sex')
    if existing:
        print("  Dataset already exists, updating...")
        reg.update_dataset(
            'unemployment-rate-by-sex',
            current_version=1,
            status='active',
            data_file='/datasets/unemployment-rate-by-sex.csv',
            mdx_file_en='src/data/data/en/unemployment-rate-by-sex.mdx',
            mdx_file_mn='src/data/data/mn/unemployment-rate-by-sex.mdx',
            chart_spec='/charts/unemployment-rate-by-sex.json',
            data_as_of='2024-09-29',
            source_updated_at='2025-09-29T09:54:19',
            last_fetched_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    else:
        dataset = Dataset(
            id='unemployment-rate-by-sex',
            source_id='nso-1212',
            name_en='Mongolia Unemployment Rate by Sex',
            name_mn='Монгол Улсын ажилгүйдлийн түвшин хүйсээр',
            category='Economy',
            description_en='Unemployment rate in Mongolia by sex (2009-2024)',
            description_mn='Монгол Улсын ажилгүйдлийн түвшин хүйсээр (2009-2024)',
            tags=['unemployment', 'labour', 'economy', 'gender'],
            keywords_en=['unemployment rate', 'gender gap', 'male unemployment', 'female unemployment'],
            keywords_mn=['ажилгүйдэл', 'хүйсийн зөрүү', 'эрэгтэй', 'эмэгтэй'],
            source_ref='DT_NSO_0400_049V1.px',
            source_path='Labour, business / Decent work',
            definition_path='tools/sources/nso-1212/datasets/unemployment-rate-by-sex.md',
            is_parent=False,
            current_version=1,
            status='active',
            data_file='/datasets/unemployment-rate-by-sex.csv',
            mdx_file_en='src/data/data/en/unemployment-rate-by-sex.mdx',
            mdx_file_mn='src/data/data/mn/unemployment-rate-by-sex.mdx',
            chart_spec='/charts/unemployment-rate-by-sex.json',
            data_as_of='2024-09-29',
            source_updated_at='2025-09-29T09:54:19',
            last_fetched_at=datetime.now().isoformat(),
            auto_update=True,
            auto_publish=True
        )
        reg.add_dataset(dataset)
        # Update with file paths
        reg.update_dataset(
            'unemployment-rate-by-sex',
            current_version=1,
            data_file='/datasets/unemployment-rate-by-sex.csv',
            mdx_file_en='src/data/data/en/unemployment-rate-by-sex.mdx',
            mdx_file_mn='src/data/data/mn/unemployment-rate-by-sex.mdx',
            chart_spec='/charts/unemployment-rate-by-sex.json',
            data_as_of='2024-09-29',
            source_updated_at='2025-09-29T09:54:19',
            last_fetched_at=datetime.now().isoformat()
        )

    print("✓ Registered unemployment-rate-by-sex")

    # Log activity
    reg.log_activity(
        action='create',
        status='success',
        dataset_id='unemployment-rate',
        message='Created unemployment rate datasets from NSO source'
    )

    print("\n✓ Done! Registered 2 unemployment datasets.")
    print("\nRegistry status:")
    print(f"  Total datasets: {len(reg.list_datasets())}")
    print(f"  Active datasets: {len(reg.list_datasets(status='active'))}")

if __name__ == "__main__":
    main()
