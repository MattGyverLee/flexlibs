# BaseOperations Implementation - Project Plan

**Project Manager**: Claude Code
**Date**: 2025-12-04
**Estimated Duration**: 4-6 hours
**Priority**: HIGH

---

## Executive Summary

Implement a `BaseOperations` parent class containing 7 reordering methods that will be inherited by all 43 operation classes. This eliminates code duplication and provides consistent reordering functionality across the entire flexlibs API.

---

## Project Scope

### Deliverables
1. ✅ New `BaseOperations.py` class with 7 reordering methods
2. ✅ Update 43 operation classes to inherit from BaseOperations
3. ✅ Comprehensive test suite for reordering functionality
4. ✅ Documentation updates

### Out of Scope
- Implementing operation-specific methods (those remain in subclasses)
- UI implementation (API only)
- Performance optimization (future enhancement)

---

## Team Assignment

### Programmer 1 - "Core Developer"
**Responsibility**: BaseOperations class implementation
- Create `flexlibs/code/BaseOperations.py`
- Implement 7 reordering methods
- Implement helper methods
- Write comprehensive docstrings

**Files to Create/Modify**: 1 file
**Estimated Time**: 2 hours

---

### Programmer 2 - "Integration Specialist"
**Responsibility**: Update operation classes to inherit BaseOperations
- Update all 43 operation classes in:
  - Lexicon/ (10 classes)
  - Grammar/ (8 classes)
  - Lists/ (6 classes)
  - Notebook/ (5 classes)
  - System/ (5 classes)
  - TextsWords/ (9 classes)
- Add `_GetSequence()` override to each
- Ensure import statements correct

**Files to Modify**: 43 files
**Estimated Time**: 2-3 hours

---

### Programmer 3 - "Test Engineer"
**Responsibility**: Create comprehensive test suite
- Create `flexlibs/sync/tests/test_base_operations.py`
- Test all 7 reordering methods
- Test edge cases (empty sequences, single item, boundaries)
- Test inheritance works correctly
- Integration tests with real FLEx objects

**Files to Create**: 1 test file
**Estimated Time**: 2 hours

---

### QA Agent - "Quality Assurance"
**Responsibility**: Review all implementations
- Code review of BaseOperations
- Verify all 43 classes updated correctly
- Review test coverage
- Check documentation completeness
- Report issues back to programmers

**Estimated Time**: 1 hour

---

## Detailed Task Breakdown

### PHASE 1: Core Implementation (Programmer 1)

#### Task 1.1: Create BaseOperations.py Structure
```python
# File: flexlibs/code/BaseOperations.py

class BaseOperations:
    """
    Base class for all FLEx operation classes.
    Provides reordering functionality for owning sequences.
    """

    def __init__(self, project):
        self.project = project
```

**Acceptance Criteria**:
- File created at correct location
- Basic class structure in place
- __init__ method accepts project parameter

---

#### Task 1.2: Implement Sort Method
```python
def Sort(self, parent_or_hvo, key_func=None, reverse=False):
    """
    Sort items in owning sequence using custom key function.

    Args:
        parent_or_hvo: Parent object or HVO containing sequence
        key_func: Optional function(item) -> comparable_value
        reverse: If True, sort descending

    Returns:
        int: Number of items sorted
    """
```

**Acceptance Criteria**:
- Method signature matches specification
- Handles None key_func (natural sort)
- Supports reverse parameter
- Uses safe Clear/Add pattern
- Returns count of items
- Complete docstring with examples

---

#### Task 1.3: Implement MoveUp Method
```python
def MoveUp(self, parent_or_hvo, item, positions=1):
    """
    Move item up (toward index 0) by specified positions.
    Auto-clamps at boundary.
    """
```

