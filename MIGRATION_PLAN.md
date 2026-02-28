# API Migration Plan: Technical to User-Centric Design

**Date:** 2026-02-27
**Status:** Planning Phase
**Timeline:** 4 quarters (estimated)

---

## Executive Summary

Migrate FlexLibs2 API from technology-centric (exposing LCM complexity) to user-centric (hiding complexity, maximizing functionality). Users will work at natural abstraction level while system manages type complexity transparently.

**Key Changes:**
- Wrapper classes for multi-type scenarios
- Smart collections with unified filtering
- Capability checks instead of type checking
- Merge warnings instead of errors
- Casting becomes implementation detail only

**Backward Compatibility:** Breaking changes required. Plan semantic versioning appropriately.

---

## Phase 1: Foundation & Infrastructure (Q2 2026)

### Goal
Build foundation for wrapper classes and smart collections. No public API changes yet.

### 1.1 Enhance lcm_casting.py

**Current State:** Basic cast_to_concrete(), validate_merge_compatibility()

**Changes Needed:**
```python
# Already done:
✅ cast_to_concrete() - Convert to concrete interface
✅ validate_merge_compatibility() - Check merge compatibility
✅ clone_properties() - Deep clone with casting

# Add:
- [ ] get_concrete_type_info() - Return property info for a concrete type
- [ ] get_common_properties() - Find properties shared across concrete types
- [ ] get_type_specific_properties() - Find properties unique to a concrete type
```

**Files to Update:**
- `flexlibs2/code/lcm_casting.py`

**Effort:** 1-2 days

---

### 1.2 Create Wrapper Class Foundation

**Create base wrapper class that other wrappers inherit from:**

```python
# New file: flexlibs2/code/Shared/wrapper_base.py

class LCMObjectWrapper:
    """
    Base class for wrappers around LCM objects.

    Handles:
    - Transparent access to concrete type properties
    - Fallback to base interface properties
    - Type information exposure (__getattr__)
    """

    def __init__(self, lcm_obj):
        self._obj = lcm_obj  # Base interface
        self._concrete = cast_to_concrete(lcm_obj)  # Concrete type

    def __getattr__(self, name):
        """Try concrete type first, then base interface."""
        if name.startswith('_'):
            raise AttributeError(f"No attribute {name}")

        try:
            return getattr(self._concrete, name)
        except AttributeError:
            return getattr(self._obj, name)

    def __str__(self):
        """Show type information."""
        return f"{self.__class__.__name__}({self._obj.ClassName})"

    @property
    def class_type(self):
        """Actual concrete type (read-only)."""
        return self._obj.ClassName

    @property
    def guid(self):
        """Object GUID."""
        return self._obj.Guid

    def get_property(self, name, default=None):
        """Safe property access (returns default if not found)."""
        try:
            return getattr(self._concrete, name)
        except AttributeError:
            return default
```

**Files to Create:**
- `flexlibs2/code/Shared/wrapper_base.py`

**Effort:** 1 day

---

### 1.3 Create Smart Collection Foundation

**Create base collection class:**

```python
# New file: flexlibs2/code/Shared/smart_collection.py

class SmartCollection:
    """
    Smart collection that manages type diversity transparently.

    Features:
    - Shows type summary on display
    - Unified filtering across types
    - Type-specific filtering available
    - Natural iteration without type awareness
    """

    def __init__(self, items):
        self.items = list(items)
        self._by_type = self._group_by_type()

    def _group_by_type(self):
        """Group by ClassName internally."""
        by_type = {}
        for item in self.items:
            class_name = item.class_type if hasattr(item, 'class_type') \
                        else item.ClassName
            if class_name not in by_type:
                by_type[class_name] = []
            by_type[class_name].append(item)
        return by_type

    def __str__(self):
        """Show type summary."""
        lines = [f"{self.__class__.__name__} ({len(self.items)} items)"]
        lines.append("─" * 60)
        for class_type, items in sorted(self._by_type.items()):
            pct = 100 * len(items) / len(self.items) if self.items else 0
            lines.append(f"  {class_type:20s}: {len(items):3d} items ({pct:5.1f}%)")
        return "\n".join(lines)

    def __iter__(self):
        """Iterate naturally."""
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def filter(self, **criteria):
        """Override in subclass with domain-specific filtering."""
        raise NotImplementedError

    def by_type(self, class_type):
        """Filter to specific type."""
        filtered = [item for item in self.items
                   if (item.class_type if hasattr(item, 'class_type')
                       else item.ClassName) == class_type]
        return self.__class__(filtered)
```

