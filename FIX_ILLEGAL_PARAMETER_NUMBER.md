# Fix for "Illegal parameter number in definition of \next" Error

## Problem

When compiling `ut.tex` with XeLaTeX, the following error occurred multiple times:

```
! Illegal parameter number in definition of \next.
<to be read again> 
                   ?
l.2041 ...nnualReport/Reports/2016_IC3Report.pdf}}
                                                  \\
```

The error appeared on lines 2041-2047, 2417-2423, 2799-2805, and other locations throughout the document (28 total instances).

## Root Cause

The error was caused by unescaped `#` characters in URLs within `\endnote` commands inside table cells. The URLs contained:

```
https://www.ic3.gov/Media/PDF/AnnualReport/2016State/StateReport.aspx#?s=47
```

In LaTeX, the `#` character is a special character used for parameter references in macro definitions. When LaTeX encounters `#` in certain contexts (especially within tables and macro arguments), it tries to interpret it as a parameter number (like `#1`, `#2`, etc.). Since `#?` is not a valid parameter reference, it causes the "Illegal parameter number" error.

## Solution

The fix is to escape all `#` characters in URLs by replacing them with `\#`. This tells LaTeX to treat the `#` as a literal character rather than a special parameter marker.

### Changes Made

All 28 instances of:
```latex
StateReport.aspx#?s=47
```

Were replaced with:
```latex
StateReport.aspx\#?s=47
```

### Example

**Before:**
```latex
2016&1&11&\endnote{original\protect\url{https://www.ic3.gov/Media/PDF/AnnualReport/2016State/StateReport.aspx#?s=47} current \protect\url{https://www.ic3.gov/AnnualReport/Reports/2016_IC3Report.pdf}}\\
```

**After:**
```latex
2016&1&11&\endnote{original\protect\url{https://www.ic3.gov/Media/PDF/AnnualReport/2016State/StateReport.aspx\#?s=47} current \protect\url{https://www.ic3.gov/AnnualReport/Reports/2016_IC3Report.pdf}}\\
```

## Result

After this fix:
- ✓ The "Illegal parameter number" error is completely resolved
- ✓ All 28 problematic URLs have been corrected
- ✓ The document now compiles past the problematic lines without parameter errors
- ✓ URLs will render correctly in the final PDF with the hash symbol properly displayed

## Note

This fix addresses only the "Illegal parameter number" error. Other compilation warnings or errors (such as missing fonts or packages) are unrelated to this fix and would need to be addressed separately if they prevent successful compilation.

## Files Changed

**`KandRStyle/ut.tex`** - Escaped `#` characters in 28 URLs
