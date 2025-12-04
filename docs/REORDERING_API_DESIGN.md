# Reordering API Design for FLEx Collections

**Purpose**: Allow users to reorder items in FLEx Owning Sequences (OS) while preserving all data connections.

**Date**: 2025-12-04

---

## Safety Guarantee

**✅ Reordering OS collections is SAFE and will NOT break data connections.**

FLEx uses GUIDs and object references (not array indices) for relationships. Reordering only changes the sequence position, not the object identity or its connections.

### What Stays Intact After Reordering:
- ✅ Object GUIDs
- ✅ Property values
- ✅ References to other objects
- ✅ Owned children
- ✅ All linguistic data

### What Changes:
- Position in the sequence (index)
- Processing order (e.g., which allomorph is tried first)
- Display order in FLEx UI

---

## Proposed API Methods

### 1. **Sort** - Reorder by user-defined criteria

```python
def Sort(self, parent_or_hvo, key_func=None, reverse=False):
    """
    Sort items in an owning sequence using a custom key function.

    Args:
        parent_or_hvo: The parent object or HVO containing the sequence
        key_func: Optional function(item) -> comparable_value
                  If None, uses natural order
        reverse: If True, sort in descending order

    Returns:
        int: Number of items reordered

    Example:
        # Sort allomorphs by environment complexity (most complex first)
        def complexity_score(allomorph):
            env = project.Allomorphs.GetEnvironment(allomorph)
            if not env:
                return 0
            # Count constraints in environment
            return len(str(env))

        project.Allomorphs.Sort(entry,
                               key_func=complexity_score,
                               reverse=True)

        # Sort senses alphabetically by gloss
        project.Senses.Sort(entry,
                           key_func=lambda s: project.Senses.GetGloss(s))

        # Sort examples by length
        project.Examples.Sort(sense,
                             key_func=lambda ex: len(project.Examples.GetText(ex)))
    """
    pass
```

### 2. **MoveBefore** - Move item before another

```python
def MoveBefore(self, item_to_move, target_item):
    """
    Move an item to position immediately before another item.

    Args:
        item_to_move: The item to reposition
        target_item: The item before which to insert

    Returns:
        bool: True if successful

    Raises:
        ValueError: If items not in same sequence or not found

    Example:
        # Move secondary sense to become primary
        primary_sense = entry.SensesOS[0]
        secondary_sense = entry.SensesOS[2]

        project.Senses.MoveBefore(secondary_sense, primary_sense)
        # Now secondary_sense is at index 0
    """
    pass
```

### 3. **MoveAfter** - Move item after another

```python
def MoveAfter(self, item_to_move, target_item):
    """
    Move an item to position immediately after another item.

    Args:
        item_to_move: The item to reposition
        target_item: The item after which to insert

    Returns:
        bool: True if successful

    Raises:
        ValueError: If items not in same sequence or not found

    Example:
        # Move an allomorph after the default form
        default_form = entry.AlternateFormsOS[0]
        variant_form = entry.AlternateFormsOS[3]

        project.Allomorphs.MoveAfter(variant_form, default_form)
        # Now variant_form is at index 1
    """
    pass
```

### 4. **MoveToIndex** - Move item to specific position

```python
def MoveToIndex(self, parent_or_hvo, item, new_index):
    """
    Move an item to a specific index position.

    Args:
        parent_or_hvo: The parent object containing the sequence
        item: The item to reposition
        new_index: Target index (0-based)

    Returns:
        bool: True if successful

    Raises:
        IndexError: If new_index out of range
        ValueError: If item not found in sequence

    Example:
        # Make third sense the primary sense
        third_sense = entry.SensesOS[2]
        project.Senses.MoveToIndex(entry, third_sense, 0)

        # Move allomorph to end
        allomorph = entry.AlternateFormsOS[1]
        last_index = entry.AlternateFormsOS.Count - 1
        project.Allomorphs.MoveToIndex(entry, allomorph, last_index)
    """
    pass
```

### 5. **Swap** - Swap two items

```python
def Swap(self, item1, item2):
    """
    Swap the positions of two items in a sequence.

    Args:
        item1: First item
        item2: Second item

    Returns:
        bool: True if successful

    Raises:
        ValueError: If items not in same sequence

    Example:
        # Swap first and second senses
        project.Senses.Swap(entry.SensesOS[0], entry.SensesOS[1])

        # Swap allomorphs based on conditions
        if should_swap(allo1, allo2):
            project.Allomorphs.Swap(allo1, allo2)
    """
    pass
```

