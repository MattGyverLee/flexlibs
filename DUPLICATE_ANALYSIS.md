# Duplicate Functionality Analysis

**Analysis Date:** 2025-11-23
**Comparing:** Original code (before SHA ff0ee42) vs New Operations files

## Summary

The original code had 5 core files:
- `FLExGlobals.py`
- `FLExInit.py`
- `FLExLCM.py`
- `FLExProject.py` (main file with ~90 methods)
- `__init__.py`

The new code added 44 `*Operations.py` files with over 800 new methods.

---

## CRITICAL DUPLICATES FOUND

### 1. **Lexicon Entry Operations**
**Original:** `FLExProject.py` | **New:** `LexEntryOperations.py`

| Original Method | New Method | Status |
|----------------|------------|--------|
| `LexiconAllEntries()` | `GetAll()` | DUPLICATE |
| `LexiconAllEntriesSorted()` | `GetAll()` + sorting | PARTIAL DUPLICATE |
| `LexiconNumberOfEntries()` | Count of `GetAll()` | DUPLICATE |
| `LexiconGetHeadword(entry)` | `GetHeadword(entry)` | DUPLICATE |
| `LexiconGetLexemeForm(entry, ws)` | `GetLexemeForm(entry, ws)` | DUPLICATE |
| `LexiconSetLexemeForm(entry, form, ws)` | `SetLexemeForm(entry, form, ws)` | DUPLICATE |
| `LexiconGetCitationForm(entry, ws)` | `GetCitationForm(entry, ws)` | DUPLICATE |
| `LexiconGetAlternateForm(entry, ws)` | Not found | MISSING IN NEW |
| `LexiconGetPublishInCount(entry)` | Not found | MISSING IN NEW |
| `LexiconEntryAnalysesCount(entry)` | Not found | MISSING IN NEW |

### 2. **Lexicon Sense Operations**
**Original:** `FLExProject.py` | **New:** `LexSenseOperations.py`

| Original Method | New Method | Status |
|----------------|------------|--------|
| `LexiconGetSenseNumber(sense)` | `GetSenseNumber(sense)` | DUPLICATE |
| `LexiconGetSenseGloss(sense, ws)` | `GetGloss(sense, ws)` | DUPLICATE |
| `LexiconSetSenseGloss(sense, gloss, ws)` | `SetGloss(sense, gloss, ws)` | DUPLICATE |
| `LexiconGetSenseDefinition(sense, ws)` | `GetDefinition(sense, ws)` | DUPLICATE |
| `LexiconGetSensePOS(sense)` | `GetPartOfSpeech(sense)` | DUPLICATE |
| `LexiconGetSenseSemanticDomains(sense)` | `GetSemanticDomains(sense)` | DUPLICATE |
| `LexiconSenseAnalysesCount(sense)` | `GetAnalysesCount(sense)` | DUPLICATE |

### 3. **Example Operations**
**Original:** `FLExProject.py` | **New:** `ExampleOperations.py`

| Original Method | New Method | Status |
|----------------|------------|--------|
| `LexiconGetExample(example, ws)` | `GetExample(example, ws)` | DUPLICATE |
| `LexiconSetExample(example, text, ws)` | `SetExample(example, text, ws)` | DUPLICATE |
| `LexiconGetExampleTranslation(trans, ws)` | `GetTranslation(trans, ws)` | DUPLICATE |

### 4. **Custom Field Operations**
**Original:** `FLExProject.py` | **New:** `CustomFieldOperations.py`

