---
name: datamn-extract-pdf
description: Extract tabular data from PDF documents. Use when downloading and parsing PDF reports from government agencies like MRPAM, ministries, or when data is only available in PDF format. Uses Playwright MCP for navigation and pdfplumber for extraction.
dependencies:
  - python3
  - pdfplumber
  - requests
---

# PDF Data Extraction Skill

Extract tabular data from PDF documents for data.mn.

## Overview

Many Mongolian government data sources publish reports as PDF documents rather than structured data. This skill provides patterns for:
1. Navigating to PDF download pages
2. Downloading PDF files
3. Extracting tables from PDFs
4. Cleaning and structuring the data

## Prerequisites

```bash
pip install pdfplumber requests
```

## Workflow

### 1. Navigate and Download

Use Playwright MCP tools to navigate to the source page and find PDF links:

```
# Example: MRPAM Monthly Report
1. browser_navigate to https://mrpam.gov.mn/page/714
2. browser_snapshot to capture page content
3. Identify the latest report link (look for date patterns)
4. Download PDF to data/tools/downloads/
```

### 2. Extract Tables

```python
import pdfplumber
import pandas as pd

def extract_tables_from_pdf(pdf_path):
    """Extract all tables from a PDF."""
    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_tables = page.extract_tables()
            for table in page_tables:
                if table:  # Skip empty tables
                    tables.append({
                        "page": i + 1,
                        "data": table
                    })

    return tables

# Extract tables
tables = extract_tables_from_pdf("report.pdf")

# Convert first table to DataFrame
if tables:
    df = pd.DataFrame(tables[0]["data"][1:], columns=tables[0]["data"][0])
```

### 3. Clean Data

```python
def clean_table(df):
    """Clean extracted table data."""

    # Remove empty rows
    df = df.dropna(how='all')

    # Remove empty columns
    df = df.dropna(axis=1, how='all')

    # Strip whitespace from string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()

    # Convert numeric columns
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col].str.replace(',', '').str.replace(' ', ''))
        except (ValueError, AttributeError):
            pass  # Keep as string

    return df
```

## Common Patterns

### Pattern 1: Monthly Report with Single Table

```python
def extract_monthly_report(pdf_path, table_page=1):
    """Extract the main data table from a monthly report."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[table_page - 1]
        tables = page.extract_tables()

        if not tables:
            raise ValueError(f"No tables found on page {table_page}")

        # Usually the first or largest table
        main_table = max(tables, key=lambda t: len(t) if t else 0)

        return pd.DataFrame(main_table[1:], columns=main_table[0])
```

### Pattern 2: Multi-Page Table

```python
def extract_multipage_table(pdf_path, start_page, end_page):
    """Extract a table that spans multiple pages."""
    all_rows = []
    header = None

    with pdfplumber.open(pdf_path) as pdf:
        for i in range(start_page - 1, end_page):
            page = pdf.pages[i]
            tables = page.extract_tables()

            if tables:
                table = tables[0]  # Assume one table per page

                if header is None:
                    header = table[0]
                    all_rows.extend(table[1:])
                else:
                    # Skip header row on continuation pages
                    all_rows.extend(table[1:])

    return pd.DataFrame(all_rows, columns=header)
```

### Pattern 3: Table with Merged Cells

```python
def extract_with_merged_cells(pdf_path, page_num):
    """Handle tables with merged header cells."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num - 1]

        # Use custom table settings
        table = page.extract_table({
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "snap_tolerance": 3,
        })

        # Handle None values from merged cells
        for row in table:
            last_value = None
            for i, cell in enumerate(row):
                if cell is None:
                    row[i] = last_value
                else:
                    last_value = cell

        return pd.DataFrame(table[1:], columns=table[0])
```

## Table Detection Settings

pdfplumber supports various settings for table detection:

```python
table_settings = {
    # Detection strategy
    "vertical_strategy": "lines",  # or "text", "explicit"
    "horizontal_strategy": "lines",

    # Tolerance for line detection
    "snap_tolerance": 3,
    "join_tolerance": 3,

    # Edge detection
    "edge_min_length": 3,

    # Text settings
    "text_tolerance": 3,
    "text_x_tolerance": 3,
    "text_y_tolerance": 3,
}

tables = page.extract_tables(table_settings)
```

## Handling Mongolian Text

PDF extraction usually handles Unicode correctly, but some issues may occur:

```python
def fix_mongolian_text(text):
    """Fix common Mongolian text encoding issues."""
    if text is None:
        return None

    # Replace known problematic characters
    replacements = {
        '\ufeff': '',  # BOM
        '\u200b': '',  # Zero-width space
        '\xa0': ' ',   # Non-breaking space
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()
```

## Output Format

After extraction, save data in standard format:

```python
def save_extracted_data(df, dataset_id, output_dir="data/tools/downloads"):
    """Save extracted data with metadata."""
    import json
    from datetime import datetime

    # Save CSV
    csv_path = f"{output_dir}/{dataset_id}.csv"
    df.to_csv(csv_path, index=False)

    # Save metadata
    metadata = {
        "dataset_id": dataset_id,
        "extracted_at": datetime.utcnow().isoformat(),
        "row_count": len(df),
        "columns": list(df.columns),
        "source_type": "pdf"
    }

    metadata_path = f"{output_dir}/{dataset_id}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    return csv_path
```

## Debugging Extraction

### Visualize Table Detection

```python
def debug_table_detection(pdf_path, page_num):
    """Create debug image showing detected tables."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num - 1]

        # Get page image with table lines highlighted
        img = page.to_image(resolution=150)
        img.debug_tablefinder()
        img.save(f"/tmp/debug_page_{page_num}.png")
```

### Check Raw Text

```python
def get_page_text(pdf_path, page_num):
    """Get raw text from a page for debugging."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num - 1]
        return page.extract_text()
```

## Common Issues

### Issue: No tables detected
**Solutions:**
1. Try different detection strategies (lines, text, explicit)
2. Check if tables use borders or whitespace separation
3. Use `debug_tablefinder()` to visualize detection

### Issue: Columns misaligned
**Solutions:**
1. Adjust `snap_tolerance` and `join_tolerance`
2. Use explicit line coordinates if table structure is known
3. Post-process with column mapping

### Issue: Merged cells cause issues
**Solutions:**
1. Identify header row structure manually
2. Forward-fill None values
3. Custom column mapping after extraction

### Issue: Numbers extracted as text
**Solutions:**
1. Remove thousand separators (`,`)
2. Handle Mongolian number formats
3. Use `pd.to_numeric(errors='coerce')`

## Notes

- Always save the original PDF for reference
- Log extraction metadata for reproducibility
- Validate extracted data against expected structure
- Handle both English and Mongolian text
- PDF structure can change between reports - build in flexibility
