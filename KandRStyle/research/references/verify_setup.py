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
        mod = __import__(package)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {package:15s} {version:10s} - {description}")
    except ImportError:
        print(f"✗ {package:15s} {'MISSING':10s} - {description}")
        all_good = False

if all_good:
    print("\n✓ All packages installed successfully!")
    print("\nNext steps:")
    print("  1. Install browsers: python -m playwright install chromium")
    print("     NOTE: PDF generation only works with Chromium, not Firefox or WebKit")
    print("  2. Generate workbook: python create_reference_tracker.py")
    sys.exit(0)
else:
    print("\n✗ Some packages are missing. Install them with:")
    print("  python -m pip install --upgrade pip setuptools wheel")
    print("  python -m pip install -r requirements.txt")
    sys.exit(1)
