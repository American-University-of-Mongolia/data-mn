# Ralph Wiggum: Improve /data-add Process

This prompt is for iteratively improving the data-add workflow by:
1. Adding a test dataset
2. Running validation
3. **Editing the worker agents/skills** when failures occur (not just fixing output files)
4. Repeating until the PROCESS reliably produces passing datasets

---

## The Prompt

```
/ralph-wiggum:ralph-loop """

## Goal: Improve the /data-add Workflow

Your task is to IMPROVE the data-add process itself, not just add datasets.
When validation fails, you must edit the worker agents and skills to fix
the ROOT CAUSE, not just patch the output files.

### Files You May Edit (The Process)

These define how datasets are created:

| File | Purpose |
|------|---------|
| `data/.claude/commands/data-add.md` | Main slash command |
| `data/.claude/agents/datamn-dataset-worker.md` | Creates dataset files |
| `data/.claude/agents/datamn-discovery-worker.md` | Searches for data |
| `data/.claude/agents/datamn-checker-worker.md` | Validates datasets |
| `/.claude/skills/datamn-chart-vega/SKILL.md` | Chart creation rules |
| `/.claude/skills/datamn-page-mdx/SKILL.md` | MDX page generation |
| `/.claude/skills/datamn-transform-split/SKILL.md` | Data transformation |

### Test Dataset

Add: **unemployment-rate** from NSO 1212.mn

This tests:
- NSO API fetching
- Time series visualization
- Bilingual content generation
- All 52+ validation checks

### Process Each Iteration

1. **Run /data-add** to create the test dataset
   - Select NSO (1212.mn)
   - Search for DT_NSO_1200_013V5.px (NUMBER OF IMPORTED VEHICLES, by country, type of vehicle, and by year by Indicator and Year)
   - Create with appropriate title and splits

2. **Run validation**:
   bash
   cd data/tools && python tests/run_all_checks.py unemployment-rate 
   
3. **Analyze failures**:

   - If validation passes → SUCCESS, exit loop
   - If validation fails → identify ROOT CAUSE

4. **Fix the PROCESS, not just the output**:

   | Failure Type                   | Fix Location                           |
   | ------------------------------ | -------------------------------------- |
   | Missing hover layer in charts  | Edit `datamn-chart-vega/SKILL.md`      |
   | Wrong language in color domain | Edit `datamn-dataset-worker.md`        |
   | Whitespace in CSV values       | Edit `datamn-transform-split/SKILL.md` |
   | Bad excerpt text               | Edit `datamn-page-mdx/SKILL.md`        |
   | Missing tableId                | Edit `datamn-dataset-worker.md`        |
   | Category not translated        | Edit `datamn-page-mdx/SKILL.md`        |

5. **Delete the failed dataset files** to start fresh:

   bash
   rm -f data.mn/src/data/data/en/unemployment-rate.mdx
   rm -f data.mn/src/data/data/mn/unemployment-rate.mdx
   rm -f data.mn/public/datasets/unemployment-rate*.csv
   rm -f data.mn/public/datasets/unemployment-rate.xlsx
   rm -f data.mn/public/charts/unemployment-rate*.json
   

6. **Re-run /data-add** with improved process

### Example Fix

If check [6.11] fails (missing hover layer):

**DON'T** just add the hover layer to the output chart file.

**DO** edit `/.claude/skills/datamn-chart-vega/SKILL.md` to ensure ALL future
charts include the hover layer pattern:

markdown
## Required Chart Patterns

### Hover Layer (MANDATORY for line/area charts)

Every line or area chart MUST use a layered structure with hover:

\`\`\`json
{
  'layer': [
    { 'mark': 'area', ... },  // Main chart
    {
      'params': [{ 'name': 'hover', 'select': { 'type': 'point', 'nearest': true, ... }}],
      'mark': { 'type': 'point', ... },
      ...
    }
  ]
}
\`\`\`

### Success Criteria

The loop completes when:

- `python tests/run_all_checks.py unemployment-rate` returns 0 (all checks pass)
- The dataset was created by the IMPROVED process (not manually fixed)

### What You're Improving

Each iteration should make the process better:

- More robust worker agents
- Clearer skill instructions
- Better error prevention
- Consistent output quality

The goal is that FUTURE datasets created by /data-add will also pass all checks
without manual intervention.

""" --max-iterations 15
```

---

## Notes

- **Start clean**: Delete any existing unemployment-rate files before first run
- **Track changes**: Note which files you edited in each iteration
- **Test generalization**: After success, try adding a DIFFERENT dataset to verify improvements work broadly
- **Commit improvements**: After the loop succeeds, commit the agent/skill changes
