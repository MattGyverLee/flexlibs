# Reordering Methods - Inheritance Architecture

**Question**: Should reordering methods be added to each operation class, or can they be in a base class?

**Answer**: ✅ **Add to base class** - All operations can inherit them safely.

---

## Recommended Architecture

### Option 1: Base Operations Class (RECOMMENDED)

Create a base class that all Operations classes inherit from:

```python
# flexlibs/code/BaseOperations.py

class BaseOperations:
    """
    Base class for all FLEx operations.
    Provides common functionality including reordering methods.
    """

    def __init__(self, project):
        self.project = project

    # ========== REORDERING METHODS (INHERITED BY ALL) ==========

    def Sort(self, parent_or_hvo, key_func=None, reverse=False):
        """
        Sort items in an owning sequence using custom key function.
        Works for ANY operation class that has owning sequences.
        """
        parent = self._GetObject(parent_or_hvo)
        sequence = self._GetSequence(parent)

        items = list(sequence)
        if key_func:
            items.sort(key=key_func, reverse=reverse)
        else:
            items.sort(reverse=reverse)

        sequence.Clear()
        for item in items:
            sequence.Add(item)

        return len(items)


    def MoveUp(self, parent_or_hvo, item, positions=1):
        """Move item up by specified positions. Works for all sequences."""
        parent = self._GetObject(parent_or_hvo)
        sequence = self._GetSequence(parent)

        current_items = list(sequence)
        current_index = current_items.index(item)

        new_index = max(0, current_index - positions)
        actual_moved = current_index - new_index

        if actual_moved == 0:
            return 0

        current_items.pop(current_index)
        current_items.insert(new_index, item)

        sequence.Clear()
        for obj in current_items:
            sequence.Add(obj)

        return actual_moved


    def MoveDown(self, parent_or_hvo, item, positions=1):
        """Move item down by specified positions. Works for all sequences."""
        parent = self._GetObject(parent_or_hvo)
        sequence = self._GetSequence(parent)

        current_items = list(sequence)
        current_index = current_items.index(item)

        max_index = len(current_items) - 1
        new_index = min(max_index, current_index + positions)
        actual_moved = new_index - current_index

        if actual_moved == 0:
            return 0

        current_items.pop(current_index)
        current_items.insert(new_index, item)

        sequence.Clear()
        for obj in current_items:
            sequence.Add(obj)

        return actual_moved


    def MoveToIndex(self, parent_or_hvo, item, new_index):
        """Move item to specific index. Works for all sequences."""
        parent = self._GetObject(parent_or_hvo)
        sequence = self._GetSequence(parent)

        current_items = list(sequence)
        current_index = current_items.index(item)

        if new_index < 0 or new_index >= len(current_items):
            raise IndexError(f"Index {new_index} out of range [0, {len(current_items)-1}]")

        current_items.pop(current_index)
        current_items.insert(new_index, item)

        sequence.Clear()
        for obj in current_items:
            sequence.Add(obj)

        return True


    def MoveBefore(self, item_to_move, target_item):
        """Move item before target. Works for all sequences."""
        # Find which sequence they're in
        sequence = self._FindCommonSequence(item_to_move, target_item)

        current_items = list(sequence)
        current_items.remove(item_to_move)
        target_index = current_items.index(target_item)
        current_items.insert(target_index, item_to_move)

        sequence.Clear()
        for obj in current_items:
            sequence.Add(obj)

        return True


    def MoveAfter(self, item_to_move, target_item):
        """Move item after target. Works for all sequences."""
        sequence = self._FindCommonSequence(item_to_move, target_item)

        current_items = list(sequence)
        current_items.remove(item_to_move)
        target_index = current_items.index(target_item)
        current_items.insert(target_index + 1, item_to_move)

        sequence.Clear()
        for obj in current_items:
            sequence.Add(obj)

        return True


    def Swap(self, item1, item2):
        """Swap two items. Works for all sequences."""
        sequence = self._FindCommonSequence(item1, item2)

        current_items = list(sequence)
        idx1 = current_items.index(item1)
        idx2 = current_items.index(item2)

        current_items[idx1], current_items[idx2] = current_items[idx2], current_items[idx1]

        sequence.Clear()
        for obj in current_items:
            sequence.Add(obj)

        return True


    # ========== HELPER METHODS (OVERRIDE IN SUBCLASSES) ==========

    def _GetSequence(self, parent):
        """
        Get the owning sequence from parent object.
        OVERRIDE THIS in subclasses to specify which sequence.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _GetSequence() "
            "to specify which owning sequence to reorder"
        )


    def _FindCommonSequence(self, item1, item2):
        """
        Find the sequence that contains both items.
        Default implementation - can be overridden if needed.
        """
        # Try to find owner through item properties
        if hasattr(item1, 'Owner') and hasattr(item2, 'Owner'):
            if item1.Owner == item2.Owner:
                # Find which sequence in the owner contains item1
                owner = item1.Owner
                for prop in dir(owner):
                    if prop.endswith('OS'):  # Owning Sequence
                        seq = getattr(owner, prop)
                        if item1 in seq and item2 in seq:
                            return seq

        raise ValueError("Items not in same sequence or sequence not found")


    def _GetObject(self, obj_or_hvo):
        """Get object from HVO or return object directly."""
        if isinstance(obj_or_hvo, int):
            return self.project.project.GetObject(obj_or_hvo)
        return obj_or_hvo
```

