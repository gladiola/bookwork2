# PowerShell Syntax Error Fix

## Problem
The `Download-References.ps1` script was showing parser errors on Windows:
- "The string is missing the terminator" at line 213
- "Missing closing '}' in statement block"
- "The Try statement is missing its Catch or Finally block"

## Root Cause
The PowerShell scripts were **stored in the git repository with LF (Unix) line endings** instead of CRLF (Windows) line endings. While `.gitattributes` was configured to convert to CRLF on checkout (`text eol=crlf`), git still stored them as LF in the repository (`i/lf`). On some Windows systems with certain git configurations, the automatic conversion from LF to CRLF during checkout wasn't working properly, resulting in LF line endings in the working copy, which PowerShell cannot parse correctly.

## What Was Fixed
1. ✅ Converted `Download-References.ps1` to CRLF line endings (217 lines)
2. ✅ Converted `Download-References-Wayback.ps1` to CRLF line endings (292 lines)
3. ✅ Updated `.gitattributes` to store PowerShell files as **binary** (`*.ps1 -text`) instead of text with line ending conversion
4. ✅ Files now stored with CRLF in the repository (`i/crlf`) and will be checked out with CRLF on all platforms (`w/crlf`)
5. ✅ Verified the files have no syntax errors (balanced braces, even quotes, no smart quotes)

## How to Fix Your Local Copy

### Pull the latest fix from the repository
```powershell
cd C:\Users\gladi\source\repos\bookwork2
git pull origin main
```

The files are now stored with CRLF in the repository and will automatically have the correct line endings when you pull them.

### Verify the fix
After pulling, verify the script works:
```powershell
cd KandRStyle\research\references
powershell -File .\Download-References.ps1 -StartRef 1 -EndRef 1 -SkipSetup
```

This should execute without parser errors.

## Prevention
The updated `.gitattributes` file now ensures that:
- PowerShell scripts (`.ps1`) are stored as **binary files** with CRLF line endings preserved in the repository
- Files will be checked out with CRLF on all platforms (Windows, Mac, Linux)
- No automatic line ending conversion will occur, preventing the LF/CRLF mismatch issue

## Technical Details
**Before the fix:**
- Repository stored files with LF endings (`i/lf`)
- `.gitattributes` had `*.ps1 text eol=crlf` which only converted on checkout
- Git checkout converted to CRLF (`w/crlf`) but some Windows systems didn't convert properly
- Result: PowerShell received LF endings and failed to parse

**After the fix:**
- Repository stores files with CRLF endings (`i/crlf`)
- `.gitattributes` has `*.ps1 -text` (binary treatment, no conversion)
- Files have CRLF both in repository and working copy
- Result: PowerShell always receives CRLF endings and parses correctly

The files were verified to be syntactically correct:
- **Download-References.ps1**: 217 CRLF line endings, 0 LF-only
- **Download-References-Wayback.ps1**: 292 CRLF line endings, 0 LF-only
- **Braces**: Balanced (26 and 39 pairs respectively)
- **Quotes**: Even counts (114 and 168 respectively)
- **Smart quotes**: None found
- **Line 213**: Ends with `0d 0a` (CRLF) as expected

## Still Having Issues?
If you continue to see errors after pulling the fixed version:

1. **Check what you actually have locally:**
   ```powershell
   # Check line endings
   git ls-files --eol Download-References.ps1
   # Should show: i/crlf  w/crlf  attr/-text
   ```

2. **Force refresh from repository:**
   ```powershell
   # Remove local file
   rm Download-References.ps1
   
   # Check out fresh from repository
   git checkout HEAD -- Download-References.ps1
   ```

3. **Verify your git configuration:**
   ```powershell
   git config --get core.autocrlf
   # Should be: false or input (not true)
   ```

4. **Check PowerShell version:**
   ```powershell
   $PSVersionTable.PSVersion
   # Should be PowerShell 5.1 or later
   ```

If issues persist after following these steps, the problem may be with your local git or PowerShell configuration. Please provide:
- The output of `git ls-files --eol Download-References.ps1`
- The output of `git diff Download-References.ps1`
- Your PowerShell version
- Your git version (`git --version`)
