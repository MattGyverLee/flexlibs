# API Clutter Audit: Duplicate Methods

**Date:** 2026-02-28
**Scope:** All 42+ Duplicate methods across flexlibs2/code
**Status:** Analysis complete

---

## Executive Summary

The Duplicate() methods have significant API clutter:

- **9 operations** accept `insert_after` parameter that is completely ignored
- **3 operations** accept parameters documented as "has no effect" or "reserved for future use"
- **3 operations** raise `NotImplementedError` but still have method signatures
- **Multiple inconsistencies** in behavior, documentation, and implementation patterns

---

## Critical Issues (Fix These First)

### 1. INSERT_AFTER PARAMETER: 9 Operations Where It's Completely Ignored

These operations **accept the parameter but don't use it at all**, yet don't document this clearly:

#### ✗ **FilterOperations.Duplicate()** (line 1212)
- **Status:** insert_after is completely ignored
- **Docstring:** "insert_after (bool): Not applicable for filters (ignored)."
- **Implementation:** Parameter never used
- **Why:** Filters are JSON-based, not LCM-registered sequences
- **Recommendation:** **REMOVE parameter** OR document more clearly at method signature level

#### ✗ **MediaOperations.Duplicate()** (line 288)
- **Status:** insert_after is completely ignored
- **Docstring:** Documents "ignored" TWICE (redundant, lines 288 & 297)
- **Implementation:** Parameter never used
- **Why:** Media files not in a sequence
- **Recommendation:** **REMOVE parameter** and redundant docs

#### ✗ **TextOperations.Duplicate()** (line 204)
- **Status:** insert_after is completely ignored
- **Docstring:** "Not applicable for texts (they are added to project-level collection, not a sequence)"
- **Implementation:** Parameter never used
- **Why:** Texts stored in collection, not sequence
- **Recommendation:** **REMOVE parameter**

#### ✗ **WordformOperations.Duplicate()** (line 716)
- **Status:** insert_after is completely ignored
- **Docstring:** "Not applicable for wordforms (they are added to inventory, not sequence)"
- **Implementation:** Parameter never used; always appends to WordformInventoryOC
- **Why:** Wordforms in collection, not sequence
- **Recommendation:** **REMOVE parameter**

#### ✓ **LexEntryOperations.Duplicate()** (line 299)
- **Status:** insert_after parameter accepted but has LIMITED effect
- **Docstring:** "insert_after parameter has limited effect since lexicon is sorted alphabetically"
- **Issue:** Users think positioning works when it doesn't reliably due to auto-sorting
- **Recommendation:** Either REMOVE parameter OR explain that auto-sorting overrides it

#### ✗ **CustomFieldOperations.Duplicate()** (line 1345)
- **Status:** Method raises NotImplementedError
- **Docstring:** "This operation is not supported"
- **Parameter:** Still accepts insert_after despite not being implemented
- **Recommendation:** Remove signature entirely or handle consistently

#### ✗ **ProjectSettingsOperations.Duplicate()** (line 988)
- **Status:** Method raises NotImplementedError
- **Issue:** Same as CustomFieldOperations
- **Recommendation:** Remove signature entirely

#### ✗ **WritingSystemOperations.Duplicate()** (line 972)
- **Status:** Method raises NotImplementedError
- **Issue:** Same as CustomFieldOperations
- **Recommendation:** Remove signature entirely

#### ✗ **ExampleOperations.Duplicate()** (line 324)
- **Status:** Questionable behavior
- **Docstring:** "insert_after=True preserves the original example's position/priority"
- **Implementation:** Does process insert_after (lines 305-312)
- **Issue:** Unclear if position preservation actually works reliably
- **Recommendation:** Test and document behavior clearly OR remove parameter

---

### 2. PARAMETERS DOCUMENTED AS "DOES NOTHING"

These operations explicitly document that a parameter has no effect—dead code that's acknowledged:

#### ✗ **PersonOperations.Duplicate()** (line 945)
- **Parameter:** deep
- **Docstring:** "Reserved for future use (persons have no owned objects). Currently has no effect."
- **Implementation:** Parameter never used
- **Recommendation:** **REMOVE parameter** (this was partially addressed with earlier cleanup)

