# Delegation Pattern Guide

**Quick Reference for Future Contributors**

This guide provides templates and decision-making tools for delegating Craig's methods to Operations classes in flexlibs.

---

## Quick Decision Tree

```
┌─────────────────────────────────────────────┐
│ Does an Operations method exist that does  │
│ exactly what Craig's method does?          │
└────────┬───────────────────────┬────────────┘
         │ YES                   │ NO
         ▼                       ▼
    ┌─────────┐          ┌────────────────────┐
    │DELEGATE │          │ Can one be added   │
    │Use      │          │ to Operations?     │
    │Template │          └───┬────────────┬───┘
    │1-7 below│              │ YES        │ NO
    └─────────┘              ▼            ▼
                      ┌────────────┐ ┌──────────────┐
                      │ Add method │ │ Keep as-is   │
                      │ to Ops,    │ │ (reflection, │
                      │ then       │ │ complexity,  │
                      │ delegate   │ │ or trivial)  │
                      └────────────┘ └──────────────┘
```

---

## Template 1: Simple Getter (No WS Parameter)

**Use when:** Getting a property/value with no writing system parameter.

```python
def MethodName(self, obj):
    """
    [Brief description of what this returns]

    Parameters:
        obj: [Object type, e.g., ILexEntry, ILexSense]

    Returns:
        [Type]: [Description of return value]

    .. note::
       This method delegates to :meth:`OperationsClass.MethodName`.
    """
    return self.Operations.MethodName(obj)
```

**Examples:**
- `LexiconGetHeadword` → `LexEntry.GetHeadword`
- `LexiconGetSensePOS` → `Senses.GetPartOfSpeech`

---

## Template 2: Simple Getter (With WS Parameter)

**Use when:** Getting multilingual string data with optional writing system.

```python
def MethodName(self, obj, languageTagOrHandle=None):
    """
    Returns [description] in the default [vernacular/analysis] WS
    or other WS as specified by `languageTagOrHandle`.

    Parameters:
        obj: [Object type]
        languageTagOrHandle: Language tag (str) or WS handle (int).
            If None, uses default [vernacular/analysis] writing system.

    Returns:
        str: [Description], or empty string if not set

    .. note::
       This method delegates to :meth:`OperationsClass.MethodName`.
    """
    return self.Operations.MethodName(obj, languageTagOrHandle)
```

**Examples:**
- `LexiconGetLexemeForm` → `LexEntry.GetLexemeForm`
- `LexiconGetSenseGloss` → `Senses.GetGloss`
- `ReversalGetForm` → `Reversal.GetForm`

---

## Template 3: Simple Setter

**Use when:** Setting a value with optional writing system parameter.

```python
def MethodName(self, obj, value, languageTagOrHandle=None):
    """
    Sets [description] for [object]:
        - `value` is the new [description]
        - `languageTagOrHandle` specifies a non-default writing system.

    Parameters:
        obj: [Object type]
        value: [Value type, e.g., str, int]
        languageTagOrHandle: Language tag (str) or WS handle (int).
            If None, uses default [vernacular/analysis] writing system.

    Returns:
        [Usually None or the object for chaining]

    .. note::
       This method delegates to :meth:`OperationsClass.MethodName`.
    """
    return self.Operations.MethodName(obj, value, languageTagOrHandle)
```

**Examples:**
- `LexiconSetLexemeForm` → `LexEntry.SetLexemeForm`
- `LexiconSetSenseGloss` → `Senses.SetGloss`
- `ReversalSetForm` → `Reversal.SetForm`

---

## Template 4: List Return (Name Extraction)

**Use when:** Returning a list of names from a collection of objects.

```python
def GetMethodName(self):
    """
    Returns a list of [description] defined in this project.

    Returns:
        list[str]: List of [description] names

    .. note::
       This method delegates to :meth:`OperationsClass.GetAll` and extracts names.
    """
    return [self.Operations.GetName(obj) for obj in self.Operations.GetAll()]
```

**Examples:**
- `GetPartsOfSpeech` → `[POS.GetName(pos) for pos in POS.GetAll()]`
- `GetPublications` → `[Publications.GetName(pub) for pub in Publications.GetAll()]`

---

## Template 5: Direct List Return

**Use when:** Returning objects directly from Operations with optional parameters.

```python
def GetMethodName(self, parameter=None):
    """
    Returns [description].

    Parameters:
        parameter: [Description of optional parameter]

    Returns:
        [Type]: [Description of return]

    .. note::
       This method delegates to :meth:`OperationsClass.GetAll`.
    """
    return self.Operations.GetAll(parameter)
```

