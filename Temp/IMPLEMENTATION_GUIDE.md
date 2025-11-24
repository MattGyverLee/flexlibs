# Implementation Guide: FLExProject Method Delegation

Quick reference for implementing the delegation refactoring.

---

## Delegation Pattern (Craig's Established Style)

### Pattern 1: Simple Delegation (Already in Use)

```python
# In FLExProject.py
def LexiconGetHeadword(self, entry):
    """
    Returns the headword for `entry`.

    Note: This method now delegates to LexEntryOperations for single source of truth.
    """
    return self.LexEntry.GetHeadword(entry)
```

### Pattern 2: Delegation with Parameter Transformation

```python
# In FLExProject.py
def LexiconGetLexemeForm(self, entry, languageTagOrHandle=None):
    """
    Returns the lexeme form for `entry` in the default vernacular WS
    or other WS as specified by `languageTagOrHandle`.

    Note: This method now delegates to LexEntryOperations for single source of truth.
    """
    return self.LexEntry.GetLexemeForm(entry, languageTagOrHandle)
```

### Pattern 3: Delegation with Deprecation Notice

```python
# In FLExProject.py
def LexiconGetExample(self, example, languageTagOrHandle=None):
    """
    Returns the example text in the default vernacular WS or
    other WS as specified by `languageTagOrHandle`.

    .. deprecated:: [version]
        Use :meth:`project.Examples.GetExample` instead.

    Note: This method now delegates to ExampleOperations for single source of truth.
    """
    return self.Examples.GetExample(example, languageTagOrHandle)
```

---

## Batch-by-Batch Implementation

### BATCH 2: Writing System Methods (2 hours)

#### 2.1: GetAllVernacularWSs
```python
# FLExProject.py - BEFORE
def GetAllVernacularWSs(self):
    """
    Returns a set containing all of the vernacular language tags
    used in the project.
    """
    wsArray = self.lp.VernWss.split(" ")
    wsSet = set(wsArray)
    if "" in wsSet: wsSet.remove("")
    return wsSet

# FLExProject.py - AFTER
def GetAllVernacularWSs(self):
    """
    Returns a set containing all of the vernacular language tags
    used in the project.

    Note: This method now delegates to WritingSystemOperations.GetVernacular()
    """
    return set(self.WritingSystems.GetVernacular())
```

**Required in WritingSystemOperations:**
```python
# WritingSystemOperations.py
def GetVernacular(self):
    """
    Returns a list of all vernacular writing system tags used in the project.

    Returns:
        list: Writing system tags (e.g., ['en', 'fr', 'es'])
    """
    ws_string = self.project.lp.VernWss
    ws_list = [ws.strip() for ws in ws_string.split() if ws.strip()]
    return ws_list
```

#### 2.2: WSHandle
```python
# FLExProject.py - OPTION 1: Keep as-is (it's trivial)
def WSHandle(self, languageTag):
    """
    Returns the handle (`hvo`) for the given language tag.
    E.g. "en" -> 1033 or "qaa-x-duployan" -> 4159618.

    Note: This is a thin wrapper around WritingSystemOperations.GetLanguageTag()
    """
    return self.project.WritingSystemFactory.GetWsFromStr(languageTag)

# FLExProject.py - OPTION 2: Delegate fully
def WSHandle(self, languageTag):
    """
    Returns the handle (`hvo`) for the given language tag.

    Note: This method delegates to WritingSystemOperations for consistency.
    """
    return self.WritingSystems.GetHandle(languageTag)
```

**RECOMMENDATION:** Keep as-is. It's a one-liner calling LCM directly. Adding a layer adds no value.

---

### BATCH 3: Simple Lexicon Methods (3 hours)

#### 3.1: LexiconNumberOfEntries
```python
# FLExProject.py - BEFORE
def LexiconNumberOfEntries(self):
    return self.ObjectCountFor(ILexEntryRepository)

# FLExProject.py - AFTER
def LexiconNumberOfEntries(self):
    """
    Returns the number of entries in the lexicon.

    Note: This method delegates to LexEntryOperations.Count()
    """
    return self.LexEntry.Count()
```

