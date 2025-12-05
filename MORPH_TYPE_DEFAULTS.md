# Morph Type Default Behaviors

## Summary of Improvements

We've updated flexlibs to match FLEx GUI behavior for morph type defaults:

### ✅ **1. LexEntry.Create() - Defaults to "stem"**

**Before**:
```python
# Had to specify "stem" explicitly
entry = project.LexEntry.Create("run", "stem")
```

**After**:
```python
# Defaults to "stem" - no parameter needed!
entry = project.LexEntry.Create("run")

# Still can specify explicitly for other types
affix = project.LexEntry.Create("-ing", "suffix")
```

### ✅ **2. Allomorph.Create() - Inherits morph type from entry**

**Before**:
```python
# Had to get and pass morph type explicitly
entry = project.LexEntry.Create("run")
morph_type = entry.LexemeFormOA.MorphTypeRA
allo = project.Allomorphs.Create(entry, "running", morph_type)
```

**After**:
```python
# Inherits automatically from entry - just like FLEx GUI!
entry = project.LexEntry.Create("run")
allo = project.Allomorphs.Create(entry, "running")

# Still can override if needed
allo = project.Allomorphs.Create(entry, "ran", custom_morph_type)
```

### ✅ **3. Automatic MoStemAllomorph vs MoAffixAllomorph Selection**

The correct allomorph class is automatically chosen based on morph type GUID:

**Stem Types** (use `MoStemAllomorph`):
- stem, root, bound root, bound stem
- clitic, enclitic, proclitic
- particle
- phrase, discontiguous phrase

**Affix Types** (use `MoAffixAllomorph`):
- prefix, suffix, infix
- circumfix, simulfix, suprafix
- interfixes

---

## API Changes

### LexEntry.Create()

```python
def Create(self,
           lexeme_form,
           morph_type_name=None,  # Changed: was "stem", now None (auto-defaults to "stem")
           wsHandle=None,
           create_blank_sense=True)
```

**Parameters**:
- `morph_type_name` (str, optional): If `None` (default), uses "stem"
  - Use "prefix", "suffix", "infix" for affixes → creates `MoAffixAllomorph`
  - Use "stem", "root", "clitic" for stems → creates `MoStemAllomorph`

**Examples**:
```python
# Simple - defaults to stem
entry = project.LexEntry.Create("run")
# → Creates MoStemAllomorph with morph type "stem"

# Explicit stem type
entry = project.LexEntry.Create("go", "root")
# → Creates MoStemAllomorph with morph type "root"

# Affix
entry = project.LexEntry.Create("-ed", "suffix")
# → Creates MoAffixAllomorph with morph type "suffix"
```

---

### Allomorphs.Create()

```python
def Create(self,
           entry_or_hvo,
           form,
           morphType=None,  # Changed: was required, now optional (inherits from entry)
           wsHandle=None)
```

**Parameters**:
- `morphType` (IMoMorphType, optional): If `None` (default), inherits from `entry.LexemeFormOA.MorphTypeRA`

**Examples**:
```python
# Create stem entry
entry = project.LexEntry.Create("run")

# Add allomorph - inherits "stem" morph type automatically
allo1 = project.Allomorphs.Create(entry, "running")
# → Creates MoStemAllomorph with morph type "stem" (inherited)

allo2 = project.Allomorphs.Create(entry, "ran")
# → Creates MoStemAllomorph with morph type "stem" (inherited)

# Create affix entry
affix = project.LexEntry.Create("-ing", "suffix")

# Add allomorph - inherits "suffix" morph type automatically
allo3 = project.Allomorphs.Create(affix, "-in'")
# → Creates MoAffixAllomorph with morph type "suffix" (inherited)
```

---

## Implementation Details

### How Morph Type is Determined

1. **LexEntry.Create()**:
   ```python
   if morph_type_name is None:
       morph_type_name = "stem"  # Default to stem
   ```

2. **Allomorphs.Create()**:
   ```python
   if morphType is None:
       morphType = entry.LexemeFormOA.MorphTypeRA  # Inherit from entry
   ```

