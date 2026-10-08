"""Language-switch downloads and rebuilds must retain the selected language."""

from pathlib import Path
import shutil
import sys

import pandas as pd
import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import rebuild_downloads as rebuild
import validate_dataset as validator
from run_all_checks import run_scripted_checks

DATASET = 'livestock-losses-by-aimag'
PROJECT = Path(__file__).resolve().parents[2] / 'data.mn'
LABELS = {'en': {'csv': 'CSV (English)', 'xlsx': 'Excel (English)'},
          'mn': {'csv': 'CSV (Монгол)', 'xlsx': 'Excel (Монгол)'}}
PAGE = """---
excelLanguage: page
dataFiles:
  - path: /datasets/{dataset}-{lang}.csv
    format: csv
    label: {csv}
  - path: /datasets/{dataset}-{lang}.xlsx
    format: xlsx
    label: {xlsx}
source:
  name: National Statistics Office of Mongolia
---
"""


@pytest.mark.parametrize('missing_language', [None, 'en', 'mn'])
def test_unified_runner_checks_both_page_language_workbooks(project, missing_language):
    # The old runner wrongly required an unlisted bilingual workbook and could
    # overlook a missing language-specific download.
    legacy = project / f'public/datasets/{DATASET}.xlsx'
    legacy.unlink(missing_ok=True)
    if missing_language:
        (project / f'public/datasets/{DATASET}-{missing_language}.xlsx').unlink()
    checks = [c for c in run_scripted_checks(DATASET, project) if c.check_id.startswith('1.5')]
    assert len(checks) == 2
    assert [c.check_id for c in checks if not c.passed] == (
        [f'1.5-{missing_language.upper()}'] if missing_language else [])


@pytest.fixture
def project(tmp_path):
    datasets = tmp_path / 'public/datasets'
    datasets.mkdir(parents=True)
    for source in (PROJECT / 'public/datasets').glob(f'{DATASET}*'):
        shutil.copyfile(source, datasets / source.name)
    # Pages are written, not copied: live frontmatter gets edited for reasons
    # unrelated to downloads (e.g. its labels were dropped).
    for lang, labels in LABELS.items():
        page = tmp_path / f'src/data/data/{lang}/{DATASET}.mdx'
        page.parent.mkdir(parents=True)
        page.write_text(PAGE.format(dataset=DATASET, lang=lang, **labels))
    return tmp_path


@pytest.mark.parametrize('problem', ['none', 'wrong-link', 'extra-sheet', 'missing-file',
                                    'mixed-modes', 'changed-cells'])
def test_language_download_validation(project, monkeypatch, problem):
    page = project / f'src/data/data/mn/{DATASET}.mdx'
    if problem == 'wrong-link':
        page.write_text(page.read_text().replace(f'{DATASET}-mn.xlsx', f'{DATASET}-en.xlsx'))
    elif problem == 'mixed-modes':
        page.write_text(page.read_text().replace('excelLanguage: page\n', ''))
    elif problem == 'missing-file':
        (project / f'public/datasets/{DATASET}-mn.xlsx').unlink()
    elif problem == 'extra-sheet':
        original = validator.openpyxl.load_workbook

        def load(path, **kwargs):
            # Simulate a stale bilingual download without writing a workbook.
            if str(path).endswith('-mn.xlsx'):
                path = project / f'public/datasets/{DATASET}.xlsx'
            return original(path, **kwargs)

        monkeypatch.setattr(validator.openpyxl, 'load_workbook', load)
    elif problem == 'changed-cells':
        original = pd.read_excel

        def read(path, **kwargs):
            frame = original(path, **kwargs)
            if str(path).endswith('-mn.xlsx'):
                # Keep the total unchanged: checks must compare individual cells.
                frame.iloc[0, 1] += 1
                frame.iloc[1, 1] -= 1
            return frame

        monkeypatch.setattr(pd, 'read_excel', read)
    errors = [error for result in validator.validate_downloads(DATASET, str(project))
              for error in result.errors]
    assert bool(errors) == (problem != 'none'), errors


@pytest.mark.parametrize('mode', ['page', 'bilingual'])
def test_rebuild_preserves_download_language(project, monkeypatch, mode):
    monkeypatch.setattr(rebuild, 'DATASETS', project / 'public/datasets')
    monkeypatch.setattr(rebuild, 'MDX_EN', project / 'src/data/data/en')
    monkeypatch.setattr(rebuild, 'MDX_MN', project / 'src/data/data/mn')
    if mode == 'bilingual':
        for lang in ('en', 'mn'):
            page = project / f'src/data/data/{lang}/{DATASET}.mdx'
            page.write_text(page.read_text().replace('excelLanguage: page\n', ''))
    writes = []
    monkeypatch.setattr(rebuild, 'write_xlsx',
                        lambda path, sheets, **kwargs: writes.append((path.name, [s[0] for s in sheets])))
    report = rebuild.process_dataset(DATASET, apply=True)
    assert report['queue'] == 'auto', report
    expected = [(f'{DATASET}-en.xlsx', ['English']), (f'{DATASET}-mn.xlsx', ['Монгол'])]
    assert writes == (expected if mode == 'page' else [(f'{DATASET}.xlsx', ['English', 'Монгол'])])
    for lang in ('en', 'mn'):
        page = (project / f'src/data/data/{lang}/{DATASET}.mdx').read_text()
        filename = f'{DATASET}-{lang}.xlsx' if mode == 'page' else f'{DATASET}.xlsx'
        assert f'/datasets/{filename}' in page
        # Rebuilds preserve the site's explicit labels.
        files = yaml.safe_load(page.split('---', 2)[1])['dataFiles']
        assert {f['format']: f.get('label') for f in files} == LABELS[lang]
