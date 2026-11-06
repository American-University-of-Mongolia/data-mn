"""Archive a new bilingual NSO pupil–teacher ratio snapshot; never overwrite one."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'tools/versions/pupil-teacher-ratio/v1/raw'
SOURCE_PATH = 'Education, health/General educational schools/DT_NSO_2002_015V1.px'


def main():
    if RAW.exists():
        raise SystemExit('Snapshot exists. Preserve v1; use a new version for a refresh.')
    RAW.mkdir(parents=True)
    files = {}

    def save(name, value):
        content = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
        (RAW / name).write_bytes(content)
        files[name] = hashlib.sha256(content).hexdigest()

    for lang in ('en', 'mn'):
        url = f'https://data.1212.mn/api/v1/{lang}/NSO/{SOURCE_PATH}'
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        metadata = response.json()
        save(f'{lang}-metadata.json', metadata)
        query = {'query': [
            {'code': var['code'], 'selection': {'filter': 'item', 'values': var['values']}}
            for var in metadata['variables']
        ], 'response': {'format': 'json-stat2'}}
        save(f'{lang}-query.json', query)
        response = requests.post(url, json=query, timeout=60)
        response.raise_for_status()
        save(f'{lang}-data.json', response.json())
    response = requests.get(f'https://data.1212.mn/api/v1/en/NSO/{SOURCE_PATH.rsplit("/", 1)[0]}/', timeout=60)
    response.raise_for_status()
    entry = next(t for t in response.json() if t['id'] == SOURCE_PATH.rsplit('/', 1)[1])
    save('table-listing.json', entry)
    manifest = {'source_path': SOURCE_PATH, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                'snapshot_date': '2026-11-01', 'source_updated_at': entry['updated'], 'files': files}
    (RAW / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
