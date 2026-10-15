"""Rebuild bilingual youth NEET pages and charts from the hash-checked NSO v1 snapshot.

Run with --register once to add the pending dataset and version to the registry.
Use --skip-excel to keep existing, validated page-language workbooks unchanged.
"""
from pathlib import Path
import csv
import json
import hashlib
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'data.mn'
SLUG = 'youth-neet-rate'
TABLE = 'DT_NSO_0400_050V1.px'
VERSION = ROOT / 'tools/versions' / SLUG / 'v1'
RAW = VERSION / 'raw'
manifest = json.loads((RAW / 'manifest.json').read_text())
for name, digest in manifest['files'].items():
    assert hashlib.sha256((RAW / name).read_bytes()).hexdigest() == digest, name

def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def source_url(lang):
    return f'https://data.1212.mn/pxweb/{lang}/NSO/NSO__Labour%2C%20business__Decent%20work/{TABLE}/'

payload = {}
for lang in ['en', 'mn']:
    metadata = json.loads((RAW / f'{lang}-metadata.json').read_text())
    data = json.loads((RAW / f'{lang}-data.json').read_text())
    indicators, years = metadata['variables']
    assert data['id'] == [indicators['code'], years['code']]
    assert data['size'] == [10, 17]
    assert indicators['values'] == [str(i) for i in range(10)]
    assert sorted(map(int, years['valueTexts'])) == list(range(2009, 2026))
    for variable in metadata['variables']:
        index = data['dimension'][variable['code']]['category']['index']
        assert index == {code: i for i, code in enumerate(variable['values'])}
    values = data['value']
    if isinstance(values, dict):
        values = [values.get(str(i)) for i in range(170)]
    assert len(values) == 170
    assert all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in values)
    labels = {code: label.strip() for code, label in zip(indicators['values'], indicators['valueTexts'])}
    if lang == 'mn':
        labels['4'] = 'Орон нутаг'  # Display wording only; raw NSO labels are retained.
    records = [
        {'year': int(year), 'code': code, 'indicator': labels[code], 'rate': values[i * 17 + j]}
        for i, code in enumerate(indicators['values'])
        for j, year in enumerate(years['valueTexts'])
    ]
    records.sort(key=lambda r: (r['year'], int(r['code'])))
    payload[lang] = {'records': records, 'labels': labels, 'source': source_url(lang)}

