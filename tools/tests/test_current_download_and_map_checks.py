"""Regressions for current download standards and bilingual choropleths."""

from pathlib import Path
import json

import pandas as pd
import pytest

from run_all_checks import check_csv_language, run_scripted_checks
from test_ai_checks import check_5_5_wide_form
from validate_dataset import validate_chart_csv_consistency


@pytest.mark.parametrize('language', ['en', 'mn'])
def test_map_lookup_language(language):
    spec = {
        'data': {'url': '/maps/mongolia-aimags.json'},
        'transform': [{'lookup': 'properties.name', 'from': {
            'data': {'url': f'/datasets/example-latest-{language}.csv'}, 'key': 'region',
        }}],
    }
    assert check_csv_language(spec, language)[0]
    other = 'mn' if language == 'en' else 'en'
    assert not check_csv_language(spec, other)[0]


def test_layered_chart_cannot_hide_wrong_language():
    spec = {'data': {'url': '/datasets/example-en.csv'}, 'layer': [
        {'data': {'url': '/datasets/another-mn.csv'}},
    ]}
    assert not check_csv_language(spec, 'en')[0]


def test_geometry_without_csv_fails():
    assert not check_csv_language({'data': {'url': '/maps/example.json'}}, 'en')[0]


@pytest.mark.parametrize('frame,expected', [
    (pd.DataFrame({'year': [2024, 2025], 'A': [10, 20], 'B': [30, 40]}), True),
    (pd.DataFrame({'он': [2024, 2025], 'А': [10, 20]}), True),
    (pd.DataFrame({'year': [2024, 2024], 'region': ['A', 'B'], 'value': [10, 20]}), False),
    (pd.DataFrame({'region': ['A', 'B'], '2024': [10, 20], '2025': [30, 40]}), False),
    (pd.DataFrame({'year': [2024, None], 'A': [10, 20]}), False),
])
def test_workbook_orientation(monkeypatch, frame, expected):
    monkeypatch.setattr(pd, 'read_excel', lambda _: frame)
    assert check_5_5_wide_form(Path('example.xlsx'))[0] is expected


@pytest.mark.parametrize('layered', [False, True])
@pytest.mark.parametrize('color,expected', [
    ({'field': 'value', 'type': 'quantitative', 'scale': {'domain': [0, 100]}}, True),
    ({'field': 'region', 'type': 'nominal', 'scale': {'domain': ['A', 'B']}}, True),
    ({'field': 'region', 'type': 'nominal', 'scale': {'domain': ['X', 'Y']}}, False),
])
def test_continuous_color_bounds_are_not_category_names(tmp_path, layered, color, expected):
    charts, datasets = tmp_path / 'public/charts', tmp_path / 'public/datasets'
    charts.mkdir(parents=True)
    datasets.mkdir(parents=True)
    chart, csv = charts / 'example-en.json', datasets / 'example-en.csv'
    encoding = {'encoding': {'color': color}}
    chart.write_text(json.dumps({'layer': [encoding]} if layered else encoding))
    csv.write_text('year,region,value\n2024,A,12\n2024,B,30\n')
    cross_check = validate_chart_csv_consistency(str(chart), str(csv))
    assert (not cross_check.errors) is expected
    category_checks = [r for r in run_scripted_checks('example', tmp_path) if r.check_id == '7.2']
    assert all(r.passed for r in category_checks) is expected
    if color['type'] == 'nominal':
        assert len(category_checks) == 1
