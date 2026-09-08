---
name: datamn-chart-vega
description: Create and validate Vega-Lite chart specifications for data.mn. Use when creating charts, visualizations, or data graphics. Includes templates for area charts, line charts, bar charts, population pyramids, and stacked areas with brand guidelines.
---

# Vega-Lite Charts Skill

Create consistent, branded Vega-Lite chart specifications for data.mn.

## CRITICAL: Visual QA Required

**ALWAYS export and review charts visually before finalizing:**

```bash
# Export chart to PNG for visual review (run from data.mn directory)
cd data/data.mn && npx vl2png public/charts/{chart-name}.json -b public/ -s 2 /tmp/{chart-name}.png
```

Then use the Read tool to view `/tmp/{chart-name}.png` and check:

### Visual QA Checklist
- [ ] **Line/area visibility**: Lines are thick enough to see clearly (strokeWidth >= 2)
- [ ] **Data point visibility**: Points are appropriately sized or omitted for dense data
- [ ] **Color contrast**: Chart elements stand out against the background
- [ ] **Label readability**: All text is legible, not overlapping
- [ ] **Proportions**: Chart fills the space well, not too sparse or cramped
- [ ] **Professional appearance**: Would this look good on Statista?

---

## CRITICAL: Library Versions

The VegaChart component uses these CDN libraries:

| Library | Version |
|---------|---------|
| Vega | 5.30.0 |
| Vega-Lite | 5.21.0 |
| Vega-Embed | 6.26.0 |

**DO NOT change these versions** without testing thoroughly.

## CRITICAL: Validation Required

**ALWAYS validate charts after creating them:**

```bash
cd data/tools && python3 scripts/validate_vega.py /path/to/chart.json --data /path/to/data.csv
```

Or validate all charts:
```bash
cd data/data.mn && python3 ../tools/scripts/validate_vega.py --all
```

Charts with errors MUST be fixed before committing.

## CRITICAL: Display Range vs Download Range

**The chart should show RELEVANT data, not necessarily ALL data.**

The CSV file can contain the full historical dataset for download, but the chart should filter to show a meaningful range for TODAY's viewer.

### Context-Aware Display Range Guidelines

Analyze the data characteristics and apply these rules:

| Data Characteristic | Display Range | Example |
|---------------------|---------------|---------|
| **Hyperinflation/extreme values** | Start AFTER normalization | Inflation: show 2000+ (not 1991+ when it was 325%) |
| **Transition economies** | Start after transition period | Mongolia: show 2000+ (post-Soviet transition) |
| **Consistent growth** | Show full range | Population: 1956-2024 is fine |
| **Recent phenomenon** | Show all available | COVID impact: 2019-2024 |
| **Cyclical data** | Show 2-3 complete cycles | Quarterly data: ~10 years |

### How to Filter in Vega-Lite

Use a `transform` to filter the display range:

```json
{
  "data": {"url": "/datasets/inflation-rate.csv"},
  "transform": [
    {"filter": "datum.year >= 2000"}
  ],
  "encoding": {...}
}
```

### Decision Process

Before creating a chart, ask:
1. **Does the historical data dwarf current values?** → Filter to relevant period
2. **Was there a regime change/transition?** → Start after the transition
3. **Is the full range meaningful for understanding current trends?** → Show all
4. **Would a viewer find the full range confusing?** → Filter

**Document your choice** in the chart's `description` field:
```json
{
  "description": "Mongolia inflation rate 2000-2024. Full data (1991-2024) available in CSV but chart excludes 1990s hyperinflation for clarity."
}
```

## Chart Colors

### Use D3 Category10 Color Scheme

**Charts use the D3 category10 color scheme** - brighter, more vibrant colors than the default tableau10. This is automatically applied by the VegaChart component.

**DO NOT specify explicit colors** unless you have a specific semantic reason. Simply omit color definitions and the component will apply category10.

