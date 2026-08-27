# Fix for xpatch Parameter Reference Syntax Error

## Problem

After adjusting endnotes in `ut.tex`, a LaTeX compilation error occurred:

```
! Extra }, or forgotten \endgroup.
\@schapter ...renewcommand {\currentchaptertitle }
                                                  {#1}\@mkboth \@gobbletwo \...
l.208 \tableofcontents
```

This error happened when `\tableofcontents` was called, which internally uses `\@schapter` (the command for unnumbered/starred chapters).

## Root Cause

The error was caused by incorrect parameter reference syntax in the `\xpatchcmd` calls. In the original code (lines 123-133 of `ut.tex`), the patches used `#1` to refer to the argument of the commands being patched:

```latex
\xpatchcmd{\@chapter}%
  {\if@openright}%
  {\renewcommand{\currentchaptertitle}{#1}\if@openright}% ❌ Wrong: #1
  {}{\PackageWarning{ut}{Failed to patch @chapter}}

\xpatchcmd{\@schapter}%
  {\@mkboth}%
  {\renewcommand{\currentchaptertitle}{#1}\@mkboth}% ❌ Wrong: #1
  {}{\PackageWarning{ut}{Failed to patch @schapter}}
```

However, when using `\xpatchcmd` (and similar macro patching commands from the `xpatch` package), the replacement text is being defined within another macro context. In LaTeX, when you want to refer to parameters that will be used when the patched command is eventually called, you must use `##1` (double hash) instead of `#1` (single hash).

Using `#1` causes LaTeX to think it's referring to a parameter of `\xpatchcmd` itself (which doesn't exist), resulting in malformed code that produces the "Extra }, or forgotten \endgroup" error.

## Solution

Change `#1` to `##1` in both the `\@chapter` and `\@schapter` patches:

```latex
\xpatchcmd{\@chapter}%
  {\if@openright}%
  {\renewcommand{\currentchaptertitle}{##1}\if@openright}% ✓ Correct: ##1
  {}{\PackageWarning{ut}{Failed to patch @chapter}}

\xpatchcmd{\@schapter}%
  {\@mkboth}%
  {\renewcommand{\currentchaptertitle}{##1}\@mkboth}% ✓ Correct: ##1
  {}{\PackageWarning{ut}{Failed to patch @schapter}}
```

## Technical Explanation

In LaTeX macro programming:
- `#1` in a definition refers to the first parameter of *that* definition
- When you're building replacement text that will itself become part of a definition, you need `##1` 
- The `##` is reduced to `#` during the first expansion, so the final patched command sees `#1` correctly

Think of it this way:
1. `\xpatchcmd` constructs new replacement code
2. During construction, `##1` becomes `#1`  
3. When the patched command is later called, it sees the correct `#1` parameter reference

## Files Changed

1. **`KandRStyle/ut.tex`** (lines 125, 132)
   - Changed `{#1}` to `{##1}` in both `\@chapter` and `\@schapter` patches

2. **`FIX_LATEX_HOOK_ERROR.md`**
   - Updated documentation to reflect the correct syntax
   - Added a new section explaining the parameter reference fix

## Expected Result

After this fix:
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
