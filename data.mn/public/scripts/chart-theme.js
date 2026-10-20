// Only theme chart backgrounds and guides. Marks, scales, and conditional
// colors carry meaning and must remain authored by the dataset.
export function applyChartTheme(spec, dark) {
  if (!dark) return spec;

  const axis = {
    labelColor: '#cbd5e1',
    titleColor: '#e2e8f0',
    gridColor: '#475569',
    domainColor: '#64748b',
    tickColor: '#64748b',
  };
  const labels = { labelColor: '#cbd5e1', titleColor: '#e2e8f0' };
  const title = { color: '#e2e8f0' };
  function recolor(value, colors) {
    if (value && typeof value === 'object') Object.assign(value, colors);
  }
  function visit(node) {
    if (!node || typeof node !== 'object') return;
    // Explicit guide settings override theme defaults, including those in
    // layered/faceted charts. Keep null/false guides disabled.
    recolor(node.title, title);
    Object.values(node.encoding || {}).forEach(function (encoding) {
      if (!encoding || typeof encoding !== 'object') return;
      recolor(encoding.axis, axis);
      recolor(encoding.legend, labels);
      recolor(encoding.header, labels);
    });
    if (node.facet) {
      recolor(node.facet.header, labels);
      recolor(node.facet.row?.header, labels);
      recolor(node.facet.column?.header, labels);
    }
    ['layer', 'concat', 'hconcat', 'vconcat'].forEach(function (key) {
      (node[key] || []).forEach(visit);
    });
    if (node.spec) visit(node.spec);
  }

  spec.background = '#1e293b';
  spec.config = spec.config || {};
  const config = spec.config;
  config.axis = Object.assign({}, config.axis, axis);
  config.legend = Object.assign({}, config.legend, labels);
  config.header = Object.assign({}, config.header, labels);
  config.title = Object.assign({}, config.title, title);
  // Axis/header variants have higher precedence than their base configs.
  Object.keys(config).forEach(function (key) {
    if (key.startsWith('axis')) recolor(config[key], axis);
    if (key.startsWith('header')) recolor(config[key], labels);
  });
  visit(spec);
  return spec;
}