### 6. **MoveUp** - Move item toward beginning

```python
def MoveUp(self, parent_or_hvo, item, positions=1):
    """
    Move an item up (toward index 0) by specified number of positions.

    Args:
        parent_or_hvo: The parent object containing the sequence
        item: The item to move
        positions: Number of positions to move up (default 1)
                   Must be positive integer

    Returns:
        int: Actual number of positions moved (may be less if hit start)

    Notes:
        - If positions would move past index 0, stops at index 0
        - Returns 0 if already at index 0
        - Returns actual positions moved (may be less than requested)

    Example:
        # Move sense up one position (e.g., from index 3 to 2)
        sense = entry.SensesOS[3]
        moved = project.Senses.MoveUp(entry, sense)
        # moved = 1, sense now at index 2

        # Move allomorph to top (up 5 positions)
        allomorph = entry.AlternateFormsOS[5]
        moved = project.Allomorphs.MoveUp(entry, allomorph, positions=5)
        # moved = 5, allomorph now at index 0

        # Try to move past start (clamped)
        first_example = sense.ExamplesOS[1]
        moved = project.Examples.MoveUp(sense, first_example, positions=10)
        # moved = 1 (only 1 position available), now at index 0

        # Already at start - no effect
        primary_sense = entry.SensesOS[0]
        moved = project.Senses.MoveUp(entry, primary_sense)
        # moved = 0, still at index 0
    """
    pass
```

### 7. **MoveDown** - Move item toward end

```python
def MoveDown(self, parent_or_hvo, item, positions=1):
    """
    Move an item down (toward last index) by specified number of positions.

    Args:
        parent_or_hvo: The parent object containing the sequence
        item: The item to move
        positions: Number of positions to move down (default 1)
                   Must be positive integer

    Returns:
        int: Actual number of positions moved (may be less if hit end)

    Notes:
        - If positions would move past end, stops at last index
        - Returns 0 if already at last index
        - Returns actual positions moved (may be less than requested)

    Example:
        # Move sense down one position (e.g., from index 1 to 2)
        sense = entry.SensesOS[1]
        moved = project.Senses.MoveDown(entry, sense)
        # moved = 1, sense now at index 2

        # Demote primary sense significantly
        primary_sense = entry.SensesOS[0]
        moved = project.Senses.MoveDown(entry, primary_sense, positions=3)
        # moved = 3, sense now at index 3

        # Try to move past end (clamped)
        last_allomorph = entry.AlternateFormsOS[8]  # Count = 10
        moved = project.Allomorphs.MoveDown(entry, last_allomorph, positions=5)
        # moved = 1 (only 1 position available), now at index 9

        # Already at end - no effect
        last_sense = entry.SensesOS[entry.SensesOS.Count - 1]
        moved = project.Senses.MoveDown(entry, last_sense)
        # moved = 0, still at last index

        # Move to end
        first_example = sense.ExamplesOS[0]
        count = sense.ExamplesOS.Count
        moved = project.Examples.MoveDown(sense, first_example, positions=count)
        # moved = count-1, example now at last position
    """
    pass
```

---

## Method Comparison Summary

| Method | Use Case | Example | Returns |
|--------|----------|---------|---------|
| **Sort** | Reorder all items by criteria | Sort allomorphs by complexity | int (count) |
| **MoveBefore** | Insert before specific item | Make sense #3 the primary | bool |
| **MoveAfter** | Insert after specific item | Put variant after default | bool |
| **MoveToIndex** | Move to exact position | Make item #5 become item #0 | bool |
| **Swap** | Exchange two items | Swap positions 1 and 3 | bool |
| **MoveUp** | Promote item (toward start) | Move sense up 2 positions | int (moved) |
| **MoveDown** | Demote item (toward end) | Move allomorph down 1 position | int (moved) |

### When to Use Each Method

**User Interface Scenarios:**

