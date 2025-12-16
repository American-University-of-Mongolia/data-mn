#!/usr/bin/env python3
"""
Fix legend orientation in Vega-Lite chart specifications.

Ensures all charts with color legends have orient: "top" so legends
appear at the top of the chart, allowing the chart to use full width.

Usage:
    python fix_legend_orient.py          # Dry run (shows changes)
    python fix_legend_orient.py --apply  # Apply changes
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple


def fix_legend_orient(spec: Dict[str, Any]) -> Tuple[Dict[str, Any], list]:
    """
    Add orient: "top" to color legend configurations.
    Returns (modified_spec, list_of_changes).
    """
    changes = []

    def add_orient_to_legend(obj: Dict, path: str) -> bool:
        """Add orient: top to a legend config. Returns True if changed."""
        if 'legend' not in obj:
            return False

        legend = obj['legend']
        if legend is None:
            return False

        if isinstance(legend, dict):
            if legend.get('orient') != 'top':
                legend['orient'] = 'top'
                changes.append(f"{path}.legend: Added orient: 'top'")
                return True
        elif legend is True:
            # Replace boolean true with object containing orient
            obj['legend'] = {'orient': 'top'}
            changes.append(f"{path}.legend: Changed to object with orient: 'top'")
            return True

        return False

    # Deep copy the spec
    new_spec = json.loads(json.dumps(spec))

    # Check top-level encoding.color
    encoding = new_spec.get('encoding', {})
    if 'color' in encoding and isinstance(encoding['color'], dict):
        if 'field' in encoding['color']:
            # This is a multi-series chart with color encoding
            if 'legend' not in encoding['color']:
                encoding['color']['legend'] = {'orient': 'top'}
                changes.append("encoding.color.legend: Added with orient: 'top'")
            else:
                add_orient_to_legend(encoding['color'], 'encoding.color')

    # Check layers
    for i, layer in enumerate(new_spec.get('layer', [])):
        layer_encoding = layer.get('encoding', {})
        if 'color' in layer_encoding and isinstance(layer_encoding['color'], dict):
            if 'field' in layer_encoding['color']:
                if 'legend' not in layer_encoding['color']:
                    layer_encoding['color']['legend'] = {'orient': 'top'}
                    changes.append(f"layer[{i}].encoding.color.legend: Added with orient: 'top'")
                else:
                    add_orient_to_legend(layer_encoding['color'], f'layer[{i}].encoding.color')

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

    new_spec, changes = fix_legend_orient(spec)

    if changes and apply:
        with open(file_path, 'w') as f:
            json.dump(new_spec, f, indent=2)
            f.write('\n')  # Trailing newline

    return bool(changes), changes


def main():
    parser = argparse.ArgumentParser(description='Fix legend orientation in Vega-Lite charts')
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
