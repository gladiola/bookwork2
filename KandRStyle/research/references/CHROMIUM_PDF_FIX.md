# Fix: PDF Generation Requires Headless Chromium

## Problem
PDF generation was failing with the error:
```
Error: Page.pdf: PDF generation is only supported for Headless Chromium
```

This occurred because the scripts were configured to use Firefox by default, but Playwright's PDF generation feature **only works with headless Chromium**.

## Root Cause
According to Playwright documentation, the `page.pdf()` method is only supported in Chromium-based browsers. Firefox and WebKit do not support PDF generation.

## Solution
Updated all scripts and documentation to use Chromium as the default browser:

### Files Changed

1. **Download-References.ps1**
   - Changed default browser from `firefox` to `chromium`
   - Updated documentation to clarify PDF generation requirements
   - Added warning notes about browser compatibility

2. **Download-References-Wayback.ps1**
   - Changed default browser from `firefox` to `chromium`
   - Updated documentation to clarify PDF generation requirements
   - Added warning notes about browser compatibility

3. **SETUP.md**
   - Updated installation instructions to install Chromium: `python -m playwright install chromium`
   - Added prominent notes about PDF generation requirements
   - Updated all references from Firefox to Chromium

4. **verify_setup.py**
   - Updated recommended browser installation to Chromium
   - Added note about PDF generation compatibility

5. **download_pdfs_range.py**
   - Updated help examples to use Chromium
   - Default was already correct (chromium)

6. **download_wayback_pdfs.py**
   - Updated help examples to use Chromium
   - Default was already correct (chromium)

## How to Use

### Install Chromium Browser
```powershell
# Windows
python -m playwright install chromium

# Linux/Mac
python3 -m playwright install chromium
```

### Run Scripts (Default Now Uses Chromium)
```powershell
# PowerShell scripts now default to Chromium
.\Download-References.ps1 -StartRef 1 -EndRef 10

# Python scripts already defaulted to Chromium
python download_pdfs_range.py --start 1 --end 10
```

### Explicitly Specify Browser (Optional)
If you still want to use other browsers for testing (though PDF generation will fail):
```powershell
# PowerShell
.\Download-References.ps1 -StartRef 1 -EndRef 10 -Browser firefox

# Python
python download_pdfs_range.py --start 1 --end 10 --browser firefox
```

## Important Notes

1. **PDF Generation Only Works with Chromium**: Firefox and WebKit cannot generate PDFs in Playwright. Attempting to use them will result in the same error.

2. **Backward Compatibility**: The scripts still accept `firefox` and `webkit` as browser options to maintain backward compatibility, but they will fail for PDF generation.

3. **Headless Mode**: All browsers run in headless mode (no visible window) for automated PDF generation.

## Testing
After these changes:
- The default behavior now uses Chromium for PDF generation
- Users no longer need to explicitly specify `--browser chromium`
- Setup documentation guides users to install Chromium instead of Firefox

## Related Issue
This fix addresses the error reported in the problem statement where PDF generation was failing with Firefox browser.
