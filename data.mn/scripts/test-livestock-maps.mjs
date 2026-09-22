// Check map values, geometry, missing-data colours and scale stability in every year.
// Optional first argument: directory for representative PNG previews.
import fs from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import * as vega from 'vega';
import { compile } from 'vega-lite';

const root = fileURLToPath(new URL('..', import.meta.url));
const output = process.argv[2];
if (output) await fs.mkdir(output, { recursive: true });
const loader = vega.loader();
loader.load = (url) => fs.readFile(path.join(root, 'public', url), 'utf8');
const results = [];
const datasets = ['livestock-losses-by-aimag', 'livestock-loss-rate-by-aimag'].filter((id) =>
  existsSync(path.join(root, 'src/data/data/en', `${id}.mdx`))
);
assert.ok(datasets.length, 'No livestock map datasets are present');
for (const id of datasets) {
  for (const lang of ['en', 'mn']) {
    const name = `${id}-${lang}`;
    const spec = JSON.parse(await fs.readFile(path.join(root, 'public/charts', `${name}.json`), 'utf8'));
    const year = lang === 'en' ? 'year' : 'он';
    const category = lang === 'en' ? 'region' : 'бүс';
    const value = lang === 'en' ? 'value' : 'утга';
    const source = vega.read(await loader.load(spec.data.url), spec.data.format);
    assert.equal(spec.params[0].bind.min, 1971);
    assert.equal(spec.params[0].bind.max, 2025);
    const compiled = compile({ ...spec, width: 700, height: 420 }).spec;
    const view = new vega.View(vega.parse(compiled), { renderer: 'none', loader }).initialize();
    await view.runAsync();
    let missing = 0;
    for (let selected = 1971; selected <= 2025; selected++) {
      await view.signal('selectedYear', selected).runAsync();
      const shapes = [];
      function visit(node) {
        if (node.mark?.marktype === 'shape' && node.datum?.boundary) shapes.push(node);
        for (const item of node.items || []) visit(item);
      }
      visit(view.scenegraph().root);
      assert.equal(shapes.length, 22, `${name}: all regions must remain visible in ${selected}`);
      const expected = source.filter((row) => row[year] === selected);
      assert.deepEqual(
        shapes.map((item) => [item.datum[category], item.datum[value]]),
        expected.map((row) => [row[category], row[value]])
      );
      assert.deepEqual(view.scale('color').domain(), spec.encoding.color.scale.domain);
      for (const item of shapes) {
        assert.equal(item.datum[year], selected);
        if (item.datum[value] == null) {
          assert.equal(item.fill, '#cbd5e1');
          assert.equal(item.datum.display_value, lang === 'en' ? 'Unavailable' : 'Мэдээлэлгүй');
          missing++;
        } else {
          assert.notEqual(item.fill, '#cbd5e1');
        }
      }
      if (output && [1971, 1980, 2024, 2025].includes(selected)) {
        const suffix = selected === 2025 ? '' : `-${selected}`;
        await fs.writeFile(path.join(output, `${name}${suffix}.png`), (await view.toCanvas()).toBuffer('image/png'));
      }
    }
    view.finalize();
    results.push({
      chart: name,
      yearsChecked: 55,
      regionsEachYear: 22,
      missingValuesShownInGrey: missing,
      fixedColourScale: true,
    });
  }
}
console.log(JSON.stringify(results));