The category10 palette:
| Index | Color | Hex | Use |
|-------|-------|-----|-----|
| 1 | Blue | `#1f77b4` | First series / single-series default |
| 2 | Orange | `#ff7f0e` | Second series |
| 3 | Green | `#2ca02c` | Third series |
| 4 | Red | `#d62728` | Fourth series |
| 5 | Purple | `#9467bd` | Fifth series |
| 6 | Brown | `#8c564b` | Sixth series |

### How Colors Are Applied

The VegaChart component applies colors in TWO ways:

1. **Multi-series charts** (with `color` encoding and a `field`):
   - Colors come from `config.range.category` (the category10 palette)
   - Each series gets the next color in the palette

2. **Single-series charts** (no `color` encoding, just one area/line/bar):
   - Default fill/stroke comes from `config.area.fill`, `config.line.stroke`, etc.
   - These are all set to **`#1f77b4`** (the first category10 blue)

**This means:** ALL charts - whether single or multi-series - will use the bright category10 colors automatically.

### Gradient Fills for Single-Series Area Charts

**Single-series area charts should use gradient fills** for a professional, lighter look:

```json
{
  "mark": {
    "type": "area",
    "line": {"stroke": "#1f77b4", "strokeWidth": 2},
    "color": {
      "x1": 1, "y1": 1,
      "x2": 1, "y2": 0,
      "gradient": "linear",
      "stops": [
        {"offset": 0, "color": "rgba(31, 119, 180, 0.02)"},
        {"offset": 1, "color": "rgba(31, 119, 180, 0.35)"}
      ]
    },
    "interpolate": "monotone"
  }
}
```

This creates a beautiful vertical fade from nearly transparent at the bottom to 35% opacity at the top, with a solid stroke line on top for visual definition.

**Note:** Multi-series charts (with color encoding) should NOT have explicit fill colors - they get colors from the category10 palette automatically.

**RULE: Maximum 6 categories.** If data has more than 6 categories, aggregate into "Other" or split into multiple charts.

**EXCEPTION: Choropleth maps show ALL regions by design** (e.g., all 21 aimags). When a dataset covers every aimag, add a choropleth map as a second chart alongside the time series instead of reducing to a subset. See section 6 below.

### Legend Position (CRITICAL)

**ALWAYS place legends at the top** so charts use full width. Legends on the right steal horizontal space.

For any chart with color encoding (multi-series), add:
```json
"color": {
  "field": "category",
  "type": "nominal",
  "legend": {"orient": "top"}   // ← REQUIRED for full-width charts
}
```

**WRONG:**
```json
"legend": {"title": "Category"}  // Defaults to right, wastes space
```

**CORRECT:**
```json
"legend": {"orient": "top", "title": "Category"}
```

### Typography

- Axis title font size: 16px
- Axis label font size: 14px
- Legend title font size: 14px
- Legend label font size: 13px

### Dimensions

**Charts are responsive by default.** The VegaChart component automatically:
- Measures container width at render time
- Calculates height using aspect ratio (default 0.625 = 16:10)
- Re-renders on window resize

**Do NOT set width/height in chart specs** - they will be overridden.

### Gridlines (CRITICAL)

**Only horizontal gridlines are allowed** on standard vertical charts:

```json
"x": {
  "field": "year",
  "type": "quantitative",
  "axis": {
    "grid": false,    // ← REQUIRED: No vertical gridlines
    "format": "d"
  }
}
```

**Exception:** Horizontal bar charts (where Y is the category axis) may have vertical gridlines to show values.

**WRONG:**
```json
"x": {"field": "year", "axis": {"format": "d"}}  // Missing grid: false
```

**CORRECT:**
```json
"x": {"field": "year", "axis": {"grid": false, "format": "d"}}
```

### Line Chart Markers

**DO NOT use permanent circle markers** on line charts. They clutter the visualization.

