import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Rebuild the browser data from the reviewed local collections. No source is modified.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const out = path.join(root, 'data.mn/public/sports');
const sourceRoot = process.env.BASKETBALL_ARCHIVE_ROOT || path.join(root, 'outputs');
const inputs = [
  ['2024-25', ['mongolian-basketball-2024-25']],
  [
    '2025-26',
    [
      'mongolian-basketball-2025-26-regular-web',
      'mongolian-basketball-playoff-screenshots-2026-10-06',
      'mongolian-basketball-2025-26-playin',
    ],
  ],
];
const teams = {
  BCH: ['BCH Knights', 'Би Си Эйч Найтс', '#4467a8'],
  BIS: ['Nalaikh Bison', 'Налайх Бизон', '#8d673d'],
  BTM: ['Bishrelt Metall', 'Бишрэлт Металл', '#64748b'],
  DUA: ['Darkhan United', 'Дархан Юнайтед', '#bd514b'],
  ETM: ['Erdenet Miners', 'Эрдэнэт Майнерс', '#218478'],
  KUL: ['Khuleguud', 'Хүлэгүүд', '#274896'],
  SEL: ['Selenge Bodons', 'Сэлэнгэ Бодонс', '#bc732d'],
  SGA: ['SG Apes', 'Эс Жи Эйпс', '#684bac'],
  TLG: ['Inut Yes TLG', 'Инүт Ес ТЛЖ', '#a3476b'],
  ZVB: ['Zavkhan Brothers', 'Завхан Бродерс', '#3384a2'],
  MFC: ['Chi Forest Mongolians', 'Чи Форест Монголианс', '#548351'],
  BSM: ['Burens Score Mongolians', 'Бүрэн Скор Монголианс', '#548351'],
  XOB: ['Khovd Shonhoruud', 'Ховд Шонхорууд', '#6e668b'],
  KHF: ['Khan Falcons', 'Хан Фалконс', '#427367'],
};
const fields = [
  'minutes',
  'fg_made',
  'fg_attempted',
  'two_pt_made',
  'two_pt_attempted',
  'three_pt_made',
  'three_pt_attempted',
  'ft_made',
  'ft_attempted',
  'off_rebounds',
  'def_rebounds',
  'total_rebounds',
  'assists',
  'turnovers',
  'steals',
  'blocks',
  'personal_fouls',
  'plus_minus',
  'efficiency',
  'points',
];
const code = (c) => (c === 'BRO' ? 'KUL' : c);
const statRow = (r) => Object.fromEntries(fields.map((k) => [k, r[k] ?? null]));
// A display fallback, not a claim about a player's official Latin spelling.
const alphabet = {
  а: 'a',
  б: 'b',
  в: 'v',
  г: 'g',
  д: 'd',
  е: 'e',
  ё: 'yo',
  ж: 'j',
  з: 'z',
  и: 'i',
  й: 'i',
  к: 'k',
  л: 'l',
  м: 'm',
  н: 'n',
  о: 'o',
  ө: 'ö',
  п: 'p',
  р: 'r',
  с: 's',
  т: 't',
  у: 'u',
  ү: 'ü',
  ф: 'f',
  х: 'kh',
  ц: 'ts',
  ч: 'ch',
  ш: 'sh',
  щ: 'shch',
  ъ: '',
  ы: 'y',
  ь: '',
  э: 'e',
  ю: 'yu',
  я: 'ya',
};
const romanize = (name) =>
  [...name]
    .map((c) => {
      const lower = c.toLocaleLowerCase(),
        value = alphabet[lower];
      return value === undefined ? c : c === lower ? value : value.charAt(0).toUpperCase() + value.slice(1);
    })
    .join('');
