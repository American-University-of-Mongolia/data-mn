// Exercise the actual opt-in component logic with real Vega views.
// Run from data.mn: node scripts/test-linked-chart-years.mjs
import fs from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import * as installedVega from 'vega';
import { compile } from 'vega-lite';

const root = fileURLToPath(new URL('..', import.meta.url));
const vega = process.env.DATA_MN_VEGA_RUNTIME
  ? createRequire(import.meta.url)(process.env.DATA_MN_VEGA_RUNTIME)
  : installedVega;
const component = await fs.readFile(path.join(root, 'src/components/ui/VegaChart.astro'), 'utf8');
const logic = component.slice(
  component.indexOf('function prepareLinkedYear('),
  component.indexOf('// Debounced resize handler')
);
assert.ok(logic.includes('addSignalListener'));
const elements = new Map();
const errors = [];
const context = vm.createContext({
  chartViews: {},
  linkedYears: {},
  document: { getElementById: (id) => elements.get(id) },
  console: { error: (...args) => errors.push(args) },
});
vm.runInContext(logic, context);
const loader = vega.loader();
loader.load = (url) => fs.readFile(path.join(root, 'public', url), 'utf8');

async function prepare(id, group, filename) {
  const label = { textContent: '' };
  const el = { id, dataset: { yearGroup: group }, closest: () => ({ querySelector: () => label }) };
  elements.set(id, el);
  const spec = JSON.parse(await fs.readFile(path.join(root, 'public/charts', filename), 'utf8'));
  const attach = context.prepareLinkedYear(el, spec);
  return { id, label, spec, attach };
}
async function embed(prepared) {
  const view = new vega.View(vega.parse(compile({ ...prepared.spec, width: 600, height: 350 }).spec), {
    renderer: 'none',
    loader,
  }).initialize();
  await view.runAsync();
  context.chartViews[prepared.id] = view;
  await prepared.attach(view);
  return view;
}
async function change(view, group, year) {
  await view.signal('selectedYear', year).runAsync();
  await context.linkedYears[group].pending;
}

let checked = 0;
const datasets = ['livestock-losses-by-aimag', 'livestock-loss-rate-by-aimag'].filter((id) =>
  existsSync(path.join(root, 'src/data/data/en', `${id}.mdx`))
);
assert.ok(datasets.length, 'No livestock map datasets are present');
for (const dataset of datasets) {
  for (const lang of ['en', 'mn']) {
    const group = `${dataset}-${lang}`;
    const map = await prepare(`${group}-map`, group, `${dataset}-${lang}.json`);
    const rank = await prepare(`${group}-rank`, group, `${dataset}-ranking-${lang}.json`);
    let mapView = await embed(map);
    // The ranking began loading before the user changed the map's year.
    await change(mapView, group, 1971);
    let rankView = await embed(rank);
    assert.equal(rankView.signal('selectedYear'), 1971);
    for (let year = 1971; year <= 2025; year++) {
      await change(mapView, group, year);
      assert.equal(rankView.signal('selectedYear'), year);
      assert.equal(map.label.textContent, String(year));
      assert.equal(rank.label.textContent, String(year));
      checked++;
    }
    await Promise.all([1971, 1980, 2010, 2024].map((year) => mapView.signal('selectedYear', year).runAsync()));
    await context.linkedYears[group].pending;
    assert.equal(rankView.signal('selectedYear'), 2024);
    // Responsive re-embedding must preserve the selection in either load order.
    mapView.finalize();
    rankView.finalize();
    delete context.chartViews[map.id];
    delete context.chartViews[rank.id];
    const resizedRank = await prepare(rank.id, group, `${dataset}-ranking-${lang}.json`);
    rankView = await embed(resizedRank);
    const resizedMap = await prepare(map.id, group, `${dataset}-${lang}.json`);
    mapView = await embed(resizedMap);
    assert.equal(mapView.signal('selectedYear'), 2024);
    assert.equal(rankView.signal('selectedYear'), 2024);
    await change(mapView, group, 1980);
    assert.equal(mapView.signal('selectedYear'), 1980);
    assert.equal(resizedMap.label.textContent, '1980');
  }
}
// Changing one dataset/language group leaves every other group untouched.
const groups = Object.keys(context.linkedYears);
await change(context.chartViews[`${groups[0]}-map`], groups[0], 1971);
for (const group of groups.slice(1)) assert.equal(context.chartViews[`${group}-map`].signal('selectedYear'), 1980);
const untouched = { params: [{ name: 'selectedYear', value: 2025 }] };
assert.equal(context.prepareLinkedYear({ dataset: {} }, untouched), null);
assert.equal(untouched.params[0].value, 2025);
assert.deepEqual(errors, []);
for (const view of Object.values(context.chartViews)) view.finalize();
console.log(
  JSON.stringify({
    vegaVersion: vega.version,
    linkedYearChanges: checked,
    delayedLoading: 'pass',
    rapidInput: 'pass',
    resize: 'pass',
    groupIsolation: 'pass',
    unlinkedCharts: 'unchanged',
  })
);
