# Action Items: BaseOperations Implementation

**QA Review Date**: 2025-12-04
**Status**: WORK REQUIRED BEFORE MERGE

---

## 🔴 CRITICAL: Programmer 2 - Complete Integration

**Assignee**: Programmer 2 (Integration Specialist)
**Priority**: CRITICAL
**Estimated Time**: 6 hours
**Status**: 25 of 43 files remaining

### Task List

#### Lists Module (6 files) - 1.5 hours

Update these files in `flexlibs/code/Lists/`:

- [ ] `AgentOperations.py`
- [ ] `ConfidenceOperations.py`
- [ ] `OverlayOperations.py`
- [ ] `PossibilityListOperations.py`
- [ ] `PublicationOperations.py`
- [ ] `TranslationTypeOperations.py`

#### Notebook Module (5 files) - 1.5 hours

Update these files in `flexlibs/code/Notebook/`:

- [ ] `AnthropologyOperations.py`
- [ ] `DataNotebookOperations.py`
- [ ] `LocationOperations.py`
- [ ] `NoteOperations.py`
- [ ] `PersonOperations.py`

#### System Module (5 files) - 1.5 hours

Update these files in `flexlibs/code/System/`:

- [ ] `AnnotationDefOperations.py`
- [ ] `CheckOperations.py`
- [ ] `CustomFieldOperations.py`
- [ ] `ProjectSettingsOperations.py`
- [ ] `WritingSystemOperations.py`

#### TextsWords Module (9 files) - 2 hours

Update these files in `flexlibs/code/TextsWords/`:

- [ ] `DiscourseOperations.py`
- [ ] `MediaOperations.py`
- [ ] `ParagraphOperations.py`
- [ ] `SegmentOperations.py`
- [ ] `TextOperations.py`
- [ ] `WfiAnalysisOperations.py`
- [ ] `WfiGlossOperations.py`
- [ ] `WfiMorphBundleOperations.py`
- [ ] `WordformOperations.py`

### Integration Pattern

For EACH file above, make these changes:

#### Step 1: Add Import (at top of file)
```python
# Add this import near the top:
from ..BaseOperations import BaseOperations
```

#### Step 2: Update Class Declaration
```python
# Change from:
class XxxOperations:

# To:
class XxxOperations(BaseOperations):
```

#### Step 3: Update __init__ Method
```python
def __init__(self, project):
    """
    Initialize XxxOperations with a FLExProject instance.

    Args:
        project: The FLExProject instance to operate on.
    """
    super().__init__(project)  # ← ADD THIS LINE
    # ... rest of existing code
```

#### Step 4: Add _GetSequence Method
```python
def _GetSequence(self, parent):
    """
    Specify which sequence to reorder for xxx.
    For Xxx, we reorder parent.XxxOS
    """
    return parent.XxxOS  # ← Determine correct OS property
```

### Finding the Correct OS Property

Use this reference (see Appendix A in Project Plan for full list):

**Lists/Notebook/System** (most use):
```python
return parent.PossibilitiesOS
```

**TextsWords**:
```python
# ParagraphOperations
return parent.ParagraphsOS

# SegmentOperations
return parent.SegmentsOS

# WfiAnalysisOperations
return parent.AnalysesOC

# WfiGlossOperations
return parent.MeaningsOC

# WfiMorphBundleOperations
return parent.MorphBundlesOS
```

### Verification Script

After updating each module, run:

```bash
# Check integration count
grep -c "class.*Operations(BaseOperations)" flexlibs/code/Lists/*.py
grep -c "class.*Operations(BaseOperations)" flexlibs/code/Notebook/*.py
grep -c "class.*Operations(BaseOperations)" flexlibs/code/System/*.py
grep -c "class.*Operations(BaseOperations)" flexlibs/code/TextsWords/*.py

# Should see matching counts:
# Lists: 6
# Notebook: 5
# System: 5
# TextsWords: 9
```

### Final Verification

- [ ] All 43 files inherit from BaseOperations
- [ ] Run: `grep -r "class.*Operations(BaseOperations)" flexlibs/code/ | wc -l` → should be 43
- [ ] Test imports work: `python -c "from flexlibs.code.Lists.AgentOperations import AgentOperations"`
- [ ] Commit changes with message: "Complete BaseOperations integration for remaining 25 classes"

---

## 🔴 CRITICAL: Programmer 3 - Fix and Run Tests

**Assignee**: Programmer 3 (Test Engineer)
**Priority**: CRITICAL
**Estimated Time**: 1 hour
**Status**: Tests blocked by import error

### Task 1: Fix Import Error (15 minutes)

#### Option A: Fix Test Import (Recommended)

Edit `flexlibs/sync/tests/test_base_operations.py`, line 23:

```python
# Change from:
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

# To:
from flexlibs.code.FLExProject import FLExProject, FLExInitialize, FLExCleanup
```

#### Option B: Fix Package __init__.py

If Option A doesn't work, edit `flexlibs/__init__.py`:

```python
# Add these exports:
from flexlibs.code.FLExProject import FLExProject, FLExInitialize, FLExCleanup

__all__ = ['FLExProject', 'FLExInitialize', 'FLExCleanup']
```

#### Verify Fix

```bash
# Test import works
python -c "from flexlibs.code.FLExProject import FLExProject, FLExInitialize, FLExCleanup"
# Should complete without error
```

### Task 2: Run Test Suite (30 minutes)

```bash
# Run all tests
cd D:\Github\flexlibs
python -m pytest flexlibs/sync/tests/test_base_operations.py -v

# Expected: 43 tests
# Target: All PASS
```

