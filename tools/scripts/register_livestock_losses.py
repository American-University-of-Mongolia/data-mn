#!/usr/bin/env python3
"""Register the current snapshot as pending, preserving earlier versions."""

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

from build_livestock_losses import DATASETS, ROOT, VERSION, VERSION_NUMBER, START, END

sys.path.insert(0, str(ROOT / 'tools'))
from registry.registry import Dataset, Registry, Version


def register(db_path):
    registry = Registry(db_path)
    manifest = json.loads((VERSION / 'raw/manifest.json').read_text())
    retrieved = manifest['retrieved_at']
    updated = manifest['tables']['losses']['updated']
    raw_files = [str(p.relative_to(ROOT)) for p in sorted((VERSION / 'raw').glob('*.json'))]
    parent_id = 'nso-livestock-losses'
    configs = {parent_id: {
        'title_en': 'Mongolia adult livestock losses and starting herds (source extract)',
        'title_mn': 'Монгол Улсын том малын зүй бус хорогдол ба оны эхний малын тоо',
        'excerpt_en': f'Bilingual source extract with national controls and aimag/capital observations, {START}–{END}.',
        'excerpt_mn': f'Улсын дүн, аймаг, нийслэлийн {START}–{END} оны хорогдол болон оны эхний малын тооны хоёр хэл дээрх эх өгөгдөл.',
    }, **{dataset_id: config for dataset_id, config in DATASETS.items()
          if (ROOT / f'data.mn/src/data/data/en/{dataset_id}.mdx').exists()}}
    for dataset_id, config in configs.items():
        parent = dataset_id == parent_id
        version_dir = VERSION if parent else ROOT / f'tools/versions/{dataset_id}/v{VERSION_NUMBER}'
        data_path = version_dir / ('observations.csv' if parent else 'data-en.csv')
        digest = hashlib.sha256(data_path.read_bytes()).hexdigest()
        with data_path.open(encoding='utf-8-sig', newline='') as file:
            records = list(csv.reader(file))
        row_count, column_count = len(records) - 1, len(records[0])
        existing = registry.get_dataset(dataset_id)
        versions = registry.get_versions(dataset_id) if existing else []
        current = next((v for v in versions if v.version == VERSION_NUMBER), None)
        if current and current.data_hash == digest and existing.current_version == VERSION_NUMBER:
            print(dataset_id, f'already registered with matching v{VERSION_NUMBER} data')
            continue
        if any(v.version >= VERSION_NUMBER for v in versions):
            raise ValueError(f'{dataset_id}: current/newer version exists; do not overwrite history')
        if existing and (existing.status != 'pending' or existing.auto_publish):
            raise ValueError(f'{dataset_id}: review the active publication workflow before updating')
        selection = None if parent else {
            'years': [START, END],
            'region': 'aimags_and_capital' if config['category'] == 'region' else '0',
            'animal': '0' if config['category'] == 'region' else ['1', '2', '3', '4', '5'],
            'measure': config['measure'],
        }
        metadata = {'tables': manifest['tables'], 'retrieved_at': retrieved,
                    'loss_years': [START, END], 'herd_years': [START - 1, END - 1],
                    'derived_rate': 'losses(t) / year_end_herd(t-1) * 100',
                    'refresh_policy': 'manual versioned two-table refresh; see parent definition'}
        dataset = Dataset(
            id=dataset_id, source_id='nso-1212', parent_id=None if parent else parent_id,
            is_parent=parent, split_filter=selection, name_en=config['title_en'], name_mn=config['title_mn'],
            description_en=config['excerpt_en'], description_mn=config['excerpt_mn'],
            category_en='Agriculture', category_mn='Хөдөө аж ахуй',
            tags=['livestock', 'agriculture', 'livestock losses'],
            keywords_en=['Mongolia livestock losses', 'adult livestock mortality'],
            keywords_mn=['том малын зүй бус хорогдол', 'малын хорогдол аймгаар'],
            source_ref='DT_NSO_1001_029V1.px',
            source_path='Industry, service/Livestock/DT_NSO_1001_029V1.px',
            definition_path=f'tools/sources/nso-1212/datasets/{dataset_id}.md',
            source_metadata=metadata,
            status='pending', auto_update=False, auto_publish=False,
        )
        if not existing:
            registry.add_dataset(dataset)
        registry.update_dataset(dataset_id, current_version=VERSION_NUMBER,
            name_en=dataset.name_en, name_mn=dataset.name_mn,
            description_en=dataset.description_en, description_mn=dataset.description_mn,
            source_metadata=metadata, split_filter=json.dumps(selection) if selection else None,
            data_file=str(data_path.relative_to(ROOT)) if parent else f'data.mn/public/datasets/{dataset_id}-en.csv',
            mdx_file_en=None if parent else f'data.mn/src/data/data/en/{dataset_id}.mdx',
            mdx_file_mn=None if parent else f'data.mn/src/data/data/mn/{dataset_id}.mdx',
            chart_spec=None if parent else f'data.mn/public/charts/{dataset_id}-en.json',
            data_as_of=f'{END}-12-31', source_updated_at=updated,
            last_checked_at=retrieved, last_fetched_at=retrieved)
        registry.add_version(Version(
            id=0, dataset_id=dataset_id, version=VERSION_NUMBER, data_hash=digest,
            data_path=str(data_path.relative_to(ROOT)), row_count=row_count, column_count=column_count,
            change_type='update' if existing else 'initial',
            change_summary=f'Extend to all available loss years, {START}–{END}; preserve historical missing values; pending review',
            source_updated_at=updated, source_raw_files=raw_files,
        ))
        registry.log_activity('update' if existing else 'add', 'success', f'Prepared v{VERSION_NUMBER} livestock-loss data for review; not published',
                              dataset_id=dataset_id, source_id='nso-1212')
        print(dataset_id, 'registered as pending:', row_count, 'rows')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=ROOT / 'tools/registry/data.db')
    register(parser.parse_args().db)
