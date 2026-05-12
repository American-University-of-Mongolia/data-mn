#!/usr/bin/env python3
"""
Fetch NSO foreign trade datasets for issue #124.

Run from repo root:
  conda run -n datamn python3 tools/scripts/fetch_foreign_trade.py
"""

import sys
import pandas as pd
from pathlib import Path

# Use the existing NSO API client
sys.path.insert(0, str(Path(__file__).parent.parent.parent /
                        ".claude" / "skills" / "datamn-source-nso"))
from fetch_data import NSO_API, jsonstat2_to_dataframe as jsonstat2_to_df

OUT = Path("data.mn/public/datasets")

SECTOR = "Economy, environment"
SUBSECTOR = "Foreign Trade"

SKIP_COUNTRIES = {
    "Total", "Europe", "Countries of EU", "Asia", "Africa", "America",
    "Oceania", "Countries of CIS", "Other countries", "Other",
    "NorthЕastern Asia", "SouthЕastern Asia",
    "Other countries of Asia", "Other countries of Europe",
    "Other countries of Africa", "Other countries of America",
    # MN equivalents
    "Нийт дүн", "Европ", "ЕХ-ны орнууд", "Ази", "Африк", "Америк",
    "Австрали ба Номхон далайн орнууд", "ТУХН-ийн орнууд", "Бусад орнууд", "Бусад",
    "Зүүн хойд Ази", "Зүүн өмнөд Ази",
    "Азийн бусад орнууд", "Европын бусад орнууд", "Африкийн бусад орнууд",
}


def fetch(lang: str, table_id: str) -> pd.DataFrame:
    api = NSO_API(language=lang)
    meta = api.get_table_metadata(SECTOR, SUBSECTOR, table_id)
    if meta is None:
        raise RuntimeError(f"Could not get metadata for {table_id} ({lang})")
    query = api._build_all_data_query(meta)
    raw = api.fetch_data(SECTOR, SUBSECTOR, table_id, query)
    if raw is None:
        raise RuntimeError(f"Could not fetch data for {table_id} ({lang})")
    return jsonstat2_to_df(raw)


def save(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"  Saved {path} ({len(df)} rows)")


def process_indicators(table_id: str, dataset_id: str, time_col_en: str, time_col_mn: str):
    """Fetch indicator×time tables ensuring EN/MN row alignment via positional join."""
    print(f"=== {dataset_id} ===")
    en_raw = fetch("en", table_id)
    mn_raw = fetch("mn", table_id)

    def clean(df):
        df = df[[c for c in df.columns if df[c].nunique() > 1 or c == "value"]].copy()
        cols = [c for c in df.columns if c != "value"]
        df[cols[0]] = df[cols[0]].str.strip()
        return df

    en = clean(en_raw)
    mn = clean(mn_raw)

    # Both frames come from the same API in the same positional order — use that order
    # so numeric values align row-for-row. Add a positional key for merge.
    en = en.reset_index(drop=True)
    mn = mn.reset_index(drop=True)
    assert len(en) == len(mn), f"Row count mismatch: EN={len(en)}, MN={len(mn)}"
    assert (en["value"].values == mn["value"].values).all(), "Values differ between languages"

    en_cols = [c for c in en.columns if c != "value"]
    mn_cols = [c for c in mn.columns if c != "value"]

    en_out = en.rename(columns={en_cols[0]: "indicator", en_cols[1]: time_col_en, "value": "value_usd_mn"})
    mn_out = mn.rename(columns={mn_cols[0]: "үзүүлэлт", mn_cols[1]: time_col_mn, "value": "value_usd_mn"})

    save(en_out, OUT / f"{dataset_id}-en.csv")
    save(mn_out, OUT / f"{dataset_id}-mn.csv")


# ── 1. Annual trade indicators ─────────────────────────────────────────────
process_indicators("DT_NSO_1400_001V1_year.px", "nso-foreign-trade-annual", "year", "он")

# ── 2. Monthly trade indicators ────────────────────────────────────────────
process_indicators("DT_NSO_1400_003V1.px", "nso-foreign-trade-monthly", "month", "сар")

# ── 3+4. By-country exports and imports ────────────────────────────────────

