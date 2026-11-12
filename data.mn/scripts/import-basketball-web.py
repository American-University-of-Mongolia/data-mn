"""Rebuild 2025-26 regular-season data from hash-verified bilingual league pages.

Usage: python import-basketball-web.py SOURCE_ARCHIVE PREVIOUS_COLLECTION OUTPUT
No network requests or edits to the previous export are performed here.
"""
import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('league_source', ROOT / 'tools/sources/basketball/fetch_league.py')
SOURCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SOURCE)
FIELDS = {'PTS': 'points', 'REB': 'total_rebounds', 'AST': 'assists',
          'STL': 'steals', 'BLK': 'blocks', 'TO': 'turnovers'}
SHOTS = {'FG': 'fg', '3P': 'three_pt', 'FT': 'ft'}
# Only these three changes have agreement between header, box score and final
# play-by-play event. All other conflicting headers retain the previous score.
SCORE_CORRECTIONS = {('MBA-680', 'DUA'): (63, 68), ('MBA-710', 'DUA'): (76, 80), ('MBA-711', 'BCH'): (91, 93)}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def stats(raw):
    result = {v: int(raw[k]) for k, v in FIELDS.items()}
    for k, prefix in SHOTS.items():
        made, attempted = map(int, raw[k].split('-'))
        assert 0 <= made <= attempted, raw
        result[prefix + '_made'] = made
        result[prefix + '_attempted'] = attempted
    result['two_pt_made'] = result['fg_made'] - result['three_pt_made']
    result['two_pt_attempted'] = result['fg_attempted'] - result['three_pt_attempted']
    assert 0 <= result['two_pt_made'] <= result['two_pt_attempted'], raw
    assert result['points'] == 2 * result['two_pt_made'] + 3 * result['three_pt_made'] + result['ft_made'], raw
    return result