**Acceptance Criteria**:
- Accepts positions parameter (default=1)
- Clamps at index 0 (doesn't error)
- Returns actual positions moved
- Handles edge cases (already at 0, positions > current index)

---

#### Task 1.4: Implement MoveDown Method
```python
def MoveDown(self, parent_or_hvo, item, positions=1):
    """
    Move item down (toward end) by specified positions.
    Auto-clamps at boundary.
    """
```

**Acceptance Criteria**:
- Accepts positions parameter (default=1)
- Clamps at last index (doesn't error)
- Returns actual positions moved
- Handles edge cases (already at end, positions > remaining)

---

#### Task 1.5: Implement MoveToIndex Method
```python
def MoveToIndex(self, parent_or_hvo, item, new_index):
    """
    Move item to specific index position.
    """
```

**Acceptance Criteria**:
- Validates index in range
- Raises IndexError if out of bounds
- Returns True on success
- Handles moving forward and backward

---

#### Task 1.6: Implement MoveBefore Method
```python
def MoveBefore(self, item_to_move, target_item):
    """
    Move item to position immediately before target.
    """
```

**Acceptance Criteria**:
- Finds common sequence automatically
- Positions item correctly before target
- Raises ValueError if items not in same sequence
- Returns True on success

---

#### Task 1.7: Implement MoveAfter Method
```python
def MoveAfter(self, item_to_move, target_item):
    """
    Move item to position immediately after target.
    """
```

**Acceptance Criteria**:
- Finds common sequence automatically
- Positions item correctly after target
- Raises ValueError if items not in same sequence
- Returns True on success

---

#### Task 1.8: Implement Swap Method
```python
def Swap(self, item1, item2):
    """
    Swap positions of two items in sequence.
    """
```

**Acceptance Criteria**:
- Finds common sequence automatically
- Correctly exchanges positions
- Raises ValueError if items not in same sequence
- Returns True on success

---

#### Task 1.9: Implement Helper Methods
```python
def _GetSequence(self, parent):
    """OVERRIDE in subclasses to specify which OS property."""
    raise NotImplementedError()

def _GetObject(self, obj_or_hvo):
    """Convert HVO to object if needed."""
    pass

def _FindCommonSequence(self, item1, item2):
    """Find sequence containing both items."""
    pass
```

**Acceptance Criteria**:
- _GetSequence raises NotImplementedError with clear message
- _GetObject handles both objects and HVOs
- _FindCommonSequence works with FLEx Owner property
- All helpers have docstrings

---

### PHASE 2: Integration (Programmer 2)

#### Task 2.1: Update Lexicon Classes (10 files)

Files to update:
1. `LexEntryOperations.py`
2. `LexSenseOperations.py`
3. `AllomorphOperations.py`
4. `ExampleOperations.py`
5. `PronunciationOperations.py`
6. `EtymologyOperations.py`
7. `VariantOperations.py`
8. `LexReferenceOperations.py`
9. `ReversalOperations.py`
10. `SemanticDomainOperations.py`

**Changes per file**:
```python
# Add import at top
from ..BaseOperations import BaseOperations

# Change class declaration
class LexSenseOperations(BaseOperations):  # Add parent

    def __init__(self, project):
        super().__init__(project)  # Add super call

    def _GetSequence(self, parent):
        """Specify which sequence to reorder."""
        return parent.SensesOS  # Specific to each class
```

**Acceptance Criteria**:
- All 10 classes inherit from BaseOperations
- All have super().__init__() in constructor
- All override _GetSequence() with correct property
- All existing methods unchanged
- All imports correct

---

#### Task 2.2: Update Grammar Classes (8 files)

Files to update:
1. `POSOperations.py` → `_GetSequence`: return parent.SubPossibilitiesOS
2. `PhonemeOperations.py` → `_GetSequence`: return parent.PhonemesOS
3. `NaturalClassOperations.py` → `_GetSequence`: return parent.SubPossibilitiesOS
4. `EnvironmentOperations.py` → `_GetSequence`: return parent.EnvironmentsOA.PossibilitiesOS
5. `MorphRuleOperations.py` → `_GetSequence`: return parent.RulesOS
6. `PhonologicalRuleOperations.py` → `_GetSequence`: return parent.PhonRulesOS
7. `GramCatOperations.py` → `_GetSequence`: return parent.SubPossibilitiesOS
8. `InflectionFeatureOperations.py` → `_GetSequence`: return parent.FeaturesOA.PossibilitiesOS

**Acceptance Criteria**: Same as Task 2.1

---

#### Task 2.3: Update Lists Classes (6 files)

Files to update:
1. `PossibilityListOperations.py`
2. `PublicationOperations.py`
3. `AgentOperations.py`
4. `ConfidenceOperations.py`
5. `OverlayOperations.py`
6. `TranslationTypeOperations.py`

**Acceptance Criteria**: Same as Task 2.1

---

#### Task 2.4: Update Notebook Classes (5 files)

Files to update:
1. `NoteOperations.py` → `_GetSequence`: return parent.NotesOS
2. `PersonOperations.py` → `_GetSequence`: return parent.PeopleOA.PossibilitiesOS
3. `LocationOperations.py` → `_GetSequence`: return parent.LocationsOA.PossibilitiesOS
4. `AnthropologyOperations.py` → `_GetSequence`: return parent.AnthroListOA.PossibilitiesOS
5. `DataNotebookOperations.py` → `_GetSequence`: return parent.RecordsOA.PossibilitiesOS

**Acceptance Criteria**: Same as Task 2.1

---

#### Task 2.5: Update System Classes (5 files)

Files to update:
1. `CustomFieldOperations.py`
2. `WritingSystemOperations.py`
3. `ProjectSettingsOperations.py`
4. `AnnotationDefOperations.py`
5. `CheckOperations.py`

**Acceptance Criteria**: Same as Task 2.1

---

#### Task 2.6: Update TextsWords Classes (9 files)

Files to update:
1. `TextOperations.py`
2. `ParagraphOperations.py` → `_GetSequence`: return parent.ParagraphsOS
3. `SegmentOperations.py` → `_GetSequence`: return parent.SegmentsOS
4. `WordformOperations.py`
5. `WfiAnalysisOperations.py` → `_GetSequence`: return parent.AnalysesOC
6. `WfiGlossOperations.py` → `_GetSequence`: return parent.MeaningsOC
7. `WfiMorphBundleOperations.py` → `_GetSequence`: return parent.MorphBundlesOS
8. `MediaOperations.py`
9. `DiscourseOperations.py`

**Acceptance Criteria**: Same as Task 2.1

---

### PHASE 3: Testing (Programmer 3)

#### Task 3.1: Setup Test Infrastructure
```python
# File: flexlibs/sync/tests/test_base_operations.py

import unittest
from unittest.mock import Mock, MagicMock
from flexlibs2 import FLExProject, FLExInitialize, FLExCleanup

class TestBaseOperations(unittest.TestCase):
    """Test suite for BaseOperations reordering methods."""

    @classmethod
    def setUpClass(cls):
        FLExInitialize()
        cls.project = FLExProject()
        cls.project.OpenProject("Sena 3", writeEnabled=True)
```

**Acceptance Criteria**:
- Test file created
- Proper imports
- Setup/teardown methods
- Test project connection works

---

#### Task 3.2: Test Sort Method
```python
def test_sort_alphabetically(self):
    """Test sorting senses alphabetically by gloss."""

def test_sort_reverse(self):
    """Test reverse sorting."""

def test_sort_with_key_func(self):
    """Test custom key function."""

def test_sort_empty_sequence(self):
    """Test sorting empty sequence."""
```

**Acceptance Criteria**:
- 4+ test cases for Sort
- Tests natural sort, custom key, reverse
- Tests edge cases (empty, single item)
- All tests pass

---

#### Task 3.3: Test MoveUp Method
```python
def test_move_up_single_position(self):
    """Test moving item up one position."""

def test_move_up_multiple_positions(self):
    """Test moving item up 3 positions."""

def test_move_up_clamps_at_zero(self):
    """Test moving past start clamps at index 0."""

def test_move_up_already_at_start(self):
    """Test moving when already at index 0 returns 0."""

def test_move_up_returns_actual_moved(self):
    """Test return value shows actual positions moved."""
```

**Acceptance Criteria**:
- 5+ test cases for MoveUp
- Tests clamping behavior
- Tests return values
- All tests pass

---

#### Task 3.4: Test MoveDown Method
```python
def test_move_down_single_position(self):
    """Test moving item down one position."""

def test_move_down_multiple_positions(self):
    """Test moving item down 3 positions."""

def test_move_down_clamps_at_end(self):
    """Test moving past end clamps at last index."""

def test_move_down_already_at_end(self):
    """Test moving when already at end returns 0."""
```

**Acceptance Criteria**:
- 4+ test cases for MoveDown
- Tests clamping behavior
- Tests return values
- All tests pass

---

#### Task 3.5: Test MoveToIndex Method
```python
def test_move_to_index_forward(self):
    """Test moving item forward to specific index."""

def test_move_to_index_backward(self):
    """Test moving item backward to specific index."""

def test_move_to_index_out_of_range(self):
    """Test IndexError raised for invalid index."""
```

**Acceptance Criteria**:
- 3+ test cases for MoveToIndex
- Tests both directions
- Tests error handling
- All tests pass

---

#### Task 3.6: Test MoveBefore/MoveAfter Methods
```python
def test_move_before(self):
    """Test moving item before another."""

def test_move_after(self):
    """Test moving item after another."""

def test_move_before_different_sequences_fails(self):
    """Test error when items in different sequences."""
```

**Acceptance Criteria**:
- 3+ test cases for MoveBefore/After
- Tests error handling
- All tests pass

---

#### Task 3.7: Test Swap Method
```python
def test_swap_two_items(self):
    """Test swapping two items."""

def test_swap_preserves_other_items(self):
    """Test swap doesn't affect other items."""
```

**Acceptance Criteria**:
- 2+ test cases for Swap
- All tests pass

---

#### Task 3.8: Test Data Preservation
```python
def test_reordering_preserves_properties(self):
    """Test that reordering doesn't change object properties."""

def test_reordering_preserves_references(self):
    """Test that reordering doesn't break references."""

def test_reordering_preserves_children(self):
    """Test that reordering doesn't affect owned children."""
```

**Acceptance Criteria**:
- 3+ tests verifying data preservation
- Tests GUIDs unchanged
- Tests properties intact
- All tests pass

---

#### Task 3.9: Integration Tests
```python
def test_multiple_operation_classes(self):
    """Test reordering works for Senses, Allomorphs, Examples."""

def test_inherited_methods_available(self):
    """Test all 43 classes have reordering methods."""
```

**Acceptance Criteria**:
- Tests multiple operation classes
- Verifies inheritance working
- All tests pass

---

### PHASE 4: QA Review (QA Agent)

#### Task 4.1: Code Review - BaseOperations.py

**Review Checklist**:
- [ ] All 7 methods implemented correctly
- [ ] Clear docstrings with examples
- [ ] Error handling appropriate
- [ ] Helper methods implemented
- [ ] Code follows Python best practices
- [ ] Type hints if applicable
- [ ] No hardcoded values
- [ ] Logging where appropriate

**Deliverable**: Code review report with issues/suggestions

---

#### Task 4.2: Code Review - Integration (43 files)

**Review Checklist** (per file):
- [ ] Imports BaseOperations correctly
- [ ] Calls super().__init__()
- [ ] Overrides _GetSequence() with correct property
- [ ] No duplicate code
- [ ] Existing functionality unchanged
- [ ] No syntax errors

**Deliverable**: Integration review report

---

#### Task 4.3: Test Coverage Review

**Review Checklist**:
- [ ] All 7 methods have tests
- [ ] Edge cases covered
- [ ] Error cases tested
- [ ] Integration tests present
- [ ] Test coverage > 90%
- [ ] All tests pass
- [ ] Test names descriptive
- [ ] Assertions meaningful

**Deliverable**: Test coverage report

---

#### Task 4.4: Documentation Review

**Review Checklist**:
- [ ] BaseOperations.py has class docstring
- [ ] All methods have complete docstrings
- [ ] Examples provided in docstrings
- [ ] REORDERING_API_DESIGN.md updated
- [ ] REORDERING_INHERITANCE_DESIGN.md accurate
- [ ] User guide mentions inheritance

**Deliverable**: Documentation review report

---

### PHASE 5: Bug Fixes (Programmers 1, 2, 3)

#### Task 5.1: Address QA Findings

**Responsibility**: All programmers
- Review QA reports
- Fix identified issues
- Re-run tests
- Update documentation if needed

**Acceptance Criteria**:
- All QA issues resolved
- Tests still pass
- Code review approved

---

### PHASE 6: Project Manager Sign-off

#### Task 6.1: Final Review

**Checklist**:
- [ ] All 43 classes inherit from BaseOperations
- [ ] All 7 reordering methods working
- [ ] Test suite passes (>90% coverage)
- [ ] Documentation complete
- [ ] QA approved
- [ ] No breaking changes to existing API
- [ ] Performance acceptable

#### Task 6.2: Deployment Preparation

**Checklist**:
- [ ] All changes committed to git
- [ ] Branch merged to main
- [ ] Version number updated
- [ ] Changelog updated
- [ ] Release notes prepared

---

## Risk Assessment

### High Risk
❌ None identified

### Medium Risk
⚠️ **Breaking existing code if super().__init__() missed**
- Mitigation: Programmer 2 creates checklist, QA verifies all files
- Mitigation: Run existing test suite to ensure no regressions

⚠️ **Incorrect _GetSequence() implementation**
- Mitigation: Integration tests verify correct sequences
- Mitigation: Test with actual FLEx project

### Low Risk
⚠️ **Test environment availability**
- Mitigation: Use "Sena 3" test project
- Mitigation: Mock tests if project unavailable

---

## Success Metrics

1. **Code Quality**
   - ✅ 0 syntax errors
   - ✅ All tests pass
   - ✅ Test coverage > 90%

2. **Functionality**
   - ✅ All 7 methods work correctly
   - ✅ All 43 classes have methods available
   - ✅ No data corruption

3. **Maintainability**
   - ✅ Single source of truth (BaseOperations)
   - ✅ Clear inheritance pattern
   - ✅ Good documentation

4. **Timeline**
   - ✅ Complete within 6 hours
   - ✅ No delays in QA phase

---

## Timeline

| Phase | Duration | Assignee | Start | End |
|-------|----------|----------|-------|-----|
| Core Implementation | 2h | Programmer 1 | T+0 | T+2h |
| Integration | 3h | Programmer 2 | T+0 | T+3h |
| Testing | 2h | Programmer 3 | T+2h | T+4h |
| QA Review | 1h | QA Agent | T+4h | T+5h |
| Bug Fixes | 1h | All Programmers | T+5h | T+6h |
| PM Sign-off | 0.5h | PM | T+6h | T+6.5h |

**Total**: 6.5 hours

---

## Communication Plan

### Daily Standup
- Time: Every 2 hours
- Format: Status update from each team member
- Duration: 5 minutes

### Issue Escalation
- Blocker issues → Report to PM immediately
- Technical questions → Team discussion
- Design decisions → PM approval required

---

## Deliverables Summary

1. **Code**
   - `flexlibs/code/BaseOperations.py` (new, ~300 lines)
   - 43 operation class files (modified, ~5 lines each)

2. **Tests**
   - `flexlibs/sync/tests/test_base_operations.py` (new, ~600 lines)
   - Expected: 40+ test cases, >90% coverage

3. **Documentation**
   - Updated class docstrings (43 files)
   - Updated design documents (2 files)

---

## Sign-off

**Programmer 1 (Core)**: _______________ Date: _______

**Programmer 2 (Integration)**: _______________ Date: _______

**Programmer 3 (Testing)**: _______________ Date: _______

**QA Agent**: _______________ Date: _______

**Project Manager**: _______________ Date: _______

---

## Appendix A: _GetSequence() Reference

Quick reference for Programmer 2:

| Class | _GetSequence() Return Value |
|-------|----------------------------|
| LexSenseOperations | `parent.SensesOS` |
| AllomorphOperations | `parent.AlternateFormsOS` |
| ExampleOperations | `parent.ExamplesOS` |
| PronunciationOperations | `parent.PronunciationsOS` |
| EtymologyOperations | `parent.EtymologyOS` |
| VariantOperations | `parent.VariantEntryBackRefsOS` |
| ParagraphOperations | `parent.ParagraphsOS` |
| SegmentOperations | `parent.SegmentsOS` |
| ... | (See FLEx schema for others) |

---

**Plan Version**: 1.0
**Status**: READY FOR EXECUTION
**Estimated Completion**: T+6.5 hours
