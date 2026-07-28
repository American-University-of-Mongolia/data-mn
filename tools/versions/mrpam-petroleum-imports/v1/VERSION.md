# MRPAM Petroleum Product Imports — Version 1

- Dataset: `mrpam-petroleum-imports`
- Data period: January 2021 through June 2026
- Data as of: 2026-06-30
- Source: MRPAM monthly statistical reports, Table 4.3
- Full rows: 570
- Chart rows: 396
- Full schema: `year`, `month`, `product`, `volume_t`

The full downloads preserve every source product position for all 66 monthly
reports, including the historical A-80 and AI-98 columns and the Euro-5
gasoline and diesel columns introduced in 2026.

The source reports 21 missing product values. Those cells remain empty rather
than being shifted to another product or converted to zero. The chart combines
regular and Euro-5 values for AI-92 and diesel, excludes Total, A-80, and AI-98,
and uses six lines. Its June 2026 AI-95 value remains empty and appears as a
line gap.
