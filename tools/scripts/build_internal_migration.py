"""Rebuild migration pages and data offline from the hash-checked NSO v1 snapshot.

Run from any directory. Excel files use the canonical rebuild_downloads helper.
Pass --register to add the pending dataset/version to the local registry once.
"""
from pathlib import Path
import csv, json, copy, hashlib, sys

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'data.mn'
SLUG = 'internal-migration-by-aimag'
VERSION = ROOT / 'tools/versions' / SLUG / 'v1'
RAW = VERSION / 'raw'
manifest = json.loads((RAW/'manifest.json').read_text())
for name, digest in manifest['files'].items():
    assert hashlib.sha256((RAW/name).read_bytes()).hexdigest() == digest, name
metadata = {lang:json.loads((RAW/f'metadata-{lang}.json').read_text()) for lang in ('en','mn')}
responses = {lang:json.loads((RAW/f'data-{lang}.json').read_text()) for lang in ('en','mn')}
values = {}
for lang, response in responses.items():
    values[lang] = {tuple(row['key']):int(row['values'][0]) for row in response['data']}
    assert len(values[lang]) == len(response['data']) == 2408
    assert all(v >= 0 for v in values[lang].values())
assert values['en'] == values['mn'], 'Bilingual numeric mismatch'
variables = metadata['en']['variables']
assert [v['code'] for v in variables] == [v['code'] for v in metadata['mn']['variables']]
assert [v['values'] for v in variables] == [v['values'] for v in metadata['mn']['variables']]
assert variables[2]['valueTexts'] == metadata['mn']['variables'][2]['valueTexts']
assert variables[0]['values'] == ['0','1']
regions = [code for code in variables[1]['values'] if len(code) == 3]
assert len(regions) == 22
years = dict(zip(variables[2]['values'],map(int,variables[2]['valueTexts'])))
assert sorted(years.values()) == list(range(1983,2026))
payload = {'names':{lang:dict(zip(meta['variables'][1]['values'],meta['variables'][1]['valueTexts'])) for lang,meta in metadata.items()}}
records, balances = [], []
source = values['en']
for code, year in years.items():
    for measure in ('0','1'):
        assert sum(source[measure, region, code] for region in regions) == source[measure,'0',code]
    balances.append({'year':year,'difference':source['0','0',code]-source['1','0',code]})
    for region in regions:
        incoming, outgoing = source['0',region,code],source['1',region,code]
        records.append({'region':region,'year':year,'incoming':incoming,'outgoing':outgoing,'net':incoming-outgoing})
