# Fix for xpatch Parameter Reference Syntax Error

## Problem

After adjusting endnotes in `ut.tex`, a LaTeX compilation error occurred:

```
! Extra }, or forgotten \endgroup.
\@schapter ...renewcommand {\currentchaptertitle }
                                                  {##1}\@mkboth \@gobbletwo \...
l.208 \tableofcontents
```

This error happened when `\tableofcontents` was called, which internally uses `\@schapter` (the command for unnumbered/starred chapters).

Additionally, a warning was present:
```
Package ut Warning: Failed to patch @chapter on input line 126.
```

## Root Cause

The original approach used `\xpatchcmd` to search for specific token sequences (`\if@openright` in `\@chapter` and `\@mkboth` in `\@schapter`) and replace them with patched versions. However, these specific sequences may not exist exactly as written in the internal definitions after hyperref and other packages have modified the commands. This caused the patches to fail.

When patches fail, the command remains unmodified, but the failure can lead to inconsistent behavior. Even when patches partially succeed, the insertion of complex replacement code into the middle of existing command definitions can cause brace mismatches and other structural issues.

## Solution

Instead of using `\xpatchcmd` to search for specific token sequences, we now use `\xpretocmd` to prepend code at the very beginning of the commands. This approach is more robust because:

1. It doesn't depend on finding specific internal tokens that might vary between LaTeX distributions or after package modifications
2. It cleanly adds code at the beginning without disrupting the internal structure
3. It still preserves LaTeX's hook system and maintains compatibility with hyperref

The corrected code:

```latex
% Patch \@chapter (regular chapters) to capture title
\xpretocmd{\@chapter}{%
  \renewcommand{\currentchaptertitle}{#1}%
}{}{\PackageWarning{ut}{Failed to patch @chapter}}

% Patch \@schapter (starred chapters) to capture title
\xpretocmd{\@schapter}{%
  \renewcommand{\currentchaptertitle}{#1}%
}{}{\PackageWarning{ut}{Failed to patch @schapter}}
```

## Parameter Reference Syntax

**CORRECTION**: The code now correctly uses `#1` (single hash) instead of `##1` (double hash) in the replacement text. The previous documentation incorrectly stated that `##1` was needed.

The correct syntax is `#1` because:

- When using `\xpretocmd` from the `xpatch` package, the replacement code is given as a direct argument, not wrapped in an additional `\newcommand` or similar macro definition
- The `#1` directly refers to the parameter of the command being patched (`\@chapter` or `\@schapter`)
- Using `##1` would create a literal `##1` in the replacement code, which causes "Illegal parameter number" errors when the .ent file is read back

The error occurred because `##1` was being written literally to the `.ent` file as part of `\currentchaptertitle`, and when LaTeX tried to read and process that file, it encountered `\enotechapsep{1}{##1}` which is invalid - `##1` only makes sense inside a `\newcommand` definition, not in normal LaTeX code

## Files Changed

1. **`KandRStyle/ut.tex`** (lines 121-133)
   - Changed from `\xpatchcmd` to `\xpretocmd` for both `\@chapter` and `\@schapter`
   - Removed search patterns that were causing failures
   - Corrected parameter reference syntax from `##1` to `#1` to fix "Illegal parameter number" error

2. **`FIX_LATEX_HOOK_ERROR.md`**
   - Updated documentation to reflect the new `\xpretocmd` approach

3. **`FIX_XPATCH_PARAMETER_SYNTAX.md`**
   - Corrected documentation to explain why `#1` (not `##1`) is the correct syntax

## Expected Result

After this fix:
- ✓ No more "Failed to patch" warnings
- ✓ `\tableofcontents` compiles without errors
- ✓ Unnumbered chapters (like Contents, Index, etc.) are properly handled
- ✓ Chapter titles are correctly captured for endnote organization
- ✓ All endnotes still appear organized by chapter at the end of the document

## Compilation

The document should now compile successfully with:
```bash
cd KandRStyle
latexmk -xelatex ut.tex
```

Or manually:
```bash
xelatex ut.tex
makeglossaries ut
xelatex ut.tex
xelatex ut.tex
```
