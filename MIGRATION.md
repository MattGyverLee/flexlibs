# FlexLibs2 v2.2.0 Migration Guide

## Overview

FlexLibs2 v2.2.0 introduces **wrapper classes** and **smart collections** that simplify working with polymorphic types in FieldWorks. This guide shows how to migrate from the old approach to the new, user-friendly API.

## Key Concept: No More Manual Casting

The main goal of v2.2.0 is to eliminate the need for users to manually check `ClassName` and cast to concrete types. All the complexity is hidden inside wrapper classes.

---

## Migration Examples

### Phonological Rules: Old vs New

#### Old Way (v2.1 and earlier)

```python
from flexlibs2 import FLExProject

project = FLExProject('MyProject')
rule_ops = project.PhonologicalRuleOperations()

# Get all rules - returns base interface IPhSegmentRule
all_rules = rule_ops.GetAll()

# To access type-specific properties, manual casting was required
for rule in all_rules:
    if rule.ClassName == 'PhRegularRule':
        # Must manually cast to access RightHandSidesOS
        concrete = IPhRegularRule(rule)
        rhs = concrete.RightHandSidesOS
        print(f"Regular rule output: {rhs}")
    elif rule.ClassName == 'PhMetathesisRule':
        concrete = IPhMetathesisRule(rule)
        lhs = concrete.LeftPartOfMetathesisOS
        print(f"Metathesis output: {lhs}")
    elif rule.ClassName == 'PhReduplicationRule':
        concrete = IPhReduplicationRule(rule)
        lpart = concrete.LeftPartOfReduplicationOS
        print(f"Reduplication output: {lpart}")
```

#### New Way (v2.2.0+)

```python
from flexlibs2 import FLExProject
from flexlibs2.wrappers import PhonologicalRule

project = FLExProject('MyProject')
rule_ops = project.PhonologicalRuleOperations()

# Get all rules - returns RuleCollection with wrapped objects
rules = rule_ops.GetAll()  # Type: RuleCollection(PhonologicalRule)

# Access type-specific properties transparently
for rule in rules:
    # rule is automatically the right type internally
    if rule.has_output_specs:  # Smart property check
        print(f"Rule outputs: {rule.output_segments}")
    if rule.has_metathesis_parts:
        print(f"Metathesis: {rule.left_part}, {rule.right_part}")
    if rule.has_reduplication_parts:
        print(f"Reduplication: {rule.left_part}, {rule.right_part}")
```

### Benefits Comparison

| Aspect | Old Way | New Way |
|--------|---------|---------|
| **Type Casting** | Manual `IPhRegularRule(rule)` | Automatic inside wrapper |
| **Property Access** | Must check `ClassName` first | Direct property access |
| **IDE Autocomplete** | Limited (base interface only) | Better (wrapper class hints) |
| **Error Handling** | `AttributeError` if wrong type | Type-safe capability checks |
| **Type Display** | Opaque | Clear `display_type` property |
| **Filtering** | Loop with manual checks | `filter_where()` across types |

---

## Morphosyntactic Analyses (MSAs): Old vs New

### Old Way (v2.1 and earlier)

```python
from flexlibs2 import FLExProject

project = FLExProject('MyProject')
msa_ops = project.MorphosyntaxAnalysisOperations()

# Get all MSAs - base interface
all_msas = msa_ops.GetAll()

for msa in all_msas:
    # Manual type checking
    if msa.ClassName == 'MoStemMsa':
        # Must cast to MoStemMsa for stem-specific properties
        stem_msa = IMoStemMsa(msa)
        pos = stem_msa.PartOfSpeechRA
    elif msa.ClassName == 'MoDerivAffMsa':
        deriv_msa = IMoDerivAffMsa(msa)
        from_pos = deriv_msa.FromPartOfSpeechRA
        to_pos = deriv_msa.ToPartOfSpeechRA
    elif msa.ClassName == 'MoInflAffMsa':
        infl_msa = IMoInflAffMsa(msa)
        slots = infl_msa.SlotsOS
```