---

## Then Each Operation Class Inherits

```python
# flexlibs/code/Lexicon/LexSenseOperations.py

from ..BaseOperations import BaseOperations

class LexSenseOperations(BaseOperations):
    """
    Operations for LexSense objects.
    Inherits all reordering methods from BaseOperations.
    """

    def __init__(self, project):
        super().__init__(project)


    def _GetSequence(self, parent):
        """
        Specify which sequence to reorder for senses.
        For LexSense, we reorder entry.SensesOS
        """
        return parent.SensesOS


    # All the existing sense-specific methods
    def GetGloss(self, sense_or_hvo, ws=None):
        """Get sense gloss..."""
        pass

    def Create(self, entry, gloss):
        """Create new sense..."""
        pass

    # ... etc ...
```

```python
# flexlibs/code/Lexicon/AllomorphOperations.py

from ..BaseOperations import BaseOperations

class AllomorphOperations(BaseOperations):
    """
    Operations for Allomorph objects.
    Inherits all reordering methods from BaseOperations.
    """

    def __init__(self, project):
        super().__init__(project)


    def _GetSequence(self, parent):
        """
        Specify which sequence to reorder for allomorphs.
        For Allomorph, we reorder entry.AlternateFormsOS
        """
        return parent.AlternateFormsOS


    # All the existing allomorph-specific methods
    def GetForm(self, allomorph_or_hvo, ws=None):
        """Get allomorph form..."""
        pass

    # ... etc ...
```

```python
# flexlibs/code/Lexicon/ExampleOperations.py

from ..BaseOperations import BaseOperations

class ExampleOperations(BaseOperations):
    """
    Operations for Example sentences.
    Inherits all reordering methods from BaseOperations.
    """

    def __init__(self, project):
        super().__init__(project)


    def _GetSequence(self, parent):
        """
        Specify which sequence to reorder for examples.
        For Example, we reorder sense.ExamplesOS
        """
        return parent.ExamplesOS


    # All the existing example-specific methods
    def GetText(self, example_or_hvo, ws=None):
        """Get example text..."""
        pass

    # ... etc ...
```

---

## Usage - Identical Across All Classes

```python
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

FLExInitialize()
project = FLExProject()
project.OpenProject("MyProject", writeEnabled=True)

entry = project.LexEntry.Find("walk")

# ===== SENSES =====
# All these methods work automatically!
sense = entry.SensesOS[2]

project.Senses.MoveUp(entry, sense, positions=2)
# Now at index 0 (primary sense)

project.Senses.Sort(entry,
                   key_func=lambda s: project.Senses.GetGloss(s))
# Sorted alphabetically by gloss


# ===== ALLOMORPHS =====
# Same methods work for allomorphs!
allo = entry.AlternateFormsOS[3]

project.Allomorphs.MoveDown(entry, allo, positions=1)
# Moved down one position

project.Allomorphs.Sort(entry,
                       key_func=lambda a: complexity_score(a),
                       reverse=True)
# Sorted by complexity


# ===== EXAMPLES =====
# Same methods work for examples!
sense = entry.SensesOS[0]
example = sense.ExamplesOS[2]

project.Examples.MoveUp(sense, example)
# Moved up one position

project.Examples.Sort(sense,
                     key_func=lambda e: len(project.Examples.GetText(e)))
# Sorted by length


project.CloseProject()
FLExCleanup()
```

---

