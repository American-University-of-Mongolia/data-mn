/**
 * Export Chart Thumbnails
 *
 * Generates WebP thumbnail images from Vega-Lite chart specifications.
 * Uses node-canvas for server-side rendering (no headless browser needed).
 *
 * IMPORTANT: This script must match the browser rendering as closely as possible.
 * The browser uses vega@5.30.0, vega-lite@5.21.0 with the 'vox' theme.
 * Make sure devDependencies versions match!
 *
 * Usage: node scripts/export-chart-thumbnails.js
 */

import * as vega from 'vega';
import * as vegaLite from 'vega-lite';
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createCanvas } from 'canvas';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const CHARTS_DIR = path.resolve(__dirname, '../public/charts');
const OUTPUT_DIR = path.resolve(__dirname, '../public/thumbnails');
const WIDTH = 800;
const HEIGHT = 500; // 16:10 aspect ratio (800 * 0.625 = 500)
const WEBP_QUALITY = 85;

// Vega 'vox' theme configuration - must match what browser uses
// Source: https://github.com/vega/vega-themes/blob/master/src/theme-vox.ts
const voxTheme = {
  background: '#ffffff',
  arc: { fill: '#1f77b4' },
  area: { fill: '#1f77b4' },
  line: { stroke: '#1f77b4', strokeWidth: 2 },
  path: { stroke: '#1f77b4' },
  rect: { fill: '#1f77b4' },
  shape: { stroke: '#1f77b4' },
  symbol: { fill: '#1f77b4', strokeWidth: 1.5, size: 50 },
  axis: {
    domainWidth: 0.5,
    domainColor: '#888888',
    gridWidth: 0.5,
    gridColor: '#ddd',
    labelColor: '#000000',
    labelFontSize: 11,
    labelFont: 'sans-serif',
    tickColor: '#888888',
    tickSize: 3,
    titleFont: 'sans-serif',
    titleFontSize: 11,
    titleFontWeight: 'bold',
    titleColor: '#000000',
  },
  axisBand: {
    grid: false,
  },
  legend: {
    labelFontSize: 11,
    labelFont: 'sans-serif',
    symbolSize: 100,
    titleFont: 'sans-serif',
    titleFontSize: 11,
    titleFontWeight: 'bold',
  },
  range: {
    category: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
    diverging: ['#e7ba52', '#c7c7c7', '#aec7e8', '#1f77b4', '#9467bd'],
    heatmap: ['#fcfcfc', '#f2f2f2', '#dedede', '#d4d4d4', '#c2c2c2', '#b0b0b0', '#9e9e9e', '#8c8c8c', '#7a7a7a', '#686868'],
    ramp: ['#f2f2f2', '#dedede', '#d4d4d4', '#c2c2c2', '#b0b0b0', '#9e9e9e', '#8c8c8c', '#7a7a7a', '#686868'],
  },
  title: {
    font: 'sans-serif',
    fontSize: 14,
    fontWeight: 'bold',
  },
};

/**
 * Export a single Vega-Lite chart to WebP
 */
async function exportChart(specPath, outputPath) {
  const specContent = fs.readFileSync(specPath, 'utf-8');
  const spec = JSON.parse(specContent);

  // Merge spec config with vox theme, then our overrides
  // This matches how vega-embed applies themes in the browser
  const existingConfig = spec.config || {};
  const chartSpec = {
    ...spec,
    width: WIDTH - 120,
    height: HEIGHT - 100,
    padding: { left: 5, right: 5, top: 5, bottom: 0 },
    autosize: { type: 'fit', contains: 'padding' },
    background: '#ffffff',
    config: {
      // Start with vox theme as base
      ...voxTheme,
      // Apply spec's own config on top
      ...existingConfig,
      // Merge nested objects properly
      axis: {
        ...voxTheme.axis,
        ...(existingConfig.axis || {}),
      },
      legend: {
        ...voxTheme.legend,
        ...(existingConfig.legend || {}),
      },
      range: {
        ...voxTheme.range,
        ...(existingConfig.range || {}),
      },
      // Default mark colors for single-series charts (no color encoding)
      area: {
        ...voxTheme.area,
        ...(existingConfig.area || {}),
        line: { stroke: '#1f77b4' },
      },
      line: {
        ...voxTheme.line,
        ...(existingConfig.line || {}),
      },
      bar: {
        ...(existingConfig.bar || {}),
        fill: '#1f77b4',
      },
      point: {
        ...(existingConfig.point || {}),
        fill: '#1f77b4',
      },
      arc: {
        ...voxTheme.arc,
        ...(existingConfig.arc || {}),
      },
    },
  };

  // Remove any existing width/height from nested specs (for layered charts)
  if (chartSpec.layer) {
    chartSpec.layer = chartSpec.layer.map(layer => {
      const { width, height, ...rest } = layer;
      return rest;
    });
  }

  // Compile Vega-Lite to Vega
  const vegaSpec = vegaLite.compile(chartSpec).spec;

  // Create Vega view with loader for resolving /datasets/*.csv
  const loader = vega.loader({
    baseURL: path.resolve(__dirname, '../public'),
  });

  // Create Vega view for server-side rendering
  // Use 'none' renderer, then toCanvas() will use node-canvas
  const view = new vega.View(vega.parse(vegaSpec), {
    renderer: 'none',
    loader: loader,
  });

  view.initialize();

  // Run the dataflow and render
  await view.runAsync();

  // Get canvas buffer directly - Vega's toCanvas() returns a node-canvas instance
  const canvas = await view.toCanvas();
  const pngBuffer = canvas.toBuffer('image/png');

  // Convert to WebP with sharp
  await sharp(pngBuffer)
    .resize(WIDTH, HEIGHT, {
      fit: 'contain',
      background: { r: 255, g: 255, b: 255, alpha: 1 }
    })
    .webp({ quality: WEBP_QUALITY })
    .toFile(outputPath);

  view.finalize();
}

/**
 * Main function - export all charts
 */
async function main() {
  console.log('🎨 Exporting chart thumbnails...\n');

  // Ensure output directory exists
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  // Get all chart JSON files
  if (!fs.existsSync(CHARTS_DIR)) {
    console.log('⚠️  No charts directory found at', CHARTS_DIR);
    return;
  }

  const chartFiles = fs.readdirSync(CHARTS_DIR)
    .filter(f => f.endsWith('.json'));

  if (chartFiles.length === 0) {
    console.log('⚠️  No chart files found');
    return;
  }

  console.log(`Found ${chartFiles.length} charts to export\n`);

  let successCount = 0;
  let errorCount = 0;

  for (const file of chartFiles) {
    const inputPath = path.join(CHARTS_DIR, file);
    const outputFile = file.replace('.json', '.webp');
    const outputPath = path.join(OUTPUT_DIR, outputFile);

    try {
      await exportChart(inputPath, outputPath);
      console.log(`  ✓ ${file} → ${outputFile}`);
      successCount++;
    } catch (error) {
      console.error(`  ✗ ${file}: ${error.message}`);
      errorCount++;
    }
  }

  console.log(`\n✨ Done! ${successCount} exported, ${errorCount} failed`);
}

// Run
main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