**WRONG:**
```json
"mark": {"type": "line", "point": true}  // Shows circles at every data point
```

**CORRECT:**
```json
"mark": {"type": "line", "strokeWidth": 2.5}  // Clean line, no permanent markers
```

The hover layer provides interactive points that appear on mouseover - this is the preferred UX.

### Common Config

Apply this config to all charts:

```json
{
  "config": {
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
}
```

## CRITICAL: Number Formatting (No Scientific Notation!)

**NEVER allow scientific notation (e.g., 1.5e+4) in charts.** Always use explicit D3 format specifiers.

### Required Formats by Data Type

| Data Type | D3 Format | Example Output | Use For |
|-----------|-----------|----------------|---------|
| **Large integers (>1000)** | `",.0f"` | `15,000` | Prices, population counts |
| **Decimals** | `",.2f"` | `15,000.00` | Currency with cents |
| **Percentages** | `".1f"` | `5.2` | Rates, percentages (add % in title) |
| **Millions (abbreviate)** | `".2s"` | `1.5M` | GDP, large aggregates |
| **Years** | `"d"` | `2024` | Year axis labels |

### Applying Formats

**Y-Axis (ALWAYS specify format):**
```json
"y": {
  "field": "price",
  "type": "quantitative",
  "title": "Price (MNT/kg)",
  "axis": {"format": ",.0f"}   // ← REQUIRED for integer values
}
```

**Tooltips (ALWAYS specify format):**
```json
"tooltip": [
  {"field": "price", "title": "Price", "format": ",.0f"}  // ← Prevents 1.5e+4
]
```

### Why This Matters

Vega-Lite defaults to scientific notation for large numbers. The format `","` alone is often not enough - you must use `",.0f"` (or similar) to guarantee proper formatting.

**WRONG:**
```json
"axis": {"format": ","}  // May still show scientific notation!
```

**CORRECT:**
```json
"axis": {"format": ",.0f"}  // Guaranteed comma-separated integers
```

## Common Mistakes to Avoid

### 1. Missing CSV Format Specification (BROKEN CHARTS!)

**ALWAYS include explicit `"format": {"type": "csv"}` in the data specification.**

Without this, Vega-Lite may fail to parse the CSV in certain environments (browsers, CDN configurations, CORS issues), causing charts to silently fail and display nothing.

```json
// ❌ WRONG - Charts may fail silently in production
"data": {
  "url": "/datasets/my-data.csv"
}

// ✅ CORRECT - Guaranteed CSV parsing
"data": {
  "url": "/datasets/my-data.csv",
  "format": {"type": "csv"}
}
```

**Why this matters:** Vega-Lite *can* auto-detect CSV format from file extensions, but this behavior is not 100% reliable. Explicit format declarations are defensive programming that prevent silent failures.

### 2. Setting Fixed Y-Axis Domain (BREAKS RESPONSIVE SIZING!)

**DO NOT set `scale.domain` on quantitative Y-axes.** This conflicts with the responsive `autosize: "fit"` behavior and causes charts to render as flat lines.

```json
// ❌ WRONG - Chart will be squished to a flat line
"y": {
  "field": "value",
  "type": "quantitative",
  "scale": {
    "domain": [50, 80]
  }
}

// ✅ CORRECT - Let Vega auto-calculate the domain
"y": {
  "field": "value",
  "type": "quantitative",
  "axis": {
    "format": ".1f"
  }
}
```

**Why this happens:** The VegaChart component sets `autosize: {"type": "fit"}` to make charts responsive. When you also set a fixed Y-axis domain, Vega tries to satisfy both constraints and ends up squishing the chart vertically.

**Exception:** You CAN use `domain` for **categorical/nominal** color scales (e.g., `["Male", "Female"]`) - the issue only affects quantitative axis scales.

### 3. Using 'ordinal' for Time Data (WRONG)

