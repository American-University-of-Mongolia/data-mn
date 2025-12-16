#!/usr/bin/env python3
"""
Update all Vega-Lite chart configurations with:
1. Nearest-point hover for better tooltip experience
2. Increased font sizes for better readability

This script handles multiple chart structures:
- Simple (non-layered) charts: Adds hover params at top level
- Layered charts: Updates hover params in point layer
- Bar charts: Updates existing hover params to add nearest: true
"""

import json
import os
from pathlib import Path
from typing import Any

# New config with increased font sizes
NEW_CONFIG = {
    "axis": {
        "labelFontSize": 14,
        "titleFontSize": 16,
        "labelColor": "#64748b",
        "titleColor": "#334155"
    },
    "legend": {
        "labelFontSize": 13,
        "titleFontSize": 14
    },
    "view": {
        "stroke": "transparent"
    }
}

# Hover params with nearest: true for better UX
HOVER_PARAMS = {
    "name": "hover",
    "select": {
        "type": "point",
        "nearest": True,
        "on": "pointerover",
        "clear": "pointerout"
    }
}


def update_config(chart: dict) -> dict:
    """Update the config section with new font sizes."""
    if "config" not in chart:
        chart["config"] = {}

    config = chart["config"]

    # Update axis config
    if "axis" not in config:
        config["axis"] = {}
    config["axis"]["labelFontSize"] = NEW_CONFIG["axis"]["labelFontSize"]
    config["axis"]["titleFontSize"] = NEW_CONFIG["axis"]["titleFontSize"]
    config["axis"]["labelColor"] = NEW_CONFIG["axis"]["labelColor"]
    config["axis"]["titleColor"] = NEW_CONFIG["axis"]["titleColor"]

    # Add/update legend config
    if "legend" not in config:
        config["legend"] = {}
    config["legend"]["labelFontSize"] = NEW_CONFIG["legend"]["labelFontSize"]
    config["legend"]["titleFontSize"] = NEW_CONFIG["legend"]["titleFontSize"]

    # Ensure view stroke is transparent
    if "view" not in config:
        config["view"] = {}
    config["view"]["stroke"] = "transparent"

    return chart


def update_hover_params(params: list) -> list:
    """Update hover params to include nearest: true."""
    for param in params:
        if param.get("name") == "hover":
            if "select" in param:
                param["select"]["nearest"] = True
            else:
                param["select"] = HOVER_PARAMS["select"]
            return params

    # No hover param found, add it
    params.append(HOVER_PARAMS.copy())
    return params


def is_bar_chart(chart: dict) -> bool:
    """Check if this is a bar chart (which uses hover differently)."""
    mark = chart.get("mark", {})
    if isinstance(mark, str):
        return mark == "bar"
    return mark.get("type") == "bar"


def is_layered_chart(chart: dict) -> bool:
    """Check if chart uses layer structure."""
    return "layer" in chart


def update_simple_chart(chart: dict) -> dict:
    """Update a simple (non-layered) chart with hover params."""
    # For bar charts, update existing params or add new ones
    if is_bar_chart(chart):
        if "params" not in chart:
            chart["params"] = []
        chart["params"] = update_hover_params(chart["params"])
    else:
        # For area/line charts, add params at top level
        if "params" not in chart:
            chart["params"] = [HOVER_PARAMS.copy()]
        else:
            chart["params"] = update_hover_params(chart["params"])

    return chart


def update_layered_chart(chart: dict) -> dict:
    """Update a layered chart's point layer with hover params."""
    for layer in chart.get("layer", []):
        # Find the point layer (used for tooltips)
        mark = layer.get("mark", {})
        mark_type = mark if isinstance(mark, str) else mark.get("type", "")

        if mark_type == "point":
            # Update params in this layer
            if "params" not in layer:
                layer["params"] = []
            layer["params"] = update_hover_params(layer["params"])

    return chart


def update_chart(chart: dict) -> dict:
    """Main function to update a chart with all improvements."""
    # Update config (font sizes)
    chart = update_config(chart)

    # Update hover params based on chart structure
    if is_layered_chart(chart):
        chart = update_layered_chart(chart)
    else:
        chart = update_simple_chart(chart)

    return chart


def process_file(filepath: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Process a single chart file. Returns (success, message)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            chart = json.load(f)

        updated_chart = update_chart(chart)

        if dry_run:
            return True, f"Would update: {filepath.name}"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(updated_chart, f, indent=2, ensure_ascii=False)
            f.write('\n')  # Add trailing newline

        return True, f"Updated: {filepath.name}"

    except json.JSONDecodeError as e:
        return False, f"JSON error in {filepath.name}: {e}"
    except Exception as e:
        return False, f"Error processing {filepath.name}: {e}"


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Update Vega-Lite chart configurations")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making changes")
    parser.add_argument("--chart-dir", type=str,
                        default="/Users/ritz/Insync/robert@aum.edu.mn/Google Drive/data/data.mn/public/charts",
                        help="Directory containing chart JSON files")
    args = parser.parse_args()

    chart_dir = Path(args.chart_dir)
    if not chart_dir.exists():
        print(f"Error: Chart directory not found: {chart_dir}")
        return 1

    chart_files = list(chart_dir.glob("*.json"))
    print(f"Found {len(chart_files)} chart files to process\n")

    success_count = 0
    error_count = 0

    for filepath in sorted(chart_files):
        success, message = process_file(filepath, dry_run=args.dry_run)
        print(message)
        if success:
            success_count += 1
        else:
            error_count += 1

    print(f"\n{'Dry run complete' if args.dry_run else 'Processing complete'}:")
    print(f"  ✓ {success_count} charts {'would be ' if args.dry_run else ''}updated")
    if error_count > 0:
        print(f"  ✗ {error_count} errors")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    exit(main())
