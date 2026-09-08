#!/usr/bin/env python3
"""
Vega-Lite Chart Validator

Validates Vega-Lite chart specifications against data visualization best practices
and ensures they will render correctly.

Usage:
    python validate_vega.py /path/to/chart.json
    python validate_vega.py /path/to/chart.json --data /path/to/data.csv
    python validate_vega.py --all  # Validate all charts in public/charts/
"""

import json
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import csv
from datetime import datetime

# Colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.suggestions: List[str] = []
        self.info: List[str] = []

    def add_error(self, msg: str):
        self.errors.append(msg)

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def add_suggestion(self, msg: str):
        self.suggestions.append(msg)

    def add_info(self, msg: str):
        self.info.append(msg)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def print_report(self, chart_name: str = "Chart"):
        print(f"\n{Colors.BOLD}═══ {chart_name} ═══{Colors.RESET}")

        if self.errors:
            print(f"\n{Colors.RED}✗ ERRORS ({len(self.errors)}):{Colors.RESET}")
            for err in self.errors:
                print(f"  • {err}")

        if self.warnings:
            print(f"\n{Colors.YELLOW}⚠ WARNINGS ({len(self.warnings)}):{Colors.RESET}")
            for warn in self.warnings:
                print(f"  • {warn}")

        if self.suggestions:
            print(f"\n{Colors.BLUE}💡 SUGGESTIONS ({len(self.suggestions)}):{Colors.RESET}")
            for sug in self.suggestions:
                print(f"  • {sug}")

        if self.info:
            print(f"\n{Colors.GREEN}ℹ INFO:{Colors.RESET}")
            for info in self.info:
                print(f"  • {info}")

        if self.is_valid and not self.warnings:
            print(f"\n{Colors.GREEN}✓ Chart is valid!{Colors.RESET}")
        elif self.is_valid:
            print(f"\n{Colors.YELLOW}✓ Chart is valid but has warnings{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}✗ Chart has errors that must be fixed{Colors.RESET}")


