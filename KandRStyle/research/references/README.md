# Reference Tracking System for ut.tex URLs

This folder contains a reference tracking system for managing URL references found in the book manuscript (ut.tex).

## Quick Start

**New to this system?** See [QUICKSTART.md](QUICKSTART.md) for a beginner-friendly guide.

**Need to install Python dependencies?** See [SETUP.md](SETUP.md) for detailed installation instructions including troubleshooting for common issues like playwright installation errors.

**Quick verification:**
```bash
python verify_setup.py
```

## Contents

### Excel Workbook
- **Reference_Tracking.xlsx** - Main workbook with two sheets:
  - **Reference Tracking** - Master list of URLs with tracking information
    - ID: Unique identifier for each URL
    - URL: The complete URL
    - Accessed Date: The "Accessed" date extracted from ut.tex endnotes (used by Wayback Machine)
    - Status: "Stored" or "Not Found" indicating if we have a PDF copy
    - Notes: Additional information about the URL or download status
  - **URL Locations** - Shows where each URL appears in ut.tex
    - ID: Matches the ID in Reference Tracking sheet
    - URL: The complete URL
    - Line Numbers in ut.tex: Comma-separated list of line numbers where this URL appears

### Python Scripts

#### Core Scripts
- **create_reference_tracker.py** - Extracts URLs from ut.tex and creates the Reference_Tracking.xlsx workbook
  - Uses relative paths (../../ut.tex) so it works in any environment
  - Identifies all unique URLs and creates tracking sheets

#### Setup & Verification
- **requirements.txt** - List of all required Python packages
- **verify_setup.py** - Checks if all dependencies are installed correctly
- **SETUP.md** - Detailed setup guide with troubleshooting

#### Download Scripts
- **download_pdfs.py** - Simple downloader for the first 10 URLs
  - Basic script for quick testing
  - Downloads PDFs as ref_XXX.pdf

- **download_pdfs_range.py** - Advanced downloader with range and browser selection
  - Supports custom ranges (e.g., references 1-50)
  - Supports multiple browsers (chromium, firefox, webkit)
  - Command-line arguments for flexibility
  
- **download_wayback_pdfs.py** - Downloads from Internet Archive Wayback Machine
  - Uses "Accessed" dates from ut.tex to find appropriate snapshots
  - Falls back to latest snapshot with --force-latest flag
  - Saves as ref_XXX_wayback.pdf to distinguish from live downloads
  - Includes snapshot date in workbook notes

### PowerShell Scripts (Windows)
- **Download-References.ps1** - Windows automation for live URL downloads
  - Easy-to-use interface with range parameters
  - Automatic dependency checking and installation
  - Firefox support by default
  
- **Download-References-Wayback.ps1** - Windows automation for Wayback Machine downloads
  - Retrieves archived versions of URLs
  - Automatically extracts "Accessed" dates from ut.tex
  - Can specify custom date or use latest snapshots

## Installation

### Option 1: Using requirements.txt (Recommended)
```bash
# 1. Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# 2. Install all dependencies
python -m pip install -r requirements.txt

# 3. Install browsers
python -m playwright install firefox

# 4. Verify installation
python verify_setup.py
```

### Option 2: Manual installation
See [SETUP.md](SETUP.md) for detailed step-by-step instructions and troubleshooting.

## Statistics
- **Total unique URLs found:** 157
- **Total URL occurrences:** 254 (some URLs appear multiple times in the document)
- **URLs with "Accessed" dates:** 90 (extracted from ut.tex endnotes)

The "Accessed Date" column is crucial for Wayback Machine downloads - it tells the script which snapshot to retrieve.

## Usage

### Initial Setup - Generate the Workbook

```bash
cd KandRStyle/research/references
python3 create_reference_tracker.py
```

### Python Usage (Linux/Mac/Windows with Python)

#### Download live URLs (range with Firefox):
```bash
python3 download_pdfs_range.py --start 1 --end 10 --browser firefox
```

#### Download from Wayback Machine (uses "Accessed" dates from ut.tex):
```bash
python3 download_wayback_pdfs.py --start 1 --end 10 --browser firefox
```

#### Download from Wayback Machine (force latest if no accessed date):
```bash
python3 download_wayback_pdfs.py --start 1 --end 10 --force-latest
```

