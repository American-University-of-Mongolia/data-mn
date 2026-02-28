---
name: vega-charts
description: "Create branded Vega-Lite chart specifications for data.mn. Use when creating charts, visualizations, or data graphics for the data.mn website. Includes templates for area charts, line charts, bar charts, population pyramids, and stacked areas."
---


# Vega-Lite Charts Skill

Create consistent, branded Vega-Lite chart specifications for data.mn.

## CRITICAL: Visual QA Required

**ALWAYS export and review charts visually before finalizing:**

```bash
# Export chart to PNG for visual review (run from data.mn directory)
cd data.mn && npx vl2png public/charts/{chart-name}.json -b public/ -s 2 /tmp/{chart-name}.png
```

Then use the Read tool to view `/tmp/{chart-name}.png` and check:

### Visual QA Checklist
- [ ] **Line/area visibility**: Lines are thick enough to see clearly (strokeWidth ≥ 2)
- [ ] **Data point visibility**: Points are appropriately sized or omitted for dense data
- [ ] **Color contrast**: Chart elements stand out against the background
- [ ] **Label readability**: All text is legible, not overlapping
- [ ] **Proportions**: Chart fills the space well, not too sparse or cramped
- [ ] **Professional appearance**: Would this look good on Statista?

If any issues are found, update the chart spec and re-export until it looks polished.

---

## CRITICAL: Library Versions

The VegaChart component dynamically loads these CDN libraries **in order** (each depends on the previous):

| Library | Version | CDN URL |
|---------|---------|---------|
| Vega | 5.30.0 | `https://cdn.jsdelivr.net/npm/vega@5.30.0` |
| Vega-Lite | 5.21.0 | `https://cdn.jsdelivr.net/npm/vega-lite@5.21.0` |
| Vega-Embed | 6.26.0 | `https://cdn.jsdelivr.net/npm/vega-embed@6.26.0` |

**DO NOT change these versions** without testing thoroughly. Version mismatches cause runtime errors like:
- `Cannot read properties of undefined (reading 'logger')`
- `Cannot read properties of undefined (reading 'isString')`

If updating versions, update all three together and test on multiple pages with charts.

The loading is handled in `data.mn/src/components/ui/VegaChart.astro`.

## CRITICAL: Validation Required

**ALWAYS validate charts after creating them:**

```bash
cd tools && python3 scripts/validate_vega.py /path/to/chart.json --data /path/to/data.csv
```

Or validate all charts:
```bash
cd data.mn && python3 ../tools/scripts/validate_vega.py --all
```

Charts with errors MUST be fixed before committing.

## Brand Guidelines

### Colors

**Primary Palette** (for single series or primary data):
- Primary Blue: `#2563eb` (Tailwind blue-600) — indigo-shifted to differentiate from Inside Mongolia
- Primary hover: `#1d4ed8` (blue-700)
- Primary light: `#3b82f6` (blue-500) — for gradients and accents

**Categorical Palette** (for multi-series data):
```json
["#2563eb", "#ec4899", "#10b981", "#f59e0b", "#8b5cf6", "#06b6d4"]
```

**Semantic Colors**:
- Male: `#2563eb` (blue)
- Female: `#ec4899` (pink)
- Positive/Growth: `#10b981` (green)
- Negative/Decline: `#ef4444` (red)

### Typography

- Title font size: 16px
- Axis title font size: 14px
- Axis label font size: 12px
- Legend font size: 12px

### Dimensions

**Charts are responsive by default.** The VegaChart component automatically:
- Measures container width at render time
- Calculates height using aspect ratio (default 0.5 = 2:1 width:height)
- Re-renders on window resize (debounced)

**Do NOT set width/height in chart specs** - they will be overridden by the responsive system.

**Aspect ratio control**: Use the `aspectRatio` prop on VegaChart component:
```astro
<VegaChart spec="/charts/my-chart.json" aspectRatio={0.6} />
```

Height constraints: min 250px, max 500px (calculated from aspect ratio)

### Common Config

Apply this config to all charts:

