# Fix for Endnote Chapter Labeling in Unnumbered Chapters

## Problem
The endnote chapter labeling system was not working. Endnotes from unnumbered chapters like "Acknowledgements" appeared without section headers in the endnotes output, and numbered chapters were also missing proper separators.

## Root Cause
The original code (lines 115-142 of ut.tex) attempted to wrap the `\chapter` command directly:
```latex
\let\orig@chapter\chapter
\renewcommand{\chapter}{...}
```

However, this approach fails because:
1. The `titlesec` package is loaded (line 11)
2. `\titleformat{\chapter}` is used (line 42)
3. When titlesec formats chapters, it internally bypasses the user-level `\chapter` command and works directly with the lower-level `\@chapter` and `\@schapter` commands
4. Our wrapper never gets called because titlesec routes around it

## Solution
Instead of wrapping `\chapter`, we now patch the lower-level LaTeX commands that titlesec actually uses:

- `\@chapter` - handles numbered chapters (`\chapter{Title}`)
- `\@schapter` - handles starred/unnumbered chapters (`\chapter*{Title}`)

The fixed code:
```latex
% Patch \@chapter (numbered chapters) to write separator BEFORE the chapter processes
\let\orig@@chapter\@chapter
\renewcommand{\@chapter}[2][]{%
  % #1 is optional TOC entry, #2 is the chapter title
  \renewcommand{\currentchaptertitle}{#2}%
  % Write separator to endnotes file
  \immediate\write\@enotes{\string\enotechapsep{\the\numexpr\value{chapter}+1}{\detokenize\expandafter{\currentchaptertitle}}}%
  % Call original \@chapter
  \orig@@chapter[#1]{#2}%
}

% Patch \@schapter (starred/unnumbered chapters) to write separator
\let\orig@@schapter\@schapter
\renewcommand{\@schapter}[1]{%
  \renewcommand{\currentchaptertitle}{#1}%
  % Write separator with chapter number 0 for unnumbered chapters
  \immediate\write\@enotes{\string\enotechapsep{0}{\detokenize\expandafter{\currentchaptertitle}}}%
  % Call original \@schapter
  \orig@@schapter{#1}%
}
```

## Expected Result
After rebuilding the document with XeLaTeX, the .ent file should contain:

```
\enotechapsep{0}{Acknowledgements}
\@doanenote {1}
... (endnote content) ...
\@endanenote
\enotechapsep{0}{Introduction}
... (endnotes from Introduction) ...
\enotechapsep{1}{Anecdotes on the Journey}
... (endnotes from Chapter 1) ...
\enotechapsep{2}{Towards Experimentation}
... (endnotes from Chapter 2) ...
```

And the printed endnotes output should show:

```
Endnotes

Acknowledgements
[1] Mybib. "MyBib Bibliography Generator."...

Introduction
(any endnotes from Introduction)

Chapter 1: Anecdotes on the Journey
[1] ...
[2] ...

Chapter 2: Towards Experimentation
[1] ...
```

## Testing
To test the fix:
1. Delete the old .ent file: `rm KandRStyle/ut.ent`
2. Build the document: `cd KandRStyle && latexmk -xelatex ut.tex`
3. Check the .ent file for proper `\enotechapsep` entries
4. View the PDF to verify endnotes are properly labeled by chapter

## Files Changed
- `KandRStyle/ut.tex` - Lines 115-140 (chapter hook implementation)
