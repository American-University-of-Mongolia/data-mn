/**
 * Generate categories.generated.json from the registry database
 *
 * Reads the registry SQLite database and extracts unique categories
 * with bilingual support (category_en, category_mn) and counts
 * published datasets per category.
 *
 * Only includes categories where is_published = 1 AND status = 'active'
 */

import sqlite3 from 'sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { writeFileSync, existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Path to registry database
const DB_PATH = join(__dirname, '../../tools/registry/data.db');

// Output path
const OUTPUT_PATH = join(__dirname, '../src/data/categories.generated.json');

function generateCategories() {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(DB_PATH, sqlite3.OPEN_READONLY, (err) => {
      if (err) {
        reject(new Error(`Failed to open database: ${err.message}`));
        return;
      }
    });

    const query = `
      SELECT
        category_en,
        category_mn,
        COUNT(*) as count
      FROM datasets
      WHERE is_published = 1 AND status = 'active'
      GROUP BY category_en, category_mn
      ORDER BY count DESC
    `;

    db.all(query, [], (err, rows) => {
      if (err) {
        db.close();
        reject(new Error(`Query failed: ${err.message}`));
        return;
      }

      // Transform rows into the format we need
      const categories = rows.map(row => ({
        en: row.category_en,
        mn: row.category_mn || row.category_en, // Fallback to EN if MN is null
        count: row.count
      }));

      db.close((err) => {
        if (err) {
          console.error('Error closing database:', err.message);
        }
      });

      resolve(categories);
    });
  });
}

async function main() {
  try {
    console.log('Generating categories from registry database...');
    console.log(`Database: ${DB_PATH}`);

    // Check if database exists - if not, use existing generated file
    if (!existsSync(DB_PATH)) {
      if (existsSync(OUTPUT_PATH)) {
        console.log('Database not found, but categories.generated.json exists. Skipping generation.');
        console.log('Done!');
        return;
      } else {
        console.error('Error: Neither database nor categories.generated.json found!');
        process.exit(1);
      }
    }

    const categories = await generateCategories();

    console.log(`Found ${categories.length} categories:`);
    categories.forEach(cat => {
      console.log(`  - ${cat.en} / ${cat.mn} (${cat.count} datasets)`);
    });

    // Write to output file
    const output = JSON.stringify(categories, null, 2);
    writeFileSync(OUTPUT_PATH, output, 'utf8');

    console.log(`\nCategories written to: ${OUTPUT_PATH}`);
    console.log('Done!');
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
