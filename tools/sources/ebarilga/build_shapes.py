#!/usr/bin/env python3
"""Build publishable UB admin shapes + boundary tables from ebarilga raw pulls.

Reads the raw admin-boundary GeoJSONs (full precision, styling properties)
and writes:
  - data.mn/public/maps/ulaanbaatar-{districts,khoroos,zip-zones}.json:
    stripped properties, 3-decimal coordinates, clockwise winding
    (Vega/d3 fills CCW rings inverted), for choropleth charts.
  - data.mn/public/datasets/ebarilga-{districts,khoroos,zip-zones}-{en,mn}.csv:
    bilingual reference tables (codes, names, parent districts, areas).

Spatial joins are authoritative: khoroo/ZIP codes mostly encode their
district as a 2-digit prefix, but prefix 15 spans two districts, so every
unit is assigned by true-centroid lookup instead.

Usage:
    .venv/bin/python tools/sources/ebarilga/build_shapes.py
"""
import csv
import json
import math
import os
import re

from shapely.geometry import mapping, shape
from shapely.ops import orient
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = f"{HERE}/raw"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
MAPS = f"{ROOT}/data.mn/public/maps"
DATASETS = f"{ROOT}/data.mn/public/datasets"

# Cyrillic -> Latin, data.mn house style (ASCII, no diacritics; see
# data.mn/public/maps/README.md: Sukhbaatar, Khuvsgul, Umnugovi, Tuv).
TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'j', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'ө': 'u', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
    'у': 'u', 'ү': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh',
    'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': 'i', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}
for _c in list(TRANSLIT):
    TRANSLIT[_c.upper()] = TRANSLIT[_c].capitalize()

# English-origin names: translate instead of transliterating.
TRANSLIT_EXCEPTIONS = {
    'Галакси сургууль': 'Galaxy surguuli',
    'Логарифм сургууль': 'Logarithm surguuli',
    'Сейнт Поул бага сургууль': 'Saint Paul baga surguuli',
    'Сингапур скүүл оф монголиа сургууль':
        'Singapore School of Mongolia surguuli',
    'И-Эс-Эм сургууль - Эрэл сургууль': 'ISM surguuli - Erel surguuli',
    # Also normalizes the source typo сургуууль -> сургууль.
    'Улаанбаатар-Эмпати сургуууль': 'Ulaanbaatar-Empathy surguuli',
    # German-origin names (same principle as English ones).
    'Дойче шуле сургууль': 'Deutsche Schule surguuli',
    'Гёте сургууль': 'Goethe surguuli',
}

# Runs of 2+ uppercase Cyrillic are acronyms: first letters only, all caps
# (ЦС -> TS, ШУТИС -> SHUTIS). Titlecase words are unaffected.
_CAPS_RUN = re.compile(r'[А-ЯЁӨҮ]{2,}')


def transliterate(name):
    if name in TRANSLIT_EXCEPTIONS:
        return TRANSLIT_EXCEPTIONS[name]
    name = _CAPS_RUN.sub(
        lambda m: ''.join(TRANSLIT[ch][0].upper() for ch in m.group(0)),
        name)
    return ''.join(TRANSLIT.get(ch, ch) for ch in name)


def area_km2(geom, lat):
    kx = 111320 * math.cos(math.radians(lat))
    return geom.area * kx * 110540 / 1e6


def round_coords(geom):
    def rnd(x):
        return round(x, 3)
    if geom.geom_type == 'Polygon':
        ext = [(rnd(x), rnd(y)) for x, y in geom.exterior.coords]
        holes = [[(rnd(x), rnd(y)) for x, y in ring.coords]
                 for ring in geom.interiors]
        from shapely.geometry import Polygon
        return Polygon(ext, holes)
    if geom.geom_type == 'MultiPolygon':
        from shapely.geometry import MultiPolygon
        return MultiPolygon([round_coords(p) for p in geom.geoms])
    raise ValueError(f'unexpected admin geometry: {geom.geom_type}')


def load(code):
    with open(f"{RAW}/ebarilga-{code}.geojson", encoding='utf-8') as f:
        return json.load(f)['features']


