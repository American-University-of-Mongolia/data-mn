"""Export a dataset builder's wide JSON using the repository's openpyxl dependency.

Run from the repository root: python tools/scripts/build_wide_excel.py
DATASET --input tools/temp/NAME.json. The original CSV values are not changed.
"""
import argparse
import json
import math
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[2]


def export(payload, dataset, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    for lang in ('en', 'mn'):
        data = payload[lang]
        columns, rows = data['columns'], data['rows']
        assert columns and rows and len(set(columns)) == len(columns)
        assert len({row[0] for row in rows}) == len(rows), 'Duplicate years'
        assert all(len(row) == len(columns) for row in rows)
        assert all(isinstance(v, (int, float)) and math.isfinite(v) for row in rows for v in row)
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'English' if lang == 'en' else 'Монгол'
        sheet.append(columns)
        for row in rows:
            sheet.append(row)
        sheet.freeze_panes = 'B2'
        sheet.sheet_view.showGridLines = False
        for i in range(1, len(columns) + 1):
            sheet.column_dimensions[get_column_letter(i)].width = 9 if i == 1 else 30
        for row in sheet:
            header = row[0].row == 1
            sheet.row_dimensions[row[0].row].height = 94 if header else 23
            for cell in row:
                cell.font = Font(name='Arial', size=11, bold=header,
                                 color='FFFFFF' if header else '334155')
                cell.alignment = Alignment(horizontal='center' if header else 'right',
                                           vertical='center', wrap_text=header)
                if header or cell.row % 2 == 0:
                    cell.fill = PatternFill('solid', fgColor='1E3A5F' if header else 'F1F5F9')
                if not header:
                    cell.number_format = '0' if cell.column == 1 else '0.0'
        # Excel stores legacy cell notes as comments; this does not create a thread.
        sheet['B2'].comment = Comment(data.get('note', data['source']), 'Data.mn')
        target = output_dir / f'{dataset}-{lang}.xlsx'
        workbook.save(target)
        print(f'{target}: {len(rows)} years x {len(columns) - 1} series')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset')
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data.mn/public/datasets')
    args = parser.parse_args()
    if not args.dataset or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in args.dataset):
        parser.error('dataset must be a lowercase slug')
    export(json.loads(args.input.read_text()), args.dataset, args.output_dir)


if __name__ == '__main__':
    main()
