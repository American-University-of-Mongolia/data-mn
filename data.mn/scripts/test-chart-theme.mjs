// Run with: node scripts/test-chart-theme.mjs
// Exercise the component's actual lifecycle with delayed fetch/embed operations.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
import { applyChartTheme } from '../public/scripts/chart-theme.js';
import * as vega from 'vega';
import { compile } from 'vega-lite';

const component = await readFile(new URL('../src/components/ui/VegaChart.astro', import.meta.url), 'utf8');
const script = component
  .split('<script is:inline>')[1]
  .split('</script>')[0]
  .replace("import('/scripts/chart-legend-layout.js')", 'Promise.resolve(legendTools)')
  .replace("import('/scripts/chart-theme.js')", 'Promise.resolve({ applyChartTheme })');

function deferred() {
  let resolve;
  const promise = new Promise((done) => (resolve = done));
  return { promise, resolve };
}

const source = {
  data: { values: [{ year: 2020, value: 3 }] },
  params: [{ name: 'region', value: 'Tuv', bind: { input: 'select', options: ['Tuv', 'Selenge'] } }],
  mark: 'line',
  encoding: { x: { field: 'year', type: 'quantitative' }, y: { field: 'value', type: 'quantitative' } },
  config: { axis: { labelColor: '#64748b' }, range: { category: { scheme: 'category10' } } },
};

function element(id) {
  return {
    id,
    isConnected: true,
    offsetWidth: 600,
    dataset: { spec: '/charts/example.json', aspectRatio: '0.5' },
    getAttribute(name) {
      return name === 'data-rendered' ? this.dataset.rendered : null;
    },
    setAttribute(name, value) {
      if (name === 'data-rendered') this.dataset.rendered = value;
    },
    removeAttribute(name) {
      if (name === 'data-rendered') delete this.dataset.rendered;
    },
  };
}

let dark = false;
let charts = [element('first'), element('second')];
const callbacks = {};
const observers = [];
const renders = [];
const errors = [];
let embedGate;
let fetchGate;
const document = {
  readyState: 'complete',
  documentElement: { classList: { contains: () => dark } },
  querySelectorAll: () => charts,
  addEventListener(name, callback) {
    (callbacks[name] ||= []).push(callback);
  },
};
const window = {
  addEventListener() {},
  async vegaEmbed(el, spec, options) {
    const listeners = {};
    const view = {
      finalized: false,
      finalize() {
        this.finalized = true;
      },
      addSignalListener(name, callback) {
        listeners[name] = callback;
      },
    };
    renders.push({ el, spec, options, view, listeners });
    if (embedGate) await embedGate.promise;
    return { view, finalize: () => view.finalize() };
  },
};
const context = vm.createContext({
  applyChartTheme,
  window,
  document,
  console: { error: (...args) => errors.push(args), warn() {} },
  setTimeout,
  clearTimeout,
  fetch: async () => {
    if (fetchGate) await fetchGate.promise;
    return { ok: true, json: async () => structuredClone(source) };
  },
  MutationObserver: class {
    constructor(callback) {
      observers.push(callback);
    }
    observe() {}
  },
  legendTools: {
    categoricalLegendLabels: () => [],
    applyCategoricalLegendLayout: () => ({ columns: 1, labelLimit: 150 }),
  },
});
const settle = async () => {
  for (let i = 0; i < 20; i++) await new Promise(setImmediate);
};
const toggle = () => {
  dark = !dark;
  observers.forEach((callback) => callback());
};
const dispatch = (name) => callbacks[name]?.forEach((callback) => callback());
const active = () => renders.filter(({ view }) => !view.finalized);

vm.runInContext(script, context);
vm.runInContext(script, context);
dispatch('astro:page-load');
await settle();
assert.equal(observers.length, 1, 'Multiple component instances install one observer');
assert.equal(renders.length, 2, 'Initial Astro page-load does not double-render');
assert.ok(renders.every(({ options }) => options.theme === 'vox'));
const lightSpec = JSON.stringify(renders[0].spec);
renders[0].listeners.region('region', 'Selenge');
observers[0]();
await settle();
assert.equal(renders.length, 2, 'Unrelated root class changes do not redraw charts');

toggle();
await settle();
assert.equal(renders.length, 4, 'All charts refresh on theme changes');
assert.equal(active().length, 2, 'Old views are finalized');
assert.ok(active().every(({ options }) => options.theme === 'dark'));
assert.equal(active()[0].spec.params[0].value, 'Selenge', 'Dropdown selection survives');
assert.equal(active()[0].spec.config.axis.labelColor, '#cbd5e1', 'Dark labels are readable');
assert.deepEqual(active()[0].spec.encoding, source.encoding, 'Data encodings are preserved');

toggle();
await settle();
assert.equal(JSON.stringify(active()[1].spec), lightSpec, 'Light spec is restored unchanged');
assert.equal(active()[0].spec.params[0].value, 'Selenge');

embedGate = deferred();
toggle();
await settle();
const inFlightCount = renders.length;
toggle();
toggle();
toggle();
await settle();
assert.equal(renders.length, inFlightCount, 'Rapid toggles never overlap embeds on one element');
embedGate.resolve();
embedGate = undefined;
await settle();
assert.equal(renders.length, inFlightCount + 2, 'Queued changes coalesce to one refresh per chart');
assert.ok(
  active().every(({ options }) => options.theme === 'vox'),
  'Latest theme wins'
);

embedGate = deferred();
toggle();
await settle();
dispatch('astro:before-swap');
charts.forEach((el) => (el.isConnected = false));
charts = [element('new-page')];
embedGate.resolve();
embedGate = undefined;
dispatch('astro:page-load');
await settle();
assert.equal(active().length, 1, 'Navigating during embed finalizes outgoing views');
assert.equal(active()[0].el.id, 'new-page');
toggle();
await settle();
assert.equal(active()[0].options.theme, 'vox', 'Observer still works after navigation');

