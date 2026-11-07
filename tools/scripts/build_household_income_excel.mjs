import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const payload = JSON.parse(await fs.readFile(path.join(root, 'tools/temp/household-income-excel.json'), 'utf8'));
const outputs = path.resolve(root, '../outputs/household-income-sources');
await fs.mkdir(outputs, { recursive: true });
for (const lang of ['en', 'mn']) {
  const { columns, rows, source } = payload[lang];
  const workbook = Workbook.create();
  const sheetName = lang === 'en' ? 'English' : 'Монгол';
  const sheet = workbook.worksheets.add(sheetName);
  // Established Data.mn download format: year down rows, all series across columns.
  const last = 'Y';
  const bottom = rows.length + 1;
  sheet.getRange(`A1:${last}${bottom}`).values = [columns, ...rows];
  sheet.showGridLines = false;
  sheet.getRange(`A1:${last}${bottom}`).format = {
    font: { name: 'Arial', size: 11, color: '#334155' },
    verticalAlignment: 'center', columnWidth: 30, rowHeight: 23,
  };
  sheet.getRange(`A1:A${bottom}`).format.columnWidth = 9;
  sheet.getRange(`A2:A${bottom}`).setNumberFormat('0');
  sheet.getRange(`B2:${last}${bottom}`).setNumberFormat('0.0');
  sheet.getRange(`A1:${last}1`).format = {
    fill: '#1e3a5f', font: { name: 'Arial', size: 11, bold: true, color: '#ffffff' },
    wrapText: true, horizontalAlignment: 'center', verticalAlignment: 'center', rowHeight: 94,
  };
  sheet.getRange(`A2:${last}${bottom}`).format.horizontalAlignment = 'right';
  for (let row = 2; row <= bottom; row += 2) sheet.getRange(`A${row}:${last}${row}`).format.fill = '#f1f5f9';
  sheet.freezePanes.freezeRows(1);
  sheet.freezePanes.freezeColumns(1);
  workbook.notes.add({
    id: `${sheetName}:B2`, target: { cell: { sheetName, sheetId: sheet.sheetId, address: 'B2' } }, authorId: '', createdAt: '',
    body: { plainText: lang === 'en'
      ? `Source: NSO Household Socio-Economic Survey, DT_NSO_1900_003V1.px. ${source}\nShare of average monthly total household income, percent (0–100). Coverage: 2007–2025; retrieved 7 November 2026. Includes total income and the monetary subtotal: do not sum all eight series. Non-cash income includes food consumed from own farming. Chart selections do not limit downloads.`
      : `Эх сурвалж: ҮСХ, Өрхийн нийгэм, эдийн засгийн судалгаа, DT_NSO_1900_003V1.px. ${source}\nНэг өрхийн сарын дундаж нийт орлогод эзлэх хувь (0–100). Хамрах хугацаа: 2007–2025; 2026 оны 11 дүгээр сарын 7-нд татав. Нийт орлого болон мөнгөн орлогын дүн орсон тул найман үзүүлэлтийг бүгдийг нь нэмж болохгүй. Мөнгөн бус орлогод өөрийн аж ахуйгаас хэрэглэсэн хүнсний үнэлгээ багтана. Графикийн сонголт татах файлыг хязгаарлахгүй.` },
  });
  workbook.recalculate();
  console.log((await workbook.inspect({ kind: 'table', range: `${sheetName}!A1:D4`, include: 'values,formulas', tableMaxRows: 4, tableMaxCols: 4, maxChars: 1200 })).ndjson);
  console.log((await workbook.inspect({ kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!', options: { useRegex: true, maxResults: 10 }, maxChars: 500 })).ndjson);
  const preview = await workbook.render({ sheetName, range: 'A1:F10', scale: 1.4, format: 'png' });
  await fs.writeFile(path.join(outputs, `excel-${lang}.png`), new Uint8Array(await preview.arrayBuffer()));
  const output = await SpreadsheetFile.exportXlsx(workbook);
  const filename = `household-income-sources-${lang}.xlsx`;
  await output.save(path.join(root, 'data.mn/public/datasets', filename));
  await fs.copyFile(path.join(root, 'data.mn/public/datasets', filename), path.join(outputs, filename));
  console.log(`Exported ${lang}: ${rows.length} years, ${columns.length - 1} series.`);
}
