# Python Environment Setup Guide

This guide helps you set up Python and install the required dependencies for the reference tracking scripts.

## Prerequisites

- Python 3.8 or higher (Python 3.12 recommended)
- pip (Python package installer)
- Internet connection for downloading packages

## Quick Setup (Recommended)

### Step 1: Upgrade pip, setuptools, and wheel

**Windows (PowerShell):**
```powershell
python -m pip install --upgrade pip setuptools wheel
```

**Linux/Mac:**
```bash
python3 -m pip install --upgrade pip setuptools wheel
```

### Step 2: Install all Python packages

Navigate to the references directory:

**Windows:**
```powershell
cd C:\Users\gladi\source\repos\bookWork2\KandRStyle\research\references
python -m pip install -r requirements.txt
```

**Linux/Mac:**
```bash
cd KandRStyle/research/references
python3 -m pip install -r requirements.txt
```

### Step 3: Install Playwright browsers

**Windows:**
```powershell
python -m playwright install firefox
```

**Linux/Mac:**
```bash
python3 -m playwright install firefox
```

### Step 4: Verify installation

**Windows:**
```powershell
python -c "import openpyxl, playwright, matplotlib, numpy, requests; print('✓ All packages installed successfully')"
```

**Linux/Mac:**
```bash
python3 -c "import openpyxl, playwright, matplotlib, numpy, requests; print('✓ All packages installed successfully')"
```

## Troubleshooting

### Issue: "Could not find a version that satisfies the requirement playwright"

**Solution:** This typically happens when pip/setuptools are outdated. Fix it by:

1. **Upgrade pip first:**
   ```powershell
   python -m pip install --upgrade pip setuptools wheel
   ```

2. **Then try installing again:**
   ```powershell
   python -m pip install playwright
   ```

3. **Alternative:** Install packages one at a time:
   ```powershell
   python -m pip install openpyxl
   python -m pip install matplotlib numpy requests
   python -m pip install playwright
   ```

### Issue: "Python not found"

**Windows Solution:**
1. Download Python from https://www.python.org/downloads/
2. **IMPORTANT:** Check "Add Python to PATH" during installation
3. Restart PowerShell after installation
4. Verify: `python --version`

**Linux/Mac Solution:**
- Ubuntu/Debian: `sudo apt install python3 python3-pip`
- Mac: `brew install python3`

### Issue: "pip not found"

Use the module syntax instead:
```powershell
python -m pip install <package_name>
```

### Issue: "Permission denied" during installation

**Windows (PowerShell as Administrator):**
```powershell
python -m pip install -r requirements.txt
```

**Linux/Mac:**
```bash
python3 -m pip install --user -r requirements.txt
```

### Issue: Multiple Python versions installed

**Windows:**
Use the Python launcher to specify Python 3:
```powershell
py -3 -m pip install -r requirements.txt
```

**Linux/Mac:**
Explicitly use `python3`:
```bash
python3 -m pip install -r requirements.txt
```

### Issue: Playwright browser download fails

If `python -m playwright install firefox` fails:

1. **Check network/firewall:** Playwright downloads ~200MB
2. **Install specific browser:**
   ```powershell
   python -m playwright install chromium
   ```
3. **Use environment variable for proxy (if needed):**
   ```powershell
   $env:HTTPS_PROXY="http://proxy.company.com:8080"
   python -m playwright install firefox
   ```

### Issue: Scripts still can't find packages after installation

1. **Check which Python is running:**
   ```powershell
   where python
   python --version
   ```

2. **Check where packages were installed:**
   ```powershell
   python -m pip list
   ```

3. **Ensure you're using the same Python that has the packages:**
   ```powershell
   # If you installed with python3, run scripts with python3
   python3 create_reference_tracker.py
   ```

## Manual Package Installation

If you prefer to install packages individually:

```powershell
# Core Excel manipulation
python -m pip install openpyxl

# Web scraping and PDF generation
python -m pip install playwright

# Data visualization
python -m pip install matplotlib numpy

# HTTP requests
python -m pip install requests

# Install browser drivers
python -m playwright install firefox
```

## Verification Script

Create a file named `test_setup.py` with the following content:

```python
#!/usr/bin/env python3
"""Verify that all required packages are installed"""

import sys

packages = {
    'openpyxl': 'Excel file manipulation',
    'playwright': 'Web page to PDF conversion',
    'matplotlib': 'Data visualization',
    'numpy': 'Numerical operations',
    'requests': 'HTTP requests'
}

print("Checking Python version...")
print(f"Python {sys.version}")
print()

all_good = True
for package, description in packages.items():
    try:
        __import__(package)
        print(f"✓ {package:15s} - {description}")
    except ImportError:
        print(f"✗ {package:15s} - MISSING ({description})")
        all_good = False

if all_good:
    print("\n✓ All packages installed successfully!")
    print("\nNext step: Install browsers with:")
    print("  python -m playwright install firefox")
else:
    print("\n✗ Some packages are missing. Install them with:")
    print("  python -m pip install -r requirements.txt")
    sys.exit(1)
```

Run it with:
```powershell
python test_setup.py
```

## Package Versions

Minimum required versions:
- openpyxl >= 3.1.0
- playwright >= 1.40.0
- matplotlib >= 3.7.0
- numpy >= 1.24.0
- requests >= 2.31.0

Current tested versions (as of August 2026):
- openpyxl 3.1.5
- playwright 1.62.0
- matplotlib 3.11.1
- numpy 2.5.2
- requests 2.31.0

## Getting Help

If you continue to have issues:

1. Check Python version: `python --version` (should be 3.8+)
2. Check pip version: `python -m pip --version` (should be recent)
3. Try upgrading everything: `python -m pip install --upgrade pip setuptools wheel`
4. Search for the specific error message online
5. Consider using a virtual environment (see below)

## Using Virtual Environments (Optional but Recommended)

Virtual environments isolate your project dependencies:

**Windows:**
```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install packages
python -m pip install -r requirements.txt

# When done
deactivate
```

**Linux/Mac:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# When done
deactivate
```