records.sort(key=lambda r:(r['year'],r['region']))
assert all(b['difference']==0 for b in balances if b['year']>=2020)
assert all(r['incoming']==r['outgoing']==0 for r in records if r['region']=='342' and r['year']<=1990)
geometry = json.loads((SITE/'public/maps/mongolia-aimags.json').read_text())
assert {payload['names']['en'][r['region']] for r in records} == {f['properties']['name'] for f in geometry['features']}
config = {'axis': {'labelFontSize':14,'titleFontSize':16,'labelColor':'#64748b','titleColor':'#334155'},'legend':{'labelFontSize':13,'titleFontSize':14},'view':{'stroke':'transparent'}}
domain = max(abs(r['net']) for r in records)
for lang in ['en','mn']:
    en = lang == 'en'
    labels = ['Year','Aimag / capital','Arrivals','Departures','Net migration (people)'] if en else ['Он','Аймаг / нийслэл','Шилжин ирсэн','Шилжин явсан','Цэвэр шилжилт (хүн)']
    fields = ['year','region','incoming','outgoing','net'] if en else ['он','бүс','ирсэн','явсан','цэвэр']
    year, region, incoming, outgoing, net = fields
    datafile=SITE/f'public/datasets/{SLUG}-{lang}.csv'
    with datafile.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(fields)
        for r in records:w.writerow([r['year'],payload['names'][lang][r['region']],r['incoming'],r['outgoing'],r['net']])
    # A single measurement per row allows the standard wide Excel pivot.
    # The chart CSV retains adjacent measures for the map's hover details.
    download = SITE/f'public/datasets/{SLUG}-all-{lang}.csv'
    with download.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f)
        w.writerow(['year','aimag_measure','people'] if en else ['он','аймаг_үзүүлэлт','хүн'])
        for r in records:
            for key, label in zip(('incoming','outgoing','net'),labels[2:]):
                w.writerow([r['year'],payload['names'][lang][r['region']]+' — '+label,r[key]])
    for file in (datafile, download):
        (VERSION/file.name).write_bytes(file.read_bytes())
    base={'$schema':'https://vega.github.io/schema/vega-lite/v5.json','config':copy.deepcopy(config),'data':{'url':f'/datasets/{SLUG}-{lang}.csv','format':{'type':'csv','parse':{x:'number' for x in [year,incoming,outgoing,net]}}}}
    tips=[{'field':field,'type':'nominal' if field==region else 'quantitative','title':label,**({} if field==region else {'format':'d' if field==year else ',.0f'})} for field,label in zip(fields,labels)]
    map_spec=copy.deepcopy(base)
    map_spec.update({'description':'Recorded internal migration, 1983–2025. Net = arrivals minus departures. Fixed symmetric color scale across all years. Historical data shown on current boundaries; see source limitations. Boundaries: geoBoundaries (ODbL) / OpenStreetMap contributors.',
      'params':[{'name':'selectedYear','value':2025,'bind':{'input':'range','min':1983,'max':2025,'step':1,'name':labels[0]+': '}}],
      'transform':[{'filter':f'datum["{year}"] == selectedYear'},{'lookup':region,'from':{'data':{'url':'/maps/mongolia-aimags.json','format':{'type':'json','property':'features'}},'key':'properties.name' if en else 'properties.name_mn'},'as':'boundary'}],
      'projection':{'type':'mercator'},'mark':{'type':'geoshape','stroke':'#94a3b8','strokeWidth':0.7},
      'encoding':{'shape':{'field':'boundary','type':'geojson'},'color':{'field':net,'type':'quantitative','scale':{'domain':[-domain,domain],'domainMid':0,'scheme':'redblue'},'legend':{'orient':'top','title':labels[-1],'format':',.0f','gradientLength':230,'tickCount':3}},'tooltip':tips}})
    rank=copy.deepcopy(base)
    rank.update({'description':'All 21 aimags and the capital, ranked by recorded net migration in the year selected on the map.',
      'params':[{'name':'selectedYear','value':2025}], 'transform':[{'filter':f'datum["{year}"] == selectedYear'}],
      'mark':{'type':'bar','cornerRadiusEnd':2},'encoding':{'y':{'field':region,'type':'nominal','sort':'-x','title':None},'x':{'field':net,'type':'quantitative','title':labels[-1],'scale':{'zero':True},'axis':{'format':',.0f','tickCount':4}},'color':{'condition':{'test':f'datum["{net}"] >= 0','value':'#1f77b4'},'value':'#d6604d'},'tooltip':tips}})
    trend=copy.deepcopy(base)
    names=sorted(payload['names'][lang][k] for k in payload['names'][lang] if len(k)==3)
    trend.update({'description':'Annual arrivals, departures and derived net migration for a selected aimag, 1983–2025. Historical source values are unchanged; see comparability limitations.',
      'params':[{'name':'selectedRegion','value':payload['names'][lang]['511'],'bind':{'input':'select','options':names,'name':labels[1]+': '}}],
      'transform':[{'filter':f'datum["{region}"] == selectedRegion'}, {'fold':[incoming,outgoing,net],'as':['measure','value']}],
      'encoding':{'x':{'field':year,'type':'quantitative','title':labels[0],'scale':{'zero':False},'axis':{'grid':False,'format':'d','tickMinStep':1,'tickCount':4}},'y':{'field':'value','type':'quantitative','title':'People' if en else 'Хүн','axis':{'format':',.0f','tickCount':5}},'color':{'field':'measure','type':'nominal','title':None,'scale':{'domain':[incoming,outgoing,net],'range':['#1f77b4','#d6604d','#2ca02c']},'legend':{'orient':'top','labelExpr':f"datum.label === '{incoming}' ? '{labels[2]}' : datum.label === '{outgoing}' ? '{labels[3]}' : '{'Net migration' if en else 'Цэвэр шилжилт'}'"}}},
      'layer':[{'mark':{'type':'line','strokeWidth':2.5}},{'params':[{'name':'hover','select':{'type':'point','nearest':True,'on':'pointerover','clear':'pointerout'}}],'mark':{'type':'point','filled':True,'size':90},'encoding':{'opacity':{'condition':{'param':'hover','empty':False,'value':1},'value':0},'tooltip':tips}}]})
    trend['encoding']['x']['scale'].update({'domain':[1983,2025],'nice':False})
    trend['encoding']['x']['axis']['values'] = [1983,1990,2000,2010,2025]
    # Keep numeric labels inside the gradient so negative labels are not clipped.
    legend_tick = round(domain * 0.75 / 1000) * 1000
    map_spec['encoding']['color']['legend']['values'] = [-legend_tick, 0, legend_tick]
    if not en:
        map_spec['description'] = 'Бүртгэгдсэн дотоод шилжилт хөдөлгөөн, 1983–2025. Цэвэр шилжилт = ирсэн − явсан. Өнгөний хуваарь бүх онд тогтмол. Өнөөгийн хилээр харуулсан; түүхэн хязгаарлалтыг анхаарна уу. Хил: geoBoundaries (ODbL) / OpenStreetMap contributors.'
        rank['description'] = 'Газрын зураг дээр сонгосон оны бүртгэгдсэн цэвэр шилжилтээр эрэмбэлсэн 21 аймаг, нийслэлийн дүн.'
        trend['description'] = 'Сонгосон аймгийн шилжин ирсэн, явсан хүний тоо болон цэвэр шилжилт, 1983–2025. Түүхэн эх утгуудыг өөрчлөөгүй; харьцуулах хязгаарлалтыг анхаарна уу.'
    for suffix,spec in [('',map_spec),('-ranking',rank),('-trend',trend)]:
        (SITE/f'public/charts/{SLUG}{suffix}-{lang}.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2))
    title='Mongolia Internal Migration by Aimag, People (1983–2025)' if en else 'Монгол Улсын дотоод шилжилт хөдөлгөөн, аймгаар, хүн (1983–2025)'
    excerpt='Recorded arrivals, departures and net migration across Mongolia’s 21 aimags and Ulaanbaatar. Select a year on the map to compare places.' if en else 'Монгол Улсын 21 аймаг, Улаанбаатарын шилжин ирсэн, явсан хүний тоо болон цэвэр шилжилт. Газрын зураг дээрх оноо сонгон харьцуулна уу.'
    front={'title':title,'publishDate':'2026-10-07','excerpt':excerpt,'category':'Demographics' if en else 'Хүн ам зүй','tags':['mongolia','migration','population'],'author':'Data.mn','dataVersion':1,'dataDate':'2025-12-31','dataFiles':[{'path':f'/datasets/{SLUG}-{lang}.csv','format':'csv','size':f'{datafile.stat().st_size//1024} KB','description':'Full source history, 1983–2025. Read historical limitations.' if en else 'Бүтэн түүхэн өгөгдөл, 1983–2025. Хязгаарлалтыг уншина уу.'}],'source':{'name':'National Statistics Office of Mongolia' if en else 'Үндэсний статистикийн хороо','url':f'https://data.1212.mn/pxweb/{lang}/NSO/NSO__Population%2C%20household__1_Population%2C%20household/DT_NSO_0300_040V1.px/','tableId':'DT_NSO_0300_040V1.px'}}
    front['publishDate'] = '2026-10-08'
    front['tags'] = ['mongolia','migration','population'] if en else ['монгол','шилжилт хөдөлгөөн','хүн ам']
    front['keywords'] = ['internal migration Mongolia','migration by aimag','Ulaanbaatar migration'] if en else ['монголын дотоод шилжилт','аймгийн шилжилт хөдөлгөөн','улаанбаатарын шилжилт']
    front['excelLanguage'] = 'page'
    front['dataFiles'][0]['path'] = f'/datasets/{SLUG}-all-{lang}.csv'
    front['dataFiles'].append({'path':f'/datasets/{SLUG}-{lang}.xlsx','format':'xlsx','size':'1 KB','description':'Excel download' if en else 'Excel татах'})
    # JSON values are valid YAML scalars/arrays, avoiding a generator dependency.
    content='---\n'+'\n'.join(f'{k}: {v if k in ("publishDate", "dataDate") else json.dumps(v,ensure_ascii=False)}' for k,v in front.items())+'\n---\n\n'
    content+="import VegaChart from '~/components/ui/VegaChart.astro';\n\n"
    sections=[('', 'Net migration across Mongolia' if en else 'Монголын цэвэр шилжилт хөдөлгөөн', 'Blue = net gain; red = net loss. Hover for arrivals and departures. Use the year slider below the map.' if en else 'Цэнхэр: эерэг, улаан: сөрөг цэвэр шилжилт. Аймаг дээр заахад ирсэн, явсан хүний тоо харагдана. Доорх гулсуураар оноо сонгоно уу.',0.625),('-ranking','Net migration by aimag' if en else 'Цэвэр шилжилт, аймгаар','All 22 places, for the year selected above. Counts are not adjusted for population size.' if en else 'Дээр сонгосон оны нийт 22 газрын дүн. Хүн амын хэмжээнд харьцуулаагүй хүний тоо.',0.8),('-trend','Arrivals and departures over time' if en else 'Шилжин ирсэн, явсан хүний тооны өөрчлөлт','Select an aimag below the chart. Net migration = arrivals − departures.' if en else 'Графикийн доороос аймгаа сонгоно уу. Цэвэр шилжилт = ирсэн − явсан.',0.65)]
    history_note=('Historical data: national arrivals and departures do not balance before 2020. Govisumber has unexplained source zeros in 1983–1990. The map uses current boundaries for all years; historical comparisons need caution.' if en else 'Түүхэн өгөгдөл: 2020 оноос өмнөх улсын нийт ирсэн, явсан хүний тоо тэнцэхгүй. Говьсүмбэрийн 1983–1990 оны эх сурвалжийн тэг утгын тайлбар тодорхойгүй. Бүх оныг өнөөгийн хилээр харуулсан тул түүхэн харьцуулалтыг болгоомжтой хийнэ үү.')
    content+=f'<div role="note" className="mb-4 text-sm text-slate-600 dark:text-slate-400">{history_note}</div>\n\n'
    for suffix,heading,caption,ratio in sections:
        group=f' yearGroup="{SLUG}"' if suffix!='-trend' else ''
        content+=f'<h2>{heading}</h2>\n\n<VegaChart spec="/charts/{SLUG}{suffix}-{lang}.json" title="{heading}" caption="{caption}" aspectRatio={{{ratio}}}{group} />\n\n'
    (SITE/f'src/data/data/{lang}/{SLUG}.mdx').write_text(content.rstrip()+'\n')

from rebuild_downloads import process_dataset
result = process_dataset(SLUG, apply=True)
assert result['queue']=='auto', result
(VERSION/'validation.json').write_text(json.dumps({'source_hashes_verified':True,'bilingual_values_match':True,'province_sums_match_national':True,'province_year_rows':len(records),'years':[1983,2025],'national_balance':balances},indent=2)+'\n')

if '--register' in sys.argv:
    sys.path.insert(0,str(ROOT/'tools'))
    from registry.registry import Registry, Dataset, Version
    registry=Registry()
    if registry.get_dataset(SLUG) is None:
        registry.add_dataset(Dataset(id=SLUG,source_id='nso-1212',name_en='Internal migration by aimag',name_mn='Дотоод шилжилт хөдөлгөөн, аймгаар',category_en='Demographics',category_mn='Хүн ам зүй',definition_path=f'tools/sources/nso-1212/datasets/{SLUG}.md',source_ref=manifest['table'],source_path=manifest['source_path'],tags=['mongolia','migration','population'],status='pending',auto_update=False,auto_publish=False,source_metadata={'frequency':'annual','unit':'people','years':[1983,2025],'regions':22,'limitations':'National imbalance before 2020; historical source zeros; current map boundaries.'}))
        registry.update_dataset(SLUG,current_version=1,data_file=f'data.mn/public/datasets/{SLUG}-all-en.csv',mdx_file_en=f'data.mn/src/data/data/en/{SLUG}.mdx',mdx_file_mn=f'data.mn/src/data/data/mn/{SLUG}.mdx',chart_spec=f'data.mn/public/charts/{SLUG}-en.json',data_as_of='2025-12-31',source_updated_at=responses['en']['metadata'][0]['updated'],last_fetched_at=manifest['retrieved_at'],canonical_slug=SLUG)
        registry.add_version(Version(id=0,dataset_id=SLUG,version=1,data_hash=hashlib.sha256((VERSION/f'{SLUG}-all-en.csv').read_bytes()).hexdigest(),data_path=f'tools/versions/{SLUG}/v1/{SLUG}-all-en.csv',row_count=2838,column_count=3,change_type='initial',change_summary='1983–2025 recorded internal migration for 21 aimags and Ulaanbaatar; net derived from arrivals minus departures.',source_updated_at=responses['en']['metadata'][0]['updated'],source_raw_files=[f'tools/versions/{SLUG}/v1/raw/{name}' for name in manifest['files']]))
print('Built bilingual migration pages, all-history charts and standard downloads.')
