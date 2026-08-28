# Python Version Compatibility

## Current Status

The `requirements.txt` file has been updated to support **Python 3.6.2+** based on the installed Python version on the target system.

## Issue Background

When attempting to install dependencies with the original requirements.txt:
```
ERROR: Could not find a version that satisfies the requirement matplotlib>=3.7.0
```

This error occurred because:
- Python 3.6.2 was installed
- matplotlib 3.7.0+ requires Python 3.8+
- The highest matplotlib version available for Python 3.6 is 3.3.4

## Current Dependency Versions (Python 3.6-compatible)

| Package | Version Constraint | Reason |
|---------|-------------------|---------|
| openpyxl | >=3.0.0,<3.1.0 | 3.1.0+ requires Python 3.7+ |
| matplotlib | >=3.0.0,<3.4.0 | 3.4.0+ requires Python 3.7+; 3.7.0+ requires Python 3.8+ |
| numpy | >=1.19.0,<1.20.0 | 1.20.0+ requires Python 3.7+; 1.24.0+ requires Python 3.8+ |
| requests | >=2.28.0,<2.32.0 | 2.28.x is the highest Python 3.6-compatible version with security fixes |
| playwright | >=1.11.0,<1.20.0 | 1.20.0+ requires Python 3.7+; 1.40.0+ requires Python 3.8+ |

## Important Security Notice

⚠️ **Python 3.6 reached end-of-life in December 2021** and no longer receives security updates.

### Recommended Action: Upgrade Python

For better security, performance, and access to modern features, it is strongly recommended to upgrade to:
- **Python 3.11** or **Python 3.12** (recommended)
- Minimum: **Python 3.8** (for current dependency versions)

### Benefits of Upgrading

1. **Security**: Active security patches and updates
2. **Performance**: Significant speed improvements in Python 3.11+
3. **Modern Dependencies**: Access to latest package versions with bug fixes and features
4. **Long-term Support**: 
   - Python 3.11 is supported until October 2027
   - Python 3.12 is supported until October 2028

### If You Choose to Upgrade Python

Once you upgrade to Python 3.8+, you can update requirements.txt to:
```txt
openpyxl>=3.1.0
matplotlib>=3.7.0
numpy>=1.24.0
requests>=2.31.0
playwright>=1.40.0
```

## Installation Instructions

With the current Python 3.6-compatible requirements.txt:

```powershell
# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
python -m pip install -r requirements.txt

# Install Playwright browsers (if using playwright)
python -m playwright install firefox
```

## References

- [Python 3.6 End of Life](https://www.python.org/dev/peps/pep-0494/)
- [Matplotlib version compatibility](https://matplotlib.org/stable/users/installing/index.html)
- [NumPy version compatibility](https://numpy.org/doc/stable/release.html)
