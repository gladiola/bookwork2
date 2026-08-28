# Quick Start Guide - Reference URL Tracking System

## What This System Does

This system helps you:
1. Track all 157 URLs referenced in your book (ut.tex)
2. Download web pages as PDFs for archival purposes
3. Use the Internet Archive's Wayback Machine for URLs that no longer exist
4. Organize everything in an Excel workbook

## The Files

### Excel Workbook
**Reference_Tracking.xlsx** - Your central tracking system with:
- ID numbers for each URL (1-157)
- The actual URLs
- **Accessed Date** - When you accessed the page (from ut.tex)
- Status - Whether you have a PDF ("Stored" or "Not Found")
- Notes - Additional info about each download

### Scripts

**For Windows (PowerShell) - EASIEST:**
- `Download-References.ps1` - Download live URLs
- `Download-References-Wayback.ps1` - Download from Internet Archive

**For Python (any OS):**
- `create_reference_tracker.py` - Creates the Excel workbook
- `download_pdfs_range.py` - Downloads live URLs
- `download_wayback_pdfs.py` - Downloads from Wayback Machine

## Getting Started - Windows Users

### Step 1: Generate the Workbook (One Time)
```powershell
cd KandRStyle\research\references
python create_reference_tracker.py
```

This creates Reference_Tracking.xlsx with all 157 URLs and their accessed dates.

### Step 2: Download PDFs

#### Option A: Try Live URLs First (for newer references)
```powershell
.\Download-References.ps1 -StartRef 1 -EndRef 10
```

#### Option B: Use Wayback Machine (for older or missing URLs)
```powershell
.\Download-References-Wayback.ps1 -StartRef 1 -EndRef 10
```

### Step 3: Check Results
- PDFs are saved in the same folder as the scripts
- Live downloads: `ref_001.pdf`, `ref_002.pdf`, etc.
- Wayback downloads: `ref_001_wayback.pdf`, `ref_002_wayback.pdf`, etc.
- Workbook Status column updates automatically

## Common Usage Patterns

### Download First 10 References
```powershell
.\Download-References.ps1 -StartRef 1 -EndRef 10
```

### Download References 20-30
```powershell
.\Download-References.ps1 -StartRef 20 -EndRef 30
```

### Download ALL References (this will take a while!)
```powershell
.\Download-References.ps1 -StartRef 1 -EndRef 157
```

### Download Using Wayback Machine (for old URLs)
```powershell
.\Download-References-Wayback.ps1 -StartRef 1 -EndRef 10
```

### Force Latest Wayback Snapshot (if no accessed date)
```powershell
.\Download-References-Wayback.ps1 -StartRef 1 -EndRef 10 -ForceLatest
```

### Skip Setup Checks (faster if you've already run it once)
```powershell
.\Download-References.ps1 -StartRef 11 -EndRef 20 -SkipSetup
```

## How the "Accessed Date" Feature Works

1. **In ut.tex**, many citations include "Accessed DD Month YYYY"
   - Example: "Accessed 12 July 2026"

2. **The workbook generator** extracts these dates automatically
   - Stored in column C of Reference_Tracking.xlsx
   - You can see and edit them manually if needed

3. **The Wayback Machine script** uses these dates to find the right version
   - First checks the workbook's "Accessed Date" column
   - Falls back to searching ut.tex if not in workbook
   - Finds the closest snapshot to that date in the Internet Archive

4. **Result**: You get the web page as it appeared when you originally accessed it!

## Understanding the Results

### Status Column Values:
- **"Not Found"** - No PDF downloaded yet (initial state)
- **"Stored"** - PDF successfully downloaded
- **"Not Found" with error** - Download failed (URL dead, timeout, etc.)

### Notes Column Shows:
- Filename: `Saved as ref_005.pdf`
- Wayback date: `(Wayback: 2026-07-12)`
- Error messages if download failed

## Troubleshooting

### "Python not found"
1. Install Python from https://www.python.org/downloads/
2. Check "Add Python to PATH" during installation
3. Restart PowerShell

### URLs Failing to Download
- **Live URL fails**: Try the Wayback Machine version
- **Wayback fails**: URL may never have been archived
- **Some succeed, some fail**: This is normal - run multiple times

### "No accessed date" Errors
```powershell
# Use --ForceLatest to get the newest snapshot
.\Download-References-Wayback.ps1 -StartRef 1 -EndRef 10 -ForceLatest
```

### Browser Installation Hangs
- The first run downloads Firefox (or Chromium)
- This can take 5-10 minutes
- Be patient, it only happens once

## Tips for Best Results

1. **Start small**: Test with 10 URLs first
2. **Try live first**: Modern URLs usually work
3. **Use Wayback for older URLs**: Anything pre-2020
4. **Run in batches**: Do 20-30 at a time, not all 157 at once
5. **Check the workbook**: Review Status column after each run
6. **Retry failures**: Some URLs timeout but work on retry

## Advanced: Batch Processing Strategy

```powershell
# References 1-50: Newer content, try live first
.\Download-References.ps1 -StartRef 1 -EndRef 50

# Check workbook, identify failures

# Retry failures with Wayback
.\Download-References-Wayback.ps1 -StartRef 1 -EndRef 50

# References 51-100: Older content
.\Download-References-Wayback.ps1 -StartRef 51 -EndRef 100

# References 101-157: Oldest content
.\Download-References-Wayback.ps1 -StartRef 101 -EndRef 157
```

## File Naming

- `ref_001.pdf` - Live download of URL #1
- `ref_001_wayback.pdf` - Wayback download of URL #1
- Both can exist for the same URL!

## Questions?

- Check README.md for detailed documentation
- Review the workbook to see which URLs have accessed dates
- Most errors are from dead URLs - Wayback Machine is your friend!