**Required in LexEntryOperations:**
```python
# LexEntryOperations.py
def Count(self):
    """
    Returns the total number of lexical entries in the lexicon.

    Returns:
        int: Number of entries

    Example:
        >>> count = project.LexEntry.Count()
        >>> print(f"Lexicon has {count} entries")
    """
    return self.project.ObjectCountFor(ILexEntryRepository)
```

#### 3.2: LexiconAllEntriesSorted
```python
# FLExProject.py - BEFORE
def LexiconAllEntriesSorted(self):
    """
    Returns an iterator over all entries in the lexicon sorted by
    the (lower-case) headword.
    """
    entries = [(str(e.HeadWord), e) for e in self.LexiconAllEntries()]
    for h, e in sorted(entries, key=lambda x: x[0].lower()):
        yield e

# FLExProject.py - AFTER
def LexiconAllEntriesSorted(self):
    """
    Returns an iterator over all entries in the lexicon sorted by
    the (lower-case) headword.

    Note: This method delegates to LexEntryOperations.GetAllSorted()
    """
    return self.LexEntry.GetAllSorted()
```

**Required in LexEntryOperations:**
```python
# LexEntryOperations.py
def GetAllSorted(self, case_sensitive=False):
    """
    Returns entries sorted alphabetically by headword.

    Args:
        case_sensitive (bool): If True, sort case-sensitively. Default: False

    Yields:
        ILexEntry: Lexical entries in sorted order

    Example:
        >>> for entry in project.LexEntry.GetAllSorted():
        ...     print(project.LexEntry.GetHeadword(entry))
    """
    entries = [(str(e.HeadWord), e) for e in self.GetAll()]
    if case_sensitive:
        sorted_entries = sorted(entries, key=lambda x: x[0])
    else:
        sorted_entries = sorted(entries, key=lambda x: x[0].lower())

    for _, entry in sorted_entries:
        yield entry
```

#### 3.3: TextsNumberOfTexts
```python
# FLExProject.py - BEFORE
def TextsNumberOfTexts(self):
    """
    Returns the number of Texts in the Texts collection.
    """
    return self.lp.TextsOC.Count

# FLExProject.py - AFTER
def TextsNumberOfTexts(self):
    """
    Returns the number of Texts in the Texts collection.

    Note: This method delegates to TextOperations.Count()
    """
    return self.Texts.Count()
```

**Required in TextOperations:**
```python
# TextOperations.py
def Count(self):
    """
    Returns the total number of texts in the project.

    Returns:
        int: Number of texts

    Example:
        >>> count = project.Texts.Count()
        >>> print(f"Project has {count} texts")
    """
    return self.project.lp.TextsOC.Count
```

---

### BATCH 4: Custom Field Methods (6 hours)

#### 4.1: GetFieldID
```python
# FLExProject.py - BEFORE
def GetFieldID(self, className, fieldName):
    """
    Return the `FieldID` ('flid') for the given field of an LCM class.
    """
    mdc = self.project.MetaDataCacheAccessor
    if fieldName[-2:] in ("OA", "OS", "OC", "RA", "RS", "RC"):
        fieldName = fieldName[:-2]
    try:
        flid = mdc.GetFieldId(className, fieldName, True)
    except (LcmInvalidFieldException, LcmInvalidClassException) as e:
        raise FP_ParameterError(e.Message) from None
    return flid

# FLExProject.py - AFTER
def GetFieldID(self, className, fieldName):
    """
    Return the `FieldID` ('flid') for the given field of an LCM class.

    Note: This method delegates to CustomFieldOperations.FindField()
    """
    return self.CustomFields.FindField(className, fieldName)
```

**Already exists in CustomFieldOperations:**
```python
# CustomFieldOperations.py (already exists)
def FindField(self, class_name, field_name):
    """
    Find a field by class and field name.

    Args:
        class_name (str): LCM class name (e.g., "LexEntry", "LexSense")
        field_name (str): Field name (suffixes like "OA", "OS" are optional)

    Returns:
        int: Field ID (flid)

    Raises:
        ValueError: If field not found
    """
    # Implementation similar to GetFieldID
```

