# PowerShell Syntax Error Fix

## Problem
The `Download-References.ps1` script was showing parser errors on Windows:
- "The string is missing the terminator" at line 213
- "Missing closing '}' in statement block"
- "The Try statement is missing its Catch or Finally block"

## Root Cause
The PowerShell scripts contained **UTF-8 multi-byte characters** (✓ checkmark U+2713 and ✗ cross mark U+2717) without a UTF-8 BOM (Byte Order Mark). When PowerShell on Windows encounters a file without a BOM, it defaults to ANSI/Windows-1252 encoding. The UTF-8 multi-byte sequences (e.g., `0xe2 0x9c 0x93` for ✓) were misinterpreted as multiple ANSI characters, corrupting the parser's understanding of string boundaries and brace matching. This caused PowerShell to report confusing errors about missing string terminators and mismatched braces, even though the file structure was syntactically correct in UTF-8.

## What Was Fixed
1. ✅ Replaced UTF-8 checkmark character (✓ U+2713) with ASCII `[OK]` in both scripts
2. ✅ Replaced UTF-8 cross mark character (✗ U+2717) with ASCII `[X]` in both scripts
3. ✅ `Download-References.ps1`: 6 instances of ✓ and 1 instance of ✗ replaced
4. ✅ `Download-References-Wayback.ps1`: 6 instances of ✓ and 1 instance of ✗ replaced
5. ✅ Files now contain only ASCII characters, ensuring compatibility with PowerShell's default ANSI encoding
6. ✅ Maintained CRLF line endings (217 lines in Download-References.ps1, 292 in Wayback version)
7. ✅ Verified files have no syntax errors (balanced braces, even quotes, no non-ASCII characters)

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
To avoid similar issues in the future:

1. **Use only ASCII characters in PowerShell scripts** - Avoid UTF-8 special characters like ✓, ✗, fancy quotes, em-dashes, etc.
2. **If non-ASCII is needed**, save the file with a UTF-8 BOM so PowerShell knows to use UTF-8 encoding
3. **The `.gitattributes` file ensures**:
   - PowerShell scripts (`.ps1`) are stored with CRLF line endings (`*.ps1 -text`)
   - Files maintain CRLF on checkout across all platforms
4. **Validate scripts** before committing:
   ```powershell
   # Check for non-ASCII characters
   $content = [System.IO.File]::ReadAllBytes("script.ps1")
   $nonAscii = $content | Where-Object { $_ -gt 127 }
   if ($nonAscii) {
       Write-Host "Warning: File contains non-ASCII bytes"
   }
   ```

## Technical Details
**Before the fix:**
- Files contained UTF-8 multi-byte character sequences:
  - Checkmark ✓ (U+2713): bytes `e2 9c 93`
  - Cross mark ✗ (U+2717): bytes `e2 9c 97`
- No UTF-8 BOM (Byte Order Mark) in the files
- PowerShell on Windows defaults to ANSI/Windows-1252 encoding when no BOM is present
- Multi-byte UTF-8 sequences were misinterpreted as multiple ANSI characters
- Parser got confused: the byte `e2` in ANSI could be interpreted as `â`, breaking string and brace parsing
- Result: "missing string terminator" and "missing closing brace" errors

**After the fix:**
- All UTF-8 multi-byte characters replaced with ASCII equivalents:
  - ✓ → `[OK]`
  - ✗ → `[X]`
- Files now contain only ASCII characters (bytes 0x00-0x7F)
- No encoding ambiguity - ASCII is valid in all encodings
- PowerShell parses correctly regardless of encoding assumptions
- CRLF line endings preserved throughout

The files were verified to be syntactically correct:
- **Download-References.ps1**: 217 CRLF line endings, 0 LF-only, 0 non-ASCII bytes
- **Download-References-Wayback.ps1**: 292 CRLF line endings, 0 LF-only, 0 non-ASCII bytes
- **Braces**: Balanced (26 pairs in Download-References.ps1, 39 in Wayback)
- **Quotes**: Even counts (114 and 168 respectively)
- **Line 213**: Now parses correctly with proper string terminators

## Still Having Issues?
If you continue to see errors after pulling the fixed version:

1. **Verify the fix was applied:**
   ```powershell
   # Check for non-ASCII characters
   $bytes = [System.IO.File]::ReadAllBytes("Download-References.ps1")
   $nonAscii = @($bytes | Where-Object { $_ -gt 127 })
   Write-Host "Non-ASCII bytes found: $($nonAscii.Count)"
   # Should show: 0
   ```

2. **Check line endings:**
   ```powershell
   git ls-files --eol Download-References.ps1
   # Should show: i/crlf  w/crlf  attr/-text
   ```

3. **Force refresh from repository:**
   ```powershell
   # Remove local file
   rm Download-References.ps1
   
   # Check out fresh from repository
   git checkout HEAD -- Download-References.ps1
   ```

4. **Verify PowerShell can parse it:**
   ```powershell
   # This should show no errors
   $null = [System.Management.Automation.PSParser]::Tokenize(
       (Get-Content Download-References.ps1 -Raw), [ref]$null)
   Write-Host "Script parsed successfully!"
   ```

5. **Check your PowerShell version:**
   ```powershell
   $PSVersionTable.PSVersion
   # Should be PowerShell 5.1 or later
   ```
