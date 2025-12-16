# Mongolbank - Bank of Mongolia

## Source Information

- **ID**: `mongolbank`
- **Name**: Bank of Mongolia
- **Name (MN)**: Монголбанк
- **URL**: https://www.mongolbank.mn
- **Type**: Mixed (API + PDF)
- **Update Frequency**: Daily/Weekly/Monthly (varies by data type)

## Data Categories

Mongolbank publishes various economic data:

1. **Exchange Rates** - Daily
2. **Interest Rates** - Monthly
3. **Monetary Statistics** - Monthly
4. **Banking Sector Statistics** - Monthly
5. **Balance of Payments** - Quarterly
6. **Economic Indicators** - Various frequencies

## Navigation Instructions

### Statistics Portal

The main statistics portal is at:
```
https://www.mongolbank.mn/eng/dbliststatisticsdate.aspx
```

Mongolian version:
```
https://www.mongolbank.mn/dbliststatisticsdate.aspx
```

### Exchange Rate Data

Official exchange rate page:
```
https://www.mongolbank.mn/eng/dblistofficialdailyrate.aspx
```

This page shows:
- Daily official exchange rates for major currencies
- Historical data by date selection

### Statistical Reports

Monthly statistical bulletin:
```
https://www.mongolbank.mn/eng/liststatbulletin.aspx
```

Contains comprehensive PDF reports with:
- Money supply (M1, M2)
- Credit to private sector
- Interest rates
- Inflation data

## Checking for Updates

### For Exchange Rates
1. Navigate to the exchange rate page
2. Check the date displayed (should be today or yesterday)
3. Compare with last fetched date

### For Monthly Statistics
1. Navigate to statistical bulletin page
2. Find the latest bulletin date
3. Compare with last fetched

## Data Extraction

### Exchange Rate Table
- Look for a table with currency codes (USD, EUR, CNY, etc.)
- Columns: Currency, Rate (MNT per unit)
- Date is usually in the page header

### Statistical Bulletin PDFs
- Download the latest PDF
- Extract relevant tables:
  - Money supply table
  - Interest rate table
  - Credit statistics

## Handling Page Changes

The Mongolbank website occasionally redesigns. If structure changes:

1. Look for "Statistics" (Статистик) in navigation
2. Look for "Exchange Rate" (Ханш) section
3. PDF bulletins usually maintain consistent format

## Key Mongolian Terms

- Ханш = Exchange rate
- Хүү = Interest rate
- Зээл = Credit/Loan
- Мөнгөний нийлүүлэлт = Money supply
- Инфляци = Inflation
- Төлбөрийн тэнцэл = Balance of payments

## Language Support

**Source Language**: Mixed (some English, some Mongolian)
**Translation Required**: Depends on dataset

MongolBank provides some data in both languages (exchange rates) and some data in Mongolian only (statistical bulletins).

### For Bilingual Datasets (e.g., Exchange Rates)
- English page: `https://www.mongolbank.mn/eng/...`
- Mongolian page: `https://www.mongolbank.mn/...`
- Fetch from both sources, no translation needed

### For Mongolian-Only Datasets (e.g., PDF Bulletins)
Follow the MRPAM translation workflow:

1. Extract data from Mongolian PDF/page
2. Translate using `tools/scripts/translate_csv.py`:
   ```bash
   python3 tools/scripts/translate_csv.py mongolbank-data-mn.csv --from mn --to en -o mongolbank-data-en.csv
   ```
3. Validate bilingual output
4. Save both versions

### Translation Mappings

**Column Names**:
- огноо → date
- ханш → exchange_rate
- хүү → interest_rate
- зээл → credit
- мөнгөний_нийлүүлэлт → money_supply
- инфляци → inflation
- валют → currency

**Common Values**:
- Америк доллар → US Dollar
- Евро → Euro
- Юань → Yuan
- Төгрөг → Tugrik
- Сар → Month
- Жил → Year

## Technical Notes

- Some pages use ASP.NET postbacks
- Historical data may require date selection forms
- Exchange rate API may be available (investigate)
- PDF bulletins are comprehensive but need parsing
- Check each dataset to determine if bilingual source or translation needed