### Task 3: Generate Coverage Report (15 minutes)

```bash
# Run with coverage
pytest flexlibs/sync/tests/test_base_operations.py --cov=flexlibs.code.BaseOperations --cov-report=html

# Target: >90% coverage
# Report will be in htmlcov/index.html
```

### Task 4: Document Results

Create file: `TEST_RESULTS_BASEOPERATIONS.md`

Include:
- Total tests run: X
- Tests passed: X
- Tests failed: X (list which ones)
- Code coverage: X%
- Any issues found

### If Tests Fail

1. Analyze failure message
2. Check if issue in test or in BaseOperations.py
3. If in BaseOperations.py, report to Programmer 1
4. If in test, fix test
5. Re-run until all pass

---

## 🟡 OPTIONAL: Programmer 1 - Enhancements

**Assignee**: Programmer 1 (Core Developer)
**Priority**: LOW (can defer to later)
**Estimated Time**: 2 hours
**Status**: Enhancement requests

### Enhancement 1: Add Type Hints (1 hour)

Add type hints to `BaseOperations.py`:

```python
from typing import Optional, Callable, Union, Any

def Sort(self,
         parent_or_hvo: Union[object, int],
         key_func: Optional[Callable[[Any], Any]] = None,
         reverse: bool = False) -> int:
    """..."""

def MoveUp(self,
           parent_or_hvo: Union[object, int],
           item: Any,
           positions: int = 1) -> int:
    """..."""

# Add to all 10 methods
```

Verify with:
```bash
mypy flexlibs/code/BaseOperations.py
```

### Enhancement 2: Add Logging (30 minutes)

Add debug logging to key operations:

```python
def Sort(self, parent_or_hvo, key_func=None, reverse=False):
    """..."""
    parent = self._GetObject(parent_or_hvo)
    sequence = self._GetSequence(parent)
    items = list(sequence)

    logger.debug(f"Sorting {len(items)} items, reverse={reverse}, key_func={'provided' if key_func else 'None'}")

    # ... rest of method

    logger.debug(f"Sort complete: {len(items)} items reordered")
    return len(items)
```

Add logging to:
- [ ] Sort
- [ ] MoveUp
- [ ] MoveDown
- [ ] MoveToIndex
- [ ] MoveBefore
- [ ] MoveAfter
- [ ] Swap

### Enhancement 3: Performance Testing (30 minutes)

Create `flexlibs/sync/tests/test_baseops_performance.py`:

```python
import unittest
from flexlibs.code.FLExProject import FLExProject
from flexlibs.code.Lexicon.LexSenseOperations import LexSenseOperations

class TestBaseOperationsPerformance(unittest.TestCase):
    def test_sort_large_sequence(self):
        """Test Sort performance with 1000+ items"""
        # Create 1000 senses
        # Time the sort operation
        # Assert completes in <1 second

    def test_moveup_large_distance(self):
        """Test MoveUp from index 999 to 0"""
        # Test worst-case movement
        # Assert completes in <0.1 second
```

Run and document results.

---

## 🟢 QA Agent - Follow-up Review

**Assignee**: QA Agent
**Priority**: MEDIUM
**Estimated Time**: 30 minutes
**Status**: Pending completion of above tasks

### Re-Review Checklist

After Programmer 2 and 3 complete their tasks:

- [ ] Verify all 43 classes inherit from BaseOperations
- [ ] Verify all tests pass
- [ ] Verify test coverage >90%
- [ ] Spot-check 5 random integration files
- [ ] Run smoke test on actual FLEx project
- [ ] Update QA_REPORT with final approval
- [ ] Create approval summary
- [ ] Notify Project Manager

### Verification Commands

```bash
# Count integrations
grep -r "class.*Operations(BaseOperations)" flexlibs/code/ | wc -l
# Expected: 43

# Run tests
pytest flexlibs/sync/tests/test_base_operations.py -v
# Expected: 43 passed

# Check coverage
pytest flexlibs/sync/tests/test_base_operations.py --cov=flexlibs.code.BaseOperations
# Expected: >90%
```

### Final Approval Criteria

✅ All checks pass → Update status to **APPROVED**
❌ Any check fails → Send back for fixes

---

## Timeline

**Current**: Day 1, 4:00 PM - QA Review Complete
**+6 hours**: Programmer 2 completes integration (Day 1, 10:00 PM)
**+1 hour**: Programmer 3 fixes tests and reports (Day 1, 11:00 PM)
**+30 min**: QA re-review and final approval (Day 1, 11:30 PM)

**Target Completion**: End of Day 1

---

## Questions or Issues?

**Programmer 2**: If you can't determine correct OS property for a class:
1. Check FLEx schema documentation
2. Look at similar classes for patterns
3. Test with actual FLEx project
4. Document uncertainty in code comment
5. Report to Project Manager

**Programmer 3**: If tests reveal bugs in BaseOperations.py:
1. Document the bug clearly
2. Create minimal reproduction case
3. Report to Programmer 1
4. Don't modify BaseOperations.py yourself

**Programmer 1**: Available for questions from Programmers 2 and 3

---

## Communication

**Status Updates**: Post in project channel every 2 hours
**Blockers**: Report immediately to Project Manager
**Completion**: Notify QA Agent when tasks complete

---

## Success Criteria

Project ready for merge when:
- ✅ All 43 files integrated
- ✅ All 43 tests pass
- ✅ Coverage >90%
- ✅ No regressions
- ✅ QA approval obtained

---

**Created by**: QA Agent
**Date**: 2025-12-04
**Status**: ACTIVE WORK ITEMS
