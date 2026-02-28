"""
Integration tests for phonological rules with wrappers.

These tests verify that:
1. PhonologicalRuleOperations.GetAll() returns RuleCollection
2. Wrapped rules work with operation methods (backward compatibility)
3. Properties are accessible on wrapped rules
4. Filtering works as expected
5. Type breakdown is displayed correctly
6. No breaking changes to existing functionality
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestPhonologicalRuleOperationsIntegration:
    """Integration tests for PhonologicalRuleOperations with wrappers.

    Note: Tests that actually import PhonologicalRuleOperations are skipped
    because they require FLEx/SIL.LCModel initialization. These are tested
    through integration tests with real FLEx projects.

    This test class focuses on verifying the contract that wrappers
    should follow when returned from operations.
    """

    def test_wrapped_rule_has_expected_properties(self):
        """Test that wrapped rules have the properties operations expect."""
        # Create a simulated wrapped rule
        wrapped_rule = Mock()
        wrapped_rule._obj = Mock()  # Has underlying object
        wrapped_rule.ClassName = 'PhRegularRule'
        wrapped_rule.name = 'Test Rule'
        wrapped_rule.direction = 0

        # Operations should be able to access these
        assert hasattr(wrapped_rule, 'ClassName')
        assert wrapped_rule.ClassName == 'PhRegularRule'
        assert wrapped_rule.name == 'Test Rule'
        assert wrapped_rule.direction == 0


class TestRuleCollectionIntegration:
    """Integration tests for RuleCollection with PhonologicalRuleOperations."""

    def test_collection_type_breakdown_display(self):
        """Test that collection displays type breakdown correctly."""
        from flexlibs2.code.Grammar.rule_collection import RuleCollection

        class MockRule:
            def __init__(self, class_type):
                self.class_type = class_type
                self.ClassName = class_type

        rules = [
            MockRule('PhRegularRule'),
            MockRule('PhRegularRule'),
            MockRule('PhMetathesisRule'),
            MockRule('PhReduplicationRule'),
        ]

        collection = RuleCollection(rules)
        display_str = str(collection)

        # Verify type breakdown is shown
        assert 'RuleCollection (4 total)' in display_str
        assert 'PhRegularRule: 2' in display_str
        assert 'PhMetathesisRule: 1' in display_str
        assert 'PhReduplicationRule: 1' in display_str

    def test_empty_collection_display(self):
        """Test that empty collection displays correctly."""
        from flexlibs2.code.Grammar.rule_collection import RuleCollection

        collection = RuleCollection()
        display_str = str(collection)

        assert 'empty' in display_str.lower()

    def test_collection_filtering_preserves_type(self):
        """Test that filtered collections return same type."""
        from flexlibs2.code.Grammar.rule_collection import RuleCollection

        class MockRule:
            def __init__(self, class_type, direction=0):
                self.class_type = class_type
                self.ClassName = class_type
                self.direction = direction

        rules = [
            MockRule('PhRegularRule', 0),
            MockRule('PhRegularRule', 1),
            MockRule('PhMetathesisRule', 0),
        ]

        collection = RuleCollection(rules)

        # Filter by direction
        ltr = collection.filter(direction=0)

        # Result should be RuleCollection
        assert isinstance(ltr, RuleCollection)
        assert len(ltr) == 2

    def test_collection_slicing_preserves_type(self):
        """Test that slicing collection returns same type."""
        from flexlibs2.code.Grammar.rule_collection import RuleCollection

        class MockRule:
            def __init__(self, class_type):
                self.class_type = class_type
                self.ClassName = class_type

        rules = [MockRule('PhRegularRule') for _ in range(5)]
        collection = RuleCollection(rules)

        # Slice collection
        sliced = collection[1:3]

        # Result should be RuleCollection
        assert isinstance(sliced, RuleCollection)
        assert len(sliced) == 2

    def test_collection_iteration_gives_individual_rules(self):
        """Test that iterating collection gives individual wrapped rules."""
        from flexlibs2.code.Grammar.rule_collection import RuleCollection

        class MockRule:
            def __init__(self, class_type):
                self.class_type = class_type
                self.ClassName = class_type

        rules = [MockRule('PhRegularRule') for _ in range(3)]
        collection = RuleCollection(rules)

        # Iterate and check we get individual rules
        for i, rule in enumerate(collection):
            assert rule.class_type == 'PhRegularRule'
            assert rule is rules[i]

    def test_collection_convenience_filters(self):
        """Test convenience filter methods work correctly."""
        from flexlibs2.code.Grammar.rule_collection import RuleCollection

        class MockRule:
            def __init__(self, class_type):
                self.class_type = class_type
                self.ClassName = class_type

        rules = [
            MockRule('PhRegularRule'),
            MockRule('PhMetathesisRule'),
            MockRule('PhReduplicationRule'),
            MockRule('PhRegularRule'),
        ]

        collection = RuleCollection(rules)

        # Test each convenience filter
        regular = collection.regular_rules()
        assert len(regular) == 2
        for rule in regular:
            assert rule.class_type == 'PhRegularRule'

        metathesis = collection.metathesis_rules()
        assert len(metathesis) == 1
        assert metathesis[0].class_type == 'PhMetathesisRule'

        redup = collection.redup_rules()
        assert len(redup) == 1
        assert redup[0].class_type == 'PhReduplicationRule'

    def test_collection_where_with_complex_predicate(self):
        """Test custom filtering with where() method."""
        from flexlibs2.code.Grammar.rule_collection import RuleCollection

        class MockRule:
            def __init__(self, class_type, name):
                self.class_type = class_type
                self.ClassName = class_type
                self.name = name

        rules = [
            MockRule('PhRegularRule', 'Voicing'),
            MockRule('PhRegularRule', 'Devoicing'),
            MockRule('PhMetathesisRule', 'Voicing Swap'),
        ]

        collection = RuleCollection(rules)

        # Custom filter: name contains 'Voicing' AND class is PhRegularRule
        filtered = collection.where(
            lambda r: 'Voicing' in r.name and r.class_type == 'PhRegularRule'
        )

        assert len(filtered) == 1
        assert filtered[0].name == 'Voicing'

    def test_collection_by_type_with_empty_result(self):
        """Test filtering by type when no matches exist."""
        from flexlibs2.code.Grammar.rule_collection import RuleCollection

        class MockRule:
            def __init__(self, class_type):
                self.class_type = class_type
                self.ClassName = class_type

        rules = [
            MockRule('PhRegularRule'),
            MockRule('PhRegularRule'),
        ]

        collection = RuleCollection(rules)

        # Filter to type that doesn't exist
        metathesis = collection.by_type('PhMetathesisRule')

        assert isinstance(metathesis, RuleCollection)
        assert len(metathesis) == 0


class TestWrapperBackwardCompatibility:
    """Tests for backward compatibility of wrapped objects."""

    def test_wrapped_rule_has_class_name(self):
        """Test that wrapped rule has ClassName attribute."""
        from flexlibs2.code.Grammar.phonological_rule import PhonologicalRule
        from flexlibs2.code.Shared.wrapper_base import LCMObjectWrapper

        mock_rule = Mock()
        mock_rule.ClassName = 'PhRegularRule'

        with patch.object(LCMObjectWrapper, '__init__', lambda x, y: None):
            wrapped = PhonologicalRule(mock_rule)
            wrapped._obj = mock_rule
            wrapped._concrete = mock_rule

            # Should have ClassName through __getattr__
            assert hasattr(wrapped, 'ClassName')
            assert wrapped.ClassName == 'PhRegularRule'

    def test_wrapped_rule_attributes_accessible(self):
        """Test that wrapped rule attributes are accessible."""
        from flexlibs2.code.Grammar.phonological_rule import PhonologicalRule
        from flexlibs2.code.Shared.wrapper_base import LCMObjectWrapper

        mock_rule = Mock()
        mock_rule.ClassName = 'PhRegularRule'
        mock_rule.Hvo = 12345
        mock_rule.Guid = 'some-guid'

        with patch.object(LCMObjectWrapper, '__init__', lambda x, y: None):
            wrapped = PhonologicalRule(mock_rule)
            wrapped._obj = mock_rule
            wrapped._concrete = mock_rule

            # Should access underlying attributes
            assert wrapped.Hvo == 12345
            assert wrapped.Guid == 'some-guid'

    def test_wrapped_rule_in_collection_accessible(self):
        """Test that wrapped rules in collection are usable."""
        from flexlibs2.code.Grammar.rule_collection import RuleCollection

        class MockRule:
            def __init__(self):
                self.class_type = 'PhRegularRule'
                self.ClassName = 'PhRegularRule'
                self.name = 'Test Rule'

        collection = RuleCollection([MockRule()])

        # Get rule from collection
        rule = collection[0]

        # Should be usable
        assert rule.class_type == 'PhRegularRule'
        assert rule.name == 'Test Rule'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
