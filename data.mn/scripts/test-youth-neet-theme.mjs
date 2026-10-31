// Dataset-specific coverage alongside main's shared lifecycle regression suite.
// Run with: node scripts/test-youth-neet-theme.mjs
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
import * as vega from 'vega';
import { compile } from 'vega-lite';
import { applyChartTheme } from '../public/scripts/chart-theme.js';

const root = new URL('../', import.meta.url);
const component = await readFile(new URL('src/components/ui/VegaChart.astro', root), 'utf8');
const context = vm.createContext({});
vm.runInContext(
  component.slice(component.indexOf('function prepareBoundParameters('), component.indexOf('// Opt-in year linking.')),
  context
);
const loader = vega.loader();
loader.load = (url) => readFile(new URL(`public${url}`, root), 'utf8');

for (const lang of ['en', 'mn']) {
  for (const suffix of ['', '-regions']) {
    const source = JSON.parse(
      await readFile(new URL(`public/charts/youth-neet-rate${suffix}-${lang}.json`, root), 'utf8')
    );
    const element = {};
    const param = source.params[0];
    const chosen = suffix ? 2013 : param.bind.options[1];
    let expectedColors;
    for (const dark of [false, true, false]) {
      const spec = structuredClone(source);
      const attachBindings = context.prepareBoundParameters(element, spec);
      if (expectedColors) assert.equal(spec.params[0].value, chosen, 'Comparison/year survives a redraw');
      applyChartTheme(spec, dark);
      assert.deepEqual(spec.data, source.data);
      assert.deepEqual(spec.transform, source.transform);
      assert.deepEqual(spec.encoding.color.scale, source.encoding.color.scale);
      const view = new vega.View(vega.parse(compile({ ...spec, width: 600, height: 300 }).spec), {
        renderer: 'none',
        loader,
      }).initialize();
      await view.runAsync();
      await attachBindings(view);
      await view.signal(param.name, chosen).runAsync();
      assert.equal(element._bindingValues[param.name], chosen);
      const colors = view.scale('color').range();
      if (expectedColors) assert.deepEqual(colors, expectedColors, 'Series colors stay stable');
      expectedColors = colors;
      const svg = await view.toSVG();
      if (dark) assert.ok(svg.includes('#cbd5e1'), 'Dark labels remain readable');
      view.finalize();
    }
  }
}
console.log('PASS: all four youth NEET charts retain comparison/year and series colors through light → dark → light.');