#### ✗ **NaturalClassOperations.Duplicate()** (line 263)
- **Parameter:** deep
- **Docstring:** "Note: NaturalClass has no owned objects, so deep has no effect." (line 273)
- **Implementation:** Parameter never used
- **Recommendation:** **REMOVE parameter** (this was partially addressed with earlier cleanup)

#### ✗ **SegmentOperations.Duplicate()** (line 537)
- **Parameter:** deep
- **Docstring:** "Currently not used for segments (analyses are never copied)." (line 550)
- **Also says:** "Parameter kept for consistency with other Duplicate() methods." (line 584)
- **Implementation:** Parameter never used
- **Issue:** EXPLICIT ADMISSION OF API CLUTTER ("kept for consistency")
- **Recommendation:** **REMOVE parameter** (this was partially addressed with earlier cleanup)

---

### 3. NOTIMPLEMENTEDERROR STUBS (Methods That Don't Work)

Three operations have Duplicate() methods that immediately raise NotImplementedError:

#### ✗ **CustomFieldOperations.Duplicate()** (line 1345+)
```python
def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
    raise NotImplementedError("Custom fields cannot be duplicated...")
```
- **Issue:** Why have method signature if not implemented?
- **Recommendation:** Remove method OR use consistent pattern for all non-implemented operations

#### ✗ **ProjectSettingsOperations.Duplicate()** (line 988+)
```python
def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
    raise NotImplementedError("Project settings cannot be duplicated...")
```
- **Same issue as above**

#### ✗ **WritingSystemOperations.Duplicate()** (line 972+)
```python
def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
    raise NotImplementedError("Writing systems cannot be duplicated...")
```
- **Same issue as above**

**Recommendation:** Use a base class approach or `@abstractmethod` instead of dummy implementations that raise errors.

---

## Secondary Issues (Should Fix)

### 4. REDUNDANT/INCONSISTENT DOCUMENTATION

#### ✗ **MediaOperations.Duplicate()** (lines 288 & 297)
- **Issue:** Documents "insert_after is ignored" TWICE—redundant
- **Location:** Lines 288 and 297 have nearly identical text
- **Recommendation:** Keep only one, remove duplicate

---

### 5. INCONSISTENT IMPLEMENTATION PATTERNS

#### The Big Picture
Different operations use different patterns for the same operation:

**Pattern A: Factory.Create() + Add/Insert**
```python
# ExampleOperations (line 301)
factory = self.project.project.ServiceLocator.GetService(IXxxFactory)
new_item = factory.Create()
duplicate.xxxOS.Add(new_item)
```

**Pattern B: CreateAndAppendElement() with Fallback**
```python
# PhonologicalRuleOperations (lines 835-850)
try:
    CreateAndAppendElement(...)
except:
    factory = self.project.project.ServiceLocator.GetService(IXxxFactory)
    new_item = factory.Create()
```

**Pattern C: Custom JSON/Dict Objects**
```python
# FilterOperations (lines 1258-1266)
# Creates dict instead of LCM objects
```

**Issue:** Users/maintainers can't predict how an operation will work—no consistent pattern
**Recommendation:** Standardize factory pattern across all operations

---

### 6. SILENT FAILURES & MISSING ERROR HANDLING

#### ✗ **SegmentOperations.Duplicate()** (lines 617-629)
```python
try:
    current_index = seg_list.index(segment_obj)
    # ... insert at position ...
except ValueError:
    pass  # Silently leave at end
```

**Issue:** If segment not found, silently leaves at end instead of raising error
**Impact:** Users don't know positioning failed
**Recommendation:** Either raise informative error OR log warning

#### ✗ **AllomorphOperations.Duplicate()** (lines 349-370)
```python
class_name = source.ClassName
factory = None
if class_name == 'MoStemAllomorph':
    # ...
else:
    # factory remains None!
# No null check before use
```

**Issue:** If allomorph type not recognized, factory is None—would fail with confusing error
**Recommendation:** Raise informative error for unrecognized types

---

### 7. INCONSISTENT insert_after IMPLEMENTATION

**Implementations that actually work:**
- AllomorphOperations (lines 368-381)
- ExampleOperations (lines 305-312)
- AgentOperations (lines 399-402)
- PersonOperations (lines 998-1005)
- NaturalClassOperations (lines 317-326)

