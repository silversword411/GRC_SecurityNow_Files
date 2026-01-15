# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Overview

This repository maintains a **Security Now! podcast transcript collection and processing pipeline**. It downloads episode transcripts from Steve Gibson's GRC website (grc.com), processes them with proper date metadata, and creates summarized/merged files compatible with Google NotebookLM (which has a 50-file limit and 500,000 word limit per file).

## Repository Structure

```
GRC_SecurityNow_Files/
├── episodes/                       # Raw transcript files (sn-001.txt to sn-NNNN.txt)
├── summarized/                     # Merged files for NotebookLM (<500K words each)
│   └── summarizedXXX-YYYY.zip      # Pre-packaged zip for distribution
├── zips/                           # Archive distributions of raw episodes
├── 1securitynow_download.py        # Stage 1: Download new episodes
├── 2securitynow_datefiles.py       # Stage 2: Fix file timestamps
├── 3securitynow_makesummary.py     # Stage 3: Create summarized bundles
├── update_securitynow.py           # Full pipeline automation script
└── README.md                       # Project documentation
```

## Quick Update (Recommended)

Use the automated pipeline script for updates:

```bash
# Check for new episodes
python update_securitynow.py --check

# Interactive update (prompts before downloading)
python update_securitynow.py

# Fully automatic update (no prompts)
python update_securitynow.py --auto
```

The script handles everything: downloading, timestamps, summaries, zip creation, and README updates.

---

## Manual Pipeline (Individual Scripts)

The scripts are numbered to indicate execution order:

### Stage 1: Download (`1securitynow_download.py`)
- Downloads episode transcripts from `https://www.grc.com/sn/sn-{:03d}.txt`
- **Before running:** Update `start_num` and `end_num` variables to specify episode range
- Saves to `episodes/` with naming pattern `sn-NNN.txt` or `sn-NNNN.txt`

### Stage 2: Date Fixing (`2securitynow_datefiles.py`)
- Parses `DATE:` field from transcript content
- Updates file timestamps to match episode broadcast date
- Run after downloading new episodes

### Stage 3: Summarization (`3securitynow_makesummary.py`)
- Merges episode files with 490,000-word maximum per output file
- Creates summary parts: `summary_sn-XXX_to_sn-YYY_partN.txt`
- Run to regenerate all summary files after adding episodes

## Updating to a New Episode

When a new Security Now! episode is released, follow this workflow:

### Step 1: Determine the latest episode number
Check https://www.grc.com/securitynow.htm or look at the highest episode in `episodes/`

### Step 2: Update and run the download script
```python
# In 1securitynow_download.py, update:
start_num = LAST_EPISODE + 1  # e.g., 1036
end_num = NEW_LATEST + 1      # e.g., 1037 (exclusive end)
```
Then run:
```bash
python 1securitynow_download.py
```

### Step 3: Fix file timestamps
```bash
python 2securitynow_datefiles.py
```

### Step 4: Regenerate summary files
```bash
python 3securitynow_makesummary.py
```

### Step 5: Update the summarized zip
Create a new zip file in `summarized/` containing all summary files:
```bash
# Update the zip filename to reflect the new episode range
# e.g., summarized001-1036.zip
```

### Step 6: Update README and commit
- Update the download link in README.md to point to the new summarized zip
- Commit with message: `Updating to episode NNNN`

## Key Commands

```bash
# Activate virtual environment (if using)
# Windows:
venv\Scripts\activate
# Linux/WSL:
source venv/bin/activate

# Install dependencies
pip install requests

# Run the full pipeline
python 1securitynow_download.py
python 2securitynow_datefiles.py
python 3securitynow_makesummary.py
```

## File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Episodes (1-999) | `sn-NNN.txt` | `sn-001.txt`, `sn-899.txt` |
| Episodes (1000+) | `sn-NNNN.txt` | `sn-1000.txt`, `sn-1035.txt` |
| Summary files | `summary_sn-XXX_to_sn-YYY_partN.txt` | `summary_sn-001_to_sn-066_part1.txt` |
| Summarized zip | `summarizedNNN-NNNN.zip` | `summarized001-1035.zip` |

## Current State

- **Latest Episode:** 1035
- **Summary Parts:** 30 files
- **Word Limit Per Summary:** 490,000 (below NotebookLM's 500,000 limit)

## Important Notes

- **Be respectful of grc.com** - Don't run downloads excessively
- The scripts use Python 3 with UTF-8 encoding
- Virtual environment (`venv/`) is gitignored
- Only `requests` library is needed beyond standard library

## Git Workflow

Typical commit messages follow the pattern:
- `Updating to episode NNNN` - When adding new episodes
- `Update download link in README for summarized zip file to NNNN` - When updating README