3. **Factory Selection** (both methods):
   ```python
   if __IsStemType(morphType):
       factory = IMoStemAllomorphFactory
   else:
       factory = IMoAffixAllomorphFactory
   ```

### Stem Type Detection

Based on FLEx source code (`MorphTypeAtomicLauncher.cs`), we check morph type GUID:

```python
def __IsStemType(morph_type):
    """Matches FLEx logic for determining stem vs affix types."""
    stem_guids = {
        MoMorphTypeTags.kguidMorphStem,
        MoMorphTypeTags.kguidMorphRoot,
        MoMorphTypeTags.kguidMorphBoundRoot,
        MoMorphTypeTags.kguidMorphBoundStem,
        MoMorphTypeTags.kguidMorphClitic,
        MoMorphTypeTags.kguidMorphEnclitic,
        MoMorphTypeTags.kguidMorphProclitic,
        MoMorphTypeTags.kguidMorphParticle,
        MoMorphTypeTags.kguidMorphPhrase,
        MoMorphTypeTags.kguidMorphDiscontiguousPhrase,
    }
    return morph_type.Guid in stem_guids
```

---

## Benefits

### 1. **Simpler API**
```python
# Before
entry = project.LexEntry.Create("run", "stem")
morph_type = entry.LexemeFormOA.MorphTypeRA
allo = project.Allomorphs.Create(entry, "running", morph_type)

# After
entry = project.LexEntry.Create("run")
allo = project.Allomorphs.Create(entry, "running")
```

### 2. **Matches FLEx GUI Behavior**
- Creating an entry in FLEx GUI defaults to "stem" morph type
- Adding alternate forms in FLEx GUI inherits the entry's morph type
- flexlibs now does the same!

### 3. **Prevents Errors**
- Automatically chooses correct allomorph class (MoStem vs MoAffix)
- No more creating `MoStemAllomorph` for affixes (which was a bug!)
- Consistent with FLEx's own type checking logic

### 4. **Still Flexible**
- Can override defaults when needed
- Full control available for advanced use cases
- Backward compatible (just with better defaults)

---

## Migration Guide

### Existing Code Still Works

Your existing code will continue to work:

```python
# This still works fine
entry = project.LexEntry.Create("run", "stem")
morph_type = entry.LexemeFormOA.MorphTypeRA
allo = project.Allomorphs.Create(entry, "running", morph_type)
```

### Can Simplify to

```python
# Can now simplify to
entry = project.LexEntry.Create("run")
allo = project.Allomorphs.Create(entry, "running")
```

### No Breaking Changes

- All parameters that were optional remain optional
- All required parameters remain required
- New defaults just make life easier!

---

## Test Results

```
Test 1: LexEntry.Create() with no morph_type_name
  ✓ Defaults to stem
  ✓ Creates MoStemAllomorph
  ✓ Creates blank sense

Test 2: LexEntry.Create() with "suffix" morph type
  ✓ Creates MoAffixAllomorph
  ✓ Sets morph type to suffix

Test 3: Allomorph.Create() inheriting from stem entry
  ✓ Inherits stem morph type
  ✓ Creates MoStemAllomorph

Test 4: Allomorph.Create() inheriting from affix entry
  ✓ Inherits suffix morph type
  ✓ Creates MoAffixAllomorph
```

---

## Related Documentation

- [OBJECT_CREATION_VALIDATION.md](OBJECT_CREATION_VALIDATION.md) - Object creation completeness
- [FLEX_CONVENIENCE_FEATURES.md](FLEX_CONVENIENCE_FEATURES.md) - FLEx GUI feature comparison
- API documentation in source code docstrings

---

## Summary

✅ **LexEntry.Create()** - Defaults to "stem", no parameter needed
✅ **Allomorphs.Create()** - Inherits morph type from entry
✅ **Automatic factory selection** - MoStem vs MoAffix based on type
✅ **Matches FLEx GUI behavior** exactly
✅ **No breaking changes** - existing code works
✅ **Simpler, cleaner API** for common cases