### New Way (v2.2.0+)

```python
from flexlibs2 import FLExProject
from flexlibs2.wrappers import MorphosyntaxAnalysis

project = FLExProject('MyProject')
msa_ops = project.MorphosyntaxAnalysisOperations()

# Get all MSAs - returns MSACollection with wrapped objects
msas = msa_ops.GetAll()  # Type: MSACollection(MorphosyntaxAnalysis)

# Filter by type with convenience methods
stem_msas = msas.stem_msas  # Only MoStemMsa objects
deriv_msas = msas.deriv_aff_msas  # Only MoDerivAffMsa objects
infl_msas = msas.infl_aff_msas  # Only MoInflAffMsa objects

# Or iterate all with transparent access
for msa in msas:
    if msa.is_stem_msa:
        print(f"Stem POS: {msa.part_of_speech}")
    elif msa.is_deriv_aff:
        print(f"Derivational: {msa.from_pos} -> {msa.to_pos}")
    elif msa.is_infl_aff:
        print(f"Inflectional slots: {msa.slots}")
```

---

## Phonological Contexts: Old vs New

### Old Way (v2.1 and earlier)

```python
from flexlibs2 import FLExProject

project = FLExProject('MyProject')
context_ops = project.PhonologicalContextOperations()

# Get all contexts
all_contexts = context_ops.GetAll()

for ctx in all_contexts:
    # Manual type checking required
    if ctx.ClassName == 'PhSimpleContextSeg':
        simple_seg = IPhSimpleContextSeg(ctx)
        segments = simple_seg.SegmentsRC
    elif ctx.ClassName == 'PhSimpleContextNC':
        simple_nc = IPhSimpleContextNC(ctx)
        nc = simple_nc.NaturalClassRA
    elif ctx.ClassName == 'PhComplexContext':
        complex_ctx = IPhComplexContext(ctx)
        parts = complex_ctx.StrucDescOS
    elif ctx.ClassName == 'PhBoundaryContext':
        boundary = IPhBoundaryContext(ctx)
        boundary_type = boundary.StrucDescOS[0]
```

### New Way (v2.2.0+)

```python
from flexlibs2 import FLExProject
from flexlibs2.wrappers import PhonologicalContext

project = FLExProject('MyProject')
context_ops = project.PhonologicalContextOperations()

# Get all contexts - returns ContextCollection with wrapped objects
contexts = context_ops.GetAll()  # Type: ContextCollection(PhonologicalContext)

# Convenience filters for common queries
simple_seg_contexts = contexts.simple_seg_contexts
simple_nc_contexts = contexts.simple_nc_contexts
complex_contexts = contexts.complex_contexts
boundary_contexts = contexts.boundary_contexts

# Or iterate all with transparent access
for ctx in contexts:
    if ctx.is_simple_context:
        if ctx.is_segment_based:
            print(f"Segments: {ctx.segments}")
        elif ctx.is_nc_based:
            print(f"Natural class: {ctx.natural_class}")
    elif ctx.is_complex_context:
        print(f"Complex parts: {ctx.parts}")
    elif ctx.is_boundary_context:
        print(f"Boundary type: {ctx.boundary_type}")
```

---

## Backward Compatibility

### Everything Still Works!

All existing v2.1 code continues to work unchanged:

```python
# Old imports still work
from flexlibs2 import FLExProject
project = FLExProject('MyProject')

# Old operations still work
rule_ops = project.PhonologicalRuleOperations()
all_rules = rule_ops.GetAll()

# Can still access base properties
for rule in all_rules:
    print(rule.Name)  # Works - common to all rules
    print(rule.ClassName)  # Still accessible
```

**Zero Breaking Changes**

- Old code runs without modification
- New wrapper classes are purely additive
- Mix old and new approaches in same codebase if needed

---

## Migration Strategy: Gradual vs Immediate

### Option 1: Gradual Migration (Recommended)

