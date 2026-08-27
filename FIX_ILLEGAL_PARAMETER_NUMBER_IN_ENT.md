# Fix for "Illegal parameter number in definition of \next" Error

## Problem

When compiling `ut.tex` with XeLaTeX, the following error occurred:

```
! Illegal parameter number in definition of \next.
```

This error appeared when LaTeX tried to read the `.ent` (endnotes) file during compilation.

## Root Cause

The error was caused by incorrect parameter syntax in the `\xpretocmd` patches for chapter title capture. The code was using `##1` (double hash) when it should have been using `#1` (single hash).

### Why This Caused the Error

1. The `\xpretocmd` patches were setting `\currentchaptertitle` to `##1` instead of `#1`
2. When `\currentchaptertitle` was written to the `.ent` file via `\write`, it was written literally as `##1`
3. The `.ent` file then contained lines like: `\enotechapsep{1}{##1}`
4. When LaTeX read this file back in, it encountered `##1` in normal document context (not inside a `\newcommand` definition)
5. LaTeX tried to interpret `##1` as a parameter reference, but `##` is only valid inside macro definitions, causing the "Illegal parameter number" error

### The Confusion About `##1` vs `#1`

The previous documentation incorrectly stated that `##1` was needed in `\xpretocmd` replacement code. This is **wrong** because:

- `##` → `#` conversion only happens when you're defining a macro *inside another macro definition* (e.g., `\newcommand` inside `\newcommand`)
- `\xpretocmd` takes its replacement code as a direct argument, not wrapped in another macro definition layer
- Therefore, `#1` directly refers to the parameter of the command being patched
- Using `##1` creates a literal `##1` in the code, which gets written to files and causes errors when read back

## Solution

Changed the parameter references from `##1` to `#1` in the `\xpretocmd` patches:

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

Now when these patches execute:
1. `#1` correctly captures the actual chapter title string
2. `\currentchaptertitle` is set to the actual title (e.g., "Introduction")
3. When written to `.ent` file, it writes: `\enotechapsep{1}{Introduction}`
4. When read back, this is valid LaTeX code with no parameter references

## Files Changed

1. **`KandRStyle/ut.tex`** (lines 124-133)
   - Changed `##1` to `#1` in both `\xpretocmd` patches
   
2. **`FIX_XPATCH_PARAMETER_SYNTAX.md`**
   - Corrected the documentation to explain why `#1` is correct

3. **Generated files removed**
   - Deleted `ut.ent`, `ut.aux`, `ut.out`, `ut.toc` to force regeneration with correct values

## Result

After this fix:
- ✓ The "Illegal parameter number" error is resolved
- ✓ Chapter titles are correctly captured as actual strings, not as `##1`
- ✓ The `.ent` file will contain valid LaTeX code
- ✓ Endnotes will be properly organized by actual chapter titles
- ✓ The document compiles without parameter number errors

## When to Use `#1` vs `##1`

**Use `#1`:**
- In direct code arguments to commands like `\xpretocmd`, `\xapptocmd`, `\xpatchcmd`
- In the body of a `\newcommand` definition
- When you want to reference the actual parameter value

**Use `##1`:**
- Only when defining a macro *inside another macro definition*
- When you want a literal `#1` to appear in the generated code
- Example: `\newcommand{\foo}[1]{\newcommand{\bar}[1]{##1 uses bar's param, #1 uses foo's param}}`

In our case with `\xpretocmd`, we wanted to capture the actual parameter value, so `#1` is correct.