**Files to Create:**
- `flexlibs2/code/Shared/smart_collection.py`

**Effort:** 1 day

---

### 1.4 Documentation & Architecture

**Create internal documentation:**
- `docs/ARCHITECTURE_WRAPPER_CLASSES.md` - How wrapper classes work
- `docs/ARCHITECTURE_SMART_COLLECTIONS.md` - How collections work
- `docs/CASTING_INTERNAL_USE.md` - Why casting is implementation detail

**Effort:** 1 day

**Phase 1 Total:** 4-5 days

---

## Phase 2: Phonological Rules Migration (Q2-Q3 2026)

### Goal
Implement full user-centric API for phonological rules. Use as reference implementation for other types.

### 2.1 Create PhonologicalRule Wrapper Class

**File:** `flexlibs2/code/Grammar/phonological_rule.py`

```python
class PhonologicalRule(LCMObjectWrapper):
    """
    User-friendly wrapper around IPhSegmentRule.

    Provides unified interface across:
    - PhRegularRule
    - PhMetathesisRule
    - PhReduplicationRule

    Users don't see these concrete types - just work with
    \"phonological rules\" naturally.
    """

    @property
    def name(self):
        """Rule name (all types)."""
        return self._obj.Name.BestAnalysisAlternative.Text

    @property
    def input_contexts(self):
        """Input contexts (all types)."""
        return list(self._concrete.StrucDescOS)

    @property
    def output_segments(self):
        """
        Output segments (smart property).

        Returns:
        - For PhRegularRule: RightHandSidesOS
        - For others: empty list (graceful degradation)
        """
        if hasattr(self._concrete, 'RightHandSidesOS'):
            return list(self._concrete.RightHandSidesOS)
        return []

    # Capability checks
    @property
    def has_output_specs(self):
        """Does this rule have output specifications?"""
        return hasattr(self._concrete, 'RightHandSidesOS')

    @property
    def has_metathesis_parts(self):
        """Does this rule have metathesis parts?"""
        return hasattr(self._concrete, 'LeftPartOfMetathesisOS')

    @property
    def has_reduplication_parts(self):
        """Does this rule have reduplication parts?"""
        return hasattr(self._concrete, 'LeftPartOfReduplicationOS')
```

**Effort:** 2-3 days

---

### 2.2 Create RuleCollection Class

**File:** `flexlibs2/code/Grammar/rule_collection.py`

```python
class RuleCollection(SmartCollection):
    """
    Smart collection of phonological rules.

    Features:
    - Shows type diversity: \"PhRegularRule (7), PhMetathesisRule (3)\"
    - Filter by common properties: filter(name_contains='voicing')
    - Type-specific access: regular_rules(), metathesis_rules()
    - Natural iteration: for rule in rules
    """

    def filter(self, name_contains=None, direction=None, stratum=None):
        """Filter by common properties."""
        results = self.items

        if name_contains:
            pattern = name_contains.lower()
            results = [r for r in results if pattern in r.name.lower()]

        if direction is not None:
            results = [r for r in results
                      if hasattr(r, 'Direction') and r.Direction == direction]

        if stratum is not None:
            results = [r for r in results
                      if hasattr(r, 'StratumRA') and r.StratumRA == stratum]

        return RuleCollection(results)

    def where(self, predicate):
        """Advanced filtering with custom function."""
        return RuleCollection([r for r in self.items if predicate(r)])

    # Convenience filters
    def regular_rules(self):
        """Get only PhRegularRule objects."""
        return self.by_type('PhRegularRule')

    def metathesis_rules(self):
        """Get only PhMetathesisRule objects."""
        return self.by_type('PhMetathesisRule')

    def reduplication_rules(self):
        """Get only PhReduplicationRule objects."""
        return self.by_type('PhReduplicationRule')
```

