#!/usr/bin/env python3
"""
Fix chart standards in Vega-Lite specifications.

Fixes:
1. Remove vertical gridlines (only horizontal allowed for vertical charts)
2. Remove permanent circle markers ("point": true) from line marks
3. Ensure consistent styling

Usage:
    python fix_chart_standards.py          # Dry run (shows changes)
    python fix_chart_standards.py --apply  # Apply changes
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple


def fix_chart_standards(spec: Dict[str, Any]) -> Tuple[Dict[str, Any], list]:
    """
    Fix chart standards in a Vega-Lite spec.
    Returns (modified_spec, list_of_changes).
    """
    changes = []

    # Deep copy the spec
    new_spec = json.loads(json.dumps(spec))

    def fix_axis_grid(axis_config: Dict, axis_name: str, path: str) -> Dict:
        """Fix gridlines on an axis."""
        new_axis = dict(axis_config)

        # For X axis (usually horizontal time/category axis) - disable grid
        if axis_name == 'x':
            if new_axis.get('grid') != False:
                new_axis['grid'] = False
                changes.append(f"{path}.axis: Disabled vertical gridlines (grid: false)")

        return new_axis

    def fix_mark_points(mark: Any, path: str) -> Any:
        """Remove point: true from line marks."""
        if isinstance(mark, str):
            return mark

        if not isinstance(mark, dict):
            return mark

        new_mark = dict(mark)
        mark_type = new_mark.get('type')

        # Remove point: true from line marks
        if mark_type == 'line' and new_mark.get('point') == True:
            del new_mark['point']
            changes.append(f"{path}: Removed permanent circle markers (point: true)")

        return new_mark

    # Fix top-level encoding axes
    if 'encoding' in new_spec:
        encoding = new_spec['encoding']

        # Fix X axis gridlines
        if 'x' in encoding and isinstance(encoding['x'], dict):
            if 'axis' not in encoding['x']:
                encoding['x']['axis'] = {}
            if isinstance(encoding['x']['axis'], dict):
                encoding['x']['axis'] = fix_axis_grid(encoding['x']['axis'], 'x', 'encoding.x')

    # Fix top-level mark
    if 'mark' in new_spec:
        new_spec['mark'] = fix_mark_points(new_spec['mark'], 'mark')

    # Fix layers
    if 'layer' in new_spec:
        for i, layer in enumerate(new_spec['layer']):
            # Fix marks in layers
            if 'mark' in layer:
                new_spec['layer'][i]['mark'] = fix_mark_points(layer['mark'], f'layer[{i}].mark')

            # Fix encoding axes in layers
            if 'encoding' in layer:
                layer_encoding = layer['encoding']
                if 'x' in layer_encoding and isinstance(layer_encoding['x'], dict):
                    if 'axis' not in layer_encoding['x']:
                        layer_encoding['x']['axis'] = {}
                    if isinstance(layer_encoding['x']['axis'], dict):
                        new_spec['layer'][i]['encoding']['x']['axis'] = fix_axis_grid(
                            layer_encoding['x']['axis'], 'x', f'layer[{i}].encoding.x'
                        )

    return new_spec, changes


def process_chart_file(file_path: Path, apply: bool = False) -> Tuple[bool, list]:
    """
    Process a single chart file.
    Returns (changed, changes).
    """
    try:
        with open(file_path, 'r') as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Error: Invalid JSON - {e}"]

    new_spec, changes = fix_chart_standards(spec)

    if changes and apply:
        with open(file_path, 'w') as f:
            json.dump(new_spec, f, indent=2, ensure_ascii=False)
            f.write('\n')  # Trailing newline

    return bool(changes), changes


def main():
    parser = argparse.ArgumentParser(description='Fix chart standards (gridlines, markers)')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry run)')
    parser.add_argument('--chart', type=str, help='Process a single chart file')
    args = parser.parse_args()

    if args.chart:
        chart_files = [Path(args.chart)]
    else:
        # Find all charts
        charts_dir = Path('/home/ritz/Insync/robert@aum.edu.mn/Google Drive/data/data.mn/public/charts')
        chart_files = sorted(charts_dir.glob('*.json'))

    if not chart_files:
        print("No chart files found")
        return 1

    print(f"\n{'='*60}")
    print(f"{'APPLYING CHANGES' if args.apply else 'DRY RUN (use --apply to make changes)'}")
    print(f"{'='*60}\n")

    total_changed = 0

    for chart_path in chart_files:
        changed, changes = process_chart_file(chart_path, args.apply)

        if changed:
            total_changed += 1
            print(f"\n📊 {chart_path.name}")
            for change in changes:
                print(f"   • {change}")

    print(f"\n{'='*60}")
    print(f"Summary: {total_changed}/{len(chart_files)} charts {'updated' if args.apply else 'would be updated'}")
    print(f"{'='*60}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
