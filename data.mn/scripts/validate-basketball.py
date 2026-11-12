"""Check the browser's published data independently of its importers."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
data = json.loads((ROOT / 'data.mn/public/sports/basketball.json').read_text(encoding='utf8'))
report = []
for season in data['seasons']:
    games = {g['id']: g for g in season['games']}
    assert len(games) == len(season['games']), 'Duplicate game IDs'
    roster_keys = [(p['game'], p['team'], p['identity']) for p in season['players']]
    assert len(set(roster_keys)) == len(roster_keys), 'Player identity collision within a game'
    if season.get('resultsOnly'):
        assert not season['players'] and not season['totals']
        assert all(not g['box'] and not g['periods'] and g['ot'] is None for g in games.values())
        appearances=Counter(c for g in games.values() for c in (g['a'],g['b']))
        pairs=Counter(tuple(sorted((g['a'],g['b']))) for g in games.values())
        assert all(n==2 for n in pairs.values())
        assert all(n==2*(len(appearances)-1) for n in appearances.values())
        assert all(g['sourceUrl']['en'].startswith('https://www.koo.mn/') for g in games.values())
    for p in season['players']:
        assert p['game'] in games and p['team'] in (games[p['game']]['a'], games[p['game']]['b'])
        assert p['nameEn'] and not any('\u0400' <= c <= '\u04ff' for c in p['nameEn']), p['nameEn']
        if not p['dnp'] and all(p[k] is not None for k in ('points','two_pt_made','three_pt_made','ft_made')):
            # Source exceptions must be explicitly flagged, never silently changed.
            if p['points'] != 2*p['two_pt_made']+3*p['three_pt_made']+p['ft_made']:
                assert any(q['game']==p['game'] and q['team']==p['team'] for q in season['issues'])
    reconciled, flagged = 0, 0
    for g in games.values():
        for team, score in ((g['a'],g['scoreA']), (g['b'],g['scoreB'])):
            players=[p for p in season['players'] if p['game']==g['id'] and p['team']==team and not p['dnp']]
            if not g['box']:
                assert not players
                continue
            totals=[t for t in season['totals'] if t['game']==g['id'] and t['team']==team]
            assert len(totals)==1, (g['id'],team,'Team total missing or duplicated')
            complete=players and all(p['points'] is not None for p in players)
            if complete and sum(p['points'] for p in players)==score==totals[0]['points']:
                reconciled+=1
            else:
                assert any(q['game']==g['id'] and q['team']==team and q['stat']=='points' for q in season['issues']), (g['id'],team,'Unflagged point gap')
                flagged+=1
    report.append({'season':season['id'],'games':len(games),'player_rows':len(roster_keys),
                   'point_reconciliations':reconciled,'flagged_point_gaps':flagged,'review_flags':len(season['issues'])})
regular=next(s for s in data['seasons'] if s['id']=='2025-26')
regular_ids={g['id'] for g in regular['games'] if g['phase']=='Regular season'}
assert len(regular_ids)==135
players=[p for p in regular['players'] if p['game'] in regular_ids]
assert len(players)==3937 and sum(not p['dnp'] for p in players)==2882
assert sum(p['points'] or 0 for p in players if p['game']=='MBA-614' and p['team']=='BTM')==70
assert all(p['off_rebounds'] is None and p['def_rebounds'] is None and p['personal_fouls'] is None and p['starter'] is None for p in players)
assert Counter(q['stat'] for q in regular['issues'] if q['game'] in regular_ids)=={'periods':8,'score':4,'score_corrected':3,'minutes':16}
print(json.dumps({'status':'PASS','seasons':report},indent=2))