```python
# UI has "Move Up" button
# User clicks 3 times -> move up 3 positions
button_clicks = 3
moved = project.Senses.MoveUp(entry, selected_sense, positions=button_clicks)

# UI has "Move to Top" button
# Move to index 0
project.Senses.MoveToIndex(entry, selected_sense, 0)

# UI has "Move to Bottom" button
# Move to last position
last_index = entry.SensesOS.Count - 1
project.Senses.MoveToIndex(entry, selected_sense, last_index)

# UI has "Sort by..." dropdown
# User selects "Sort by Gloss"
project.Senses.Sort(entry, key_func=lambda s: project.Senses.GetGloss(s))

# UI has drag-and-drop
# User drags sense from position 5 to after sense at position 2
dragged_sense = entry.SensesOS[5]
target_sense = entry.SensesOS[2]
project.Senses.MoveAfter(dragged_sense, target_sense)
```

---

## Implementation Pattern

All reordering methods follow this safe pattern:

```python
def _reorder_sequence(sequence, new_order_items):
    """
    Internal helper to safely reorder an OS collection.

    Args:
        sequence: The ILcmOwningSequence to reorder
        new_order_items: List of items in desired order

    Process:
        1. Validate all items belong to sequence
        2. Clear sequence (removes from collection, preserves objects)
        3. Add items back in new order
        4. All object connections remain intact
    """
    # Validate
    if len(new_order_items) != sequence.Count:
        raise ValueError("Item count mismatch")

    # Clear (doesn't delete objects, just removes from sequence)
    sequence.Clear()

    # Re-add in new order
    for item in new_order_items:
        sequence.Add(item)

    # Done - all GUIDs, properties, references preserved!
```

### MoveUp/MoveDown Implementation Example

```python
def MoveUp(self, parent_or_hvo, item, positions=1):
    """Move item up (toward index 0) by specified positions."""
    # Get the sequence
    parent = self._GetObject(parent_or_hvo)
    sequence = self._GetSequence(parent)  # e.g., entry.SensesOS

    # Find current index
    current_items = list(sequence)
    try:
        current_index = current_items.index(item)
    except ValueError:
        raise ValueError("Item not found in sequence")

    # Calculate new index (clamped to 0)
    new_index = max(0, current_index - positions)
    actual_moved = current_index - new_index

    # If no movement needed
    if actual_moved == 0:
        return 0

    # Reorder
    current_items.pop(current_index)
    current_items.insert(new_index, item)

    # Apply to sequence
    sequence.Clear()
    for obj in current_items:
        sequence.Add(obj)

    return actual_moved


def MoveDown(self, parent_or_hvo, item, positions=1):
    """Move item down (toward end) by specified positions."""
    # Get the sequence
    parent = self._GetObject(parent_or_hvo)
    sequence = self._GetSequence(parent)

    # Find current index
    current_items = list(sequence)
    try:
        current_index = current_items.index(item)
    except ValueError:
        raise ValueError("Item not found in sequence")

    # Calculate new index (clamped to last position)
    max_index = len(current_items) - 1
    new_index = min(max_index, current_index + positions)
    actual_moved = new_index - current_index

    # If no movement needed
    if actual_moved == 0:
        return 0

    # Reorder
    current_items.pop(current_index)
    current_items.insert(new_index, item)

    # Apply to sequence
    sequence.Clear()
    for obj in current_items:
        sequence.Add(obj)

    return actual_moved
```

---

## Example Use Cases

### Use Case 1: Sort Allomorphs by Environment Complexity

```python
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

FLExInitialize()
project = FLExProject()
project.OpenProject("MyProject", writeEnabled=True)

# Get an entry with multiple allomorphs
entry = project.LexEntry.Find("walk")

def environment_complexity(allomorph):
    """
    Score environment complexity.
    More complex = higher score = should come first.
    """
    # Get the environment string representation
    env = project.Allomorphs.GetEnvironment(allomorph)
    if not env:
        return 0  # No environment = least specific

    env_str = str(env)

    # Count complexity factors:
    complexity = 0
    complexity += env_str.count('[')  # Features
    complexity += env_str.count('/')  # Phonemes
    complexity += env_str.count('_')  # Boundaries

    # Also consider length
    complexity += len(env_str) * 0.1

    return complexity

# Sort allomorphs: most complex environments first
count = project.Allomorphs.Sort(entry,
                               key_func=environment_complexity,
                               reverse=True)

print(f"Reordered {count} allomorphs by environment complexity")

# Verify new order
for i, allo in enumerate(entry.AlternateFormsOS):
    form = project.Allomorphs.GetForm(allo)
    env = project.Allomorphs.GetEnvironment(allo)
    score = environment_complexity(allo)
    print(f"{i+1}. {form} / {env} (complexity: {score})")

project.CloseProject()
FLExCleanup()
```

