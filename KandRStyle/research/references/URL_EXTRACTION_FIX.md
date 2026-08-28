# URL Extraction Fix - August 2026

## Problem Statement

The reference tracking script was only finding 157 unique URLs from ut.tex, but there were actually more URLs that weren't being captured due to LaTeX escape sequences.

## Root Cause

The original URL extraction regex pattern `https?://[^\s}\]"\\]+` stopped at backslashes (`\`), which meant URLs containing LaTeX escape sequences like:
- `\#` (escaped hash for fragment identifiers)
- `\&` (escaped ampersand for query parameters)
- `\%` (escaped percent signs)

were being truncated. For example:
- `https://www.ic3.gov/Media/PDF/AnnualReport/2016State/StateReport.aspx\#?s=47` was cut off at `\#`
- `https://man.freebsd.org/cgi/man.cgi?query=zfs\&apropos=0\&sektion=0` was cut off at the first `\&`

## Solution

Updated `create_reference_tracker.py` to use a two-phase URL extraction approach:

1. **Phase 1**: Extract URLs from `\url{...}` LaTeX commands
   - Pattern: `\\url\{([^}]+)\}`
   - This preserves LaTeX escapes inside the command
   - More reliable as these are properly formatted URLs

2. **Phase 2**: Extract raw URLs from text
   - Pattern: `https?://[^\s}\]"\\]+` (original pattern)
   - Only processes text *after* removing `\url{}` commands to avoid duplicates

This approach ensures:
- URLs with LaTeX escapes are captured correctly
- No double-counting of URLs
- Both `\url{}`-wrapped and raw URLs are found

## Results

### Before Fix
- **Total unique URLs:** 157
- **Total URL occurrences:** 254
- **URLs with "Accessed" dates:** 90

### After Fix
- **Total unique URLs:** 192 (+35 URLs)
- **Total URL occurrences:** 377 (+123 occurrences)
- **URLs with "Accessed" dates:** 96 (+6 dates)

### Breakdown of Added URLs
- **28 unique URLs** with `\#` escape sequences (mostly IC3 annual reports)
- **7 unique URLs** with `\&` escape sequences (mostly FreeBSD man pages)
- These 35 URLs account for the increase from 157 to 192

## Files Modified

### Core Script
- `create_reference_tracker.py` - Updated URL extraction logic

### Documentation
- `README.md` - Updated statistics and examples
- `QUICKSTART.md` - Updated counts throughout
- `SOLUTION_PLAYWRIGHT_INSTALL_FIX.md` - Updated URL count

### PowerShell Scripts
- `Download-References.ps1` - Updated example and maximum reference count
- `Download-References-Wayback.ps1` - Updated example, validation, and maximum reference count

### Generated Files
- `Reference_Tracking.xlsx` - Regenerated with 192 URLs

## Verification

The fix was verified by:
1. Running the updated script and confirming 192 URLs extracted
2. Checking that URLs with `\#` escapes are properly captured (28 found)
3. Checking that URLs with `\&` escapes are properly captured (7+ found)
4. Confirming no duplicate URLs are created
5. Verifying the Excel workbook contains all 192 URLs with proper metadata

## Examples of Previously Missing URLs

### IC3 Annual Reports (with `\#`)
```
https://www.ic3.gov/Media/PDF/AnnualReport/2016State/StateReport.aspx\#?s=47
https://www.ic3.gov/Media/PDF/AnnualReport/2017State/StateReport.aspx\#?s=47
https://www.ic3.gov/Media/PDF/AnnualReport/2018State/StateReport.aspx\#?s=47
...
```

### FreeBSD Manual Pages (with `\&`)
```
https://man.freebsd.org/cgi/man.cgi?query=zfs\&apropos=0\&sektion=0\&manpath=FreeBSD+14.0-RELEASE
https://man.freebsd.org/cgi/man.cgi?query=zpool\&apropos=0\&sektion=0\&manpath=FreeBSD+14.0-RELEASE
https://man.freebsd.org/cgi/man.cgi?query=geli\&apropos=0\&sektion=0\&manpath=FreeBSD+14.1-RELEASE
...
```

## Note on Source Citations

The problem statement mentioned "hundreds of sources in ut.tex" - this is correct:
- **Total endnotes in ut.tex:** 395
- **URLs in endnotes:** 192 (now captured)
- **Non-URL sources:** 203 (books, journals, print materials without URLs)

The reference tracking system is designed specifically for web URLs that can be downloaded as PDFs. Print sources (books, academic journals, etc.) are properly cited in the manuscript but don't require PDF downloads.
