#!/usr/bin/env python3
"""Build row-aligned public downloads from the sports browser's committed JSON."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUBLIC = ROOT / 'data.mn/public/datasets'
INPUT = ROOT / 'data.mn/public/sports/basketball.json'
IDS = ('basketball-game-results', 'basketball-team-records', 'basketball-player-game-stats')
STAGES = {'Regular season': 'Улирлын тоглолт', 'Play-in': 'Плей-ин', 'Playoffs': 'Плей-офф'}
LABELS = {
    'season': 'Тэмцээний улирал', 'game_id': 'Тоглолтын дугаар', 'date': 'Огноо',
    'stage': 'Шат', 'team_a_id': 'А багийн код', 'team_a': 'А баг', 'score_a': 'А багийн оноо',
    'team_b_id': 'Б багийн код', 'team_b': 'Б баг', 'score_b': 'Б багийн оноо',
    'box_score_available': 'Статистикийн тайлантай', 'source_type': 'Эх сурвалжийн төрөл',
    'source_url': 'Эх сурвалжийн холбоос', 'review_flag': 'Хяналтын тэмдэглэгээ',
    'team_id': 'Багийн код', 'team': 'Баг', 'games': 'Тоглолт', 'wins': 'Хожил',
    'losses': 'Хожигдол', 'points_for_per_game': 'Авсан онооны дундаж',
    'points_against_per_game': 'Алдсан онооны дундаж', 'player_id': 'Тоглогчийн код',
    'player': 'Тоглогч', 'name_source': 'Нэрийн эх сурвалж', 'jersey': 'Өмсгөлийн дугаар',
    'starter': 'Гарааны тоглогч', 'did_not_play': 'Тоглоогүй', 'minutes': 'Тоглосон минут',
    'minutes_precision': 'Минутын нарийвчлал', 'points': 'Оноо',
    'fg_made': 'Амжилттай шидэлт', 'fg_attempted': 'Нийт шидэлт',
    'two_pt_made': 'Амжилттай хоёр онооны шидэлт', 'two_pt_attempted': 'Нийт хоёр онооны шидэлт',
    'three_pt_made': 'Амжилттай гурван онооны шидэлт', 'three_pt_attempted': 'Нийт гурван онооны шидэлт',
    'ft_made': 'Амжилттай чөлөөт шидэлт', 'ft_attempted': 'Нийт чөлөөт шидэлт',
    'off_rebounds': 'Довтолгооны самбар', 'def_rebounds': 'Хамгаалалтын самбар',
    'total_rebounds': 'Нийт самбар', 'assists': 'Оновчтой дамжуулалт', 'turnovers': 'Бөмбөг алдалт',
    'steals': 'Бөмбөг таслалт', 'blocks': 'Хаалт', 'personal_fouls': 'Хувийн алдаа',
    'plus_minus': 'Онооны зөрүү', 'efficiency': 'Ашигт ажиллагаа',
}
STATS = tuple(k for k in LABELS if k in (
    'minutes', 'points', 'fg_made', 'fg_attempted', 'two_pt_made', 'two_pt_attempted',
    'three_pt_made', 'three_pt_attempted', 'ft_made', 'ft_attempted', 'off_rebounds',
    'def_rebounds', 'total_rebounds', 'assists', 'turnovers', 'steals', 'blocks',
    'personal_fouls', 'plus_minus', 'efficiency'))


def provenance(game):
    urls = game.get('sourceUrl') or {}
    # dateSource only corroborates metadata; it is not a public box-score source.
    url = urls.get('en') or urls.get('mn') or ''
    if game['id'].startswith('KOO-'):
        kind = 'koo archive'
    elif url.startswith('https://mongolia.basketball/'):
        kind = 'league page'
    elif game.get('source'):
        kind = 'transcribed image'
    else:
        raise ValueError(f"Unclassified source for {game['id']}")
    return {'source_type': kind, 'source_url': url}


def records(data):
    """Return language-neutral rows; names are resolved only during export."""
    games, teams, players = [], [], []
    for season in sorted(data['seasons'], key=lambda s: s['id']):
        lookup = {g['id']: g for g in season['games']}
        if len(lookup) != len(season['games']):
            raise ValueError('Duplicate game ID')
        flagged = {q['game'] for q in season['issues']}
        groups = defaultdict(list)
        for g in sorted(season['games'], key=lambda g: (g['date'], g['id'])):
            base = {'season': season['id'], 'game_id': g['id'], 'date': g['date'], 'stage': g['phase']}
            games.append({**base, 'team_a_id': g['a'], 'team_a': g['a'], 'score_a': g['scoreA'],
                          'team_b_id': g['b'], 'team_b': g['b'], 'score_b': g['scoreB'],
                          'box_score_available': int(g['box']), **provenance(g),
                          'review_flag': int(g['id'] in flagged)})
            for team, pf, pa in ((g['a'], g['scoreA'], g['scoreB']), (g['b'], g['scoreB'], g['scoreA'])):
                if pf == pa:
                    raise ValueError(f"Tied final score: {g['id']}")
                groups[g['phase'], team].append((g, pf, pa))
        for (stage, team), group in sorted(groups.items()):
            n = len(group)
            teams.append({'season': season['id'], 'stage': stage, 'team_id': team, 'team': team,
                          'games': n, 'wins': sum(pf > pa for _, pf, pa in group),
                          'losses': sum(pf < pa for _, pf, pa in group),
                          'points_for_per_game': round(sum(pf for _, pf, _ in group) / n, 6),
                          'points_against_per_game': round(sum(pa for _, _, pa in group) / n, 6),
                          'source_type': '; '.join(sorted({provenance(g)['source_type'] for g, _, _ in group})),
                          'source_url': '',  # Calculated aggregate has no single source page.
                          'review_flag': int(any(g['id'] in flagged for g, _, _ in group))})
        for p in sorted(season['players'], key=lambda p: (lookup[p['game']]['date'], p['game'], p['team'], p['identity'])):
            g = lookup[p['game']]
            if p['team'] not in (g['a'], g['b']):
                raise ValueError('Player belongs to neither team')
            players.append({'season': season['id'], 'game_id': g['id'], 'date': g['date'], 'stage': g['phase'],
                            'team_id': p['team'], 'team': p['team'], 'player_id': p['identity'],
                            'player': {'en': p['nameEn'], 'mn': p['name']}, 'name_source': p['nameSource'],
                            'jersey': p['jersey'], 'starter': None if p['starter'] is None else int(p['starter']),
                            'did_not_play': int(p['dnp']), 'minutes_precision': g['minutesPrecision'],
                            **{k: p.get(k) for k in STATS}, **provenance(g),
                            'review_flag': int(g['id'] in flagged)})
    return dict(zip(IDS, (games, teams, players)))


def localized(row, lang, data):
    result = dict(row)
    result['stage'] = STAGES[row['stage']] if lang == 'mn' else row['stage']
    for field in ('team', 'team_a', 'team_b'):
        if field in row:
            result[field] = data['teams'][row[field]][int(lang == 'mn')]
    if 'player' in row:
        result['player'] = row['player'][lang]
    return result


def build(input_path=INPUT, output=PUBLIC, csv_only=False):
    data = json.loads(input_path.read_text(encoding='utf-8'))
    tables = records(data)
    output.mkdir(parents=True, exist_ok=True)
    for dataset_id, rows in tables.items():
        keys = list(rows[0])
        for lang in ('en', 'mn'):
            with (output / f'{dataset_id}-{lang}.csv').open('w', encoding='utf-8', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow([LABELS[k] if lang == 'mn' else k for k in keys])
                writer.writerows([localized(r, lang, data)[k] for k in keys] for r in rows)
        print(f'{dataset_id}: {len(rows)} rows')
    if not csv_only:
        # Use the repository's canonical bilingual workbook writer and download metadata.
        sys.path.insert(0, str(ROOT / 'tools/scripts'))
        import pandas as pd
        from rebuild_downloads import write_bilingual_xlsx, rewrite_mdx_datafiles, drop_constant_dims
        if output.resolve() != PUBLIC.resolve():
            raise ValueError('Custom output requires --csv-only')
        for dataset_id in IDS:
            frames = [drop_constant_dims(pd.read_csv(output / f'{dataset_id}-{lang}.csv'))[0] for lang in ('en', 'mn')]
            write_bilingual_xlsx(output / f'{dataset_id}.xlsx', *frames)
            for lang in ('en', 'mn'):
                page = ROOT / f'data.mn/src/data/data/{lang}/{dataset_id}.mdx'
                rewrite_mdx_datafiles(page, f'{dataset_id}-{lang}.csv', f'{dataset_id}.xlsx', lang, dataset_id)
                dates = tables[dataset_id] if 'date' in tables[dataset_id][0] else tables[IDS[0]]
                latest = max(r['date'] for r in dates)
                page.write_text(re.sub(r'^dataDate:.*$', 'dataDate: ' + latest, page.read_text(encoding='utf-8'), flags=re.M), encoding='utf-8')
    return tables


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=INPUT)
    parser.add_argument('--output', type=Path, default=PUBLIC)
    parser.add_argument('--csv-only', action='store_true')
    args = parser.parse_args()
    build(args.input, args.output, args.csv_only)
