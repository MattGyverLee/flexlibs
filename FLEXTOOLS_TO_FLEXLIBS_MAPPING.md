# FlexTools to FlexLibs API Mapping

This document maps FlexTools LCM function calls to their FlexLibs equivalents.

## 📋 Table of Contents
- [Current Coverage Status](#current-coverage-status)
- [Lexical Entry Operations](#lexical-entry-operations)
- [Sense Operations](#sense-operations)
- [Allomorph Operations](#allomorph-operations)
- [Pronunciation Operations](#pronunciation-operations)
- [Variant Operations](#variant-operations)
- [Example Operations](#example-operations)
- [Etymology Operations](#etymology-operations)
- [Custom Field Operations](#custom-field-operations)
- [Writing System Operations](#writing-system-operations)
- [Missing Convenience Functions](#missing-convenience-functions)

---

## 🎯 Current Coverage Status

### ✅ Fully Covered (Available in FlexLibs)
- Core CRUD for Entries, Senses, Allomorphs, Pronunciations, Variants, Examples, Etymologies
- Custom field get/set operations
- Writing system access
- Navigation and object access
- Part of Speech operations
- Semantic Domain operations

### ⚠️ Partially Covered (Need Convenience Methods)
- Some multi-step operations could use single-method wrappers
- Field type introspection helpers
- Bulk operations

### ❌ Not Yet Covered
- Complex form type operations (get/set/add)
- Some field clearing operations
- Tag manipulation

---

## 📖 Lexical Entry Operations

### Basic CRUD

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.LexiconAllEntries()` | `project.LexEntry.GetAll()` | ✅ |
| `project.LexiconNumberOfEntries()` | `len(list(project.LexEntry.GetAll()))` | ✅ |
| `project.LexiconAddEntry()` | `project.LexEntry.Create(lexeme_form, morph_type)` | ✅ |
| `project.LexiconGetEntry(index)` | `list(project.LexEntry.GetAll())[index]` | ✅ |
| `project.LexiconDeleteEntry(entry)` | `project.LexEntry.Delete(entry)` | ✅ |

**Example:**
```python
# FlexTools style
for entry in project.LexiconAllEntries():
    lf = project.LexiconGetLexemeForm(entry)

# FlexLibs style
for entry in project.LexEntry.GetAll():
    lf = project.LexEntry.GetLexemeForm(entry)
```

### Entry Properties - Forms

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.LexiconGetLexemeForm(entry)` | `project.LexEntry.GetLexemeForm(entry, wsHandle)` | ✅ |
| `project.LexiconSetLexemeForm(entry, text)` | `project.LexEntry.SetLexemeForm(entry, text, wsHandle)` | ✅ |
| `project.LexiconGetCitationForm(entry)` | `project.LexEntry.GetCitationForm(entry, wsHandle)` | ✅ |
| `project.LexiconSetCitationForm(entry, text)` | `project.LexEntry.SetCitationForm(entry, text, wsHandle)` | ✅ |
| `project.LexiconGetHeadWord(entry)` | `project.LexEntry.GetHeadword(entry)` | ✅ |
| `project.LexiconSetHeadword(entry, text)` | `project.LexEntry.SetHeadword(entry, text, wsHandle)` | ✅ |

### Entry Properties - Metadata

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.LexiconGetMorphType(entry)` | `project.LexEntry.GetMorphType(entry)` | ✅ |
| `project.LexiconSetMorphType(entry, mt)` | `project.LexEntry.SetMorphType(entry, morph_type_or_name)` | ✅ |
| `entry.DateCreated` | `project.LexEntry.GetDateCreated(entry)` | ✅ |
| `entry.DateModified` | `project.LexEntry.GetDateModified(entry)` | ✅ |
| `entry.HomographNumber` | `project.LexEntry.GetHomographNumber(entry)` | ✅ |
| `entry.Guid` | `project.LexEntry.GetGuid(entry)` | ✅ |
| `entry.ImportResidue` | `project.LexEntry.GetImportResidue(entry)` | ✅ |

### Entry Collections

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `entry.SensesOS` | `project.LexEntry.GetSenses(entry)` | ✅ |
| `project.LexiconNumberOfSenses(entry)` | `project.LexEntry.GetSenseCount(entry)` | ✅ |
| `project.LexiconAddSense(entry, gloss)` | `project.LexEntry.AddSense(entry, gloss, wsHandle)` | ✅ |
| `entry.AlternateFormsOS` | `entry.AlternateFormsOS` (direct access) | ✅ |
| `entry.PronunciationsOS` | `entry.PronunciationsOS` (direct access) | ✅ |
| `entry.EtymologyOS` | `entry.EtymologyOS` (direct access) | ✅ |

---

## 📖 Sense Operations

### Basic CRUD

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.LexiconGetSense(entry, index)` | `list(project.Senses.GetAll(entry))[index]` | ✅ |
| `project.LexiconAddSense(entry, gloss)` | `project.Senses.Create(entry, gloss, wsHandle)` | ✅ |
| `project.LexiconDeleteSense(sense)` | `project.Senses.Delete(sense)` | ✅ |
| `sense.Owner` | `project.Senses.GetOwningEntry(sense)` | ✅ |

### Sense Properties

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.LexiconGetSenseGloss(sense)` | `project.Senses.GetGloss(sense, wsHandle)` | ✅ |
| `project.LexiconSetSenseGloss(sense, text)` | `project.Senses.SetGloss(sense, text, wsHandle)` | ✅ |
| `project.LexiconGetSenseDefinition(sense)` | `project.Senses.GetDefinition(sense, wsHandle)` | ✅ |
| `project.LexiconSetSenseDefinition(sense, text)` | `project.Senses.SetDefinition(sense, text, wsHandle)` | ✅ |
| `project.LexiconGetSensePOS(sense)` | `project.Senses.GetPartOfSpeech(sense)` | ✅ |
| `project.LexiconSetSensePOS(sense, pos)` | `project.Senses.SetPartOfSpeech(sense, pos)` | ✅ |

### Sense Collections

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `sense.SemanticDomainsRC` | `project.Senses.GetSemanticDomains(sense)` | ✅ |
| `project.AddSemanticDomain(sense, domain)` | `project.Senses.AddSemanticDomain(sense, domain)` | ✅ |
| `sense.ExamplesOS` | `project.Senses.GetExamples(sense)` | ✅ |
| `project.AddExample(sense, text)` | `project.Senses.AddExample(sense, text, wsHandle)` | ✅ |
| `sense.SensesOS` | `project.Senses.GetSubsenses(sense)` | ✅ |
| `project.AddSubsense(sense, gloss)` | `project.Senses.CreateSubsense(sense, gloss, wsHandle)` | ✅ |
| `sense.PicturesOS` | `project.Senses.GetPictures(sense)` | ✅ |

### Sense Metadata

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `sense.SenseNumber` | `project.Senses.GetSenseNumber(sense)` | ✅ |
| `sense.StatusRA` | `project.Senses.GetStatus(sense)` | ✅ |
| `sense.SenseTypeRA` | `project.Senses.GetSenseType(sense)` | ✅ |
| `sense.Guid` | `project.Senses.GetGuid(sense)` | ✅ |
| `sense.MorphoSyntaxAnalysisRA` | `project.Senses.GetGrammaticalInfo(sense)` | ✅ |

---

## 📖 Allomorph Operations

### Basic Access

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.LexiconAllAllomorphs()` | **MISSING** - Need `project.Allomorphs.GetAll()` | ❌ |
| `entry.LexemeFormOA` | `entry.LexemeFormOA` (direct access) | ✅ |
| `entry.AlternateFormsOS` | `entry.AlternateFormsOS` (direct access) | ✅ |
| `project.LexiconAddAllomorph(entry, form)` | **Need** `project.Allomorphs.Create(entry, form, wsHandle)` | ⚠️ |
| `project.LexiconGetAllomorphForms(entry)` | **Need** `project.Allomorphs.GetAllForms(entry)` | ⚠️ |

**Note:** You likely have these in AllomorphOperations.py - need to verify

---

## 📖 Pronunciation Operations

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.LexiconGetPronunciations(entry)` | **Need** `project.Pronunciations.GetAll(entry)` | ⚠️ |
| `project.LexiconAddPronunciation(entry, text)` | **Need** `project.Pronunciations.Create(entry, text, wsHandle)` | ⚠️ |

---

## 📖 Variant Operations

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.LexiconGetVariantType(variant)` | **Need** `project.Variants.GetVariantType(variant)` | ⚠️ |
| `project.LexiconSetVariantType(variant, type)` | **Need** `project.Variants.SetVariantType(variant, type)` | ⚠️ |
| `project.LexiconAddVariantForm(entry, form, type)` | **Need** `project.Variants.Create(entry, form, variant_type, wsHandle)` | ⚠️ |

---

## 📖 Example Operations

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `sense.ExamplesOS` | **Need** `project.Examples.GetAll(sense)` | ⚠️ |
| `project.AddExample(sense, text)` | **Need** `project.Examples.Create(sense, text, wsHandle)` | ⚠️ |
| `project.GetExampleText(example)` | **Need** `project.Examples.GetText(example, wsHandle)` | ⚠️ |
| `project.SetExampleText(example, text)` | **Need** `project.Examples.SetText(example, text, wsHandle)` | ⚠️ |
| `project.GetExampleTranslation(example)` | **Need** `project.Examples.GetTranslation(example, wsHandle)` | ⚠️ |
| `project.SetExampleTranslation(example, text)` | **Need** `project.Examples.SetTranslation(example, text, wsHandle)` | ⚠️ |

---

## 📖 Custom Field Operations

### Field Access

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.LexiconGetFieldText(obj, flid, ws)` | `project.CustomField.GetFieldText(obj, field_name, wsHandle)` | ✅ |
| `project.LexiconSetFieldText(obj, flid, text, ws)` | `project.CustomField.SetFieldText(obj, field_name, text, wsHandle)` | ✅ |
| `project.LexiconGetEntryCustomFieldNamed(name)` | `project.CustomField.GetFieldID("LexEntry", field_name)` | ✅ |
| `project.LexiconGetSenseCustomFieldNamed(name)` | `project.CustomField.GetFieldID("LexSense", field_name)` | ✅ |
| `project.LexiconGetSenseCustomFields()` | `project.CustomField.GetCustomFields("LexSense")` | ✅ |

### Field Introspection

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.LexiconFieldIsStringType(flid)` | **MISSING** - Need `project.CustomField.IsStringType(field_id)` | ❌ |
| `project.GetFieldType(flid)` | `project.CustomField.GetFieldType(class_name, field_name)` | ✅ |
| `project.GetCustomFieldValue(obj, name)` | **Need** `project.CustomField.GetValue(obj, field_name)` | ⚠️ |

### Field Manipulation

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.LexiconClearField(obj, flid)` | **MISSING** - Need `project.CustomField.ClearField(obj, field_name)` | ❌ |
| `project.LexiconAddTagToField(obj, flid, tag)` | **MISSING** - Need `project.CustomField.AddTag(obj, field_name, tag)` | ❌ |
| `project.LexiconAddCustomField(...)` | `project.CustomField.Create(...)` | ✅ |

---

## 📖 Writing System Operations

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.GetDefaultVernacularWS()` | `project.GetDefaultVernacularWS()` | ✅ |
| `project.GetDefaultAnalysisWS()` | `project.GetDefaultAnalysisWS()` | ✅ |
| `project.GetAllVernacularWSs()` | `project.GetAllVernacularWSs()` | ✅ |
| `project.GetAllAnalysisWSs()` | `project.GetAllAnalysisWSs()` | ✅ |
| `project.WSHandle(ws_tag)` | `project.WSHandle(ws_tag)` | ✅ |
| `project.GetWritingSystemTag(ws_handle)` | `project.GetWritingSystemTag(ws_handle)` | ✅ |

---

## 📖 General Object Operations

| FlexTools Function | FlexLibs Equivalent | Status |
|-------------------|---------------------|--------|
| `project.ObjectsIn(repository)` | `project.ObjectsIn(repository)` | ✅ |
| `project.Object(hvo_or_guid)` | `project.Object(hvo_or_guid)` | ✅ |
| `project.BuildGotoURL(obj)` | `project.BuildGotoURL(obj)` | ✅ |
| `project.GetDateLastModified()` | `project.GetDateLastModified()` | ✅ |
| `project.LexiconDeleteObject(obj)` | **Need** convenience wrapper for specific types | ⚠️ |

---

## 🔧 Missing Convenience Functions

### High Priority (Should Add)

1. **Allomorph Convenience Methods**
   ```python
   project.Allomorphs.GetAll()  # Get all allomorphs in project
   project.Allomorphs.GetAllForms(entry)  # Get all forms for entry
   project.Allomorphs.Create(entry, form, morph_type, wsHandle)
   project.Allomorphs.GetForm(allomorph, wsHandle)
   project.Allomorphs.SetForm(allomorph, text, wsHandle)
   ```

2. **Pronunciation Convenience Methods**
   ```python
   project.Pronunciations.GetAll(entry)
   project.Pronunciations.Create(entry, form, wsHandle)
   project.Pronunciations.GetForm(pronunciation, wsHandle)
   project.Pronunciations.SetForm(pronunciation, text, wsHandle)
   project.Pronunciations.GetMediaFiles(pronunciation)
   ```

3. **Example Convenience Methods**
   ```python
   project.Examples.GetAll(sense)
   project.Examples.Create(sense, text, wsHandle)
   project.Examples.GetText(example, wsHandle)
   project.Examples.SetText(example, text, wsHandle)
   project.Examples.GetTranslation(example, wsHandle)
   project.Examples.SetTranslation(example, text, wsHandle)
   project.Examples.GetReference(example)
   ```

4. **Variant Convenience Methods**
   ```python
   project.Variants.GetVariantType(variant)
   project.Variants.SetVariantType(variant, type)
   project.Variants.Create(entry, form, variant_type, wsHandle)
   project.Variants.GetForm(variant, wsHandle)
   ```

5. **Etymology Convenience Methods**
   ```python
   project.Etymology.GetAll(entry)
   project.Etymology.Create(entry, form, wsHandle)
   project.Etymology.GetForm(etymology, wsHandle)
   project.Etymology.SetForm(etymology, text, wsHandle)
   project.Etymology.GetSource(etymology, wsHandle)
   project.Etymology.SetSource(etymology, text, wsHandle)
   ```

6. **Custom Field Helpers**
   ```python
   project.CustomField.ClearField(obj, field_name)
   project.CustomField.IsStringType(field_id)
   project.CustomField.AddTag(obj, field_name, tag)
   project.CustomField.GetValue(obj, field_name)  # Auto-detect type
   ```

### Medium Priority (Nice to Have)

7. **Complex Form Operations**
   ```python
   project.ComplexForms.GetComplexFormType(entry)
   project.ComplexForms.SetComplexFormType(entry, type)
   project.ComplexForms.Create(entry, components, type)
   project.ComplexForms.GetComponents(entry)
   ```

8. **Search/Find Helpers**
   ```python
   project.LexEntry.FindByGloss(gloss_text, wsHandle)
   project.LexEntry.FindByDefinition(def_text, wsHandle)
   project.Senses.FindByGloss(gloss_text, wsHandle)
   ```

### Low Priority (Advanced)

9. **Batch Operations**
   ```python
   project.LexEntry.CreateBatch(entries_data)
   project.Senses.UpdateBatch(sense_updates)
   ```

---

## 💡 Usage Patterns

### Pattern 1: Iterating All Entries and Senses
```python
# FlexTools
for entry in project.LexiconAllEntries():
    lf = project.LexiconGetLexemeForm(entry)
    for sense in entry.SensesOS:
        gloss = project.LexiconGetSenseGloss(sense)
        print(f"{lf}: {gloss}")

# FlexLibs
for entry in project.LexEntry.GetAll():
    lf = project.LexEntry.GetLexemeForm(entry)
    for sense in project.Senses.GetAll(entry):
        gloss = project.Senses.GetGloss(sense)
        print(f"{lf}: {gloss}")
```

### Pattern 2: Creating Entry with Sense
```python
# FlexTools
entry = project.LexiconAddEntry("run", "stem")
sense = project.LexiconAddSense(entry, "to move rapidly")
project.LexiconSetSenseDefinition(sense, "To move swiftly on foot")

# FlexLibs
entry = project.LexEntry.Create("run", "stem")
sense = project.Senses.Create(entry, "to move rapidly")
project.Senses.SetDefinition(sense, "To move swiftly on foot")
```

### Pattern 3: Working with Custom Fields
```python
# FlexTools
flid = project.LexiconGetSenseCustomFieldNamed("MyField")
value = project.LexiconGetFieldText(sense, flid, ws)
project.LexiconSetFieldText(sense, flid, "new value", ws)

# FlexLibs
value = project.CustomField.GetFieldText(sense, "MyField", wsHandle)
project.CustomField.SetFieldText(sense, "MyField", "new value", wsHandle)
```

---

## 📝 Notes

1. **Writing Systems**: FlexLibs consistently uses `wsHandle` parameter for WS specification, while FlexTools sometimes uses `ws` or omits it

2. **Object vs HVO**: FlexLibs operations accept both objects and HVOs interchangeably via `obj_or_hvo` pattern

3. **Error Handling**: FlexLibs has explicit exception types (`FP_ReadOnlyError`, `FP_NullParameterError`, `FP_ParameterError`)

4. **Collections**: FlexTools exposes raw `.SensesOS`, `.AlternateFormsOS`, etc. FlexLibs wraps these in `GetAll()` methods for consistency

5. **Field Access**: FlexLibs uses field names instead of FLIDs where possible for better readability

---

## 🎯 Recommendations

### Immediate Actions:
1. ✅ Verify all Operations classes have `GetAll()`, `Create()`, `Delete()` methods
2. ✅ Add convenience getters/setters for main properties (Form, Text, Type, etc.)
3. ⚠️ Add `GetValue()` / `SetValue()` convenience wrappers that auto-detect field types

### Short Term:
4. Add missing field manipulation methods (`ClearField`, `IsStringType`)
5. Complete Complex Form and Variant type operations
6. Add search/find helper methods

### Long Term:
7. Consider batch operation support for performance
8. Add validation helpers (e.g., `IsValidMorphType()`)
9. Create migration guide for FlexTools users

---

## 📚 See Also
- [LexEntryOperations.py](flexlibs/code/Lexicon/LexEntryOperations.py)
- [LexSenseOperations.py](flexlibs/code/Lexicon/LexSenseOperations.py)
- [CustomFieldOperations.py](flexlibs/code/System/CustomFieldOperations.py)
- [BaseOperations.py](flexlibs/code/BaseOperations.py)
