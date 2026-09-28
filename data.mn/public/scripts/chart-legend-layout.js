const DEFAULT_MAX_COLUMNS = 4;
const LEGEND_HORIZONTAL_CHROME = 42;
const LEGEND_COLUMN_PADDING = 18;

function colorEncodings(value, encodings = []) {
  if (!value || typeof value !== 'object') return encodings;
  if (Array.isArray(value)) {
    value.forEach((child) => colorEncodings(child, encodings));
    return encodings;
  }

  const color = value.encoding && value.encoding.color;
  if (
    color &&
    typeof color === 'object' &&
    (color.type === 'nominal' || color.type === 'ordinal') &&
    color.legend !== null &&
    color.legend !== false
  ) {
    encodings.push(color);
  }

  Object.values(value).forEach((child) => colorEncodings(child, encodings));
  return encodings;
}

export function categoricalLegendLabels(spec, rows = []) {
  const labels = [];
  const sourceRows = Array.isArray(rows) ? rows : [];
  colorEncodings(spec).forEach((encoding) => {
    const domain = encoding.scale && encoding.scale.domain;
    const values = Array.isArray(domain)
      ? domain
      : sourceRows
          .map((row) => row[encoding.field])
          .filter((value) => value !== undefined && value !== null && value !== '');
    values.forEach((value) => labels.push(String(value)));
  });
  return Array.from(new Set(labels));
}

export function estimateLegendLabelWidth(label, fontSize = 13) {
  return Array.from(String(label)).reduce((width, character) => {
    if (/\s/.test(character)) return width + fontSize * 0.34;
    if (/[ilI1|.,:;'`]/.test(character)) return width + fontSize * 0.32;
    if (/[MW@#%&]/.test(character)) return width + fontSize * 0.9;
    return width + fontSize * 0.66;
  }, 0);
}

export function calculateLegendLayout(labels, containerWidth, fontSize = 13) {
  const availableWidth = Math.max(120, containerWidth - 80);
  const widestLabel = Math.max(80, ...labels.map((label) => estimateLegendLabelWidth(label, fontSize)));
  const itemWidth = widestLabel + LEGEND_HORIZONTAL_CHROME;
  const fittingColumns = Math.floor((availableWidth + LEGEND_COLUMN_PADDING) / (itemWidth + LEGEND_COLUMN_PADDING));

  return {
    columns: Math.max(1, Math.min(labels.length || DEFAULT_MAX_COLUMNS, DEFAULT_MAX_COLUMNS, fittingColumns || 1)),
    // Vega interprets zero as unlimited. Columns are chosen from the actual
    // label widths, so full labels wrap to another row instead of ellipsizing.
    labelLimit: 0,
  };
}

export function applyCategoricalLegendLayout(spec, labels, containerWidth, fontSize = 13) {
  const layout = calculateLegendLayout(labels, containerWidth, fontSize);
  colorEncodings(spec).forEach((encoding) => {
    encoding.legend = {
      ...(encoding.legend || {}),
      columns: layout.columns,
      labelLimit: layout.labelLimit,
    };
  });
  return layout;
}