**NEVER use `type: "ordinal"` for years/dates.** Ordinal treats values as categories with equal spacing, hiding gaps in data.

```json
// WRONG - hides that 1956->1963 is 7 years but 1989->1990 is 1 year
"x": {"field": "year", "type": "ordinal"}

// CORRECT - shows true time spacing
"x": {"field": "year", "type": "quantitative"}
```

### 2. Not Starting at Zero for Absolute Values (MISLEADING)

Bar charts and area charts showing counts/totals MUST start at zero.

```json
// WRONG - exaggerates differences
"y": {"field": "population", "scale": {"zero": false}}

// CORRECT - honest representation (zero: true is default)
"y": {"field": "population", "type": "quantitative"}
```

### 3. Setting width/height (NOT RESPONSIVE)

```json
// WRONG
{"width": 600, "height": 400, ...}

// CORRECT - omit width/height entirely
{"$schema": "...", "data": {...}, "mark": {...}, "encoding": {...}}
```

## Chart Types

### CRITICAL: Layered Structure Required for Line/Area Charts

**ALL line and area charts MUST use a layered structure** for proper nearest-point hover:

```
┌─────────────────────────────────────────────────────────────┐
│  WHY LAYERED STRUCTURE IS REQUIRED                          │
│                                                             │
│  The `nearest: true` selection needs POINT marks to work.   │
│  Area/line marks are continuous shapes - the algorithm      │
│  can't find the "nearest" point on a line.                  │
│                                                             │
│  Solution: Add an invisible point layer that appears on     │
│  hover, providing selection targets at each data point.     │
└─────────────────────────────────────────────────────────────┘
```

**WRONG - Hover won't work properly:**
```json
{
  "mark": {"type": "area"},
  "params": [{"name": "hover", "select": {"nearest": true, ...}}],
  "encoding": {"tooltip": [...]}
}
```

**CORRECT - Layered structure with point layer:**
```json
{
  "encoding": {"x": {...}, "y": {...}},
  "layer": [
    {"mark": {"type": "area", ...}},
    {
      "params": [{"name": "hover", "select": {"type": "point", "nearest": true, ...}}],
      "mark": {"type": "point", "filled": true, "size": 100},
      "encoding": {
        "opacity": {"condition": {"param": "hover", "value": 1}, "value": 0},
        "tooltip": [...]
      }
    }
  ]
}
```

**Bar charts are different** - they use hover directly on bars (no point layer needed).

---

### 1. Area Chart with Line (Time Series) - RECOMMENDED