**Examples:**
- `GetAllSemanticDomains` → `SemanticDomains.GetAll(flat=flat)`

---

## Template 6: Generator Wrapper (Formatting)

**Use when:** Providing formatted/filtered iteration over Operations data.

```python
def GetMethodName(self, supplyX=True, supplyY=True):
    """
    A generator that returns [description] as tuples of ([x], [y]).

    Parameters:
        supplyX: If True, includes [x] in results
        supplyY: If True, includes [y] in results

    Yields:
        tuple or str: [Description of yielded values]

    .. note::
       This method delegates to :meth:`OperationsClass.GetAll` for data retrieval.
    """
    for obj in self.Operations.GetAll():
        x = self.Operations.GetX(obj) if supplyX else None
        y = self.Operations.GetY(obj) if supplyY else None

        if supplyX and supplyY:
            yield (x, y)
        elif supplyX:
            yield x
        elif supplyY:
            yield y
```

**Examples:**
- `TextsGetAll` → Iterates over `Texts.GetAll()` with formatting

---

## Template 7: Count/Aggregate

**Use when:** Counting or aggregating items from an Operations iterator.

```python
def NumberOfThings(self):
    """
    Returns the total number of [things] in the project.

    Returns:
        int: Count of [things]

    .. note::
       This method delegates to :meth:`OperationsClass.GetAll` for counting.
    """
    return sum(1 for _ in self.Operations.GetAll())
```

**Examples:**
- `TextsNumberOfTexts` → `sum(1 for _ in Texts.GetAll())`

---

## Template 8: Conditional Delegation

**Use when:** Multi-step delegation with null safety or precondition checks.

```python
def MethodName(self, parameter):
    """
    [Description with note about potential None return]

    Parameters:
        parameter: [Description]

    Returns:
        [Type] or None: [Description of when None is returned]

    .. note::
       This method delegates to :meth:`OperationsClass.Method1` and
       :meth:`OperationsClass.Method2`.
    """
    intermediate = self.Operations.Method1(parameter)
    if intermediate:
        return self.Operations.Method2(intermediate)
    return None
```

**Examples:**
- `ReversalEntries` → Gets index, then gets entries if index exists
- `ReversalIndex` → Returns index or None

---

## Anti-Patterns to Avoid

### ❌ Don't Duplicate Logic

**Bad:**
```python
def LexiconGetHeadword(self, entry):
    # DON'T replicate Operations logic here!
    entry = self.__ResolveObject(entry)
    return entry.HeadWord.Text or ""
```

**Good:**
```python
def LexiconGetHeadword(self, entry):
    return self.LexEntry.GetHeadword(entry)
```

---

### ❌ Don't Add Premature Optimization

**Bad:**
```python
def LexiconGetHeadword(self, entry):
    # DON'T add caching here
    if entry.Hvo not in self._cache:
        self._cache[entry.Hvo] = self.LexEntry.GetHeadword(entry)
    return self._cache[entry.Hvo]
```

**Good:**
```python
def LexiconGetHeadword(self, entry):
    return self.LexEntry.GetHeadword(entry)
```

*(Add caching to Operations class if really needed)*

---

### ❌ Don't Use Inconsistent Property Names

**Bad:**
```python
def LexiconGetHeadword(self, entry):
    return self.LexEntry.GetHeadword(entry)

def LexiconGetSenseGloss(self, sense):
    return self.SenseOps.GetGloss(sense)  # WRONG property name!
```

**Good:**
```python
def LexiconGetHeadword(self, entry):
    return self.LexEntry.GetHeadword(entry)

def LexiconGetSenseGloss(self, sense):
    return self.Senses.GetGloss(sense)  # Consistent naming
```

---

## Pre-Implementation Checklist

Before you start delegating:

- [ ] Operations method exists with matching functionality
- [ ] Signatures are compatible (parameters, return types)
- [ ] Behavior is identical (test with real data)
- [ ] Error handling is preserved
- [ ] Writing system parameters handled correctly
- [ ] Documentation is accurate

---

## Implementation Checklist

While implementing:

- [ ] Choose correct template from this guide
- [ ] Update docstring with Sphinx RST format
- [ ] Add `:meth:` cross-reference to Operations method
- [ ] Preserve original method signature (no changes)
- [ ] Test both APIs return identical results
- [ ] Check for unintended side effects

---

## Post-Implementation Checklist

After delegation:

