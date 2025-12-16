#!/usr/bin/env python3
"""
Add gradient fills to Vega-Lite area chart specifications.

Applies a beautiful vertical gradient from transparent at bottom to
semi-transparent at top, using category10 blue (#1f77b4 = rgb(31, 119, 180)).

The gradient gives area charts a lighter, more professional look while
maintaining the solid stroke line on top for visual definition.

Usage:
    python add_chart_gradients.py          # Dry run (shows changes)
    python add_chart_gradients.py --apply  # Apply changes
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple

# Category10 blue in RGB for gradient
BLUE_RGB = "31, 119, 180"  # #1f77b4

# Gradient definition - vertical fade from transparent (bottom) to semi-transparent (top)
GRADIENT_FILL = {
    "x1": 1,
    "y1": 1,
    "x2": 1,
    "y2": 0,
    "gradient": "linear",
    "stops": [
        {"offset": 0, "color": f"rgba({BLUE_RGB}, 0.02)"},
        {"offset": 1, "color": f"rgba({BLUE_RGB}, 0.35)"}
    ]
}


def add_gradient_to_spec(spec: Dict[str, Any]) -> Tuple[Dict[str, Any], list]:
    """
    Add gradient fill to area marks in a Vega-Lite spec.
    Returns (modified_spec, list_of_changes).
    """
    changes = []

    def process_mark(mark: Any, path: str) -> Any:
        """Add gradient to an area mark."""
        if isinstance(mark, str):
            if mark == "area":
                changes.append(f"{path}: Area mark detected but can't add gradient to string mark")
            return mark

        if not isinstance(mark, dict):
            return mark

        mark_type = mark.get("type")
        if mark_type != "area":
            return mark

        new_mark = dict(mark)

        # Check if this is a multi-series chart (has color encoding)
        # Multi-series charts shouldn't have explicit fill colors
        # as they get colors from the color encoding

        # Add gradient fill
        if "color" not in new_mark:
            new_mark["color"] = GRADIENT_FILL
            changes.append(f"{path}: Added gradient fill")
        elif isinstance(new_mark.get("color"), dict) and "gradient" in new_mark["color"]:
            # Already has a gradient, skip
            pass
        elif isinstance(new_mark.get("color"), str):
            # Has a solid color, replace with gradient
            new_mark["color"] = GRADIENT_FILL
            changes.append(f"{path}: Replaced solid color with gradient fill")

        # Ensure there's a solid line on top
        if "line" not in new_mark:
            new_mark["line"] = {"stroke": "#1f77b4", "strokeWidth": 2}
            changes.append(f"{path}: Added stroke line")
        elif isinstance(new_mark["line"], dict):
            if "stroke" not in new_mark["line"]:
                new_mark["line"]["stroke"] = "#1f77b4"
                changes.append(f"{path}.line: Added stroke color")
            if "strokeWidth" not in new_mark["line"]:
                new_mark["line"]["strokeWidth"] = 2
        elif new_mark["line"] is True:
            new_mark["line"] = {"stroke": "#1f77b4", "strokeWidth": 2}
            changes.append(f"{path}: Converted line:true to object with stroke")

        return new_mark

    def has_color_encoding(spec_or_layer: Dict) -> bool:
        """Check if this spec or layer has a color field encoding (multi-series)."""
        encoding = spec_or_layer.get("encoding", {})
        color_enc = encoding.get("color", {})
        return isinstance(color_enc, dict) and "field" in color_enc

    # Deep copy the spec
    new_spec = json.loads(json.dumps(spec))

    # Check if this is a multi-series chart at top level
    is_multi_series = has_color_encoding(new_spec)

    # Process top-level mark (only for single-series charts)
    if "mark" in new_spec and not is_multi_series:
        new_spec["mark"] = process_mark(new_spec["mark"], "mark")

    # Process layers
    if "layer" in new_spec:
        for i, layer in enumerate(new_spec["layer"]):
            # Check if this specific layer has color encoding
            layer_is_multi = has_color_encoding(layer) or is_multi_series

            if "mark" in layer and not layer_is_multi:
                new_spec["layer"][i]["mark"] = process_mark(layer["mark"], f"layer[{i}].mark")

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

    new_spec, changes = add_gradient_to_spec(spec)

    if changes and apply:
        with open(file_path, 'w') as f:
            json.dump(new_spec, f, indent=2)
            f.write('\n')  # Trailing newline

    return bool(changes), changes


def main():
    parser = argparse.ArgumentParser(description='Add gradient fills to area charts')
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