```json
{
  "config": {
    "axis": {
      "labelFontSize": 12,
      "titleFontSize": 14,
      "labelColor": "#64748b",
      "titleColor": "#334155"
    },
    "legend": {
      "labelFontSize": 12,
      "titleFontSize": 12
    },
    "view": {
      "stroke": "transparent"
    }
  }
}
```

## Data Visualization Best Practices

### ⚠️ COMMON MISTAKES TO AVOID

#### 1. Missing CSV Format Specification (BROKEN CHARTS!)

**ALWAYS include explicit `"format": {"type": "csv"}` in the data specification.**

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

**Why?** Vega-Lite can auto-detect formats, but this is unreliable across different environments. Explicit format declarations prevent silent failures.

#### 2. Setting Fixed Y-Axis Domain (BREAKS RESPONSIVE SIZING!)

**DO NOT set `scale.domain` on quantitative Y-axes.** This conflicts with the responsive `autosize: "fit"` behavior.

```json
// ❌ WRONG - Chart will be squished to a flat line
"y": {
  "field": "value",
  "type": "quantitative",
  "scale": {"domain": [50, 80]}
}

// ✅ CORRECT - Let Vega auto-calculate the domain
"y": {
  "field": "value",
  "type": "quantitative"
}
```

**Exception:** You CAN use `domain` for categorical/nominal color scales - only quantitative axis scales are affected.

#### 3. Using 'ordinal' for Time Data (WRONG)

**NEVER use `type: "ordinal"` for years/dates.** Ordinal treats values as categories with equal spacing, hiding gaps in data.

```json
// ❌ WRONG - hides that 1956→1963 is 7 years but 1989→1990 is 1 year
"x": {"field": "year", "type": "ordinal"}

// ✅ CORRECT - shows true time spacing
"x": {"field": "year", "type": "quantitative"}
// or
"x": {"field": "date", "type": "temporal"}
```

#### 2. Not Starting at Zero for Absolute Values (MISLEADING)

Bar charts and area charts showing counts/totals MUST start at zero.

```json
// ❌ WRONG - exaggerates differences
"y": {"field": "population", "scale": {"zero": false}}

// ✅ CORRECT - honest representation
"y": {"field": "population", "type": "quantitative"}
// (zero: true is default for quantitative)
```

**Exception**: Line charts showing trends CAN use `zero: false` when the focus is on change over time, not absolute magnitude. But add a note explaining this choice.

#### 3. Skipping Years in Time Series Data

If your source data has gaps (e.g., only census years), you must either:

1. **Use quantitative x-axis** (recommended) - shows true spacing
2. **Interpolate missing years** - fill gaps with estimates
3. **Add annotation** - clearly note missing data

```python
# Option 2: Linear interpolation in Python
import pandas as pd

df = pd.read_csv('data.csv')
df['year'] = df['year'].astype(int)
df = df.set_index('year').reindex(range(df['year'].min(), df['year'].max()+1))
df = df.interpolate(method='linear').reset_index()
```

#### 4. Setting width/height (NOT RESPONSIVE)

Do NOT set width/height in chart specs. The VegaChart component handles responsive sizing.

```json
// ❌ WRONG
{"width": 600, "height": 400, ...}

// ✅ CORRECT - omit width/height entirely
{"$schema": "...", "data": {...}, "mark": {...}, "encoding": {...}}
```

### ✅ BEST PRACTICES CHECKLIST

Before finalizing any chart:

- [ ] **CSV FORMAT SPECIFIED**: `"format": {"type": "csv"}` in data block (CRITICAL!)
- [ ] **NO FIXED Y-AXIS DOMAIN**: Do not use `scale.domain` on quantitative Y-axes (breaks responsive sizing!)
- [ ] **Schema**: Has `$schema` pointing to vega-lite v5
- [ ] **Data source**: Uses `/datasets/{id}.csv` path
- [ ] **No width/height**: Let component handle sizing
- [ ] **Time axis**: Uses `quantitative` or `temporal`, NOT `ordinal`
- [ ] **Zero baseline**: Bar/area charts start at zero
- [ ] **Tooltips enabled**: `"tooltip": true` in mark
- [ ] **Number formatting**: `.2s` for large numbers, `,` for thousands
- [ ] **Axis titles**: Clear, descriptive titles on both axes
- [ ] **Brand colors**: Uses approved color palette
- [ ] **Validates**: `python3 validate_vega.py chart.json` passes

