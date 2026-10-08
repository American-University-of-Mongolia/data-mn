"""Keep every published migration count traceable to the bilingual NSO snapshot."""

import csv
import json
from pathlib import Path

import openpyxl
import pytest

ROOT = Path(__file__).resolve().parents[2]
SLUG = 'internal-migration-by-aimag'
RAW = ROOT / 'tools/versions' / SLUG / 'v1/raw'
DATA = ROOT / 'data.mn/public/datasets'


@pytest.mark.parametrize('lang', ['en', 'mn'])
def test_source_to_chart_download_and_workbook(lang):
    meta = json.loads((RAW / f'metadata-{lang}.json').read_text())
    raw = json.loads((RAW / f'data-{lang}.json').read_text())
    values = {tuple(r['key']): int(r['values'][0]) for r in raw['data']}
    _, geography, time = meta['variables']
    names = dict(zip(geography['values'], geography['valueTexts']))
    years = dict(zip(time['valueTexts'], time['values']))
    places = {names[code]: code for code in geography['values'] if len(code) == 3}
    with (DATA / f'{SLUG}-{lang}.csv').open() as file:
        rows = list(csv.reader(file))[1:]
    assert len(rows) == 946
    chart = {}
    for year, name, incoming, outgoing, net in rows:
        expected_in = values['0', places[name], years[year]]
        expected_out = values['1', places[name], years[year]]
        assert [int(incoming), int(outgoing), int(net)] == [
            expected_in, expected_out, expected_in - expected_out]
        chart[int(year), name] = [expected_in, expected_out, expected_in - expected_out]

    labels = (['Arrivals', 'Departures', 'Net migration (people)'] if lang == 'en'
              else ['Шилжин ирсэн', 'Шилжин явсан', 'Цэвэр шилжилт (хүн)'])
    expected = {(year, f'{place} — {label}'): values[i]
                for (year, place), values in chart.items()
                for i, label in enumerate(labels)}
    with (DATA / f'{SLUG}-all-{lang}.csv').open() as file:
        download = list(csv.reader(file))[1:]
    assert len(download) == len(expected) == 2838
    assert {(int(y), category): int(value) for y, category, value in download} == expected

    workbook = openpyxl.load_workbook(DATA / f'{SLUG}-{lang}.xlsx', data_only=True)
    assert workbook.sheetnames == (['English'] if lang == 'en' else ['Монгол'])
    sheet = workbook.active
    headers, *wide = list(sheet.values)
    assert len(wide) == 43 and len(headers) == 67
    assert sheet.freeze_panes == 'B2'
    assert {(row[0], category): row[i+1] for row in wide
            for i, category in enumerate(headers[1:])} == expected


@pytest.mark.parametrize('lang', ['en', 'mn'])
def test_full_history_controls_and_fixed_map_scale(lang):
    directory = ROOT / 'data.mn/public/charts'
    map_spec = json.loads((directory / f'{SLUG}-{lang}.json').read_text())
    trend = json.loads((directory / f'{SLUG}-trend-{lang}.json').read_text())
    assert map_spec['params'][0]['bind']['min'] == 1983
    assert map_spec['params'][0]['bind']['max'] == 2025
    assert trend['encoding']['x']['scale']['domain'] == [1983, 2025]
    assert '2020' not in json.dumps(trend['transform'])
    with (DATA / f'{SLUG}-{lang}.csv').open() as file:
        maximum = max(abs(int(r[-1])) for r in list(csv.reader(file))[1:])
    assert map_spec['encoding']['color']['scale']['domain'] == [-maximum, maximum]
