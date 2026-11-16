const escape = (value) =>
  String(value ?? '').replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
  );
export const playerIdentity = (p) => `${p.team}|${p.identity || p.sourceName || p.name}`;
export const latestSeason = (seasons) =>
  [...seasons].sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true })).at(-1);
export function compareStatRows(a, b, sort, direction) {
  const x = a[sort],
    y = b[sort];
  if (x == null && y == null) return 0;
  if (x == null) return 1;
  if (y == null) return -1;
  return (
    (typeof x === 'string' ? x.localeCompare(y) : x - y) * direction ||
    (b.w || 0) - (a.w || 0) ||
    (b.diff || 0) - (a.diff || 0) ||
    String(a.name || a.id).localeCompare(String(b.name || b.id))
  );
}
const icons = {
  teams: '<path d="M5 20v-8m7 8V4m7 16V8M2 20h20"/>',
  players: '<circle cx="12" cy="7" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>',
  games: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 11h18m-12 4h2m4 0h2"/>',
  compare: '<path d="M3 7h17l-4-4m5 14H4l4 4M20 7l-4 4M4 17l4-4"/>',
  coverage: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-11v2"/>',
  search: '<circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/>',
  download: '<path d="M12 3v12m-4-4 4 4 4-4M4 16v5h16v-5"/>',
  arrow: '<path d="m9 5 7 7-7 7"/>',
};
const svg = (k) =>
  `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[k] || icons.arrow}</svg>`;

