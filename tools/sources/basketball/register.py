#!/usr/bin/env python3
"""Register the basketball source and its three public, stable dataset IDs."""
from dataclasses import asdict
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from registry import Dataset, Registry, Source, Version
from build_public import INPUT, IDS, records

TITLES = {
    IDS[0]: ('Mongolian Basketball Game Results', 'Монголын сагсан бөмбөгийн тоглолтын үр дүн'),
    IDS[1]: ('Mongolian Basketball Team Records', 'Монголын сагсан бөмбөгийн багийн үзүүлэлт'),
    IDS[2]: ('Mongolian Basketball Player Game Statistics', 'Монголын сагсан бөмбөгийн тоглогчдын тоглолтын статистик'),
}


def main():
    registry = Registry()
    source = registry.get_source('basketball')
    if source is None:
        registry.add_source(Source(id='basketball', name='Mongolian basketball archive',
            name_mn='Монголын сагсан бөмбөгийн архив', type='mixed',
            definition_path='sources/basketball/source.md', base_url='https://mongolia.basketball/',
            update_frequency='after reviewed game reports', config={'browser_json': str(INPUT.relative_to(ROOT))}))
    elif source.definition_path != 'sources/basketball/source.md':
        raise ValueError('Unexpected existing basketball source')
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    tables = records(data)
    for dataset_id, rows in tables.items():
        en, mn = TITLES[dataset_id]
        date = max(r['date'] for r in rows) if 'date' in rows[0] else max(g['date'] for s in data['seasons'] for g in s['games'])
        dataset = Dataset(id=dataset_id, source_id='basketball', name_en=en, name_mn=mn,
            description_en=en + ' derived from the reviewed sports browser JSON; coverage limits are documented.',
            description_mn=mn + '. Хамрах хүрээ болон эх сурвалжийн хязгаарлалтыг тайлбарлав.',
            category_en='Sports', category_mn='Спорт',
            definition_path=f'sources/basketball/datasets/{dataset_id}.md',
            source_ref='https://mongolia.basketball/', source_path=str(INPUT.relative_to(ROOT)),
            source_metadata={'rows': len(rows), 'browser_json_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest()},
            tags=['basketball', 'sports', 'Mongolia'], keywords_en=['Mongolian basketball', en],
            keywords_mn=['сагсан бөмбөг', mn], status='active', auto_publish=False, auto_update=False,
            data_file=f'data.mn/public/datasets/{dataset_id}-en.csv', data_as_of=date,
            mdx_file_en=f'data.mn/src/data/data/en/{dataset_id}.mdx',
            mdx_file_mn=f'data.mn/src/data/data/mn/{dataset_id}.mdx',
            chart_spec=f'data.mn/public/charts/{dataset_id}-en.json')
        existing = registry.get_dataset(dataset_id)
        if existing is None:
            registry.add_dataset(dataset)
        elif existing.source_id != 'basketball':
            raise ValueError(f'Unexpected existing dataset: {dataset_id}')
        else:
            # Refresh content metadata without resetting permanent URL/publication/version state.
            values = asdict(dataset)
            for key in ('id', 'canonical_slug', 'first_published_at', 'is_published', 'current_version',
                        'created_at', 'updated_at', 'deprecated_at', 'deprecation_reason', 'successor_id'):
                values.pop(key, None)
            registry.update_dataset(dataset_id, **values)
        print(f'Registered {dataset_id}: {len(rows)} rows through {date}')
        versions = registry.get_versions(dataset_id)
        csvs = {lang: ROOT / f'data.mn/public/datasets/{dataset_id}-{lang}.csv' for lang in ('en', 'mn')}
        changed = not versions or any(
            csvs[lang].read_bytes() != (ROOT / f'tools/versions/{dataset_id}/v{versions[0].version}/data-{lang}.csv').read_bytes()
            for lang in csvs)
        version = versions[0].version if versions else 0
        if changed:
            version += 1
            folder = ROOT / f'tools/versions/{dataset_id}/v{version}'
            folder.mkdir(parents=True, exist_ok=True)
            hashes = {}
            for lang in ('en', 'mn'):
                target = folder / f'data-{lang}.csv'
                if target.exists() and target.read_bytes() != csvs[lang].read_bytes():
                    raise ValueError(f'Refusing to overwrite a different version snapshot: {target}')
                shutil.copyfile(csvs[lang], target)
                hashes[target.name] = hashlib.sha256(target.read_bytes()).hexdigest()
            manifest_path = folder / 'manifest.json'
            if not manifest_path.exists():
                manifest_path.write_text(json.dumps({'dataset': dataset_id, 'version': version,
                    'input': str(INPUT.relative_to(ROOT)), 'input_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest(),
                    'files': hashes, 'command': 'python tools/sources/basketball/build_public.py'}, indent=2)+'\n', encoding='utf-8')
            registry.add_version(Version(id=0, dataset_id=dataset_id, version=version,
                data_hash=hashes['data-en.csv'], data_path=f'versions/{dataset_id}/v{version}/data-en.csv',
                row_count=len(rows), column_count=len(rows[0]), change_type='initial' if version == 1 else 'update',
                change_summary='Public downloads from reviewed basketball browser JSON',
                source_updated_at=date, source_raw_files=[str(INPUT.relative_to(ROOT))]))
        registry.update_dataset(dataset_id, current_version=version)
        for lang in ('en', 'mn'):
            page = ROOT / f'data.mn/src/data/data/{lang}/{dataset_id}.mdx'
            page.write_text(re.sub(r'^dataVersion:.*$', f'dataVersion: {version}',
                page.read_text(encoding='utf-8'), flags=re.M), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