Use for: Trends over time.

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "Description of chart and any filtering applied",
  "data": {
    "url": "/datasets/{dataset-id}.csv",
    "format": {"type": "csv"}
  },
  "encoding": {
    "x": {
      "field": "year",
      "type": "quantitative",
      "title": "Year",
      "axis": {"format": "d", "tickMinStep": 10, "grid": false}
    },
    "y": {
      "field": "value",
      "type": "quantitative",
      "title": "Value",
      "axis": {"format": ".2s"}
    }
  },
  "layer": [
    {
      "mark": {
        "type": "area",
        "line": {"strokeWidth": 2.5},
        "interpolate": "monotone"
      }
    },
    {
      "params": [
        {
          "name": "hover",
          "select": {
            "type": "point",
            "nearest": true,
            "on": "pointerover",
            "clear": "pointerout"
          }
        }
      ],
      "mark": {
        "type": "point",
        "filled": true,
        "size": 100
      },
      "encoding": {
        "opacity": {
          "condition": {"param": "hover", "empty": false, "value": 1},
          "value": 0
        },
        "tooltip": [
          {"field": "year", "title": "Year", "format": "d"},
          {"field": "value", "title": "Value", "format": ",.0f"}
        ]
      }
    }
  ],
  "config": {
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
    "view": {"stroke": "transparent"}
  }
}
```

### 2. Multi-Line Chart (Comparison)

Use for: Comparing multiple categories over time

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {
    "url": "/datasets/{dataset-id}.csv",
    "format": {"type": "csv"}
  },
  "encoding": {
    "x": {
      "field": "year",
      "type": "quantitative",
      "title": "Year",
      "axis": {"format": "d", "tickMinStep": 10, "grid": false}
    },
    "y": {
      "field": "value",
      "type": "quantitative",
      "title": "Value",
      "axis": {"format": ".2s"}
    },
    "color": {
      "field": "category",
      "type": "nominal",
      "legend": {"orient": "top", "title": "Category"}
    }
  },
  "layer": [
    {
      "mark": {
        "type": "line",
        "strokeWidth": 2.5,
        "interpolate": "monotone"
      }
    },
    {
      "params": [
        {
          "name": "hover",
          "select": {
            "type": "point",
            "nearest": true,
            "on": "pointerover",
            "clear": "pointerout"
          }
        }
      ],
      "mark": {
        "type": "point",
        "filled": true,
        "size": 100
      },
      "encoding": {
        "opacity": {
          "condition": {"param": "hover", "empty": false, "value": 1},
          "value": 0
        },
        "tooltip": [
          {"field": "category", "title": "Category"},
          {"field": "year", "title": "Year", "format": "d"},
          {"field": "value", "title": "Value", "format": ",.0f"}
        ]
      }
    }
  ],
  "config": {
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
    "view": {"stroke": "transparent"}
  }
}
```

### 3. Bar Chart (Categorical)

Use for: Comparing values across categories

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {
    "url": "/datasets/{dataset-id}.csv",
    "format": {"type": "csv"}
  },
  "params": [
    {
      "name": "hover",
      "select": {
        "type": "point",
        "on": "pointerover",
        "clear": "pointerout"
      }
    }
  ],
  "mark": {
    "type": "bar",
    "cursor": "pointer"
  },
  "encoding": {
    "x": {
      "field": "category",
      "type": "nominal",
      "title": "Category",
      "axis": {"labelAngle": -45}
    },
    "y": {
      "field": "value",
      "type": "quantitative",
      "title": "Value",
      "axis": {"format": ".2s"}
    },
    "tooltip": [
      {"field": "category", "title": "Category"},
      {"field": "value", "title": "Value", "format": ",.0f"}
    ]
  },
  "config": {
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
    "view": {"stroke": "transparent"}
  }
}
```

### 4. Population Pyramid

Use for: Age/sex distribution

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {
    "url": "/datasets/{dataset-id}.csv",
    "format": {"type": "csv"}
  },
  "transform": [
    {
      "calculate": "datum.sex === 'Male' ? -datum.population : datum.population",
      "as": "signed_population"
    }
  ],
  "params": [
    {
      "name": "hover",
      "select": {
        "type": "point",
        "on": "pointerover",
        "clear": "pointerout"
      }
    }
  ],
  "mark": {
    "type": "bar",
    "cursor": "pointer"
  },
  "encoding": {
    "y": {
      "field": "age",
      "type": "ordinal",
      "title": "Age Group",
      "sort": ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70+"]
    },
    "x": {
      "field": "signed_population",
      "type": "quantitative",
      "title": "Population",
      "axis": {
        "format": ".2s",
        "labelExpr": "abs(datum.value) >= 1000000 ? format(abs(datum.value) / 1000000, '.1f') + 'M' : format(abs(datum.value) / 1000, '.0f') + 'K'"
      }
    },
    "color": {
      "field": "sex",
      "type": "nominal",
      "legend": {"orient": "top", "title": "Sex"}
    },
    "opacity": {
      "condition": {"param": "hover", "empty": true, "value": 1},
      "value": 0.7
    },
    "tooltip": [
      {"field": "age", "title": "Age Group"},
      {"field": "sex", "title": "Sex"},
      {"field": "population", "title": "Population", "format": ","}
    ]
  },
  "config": {
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
    "view": {"stroke": "transparent"}
  }
}
```