async function mountSports() {
  const app = document.getElementById('sports-app');
  if (!app || app.dataset.mounted) return;
  app.dataset.mounted = 'true';
  const t = JSON.parse(app.dataset.copy);
  const lang = app.dataset.language;
  let data;
  try {
    const response = await fetch('/sports/basketball.json');
    if (!response.ok) throw new Error('Data unavailable');
    data = await response.json();
  } catch {
    app.innerHTML = `<p class="sports-loading">${lang === 'mn' ? 'Өгөгдөл ачаалсангүй. Хуудсыг дахин ачаална уу.' : 'The data could not be loaded. Please reload this page.'}</p>`;
    return;
  }
  const stagesFor = (id) =>
    ['Regular season', 'Playoffs', 'Play-in']
      .filter((p) => data.seasons.find((s) => s.id === id).games.some((g) => g.phase === p))
      .concat('All');
  const params = new URLSearchParams(location.search);
  data.seasons.sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
  for (const s of data.seasons)
    for (const p of s.players) {
      p.sourceName = p.name;
      p.name = lang === 'en' ? p.nameEn || p.name : p.name;
    }
  const latest = latestSeason(data.seasons);
  const comparisonTeams = [...new Set(latest.games.flatMap((g) => [g.a, g.b]))].sort();
  const playerKey = playerIdentity;
  const state = {
    season: data.seasons.some((s) => s.id === params.get('season')) ? params.get('season') : latest.id,
    phase: 'Regular season',
    tab: ['teams', 'players', 'games', 'compare', 'coverage'].includes(params.get('view'))
      ? params.get('view')
      : 'teams',
    query: '',
    sort: 'pct',
    direction: -1,
    page: 1,
    compareA: `${latest.id}:${comparisonTeams[0]}`,
    compareB: `${latest.id}:${comparisonTeams[1] || comparisonTeams[0]}`,
  };
  if (['Regular season', 'Playoffs', 'Play-in', 'All'].includes(params.get('stage'))) state.phase = params.get('stage');
  if (!stagesFor(state.season).includes(state.phase)) state.phase = stagesFor(state.season)[0];
  state.sort = state.tab === 'games' ? 'date' : state.tab === 'players' ? 'ppg' : 'pct';
  let focusBeforeDialog;
  let currentExport = { columns: [], rows: [] };
  const season = (id) => data.seasons.find((s) => s.id === (id || state.season));
  const teamName = (c) => data.teams[c]?.[lang === 'mn' ? 1 : 0] || c;
  const teamColor = (c) => data.teams[c]?.[2] || '#52617b';
  const phaseName = (p) =>
    ({
      'Regular season': t.regular,
      Playoffs: t.playoffs,
      'Play-in': t.playin,
      All: t.all,
      Final: t.final,
      Finals: t.final,
      Semifinal: t.semifinal,
      Quarterfinal: t.quarterfinal,
    })[p] || p;
  const f = (n, d = 1) =>
    n === null || n === undefined || !Number.isFinite(n)
      ? '—'
      : n.toLocaleString(lang === 'mn' ? 'mn-MN' : 'en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
  const pct = (n) => (n == null ? '—' : `${f(n * 100, 1)}%`);
  const sum = (rows, key) =>
    rows.length && rows.every((r) => r[key] != null) ? rows.reduce((n, r) => n + Number(r[key]), 0) : null;
  const avg = (rows, key) => {
    const n = sum(rows, key);
    return n == null ? null : n / rows.length;
  };
  const shooting = (rows, m, a) => {
    const made = sum(rows, m),
      attempted = sum(rows, a);
    return made == null || !attempted ? null : made / attempted;
  };
  const shortCode = (c) => data.teams[c]?.[3] || c;
  const initials = (c) => (c === 'KUL' ? 'KH' : shortCode(c).slice(0, 2));
  const badge = (c) => `<span class="sp-badge" style="--team:${teamColor(c)}">${initials(c)}</span>`;
  const teamLink = (c) =>
    `<button class="sp-team-link" data-team="${c}">${badge(c)}<span>${escape(teamName(c))}<small>${shortCode(c)}</small></span></button>`;
  const matches = (value) => String(value).toLocaleLowerCase().includes(state.query.toLocaleLowerCase());
  const gamesFor = (s = season(), p = state.phase) => s.games.filter((g) => p === 'All' || g.phase === p);
  const issuesFor = (s, gs, c, key) => s.issues.some((q) => gs.has(q.game) && q.team === c && (!key || q.stat === key));
  function teamStats(s = season(), p = state.phase) {
    const games = gamesFor(s, p),
      map = new Map();
    for (const g of games)
      for (const c of [g.a, g.b]) {
        if (!map.has(c)) map.set(c, { code: c, name: teamName(c), gp: 0, w: 0, l: 0, pf: 0, pa: 0, form: [] });
        const r = map.get(c),
          a = g.a === c,
          scored = a ? g.scoreA : g.scoreB,
          allowed = a ? g.scoreB : g.scoreA;
        r.gp++;
        r.pf += scored;
        r.pa += allowed;
        r.w += scored > allowed ? 1 : 0;
        r.l += scored < allowed ? 1 : 0;
        r.form.push(scored > allowed ? 'W' : 'L');
      }
    const ids = new Set(games.map((g) => g.id));
    return [...map.values()].map((r) => {
      const rows = s.totals.filter((v) => v.team === r.code && ids.has(v.game));
      return {
        ...r,
        pct: r.w / r.gp,
        ppg: r.pf / r.gp,
        opp: r.pa / r.gp,
        diff: (r.pf - r.pa) / r.gp,
        fg: shooting(rows, 'fg_made', 'fg_attempted'),
        three: shooting(rows, 'three_pt_made', 'three_pt_attempted'),
        ft: shooting(rows, 'ft_made', 'ft_attempted'),
        reb: avg(rows, 'total_rebounds'),
        ast: avg(rows, 'assists'),
        box: rows.length,
        review: issuesFor(s, ids, r.code),
        form: r.form.slice(-5),
      };
    });
  }
  function playerStats(s = season(), p = state.phase, team = null, min = 3) {
    const ids = new Set(gamesFor(s, p).map((g) => g.id)),
      map = new Map();
    for (const row of s.players) {
      if (row.dnp || !ids.has(row.game) || (team && row.team !== team)) continue;
      const key = playerKey(row);
      if (!map.has(key)) map.set(key, { key, name: row.name, code: row.team, teamName: teamName(row.team), rows: [] });
      map.get(key).rows.push(row);
    }
    return [...map.values()]
      .filter((r) => r.rows.length >= min)
      .map((r) => ({
        ...r,
        gp: r.rows.length,
        ppg: avg(r.rows, 'points'),
        reb: avg(r.rows, 'total_rebounds'),
        ast: avg(r.rows, 'assists'),
        fg: shooting(r.rows, 'fg_made', 'fg_attempted'),
        three: shooting(r.rows, 'three_pt_made', 'three_pt_attempted'),
        ft: shooting(r.rows, 'ft_made', 'ft_attempted'),
        review: issuesFor(s, new Set(r.rows.map((v) => v.game)), r.code),
      }));
  }
  function sortRows(rows) {
    return [...rows].sort((a, b) => compareStatRows(a, b, state.sort, state.direction));
  }
  const flag = (row, field) => {
    const key = {
      ppg: 'points',
      reb: 'total_rebounds',
      ast: 'assists',
      fg: 'fg_made',
      three: 'three_pt_made',
      ft: 'ft_made',
    }[field];
    const keys = {
      fg: ['fg_made', 'fg_attempted'],
      three: ['three_pt_made', 'three_pt_attempted'],
      ft: ['ft_made', 'ft_attempted'],
    }[field] || [key];
    const ids = new Set(row.rows ? row.rows.map((v) => v.game) : gamesFor().map((g) => g.id));
    return key && keys.some((k) => issuesFor(season(), ids, row.code, k))
      ? '<sup title="' + escape(t.qualityText) + '">†</sup>'
      : '';
  };
  function table(columns, rows, { sortable = true } = {}) {
    currentExport = { columns, rows };
    return `<p class="sp-scroll-hint">${t.scrollHint} →</p><div class="sp-table-scroll" tabindex="0" role="region" aria-label="${t.scrollHint}"><table class="sp-table"><thead><tr>${columns.map((c) => `<th ${sortable ? 'aria-sort="' + (state.sort === c.key ? (state.direction === 1 ? 'ascending' : 'descending') : 'none') + '"' : ''}>${sortable && c.key ? `<button data-sort="${c.key}" title="${escape(c.title || c.label)}">${escape(c.label)}<span class="sp-sort">${state.sort === c.key ? (state.direction === 1 ? '↑' : '↓') : '↕'}</span></button>` : escape(c.label)}</th>`).join('')}</tr></thead><tbody>${rows.length ? rows.map((r, i) => `<tr>${columns.map((c) => `<td class="${c.class || ''}">${c.render ? c.render(r, i) : escape(r[c.key])}</td>`).join('')}</tr>`).join('') : `<tr><td colspan="${columns.length}" class="sp-empty">${t.noResults}</td></tr>`}</tbody></table></div>`;
  }
  const playerColumns = [
    {
      key: 'name',
      label: t.player,
      class: 'sp-name-cell',
      render: (r) =>
        `<button class="sp-player-link" data-player="${escape(r.key)}">${escape(r.name)}</button><small class="sp-subtext">${escape(teamName(r.code))}</small>`,
    },
    { key: 'gp', label: t.gp, title: t.played },
    { key: 'ppg', label: t.ppg, title: t.pts, render: (r) => `<strong>${f(r.ppg)}</strong>${flag(r, 'ppg')}` },
    { key: 'reb', label: t.reb, render: (r) => f(r.reb) + flag(r, 'reb') },
    { key: 'ast', label: t.ast, render: (r) => f(r.ast) + flag(r, 'ast') },
    { key: 'fg', label: t.fg, render: (r) => pct(r.fg) + flag(r, 'fg') },
    { key: 'three', label: t.three, render: (r) => pct(r.three) + flag(r, 'three') },
    { key: 'ft', label: t.ft, render: (r) => pct(r.ft) + flag(r, 'ft') },
  ];
  const recordColumns = [
    { key: null, label: '#', render: (r, i) => `<span class="sp-rank">${i + 1}</span>` },
    { key: 'name', label: t.team, class: 'sp-name-cell', render: (r) => teamLink(r.code) },
    { key: 'gp', label: t.gp, title: t.played },
    { key: 'w', label: t.wins },
    { key: 'l', label: t.losses },
    {
      key: 'pct',
      label: t.winpct,
      render: (r) => `<div class="sp-pct"><span>${pct(r.pct)}</span><i style="--value:${r.pct * 100}%"></i></div>`,
    },
    { key: 'ppg', label: t.ppg, render: (r) => f(r.ppg) },
    { key: 'opp', label: t.opp, render: (r) => f(r.opp) },
    {
      key: 'diff',
      label: t.diff,
      render: (r) =>
        `<span class="${r.diff >= 0 ? 'sp-positive' : 'sp-negative'}">${r.diff > 0 ? '+' : ''}${f(r.diff)}</span>`,
    },
    {
      key: null,
      label: t.form,
      render: (r) =>
        `<div class="sp-form">${r.form.map((v) => `<span class="${v.toLowerCase()}" title="${v === 'W' ? t.wins : t.losses}">${v === 'W' ? t.wins : t.losses}</span>`).join('')}</div>`,
    },
  ];
  const gameColumns = [
    { key: 'date', label: t.date, render: (r) => `<span class="sp-date">${r.date}</span>` },
    {
      key: 'name',
      label: t.matchup,
      class: 'sp-name-cell',
      render: (r) =>
        `<button class="sp-match-link" data-game="${r.id}">${badge(r.a)}<span>${escape(teamName(r.a))}<small>${escape(teamName(r.b))}</small></span>${badge(r.b)}</button>`,
    },
    {
      key: null,
      label: t.result,
      render: (r) =>
        `<button class="sp-score-inline" data-game="${r.id}">${r.scoreA} <span>–</span> ${r.scoreB}${season().issues.some((q) => q.game === r.id) ? ' <sup>†</sup>' : ''}${r.ot ? `<small>${r.ot}${t.overtime}</small>` : ''}</button>`,
    },
    { key: 'round', label: t.round, render: (r) => escape(phaseName(r.round)) },
    {
      key: null,
      label: t.report,
      render: (r) =>
        `<button class="sp-text-button" data-game="${r.id}">${r.box ? t.box : t.resultOnly} ${svg('arrow')}</button>`,
    },
  ];
  function leaderPanel() {
    if (!season().players.length)
      return `<aside class="sp-leaders"><div class="sp-section-heading"><h2>${t.resultsArchive}</h2></div><p class="sp-table-note">${t.noPlayerStats}</p><button class="sp-view-link" data-tab="games">${t.games} ${svg('arrow')}</button></aside>`;
    const leaders = playerStats()
      .sort((a, b) => b.ppg - a.ppg)
      .slice(0, 5);
    return `<aside class="sp-leaders"><div class="sp-section-heading"><h2>${t.leaders}</h2><span class="sp-unit">${t.ppg}</span></div><p class="sp-caption">${lang === 'mn' ? 'Доод тал нь 3 тоглолт' : 'Minimum 3 appearances'}</p>${leaders.map((r, i) => `<button class="sp-leader" data-player="${escape(r.key)}"><span class="sp-rank">${i + 1}</span>${badge(r.code)}<span class="sp-leader-name">${escape(r.name)}<small>${escape(teamName(r.code))}</small></span><strong>${f(r.ppg)}</strong></button>`).join('')}<button class="sp-view-link" data-tab="players">${t.viewAll} ${svg('arrow')}</button><div class="sp-sidebar-note"><span class="sp-note-icon">i</span><p>${t.tableNote}</p></div></aside>`;
  }
  function recentStrip() {
    return `<div class="sp-section-heading sp-results-heading"><h2>${t.recent}</h2><button class="sp-text-button" data-tab="games">${t.viewAll} ${svg('arrow')}</button></div><div class="sp-results">${gamesFor()
      .slice(-4)
      .reverse()
      .map(
        (g) =>
          `<button class="sp-result" data-game="${g.id}"><div class="sp-result-top"><span>${g.date.slice(5).replace('-', ' / ')}</span><span>${g.ot ? g.ot + t.overtime : t.final}</span></div><div class="sp-result-line ${g.scoreA > g.scoreB ? 'winner' : ''}">${badge(g.a)}<span>${escape(teamName(g.a))}</span><strong>${g.scoreA}</strong></div><div class="sp-result-line ${g.scoreB > g.scoreA ? 'winner' : ''}">${badge(g.b)}<span>${escape(teamName(g.b))}</span><strong>${g.scoreB}</strong></div></button>`
      )
      .join('')}</div>`;
  }
  function compareOptions(value) {
    return data.seasons
      .map(
        (s) =>
          `<optgroup label="${s.id}">${[...new Set(s.games.flatMap((g) => [g.a, g.b]))]
            .sort((a, b) => teamName(a).localeCompare(teamName(b)))
            .map(
              (c) =>
                `<option value="${s.id}:${c}" ${value === `${s.id}:${c}` ? 'selected' : ''}>${escape(teamName(c))} · ${s.id}</option>`
            )
            .join('')}</optgroup>`
      )
      .join('');
  }
  function compareView() {
    const [sa, ca] = state.compareA.split(':'),
      [sb, cb] = state.compareB.split(':');
    const a = teamStats(season(sa)).find((r) => r.code === ca),
      b = teamStats(season(sb)).find((r) => r.code === cb);
    const metrics = [
      ['gp', t.gp],
      ['pct', t.winpct],
      ['ppg', t.ppg],
      ['opp', t.opp],
      ['diff', t.diff],
      ['reb', t.reb],
      ['ast', t.ast],
      ['fg', t.fg],
      ['three', t.three],
      ['ft', t.ft],
    ];
    const fmt = (v, k) => (['pct', 'fg', 'three', 'ft'].includes(k) ? pct(v) : f(v, k === 'gp' ? 0 : 1));
    const meetings = gamesFor(season(sa)).filter(
      (g) => ca !== cb && [g.a, g.b].includes(ca) && [g.a, g.b].includes(cb)
    );
    const meetingsOther =
      sa === sb
        ? []
        : gamesFor(season(sb)).filter((g) => ca !== cb && [g.a, g.b].includes(ca) && [g.a, g.b].includes(cb));
    currentExport = {
      columns: [
        { key: 'metric', label: t.comparison },
        { key: 'a', label: `${teamName(ca)} ${sa}` },
        { key: 'b', label: `${teamName(cb)} ${sb}` },
      ],
      rows: metrics.map(([k, label]) => ({ metric: label, a: fmt(a?.[k], k), b: fmt(b?.[k], k) })),
    };
    return `<section class="sp-panel sp-comparison"><div class="sp-section-heading"><h2>${t.compare}</h2><span class="sp-unit">${phaseName(state.phase)}</span></div><p class="sp-caption">${t.comparisonText}</p>${!a?.box || !b?.box ? `<p class="sp-table-note">${t.resultComparison}</p>` : ''}<div class="sp-compare-select"><label>${t.team} A<select id="sp-compare-a">${compareOptions(state.compareA)}</select></label><span>${t.versus}</span><label>${t.team} B<select id="sp-compare-b">${compareOptions(state.compareB)}</select></label></div><div class="sp-compare-hero"><div>${badge(ca)}<h3>${escape(teamName(ca))}</h3><p>${sa} · ${a ? `${a.w}–${a.l}` : '—'}</p></div><span>${svg('compare')}</span><div>${badge(cb)}<h3>${escape(teamName(cb))}</h3><p>${sb} · ${b ? `${b.w}–${b.l}` : '—'}</p></div></div>${metrics
      .map(([k, label]) => {
        const x = a?.[k],
          y = b?.[k],
          max = Math.max(Math.abs(x || 0), Math.abs(y || 0), 1);
        return `<div class="sp-compare-row"><strong>${fmt(x, k)}</strong><div class="sp-compare-bar left"><i style="width:${(Math.abs(x || 0) / max) * 100}%;background:${teamColor(ca)}"></i></div><span>${label}</span><div class="sp-compare-bar"><i style="width:${(Math.abs(y || 0) / max) * 100}%;background:${teamColor(cb)}"></i></div><strong>${fmt(y, k)}</strong></div>`;
      })
      .join(
        ''
      )}<p class="sp-caption">${t.boxscores}: ${a?.box ?? 0} / ${a?.gp ?? 0} · ${b?.box ?? 0} / ${b?.gp ?? 0}. ${t.qualityText}</p><h3 class="sp-subheading">${t.headToHead}</h3>${[...meetings, ...meetingsOther].length ? `<ul class="sp-meetings">${[...meetings, ...meetingsOther].map((g) => `<li><span>${g.date}</span> ${escape(teamName(g.a))} <strong>${g.scoreA}–${g.scoreB}</strong> ${escape(teamName(g.b))}</li>`).join('')}</ul>` : `<p class="sp-caption">${t.noMeeting}</p>`}</section>`;
  }
  function coverageSummary(s) {
    const stages = ['Regular season', 'Playoffs', 'Play-in'].map((phase) => {
      const count = s.games.filter((g) => g.phase === phase).length;
      return `${phaseName(phase)}: ${count}${phase === 'Regular season' && s.regularTarget ? ` / ${s.regularTarget}` : ''}`;
    });
    return `${s.resultsOnly ? t.resultsArchive + '. ' : ''}${stages.join(' · ')}. ${s.games.filter((g) => !g.box).length} ${t.scoreOnly}. ${t.reviewFlags}: ${s.issues.length}.`;
  }
  function reviewList(s, game = null) {
    const issues = s.issues.filter((q) => !game || q.game === game);
    return issues.length
      ? `<details class="sp-source sp-review" ${game ? 'open' : ''}><summary>${t.reviewFlags} (${issues.length})</summary><ul>${issues.map((q) => `<li><strong>${escape(q.game)} · ${escape(teamName(q.team))}</strong>: ${escape(lang === 'mn' ? q.issueMn || t.legacyFlag : q.issue)}${lang === 'mn' && !q.issueMn ? `<details><summary>${t.originalNote}</summary><p lang="en">${escape(q.issue)}</p></details>` : ''}</li>`).join('')}</ul></details>`
      : '';
  }
  const datasetLinks = () =>
    [
      ['basketball-game-results', t.datasetGames],
      ['basketball-team-records', t.datasetTeams],
      ['basketball-player-game-stats', t.datasetPlayers],
    ]
      .map(([id, label]) => `<li><a href="/${lang}/data/${id}">${label}</a></li>`)
      .join('');
  function coverageView() {
    currentExport = {
      columns: [
        { key: 'season', label: t.season },
        { key: 'games', label: t.games },
        { key: 'boxes', label: t.boxscores },
        { key: 'issues', label: t.reviewFlags },
      ],
      rows: data.seasons.map((s) => ({
        season: s.id,
        games: s.games.length,
        boxes: s.games.filter((g) => g.box).length,
        issues: s.issues.length,
      })),
    };
    return `<section class="sp-panel sp-methodology"><span class="sp-eyebrow">${t.coverage}</span><h2>${t.aboutTitle}</h2><div class="sp-coverage-grid">${data.seasons.map((s) => `<article><h3>${s.id}</h3><strong>${s.games.length}<small>${t.games}</small></strong><p>${coverageSummary(s)}</p>${s.coverageNote ? `<p>${escape(s.coverageNote[lang])}</p>` : ''}<dl><dt>${t.full}</dt><dd>${s.games.filter((g) => g.box).length}</dd><dt>${t.range}</dt><dd>${s.games[0]?.date || '—'} → ${s.games.at(-1)?.date || '—'}</dd></dl></article>`).join('')}</div><h3>${t.fullDatasets}</h3><ul class="sp-dataset-links">${datasetLinks()}</ul><h3>${t.methodology}</h3><p>${t.methodologyText}</p><p>${t.qualityText}</p><p>${t.nameNote}</p><p>${t.historicalNames}</p><p>${t.precisionNote}</p><h3>${t.missing}</h3><p>${t.missingText}</p>${data.seasons
      .map(
        (s) =>
          `<h4>${s.id}</h4><ul>${
            s.missing
              .filter((g) => !g.included_in_games)
              .map(
                (g) =>
                  `<li>${escape(g.team1)} — ${escape(g.team2)}${g.date ? ` · ${g.date}` : ''} <span class="sp-subtext">${escape(phaseName(g.phase))}</span></li>`
              )
              .join('') || `<li>${t.noMissing}</li>`
          }</ul>${reviewList(s)}`
      )
      .join(
        ''
      )}<h3>${t.source}</h3><p>${t.dataNote}</p><p><a href="https://mongolia.basketball/${lang}/competitions/league/schedule" target="_blank" rel="noopener">${t.league} ↗</a></p></section>`;
  }
  function renderContent() {
    const target = app.querySelector('#sp-content');
    if (state.tab === 'teams') {
      const rows = sortRows(teamStats().filter((r) => matches(r.name) || matches(r.code)));
      const teamTable = table(recordColumns, rows);
      target.innerHTML = `<div class="sp-main-grid"><section class="sp-panel"><div class="sp-section-heading"><div><h2>${t.records}</h2><p class="sp-caption">${t.recordNote}</p></div><span class="sp-pill">${phaseName(state.phase)}</span></div>${teamTable}<p class="sp-table-note">${t.tableNote}</p></section>${leaderPanel()}</div><section class="sp-recent-section">${recentStrip()}</section>`;
    } else if (state.tab === 'players' && !season().players.length) {
      target.innerHTML = `<section class="sp-panel sp-methodology"><h2>${t.players}</h2><p>${t.noPlayerStats}</p><button class="sp-view-link" data-tab="games">${t.games} ${svg('arrow')}</button></section>`;
      currentExport = { columns: [], rows: [] };
    } else if (state.tab === 'players') {
      const all = sortRows(playerStats().filter((r) => matches(r.name) || matches(teamName(r.code))));
      const size = 25,
        max = Math.max(1, Math.ceil(all.length / size));
      state.page = Math.min(state.page, max);
      target.innerHTML = `<section class="sp-panel"><div class="sp-section-heading"><div><h2>${t.players}</h2><p class="sp-caption">${t.playerNote}</p><p class="sp-caption">${t.nameNote}</p></div><span class="sp-pill">${all.length} ${t.recordsCount}</span></div>${table(playerColumns, all.slice((state.page - 1) * size, state.page * size))}<div class="sp-pagination"><span>${(state.page - 1) * size + (all.length ? 1 : 0)}–${Math.min(state.page * size, all.length)} / ${all.length}</span><div><button data-page="-1" ${state.page === 1 ? 'disabled' : ''}>←</button><span>${state.page} / ${max}</span><button data-page="1" ${state.page === max ? 'disabled' : ''}>→</button></div></div><p class="sp-table-note">${t.qualityText}</p></section>`;
      currentExport = {
        columns: [playerColumns[0], { key: 'teamName', label: t.team }, ...playerColumns.slice(1)],
        rows: all,
      };
    } else if (state.tab === 'games') {
      const all = sortRows(
        gamesFor()
          .map((g) => ({ ...g, name: teamName(g.a) + ' ' + teamName(g.b) }))
          .filter((g) => matches(g.name) || matches(g.date))
      );
      const size = 20,
        max = Math.max(1, Math.ceil(all.length / size));
      state.page = Math.min(state.page, max);
      target.innerHTML = `<section class="sp-panel"><div class="sp-section-heading"><div><h2>${t.games}</h2><p class="sp-caption">${t.available} · ${phaseName(state.phase)}</p></div><span class="sp-pill">${all.length} ${t.recordsCount}</span></div>${table(gameColumns, all.slice((state.page - 1) * size, state.page * size))}<div class="sp-pagination"><span>${(state.page - 1) * size + (all.length ? 1 : 0)}–${Math.min(state.page * size, all.length)} / ${all.length}</span><div><button data-page="-1" ${state.page === 1 ? 'disabled' : ''}>←</button><span>${state.page} / ${max}</span><button data-page="1" ${state.page === max ? 'disabled' : ''}>→</button></div></div></section>`;
      currentExport = {
        columns: [
          { key: 'date', label: t.date },
          { key: 'a', label: t.team + ' A' },
          { key: 'scoreA', label: t.pts + ' A' },
          { key: 'b', label: t.team + ' B' },
          { key: 'scoreB', label: t.pts + ' B' },
          { key: 'round', label: t.round },
          { key: 'box', label: t.box },
        ],
        rows: all.map((g) => ({ ...g, a: teamName(g.a), b: teamName(g.b), round: phaseName(g.round) })),
      };
    } else if (state.tab === 'compare') target.innerHTML = compareView();
    else target.innerHTML = coverageView();
    app.querySelectorAll('[data-tab]').forEach((el) => {
      el.classList.toggle('active', el.dataset.tab === state.tab);
      if (el.classList.contains('sp-nav-item'))
        el.setAttribute('aria-current', el.dataset.tab === state.tab ? 'page' : 'false');
    });
    app.querySelector('#sp-search').closest('label').hidden = ['compare', 'coverage'].includes(state.tab);
  }
  function update() {
    const s = season(),
      gs = gamesFor(s),
      ids = new Set(gs.map((g) => g.id));
    const stats = [
      [gs.length, t.played],
      [new Set(gs.flatMap((g) => [g.a, g.b])).size, t.teamsCount],
      [gs.filter((g) => g.box).length, t.boxscores],
      [
        s.players.length ? new Set(s.players.filter((p) => !p.dnp && ids.has(p.game)).map(playerKey)).size : '—',
        t.playerCount,
      ],
    ];
    app.querySelector('#sp-summary').innerHTML = stats
      .map(([v, label]) => `<div><strong>${v.toLocaleString()}</strong><span>${label}</span></div>`)
      .join('');
    app.querySelector('#sp-coverage-text').textContent = coverageSummary(s);
    app.querySelector('#sp-season-label').textContent = state.season.replace('-', '–');
    app.querySelector('#sp-season').value = state.season;
    app.querySelector('#sp-stage').innerHTML = stagesFor(state.season)
      .map((p) => `<option value="${p}" ${state.phase === p ? 'selected' : ''}>${phaseName(p)}</option>`)
      .join('');
    app.querySelectorAll('[data-season]').forEach((b) => {
      const selected = b.dataset.season === state.season && (!b.dataset.stage || b.dataset.stage === state.phase);
      b.classList.toggle('active', selected);
      b.setAttribute('aria-pressed', String(selected));
    });
    app.querySelector('#sp-download').disabled = state.tab === 'players' && !s.players.length;
    renderContent();
    const url = new URL(location.href);
    url.searchParams.set('season', state.season);
    url.searchParams.set('stage', state.phase);
    url.searchParams.set('view', state.tab);
    history.replaceState({}, '', url);
  }
  function showDialog(title, body) {
    const dialog = app.querySelector('dialog');
    if (!dialog.open) focusBeforeDialog = document.activeElement;
    dialog.innerHTML = `<div class="sp-dialog-top"><span class="sp-eyebrow">${t.basketball} / ${state.season}</span><button class="sp-close" aria-label="${t.close}">×</button></div><h2 id="sp-dialog-title">${title}</h2>${body}`;
    if (!dialog.open) dialog.showModal();
    dialog.scrollTop = 0;
    dialog.querySelector('.sp-close').focus();
  }
  function showTeam(c) {
    const r = teamStats().find((v) => v.code === c);
    if (!r) return;
    const oldExport = currentExport;
    const roster = playerStats(season(), state.phase, c, 1).sort((a, b) => b.ppg - a.ppg);
    const rows = gamesFor()
      .filter((g) => g.a === c || g.b === c)
      .reverse();
    showDialog(
      `${badge(c)} ${escape(teamName(c))}`,
      `<p class="sp-caption">${phaseName(state.phase)} · ${r.gp} ${t.available} · ${r.box} ${t.boxscores}</p><div class="sp-dialog-metrics"><div><strong>${r.w}–${r.l}</strong><span>${t.result}</span></div><div><strong>${f(r.ppg)}</strong><span>${t.ppg}</span></div><div><strong>${pct(r.fg)}</strong><span>${t.fg}</span></div><div><strong>${f(r.reb)}</strong><span>${t.reb}</span></div></div><h3>${t.roster}</h3>${roster.length ? table(playerColumns, roster, { sortable: false }) : `<p class="sp-table-note">${t.noPlayerStats}</p>`}<h3>${t.gameLog}</h3>${table(gameColumns, rows, { sortable: false })}<p class="sp-table-note">${t.tableNote}</p>`
    );
    currentExport = oldExport;
  }
  function showPlayer(key) {
    const r = playerStats(season(), state.phase, null, 1).find((v) => v.key === key);
    if (!r) return;
    const rows = [...r.rows].sort((a, b) =>
      season()
        .games.find((g) => g.id === b.game)
        .date.localeCompare(season().games.find((g) => g.id === a.game).date)
    );
    showDialog(
      escape(r.name),
      `<p class="sp-caption">${escape(teamName(r.code))} · ${phaseName(state.phase)} · ${r.gp} ${t.available}</p><div class="sp-dialog-metrics"><div><strong>${f(r.ppg)}</strong><span>${t.ppg}</span></div><div><strong>${f(r.reb)}</strong><span>${t.reb}</span></div><div><strong>${f(r.ast)}</strong><span>${t.ast}</span></div><div><strong>${pct(r.fg)}</strong><span>${t.fg}</span></div></div><h3>${t.gameLog}</h3><p class="sp-scroll-hint">${t.scrollHint} →</p><div class="sp-table-scroll" tabindex="0" role="region" aria-label="${t.scrollHint}"><table class="sp-table"><thead><tr><th>${t.date}</th><th>${t.matchup}</th><th>${t.minutes}</th><th>${t.pts}</th><th>${t.rebounds}</th><th>${t.assists}</th><th>${t.fg}</th></tr></thead><tbody>${rows
        .map((p) => {
          const g = season().games.find((v) => v.id === p.game),
            opp = g.a === r.code ? g.b : g.a;
          return `<tr><td>${g.date}</td><td><button class="sp-player-link" data-game="${g.id}">${escape(teamName(opp))}</button></td><td>${escape(p.minutes)}</td><td><strong>${f(p.points, 0)}</strong></td><td>${f(p.total_rebounds, 0)}</td><td>${f(p.assists, 0)}</td><td>${p.fg_made ?? '—'}/${p.fg_attempted ?? '—'}</td></tr>`;
        })
        .join('')}</tbody></table></div><p class="sp-table-note">${t.qualityText}</p>`
    );
  }
  function showGame(id) {
    const s = season(),
      g = s.games.find((v) => v.id === id);
    if (!g) return;
    const rows = s.players.filter((p) => p.game === id);
    const statCells = (p) =>
      `<td>${p.dnp ? t.dnp : escape(p.minutes)}${!p.dnp && s.issues.some((q) => q.game === id && q.team === p.team && q.stat === 'minutes') ? '<sup>†</sup>' : ''}</td>${['points', 'total_rebounds', 'assists', 'steals', 'blocks', 'turnovers'].map((k) => `<td>${p.dnp ? '—' : f(p[k], 0)}${!p.dnp && s.issues.some((q) => q.game === id && q.team === p.team && q.stat === k) ? '<sup>†</sup>' : ''}</td>`).join('')}<td>${p.dnp ? '—' : `${p.fg_made ?? '—'}/${p.fg_attempted ?? '—'}`}</td><td>${p.dnp ? '—' : `${p.three_pt_made ?? '—'}/${p.three_pt_attempted ?? '—'}`}</td><td>${p.dnp ? '—' : `${p.ft_made ?? '—'}/${p.ft_attempted ?? '—'}`}</td>`;
    showDialog(
      `${escape(teamName(g.a))} <span class="sp-modal-score">${g.scoreA} – ${g.scoreB}</span> ${escape(teamName(g.b))}`,
      `<p class="sp-caption">${g.date} · ${phaseName(g.round)}${g.ot ? ' · ' + g.ot + t.overtime : ''}</p>${g.periods.length ? `<div class="sp-periods"><span></span>${g.periods.map((p, i) => `<span>${i < 4 ? t.quarter + (i + 1) : t.overtime + (i - 3)}</span>`).join('')}<strong>${g.a}</strong>${g.periods.map((p) => `<span>${p[0] ?? '—'}</span>`).join('')}<strong>${g.b}</strong>${g.periods.map((p) => `<span>${p[1] ?? '—'}</span>`).join('')}</div>` : ''}${
        g.box
          ? [g.a, g.b]
              .map(
                (c) =>
                  `<h3>${badge(c)} ${escape(teamName(c))}</h3><p class="sp-scroll-hint">${t.scrollHint} →</p><div class="sp-table-scroll" tabindex="0" role="region" aria-label="${t.scrollHint}"><table class="sp-table"><thead><tr><th>#</th><th>${t.player}</th><th>${t.minutes}</th><th>${t.pts}</th><th>${t.rebounds}</th><th>${t.assists}</th><th>${t.steals}</th><th>${t.blocks}</th><th>${t.turnovers}</th><th>${t.fieldGoals}</th><th>${t.threePoints}</th><th>${t.freeThrows}</th></tr></thead><tbody>${rows
                    .filter((p) => p.team === c)
                    .map(
                      (p) =>
                        `<tr class="${p.dnp ? 'sp-dnp' : ''}"><td>${p.jersey ?? '—'}</td><td class="sp-name-cell">${escape(p.name)}${p.starter ? ' *' : ''}</td>${statCells(p)}</tr>`
                    )
                    .join('')}${s.totals
                    .filter((p) => p.game === id && p.team === c)
                    .map((p) => `<tr class="sp-total"><td></td><td>${t.totals}</td>${statCells(p)}</tr>`)
                    .join('')}</tbody></table></div>`
              )
              .join('')
          : `<p class="sp-empty">${t.resultsOnlyNote}</p>`
      }<p class="sp-table-note">${t.qualityText}</p>${g.minutesPrecision === 'whole' ? `<p class="sp-table-note">${t.precisionNote}</p>` : ''}${reviewList(s, id)}<details class="sp-source"><summary>${t.source}</summary><p>${t.original}: ${escape(g.source)}</p>${g.sourceUrl?.[lang] ? `<p><a href="${escape(g.sourceUrl[lang])}" target="_blank" rel="noopener">${t.source} ↗</a></p>` : ''}${g.dateSource ? `<a href="${escape(g.dateSource)}" target="_blank" rel="noopener">${t.date} ↗</a>` : ''}</details>`
    );
    const periods = app.querySelector('.sp-periods');
    if (periods) periods.style.gridTemplateColumns = `80px repeat(${g.periods.length}, 1fr)`;
  }
  app.innerHTML = `<div class="sp-shell"><aside class="sp-sidebar"><a class="sp-section-brand" href="/${lang}/sports/basketball"><span class="sp-ball-small">◉</span><span>${t.sport}<small>data.mn</small></span></a><p class="sp-sidebar-label">${t.explore}</p><nav aria-label="${t.sport}">${['teams', 'players', 'games', 'compare', 'coverage'].map((k) => `<button class="sp-nav-item" data-tab="${k}">${svg(k)}<span>${t[k]}</span>${k === 'games' ? '<small>' + data.seasons.reduce((n, s) => n + s.games.length, 0) + '</small>' : ''}</button>`).join('')}</nav><p class="sp-sidebar-label sp-archive-label">${t.archive}</p><div class="sp-season-nav">${data.seasons.map((s) => `<button data-season="${s.id}"><span>${s.id.replace('-', '–')}</span><small>${s.games.length}</small></button>`).join('')}</div><div class="sp-sidebar-bottom"><span class="sp-status-dot"></span>${t.basketball}<small>${t.dataNote}</small><a href="https://github.com/American-University-of-Mongolia/data-mn" target="_blank" rel="noopener">GitHub ↗</a></div></aside><main class="sp-main"><div class="sp-breadcrumb"><span>data.mn</span><span>/</span><span>${t.sport}</span><span>/</span><strong>${t.basketball}</strong></div><section class="sp-hero"><div class="sp-hero-content"><span class="sp-eyebrow"><i></i>${t.league}</span><h1>${t.title}</h1><p>${t.subtitle}</p><span class="sp-season-tag" id="sp-season-label"></span></div><svg class="sp-court-art" viewBox="0 0 270 240" fill="none" aria-hidden="true"><circle cx="150" cy="125" r="95"/><path d="M55 125h190M150 30v190M83 58q120 68 0 134M217 58q-120 68 0 134"/><circle cx="150" cy="125" r="113" stroke-dasharray="3 8"/><path d="M12 215h65M247 22v45"/></svg><div class="sp-summary" id="sp-summary"></div></section><div class="sp-toolbar"><div class="sp-select-wrap"><label for="sp-season">${t.season}</label><select id="sp-season">${data.seasons.map((s) => `<option>${s.id}</option>`).join('')}</select></div><div class="sp-select-wrap"><label for="sp-stage">${t.phase}</label><select id="sp-stage"></select></div><label class="sp-search">${svg('search')}<input id="sp-search" type="search" placeholder="${t.search}" aria-label="${t.search}" /></label><button id="sp-download" class="sp-download" title="${t.downloadNote}">${svg('download')}<span>${t.download}</span></button><details class="sp-full-datasets"><summary>${t.fullDatasets}</summary><ul>${datasetLinks()}</ul></details></div><div class="sp-coverage-notice"><span class="sp-note-icon">i</span><p id="sp-coverage-text"></p><button data-tab="coverage" aria-label="${t.coverage}">${svg('arrow')}</button></div><div id="sp-content" aria-live="polite"></div><footer class="sp-footer"><span>${t.dataNote}</span><span>data.mn <b>${t.sport}</b></span></footer></main></div><dialog class="sp-dialog" aria-labelledby="sp-dialog-title"></dialog>`;
  app.querySelector('.sp-season-nav').innerHTML = data.seasons
    .map(
      (s) => `<div class="sp-season-group">
    <button class="sp-season-title" data-season="${s.id}"><span>${s.id.replace('-', '–')}</span><small>${s.games.length}</small></button>
    ${stagesFor(s.id)
      .filter((p) => p !== 'All')
      .map(
        (p) =>
          `<button class="sp-season-stage" data-season="${s.id}" data-stage="${p}" aria-label="${s.id} ${phaseName(p)}"><span>${phaseName(p)}</span><small>${s.games.filter((g) => g.phase === p).length}</small></button>`
      )
      .join('')}
  </div>`
    )
    .join('');
  app.addEventListener('click', (event) => {
    const button = event.target.closest('button');
    if (!button) return;
    if (button.classList.contains('sp-close')) {
      app.querySelector('dialog').close();
      return;
    }
    if (button.dataset.tab) {
      state.tab = button.dataset.tab;
      state.sort = state.tab === 'players' ? 'ppg' : state.tab === 'games' ? 'date' : 'pct';
      state.direction = -1;
      state.page = 1;
      update();
    } else if (button.dataset.season) {
      state.season = button.dataset.season;
      state.phase =
        button.dataset.stage ||
        (stagesFor(state.season).includes(state.phase) ? state.phase : stagesFor(state.season)[0]);
      state.page = 1;
      update();
    } else if (button.dataset.sort) {
      state.direction =
        state.sort === button.dataset.sort ? -state.direction : ['name', 'date'].includes(button.dataset.sort) ? 1 : -1;
      state.sort = button.dataset.sort;
      renderContent();
    } else if (button.dataset.page) {
      state.page += Number(button.dataset.page);
      renderContent();
    } else if (button.dataset.team) showTeam(button.dataset.team);
    else if (button.dataset.player) showPlayer(button.dataset.player);
    else if (button.dataset.game) showGame(button.dataset.game);
    else if (button.id === 'sp-download') {
      const { columns, rows } = currentExport,
        cols = columns.filter((c) => c.key);
      const cell = (v) => '"' + String(v ?? '').replaceAll('"', '""') + '"';
      const csv =
        '\uFEFF' +
        [
          cols.map((c) => cell(c.label)).join(','),
          ...rows.map((r) =>
            cols
              .map((c) =>
                cell(
                  ['pct', 'fg', 'three', 'ft'].includes(c.key) && r[c.key] != null
                    ? Number((r[c.key] * 100).toFixed(1))
                    : r[c.key]
                )
              )
              .join(',')
          ),
        ].join('\r\n');
      const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' })),
        link = document.createElement('a');
      link.href = url;
      link.download = `mnbl-${state.season}-${state.tab}-${lang}.csv`;
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
  });
  app.addEventListener('change', (event) => {
    if (event.target.id === 'sp-season') {
      state.season = event.target.value;
      if (!stagesFor(state.season).includes(state.phase)) state.phase = stagesFor(state.season)[0];
      state.page = 1;
      update();
    }
    if (event.target.id === 'sp-stage') {
      state.phase = event.target.value;
      state.page = 1;
      update();
    }
    if (event.target.id === 'sp-compare-a') {
      state.compareA = event.target.value;
      renderContent();
    }
    if (event.target.id === 'sp-compare-b') {
      state.compareB = event.target.value;
      renderContent();
    }
  });
  app.querySelector('#sp-search').addEventListener('input', (e) => {
    state.query = e.target.value;
    state.page = 1;
    renderContent();
  });
  app
    .querySelector('dialog')
    .addEventListener('close', () => focusBeforeDialog?.isConnected && focusBeforeDialog.focus());
  app.querySelector('dialog').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      const r = e.currentTarget.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom)
        e.currentTarget.close();
    }
  });
  update();
}
if (typeof document !== 'undefined') {
  mountSports();
  document.addEventListener('astro:page-load', mountSports);
}
