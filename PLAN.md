# FlexLibs2 v2.2 Implementation Plan - Complete

**Target Version:** v2.2 (comprehensive improvement)
**Scope:** Wrapper classes + smart collections for all multi-type scenarios
**Backward Compatible:** All existing code continues to work
**Timeline:** 4-5 weeks (5-6 sprints)
**Effort:** ~60-80 hours total

---

## What We Already Have ✅

- `clone_properties()` - Deep cloning with automatic casting
- `validate_merge_compatibility()` - Type-safe merge validation
- Type-safe merge operations with warnings (not errors)
- Standardized cloning across all operations
- Casting utilities in `lcm_casting.py`

## What v2.2 Adds (Complete)

**Wrapper Classes** for all multi-type scenarios:
- PhonologicalRule (PhRegularRule, PhMetathesisRule, PhReduplicationRule)
- MorphosyntaxAnalysis (MoStemMsa, MoDerivAffMsa, MoInflAffMsa, etc.)
- PhonologicalContext (PhSimpleContextSeg, PhSimpleContextNC, etc.)

**Smart Collections** with unified filtering:
- RuleCollection (for all phonological rules)
- MSACollection (for all MSAs)
- ContextCollection (for all contexts)

**Enhanced Operations** returning wrapped objects:
- PhonologicalRuleOperations
- LexEntryOperations (for MSA access)
- EnvironmentOperations (for context access)

**Better error messages** - Type mismatches inform instead of crash

---

## Implementation Phases

### Phase 1: Foundation (Week 1) - 12 hours

#### Sprint 1.1: Base Infrastructure (4 hours)

**Task 1.1.1: Create wrapper_base.py**
- File: `flexlibs2/code/Shared/wrapper_base.py`
- Simple base class with:
  - `__init__(lcm_obj)` - store base interface and concrete type
  - `__getattr__()` - route property access intelligently
  - `class_type` property - show actual concrete type
  - `get_property()` method - safe property access

**Task 1.1.2: Create smart_collection.py**
- File: `flexlibs2/code/Shared/smart_collection.py`
- Base class with:
  - `__iter__()` - natural iteration
  - `__str__()` - show type breakdown
  - `__len__()` - support len()
  - `filter()` - abstract, override in subclasses
  - `by_type()` - filter to specific concrete type

**Task 1.1.3: Add helper functions to lcm_casting.py**
- `get_common_properties()` - find properties across types
- `get_concrete_type_properties()` - find type-specific properties

**Review Checklist:**
- [ ] Wrapper base class works with all object types
- [ ] Smart collection handles empty lists
- [ ] Type grouping works correctly

---

#### Sprint 1.2: Test Infrastructure (3 hours)

**Task 1.2.1: Create tests/test_wrappers.py**
- Test wrapper base class
- Test property routing
- Test class_type detection
- Test get_property() method

**Task 1.2.2: Create tests/test_collections.py**
- Test collection creation
- Test iteration
- Test __str__() output format
- Test by_type() filtering
- Test empty collection handling

**Review Checklist:**
- [ ] All base class functionality tested
- [ ] Edge cases covered (None values, empty collections)
- [ ] Tests pass without exceptions

---

#### Sprint 1.3: Documentation (2 hours)

**Task 1.3.1: Create docs/ARCHITECTURE_WRAPPERS.md**
- Why wrapper classes exist
- How they work internally
- Pattern for creating new wrappers
- Code examples

**Task 1.3.2: Create docs/ARCHITECTURE_COLLECTIONS.md**
- Why smart collections exist
- Filtering patterns
- Type breakdown display
- Extension patterns

**Task 1.3.3: Update CLAUDE.md**
- Add to "When to Consult Claude"
- Link to new architecture docs

---

### Phase 2: Phonological Rules (Week 2) - 16 hours

#### Sprint 2.1: Wrapper Class (5 hours)

**Task 2.1.1: Create phonological_rule.py**
- File: `flexlibs2/code/Grammar/phonological_rule.py`
- Wrapper class with:
  - `name` property - rule name across all types
  - `input_contexts` property - input structural description
  - `has_output_specs` property - check for RHS
  - `output_specs` property - get RHS if exists
  - `has_metathesis_parts` property - check for metathesis
  - `has_redup_parts` property - check for reduplication