| Original Method | New Method | Status |
|----------------|------------|--------|
| `GetFieldID(className, fieldName)` | `FindField(className, fieldName)` | SIMILAR/DUPLICATE |
| `GetCustomFieldValue(obj, fieldID, ws)` | `GetValue(obj, field, ws)` | DUPLICATE |
| `LexiconFieldIsStringType(fieldID)` | Part of `GetFieldType()` | PARTIAL |
| `LexiconFieldIsMultiType(fieldID)` | `IsMultiString(fieldID)` | DUPLICATE |
| `LexiconFieldIsAnyStringType(fieldID)` | Part of type checking | PARTIAL |
| `LexiconGetFieldText(obj, fieldID, ws)` | `GetValue(obj, field, ws)` | DUPLICATE |
| `LexiconSetFieldText(obj, fieldID, text, ws)` | `SetValue(obj, field, text, ws)` | DUPLICATE |
| `LexiconClearField(obj, fieldID)` | `ClearValue(obj, field)` | DUPLICATE |
| `LexiconSetFieldInteger(obj, fieldID, int)` | `SetValue(obj, field, int)` | DUPLICATE |
| `LexiconAddTagToField(obj, fieldID, tag)` | `AddListValue(obj, field, tag)` | DUPLICATE |
| `ListFieldPossibilityList(obj, fieldID)` | Not found | MISSING IN NEW |
| `ListFieldPossibilities(obj, fieldID)` | `GetListValues()` | SIMILAR |
| `ListFieldLookup(obj, fieldID, value)` | Not found | MISSING IN NEW |
| `LexiconSetListFieldSingle(obj, fieldID, val)` | `SetListFieldSingle(obj, field, val)` | DUPLICATE |
| `LexiconClearListFieldSingle(obj, fieldID)` | `ClearValue()` | DUPLICATE |
| `LexiconSetListFieldMultiple(obj, fieldID, vals)` | `SetListFieldMultiple(obj, field, vals)` | DUPLICATE |
| `LexiconGetEntryCustomFields()` | Filter by class | PARTIAL |
| `LexiconGetSenseCustomFields()` | Filter by class | PARTIAL |
| `LexiconGetExampleCustomFields()` | Filter by class | PARTIAL |
| `LexiconGetAllomorphCustomFields()` | Filter by class | PARTIAL |
| `LexiconGetEntryCustomFieldNamed(name)` | `FindField('LexEntry', name)` | DUPLICATE |
| `LexiconGetSenseCustomFieldNamed(name)` | `FindField('LexSense', name)` | DUPLICATE |

### 5. **Reversal Operations**
**Original:** `FLExProject.py` | **New:** `ReversalOperations.py`

| Original Method | New Method | Status |
|----------------|------------|--------|
| `ReversalIndex(languageTag)` | `GetIndex(languageTag)` | DUPLICATE |
| `ReversalEntries(languageTag)` | `GetAll(languageTag)` | DUPLICATE |
| `ReversalGetForm(entry, ws)` | `GetForm(entry, ws)` | DUPLICATE |
| `ReversalSetForm(entry, form, ws)` | `SetForm(entry, form, ws)` | DUPLICATE |

### 6. **Text Operations**
**Original:** `FLExProject.py` | **New:** `TextOperations.py`

| Original Method | New Method | Status |
|----------------|------------|--------|
| `TextsNumberOfTexts()` | Count of `GetAll()` | DUPLICATE |
| `TextsGetAll(supplyName, supplyText)` | `GetAll()` | DUPLICATE (params differ) |

### 7. **Parts of Speech Operations**
**Original:** `FLExProject.py` | **New:** `POSOperations.py`

| Original Method | New Method | Status |
|----------------|------------|--------|
| `GetPartsOfSpeech()` | `GetAll()` | DUPLICATE |

### 8. **Semantic Domain Operations**
**Original:** `FLExProject.py` | **New:** `SemanticDomainOperations.py`

| Original Method | New Method | Status |
|----------------|------------|--------|
| `GetAllSemanticDomains(flat)` | `GetAll()` | DUPLICATE |

### 9. **Writing System Operations**
**Original:** `FLExProject.py` | **New:** `WritingSystemOperations.py`