## Chart Types

### IMPORTANT: Hover-Only Data Points

**ALL charts should use hover-only data points** for a cleaner look. Points are hidden by default and only appear when the user hovers near them. This is achieved with:

```json
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
"encoding": {
  "opacity": {
    "condition": {"param": "hover", "empty": false, "value": 1},
    "value": 0
  }
}
```

---

### 1. Area Chart with Line (Time Series) - RECOMMENDED

Use for: Trends over time. **Prefer area charts over plain lines** for better visual impact.

**IMPORTANT**: Use `type: "quantitative"` for year to show true time spacing.

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
    }
  },
  "layer": [
    {
      "mark": {
        "type": "area",
        "line": {"color": "#2563eb", "strokeWidth": 2.5},
        "color": {
          "x1": 1, "y1": 1, "x2": 1, "y2": 0,
          "gradient": "linear",
          "stops": [
            {"offset": 0, "color": "rgba(37, 99, 235, 0.01)"},
            {"offset": 1, "color": "rgba(37, 99, 235, 0.3)"}
          ]
        },
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
        "color": "#2563eb",
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
      "labelFontSize": 12,
      "titleFontSize": 14,
      "labelColor": "#64748b",
      "titleColor": "#334155"
    },
    "view": {"stroke": "transparent"}
  }
}
```

### 2. Multi-Line Chart (Comparison)

Use for: Comparing multiple categories over time

**IMPORTANT**: Use `type: "quantitative"` for year to show true time spacing.

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
      "scale": {"range": ["#2563eb", "#ec4899", "#10b981", "#f59e0b"]},
      "legend": {"title": "Category"}
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
      "labelFontSize": 12,
      "titleFontSize": 14,
      "labelColor": "#64748b",
      "titleColor": "#334155"
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
    "color": {
      "condition": {"param": "hover", "empty": false, "value": "#1d4ed8"},
      "value": "#2563eb"
    },
    "tooltip": [
      {"field": "category", "title": "Category"},
      {"field": "value", "title": "Value", "format": ",.0f"}
    ]
  },
  "config": {
    "axis": {
      "labelFontSize": 12,
      "titleFontSize": 14,
      "labelColor": "#64748b",
      "titleColor": "#334155"
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
      "scale": {"domain": ["Male", "Female"], "range": ["#2563eb", "#ec4899"]},
      "legend": {"title": "Sex"}
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
      "labelFontSize": 12,
      "titleFontSize": 14,
      "labelColor": "#64748b",
      "titleColor": "#334155"
    },
    "view": {"stroke": "transparent"}
  }
}
```

### 5. Area Chart (Stacked)

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
      "scale": {"range": ["#2563eb", "#ec4899", "#10b981", "#f59e0b"]},
      "legend": {"title": "Category"}
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
      "labelFontSize": 12,
      "titleFontSize": 14,
      "labelColor": "#64748b",
      "titleColor": "#334155"
    },
    "view": {"stroke": "transparent"}
  }
}
```

## File Location

Save chart specs to: `data.mn/public/charts/{dataset-id}.json`

## Usage in MDX

```mdx
<VegaChart
  spec="/charts/{dataset-id}.json"
  title="Chart Title"
/>
```

## Checklist

Before creating a chart, verify:

- [ ] Uses data from `/datasets/{id}.csv` (not hardcoded values)
- [ ] **NO width/height in spec** (component handles responsive sizing)
- [ ] Colors follow brand palette
- [ ] Axis labels are readable (use labelAngle: -45 if needed)
- [ ] Large numbers use format `.2s` (e.g., 1.5M)
- [ ] Tooltips are enabled
- [ ] Chart answers ONE clear question
