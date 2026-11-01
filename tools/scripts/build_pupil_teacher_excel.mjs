// Run with the bundled @oai/artifact-tool runtime. The source JSON is emitted
// by build_pupil_teacher_ratio.py and contains the canonical wide CSV pivots.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const payload = JSON.parse(await fs.readFile(path.join(root, 'tools/temp/pupil-teacher-excel.json'), 'utf8'));
const previewDir = process.env.PUPIL_TEACHER_PREVIEW_DIR || path.join(root, 'tools/temp');
await fs.mkdir(previewDir, { recursive: true });

function colName(n) {
  let name = '';
  while (n) {
    n--;
    name = String.fromCharCode(65 + (n % 26)) + name;
    n = Math.floor(n / 26);
  }
  return name;
}

for (const lang of ['en', 'mn']) {
  const { sheet: sheetName, columns, rows, source } = payload[lang];
  const workbook = Workbook.create();
  const sheet = workbook.worksheets.add(sheetName);
  const last = colName(columns.length);
  const bottom = rows.length + 1;
  sheet.getRange(`A1:${last}${bottom}`).values = [columns, ...rows];
  sheet.showGridLines = false;
  sheet.getRange(`A1:${last}${bottom}`).format.font = { name: 'Arial', size: 11, color: '#334155' };
  sheet.getRange(`A1:${last}${bottom}`).format.verticalAlignment = 'center';
  sheet.getRange(`A1:${last}${bottom}`).format.rowHeight = 22;
  sheet.getRange(`A1:${last}${bottom}`).format.columnWidth = 24;
  sheet.getRange(`A1:A${bottom}`).format.columnWidth = 9;
  sheet.getRange(`A2:A${bottom}`).setNumberFormat('0');
  sheet.getRange(`B2:${last}${bottom}`).setNumberFormat('0.0');
  sheet.getRange(`A1:${last}1`).format = {
    fill: '#1E3A5F',
    font: { name: 'Arial', size: 11, bold: true, color: '#FFFFFF' },
    wrapText: true,
    horizontalAlignment: 'center',
    verticalAlignment: 'center',
    rowHeight: 46,
  };
  sheet.getRange(`A2:${last}${bottom}`).format.horizontalAlignment = 'right';
  for (let row = 2; row <= bottom; row += 2) {
    sheet.getRange(`A${row}:${last}${row}`).format.fill = '#F1F5F9';
  }
  sheet.freezePanes.freezeRows(1);
  sheet.freezePanes.freezeColumns(1);
  workbook.notes.add({
    id: `${sheetName}:B2`,
    target: { cell: { sheetName, sheetId: sheet.sheetId, address: 'B2' } },
    authorId: '', createdAt: '',
    body: { plainText: lang === 'en'
      ? `Source: NSO / Ministry of Education, table DT_NSO_2002_015V1. ${source}\nUnit: pupils per teacher (not percent). Source year labels retained. Each column combines education level and location. National ratios are official source values. School-year definitions and historical comparability are explained on the dataset page.`
      : `Эх сурвалж: ҮСХ / Боловсролын яам, DT_NSO_2002_015V1 хүснэгт. ${source}\nНэгж: нэг багшид ногдох сурагчийн тоо (хувь биш). Эх сурвалжийн оны тэмдэглэгээг хадгалсан. Багана бүр боловсролын түвшин, байршлын хослол. Улсын дундаж нь эх сурвалжийн утга. Хичээлийн жил, түүхэн харьцуулагдах байдлын тайлбарыг өгөгдлийн хуудаснаас үзнэ үү.` },
  });
  workbook.recalculate();
  console.log((await workbook.inspect({ kind: 'table', range: `${sheetName}!A1:D4`, include: 'values,formulas', tableMaxRows: 4, tableMaxCols: 4, maxChars: 1500 })).ndjson);
  console.log((await workbook.inspect({ kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!', options: { useRegex: true, maxResults: 10 }, maxChars: 500 })).ndjson);
  const image = await workbook.render({ sheetName, range: 'A1:F12', scale: 1.5, format: 'png' });
  await fs.writeFile(path.join(previewDir, `excel-${lang}.png`), new Uint8Array(await image.arrayBuffer()));
  await (await SpreadsheetFile.exportXlsx(workbook)).save(path.join(root, `data.mn/public/datasets/pupil-teacher-ratio-${lang}.xlsx`));
  console.log(`Exported ${lang}: ${rows.length} years x ${columns.length - 1} series`);
}
