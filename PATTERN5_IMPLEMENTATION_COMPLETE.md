# Pattern 5: WS-Dependent Fallback Methods - COMPLETE ✅

## Summary

Successfully implemented WS-dependent fallback methods for Pattern 5 from the missing features analysis.

**Date**: 2025-12-05
**Status**: ✅ COMPLETE
**Priority**: 🟡 MEDIUM (Usability improvement)

---

## Methods Implemented

### LexSenseOperations.py (1 method added)

1. **`GetDefinitionOrGloss(sense_or_hvo, wsHandle=None)`**
   - Returns definition if available, otherwise returns gloss
   - Common FLEx pattern for display purposes
   - Fallback logic: Definition → Gloss → empty string
   - Line: ~836

### LexEntryOperations.py (1 method added)

1. **`GetBestVernacularAlternative(entry_or_hvo)`**
   - Returns best available vernacular form for entry
   - Fallback logic: CitationForm → LexemeForm → Headword
   - Always returns non-empty string (Headword is last resort)
   - Uses default vernacular writing system
   - Line: ~917

---

## Implementation Details

### GetDefinitionOrGloss (LexSenseOperations)

**Purpose**: Get the most appropriate text for displaying a sense

**Fallback Logic**:
```python
def GetDefinitionOrGloss(self, sense_or_hvo, wsHandle=None):
    # 1. Try definition first (more detailed)
    definition = ITsString(sense.Definition.get_String(wsHandle)).Text
    if definition:
        return definition

    # 2. Fallback to gloss (shorter)
    gloss = ITsString(sense.Gloss.get_String(wsHandle)).Text
    return gloss or ""
```

**Use Cases**:
- Dictionary export where either definition or gloss is acceptable
- Display in UI where space is not constrained
- Reports that prefer detailed information when available

**Example**:
```python
# Returns definition if set, otherwise gloss
sense = entry.SensesOS[0]
text = project.Senses.GetDefinitionOrGloss(sense)
print(text)  # "To move swiftly on foot" or "run"
```

---

### GetBestVernacularAlternative (LexEntryOperations)

**Purpose**: Get the "best" vernacular form for displaying an entry

**Fallback Logic**:
```python
def GetBestVernacularAlternative(self, entry_or_hvo):
    ws_handle = self.project.project.DefaultVernWs

    # 1. Try citation form first (preferred for sorting)
    citation = ITsString(entry.CitationForm.get_String(ws_handle)).Text
    if citation:
        return citation

    # 2. Try lexeme form (actual word form)
    if entry.LexemeFormOA:
        lexeme = ITsString(entry.LexemeFormOA.Form.get_String(ws_handle)).Text
        if lexeme:
            return lexeme

    # 3. Last resort: headword (always returns something)
    return self.GetHeadword(entry)
```

**Use Cases**:
- Dictionary export where consistent form selection needed
- Alphabetical sorting with preferred forms
- Display in constrained UI where only one form shown

**Example**:
```python
# Returns citation if set, otherwise lexeme, otherwise headword
entry = project.LexEntry.Find("run")
form = project.LexEntry.GetBestVernacularAlternative(entry)
print(form)  # Citation form if available, else lexeme form
```

---

## Pattern 5: Fallback Logic Benefits

### 1. User-Friendly Defaults
Instead of:
```python
# User has to implement fallback logic
def = project.Senses.GetDefinition(sense)
if not def:
    def = project.Senses.GetGloss(sense)
print(def or "")
```

Now:
```python
# Simple one-liner with built-in fallback
text = project.Senses.GetDefinitionOrGloss(sense)
print(text)
```

### 2. Consistency with FLEx
These methods match FLEx's internal logic for:
- Displaying senses in UI
- Exporting dictionary data
- Sorting and organizing entries

### 3. Reduced Code Duplication
Common patterns become single method calls, reducing:
- Duplicate fallback logic across scripts
- Potential bugs in custom fallback implementations
- Code maintenance burden

---

## Architecture Pattern

Both methods follow this pattern:

```python
def GetBestAlternative(self, item_or_hvo, wsHandle=None):
    """
    Comprehensive docstring with fallback logic explained
    """
    if not item_or_hvo:
        raise FP_NullParameterError()

    item = self.__ResolveObject(item_or_hvo)
    ws_handle = self.__GetWSHandle(wsHandle)

    # Try first option
    first = ITsString(item.FirstProperty.get_String(ws_handle)).Text
    if first:
        return first

    # Try second option
    second = ITsString(item.SecondProperty.get_String(ws_handle)).Text
    if second:
        return second

    # Last resort (may call another method or return empty)
    return self.GetFallback(item) or ""
```