fetchGate = deferred();
toggle();
await settle();
const beforeNavigation = renders.length;
dispatch('astro:before-swap');
charts.forEach((el) => (el.isConnected = false));
charts = [element('after-fetch')];
fetchGate.resolve();
fetchGate = undefined;
dispatch('astro:page-load');
await settle();
assert.equal(renders.length, beforeNavigation + 1, 'Stale fetch does not embed into an outgoing page');
assert.equal(active().length, 1);
assert.equal(active()[0].el.id, 'after-fetch');
assert.deepEqual(errors, []);
console.log(
  'PASS: theme toggles, parameter persistence, rapid changes, single observer, and navigation during loading.'
);

const nested = {
  title: { text: 'Example', color: '#000' },
  config: { axisY: { titleColor: '#000' }, headerRow: { labelColor: '#000' } },
  facet: { field: 'group', header: { labelColor: '#000' } },
  spec: {
    layer: [
      {
        mark: { type: 'line', color: '#b91c1c' },
        encoding: { x: { axis: { labelColor: '#000' } }, color: { legend: null, scale: { range: ['red'] } } },
      },
      { mark: 'point', encoding: { x: { axis: null }, color: { legend: false } } },
    ],
  },
};
applyChartTheme(nested, true);
assert.equal(nested.title.color, '#e2e8f0');
assert.equal(nested.config.axisY.titleColor, '#e2e8f0');
assert.equal(nested.config.headerRow.labelColor, '#cbd5e1');
assert.equal(nested.facet.header.labelColor, '#cbd5e1');
assert.equal(nested.spec.layer[0].encoding.x.axis.labelColor, '#cbd5e1');
assert.equal(nested.spec.layer[0].mark.color, '#b91c1c');
assert.deepEqual(nested.spec.layer[0].encoding.color.scale.range, ['red']);
assert.equal(nested.spec.layer[0].encoding.color.legend, null);
assert.equal(nested.spec.layer[1].encoding.x.axis, null);
assert.equal(nested.spec.layer[1].encoding.color.legend, false);

// Compile and export real charts, including layered lines, a map, a
// horizontal ranking, and a heatmap. Check that data and mark colors survive.
const loader = vega.loader();
loader.load = (url) => readFile(new URL(`../public${url}`, import.meta.url), 'utf8');
for (const lang of ['en', 'mn']) {
  for (const slug of [
    'gdp-growth-rate',
    'wheat-prices-by-region',
    'internal-migration-by-aimag',
    'internal-migration-by-aimag-ranking',
    'birth-rate-heatmap',
  ]) {
    const original = JSON.parse(
      await readFile(new URL(`../public/charts/${slug}-${lang}.json`, import.meta.url), 'utf8')
    );
    const light = structuredClone(original);
    applyChartTheme(light, false);
    assert.deepEqual(light, original, `${slug}: light styling is untouched`);
    const darkSpec = applyChartTheme(structuredClone(original), true);
    for (const key of ['data', 'transform', 'params', 'mark']) {
      assert.deepEqual(darkSpec[key], original[key], `${slug}: ${key} is unchanged`);
    }
    assert.deepEqual(darkSpec.encoding?.color?.scale, original.encoding?.color?.scale);
    const view = new vega.View(vega.parse(compile({ ...darkSpec, width: 600, height: 300 }).spec), {
      renderer: 'none',
      loader,
    }).initialize();
    try {
      await view.runAsync();
      const svg = await view.toSVG();
      assert.ok(svg.includes('#1e293b'), `${slug}: SVG export uses dark background`);
      assert.ok(svg.includes('#cbd5e1'), `${slug}: SVG export has readable labels`);
    } finally {
      view.finalize();
    }
  }
}
console.log('PASS: nested/disabled guides and real EN/MN bar, line, map, ranking, and heatmap SVG exports.');

// A legend-bound point selection has a different state shape from a scalar
// dropdown. Reuse the actual binding code to verify it survives re-embedding.
const bindingContext = vm.createContext({});
vm.runInContext(
  component.slice(component.indexOf('function prepareBoundParameters('), component.indexOf('// Opt-in year linking.')),
  bindingContext
);
const legendSource = JSON.parse(
  await readFile(new URL('../public/charts/mp-parliament-attendance-en.json', import.meta.url), 'utf8')
);
const legendElement = {};
let selectedParty;
for (const dark of [false, true, false]) {
  const spec = structuredClone(legendSource);
  const attach = bindingContext.prepareBoundParameters(legendElement, spec);
  applyChartTheme(spec, dark);
  const view = new vega.View(vega.parse(compile({ ...spec, width: 600, height: 300 }).spec), {
    renderer: 'none',
    loader,
  }).initialize();
  try {
    await view.runAsync();
    await attach(view);
    if (!selectedParty) {
      selectedParty = view.data('party_filter_store')[0];
      await view
        .change(
          'party_filter_store',
          vega
            .changeset()
            .remove(() => true)
            .insert(selectedParty)
        )
        .runAsync();
    }
    assert.equal(view.data('party_filter_store').length, 1, 'Selected party survives both theme directions');
    assert.deepEqual(view.data('party_filter_store')[0].values, selectedParty.values);
    legendElement._selectionState = view.getState({
      signals: () => false,
      data: (name) => legendElement._selectionStores.includes(name),
      recurse: false,
    });
    assert.deepEqual(Object.keys(legendElement._selectionState.data), ['party_filter_store']);
  } finally {
    view.finalize();
  }
}
console.log('PASS: legend selections survive light/dark/light without restoring transient hover state.');