### Use Case 2: Promote Secondary Sense to Primary

```python
# User identifies that sense #3 should be primary
entry = project.LexEntry.Find("run")
secondary_sense = entry.SensesOS[2]

# Move to position 0 (primary)
project.Senses.MoveToIndex(entry, secondary_sense, 0)

# Or use MoveBefore
current_primary = entry.SensesOS[0]
project.Senses.MoveBefore(secondary_sense, current_primary)
```

### Use Case 3: Custom Sense Ordering

```python
# Sort senses by frequency (from custom field or corpus analysis)
def sense_frequency(sense):
    # Get frequency from custom field or calculated value
    freq = project.Senses.GetCustomField(sense, "Frequency")
    return int(freq) if freq else 0

# Most frequent senses first
project.Senses.Sort(entry,
                   key_func=sense_frequency,
                   reverse=True)
```

### Use Case 4: UI with Up/Down Buttons

```python
# User selects a sense in the UI and clicks "Move Up" multiple times
selected_sense = entry.SensesOS[5]

# First click
moved = project.Senses.MoveUp(entry, selected_sense, positions=1)
print(f"Moved up {moved} positions")  # "Moved up 1 positions"
# Sense now at index 4

# Hold button for 3 more positions
moved = project.Senses.MoveUp(entry, selected_sense, positions=3)
print(f"Moved up {moved} positions")  # "Moved up 3 positions"
# Sense now at index 1

# Try to move past top
moved = project.Senses.MoveUp(entry, selected_sense, positions=10)
print(f"Moved up {moved} positions")  # "Moved up 1 positions" (clamped)
# Sense now at index 0 (primary)

# User changes mind - move it down a bit
moved = project.Senses.MoveDown(entry, selected_sense, positions=2)
print(f"Moved down {moved} positions")  # "Moved down 2 positions"
# Sense now at index 2
```

### Use Case 5: Keyboard Shortcuts

```python
# User interface with keyboard shortcuts
# Ctrl+Up = move up 1, Ctrl+Shift+Up = move to top
# Ctrl+Down = move down 1, Ctrl+Shift+Down = move to bottom

def handle_keyboard(key, shift_held, selected_allomorph):
    if key == "UP":
        if shift_held:
            # Move to top (Ctrl+Shift+Up)
            project.Allomorphs.MoveToIndex(entry, selected_allomorph, 0)
        else:
            # Move up one (Ctrl+Up)
            project.Allomorphs.MoveUp(entry, selected_allomorph)

    elif key == "DOWN":
        if shift_held:
            # Move to bottom (Ctrl+Shift+Down)
            last_index = entry.AlternateFormsOS.Count - 1
            project.Allomorphs.MoveToIndex(entry, selected_allomorph, last_index)
        else:
            # Move down one (Ctrl+Down)
            project.Allomorphs.MoveDown(entry, selected_allomorph)
```

### Use Case 6: Interleave Examples from Multiple Sources

```python
# User wants examples alternating between elicited and corpus
sense = entry.SensesOS[0]

def example_source_order(example):
    """
    Custom ordering: elicited examples first, then corpus.
    Within each group, maintain original order.
    """
    source = project.Examples.GetSource(example)
    original_index = list(sense.ExamplesOS).index(example)

    if source == "elicited":
        return (0, original_index)  # Group 0, preserve order
    elif source == "corpus":
        return (1, original_index)  # Group 1, preserve order
    else:
        return (2, original_index)  # Group 2, unknown sources

project.Examples.Sort(sense, key_func=example_source_order)
```

---

## Safety Checklist

Before implementing reordering operations, verify:

- ✅ Working with `OS` (Owning Sequence) property
- ✅ Project opened with `writeEnabled=True`
- ✅ Using `.Clear()` and `.Add()` pattern
- ✅ Not modifying sequence during iteration
- ✅ All items belong to same parent sequence
- ✅ Transaction/undo handling if needed

---

## What NOT to Worry About

These are **automatically preserved** during reordering:

- ❌ No need to update GUIDs (immutable)
- ❌ No need to fix references (use GUIDs, not indices)
- ❌ No need to update child objects (owned relationship preserved)
- ❌ No need to refresh caches (FLEx handles automatically)
- ❌ No need to save explicitly (part of normal project save)

