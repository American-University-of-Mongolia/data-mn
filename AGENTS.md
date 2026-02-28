# Repository Guidelines

## Scope

Data platform orchestration repository containing:

- `data.mn/` Astro website
- `tools/` registry, source definitions, validation/translation scripts
- project-local Codex skills in `.agents/skills`

## Instruction Chain

- This file controls repo-level workflow for `/Users/ritz/projects/data`.
- Additional app-specific rules live in `data.mn/AGENTS.md`.

## Skill Locations

- Codex project skills: `.agents/skills/`
- Claude compatibility path: `.claude/skills/`
- `.agents/skills` is linked to `.claude/skills` intentionally.

## Core Workflow Rules

- Use worker-oriented skills for discovery, dataset build, and validation.
- Treat registry and URL stability as first-class constraints.
- Never skip validation before considering dataset work complete.
- Keep generated artifacts and source-of-truth metadata consistent.

## Primary Scripts

```bash
python3 tools/scripts/validate_dataset.py --all <dataset_id>
python3 tools/scripts/validate_vega.py --all --data-root data.mn/public
python3 tools/scripts/validate_mdx_datafiles.py
python3 tools/scripts/translate_csv.py --help
```

## Data Safety

- Do not commit plaintext credentials.
- Use age-encrypted secret files and env vars only.

## Notes

- Existing `.claude/commands` and `.claude/agents` are retained for compatibility.
- Codex-native command workflows are implemented as skills and runner scripts.
