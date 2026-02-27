# Casting Audit Report: Clone/Merge Functions

**Date:** 2026-02-26
**Status:** In Progress
**Summary:** Comprehensive audit of clone/merge functions to ensure proper casting to concrete interfaces.

---

## Executive Summary

**Finding:** The codebase has a **mixed approach** to cloning operations:

1. **PhonologicalRuleOperations.Duplicate()** - ✅ **PROPERLY IMPLEMENTED**
   - Uses `clone_properties()` from `lcm_casting.py`
   - Properly casts objects to concrete interfaces via `cast_to_concrete()`
   - Handles deep cloning recursively with correct casting

2. **EnvironmentOperations.Duplicate()** - ❌ **BROKEN IMPLEMENTATION**
   - Attempts to call `SetCloneProperties()` (not exposed in Python.NET)
   - Has custom `__CopyContextObject()` that will fail on deep copy
   - Calls `hasattr(source_context, 'SetCloneProperties')` - this will never succeed

3. **PhonemeOperations.Duplicate()** - ❌ **BROKEN IMPLEMENTATION**
   - Attempts to call `SetCloneProperties()` (not exposed in Python.NET)
   - Has custom deep copy logic that will fail
   - Calls `hasattr(source_features, 'SetCloneProperties')` - this will never succeed

4. **All Other Duplicate Methods (39+ files)** - ⚠️ **VARIES**
   - Most implement `deep=False` by default
   - Those with `deep=True` likely have similar issues
   - No usage of `clone_properties()` found

---

## Current Implementation Patterns

### Pattern 1: Using clone_properties() ✅

**Files:** `PhonologicalRuleOperations.py`

```python
def Duplicate(self, item_or_hvo, insert_after=True, deep=True):
    # ...
    if deep:
        from ..lcm_casting import clone_properties
        clone_properties(source, duplicate, self.project)
    # ...
```

**Status:** Working correctly with proper casting.

---

### Pattern 2: Using SetCloneProperties() ❌

**Files:** `EnvironmentOperations.py`, `PhonemeOperations.py`, and possibly others

```python
def Duplicate(self, item_or_hvo, insert_after=True, deep=True):
    # ...
    if deep:
        # Calls custom __CopyContextObject()
        if hasattr(source, 'LeftContextOA') and source.LeftContextOA:
            duplicate.LeftContextOA = self.__CopyContextObject(source.LeftContextOA)
    # ...

def __CopyContextObject(self, source_context):
    # ...
    if hasattr(source_context, 'SetCloneProperties'):
        source_context.SetCloneProperties(new_obj)  # ❌ FAILS - NOT EXPOSED IN PYTHON.NET
    # ...
```

**Status:** Broken - SetCloneProperties is not exposed in Python.NET interfaces.

---

### Pattern 3: No Deep Copy Implementation

**Files:** Most other Operations files

```python
def Duplicate(self, item_or_hvo, insert_after=True, deep=False):  # deep=False by default
    # Only copies simple properties, no deep cloning
```

**Status:** Intentionally shallow, no deep copy needed.

---

## Casting Issues Found

### Issue 1: PhonologicalRuleOperations.__CopyOwnedObjectsDeep

**Status:** ✅ UNUSED - Not called anywhere

- Method exists (lines 872-899) but is not referenced in current code
- Replaced by `clone_properties()` approach
- **Recommendation:** Remove or deprecate

### Issue 2: PhonologicalRuleOperations Helper Methods

**Status:** ✅ UNUSED - Not called by Duplicate()

- `__CopyContextObject()` (lines 901-925)
- `__CopyRHSObject()` (lines 927-951)
- `__CopyContextProperties()` (lines 978-1012)
- `__CopyRHSProperties()` (lines 1015-1049)
- `__CopyOwnedObject()` (lines 1052-1104)
- `__CopyAllProperties()` (lines 1106-1133)

All these methods were used by the old cloning approach but are now superseded by `clone_properties()`.

**Issues with these methods (if they were used):**
1. **Missing casting** - They use `hasattr()` checks instead of casting to concrete interfaces
2. **Type-unsafe property access** - Directly access properties without casting
3. **Context type ambiguity** - Don't determine actual context interface type (IPhSimpleContextSeg vs IPhSimpleContextNC)

**Recommendation:** Remove or mark as deprecated since `clone_properties()` is the standard approach.

### Issue 3: EnvironmentOperations.__CopyContextObject

**Status:** ❌ BROKEN

```python
def __CopyContextObject(self, source_context):
    # ...
    if hasattr(source_context, 'SetCloneProperties'):
        source_context.SetCloneProperties(new_obj)  # ❌ NEVER SUCCEEDS
    # ...
```

