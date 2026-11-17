import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import * as vega from 'vega';
import { compile } from 'vega-lite';
import { applyChartTheme } from '../public/scripts/chart-theme.js';

const root = new URL('../public/', import.meta.url);
let cases = 0;
for (const lang of ['en', 'mn']) {
  const rows = vega.read(await readFile(new URL(`datasets/household-income-sources-${lang}.csv`, root), 'utf8'), {
    type: 'csv',
    parse: 'auto',
  });
  const [year, series, value] = Object.keys(rows[0]);
  const years = [...new Set(rows.map((r) => r[year]))];
  for (const dark of [false, true]) {
    for (const kind of ['', '-trend']) {
      const spec = JSON.parse(
        await readFile(new URL(`charts/household-income-sources${kind}-${lang}.json`, root), 'utf8')
      );
      const colors = structuredClone(kind ? spec.encoding.color.scale : spec.layer[0].encoding.color.scale);
      spec.data = { values: rows.map((row) => ({ ...row })) };
      if (dark) applyChartTheme(spec, true);
      assert.deepEqual(kind ? spec.encoding.color.scale : spec.layer[0].encoding.color.scale, colors);
      const compiled = compile(spec).spec;
      const view = new vega.View(vega.parse(compiled), { renderer: 'none' });
      await view.runAsync();
      // Read the dataset used by the actual bar/line mark, not an unfiltered input.
      const findData = (marks, type) => {
        for (const mark of marks) {
          if (mark.type === type) return mark.from.data;
          if (mark.marks) {
            const found = findData(mark.marks, type);
            if (found) return found;
          }
        }
      };
      if (!kind) {
        const dataset = findData(compiled.marks, 'rect');
        for (const y of years) {
          await view.signal('selectedYear', y).runAsync();
          const actual = view.data(dataset);
          assert.equal(actual.length, 18);
          for (const place of view.scale('x').domain()) {
            const segments = actual.filter((r) => r.place === place).sort((a, b) => a.sourceOrder - b.sourceOrder);
            assert.equal(segments.length, 6);
            let total = 0;
            for (const row of segments) {
              assert.equal(row[year], y);
              assert(Math.abs(row.y0 - total) < 1e-8);
              const original = rows.find((r) => r[year] === y && r[series] === row[series]);
              assert.equal(row[value], original[value]);
              total += row[value];
              assert(Math.abs(row.y1 - total) < 1e-8);
            }
            assert(Math.abs(total - 100) < 1e-8);
          }
          cases++;
        }
      } else {
        // Line facets use the filtered dataset that feeds the grouping mark.
        const dataset = compiled.marks.find((m) => m.from?.facet)?.from.facet.data;
        assert(dataset);
        const normalize = (data) =>
          data.map((r) => [r[year], r[series], r[value]]).sort((a, b) => a[0] - b[0] || a[1].localeCompare(b[1]));
        const locations = spec.params[1].bind.options;
        for (const source of spec.params[0].bind.options) {
          for (const location of locations) {
            await view.signal('selectedSource', source).signal('selectedLocation', location).runAsync();
            const expected = rows.filter((r) => {
              const [place, income] = r[series].split(' / ');
              return income === source && (location === locations[0] || place === location);
            });
            assert.equal(expected.length, years.length * (location === locations[0] ? 3 : 1));
            assert.deepEqual(normalize(view.data(dataset)), normalize(expected));
            cases++;
          }
        }
      }
      view.finalize();
    }
  }
}
console.log(`Household income: ${cases} year/source/location/theme cases passed in EN and MN.`);