assert [(r['year'], r['code'], r['rate']) for r in payload['en']['records']] == [(r['year'], r['code'], r['rate']) for r in payload['mn']['records']]
config = {'axis': {'labelFontSize': 14, 'titleFontSize': 16, 'labelColor': '#64748b', 'titleColor': '#334155'}, 'legend': {'labelFontSize': 13, 'titleFontSize': 14}, 'view': {'stroke': 'transparent'}}
for lang in ['en', 'mn']:
    en = lang == 'en'
    records = payload[lang]['records']
    names = payload[lang]['labels']
    year, indicator, rate = ['year', 'indicator', 'rate_percent'] if en else ['он', 'үзүүлэлт', 'хувь']
    csvpath = SITE / f'public/datasets/{SLUG}-{lang}.csv'
    with csvpath.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([year, indicator, rate])
        writer.writerows([r['year'], r['indicator'], r['rate']] for r in records)
    base = {'$schema': 'https://vega.github.io/schema/vega-lite/v5.json', 'data': {'url': f'/datasets/{SLUG}-{lang}.csv', 'format': {'type': 'csv', 'parse': {year: 'number', rate: 'number'}}}, 'config': config}
    title = 'Mongolia Youth Not in Employment, Education or Training, % (2009–2025)' if en else 'Хөдөлмөр эрхлээгүй, боловсрол, сургалтад хамрагдаагүй залуучууд, хувь (2009–2025)'
    yearlabel = 'Year' if en else 'Он'
    ratelabel = 'Share of youth (%)' if en else 'Залуучуудын эзлэх хувь (%)'
    compare = ['By sex', 'Urban and rural'] if en else ['Хүйсээр', 'Хот, орон нутаг']
    tip = [{'field': year, 'type': 'quantitative', 'title': yearlabel, 'format': 'd'}, {'field': indicator, 'type': 'nominal', 'title': 'Group' if en else 'Бүлэг'}, {'field': rate, 'type': 'quantitative', 'title': ratelabel, 'format': '.1f'}]
    sexnames = [names[c] for c in ['0', '1', '2']]
    locnames = [names[c] for c in ['0', '3', '4']]
    spec = {**base, 'description': title + ('. Labour Force Survey rates using the currently published source weights. Full history and all ten groups are included in downloads.' if en else '. Ажиллах хүчний судалгааны одоо нийтэлсэн жинг ашигласан дүн. Татах файлд бүх он, бүх арван бүлэг багтсан.'),
        'params': [{'name': 'comparison', 'value': compare[0], 'bind': {'input': 'select', 'options': compare, 'name': 'Compare: ' if en else 'Харьцуулах: '}}],
        'transform': [{'filter': f'indexof(comparison === {json.dumps(compare[0],ensure_ascii=False)} ? {json.dumps(sexnames,ensure_ascii=False)} : {json.dumps(locnames,ensure_ascii=False)}, datum[{json.dumps(indicator)}]) >= 0'}],
        'encoding': {'x': {'field': year, 'type': 'quantitative', 'title': yearlabel, 'scale': {'domain': [2009, 2025], 'zero': False, 'nice': False}, 'axis': {'grid': False, 'format': 'd', 'values': [2009, 2013, 2017, 2021, 2025]}},
            'y': {'field': rate, 'type': 'quantitative', 'title': ratelabel, 'scale': {'zero': True}, 'axis': {'format': '.0f', 'tickCount': 5}},
            'color': {'field': indicator, 'type': 'nominal', 'title': None, 'sort': [names[str(i)] for i in range(5)], 'legend': {'orient': 'top', 'gridAlign': 'none', 'columnPadding': 24, 'rowPadding': 10}},
            'tooltip': tip},
        'layer': [{'mark': {'type': 'line', 'strokeWidth': 2.5}}, {'params': [{'name': 'hover', 'select': {'type': 'point', 'nearest': True, 'on': 'pointerover', 'clear': 'pointerout'}}], 'mark': {'type': 'point', 'filled': True, 'size': 90}, 'encoding': {'opacity': {'condition': {'param': 'hover', 'empty': False, 'value': 1}, 'value': 0}, 'tooltip': tip}}]}
    write_json(SITE / f'public/charts/{SLUG}-{lang}.json', spec)
    regions = [names[str(i)] for i in range(5, 10)]
    region_spec = {**base, 'description': ('Youth NEET rate by four major regions and Ulaanbaatar. Percent of the population aged 15–24 within each region. These are not aimag-level observations.' if en else 'Хөдөлмөр эрхлээгүй, боловсрол, сургалтад хамрагдаагүй 15–24 насны залуучуудын эзлэх хувь, дөрвөн бүс ба Улаанбаатараар. Аймгийн түвшний өгөгдөл биш.'),
        'params': [{'name': 'selectedYear', 'value': 2025, 'bind': {'input': 'range', 'min': 2009, 'max': 2025, 'step': 1, 'name': yearlabel + ': '}}],
        'transform': [{'filter': f'indexof({json.dumps(regions,ensure_ascii=False)}, datum[{json.dumps(indicator)}]) >= 0 && datum[{json.dumps(year)}] == selectedYear'}],
        'mark': {'type': 'bar', 'cornerRadiusEnd': 2},
        'encoding': {'y': {'field': indicator, 'type': 'nominal', 'sort': '-x', 'title': None}, 'x': {'field': rate, 'type': 'quantitative', 'title': ratelabel, 'scale': {'domain': [0, 40], 'nice': False}, 'axis': {'format': '.0f', 'tickCount': 5}}, 'color': {'field': indicator, 'type': 'nominal', 'scale': {'domain': regions, 'range': ['#4e79a7', '#f28e2b', '#59a14f', '#b07aa1', '#e15759']}, 'legend': None}, 'tooltip': tip}}
    write_json(SITE / f'public/charts/{SLUG}-regions-{lang}.json', region_spec)
    excerpt = ('Share of 15–24-year-olds who are not working or participating in education or training. The national rate was 9.1% in 2025, compared with 10.1% in 2024.' if en else 'Хөдөлмөр эрхлээгүй, боловсрол, сургалтад хамрагдаагүй 15–24 насны залуучуудын эзлэх хувь. Улсын дундаж 2024 онд 10.1%, 2025 онд 9.1% байв.')
    front = {'title': title, 'publishDate': '2026-10-14', 'excerpt': excerpt, 'category': 'Labor Market' if en else 'Хөдөлмөрийн зах зээл', 'tags': ['mongolia', 'youth', 'education', 'employment'] if en else ['монгол', 'залуучууд', 'боловсрол', 'хөдөлмөр'], 'keywords': ['Mongolia youth NEET rate', 'youth employment education training', 'urban rural youth', 'NEET'] if en else ['залуучуудын хөдөлмөр эрхлэлт', 'боловсрол сургалтад хамрагдаагүй залуучууд', 'хот орон нутаг', 'NEET'], 'author': 'Data.mn', 'dataVersion': 1, 'dataDate': '2025-12-31', 'excelLanguage': 'page', 'dataFiles': [{'path': f'/datasets/{SLUG}-{lang}.csv', 'format': 'csv', 'size': f'{csvpath.stat().st_size / 1024:.1f} KB', 'description': 'Download all 10 groups, 2009–2025' if en else 'Бүх 10 бүлгийн өгөгдөл, 2009–2025'}, {'path': f'/datasets/{SLUG}-{lang}.xlsx', 'format': 'xlsx', 'size': '6 KB', 'description': 'Open in Excel' if en else 'Excel татах'}], 'source': {'name': 'National Statistics Office of Mongolia' if en else 'Үндэсний статистикийн хороо', 'url': source_url(lang), 'tableId': TABLE}}
    body = '---\n' + '\n'.join(f'{k}: {v if k in ("publishDate", "dataDate") else json.dumps(v,ensure_ascii=False)}' for k,v in front.items()) + '\n---\n\n'
    body += "import VegaChart from '~/components/ui/VegaChart.astro';\n\n"
    trend_title = 'Youth outside employment, education or training' if en else 'Хөдөлмөр эрхлээгүй, суралцаагүй залуучууд'
    trend_caption = 'Ages 15–24. Use the comparison selector below the chart. Hover over a point for its value.' if en else '15–24 нас. Доорх сонголтоор харьцуулна уу. Цэг дээр заахад утга харагдана.'
    body += f'<VegaChart spec="/charts/{SLUG}-{lang}.json" title="{trend_title}" caption="{trend_caption}" prominentControls />\n\n'
    body += '<div role="note" className="text-sm text-slate-600 dark:text-slate-400 mt-3">' + ('NSO revised its 2019–2023 estimates after updating survey weights in 2024. The dataset uses the currently published values.' if en else 'ҮСХ 2024 онд судалгааны жинг шинэчилж, 2019–2023 оны дүнг засварласан. Энд одоо нийтэлсэн утгыг ашиглав.') + '</div>\n\n'
    regional_heading = 'Compare regions' if en else 'Бүсүүдийг харьцуулах'
    regional_title = 'Youth NEET rate by region' if en else 'Хөдөлмөр эрхлээгүй, суралцаагүй залуучууд, бүсээр'
    regional_caption = 'Four major regions and Ulaanbaatar. Select a year below; the 0–40% scale stays fixed.' if en else 'Дөрвөн бүс ба Улаанбаатар. Доороос оноо сонгоно уу. Хуваарь 0–40% тогтмол байна.'
    body += f'<h2>{regional_heading}</h2>\n\n<VegaChart spec="/charts/{SLUG}-regions-{lang}.json" title="{regional_title}" caption="{regional_caption}" aspectRatio={{0.6}} />\n\n'
    body += '<details className="mt-5"><summary>' + ('Definition and source notes' if en else 'Тодорхойлолт ба эх сурвалжийн тайлбар') + '</summary><div className="mt-3 text-sm leading-relaxed">'
    body += ('The NEET rate is the percentage of all young people aged 15–24 in each group who are neither employed nor in education or training. It includes those who are not looking for work, so it differs from the unemployment rate. Male, female, urban, rural and regional figures use their own youth populations as denominators and must not be added together. The data come from the Labour Force Survey; the source cites the labour-statistics methodology adopted in January 2019 and revised survey weights for 2019–2023. Trends alone do not explain why rates changed. CSV and Excel include all 10 groups and all 17 years. Excel uses years as rows, groups as columns, and the language of this page. Values are percentages, so 9.1 means 9.1%.' if en else 'Энэ үзүүлэлт нь тухайн бүлгийн нийт 15–24 насны залуучуудаас хөдөлмөр эрхлээгүй, боловсрол, сургалтад хамрагдаагүй залуучуудын эзлэх хувь юм. Ажил хайхгүй байгаа хүмүүсийг мөн хамруулдаг тул ажилгүйдлийн түвшнээс ялгаатай. Хүйс, хот, орон нутаг, бүсийн үзүүлэлт бүрийг тухайн бүлгийн залуучуудын тоонд харьцуулсан тул хооронд нь нэмж болохгүй. Өгөгдөл нь Ажиллах хүчний судалгаанаас авсан. Эх сурвалжид 2019 оны 1-р сард баталсан хөдөлмөрийн статистикийн аргачлал болон 2019–2023 оны шинэчилсэн жинг дурдсан. Түвшний өөрчлөлт нь шалтгааныг дангаараа тайлбарлахгүй. CSV, Excel файлд бүх 10 бүлэг, 17 оны өгөгдөл орсон. Excel-д онууд мөрөөр, бүлгүүд баганаар байрлах бөгөөд энэ хуудасны хэлээр байна. Утгууд хувиар илэрхийлэгдсэн тул 9.1 нь 9.1% гэсэн үг.')
    body += '</div></details>\n'
    # Match Data.mn's rule that dataset content ends with the last chart.
    details = body.index('<details')
    region_section = body.index('<h2>')
    body = body[:region_section] + body[details:] + '\n' + body[region_section:details]
    (SITE / f'src/data/data/{lang}/{SLUG}.mdx').write_text(body.rstrip() + '\n')

