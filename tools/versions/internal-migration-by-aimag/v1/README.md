# Migration snapshot v1

Official bilingual NSO metadata, full queries and data are preserved in `raw/`.
`manifest.json` records retrieval provenance and hashes; the builder verifies
them before generating files. The chart CSVs and long download CSVs are retained
here alongside the national-balance audit in `validation.json`.

See `tools/sources/nso-1212/datasets/internal-migration-by-aimag.md` for selection,
limitations and refresh procedure. Run `python tools/scripts/build_internal_migration.py`
from the repository to rebuild without network access. This snapshot is pending
review, not a claim of publication or historical comparability.