**Task 2.1.2: Create rule_collection.py**
- File: `flexlibs2/code/Grammar/rule_collection.py`
- Collection class with:
  - `filter()` - by name, direction, stratum
  - `where()` - custom predicate filtering
  - `regular_rules()` - shortcut filter
  - `metathesis_rules()` - shortcut filter
  - `redup_rules()` - shortcut filter

**Task 2.1.3: Unit tests for wrappers and collections**
- File: `tests/test_phonological_rules_wrappers.py`
- Test each wrapper property
- Test filtering by each criterion
- Test type-specific filters
- Test with actual FLEx data

**Review Checklist:**
- [ ] All wrapper properties work with all rule types
- [ ] Filtering returns correct subsets
- [ ] Type-specific filters work correctly
- [ ] Display shows correct type breakdown

---

#### Sprint 2.2: Operations Integration (4 hours)

**Task 2.2.1: Update PhonologicalRuleOperations.GetAll()**
- Return `RuleCollection` instead of raw list
- Wrap each rule in `PhonologicalRule`

**Task 2.2.2: Update PhonologicalRuleOperations.Find()**
- Return wrapped `PhonologicalRule`
- Work with wrapped rules

**Task 2.2.3: Test integration**
- Existing tests still pass
- New patterns work correctly
- Performance acceptable

**Task 2.2.4: Update docstrings**
- Add examples showing new patterns
- Show filtering examples
- Show property access examples

**Review Checklist:**
- [ ] GetAll() returns RuleCollection
- [ ] Find() returns wrapped rule
- [ ] All existing tests pass
- [ ] New usage examples in docstrings

---

#### Sprint 2.3: Documentation (3 hours)

**Task 2.3.1: Create docs/USAGE_PHONOLOGICAL_RULES.md**
- Before/after examples
- How to access properties
- How to filter across types
- How to check capabilities

**Task 2.3.2: Update README.rst**
- Add section on phonological rules
- Show new simple patterns
- Link to migration guide

**Task 2.3.3: Create migration guide snippet**
- Old way vs new way
- Show both still work

---

#### Sprint 2.4: Integration Testing (4 hours)

**Task 2.4.1: End-to-end tests**
- Get all rules
- Filter by various criteria
- Access properties
- Verify type information
- Test with real FLEx project data

**Task 2.4.2: Performance tests**
- Verify no significant slowdown
- Check memory usage
- Document performance characteristics

**Task 2.4.3: Merge operation testing**
- Test merge warnings
- Test with different rule types
- Test successful merges

**Review Checklist:**
- [ ] All integration tests pass
- [ ] Performance acceptable
- [ ] No regressions in existing functionality

---

### Phase 3: Morphosyntactic Analyses (Week 3) - 16 hours

#### Sprint 3.1: Wrapper & Collection (5 hours)

**Task 3.1.1: Create morphosyntax_analysis.py**
- File: `flexlibs2/code/Lexicon/morphosyntax_analysis.py`
- Wrapper class for IMoMorphSynAnalysis with properties:
  - `class_type` - which concrete type (inherited)
  - `is_stem_msa` - check if MoStemMsa
  - `is_deriv_aff_msa` - check if MoDerivAffMsa
  - `is_infl_aff_msa` - check if MoInflAffMsa
  - And type-specific property accessors

**Task 3.1.2: Create msa_collection.py**
- File: `flexlibs2/code/Lexicon/msa_collection.py`
- Collection class with:
  - `filter()` - by any common property
  - Type-specific filters
  - Display showing type breakdown

**Task 3.1.3: Tests**
- File: `tests/test_msa_wrappers.py`
- Test wrapper with all MSA types
- Test filtering
- Test with real LexEntry data

**Review Checklist:**
- [ ] Works with all MSA types
- [ ] Filtering correct
- [ ] No crashes on edge cases

---

#### Sprint 3.2: Operations Integration (4 hours)

**Task 3.2.1: Update AllomorphOperations or relevant file**
- GetAll() return wrapped MSAs
- Find() return wrapped MSA
- Update docstrings

