"""Archive bilingual NSO income composition, preserving the complete source."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]
SLUG = 'household-income-sources'
SOURCE = 'Society, development/Household income and expenditure/DT_NSO_1900_003V1.px'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', type=int, required=True)
    args = parser.parse_args()
    if args.version < 1:
        parser.error('version must be positive')
    RAW = ROOT / 'tools/versions' / SLUG / f'v{args.version}' / 'raw'
    if RAW.exists():
        raise SystemExit('Snapshot already exists; use a new version for refreshes.')
    RAW.mkdir(parents=True)
    hashes = {}

    def save(name, value):
        content = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
        (RAW / name).write_bytes(content)
        hashes[name] = hashlib.sha256(content).hexdigest()

    for lang in ('en', 'mn'):
        url = f'https://data.1212.mn/api/v1/{lang}/NSO/{SOURCE}'
        r = requests.get(url, timeout=45)
        r.raise_for_status()
        metadata = r.json()
        save(f'{lang}-metadata.json', metadata)
        query = {'query': [{'code': v['code'], 'selection': {'filter': 'item', 'values': v['values']}}
                           for v in metadata['variables']], 'response': {'format': 'json-stat2'}}
        save(f'{lang}-query.json', query)
        r = requests.post(url, json=query, timeout=45)
        r.raise_for_status()
        save(f'{lang}-data.json', r.json())
    r = requests.get(f'https://data.1212.mn/api/v1/en/NSO/{SOURCE.rsplit("/", 1)[0]}/', timeout=45)
    r.raise_for_status()
    listing = next(row for row in r.json() if row['id'] == SOURCE.rsplit('/', 1)[1])
    save('table-listing.json', listing)
    manifest = {'source_path': SOURCE, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                'snapshot_date': datetime.now(timezone.utc).date().isoformat(), 'source_updated_at': listing['updated'], 'files': hashes}
    (RAW / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Archived both languages; source updated {listing["updated"]}.')


if __name__ == '__main__':
    main()