for lang in ['en', 'mn']:
    shutil.copy2(SITE / f'public/datasets/{SLUG}-{lang}.csv', VERSION / f'data-{lang}.csv')
if '--skip-excel' not in sys.argv:
    from rebuild_downloads import process_dataset
    result = process_dataset(SLUG, apply=True)
    assert result['queue'] == 'auto', result
write_json(VERSION / 'validation.json', {'source_hashes_verified': True, 'bilingual_values_identical': True, 'observations_per_language': 170, 'years': [2009, 2025], 'missing_values': 0})

if '--register' in sys.argv:
    sys.path.insert(0, str(ROOT / 'tools'))
    from registry.registry import Registry, Dataset, Version
    registry = Registry()
    if registry.get_dataset(SLUG) is None:
        registry.add_dataset(Dataset(id=SLUG, source_id='nso-1212', name_en='Youth not in employment, education or training', name_mn='Хөдөлмөр эрхлээгүй, боловсрол, сургалтад хамрагдаагүй залуучууд', category_en='Labor Market', category_mn='Хөдөлмөрийн зах зээл', definition_path=f'tools/sources/nso-1212/datasets/{SLUG}.md', source_ref=TABLE, source_path=manifest['source_path'], tags=['mongolia', 'youth', 'education', 'employment'], status='pending', auto_update=False, auto_publish=False, source_metadata={'frequency': 'annual', 'unit': 'percent', 'years': [2009, 2025], 'groups': 10, 'limitations': '2019–2023 revised following the 2024 sampling-weight update; subgroup denominators differ.'}))
        registry.update_dataset(SLUG, current_version=1, data_file=f'data.mn/public/datasets/{SLUG}-en.csv', mdx_file_en=f'data.mn/src/data/data/en/{SLUG}.mdx', mdx_file_mn=f'data.mn/src/data/data/mn/{SLUG}.mdx', chart_spec=f'data.mn/public/charts/{SLUG}-en.json', data_as_of='2025-12-31', source_updated_at=manifest['source_updated_at'], last_fetched_at=manifest['snapshot_date'], canonical_slug=SLUG)
        registry.add_version(Version(id=0, dataset_id=SLUG, version=1, data_hash=hashlib.sha256((VERSION / 'data-en.csv').read_bytes()).hexdigest(), data_path=f'tools/versions/{SLUG}/v1/data-en.csv', row_count=170, column_count=3, change_type='initial', change_summary='Annual youth NEET rates, 2009–2025; total, sex, urban/rural and major regions.', source_updated_at=manifest['source_updated_at'], source_raw_files=[f'tools/versions/{SLUG}/v1/raw/{name}' for name in manifest['files']]))
print('Built bilingual youth NEET pages, charts and downloads from the verified v1 snapshot.')