const normalizedName = (name) => name.normalize('NFC').trim().toLocaleLowerCase().replace(/\s+/g, ' ');
const initialsName = (name) => {
  const parts = normalizedName(name).split(' ');
  return parts.length === 2 ? `${parts[0][0]}.${parts[1]}` : normalizedName(name);
};
const seasons = inputs.map(([id, folders]) => {
  const sources = folders.map((folder) =>
    JSON.parse(fs.readFileSync(path.join(sourceRoot, folder, 'data/collection.json'), 'utf8').replace(/^\uFEFF/, ''))
  );
  const source = Object.fromEntries(
    ['games', 'players', 'team_totals', 'qa_checks', 'missing_games'].map((key) => [
      key,
      sources.flatMap((s) => s[key] || []),
    ])
  );
  if (new Set(source.games.map((g) => String(g.game_id))).size !== source.games.length)
    throw new Error(`Duplicate game IDs in ${id}`);
  const games = source.games
    .map((g) => ({
      id: String(g.game_id),
      date: g.date,
      phase: g.phase === 'Finals' ? 'Playoffs' : g.phase,
      round: g.round || g.phase,
      a: code(g.team1_code),
      b: code(g.team2_code),
      scoreA: g.team1_score,
      scoreB: g.team2_score,
      ot: g.overtime_periods ?? null,
      box: g.boxscore_available !== false,
      periods: [1, 2, 3, 4, 5, 6]
        .map((n) => [g[`team1_q${n}`] ?? null, g[`team2_q${n}`] ?? null])
        .filter((p) => p.some((v) => v !== null)),
      source: g.source_file,
      dateSource: g.metadata_source_url || null,
      sourceUrl: { en: g.source_url_en || null, mn: g.source_url_mn || null },
      minutesPrecision: g.minutes_precision || 'seconds',
    }))
    .sort((a, b) => a.date.localeCompare(b.date) || a.id.localeCompare(b.id));
  const officialNames = new Map();
  for (const p of source.players.filter((p) => p.player_name_en && p.source_player_id)) {
    const key = `${code(p.team_code)}|${normalizedName(p.player_name_mn)}`;
    const identities = officialNames.get(key) || new Map();
    identities.set(p.source_player_id, p);
    officialNames.set(key, identities);
  }
  const players = source.players.map((p) => {
    const name = (p.player_name_mn || p.player_name || '').normalize('NFC').trim();
    const names =
      officialNames.get(`${code(p.team_code)}|${normalizedName(name)}`) ||
      officialNames.get(`${code(p.team_code)}|${initialsName(name)}`);
    const official = p.player_name_en ? p : names?.size === 1 ? [...names.values()][0] : null;
    return {
      game: String(p.game_id),
      team: code(p.team_code),
      name,
      nameEn: official?.player_name_en || romanize(name),
      nameSource: official ? 'league' : /[А-Яа-яЁёӨөҮү]/.test(name) ? 'transliterated' : 'report',
      // Match initials only when unambiguous within this season and team.
      identity: official ? `league:${official.source_player_id}` : `report:${normalizedName(name)}`,
      jersey: p.jersey_no,
      starter: p.starter ?? null,
      dnp: !!p.did_not_play,
      ...statRow(p),
    };
  });
  return {
    id,
    resultsOnly: false,
    games,
    players,
    totals: source.team_totals.map((t) => ({ game: String(t.game_id), team: code(t.team_code), ...statRow(t) })),
    issues: source.qa_checks.map((q) => ({
      game: String(q.game_id),
      team: code(q.team_code),
      stat: q.stat,
      issue: q.issue,
      issueMn: q.issue_mn || null,
    })),
    missing: source.missing_games || [],
    regularTarget: 135,
    sourceLabel: folders.join(' + '),
  };
});
// Older Koo seasons expose final results only. Keep historical team labels and
// season-scoped IDs; sponsor changes do not establish franchise identities.
const colors = Object.values(teams).map((t) => t[2]);
for (const id of ['2022-23', '2023-24']) {
  const folder = `koo-basketball-${id}`;
  const source = JSON.parse(
    fs.readFileSync(path.join(sourceRoot, folder, 'data/season.json'), 'utf8').replace(/^\uFEFF/, '')
  );
  const teamId = (c) => `KOO-${id}-${c}`;
  for (const [i, team] of source.teams.entries()) {
    teams[teamId(team.team_id)] = [team.team_en, team.team_mn, colors[i % colors.length], team.team_id];
  }
  const games = source.games
    .map((g) => ({
      id: `KOO-${id}-${g.source_game_id}`,
      date: g.date,
      phase: 'Regular season',
      round: 'Regular season',
      a: teamId(g.team1_id),
      b: teamId(g.team2_id),
      scoreA: g.score1,
      scoreB: g.score2,
      box: false,
      ot: null,
      periods: [],
      source: `${folder}/raw · page ${g.source_page}, record ${g.source_game_id}`,
      sourceUrl: { en: g.source_url, mn: g.source_url },
      dateSource: null,
    }))
    .sort((a, b) => a.date.localeCompare(b.date) || a.id.localeCompare(b.id));
  const expected = source.teams.length * (source.teams.length - 1);
  if (games.length !== expected || new Set(games.map((g) => g.id)).size !== expected) {
    throw new Error(`Unexpected Koo archive coverage: ${id}`);
  }
  seasons.push({
    id,
    resultsOnly: true,
    games,
    players: [],
    totals: [],
    issues: [],
    missing: [],
    regularTarget: expected,
    sourceLabel: folder,
    coverageNote:
      id === '2022-23'
        ? {
            en: 'Koo results archive: 10 teams, 18 games each. The supplied export excludes the April 18 Miners 4–0 Metal record (19223), preserved in the source audit. No playoff or player data is supplied.',
            mn: 'Koo үр дүнгийн архив: 10 баг, баг бүр 18 тоглолт. Ирүүлсэн экспортод 4-р сарын 18-ны Майнерс 4–0 Металл (19223) мөрийг хасаж, эх аудитад хадгалсан. Плей-офф болон тоглогчдын өгөгдөл байхгүй.',
          }
        : {
            en: 'Koo results archive: 13 teams, 24 games each; every pair meets twice. No playoff or player data is supplied.',
            mn: 'Koo үр дүнгийн архив: 13 баг, баг бүр 24 тоглолт; багийн хос бүр хоёр удаа тоглосон. Плей-офф болон тоглогчдын өгөгдөл байхгүй.',
          },
  });
}
seasons.sort((a, b) => a.id.localeCompare(b.id));
fs.mkdirSync(out, { recursive: true });
fs.writeFileSync(path.join(out, 'basketball.json'), JSON.stringify({ teams, seasons }));
console.log(seasons.map((s) => `${s.id}: ${s.games.length} games, ${s.players.length} player rows`).join('\n'));