### 5. Stacked Area Chart

Use for: Part-to-whole over time

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {
    "url": "/datasets/{dataset-id}.csv",
    "format": {"type": "csv"}
  },
  "encoding": {
    "x": {
      "field": "year",
      "type": "quantitative",
      "title": "Year",
      "axis": {"format": "d", "tickMinStep": 10, "grid": false}
    },
    "y": {
      "field": "value",
      "type": "quantitative",
      "title": "Value",
      "stack": "zero",
      "axis": {"format": ".2s"}
    },
    "color": {
      "field": "category",
      "type": "nominal",
      "legend": {"orient": "top", "title": "Category"}
    }
  },
  "layer": [
    {
      "mark": {
        "type": "area",
        "interpolate": "monotone"
      }
    },
    {
      "params": [
        {
          "name": "hover",
          "select": {
            "type": "point",
            "nearest": true,
            "on": "pointerover",
            "clear": "pointerout"
          }
        }
      ],
      "mark": {
        "type": "point",
        "filled": true,
        "size": 100
      },
      "encoding": {
        "opacity": {
          "condition": {"param": "hover", "empty": false, "value": 1},
          "value": 0
        },
        "tooltip": [
          {"field": "category", "title": "Category"},
          {"field": "year", "title": "Year", "format": "d"},
          {"field": "value", "title": "Value", "format": ",.0f"}
        ]
      }
    }
  ],
  "config": {
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
    "view": {"stroke": "transparent"}
  }
}
```

### 6. Choropleth Map (Aimag-Level Data)

Use for: Showing a single-week/month snapshot across all 21 aimags. For aimag-level datasets the map IS the embedded chart (slug-named `{dataset-id}-{lang}.json` so listing thumbnails derive from it); rename any reduced-subset time series to `{dataset-id}-trend-{lang}.json` and leave it unembedded.

**Boundary file** (static, shared by all maps — never regenerate):
`data.mn/public/maps/mongolia-aimags.json`. Feature properties are `name` (English, matches `-en.csv` region values) and `name_mn` (Mongolian, matches `-mn.csv` бүс values). See `data.mn/public/maps/README.md` for provenance.

**Latest-week snapshot convention:** Vega-Lite `lookup` cannot filter time series, so the update transformation MUST export a snapshot CSV with max-date rows only:
- `{dataset-id}-latest-en.csv` with columns `name,value-column`
- `{dataset-id}-latest-mn.csv` with columns `бүс,value-column-mn`

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "Description + boundary credit: geoBoundaries (ODbL) / OpenStreetMap contributors",
  "data": {
    "url": "/maps/mongolia-aimags.json",
    "format": {"type": "json", "property": "features"}
  },
  "transform": [
    {
      "lookup": "properties.name",
      "from": {
        "data": {
          "url": "/datasets/{dataset-id}-latest-en.csv",
          "format": {"type": "csv"}
        },
        "key": "name",
        "fields": ["value"]
      }
    }
  ],
  "projection": {"type": "mercator"},
  "mark": {
    "type": "geoshape",
    "stroke": "white",
    "strokeWidth": 1
  },
  "encoding": {
    "color": {
      "field": "value",
      "type": "quantitative",
      "scale": {"scheme": "oranges"},
      "legend": {"orient": "top", "title": "Value"}
    },
    "tooltip": [
      {"field": "properties.name", "title": "Aimag"},
      {"field": "value", "title": "Value", "format": ",.0f"}
    ]
  },
  "config": {
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
    "view": {"stroke": "transparent"}
  }
}
```

**MN version differences:** `lookup` on `properties.name_mn`, `key` on `бүс`, value field in Mongolian, translated legend/tooltip titles, `-latest-mn.csv` data URL.

