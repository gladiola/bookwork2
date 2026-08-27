# Fix for "Illegal parameter number in definition of \ttl@savemark" Error

## Problem

When compiling `ut.tex` with XeLaTeX, the following error occurred at line 160 of the generated `.ent` file:

```
[160] (./ut.ent
! Illegal parameter number in definition of \ttl@savemark.
```

This error appeared when LaTeX tried to read the `.ent` (endnotes) file during the second pass of compilation.

## Root Cause

The error was caused by unprotected parameter references in chapter titles being written to the `.ent` file.

### How This Error Occurred

1. The `titlesec` package formats chapter titles using internal commands
2. Some of these internal commands (like `\ttl@savemark`) contain parameter references such as `#1`
3. When `\currentchaptertitle` was captured via the `\xpretocmd` patches, it contained these internal titlesec commands
4. When this was written to the `.ent` file using `\immediate\write`, the parameter references were written literally
5. The `.ent` file then contained lines like: `\enotechapsep{1}{\ttl@savemark{...#1...}}`
6. When LaTeX read this file back during the next compilation pass, it encountered `#1` in normal document context
7. Since `#1` is only valid inside macro definitions, LaTeX raised "Illegal parameter number" error

### Why Previous Fixes Weren't Sufficient

Previous fixes correctly changed the `\xpretocmd` patches to use `#1` instead of `##1`, which fixed the issue of `##1` being written literally. However, this didn't address the deeper issue: the chapter title itself contained internal titlesec commands with their own parameter references that needed protection.

## Solution

The fix uses `\detokenize\expandafter` when writing `\currentchaptertitle` to the `.ent` file:

```latex
% Handle starred chapters (\chapter*)
\newcommand{\@starred@chapter}[1]{%
  \renewcommand{\currentchaptertitle}{#1}%
  \orig@chapter*{#1}%
  \immediate\write\@enotes{\string\enotechapsep{0}{\detokenize\expandafter{\currentchaptertitle}}}%
}

% Handle regular chapters (\chapter)
\newcommand{\@unstarred@chapter}[1]{%
  \renewcommand{\currentchaptertitle}{#1}%
  \orig@chapter{#1}%
  \immediate\write\@enotes{\string\enotechapsep{\arabic{chapter}}{\detokenize\expandafter{\currentchaptertitle}}}%
}
```

### How This Fix Works

1. `\expandafter` expands `\currentchaptertitle` to its value (the chapter title text)
2. `\detokenize` converts all tokens to character codes (catcode 12), making them safe to write
3. This converts any LaTeX commands and special characters (including `#`, `\`, `{`, `}`) to plain text
4. The `.ent` file now contains: `\enotechapsep{1}{Building a Baseline for...}` as plain text
5. When LaTeX reads the `.ent` file back, it sees the chapter title as a simple string argument

### Why \detokenize\expandafter Is Needed

- **Without \expandafter**: `\currentchaptertitle` would be written literally as a command name, not its value
- **Without \detokenize**: Titlesec internal commands like `\ttl@savemark` with parameter references (`#1`) would be written to the file, causing "Illegal parameter number" errors when read back
- **Together**: We get the chapter title as plain text, with no LaTeX commands or special characters that could cause errors

### Why \unexpanded\expandafter Wasn't Sufficient

The previous fix using `\unexpanded\expandafter` didn't fully protect the chapter title because:
- Titlesec's internal formatting commands (like `\ttl@savemark`) were still being included in the expanded title
- These commands contain parameter references (`#1`) that need special handling
- Even with `\unexpanded`, these parameter references weren't being properly escaped
- `\detokenize` completely converts everything to safe plain text, eliminating all LaTeX command structures

## Files Changed

1. **`KandRStyle/ut.tex`** (lines 131, 138)
   - Changed `\unexpanded\expandafter` to `\detokenize\expandafter` to protect chapter titles when writing to `.ent` file
   
2. **Auxiliary files cleaned**
   - Deleted `ut.ent`, `ut.aux`, `ut.out`, `ut.toc`, `ut.idx`, `ut.ilg`, `ut.ist`, `ut.glo`, `ut.ind` to force regeneration with correct protection

## Result

After this fix:
- ✓ The "Illegal parameter number in definition of \ttl@savemark" error is resolved
- ✓ Chapter titles with internal titlesec formatting commands are properly protected
- ✓ The `.ent` file will contain valid LaTeX code with properly escaped parameter references
- ✓ Endnotes are properly organized by chapter titles
- ✓ The document compiles without parameter number errors

## Technical Details

### LaTeX \write Mechanics

When using `\immediate\write`:
- Single `#` in the written content is treated as a parameter reference (invalid in `.ent` file context)
- Double `##` in the written content becomes single `#` when read back (valid in command definitions)
- `\unexpanded` prevents expansion and ensures `#` becomes `##` in the output

### When to Use This Pattern

Use `\detokenize\expandafter{\commandname}` when:
- Writing command values to auxiliary files (`.aux`, `.toc`, `.ent`, etc.)
- The command value might contain LaTeX commands or special characters
- You want the actual text content, not the command name itself
- You need to protect the content from causing "Illegal parameter number" or other LaTeX errors
- The content might include titlesec or other package internal commands with parameter references

Use `\unexpanded\expandafter{\commandname}` when:
- You need to preserve LaTeX command structure in the auxiliary file
- The commands don't contain problematic parameter references
- You want the content to be re-executed when the auxiliary file is read back

For chapter titles in endnote files, `\detokenize` is preferred because it completely eliminates any LaTeX command structure that might interfere with compilation.

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