**Task 3.2.2: Consider LexEntryOperations**
- Entries have MSAs collection
- May need special handling

**Task 3.2.3: Integration tests**
- Test MSA access from entries
- Test filtering
- Test merging MSAs

**Review Checklist:**
- [ ] MSAs accessible from entries
- [ ] Operations return wrapped objects
- [ ] Tests pass

---

#### Sprint 3.3: Documentation (3 hours)

**Task 3.3.1: Create docs/USAGE_MORPHOSYNTAX.md**
- Before/after examples
- MSA type checking
- Filtering patterns

**Task 3.3.2: Update README**
- Add MSA section
- Link to docs

---

#### Sprint 3.4: Testing (4 hours)

**Task 3.4.1: Comprehensive MSA tests**
- All types covered
- All operations tested
- Real data testing

**Review Checklist:**
- [ ] All tests pass
- [ ] Performance good
- [ ] No regressions

---

### Phase 4: Phonological Contexts (Week 4) - 12 hours

#### Sprint 4.1: Wrapper & Collection (4 hours)

**Task 4.1.1: Create phonological_context.py**
- Wrapper for IPhPhonContext types

**Task 4.1.2: Create context_collection.py**
- Collection with filtering

**Task 4.1.3: Tests for context wrappers**

**Review Checklist:**
- [ ] All context types handled
- [ ] Properties accessible

---

#### Sprint 4.2: Operations Integration (3 hours)

**Task 4.2.1: Update EnvironmentOperations**
- Return wrapped contexts

**Task 4.2.2: Update PhonologicalRuleOperations**
- input_contexts returns wrapped contexts

**Task 4.2.3: Tests**

---

#### Sprint 4.3: Documentation & Testing (5 hours)

**Task 4.3.1: Create docs/USAGE_CONTEXTS.md**

**Task 4.3.2: Comprehensive testing**

**Task 4.3.3: Update README**

**Review Checklist:**
- [ ] All context operations work
- [ ] Tests comprehensive
- [ ] Documentation complete

---

### Phase 5: Quality & Release (Week 5) - 12 hours

#### Sprint 5.1: Comprehensive Testing (4 hours)

**Task 5.1.1: Run full test suite**
```bash
pytest tests/ -v
pytest tests/operations/ -v
pytest tests/integration/ -v
```

**Task 5.1.2: Performance profiling**
- Wrapper object overhead
- Collection overhead
- Document findings

**Task 5.1.3: Edge case testing**
- Empty collections
- None values
- Large datasets
- Type mismatches

**Review Checklist:**
- [ ] All tests pass
- [ ] No performance regression
- [ ] Edge cases handled

---

#### Sprint 5.2: Documentation Completion (4 hours)

**Task 5.2.1: Create MIGRATION.md**
- Complete migration guide
- Old vs new for all three types
- Backward compatibility note

**Task 5.2.2: Update API documentation**
- Docstring examples
- Type hints
- Usage patterns

**Task 5.2.3: Create CHANGELOG entry**
- New features
- Improvements
- Bug fixes (if any)

---

#### Sprint 5.3: Final Release (4 hours)

**Task 5.3.1: Version bump**
- Update version to 2.2.0
- Update setup.py
- Update requirements if needed

**Task 5.3.2: Final checks**
- All tests pass
- Documentation complete
- Examples working
- No regressions

**Task 5.3.3: Release**
- Tag v2.2.0
- Push to PyPI
- Create GitHub release
- Announce on appropriate channels

**Review Checklist:**
- [ ] Version bumped
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Package ready for PyPI

---

## Team Assignments

### Phase 1: Foundation
**Lead:** [Senior Developer]
- 1.1: Base classes (4 hours)
- 1.2: Testing (3 hours)
- 1.3: Documentation (2 hours)
- **Total:** 9 hours + 3 hours review

### Phase 2: Phonological Rules (Reference Implementation)
**Lead:** [Developer A]
- 2.1: Wrappers & collections (5 hours)
- 2.2: Operations integration (4 hours)
- 2.3: Documentation (3 hours)
- 2.4: Integration testing (4 hours)
- **Total:** 16 hours