**MDX caption:** describe as "latest available week" and note any coverage gaps (e.g., Ulaanbaatar not surveyed). NEVER hardcode the snapshot date in the caption — it must stay correct between updates.

## File Location

**IMPORTANT:** Save chart specs to the CORRECT location:

```
/home/ritz/Insync/robert@aum.edu.mn/Google Drive/data/data.mn/public/charts/{dataset-id}-{lang}.json
```

Or relative from the data directory: `data.mn/public/charts/{dataset-id}-{lang}.json`

**DO NOT save to `src/data/charts/`** - that path is incorrect and charts won't load.

## CRITICAL: Bilingual Charts Required

**ALWAYS create TWO chart files** - one for English and one for Mongolian:

```
public/charts/
├── inflation-rate-en.json   # English labels, uses -en.csv
└── inflation-rate-mn.json   # Mongolian labels, uses -mn.csv
```

### New Bilingual CSV Architecture

**Charts now use language-matched CSV files:**

```json
// EN chart
{"data": {"url": "/datasets/{dataset-id}-en.csv"}}

// MN chart
{"data": {"url": "/datasets/{dataset-id}-mn.csv"}}
```

The NSO fetch script outputs bilingual CSVs:
- `{dataset-id}-en.csv` - English data with English string values
- `{dataset-id}-mn.csv` - Mongolian data with Mongolian string values

**This means data VALUES are pre-translated** - no transforms needed!

### What to Translate in Mongolian Charts

With bilingual CSVs, you ONLY translate **UI text**, NOT data values:

| Element | English | Mongolian | Notes |
|---------|---------|-----------|-------|
| **Axis titles** | "Year" | "Он" | ✓ Translate |
| **Axis titles** | "Population" | "Хүн ам" | ✓ Translate |
| **Axis titles** | "Value" | "Утга" | ✓ Translate |
| **Axis titles** | "Rate (%)" | "Түвшин (%)" | ✓ Translate |
| **Axis titles** | "Million MNT" | "Сая төгрөг" | ✓ Translate |
| **Tooltip field titles** | "Year" | "Он" | ✓ Translate title only |
| **Tooltip field titles** | "Value" | "Утга" | ✓ Translate title only |
| **Tooltip field titles** | "Sector" | "Салбар" | ✓ Translate title only |
| **Legend titles** | "Category" | "Ангилал" | ✓ Translate title only |
| **Legend titles** | "Sex" | "Хүйс" | ✓ Translate title only |
| **Data values** | "Male", "Female" | Pre-translated in CSV | ✗ Don't translate (automatic) |
| **Data values** | Sector names | Pre-translated in CSV | ✗ Don't translate (automatic) |
| **Legend label values** | Auto from data | Pre-translated in CSV | ✗ Don't translate (automatic) |

### DEPRECATED: Data Value Translation

**⚠️ This section is DEPRECATED as of the bilingual CSV architecture.**

With the new fetch script, bilingual CSVs are generated automatically:
- EN charts use `{dataset-id}-en.csv` with English values
- MN charts use `{dataset-id}-mn.csv` with Mongolian values

**You NO LONGER need:**
- ❌ `calculate` transforms to translate data values
- ❌ `labelExpr` hacks for legend/axis values
- ❌ Manual translation mappings in chart specs

**Legacy charts** may still use single CSVs with calculate transforms. When updating these charts, migrate to bilingual CSVs by:
1. Fetching data with the updated NSO script (outputs `-en.csv` and `-mn.csv`)
2. Updating EN chart to use `-en.csv`
3. Updating MN chart to use `-mn.csv`
4. Removing calculate transforms from both charts

### The New Architecture is SIMPLER

**Before (old approach - DEPRECATED):**
```json
// Single CSV with English values
// MN chart needs complex transforms
{
  "data": {"url": "/datasets/salary-by-sector.csv"},
  "transform": [
    {
      "calculate": "datum.sector == 'Agriculture' ? 'Хөдөө аж ахуй' : datum.sector == 'Mining' ? 'Уул уурхай' : ...",
      "as": "sector_mn"
    }
  ],
  "encoding": {
    "tooltip": [{"field": "sector_mn", "title": "Салбар"}]
  }
}
```

