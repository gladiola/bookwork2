# Diagnosis and Fix: Endnote Chapter Title Capture Issue

## Problem Summary

After 20 previous PRs attempting to fix the "Illegal parameter number in definition of \ttl@savemark" error, the document still failed with literal `#1` being written to the `.ent` file instead of actual chapter titles.

## Root Cause Discovery

### What Was Happening

1. **Previous approach**: Used `\xpretocmd` from the `xpatch` package to patch `\@chapter` and `\@schapter`
2. **Why it failed**: The `titlesec` package completely rewrites LaTeX's internal `\@chapter` and `\@schapter` commands
3. **Result**: The xpatch patches appeared to succeed (no errors) but didn't actually capture the chapter title argument
4. **Evidence**: The `.ent` file contained `\enotechapsep{1}{#1}` instead of `\enotechapsep{1}{Anecdotes on the Journey}`

### Diagnostic Process

1. **Compiled the document** to generate the `.ent` file
2. **Examined line 160 area** of `.ent` and found literal `#1` entries
3. **Searched for all `\enotechapsep` entries** in `.ent`:
   - Starred chapters (like "Introduction"): ✅ Worked correctly
   - Numbered chapters: ❌ Showed `{#1}` instead of actual titles
4. **Created test cases** to verify patching strategies
5. **Found the solution**: Patch `\chapter` directly before `titlesec` processes it

## The Fix

### Before (lines 117-142, not working):
```latex
\usepackage{xpatch}
\makeatletter

\xpretocmd{\@chapter}{%
  \renewcommand{\currentchaptertitle}{#1}%
}{}{\PackageWarning{ut}{Failed to patch @chapter}}

\xpretocmd{\@schapter}{%
  \renewcommand{\currentchaptertitle}{#1}%
}{}{\PackageWarning{ut}{Failed to patch @schapter}}

\xapptocmd{\@makechapterhead}{%
  \immediate\write\@enotes{\string\enotechapsep{\arabic{chapter}}{\unexpanded\expandafter{\currentchaptertitle}}}%
}{}{\PackageWarning{ut}{Failed to patch @makechapterhead}}

\xapptocmd{\@makeschapterhead}{%
  \immediate\write\@enotes{\string\enotechapsep{0}{\unexpanded\expandafter{\currentchaptertitle}}}%
}{}{\PackageWarning{ut}{Failed to patch @makeschapterhead}}

\makeatother
```

### After (lines 114-141, working):
```latex
\makeatletter

% Save the original \chapter command
\let\orig@chapter\chapter

% Redefine \chapter to capture the title before processing
\renewcommand{\chapter}{%
  \@ifstar{\@starred@chapter}{\@unstarred@chapter}%
}

% Handle starred chapters (\chapter*)
\newcommand{\@starred@chapter}[1]{%
  \renewcommand{\currentchaptertitle}{#1}%
  \orig@chapter*{#1}%
  \immediate\write\@enotes{\string\enotechapsep{0}{\unexpanded\expandafter{\currentchaptertitle}}}%
}

% Handle regular chapters (\chapter)
\newcommand{\@unstarred@chapter}[1]{%
  \renewcommand{\currentchaptertitle}{#1}%
  \orig@chapter{#1}%
  \immediate\write\@enotes{\string\enotechapsep{\arabic{chapter}}{\unexpanded\expandafter{\currentchaptertitle}}}%
}

\makeatother
```

## Why This Works

1. **Intercepts at the right level**: Captures the title from `\chapter` before `titlesec` modifies the internals
2. **No package dependency**: Removed the need for `xpatch` package entirely
3. **Direct argument access**: The `#1` in our redefinition refers to the actual chapter title string
4. **Preserves functionality**: Still calls the original `\chapter` command, so all formatting and features work

## Results

### Before Fix (ut.ent):
```latex
\enotechapsep{0}{Introduction}     % ✅ Starred chapters worked
\enotechapsep{1}{#1}              % ❌ Numbered chapters failed
\enotechapsep{2}{#1}              % ❌
```

### After Fix (ut.ent):
```latex
\enotechapsep{0}{Introduction}                                         % ✅
\enotechapsep{1}{Anecdotes on the Journey}                            % ✅
\enotechapsep{2}{Towards Experimentation}                              % ✅
\enotechapsep{3}{Building a Baseline for Quantitiative Risk Assessments} % ✅
```

## Key Lessons

1. **Package interactions matter**: When packages modify LaTeX internals (like `titlesec` does), traditional patching strategies may not work
2. **Diagnose before fixing**: Compiling and examining actual output files is essential
3. **Test at the right level**: Sometimes patching internal commands isn't the answer; work at the user-facing command level
4. **The cycle of `\detokenize` vs `\unexpanded`**: Neither was the issue - the problem was where we were trying to capture the title

## Why This Issue Was Hard

This is actually a **common book publishing task**, so why was it so difficult?

1. **The patches appeared to succeed**: No error messages, so it seemed like the code was working
2. **Titlesec's internals are opaque**: The package completely rewrites `\@chapter` in undocumented ways
3. **The error manifested elsewhere**: The "Illegal parameter number" error appeared in the `.ent` file on the *second* compilation pass, making it hard to trace back to the source

## Verification

- ✅ Document compiles without errors
- ✅ Chapter titles captured correctly in `.ent` file
- ✅ No "Illegal parameter number" errors
- ✅ Endnotes will display with proper chapter headings
- ✅ Both numbered and starred chapters work correctly
