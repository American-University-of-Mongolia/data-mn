# nso-livestock-losses

**Source:** National Statistics Office of Mongolia, 1212.mn
**Category:** Agriculture / Хөдөө аж ахуй
**Frequency:** Annual
**Version 2:** All available loss years, 1971–2025, joined to 1970–2024 year-end herds
**Geography:** National control, 21 aimags and Ulaanbaatar
**Retrieved:** 2026-09-21

## Official tables

| Role | Table | Last source update | Unit |
|---|---|---|---|
| Adult livestock losses | `DT_NSO_1001_029V1.px` | 2026-08-26T15:47:59 | Thousand head |
| Year-end livestock | `DT_NSO_1001_021V1.px` | 2026-08-21T16:58:29 | Thousand head |

[Losses table](https://data.1212.mn/pxweb/en/NSO/NSO__Industry,%20service__Livestock/DT_NSO_1001_029V1.px/) · [Herd table](https://data.1212.mn/pxweb/en/NSO/NSO__Industry,%20service__Livestock/DT_NSO_1001_021V1.px/)

Metadata GET and data POST endpoint:

```text
https://data.1212.mn/api/v1/{lang}/NSO/Industry,%20service/Livestock/{table}
```

Fetch both `en` and `mn`. POST bodies are saved in the version's `raw/` directory; response format is `json-stat2`. Discover year selection codes from current metadata labels: code `0` is a moving year position, not a calendar year.

## Selection and joins

- `Малын төрөл`: codes `0`–`5` (total, horses, cattle, camels, sheep, goats).
- `Бүс`: code `0` for the national control and the 22 three-character aimag/capital codes. Capital code `511` is retained; duplicate capital regional total `5`, other regional group totals, soums and bags are excluded.
- Loss year `t` joins herd year `t − 1` using source region and animal codes. The EN herd endpoint currently supplies Mongolian region labels, so bilingual display labels come from the losses table. Trim source label whitespace.
- Each table/language extract contains 7,590 values: 55 years × 23 geographic units × 6 animal groups.

## Meaning and calculation

Adult livestock losses include losses from natural disasters, disease, predators and other causes. They exclude young animals born during the reporting year. These counts must not be described as deaths attributable exclusively to dzud.

```text
loss_rate_percent(t, region) =
  losses_thousand(t, region, total animals)
  / livestock_thousand(t − 1, region, total animals) × 100
```

The rate is calculated by Data.mn from two NSO tables; it is not a separately retrieved published rate. Preserve six decimal places in downloadable percentages. Counts retain the source's precision in thousand head; older years are rounded to one decimal and should not be presented as exact individual counts.

Preserve source nulls and status `..`; never convert them to zero. Version 2 contains 314 missing loss values and 207 missing opening-herd values in the full extract. A missing loss or missing/nonpositive denominator produces a blank rate. Of the exported regional observations, 25 loss counts and 30 rates are unavailable. National animal-type series contain no missing values.

Orkhon losses are unavailable in 1971–1975; Govisumber losses are unavailable in 1971–1990. In addition to those 25 missing observations, regional rates are unavailable for Orkhon in 1976 and 1980, Darkhan-Uul and Ulaanbaatar in 1980, and Govisumber in 1991 because the required previous-year herd is missing. Do not substitute the current year's herd or interpolate. Rankings exclude unavailable values. CSV and XLSX downloads retain their year/category rows with blank values.

Historical geography follows the source's current region labels; administrative boundaries changed over time. Do not assume today's boundaries applied throughout the series. The map uses present-day geometry for every selected year; it does not reconstruct historical borders. Available regional losses reconcile to the independent national total within 0.2 thousand head across all 55 years. The national total is a control and is not added to aimags.

The five national animal-type values do not exactly sum to the separately reported total in some historical years. Differences larger than the maximum 0.3-thousand one-decimal rounding tolerance occur in 1996 (+0.7), 1997 (−0.6), 1998 (+0.6), 1999 (−0.4), and 2005 (−0.6), in thousand head. Both language responses agree. These source discrepancies are preserved and recorded in `validation.json`; they are not corrected, scaled, or described as rounding errors.

## Outputs

| Dataset | Selection | Rows per language | Value |
|---|---|---:|---|
| `livestock-losses-by-aimag` | Total animals, 22 regions | 1,210 | Thousand head |
| `livestock-loss-rate-by-aimag` | Total animals, 22 regions | 1,210 | Percent |
| `livestock-losses-by-type` | National, five animal types | 275 | Thousand head |

CSV rows align by stable source codes in both languages. Both pages set `excelLanguage: page`: the EN page links `{id}-en.xlsx` with only the `English` sheet, and MN links `{id}-mn.xlsx` with only `Монгол`, with years down rows and categories across columns. Regional maps and rankings default to 2025. One year slider under the map updates both views across 1971–2025, including their displayed years and tooltips. Grey map regions are unavailable values; a zero remains a valid value. Colour bounds are derived from the full series and stay constant between years. The selection is retained when charts resize. Full CSV/XLSX downloads contain all 22 regions and all 55 years, retaining historical blanks. The type chart shows all five series. Maps reuse `public/maps/mongolia-aimags.json` and its existing attribution/license.

## Reproduction and refresh

From the repository root:

```bash
# Offline reproduction from the preserved, hash-checked v2 source:
python3 tools/scripts/build_livestock_losses.py

# Standard repository XLSX writer for future contributor refreshes:
python3 tools/scripts/rebuild_downloads.py --dataset livestock-losses-by-aimag --apply
python3 tools/scripts/rebuild_downloads.py --dataset livestock-loss-rate-by-aimag --apply
python3 tools/scripts/rebuild_downloads.py --dataset livestock-losses-by-type --apply
python3 tools/scripts/build_livestock_losses.py

# Register this contribution as pending, without publishing URLs:
python3 tools/scripts/register_livestock_losses.py

# Apply the site's formatting after regenerating JSON/MDX:
cd data.mn
npx prettier --write 'public/charts/livestock-loss*.json' 'src/data/data/{en,mn}/livestock-loss*.mdx'
```

The initial XLSX files were authored with the spreadsheet artifact tool, visually inspected in both languages, and verified cell-for-cell against the repository's canonical pivots. The canonical writer may change styling but preserves the same sheet data and download contract.

For a later source refresh, fetch into a **new version directory**, for example `python3 tools/scripts/fetch_livestock_losses.py --output tools/versions/nso-livestock-losses/v3/raw`. Omitting `--start` and `--end` discovers the full range from current loss-table metadata. The fetch validates that corresponding previous-year herd years exist. Update the builder/version metadata and date range deliberately; never overwrite earlier audit evidence. Automated updates and publication remain disabled until this custom two-table pipeline is reviewed. Before first deployment, run `registry publish` for the three page datasets, following the URL-stability policy.

Current evidence, query bodies, source metadata, hashes and numerical reconciliation are under `tools/versions/nso-livestock-losses/v2/`. Version 1 preserves the original 2010–2025 draft; every overlapping observation is unchanged in v2. CSVs are plain UTF-8: a byte-order mark would become part of the first column name in Vega's CSV loader.
