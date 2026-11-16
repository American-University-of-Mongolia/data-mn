"""Archive public bilingual league schedules and box scores (standard library only)."""
import os
import argparse
import gzip
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import tempfile
import time
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

OUT = Path(os.environ.get('BASKETBALL_WEB_ARCHIVE', 'outputs/basketball-league-2025-26'))
BASE = 'https://mongolia.basketball'
SCHEDULE = BASE + '/mn/competitions/league/schedule?season=c1a0488c-31a5-429d-8254-3b27aa45e702&type=regular'
ARCHIVE = OUT / 'sources'

manifest_path = OUT / 'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf8')) if manifest_path.exists() else {}
last_request = 0


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def fetch(url, filename, seed=None):
    global last_request
    path = ARCHIVE / (filename + '.html.gz')
    if path.exists():
        assert manifest[filename]['url'] == url, 'Cache belongs to another URL; use a new output directory'
        raw = gzip.decompress(path.read_bytes())
        assert hashlib.sha256(raw).hexdigest() == manifest[filename]['sha256_html']
        return raw.decode('utf8')
    if seed and seed.exists():
        raw = seed.read_bytes()
        retrieved = datetime.fromtimestamp(seed.stat().st_mtime, timezone.utc).isoformat()
    else:
        time.sleep(max(0, 0.8 - (time.monotonic() - last_request)))
        last_request = time.monotonic()
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (data.mn source verification)'})
        for attempt in range(3):
            try:
                with urlopen(req, timeout=45) as response:
                    raw = response.read()
                break
            except HTTPError as error:
                if error.code not in (429, 502, 503, 504) or attempt == 2:
                    raise
                time.sleep(5 * (attempt + 1))
            except (URLError, ConnectionError, TimeoutError):
                if attempt == 2:
                    raise
                time.sleep(5 * (attempt + 1))
        retrieved = datetime.now(timezone.utc).isoformat()
    compressed = gzip.compress(raw, mtime=0)
    path.write_bytes(compressed)
    manifest[filename] = {
        'url': url, 'retrieved_at_utc': retrieved,
        'file': str(path.relative_to(OUT)).replace('\\', '/'),
        'sha256_html': hashlib.sha256(raw).hexdigest(),
        'sha256_gzip': hashlib.sha256(compressed).hexdigest(),
        'bytes_html': len(raw), 'bytes_gzip': len(compressed),
    }
    write_json(manifest_path, manifest)
    return raw.decode('utf8')


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.table = self.row = self.cell = None
        self.in_caption = False
        self.in_name = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'table':
            self.table = {'caption': '', 'rows': []}
        if tag == 'caption':
            self.in_caption = True
        if tag == 'tr' and self.table is not None:
            self.row = {'cells': [], 'profile': None, 'name': None}
        if tag in ('th', 'td') and self.row is not None:
            self.cell = []
        if tag == 'a' and self.row is not None and '/players/' in attrs.get('href', ''):
            self.row['profile'] = attrs['href']
        if tag == 'img' and self.row is not None and attrs.get('alt'):
            self.row['name'] = attrs['alt']
        if tag == 'span' and self.row is not None and 'group-hover:underline' in attrs.get('class', ''):
            self.in_name = True
            self.row['name'] = ''

    def handle_data(self, text):
        if self.cell is not None:
            self.cell.append(text)
        if self.in_caption and self.table is not None:
            self.table['caption'] += text
        if self.in_name and self.row is not None:
            self.row['name'] += text

    def handle_endtag(self, tag):
        if tag == 'span':
            self.in_name = False
        if tag in ('th', 'td') and self.cell is not None:
            self.row['cells'].append(''.join(self.cell).strip())
            self.cell = None
        if tag == 'tr' and self.row is not None:
            self.table['rows'].append(self.row)
            self.row = None
        if tag == 'caption':
            self.in_caption = False
        if tag == 'table' and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def parse_game(source, url):
    parser = Tables()
    parser.feed(source)
    events = [json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source)]
    event = next(e for e in events if e.get('@type') == 'SportsEvent')
    assert len(parser.tables) == 3, (url, 'Unexpected table count', len(parser.tables))
    periods = parser.tables[0]['rows']
    teams = []
    for side, table, period in zip(('home', 'away'), parser.tables[1:], periods[1:]):
        headers = table['rows'][0]['cells']
        core = ['MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'FG', '3P', 'FT', 'TO']
        assert headers[2:] in (core, core + ['PF']), (url, headers)
        players = []
        for row in table['rows'][1:-1]:
            cells = row['cells']
            assert row['profile'] and row['name'], (url, row)
            number = re.search(r'#\s*(\d+)\s*$', cells[0])
            assert number, (url, cells[0])
            dnp = len(cells) == 3 and 'DNP' in cells[2]
            assert dnp or len(cells) == len(headers), (url, cells)
            players.append({
                'name': row['name'], 'profile_url': urljoin(BASE, row['profile']),
                'player_slug': urlsplit(row['profile']).path.split('/players/')[1],
                'jersey': int(number.group(1)), 'position': cells[1], 'dnp': dnp,
                'dnp_label': cells[2] if dnp else None,
                'minutes_display': None if dnp else cells[2],
                'stats': None if dnp else dict(zip(headers[3:], cells[3:])),
            })
        total_cells = table['rows'][-1]['cells']
        totals = dict(zip(headers[2:], total_cells[2:]))
        score = int(period['cells'][-1])
        teams.append({
            'side': side, 'name': event[side + 'Team']['name'],
            'team_slug': urlsplit(event[side + 'Team']['url']).path.split('/teams/')[1],
            'score': score, 'period_scores': [int(v) for v in period['cells'][1:-1]],
            'players': players, 'totals': totals,
        })
    return {'url': url, 'site_game_id': urlsplit(url).path.rsplit('/', 1)[1],
            'start_utc': event['startDate'],
            'date': datetime.fromisoformat(event['startDate'].replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=8))).date().isoformat(),
            'venue': event['location']['name'], 'teams': teams}


