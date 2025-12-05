# FLEx GUI Convenience Features Analysis

Based on examination of FLEx source code (D:\Github\FieldWorks), here are the convenience features that FLEx provides when creating lexical entries.

## 1. ✅ **IMPLEMENTED: Blank Sense Creation**

### What FLEx Does:
When creating an entry via GUI, FLEx automatically creates a blank sense.

### Factory Methods:
```csharp
// Simple: No sense created
ILexEntry Create()

// Convenience: Creates entry + lexeme form + sense with gloss
ILexEntry Create(string lexemeForm, string gloss, SandboxGenericMSA msa)
ILexEntry Create(IMoMorphType morphType, ITsString form, ITsString gloss, SandboxGenericMSA msa)
```

### flexlibs Implementation:
```python
# Now implemented with create_blank_sense parameter
entry = project.LexEntry.Create("run")  # Creates entry + lexeme form + blank sense
entry = project.LexEntry.Create("run", create_blank_sense=False)  # No sense
```

**Status**: ✅ COMPLETE (just implemented)

---

## 2. **Multi-Writing System Support**

### What FLEx Does:
The InsertEntryDlg allows entering:
- **Lexeme form** in multiple vernacular writing systems
- **Gloss** in multiple analysis writing systems

### Factory Method:
```csharp
ILexEntry Create(LexEntryComponents components)
```

Where `LexEntryComponents` includes:
- `MorphType` - The morph type
- `LexemeFormAlternatives` - List<ITsString> for multiple WS
- `GlossAlternatives` - List<ITsString> for multiple WS
- `MSA` - Morphosyntactic analysis
- `GlossFeatures` - Additional grammatical features

### flexlibs Status:
Currently we only support ONE writing system per Create() call.

**Recommendation**:
- Add optional `lexeme_form_ws_dict` parameter: `{"en": "run", "fr": "courir"}`
- Add optional `gloss_ws_dict` parameter: `{"en": "to run", "es": "correr"}`

Example:
```python
entry = project.LexEntry.Create(
    lexeme_form="run",  # Default WS
    lexeme_form_ws={"fr": "courir", "es": "correr"},  # Additional WS
    gloss_ws={"en": "to run", "es": "correr"}  # Set gloss in multiple WS
)
```

**Priority**: MEDIUM (useful but not critical)

---

## 3. **Complex Form Creation**

### What FLEx Does:
When creating a complex form (compound, phrase, etc.), FLEx automatically:
1. Creates the entry
2. Adds an `ILexEntryRef` to `EntryRefsOS`
3. Sets the complex form type
4. Sets `RefType = LexEntryRefTags.krtComplexForm`

### Source Code:
```csharp
if (m_fComplexForm)
{
    ILexEntryRef ler = cache.GetInstance<ILexEntryRefFactory>().Create();
    newEntry.EntryRefsOS.Add(ler);
    if (m_complexType != null)
        ler.ComplexEntryTypesRS.Add(m_complexType);
    ler.RefType = LexEntryRefTags.krtComplexForm;
}
```

### flexlibs Status:
We have `VariantOperations` but no convenience method for complex forms.

**Recommendation**:
Add helper method to LexEntryOperations:
```python
def CreateComplexForm(self, lexeme_form, complex_form_type, components=None, **kwargs):
    """Create entry configured as a complex form."""
    entry = self.Create(lexeme_form, **kwargs)
    # Use VariantOperations to add complex form setup
    variant = self.project.Variants.Create(entry, ...)
    return entry
```

**Priority**: LOW (advanced feature, users can do manually)

---

## 4. **MSA (Morphosyntactic Analysis) Creation**

### What FLEx Does:
The InsertEntryDlg includes an MSAGroupBox that lets you set:
- Part of Speech
- Inflection features
- Grammatical info

All in one dialog during entry creation.

### flexlibs Status:
We have separate operations:
- `LexEntry.Create()` - Creates entry
- `Senses.SetGrammaticalInfo()` - Sets MSA on sense
- Must be done in two steps

**Recommendation**:
Add optional `pos` and `grammatical_info` parameters to Create():
```python
entry = project.LexEntry.Create(
    "run",
    pos="Verb",  # Convenience: auto-create MSA and attach to sense
    inflection_class="Class I"
)
```

**Priority**: MEDIUM (common workflow)

---

## 5. **Homograph Number Auto-Calculation**

### What FLEx Does:
When you create an entry with the same form as an existing entry, FLEx automatically calculates and assigns homograph numbers.

### flexlibs Status:
Homograph numbers are computed properties - FLEx manages this automatically.

**Status**: ✅ Already handled by FLEx/LCM

---

## 6. **Citation Form Auto-Fill**

### What FLEx Does:
If citation form is not explicitly set, FLEx uses the lexeme form as the citation form for display purposes.

### flexlibs Status:
This is a computed/virtual property in FLEx.

**Recommendation**:
Add convenience parameter to optionally set citation form during Create():
```python
entry = project.LexEntry.Create(
    lexeme_form="running",
    citation_form="run"  # Set explicitly if different
)
```

**Priority**: LOW (can set separately)

---

## 7. **Entry from Interlinear Text**

### What FLEx Does:
In "Add Words to Lexicon" mode, creating entries from interlinear text auto-populates:
- Lexeme form (from text word form)
- Gloss (from user's interlinear gloss)
- Part of Speech (from parsing)
- All in one operation

### Source:
`SandboxBase.cs` - `BuildEntryComponents()` method

**flexlibs Status**: Not directly applicable (no interlinear mode)

**Priority**: N/A (different workflow)

---

## 8. **Matching Entries Display**

### What FLEx Does:
The InsertEntryDlg shows a "Matching Entries" panel that displays similar entries as you type, preventing duplicates.

**flexlibs Status**:
We have `Find()` and `Exists()` but no fuzzy matching.

**Recommendation**:
Add helper method:
```python
def FindSimilar(self, lexeme_form, max_results=10):
    """Find entries with similar lexeme forms."""
    # Could use fuzzy matching or startswith
```

**Priority**: LOW (users can implement as needed)

---

## Summary of Recommendations

### ✅ Already Implemented:
1. Blank sense creation - `create_blank_sense=True` (default)

### 🟡 Medium Priority:
2. Multi-writing system support in Create()
3. MSA/POS during creation

### 🔵 Low Priority:
4. Complex form creation helper
5. Citation form parameter
6. FindSimilar() fuzzy matching

### ⚪ Not Needed:
7. Homograph numbering (auto-managed by LCM)
8. Interlinear workflows (different use case)

---

## Implementation Notes

The key insight is that FLEx uses different factory overloads for different scenarios:

1. **Minimal**: `Create()` - Just entry object
2. **Basic**: `Create(form, gloss, MSA)` - Entry + sense with gloss
3. **Full**: `Create(LexEntryComponents)` - Multi-WS, complex forms, features

flexlibs currently implements #1, and we just added convenience for creating a blank sense. We could optionally add more convenience parameters to match #2 and #3.

**Decision**: Focus on the 80% use case (single WS, simple entries with blank sense) and let advanced users use the full API.
