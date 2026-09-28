"""Language-switch downloads and rebuilds must retain the selected language."""

from pathlib import Path
import shutil
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import rebuild_downloads as rebuild
import validate_dataset as validator

DATASET = 'livestock-losses-by-aimag'
PROJECT = Path(__file__).resolve().parents[2] / 'data.mn'


@pytest.fixture
def project(tmp_path):
    for folder, pattern in [('public/datasets', f'{DATASET}*'),
                            ('src/data/data/en', f'{DATASET}.mdx'),
                            ('src/data/data/mn', f'{DATASET}.mdx')]:
        target = tmp_path / folder
        target.mkdir(parents=True)
        for source in (PROJECT / folder).glob(pattern):
            shutil.copyfile(source, target / source.name)
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
        assert 'label:' in page  # Rebuilds preserve the site's explicit labels.