---

## Performance Considerations

### Efficient Reordering

```python
# ✅ GOOD - Single operation
items = list(sequence)
items.sort(key=key_func)
sequence.Clear()
for item in items:
    sequence.Add(item)

# ❌ BAD - Multiple operations
for i in range(len(sequence)):
    for j in range(i+1, len(sequence)):
        if should_swap(sequence[i], sequence[j]):
            # Many Clear/Add operations = slow
```

### Batch Operations

```python
# If reordering many entries:
for entry in project.LexEntry.GetAll():
    if needs_reordering(entry):
        project.Senses.Sort(entry, key_func=my_sort)
        # Each entry reordered individually
```

---

## Testing Strategy

### Unit Tests

```python
def test_sort_preserves_connections():
    """Verify that sorting doesn't break object relationships."""
    entry = create_test_entry_with_senses()

    # Get original data
    sense1 = entry.SensesOS[0]
    original_gloss = project.Senses.GetGloss(sense1)
    original_pos = project.Senses.GetPOS(sense1)
    original_examples = list(sense1.ExamplesOS)

    # Reverse order
    project.Senses.Sort(entry, reverse=True)

    # Verify sense1 still has all its data
    assert project.Senses.GetGloss(sense1) == original_gloss
    assert project.Senses.GetPOS(sense1) == original_pos
    assert list(sense1.ExamplesOS) == original_examples

    # Verify it just moved position
    assert entry.SensesOS[-1] == sense1  # Now at end
```

### Integration Tests

```python
def test_allomorph_reordering_affects_parser():
    """
    Verify that reordering allomorphs affects parser behavior.
    This proves reordering works semantically.
    """
    entry = create_entry_with_conditioned_allomorphs()

    # Initial order: specific before general
    # Parser tries each in sequence
    parse1 = parse_word_with_entry(word, entry)

    # Reverse allomorph order
    project.Allomorphs.Sort(entry, reverse=True)

    # Parser now tries in different order
    parse2 = parse_word_with_entry(word, entry)

    # Different allomorph selected
    assert parse1.selected_allomorph != parse2.selected_allomorph
```

---

## Documentation for Users

### Warning Message

When implementing these methods, include this in the docstrings:

```
⚠️  LINGUISTIC SIGNIFICANCE WARNING

Reordering changes the linguistic meaning and behavior:

- Senses: Primary sense is first, affects display and semantics
- Allomorphs: First matching allomorph is selected by parser
- Examples: Order may reflect preference or pedagogy
- Morphemes: Order represents morphological structure

Reorder only when linguistically justified!

This operation is SAFE (preserves data connections) but
SIGNIFICANT (changes linguistic meaning).
```

---

## Conclusion

**Direct Answer to Your Question:**

> Would reordering break data connections?

**NO** - Reordering is safe and will NOT break:
- GUIDs
- Object references
- Properties
- Owned children
- Any data connections

**What reordering WILL change:**
- Sequence position (index)
- Processing order (which item is tried/displayed first)
- Linguistic meaning (which sense is primary, which allomorph is default)

**Recommended API methods:**
1. ✅ `Sort(parent, key_func, reverse)` - User provides sort algorithm
2. ✅ `MoveBefore(item, target)` - Precise repositioning
3. ✅ `MoveAfter(item, target)` - Precise repositioning
4. ✅ `MoveToIndex(parent, item, index)` - Direct index setting
5. ✅ `Swap(item1, item2)` - Simple swap
6. ✅ `MoveUp(parent, item, positions)` - Move toward start (with clamping)
7. ✅ `MoveDown(parent, item, positions)` - Move toward end (with clamping)

All are safe to implement using the `.Clear()` and `.Add()` pattern.

### Key Features of MoveUp/MoveDown

- **Automatic clamping**: Moving past boundaries stops at first/last position
- **Multi-position moves**: `positions` parameter allows moving multiple slots at once
- **Return value**: Returns actual positions moved (useful for UI feedback)
- **No effect at boundaries**: Returns 0 if already at limit
- **Perfect for UI**: Maps directly to up/down buttons, keyboard shortcuts, mouse wheel

---

**Document Version**: 1.0
**Status**: Design Proposal
**Ready for Implementation**: YES