| Original Method | New Method | Status |
|----------------|------------|--------|
| `GetAllVernacularWSs()` | `GetVernacular()` | DUPLICATE |
| `GetAllAnalysisWSs()` | `GetAnalysis()` | DUPLICATE |
| `GetDefaultVernacularWS()` | `GetDefaultVernacular()` | DUPLICATE |
| `GetDefaultAnalysisWS()` | `GetDefaultAnalysis()` | DUPLICATE |
| `GetWritingSystems()` | `GetAll()` | DUPLICATE |
| `WSUIName(languageTagOrHandle)` | `GetDisplayName()` | DUPLICATE |
| `WSHandle(languageTag)` | Internal `_GetWSByTag()` | DUPLICATE |

### 10. **Publication Operations**
**Original:** `FLExProject.py` | **New:** `PublicationOperations.py`

| Original Method | New Method | Status |
|----------------|------------|--------|
| `GetPublications()` | `GetAll()` | DUPLICATE |
| `PublicationType(publicationName)` | `Find(name)` | DUPLICATE |

### 11. **Lexical Reference Operations**
**Original:** `FLExProject.py` | **New:** `LexReferenceOperations.py`

| Original Method | New Method | Status |
|----------------|------------|--------|
| `GetLexicalRelationTypes()` | `GetAllTypes()` | DUPLICATE |

---

## NAMING CONVENTION ISSUES