#### Download from Wayback Machine (specific date):
```bash
python3 download_wayback_pdfs.py --start 1 --end 10 --date 2026-07-12
```

### PowerShell Usage (Windows - Recommended)

#### Download live URLs:
```powershell
.\Download-References.ps1 -StartRef 1 -EndRef 10 -Browser firefox
```

#### Download all references (1-157):
```powershell
.\Download-References.ps1 -StartRef 1 -EndRef 157 -Browser firefox
```

#### Download from Wayback Machine:
```powershell
.\Download-References-Wayback.ps1 -StartRef 1 -EndRef 10 -Browser firefox
```

#### Download from Wayback Machine with specific date:
```powershell
.\Download-References-Wayback.ps1 -StartRef 1 -EndRef 10 -Date "2026-07-12"
```

#### Download from Wayback Machine, force latest if no accessed date:
```powershell
.\Download-References-Wayback.ps1 -StartRef 1 -EndRef 10 -ForceLatest
```

#### Skip dependency checking (faster if already installed):
```powershell
.\Download-References.ps1 -StartRef 1 -EndRef 10 -SkipSetup
```

**Note:** PowerShell scripts automatically check and install dependencies (Python packages, browsers)

## PDF Naming Convention

### Live URLs
PDFs from live downloads are named: `ref_XXX.pdf`

For example:
- ref_001.pdf corresponds to ID 1 (https://www.mybib.com)
- ref_002.pdf corresponds to ID 2 (http://php.net/manual/en/security.database.sql-injection.php)

### Wayback Machine URLs
PDFs from Wayback Machine are named: `ref_XXX_wayback.pdf`

For example:
- ref_001_wayback.pdf corresponds to ID 1 archived version
- ref_002_wayback.pdf corresponds to ID 2 archived version

The workbook Notes column includes the snapshot date for Wayback downloads.

## First 10 URLs Identified
1. https://www.mybib.com
2. http://php.net/manual/en/security.database.sql-injection.php
3. https://owasp.org/index.php/Top
4. https://www.scrt.ch/outils/mms/mms
5. https://www.youtube.com/watch?v=uK3
6. https://www.scrt.ch/en/
7. https://www.nist.gov/news-events/events/2017/03/cybersecurity-framework-virtual-events
8. http://faculty.ucmerced.edu/wshadish/shadish-cv-jan-2015
9. http://faculty.ucmerced.edu/wshadish/biosketch
10. http://www.ipr.northwestern.edu/workshops/annual-summer-workshops/quasi-experimental-design-and-analysis/

## When to Use Each Script

### Use Live Downloads (Download-References.ps1) when:
- URLs are still active and accessible
- You want the current version of the page
- The website hasn't changed significantly since citation

### Use Wayback Machine (Download-References-Wayback.ps1) when:
- Original URL no longer exists (404 errors)
- Website has changed significantly since citation
- You want the version that was accessed when writing the book
- You need to preserve the exact content that was referenced

### Wayback Machine Benefits:
- Retrieves content from URLs that no longer exist
- Gets the page as it appeared on the "Accessed" date from the workbook
- Falls back to ut.tex if accessed date not in workbook
- Creates a permanent archive reference
- Useful for academic citation verification

**How Accessed Dates Work:**
1. The script first checks the "Accessed Date" column in the workbook
2. If not found, it searches ut.tex for "Accessed DD Month YYYY" patterns
3. Uses that date to find the closest Wayback Machine snapshot
4. If no date found, use `--force-latest` to get the most recent snapshot

## Troubleshooting

### URLs Fail to Download
- Try the Wayback Machine version - many old URLs are archived
- Check if URL is still valid by visiting in a browser
- Some sites may block automated downloads

### "No accessed date" Errors
- Use the `--force-latest` flag to get the most recent snapshot
- Or specify a date with `--date YYYY-MM-DD`

### Browser Installation Issues
- The PowerShell script auto-installs browsers
- Manual install: `python -m playwright install firefox`

## Future Work
- The remaining 147 URLs (IDs 11-157) can be processed by modifying the download_pdfs.py script
- Consider adding a column for the date the PDF was downloaded
- Consider adding a checksum or hash for downloaded PDFs
- Implement retry logic for failed downloads
