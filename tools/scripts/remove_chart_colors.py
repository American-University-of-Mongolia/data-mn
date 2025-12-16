#!/usr/bin/env python3
"""
Remove hardcoded brand colors from Vega-Lite chart specifications.

This script converts charts from using explicit brand colors (#2563eb, etc.)
to using Vega-Lite's default color scheme (tableau10/Altair defaults).

What it removes:
- Explicit "color": "#2563eb" in marks
- "scale": {"range": [...]} from color encodings
- Gradient fills (replaced with simple area marks)

What it preserves:
- Chart structure (layers, params, etc.)
- Typography config (font sizes, colors)
- All other mark properties

Usage:
    python remove_chart_colors.py          # Dry run (shows changes)
    python remove_chart_colors.py --apply  # Apply changes
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple


def remove_colors_from_spec(spec: Dict[str, Any]) -> Tuple[Dict[str, Any], list]:
    """
    Remove explicit color definitions from a Vega-Lite spec.
    Returns (modified_spec, list_of_changes).
    """
    changes = []

    def process_mark(mark: Any, path: str = "mark") -> Any:
        """Process a mark definition to remove colors."""
        if isinstance(mark, str):
            return mark

        if not isinstance(mark, dict):
            return mark

        new_mark = dict(mark)

        # Remove explicit color from mark
        if 'color' in new_mark:
            color = new_mark['color']
            # Check if it's a gradient (dict with 'gradient' key)
            if isinstance(color, dict) and 'gradient' in color:
                del new_mark['color']
                changes.append(f"{path}: Removed gradient fill (Vega defaults will apply)")
            elif isinstance(color, str) and color.startswith('#'):
                del new_mark['color']
                changes.append(f"{path}: Removed color '{color}'")

        # Handle line color inside area mark
        if 'line' in new_mark and isinstance(new_mark['line'], dict):
            if 'color' in new_mark['line']:
                del new_mark['line']['color']
                changes.append(f"{path}.line: Removed explicit line color")

        return new_mark

    def process_encoding(encoding: Dict, path: str = "encoding") -> Dict:
        """Process encoding to remove color scale ranges."""
        if 'color' not in encoding:
            return encoding

        new_encoding = dict(encoding)
        color_enc = encoding['color']

        if isinstance(color_enc, dict):
            new_color = dict(color_enc)

            # Remove explicit color value
            if 'value' in new_color and isinstance(new_color['value'], str):
                if new_color['value'].startswith('#'):
                    del new_color['value']
                    changes.append(f"{path}.color: Removed explicit color value")

            # Remove condition with explicit colors
            if 'condition' in new_color:
                cond = new_color['condition']
                if isinstance(cond, dict) and 'value' in cond:
                    if isinstance(cond['value'], str) and cond['value'].startswith('#'):
                        del new_color['condition']
                        changes.append(f"{path}.color: Removed hover color condition")

            # Remove scale.range (explicit color palette)
            if 'scale' in new_color and isinstance(new_color['scale'], dict):
                if 'range' in new_color['scale']:
                    new_scale = dict(new_color['scale'])
                    del new_scale['range']
                    if new_scale:  # Keep scale if it has other properties
                        new_color['scale'] = new_scale
                    else:
                        del new_color['scale']
                    changes.append(f"{path}.color.scale: Removed explicit color range")

            # Clean up empty color encoding
            if new_color:
                new_encoding['color'] = new_color
            else:
                del new_encoding['color']

        return new_encoding

    # Deep copy the spec
    new_spec = json.loads(json.dumps(spec))

    # Process top-level mark
    if 'mark' in new_spec:
        new_spec['mark'] = process_mark(new_spec['mark'])

    # Process top-level encoding
    if 'encoding' in new_spec:
        new_spec['encoding'] = process_encoding(new_spec['encoding'])

    # Process layers
    if 'layer' in new_spec:
        for i, layer in enumerate(new_spec['layer']):
            if 'mark' in layer:
                new_spec['layer'][i]['mark'] = process_mark(layer['mark'], f"layer[{i}].mark")
            if 'encoding' in layer:
                new_spec['layer'][i]['encoding'] = process_encoding(layer['encoding'], f"layer[{i}].encoding")

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

    new_spec, changes = remove_colors_from_spec(spec)

    if changes and apply:
        with open(file_path, 'w') as f:
            json.dump(new_spec, f, indent=2)
            f.write('\n')  # Trailing newline

    return bool(changes), changes


def main():
    parser = argparse.ArgumentParser(description='Remove hardcoded colors from Vega-Lite charts')
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
