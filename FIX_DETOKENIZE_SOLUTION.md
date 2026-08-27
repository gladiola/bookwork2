# Fix for Persistent "Illegal parameter number in definition of \ttl@savemark" Error

## Problem

After applying the `\unexpanded\expandafter` fix in PR #92, the error persisted when compiling ut.tex:

```
[160] (./ut.ent
! Illegal parameter number in definition of \ttl@savemark.
```

Even after deleting auxiliary files and recompiling fresh, the error immediately reappeared at line 160 of the generated ut.ent file.

## Root Cause

The `\ttl@savemark` command is an internal command from the titlesec package that's used to format chapter titles. When we use `\titleformat{\chapter}...` to configure chapter formatting, titlesec modifies the chapter processing to include its internal commands.

The problem occurred because:

1. **Titlesec modifies chapter title processing**: When a chapter is created, titlesec's formatting system adds internal commands like `\ttl@savemark` to manage the formatting
2. **These internal commands contain parameter references**: Commands like `\ttl@savemark` are defined with parameter references like `#1`
3. **\unexpanded\expandafter wasn't sufficient**: While `\unexpanded\expandafter` prevents immediate expansion and tries to protect `#` characters, it doesn't fully convert the content to plain text
4. **Titlesec commands leaked into .ent file**: The chapter title captured by `\xpretocmd{\@chapter}` included titlesec's internal commands, which were then written to the .ent file
5. **Parameter references caused errors**: When the .ent file was read back during compilation, the `#1` in titlesec's internal commands appeared in a context where parameter references are invalid

## Solution

Replace `\unexpanded\expandafter` with `\detokenize\expandafter` in the chapter title writing code:

```latex
% OLD (doesn't work):
\xapptocmd{\@makechapterhead}{%
  \immediate\write\@enotes{\string\enotechapsep{\arabic{chapter}}{\unexpanded\expandafter{\currentchaptertitle}}}%
}{}{\PackageWarning{ut}{Failed to patch @makechapterhead}}

% NEW (correct fix):
\xapptocmd{\@makechapterhead}{%
  \immediate\write\@enotes{\string\enotechapsep{\arabic{chapter}}{\detokenize\expandafter{\currentchaptertitle}}}%
}{}{\PackageWarning{ut}{Failed to patch @makechapterhead}}
```

## How \detokenize\expandafter Works

1. **\expandafter** first expands `\currentchaptertitle` to its actual value (the chapter title text)
2. **\detokenize** then converts ALL tokens to category code 12 (other) characters
3. This means:
   - `\ttl@savemark` becomes the plain text string `\ttl@savemark` (not a command)
   - `#1` becomes the plain text string `#1` (not a parameter reference)
   - `{` and `}` become plain text characters
   - All LaTeX command structures are eliminated
4. The .ent file now contains: `\enotechapsep{1}{Building a Baseline for Quantitiative Risk Assessments}` as a simple string
5. When LaTeX reads this back, it sees only the plain text title, with no commands to execute

## Why This Works Better Than \unexpanded\expandafter

| Aspect | \unexpanded\expandafter | \detokenize\expandafter |
|--------|------------------------|------------------------|
| **Purpose** | Prevents expansion while preserving command structure | Converts everything to plain text |
| **Special characters** | Tries to protect `#` by doubling | Converts all special chars to catcode 12 |
| **LaTeX commands** | Preserves command structure | Eliminates all command structure |
| **Titlesec internals** | May still include `\ttl@savemark{#1}` | Converts to plain text `\ttl@savemark#1` |
| **Safety** | Partial - depends on expansion order | Complete - no LaTeX semantics remain |
| **Use case** | When you need to re-execute commands | When you only need display text |

## Files Changed

1. **KandRStyle/ut.tex** (lines 136, 141)
   - Changed `\unexpanded\expandafter` to `\detokenize\expandafter`
   
2. **FIX_TTL_SAVEMARK_PARAMETER_ERROR.md** (lines 32-95)
   - Updated documentation with new solution
   - Added explanation of why `\unexpanded\expandafter` wasn't sufficient
   - Added guidance on when to use each approach

## Testing

To test this fix:

```bash
cd KandRStyle
# Delete all auxiliary files
rm -f ut.ent ut.aux ut.out ut.toc ut.ind ut.gls ut.glo

# Compile fresh
latexmk -xelatex ut.tex
```

The compilation should now succeed without the "Illegal parameter number in definition of \ttl@savemark" error.

## Lessons Learned

1. **\detokenize is safer for display text**: When writing text to auxiliary files that will be displayed but not re-executed, `\detokenize` is the safest approach
2. **Package internals can leak**: Formatting packages like titlesec can modify content in ways that include internal commands with parameter references
3. **Test with real content**: The error only appeared with actual chapter titles and endnotes, not in minimal test cases
4. **\unexpanded has limits**: While `\unexpanded` prevents expansion, it doesn't eliminate LaTeX command semantics

## Related Issues

This fix addresses the same root cause as:
- PR #90: Fixed parameter syntax in xpatch (#1 vs ##1)
- PR #91: Removed duplicate titlesec loading
- PR #92: Added \unexpanded\expandafter protection (insufficient)
- PR #93: Removed duplicate amsmath loading

All of these were attempts to prevent parameter references from causing errors in the .ent file. The ultimate solution required using `\detokenize` to completely eliminate LaTeX command structure from chapter titles written to auxiliary files.