**Effort:** 1-2 days

---

### 2.3 Update PhonologicalRuleOperations

**Current State:** Raw LCM objects, user must cast

**Changes:**
```python
class PhonologicalRuleOperations(BaseOperations):

    def GetAll(self):
        """
        Get all phonological rules.

        Returns:
            RuleCollection: Smart collection showing type diversity
                \"PhRegularRule (7), PhMetathesisRule (3), PhReduplicationRule (2)\"

        Users iterate naturally without thinking about types.
        """
        rules = self.project.lp.PhonologicalDataOA.PhonRulesOS
        wrapped = [PhonologicalRule(r) for r in rules]
        return RuleCollection(wrapped)

    def Find(self, name):
        """Find rule by name. Returns wrapped PhonologicalRule."""
        for rule in self.GetAll():
            if rule.name == name:
                return rule
        return None

    def MergeObject(self, survivor_or_hvo, victim_or_hvo, force=False):
        """
        Merge rules.

        CHANGED: If types don't match, shows warning with:
        - What will merge (common properties)
        - What will be lost (type-specific properties)
        - Asks user: \"Continue? (y/n):\"

        No error thrown - user decides.
        """
        # ... implementation with MergeWarning ...
```

**Key Changes:**
- `GetAll()` returns `RuleCollection(wrapped)`
- `Find()` returns `PhonologicalRule(wrapped)`
- `MergeObject()` warns instead of errors
- All property access works transparently

**Effort:** 2-3 days

---

### 2.4 Update Tests

**Files to Update:**
- `tests/operations/test_phonological_rules.py` - Update all tests to work with new API

**New Tests to Add:**
- Test wrapper property access
- Test collection type summary display
- Test filtering across types
- Test merge warning display

**Effort:** 3-4 days

---

### 2.5 Documentation

**Update:**
- Docstrings in PhonologicalRuleOperations
- User guide showing new API patterns
- Migration guide for users upgrading

**Effort:** 1-2 days

**Phase 2 Total:** 12-18 days

---

## Phase 3: MSA (Morphosyntactic Analysis) Migration (Q3 2026)

### Goal
Apply same pattern to MSAs. Use phonological rules as reference.

### Types to Handle
- MoStemMsa
- MoDerivAffMsa
- MoInflAffMsa
- MoUnclassifiedAffixMsa

### 3.1 Create Wrapper & Collection

**Files:**
- `flexlibs2/code/Lexicon/morphosyntax_analysis.py` - MorphosyntaxAnalysis wrapper
- `flexlibs2/code/Lexicon/msa_collection.py` - MSACollection smart collection

**Effort:** 5-7 days

### 3.2 Update Operations

**Files:**
- Update `LexEntryOperations.py` to use MSACollection
- Update `AllomorphOperations.py` if it exposes MSAs

**Effort:** 2-3 days

### 3.3 Tests & Documentation

**Effort:** 2-3 days

**Phase 3 Total:** 10-13 days

---

## Phase 4: Context Types Migration (Q3-Q4 2026)

### Goal
Apply pattern to phonological contexts.

### Types to Handle
- PhSimpleContextSeg
- PhSimpleContextNC
- PhIterationContext

### 4.1 Create Wrappers & Collection

**Files:**
- `flexlibs2/code/Grammar/phonological_context.py` - Context wrapper
- `flexlibs2/code/Grammar/context_collection.py` - ContextCollection

**Effort:** 5-7 days

### 4.2 Update Operations

**Files:**
- Update `EnvironmentOperations.py`
- Update `PhonologicalRuleOperations.py` (StrucDescOS now returns wrapped contexts)

**Effort:** 2-3 days

### 4.3 Tests & Documentation

**Effort:** 2-3 days

