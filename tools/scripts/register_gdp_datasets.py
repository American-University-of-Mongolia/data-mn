#!/usr/bin/env python3
"""
Register GDP datasets in the registry
"""

import sys
from pathlib import Path

# Add tools directory to path
TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from registry import Registry, Dataset

def register_datasets():
    """Register GDP datasets"""
    reg = Registry()

    print("Registering GDP datasets...")
    print("="*60)

    # Check if nso-1212 source exists
    source = reg.get_source('nso-1212')
    if not source:
        print("WARNING: Source 'nso-1212' not found in registry")
        print("You may need to add the source first")

    # GDP Total dataset
    gdp_total = Dataset(
        id='gdp-total',
        source_id='nso-1212',
        name_en='Mongolia GDP',
        name_mn='Монгол Улсын ДНБ',
        description_en='Gross Domestic Product of Mongolia at current prices (1990-2024)',
        description_mn='Монгол Улсын Дотоод нийт бүтээгдэхүүн тухайн үеийн үнээр (1990-2024)',
        category='Economy',
        tags=['gdp', 'economy', 'national accounts', 'mongolia'],
        keywords_en=['mongolia gdp', 'gross domestic product', 'economic growth', 'mongolia economy'],
        keywords_mn=['монгол днб', 'дотоод нийт бүтээгдэхүүн', 'эдийн засгийн өсөлт'],
        source_ref='DT_NSO_0500_001V1.px',
        source_path='Economy, environment / National Accounts',
        definition_path='tools/sources/nso-1212/datasets/gdp-total.md',
        source_metadata={
            'table_id': 'DT_NSO_0500_001V1.px',
            'sector': 'Economy, environment',
            'subsector': 'National Accounts',
            'indicator': 'GDP, at current prices',
            'economic_activity': 'Total'
        },
        status='active',
        current_version=1,
        data_file='datasets/gdp-total.csv',
        mdx_file_en='data/data/en/gdp-total.mdx',
        mdx_file_mn='data/data/mn/gdp-total.mdx',
        chart_spec='charts/gdp-total.json',
        auto_update=True,
        auto_publish=True,
        is_parent=False,
        parent_id=None,
        split_filter=None
    )

    try:
        reg.add_dataset(gdp_total)
        print("✓ Registered: gdp-total")
    except Exception as e:
        print(f"✗ Failed to register gdp-total: {e}")

    # GDP Per Capita dataset
    gdp_percap = Dataset(
        id='gdp-per-capita',
        source_id='nso-1212',
        name_en='Mongolia GDP Per Capita',
        name_mn='Нэг хүнд ногдох ДНБ',
        description_en='GDP per capita of Mongolia in USD (1990-2024)',
        description_mn='Монгол Улсын нэг хүнд ногдох ДНБ ам.доллараар (1990-2024)',
        category='Economy',
        tags=['gdp per capita', 'economy', 'income', 'development', 'mongolia'],
        keywords_en=['mongolia gdp per capita', 'per capita income', 'economic development', 'mongolia income'],
        keywords_mn=['нэг хүнд ногдох днб', 'хүн ам тутмын орлого', 'эдийн засгийн хөгжил'],
        source_ref='DT_NSO_0500_010V1.px',
        source_path='Economy, environment / National Accounts',
        definition_path='tools/sources/nso-1212/datasets/gdp-per-capita.md',
        source_metadata={
            'table_id': 'DT_NSO_0500_010V1.px',
            'sector': 'Economy, environment',
            'subsector': 'National Accounts',
            'indicator': 'at current prices',
            'gdp_type': 'GDP per capita, USD'
        },
        status='active',
        current_version=1,
        data_file='datasets/gdp-per-capita.csv',
        mdx_file_en='data/data/en/gdp-per-capita.mdx',
        mdx_file_mn='data/data/mn/gdp-per-capita.mdx',
        chart_spec='charts/gdp-per-capita.json',
        auto_update=True,
        auto_publish=True,
        is_parent=False,
        parent_id=None,
        split_filter=None
    )

    try:
        reg.add_dataset(gdp_percap)
        print("✓ Registered: gdp-per-capita")
    except Exception as e:
        print(f"✗ Failed to register gdp-per-capita: {e}")

    print("\n" + "="*60)
    print("Registration complete!")
    print("\nDatasets in registry:")
    datasets = reg.list_datasets(category='Economy')
    for ds in datasets:
        print(f"  - {ds.id}: {ds.name_en}")

if __name__ == "__main__":
    register_datasets()
