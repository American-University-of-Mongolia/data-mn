# Dataset: University Graduates by Professional Field

## Identification

- **ID**: `nso-university-graduates-by-field`
- **Source**: `nso-1212`
- **Category**: Education
- **Type**: Parent dataset (not published directly)

## Source Reference

- **Table ID**: `DT_NSO_2001_014V1.px`
- **Title EN**: University and college graduates by professional field
- **Title MN**: Их, дээд сургуулийн төгсөгчид мэргэжлийн чиглэлээр

## Structure

The source contains annual graduate counts by professional field. The parent
preserves the complete bilingual NSO response and produces two published
datasets:

- `university-graduates-total` — the `Total` professional-field rows
- `university-graduates-by-field` — all professional fields except `Total`

## Update Instructions

1. Check `DT_NSO_2001_014V1.px` through the NSO 1212 API.
2. Compare its update timestamp with `source_updated_at` in the registry.
3. Fetch both English and Mongolian responses when the source changes.
4. Store the raw bilingual files under the next parent version directory.
5. Regenerate both child datasets, their XLSX downloads, charts, and bilingual
   MDX pages without changing their published slugs.

## Validation

- English and Mongolian parent files must have identical shapes and numeric
  values.
- Years must be four-digit calendar years.
- Graduate counts must be non-negative integers.
- Each year must have one `Total` row.
- The two published child datasets must retain their existing canonical URLs.

## Current Version

Version 1 contains six years of data through 2024. Its bilingual raw files are
stored in `tools/versions/nso-university-graduates-by-field/v1/`.