**Phase 4 Total:** 10-13 days

---

## Phase 5: Final Polish & Release (Q4 2026)

### 5.1 Audit All Operations

**Review:** Every Operations class for:
- GetAll() returns smart collection
- Find() returns wrapped object
- MergeObject() has warnings not errors
- CloneObject() uses clone_properties()

**Effort:** 3-4 days

### 5.2 Update User Documentation

**Create:**
- **Getting Started Guide** - Show new natural API patterns
- **Migration Guide** - Show old vs new code
- **Type System Guide** - Explain wrapper/collection pattern
- **API Reference** - Updated with new return types

**Effort:** 3-5 days

### 5.3 Version & Release

**Actions:**
- Update version to 3.0.0 (major breaking change)
- Create MIGRATION_GUIDE.md for users
- Update CHANGELOG
- Release on PyPI

**Effort:** 1-2 days

### 5.4 Extended Testing

**Create:**
- Integration tests showing new patterns
- Performance tests (collections shouldn't be slower)
- Type-specific tests for wrapped objects

**Effort:** 2-3 days

**Phase 5 Total:** 10-14 days

---

## Timeline Summary

| Phase | Duration | Quarter | Key Deliverable |
|-------|----------|---------|---|
| 1: Foundation | 4-5 days | Q2 | Wrapper base classes, smart collections |
| 2: Phon Rules | 12-18 days | Q2-Q3 | Reference implementation |
| 3: MSAs | 10-13 days | Q3 | Morphosyntactic analysis API |
| 4: Contexts | 10-13 days | Q3-Q4 | Phonological context API |
| 5: Polish | 10-14 days | Q4 | Documentation, release |
| **Total** | **46-63 days** | **Q2-Q4** | **Full API redesign** |

---

## Rollout Strategy

### Option A: All at Once
- Complete all phases
- Release as v3.0.0
- Clear breaking change message
- Pro: Clean migration, no confusion
- Con: Large breaking change

### Option B: Gradual Rollout
- Phase 1-2 (Phon Rules) as v2.5.0-beta
- Phase 3 (MSAs) as v2.6.0-beta
- Phase 4 (Contexts) as v2.7.0-beta
- Phase 5 as v3.0.0 stable
- Pro: Users can adapt gradually
- Con: Dual APIs during transition

### Recommendation
**Option A (All at Once)** - Benefits:
- Single migration path for users
- No confusion from dual APIs
- Clear story: "We redesigned the API to be more intuitive"
- Cleaner codebase

---

## Risk Mitigation

### Risk 1: Breaking Changes Upset Users
**Mitigation:**
- Provide clear migration guide
- Version appropriately (v3.0.0)
- Create before/after examples
- Host webinar showing new patterns

### Risk 2: Wrapper/Collection Performance
**Mitigation:**
- Profile early (Phase 2)
- Keep wrappers lightweight
- Cache concrete type on first access
- Document performance characteristics

### Risk 3: Incomplete Type Coverage
**Mitigation:**
- Start with well-understood types (phonological rules)
- Reference implementation serves as template
- Build in extensibility from start

### Risk 4: Testing Complexity
**Mitigation:**
- Comprehensive test suite from start
- Integration tests show real workflows
- Maintain old tests during migration (adapt them)

---

## Success Criteria

Phase completion criteria:

✅ **Phase 1**
- Wrapper base class works
- Smart collection works
- Internal documentation complete

✅ **Phase 2**
- Phonological rules API works naturally
- Users can filter across types without thinking about ClassName
- Merge warnings inform without blocking
- Tests pass with new API

✅ **Phase 3**
- MSA API follows same pattern as Phase 2
- No users complaining about MSA complexity
- Performance acceptable

✅ **Phase 4**
- Context API follows same pattern
- All type combinations work together

✅ **Phase 5**
- Users understand new API from docs
- Old code easily converts to new patterns
- v3.0.0 released with clear communication

---

## Decision Points

### Decision 1: Wrapper Performance (Phase 1-2)
If wrapper performance is poor:
- **Option A:** Optimize wrappers (caching, lazy evaluation)
- **Option B:** Return raw objects but add methods for safe access
- **Recommendation:** Option A - Profile and optimize

### Decision 2: Collection Display Format (Phase 2)
If type summary is too verbose:
- **Option A:** Show ASCII table (current design)
- **Option B:** Show one-line summary
- **Option C:** Show nothing, let user call .types property
- **Recommendation:** Option A with option to customize

### Decision 3: Backward Compatibility (Phase 5)
If users need old API:
- **Option A:** Provide compatibility wrapper (v2.x branch)
- **Option B:** Create v2.x → v3.0 converter script
- **Option C:** No backward compatibility
- **Recommendation:** Option B - Script to help migration

---

## Documentation to Create

### User-Facing
- [ ] Migration Guide: Old API → New API
- [ ] Getting Started: New API patterns
- [ ] API Reference: Updated with new return types
- [ ] Type System Guide: Wrapper/collection explanation
- [ ] Before/After Examples: Common workflows

### Developer-Facing
- [ ] Architecture: Wrapper classes
- [ ] Architecture: Smart collections
- [ ] Casting: Why it's internal only
- [ ] Extending: How to add wrappers for new types

### Internal
- [ ] Phase 1: Foundation checklist
- [ ] Phase 2: Phonological rules checklist
- [ ] Phases 3-4: Template for new types
- [ ] Testing: Comprehensive test patterns

---

## Communication Plan

### Month 1 (Start of Q2)
- **Announce** design decision on GitHub discussions
- **Share** API_DESIGN_USER_CENTRIC.md with community
- **Gather** feedback from power users

### Month 2-3 (Phase 1-2)
- **Weekly** progress updates
- **Announce** beta release when Phase 2 complete
- **Invite** beta testing

### Month 4 (Phase 3-4)
- **Highlight** improvements in blog post
- **Show** before/after code comparisons
- **Gather** user feedback on beta

### Month 5 (Phase 5)
- **Announce** v3.0.0 release date
- **Release** comprehensive migration guide
- **Host** webinar: \"What's New in FlexLibs2 v3.0\"
- **Release** v3.0.0

---

## Appendix: Code Examples

### Example 1: Get All Rules (Old vs New)

**OLD API**
```python
# User must manage multiple concrete types
regular = phonRuleOps.GetAll(class_type='PhRegularRule')
metathesis = phonRuleOps.GetAll(class_type='PhMetathesisRule')

for rule in regular:
    # Cast to access properties
    concrete = IPhRegularRule(rule)
    print(f"{rule.Name}: {concrete.RightHandSidesOS.Count} outputs")
```

**NEW API**
```python
# Simple, natural query
rules = phonRuleOps.GetAll()
print(rules)  # Shows type breakdown

for rule in rules:
    # Works for any type
    print(f"{rule.name}: {len(rule.output_segments)} outputs")
```

### Example 2: Filter Rules (Old vs New)

**OLD API**
```python
# Must query and filter separately per type
regular = [r for r in phonRuleOps.GetAll(class_type='PhRegularRule')
          if 'voic' in r.Name.BestAnalysisAlternative.Text.lower()]
metathesis = [r for r in phonRuleOps.GetAll(class_type='PhMetathesisRule')
             if 'voic' in r.Name.BestAnalysisAlternative.Text.lower()]
voicing = regular + metathesis
```

**NEW API**
```python
# Simple, unified filter
voicing = phonRuleOps.GetAll().filter(name_contains='voicing')
```

### Example 3: Type-Specific Operations (Old vs New)

**OLD API**
```python
# Must check ClassName
for rule in rules:
    if rule.ClassName == 'PhRegularRule':
        concrete = IPhRegularRule(rule)
        for rhs in concrete.RightHandSidesOS:
            print(rhs.Guid)
```

**NEW API**
```python
# Capability check, not type check
for rule in rules:
    if rule.has_output_specs:
        for rhs in rule.output_specs:
            print(rhs.Guid)
```