class VegaValidator:
    """Validates Vega-Lite specifications"""

    VALID_MARK_TYPES = ['line', 'bar', 'area', 'point', 'circle', 'square', 'rect',
                        'rule', 'text', 'tick', 'geoshape', 'arc', 'boxplot']

    VALID_DATA_TYPES = ['quantitative', 'temporal', 'ordinal', 'nominal', 'geojson']

    # Chart colors: Use Vega-Lite defaults (tableau10 scheme)
    # We no longer enforce brand colors on charts - let Vega handle it
    # The UI uses brand colors but charts use standard Vega defaults for consistency

    # Semantic colors for specific data types (optional overrides)
    # These are suggestions, not requirements - charts can use Vega defaults
    SEMANTIC_COLORS = {
        'male': '#4c78a8',      # Vega default blue (tableau10 first color)
        'female': '#f58518',    # Vega default orange (tableau10 second color)
        'urban': '#4c78a8',
        'rural': '#e45756',     # Vega default red
        'positive': '#54a24b',  # Vega default green
        'negative': '#e45756',  # Vega default red
    }

    # Required typography configuration
    BRAND_CONFIG = {
        'axis': {
            'labelFontSize': 14,
            'titleFontSize': 16,
            'labelColor': '#64748b',
            'titleColor': '#334155',
        },
        'legend': {
            'labelFontSize': 13,
            'titleFontSize': 14,
        },
    }

    # English terms that should be translated in MN charts
    ENGLISH_AXIS_TERMS = ['Year', 'Value', 'Rate', 'Percent', 'Population', 'Count',
                          'Category', 'Sex', 'Region', 'Age', 'Total', 'GDP', 'Amount']

    # Translation reference for MN charts
    MONGOLIAN_TRANSLATIONS = {
        'Year': 'Он',
        'Value': 'Утга',
        'Rate (%)': 'Түвшин (%)',
        'Rate': 'Түвшин',
        'Percent': 'Хувь',
        'Population': 'Хүн ам',
        'Count': 'Тоо',
        'Category': 'Ангилал',
        'Sex': 'Хүйс',
        'Male': 'Эрэгтэй',
        'Female': 'Эмэгтэй',
        'Region': 'Бүс',
        'Urban': 'Хот',
        'Rural': 'Хөдөө',
        'Age': 'Нас',
        'Total': 'Нийт',
        'GDP': 'ДНБ',
        'Amount': 'Дүн',
    }

    def __init__(self, spec: Dict, data_path: Optional[Path] = None, spec_path: Optional[Path] = None):
        self.spec = spec
        self.data_path = data_path
        self.spec_path = spec_path
        self.data: Optional[List[Dict]] = None
        self.result = ValidationResult()

        # Detect if this is a Mongolian chart (for translation validation)
        self.is_mongolian = False
        if spec_path:
            self.is_mongolian = str(spec_path).endswith('-mn.json')

        if data_path and data_path.exists():
            self._load_data()

    def _load_data(self):
        """Load CSV data for validation"""
        try:
            with open(self.data_path, 'r') as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
            self.result.add_info(f"Loaded {len(self.data)} rows from {self.data_path.name}")
        except Exception as e:
            self.result.add_warning(f"Could not load data file: {e}")

    def validate(self) -> ValidationResult:
        """Run all validations"""
        self._validate_schema()
        self._validate_structure()
        self._validate_data_source()
        self._validate_mark()
        self._validate_encoding()
        self._validate_config()
        self._validate_number_formats()
        self._validate_year_formats()
        self._validate_best_practices()
        self._validate_brand_compliance()

        if self.is_mongolian:
            self._validate_mongolian_translation()

        if self.data:
            self._validate_against_data()

        return self.result

    def _validate_number_formats(self):
        """Reject explicit formats that bypass the site's decimal default."""
        def walk(value, path='spec'):
            if isinstance(value, dict):
                for key, child in value.items():
                    child_path = f"{path}.{key}"
                    if key == 'format' and isinstance(child, str):
                        # D3/Vega exponential format types end in e/E. Time
                        # formats (for example %Y) and SI formats (.2s) are OK.
                        if child.lower().endswith('e') and '%' not in child:
                            self.result.add_error(
                                f"{child_path} uses scientific notation ({child!r}); "
                                "use ',' or a fixed-point format instead"
                            )
                    walk(child, child_path)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, f"{path}[{index}]")

        walk(self.spec)

    def _validate_year_formats(self):
        """Integer years must use format 'd', else tooltips render '2,024'."""
        def walk(value, path='spec'):
            if isinstance(value, dict):
                if 'tooltip' in value and isinstance(value['tooltip'], list):
                    for index, entry in enumerate(value['tooltip']):
                        if not isinstance(entry, dict):
                            continue
                        if entry.get('field') not in ('year', 'Year', 'он', 'Он'):
                            continue
                        if entry.get('type', 'quantitative') != 'quantitative':
                            continue
                        if 'timeUnit' in entry:
                            continue
                        if entry.get('format') != 'd':
                            self.result.add_error(
                                f"{path}.tooltip[{index}] year field without "
                                "format 'd' renders comma years ('2,024')"
                            )
                for key, child in value.items():
                    walk(child, f"{path}.{key}")
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, f"{path}[{index}]")

        walk(self.spec)

    def _validate_schema(self):
        """Check $schema is present and valid"""
        schema = self.spec.get('$schema', '')
        if not schema:
            self.result.add_error("Missing $schema - add: \"$schema\": \"https://vega.github.io/schema/vega-lite/v5.json\"")
        elif 'vega-lite' not in schema:
            self.result.add_warning(f"Unexpected schema: {schema}")
        elif 'v5' not in schema:
            self.result.add_suggestion("Consider upgrading to Vega-Lite v5 for latest features")

    def _validate_structure(self):
        """Check basic structure"""
        if 'data' not in self.spec:
            self.result.add_error("Missing 'data' property")

        # Check for mark or layer (layered specs don't have top-level mark)
        has_mark = 'mark' in self.spec
        has_layer = 'layer' in self.spec

        if not has_mark and not has_layer:
            self.result.add_error("Missing 'mark' property")

        # For single-view specs, encoding is required
        # For layered specs, each layer has its own encoding
        if not has_layer and 'encoding' not in self.spec:
            self.result.add_error("Missing 'encoding' property")

        # Check for width/height (should NOT be set for responsive charts)
        if 'width' in self.spec:
            self.result.add_warning("'width' is set - chart may not be responsive. Remove for auto-sizing.")
        if 'height' in self.spec:
            self.result.add_warning("'height' is set - chart may not be responsive. Remove for auto-sizing.")

    def _validate_data_source(self):
        """Validate data source configuration"""
        data = self.spec.get('data', {})

        if 'url' in data:
            url = data['url']
            if not url.startswith(('/datasets/', '/maps/')):
                self.result.add_warning(f"Data URL '{url}' should start with '/datasets/' (or '/maps/' for boundary files)")

            if 'format' not in data:
                self.result.add_warning("Missing 'format' in data - add: \"format\": {\"type\": \"csv\"}")
        elif 'values' in data:
            self.result.add_info("Using inline data values")
        else:
            self.result.add_error("Data source must have 'url' or 'values'")

    def _validate_mark(self):
        """Validate mark configuration"""
        # Handle layered specs
        if 'layer' in self.spec:
            for i, layer in enumerate(self.spec['layer']):
                if 'mark' in layer:
                    self._validate_single_mark(layer['mark'], f"layer {i}")
            return

        # Handle single-view specs
        if 'mark' in self.spec:
            self._validate_single_mark(self.spec['mark'])

    def _validate_single_mark(self, mark, context=""):
        """Validate a single mark configuration"""
        prefix = f"{context}: " if context else ""

        if isinstance(mark, str):
            mark_type = mark
        else:
            mark_type = mark.get('type', '')

        if mark_type not in self.VALID_MARK_TYPES:
            self.result.add_error(f"{prefix}Invalid mark type: '{mark_type}'. Valid types: {self.VALID_MARK_TYPES}")

        # Check for tooltip (mark-level or encoding-level both count)
        if isinstance(mark, dict):
            has_encoding_tooltip = 'tooltip' in self.spec.get('encoding', {})
            if not mark.get('tooltip') and not has_encoding_tooltip:
                self.result.add_suggestion(f"{prefix}Consider adding \"tooltip\": true for interactivity")

    def _validate_encoding(self):
        """Validate encoding channels"""
        encoding = self.spec.get('encoding', {})

        if not encoding:
            self.result.add_error("Encoding is empty")
            return

        # Check x and y axes
        for axis in ['x', 'y']:
            if axis in encoding:
                self._validate_axis_encoding(axis, encoding[axis])

        # Check color encoding
        if 'color' in encoding:
            self._validate_color_encoding(encoding['color'])

    def _validate_axis_encoding(self, axis: str, enc: Dict):
        """Validate axis encoding"""
        if 'field' not in enc and 'value' not in enc:
            self.result.add_error(f"{axis}-axis encoding missing 'field'")
            return

        field = enc.get('field', '')
        dtype = enc.get('type', '')

        if not dtype:
            self.result.add_warning(f"{axis}-axis missing 'type' - explicitly set to avoid inference issues")
        elif dtype not in self.VALID_DATA_TYPES:
            self.result.add_error(f"Invalid type for {axis}-axis: '{dtype}'")

        # Check for title
        if 'title' not in enc:
            self.result.add_suggestion(f"Add 'title' to {axis}-axis for clarity")

        # Check scale configuration
        scale = enc.get('scale', {})
        if dtype == 'quantitative':
            self._validate_quantitative_scale(axis, scale, field)

        # TIME SERIES SPECIFIC: Check for ordinal years (common mistake)
        if field.lower() in ['year', 'date', 'time', 'month', 'day']:
            if dtype == 'ordinal':
                self.result.add_error(
                    f"{axis}-axis: Field '{field}' is temporal data but uses 'ordinal' type. "
                    f"This causes uneven spacing (e.g., 1956→1963 looks same as 1989→1990). "
                    f"Use 'temporal' or 'quantitative' instead."
                )

    def _validate_quantitative_scale(self, axis: str, scale: Dict, field: str):
        """Validate quantitative axis scale settings"""
        zero = scale.get('zero')

        # Check if zero is explicitly set to false
        if zero is False:
            # This can be okay for some charts but should be justified
            self.result.add_warning(
                f"{axis}-axis has scale.zero=false. This can exaggerate differences. "
                f"Consider using zero=true for absolute comparisons unless intentionally showing trends."
            )

        # For fields that typically should start at zero
        absolute_fields = ['population', 'count', 'total', 'amount', 'value', 'number', 'sum']
        if any(af in field.lower() for af in absolute_fields):
            if zero is False:
                self.result.add_warning(
                    f"'{field}' represents an absolute count but scale.zero=false. "
                    f"This can mislead viewers about magnitude. Consider scale.zero=true."
                )

    def _validate_color_encoding(self, color: Dict):
        """Validate color encoding"""
        if 'value' in color:
            # Single color
            value = color['value']
            if not value.startswith('#'):
                self.result.add_warning(f"Color '{value}' should be hex format (e.g., #4c78a8)")
        # Note: We no longer suggest adding explicit color scales - Vega defaults are preferred

    def _validate_config(self):
        """Validate config section"""
        config = self.spec.get('config', {})

        if not config:
            self.result.add_suggestion("Add 'config' section for consistent styling")
            return

        axis_config = config.get('axis', {})
        if not axis_config.get('labelFontSize'):
            self.result.add_suggestion("Set axis.labelFontSize in config (recommended: 12)")
        if not axis_config.get('titleFontSize'):
            self.result.add_suggestion("Set axis.titleFontSize in config (recommended: 14)")

    def _validate_best_practices(self):
        """Check data visualization best practices"""
        mark = self.spec.get('mark', {})
        mark_type = mark if isinstance(mark, str) else mark.get('type', '')
        encoding = self.spec.get('encoding', {})

        # Line charts should have points for sparse data
        if mark_type == 'line':
            if isinstance(mark, dict) and not mark.get('point'):
                self.result.add_suggestion("Consider adding \"point\": true for line charts to show data points")

        # Bar charts should typically start at zero
        if mark_type == 'bar':
            y_enc = encoding.get('y', {})
            scale = y_enc.get('scale', {})
            if scale.get('zero') is False:
                self.result.add_error(
                    "Bar charts MUST start at zero (scale.zero=true or omit). "
                    "Truncated bar charts are misleading."
                )

        # Check for proper number formatting
        for axis in ['x', 'y']:
            if axis in encoding:
                enc = encoding[axis]
                if enc.get('type') == 'quantitative':
                    axis_config = enc.get('axis', {})
                    if 'format' not in axis_config:
                        self.result.add_suggestion(
                            f"Add number format to {axis}-axis (e.g., \".2s\" for SI units, \",\" for thousands separator)"
                        )

    def _validate_brand_compliance(self):
        """
        Validate chart follows data.mn brand guidelines.

        Checks:
        - Layered structure for line/area charts (for hover interactivity)
        - Primary color #2563eb for single-series
        - Categorical color palette from brand colors
        - Semantic colors for male/female, urban/rural
        - Gradient fill for area marks
        - Typography configuration (font sizes, colors)
        """
        has_layer = 'layer' in self.spec
        mark = self.spec.get('mark', {})
        mark_type = mark if isinstance(mark, str) else mark.get('type', '')
        config = self.spec.get('config', {})

        # === Check 21: Layered structure for line/area charts ===
        # Line and area charts MUST use layer structure for hover points
        if mark_type in ['line', 'area'] and not has_layer:
            self.result.add_error(
                f"'{mark_type}' chart must use layered structure for hover interactivity. "
                f"Use 'layer' array with area/line mark + point mark for hover effect. "
                f"See gdp-nominal-en.json for reference template."
            )

        # === Check 21b: Validate hover point pattern for layered charts ===
        if has_layer:
            self._validate_hover_point_pattern()

        # === Check 24: Color validation (relaxed - allow Vega defaults) ===
        # Charts now use Vega-Lite default colors (tableau10 scheme)
        # We no longer enforce brand colors - just log what colors are used
        colors_found = self._extract_all_colors()
        if colors_found:
            self.result.add_info(f"Colors used: {colors_found}")

        # === Check 27: Gradient fill for area marks (now optional) ===
        # Gradients are nice but not required - Vega defaults work well too
        # Just log if area marks are present
        if has_layer:
            for i, layer in enumerate(self.spec.get('layer', [])):
                layer_mark = layer.get('mark', {})
                if isinstance(layer_mark, dict) and layer_mark.get('type') == 'area':
                    color = layer_mark.get('color', {})
                    if isinstance(color, dict) and 'gradient' in color:
                        self.result.add_info(f"layer[{i}]: Using gradient fill (optional)")

        # === Check 25: Categorical palette for multi-series (now uses Vega defaults) ===
        # Multi-series charts will automatically use Vega's tableau10 scheme
        # No need to specify explicit colors - just log for info
        encoding = self.spec.get('encoding', {})
        color_enc = encoding.get('color', {})
        if isinstance(color_enc, dict) and 'field' in color_enc:
            scale = color_enc.get('scale', {})
            if 'range' in scale or 'scheme' in scale:
                self.result.add_info(f"Multi-series chart using custom color scale")
            else:
                self.result.add_info(f"Multi-series chart using Vega default colors (category10)")

            # === Check 25b: Legend must be at top for full-width charts ===
            legend = color_enc.get('legend', {})
            if legend is None:
                pass  # Legend explicitly disabled, that's fine
            elif isinstance(legend, dict):
                orient = legend.get('orient', 'right')  # Vega default is 'right'
                if orient != 'top':
                    self.result.add_error(
                        f"Legend orient should be 'top' for full-width charts, found: '{orient}'. "
                        f"Add \"legend\": {{\"orient\": \"top\"}} to color encoding."
                    )
            else:
                # legend: true or other truthy value without orient
                self.result.add_error(
                    "Legend must have orient: 'top' for full-width charts. "
                    "Add \"legend\": {\"orient\": \"top\"} to color encoding."
                )

        # === Check 26: Semantic colors for sex/location data ===
        self._check_semantic_colors(color_enc)

        # === Checks 28-32: Typography configuration ===
        self._validate_typography_config(config)

    def _extract_all_colors(self) -> List[str]:
        """Extract all color values from the spec"""
        colors = []

        def extract_from_dict(d: Dict):
            for key, value in d.items():
                if key == 'color':
                    if isinstance(value, str):
                        colors.append(value)
                    elif isinstance(value, dict):
                        # Check for gradient stops
                        if 'stops' in value:
                            # Skip gradient definitions - they're rgba which is fine
                            pass
                        elif 'value' in value:
                            colors.append(value['value'])
                elif isinstance(value, dict):
                    extract_from_dict(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            extract_from_dict(item)

        extract_from_dict(self.spec)
        return colors

    def _check_semantic_colors(self, color_enc: Dict):
        """Check semantic colors for sex/location data (informational only)"""
        if not isinstance(color_enc, dict) or 'field' not in color_enc:
            return

        field = color_enc.get('field', '').lower()
        scale = color_enc.get('scale', {})

        # Just log if sex/location data is being used - no longer enforce colors
        # Vega defaults will apply appropriate colors automatically
        if field in ['sex', 'gender', 'хүйс']:
            if 'range' in scale:
                self.result.add_info("Sex/gender chart using custom colors")
            else:
                self.result.add_info("Sex/gender chart using Vega default colors")

        if field in ['location', 'type', 'байршил']:
            if 'range' in scale:
                self.result.add_info("Location chart using custom colors")
            else:
                self.result.add_info("Location chart using Vega default colors")

    def _validate_typography_config(self, config: Dict):
        """Validate typography follows brand guidelines"""
        axis_config = config.get('axis', {})
        legend_config = config.get('legend', {})

        # === Check 28: axis.labelFontSize must be 14 ===
        label_size = axis_config.get('labelFontSize')
        if label_size != self.BRAND_CONFIG['axis']['labelFontSize']:
            self.result.add_error(
                f"config.axis.labelFontSize must be {self.BRAND_CONFIG['axis']['labelFontSize']}, "
                f"found: {label_size}"
            )

        # === Check 29: axis.titleFontSize must be 16 ===
        title_size = axis_config.get('titleFontSize')
        if title_size != self.BRAND_CONFIG['axis']['titleFontSize']:
            self.result.add_error(
                f"config.axis.titleFontSize must be {self.BRAND_CONFIG['axis']['titleFontSize']}, "
                f"found: {title_size}"
            )

        # === Check 30: axis.labelColor must be #64748b ===
        label_color = axis_config.get('labelColor')
        if label_color != self.BRAND_CONFIG['axis']['labelColor']:
            self.result.add_error(
                f"config.axis.labelColor must be {self.BRAND_CONFIG['axis']['labelColor']}, "
                f"found: {label_color}"
            )

        # === Check 31: axis.titleColor must be #334155 ===
        title_color = axis_config.get('titleColor')
        if title_color != self.BRAND_CONFIG['axis']['titleColor']:
            self.result.add_error(
                f"config.axis.titleColor must be {self.BRAND_CONFIG['axis']['titleColor']}, "
                f"found: {title_color}"
            )

        # === Check 32: legend font sizes ===
        legend_label_size = legend_config.get('labelFontSize')
        if legend_label_size is not None and legend_label_size != self.BRAND_CONFIG['legend']['labelFontSize']:
            self.result.add_error(
                f"config.legend.labelFontSize must be {self.BRAND_CONFIG['legend']['labelFontSize']}, "
                f"found: {legend_label_size}"
            )

        legend_title_size = legend_config.get('titleFontSize')
        if legend_title_size is not None and legend_title_size != self.BRAND_CONFIG['legend']['titleFontSize']:
            self.result.add_error(
                f"config.legend.titleFontSize must be {self.BRAND_CONFIG['legend']['titleFontSize']}, "
                f"found: {legend_title_size}"
            )

    def _validate_hover_point_pattern(self):
        """
        Validate that layered charts have proper hover point interactivity.

        Required pattern for line/area charts:
        - Layer with main mark (line/area)
        - Layer with point mark that has:
          - params with hover selection (nearest: true, on: pointerover, clear: pointerout)
          - opacity condition (value: 1 when hover, value: 0 otherwise)
          - tooltip array with field definitions

        This creates the "nearest point" tooltip effect where hovering anywhere
        on the chart highlights and shows tooltip for the closest data point.
        """
        layers = self.spec.get('layer', [])

        if not layers:
            return

        # Check if this is a line/area chart that needs hover points
        main_mark_types = []
        point_layer_index = None

        for i, layer in enumerate(layers):
            layer_mark = layer.get('mark', {})
            if isinstance(layer_mark, str):
                mark_type = layer_mark
            else:
                mark_type = layer_mark.get('type', '')

            main_mark_types.append(mark_type)

            if mark_type == 'point':
                point_layer_index = i

        # Only validate if this is a line/area chart
        needs_hover = any(m in ['line', 'area'] for m in main_mark_types)
        if not needs_hover:
            return

        # Check for point layer
        if point_layer_index is None:
            self.result.add_error(
                "Layered line/area chart missing point layer for hover interactivity. "
                "Add a layer with mark type 'point' for hover tooltips."
            )
            return

        point_layer = layers[point_layer_index]
        point_mark = point_layer.get('mark', {})
        point_encoding = point_layer.get('encoding', {})
        point_params = point_layer.get('params', [])

        # === Check point mark configuration ===
        if isinstance(point_mark, dict):
            if not point_mark.get('filled'):
                self.result.add_warning(
                    f"Point layer mark should have 'filled': true for visibility"
                )
            if not point_mark.get('size'):
                self.result.add_suggestion(
                    f"Consider adding 'size': 100 to point mark for better hover target"
                )

        # === Check for hover params ===
        hover_param = None
        for param in point_params:
            if isinstance(param, dict):
                param_name = param.get('name', '')
                if param_name == 'hover' or 'select' in param:
                    hover_param = param
                    break

        if not hover_param:
            self.result.add_error(
                "Point layer missing hover params. Add:\n"
                "  \"params\": [{\"name\": \"hover\", \"select\": {...}}]"
            )
        else:
            # Validate hover select configuration
            select = hover_param.get('select', {})
            if isinstance(select, dict):
                # Check for nearest: true
                if not select.get('nearest'):
                    self.result.add_error(
                        "Hover selection should use 'nearest': true for best UX. "
                        "This shows tooltip for closest point when hovering anywhere on chart."
                    )

                # Check for type: point
                select_type = select.get('type', '')
                if select_type != 'point':
                    self.result.add_warning(
                        f"Hover selection type should be 'point', found: '{select_type}'"
                    )

                # Check for pointerover/pointerout events
                on_event = select.get('on', '')
                clear_event = select.get('clear', '')
                if 'pointerover' not in str(on_event):
                    self.result.add_warning(
                        "Hover selection should use 'on': 'pointerover' for mouse hover"
                    )
                if 'pointerout' not in str(clear_event):
                    self.result.add_warning(
                        "Hover selection should use 'clear': 'pointerout' to hide on mouse leave"
                    )

        # === Check for opacity condition ===
        opacity_enc = point_encoding.get('opacity', {})
        if not opacity_enc:
            self.result.add_error(
                "Point layer missing opacity encoding. Points should be hidden by default "
                "and shown on hover. Add opacity with condition."
            )
        else:
            condition = opacity_enc.get('condition', {})
            default_value = opacity_enc.get('value')

            if not condition:
                self.result.add_error(
                    "Point opacity missing condition. Should show on hover (value: 1), "
                    "hide otherwise (value: 0)."
                )
            elif isinstance(condition, dict):
                # Check condition references hover param
                cond_param = condition.get('param', '')
                if cond_param != 'hover':
                    self.result.add_warning(
                        f"Opacity condition should reference 'hover' param, found: '{cond_param}'"
                    )

                # Check condition value
                cond_value = condition.get('value')
                if cond_value != 1:
                    self.result.add_warning(
                        f"Opacity condition value should be 1 (visible), found: {cond_value}"
                    )

                # Check empty: false for proper hover behavior
                if condition.get('empty') is not False:
                    self.result.add_warning(
                        "Opacity condition should have 'empty': false to hide points when not hovering"
                    )

            # Check default opacity is 0 (hidden)
            if default_value != 0:
                self.result.add_warning(
                    f"Point default opacity should be 0 (hidden), found: {default_value}"
                )

        # === Check for tooltip ===
        tooltip_enc = point_encoding.get('tooltip', [])
        if not tooltip_enc:
            self.result.add_error(
                "Point layer missing tooltip encoding. Add tooltip array with field definitions."
            )
        elif isinstance(tooltip_enc, list):
            if len(tooltip_enc) == 0:
                self.result.add_error("Tooltip array is empty. Add field definitions.")
            else:
                # Check tooltip entries have required fields
                for i, tip in enumerate(tooltip_enc):
                    if isinstance(tip, dict):
                        if 'field' not in tip:
                            self.result.add_warning(f"Tooltip[{i}] missing 'field'")
                        if 'type' not in tip:
                            self.result.add_warning(f"Tooltip[{i}] missing 'type'")
                        # Title is optional but recommended
                        if 'title' not in tip:
                            self.result.add_suggestion(f"Tooltip[{i}] could have 'title' for clarity")

        self.result.add_info(
            f"Hover pattern validated: point layer at index {point_layer_index}"
        )

    def _validate_mongolian_translation(self):
        """
        Validate Mongolian chart has translated axis/legend/tooltip titles.

        Only runs for charts ending in -mn.json.
        """
        encoding = self.spec.get('encoding', {})

        # === Check 33: X-axis title should be "Он" not "Year" ===
        x_enc = encoding.get('x', {})
        x_title = x_enc.get('title', '')
        if x_title and x_title in self.ENGLISH_AXIS_TERMS:
            mn_translation = self.MONGOLIAN_TRANSLATIONS.get(x_title, '[unknown]')
            self.result.add_error(
                f"MN chart: X-axis title '{x_title}' is English. "
                f"Use Mongolian: '{mn_translation}'"
            )

        # Check Y-axis title
        y_enc = encoding.get('y', {})
        y_title = y_enc.get('title', '')
        if y_title:
            # Check if any English terms are in the title
            for eng_term in self.ENGLISH_AXIS_TERMS:
                if eng_term in y_title and eng_term in self.MONGOLIAN_TRANSLATIONS:
                    self.result.add_error(
                        f"MN chart: Y-axis title contains English term '{eng_term}'. "
                        f"Use Mongolian equivalent."
                    )
                    break

        # === Check 35: Legend title should be translated ===
        color_enc = encoding.get('color', {})
        if isinstance(color_enc, dict):
            legend = color_enc.get('legend', {})
            if isinstance(legend, dict):
                legend_title = legend.get('title', '')
                if legend_title and legend_title in self.ENGLISH_AXIS_TERMS:
                    mn_translation = self.MONGOLIAN_TRANSLATIONS.get(legend_title, '[unknown]')
                    self.result.add_error(
                        f"MN chart: Legend title '{legend_title}' is English. "
                        f"Use Mongolian: '{mn_translation}'"
                    )

        # Also check top-level legend in color scale
        if isinstance(color_enc, dict):
            scale = color_enc.get('scale', {})
            if isinstance(scale, dict):
                domain = scale.get('domain', [])
                # Check if domain values are English when they should be Mongolian
                for val in domain:
                    if isinstance(val, str) and val in self.MONGOLIAN_TRANSLATIONS:
                        self.result.add_error(
                            f"MN chart: Color domain value '{val}' is English. "
                            f"Use Mongolian: '{self.MONGOLIAN_TRANSLATIONS[val]}'"
                        )

        # === Check 36: Tooltip titles should be translated ===
        # Check for tooltips in layers
        if 'layer' in self.spec:
            for i, layer in enumerate(self.spec['layer']):
                layer_enc = layer.get('encoding', {})
                tooltips = layer_enc.get('tooltip', [])
                if isinstance(tooltips, list):
                    for j, tip in enumerate(tooltips):
                        if isinstance(tip, dict):
                            tip_title = tip.get('title', '')
                            if tip_title and tip_title in self.ENGLISH_AXIS_TERMS:
                                mn_translation = self.MONGOLIAN_TRANSLATIONS.get(tip_title, '[unknown]')
                                self.result.add_error(
                                    f"MN chart: Tooltip title '{tip_title}' is English. "
                                    f"Use Mongolian: '{mn_translation}'"
                                )

        # Check top-level tooltip encoding
        tooltip_enc = encoding.get('tooltip', [])
        if isinstance(tooltip_enc, list):
            for tip in tooltip_enc:
                if isinstance(tip, dict):
                    tip_title = tip.get('title', '')
                    if tip_title and tip_title in self.ENGLISH_AXIS_TERMS:
                        mn_translation = self.MONGOLIAN_TRANSLATIONS.get(tip_title, '[unknown]')
                        self.result.add_error(
                            f"MN chart: Tooltip title '{tip_title}' is English. "
                            f"Use Mongolian: '{mn_translation}'"
                        )

    def _validate_against_data(self):
        """Validate spec against actual data"""
        if not self.data:
            return

        encoding = self.spec.get('encoding', {})
        csv_fields = set(self.data[0].keys()) if self.data else set()

        # === NEW: Validate transform SOURCE fields exist in CSV ===
        # This catches bugs like referencing 'exports' when CSV has 'экспорт'
        transforms = self.spec.get('transform', [])
        transform_fields = set()  # Fields CREATED by transforms

        # First pass: collect all fields created by transforms (aggregate ops, calculate as, etc.)
        for transform in transforms:
            if 'aggregate' in transform:
                for agg_op in transform.get('aggregate', []):
                    if 'as' in agg_op:
                        transform_fields.add(agg_op['as'])
            if 'as' in transform:
                as_field = transform['as']
                if isinstance(as_field, list):
                    transform_fields.update(as_field)
                else:
                    transform_fields.add(as_field)

        for transform in transforms:
            # Check FOLD transform - source fields must exist in CSV or be created by transforms
            if 'fold' in transform:
                fold_fields = transform['fold']
                for field in fold_fields:
                    if field not in csv_fields and field not in transform_fields:
                        self.result.add_error(
                            f"Fold transform references field '{field}' which doesn't exist in CSV. "
                            f"Available columns: {sorted(csv_fields)}"
                        )

            # Check PIVOT transform - field must exist in CSV
            if 'pivot' in transform:
                pivot_field = transform['pivot']
                if pivot_field not in csv_fields:
                    self.result.add_error(
                        f"Pivot transform references field '{pivot_field}' which doesn't exist in CSV. "
                        f"Available columns: {sorted(csv_fields)}"
                    )

            # Check LOOKUP transform - from.fields must exist (if local data)
            if 'lookup' in transform:
                lookup_field = transform['lookup']
                if lookup_field not in csv_fields and lookup_field not in transform_fields:
                    self.result.add_warning(
                        f"Lookup transform references field '{lookup_field}' - verify it exists in data"
                    )

            # Check CALCULATE transform - validate field references in expression
            if 'calculate' in transform:
                expr = transform['calculate']
                # Check for datum.fieldName references
                datum_refs = re.findall(r'datum\.(\w+)', expr)
                for ref in datum_refs:
                    if ref not in csv_fields and ref not in transform_fields:
                        self.result.add_warning(
                            f"Calculate expression references 'datum.{ref}' - verify field exists"
                        )

            # Track fields CREATED by transforms (for downstream validation)
            if 'as' in transform:
                as_field = transform['as']
                if isinstance(as_field, list):
                    transform_fields.update(as_field)
                else:
                    transform_fields.add(as_field)

        # Check that encoded fields exist in data or are created by transforms
        for channel, enc in encoding.items():
            if isinstance(enc, dict) and 'field' in enc:
                field = enc['field']
                if field not in csv_fields and field not in transform_fields:
                    self.result.add_error(f"Field '{field}' in {channel} encoding not found in data or transforms")

        # Check for time series gaps
        x_enc = encoding.get('x', {})
        x_field = x_enc.get('field', '')

        if x_field.lower() in ['year', 'date']:
            self._check_time_gaps(x_field)

    def _check_time_gaps(self, field: str):
        """Check for gaps in time series data"""
        if not self.data:
            return

        try:
            years = sorted(set(int(row[field]) for row in self.data if row.get(field)))
        except (ValueError, TypeError):
            return

        if len(years) < 2:
            return

        gaps = []
        for i in range(1, len(years)):
            gap = years[i] - years[i-1]
            if gap > 1:
                gaps.append((years[i-1], years[i], gap))

        if gaps:
            gap_str = ", ".join(f"{a}→{b} ({g}yr)" for a, b, g in gaps[:5])
            self.result.add_warning(
                f"Time series has gaps: {gap_str}. "
                f"Consider: 1) Using temporal/quantitative x-axis to show true spacing, "
                f"2) Interpolating missing years, or 3) Adding annotation about missing data."
            )

            # Check if using ordinal (which hides gaps)
            x_enc = self.spec.get('encoding', {}).get('x', {})
            if x_enc.get('type') == 'ordinal':
                self.result.add_error(
                    "Using 'ordinal' type with gapped time data is MISLEADING. "
                    "Gaps are hidden because ordinal treats each value as equally spaced. "
                    "Use 'temporal' or 'quantitative' type instead."
                )


def validate_chart(spec_path: Path, data_path: Optional[Path] = None) -> ValidationResult:
    """Validate a single chart specification"""
    try:
        with open(spec_path, 'r') as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        result = ValidationResult()
        result.add_error(f"Invalid JSON: {e}")
        return result
    except FileNotFoundError:
        result = ValidationResult()
        result.add_error(f"File not found: {spec_path}")
        return result

    # Try to find data file if not specified
    if not data_path:
        data = spec.get('data', {})
        if 'url' in data:
            url = data['url']
            # Try to resolve relative to public/
            potential_path = spec_path.parent.parent / url.lstrip('/')
            if potential_path.exists():
                data_path = potential_path

    validator = VegaValidator(spec, data_path, spec_path)
    return validator.validate()


def find_all_charts(base_path: Path) -> List[Path]:
    """Find all Vega-Lite chart specs"""
    charts_dir = base_path / 'public' / 'charts'
    if not charts_dir.exists():
        # Try relative paths
        for candidate in [Path('public/charts'), Path('data.mn/public/charts')]:
            if candidate.exists():
                charts_dir = candidate
                break

    if not charts_dir.exists():
        return []

    return list(charts_dir.glob('*.json'))


def main():
    parser = argparse.ArgumentParser(description='Validate Vega-Lite chart specifications')
    parser.add_argument('chart', nargs='?', help='Path to chart JSON file')
    parser.add_argument('--data', '-d', help='Path to data CSV file')
    parser.add_argument('--all', '-a', action='store_true', help='Validate all charts in public/charts/')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only show errors')

    args = parser.parse_args()

    if args.all:
        # Find and validate all charts
        base_path = Path('.')
        charts = find_all_charts(base_path)

        if not charts:
            print("No charts found in public/charts/")
            return 1

        print(f"\n{Colors.BOLD}Validating {len(charts)} charts...{Colors.RESET}")

        all_valid = True
        for chart_path in sorted(charts):
            result = validate_chart(chart_path)
            if not result.is_valid or not args.quiet:
                result.print_report(chart_path.name)
            if not result.is_valid:
                all_valid = False

        print(f"\n{Colors.BOLD}{'═' * 40}{Colors.RESET}")
        if all_valid:
            print(f"{Colors.GREEN}All charts valid!{Colors.RESET}")
            return 0
        else:
            print(f"{Colors.RED}Some charts have errors{Colors.RESET}")
            return 1

    elif args.chart:
        chart_path = Path(args.chart)
        data_path = Path(args.data) if args.data else None

        result = validate_chart(chart_path, data_path)
        result.print_report(chart_path.name)

        return 0 if result.is_valid else 1

    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
