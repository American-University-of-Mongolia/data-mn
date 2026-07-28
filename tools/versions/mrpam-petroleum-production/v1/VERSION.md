# MRPAM Petroleum Production and Exports — Version 1

- Dataset: `mrpam-petroleum-production`
- Data period: January 2021 through June 2026
- Data as of: 2026-06-30
- Source: MRPAM monthly statistical reports, Tables 4.1 and 4.2
- Rows: 66
- Schema: `year`, `month`, `production_barrels`, `export_barrels`

The annual year-end reports were used for 2021–2025 so that the dataset
contains MRPAM's latest revisions for each completed year. The June report was
used for January–June 2026.

All 2021 production months are extractable. MRPAM reports no export value
(`-`) for December 2021. It likewise reports no export values for January
through May 2022; those six source-null values remain empty rather than being
invented or converted to zero.
