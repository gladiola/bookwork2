# Python Version Compatibility

## Current Status - Updated for Python 3.8+

The `requirements.txt` file has been updated to use **modern package versions** that require **Python 3.8 or higher**. Python 3.12 or 3.13 is recommended for best performance and security.

## Change History

### Previous Version (Python 3.6 Support)
The requirements.txt was previously constrained for Python 3.6.2 compatibility due to installation errors. Python 3.6 reached end-of-life in December 2021.

### Current Version (Python 3.8+ Support)
Now supports modern Python versions with the latest security fixes and features.

## Current Dependency Versions (Python 3.8+)

| Package | Version Constraint | Notes |
|---------|-------------------|-------|
| openpyxl | >=3.1.0 | Latest stable version with full feature support |
| matplotlib | >=3.7.0 | Requires Python 3.8+, recommended for data visualization |
| numpy | >=1.24.0 | Requires Python 3.8+, optimized for modern CPUs |
| requests | >=2.31.0 | Latest with security fixes |
| playwright | >=1.40.0 | Requires Python 3.8+, for browser automation |

## Python Version Requirements

### Minimum: Python 3.8
All packages in requirements.txt require **Python 3.8** or higher.

### Recommended: Python 3.12 or 3.13
For best experience, use **Python 3.12** or **Python 3.13**:
- **Performance**: Significant speed improvements (up to 25% faster than 3.10)
- **Security**: Active security patches and updates
- **Modern Features**: Latest language features and improvements
- **Long-term Support**: 
  - Python 3.12 is supported until October 2028
  - Python 3.13 is supported until October 2029

## Adding Python to PATH (Windows)

If Python is not in your PATH, you have several options:

### Option 1: Re-run Installer
1. Re-run the Python installer
2. Check "Add Python to PATH" during installation
3. Complete the installation

### Option 2: Manual PATH Configuration
1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", find "Path" and click "Edit"
5. Click "New" and add (adjust version number):
   - `C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python312\`
   - `C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python312\Scripts\`
6. Click OK on all dialogs
7. **Restart PowerShell** for changes to take effect

### Option 3: PowerShell Command (as Administrator)
```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python312\;C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python312\Scripts\", "User")
```

After adding to PATH, verify with:
```powershell
python --version
```

## Installation Instructions

With Python 3.8+ installed and in your PATH:

```powershell
# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
python -m pip install -r requirements.txt

# Install Playwright browsers (required for PDF download scripts)
python -m playwright install firefox
```

## Verifying Installation

After installation, verify everything works:

```powershell
cd KandRStyle/research/references
python verify_setup.py
```

## Troubleshooting

### "python is not recognized as an internal or external command"
- Python is not in your PATH. Follow the PATH instructions above.
- Make sure to restart PowerShell after modifying PATH.

### Package installation fails
- Ensure you're using Python 3.8 or higher: `python --version`
- Upgrade pip: `python -m pip install --upgrade pip setuptools wheel`
- Try installing packages individually to identify the problem

### Playwright installation fails
- Run: `python -m playwright install firefox`
- On Windows, you may need administrator privileges
- Ensure you have sufficient disk space (~200MB for Firefox)

## References

- [Python Download](https://www.python.org/downloads/)
- [Python 3.12 Release Schedule](https://peps.python.org/pep-0693/)
- [Python 3.13 Release Schedule](https://peps.python.org/pep-0719/)
- [Matplotlib Documentation](https://matplotlib.org/)
- [Playwright for Python](https://playwright.dev/python/)
