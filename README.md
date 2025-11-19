# Data Tools

A collection of Claude Code skills, scripts, and utilities for working with data, with a focus on Mongolia statistical data.

## Skills

### 1212.mn API Query Skill

Query Mongolia's National Statistical Office (NSO) open data API directly from Claude Code.

**Location**: `skills/1212mn-api/`

**Features**:
- Natural language queries for Mongolia statistical data
- Smart keyword matching with synonyms
- Local metadata caching for fast searches
- Access to 34+ sectors of statistical data
- Full-text search across all available tables

**Quick Start**:
```bash
cd skills/1212mn-api
python3 query_api.py --refresh   # Initialize metadata
python3 query_api.py --list      # List all tables
python3 query_api.py apartment price Sukhbaatar  # Query
```

**Use in Claude Code**:
Just ask questions about Mongolia statistics:
- "What is the average apartment price in Sukhbaatar district?"
- "Show me unemployment statistics"
- "What's the GDP growth rate?"

See [skills/1212mn-api/README.md](skills/1212mn-api/README.md) for detailed documentation.

## Installation

### Prerequisites
- Python 3.7+
- pip
- sqlite3

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd data-tools
   ```

2. **Install Python dependencies**:
   ```bash
   cd skills/1212mn-api
   pip install -r requirements.txt
   ```

3. **Initialize the 1212.mn skill**:
   ```bash
   python3 query_api.py --refresh
   ```

## Project Structure

```
data-tools/
├── README.md              # This file
├── skills/                # Claude Code skills
│   └── 1212mn-api/       # Mongolia NSO API query skill
│       ├── SKILL.md      # Skill definition
│       ├── query_api.py  # Main query module
│       ├── examples.py   # Example usage
│       ├── README.md     # Skill documentation
│       └── metadata/     # Cached metadata (generated)
└── scripts/              # Utility scripts (future)
```

## Usage with Claude Code

This repository is designed to work seamlessly with Claude Code. The skills in the `skills/` directory are automatically available when you're working in this repository.

### Example Session

```
You: What's the average apartment price in Sukhbaatar?

Claude: Let me query the 1212.mn database for apartment prices...
[Uses 1212mn-api skill]

The NSO database shows:
- Average price per square meter for new apartments in Sukhbaatar:
  MNT 5.61 million/sqm (as of February 2025)
- Average price per square meter for old apartments in Sukhbaatar:
  MNT 5.67 million/sqm (as of February 2025)

Note: The data provides price per square meter, not total apartment price.
```

## Data Sources

### 1212.mn (Mongolia NSO)
- **Website**: https://1212.mn
- **API Documentation**: http://opendata.1212.mn/en/doc
- **Coverage**: 34+ sectors including demographics, economy, housing, employment, health, education, and more
- **Update Frequency**: Varies by dataset (monthly, quarterly, annual)
- **Language**: English and Mongolian

## Contributing

Contributions are welcome! This repository is intended to grow with more skills and tools for data analysis.

### Adding New Skills

1. Create a new directory under `skills/`
2. Add a `SKILL.md` file with proper frontmatter
3. Include a `README.md` with documentation
4. Add your skill logic (Python, shell scripts, etc.)
5. Update this README

### Roadmap

Potential future additions:
- [ ] Data visualization tools
- [ ] Export utilities (CSV, Excel, JSON)
- [ ] Time series analysis helpers
- [ ] Additional data source integrations
- [ ] Data cleaning and transformation scripts
- [ ] Mongolian language support
- [ ] Geographic data mapping tools

## Maintenance

### Updating Metadata

The 1212.mn skill caches metadata locally. Refresh periodically:

```bash
cd skills/1212mn-api
python3 query_api.py --refresh
```

Recommended refresh schedule:
- **Monthly**: For general use
- **Weekly**: If you need the latest datasets
- **On-demand**: When NSO announces new data releases

## Troubleshooting

### Python Dependencies
```bash
pip install --upgrade -r skills/1212mn-api/requirements.txt
```

### Database Issues
If the SQLite database becomes corrupted:
```bash
rm skills/1212mn-api/metadata/tables.db
python3 skills/1212mn-api/query_api.py --refresh
```

### API Access Problems
- Check internet connection
- Verify API is accessible: `curl http://opendata.1212.mn/api/Sector?type=en`
- Some networks may block Mongolia domains
- API might be temporarily unavailable

## License

This project is provided as-is for working with publicly available data sources.

## Links

- **Claude Code Documentation**: https://code.claude.com/docs
- **1212.mn NSO**: https://1212.mn
- **Open Data Portal**: http://opendata.1212.mn

## Acknowledgments

- Mongolia National Statistical Office for providing open data access
- Anthropic for Claude Code and the Agent SDK

---

**Last Updated**: November 2025
