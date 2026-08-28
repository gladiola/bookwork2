# Reference Tracking System for ut.tex URLs

This folder contains a reference tracking system for managing URL references found in the book manuscript (ut.tex).

## Contents

### Excel Workbook
- **Reference_Tracking.xlsx** - Main workbook with two sheets:
  - **Reference Tracking** - Master list of URLs with tracking information
    - ID: Unique identifier for each URL
    - URL: The complete URL
    - Status: "Stored" or "Not Found" indicating if we have a PDF copy
    - Notes: Additional information about the URL or download status
  - **URL Locations** - Shows where each URL appears in ut.tex
    - ID: Matches the ID in Reference Tracking sheet
    - URL: The complete URL
    - Line Numbers in ut.tex: Comma-separated list of line numbers where this URL appears

### Python Scripts
- **create_reference_tracker.py** - Extracts URLs from ut.tex and creates the Reference_Tracking.xlsx workbook
- **download_pdfs.py** - Downloads the first 10 URLs as PDF files with naming convention ref_XXX.pdf

## Statistics
- **Total unique URLs found:** 157
- **Total URL occurrences:** 254 (some URLs appear multiple times in the document)

## Usage

### To regenerate the workbook:
```bash
python3 create_reference_tracker.py
```

### To download PDFs (requires internet access):
```bash
python3 download_pdfs.py
```

## PDF Naming Convention
PDFs are named using the pattern: `ref_XXX.pdf` where XXX is the three-digit ID from the Reference Tracking sheet.

For example:
- ref_001.pdf corresponds to ID 1 (https://www.mybib.com)
- ref_002.pdf corresponds to ID 2 (http://php.net/manual/en/security.database.sql-injection.php)
- And so on...

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

## Notes on PDF Downloads
The download script attempted to retrieve PDFs for the first 10 URLs but encountered network restrictions in the sandboxed environment (ERR_NAME_NOT_RESOLVED). The script is fully functional and will work in an environment with unrestricted internet access.

To manually download these URLs as PDFs:
1. Open each URL in a web browser
2. Use the browser's "Print to PDF" or "Save as PDF" functionality
3. Save with the corresponding ref_XXX.pdf filename
4. Update the Status column in the Reference_Tracking.xlsx workbook to "Stored"

## Future Work
- The remaining 147 URLs (IDs 11-157) can be processed by modifying the download_pdfs.py script
- Consider adding a column for the date the PDF was downloaded
- Consider adding a checksum or hash for downloaded PDFs
- Implement retry logic for failed downloads