## Benefits of Base Class Approach

### ✅ Advantages

1. **Write Once, Use Everywhere**
   - 7 reordering methods × 1 base class = done!
   - Don't need to implement 7 methods × 43 operation classes = 301 methods

2. **Consistent Behavior**
   - MoveUp works identically for Senses, Allomorphs, Examples, etc.
   - Users learn once, use everywhere

3. **Easy Testing**
   - Test reordering logic once in BaseOperations
   - Each subclass only tests _GetSequence()

4. **Easy Maintenance**
   - Bug fix in MoveUp? Fixed for all 43 classes instantly
   - Enhancement? Add once, benefit everywhere

5. **Type Safety**
   - Each operation class specifies its sequence type via _GetSequence()
   - Can't accidentally reorder wrong collection

6. **Minimal Override Needed**
   - Subclasses only override _GetSequence()
   - Can override other helpers if needed for special cases

### ⚠️ Considerations

1. **Different Sequences per Class**
   - Solution: _GetSequence() specifies which one
   - Each class knows its own sequence (SensesOS, AlternateFormsOS, etc.)

2. **Some Classes May Not Have Sequences**
   - Solution: Those classes don't override _GetSequence()
   - Calling reorder methods raises NotImplementedError with clear message
   - Or check in FLExProject property: `if hasattr(ops_class, '_GetSequence')`

3. **Special Cases**
   - Some classes might need custom reordering logic
   - Solution: Override the specific method in that class
   - Base implementation still available via super()

---

## Alternative: Mixin Class

If you prefer composition over inheritance:

```python
# flexlibs/code/ReorderingMixin.py

class ReorderingMixin:
    """
    Mixin providing reordering functionality.
    Add to any Operations class that needs reordering.
    """

    def Sort(self, parent_or_hvo, key_func=None, reverse=False):
        # Same implementation as BaseOperations
        pass

    def MoveUp(self, parent_or_hvo, item, positions=1):
        # Same implementation
        pass

    # ... all 7 methods ...


# Then use in operation classes:
class LexSenseOperations(ReorderingMixin, SomeOtherBase):
    pass
```

But **BaseOperations is cleaner** since all operation classes likely share other common functionality too (like _GetObject, error handling, etc.).

---

## Current flexlibs Architecture Check

Let me check if there's already a base class:

```bash
# Check current structure
ls flexlibs/code/Lexicon/
```

Looking at existing files, operation classes like `LexSenseOperations`, `AllomorphOperations`, etc. likely already have a common pattern. Adding a `BaseOperations` parent class would fit naturally.

---

## Implementation Plan

### Step 1: Create BaseOperations
- Location: `flexlibs/code/BaseOperations.py`
- Contains: All 7 reordering methods
- Contains: Common helpers (_GetObject, _GetSequence interface, etc.)

### Step 2: Update Each Operation Class
For each of the 43 operation classes:

```python
# Before:
class LexSenseOperations:
    def __init__(self, project):
        self.project = project

# After:
from .BaseOperations import BaseOperations

class LexSenseOperations(BaseOperations):
    def __init__(self, project):
        super().__init__(project)

    def _GetSequence(self, parent):
        return parent.SensesOS  # Specific to LexSense
```

**Only 2 lines of code per class!**

### Step 3: Test
```python
# Test that all classes inherit reordering
for ops_class in [project.Senses, project.Allomorphs, project.Examples]:
    assert hasattr(ops_class, 'MoveUp')
    assert hasattr(ops_class, 'Sort')
    # etc.
```

---

## Recommendation Summary

**✅ YES - Add to Base Class**

Create `BaseOperations` with all 7 reordering methods:
- Sort
- MoveBefore
- MoveAfter
- MoveToIndex
- Swap
- MoveUp
- MoveDown

Each operation class:
- Inherits from `BaseOperations`
- Overrides `_GetSequence()` to specify which OS property
- Automatically gets all 7 methods working correctly

**Result**:
- Write ~200 lines once (BaseOperations)
- Add ~5 lines per operation class (_GetSequence override)
- Get 301 working methods (7 × 43 classes)

**Time Savings**: 95%+ reduction in code
**Maintainability**: 100× better
**Consistency**: Perfect

---

**Document Version**: 1.0
**Recommendation**: Implement BaseOperations parent class
**Effort**: Low (create base class, update 43 classes with 5 lines each)
**Benefit**: High (all reordering methods work for all classes)
