# datamn-source-mongolbank

Skill for fetching data from the Bank of Mongolia (mongolbank.mn).

Base directory for this skill (repo-relative): `.claude/skills/datamn-source-mongolbank`

---

## Source Overview

| Field | Value |
|-------|-------|
| **Source ID** | `mongolbank` |
| **Name EN** | Bank of Mongolia |
| **Name MN** | Монголбанк |
| **Base URL** | https://www.mongolbank.mn |
| **Language** | Mixed — exchange rates are bilingual; statistics bulletins are Mongolian-only |
| **Update Frequency** | Exchange rates: daily; Monetary stats: monthly |

---

## Website Structure (2025+)

The Bank of Mongolia redesigned its website. Old `.aspx` URLs are 404. Use these paths:

| Data | Mongolian URL | English URL |
|------|--------------|-------------|
| Exchange rates (today) | `/mn/currency-rates` | `/eng/currency-rates` (may 404 — use MN) |
| Historical rates | `/mn/currency-rate-movement` | — |
| Monthly averages | `/mn/currency-rate-movement/monthly` | — |
| Statistics bulletins | `/mn/category/statistics` | `/eng/liststatbulletin.aspx` (may 404) |
| Monetary policy rate | `/mn/p/monetary-policy-rate` or in bulletin | — |

> **Note:** The English subdomain (`/eng/`) is inconsistent — some pages 404. Always try the Mongolian URL first, then apply translation workflow.

---

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `fetch_exchange_rates.py` | Download daily/historical exchange rates → bilingual CSVs |
| `fetch_bulletin_table.py` | Locate and parse statistics bulletin tables → bilingual CSVs |

---

## Data Access Methods

### Exchange Rates (Bilingual)

The exchange rates page (`/mn/currency-rates`) provides:
- **Today's closing rates** — all currencies vs MNT
- **Historical rates** tab — selectable date range
- **Excel download button** — "Excel татах"
- **PDF download button** — "PDF татах"

The Excel download is the preferred method. The page is JavaScript-rendered, so use the script:

```bash
cd .claude/skills/datamn-source-mongolbank
conda run -n datamn python3 fetch_exchange_rates.py --output /tmp/exchange-rates
```

Exchange rate data is inherently **bilingual** — currency codes (USD, EUR, CNY, RUB, JPY, KRW) are universal. The only translated field is the currency name. Use the translation map in this skill.

### Statistics Bulletins (Mongolian-only → requires translation)

Monthly PDF/Excel bulletins contain:
- Policy rate (бодлогын хүү)
- M1, M2 money supply
- Lending rates / deposit rates
- Credit to private sector

Use `fetch_bulletin_table.py` to locate and download the latest bulletin.

---

## Language Detection & Translation Flow

```
Fetch MongolBank data
        │
        ▼
Is source bilingual?
  ┌─────┴─────┐
  YES         NO (MN only)
  │           │
  ▼           ▼
Fetch EN    Fetch MN
+ MN        Extract table
  │         Translate headers + categorical values
  │         Save both -en.csv and -mn.csv
  └────┬────┘
       ▼
Save dataset-id-en.csv
     dataset-id-mn.csv
     dataset-id.xlsx
```

### When Translation IS Required (bulletins, statistics portal)

1. Extract data from Mongolian source
2. Save as `{id}-mn.csv`
3. Run translation:
   ```bash
   conda run -n datamn python3 tools/scripts/translate_csv.py {id}-mn.csv --from mn --to en -o {id}-en.csv
   ```
4. Validate: both CSVs must have identical row counts and numeric values

### When Translation is NOT Required (exchange rates)

Exchange rates use universal currency codes. Just map the MN currency name column to EN:

```python
CURRENCY_NAME_MAP = {
    "Америк доллар": "US Dollar",
    "Евро": "Euro",
    "Хятад юань": "Chinese Yuan",
    "Оросын рубль": "Russian Ruble",
    "Японы иен": "Japanese Yen",
    "Солонгосын вон": "South Korean Won",
    "Их Британийн фунт": "British Pound",
    "Австралийн доллар": "Australian Dollar",
    "Казахстаны тенге": "Kazakhstani Tenge",
    "Сингапурын доллар": "Singapore Dollar",
    "Гонконгийн доллар": "Hong Kong Dollar",
    "Канадын доллар": "Canadian Dollar",
    "Швейцарийн франк": "Swiss Franc",
    "Турк лир": "Turkish Lira",
}
```

