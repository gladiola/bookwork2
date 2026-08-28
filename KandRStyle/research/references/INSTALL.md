# Quick Installation Guide

## Prerequisites

- **Python 3.8 or higher** (Python 3.12+ recommended)
- Windows PowerShell or Command Prompt

## Step 1: Verify Python Installation

Open PowerShell and run:
```powershell
python --version
```

If you see "python is not recognized", Python is not in your PATH. See **Adding Python to PATH** below.

## Step 2: Add Python to PATH (if needed)

Choose one method:

### Method A: Re-run Python Installer (Easiest)
1. Find and re-run the Python installer
2. Select "Modify"
3. Ensure "Add Python to PATH" is checked
4. Complete the installation
5. **Restart PowerShell**

### Method B: Manual Configuration
1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", find "Path" and click "Edit"
5. Click "New" and add these paths (adjust Python version):
   ```
   C:\Users\gladi\AppData\Local\Programs\Python\Python312\
   C:\Users\gladi\AppData\Local\Programs\Python\Python312\Scripts\
   ```
6. Click OK on all dialogs
7. **Restart PowerShell**

### Method C: PowerShell Command (Run as Administrator)
```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\gladi\AppData\Local\Programs\Python\Python312\;C:\Users\gladi\AppData\Local\Programs\Python\Python312\Scripts\", "User")
```
Then **restart PowerShell**.

## Step 3: Install Dependencies

Navigate to the references directory and install:

```powershell
cd C:\Users\gladi\source\repos\bookWork2\KandRStyle\research\references

# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Install all dependencies
python -m pip install -r requirements.txt

# Install Playwright browsers (required for PDF downloads)
python -m playwright install firefox
```

## Step 4: Verify Installation

Run the verification script:

```powershell
python verify_setup.py
```

This will check that all required packages are installed and working correctly.

## What Gets Installed

The following packages will be installed:
- **openpyxl** (>=3.1.0) - Excel file handling
- **matplotlib** (>=3.7.0) - Data visualization
- **numpy** (>=1.24.0) - Numerical computing
- **requests** (>=2.31.0) - HTTP library
- **playwright** (>=1.40.0) - Browser automation for PDF downloads

## Troubleshooting

### "python is not recognized"
- Python is not in your PATH
- Follow Step 2 above to add Python to PATH
- Make sure to **restart PowerShell** after modifying PATH

### Package installation fails
```powershell
# Check Python version (must be 3.8+)
python --version

# Try upgrading pip again
python -m pip install --upgrade pip setuptools wheel

# Install packages one at a time to identify the problem
python -m pip install openpyxl
python -m pip install matplotlib
python -m pip install numpy
python -m pip install requests
python -m pip install playwright
```

### Playwright installation fails
```powershell
# Install Playwright package first
python -m pip install playwright

# Then install browsers
python -m playwright install firefox

# If that fails, try with chromium instead
python -m playwright install chromium
```

### Permission errors on Windows
- Run PowerShell as Administrator
- Or install packages just for your user:
  ```powershell
  python -m pip install --user -r requirements.txt
  ```

## Next Steps

After successful installation:
1. See `QUICKSTART.md` for how to use the reference tracking scripts
2. See `README.md` for detailed documentation
3. Run `python create_reference_tracker.py` to create a new reference tracking workbook

## Getting Help

If you encounter issues:
1. Check `PYTHON_VERSION_COMPATIBILITY.md` for detailed version information
2. Ensure your Python version is 3.8 or higher
3. Make sure all commands are run from the `KandRStyle/research/references` directory