def run():
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    initial = fetch(SCHEDULE, 'schedule')
    month_links = list(dict.fromkeys(html.unescape(x) for x in re.findall(r'href="([^"]+month=\d{4}-\d{2})"', initial)))
    game_links = list(dict.fromkeys(re.findall(r'href="(/mn/games/\d+)"', initial)))
    for relative in month_links:
        month = relative.rsplit('=', 1)[1]
        page = fetch(urljoin(BASE, relative), 'schedule-' + month)
        links = list(dict.fromkeys(re.findall(r'href="(/mn/games/\d+)"', page)))
        print('Month', month, len(links), flush=True)
        game_links.extend(links)
    game_links = list(dict.fromkeys(game_links))
    assert game_links, 'No game links found; check the schedule URL and source layout'
    print('Schedule game count:', len(game_links), flush=True)
    games = []
    failures = []
    for index, relative in enumerate(game_links):
        game_id = relative.rsplit('/', 1)[1]
        bilingual = {}
        for lang in ('mn', 'en'):
            url = BASE + relative.replace('/mn/', '/' + lang + '/')
            try:
                source = fetch(url, f'game-{game_id}-{lang}')
                bilingual[lang] = parse_game(source, url)
            except Exception as exc:
                failures.append({'url': url, 'error': str(exc)})
                print('FAIL', url, str(exc), flush=True)
        games.append(bilingual)
        write_json(OUT / 'boxscores.json', games)
        write_json(OUT / 'fetch-errors.json', failures)
        if (index + 1) % 10 == 0 or index + 1 == len(game_links):
            print('Fetched', index + 1, '/', len(game_links), 'games;', len(failures), 'errors', flush=True)
    return games, failures


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--schedule-url', default=SCHEDULE, help='Public Mongolian schedule URL with season and type selected')
    parser.add_argument('--output', type=Path, default=OUT, help='New directory for this public collection')
    args = parser.parse_args()
    if not args.schedule_url.startswith(BASE + '/mn/competitions/league/schedule?'):
        parser.error('Use the public mongolia.basketball Mongolian league schedule URL')
    SCHEDULE, OUT = args.schedule_url, args.output
    ARCHIVE, manifest_path = OUT / 'sources', OUT / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf8')) if manifest_path.exists() else {}
    games, errors = run()
    write_json(OUT / 'collection-meta.json', {'schedule_url': SCHEDULE, 'games': len(games), 'errors': len(errors)})
    raise SystemExit(1 if errors else 0)
