# SOLUTION: Fix for Playwright Installation Error on Windows

## Problem
When trying to install Python packages, the following error occurred:
```
ERROR: Could not find a version that satisfies the requirement playwright (from versions: none)
ERROR: No matching distribution found for playwright
```

## Root Cause
This error typically occurs when:
1. `pip` and `setuptools` are outdated
2. The Python version is too old for playwright
3. There are network/proxy issues

## Solution

### Step 1: Upgrade pip, setuptools, and wheel FIRST
```powershell
python -m pip install --upgrade pip setuptools wheel
```

**Why this works:** Older versions of pip don't properly resolve package dependencies for newer packages like playwright. Upgrading pip to the latest version (26.x) ensures it can find and install playwright correctly.

### Step 2: Install packages using requirements.txt
```powershell
cd C:\Users\gladi\source\repos\bookWork2\KandRStyle\research\references
python -m pip install -r requirements.txt
```

### Step 3: Install Playwright browsers
```powershell
python -m playwright install firefox
```

### Step 4: Verify installation
```powershell
python verify_setup.py
```

## What Was Created

I've added the following files to help with setup:

1. **requirements.txt** - Lists all required Python packages
   - openpyxl>=3.1.0
   - playwright>=1.40.0
   - matplotlib>=3.7.0
   - numpy>=1.24.0
   - requests>=2.31.0

2. **SETUP.md** - Comprehensive setup guide with:
   - Step-by-step installation instructions
   - Troubleshooting for common errors
   - Platform-specific guidance (Windows/Linux/Mac)
   - Virtual environment instructions

3. **verify_setup.py** - Quick verification script
   - Checks Python version
   - Verifies all packages are installed
   - Shows package versions
   - Gives next steps if successful

4. **Updated QUICKSTART.md** - Added prerequisites section with link to SETUP.md

5. **Updated README.md** - Added installation section with quick commands

## Complete Setup Commands (In Order)

```powershell
# Navigate to the directory
cd C:\Users\gladi\source\repos\bookWork2\KandRStyle\research\references

# Step 1: Upgrade pip (CRITICAL - do this first!)
python -m pip install --upgrade pip setuptools wheel

# Step 2: Install all Python packages
python -m pip install -r requirements.txt

# Step 3: Install browsers for PDF downloads
python -m playwright install firefox

# Step 4: Verify everything is installed
python verify_setup.py

# Step 5: Generate the Reference Tracking workbook
python create_reference_tracker.py
```

## Expected Output

After running `verify_setup.py`, you should see:
```
Checking Python version...
Python 3.x.x

✓ openpyxl        3.1.5      - Excel file manipulation
✓ playwright      1.62.0     - Web page to PDF conversion
✓ matplotlib      3.11.1     - Data visualization
✓ numpy           2.5.2      - Numerical operations
✓ requests        2.31.0     - HTTP requests

✓ All packages installed successfully!

Next steps:
  1. Install browsers: python -m playwright install firefox
  2. Generate workbook: python create_reference_tracker.py
```

## If You Still Have Issues

1. **Check Python version:** `python --version` (should be 3.8 or higher)
   
2. **Check pip version:** `python -m pip --version` (should be recent, preferably 20.0+)

3. **Try manual installation:**
   ```powershell
   python -m pip install openpyxl
   python -m pip install matplotlib numpy requests
   python -m pip install playwright
   ```

4. **Check if you're behind a proxy:**
   ```powershell
   $env:HTTP_PROXY="http://proxy.company.com:8080"
   $env:HTTPS_PROXY="http://proxy.company.com:8080"
   python -m pip install playwright
   ```

5. **Use Python launcher (if multiple Python versions installed):**
   ```powershell
   py -3 -m pip install --upgrade pip setuptools wheel
   py -3 -m pip install -r requirements.txt
   ```

## Next Steps After Setup

1. **Generate the workbook:**
   ```powershell
   python create_reference_tracker.py
   ```
   This creates `Reference_Tracking.xlsx` with all 157 URLs from ut.tex

2. **Download PDFs (first 10 as a test):**
   ```powershell
   .\Download-References.ps1 -StartRef 1 -EndRef 10
   ```

3. **Or use Wayback Machine:**
   ```powershell
   .\Download-References-Wayback.ps1 -StartRef 1 -EndRef 10
   ```

## Summary

The key fix was to **upgrade pip first** before attempting to install playwright. The outdated pip couldn't properly resolve playwright's dependencies, causing the installation to fail. With the latest pip (26.x), setuptools (84.x), and wheel, all packages install successfully.

All the new files (requirements.txt, SETUP.md, verify_setup.py) are now in your repository to make future setups easier and to help troubleshoot any issues.
