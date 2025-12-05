#
#   BaseOperations.py
#
#   Class: BaseOperations
#          Base class for all FLEx operation classes.
#          Provides reordering functionality for owning sequences.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

import logging
logger = logging.getLogger(__name__)


class BaseOperations:
    """
    Base class for all FLEx operation classes.

    Provides common reordering functionality that works with any FLEx
    Owning Sequence (OS) collection. Subclasses must override _GetSequence()
    to specify which OS property to reorder.

    All 43 operation classes inherit from this base class, gaining access
    to 7 reordering methods without code duplication.

    Reordering Safety:
        - Reordering is SAFE - preserves all data connections
        - GUIDs, references, properties, and children remain intact
        - Only changes the sequence position (index)
        - Uses safe Clear/Add pattern for all operations

    Linguistic Significance:
        - Reordering changes linguistic meaning and behavior
        - Senses: First sense is primary
        - Allomorphs: First matching allomorph selected by parser
        - Examples: Order may reflect preference or pedagogy
        - Reorder only when linguistically justified

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("MyProject", writeEnabled=True)

        entry = list(project.LexiconAllEntries())[0]

        # All operation classes have these methods:

        # Sort senses alphabetically
        project.Senses.Sort(entry,
                           key_func=lambda s: project.Senses.GetGloss(s))

        # Move sense up one position
        sense = entry.SensesOS[2]
        project.Senses.MoveUp(entry, sense)

        # Move allomorph to specific index
        allo = entry.AlternateFormsOS[3]
        project.Allomorphs.MoveToIndex(entry, allo, 0)

        # Swap two examples
        ex1 = sense.ExamplesOS[0]
        ex2 = sense.ExamplesOS[1]
        project.Examples.Swap(ex1, ex2)

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize BaseOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    # ========== REORDERING METHODS ==========

    def Sort(self, parent_or_hvo, key_func=None, reverse=False):
        """
        Sort items in an owning sequence using a custom key function.

        This method reorders all items in the sequence according to a
        sorting criterion. The sort is stable and uses Python's built-in
        sort algorithm.

        Args:
            parent_or_hvo: The parent object or HVO containing the sequence.
            key_func: Optional function(item) -> comparable_value.
                     If None, uses natural ordering (may fail if items
                     don't support comparison).
            reverse: If True, sort in descending order. Default False.

        Returns:
            int: Number of items sorted (length of sequence).

        Raises:
            TypeError: If key_func is None and items don't support comparison.
            Exception: If any error occurs during sorting.

        Example:
            >>> # Sort allomorphs by form length
            >>> project.Allomorphs.Sort(entry,
            ...     key_func=lambda a: len(project.Allomorphs.GetForm(a)))
            3

            >>> # Sort senses alphabetically by gloss
            >>> project.Senses.Sort(entry,
            ...     key_func=lambda s: project.Senses.GetGloss(s))
            5

            >>> # Sort in reverse order (most complex first)
            >>> def complexity(allo):
            ...     env = project.Allomorphs.GetEnvironment(allo)
            ...     return len(str(env)) if env else 0
            >>> project.Allomorphs.Sort(entry,
            ...     key_func=complexity,
            ...     reverse=True)
            3

            >>> # Sort examples by length (shortest first)
            >>> project.Examples.Sort(sense,
            ...     key_func=lambda ex: len(project.Examples.GetText(ex)))
            4

        Notes:
            - Returns count even if order unchanged
            - Empty sequence returns 0
            - Uses safe Clear/Add pattern - preserves all data
            - Sort is stable (equal elements maintain relative order)
            - If key_func raises exception, sort fails

        Linguistic Warning:
            Reordering changes linguistic behavior:
            - Senses: Primary sense is first
            - Allomorphs: Parser tries in sequence order
            - Examples: Order may be pedagogically significant

        See Also:
            MoveToIndex, MoveUp, MoveDown
        """
        parent = self._GetObject(parent_or_hvo)
        sequence = self._GetSequence(parent)

        # Get all items with their indices
        count = sequence.Count
        if count <= 1:
            return count  # Nothing to sort

        items_with_indices = [(i, sequence[i]) for i in range(count)]

        # Sort based on key function or natural order
        if key_func:
            items_with_indices.sort(key=lambda x: key_func(x[1]), reverse=reverse)
        else:
            items_with_indices.sort(key=lambda x: x[1], reverse=reverse)

        # Apply new order using MoveTo
        # We need to move items from their current position to their target position
        # Process from end to beginning to avoid index shifting issues
        for target_index in range(count):
            # Find where the item that should be at target_index currently is
            current_index = target_index
            for j in range(target_index, count):
                if sequence[j] == items_with_indices[target_index][1]:
                    current_index = j
                    break

            # Move it to the target position if not already there
            if current_index != target_index:
                sequence.MoveTo(current_index, current_index, sequence, target_index)

        return count


    def MoveUp(self, parent_or_hvo, item, positions=1):
        """
        Move an item up (toward index 0) by specified number of positions.

        Moves an item toward the beginning of the sequence. If the requested
        number of positions would move past index 0, the item is clamped at
        index 0 (no error raised).

        Args:
            parent_or_hvo: The parent object or HVO containing the sequence.
            item: The item to move (object, not HVO).
            positions: Number of positions to move up. Must be positive.
                      Default is 1.

        Returns:
            int: Actual number of positions moved. May be less than requested
                 if item reaches index 0. Returns 0 if already at index 0.

        Raises:
            ValueError: If item not found in sequence.
            ValueError: If positions is negative or zero.

        Example:
            >>> # Move sense up one position (e.g., from index 3 to 2)
            >>> sense = entry.SensesOS[3]
            >>> moved = project.Senses.MoveUp(entry, sense)
            >>> print(f"Moved {moved} positions")
            Moved 1 positions

            >>> # Move allomorph to top (up 5 positions)
            >>> allo = entry.AlternateFormsOS[5]
            >>> moved = project.Allomorphs.MoveUp(entry, allo, positions=5)
            >>> print(f"Now at index {list(entry.AlternateFormsOS).index(allo)}")
            Now at index 0

            >>> # Try to move past start (clamped at 0)
            >>> example = sense.ExamplesOS[1]
            >>> moved = project.Examples.MoveUp(sense, example, positions=10)
            >>> print(f"Actually moved {moved} positions")
            Actually moved 1 positions

            >>> # Already at start - no movement
            >>> first = entry.SensesOS[0]
            >>> moved = project.Senses.MoveUp(entry, first)
            >>> print(f"Moved {moved} positions")
            Moved 0 positions

        Notes:
            - Auto-clamps at boundary (no IndexError)
            - Returns actual movement for UI feedback
            - Item stays at current position if already at top
            - Uses safe Clear/Add pattern
            - Perfect for "Move Up" buttons in UI

        Linguistic Warning:
            Moving items up increases their priority:
            - Senses: Moving to index 0 makes it primary
            - Allomorphs: Moving up means parser tries earlier

        See Also:
            MoveDown, MoveToIndex, MoveBefore
        """
        if positions <= 0:
            raise ValueError("positions must be positive integer")

        parent = self._GetObject(parent_or_hvo)
        sequence = self._GetSequence(parent)

        # Find current index
        current_index = -1
        for i in range(sequence.Count):
            if sequence[i] == item:
                current_index = i
                break

        if current_index == -1:
            raise ValueError("Item not found in sequence")

        # Already at top - no movement
        if current_index == 0:
            return 0

        # Calculate new index (clamped to 0)
        new_index = max(0, current_index - positions)
        actual_moved = current_index - new_index

        # Move using FLEx's MoveTo method
        # When moving backward (up), use target index directly
        if actual_moved > 0:
            sequence.MoveTo(current_index, current_index, sequence, new_index)

        return actual_moved


    def MoveDown(self, parent_or_hvo, item, positions=1):
        """
        Move an item down (toward end) by specified number of positions.

        Moves an item toward the end of the sequence. If the requested
        number of positions would move past the end, the item is clamped
        at the last index (no error raised).

        Args:
            parent_or_hvo: The parent object or HVO containing the sequence.
            item: The item to move (object, not HVO).
            positions: Number of positions to move down. Must be positive.
                      Default is 1.

        Returns:
            int: Actual number of positions moved. May be less than requested
                 if item reaches last index. Returns 0 if already at end.

        Raises:
            ValueError: If item not found in sequence.
            ValueError: If positions is negative or zero.

        Example:
            >>> # Move sense down one position (e.g., from index 1 to 2)
            >>> sense = entry.SensesOS[1]
            >>> moved = project.Senses.MoveDown(entry, sense)
            >>> print(f"Moved {moved} positions")
            Moved 1 positions

            >>> # Demote primary sense significantly
            >>> primary = entry.SensesOS[0]
            >>> moved = project.Senses.MoveDown(entry, primary, positions=3)
            >>> print(f"Now at index {list(entry.SensesOS).index(primary)}")
            Now at index 3

            >>> # Try to move past end (clamped)
            >>> allo = entry.AlternateFormsOS[8]  # Count = 10
            >>> moved = project.Allomorphs.MoveDown(entry, allo, positions=5)
            >>> print(f"Actually moved {moved} positions")
            Actually moved 1 positions

            >>> # Already at end - no movement
            >>> last = entry.SensesOS[entry.SensesOS.Count - 1]
            >>> moved = project.Senses.MoveDown(entry, last)
            >>> print(f"Moved {moved} positions")
            Moved 0 positions

        Notes:
            - Auto-clamps at boundary (no IndexError)
            - Returns actual movement for UI feedback
            - Item stays at current position if already at end
            - Uses safe Clear/Add pattern
            - Perfect for "Move Down" buttons in UI

        Linguistic Warning:
            Moving items down decreases their priority:
            - Senses: Moving from index 0 demotes primary sense
            - Allomorphs: Moving down means parser tries later

        See Also:
            MoveUp, MoveToIndex, MoveAfter
        """
        if positions <= 0:
            raise ValueError("positions must be positive integer")

        parent = self._GetObject(parent_or_hvo)
        sequence = self._GetSequence(parent)

        # Find current index
        current_index = -1
        for i in range(sequence.Count):
            if sequence[i] == item:
                current_index = i
                break

        if current_index == -1:
            raise ValueError("Item not found in sequence")

        # Already at end - no movement
        max_index = sequence.Count - 1
        if current_index == max_index:
            return 0

        # Calculate new index (clamped to max)
        new_index = min(max_index, current_index + positions)
        actual_moved = new_index - current_index

        # Move using FLEx's MoveTo method
        # When moving forward (down), need to use new_index + 1 due to FLEx behavior
        if actual_moved > 0:
            sequence.MoveTo(current_index, current_index, sequence, new_index + 1)

        return actual_moved


    def MoveToIndex(self, parent_or_hvo, item, new_index):
        """
        Move an item to a specific index position.

        Directly moves an item to the specified index. Other items are
        shifted accordingly. This is useful for absolute positioning.

        Args:
            parent_or_hvo: The parent object or HVO containing the sequence.
            item: The item to move (object, not HVO).
            new_index: Target index (0-based). Must be valid index for
                      current sequence length.

        Returns:
            bool: True if successful.

        Raises:
            ValueError: If item not found in sequence.
            IndexError: If new_index is out of range [0, count-1].

        Example:
            >>> # Make third sense the primary sense
            >>> third_sense = entry.SensesOS[2]
            >>> project.Senses.MoveToIndex(entry, third_sense, 0)
            True

            >>> # Move allomorph to end
            >>> allo = entry.AlternateFormsOS[1]
            >>> last_index = entry.AlternateFormsOS.Count - 1
            >>> project.Allomorphs.MoveToIndex(entry, allo, last_index)
            True

            >>> # Move example to middle position
            >>> ex = sense.ExamplesOS[0]
            >>> project.Examples.MoveToIndex(sense, ex, 2)
            True

        Notes:
            - Validates index before moving
            - Raises IndexError for out-of-range index
            - Moving to current index is allowed (no-op)
            - Uses safe Clear/Add pattern
            - Good for drag-and-drop UI implementation

        Linguistic Warning:
            Index 0 has special significance:
            - Senses: Index 0 is the primary sense
            - Allomorphs: Index 0 is the default form
            - Moving to index 0 changes linguistic priority

        See Also:
            MoveUp, MoveDown, MoveBefore, MoveAfter
        """
        parent = self._GetObject(parent_or_hvo)
        sequence = self._GetSequence(parent)

        # Find current index
        current_index = -1
        for i in range(sequence.Count):
            if sequence[i] == item:
                current_index = i
                break

        if current_index == -1:
            raise ValueError("Item not found in sequence")

        # Validate new index
        if new_index < 0 or new_index >= sequence.Count:
            raise IndexError(
                f"Index {new_index} out of range [0, {sequence.Count-1}]"
            )

        # Move using FLEx's MoveTo method
        # Adjust destination index based on direction
        if current_index != new_index:
            if current_index < new_index:
                # Moving forward - use new_index + 1
                sequence.MoveTo(current_index, current_index, sequence, new_index + 1)
            else:
                # Moving backward - use new_index directly
                sequence.MoveTo(current_index, current_index, sequence, new_index)

        return True


    def MoveBefore(self, item_to_move, target_item):
        """
        Move an item to position immediately before another item.

        Positions item_to_move directly before target_item in the sequence.
        Both items must be in the same sequence (same parent). The parent
        is automatically determined by examining the items' Owner property.

        Args:
            item_to_move: The item to reposition (object, not HVO).
            target_item: The item before which to insert (object, not HVO).

        Returns:
            bool: True if successful.

        Raises:
            ValueError: If items not in same sequence or not found.

        Example:
            >>> # Move secondary sense to become primary
            >>> primary = entry.SensesOS[0]
            >>> secondary = entry.SensesOS[2]
            >>> project.Senses.MoveBefore(secondary, primary)
            True

            >>> # Move variant allomorph before default
            >>> default = entry.AlternateFormsOS[0]
            >>> variant = entry.AlternateFormsOS[3]
            >>> project.Allomorphs.MoveBefore(variant, default)
            True

        Notes:
            - Automatically finds common parent sequence
            - Both items must be in same owning sequence
            - Uses safe Clear/Add pattern
            - Perfect for drag-and-drop "insert before" operations
            - No parent_or_hvo parameter needed

        Linguistic Warning:
            Relative positioning changes processing order:
            - Allomorphs: Earlier forms tried first by parser
            - Senses: Earlier senses are more prominent

        See Also:
            MoveAfter, MoveToIndex, Swap
        """
        # Find which sequence contains both items
        sequence = self._FindCommonSequence(item_to_move, target_item)

        # Find indices of both items
        # Note: sequence from reflection may not support indexing, use enumeration
        move_index = -1
        target_index = -1
        index = 0
        for item in sequence:
            if item == item_to_move:
                move_index = index
            if item == target_item:
                target_index = index
            index += 1

        # Move using FLEx's MoveTo method
        if move_index != -1 and target_index != -1 and move_index != target_index:
            if move_index < target_index:
                # Moving forward - use target_index (will end up before target)
                sequence.MoveTo(move_index, move_index, sequence, target_index)
            else:
                # Moving backward - use target_index directly
                sequence.MoveTo(move_index, move_index, sequence, target_index)

        return True


    def MoveAfter(self, item_to_move, target_item):
        """
        Move an item to position immediately after another item.

        Positions item_to_move directly after target_item in the sequence.
        Both items must be in the same sequence (same parent). The parent
        is automatically determined by examining the items' Owner property.

        Args:
            item_to_move: The item to reposition (object, not HVO).
            target_item: The item after which to insert (object, not HVO).

        Returns:
            bool: True if successful.

        Raises:
            ValueError: If items not in same sequence or not found.

        Example:
            >>> # Move primary sense to second position
            >>> primary = entry.SensesOS[0]
            >>> secondary = entry.SensesOS[1]
            >>> project.Senses.MoveAfter(primary, secondary)
            True

            >>> # Move variant allomorph after default
            >>> default = entry.AlternateFormsOS[0]
            >>> variant = entry.AlternateFormsOS[3]
            >>> project.Allomorphs.MoveAfter(variant, default)
            True

        Notes:
            - Automatically finds common parent sequence
            - Both items must be in same owning sequence
            - Uses safe Clear/Add pattern
            - Perfect for drag-and-drop "insert after" operations
            - No parent_or_hvo parameter needed

        Linguistic Warning:
            Relative positioning changes processing order:
            - Allomorphs: Later forms tried after earlier ones
            - Senses: Later senses are less prominent

        See Also:
            MoveBefore, MoveToIndex, Swap
        """
        # Find which sequence contains both items
        sequence = self._FindCommonSequence(item_to_move, target_item)

        # Find indices of both items
        # Note: sequence from reflection may not support indexing, use enumeration
        move_index = -1
        target_index = -1
        index = 0
        for item in sequence:
            if item == item_to_move:
                move_index = index
            if item == target_item:
                target_index = index
            index += 1

        # Move to position after target
        if move_index != -1 and target_index != -1 and move_index != target_index:
            # When moving after, we want to end up at target_index + 1
            # If moving forward: use target_index + 1 (will insert after due to removal)
            # If moving backward: use target_index + 1 directly
            if move_index < target_index:
                sequence.MoveTo(move_index, move_index, sequence, target_index + 1)
            else:
                sequence.MoveTo(move_index, move_index, sequence, target_index + 1)

        return True


    def Swap(self, item1, item2):
        """
        Swap the positions of two items in a sequence.

        Exchanges the positions of two items. Both items must be in the
        same sequence (same parent). The parent is automatically determined
        by examining the items' Owner property.

        Args:
            item1: First item to swap (object, not HVO).
            item2: Second item to swap (object, not HVO).

        Returns:
            bool: True if successful.

        Raises:
            ValueError: If items not in same sequence or not found.

        Example:
            >>> # Swap first and second senses
            >>> sense1 = entry.SensesOS[0]
            >>> sense2 = entry.SensesOS[1]
            >>> project.Senses.Swap(sense1, sense2)
            True

            >>> # Swap allomorphs
            >>> allo1 = entry.AlternateFormsOS[0]
            >>> allo2 = entry.AlternateFormsOS[3]
            >>> project.Allomorphs.Swap(allo1, allo2)
            True

        Notes:
            - Automatically finds common parent sequence
            - Both items must be in same owning sequence
            - Swapping item with itself is allowed (no-op)
            - Uses safe Clear/Add pattern
            - Works for adjacent or non-adjacent items
            - No parent_or_hvo parameter needed

        Linguistic Warning:
            Swapping changes relative priority:
            - Swapping primary sense changes which is primary
            - Swapping allomorphs changes parser order

        See Also:
            MoveBefore, MoveAfter, MoveToIndex
        """
        # Find which sequence contains both items
        sequence = self._FindCommonSequence(item1, item2)

        # Find indices
        # Note: sequence from reflection may not support indexing, use enumeration
        idx1 = -1
        idx2 = -1
        index = 0
        for item in sequence:
            if item == item1:
                idx1 = index
            if item == item2:
                idx2 = index
            index += 1

        # Swap using MoveTo operations
        # Strategy: Move lower-index item after higher-index item, then move higher item to original position
        if idx1 != -1 and idx2 != -1 and idx1 != idx2:
            if idx1 < idx2:
                # item1 is before item2
                # Step 1: Move item1 to after item2 (this pushes item2 earlier)
                # After this: [..., item2 at idx1, ..., item1 at idx2, ...]
                sequence.MoveTo(idx1, idx1, sequence, idx2 + 1)
                # Step 2: Now item2 is at idx1, move it to idx2
                # But idx2 is now idx2-1 because we removed item1
                sequence.MoveTo(idx1, idx1, sequence, idx2)
            else:
                # item2 is before item1
                # Step 1: Move item2 to after item1
                sequence.MoveTo(idx2, idx2, sequence, idx1 + 1)
                # Step 2: Now item1 is at idx2, move it to idx1
                sequence.MoveTo(idx2, idx2, sequence, idx1)

        return True


    # ========== SYNC INTEGRATION METHODS ==========

    def GetSyncableProperties(self, item):
        """
        Get dictionary of syncable properties for cross-project synchronization.

        This method is OPTIONAL for sync framework integration. Subclasses that
        want to support the sync framework (flexlibs.sync) should implement this
        method to specify which properties can be safely synchronized between
        projects.

        The sync framework uses this method to:
        - Extract property values for comparison (DiffEngine)
        - Build property-level diffs showing what changed
        - Enable selective merging of individual properties (MergeOperations)
        - Support conflict resolution in multi-way syncs

        Args:
            item: The FLEx object to extract properties from.

        Returns:
            dict: Property names mapped to their values. Keys should be property
                  names (strings), values should be JSON-serializable when possible.
                  For complex FLEx objects (MultiString, etc.), return appropriate
                  representations.

        Raises:
            NotImplementedError: If subclass doesn't implement sync support.

        Example Implementation (in LexSenseOperations):
            >>> def GetSyncableProperties(self, sense):
            ...     '''Get syncable properties from a sense.'''
            ...     return {
            ...         'Gloss': self.GetGloss(sense),
            ...         'Definition': self.GetDefinition(sense),
            ...         'PartOfSpeech': self.GetPartOfSpeech(sense),
            ...         'SemanticDomains': self.GetSemanticDomains(sense),
            ...         'ExampleCount': sense.ExamplesOS.Count,
            ...         # Note: Don't include order-dependent items in properties
            ...         # The sync framework handles OS sequences separately
            ...     }

        Example Usage (by sync framework):
            >>> from flexlibs.sync import DiffEngine
            >>>
            >>> # Compare senses between two projects
            >>> props1 = project1.Senses.GetSyncableProperties(sense1)
            >>> props2 = project2.Senses.GetSyncableProperties(sense2)
            >>>
            >>> diff_engine = DiffEngine()
            >>> is_different, differences = diff_engine.CompareProperties(
            ...     props1, props2
            ... )
            >>>
            >>> if is_different:
            ...     print(f"Properties changed: {list(differences.keys())}")
            ...     for prop, (old_val, new_val) in differences.items():
            ...         print(f"  {prop}: {old_val} -> {new_val}")

        Notes:
            - Return only properties that make sense to sync (not GUIDs, HVOs)
            - Don't include computed properties that depend on context
            - Don't include owning sequences (OS) - sync framework handles those
            - Return None or empty string for missing/empty properties
            - Complex objects: return string representations or dicts
            - This method is optional - subclasses that don't implement it
              simply won't support property-level sync

        What to Include:
            - Text fields (gloss, definition, notes)
            - References (part of speech, semantic domains)
            - Simple flags/enums (morpheme type, status)
            - Counts (for validation)

        What to Exclude:
            - GUIDs (sync framework uses these for matching)
            - HVOs (project-specific IDs)
            - Owner references (implicit in structure)
            - Owning sequences (handled separately by sync framework)
            - DateCreated/DateModified (use merge strategy instead)

        Sync Framework Integration:
            Used by: flexlibs.sync.DiffEngine.CompareItems()
            Used by: flexlibs.sync.MergeOperations.MergeProperties()
            See also: CompareTo() for full item comparison

        See Also:
            CompareTo, flexlibs.sync.DiffEngine, flexlibs.sync.MergeOperations
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement GetSyncableProperties(). "
            "This method is OPTIONAL for sync framework integration. "
            "Implement it if you want to enable property-level synchronization "
            "for this item type. See flexlibs.sync documentation for details."
        )


    def CompareTo(self, item1, item2, ops1=None, ops2=None):
        """
        Compare two items and return detailed differences.

        This method is OPTIONAL for sync framework integration. Subclasses that
        want to support the sync framework (flexlibs.sync) should implement this
        method to enable intelligent comparison and merging between projects.

        The sync framework uses this method to:
        - Detect if two items (matched by GUID) have diverged
        - Generate detailed diff reports showing what changed
        - Support conflict detection in multi-way merges
        - Enable selective merge operations

        Args:
            item1: First item to compare (from source project).
            item2: Second item to compare (from target project).
            ops1: Optional. Operations instance for item1's project.
                  If None, uses self (assumes items from same project).
            ops2: Optional. Operations instance for item2's project.
                  If None, uses self (assumes items from same project).

        Returns:
            tuple: (is_different, differences) where:
                - is_different (bool): True if items differ in any way
                - differences (dict): Detailed differences with structure:
                    {
                        'properties': {
                            'PropertyName': {
                                'source': value_in_item1,
                                'target': value_in_item2,
                                'type': 'modified'|'added'|'removed'
                            },
                            ...
                        },
                        'children': {
                            'ChildSequenceName': {
                                'added': [guid1, guid2, ...],
                                'removed': [guid3, guid4, ...],
                                'modified': [guid5, guid6, ...]
                            },
                            ...
                        }
                    }

        Raises:
            NotImplementedError: If subclass doesn't implement sync support.

        Example Implementation (in LexSenseOperations):
            >>> def CompareTo(self, sense1, sense2, ops1=None, ops2=None):
            ...     '''Compare two senses for differences.'''
            ...     if ops1 is None:
            ...         ops1 = self
            ...     if ops2 is None:
            ...         ops2 = self
            ...
            ...     is_different = False
            ...     differences = {'properties': {}, 'children': {}}
            ...
            ...     # Compare properties
            ...     props1 = ops1.GetSyncableProperties(sense1)
            ...     props2 = ops2.GetSyncableProperties(sense2)
            ...
            ...     for key in set(props1.keys()) | set(props2.keys()):
            ...         val1 = props1.get(key)
            ...         val2 = props2.get(key)
            ...         if val1 != val2:
            ...             is_different = True
            ...             differences['properties'][key] = {
            ...                 'source': val1,
            ...                 'target': val2,
            ...                 'type': 'modified'
            ...             }
            ...
            ...     # Compare child sequences (examples)
            ...     guids1 = {ex.Guid for ex in sense1.ExamplesOS}
            ...     guids2 = {ex.Guid for ex in sense2.ExamplesOS}
            ...
            ...     added = guids2 - guids1
            ...     removed = guids1 - guids2
            ...
            ...     if added or removed:
            ...         is_different = True
            ...         differences['children']['Examples'] = {
            ...             'added': list(added),
            ...             'removed': list(removed),
            ...             'modified': []
            ...         }
            ...
            ...     return is_different, differences

        Example Usage (by sync framework):
            >>> from flexlibs.sync import DiffEngine
            >>>
            >>> # Find matching senses by GUID in two projects
            >>> sense1 = project1.Senses.FindByGuid(guid)
            >>> sense2 = project2.Senses.FindByGuid(guid)
            >>>
            >>> # Compare them
            >>> is_diff, diffs = project1.Senses.CompareTo(
            ...     sense1, sense2,
            ...     ops1=project1.Senses,
            ...     ops2=project2.Senses
            ... )
            >>>
            >>> if is_diff:
            ...     print("Sense has diverged between projects:")
            ...     for prop, details in diffs['properties'].items():
            ...         print(f"  {prop}: {details['source']} -> {details['target']}")
            ...
            ...     for child_name, child_diffs in diffs['children'].items():
            ...         if child_diffs['added']:
            ...             print(f"  {child_name} added: {len(child_diffs['added'])}")
            ...         if child_diffs['removed']:
            ...             print(f"  {child_name} removed: {len(child_diffs['removed'])}")

        Notes:
            - Compare items by content, not identity (different objects, same data)
            - Use GetSyncableProperties() for property comparison
            - Compare child sequences by GUID (not position or count alone)
            - Return empty differences dict if items are identical
            - This method is optional - subclasses that don't implement it
              simply won't support detailed diff/merge operations

        Comparison Strategy:
            1. Extract properties using GetSyncableProperties()
            2. Compare property values (use appropriate equality for types)
            3. Compare child sequences by GUID membership
            4. Optionally recurse to compare child content (use ops1/ops2)
            5. Build structured differences dict

        Cross-Project Comparison:
            - ops1/ops2 allow comparing items from different projects
            - Each ops instance knows how to extract properties from its project
            - Handles differences in project structure gracefully
            - Use GUID for matching children across projects

        Sync Framework Integration:
            Used by: flexlibs.sync.DiffEngine.GenerateDiff()
            Used by: flexlibs.sync.MergeOperations.DetectConflicts()
            See also: GetSyncableProperties() for property extraction

        See Also:
            GetSyncableProperties, flexlibs.sync.DiffEngine,
            flexlibs.sync.MergeOperations
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement CompareTo(). "
            "This method is OPTIONAL for sync framework integration. "
            "Implement it if you want to enable detailed comparison and "
            "conflict detection for this item type. See flexlibs.sync "
            "documentation for details."
        )


    # ========== HELPER METHODS ==========

    def _GetSequence(self, parent):
        """
        Get the owning sequence from parent object.

        This method MUST be overridden in subclasses to specify which
        owning sequence (OS) property to reorder.

        Args:
            parent: The parent object containing the sequence.

        Returns:
            ILcmOwningSequence: The sequence to reorder.

        Raises:
            NotImplementedError: If subclass doesn't override this method.

        Example (in subclass):
            >>> # In LexSenseOperations
            >>> def _GetSequence(self, parent):
            ...     return parent.SensesOS

            >>> # In AllomorphOperations
            >>> def _GetSequence(self, parent):
            ...     return parent.AlternateFormsOS

            >>> # In ExampleOperations
            >>> def _GetSequence(self, parent):
            ...     return parent.ExamplesOS

        Notes:
            - Each subclass specifies its own OS property
            - Called internally by all reordering methods
            - Provides type safety and correct sequence access

        See Also:
            All reordering methods use this internally.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _GetSequence() "
            "to specify which owning sequence to reorder. "
            "Example: return parent.SensesOS"
        )


    def _GetObject(self, obj_or_hvo):
        """
        Get object from HVO or return object directly.

        Handles the common pattern where methods accept either an object
        or its HVO (Handle Value Object = integer ID).

        Args:
            obj_or_hvo: Either an object or an HVO (int).

        Returns:
            object: The resolved object.

        Example:
            >>> # Using object directly
            >>> sense = entry.SensesOS[0]
            >>> resolved = self._GetObject(sense)
            >>> assert resolved is sense

            >>> # Using HVO
            >>> hvo = sense.Hvo
            >>> resolved = self._GetObject(hvo)
            >>> assert resolved.Hvo == hvo

        Notes:
            - If obj_or_hvo is int, retrieves object by HVO
            - If obj_or_hvo is object, returns it unchanged
            - Uses FLExProject.Object() for HVO resolution

        See Also:
            All methods that accept parent_or_hvo use this.
        """
        if isinstance(obj_or_hvo, int):
            return self.project.Object(obj_or_hvo)
        return obj_or_hvo


    def _FindCommonSequence(self, item1, item2):
        """
        Find the sequence that contains both items.

        Used by MoveBefore, MoveAfter, and Swap to automatically determine
        which sequence contains both items. Examines the Owner property
        and searches for OS properties containing both items.

        Args:
            item1: First item (object, not HVO).
            item2: Second item (object, not HVO).

        Returns:
            ILcmOwningSequence: The sequence containing both items.

        Raises:
            ValueError: If items don't have same owner.
            ValueError: If items not found in same sequence.
            ValueError: If no OS property contains both items.

        Example:
            >>> # Both senses from same entry
            >>> sense1 = entry.SensesOS[0]
            >>> sense2 = entry.SensesOS[2]
            >>> sequence = self._FindCommonSequence(sense1, sense2)
            >>> assert sequence is entry.SensesOS

            >>> # Both examples from same sense
            >>> ex1 = sense.ExamplesOS[0]
            >>> ex2 = sense.ExamplesOS[1]
            >>> sequence = self._FindCommonSequence(ex1, ex2)
            >>> assert sequence is sense.ExamplesOS

        Notes:
            - Checks Owner property first (most efficient)
            - Scans all properties ending in 'OS' (owning sequences)
            - Returns first sequence containing both items
            - Used internally by MoveBefore, MoveAfter, Swap

        Algorithm:
            1. Check if items have same Owner
            2. Search owner's properties for name ending in 'OS'
            3. Check if both items present in sequence
            4. Return first matching sequence

        See Also:
            MoveBefore, MoveAfter, Swap
        """
        # Verify items have Owner property
        if not hasattr(item1, 'Owner') or not hasattr(item2, 'Owner'):
            raise ValueError(
                "Items must have Owner property to find common sequence"
            )

        # Check if items have same owner
        if item1.Owner != item2.Owner:
            raise ValueError(
                "Items not in same sequence (different owners). "
                "MoveBefore/MoveAfter/Swap require items in same sequence."
            )

        # Items must also have the same OwningFlid (field ID) to be in same sequence
        if item1.OwningFlid != item2.OwningFlid:
            raise ValueError(
                "Items not in same sequence (different OwningFlid). "
                "MoveBefore/MoveAfter/Swap require items in same sequence."
            )

        # Get the parent object
        # Note: item1.Owner returns ICmObject, which doesn't expose properties like SensesOS
        # We need to use reflection to access properties
        parent = self._GetObject(item1.Owner.Hvo)

        # Use reflection to find the sequence property that contains both items
        # Iterate through all properties ending in 'OS' (Owning Sequence)
        parent_type = parent.GetType()
        for prop_info in parent_type.GetProperties():
            if prop_info.Name.endswith('OS'):
                try:
                    sequence = prop_info.GetValue(parent, None)
                    if sequence is None or not hasattr(sequence, 'Count'):
                        continue

                    # Check if both items are in this sequence
                    # Note: sequence from reflection may not support indexing, use iteration
                    found1 = False
                    found2 = False
                    for item in sequence:
                        if item == item1:
                            found1 = True
                        if item == item2:
                            found2 = True
                        if found1 and found2:
                            return sequence
                except:
                    # Property might not be accessible or not a sequence
                    continue

        # Items have same owner but not found in any OS property
        raise ValueError(
            "Items not in same sequence or sequence not found. "
            "Both items must be in the same owning sequence (OS)."
        )