#### 4.2: LexiconFieldIsAnyStringType
```python
# FLExProject.py - BEFORE
def LexiconFieldIsAnyStringType(self, fieldID):
    """
    Returns `True` if the given field is any of the string types.
    """
    if not fieldID: raise FP_NullParameterError()
    field_type = self.CustomFields.GetFieldType(fieldID)
    return field_type in (CellarPropertyType.String,
                          CellarPropertyType.MultiString,
                          CellarPropertyType.MultiUnicode)

# FLExProject.py - AFTER
def LexiconFieldIsAnyStringType(self, fieldID):
    """
    Returns `True` if the given field is any of the string types.

    Note: This method delegates to CustomFieldOperations.IsStringType()
    """
    if not fieldID: raise FP_NullParameterError()
    return self.CustomFields.IsStringType(fieldID, include_multi=True)
```

**Required in CustomFieldOperations:**
```python
# CustomFieldOperations.py
def IsStringType(self, field_id, include_multi=True):
    """
    Check if a field is a string type.

    Args:
        field_id (int): Field ID to check
        include_multi (bool): If True, also returns True for MultiString/MultiUnicode

    Returns:
        bool: True if field is a string type

    Example:
        >>> if project.CustomFields.IsStringType(field_id):
        ...     print("This is a string field")
    """
    from SIL.LCModel.Core.Cellar import CellarPropertyType

    field_type = self.GetFieldType(field_id)

    if include_multi:
        return field_type in (CellarPropertyType.String,
                             CellarPropertyType.MultiString,
                             CellarPropertyType.MultiUnicode)
    else:
        return field_type == CellarPropertyType.String
```

---

### BATCH 5: Custom Field Getters (4 hours)

#### 5.1: LexiconGetEntryCustomFields
```python
# FLExProject.py - AFTER
def LexiconGetEntryCustomFields(self):
    """
    Returns a list of custom field objects for entry-level custom fields.

    Note: This method delegates to LexEntryOperations.GetCustomFields()
    """
    return self.LexEntry.GetCustomFields()
```

**Required in LexEntryOperations:**
```python
# LexEntryOperations.py
def GetCustomFields(self):
    """
    Returns all custom fields defined for lexical entries.

    Returns:
        list: List of field IDs for entry-level custom fields

    Example:
        >>> fields = project.LexEntry.GetCustomFields()
        >>> for field_id in fields:
        ...     name = project.CustomFields.GetFieldName(field_id)
        ...     print(f"Custom field: {name}")
    """
    from SIL.LCModel import LexEntryTags
    from SIL.LCModel.Infrastructure import IFwMetaDataCacheManaged

    mdc = IFwMetaDataCacheManaged(self.project.project.MetaDataCacheAccessor)

    # Get all fields for LexEntry class
    class_id = LexEntryTags.kClassId
    field_count = mdc.FieldCount

    custom_fields = []
    for flid in range(1, field_count + 1):
        try:
            field_class = mdc.GetOwnClsId(flid)
            if field_class == class_id:
                if mdc.IsCustom(flid):
                    custom_fields.append(flid)
        except:
            pass

    return custom_fields
```

---

### BATCH 6: Complex Entry Methods (4 hours)

#### 6.1: LexiconEntryAnalysesCount
```python
# FLExProject.py - BEFORE
def LexiconEntryAnalysesCount(self, entry):
    """
    Returns a count of the occurrences of the entry in the text corpus.
    """
    # Uses reflection
    count = ReflectionHelper.GetProperty(entry, "EntryAnalysesCount")
    return count

# FLExProject.py - AFTER
def LexiconEntryAnalysesCount(self, entry):
    """
    Returns a count of the occurrences of the entry in the text corpus.

    Note: This method delegates to LexEntryOperations.GetAnalysesCount()
    """
    return self.LexEntry.GetAnalysesCount(entry)
```

