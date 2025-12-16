# /data-add - Add New Dataset

Add a new dataset to data.mn with quality validation.

## Workflow

### Phase 1: Discovery & Creation

1. **Select source type**: NSO (1212.mn), MRPAM, MongolBank, or new source
2. **Search/browse** available data using appropriate skill:
   - NSO: `datamn-source-nso` skill
   - Others: Source-specific skills or manual fetch
3. **Analyze data structure** and determine if splits are needed
4. **Create files**:
   - Fetch/transform data to CSV (EN + MN)
   - Generate XLSX (wide format)
   - Create Vega-Lite chart specs (EN + MN)
   - Generate MDX pages (EN + MN)
   - Register in database

### Phase 2: Quality Validation (NEW)

After creating all files, **spawn the checker subagent**:

```
Use Task tool with subagent_type='datamn-checker-worker':
- dataset_id: The ID you just created
- task: Validate against comprehensive checklist
```

The checker will return a detailed report with:
- Pass/fail status for all 85 checks
- Specific issues to fix
- Priority ordering (critical issues first)

### Phase 3: Fix Loop

1. Parse the checker report
2. Fix each issue in priority order:
   - **Critical**: Chart-CSV mismatches, whitespace issues (cause silent failures)
   - **Required**: Missing files, invalid fields, hover pattern issues
   - **Warnings**: Suggestions for improvement
3. Re-run checker
4. Repeat until all checks pass

### Phase 4: Finalize

Once checker reports all green:
1. Run full build: `cd data.mn && npm run build`
2. Preview: `npm run preview`
3. Deploy when ready: `kamal deploy`

## Checklist Reference

See `tools/config/data-page-checklist.md` for complete list of 85 checks.

## Key Quality Gates

These MUST pass before deployment:

### Critical (silent chart failures)
- [ ] 7.1-7.4: Chart-CSV color domain consistency
- [ ] 4.7-4.9: No whitespace in CSV categorical values
- [ ] 6.7-6.8: Chart data URL matches language

### Required (charts won't render correctly)
- [ ] 6.11-6.18: Hover point pattern for line/area charts
- [ ] 6.5-6.6: No hardcoded width/height
- [ ] 6.9: Year fields not ordinal type

### File completeness
- [ ] 1.1-1.7: All 7 files exist
- [ ] 2.14-2.21: dataFiles frontmatter correct

## Example Session

```
User: /data-add

Agent: What type of data source?
1. NSO (1212.mn) - National Statistics Office
2. MRPAM - Mining & Petroleum Authority
3. MongolBank - Bank of Mongolia
4. Other/New source

User: 1 (NSO)

Agent: [Uses datamn-source-nso skill to search]
       Found: GDP data, Population, Inflation...

User: GDP data

Agent: [Creates all 7 files]
       - gdp-nominal-en.csv, gdp-nominal-mn.csv
       - gdp-nominal.xlsx
       - gdp-nominal-en.json, gdp-nominal-mn.json
       - en/gdp-nominal.mdx, mn/gdp-nominal.mdx

       Now running quality checker...

       [Spawns datamn-checker-worker subagent]

Checker Report:
  ✓ 80/85 checks passed
  ✗ 5 issues found:

  Critical:
  - [6.15] Hover selection missing nearest: true

  Required:
  - [6.19] Legend orient should be "top"
  ...

Agent: Fixing 5 issues...
       [Makes edits]

       Re-running checker...

Checker Report:
  ✓ 85/85 checks passed

Agent: All quality checks passed! Dataset ready.

       Preview: cd data.mn && npm run dev
       Build: npm run build
       Deploy: kamal deploy
```

## Skills Used

- `datamn-source-nso` - Search and fetch NSO data
- `datamn-chart-vega` - Chart creation guidelines
- `datamn-page-mdx` - MDX page generation
- `datamn-registry` - Database registration

## Related Commands

- `/data-status` - View registry status
- `/data-update` - Check for updates
- `/data-batch` - Create multiple datasets