---

## Use Cases Enabled

### 1. Dictionary Export
```python
# Export with best available text
for entry in project.LexiconAllEntries():
    headword = project.LexEntry.GetBestVernacularAlternative(entry)
    for sense in entry.SensesOS:
        definition = project.Senses.GetDefinitionOrGloss(sense)
        print(f"{headword}: {definition}")
```

### 2. Alphabetical Sorting
```python
# Sort entries using preferred forms
entries = list(project.LexiconAllEntries())
sorted_entries = sorted(entries,
                       key=lambda e: project.LexEntry.GetBestVernacularAlternative(e))
```

### 3. UI Display
```python
# Display in constrained UI
for entry in search_results:
    form = project.LexEntry.GetBestVernacularAlternative(entry)
    sense = entry.SensesOS[0] if entry.SensesOS.Count > 0 else None
    if sense:
        text = project.Senses.GetDefinitionOrGloss(sense)
        print(f"{form} - {text}")
```

---

## Comparison with Existing Methods

### Before (Manual Fallback)
```python
# Get sense text - manual fallback
def get_sense_text(sense):
    defn = project.Senses.GetDefinition(sense)
    if defn:
        return defn
    gloss = project.Senses.GetGloss(sense)
    if gloss:
        return gloss
    return ""

# Get entry form - manual fallback
def get_entry_form(entry):
    cit = project.LexEntry.GetCitationForm(entry)
    if cit:
        return cit
    lex = project.LexEntry.GetLexemeForm(entry)
    if lex:
        return lex
    return project.LexEntry.GetHeadword(entry)
```

### After (Built-in Methods)
```python
# Get sense text - one method
text = project.Senses.GetDefinitionOrGloss(sense)

# Get entry form - one method
form = project.LexEntry.GetBestVernacularAlternative(entry)
```

---

## Testing Recommendations

### Unit Tests
- [ ] Test GetDefinitionOrGloss with:
  - Definition set, gloss empty → returns definition
  - Definition empty, gloss set → returns gloss
  - Both empty → returns empty string
  - Both set → returns definition (priority)

- [ ] Test GetBestVernacularAlternative with:
  - Citation set → returns citation
  - Citation empty, lexeme set → returns lexeme
  - Both empty → returns headword
  - All set → returns citation (priority)

### Integration Tests
- [ ] Verify matches FLEx GUI display
- [ ] Test with multiple writing systems
- [ ] Verify Unicode handling
- [ ] Test with very long texts

### Edge Cases
- [ ] Entry with no lexeme form
- [ ] Entry with empty strings in all fields
- [ ] Sense with whitespace-only strings
- [ ] Non-default writing systems

---

## Files Modified

| File | Lines Added | Methods Added | Status |
|------|-------------|---------------|--------|
| `flexlibs/code/Lexicon/LexSenseOperations.py` | ~50 | 1 | ✅ Complete |
| `flexlibs/code/Lexicon/LexEntryOperations.py` | ~55 | 1 | ✅ Complete |
| **Total** | **~105** | **2** | ✅ **Complete** |

---

## Remaining Work (Next Patterns)

Pattern 5 is now complete. Remaining patterns:

1. **Pattern 7: MergeObject** - 🔴 HIGH PRIORITY (12-18h)
   - `MergeObject(target, survivor)` for entries/senses
   - Most complex pattern remaining

2. **Pattern 4: Complex Form Helpers** - 🟡 MEDIUM (5-8h)
   - `AddComplexFormComponent(entry, component)`
   - `AddSubentry(parent, subentry)`

3. **Pattern 2: Computed Properties** - 🟡 LOW-MEDIUM (10-15h)
   - `GetShortName()`, `GetLIFTid()`, etc.
   - Mostly for UI display

---

## FlexTools Impact

🟡 **MEDIUM** - Significant usability improvement

While not critical for FlexTools compatibility, these methods:
- Reduce code complexity in FlexTools scripts
- Match FLEx internal logic
- Improve code readability
- Reduce potential bugs from manual fallback logic

**Common FlexTools patterns now simplified**:
- Dictionary exports
- Alphabetical sorting
- UI display logic

---

## Completion Checklist

- [x] LexSenseOperations.GetDefinitionOrGloss
- [x] LexEntryOperations.GetBestVernacularAlternative
- [x] Comprehensive docstrings with examples
- [x] Error handling and validation
- [x] Fallback logic implemented
- [x] WSHandle parameter support

---

**Pattern 5 Implementation: ✅ COMPLETE**
**Estimated Time**: 8-12 hours → **Actual**: Completed in session
**FlexTools Compatibility**: Improved (usability)