**Implementations that are half-implemented:**
- SegmentOperations (tries but silently fails on ValueError)
- PhonologicalRuleOperations (uses fallback pattern)

**Not implemented at all:**
- FilterOperations, MediaOperations, TextOperations, WordformOperations (and 3 with NotImplementedError)

**Issue:** Users can't know which operations support insert_after without reading code
**Recommendation:** Document clearly in method signature or class docstring

---

### 8. INCONSISTENT deep PARAMETER DEFAULTS

**deep=True by default (24 operations):**
- LexEntryOperations, LexSenseOperations, TextOperations, ParagraphOperations, etc.
- Pattern: Composite/hierarchical objects

**deep=False by default (3 operations):**
- ExampleOperations, PronunciationOperations, GramCatOperations, POSOperations
- Pattern: Mixed (some own objects, some prefer flat)

**Issue:** No clear rule for which should be True vs False
**Recommendation:** Document the pattern clearly OR standardize all to True (since we're making deep=True the norm for objects that own things)

---

### 9. INCOMPLETE METHOD IMPLEMENTATION

#### ✗ **DiscourseOperations.Duplicate()** (lines 1067-1076)
```python
if deep and hasattr(source, 'RowsOS') and source.RowsOS.Count > 0:
    for row in source.RowsOS:
        dup_row = row_factory.Create()
        duplicate.RowsOS.Add(dup_row)

        # Note: Full row/cell duplication is complex and would require
        # additional logic to copy cell contents, word groups, markers, etc.
        # For now, we create empty rows
```

**Issue:** Deep duplication creates empty rows instead of copying content
**Impact:** Users get structure but no data
**Recommendation:** Either implement fully OR document limitation clearly

---

## API Clutter Summary Table

| Issue | Count | Examples | Severity |
|-------|-------|----------|----------|
| insert_after ignored but accepted | 4 | FilterOps, MediaOps, TextOps, WordformOps | 🔴 HIGH |
| insert_after limited/questionable | 2 | LexEntryOps, ExampleOps | 🟡 MEDIUM |
| insert_after NotImplementedError | 3 | CustomFieldOps, ProjectSettingsOps, WritingSystemOps | 🟡 MEDIUM |
| Parameters documented as "no effect" | 3 | PersonOps, NaturalClassOps, SegmentOps | 🟡 MEDIUM |
| Redundant documentation | 1 | MediaOps (insert_after noted twice) | 🟢 LOW |
| Inconsistent patterns | 5+ | Factory usage varies wildly | 🟡 MEDIUM |
| Silent failures | 1 | SegmentOps silent ValueError | 🟡 MEDIUM |
| Incomplete implementation | 1 | DiscourseOps empty rows | 🟡 MEDIUM |

---

## Recommended Cleanup Priority

### Phase 1: Remove Useless Parameters (HIGH)
1. Remove `insert_after` from: FilterOperations, MediaOperations, TextOperations, WordformOperations
2. Remove `deep` from remaining operations that document "no effect"

### Phase 2: Fix NotImplementedError Stubs (MEDIUM)
3. CustomFieldOperations, ProjectSettingsOperations, WritingSystemOperations - decide on consistent pattern

### Phase 3: Standardize Implementation (MEDIUM)
4. Standardize factory pattern across all operations
5. Standardize insert_after implementation or document which ops don't support it

### Phase 4: Clean Up Documentation (LOW)
6. Remove redundant docs (MediaOperations duplicate notes)
7. Document clearly which operations support which features

### Phase 5: Fix Error Handling (MEDIUM)
8. Add proper error handling instead of silent failures
9. Validate inputs before use (AllomorphOperations factory type check)

---

## Impact of Cleanup

**Current State:**
- 42 Duplicate methods
- Inconsistent parameter support
- Unclear which operations work how
- 9 operations accept parameters that don't work
- Dead code acknowledged in comments

**After Cleanup:**
- Consistent parameter expectations
- Clear documentation of what's supported
- Removal of dead code
- Easier to use and maintain
- Reduced confusion for users

---

## Related Documents

- DEEP_PARAMETER_REMOVAL.md - Already completed cleanup
- DEEP_CLONE_IMPLEMENTATION.md - Deep parameter standardization
- DEEP_CLONE_ANALYSIS.md - Original analysis
