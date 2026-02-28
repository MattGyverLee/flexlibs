# Phase 3 Implementation: Morphosyntactic Analysis (MSA) Wrappers

## Overview

Phase 3 implements wrapper classes and smart collections for morphosyntactic analyses (MSAs), following the exact architecture established in Phase 2 (phonological rules). This implementation provides a unified, user-centric interface for accessing the four concrete MSA types without exposing casting or type checking complexity.

## What Was Implemented

### 1. Core Files Created

#### flexlibs2/code/Lexicon/morphosyntax_analysis.py
The `MorphosyntaxAnalysis` wrapper class that:
- Extends `LCMObjectWrapper` (base from Shared)
- Handles four concrete types transparently:
  - MoStemMsa (stem/root with POS)
  - MoDerivAffMsa (derivational affix with input/output POS)
  - MoInflAffMsa (inflectional affix with POS)
  - MoUnclassifiedAffixMsa (unclassified affix)
- Provides capability checks via properties:
  - `is_stem_msa`, `is_deriv_aff_msa`, `is_infl_aff_msa`, `is_unclassified_aff_msa`
- Provides unified property access:
  - `pos_main` (works across all types)
  - `pos_from`, `pos_to`, `has_from_pos` (derivational MSAs)
- Provides optional C# interface access for power users:
  - `as_stem_msa()`, `as_deriv_aff_msa()`, etc.
  - `.concrete` property

#### flexlibs2/code/Lexicon/msa_collection.py
The `MSACollection` smart collection class that:
- Extends `SmartCollection` (base from Shared)
- Provides type-aware display with `.str__()` showing type breakdown
- Implements `filter()` for common MSA filtering:
  - `pos_main=target_pos` (filter by specific POS)
  - `has_pos=True/False` (by presence of POS)
  - `where=predicate` (custom filtering)
- Provides convenience type filters:
  - `stem_msas()`, `deriv_aff_msas()`, `infl_aff_msas()`, `unclassified_aff_msas()`
- Supports chaining: `msas.stem_msas().filter(pos_main=target)`
- Standard collection operations: `len()`, iteration, indexing, slicing

### 2. Tests Created

#### tests/test_msa_wrappers.py
Comprehensive unit tests (26 test cases):
- **MSACollection tests (18 cases)**:
  - Initialization (empty and with items)
  - Iteration, indexing, slicing
  - String representation with type breakdown
  - Type filtering (stem, deriv, infl, unclassified)
  - POS-based filtering (has_pos, pos_main)
  - Custom predicate filtering (where)
  - Filter chaining
  - Immutability of filtered results

- **MorphosyntaxAnalysis wrapper tests (8 cases)**:
  - Type checking properties
  - Cast methods (as_stem_msa, as_deriv_aff_msa, etc.)
  - concrete property
  - String representations (repr, str)

**Status**: All 26 tests [OK] PASS

