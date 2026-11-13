"""Build the Data.mn income composition dataset from its archived snapshot."""
import argparse
import csv
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'data.mn'
SLUG = 'household-income-sources'
PARSER = argparse.ArgumentParser(description=__doc__)
PARSER.add_argument('--version', type=int, default=1)
PARSER.add_argument('--end-year', type=int, default=2025)
PARSER.add_argument('--register', action='store_true')
ARGS = PARSER.parse_args()
if ARGS.version < 1 or ARGS.end_year < 2007:
    PARSER.error('version must be positive and end-year must be at least 2007')
VERSION = ROOT / 'tools/versions' / SLUG / f'v{ARGS.version}'
RAW = VERSION / 'raw'
YEARS = list(range(2007, ARGS.end_year + 1))
COUNT = len(YEARS) * 24
TABLE = 'DT_NSO_1900_003V1.px'
COLORS = ['#2563eb', '#b45309', '#15803d', '#7c3aed', '#be185d', '#0e7490']
COMPONENTS = ['2', '3', '4', '5', '6', '7']


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def source_url(lang):
    return f'https://data.1212.mn/pxweb/{lang}/NSO/NSO__Society%2C%20development__Household%20income%20and%20expenditure/{TABLE}/'


def load(lang):
    meta = json.loads((RAW / f'{lang}-metadata.json').read_text())
    data = json.loads((RAW / f'{lang}-data.json').read_text())
    variables = meta['variables']
    assert data['id'] == [v['code'] for v in variables]
    assert data['size'][:2] == [3, 8]
    assert data['size'][2] == len(variables[2]['values'])
    for v in variables:
        assert data['dimension'][v['code']]['category']['index'] == {c: i for i, c in enumerate(v['values'])}
    labels = [dict(zip(v['values'], [t.strip() for t in v['valueTexts']])) for v in variables]
    values = data['value']
    if isinstance(values, dict):
        values = [values.get(str(i)) for i in range(math.prod(data['size']))]
    return labels, dict(zip(itertools.product(*(v['values'] for v in variables)), values))


