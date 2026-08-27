# Endnotes Reorganization Implementation

## Summary of Changes

The endnote system in `ut.tex` has been reorganized so that all endnotes are printed together at the end of the document, organized by chapter, instead of being printed after each chapter.

## What Changed

### 1. Modified Preamble (lines 56-115)
- Replaced the `\printchapterendnotes` command with two new commands:
  - `\markchapterendnotes`: Called at the end of each chapter to reset the endnote counter
  - `\printallendnotesbychapter`: Called once at the end to print all endnotes organized by chapter
  
- Added a hook to the `\chapter` command that automatically writes chapter separators to the endnotes file

### 2. Document Body Changes
Replaced all 9 instances of `\printchapterendnotes` with `\markchapterendnotes`:
- After Acknowledgements section
- After Introduction section  
- After Chapter 1 (Anecdotes on the Journey)
- After Chapter 2 (Towards Experimentation)
- After Chapter 3 (Building a Baseline for Quantitative Risk Assessments)
- After Chapter 4 (Amnesiac Systems in FreeBSD)
- After Chapter 5 (Login Procedures for Disconnected Systems)
- After Chapter 6 (Basic Tape Operations with FreeBSD)
- Before backmatter

### 3. Backmatter Changes
- Moved endnotes section to come before the glossary
- Changed from `\printchapterendnotes` to `\printallendnotesbychapter`
- Now prints: Endnotes → Glossary → Index

## How It Works

1. **During Document Processing:**
   - When a `\chapter{Title}` command is encountered, a separator marker is automatically written to the `.ent` file
   - Endnotes are written to the `.ent` file as they appear in the text
   - At the end of each chapter, `\markchapterendnotes` resets the endnote counter so numbering starts at 1 for the next chapter

2. **At the End of the Document:**
   - `\printallendnotesbychapter` creates a single "Endnotes" chapter
   - It then calls `\theendnotes` which reads the `.ent` file
   - The `.ent` file contains both separators and endnotes
   - Each chapter's endnotes appear under a subsection header like "Chapter 1: Anecdotes on the Journey"

## Result

The final document now has:
- All endnotes collected in a single "Endnotes" section at the end (before Glossary and Index)
- Within that section, subsections for each chapter showing "Chapter N: Title"
- Endnote numbering still resets to 1 for each chapter (maintaining the original behavior)
- Unnumbered chapters (Author, Preface, Acknowledgements, Introduction) show their title without a chapter number

## Compilation

To compile the document:
```bash
cd KandRStyle
latexmk -xelatex ut.tex
```

Or run XeLaTeX multiple times manually:
```bash
xelatex ut.tex
makeglossaries ut
xelatex ut.tex
xelatex ut.tex
```

Note: Multiple passes are required for:
1. First pass: Generate the `.ent` file with endnotes and separators
2. Second pass: Process endnotes from the `.ent` file
3. Additional passes may be needed for glossary, index, and cross-references

## Testing Checklist

When testing the compilation, verify:
- [ ] All endnotes appear in the final "Endnotes" section
- [ ] Endnotes are properly organized under chapter headings
- [ ] Endnote numbering resets for each chapter (starts at [1] in each chapter)
- [ ] The "Endnotes" section appears before "Glossary" in the table of contents
- [ ] Unnumbered chapters (Introduction, etc.) have proper headings in the endnotes section
- [ ] All endnote references in the main text still link correctly to the endnotes section