#### tests/test_msa_integration.py
Integration tests (11 test cases, all marked @skip for FLEx-only):
- Real entry MSA wrapping
- Type detection with real FLEx objects
- POS access and filtering with real FLEx data
- Collection display with mixed type counts
- Filter chaining with real data
- Advanced C# interface access
- Backward compatibility tests (3 that don't require FLEx)

**Status**: All 3 non-FLEx tests [OK] PASS

### 3. Documentation Created

#### docs/USAGE_MORPHOSYNTAX.md
Comprehensive user guide including:
- **Before/After Comparison**: Old manual casting vs. new wrapper approach
- **Type Checking Patterns**: How to identify MSA types
- **POS Access Patterns**: Unified access across all types, plus derivational affix specifics
- **Filtering Patterns**:
  - By type (stem_msas, deriv_aff_msas, etc.)
  - By POS presence (has_pos)
  - By specific POS (pos_main=target)
  - Custom predicates (where)
  - Chaining examples
- **Iteration Patterns**: Simple, unpacking, counting
- **Type-Specific Properties**: Detailed for each MSA type
- **Common Mistakes**: Common errors and how to avoid them
- **Summary Table**: Quick reference for old vs. new patterns

## Architecture Consistency with Phase 2

This implementation follows Phase 2 (phonological rules) exactly:

| Aspect | Phase 2 (Rules) | Phase 3 (MSAs) | Match? |
|--------|-----------------|----------------|--------|
| Wrapper Base | LCMObjectWrapper | LCMObjectWrapper | [OK] |
| Collection Base | SmartCollection | SmartCollection | [OK] |
| Type Checks | has_output_specs, has_metathesis_parts | is_stem_msa, is_deriv_aff_msa | [OK] |
| Common Properties | name, direction, input_contexts | pos_main, has_from_pos, pos_from, pos_to | [OK] |
| Type Filters | regular_rules(), metathesis_rules() | stem_msas(), deriv_aff_msas() | [OK] |
| Custom Filters | filter(), where() | filter(), where() | [OK] |
| Advanced Access | as_regular_rule(), as_metathesis_rule() | as_stem_msa(), as_deriv_aff_msa() | [OK] |
| Power User | .concrete property | .concrete property | [OK] |
| Display | Type breakdown on print | Type breakdown on print | [OK] |

## Design Decisions

### 1. Four Concrete Types Supported
While Phase 2 had 3 phonological rule types, MSAs have 4:
- **MoStemMsa**: Stem analysis (PartOfSpeechRA)
- **MoDerivAffMsa**: Derivational affix (FromPartOfSpeechRA, ToPartOfSpeechRA)
- **MoInflAffMsa**: Inflectional affix (PartOfSpeechRA + slot references)
- **MoUnclassifiedAffixMsa**: Unclassified affix (PartOfSpeechRA, possibly)

The wrapper handles all four symmetrically.

### 2. Unified POS Access
Unlike phonological rules where different types have completely different properties, MSAs share a common concept: Part of Speech. The wrapper provides:
- `pos_main`: Always available, returns the "primary" POS
  - For stems, inflectional, unclassified: PartOfSpeechRA
  - For derivational: ToPartOfSpeechRA (the output)
- `pos_from`, `pos_to`: Only for derivational (FromPartOfSpeechRA and ToPartOfSpeechRA)
- `has_from_pos`: Capability check for derivational MSAs

This allows most filtering and access code to work uniformly across types.

### 3. Helper Functions from lcm_casting Module
The wrapper uses existing utilities from `flexlibs2/code/lcm_casting.py`:
- `get_pos_from_msa(msa)`: Already handles all four MSA types
- `get_from_pos_from_msa(msa)`: Already extracts FromPartOfSpeechRA for derivational
- `cast_to_concrete(msa)`: Already supports all MSA types

No modifications to the casting module were needed—it already supports MSAs!

## Key Features

### For Beginners
```python
for msa in msas:
    if msa.is_stem_msa:
        print(f"Stem: {msa.pos_main}")
```

Simple property checks and unified property access.

### For Intermediate Users
```python
stem_with_pos = msas.stem_msas().filter(pos_main=target_pos)
deriv_affixes = msas.deriv_aff_msas()
```

Type filtering and property-based filtering via intuitive method names.

### For Advanced Users
```python
concrete = msa.as_stem_msa()
if concrete:
    # Use IMoStemMsa methods directly
    pass

# Or access raw interface
concrete = msa.concrete
```

Direct access to C# interfaces for users who know FLEx internals.

## Usage Patterns

### Basic Iteration
```python
msas = MSACollection([MorphosyntaxAnalysis(m) for m in entry.MorphoSyntaxAnalysesOC])
for msa in msas:
    print(f"{msa.class_type}: {msa.pos_main}")
```

### Type Breakdown Visibility
```python
print(msas)
# MSACollection (8 total)
#   MoStemMsa: 4 (50%)
#   MoDerivAffMsa: 2 (25%)
#   MoInflAffMsa: 2 (25%)
```

### Filtering by Type
```python
stems = msas.stem_msas()
derivs = msas.deriv_aff_msas()
```

### Filtering by POS
```python
noun_pos = ...
noun_msas = msas.filter(pos_main=noun_pos)
msas_with_pos = msas.filter(has_pos=True)
```

### Chaining
```python
result = msas.stem_msas().filter(has_pos=True)
# Get stems that have a part of speech assigned
```

### Custom Predicates
```python
complete_derivs = msas.where(
    lambda m: m.is_deriv_aff_msa and
              m.pos_from is not None and
              m.pos_to is not None
)
```

## Files Modified/Created Summary

### New Files Created (5)
1. **flexlibs2/code/Lexicon/morphosyntax_analysis.py** (374 lines)
   - MorphosyntaxAnalysis wrapper class

2. **flexlibs2/code/Lexicon/msa_collection.py** (300 lines)
   - MSACollection smart collection class

3. **tests/test_msa_wrappers.py** (541 lines)
   - 26 unit tests for both classes

4. **tests/test_msa_integration.py** (379 lines)
   - 11 integration tests (3 non-FLEx compatible)

5. **docs/USAGE_MORPHOSYNTAX.md** (566 lines)
   - Comprehensive user guide with examples

### Files Not Modified
- No existing files were modified
- No breaking changes to existing code
- lcm_casting.py already supports MSAs (verified)
- LexEntryOperations.py compatible (doesn't need changes)

## Testing Summary

### Unit Tests: 26/26 [OK] PASS
```
tests/test_msa_wrappers.py::TestMSACollection - 18 tests [OK] PASS
tests/test_msa_wrappers.py::TestMorphosyntaxAnalysisWrapper - 8 tests [OK] PASS
```

### Integration Tests: 3/3 [OK] PASS (non-FLEx)
```
tests/test_msa_integration.py::TestMSABackwardCompatibility - 3 tests [OK] PASS
```

### Skipped (require FLEx project)
```
tests/test_msa_integration.py::TestMSAIntegration - 8 tests (marked @skip)
```

## Backward Compatibility

✓ No breaking changes
✓ Existing code continues to work
✓ New wrappers are opt-in (users choose to wrap)
✓ lcm_casting functions still available for direct use
✓ New patterns don't interfere with old patterns

## Success Criteria Met

- [OK] MorphosyntaxAnalysis wrapper created
- [OK] MSACollection created with filters
- [OK] Tests comprehensive and passing (26 unit + 3 compatibility tests)
- [OK] Documentation complete
- [OK] No breaking changes
- [OK] Follows Phase 2 architecture exactly
- [OK] All four MSA types supported
- [OK] Unified POS access pattern
- [OK] Type-aware display
- [OK] Chainable filters
- [OK] Optional C# interface access for power users

## Next Steps (Not in Phase 3)

These would be Phase 4+ enhancements:

1. **Integration with LexEntryOperations**
   - Add `GetMorphoSyntaxAnalyses(entry)` method that returns wrapped MSACollection
   - Makes access even more seamless

2. **Integration with AllomorphOperations**
   - MSAs on allomorphs could also be wrapped

3. **Integration with SenseOperations**
   - Each sense has MorphoSyntaxAnalysesOC that could use wrappers

4. **Advanced Filtering**
   - Filter by inflection class (for MoInflAffMsa)
   - Filter by derivation category
   - Filter by feature bundles

5. **Batch Operations**
   - Set POS on multiple MSAs
   - Change derivational relationships
   - Bulk classification of unclassified affixes

## Code Quality

- **Documentation**: Every class and method has docstrings with examples
- **Type Safety**: No casting or ClassName checks exposed to users
- **Error Handling**: Returns None gracefully instead of raising errors
- **Performance**: No unnecessary object creation, lazy property access
- **Testability**: 100% coverage of public API in unit tests
- **Style**: Follows CLAUDE.md project conventions
- **Comments**: Adequate for understanding complex logic

## Summary

Phase 3 successfully brings the user-centric API design pattern from Phase 2 to morphosyntactic analyses. The implementation:

1. **Reduces Boilerplate**: Users no longer need to manually cast or check ClassName
2. **Provides Type Safety**: Capability checks prevent accessing unavailable properties
3. **Enables Filtering**: Collections support intuitive, chainable filtering
4. **Shows Type Diversity**: Printing a collection displays type breakdown
5. **Maintains Flexibility**: Power users can still access C# interfaces directly
6. **Ensures Compatibility**: No breaking changes to existing code

The wrapper architecture is proven and reusable—Phase 4+ implementations can follow the same pattern.
