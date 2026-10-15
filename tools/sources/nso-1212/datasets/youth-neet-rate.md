# Mongolia youth NEET rate

- ID: `youth-neet-rate`
- Source: NSO Labour Force Survey, table `DT_NSO_0400_050V1.px`.
- API path: `Labour, business/Decent work/DT_NSO_0400_050V1.px`.
- Coverage: 2009–2025, annual; 170 observations for 10 groups per language.
- Unit: percent as published (9.1 means 9.1%).
- Work card: https://fizzy.aum.edu.mn/1/cards/191
- Status: pending review; automatic updates and publication disabled.

## Meaning and selection

NEET is the share of people aged 15–24 who are not in employment, education
or training. It includes people not seeking work and differs from unemployment.
Each subgroup uses its own youth population as the denominator; overlapping
categories must not be summed. Include all source groups: total, male, female,
urban, rural, Western, Khangai, Central, Eastern and Ulaanbaatar. Regional
observations are macroregions, not individual aimags.

The Mongolian display label for source Rural (code 4) is “Орон нутаг”, with
“Хот, орон нутаг” in the comparison control. This does not change the source
category to all places outside Ulaanbaatar. Raw NSO labels are preserved.

## Comparability

NSO revised its 2019–2023 estimates after updating survey weights in 2024.
The source also cites the labour-statistics methodology adopted in January
2019. Retain the published observations without interpolation or invented
corrections; trends alone do not establish the causes of changes.

## Charts and downloads

The trend chart switches between total/male/female and total/urban/rural.
Its opt-in comparison control follows the existing Data.mn bordered-control
style. Redrawing after a switch prevents stale legend widths; selections
persist across resizing. The regional chart has a year slider, a fixed 0–40%
axis, and one stable color per region in both languages.

CSV downloads contain all 170 rows irrespective of UI selections. Page-language
Excel files use 17 year rows and 10 group columns, with numeric percentage
values and no extra sheets. The EN/MN CSV rows align by year and source code.

## Reproduction and refresh

```bash
python tools/scripts/build_youth_neet.py
# Register the pending dataset and version once; does not publish.
python tools/scripts/build_youth_neet.py --register
python tools/tests/run_all_checks.py youth-neet-rate
python tools/scripts/validate_dataset.py --all youth-neet-rate --base-dir data.mn
cd data.mn && npm run build && npm run check
```

The offline builder checks SHA-256 hashes for metadata, query and JSON-stat2
responses in `tools/versions/youth-neet-rate/v1/raw/manifest.json`, validates
dimension ordering and complete coverage, and checks bilingual numeric parity.
It regenerates pages, charts, CSVs and canonical page-language XLSX files.
`--skip-excel` preserves the existing workbooks when only rebuilding charts or
page copy. The source snapshot date is 14 October 2026; the response's own
update timestamp is `2026-06-03T00:00:00Z`.

For refreshes, preserve v1. GET metadata from the API path above in both
languages, then POST the complete per-language query selecting every discovered
code with response format `json-stat2`. Review new years, dimension ordering,
source notes and revisions before archiving a new version with hashes and
updating coverage assertions. Do not infer positional year codes.

Source page: https://data.1212.mn/pxweb/en/NSO/NSO__Labour%2C%20business__Decent%20work/DT_NSO_0400_050V1.px/
