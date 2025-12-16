#!/usr/bin/env python3
"""
Create unemployment datasets from NSO table DT_NSO_0400_049V1.px
"""

import pandas as pd
import json
import os

# Base directory paths
BASE_DIR = "/Users/ritz/Insync/robert@aum.edu.mn/Google Drive/data"
DATA_MN_DIR = f"{BASE_DIR}/data.mn"
SOURCE_DIR = f"{DATA_MN_DIR}/src/data/datasets"
PUBLIC_DIR = f"{DATA_MN_DIR}/public"

# Ensure output directories exist
os.makedirs(f"{PUBLIC_DIR}/datasets", exist_ok=True)
os.makedirs(f"{PUBLIC_DIR}/charts", exist_ok=True)

print("Creating unemployment datasets...")
print("=" * 50)

# ============================================================================
# Dataset 1: National Unemployment Rate (Total only)
# ============================================================================

print("\n1. Creating unemployment-rate-national dataset...")

# Load English data
df_en = pd.read_csv(f"{SOURCE_DIR}/nso-0400-049v1-en.csv")
df_national_en = df_en[df_en['Category'] == 'Total'].copy()
df_national_en = df_national_en.sort_values('Year')
df_national_en.to_csv(f"{PUBLIC_DIR}/datasets/unemployment-rate-national-en.csv", index=False)
print(f"   Created: unemployment-rate-national-en.csv ({len(df_national_en)} rows)")

# Load Mongolian data
df_mn = pd.read_csv(f"{SOURCE_DIR}/nso-0400-049v1-mn.csv")
df_national_mn = df_mn[df_mn['Ангилал'] == 'Бүгд'].copy()
df_national_mn = df_national_mn.sort_values('Он')
df_national_mn.to_csv(f"{PUBLIC_DIR}/datasets/unemployment-rate-national-mn.csv", index=False)
print(f"   Created: unemployment-rate-national-mn.csv ({len(df_national_mn)} rows)")

# Create XLSX
with pd.ExcelWriter(f"{PUBLIC_DIR}/datasets/unemployment-rate-national-en.xlsx", engine='openpyxl') as writer:
    df_national_en.to_excel(writer, index=False, sheet_name='Data')
print(f"   Created: unemployment-rate-national-en.xlsx")

with pd.ExcelWriter(f"{PUBLIC_DIR}/datasets/unemployment-rate-national-mn.xlsx", engine='openpyxl') as writer:
    df_national_mn.to_excel(writer, index=False, sheet_name='Data')
print(f"   Created: unemployment-rate-national-mn.xlsx")

# Create Vega-Lite chart (EN)
chart_national_en = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Mongolia National Unemployment Rate (2009-2024)",
    "data": {
        "url": "/datasets/unemployment-rate-national-en.csv"
    },
    "mark": {
        "type": "area",
        "line": True,
        "point": True,
        "color": "#3b82f6",
        "opacity": 0.3
    },
    "encoding": {
        "x": {
            "field": "Year",
            "type": "temporal",
            "timeUnit": "year",
            "axis": {
                "title": "Year",
                "format": "%Y",
                "labelAngle": 0
            }
        },
        "y": {
            "field": "value",
            "type": "quantitative",
            "axis": {
                "title": "Unemployment Rate (%)"
            },
            "scale": {
                "zero": False
            }
        },
        "tooltip": [
            {
                "field": "Year",
                "type": "temporal",
                "timeUnit": "year",
                "title": "Year",
                "format": "%Y"
            },
            {
                "field": "value",
                "type": "quantitative",
                "title": "Unemployment Rate",
                "format": ".1f"
            }
        ]
    },
    "config": {
        "view": {
            "stroke": "transparent"
        }
    }
}

with open(f"{PUBLIC_DIR}/charts/unemployment-rate-national-en.json", 'w') as f:
    json.dump(chart_national_en, f, indent=2)
print(f"   Created: unemployment-rate-national-en.json")

# Create Vega-Lite chart (MN)
chart_national_mn = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Монгол Улсын ажилгүйдлийн түвшин (2009-2024)",
    "data": {
        "url": "/datasets/unemployment-rate-national-mn.csv"
    },
    "mark": {
        "type": "area",
        "line": True,
        "point": True,
        "color": "#3b82f6",
        "opacity": 0.3
    },
    "encoding": {
        "x": {
            "field": "Он",
            "type": "temporal",
            "timeUnit": "year",
            "axis": {
                "title": "Он",
                "format": "%Y",
                "labelAngle": 0
            }
        },
        "y": {
            "field": "value",
            "type": "quantitative",
            "axis": {
                "title": "Ажилгүйдлийн түвшин (%)"
            },
            "scale": {
                "zero": False
            }
        },
        "tooltip": [
            {
                "field": "Он",
                "type": "temporal",
                "timeUnit": "year",
                "title": "Он",
                "format": "%Y"
            },
            {
                "field": "value",
                "type": "quantitative",
                "title": "Ажилгүйдлийн түвшин",
                "format": ".1f"
            }
        ]
    },
    "config": {
        "view": {
            "stroke": "transparent"
        }
    }
}

with open(f"{PUBLIC_DIR}/charts/unemployment-rate-national-mn.json", 'w') as f:
    json.dump(chart_national_mn, f, indent=2)
print(f"   Created: unemployment-rate-national-mn.json")

# Stats
stats_national = {
    "row_count": len(df_national_en),
    "first_year": int(df_national_en['Year'].min()),
    "last_year": int(df_national_en['Year'].max()),
    "min_value": float(df_national_en['value'].min()),
    "max_value": float(df_national_en['value'].max()),
    "latest_value": float(df_national_en[df_national_en['Year'] == df_national_en['Year'].max()]['value'].iloc[0])
}
print(f"   Stats: {stats_national}")

