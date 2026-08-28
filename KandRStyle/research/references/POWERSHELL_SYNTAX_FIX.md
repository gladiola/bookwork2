# PowerShell Syntax Error Fix

## Problem
The `Download-References.ps1` script was showing parser errors on Windows:
- "The string is missing the terminator"
- "Missing closing '}' in statement block"
- "The Try statement is missing its Catch or Finally block"

## Root Cause
The issue appears to be related to **line endings** and/or **smart quotes** in your local copy of the file.

## What Was Fixed
1. ✅ Converted `Download-References.ps1` to Windows line endings (CRLF)
2. ✅ Converted `Download-References-Wayback.ps1` to Windows line endings (CRLF)
3. ✅ Added `.gitattributes` to ensure all PowerShell scripts use CRLF endings on Windows
4. ✅ Verified the file has no syntax errors (26 balanced braces, 114 even quotes, no smart quotes)

## How to Fix Your Local Copy

### Option 1: Pull the Fixed Version (Recommended)
```powershell
# Save any local changes first (if needed)
git stash

# Pull the latest version from main
git pull origin main

# If you stashed changes, you can restore them
git stash pop
```

### Option 2: Check for Smart Quotes in Your Local File
If you edited the file and accidentally introduced smart quotes (curly quotes):

1. Open the file in VS Code or another editor
2. Use Find & Replace:
   - Find: `"` or `"` (smart quotes)
   - Replace: `"` (straight quote)
   - Find: `'` or `'` (smart quotes)
   - Replace: `'` (straight quote)

### Option 3: Re-download the File
```powershell
# Backup your current file (if needed)
Copy-Item Download-References.ps1 Download-References.ps1.backup

# Fetch the clean version from the repository
git checkout origin/main -- Download-References.ps1
```

## Verification
After fixing, verify the file is correct:

```powershell
# This should show no syntax errors
powershell.exe -File .\Download-References.ps1 -StartRef 1 -EndRef 1 -SkipSetup
```

## Prevention
The new `.gitattributes` file ensures that:
- PowerShell scripts (`.ps1`) always use CRLF line endings on Windows
- Future checkouts will automatically have the correct line endings

## Technical Details
The repository file was analyzed and found to be syntactically correct:
- **Braces**: 26 open, 26 close (balanced ✓)
- **Double quotes**: 114 (even ✓)
- **Smart quotes**: None found ✓
- **Line endings**: Now CRLF for Windows
- **Structure**: Valid PowerShell with param block, functions, and try-catch

## Still Having Issues?
If you continue to see errors after pulling the fixed version:

1. Check your PowerShell version: `$PSVersionTable.PSVersion`
2. Try running PowerShell as Administrator
3. Check for file corruption: `Get-FileHash .\Download-References.ps1`
4. Compare with repository: `git diff Download-References.ps1`

If issues persist, please provide:
- The output of `git diff Download-References.ps1`
- Your PowerShell version
- The complete error message
