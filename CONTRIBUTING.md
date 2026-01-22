# Contributing to Data.mn

Welcome! This guide helps new contributors get up and running with the data.mn project. If you're new to Git or GitHub, don't worry—we'll walk through everything step by step.

## What is Data.mn?

Data.mn is Mongolia's open data platform. We collect publicly available statistics from sources like the National Statistics Office (NSO), Bank of Mongolia, and government ministries, then present them in an accessible, bilingual (English/Mongolian) format.

As a contributor, you'll help add new datasets, update existing ones, and improve the platform.

---

## Prerequisites

Before you start, install these tools:

| Tool | Purpose | How to Check |
|------|---------|--------------|
| **Git** | Version control | `git --version` |
| **Node.js 20+** | Website builds | `node --version` |
| **Conda/Miniconda** | Python environment | `conda --version` |
| **GitHub CLI (gh)** | Git operations from terminal | `gh --version` |
| **Claude Code** | AI-assisted development | `claude --version` |

### Installing Git

**macOS:**
```bash
xcode-select --install
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install git
```

**Arch Linux:**
```bash
sudo pacman -S git
```

**Windows:**
Download from [git-scm.com](https://git-scm.com/download/win)

After installing, configure your identity:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Installing Node.js

We recommend using nvm (Node Version Manager):

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Restart your terminal, then:
nvm install 20
nvm use 20
```

Or download directly from [nodejs.org](https://nodejs.org) (use the LTS version).

### Installing Conda

Download Miniconda from [docs.conda.io](https://docs.conda.io/en/latest/miniconda.html) and follow the installer.

After installation, restart your terminal and verify:
```bash
conda --version
```

### Installing GitHub CLI (gh)

The `gh` CLI makes Git operations much easier and enables Claude Code to help you with GitHub tasks.

**macOS:**
```bash
brew install gh
```

**Ubuntu/Debian:**
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh
```

**Arch Linux:**
```bash
sudo pacman -S github-cli
```

**Windows:**
```bash
winget install GitHub.cli
```

#### Authenticate with GitHub

After installing, log in to your GitHub account:

```bash
gh auth login
```

Follow the prompts:
1. Select **GitHub.com**
2. Select **HTTPS**
3. Select **Login with a web browser**
4. Copy the one-time code shown
5. Press Enter to open the browser
6. Paste the code and authorize

Verify it worked:
```bash
gh auth status
```

### Installing Claude Code

Claude Code is an AI assistant that understands this codebase and can help you with tasks.

```bash
npm install -g @anthropic-ai/claude-code
```

You'll need an Anthropic API key. Ask the project lead for access or sign up at [anthropic.com](https://www.anthropic.com).

---

## Getting the Code

### Step 1: Fork the Repository

A "fork" is your personal copy of the repository where you can make changes freely.

```bash
# This creates a fork under your GitHub account and clones it locally
gh repo fork datamn/data --clone
cd data
```

This command does three things:
1. Creates a copy (fork) of the repo in your GitHub account
2. Clones that fork to your computer
3. Sets up the connection to the original repo (called "upstream")

### Step 2: Set Up the Environment

```bash
# Create the Python environment
conda env create -f environment.yml
conda activate datamn

# Install website dependencies
cd data.mn
npm install
cd ..
```

### Step 3: Verify Everything Works

```bash
# Check registry (should show stats)
cd tools && python -m registry status && cd ..

# Start development server (should open at localhost:4321)
cd data.mn && npm run dev
```

Press `Ctrl+C` to stop the dev server.

---

## Git Basics

If you're new to Git, here's what you need to know:

### Key Concepts

| Term | What It Means |
|------|---------------|
| **Repository (repo)** | A project folder tracked by Git |
| **Commit** | A saved snapshot of your changes |
| **Branch** | A parallel version of the code for working on features |
| **Fork** | Your personal copy of someone else's repo |
| **Pull Request (PR)** | A request to merge your changes into the main project |
| **Origin** | Your fork on GitHub |
| **Upstream** | The original repo you forked from |

### The Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Create branch  →  2. Make changes  →  3. Commit        │
│         ↓                                      ↓            │
│  4. Push to your fork  →  5. Open PR  →  6. Get reviewed   │
│                                               ↓            │
│                                    7. Changes merged! 🎉    │
└─────────────────────────────────────────────────────────────┘
```

---

## Making Changes

### Step 1: Sync Your Fork

Before starting new work, make sure you have the latest code:

```bash
# Fetch latest from the original repo
gh repo sync

# Or manually:
git fetch upstream
git checkout main
git merge upstream/main
```

### Step 2: Create a Branch

Never work directly on `main`. Create a branch for your changes:

```bash
# Create and switch to a new branch
git checkout -b feature/my-new-dataset
```

Branch naming conventions:
- `feature/dataset-name` - Adding a new dataset
- `feature/description` - Adding a new feature
- `fix/issue-description` - Fixing a bug
- `docs/what-changed` - Documentation updates

### Step 3: Make Your Changes

Now you can edit files, add datasets, etc. Use Claude Code to help:

```bash
# Start Claude Code
claude

# Inside Claude Code, use commands like:
/data-add      # Add a new dataset
/data-status   # Check current status
```

### Step 4: Check Your Changes

See what you've changed:

```bash
git status           # List changed files
git diff             # Show line-by-line changes
```

### Step 5: Stage and Commit

"Staging" means selecting which changes to include in your commit:

```bash
# Stage specific files
git add path/to/file.csv
git add path/to/another-file.mdx

# Or stage all changes
git add .

# Commit with a descriptive message
git commit -m "Add unemployment rate dataset from NSO"
```

Write clear commit messages:
- ✅ "Add population pyramid dataset from NSO 1212.mn"
- ✅ "Fix chart axis labels for inflation data"
- ❌ "Updated stuff"
- ❌ "WIP"

### Step 6: Push to Your Fork

```bash
git push origin feature/my-new-dataset
```

If this is a new branch, Git will show a link to create a Pull Request.

---

## Opening a Pull Request

A Pull Request (PR) asks the maintainers to review and merge your changes.

### Using gh CLI (Recommended)

```bash
gh pr create --fill
```

This opens an editor to write your PR description. Include:

1. **What** you changed
2. **Why** you made this change
3. **Testing** you did to verify it works

Example:
```markdown
## Summary
- Add unemployment rate dataset from NSO 1212.mn
- Create bilingual CSVs (en/mn)
- Add area chart visualization

## Test Plan
- [x] Ran `npm run build` successfully
- [x] Validated charts with `validate_vega.py --all`
- [x] Checked both EN and MN pages render correctly
```

### Using GitHub Web Interface

1. Go to the original repo on GitHub
2. Click "Pull requests" → "New pull request"
3. Click "compare across forks"
4. Select your fork and branch
5. Fill in the description and submit

### After Submitting

- A maintainer will review your PR
- They may request changes—don't worry, this is normal!
- Make additional commits to address feedback
- Once approved, your changes will be merged

---

## Using Claude Code

Claude Code is your AI pair programmer. It understands this project's structure and can help with most tasks.

### Starting Claude Code

```bash
cd ~/path/to/data    # Navigate to the project root
claude               # Start Claude Code
```

### Key Commands

| Command | What It Does |
|---------|--------------|
| `/data-add` | Interactive wizard to add a new dataset |
| `/data-update` | Check and update existing datasets |
| `/data-status` | Show registry status and recent activity |
| `/data-validate` | Validate all charts and data files |

### Example Session

```
> claude

You: /data-add

Claude: I'll help you add a new dataset. What topic are you looking for?

You: Unemployment statistics

Claude: [Searches NSO 1212.mn, finds relevant tables, helps you create the dataset]
```

### How Skills Work

This project has custom "skills" that give Claude Code specialized knowledge:

| Skill | What It Knows |
|-------|---------------|
| `datamn-source-nso` | How to query the NSO 1212.mn API |
| `datamn-registry` | How to manage the dataset registry |
| `datamn-chart-vega` | How to create Vega-Lite charts |
| `datamn-page-mdx` | How to generate bilingual MDX pages |

These are automatically loaded when you run Claude Code from this directory.

### Tips

- **Be specific** - "Add the unemployment rate by age group from NSO" works better than "add some data"
- **Ask questions** - If you're unsure about something, ask Claude Code to explain
- **Review changes** - Always review what Claude Code creates before committing

---

## Code Standards

### Bilingual Requirement

**All datasets must have both English and Mongolian versions:**

- `dataset-name-en.csv` - English data
- `dataset-name-mn.csv` - Mongolian data
- `/en/data/dataset-name.mdx` - English page
- `/mn/data/dataset-name.mdx` - Mongolian page

### Before Submitting a PR

Run these checks:

```bash
# Validate all charts
cd data.mn && python3 ../tools/scripts/validate_vega.py --all

# Validate MDX data file references
python3 ../tools/scripts/validate_mdx_datafiles.py

# Build the site (must succeed)
npm run build
```

### URL Stability (Important!)

Once a dataset URL is published, it can never change or be deleted. People will link to these URLs in research papers and reports.

- ✅ Add new datasets
- ✅ Update data in existing datasets
- ❌ Delete published datasets
- ❌ Change URLs of published datasets

See `docs/principles/url-stability.md` for details.

---

## Project Structure

```
data/
├── .claude/              # Claude Code configuration
│   ├── skills/           # Project-specific knowledge
│   ├── commands/         # Slash commands
│   └── agents/           # Worker definitions
├── data.mn/              # Astro website
│   ├── src/data/data/    # MDX pages
│   │   ├── en/           # English pages
│   │   └── mn/           # Mongolian pages
│   └── public/
│       ├── datasets/     # CSV/XLSX downloads
│       └── charts/       # Vega-Lite JSON specs
├── tools/                # Python utilities
│   ├── registry/         # SQLite database
│   ├── scripts/          # Validation scripts
│   └── sources/          # Data source definitions
├── docs/                 # Documentation
├── CLAUDE.md             # AI assistant instructions
└── CONTRIBUTING.md       # This file
```

---

## Getting Help

1. **Check existing datasets** - Look at `data.mn/src/data/data/en/` for examples
2. **Read the docs** - `docs/` folder has detailed documentation
3. **Ask Claude Code** - It has context about this specific project
4. **Check skill files** - `.claude/skills/` explains how each component works

---

## Quick Reference

```bash
# Daily workflow
gh repo sync                              # Get latest changes
git checkout -b feature/my-feature        # Create branch
# ... make changes ...
git add .                                 # Stage changes
git commit -m "Description of changes"    # Commit
git push origin feature/my-feature        # Push
gh pr create --fill                       # Open PR

# Useful commands
git status                    # What's changed?
git log --oneline -5          # Recent commits
gh pr status                  # Your open PRs
gh pr view                    # View current PR

# Validation
cd data.mn
python3 ../tools/scripts/validate_vega.py --all
npm run build
```

---

Welcome to the team! 🇲🇳
