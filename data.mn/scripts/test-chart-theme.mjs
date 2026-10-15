// Theme changes must restyle chart chrome without losing filters or series colors.
// Run from data.mn: node scripts/test-chart-theme.mjs
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import * as vega from 'vega';
import { compile } from 'vega-lite';

const root = fileURLToPath(new URL('..', import.meta.url));
const component = await fs.readFile(path.join(root, 'src/components/ui/VegaChart.astro'), 'utf8');
const logic = component.slice(
  component.indexOf('function applyChartTheme('),
  component.indexOf('// Opt-in year linking.')
);
const context = vm.createContext({});
vm.runInContext(logic, context);
const loader = vega.loader();
loader.load = (url) => fs.readFile(path.join(root, 'public', url), 'utf8');

for (const lang of ['en', 'mn']) {
  for (const suffix of ['', '-regions']) {
    const source = JSON.parse(
      await fs.readFile(path.join(root, `public/charts/youth-neet-rate${suffix}-${lang}.json`), 'utf8')
    );
    const element = {};
    const param = source.params[0];
    const chosen = suffix ? 2013 : param.bind.options[1];
    let expectedColors;
    for (const dark of [false, true, false]) {
      const spec = structuredClone(source);
      const attach = context.prepareBoundParameters(element, spec);
      context.applyChartTheme(spec, dark, true);
      if (expectedColors) assert.equal(spec.params[0].value, chosen, 'Selected parameter survives a redraw');
      assert.deepEqual(spec.data, source.data);
      assert.deepEqual(spec.transform, source.transform);
      assert.deepEqual(spec.encoding.color.scale, source.encoding.color.scale, 'Series colors remain unchanged');
      if (dark) {
        assert.equal(spec.background, '#1e293b');
        assert.equal(spec.config.axis.labelColor, '#cbd5e1');
        assert.equal(spec.config.legend.labelColor, '#cbd5e1');
      } else {
        assert.deepEqual(spec, { ...source, params: spec.params }, 'Original light styling is restored');
      }
      const view = new vega.View(vega.parse(compile({ ...spec, width: 600, height: 300 }).spec), {
        renderer: 'none',
        loader,
      }).initialize();
      await view.runAsync();
      attach(view);
      await view.signal(param.name, chosen).runAsync();
      assert.equal(element._bindingValues[param.name], chosen);
      const colors = view.scale('color').range();
      if (expectedColors) assert.deepEqual(colors, expectedColors);
      expectedColors = colors;
      const svg = await view.toSVG();
      if (dark) {
        assert.ok(svg.includes('#1e293b'), 'Exported SVG gets the dark background');
        assert.ok(svg.includes('#cbd5e1'), 'Exported SVG gets readable labels');
      }
      view.finalize();
    }
  }
}
const layered = {
  config: { axisY: { labelColor: '#111' } },
  layer: [{ encoding: { x: { axis: { labelColor: '#111' } }, color: { legend: null, scale: { range: ['red'] } } } }],
};
const unmodified = structuredClone(layered);
context.applyChartTheme(layered, true, false);
assert.deepEqual(layered, unmodified, 'Non-opted-in specs retain every custom color');
context.applyChartTheme(layered, true, true);
assert.equal(layered.layer[0].encoding.x.axis.labelColor, '#cbd5e1');
assert.equal(layered.config.axisY.labelColor, '#cbd5e1');
assert.equal(layered.layer[0].encoding.color.legend, null);
assert.deepEqual(layered.layer[0].encoding.color.scale.range, ['red']);
console.log(
  'PASS: EN/MN light → dark → light, comparison/year persistence, SVG exports, nested overrides and stable colors.'
);

// Multiple inline chart scripts must share one observer and use the current handler.
let darkMode = false;
let observerCount = 0;
let observerCallback;
const observerContext = vm.createContext({
  window: {},
  document: { documentElement: { classList: { contains: () => darkMode } } },
  MutationObserver: class {
    constructor(callback) {
      observerCount++;
      observerCallback = callback;
    }
    observe() {}
  },
});
const observerCode = component.slice(
  component.indexOf('if (!window._vegaThemeObserverAdded)'),
  component.indexOf('// Run on initial load')
);
for (let i = 0; i < 3; i++) vm.runInContext(observerCode, observerContext);
assert.equal(observerCount, 1, 'One observer for multiple chart instances');
let refreshCount = 0;
observerContext.window.refreshVegaCharts = (themeOnly) => {
  assert.equal(themeOnly, true);
  refreshCount++;
};
observerCallback();
assert.equal(refreshCount, 0, 'Unrelated class changes do not redraw charts');
darkMode = true;
observerCallback();
assert.equal(refreshCount, 1, 'One refresh per theme toggle');
observerContext.window.refreshVegaCharts = () => {
  refreshCount += 10;
};
darkMode = false;
observerCallback();
assert.equal(refreshCount, 11, 'Observer calls the current global handler');
const selectors = [];
const refreshed = [];
const refreshContext = vm.createContext({
  document: {
    querySelectorAll: (selector) => {
      selectors.push(selector);
      return ['chart'];
    },
  },
  invalidateChart: (chart) => refreshed.push(chart),
  initVegaCharts: () => {},
});
vm.runInContext(
  component.slice(component.indexOf('function refreshCharts('), component.indexOf('// Debounced resize handler')),
  refreshContext
);
refreshContext.refreshCharts(true);
assert.equal(
  selectors[0],
  '.vega-chart[data-spec][data-theme-aware="true"]',
  'Theme refresh targets only opted-in charts'
);
refreshContext.refreshCharts();
assert.equal(selectors[1], '.vega-chart[data-spec]', 'Resize still targets all charts');
assert.equal(refreshed.length, 2);
console.log('PASS: opt-in styling, scoped theme refresh, one observer and current global callback.');
