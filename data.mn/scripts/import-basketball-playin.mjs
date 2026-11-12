import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

// Reviewed transcription of the three supplied FIBA reports. Ratios are printed
// makes/attempts; DNP cells stay null. Team order is not a home/away assertion.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const out = path.join(root, 'outputs/mongolian-basketball-2025-26-playin');
const names = {
  BSM: {
    1: 'Насанжаргал Ганбаатар',
    5: 'Галлоуэй Жонатан',
    6: 'Сүхбат Батзориг',
    7: 'Цэлмэг Гантулга',
    8: 'Авирмэд Лхагва',
    9: 'Өлзийбат Мягмарсүрэн',
    11: 'Төгөлдөр Отгонжаргал',
    12: 'Мандахбаяр Ганбат',
    15: 'Карьер Гринавэй',
    21: 'Наранбаатар Батдэлгэр',
    27: 'Дорж-Арилд Энхбат',
    33: 'Очирбат Отгонбаяр',
  },
  TLG: {
    0: 'Уртнасан Урдийнбиш',
    1: 'Жр Кори Сандерс',
    2: 'Гантөмөр Эрдэнэ-Очир',
    7: 'Ирмүүн Эрдэнэцогт',
    8: 'Дөлгөөн Энхцогт',
    9: 'Чинбат Гэрэл',
    13: 'Хосбаяр Эрдэнэбат',
    15: 'Билгүүн Наран-Оюун',
    17: 'Билгүүн Гансүх',
    19: 'Батзолбоо Боргил',
    21: 'Агваанданзанням Эрдэнэхуяг',
    23: 'Тулга Сүхбаатар',
    24: 'Рэнцэнтогтох Доржсүрэн',
    34: 'Жонес Арон',
  },
};
const reports = [
  {
    id: '5196480',
    date: '2026-03-24',
    time: '18:10',
    duration: '01:49',
    file: '881507872_955564280687987_125731774450485901_n.jpg',
    a: 'BSM',
    b: 'TLG',
    score: [73, 76],
    quarters: [
      [19, 13],
      [16, 24],
      [25, 18],
      [13, 21],
    ],
    rows: {
      BSM: `1 06:19 0/3 0/2 0/1 0/0 0 0 0 0 1 0 0 0 0 -11 -4 0
5* 34:10 7/7 7/7 0/0 5/5 3 11 14 1 3 1 0 2 4 -1 32 19
6* 35:22 10/27 7/17 3/10 8/10 2 3 5 7 4 0 0 5 8 2 20 31
7* 25:28 1/5 1/2 0/3 0/0 0 3 3 1 1 1 0 1 0 0 2 2
8 14:39 2/5 1/2 1/3 0/0 2 2 4 1 2 1 0 3 1 -4 6 5
9* 16:22 1/3 1/2 0/1 0/0 1 2 3 0 0 2 0 2 1 -8 5 2
11* 31:08 2/7 2/6 0/1 0/0 2 3 5 1 5 1 0 5 2 13 1 4
12 DNP
15 23:46 5/10 5/6 0/4 0/1 0 3 3 4 4 2 0 2 4 5 9 10
21 05:42 0/1 0/0 0/1 0/0 0 1 1 0 0 0 1 0 0 -2 1 0
27 07:04 0/0 0/0 0/0 0/0 0 1 1 0 0 0 0 0 0 -9 1 0
33 DNP`,
      TLG: `1 34:16 12/20 11/17 1/3 10/13 1 5 6 7 4 3 0 0 9 7 36 35
2* 04:43 1/3 1/1 0/2 0/0 0 0 0 1 1 0 0 0 0 -4 0 2
7 21:27 2/4 0/2 2/2 1/2 2 2 4 0 1 1 1 1 2 -3 9 7
8 17:34 0/5 0/0 0/5 3/4 1 1 2 2 2 1 0 2 2 -4 0 3
9 17:06 1/2 1/2 0/0 0/0 1 2 3 1 0 2 0 4 0 0 7 2
13* 19:41 2/6 2/5 0/1 1/2 0 3 3 1 1 0 0 4 2 1 3 5
15 DNP
17 16:40 1/2 1/2 0/0 3/4 0 1 1 1 3 0 0 2 2 11 2 5
19* 24:00 0/3 0/0 0/3 0/0 0 2 2 0 0 1 0 3 0 7 0 0
21* 14:33 0/0 0/0 0/0 2/4 2 3 5 0 2 1 2 2 2 7 6 2
23 DNP
24 04:16 0/3 0/1 0/2 0/0 0 0 0 0 0 0 0 0 0 -4 -3 0
34* 25:44 7/14 6/9 1/5 0/2 2 5 7 1 0 5 0 2 1 -3 19 15`,
    },
    totals: {
      BSM: '200:00 28/68 24/44 4/24 13/16 14 31 45 15 20 8 1 20 20 -3 79 73',
      TLG: '200:00 26/62 22/39 4/23 20/31 11 24 35 14 14 14 3 20 20 3 81 76',
    },
    coach: { BSM: [4, 2, 6, 0], TLG: [2, 0, 2, 0] },
  },
  {
    id: '5196481',
    date: '2026-03-26',
    time: '18:10',
    duration: '01:48',
    file: '880870260_990035433529532_5420118400063388803_n.jpg',
    a: 'TLG',
    b: 'BSM',
    score: [65, 71],
    quarters: [
      [16, 17],
      [17, 15],
      [18, 18],
      [14, 21],
    ],
    rows: {
      TLG: `0 DNP
1 30:07 0/7 0/2 0/5 5/8 2 4 6 10 3 2 0 2 5 -1 10 5
2* 11:08 2/2 1/1 1/1 0/2 0 1 1 0 5 2 0 0 3 0 1 5
7 20:57 6/7 6/7 0/0 3/4 1 3 4 1 3 1 1 3 4 2 17 15
8 28:32 6/13 3/5 3/8 0/0 2 4 6 3 1 0 0 3 3 0 16 15
9 08:12 0/1 0/0 0/1 0/0 0 2 2 1 1 0 0 1 0 -1 1 0
13* 22:02 2/7 2/4 0/3 2/3 0 0 0 4 3 1 0 5 3 -6 2 6
15 DNP
17 07:35 1/2 1/2 0/0 0/2 0 1 1 0 1 1 0 0 1 -8 0 2
19* 23:03 2/8 1/2 1/6 0/0 2 1 3 0 0 0 0 3 1 -5 2 5
21* 18:15 2/5 2/3 0/2 0/0 2 2 4 0 0 0 0 5 2 -8 5 4
23 DNP
24 00:16 0/0 0/0 0/0 0/0 0 0 0 0 0 0 0 0 0 0 0 0
34* 29:53 4/10 4/7 0/3 0/0 4 7 11 2 1 2 4 2 1 -3 20 8`,
      BSM: `1 05:11 0/0 0/0 0/0 0/0 0 1 1 0 2 0 0 3 0 1 -1 0
5* 38:27 4/6 4/6 0/0 5/8 4 7 11 4 4 1 0 4 5 3 20 13
6* 35:21 5/13 4/9 1/4 2/2 0 3 3 3 1 1 0 3 6 10 11 13
7* 22:53 2/6 2/6 0/0 1/2 1 5 6 1 1 2 0 1 1 3 8 5
8 16:28 2/5 2/3 0/2 1/2 2 2 4 1 0 0 0 4 2 4 6 5
9* 24:11 4/11 2/3 2/8 2/3 1 1 2 3 1 4 0 4 2 6 12 12
11* 26:12 3/9 2/5 1/4 1/2 1 2 3 1 0 2 0 2 2 6 7 8
12 DNP
15 19:04 4/9 3/5 1/4 4/5 0 4 4 3 4 1 0 0 5 3 11 13
21 08:12 1/1 1/1 0/0 0/0 0 3 3 0 1 0 0 3 0 -5 4 2
27 04:01 0/0 0/0 0/0 0/0 0 0 0 1 1 0 0 0 0 -1 0 0
33 DNP`,
    },
    totals: {
      TLG: '200:00 25/62 20/33 5/29 10/19 14 27 41 21 19 9 5 24 23 -6 76 65',
      BSM: '200:00 25/60 20/38 5/22 16/24 12 28 40 17 15 11 0 24 23 6 81 71',
    },
    coach: { TLG: [1, 2, 3, 1], BSM: [3, 0, 3, 0] },
  },
  {
    id: '5197952',
    date: '2026-03-28',
    time: '13:40',
    duration: '01:47',
    file: '881387860_2172173860351401_6745540216514604579_n.jpg',
    a: 'BSM',
    b: 'TLG',
    score: [75, 76],
    quarters: [
      [26, 21],
      [14, 18],
      [18, 12],
      [17, 25],
    ],
    rows: {
      BSM: `1 02:13 0/0 0/0 0/0 0/0 0 0 0 0 1 0 0 0 0 -4 -1 0
5* 40:00 0/0 0/0 0/0 10/12 3 8 11 3 1 0 1 3 9 -1 22 10
6* 23:03 2/8 0/4 2/4 1/1 2 2 4 3 3 0 0 4 1 -10 5 7
7* 32:51 6/10 4/7 2/3 1/2 3 8 11 2 2 0 1 4 3 10 22 15
8 16:01 1/8 0/4 1/4 0/0 1 1 2 1 1 1 0 4 1 8 -1 3
9* 09:28 0/5 0/2 0/3 1/2 0 1 1 0 2 1 0 0 2 -9 -5 1
11* 37:47 8/13 5/9 3/4 0/0 0 5 5 1 7 2 0 3 1 3 15 19
12 DNP
15 20:00 2/6 2/3 0/3 3/4 0 3 3 3 1 1 0 2 3 2 8 7
21 02:32 0/0 0/0 0/0 0/0 0 1 1 0 1 0 0 0 0 -7 0 0
27 16:05 5/8 2/4 3/4 0/0 0 0 0 1 0 1 0 2 0 3 12 13
33 DNP`,
      TLG: `1 33:11 7/19 6/15 1/4 8/12 1 6 7 7 2 3 0 1 10 -8 22 23
2 02:15 0/0 0/0 0/0 0/0 0 0 0 0 1 1 0 1 0 3 0 0
7 29:19 4/11 2/6 2/5 2/3 2 4 6 0 1 1 0 3 3 -9 10 12
8* 29:29 4/6 0/0 4/6 2/2 2 3 5 1 2 3 0 4 2 24 19 14
9 08:25 0/0 0/0 0/0 0/2 1 1 2 0 0 0 0 0 1 -9 0 0
13 22:13 3/9 3/8 0/1 0/0 0 3 3 0 0 0 0 1 2 -11 3 6
17* 15:38 5/11 5/11 0/0 1/1 2 1 3 0 2 0 0 2 2 -5 6 11
19* 14:55 1/3 0/0 1/3 0/0 2 3 5 2 2 0 0 5 1 18 6 3
21* 14:40 0/3 0/3 0/0 0/0 1 0 1 0 0 1 0 2 0 4 -1 0
23 DNP
24 03:06 0/1 0/0 0/1 0/0 0 0 0 0 0 0 0 0 0 -9 -1 0
34* 26:49 3/11 3/7 0/4 1/2 8 3 11 2 2 3 2 2 1 7 14 7`,
    },
    totals: {
      BSM: '200:00 24/58 13/33 11/25 16/21 10 30 40 14 20 6 2 22 20 -1 78 75',
      TLG: '200:00 27/74 19/50 8/24 14/22 20 24 44 12 12 12 2 21 22 1 79 76',
    },
    coach: { BSM: [1, 1, 2, 1], TLG: [1, 0, 1, 0] },
  },
];
const countKeys = [
  'off_rebounds',
  'def_rebounds',
  'total_rebounds',
  'assists',
  'turnovers',
  'steals',
  'blocks',
  'personal_fouls',
  'fouls_drawn',
  'plus_minus',
  'efficiency',
  'points',
];
const shotKeys = ['fg', 'two_pt', 'three_pt', 'ft'];
// The reports use ties-to-even rounding (13/16 is printed as 81.2%).
const percentage = (m, a) => {
  if (!a) return 0;
  const numerator = m * 1000,
    whole = Math.floor(numerator / a),
    remainder = numerator % a;
  return (2 * remainder === a ? whole + (whole % 2) : Math.round(numerator / a)) / 10;
};
function stats(text) {
  const [minutes, ...v] = text.split(/\s+/);
  if (v.length !== 16) throw new Error(`Expected 16 stat cells: ${text} (${v.length})`);
  const row = { minutes };
  shotKeys.forEach((k, i) => {
    const [m, a] = v[i].split('/').map(Number);
    row[k + '_made'] = m;
    row[k + '_attempted'] = a;
    row[k + '_pct'] = percentage(m, a);
  });
  countKeys.forEach((k, i) => {
    row[k] = Number(v[i + 4]);
  });
  return row;
}
const collection = { games: [], players: [], team_totals: [], team_coach_rows: [], qa_checks: [], missing_games: [] };
for (const r of reports) {
  const base = { game_id: r.id, date: r.date, season: '2025-26', phase: 'Play-in', source_file: r.file };
  const game = {
    ...base,
    round: 'Play-in',
    venue: 'MBank Arena',
    start_time: r.time,
    game_duration: r.duration,
    team1_code: r.a,
    team2_code: r.b,
    team1_score: r.score[0],
    team2_score: r.score[1],
    winner_code: r.score[0] > r.score[1] ? r.a : r.b,
    overtime_periods: 0,
    boxscore_available: true,
  };
  r.quarters.forEach((q, i) => {
    game[`team1_q${i + 1}`] = q[0];
    game[`team2_q${i + 1}`] = q[1];
  });
  collection.games.push(game);
  for (const team of [r.a, r.b]) {
    const context = {
      ...base,
      team_code: team,
      source_team_code: team === 'BSM' ? 'МЛС' : 'TLG',
      team_name: team === 'BSM' ? 'MONGOLIANS' : 'ТЛЖ Түшиг Багана',
    };
    for (const line of r.rows[team].split('\n')) {
      const [jersey, ...cells] = line.split(/\s+/);
      const number = Number(jersey.replace('*', ''));
      const dnp = cells[0] === 'DNP';
      const stat = dnp
        ? Object.fromEntries(
            ['minutes', ...shotKeys.flatMap((k) => [k + '_made', k + '_attempted', k + '_pct']), ...countKeys].map(
              (k) => [k, null]
            )
          )
        : stats(cells.join(' '));
      collection.players.push({
        ...context,
        jersey_no: number,
        player_name_mn: names[team][number],
        starter: jersey.includes('*'),
        did_not_play: dnp,
        ...stat,
      });
    }
    collection.team_totals.push({ ...context, ...stats(r.totals[team]) });
    const [or, dr, tr, to] = r.coach[team];
    collection.team_coach_rows.push({
      ...context,
      off_rebounds: or,
      def_rebounds: dr,
      total_rebounds: tr,
      turnovers: to,
    });
  }
}
fs.mkdirSync(path.join(out, 'data'), { recursive: true });
fs.writeFileSync(path.join(out, 'data/collection.json'), JSON.stringify(collection, null, 2) + '\n');
const checks = [];
function check(label, actual, expected) {
  checks.push({ label, actual, expected, pass: actual === expected });
}
for (const g of collection.games) {
  for (const [side, team] of [
    [1, g.team1_code],
    [2, g.team2_code],
  ]) {
    const total = collection.team_totals.find((t) => t.game_id === g.game_id && t.team_code === team);
    const players = collection.players.filter(
      (p) => p.game_id === g.game_id && p.team_code === team && !p.did_not_play
    );
    const coach = collection.team_coach_rows.find((t) => t.game_id === g.game_id && t.team_code === team);
    const label = `${g.game_id} ${team}`;
    check(
      label + ' quarters',
      [1, 2, 3, 4].reduce((n, q) => n + g[`team${side}_q${q}`], 0),
      g[`team${side}_score`]
    );
    check(label + ' points', total.points, g[`team${side}_score`]);
    for (const k of [
      ...shotKeys.flatMap((s) => [s + '_made', s + '_attempted']),
      ...countKeys.filter((k) => !['plus_minus', 'efficiency'].includes(k)),
    ])
      check(label + ' ' + k, players.reduce((n, p) => n + p[k], 0) + (coach[k] || 0), total[k]);
    check(
      label + ' plus_minus',
      players.reduce((n, p) => n + p.plus_minus, 0),
      total.plus_minus * 5
    );
    check(
      label + ' playing seconds',
      players.reduce((n, p) => {
        const [m, s] = p.minutes.split(':').map(Number);
        return n + m * 60 + s;
      }, 0),
      12000
    );
    check(label + ' starters', players.filter((p) => p.starter).length, 5);
    for (const p of [...players, total]) {
      const key = label + ' #' + (p.jersey_no ?? 'total');
      check(key + ' shooting points', 2 * p.two_pt_made + 3 * p.three_pt_made + p.ft_made, p.points);
      check(key + ' fg made', p.two_pt_made + p.three_pt_made, p.fg_made);
      check(key + ' fg attempts', p.two_pt_attempted + p.three_pt_attempted, p.fg_attempted);
      check(key + ' rebounds', p.off_rebounds + p.def_rebounds, p.total_rebounds);
    }
  }
}
const failed = checks.filter((c) => !c.pass);
fs.writeFileSync(
  path.join(out, 'validation.json'),
  JSON.stringify({ checks: checks.length, failures: failed }, null, 2) + '\n'
);
console.log(
  JSON.stringify(
    {
      games: collection.games.length,
      players: collection.players.length,
      totals: collection.team_totals.length,
      checks: checks.length,
      failures: failed,
    },
    null,
    2
  )
);
if (failed.length) process.exitCode = 1;