def main():
    manifest = json.loads((RAW / 'manifest.json').read_text())
    for name, digest in manifest['files'].items():
        assert hashlib.sha256((RAW / name).read_bytes()).hexdigest() == digest
    sources = {lang: load(lang) for lang in ('en', 'mn')}
    assert sources['en'][1] == sources['mn'][1]
    labels, cells = sources['en']
    years = sorted([y for y in labels[2] if 2007 <= int(labels[2][y]) <= ARGS.end_year], key=lambda y: int(labels[2][y]))
    places = ['0', '1', '2']
    assert [int(labels[2][y]) for y in years] == YEARS
    for p, y in itertools.product(places, years):
        values = [cells[p, s, y] for s in labels[1]]
        assert all(isinstance(v, (int, float)) and math.isfinite(v) and 0 <= v <= 100 for v in values)
        assert cells[p, '0', y] == 100
        assert abs(sum(cells[p, s, y] for s in COMPONENTS) - 100) < 1e-8
        assert abs(sum(cells[p, s, y] for s in COMPONENTS[:4]) - cells[p, '1', y]) < 1e-8
    payload = {}
    for lang, (labels, cells) in sources.items():
        en = lang == 'en'
        j = lambda v: json.dumps(v, ensure_ascii=False)
        year, series, val = ('year', 'series', 'share_pct') if en else ('он', 'үзүүлэлт', 'эзлэх_хувь')
        place = labels[0]
        income = {s: name.removeprefix('1. ').removeprefix('2. ').removeprefix('3. ') for s, name in labels[1].items()}
        rows = [[int(labels[2][y]), place[p] + ' / ' + income[s], cells[p, s, y]]
                for y in years for p in places for s in labels[1]]
        csv_path = SITE / f'public/datasets/{SLUG}-{lang}.csv'
        with csv_path.open('w', newline='', encoding='utf-8') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerow([year, series, val])
            w.writerows(rows)
        (VERSION / f'data-{lang}.csv').write_bytes(csv_path.read_bytes())
        columns = sorted(r[1] for r in rows if r[0] == 2007)
        index = {(r[0], r[1]): r[2] for r in rows}
        payload[lang] = {'columns': [year, *columns], 'rows': [[y, *[index[y, c] for c in columns]] for y in YEARS], 'source': source_url(lang), 'note': (f'Source: NSO Household Socio-Economic Survey, {TABLE}. {source_url(lang)}\nShare of average monthly total household income, percent (0–100). Includes total income and monetary subtotal: do not sum all eight series. Non-cash income includes food consumed from own farming.' if en else f'Эх сурвалж: ҮСХ, Өрхийн нийгэм, эдийн засгийн судалгаа, {TABLE}. {source_url(lang)}\nНэг өрхийн сарын дундаж нийт орлогод эзлэх хувь (0–100). Нийт орлого болон мөнгөн орлогын дүн орсон тул найман үзүүлэлтийг бүгдийг нь нэмж болохгүй. Мөнгөн бус орлогод өөрийн аж ахуйгаас хэрэглэсэн хүнсний үнэлгээ багтана.')}
        names = [income[s] for s in COMPONENTS]
        base = {'$schema': 'https://vega.github.io/schema/vega-lite/v5.json',
                'data': {'url': f'/datasets/{SLUG}-{lang}.csv', 'format': {'type': 'csv', 'parse': {year: 'number', val: 'number'}}},
                'config': {'axis': {'labelFontSize': 14, 'titleFontSize': 16, 'titlePadding': 12, 'labelColor': '#64748b', 'titleColor': '#334155'},
                           'legend': {'labelFontSize': 13}, 'view': {'stroke': None}}}
        decode = [{'calculate': f'split(datum[{j(series)}], " / ")[0]', 'as': 'place'},
                  {'calculate': f'split(datum[{j(series)}], " / ")[1]', 'as': 'income'},
                  {'calculate': f'indexof({j(names)}, datum.income)', 'as': 'sourceOrder'},
                  {'filter': 'datum.sourceOrder >= 0'}]
        tip = [{'field': year, 'type': 'quantitative', 'title': 'Year' if en else 'Он', 'format': 'd'},
               {'field': 'place', 'type': 'nominal', 'title': 'Location' if en else 'Байршил'},
               {'field': 'income', 'type': 'nominal', 'title': 'Income source' if en else 'Орлогын эх үүсвэр'},
               {'field': val, 'type': 'quantitative', 'title': 'Share (%)' if en else 'Эзлэх хувь (%)', 'format': '.1f'}]
        share_title = 'Share of total income (%)' if en else 'Нийт орлогод эзлэх хувь (%)'
        stack = {**base, 'description': 'Household income composition, national, urban and rural, 2007–2025.' if en else 'Өрхийн орлогын бүтэц, улсын дундаж, хот, хөдөө, 2007–2025.',
                 'params': [{'name': 'selectedYear', 'value': ARGS.end_year, 'bind': {'input': 'select', 'options': list(reversed(YEARS)), 'name': 'Year: ' if en else 'Он: '}}],
                 'transform': decode + [{'filter': f'datum[{j(year)}] === selectedYear'},
                      {'stack': val, 'groupby': ['place'], 'sort': [{'field': 'sourceOrder', 'order': 'ascending'}], 'as': ['y0', 'y1']},
                      {'calculate': '(datum.y0 + datum.y1) / 2', 'as': 'mid'}],
                 'encoding': {'x': {'field': 'place', 'type': 'nominal', 'title': None, 'sort': list(place.values()), 'axis': {'labelAngle': 0, 'labelLimit': 140}, 'scale': {'padding': 0.32}}},
                 'layer': [
                     {'mark': {'type': 'bar'}, 'encoding': {
                         'y': {'field': 'y1', 'type': 'quantitative', 'title': share_title, 'scale': {'domain': [0, 100], 'nice': False}, 'axis': {'values': [0, 25, 50, 75, 100], 'format': '.0f'}},
                         'y2': {'field': 'y0'}, 'color': {'field': 'income', 'type': 'nominal', 'scale': {'domain': names, 'range': COLORS}, 'legend': None}, 'tooltip': tip}},
                     {'transform': [{'filter': f'datum[{j(val)}] >= 7'}], 'mark': {'type': 'text', 'fill': '#ffffff', 'fontWeight': 'bold', 'fontSize': 12},
                      'encoding': {'y': {'field': 'mid', 'type': 'quantitative'}, 'text': {'field': val, 'type': 'quantitative', 'format': '.1f'}, 'tooltip': tip}}
                 ]}
        stack['description'] = stack['description'].replace('2007–2025', f'2007–{ARGS.end_year}')
        dump(SITE / f'public/charts/{SLUG}-{lang}.json', stack)
        all_places = 'All locations' if en else 'Бүх байршил'
        trend = {**base, 'description': 'Income source shares over time, 2007–2025.' if en else 'Орлогын эх үүсвэрийн эзлэх хувийн өөрчлөлт, 2007–2025.',
                 'params': [{'name': 'selectedSource', 'value': names[0], 'bind': {'input': 'select', 'options': names, 'labels': (['Wages and salaries', 'Pensions and allowances', 'Household businesses', 'Other income', 'Received free of charge', 'Food from own farming'] if en else ['Цалин хөлс', 'Тэтгэвэр, тэтгэмж', 'Өрхийн үйлдвэрлэл, үйлчилгээ', 'Бусад орлого', 'Бусдаас үнэгүй авсан', 'Өөрийн аж ахуйн хүнс']), 'name': 'Income source: ' if en else 'Орлогын эх үүсвэр: '}},
                            {'name': 'selectedLocation', 'value': all_places, 'bind': {'input': 'select', 'options': [all_places, *place.values()], 'name': 'Location: ' if en else 'Байршил: '}}],
                 'transform': decode + [{'filter': f'datum.income === selectedSource && (selectedLocation === {j(all_places)} || datum.place === selectedLocation)'}],
                 'layer': [{'mark': {'type': 'line', 'strokeWidth': 2.5, 'point': {'filled': True, 'size': 28}}},
                           {'params': [{'name': 'hover', 'select': {'type': 'point', 'nearest': True, 'on': 'pointerover', 'clear': 'pointerout'}}],
                            'mark': {'type': 'point', 'filled': True, 'size': 100},
                            'encoding': {'opacity': {'condition': {'param': 'hover', 'empty': False, 'value': 1}, 'value': 0}, 'tooltip': tip}}],
                 'encoding': {'x': {'field': year, 'type': 'quantitative', 'title': 'Year' if en else 'Он', 'scale': {'domain': [2007, ARGS.end_year], 'zero': False, 'nice': False}, 'axis': {'values': sorted({2007, *range(2010, ARGS.end_year + 1, 5), ARGS.end_year}), 'format': 'd', 'grid': False}},
                              'y': {'field': val, 'type': 'quantitative', 'title': share_title, 'scale': {'domain': [0, 100], 'nice': False}, 'axis': {'values': [0, 25, 50, 75, 100], 'format': '.0f'}},
                              'color': {'field': 'place', 'type': 'nominal', 'title': None, 'scale': {'domain': list(place.values()), 'range': ['#64748b', '#2563eb', '#b45309']}, 'legend': {'orient': 'top'}},
                              'strokeDash': {'condition': {'test': f'datum.place === {j(place["0"])}', 'value': [6, 4]}, 'value': [1, 0]}, 'tooltip': tip}}
        trend['description'] = trend['description'].replace('2007–2025', f'2007–{ARGS.end_year}')
        dump(SITE / f'public/charts/{SLUG}-trend-{lang}.json', trend)
        front = {'title': 'Household Income Sources in Mongolia: Urban vs Rural (2007–2025)' if en else 'Өрхийн орлогын бүтэц: хот, хөдөө (2007–2025)',
                 'publishDate': '2026-11-07',
                 'excerpt': 'Explore how wages, pensions, household businesses and non-cash sources contribute to household income. In 2025, wages accounted for 62.7% of urban income and 32.8% of rural income.' if en else 'Цалин хөлс, тэтгэвэр, тэтгэмж, өрхийн үйлдвэрлэл, үйлчилгээ болон мөнгөн бус орлогын эзлэх хувийг харьцуулна уу. 2025 онд цалин хөлс хотын өрхийн нийт орлогын 62.7%, хөдөөгийн өрхийн орлогын 32.8%-ийг бүрдүүлжээ.',
                 'category': 'Household & Income' if en else 'Өрх ба орлого',
                 'tags': ['mongolia', 'household', 'income', 'urban', 'rural'] if en else ['монгол', 'өрх', 'орлого', 'хот', 'хөдөө'],
                 'keywords': ['income sources', 'wages', 'pensions', 'household businesses'] if en else ['орлогын бүтэц', 'цалин хөлс', 'тэтгэвэр тэтгэмж', 'өрхийн үйлдвэрлэл үйлчилгээ'],
                 'author': 'Data.mn', 'dataVersion': ARGS.version, 'dataDate': f'{ARGS.end_year}-12-31', 'excelLanguage': 'page', 'dataFiles': [],
                 'source': {'name': 'National Statistics Office of Mongolia' if en else 'Үндэсний статистикийн хороо', 'url': source_url(lang), 'tableId': TABLE}}
        front['title'] = front['title'].replace('2007–2025', f'2007–{ARGS.end_year}')
        urban, rural = cells['1', '2', years[-1]], cells['2', '2', years[-1]]
        front['excerpt'] = (f'Explore how wages, pensions, household businesses and non-cash sources contribute to household income. In {ARGS.end_year}, wages accounted for {urban:.1f}% of urban income and {rural:.1f}% of rural income.' if en else
                            f'Цалин хөлс, тэтгэвэр, тэтгэмж, өрхийн үйлдвэрлэл, үйлчилгээ болон мөнгөн бус орлогын эзлэх хувийг харьцуулна уу. {ARGS.end_year} онд цалин хөлс хотын өрхийн нийт орлогын {urban:.1f}%, хөдөөгийн өрхийн орлогын {rural:.1f}%-ийг бүрдүүлжээ.')
        for ext in ('csv', 'xlsx'):
            p = SITE / f'public/datasets/{SLUG}-{lang}.{ext}'
            front['dataFiles'].append({'path': f'/datasets/{p.name}', 'format': ext, 'size': f'{p.stat().st_size / 1024:.1f} KB' if p.exists() else '10 KB',
                                       'description': ('Download all data' if en else 'Бүх өгөгдлийг татах') + f' ({ext.upper()})'})
        method = ('Shares of average monthly household total income, as published by NSO’s Household Socio-Economic Survey. Unit: percent. The national figure is the official survey estimate, not a simple average of urban and rural values. Source updated 29 May 2026; retrieved 7 November 2026.\n\nTotal income includes monetary income, the value of items received free of charge, and food consumed from own farming. Wages, pensions and allowances, household businesses and other monetary income make up the monetary subtotal. Charts show only the six mutually exclusive components; totals and subtotals are excluded from the stack. These shares do not measure the percentage of households receiving each income source.\n\nThis page focuses on 2007–2025. All 456 observations in this selected period are present. The source extends to 1997, with missing non-cash components in 1997–1999; the complete source response is archived separately. Published historical values are retained without interpolation. The table does not provide uncertainty intervals or a complete account of survey-design changes, so long-run comparisons should be interpreted with that limitation.\n\nEach download contains the full 2007–2025 page coverage: 19 years, three locations and eight source series (including total income and the monetary subtotal). CSV has one observation per row; Excel has years down rows and location/source combinations across columns. Values are percentages on a 0–100 scale. Chart selections do not limit downloads.' if en else
                  'ҮСХ-ны Өрхийн нийгэм, эдийн засгийн судалгаагаар нийтэлсэн нэг өрхийн сарын дундаж нийт орлогын бүтэц. Хэмжих нэгж: хувь. Улсын дундаж нь хот, хөдөөгийн утгын энгийн дундаж биш, судалгааны албан ёсны тооцоо юм. Эх сурвалжийг 2026 оны 5 дугаар сарын 29-нд шинэчилсэн; 2026 оны 11 дүгээр сарын 7-нд татав.\n\nНийт орлогод мөнгөн орлого, бусдаас үнэгүй авч хэрэглэсэн зүйлийн мөнгөн үнэлгээ, өөрийн аж ахуйгаас хэрэглэсэн хүнсний бүтээгдэхүүний үнэлгээ багтана. Цалин хөлс, тэтгэвэр, тэтгэмж, өрхийн үйлдвэрлэл, үйлчилгээний орлого болон бусад мөнгөн орлого нь мөнгөн орлогын дүнг бүрдүүлнэ. Графикт давхардаагүй зургаан бүрэлдэхүүнийг харуулж, нийт орлого болон мөнгөн орлогын дүнг давхар нэмж оруулаагүй. Эдгээр нь тухайн орлогыг авдаг өрхийн хувь биш, нийт орлогод эзлэх хувь юм.\n\nЭнэ хуудас 2007–2025 оныг хамарна. Сонгосон хугацааны 456 утга бүрэн байна. Эх хүснэгт 1997 оноос эхлэх боловч 1997–1999 оны мөнгөн бус орлогын зарим утга дутуу; эх хариуг бүтнээр нь тусад нь хадгалсан. Нийтэлсэн утгыг нөхөлт, тэгшитгэлгүйгээр ашиглав. Хүснэгтэд итгэх интервал болон судалгааны загварын өөрчлөлтийн бүрэн тайлбар байхгүй тул олон жилийн өөрчлөлтийг тайлбарлахдаа үүнийг харгалзана.\n\nТатах файл бүр хуудасны 2007–2025 оны бүх өгөгдлийг агуулна: 19 он, гурван байршил, нийт орлого болон мөнгөн орлогын дүнг багтаасан найман үзүүлэлт. CSV-ийн нэг мөр нэг утга агуулна. Excel-д онууд мөрөөр, байршил ба орлогын төрлийн хослолууд баганаар байрлана. Утгыг 0–100 хэмжээсээр, хувиар илэрхийлсэн. Графикийн сонголт татах файлын хамрах хүрээг хязгаарлахгүй.')
        method = method.replace('2007–2025', f'2007–{ARGS.end_year}').replace('456', str(COUNT)).replace('19 years', f'{len(YEARS)} years').replace('19 он', f'{len(YEARS)} он')
        method = method.replace('29 May 2026', manifest['source_updated_at'][:10]).replace('7 November 2026', manifest['snapshot_date']).replace('2026 оны 5 дугаар сарын 29', manifest['source_updated_at'][:10]).replace('2026 оны 11 дүгээр сарын 7', manifest['snapshot_date'])
        body = '---\n' + '\n'.join(f'{k}: {v if k in ("publishDate", "dataDate") else j(v)}' for k, v in front.items())
        body += '\nmethodology: |\n' + '\n'.join('  ' + line if line else '' for line in method.split('\n')) + '\n---\n\n'
        body += "import DatasetChart from '~/components/ui/DatasetChart.astro';\n\n"
        body += f"import incomeSpec from '../../../../public/charts/{SLUG}-{lang}.json';\n\n"
        title = 'Where does household income come from?' if en else 'Өрхийн орлого юунаас бүрддэг вэ?'
        caption = 'Each bar totals 100%. Labels show shares of 7% or more; hover or tap for every value.' if en else 'Багана бүрийн нийлбэр 100%. 7% ба түүнээс дээш утгыг бичсэн. Бүх утгыг харахын тулд дээр нь заах буюу товшино уу.'
        body += f'<DatasetChart spec={{incomeSpec}} title="{title}" caption="{caption}" aspectRatio={{0.6}} legend={{incomeSpec.layer[0].encoding.color.scale}} />\n\n'
        body += ('<div className="my-4 text-sm text-gray-600 dark:text-gray-300">Total income includes non-cash items, such as food produced and consumed by the household. The percentages describe the income mix, not how many households receive each source.</div>\n\n' if en else '<div className="my-4 text-sm text-gray-600 dark:text-gray-300">Нийт орлогод өөрийн аж ахуйгаас хэрэглэсэн хүнс зэрэг мөнгөн бус орлогын үнэлгээ багтана. Хувь нь тухайн эх үүсвэрийн нийт орлогод эзлэх хэмжээг илэрхийлнэ.</div>\n\n')
        title = 'How has the income mix changed?' if en else 'Орлогын бүтэц хэрхэн өөрчлөгдсөн бэ?'
        caption = 'Choose an income source and compare locations. The dashed line shows the official national share.' if en else 'Орлогын эх үүсвэрээ сонгож, байршлуудыг харьцуулна уу. Тасархай шугам нь улсын дундаж үзүүлэлт.'
        body += f'<h2>{title}</h2>\n\n<DatasetChart spec="/charts/{SLUG}-trend-{lang}.json" title="" caption="{caption}" aspectRatio={{0.6}} />\n'
        (SITE / f'src/data/data/{lang}/{SLUG}.mdx').write_text(body)
    dump(ROOT / 'tools/temp/household-income-excel.json', payload)
    dump(VERSION / 'validation.json', {'observations_per_language': COUNT, 'years': [2007, ARGS.end_year], 'bilingual_values_equal': True, 'missing_values': 0, 'component_totals': 100, 'monetary_subtotals_verified': True, 'source_hashes_verified': True})
    if ARGS.register:
        sys.path.insert(0, str(ROOT / 'tools'))
        from registry.registry import Registry, Dataset, Version
        registry = Registry()
        pupil = registry.get_dataset('pupil-teacher-ratio')
        if not pupil or not pupil.is_published:
            raise SystemExit('Wait for PR #181 to merge and publish, then merge main before registering this dataset.')
        if registry.get_dataset(SLUG) is None:
            registry.add_dataset(Dataset(id=SLUG, source_id='nso-1212', name_en='Household income sources', name_mn='Өрхийн орлогын бүтэц',
                                         category_en='Household & Income', category_mn='Өрх ба орлого', definition_path=f'tools/sources/nso-1212/datasets/{SLUG}.md', source_ref=TABLE,
                                         source_path=manifest['source_path'], status='pending', auto_update=False, auto_publish=False,
                                         tags=['mongolia', 'household', 'income', 'urban', 'rural']))
        existing = registry.get_dataset(SLUG)
        assert existing.current_version <= ARGS.version, 'Refusing to downgrade the registry'
        matching = [v for v in registry.get_versions(SLUG, limit=10000) if v.version == ARGS.version]
        digest = hashlib.sha256((VERSION / 'data-en.csv').read_bytes()).hexdigest()
        assert not matching or matching[0].data_hash == digest, 'Existing version changed; create a new snapshot'
        registry.update_dataset(SLUG, current_version=ARGS.version, data_file=f'data.mn/public/datasets/{SLUG}-en.csv', mdx_file_en=f'data.mn/src/data/data/en/{SLUG}.mdx',
                                mdx_file_mn=f'data.mn/src/data/data/mn/{SLUG}.mdx', chart_spec=f'data.mn/public/charts/{SLUG}-en.json', data_as_of=f'{ARGS.end_year}-12-31',
                                source_updated_at=manifest['source_updated_at'], last_fetched_at=manifest['retrieved_at'], canonical_slug=SLUG,
                                source_metadata={'unit': 'percent (0–100)', 'frequency': 'annual', 'years': [2007, ARGS.end_year], 'locations': 3, 'income_series': 8})
        if not matching:
            registry.add_version(Version(id=0, dataset_id=SLUG, version=ARGS.version, data_hash=digest,
                                         data_path=f'tools/versions/{SLUG}/v{ARGS.version}/data-en.csv', row_count=COUNT, column_count=3,
                                         change_type='initial' if ARGS.version == 1 else 'update', change_summary='Annual household income composition, national, urban and rural.',
                                         source_updated_at=manifest['source_updated_at'], source_raw_files=[f'tools/versions/{SLUG}/v{ARGS.version}/raw/{n}' for n in manifest['files']]))
    print(f'Built aligned bilingual CSVs ({COUNT} values each), four charts, two pages and Excel input.')


if __name__ == '__main__':
    main()