**Problems:**
1. `SetCloneProperties()` is not exposed in Python.NET
2. `hasattr()` check will return False (method exists but Python can't access it)
3. Method returns None if SetCloneProperties check fails
4. No fallback cloning mechanism

**Recommendation:** Replace with `clone_properties()`.

### Issue 4: PhonemeOperations Deep Copy Logic

**Status:** ❌ BROKEN (for FeaturesOA)

```python
if deep:
    if hasattr(source, 'FeaturesOA') and source.FeaturesOA:
        # ...
        if hasattr(source_features, 'SetCloneProperties'):
            source_features.SetCloneProperties(new_features)  # ❌ FAILS
```

**Problems:**
1. Same issue as EnvironmentOperations - SetCloneProperties not accessible
2. CodesOS handling is shallow (just copies Representation, not nested objects)
3. Casting needed for CodesOS iteration

**Recommendation:** Replace with `clone_properties()`.

---

## clone_properties() Implementation Analysis

**File:** `lcm_casting.py` (lines 319-415)

**Strengths:**
- ✅ Casts source and dest to concrete types at start (lines 358-359)
- ✅ Uses `cast_to_concrete()` before accessing properties
- ✅ Recursively clones owned collections
- ✅ Handles collection iteration properly
- ✅ Has factory lookup for creating cloned objects

**Casting Flow:**
```python
def clone_properties(source_obj, dest_obj, project=None):
    # Proper casting upfront
    source = cast_to_concrete(source_obj)    # line 358
    dest = cast_to_concrete(dest_obj)        # line 359

    # Then safely iterate and access properties
    for attr_name in dir(source):
        attr_value = getattr(source, attr_name, None)
        # ...
        if hasattr(attr_value, 'Count') and hasattr(attr_value, 'Add'):
            # Recursively clone collections
            for item in attr_value:
                factory = _get_factory_for_class(item.ClassName, project.project)
                cloned_item = factory.Create()
                dest_collection.Add(cloned_item)
                clone_properties(item, cloned_item, project)  # Recursive!
```

**Supported Factories:**
- ✅ PhRegularRule, PhMetathesisRule, PhReduplicationRule
- ✅ PhSegRuleRHS
- ✅ PhSimpleContextSeg, PhSimpleContextNC

---

## Recommendations

### Immediate Actions (Critical)

1. **Update EnvironmentOperations.Duplicate()**
   - Replace `__CopyContextObject()` calls with `clone_properties()`
   - Remove the broken SetCloneProperties approach

2. **Update PhonemeOperations.Duplicate()**
   - Replace deep copy logic with `clone_properties()`
   - Properly handle FeaturesOA and CodesOS

3. **Remove Unused Helper Methods from PhonologicalRuleOperations**
   - Delete or deprecate:
     - `__CopyOwnedObjectsDeep()`
     - `__CopyContextObject()`
     - `__CopyRHSObject()`
     - `__CopyContextProperties()`
     - `__CopyRHSProperties()`
     - `__CopyOwnedObject()`
     - `__CopyAllProperties()`

### Medium-term Actions

4. **Extend clone_properties() Factory Support**
   - Add more factory types as needed
   - Currently supports: Phone rules, contexts, RHS objects
   - May need: Feature structures, natural classes, etc.

5. **Audit All Duplicate() Methods**
   - Review the 40+ Duplicate methods across all Operations files
   - Those with `deep=True` should use `clone_properties()`
   - Update as needed

### Documentation

6. **Update CLAUDE.md** with standard pattern:
   ```python
   # Standard Duplicate() pattern for deep cloning:
   if deep:
       from ..lcm_casting import clone_properties
       clone_properties(source, duplicate, self.project)
   ```

---

## Testing Implications

- PhonologicalRuleOperations.Duplicate() should work correctly
- EnvironmentOperations.Duplicate() with `deep=True` will return None for owned contexts
- PhonemeOperations.Duplicate() with `deep=True` will not clone FeaturesOA properly
- No existing tests for deep copying in EnvironmentOperations or PhonemeOperations

---

## Casting Pattern Summary

**Correct Pattern (Used in clone_properties()):**
```python
def clone_properties(source_obj, dest_obj, project=None):
    # Step 1: Cast to concrete interface
    source = cast_to_concrete(source_obj)
    dest = cast_to_concrete(dest_obj)

    # Step 2: Safe property access
    for attr_name in dir(source):
        attr_value = getattr(source, attr_name, None)
        # Properties are now accessible because source is concrete type
```

**Incorrect Pattern (Used in old helper methods):**
```python
def __CopyContextObject(self, src_context):
    # No casting - relies on hasattr() which may fail
    if hasattr(src_context, 'LeftContextOA'):  # May be False even if property exists
        left = src_context.LeftContextOA  # AttributeError possible
```

---

## Files Requiring Updates

| File | Method | Status | Action |
|------|--------|--------|--------|
| PhonologicalRuleOperations.py | Duplicate() | ✅ OK | Remove unused helpers |
| EnvironmentOperations.py | Duplicate() | ❌ Broken | Update to use clone_properties() |
| PhonemeOperations.py | Duplicate() | ❌ Broken | Update to use clone_properties() |
| AllomorphOperations.py | Duplicate() | ⚠️ Check | Review and test |
| And 36+ others... | Duplicate() | ⚠️ Check | Audit if deep=True |

---

## Success Criteria

- [x] PhonologicalRuleOperations correctly deep clones with all properties
- [ ] EnvironmentOperations correctly deep clones with clone_properties()
- [ ] PhonemeOperations correctly deep clones with clone_properties()
- [ ] All helper methods either removed or verified as unused
- [ ] No calls to SetCloneProperties() remain (except commented references to C# source)
- [ ] All casting uses cast_to_concrete() properly
- [ ] Tests pass for all Duplicate() methods with deep=True

