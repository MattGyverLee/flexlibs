# FlexLibs → FlexLibs2 Migration Guide

FlexLibs2 is a major version upgrade (2.0) with improvements to API consistency and user experience. This guide covers breaking changes and how to update your scripts.

## Breaking Change: Empty Multistring Field Handling

### What Changed

FlexLibs2 **automatically converts FLEx's empty placeholder ("***") to Python's empty string ("")** in all functions that return multistring field values (glosses, definitions, forms, etc.).

| Behavior | FlexLibs (v1.x) | FlexLibs2 (v2.0) |
|----------|-----------------|------------------|
| `LexiconGetSenseGloss(sense)` | Returns `"***"` | Returns `""` |
| `sense.Gloss.BestAnalysisAlternative.Text` | Returns `"***"` | Still returns `"***"` (raw C# result) |
| Requires `BestStr()` wrapping? | Sometimes | No (automatic) |

### Why This Changed

**Consistency Problem in FlexLibs:**
- Most methods use `or ""` fallback (don't explicitly handle "***")
- Some methods explicitly check for "***" (BestStr, custom fields)
- Users had to know which methods needed wrapping and which didn't

**Better UX in FlexLibs2:**
- All public functions automatically normalize empty strings
- Users write simpler, more Pythonic code
- No need to learn the "***" FLEx convention

### Migration: Check for "***"

If your script checks for the "***" placeholder, update it:

**Before (FlexLibs):**
```python
gloss = project.LexiconGetSenseGloss(sense)
if gloss == "***":
    print("Gloss is empty")
```

**After (FlexLibs2):**
```python
gloss = project.LexiconGetSenseGloss(sense)
if not gloss:  # or: if gloss == ""
    print("Gloss is empty")
```

### Migration: BestStr() Wrapping

If your script wrapped results with `BestStr()`, you can remove it:

**Before (FlexLibs):**
```python
# Sometimes needed because some methods return "***"
gloss = project.BestStr(sense.Gloss)
form = project.BestStr(entry.LexemeFormOA.Form)
definition = project.BestStr(sense.Definition)
```

**After (FlexLibs2):**
```python
# Not needed - these already return normalized strings
gloss = sense.Gloss.BestAnalysisAlternative.Text  # Still "***" if direct access
# Better: use the operation methods which do the normalization
# (This assumes we've created SenseOperations methods)
```

### Migration: Direct C# Field Access

If your script accesses C# objects directly (not through FlexLibs methods), you'll still get "***":

**Before (FlexLibs):**
```python
# Direct access - you see "***"
text = sense.Gloss.BestAnalysisAlternative.Text
if text == "***":
    print("Empty")
```

**After (FlexLibs2):**
```python
# Direct access still returns "***" (raw C#)
text = sense.Gloss.BestAnalysisAlternative.Text
if text == "***":
    print("Empty")  # Still need this check

# Better: use FlexLibs2 operations methods
# (These do automatic conversion)
gloss = SenseOperations.GetGloss(sense)  # Returns ""
```

---

## Summary of Changes

| Feature | FlexLibs | FlexLibs2 | Action |
|---------|----------|-----------|--------|
| Empty multistring handling | Inconsistent | Automatic (all functions) | Remove "***" checks, use `if not value:` instead |
| BestStr() utility | Available | Still available (but not needed) | Can remove from scripts |
| Direct C# field access | Returns "***" | Still returns "***" | If using direct access, keep "***" checks |
| Function return values | Mixed | Consistent "" | Update empty checks |

---

## Testing Your Migration

Quick checklist:
- [ ] Search your script for `== "***"` - change to `== ""` or `if not value:`
- [ ] Search for `BestStr()` calls - can usually remove them
- [ ] Test with entries/senses that have empty glosses/definitions
- [ ] Verify your conditional logic still works

---

## Questions?

See [CLAUDE.md](../CLAUDE.md) for more details on FLEx conventions and data handling.