def build(archive, previous, output):
    manifest = read(archive / 'manifest.json')
    mappings = read(archive / 'game-id-mapping.json')
    old = read(previous)
    old_games = {g['game_id']: g for g in old['games']}
    play_by_play = {p['site_game_id']: p['final_play_by_play_event'] for p in read(archive / 'conflicting-score-play-by-play.json')}
    result = {k: [] for k in ('games', 'players', 'team_totals', 'qa_checks', 'missing_games')}
    reconciled = []
    corrected = set()
    assert len(mappings) == len(old_games) == 135
    assert len({m['previous_game_id'] for m in mappings}) == len(mappings)

    def flag(gid, team, field, message, mn, **values):
        result['qa_checks'].append(dict(game_id=gid, team_code=team, stat=field, issue=message, issue_mn=mn, **values))

    for mapping in mappings:
        gid, sid = mapping['previous_game_id'], mapping['site_game_id']
        original = old_games[gid]
        parsed = {}
        for lang in ('en', 'mn'):
            record = manifest[f'game-{sid}-{lang}']
            compressed = (archive / record['file']).read_bytes()
            assert hashlib.sha256(compressed).hexdigest() == record['sha256_gzip']
            html = gzip.decompress(compressed)
            assert hashlib.sha256(html).hexdigest() == record['sha256_html']
            parsed[lang] = SOURCE.parse_game(html.decode('utf8'), record['url'])
        assert parsed['en']['date'] == parsed['mn']['date'] == original['date'] == mapping['date']
        assert (mapping['home_code'], mapping['away_code']) == (original['team1_code'], original['team2_code'])
        game = {**original, 'source_file': f'game-{sid}-en.html.gz / game-{sid}-mn.html.gz',
                'source_type': 'MBA public bilingual box scores', 'source_url_en': parsed['en']['url'],
                'source_url_mn': parsed['mn']['url'], 'minutes_precision': 'whole',
                'website_game_id': sid, 'boxscore_available': True}
        for i, (en, mn) in enumerate(zip(parsed['en']['teams'], parsed['mn']['teams']), 1):
            code = original[f'team{i}_code']
            assert en['team_slug'] == mn['team_slug'] and en['totals'] == mn['totals']
            assert en['score'] == mn['score'] and en['period_scores'] == mn['period_scores']
            assert len(en['players']) == len(mn['players'])
            total = stats(en['totals'])
            player_rows = []
            for p, local in zip(en['players'], mn['players']):
                assert all(p[k] == local[k] for k in ('player_slug', 'jersey', 'dnp', 'minutes_display', 'stats'))
                row = dict(game_id=gid, team_code=code, player_name_en=p['name'], player_name_mn=local['name'],
                           source_player_id=p['player_slug'], source_player_url=p['profile_url'],
                           jersey_no=p['jersey'], did_not_play=p['dnp'], starter=None,
                           minutes=p['minutes_display'], minutes_precision='whole')
                if not p['dnp']:
                    row.update(stats(p['stats']))
                player_rows.append(row)
            assert len({p['source_player_id'] for p in player_rows}) == len(player_rows)
            points = sum(p.get('points', 0) for p in player_rows)
            previous_score = original[f'team{i}_score']
            score = previous_score
            if (gid, code) in SCORE_CORRECTIONS:
                before, after = SCORE_CORRECTIONS[gid, code]
                assert before == previous_score and after == en['score'] == total['points'] == points
                assert play_by_play[sid]['home' if i == 1 else 'away'] == after
                score = after
                corrected.add((gid, code))
                flag(gid, code, 'score_corrected', f'Previous export: {before}; current header, player total, team total and final play-by-play agree on {after}.',
                     f'Өмнөх экспорт: {before}; одоогийн үр дүн, тоглогчдын нийлбэр, багийн нийт болон тоглолтын төгсгөлийн тэмдэглэл: {after}.', previous=before, recorded=after)
            game[f'team{i}_score'] = score
            if en['score'] != score:
                flag(gid, code, 'score', f'Website header: {en["score"]}; retained final score and box-score points: {score}.',
                     f'Сайтын гарчгийн оноо: {en["score"]}; хадгалсан эцсийн оноо болон статистикийн нийлбэр: {score}.', source=en['score'], recorded=score)
            if sum(en['period_scores']) != score:
                flag(gid, code, 'periods', f'Published period scores sum to {sum(en["period_scores"])}; recorded final score: {score}. Period scores retained as published.',
                     f'Нийтэлсэн үеийн онооны нийлбэр {sum(en["period_scores"])}; эцсийн оноо {score}. Үеийн оноог эх сурвалжийн дагуу хадгалав.')
            for n, value in enumerate(en['period_scores'], 1):
                game[f'team{i}_q{n}'] = value
            for field in ('points', 'fg_made', 'fg_attempted', 'three_pt_made', 'three_pt_attempted', 'ft_made', 'ft_attempted'):
                player_sum = sum(p.get(field, 0) for p in player_rows)
                assert player_sum == total[field], (gid, code, field, player_sum, total[field])
            if points != score:
                flag(gid, code, 'points', f'Player points {points} do not reconcile to final score {score}.',
                     f'Тоглогчдын онооны нийлбэр {points}; эцсийн оноо {score}.')
            active = [p for p in player_rows if not p['did_not_play']]
            displayed_minutes = sum(int(p['minutes']) for p in active)
            period_minutes = 200 + 25 * max(0, len(en['period_scores']) - 4)
            if abs(displayed_minutes - period_minutes) > len(active):
                flag(gid, code, 'minutes',
                     f'Published player minutes total {displayed_minutes}; displayed periods imply {period_minutes} team-minutes. The difference exceeds one minute per appearance. Overtime may be omitted or playing times may be incorrect; source values retained.',
                     f'Нийтэлсэн тоглогчдын минутын нийлбэр {displayed_minutes}; харуулсан үеэс тооцвол {period_minutes} багийн минут. Зөрүү нь тоглосон хүн бүрд нэг минутаас их. Нэмэлт үе дутуу эсвэл хугацаа буруу байж болзошгүй; эх утгыг хадгалав.')
            result['players'].extend(player_rows)
            result['team_totals'].append(dict(game_id=gid, team_code=code, minutes=en['totals']['MIN'], minutes_precision='whole', **total))
            reconciled.append(dict(game_id=gid, team_code=code, previous_score=previous_score, website_header=en['score'], recorded_score=score, team_points=total['points'], player_points=points, source_url=parsed['en']['url']))
        # Four displayed periods alone do not prove that a game had no overtime.
        game['overtime_periods'] = max(len(t['period_scores']) for t in parsed['en']['teams']) - 4 or None
        result['games'].append(game)
    assert corrected == set(SCORE_CORRECTIONS)
    assert len(result['players']) == 3937 and len(result['team_totals']) == 270
    assert all(r['recorded_score'] == r['team_points'] == r['player_points'] for r in reconciled)
    write(output / 'data/collection.json', result)
    write(output / 'reconciliation.json', reconciled)
    # Row-aligned downloads use the source's own English and Mongolian names.
    for kind in ('games', 'players', 'team_totals'):
        source_rows = result[kind]
        for lang in ('en', 'mn'):
            rows = [{**{k: v for k, v in r.items() if not k.startswith('player_name_')},
                     **({'player_name': r['player_name_' + lang]} if kind == 'players' else {})} for r in source_rows]
            keys = list(dict.fromkeys(k for r in rows for k in r))
            with (output / 'data' / f'{kind}-{lang}.csv').open('w', encoding='utf-8-sig', newline='') as stream:
                writer = csv.DictWriter(stream, keys)
                writer.writeheader()
                writer.writerows(rows)
    summary = dict(games=len(result['games']), team_games=len(reconciled), player_rows=len(result['players']),
                   appearances=sum(not p['did_not_play'] for p in result['players']), review_flags=len(result['qa_checks']),
                   reconciled_team_games=sum(r['recorded_score'] == r['player_points'] for r in reconciled))
    write(output / 'validation.json', summary)
    print(json.dumps(summary))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('previous', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    build(args.archive, args.previous, args.output)