def main():
    districts = load('district_border')
    khoroos = load('khoroo_border')
    zips = load('zippolygons')

    dname = {}
    dgeom = []
    dcodes = []  # file order, parallel to dgeom (STRtree hits index this)
    for f in districts:
        code = int(f['properties']['object_no'])
        dname[code] = (f['properties']['object_name'] or '').strip()
        dgeom.append(shape(f['geometry']))
        dcodes.append(code)
    dtree = STRtree(dgeom)

    def parent_district(feat):
        pt = shape(feat['geometry']).centroid
        hits = sorted(int(i) for i in dtree.query(pt, predicate='intersects'))
        if len(hits) != 1:
            return None
        return dcodes[hits[0]]

    units = {'districts': [], 'khoroos': [], 'zip-zones': []}
    khoroo_counts = {c: 0 for c in dcodes}
    unmatched = []

    for level, feats, parent in [('khoroos', khoroos, True),
                                 ('zip-zones', zips, True),
                                 ('districts', districts, False)]:
        for f in feats:
            p = f['properties']
            code = int(p['object_no'])
            name_mn = (p['object_name'] or '').strip()
            g = shape(f['geometry'])
            c = g.centroid
            dcode = parent_district(f) if parent else None
            if parent and dcode is None:
                unmatched.append((level, code, name_mn))
            else:
                if level == 'khoroos':
                    khoroo_counts[dcode] += 1
            # Clockwise exterior winding (Vega/d3 requirement), 3 decimals.
            clean = round_coords(orient(g, sign=-1.0))
            units[level].append({
                'code': code, 'name_mn': name_mn,
                'name_en': transliterate(name_mn),
                'district_code': dcode,
                'area_km2': round(area_km2(g, c.y), 3),
                'lon': round(c.x, 6), 'lat': round(c.y, 6),
                'geometry': mapping(clean),
            })
        units[level].sort(key=lambda u: u['code'])

    for level, feats in [('districts', units['districts']),
                         ('khoroos', units['khoroos']),
                         ('zip-zones', units['zip-zones'])]:
        features = []
        for u in feats:
            props = {'code': u['code'], 'name': u['name_en'],
                     'name_mn': u['name_mn'], 'area_km2': u['area_km2']}
            if level != 'districts':
                dc = u['district_code']
                props['district_code'] = dc
                props['district'] = transliterate(dname[dc]) if dc else None
                props['district_mn'] = dname.get(dc)
            features.append({'type': 'Feature', 'properties': props,
                             'geometry': u['geometry']})
        path = f"{MAPS}/ulaanbaatar-{level}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'type': 'FeatureCollection', 'features': features}, f,
                      ensure_ascii=False)
        print(f'wrote {path} ({os.path.getsize(path)} bytes, '
              f'{len(features)} features)')

    tables = {
        'ebarilga-districts': (
            ['code', 'district', 'khoroos', 'area_km2', 'lon', 'lat'],
            ['код', 'дүүрэг', 'хорооны_тоо', 'талбай_км2', 'lon', 'lat'],
            [ (u['code'], u['name_en'], khoroo_counts[u['code']],
               u['area_km2'], u['lon'], u['lat'])
              for u in units['districts'] ],
            [ (u['code'], u['name_mn'], khoroo_counts[u['code']],
               u['area_km2'], u['lon'], u['lat'])
              for u in units['districts'] ]),
        'ebarilga-khoroos': (
            ['code', 'khoroo', 'district_code', 'district', 'area_km2',
             'lon', 'lat'],
            ['код', 'хороо', 'дүүргийн_код', 'дүүрэг', 'талбай_км2',
             'lon', 'lat'],
            [ (u['code'], u['name_en'], u['district_code'],
               transliterate(dname[u['district_code']]), u['area_km2'],
               u['lon'], u['lat'])
              for u in units['khoroos'] ],
            [ (u['code'], u['name_mn'], u['district_code'],
               dname[u['district_code']], u['area_km2'], u['lon'], u['lat'])
              for u in units['khoroos'] ]),
        'ebarilga-zip-zones': (
            ['code', 'zone', 'district_code', 'district', 'area_km2',
             'lon', 'lat'],
            ['код', 'бүс', 'дүүргийн_код', 'дүүрэг', 'талбай_км2',
             'lon', 'lat'],
            [ (u['code'], u['name_en'], u['district_code'] or '',
               transliterate(dname[u['district_code']])
               if u['district_code'] else '', u['area_km2'], u['lon'],
               u['lat'])
              for u in units['zip-zones'] ],
            [ (u['code'], u['name_mn'], u['district_code'] or '',
               dname.get(u['district_code']) or '', u['area_km2'], u['lon'],
               u['lat'])
              for u in units['zip-zones'] ]),
    }
    for dsid, (en_head, mn_head, en_rows, mn_rows) in tables.items():
        for lang, head, rows in (('en', en_head, en_rows),
                                 ('mn', mn_head, mn_rows)):
            path = f"{DATASETS}/{dsid}-{lang}.csv"
            with open(path, 'w', encoding='utf-8', newline='') as f:
                w = csv.writer(f)
                w.writerow(head)
                w.writerows(rows)
            print(f'wrote {path} ({len(rows)} rows)')

    assert sum(khoroo_counts.values()) == len(units['khoroos']), \
        'every khoroo must match exactly one district'
    print(f'khoroo counts by district: '
          f'{ {dname[c]: khoroo_counts[c] for c in sorted(dname)} }')
    for level, code, name in unmatched:
        print(f'UNMATCHED: {level} {code} {name} (outside all districts)')


if __name__ == '__main__':
    main()
