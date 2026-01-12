# Data Status Command

Show current status of all data sources and datasets in the registry.

## Steps

1. **Run registry status**:
   ```bash
   cd tools && python -m registry status
   ```

2. **Run registry sources** to see source details:
   ```bash
   cd tools && python -m registry sources
   ```

3. **List datasets** if any exist:
   ```bash
   cd tools && python -m registry list
   ```

4. **Summarize** for the user:
   - How many sources are configured
   - How many datasets are being tracked
   - Which datasets need updates (status = 'outdated')
   - Recent activity

## Optional: Detailed Status

If user wants more detail on a specific dataset:
```bash
cd tools && python -m registry info DATASET_ID
```

## Quick View

For a quick summary, show:

| Category | Count |
|----------|-------|
| Sources | N enabled |
| Datasets | N total |
| Active | N |
| Pending | N |
| Outdated | N |

## Notes

- Run from the `data/` directory
- The registry database is at `tools/registry/data.db`
- Source definitions are in `tools/sources/{source-id}/`
