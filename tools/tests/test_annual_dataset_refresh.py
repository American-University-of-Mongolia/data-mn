"""Offline refresh regression: extend a copied snapshot without touching real data."""
import csv
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[2]
DATASETS = {
    'pupil-teacher-ratio': ('pupil_teacher_ratio', 'pupil-teacher-excel', 46),
    'household-income-sources': ('household_income_sources', 'household-income-excel', 24),
}


class AnnualRefreshTest(unittest.TestCase):
    def test_future_snapshot_and_portable_excel(self):
        for slug, (script, payload, series_count) in DATASETS.items():
            builder = ROOT / f'tools/scripts/build_{script}.py'
            if not builder.exists():
                continue  # Each PR initially contains only its own dataset.
            with self.subTest(dataset=slug), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                scripts = root / 'tools/scripts'
                scripts.mkdir(parents=True)
                for name in (f'build_{script}.py', f'fetch_{script}.py', 'build_wide_excel.py'):
                    shutil.copy2(ROOT / 'tools/scripts' / name, scripts / name)
                for folder in ('public/datasets', 'public/charts', 'src/data/data/en', 'src/data/data/mn'):
                    (root / 'data.mn' / folder).mkdir(parents=True)
                raw = root / f'tools/versions/{slug}/v2/raw'
                shutil.copytree(ROOT / f'tools/versions/{slug}/v1/raw', raw)
                manifest = json.loads((raw / 'manifest.json').read_text())
                # Add a synthetic 2026 column, copying the latest values in each
                # series. This checks plumbing, not a claim about future NSO data.
                for lang in ('en', 'mn'):
                    meta = json.loads((raw / f'{lang}-metadata.json').read_text())
                    data = json.loads((raw / f'{lang}-data.json').read_text())
                    variable = meta['variables'][-1]
                    count = len(variable['values'])
                    latest = max(range(count), key=lambda i: int(variable['valueTexts'][i]))
                    variable['values'].append('test-next-year')
                    variable['valueTexts'].append('2026')
                    category = data['dimension'][data['id'][-1]]['category']
                    category['index']['test-next-year'] = count
                    category['label']['test-next-year'] = '2026'
                    original = data['value']
                    if isinstance(original, dict):
                        original = [original.get(str(i)) for i in range(math.prod(data['size']))]
                    extended = []
                    for start in range(0, len(original), count):
                        block = original[start:start + count]
                        extended.extend([*block, block[latest]])
                    data['value'] = extended
                    data['size'][-1] += 1
                    (raw / f'{lang}-metadata.json').write_text(json.dumps(meta))
                    (raw / f'{lang}-data.json').write_text(json.dumps(data))
                for name in manifest['files']:
                    manifest['files'][name] = hashlib.sha256((raw / name).read_bytes()).hexdigest()
                (raw / 'manifest.json').write_text(json.dumps(manifest))
                run = subprocess.run([sys.executable, str(scripts / f'build_{script}.py'),
                                      '--version', '2', '--end-year', '2026'], capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                result = subprocess.run([sys.executable, str(scripts / 'build_wide_excel.py'), slug,
                                         '--input', str(root / f'tools/temp/{payload}.json')],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                for lang in ('en', 'mn'):
                    mdx = (root / f'data.mn/src/data/data/{lang}/{slug}.mdx').read_text()
                    self.assertIn('dataVersion: 2', mdx)
                    self.assertIn('dataDate: 2026-12-31', mdx)
                    self.assertIn('2007–2026', mdx)
                    with (root / f'data.mn/public/datasets/{slug}-{lang}.csv').open() as f:
                        rows = list(csv.reader(f))[1:]
                    self.assertEqual(len(rows), 20 * series_count)
                    expected = {(int(y), name): float(value) for y, name, value in rows}
                    book = load_workbook(root / f'data.mn/public/datasets/{slug}-{lang}.xlsx')
                    sheet = book.active
                    self.assertEqual(sheet.freeze_panes, 'B2')
                    self.assertEqual(sheet.max_row, 21)
                    self.assertEqual(sheet.max_column, series_count + 1)
                    headers = [c.value for c in sheet[1]]
                    for row in list(sheet.rows)[1:]:
                        for i, cell in enumerate(row[1:], 1):
                            self.assertEqual(cell.value, expected[row[0].value, headers[i]])
                            self.assertEqual(cell.data_type, 'n')
                            self.assertEqual(cell.number_format, '0.0')
                    self.assertIn('http', sheet['B2'].comment.text)
                    book.close()
                # Reusing a version must fail before making any HTTP request.
                before = (raw / 'manifest.json').read_bytes()
                fetch = subprocess.run([sys.executable, str(scripts / f'fetch_{script}.py'), '--version', '2'],
                                       capture_output=True, text=True)
                self.assertNotEqual(fetch.returncode, 0)
                self.assertEqual((raw / 'manifest.json').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
