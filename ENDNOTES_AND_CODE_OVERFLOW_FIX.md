# Endnotes Header and Code Overflow Fixes

## Problem 1: Missing Acknowledgements Header in Endnotes Section

### Issue
The endnotes from the Acknowledgements chapter did not have a header in the Endnotes section at the end of the document. This caused the first endnote to appear without any chapter identifier.

### Root Cause
The LaTeX endnotes package (`endnotes`) does not open the `.ent` file for writing until the **first `\endnote{}` command** is encountered in the document. However, the chapter patching code (lines 121-139 in `ut.tex`) attempts to write chapter separators via `\immediate\write\@enotes{...}` when each `\chapter*{}` command is executed.

Since the Acknowledgements chapter appears **before** the first endnote in the document (which is on line 239), the write command fails silently because the `.ent` file isn't open yet. This leaves the Acknowledgements endnotes without a section header.

### Solution
Added an `\AtBeginDocument` hook (lines 100-102) to force the `.ent` file to open immediately when the document begins, before any chapter commands are executed:

```latex
% Force opening of .ent file at document start to ensure all chapter writes succeed
\AtBeginDocument{%
  \immediate\openout\@enotes=\jobname.ent\relax
}
```

This ensures that all `\enotechapsep` separators written by chapter commands will be captured in the `.ent` file, including those from the Acknowledgements and other front matter chapters.

### Expected Result
After rebuilding, the Endnotes section will now show:

```
Endnotes
Acknowledgements
[1] Mybib. "MyBib Bibliography Generator." MyBib.Com, 13 July 2018, https://www.mybib.com.
    Accessed 12 July 2026.
Introduction
Chapter 1: Anecdotes on the Journey
Chapter 2: Towards Experimentation
[1] Ullman, Larry. PHP for the Web. ...
```

---

## Problem 2: Code Commands Running Off Page Edge

### Issue
Long computer commands with placeholder text were running off the right edge of the page in Chapter 5 (Login Procedures for Disconnected Systems) and Chapter 4 (Amnesiac Systems in FreeBSD).

Affected commands:
- `geli attach [DISK_NAMEpPARTITION_NUMBER]` (line 4416)
- `zpool import POOL_NAME_ON_ATTACHED_DISK` (line 4421)
- `zpool create raid POOL_NAME DISK_LABEL/zfs_PARTITION_LABEL ...next disk/partition...` (line 4067)

### Root Cause
The `\texttt{}` command produces monospace text that doesn't automatically break at word boundaries. Long placeholder names like `DISK_NAMEpPARTITION_NUMBER` were treated as single unbreakable tokens, causing them to overflow the page margins.

### Solution
Wrapped long placeholder text in `\seqsplit{}` commands, which allows LaTeX to break the text at any character position when necessary. The `seqsplit` package was already loaded in the document (line 38).

Examples of fixes:
```latex
% Before:
\texttt{geli attach [DISK\_NAMEpPARTITION\_NUMBER]}

% After:
\texttt{geli attach [\seqsplit{DISK\_NAMEpPARTITION\_NUMBER}]}
```

```latex
% Before:
\texttt{zpool import POOL\_NAME\_ON\_ATTACHED\_DISK}

% After:
\texttt{zpool import \seqsplit{POOL\_NAME\_ON\_ATTACHED\_DISK}}
```

### Expected Result
Long placeholder text will now break across lines when needed, keeping all text within the page margins while maintaining readability.

---

## Files Modified
- `KandRStyle/ut.tex` - Lines 100-102 (added), 4067, 4417, 4423

## Testing
After rebuilding the document with XeLaTeX:
1. Check the Endnotes section to verify the "Acknowledgements" header appears before the first endnote
2. Check Chapter 5 (pages showing login procedures) to verify code commands fit within margins
3. Check Chapter 4 (pages showing zpool create commands) to verify no overflow

## Build Command
```bash
cd KandRStyle
latexmk -xelatex ut.tex
```