- [ ] Run verification tests (if available)
- [ ] Manually test with real FLEx project
- [ ] Update SYNTHESIS_REPORT.md metrics (if tracking)
- [ ] Clear git commit message listing methods
- [ ] Verify Sphinx documentation builds correctly

---

## Common Operations Properties

Reference for which Operations property to use:

| Domain | Property Name | Operations Class |
|--------|---------------|------------------|
| Lexical Entries | `self.LexEntry` | LexEntryOperations |
| Senses | `self.Senses` | LexSenseOperations |
| Examples | `self.Examples` | ExampleOperations |
| Pronunciations | `self.Pronunciations` | PronunciationOperations |
| Allomorphs | `self.Allomorphs` | AllomorphOperations |
| Reversals | `self.Reversal` | ReversalOperations |
| Texts | `self.Texts` | TextOperations |
| Parts of Speech | `self.POS` | POSOperations |
| Semantic Domains | `self.SemanticDomains` | SemanticDomainOperations |
| Custom Fields | `self.CustomFields` | CustomFieldOperations |
| Lex References | `self.LexReferences` | LexReferenceOperations |
| Publications | `self.Publications` | PublicationOperations |

---

## When NOT to Delegate

Keep original implementation if:

- ✅ Method uses reflection (e.g., `ReflectionHelper.GetProperty`)
- ✅ Method is trivial one-liner (e.g., `entry.PublishIn.Count`)
- ✅ Method calls private FLExProject helper (e.g., `__GetCustomFieldsOfType`)
- ✅ No clear Operations class home exists
- ✅ Logic is complex and UI-specific
- ✅ Operations method would need to be created just for this one use

**Examples of methods to keep:**
- `LexiconEntryAnalysesCount` (uses reflection)
- `LexiconGetSenseNumber` (uses reflection)
- `GetFieldID` (core metadata, used by many methods)
- `UnpackNestedPossibilityList` (recursive algorithm, not domain-specific)

---

## Pattern Statistics (Current Project)

From 23 delegated methods:

| Pattern | Count | % |
|---------|-------|---|
| Template 1-3: Direct 1-to-1 | 15 | 65% |
| Template 4: Name Extraction | 2 | 9% |
| Template 6: Generator Wrapper | 2 | 9% |
| Template 7: Count/Aggregate | 2 | 9% |
| Template 8: Conditional | 2 | 9% |

**Most common:** Direct 1-to-1 delegation (Templates 1-3)

---

## Example: Complete Delegation

Here's a full example showing the delegation process:

### Before (Original Craig's Method):
```python
def LexiconGetLexemeForm(self, entry, languageTagOrHandle=None):
    """
    Returns the lexeme form for `entry` in the default vernacular WS
    or other WS as specified by `languageTagOrHandle`.
    """
    WSHandle = self.__WSHandleVernacular(languageTagOrHandle)

    # ILexEntry.LexemeFormOA is IMoForm (IMoStemAllomorph or IMoAffixAllomorph)
    # IMoForm.Form is a MultiUnicodeAccessor
    form = ITsString(entry.LexemeFormOA.Form.get_String(WSHandle)).Text
    return form or ""
```

**Lines:** 8 (including logic)

### After (Delegated):
```python
def LexiconGetLexemeForm(self, entry, languageTagOrHandle=None):
    """
    Returns the lexeme form for `entry` in the default vernacular WS
    or other WS as specified by `languageTagOrHandle`.

    .. note::
       This method delegates to :meth:`LexEntryOperations.GetLexemeForm`.
    """
    return self.LexEntry.GetLexemeForm(entry, languageTagOrHandle)
```

**Lines:** 4 (just delegation)

**Code reduction:** 50% (8 lines → 4 lines)

**Benefits:**
- ✅ Logic centralized in Operations class
- ✅ Both APIs return identical results
- ✅ Bug fixes automatically propagate
- ✅ Easier to maintain

---

## Questions?

If you're unsure whether to delegate a method:

1. **Check this guide** - Does it match a template?
2. **Check SYNTHESIS_REPORT.md** - Is there a similar example?
3. **Check TEAM_DELEGATION_PLAN.md** - Was it analyzed already?
4. **Ask the team** - Get a second opinion

When in doubt, **keep it simple**. A clear, straightforward delegation is better than a clever one.

---

**Last updated:** 2025-11-24
**See also:**
- SYNTHESIS_REPORT.md (complete analysis)
- VERIFICATION_REPORT.md (V1's verification)
- TEAM_DELEGATION_PLAN.md (original plan)
