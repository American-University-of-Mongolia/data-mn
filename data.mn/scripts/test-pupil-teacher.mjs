// Exercise compiled Vega dataflows against the archived NSO values, including
// every year/level combination, national reference and optional comparisons.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import * as vega from 'vega';
import { compile } from 'vega-lite';
import { applyChartTheme } from '../public/scripts/chart-theme.js';

const root = new URL('../', import.meta.url);
let cases = 0;
for (const lang of ['en', 'mn']) {
  const csv = await readFile(new URL(`public/datasets/pupil-teacher-ratio-${lang}.csv`, root), 'utf8');
  const rows = vega.read(csv, { type: 'csv', parse: 'auto' });
  const [year, series, value] = Object.keys(rows[0]);
  const source = JSON.parse(
    await readFile(new URL(`../tools/versions/pupil-teacher-ratio/v1/raw/${lang}-data.json`, root), 'utf8')
  );
  const [levelDim, placeDim, yearDim] = source.id.map((id) => source.dimension[id].category);
  const levels = lang === 'en' ? ['All levels', 'Primary'] : ['Бүх түвшин', 'Бага боловсрол'];
  const national = lang === 'en' ? 'National average' : 'Улсын дундаж';
  const sourceValue = (l, p, y) =>
    source.value[levelDim.index[l] * 28 * 19 + placeDim.index[p] * 19 + yearDim.index[y]];
  const yearCodes = Object.entries(yearDim.label).map(([code, label]) => [code, Number(label)]);
  assert.equal(rows.length, 874);
  const placeCodes = Object.keys(placeDim.index).filter((p) => p.length === 3);

  async function build(kind, dark = false) {
    const spec = JSON.parse(
      await readFile(new URL(`public/charts/pupil-teacher-ratio${kind}-${lang}.json`, root), 'utf8')
    );
    spec.data = { values: rows.map((row) => ({ ...row })) };
    if (dark) applyChartTheme(spec, true);
    const compiled = compile(spec).spec;
    const view = new vega.View(vega.parse(compiled), { renderer: 'none' });
    await view.runAsync();
    return view;
  }

  // The y domain is the actual displayed ordering, not just a filtered count.
  for (const dark of [false, true]) {
    const view = await build('', dark);
    for (const [levelCode, levelName] of levels.entries()) {
      for (const [yearCode, yearValue] of yearCodes) {
        await view.signal('educationLevel', levelName).signal('selectedYear', yearValue).runAsync();
        const domain = view.scale('y').domain();
        assert.equal(domain.length, 22);
        assert(!domain.includes(national));
        const expected = new Map(
          placeCodes.map((p) => [placeDim.label[p].trim(), sourceValue(String(levelCode), p, yearCode)])
        );
        const sortedValues = domain.map((p) => expected.get(p));
        assert.deepEqual(
          sortedValues,
          [...sortedValues].sort((a, b) => b - a)
        );
        const data = view.data('data_0');
        assert.equal(data.length, 23);
        assert.equal(data.find((r) => r.place === national)[value], sourceValue(String(levelCode), '0', yearCode));
        for (const row of data.filter((r) => r.place !== national)) assert.equal(row[value], expected.get(row.place));
        cases++;
      }
    }
    view.finalize();
  }

  const trend = await build('-trend');
  const first = placeDim.label['262'].trim();
  const second = placeDim.label['511'].trim();
  assert.equal(trend.data('data_0').length, 57);
  for (const levelName of levels) {
    for (const p of placeCodes) {
      const place = placeDim.label[p].trim();
      await trend
        .signal('educationLevel', levelName)
        .signal('locationOne', place)
        .signal('locationTwo', second)
        .runAsync();
      const actual = trend.data('data_0');
      assert.equal(actual.length, place === second ? 38 : 57);
      const expected = rows.filter(
        (r) => r[series].startsWith(`${levelName} / `) && [place, second, national].includes(r[series].split(' / ')[1])
      );
      const normalized = (data) =>
        data.map((r) => [r[year], r[series], r[value]]).sort((a, b) => a[0] - b[0] || a[1].localeCompare(b[1]));
      assert.deepEqual(normalized(actual), normalized(expected));
      cases++;
    }
  }
  await trend
    .signal('locationOne', first)
    .signal('locationTwo', lang === 'en' ? 'None' : 'Сонгохгүй')
    .runAsync();
  assert.equal(trend.data('data_0').length, 38);
  trend.finalize();
}
console.log(`Pupil–teacher ratio: ${cases} year/level/location/theme cases passed in EN and MN.`);
