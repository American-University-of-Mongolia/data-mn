# Data.mn Documentation Architecture

This document maps how commands, agents, and skills relate to each other in the streamlined data.mn system.

## Visual Flowchart

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              USER ENTRY POINTS (Slash Commands)                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│   /data-add              /data-batch              /data-update           /data-status   │
│   (Interactive)          (Bulk creation)          (Check & refresh)      (View only)    │
│        │                       │                        │                      │        │
└────────┼───────────────────────┼────────────────────────┼──────────────────────┼────────┘
         │                       │                        │                      │
         ▼                       ▼                        ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          COMMAND FILES (.claude/commands/) - ORCHESTRATION ONLY         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  data-add.md            data-batch.md           data-update.md         data-status.md   │
│  ┌──────────────┐       ┌──────────────┐        ┌──────────────┐       ┌────────────┐   │
│  │• User flow   │       │• Input parsing│       │• Discovery   │       │• Registry  │   │
│  │• Source      │       │• Parallel     │       │  phase       │       │  queries   │   │
│  │  selection   │       │  spawning     │       │• Batch       │       │            │   │
│  │• Split       │       │              │        │  execution   │       │            │   │
│  │  planning    │       │              │        │• Summary     │       │            │   │
│  │• Spawn agent │       │              │        │              │       │            │   │
│  └──────────────┘       └──────────────┘        └──────────────┘       └────────────┘   │
│         │                      │                       │                               │
│         └──────────────────────┼───────────────────────┘                               │
│                                │                                                        │
│                                │ spawns (Task tool)                                     │
│                                ▼                                                        │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        AGENT FILE (.claude/agents/) - SINGLE WORKER                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  datamn-dataset-worker.md (AUTO-LOADED when spawned via Task tool)                      │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │ Complete, self-contained worker with:                                           │   │
│  │ • Brand compliance (colors, typography)                                         │   │
│  │ • Step-by-step workflow (fetch → transform → chart → MDX → registry)            │   │
│  │ • Chart templates (area, line, bar - with layered hover)                        │   │
│  │ • XLSX pivot export code                                                        │   │
│  │ • Validation commands                                                           │   │
│  │ • WORKER_RESULT format                                                          │   │
│  │                                                                                 │   │
│  │ References skills for: translations, detailed templates, export functions      │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                         │
│  datamn-discovery-worker.md (read-only searches)                                        │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │ • Search sources for datasets                                                   │   │
│  │ • Check for updates (no modifications)                                          │   │
│  │ • Analyze table structure                                                       │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ references
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         SKILLS (.claude/skills/) - REFERENCE KNOWLEDGE                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │ datamn-page-mdx     │  │ datamn-chart-vega   │  │ datamn-transform-   │              │
│  │ ═══════════════════ │  │ ═══════════════════ │  │ split               │              │
│  │ SINGLE SOURCE OF    │  │ • Full chart        │  │ ═══════════════════ │              │
│  │ TRUTH FOR:          │  │   templates         │  │ • CSV vs XLSX       │              │
│  │ • ALL translations  │  │ • Brand colors      │  │   formats           │              │
│  │   (tags, axis,      │  │ • Validation rules  │  │ • export_all_files()│              │
│  │   categories, etc.) │  │ • Responsive sizing │  │ • Pivot logic       │              │
│  │ • MDX templates     │  │                     │  │ • Filter functions  │              │
│  │ • Source names      │  │                     │  │                     │              │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘              │
│                                                                                         │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │ datamn-source-nso   │  │ datamn-registry     │  │ datamn-extract-pdf  │              │
│  │ ─────────────────── │  │ ─────────────────── │  │ ─────────────────── │              │
│  │ • API endpoints     │  │ • CLI commands      │  │ • pdfplumber usage  │              │
│  │ • query_api.py      │  │ • Python API        │  │ • Table extraction  │              │
│  │ • fetch_data.py     │  │ • Status values     │  │                     │              │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘              │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Layered Architecture Principle

| Layer | Purpose | Auto-Loaded? | Contains |
|-------|---------|--------------|----------|
| **Commands** | User entry, orchestration | Yes (on `/command`) | Workflow phases, user interaction, agent spawning |
| **Agents** | Self-contained task execution | Yes (on Task tool call) | Complete step-by-step instructions |
| **Skills** | Reusable reference knowledge | Yes (model-discovered) | Templates, translations, code patterns |

## Key Design Decisions

### 1. Single Worker Agent

Instead of separate `data-add-worker.md` and `data-update-worker.md` files (which weren't auto-loaded anyway), we have ONE comprehensive agent:

**`datamn-dataset-worker.md`** handles both create and update workflows because they're nearly identical:
- Fetch/load data
- Transform and export (CSV long form, XLSX pivot form)
- Generate charts
- Create MDX pages
- Update registry

### 2. Single Source of Truth for Translations

All translation tables live in **`datamn-page-mdx`**:
- Tag translations (mongolia → монгол)
- Axis/legend translations (Year → Он)
- Category translations (Male → Эрэгтэй)
- Source names
- Download button text

Other files reference this skill instead of duplicating tables.

### 3. Skills Are Auto-Discovered

Claude automatically loads skills when their `description` matches the task. The agent file includes explicit callouts:

```markdown
**→ See the `datamn-page-mdx` skill for the complete translation reference tables**
```

This makes skill usage explicit while leveraging auto-discovery.

## File Inventory

### Commands (Orchestration)
| File | Lines | Purpose |
|------|-------|---------|
| `data-add.md` | ~720 | Interactive dataset creation |
| `data-batch.md` | ~270 | Bulk creation with parallel workers |
| `data-update.md` | ~480 | Check and refresh datasets |
| `data-status.md` | ~50 | View registry status |

### Agents (Execution)
| File | Lines | Purpose |
|------|-------|---------|
| `datamn-dataset-worker.md` | ~800 | Create/update single dataset |
| `datamn-discovery-worker.md` | ~150 | Search and check sources (read-only) |

### Skills (Reference)
| File | Key Content |
|------|-------------|
| `datamn-page-mdx` | **ALL translations**, MDX templates, categories |
| `datamn-chart-vega` | Vega-Lite templates, brand colors, validation |
| `datamn-transform-split` | CSV/XLSX export logic, filter functions |
| `datamn-registry` | CLI commands, Python API |
| `datamn-source-nso` | NSO API access, query scripts |
| `datamn-extract-pdf` | PDF table extraction |

## Quick Reference: What to Edit

| Change Needed | Edit This File |
|---------------|----------------|
| User workflow or interaction | Command file (`data-add.md`, etc.) |
| Dataset creation/update steps | Agent (`datamn-dataset-worker.md`) |
| Translation tables | **Only** `datamn-page-mdx` |
| Chart styling or templates | `datamn-chart-vega` |
| CSV/XLSX export format | `datamn-transform-split` |
| Registry CLI usage | `datamn-registry` |

## Spawning Workers

Commands spawn the dataset worker like this:

```
Task tool:
  subagent_type: "datamn-dataset-worker"
  prompt: |
    Create dataset with parameters:
    - DATASET_ID: weekly-beef-prices
    - SOURCE_ID: nso-1212
    - TITLE_EN: "Weekly Beef Prices by Region"
    - TITLE_MN: "Бүс нутгаар үхрийн махны долоо хоногийн үнэ"
    - CATEGORY_EN: "Economy"
    - CATEGORY_MN: "Эдийн засаг"
    - CHART_TYPE: multi-line
    ...
```

The agent file is automatically injected into the subagent's context.
