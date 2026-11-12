"""Regression checks for lossless downloads and score-derived team records."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from build_public import INPUT, IDS, LABELS, STATS, build


class PublicDownloads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.data = json.loads(INPUT.read_text(encoding='utf-8'))
        build(INPUT, Path(cls.tmp.name), csv_only=True)
        cls.tables = {}
        for ds in IDS:
            for lang in ('en', 'mn'):
                with (Path(cls.tmp.name)/f'{ds}-{lang}.csv').open(encoding='utf-8-sig', newline='') as stream:
                    cls.tables[ds, lang] = list(csv.DictReader(stream))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_alignment_and_numeric_identity(self):
        localized_fields = {'team', 'team_a', 'team_b', 'player', 'stage'}
        for ds in IDS:
            en, mn = self.tables[ds, 'en'], self.tables[ds, 'mn']
            self.assertEqual(len(en), len(mn))
            for a, b in zip(en, mn):
                for key, value in a.items():
                    if key not in localized_fields:
                        self.assertEqual(value, b[LABELS[key]], (ds, key))

    def test_games_and_flags(self):
        exported = {(r['season'],r['game_id']):r for r in self.tables[IDS[0], 'en']}
        self.assertEqual(len(exported), sum(len(s['games']) for s in self.data['seasons']))
        for s in self.data['seasons']:
            flags = {q['game'] for q in s['issues']}
            for g in s['games']:
                r=exported[s['id'],g['id']]
                self.assertEqual((int(r['score_a']),int(r['score_b'])),(g['scoreA'],g['scoreB']))
                self.assertEqual(r['review_flag'],str(int(g['id'] in flags)))
                if r['source_type']=='transcribed image': self.assertEqual(r['source_url'],'')

    def test_player_rows_and_nulls(self):
        exported={(r['season'],r['game_id'],r['team_id'],r['player_id']):r for r in self.tables[IDS[2], 'en']}
        self.assertEqual(len(exported),sum(len(s['players']) for s in self.data['seasons']))
        for s in self.data['seasons']:
            for p in s['players']:
                r=exported[s['id'],p['game'],p['team'],p['identity']]
                self.assertEqual(r['did_not_play'],str(int(p['dnp'])))
                for field in STATS:
                    self.assertEqual(r[field],'' if p.get(field) is None else str(p[field]))

    def test_team_record_grain_and_scores(self):
        rows=self.tables[IDS[1], 'en']
        self.assertEqual(len(rows),len({(r['season'],r['stage'],r['team_id']) for r in rows}))
        for r in rows:
            s=next(s for s in self.data['seasons'] if s['id']==r['season'])
            games=[g for g in s['games'] if g['phase']==r['stage'] and r['team_id'] in (g['a'],g['b'])]
            scores=[(g['scoreA'],g['scoreB']) if g['a']==r['team_id'] else (g['scoreB'],g['scoreA']) for g in games]
            self.assertEqual(int(r['games']),len(games))
            self.assertEqual(int(r['wins']),sum(a>b for a,b in scores))
            self.assertEqual(int(r['losses']),sum(a<b for a,b in scores))
            self.assertAlmostEqual(float(r['points_for_per_game']),sum(a for a,b in scores)/len(scores),places=5)
            self.assertAlmostEqual(float(r['points_against_per_game']),sum(b for a,b in scores)/len(scores),places=5)


if __name__=='__main__': unittest.main()