### Original Pattern
The original code (Craig's work) used **verbose, explicit naming**:
- Prefix indicates domain: `Lexicon*`, `Reversal*`, `Texts*`
- Full descriptive names: `LexiconGetSenseGloss`, `GetAllVernacularWSs`
- Clear parameter names: `languageTagOrHandle`, `senseOrEntryOrHvo`

### New Pattern
The new Operations files use **shorter, object-oriented naming**:
- Domain in filename, not method name: `LexSenseOperations.GetGloss()`
- Shorter method names: `GetAll()`, `Create()`, `Delete()`
- More consistent CRUD pattern

### **RECOMMENDATION**
The original naming convention should be **preserved** as it was Craig's established pattern. The new code should either:
1. Adopt the verbose naming style, OR
2. Be clearly separated as a different API layer

---

## STRUCTURAL ISSUES

### 1. **Code Organization**
- **Original:** Monolithic `FLExProject.py` with all methods as instance methods
- **New:** Separated into 44 specialized operation files

**Issue:** Two completely different organizational approaches coexist

### 2. **Access Patterns**
- **Original:** `project.LexiconGetSenseGloss(sense, ws)`
- **New:** `project.Senses().GetGloss(sense, ws)` or `LexSenseOperations.GetGloss(project, sense, ws)`

**Issue:** Inconsistent API surface

### 3. **Missing Functionality**
The following original functions have NO equivalent in new code:
- `LexiconGetAlternateForm()`
- `LexiconGetPublishInCount()`
- `LexiconEntryAnalysesCount()` (though appears in LexSenseOperations)
- `ListFieldPossibilityList()`
- `ListFieldLookup()`
- `UnpackNestedPossibilityList()` (utility function)
- `BestStr()` (utility function)

---

## NEW FUNCTIONALITY (Not in Original)

The new Operations files add many **CRUD operations** not in the original:

### Creation Operations (Missing from Original)
- `LexEntry.Create()` - Create new entries
- `LexSense.Create()` - Create new senses
- `Example.Create()` - Create new examples
- `Phoneme.Create()` - Create phonemes
- `NaturalClass.Create()` - Create natural classes
- `Allomorph.Create()` - Create allomorphs
- And ~40 more Create() methods across all domains

### Deletion Operations (Missing from Original)
- `Delete()` methods across all operation classes
- Original had NO deletion capabilities

### Advanced Operations
- `POSOperations.AddSubcategory()`, `GetInflectionClasses()`
- `SemanticDomainOperations.GetSubdomains()`, `GetSensesInDomain()`
- `PhonemeOperations.GetFeatures()`, `IsVowel()`, `IsConsonant()`
- `WordformOperations.GetSpellingStatus()`, `ApproveSpelling()`
- `WfiAnalysisOperations.ApproveAnalysis()`, `RejectAnalysis()`
- And hundreds more advanced operations

---

## FILES WITH NO ORIGINAL EQUIVALENT

These are **entirely new** domains not covered in the original code:

1. **AgentOperations.py** - Human and parser agents
2. **AnnotationDefOperations.py** - Annotation definitions
3. **AnthropologyOperations.py** - Anthropological data
4. **CheckOperations.py** - Consistency checks
5. **ConfidenceOperations.py** - Confidence levels
6. **DataNotebookOperations.py** - Researcher notebooks
7. **DiscourseOperations.py** - Discourse charts
8. **EtymologyOperations.py** - Etymology information
9. **FilterOperations.py** - Data filtering
10. **LocationOperations.py** - Geographic locations
11. **MediaOperations.py** - Media file management
12. **NoteOperations.py** - Notes/comments
13. **OverlayOperations.py** - Chart overlays
14. **PersonOperations.py** - People/researchers
15. **PhonologicalRuleOperations.py** - Phonological rules
16. **ProjectSettingsOperations.py** - Project configuration
17. **TranslationTypeOperations.py** - Translation types
18. **VariantOperations.py** - Lexical variants
19. **WfiAnalysisOperations.py** - Wordform analyses
20. **WfiGlossOperations.py** - Wordform glosses
21. **WfiMorphBundleOperations.py** - Morpheme bundles

---

## CORRECTNESS ISSUES TO CHECK

Need to verify these in detail:

1. **Parameter handling** - Original uses flexible `languageTagOrHandle`, do new methods handle both?
2. **Error handling** - Original has specific exception types, do new methods match?
3. **Return types** - Original returns FDO objects directly, do new methods match?
4. **Writing system defaults** - Original has `__WSHandleVernacular()` and `__WSHandleAnalysis()` helpers
5. **HVO vs GUID vs Object** - Original accepts multiple input types, flexibility in new code?

---

## RECOMMENDATIONS

### Immediate Actions Needed:

1. **Decide on API Strategy:**
   - Option A: Keep both (legacy + new) with clear deprecation path
   - Option B: Remove duplicates, keep only original
   - Option C: Remove duplicates, migrate to new (breaking change)

2. **If Keeping Both:**
   - Clearly document which API is "primary"
   - Add deprecation warnings to one set
   - Ensure identical behavior between duplicates

3. **If Consolidating:**
   - Rename new methods to match Craig's conventions
   - Move all functionality back into FLExProject.py or use property accessors
   - Update all documentation

4. **Missing Original Functions:**
   - Implement in new code OR document why removed

5. **Testing:**
   - Create integration tests showing original vs new produce identical results
   - Test all duplicate pairs for behavioral consistency

### Naming Convention Choice:

**Recommend adopting ORIGINAL naming** because:
- It's Craig's established pattern (before SHA ff0ee42)
- It's self-documenting (clear what domain each method belongs to)
- Backwards compatible with existing code
- More explicit for library users

---

## LOGICAL ARRANGEMENT ISSUES

Current file organization is reasonable by domain, but:

1. **FLExProject.py** now has BOTH old methods AND property accessors to Operations classes
2. Creates **two ways** to do everything
3. No clear migration path documented

Suggested arrangement:
- Keep `FLExProject.py` as the main API surface
- Operations files as **internal implementation details**
- OR: Fully separate into `flexlibs.legacy` and `flexlibs.operations` modules

---

## TOTAL DUPLICATE COUNT

**Conservative estimate: 60-80 duplicate method pairs**

Major categories:
- Lexicon operations: ~35 duplicates
- Custom fields: ~15 duplicates
- Writing systems: ~7 duplicates
- Reversal: ~4 duplicates
- Texts: ~2 duplicates
- Semantic domains: ~2 duplicates
- POS: ~2 duplicates
- Publications: ~2 duplicates
- Lex references: ~1 duplicate

Plus ~700 NEW methods with no original equivalent.