**After (new approach - RECOMMENDED):**
```json
// EN chart - simple and clean
{
  "data": {"url": "/datasets/salary-by-sector-en.csv"},
  "encoding": {
    "tooltip": [{"field": "sector", "title": "Sector"}]
  }
}

// MN chart - equally simple
{
  "data": {"url": "/datasets/salary-by-sector-mn.csv"},
  "encoding": {
    "tooltip": [{"field": "sector", "title": "Салбар"}]
  }
}
```

**Key difference:** EN and MN charts now differ ONLY in:
1. Data URL (`-en.csv` vs `-mn.csv`)
2. UI text (axis titles, tooltip field titles, legend titles)

Data values come pre-translated from the CSV - no transforms needed!

### Common Axis Title Translations

| English | Mongolian |
|---------|-----------|
| Population | Хүн ам |
| GDP | ДНБ |
| GDP (Billion MNT) | ДНБ (Тэрбум төгрөг) |
| GDP per capita (USD) | Нэг хүнд ногдох ДНБ (ам.доллар) |
| Inflation Rate (%) | Инфляцийн түвшин (%) |
| Unemployment Rate (%) | Ажилгүйдлийн түвшин (%) |
| Average Salary (thousand MNT) | Дундаж цалин (мянган төгрөг) |
| Household Income (MNT) | Өрхийн орлого (төгрөг) |
| Trade (Million USD) | Худалдаа (Сая ам.доллар) |
| Livestock (millions) | Мал (сая) |
| Labor Force Participation (%) | Хөдөлмөрийн оролцооны түвшин (%) |

## Usage in MDX

**IMPORTANT:** Reference the language-specific chart file matching the page language:

```mdx
{/* In English page (en/my-data.mdx) */}
<VegaChart
  spec="/charts/{dataset-id}-en.json"
  title="Chart Title in English"
/>

{/* In Mongolian page (mn/my-data.mdx) */}
<VegaChart
  spec="/charts/{dataset-id}-mn.json"
  title="Монгол хэлээр гарчиг"
/>
```

**DO NOT** use a single chart file for both languages - always use `-en.json` for English pages and `-mn.json` for Mongolian pages.

## Best Practices Checklist

Before finalizing any chart:

- [ ] **CSV FORMAT SPECIFIED**: Data block includes `"format": {"type": "csv"}` (CRITICAL!)
- [ ] **NO FIXED Y-AXIS DOMAIN**: Do not use `scale.domain` on quantitative Y-axes (breaks responsive sizing!)
- [ ] **BILINGUAL: Created BOTH `-en.json` and `-mn.json` versions**
- [ ] **LANGUAGE-MATCHED CSV**: EN chart uses `-en.csv`, MN chart uses `-mn.csv`
- [ ] **UI TEXT TRANSLATED**: Axis titles, tooltip field titles, legend titles in MN chart
- [ ] Uses data from `/datasets/{id}-{lang}.csv` (not hardcoded values)
- [ ] **NO width/height in spec** (component handles sizing)
- [ ] Colors follow brand palette
- [ ] Axis labels are readable (use labelAngle: -45 if needed)
- [ ] Large numbers use format `.2s` (e.g., 1.5M)
- [ ] Tooltips are enabled
- [ ] Chart answers ONE clear question
- [ ] Time axes use `quantitative` or `temporal` (NOT `ordinal`)
- [ ] Bar/area charts start at zero
- [ ] Validated with `validate_vega.py`
- [ ] MDX pages reference language-specific chart (`-en.json` for EN, `-mn.json` for MN)
- [ ] **NO calculate transforms** for data value translation (pre-translated in CSV)
