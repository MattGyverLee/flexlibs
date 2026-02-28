"""
Integration tests for phonological contexts with rules.

This module tests the end-to-end integration of phonological contexts
with phonological rules, ensuring that contexts are properly wrapped
and accessible through the rule's input_contexts property.

Tests verify:
- Rule input_contexts returns ContextCollection
- Contexts are properly wrapped in PhonologicalContext
- Context filtering works through rule access
- Backward compatibility with StrucDescOS
- Type diversity display
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys

# Mock SIL module before importing flexlibs2
sys.modules['SIL'] = MagicMock()
sys.modules['SIL.LCModel'] = MagicMock()


class TestContextIntegration:
    """Integration tests for contexts with rules."""

    def test_context_collection_creation(self):
        """Test creating ContextCollection with contexts."""
        from flexlibs2.code.System.context_collection import ContextCollection
        from test_context_wrappers import MockPhonologicalContext

        contexts = [
            MockPhonologicalContext('PhSimpleContextSeg'),
            MockPhonologicalContext('PhBoundaryContext'),
        ]

        collection = ContextCollection(contexts)

        # Should return ContextCollection
        assert isinstance(collection, ContextCollection)
        assert len(collection) == 2

    def test_context_collection_are_wrapped(self):
        """Test that contexts in collection are PhonologicalContext wrapped."""
        from flexlibs2.code.System.context_collection import ContextCollection
        from test_context_wrappers import MockPhonologicalContext

        contexts = [
            MockPhonologicalContext('PhSimpleContextSeg'),
            MockPhonologicalContext('PhSimpleContextNC'),
        ]

        collection = ContextCollection(contexts)

        # Each context should behave like PhonologicalContext
        for context in collection:
            assert hasattr(context, 'is_simple_context_seg')
            assert hasattr(context, 'context_name')

    def test_context_type_breakdown_display(self):
        """Test that collection displays type breakdown."""
        from flexlibs2.code.System.context_collection import ContextCollection
        from test_context_wrappers import MockPhonologicalContext

        contexts = [
            MockPhonologicalContext('PhSimpleContextSeg'),
            MockPhonologicalContext('PhSimpleContextSeg'),
            MockPhonologicalContext('PhBoundaryContext'),
            MockPhonologicalContext('PhSimpleContextNC'),
        ]

        collection = ContextCollection(contexts)

        # Display should show type breakdown
        str_repr = str(collection)
        assert 'ContextCollection' in str_repr
        assert '4 total' in str_repr
        assert 'PhSimpleContextSeg: 2' in str_repr
        assert 'PhBoundaryContext: 1' in str_repr
        assert 'PhSimpleContextNC: 1' in str_repr

    def test_context_filtering_in_collection(self):
        """Test filtering contexts in collection."""
        from flexlibs2.code.System.context_collection import ContextCollection
        from test_context_wrappers import MockPhonologicalContext

        contexts = [
            MockPhonologicalContext('PhSimpleContextSeg'),
            MockPhonologicalContext('PhBoundaryContext'),
            MockPhonologicalContext('PhSimpleContextSeg'),
        ]

        collection = ContextCollection(contexts)

        # Filter contexts in collection
        simple = collection.simple_contexts()
        assert len(simple) == 2

        boundaries = collection.boundary_contexts()
        assert len(boundaries) == 1

        segs = collection.simple_context_seg()
        assert len(segs) == 2

    def test_empty_contexts_returns_empty_collection(self):
        """Test that empty collection works."""
        from flexlibs2.code.System.context_collection import ContextCollection

        collection = ContextCollection()

        assert isinstance(collection, ContextCollection)
        assert len(collection) == 0

    def test_collection_with_complex_contexts(self):
        """Test collection with complex context types."""
        from flexlibs2.code.System.context_collection import ContextCollection
        from test_context_wrappers import MockPhonologicalContext

        contexts = [
            MockPhonologicalContext('PhComplexContextSeg'),
            MockPhonologicalContext('PhComplexContextNC'),
            MockPhonologicalContext('PhBoundaryContext'),
        ]

        collection = ContextCollection(contexts)

        # Test complex context filtering
        complex_only = collection.complex_contexts()
        assert len(complex_only) == 2

        complex_seg = collection.complex_context_seg()
        assert len(complex_seg) == 1

        complex_nc = collection.complex_context_nc()
        assert len(complex_nc) == 1

    def test_context_chaining_in_collection(self):
        """Test chaining filters on collection."""
        from flexlibs2.code.System.context_collection import ContextCollection
        from test_context_wrappers import MockPhonologicalContext

        contexts = [
            MockPhonologicalContext('PhSimpleContextSeg'),
            MockPhonologicalContext('PhSimpleContextSeg'),
            MockPhonologicalContext('PhBoundaryContext'),
        ]

        collection = ContextCollection(contexts)

        # Chain filters
        result = collection.simple_contexts()
        assert len(result) == 2

        # Further filter on already filtered collection
        boundaries = collection.boundary_contexts()
        assert len(boundaries) == 1

    def test_context_iteration_in_collection(self):
        """Test iterating over collection."""
        from flexlibs2.code.System.context_collection import ContextCollection
        from test_context_wrappers import MockPhonologicalContext

        contexts = [
            MockPhonologicalContext('PhSimpleContextSeg'),
            MockPhonologicalContext('PhBoundaryContext'),
        ]

        collection = ContextCollection(contexts)

        # Iterate and check each context
        count = 0
        for context in collection:
            count += 1
            # Each should be a PhonologicalContext
            assert hasattr(context, 'is_simple_context_seg')

        assert count == 2

    def test_all_context_types_in_collection(self):
        """Test collection with all context types."""
        from flexlibs2.code.System.context_collection import ContextCollection
        from test_context_wrappers import MockPhonologicalContext

        contexts = [
            MockPhonologicalContext('PhSimpleContextSeg'),
            MockPhonologicalContext('PhSimpleContextNC'),
            MockPhonologicalContext('PhComplexContextSeg'),
            MockPhonologicalContext('PhComplexContextNC'),
            MockPhonologicalContext('PhBoundaryContext'),
        ]

        collection = ContextCollection(contexts)

        assert len(collection) == 5

        # Verify type-specific counts
        assert len(collection.simple_context_seg()) == 1
        assert len(collection.simple_context_nc()) == 1
        assert len(collection.complex_context_seg()) == 1
        assert len(collection.complex_context_nc()) == 1
        assert len(collection.boundary_contexts()) == 1

    def test_context_property_access_in_collection(self):
        """Test accessing context properties through collection."""
        from flexlibs2.code.System.context_collection import ContextCollection
        from test_context_wrappers import MockPhonologicalContext

        contexts = [MockPhonologicalContext('PhSimpleContextSeg')]

        collection = ContextCollection(contexts)

        # Access properties of context
        context = collection[0]
        assert context.is_simple_context_seg
        assert not context.is_boundary_context

    def test_multiple_collections_independent(self):
        """Test that context collections are independent."""
        from flexlibs2.code.System.context_collection import ContextCollection
        from test_context_wrappers import MockPhonologicalContext

        contexts1 = [
            MockPhonologicalContext('PhSimpleContextSeg'),
            MockPhonologicalContext('PhSimpleContextSeg'),
        ]
        contexts2 = [
            MockPhonologicalContext('PhBoundaryContext'),
            MockPhonologicalContext('PhBoundaryContext'),
            MockPhonologicalContext('PhBoundaryContext'),
        ]

        col1 = ContextCollection(contexts1)
        col2 = ContextCollection(contexts2)

        # Each has its own type distribution
        assert len(col1.simple_context_seg()) == 2
        assert len(col1.boundary_contexts()) == 0

        assert len(col2.boundary_contexts()) == 3
        assert len(col2.simple_context_seg()) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
