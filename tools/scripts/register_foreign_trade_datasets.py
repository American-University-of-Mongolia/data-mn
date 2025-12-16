#!/usr/bin/env python3
"""
Register Foreign Trade datasets in the registry
"""

import sys
from pathlib import Path

# Add tools directory to path
TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from registry import Registry, Dataset

def register_datasets():
    """Register Foreign Trade datasets"""
    reg = Registry()

    print("Registering Foreign Trade datasets...")
    print("="*60)

    # Check if nso-1212 source exists
    source = reg.get_source('nso-1212')
    if not source:
        print("WARNING: Source 'nso-1212' not found in registry")
        print("You may need to add the source first")

    # Foreign Trade Total dataset
    foreign_trade = Dataset(
        id='foreign-trade',
        source_id='nso-1212',
        name_en='Mongolia Foreign Trade Turnover',
        name_mn='Монгол Улсын гадаад худалдааны эргэлт',
        description_en='Total foreign trade turnover of Mongolia (1924-2024)',
        description_mn='Монгол Улсын гадаад худалдааны нийт эргэлт (1924-2024)',
        category='Economy',
        tags=['foreign trade', 'trade', 'turnover', 'economy', 'mongolia'],
        keywords_en=['mongolia foreign trade', 'trade turnover', 'mongolia trade statistics', 'foreign trade mongolia'],
        keywords_mn=['монгол гадаад худалдаа', 'худалдааны эргэлт', 'гадаад худалдааны статистик'],
        source_ref='DT_NSO_1400_001V1_year.px',
        source_path='Economy, environment / Foreign Trade',
        definition_path='tools/sources/nso-1212/datasets/foreign-trade.md',
        source_metadata={
            'table_id': 'DT_NSO_1400_001V1_year.px',
            'sector': 'Economy, environment',
            'subsector': 'Foreign Trade',
            'indicator': 'Total turnover'
        },
        status='active',
        current_version=1,
        data_file='datasets/foreign-trade.csv',
        mdx_file_en='content/data/en/foreign-trade.mdx',
        mdx_file_mn='content/data/mn/foreign-trade.mdx',
        chart_spec='charts/foreign-trade.json',
        auto_update=True,
        auto_publish=True,
        is_parent=False,
        parent_id=None,
        split_filter=None
    )

    try:
        reg.add_dataset(foreign_trade)
        print("✓ Registered: foreign-trade")
    except Exception as e:
        print(f"✗ Failed to register foreign-trade: {e}")

    # Foreign Trade Balance dataset
    foreign_trade_balance = Dataset(
        id='foreign-trade-balance',
        source_id='nso-1212',
        name_en='Mongolia Foreign Trade Balance',
        name_mn='Монгол Улсын гадаад худалдааны тэнцэл',
        description_en='Exports, imports, and trade balance of Mongolia (1924-2024)',
        description_mn='Монгол Улсын экспорт, импорт, худалдааны тэнцэл (1924-2024)',
        category='Economy',
        tags=['foreign trade', 'exports', 'imports', 'trade balance', 'economy', 'mongolia'],
        keywords_en=['mongolia trade balance', 'mongolia exports', 'mongolia imports', 'trade surplus', 'foreign trade balance'],
        keywords_mn=['монгол худалдааны тэнцэл', 'монгол экспорт', 'монгол импорт', 'худалдааны илүүдэл'],
        source_ref='DT_NSO_1400_001V1_year.px',
        source_path='Economy, environment / Foreign Trade',
        definition_path='tools/sources/nso-1212/datasets/foreign-trade-balance.md',
        source_metadata={
            'table_id': 'DT_NSO_1400_001V1_year.px',
            'sector': 'Economy, environment',
            'subsector': 'Foreign Trade',
            'indicators': ['Exports', 'Imports', 'Balance']
        },
        status='active',
        current_version=1,
        data_file='datasets/foreign-trade-balance.csv',
        mdx_file_en='content/data/en/foreign-trade-balance.mdx',
        mdx_file_mn='content/data/mn/foreign-trade-balance.mdx',
        chart_spec='charts/foreign-trade-balance.json',
        auto_update=True,
        auto_publish=True,
        is_parent=False,
        parent_id=None,
        split_filter=None
    )

    try:
        reg.add_dataset(foreign_trade_balance)
        print("✓ Registered: foreign-trade-balance")
    except Exception as e:
        print(f"✗ Failed to register foreign-trade-balance: {e}")

    print("\n" + "="*60)
    print("Registration complete!")
    print("\nForeign Trade datasets in registry:")
    datasets = reg.list_datasets(source_id='nso-1212')
    for ds in datasets:
        if 'foreign-trade' in ds.id:
            print(f"  - {ds.id}: {ds.name_en}")

if __name__ == "__main__":
    register_datasets()