---

## CSV Output Contract

All output CSVs must follow the data.mn bilingual contract:

### Exchange Rates CSV

**EN (`mongolbank-exchange-rates-daily-en.csv`)**:
```
date,currency_code,currency_name,rate_mnt
2025-01-15,USD,US Dollar,3450.25
2025-01-15,EUR,Euro,3720.10
...
```

**MN (`mongolbank-exchange-rates-daily-mn.csv`)**:
```
огноо,валютын_код,валютын_нэр,ханш_төгрөг
2025-01-15,USD,Америк доллар,3450.25
...
```

### Policy Rate CSV

**EN (`mongolbank-policy-rate-en.csv`)**:
```
date,policy_rate_pct
2020-01-01,11.0
2020-04-01,10.0
...
```

**MN (`mongolbank-policy-rate-mn.csv`)**:
```
огноо,бодлогын_хүү_хувь
2020-01-01,11.0
...
```

### Rules
- `date` column: ISO format `YYYY-MM-DD`
- Rates: numeric, no commas, no `%` symbol
- EN CSV: English column headers + English categorical values
- MN CSV: Mongolian column headers + Mongolian categorical values
- Numeric values MUST be identical in both CSVs

---

## Checking for Updates

### Exchange Rates
```bash
conda run -n datamn python3 fetch_exchange_rates.py --check-update
```
Compares latest date in saved CSV vs today's date. Returns `UPDATE_AVAILABLE` or `UP_TO_DATE`.

### Statistics Bulletins
```bash
conda run -n datamn python3 fetch_bulletin_table.py --check-update
```
Checks the bulletin listing page for the latest publication date.

---

## Column Name Translation Reference

| Mongolian | English |
|-----------|---------|
| огноо | date |
| ханш | exchange_rate |
| хүү | interest_rate |
| бодлогын хүү | policy_rate |
| зээлийн хүү | lending_rate |
| хадгаламжийн хүү | deposit_rate |
| мөнгөний нийлүүлэлт | money_supply |
| валют | currency |
| валютын код | currency_code |
| валютын нэр | currency_name |
| хаалтын ханш | closing_rate |
| нэгж | unit |
| сар | month |
| жил | year |

---

## Example: Fetch Exchange Rates

```bash
cd /Users/dlgvnbyr/Documents/internship/data-mn/.claude/skills/datamn-source-mongolbank

# Fetch last 5 years of USD, EUR, CNY, RUB, JPY, KRW
conda run -n datamn python3 fetch_exchange_rates.py \
  --currencies USD EUR CNY RUB JPY KRW \
  --start 2020-01-01 \
  --output /tmp/exchange-rates

# Output:
#   /tmp/exchange-rates/mongolbank-exchange-rates-daily-en.csv
#   /tmp/exchange-rates/mongolbank-exchange-rates-daily-mn.csv
```

## Example: Fetch Policy Rate (monthly indicator)

```bash
cd /Users/dlgvnbyr/Documents/internship/data-mn/.claude/skills/datamn-source-mongolbank

# Fetch policy rate history
conda run -n datamn python3 fetch_bulletin_table.py \
  --indicator policy-rate \
  --output /tmp/policy-rate

# Output:
#   /tmp/policy-rate/mongolbank-policy-rate-en.csv
#   /tmp/policy-rate/mongolbank-policy-rate-mn.csv
```

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| Page returns 404 | Try `/mn/` prefix instead of `/eng/` |
| JS-rendered page (no data in HTML) | Use `--use-playwright` flag; requires `playwright install chromium` |
| Excel download fails | Fall back to HTML table parsing with BeautifulSoup |
| MN-only source | Use `translate_csv.py` workflow above |
| Rate values have commas (1,234.56) | Script strips commas automatically |

---

## Dependencies

```
requests>=2.31.0
pandas>=2.0.0
beautifulsoup4>=4.12.0
openpyxl>=3.1.0
lxml>=4.9.0
playwright>=1.40.0  # optional, for JS-rendered pages
```

Install:
```bash
conda run -n datamn pip install beautifulsoup4 lxml playwright
conda run -n datamn playwright install chromium
```
