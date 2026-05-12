# Monthly Average Nominal Wages by Occupation and Sex

## Source Table
- **Table ID**: `DT_NSO_0400_025V1.px`
- **Sector**: Labour, business
- **Subsector**: Wages
- **Parent**: MONTHLY AVERAGE NOMINAL WAGES, by occupation and gender

## API Path
```
GET /api/v1/{lang}/NSO/Labour%2C%20business/Wages/MONTHLY%20AVERAGE%20NOMINAL%20WAGES%2C%20by%20occupation%20and%20gender/DT_NSO_0400_025V1.px
```

Note: The CSV response uses Windows-1252 content-type header but is actually UTF-8 BOM encoded. Use `post.content.decode('utf-8-sig')` to parse correctly.

## Dimensions
1. **Sex** (Хүйс): National average (Бүгд), Female (Эмэгтэй), Male (Эрэгтэй)
2. **Occupation classification** (Ажил мэргэжлийн ангилал): 11 categories including National average
3. **Year** (Annual): 2001-2025

## Occupation categories (EN)
- National average
- Managers
- Professionals
- Technicians and associate professionals
- Clerical support workers
- Service and sales workers
- Skilled agricultural, forestry and fishery workers
- Craft and related trades workers
- Plant and machine operators, and assemblers
- Elementary occupations
- Armed forces occupations

## Dataset: nso-wages-by-occupation-sex
- **Chart CSV**: Latest year (2025), Male and Female only, all occupations except National average
- **All CSV**: All years, all sex categories, all occupations (long format)
- **Chart**: Grouped horizontal bar chart, occupations sorted by descending male wages
- **Rows (chart)**: 10 occupations x 2 sexes = 20
- **Rows (all)**: 11 occupations x 3 sexes x 25 years = 789 (after dropping NaN)

## Values
- Unit: MNT thousands (1000s)
- Monthly average nominal wages
