# mrpam-commodity-prices

World market mineral commodity prices from MRPAM monthly reports.

## Dataset Info

| Field | Value |
|-------|-------|
| **Dataset ID** | `mrpam-commodity-prices` |
| **Source** | `mrpam` |
| **Source Tables** | 3.8 |
| **Update Frequency** | Monthly |

## Description

World market prices for key minerals including gold, silver, copper, zinc, coal, and others. Sourced from Table 3.8 of the MRPAM monthly statistical report.

## CSV Schema

### English (`mrpam-commodity-prices-en.csv`)
```
year,month,commodity,price,unit
2025,1,Gold,2650.5,USD/troy oz
2025,1,Copper,9100.0,USD/tonne
2025,1,Coal (coking),220.0,USD/tonne
```

### Mongolian (`mrpam-commodity-prices-mn.csv`)
```
он,сар,бараа,үнэ,нэгж
2025,1,Алт,2650.5,USD/тройн унц
2025,1,Зэс,9100.0,USD/тонн
```

## Extraction

```bash
conda run -n datamn python3 extract_tables.py --dataset mrpam-commodity-prices --year 2025
```

## Section Keywords

Search for pages containing: `дэлхийн зах зээл`, `3.8`, `алт`, `зэс`

## Common Commodity Names (MN → EN)

| Mongolian | English |
|-----------|---------|
| Алт | Gold |
| Мөнгө | Silver |
| Зэс | Copper |
| Цайр | Zinc |
| Хар тугалга | Lead |
| Нүүрс (коксжих) | Coal (coking) |
| Нүүрс (эрчим хүч) | Coal (thermal) |
| Хөнгөн цагаан | Aluminum |
| Никель | Nickel |
| Молибден | Molybdenum |
| Флюоршпат | Fluorspar |
