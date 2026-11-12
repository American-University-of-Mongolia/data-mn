#!/usr/bin/env python3
"""Append a new season from public league pages, preserving all existing seasons."""
import argparse
import gzip
import hashlib
import json
import re
from pathlib import Path

from fetch_league import parse_game
from build_public import INPUT, STATS, STAGES


def numeric_stats(raw):
    out = dict.fromkeys(STATS)
    for source, field in {'PTS':'points','REB':'total_rebounds','AST':'assists','STL':'steals','BLK':'blocks','TO':'turnovers'}.items():
        out[field] = int(raw[source])
    if raw.get('PF') not in (None, '', '-'):
        out['personal_fouls'] = int(raw['PF'])
    for source, prefix in {'FG':'fg','3P':'three_pt','FT':'ft'}.items():
        made, attempted = map(int, raw[source].split('-'))
        if not 0 <= made <= attempted:
            raise ValueError(f'Invalid shooting count: {raw}')
        out[prefix+'_made'], out[prefix+'_attempted'] = made, attempted
    out['two_pt_made'] = out['fg_made'] - out['three_pt_made']
    out['two_pt_attempted'] = out['fg_attempted'] - out['three_pt_attempted']
    if not 0 <= out['two_pt_made'] <= out['two_pt_attempted']:
        raise ValueError('Invalid derived two-point count')
    return out


def add(archive, season_id, stage, input_path, output_path):
    data = json.loads(input_path.read_text(encoding='utf-8'))
    if any(s['id'] == season_id for s in data['seasons']):
        raise ValueError('Season already exists; this command only appends a new season and never replaces reviewed data')
    if not re.fullmatch(r'20\d{2}-\d{2}', season_id) or int(season_id[5:]) != (int(season_id[:4])+1) % 100:
        raise ValueError('Expected a consecutive season label such as 2026-27')
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    if read(archive/'fetch-errors.json'):
        raise ValueError('Collection has fetch errors; resolve them before importing')
    manifest, collected = read(archive/'manifest.json'), read(archive/'boxscores.json')
    if not collected:
        raise ValueError('Empty collection')
    season = dict(id=season_id, resultsOnly=False, games=[], players=[], totals=[], issues=[], missing=[],
                  regularTarget=None, sourceLabel='Public bilingual league pages')
    def flag(gid, team, stat, text):
        season['issues'].append(dict(game=gid, team=team, stat=stat, issue=text, issueMn=None))
    seen = set()
    for pair in collected:
        sid = pair['en']['site_game_id']
        if sid in seen:
            raise ValueError('Duplicate public game ID')
        seen.add(sid)
        parsed = {}
        for lang in ('en','mn'):
            record = manifest[f'game-{sid}-{lang}']
            path = (archive/record['file']).resolve()
            if not path.is_relative_to(archive.resolve()):
                raise ValueError('Unsafe archive path')
            compressed=path.read_bytes(); html=gzip.decompress(compressed)
            if hashlib.sha256(compressed).hexdigest()!=record['sha256_gzip'] or hashlib.sha256(html).hexdigest()!=record['sha256_html']:
                raise ValueError('Source hash mismatch')
            parsed[lang]=parse_game(html.decode('utf-8'),record['url'])
        en,mn=parsed['en'],parsed['mn']
        if en['date']!=mn['date']:
            raise ValueError('Bilingual dates disagree')
        if int(en['date'][:4]) not in (int(season_id[:4]), int(season_id[:4])+1):
            raise ValueError('Game date is outside the named season years')
        gid=f'LEAGUE-{season_id}-{sid}'
        codes=[]
        for a,b in zip(en['teams'],mn['teams'],strict=True):
            if any(a[k]!=b[k] for k in ('team_slug','score','period_scores','totals')) or len(a['players'])!=len(b['players']):
                raise ValueError('Bilingual team data disagree')
            code=f'LEAGUE-{season_id}-{a["team_slug"]}';codes.append(code)
            data['teams'][code]=[a['name'],b['name'],'#4467a8']
            total=numeric_stats(a['totals']); total['minutes']=a['totals'].get('MIN')
            season['totals'].append(dict(game=gid,team=code,**total))
            points=0; identities=set()
            for p,local in zip(a['players'],b['players'],strict=True):
                if any(p[k]!=local[k] for k in ('player_slug','jersey','dnp','minutes_display','stats')):
                    raise ValueError('Bilingual player data disagree')
                if p['player_slug'] in identities: raise ValueError('Duplicate player identity')
                identities.add(p['player_slug'])
                stats=dict.fromkeys(STATS) if p['dnp'] else numeric_stats(p['stats'])
                stats['minutes']=p['minutes_display']
                points+=stats['points'] or 0
                season['players'].append(dict(game=gid,team=code,name=local['name'],nameEn=p['name'],
                    nameSource='league',identity='league:'+p['player_slug'],jersey=p['jersey'],starter=None,dnp=p['dnp'],**stats))
                if not p['dnp'] and stats['points']!=2*stats['two_pt_made']+3*stats['three_pt_made']+stats['ft_made']:
                    flag(gid,code,'points',f"{p['name']}: shooting counts do not reconcile with published player points; source retained.")
            if not points==total['points']==a['score']:
                flag(gid,code,'points',f"Player points {points}; team total {total['points']}; final score {a['score']}. Source values retained.")
            if sum(a['period_scores'])!=a['score']:
                flag(gid,code,'periods','Published period scores do not reconcile with the final score; source retained.')
        season['games'].append(dict(id=gid,date=en['date'],phase=stage,round=stage,a=codes[0],b=codes[1],
            scoreA=en['teams'][0]['score'],scoreB=en['teams'][1]['score'],ot=max(len(t['period_scores']) for t in en['teams'])-4 or None,
            box=True,periods=[list(x) for x in zip(en['teams'][0]['period_scores'],en['teams'][1]['period_scores'],strict=True)],
            source=f'game-{sid}-en.html.gz / game-{sid}-mn.html.gz',dateSource=None,
            sourceUrl={lang:parsed[lang]['url'] for lang in ('en','mn')},minutesPrecision='whole'))
    season['games'].sort(key=lambda g:(g['date'],g['id']))
    data['seasons'].append(season);data['seasons'].sort(key=lambda s:s['id'])
    temp=output_path.with_suffix('.tmp')
    temp.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8');temp.replace(output_path)
    print(f"Added {season_id}: {len(season['games'])} games, {len(season['players'])} player records, {len(season['issues'])} review flags")


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',type=Path,required=True)
    p.add_argument('--season',required=True)
    p.add_argument('--stage',choices=list(STAGES),default='Regular season')
    p.add_argument('--input',type=Path,default=INPUT)
    p.add_argument('--output',type=Path,default=INPUT)
    a=p.parse_args();add(a.archive,a.season,a.stage,a.input,a.output)
