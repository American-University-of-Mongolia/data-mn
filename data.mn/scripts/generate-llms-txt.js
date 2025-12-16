/**
 * Generate llms.txt
 *
 * Creates an index file at /llms.txt for AI agents to discover
 * available datasets and understand how to access them.
 *
 * Usage: node scripts/generate-llms-txt.js
 * Runs after: astro build and generate-ai-markdown.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import matter from 'gray-matter';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const MDX_BASE = path.resolve(__dirname, '../src/data/data/en'); // Use English as index
const DIST_DIR = path.resolve(__dirname, '../dist');
const SITE_URL = 'https://data.mn';

/**
 * Group datasets by category
 */
function groupByCategory(datasets) {
  const groups = {};

  for (const dataset of datasets) {
    const category = dataset.category || 'Other';
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(dataset);
  }

  // Sort categories alphabetically, but put "Other" last
  const sortedCategories = Object.keys(groups).sort((a, b) => {
    if (a === 'Other') return 1;
    if (b === 'Other') return -1;
    return a.localeCompare(b);
  });

  return sortedCategories.map((cat) => ({
    name: cat,
    datasets: groups[cat].sort((a, b) => a.title.localeCompare(b.title)),
  }));
}

/**
 * Main function
 */
async function main() {
  console.log('📄 Generating llms.txt...\n');

  // Check if dist directory exists
  if (!fs.existsSync(DIST_DIR)) {
    console.error('❌ dist/ directory not found. Run "astro build" first.');
    process.exit(1);
  }

  // Read all MDX files to get dataset info
  const datasets = [];

  if (fs.existsSync(MDX_BASE)) {
    const mdxFiles = fs.readdirSync(MDX_BASE).filter((f) => f.endsWith('.mdx'));

    for (const file of mdxFiles) {
      const mdxPath = path.join(MDX_BASE, file);
      const mdxContent = fs.readFileSync(mdxPath, 'utf-8');
      const { data: frontmatter } = matter(mdxContent);

      // Skip drafts
      if (frontmatter.draft === true) continue;

      const slug = file.replace(/\.mdx?$/, '');

      datasets.push({
        slug,
        title: frontmatter.title || slug,
        excerpt: frontmatter.excerpt || '',
        category: frontmatter.category || 'Other',
      });
    }
  }

  console.log(`Found ${datasets.length} datasets`);

  // Group by category
  const categories = groupByCategory(datasets);

  // Generate llms.txt content
  let content = `# Data.mn - Mongolia's Open Data Platform

> Bilingual statistical data (English/Mongolian) on Mongolia's economy,
> population, trade, and more. All data available as CSV and Excel downloads.

## How to Access Data

### Option 1: Request Markdown (Recommended)

Add the \`Accept: text/markdown\` header to get clean markdown instead of HTML:

\`\`\`bash
curl -H "Accept: text/markdown" ${SITE_URL}/en/data/gdp-sector-trends
\`\`\`

### Option 2: Direct .md URL

Append \`.md\` to any data page URL:

\`\`\`
${SITE_URL}/en/data/gdp-sector-trends.md
\`\`\`

### Option 3: Download Raw Data

CSV and Excel files are available at:
- \`${SITE_URL}/datasets/{dataset-slug}-en.csv\` (English)
- \`${SITE_URL}/datasets/{dataset-slug}-mn.csv\` (Mongolian)
- \`${SITE_URL}/datasets/{dataset-slug}.xlsx\` (Excel with both languages)

## Languages

All content is available in both English and Mongolian:
- English: \`${SITE_URL}/en/data/{slug}\`
- Mongolian: \`${SITE_URL}/mn/data/{slug}\`

## Available Datasets

`;

  // Add categorized dataset list
  for (const category of categories) {
    content += `### ${category.name}\n\n`;

    for (const dataset of category.datasets) {
      // Truncate excerpt if too long
      let excerpt = dataset.excerpt;
      if (excerpt.length > 100) {
        excerpt = excerpt.substring(0, 100).trim() + '...';
      }
      content += `- [${dataset.title}](${SITE_URL}/en/data/${dataset.slug}): ${excerpt}\n`;
    }

    content += '\n';
  }

  // Footer
  content += `---

## Contact

For questions about the data, contact: hello@data.mn

## About

Data.mn provides free, open access to Mongolian statistical data.
Data is sourced from official government agencies including the
National Statistics Office (1212.mn) and other ministries.

Last updated: ${new Date().toISOString().split('T')[0]}
`;

  // Write to dist
  const outputPath = path.join(DIST_DIR, 'llms.txt');
  fs.writeFileSync(outputPath, content, 'utf-8');

  console.log(`\n✨ Generated ${outputPath}`);
  console.log(`   ${datasets.length} datasets indexed across ${categories.length} categories`);
}

// Run
main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