TOP_N = 10


def process_by_country(table_id: str, dataset_id: str, val_en: str, val_mn: str):
    print(f"=== {dataset_id} ===")

    # Build EN→MN country map from API metadata (positional, not from data rows)
    api_en = NSO_API("en")
    meta_en = api_en.get_table_metadata(SECTOR, SUBSECTOR, table_id)
    api_mn = NSO_API("mn")
    meta_mn = api_mn.get_table_metadata(SECTOR, SUBSECTOR, table_id)

    country_var_en = next(v for v in meta_en["variables"] if "ountr" in v["text"] or "лс" in v["text"])
    country_var_mn = next(v for v in meta_mn["variables"] if "ountr" in v["text"] or "лс" in v["text"])
    en_meta_countries = [c.strip() for c in country_var_en["valueTexts"]]
    mn_meta_countries = [c.strip() for c in country_var_mn["valueTexts"]]
    en_to_mn = {e: m for e, m in zip(en_meta_countries, mn_meta_countries)}

    dfs = {lang: fetch(lang, table_id) for lang in ["en", "mn"]}

    # Use EN to select top-10 countries by most recent year
    en = dfs["en"].copy()
    cols = [c for c in en.columns if c != "value"]
    c_col, y_col = cols[0], cols[1]
    en[c_col] = en[c_col].str.strip()
    en[y_col] = en[y_col].astype(str)
    # Deduplicate: sum values for same (country, year) — handles API quirk of duplicate entries
    en = en.groupby([c_col, y_col], as_index=False)["value"].sum()

    most_recent = (en[en["value"].notna() & (en["value"] > 0)]
                   .groupby(y_col)["value"].sum().idxmax())
    print(f"  Most recent year: {most_recent}")

    top_en = (en[(en[y_col] == most_recent) & (~en[c_col].isin(SKIP_COUNTRIES))]
              .groupby(c_col)["value"].sum()
              .sort_values(ascending=False)
              .head(TOP_N).index.tolist())
    print(f"  Top-10: {top_en}")

    top_mn = [en_to_mn.get(c, c) for c in top_en]
    print(f"  Top-10 MN: {top_mn}")

    # Deduplicate MN
    mn_raw = dfs["mn"].copy()
    mc_col = mn_raw.columns[0]
    my_col = mn_raw.columns[1]
    mn_raw[mc_col] = mn_raw[mc_col].str.strip()
    mn_raw[my_col] = mn_raw[my_col].astype(str)
    mn = mn_raw.groupby([mc_col, my_col], as_index=False)["value"].sum()

    for lang, df_raw, top_list in [("en", en, top_en), ("mn", mn, top_mn)]:
        orig_cc = df_raw.columns[0]
        orig_yc = df_raw.columns[1]
        cc = "country" if lang == "en" else "улс"
        yc = "year" if lang == "en" else "он"
        vc = val_en if lang == "en" else val_mn

        # -all- CSV
        df_all = df_raw[~df_raw[orig_cc].isin(SKIP_COUNTRIES)].copy()
        df_all = df_all.rename(columns={orig_cc: cc, orig_yc: yc, "value": vc})
        df_all = df_all.sort_values([yc, cc]).reset_index(drop=True)
        save(df_all, OUT / f"{dataset_id}-all-{lang}.csv")

        # top CSV
        df_top = df_raw[df_raw[orig_cc].isin(top_list)].copy()
        df_top[orig_cc] = pd.Categorical(df_top[orig_cc], categories=top_list, ordered=True)
        df_top = df_top.sort_values([orig_yc, orig_cc]).reset_index(drop=True)
        df_top = df_top.rename(columns={orig_cc: cc, orig_yc: yc, "value": vc})
        save(df_top, OUT / f"{dataset_id}-{lang}.csv")


process_by_country("DT_NSO_1400_006V3.px", "nso-exports-by-country-top",
                   "exports_usd_mn", "экспорт_сая_ам_дол")
process_by_country("DT_NSO_1400_010V3.px", "nso-imports-by-country-top",
                   "imports_usd_mn", "импорт_сая_ам_дол")

print("\nAll done.")