Migrate code over time as you work on different features:

```python
# Old code (v2.1)
all_rules = rule_ops.GetAll()
for rule in all_rules:
    if rule.ClassName == 'PhRegularRule':
        # ... manual casting ...

# New code (v2.2.0)
rules = rule_ops.GetAll()  # Now returns RuleCollection
regular_rules = rules.regular_rules  # Use new convenience filter
for rule in regular_rules:
    print(rule.name)  # Wrapped interface, cleaner API
```

**Advantages:**
- No need to refactor everything at once
- Can work incrementally
- Test each section as you update it
- Old and new code can coexist

### Option 2: Immediate Full Migration

Update all code to use new wrappers immediately:

1. Replace all `GetAll()` calls with wrapper-aware versions
2. Remove manual `ClassName` checks
3. Use convenience filter methods
4. Update imports to use new wrapper classes

**Advantages:**
- Cleaner codebase
- Consistent style
- Better IDE support from the start
- No legacy code paths

**Disadvantages:**
- Larger refactoring effort upfront
- More testing needed

---

## New Features Available in v2.2.0

### Smart Collections

All collection types now show type diversity:

```python
# Display shows breakdown of types
rules = rule_ops.GetAll()
print(rules)
# Output:
# Phonological Rules (12 total)
#   PhRegularRule: 7 (58%)
#   PhMetathesisRule: 3 (25%)
#   PhReduplicationRule: 2 (17%)
```

### Convenience Filters

Type-specific filters work without checking `ClassName`:

```python
# Phonological rules
regular_rules = rules.regular_rules
metathesis_rules = rules.metathesis_rules
redup_rules = rules.reduplication_rules

# MSAs
stem_msas = msas.stem_msas
deriv_msas = msas.deriv_aff_msas
infl_msas = msas.infl_aff_msas

# Contexts
simple_seg = contexts.simple_seg_contexts
simple_nc = contexts.simple_nc_contexts
complex = contexts.complex_contexts
boundary = contexts.boundary_contexts
```

### Capability Checks

Check what properties are available without checking `ClassName`:

```python
rule = rules[0]

# Instead of: if rule.ClassName == 'PhRegularRule'
if rule.has_output_specs:  # True only for regular rules
    output = rule.output_segments

# Instead of: if rule.ClassName == 'PhMetathesisRule'
if rule.has_metathesis_parts:  # True only for metathesis rules
    lpart = rule.left_metathesis_part
    rpart = rule.right_metathesis_part
```

### Chain Filtering

Combine multiple filters:

```python
# Complex query: only metathesis rules with "feature" in name, direction L->R
specific = rules \
    .metathesis_rules \
    .filter_where(lambda r: 'feature' in r.name) \
    .filter_where(lambda r: r.direction == 'LtoR')
```

---

## Key Takeaways

| Before v2.2.0 | v2.2.0+ |
|---------------|---------|
| Check `ClassName` | Use `is_*` properties |
| Manual casting with `IType()` | Automatic inside wrapper |
| Loop with many if-else | Use convenience filter methods |
| Limited IDE support | Better autocomplete |
| Opaque types | Clear `class_type` property |

---

## Version Timeline

- **v2.1.0 and earlier**: Base operations only, manual casting required
- **v2.2.0**: Wrapper classes and smart collections available (NEW)
  - Wrappers: `PhonologicalRule`, `MorphosyntaxAnalysis`, `PhonologicalContext`
  - Collections: `RuleCollection`, `MSACollection`, `ContextCollection`
  - All new, existing code continues to work unchanged
- **v2.3.0+ (planned)**: Extended wrapper support for additional domains

---

## Getting Help

- See `API_DESIGN_USER_CENTRIC.md` for design philosophy
- Check `flexlibs2/code/wrappers/` for wrapper implementations
- Review test files for usage examples

## Support for Old API

The old API is fully supported and will continue to work. However, new code should use wrapper classes where available for better ergonomics and type safety.

