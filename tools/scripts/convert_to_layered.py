#!/usr/bin/env python3
"""
Convert simple (non-layered) Vega-Lite charts to layered structure.

This enables proper nearest-point hover for tooltips. The `nearest: true`
selection parameter only works when there's a point layer to select on.

Structure before (SIMPLE - hover doesn't work well):
{
  "mark": {"type": "area", ...},
  "encoding": {..., "tooltip": [...]},
  "params": [{"name": "hover", ...}]  // Added but doesn't work!
}

Structure after (LAYERED - hover works):
{
  "encoding": {...},  // Shared x/y encoding
  "layer": [
    {"mark": {"type": "area", ...}},  // Visual layer
    {
      "params": [{"name": "hover", "select": {"nearest": true, ...}}],
      "mark": {"type": "point", ...},
      "encoding": {
        "opacity": {"condition": {...}, "value": 0},
        "tooltip": [...]
      }
    }
  ]
}
"""

import json
import os
from pathlib import Path
from copy import deepcopy


# Hover params with nearest: true
HOVER_PARAMS = {
    "name": "hover",
    "select": {
        "type": "point",
        "nearest": True,
        "on": "pointerover",
        "clear": "pointerout"
    }
}


def get_primary_color(chart: dict) -> str:
    """Extract the primary color from a chart's mark or encoding."""
    mark = chart.get("mark", {})

    # Check mark.color
    if isinstance(mark, dict):
        if "color" in mark:
            return mark["color"]
        if "line" in mark and isinstance(mark["line"], dict):
            return mark["line"].get("color", "#2563eb")

    # Check encoding.color
    encoding = chart.get("encoding", {})
    color_enc = encoding.get("color", {})
    if isinstance(color_enc, dict):
        scale = color_enc.get("scale", {})
        if "range" in scale and len(scale["range"]) > 0:
            return scale["range"][0]

    return "#2563eb"  # Default brand color


def is_bar_chart(chart: dict) -> bool:
    """Check if this is a bar chart."""
    mark = chart.get("mark", {})
    if isinstance(mark, str):
        return mark == "bar"
    return mark.get("type") == "bar"


def is_layered(chart: dict) -> bool:
    """Check if chart already uses layer structure."""
    return "layer" in chart


def convert_to_layered(chart: dict) -> dict:
    """Convert a simple chart to layered structure with proper hover."""

    if is_layered(chart):
        return chart  # Already layered

    if is_bar_chart(chart):
        # Bar charts work differently - they use hover on the bars themselves
        # Just ensure params are correct
        return chart

    # Extract components
    mark = chart.get("mark", {})
    encoding = chart.get("encoding", {})
    tooltip = encoding.pop("tooltip", None)  # Remove tooltip from main encoding

    # Get color for the point layer
    primary_color = get_primary_color(chart)

    # Remove params from top level (will be in point layer)
    chart.pop("params", None)

    # Create the visual layer (area/line)
    visual_layer = {"mark": deepcopy(mark)}

    # Create the point layer for hover/tooltip
    point_layer = {
        "params": [HOVER_PARAMS],
        "mark": {
            "type": "point",
            "filled": True,
            "color": primary_color,
            "size": 100
        },
        "encoding": {
            "opacity": {
                "condition": {
                    "param": "hover",
                    "empty": False,
                    "value": 1
                },
                "value": 0
            }
        }
    }

    # Add tooltip to point layer if it existed
    if tooltip:
        point_layer["encoding"]["tooltip"] = tooltip

    # Build the new layered structure
    new_chart = {
        "$schema": chart.get("$schema", "https://vega.github.io/schema/vega-lite/v5.json"),
    }

    # Copy description if present
    if "description" in chart:
        new_chart["description"] = chart["description"]

    # Copy data
    if "data" in chart:
        new_chart["data"] = chart["data"]

    # Copy transform if present
    if "transform" in chart:
        new_chart["transform"] = chart["transform"]

    # Keep encoding at top level (shared between layers)
    # But remove tooltip since it's now in the point layer
    new_chart["encoding"] = encoding

    # Add layers
    new_chart["layer"] = [visual_layer, point_layer]

    # Copy config
    if "config" in chart:
        new_chart["config"] = chart["config"]

    return new_chart


def process_file(filepath: Path, dry_run: bool = False) -> tuple[bool, str, bool]:
    """Process a single chart file. Returns (success, message, was_changed)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            chart = json.load(f)

        if is_layered(chart):
            return True, f"SKIP (already layered): {filepath.name}", False

        if is_bar_chart(chart):
            return True, f"SKIP (bar chart): {filepath.name}", False

        converted = convert_to_layered(chart)

        if dry_run:
            return True, f"WOULD CONVERT: {filepath.name}", True

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(converted, f, indent=2, ensure_ascii=False)
            f.write('\n')

        return True, f"CONVERTED: {filepath.name}", True

    except Exception as e:
        return False, f"ERROR {filepath.name}: {e}", False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Convert simple charts to layered structure")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--chart-dir", type=str,
                        default="/Users/ritz/Insync/robert@aum.edu.mn/Google Drive/data/data.mn/public/charts",
                        help="Directory containing chart JSON files")
    parser.add_argument("--file", type=str, help="Process single file instead of directory")
    args = parser.parse_args()

    if args.file:
        filepath = Path(args.file)
        success, message, changed = process_file(filepath, dry_run=args.dry_run)
        print(message)
        return 0 if success else 1

    chart_dir = Path(args.chart_dir)
    if not chart_dir.exists():
        print(f"Error: Chart directory not found: {chart_dir}")
        return 1

    chart_files = sorted(chart_dir.glob("*.json"))
    print(f"Processing {len(chart_files)} chart files...\n")

    converted = 0
    skipped = 0
    errors = 0

    for filepath in chart_files:
        success, message, changed = process_file(filepath, dry_run=args.dry_run)
        print(message)

        if not success:
            errors += 1
        elif changed:
            converted += 1
        else:
            skipped += 1

    print(f"\n{'Dry run complete' if args.dry_run else 'Processing complete'}:")
    print(f"  {'Would convert' if args.dry_run else 'Converted'}: {converted}")
    print(f"  Skipped (already layered/bar): {skipped}")
    if errors:
        print(f"  Errors: {errors}")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    exit(main())