**Required in LexEntryOperations:**
```python
# LexEntryOperations.py
def GetAnalysesCount(self, entry):
    """
    Returns the number of times this entry appears in analyzed texts.

    Args:
        entry (ILexEntry): Lexical entry

    Returns:
        int: Count of analyses using this entry

    Note:
        This uses reflection to access the internal EntryAnalysesCount property.
        Results may differ slightly from FieldWorks displays (see LT-13997).

    Example:
        >>> entry = project.LexEntry.Find("run")
        >>> count = project.LexEntry.GetAnalysesCount(entry)
        >>> print(f"Entry appears {count} times in texts")
    """
    from SIL.LCModel.Utils import ReflectionHelper
    return ReflectionHelper.GetProperty(entry, "EntryAnalysesCount")
```

---

## Testing Pattern

For each delegated method, create a test:

```python
# tests/test_delegation.py
def test_lexicon_number_of_entries(project):
    """Test that LexiconNumberOfEntries matches LexEntry.Count()"""
    old_way = project.LexiconNumberOfEntries()
    new_way = project.LexEntry.Count()
    assert old_way == new_way

def test_writing_systems_vernacular(project):
    """Test that GetAllVernacularWSs matches WritingSystems.GetVernacular()"""
    old_way = project.GetAllVernacularWSs()
    new_way = set(project.WritingSystems.GetVernacular())
    assert old_way == new_way
```

---

## Migration Guide for Users

```python
# Old way (still works but deprecated)
count = project.LexiconNumberOfEntries()
entries = project.LexiconAllEntries()
ws_list = project.GetAllVernacularWSs()

# New way (recommended)
count = project.LexEntry.Count()
entries = project.LexEntry.GetAll()
ws_list = project.WritingSystems.GetVernacular()

# Both work during transition period!
```

---

## Checklist for Each Method

- [ ] Implement new method in Operations class (if needed)
- [ ] Update FLExProject method to delegate
- [ ] Add "Note:" comment showing delegation
- [ ] Add deprecation notice (if appropriate)
- [ ] Create unit test comparing old vs new
- [ ] Update documentation examples
- [ ] Update any demo scripts
- [ ] Test with real FLEx project

---

## Common Pitfalls

### 1. WSHandle Conversion
```python
# ❌ Wrong - loses WS conversion logic
def GetForm(self, obj):
    return obj.Form.get_String(ws)

# ✅ Right - preserves WS handling
def GetForm(self, obj, language_tag_or_handle=None):
    ws_handle = self._get_ws_handle(language_tag_or_handle)
    return obj.Form.get_String(ws_handle)
```

### 2. Error Handling
```python
# ❌ Wrong - loses error context
def SetField(self, entry, field, value):
    self.project.DomainDataByFlid.SetString(entry.Hvo, field, value)

# ✅ Right - maintains error handling
def SetField(self, entry, field, value):
    try:
        self.project.DomainDataByFlid.SetString(entry.Hvo, field, value)
    except LcmInvalidFieldException:
        raise FP_ReadOnlyError()
```

### 3. Repository Access
```python
# ❌ Wrong - bypasses project
def GetAll(self):
    repo = SomeRepository()
    return repo.AllInstances()

# ✅ Right - uses project's repository
def GetAll(self):
    repo = self.project.ObjectRepository(ISomeRepository)
    return repo.AllInstances()
```

---

## Quick Reference: What Goes Where?

| Functionality | Keep in FLExProject | Move to Operations |
|--------------|--------------------|--------------------|
| OpenProject/CloseProject | ✅ | ❌ |
| Operations properties (@property) | ✅ | ❌ |
| Business logic methods | ❌ | ✅ |
| LCM repository access helpers | ✅ (as internal) | ❌ |
| Object transformations | ❌ | ✅ |
| Writing system utilities | ❌ | ✅ |
| Custom field operations | ❌ | ✅ |
| BuildGotoURL, BestStr | ✅ (utility) | ❌ |

---

## Next: See Full Reports

- `DELEGATION_ANALYSIS_REPORT.md` - Comprehensive analysis
- `DELEGATION_SUMMARY.md` - Executive summary
- `analyze_methods.py` - Analysis script

**Start with:** Batch 2 (Writing Systems) - easiest wins!
