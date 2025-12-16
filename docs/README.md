# Data.mn Documentation

This folder contains project documentation, principles, and architectural decisions for the data.mn platform.

## Start Here

| Document | Description |
|----------|-------------|
| **[Vision & Strategy](vision.md)** | Mission, target audience, principles, and roadmap |

## Contents

### Principles
Guiding principles that shape how the platform is built and maintained.

| Document | Description |
|----------|-------------|
| [URL Stability](principles/url-stability.md) | Rules for maintaining permanent, citable URLs |
| [Categories](principles/categories.md) | Canonical category system for organizing datasets |
| [Coverage Detection](principles/coverage-detection.md) | Finding related tables with different geographic coverage |

### Architecture
Technical architecture documentation.

| Document | Description |
|----------|-------------|
| [Data.mn Architecture](datamn-architecture.md) | Technical architecture, data flows, and system design |

### Postmortems
Lessons learned from incidents and debugging sessions.

| Document | Description |
|----------|-------------|
| [Validation Postmortem (Dec 2024)](validation-postmortem-2024-12.md) | Lessons from chart/data validation issues |

### Guides
How-to guides for common tasks.

*Coming soon* — See the main `CLAUDE.md` for workflow documentation in the meantime.

---

## Document Types

### Principles (`/principles`)
High-level philosophical guidelines that inform decision-making. These don't change frequently and represent core values of the platform.

Examples:
- URL stability
- Bilingual-first design
- Data versioning philosophy
- Citation and attribution standards

### Architecture (`/architecture`)
Technical documentation of system design, data flows, and infrastructure.

Examples:
- Registry database design
- Astro site structure
- Data pipeline architecture

### Guides (`/guides`)
Step-by-step instructions for common tasks.

Examples:
- Adding a new data source
- Publishing a dataset
- Handling deprecation

---

## Contributing

When adding documentation:

1. **Principles** should be timeless — avoid implementation details
2. **Architecture** should explain *why*, not just *what*
3. **Guides** should be actionable with copy-paste commands
4. Keep documents focused on one topic
5. Link between documents where relevant