# ============================================================================
# Dataset 2: Unemployment by Sex (Male + Female)
# ============================================================================

print("\n2. Creating unemployment-by-sex dataset...")

# Load English data - filter for Male and Female only
df_sex_en = df_en[df_en['Category'].str.strip().isin(['Male', 'Female'])].copy()
df_sex_en = df_sex_en.sort_values(['Year', 'Category'])
df_sex_en.to_csv(f"{PUBLIC_DIR}/datasets/unemployment-by-sex-en.csv", index=False)
print(f"   Created: unemployment-by-sex-en.csv ({len(df_sex_en)} rows)")

# Load Mongolian data - filter for Эрэгтэй and Эмэгтэй
df_sex_mn = df_mn[df_mn['Ангилал'].str.strip().isin(['Эрэгтэй', 'Эмэгтэй'])].copy()
df_sex_mn = df_sex_mn.sort_values(['Он', 'Ангилал'])
df_sex_mn.to_csv(f"{PUBLIC_DIR}/datasets/unemployment-by-sex-mn.csv", index=False)
print(f"   Created: unemployment-by-sex-mn.csv ({len(df_sex_mn)} rows)")

# Create XLSX
with pd.ExcelWriter(f"{PUBLIC_DIR}/datasets/unemployment-by-sex-en.xlsx", engine='openpyxl') as writer:
    df_sex_en.to_excel(writer, index=False, sheet_name='Data')
print(f"   Created: unemployment-by-sex-en.xlsx")

with pd.ExcelWriter(f"{PUBLIC_DIR}/datasets/unemployment-by-sex-mn.xlsx", engine='openpyxl') as writer:
    df_sex_mn.to_excel(writer, index=False, sheet_name='Data')
print(f"   Created: unemployment-by-sex-mn.xlsx")

# Create Vega-Lite chart (EN)
chart_sex_en = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Mongolia Unemployment Rate by Sex (2009-2024)",
    "data": {
        "url": "/datasets/unemployment-by-sex-en.csv"
    },
    "mark": {
        "type": "line",
        "point": True
    },
    "encoding": {
        "x": {
            "field": "Year",
            "type": "temporal",
            "timeUnit": "year",
            "axis": {
                "title": "Year",
                "format": "%Y",
                "labelAngle": 0
            }
        },
        "y": {
            "field": "value",
            "type": "quantitative",
            "axis": {
                "title": "Unemployment Rate (%)"
            },
            "scale": {
                "zero": False
            }
        },
        "color": {
            "field": "Category",
            "type": "nominal",
            "scale": {
                "domain": ["Male", "Female"],
                "range": ["#3b82f6", "#ec4899"]
            },
            "legend": {
                "title": "Sex"
            }
        },
        "tooltip": [
            {
                "field": "Year",
                "type": "temporal",
                "timeUnit": "year",
                "title": "Year",
                "format": "%Y"
            },
            {
                "field": "Category",
                "type": "nominal",
                "title": "Sex"
            },
            {
                "field": "value",
                "type": "quantitative",
                "title": "Unemployment Rate",
                "format": ".1f"
            }
        ]
    },
    "config": {
        "view": {
            "stroke": "transparent"
        }
    }
}

with open(f"{PUBLIC_DIR}/charts/unemployment-by-sex-en.json", 'w') as f:
    json.dump(chart_sex_en, f, indent=2)
print(f"   Created: unemployment-by-sex-en.json")

# Create Vega-Lite chart (MN)
chart_sex_mn = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Монгол Улсын ажилгүйдлийн түвшин хүйсээр (2009-2024)",
    "data": {
        "url": "/datasets/unemployment-by-sex-mn.csv"
    },
    "mark": {
        "type": "line",
        "point": True
    },
    "encoding": {
        "x": {
            "field": "Он",
            "type": "temporal",
            "timeUnit": "year",
            "axis": {
                "title": "Он",
                "format": "%Y",
                "labelAngle": 0
            }
        },
        "y": {
            "field": "value",
            "type": "quantitative",
            "axis": {
                "title": "Ажилгүйдлийн түвшин (%)"
            },
            "scale": {
                "zero": False
            }
        },
        "color": {
            "field": "Ангилал",
            "type": "nominal",
            "scale": {
                "domain": ["Эрэгтэй", "Эмэгтэй"],
                "range": ["#3b82f6", "#ec4899"]
            },
            "legend": {
                "title": "Хүйс"
            }
        },
        "tooltip": [
            {
                "field": "Он",
                "type": "temporal",
                "timeUnit": "year",
                "title": "Он",
                "format": "%Y"
            },
            {
                "field": "Ангилал",
                "type": "nominal",
                "title": "Хүйс"
            },
            {
                "field": "value",
                "type": "quantitative",
                "title": "Ажилгүйдлийн түвшин",
                "format": ".1f"
            }
        ]
    },
    "config": {
        "view": {
            "stroke": "transparent"
        }
    }
}

with open(f"{PUBLIC_DIR}/charts/unemployment-by-sex-mn.json", 'w') as f:
    json.dump(chart_sex_mn, f, indent=2)
print(f"   Created: unemployment-by-sex-mn.json")

# Stats
stats_sex = {
    "row_count": len(df_sex_en),
    "first_year": int(df_sex_en['Year'].min()),
    "last_year": int(df_sex_en['Year'].max()),
    "categories": df_sex_en['Category'].unique().tolist()
}
print(f"   Stats: {stats_sex}")

print("\n" + "=" * 50)
print("✓ All datasets created successfully!")
print("\nNext steps:")
print("1. Validate charts")
print("2. Generate MDX pages")
print("3. Register datasets")
print("4. Publish datasets")