// Copy only the supplied report images when their input directory is provided.
if (process.argv[2]) {
  fs.mkdirSync(path.join(out, 'sources'), { recursive: true });
  for (const r of reports) fs.copyFileSync(path.join(process.argv[2], r.file), path.join(out, 'sources', r.file));
}
const manifest = reports.map((r) => ({
  game_id: r.id,
  source_file: r.file,
  sha256: fs.existsSync(path.join(out, 'sources', r.file))
    ? crypto
        .createHash('sha256')
        .update(fs.readFileSync(path.join(out, 'sources', r.file)))
        .digest('hex')
    : null,
}));
fs.writeFileSync(path.join(out, 'source-manifest.json'), JSON.stringify(manifest, null, 2) + '\n');

// Language-paired CSV intermediates use identical columns and numeric values.
// Proper names and original report labels are preserved in both languages.
const mn = {
  game_id: 'Тоглолтын дугаар',
  date: 'Огноо',
  season: 'Улирал',
  phase: 'Шат',
  source_file: 'Эх сурвалжийн файл',
  round: 'Үе шат',
  venue: 'Танхим',
  start_time: 'Эхлэх цаг',
  game_duration: 'Үргэлжилсэн хугацаа',
  team1_code: 'Баг 1 код',
  team2_code: 'Баг 2 код',
  team1_score: 'Баг 1 оноо',
  team2_score: 'Баг 2 оноо',
  winner_code: 'Ялагчийн код',
  overtime_periods: 'Нэмэлт үе',
  boxscore_available: 'Дэлгэрэнгүй статистиктай',
  team_code: 'Багийн код',
  source_team_code: 'Эх сурвалжийн багийн код',
  team_name: 'Багийн нэр',
  jersey_no: 'Өмсгөлийн дугаар',
  player_name_mn: 'Тоглогчийн нэр',
  starter: 'Гарааны тоглогч',
  did_not_play: 'Тоглоогүй',
  minutes: 'Тоглосон минут',
  off_rebounds: 'Довтолгооны самбар',
  def_rebounds: 'Хамгаалалтын самбар',
  total_rebounds: 'Нийт самбар',
  assists: 'Дамжуулалт',
  turnovers: 'Бөмбөг алдалт',
  steals: 'Бөмбөг таслалт',
  blocks: 'Хаалт',
  personal_fouls: 'Хувийн алдаа',
  fouls_drawn: 'Эсрэг багийн алдаа',
  plus_minus: 'Нэмэх хасах',
  efficiency: 'Үр ашиг',
  points: 'Оноо',
};
for (const [key, label] of Object.entries({
  fg: 'Нийт шидэлт',
  two_pt: '2 онооны шидэлт',
  three_pt: '3 онооны шидэлт',
  ft: 'Чөлөөт шидэлт',
}))
  for (const [suffix, word] of Object.entries({ made: 'амжилттай', attempted: 'оролдлого', pct: 'хувь' }))
    mn[key + '_' + suffix] = label + ' ' + word;
for (const side of [1, 2]) for (const q of [1, 2, 3, 4]) mn[`team${side}_q${q}`] = `Баг ${side} үе ${q}`;
const csvCell = (v) => {
  const s = String(v ?? '');
  return /[",\n\r]/.test(s) ? '"' + s.replaceAll('"', '""') + '"' : s;
};
for (const table of ['games', 'players', 'team_totals']) {
  const rows = collection[table],
    keys = Object.keys(rows[0]);
  for (const lang of ['en', 'mn']) {
    const lines = [
      keys.map((k) => (lang === 'mn' ? mn[k] : k)),
      ...rows.map((r) =>
        keys.map((k) => ((lang === 'mn' && k === 'phase') || (lang === 'mn' && k === 'round') ? 'Плей-ин' : r[k]))
      ),
    ];
    fs.writeFileSync(
      path.join(out, 'data', `${table}-${lang}.csv`),
      '\uFEFF' + lines.map((r) => r.map(csvCell).join(',')).join('\r\n') + '\r\n'
    );
  }
}