### Phase 3: Morphosyntactic Analyses
**Lead:** [Developer B] (use Phase 2 as template)
- 3.1: Wrappers & collections (5 hours)
- 3.2: Operations integration (4 hours)
- 3.3: Documentation (3 hours)
- 3.4: Testing (4 hours)
- **Total:** 16 hours

### Phase 4: Contexts
**Lead:** [Developer C] (use Phase 2 as template)
- 4.1: Wrappers & collections (4 hours)
- 4.2: Operations integration (3 hours)
- 4.3: Documentation & testing (5 hours)
- **Total:** 12 hours

### Phase 5: Quality & Release
**Lead:** [Senior Developer]
- 5.1: Testing (4 hours)
- 5.2: Documentation (4 hours)
- 5.3: Release (4 hours)
- **Total:** 12 hours + coordination

---

## Dependency Chain

```
Phase 1: Foundation (must complete first)
    ↓
Phase 2: Phonological Rules (reference implementation)
    ↓
Phase 3: MSAs (use Phase 2 as template)
    ↓
Phase 4: Contexts (use Phase 2 as template)
    ↓
Phase 5: Quality & Release (start after Phase 4 halfway)
```

Parallel work possible:
- Phase 3 can start once Phase 2 is in code review
- Phase 4 can start once Phase 3 is in code review
- Phase 5 testing can start once Phase 4 starts

---

## Definition of Done (Per Sprint)

✅ Code written
✅ Tests written and passing
✅ Code reviewed
✅ Documentation updated
✅ No regressions in existing tests
✅ Performance acceptable
✅ Ready to merge to master

---

## Success Criteria (v2.2 Release)

✅ All three types (rules, MSAs, contexts) have wrappers & collections
✅ All existing code continues to work unchanged
✅ New usage patterns simpler and more intuitive
✅ Full test coverage for new code
✅ Complete documentation for users
✅ Migration guide for existing users
✅ No breaking changes
✅ Released to PyPI
✅ Users can access simpler API without changing existing code

---

## Rollback Plan

If any phase fails:
1. Remove wrapper/collection files from that phase
2. Revert Operations classes to use raw objects
3. Keep casting/clone/merge improvements (already in codebase)
4. Re-plan failed phase for next version

Low risk - changes are additive and can be removed cleanly.

---

## Known Risks & Mitigations

**Risk 1: Wrapper performance overhead**
- Mitigation: Profile Phase 2, optimize if needed
- Fallback: Expose `_obj` for power users

**Risk 2: Breaking existing code**
- Mitigation: Keep both wrapper and raw object accessible
- Fallback: Add compatibility layer if needed

**Risk 3: Testing coverage gaps**
- Mitigation: Comprehensive integration tests in Phase 2
- Fallback: Additional testing in Phase 5

**Risk 4: Documentation incomplete**
- Mitigation: Assign dedicated person to documentation
- Fallback: Delay release until complete

---

## Timeline Summary

| Phase | Sprint | Duration | Key Deliverable | Status |
|-------|--------|----------|---|---|
| 1 | 1.1-1.3 | 1 week | Base classes, tests, docs | Ready to start |
| 2 | 2.1-2.4 | 1 week | Reference impl (PhonRules) | After Phase 1 |
| 3 | 3.1-3.4 | 1 week | MSAs (parallel with 2.4) | After Phase 2 |
| 4 | 4.1-4.3 | 1 week | Contexts (parallel with 3.4) | After Phase 3 |
| 5 | 5.1-5.3 | 1 week | Quality & Release | After Phase 4 |
| **Total** | **15 sprints** | **~4-5 weeks** | **v2.2 released** | **On schedule** |

---

## What v2.2 Does NOT Do

❌ Break existing code
❌ Require schema changes
❌ Change FLEx data model
❌ Require user migration
❌ Change fundamental architecture
❌ Remove existing APIs

## What v2.2 DOES Do

✅ Simplify property access for common cases
✅ Provide unified filtering across type hierarchies
✅ Show type diversity transparently
✅ Provide better error messages
✅ Add convenient shortcut methods
✅ Enable more Pythonic usage patterns

