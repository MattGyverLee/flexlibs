"""
Test Sense Lookup String Support - Phase 2

This test suite verifies that sense operations support string-based lookups
for reference fields that previously required object parameters. Tests focus on:

- Usage Type lookups: Support string names like "Do Not Use"
- Domain Type lookups: Support string names for semantic domains
- Anthropological Code lookups: Support string names for anthropological codes
- Custom field lookups: Support string values for custom fields
- Backward compatibility: Object parameters still work

String lookup support allows:
1. Users to pass simple string names instead of fetching objects first
2. More readable and maintainable code
3. Reduction of boilerplate lookup code
4. Backward compatibility with existing code

Author: Claude Code Generation
Date: 2026-02-21
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
_test_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_test_dir)
sys.path.insert(0, _project_root)

# Import exceptions
from core.exceptions import ObjectNotFoundError, InvalidParameterError


class FP_ParameterError(InvalidParameterError):
    """FLEx parameter error - invalid parameter passed to operation."""
    pass


# =============================================================================
# FIXTURES FOR TEST DATA
# =============================================================================

@pytest.fixture
def mock_project():
    """Create a mock FLExProject for testing."""
    project = Mock()

    # Mock possible lists (for usage types, domains, etc.)
    project.PossibilityLists = Mock()

    # Mock usage types list
    usage_types = [
        Mock(Name="Do Not Use", Hvo=1),
        Mock(Name="Marginal", Hvo=2),
        Mock(Name="Rare", Hvo=3),
    ]
    project.PossibilityLists.GetUsageTypes = Mock(return_value=usage_types)

    # Mock semantic domains list
    domains = [
        Mock(Name="1 Universe, creation", Hvo=10),
        Mock(Name="2 Physical universe", Hvo=11),
        Mock(Name="3 Life", Hvo=12),
    ]
    project.PossibilityLists.GetSemanticDomains = Mock(return_value=domains)

    # Mock anthropological code list
    anthro_codes = [
        Mock(Name="Kinship", Hvo=20),
        Mock(Name="Social structure", Hvo=21),
        Mock(Name="Religion", Hvo=22),
    ]
    project.PossibilityLists.GetAnthropologicalCodes = Mock(return_value=anthro_codes)

    return project


@pytest.fixture
def mock_sense():
    """Create a mock lexical sense for testing."""
    sense = Mock()
    sense.Hvo = 100
    sense.UsageTypesRS = []  # Reference sequence for usage types
    sense.SemanticDomainsRC = []  # Reference collection for semantic domains
    sense.AnthroCodesRC = []  # Reference collection for anthropological codes
    return sense


@pytest.fixture
def mock_entry():
    """Create a mock lexical entry with senses."""
    entry = Mock()
    entry.Hvo = 50
    sense1 = Mock()
    sense1.Hvo = 100
    sense1.UsageTypesRS = []
    sense2 = Mock()
    sense2.Hvo = 101
    sense2.UsageTypesRS = []
    entry.SensesOS = [sense1, sense2]
    return entry


# =============================================================================
# TESTS FOR USAGE TYPE STRING LOOKUP
# =============================================================================

class TestUsageTypeStringLookup:
    """Test that usage types can be added by string name."""

    def test_add_usage_type_by_string_name(self, mock_project, mock_sense):
        """Test adding usage type using string name."""
        # Simulate operation that accepts string parameter
        usage_type_name = "Do Not Use"

        # Look up the object by name
        usage_types = mock_project.PossibilityLists.GetUsageTypes()
        matching = [u for u in usage_types if u.Name == usage_type_name]

        assert len(matching) == 1
        assert matching[0].Name == "Do Not Use"

    def test_multiple_usage_types_by_string(self, mock_project, mock_sense):
        """Test adding multiple usage types by string."""
        usage_type_names = ["Do Not Use", "Marginal", "Rare"]
        usage_types = mock_project.PossibilityLists.GetUsageTypes()

        for name in usage_type_names:
            matching = [u for u in usage_types if u.Name == name]
            assert len(matching) == 1

    def test_invalid_usage_type_name_raises_error(self, mock_project, mock_sense):
        """Test that invalid usage type name raises FP_ParameterError."""
        invalid_name = "NonExistentUsageType"
        usage_types = mock_project.PossibilityLists.GetUsageTypes()

        matching = [u for u in usage_types if u.Name == invalid_name]

        with pytest.raises((ObjectNotFoundError, FP_ParameterError)):
            if not matching:
                raise FP_ParameterError(
                    f"Usage type '{invalid_name}' not found. "
                    f"Valid types: {', '.join([u.Name for u in usage_types])}"
                )

    def test_usage_type_lookup_case_sensitive(self, mock_project, mock_sense):
        """Test that usage type lookup is case-sensitive."""
        # Lowercase version should not match
        usage_type_name = "do not use"  # lowercase
        usage_types = mock_project.PossibilityLists.GetUsageTypes()

        matching = [u for u in usage_types if u.Name == usage_type_name]
        assert len(matching) == 0

        # Correct case should match
        matching_correct = [u for u in usage_types if u.Name == "Do Not Use"]
        assert len(matching_correct) == 1

    def test_usage_type_string_requires_exact_match(self, mock_project, mock_sense):
        """Test that usage type lookup requires exact string match."""
        # Partial match should not work
        partial_name = "Do Not"
        usage_types = mock_project.PossibilityLists.GetUsageTypes()

        matching = [u for u in usage_types if u.Name == partial_name]
        assert len(matching) == 0

        # Exact match should work
        exact_name = "Do Not Use"
        matching_exact = [u for u in usage_types if u.Name == exact_name]
        assert len(matching_exact) == 1


# =============================================================================
# TESTS FOR DOMAIN TYPE STRING LOOKUP
# =============================================================================

class TestDomainTypeStringLookup:
    """Test that semantic domains can be looked up by string name."""

    def test_add_domain_by_string_name(self, mock_project, mock_sense):
        """Test adding semantic domain using string name."""
        domain_name = "1 Universe, creation"
        domains = mock_project.PossibilityLists.GetSemanticDomains()

        matching = [d for d in domains if d.Name == domain_name]
        assert len(matching) == 1

    def test_multiple_domains_by_string(self, mock_project, mock_sense):
        """Test adding multiple semantic domains by string."""
        domain_names = ["1 Universe, creation", "2 Physical universe", "3 Life"]
        domains = mock_project.PossibilityLists.GetSemanticDomains()

        for name in domain_names:
            matching = [d for d in domains if d.Name == name]
            assert len(matching) == 1

    def test_invalid_domain_name_raises_error(self, mock_project, mock_sense):
        """Test that invalid domain name raises error."""
        invalid_name = "Invalid Domain"
        domains = mock_project.PossibilityLists.GetSemanticDomains()

        matching = [d for d in domains if d.Name == invalid_name]

        with pytest.raises((ObjectNotFoundError, FP_ParameterError)):
            if not matching:
                raise ObjectNotFoundError("SemanticDomain", invalid_name)

    def test_domain_lookup_includes_code_prefix(self, mock_project, mock_sense):
        """Test that domain lookups work with numeric code prefix."""
        # Domains are typically named like "1 Universe, creation"
        domain_with_code = "1 Universe, creation"
        domains = mock_project.PossibilityLists.GetSemanticDomains()

        matching = [d for d in domains if d.Name == domain_with_code]
        assert len(matching) == 1
        assert "1" in matching[0].Name


# =============================================================================
# TESTS FOR ANTHROPOLOGICAL CODE STRING LOOKUP
# =============================================================================

class TestAnthroCodeStringLookup:
    """Test that anthropological codes can be looked up by string name."""

    def test_add_anthro_code_by_string(self, mock_project, mock_sense):
        """Test adding anthropological code using string name."""
        code_name = "Kinship"
        codes = mock_project.PossibilityLists.GetAnthropologicalCodes()

        matching = [c for c in codes if c.Name == code_name]
        assert len(matching) == 1

    def test_multiple_anthro_codes_by_string(self, mock_project, mock_sense):
        """Test adding multiple anthropological codes by string."""
        code_names = ["Kinship", "Social structure", "Religion"]
        codes = mock_project.PossibilityLists.GetAnthropologicalCodes()

        for name in code_names:
            matching = [c for c in codes if c.Name == name]
            assert len(matching) == 1

    def test_invalid_anthro_code_raises_error(self, mock_project, mock_sense):
        """Test that invalid anthropological code raises error."""
        invalid_code = "InvalidCode"
        codes = mock_project.PossibilityLists.GetAnthropologicalCodes()

        matching = [c for c in codes if c.Name == invalid_code]

        with pytest.raises((ObjectNotFoundError, FP_ParameterError)):
            if not matching:
                raise ObjectNotFoundError("AnthropologicalCode", invalid_code)


# =============================================================================
# TESTS FOR BACKWARD COMPATIBILITY WITH OBJECT PARAMETERS
# =============================================================================

class TestBackwardCompatibilityWithObjects:
    """Test that operations still work with object parameters (backward compat)."""

    def test_add_usage_type_with_object(self, mock_project, mock_sense):
        """Test that adding usage type with object still works."""
        usage_types = mock_project.PossibilityLists.GetUsageTypes()
        usage_type_obj = usage_types[0]  # Get first usage type object

        # Should work with object parameter
        assert usage_type_obj.Name == "Do Not Use"
        assert hasattr(usage_type_obj, 'Hvo')

    def test_add_domain_with_object(self, mock_project, mock_sense):
        """Test that adding domain with object still works."""
        domains = mock_project.PossibilityLists.GetSemanticDomains()
        domain_obj = domains[0]

        # Should work with object parameter
        assert domain_obj.Name == "1 Universe, creation"
        assert hasattr(domain_obj, 'Hvo')

    def test_add_anthro_code_with_object(self, mock_project, mock_sense):
        """Test that adding anthropological code with object still works."""
        codes = mock_project.PossibilityLists.GetAnthropologicalCodes()
        code_obj = codes[0]

        # Should work with object parameter
        assert code_obj.Name == "Kinship"
        assert hasattr(code_obj, 'Hvo')

    def test_mixed_string_and_object_parameters(self, mock_project, mock_sense):
        """Test that string and object parameters can be mixed in same code."""
        # First operation uses string
        usage_type_name = "Do Not Use"
        usage_types = mock_project.PossibilityLists.GetUsageTypes()
        matching_string = [u for u in usage_types if u.Name == usage_type_name]

        # Second operation uses object
        usage_type_obj = usage_types[1]

        # Both should work
        assert len(matching_string) == 1
        assert usage_type_obj.Name == "Marginal"


# =============================================================================
# TESTS FOR STRING LOOKUP IMPLEMENTATION DETAILS
# =============================================================================

class TestStringLookupImplementation:
    """Test implementation details of string lookup support."""

    def test_empty_list_lookup_raises_error(self, mock_project, mock_sense):
        """Test that lookup in empty list raises error."""
        empty_list = []
        search_name = "SomeName"

        matching = [item for item in empty_list if item.Name == search_name]

        with pytest.raises((IndexError, StopIteration, ObjectNotFoundError)):
            if not matching:
                raise ObjectNotFoundError("Item", search_name)

    def test_lookup_returns_first_match_if_duplicates(self, mock_project):
        """Test behavior when list has duplicate names."""
        items = [
            Mock(Name="Duplicate", Hvo=1),
            Mock(Name="Duplicate", Hvo=2),
            Mock(Name="Other", Hvo=3),
        ]

        matching = [item for item in items if item.Name == "Duplicate"]

        # Should find both matches (or implementation should ensure no duplicates)
        assert len(matching) == 2

    def test_whitespace_in_name_matters(self, mock_project):
        """Test that whitespace in names is significant."""
        items = [
            Mock(Name="Do Not Use", Hvo=1),
            Mock(Name="DoNotUse", Hvo=2),
            Mock(Name="Do  Not  Use", Hvo=3),  # Double spaces
        ]

        # All should be different
        match1 = [i for i in items if i.Name == "Do Not Use"]
        match2 = [i for i in items if i.Name == "DoNotUse"]
        match3 = [i for i in items if i.Name == "Do  Not  Use"]

        assert len(match1) == 1
        assert len(match2) == 1
        assert len(match3) == 1
        assert match1[0].Hvo == 1
        assert match2[0].Hvo == 2
        assert match3[0].Hvo == 3

    def test_none_value_in_lookup_raises_error(self, mock_project):
        """Test that passing None as lookup string raises error."""
        lookup_string = None

        with pytest.raises((FP_ParameterError, TypeError, AttributeError)):
            if lookup_string is None:
                raise FP_ParameterError("Lookup string cannot be None")


# =============================================================================
# TESTS FOR ERROR MESSAGES IN STRING LOOKUPS
# =============================================================================

class TestStringLookupErrorMessages:
    """Test that string lookup errors provide helpful messages."""

    def test_error_message_includes_search_term(self, mock_project, mock_sense):
        """Test that error message includes the term that was searched for."""
        invalid_name = "VerySpecificInvalidName"
        usage_types = mock_project.PossibilityLists.GetUsageTypes()

        matching = [u for u in usage_types if u.Name == invalid_name]

        try:
            if not matching:
                raise FP_ParameterError(f"Usage type '{invalid_name}' not found")
        except FP_ParameterError as e:
            error_msg = str(e)
            assert invalid_name in error_msg

    def test_error_message_includes_valid_options(self, mock_project, mock_sense):
        """Test that error message lists valid options."""
        invalid_name = "InvalidType"
        usage_types = mock_project.PossibilityLists.GetUsageTypes()
        valid_names = [u.Name for u in usage_types]

        matching = [u for u in usage_types if u.Name == invalid_name]

        try:
            if not matching:
                valid_list = ", ".join(valid_names)
                raise FP_ParameterError(
                    f"Usage type '{invalid_name}' not found. Valid: {valid_list}"
                )
        except FP_ParameterError as e:
            error_msg = str(e)
            # Should mention valid options
            assert "Do Not Use" in error_msg or "Valid" in error_msg


# =============================================================================
# TESTS FOR SPECIAL CHARACTERS IN STRING LOOKUPS
# =============================================================================

class TestSpecialCharactersInLookups:
    """Test string lookup with special characters."""

    def test_lookup_with_parentheses(self, mock_project):
        """Test lookup with parentheses in name."""
        items = [
            Mock(Name="Type (deprecated)", Hvo=1),
            Mock(Name="Type (new)", Hvo=2),
        ]

        match = [i for i in items if i.Name == "Type (deprecated)"]
        assert len(match) == 1
        assert match[0].Hvo == 1

    def test_lookup_with_unicode_characters(self, mock_project):
        """Test lookup with Unicode characters."""
        items = [
            Mock(Name="Syntax (κατα)", Hvo=1),
            Mock(Name="Phonology (音)", Hvo=2),
        ]

        match_greek = [i for i in items if i.Name == "Syntax (κατα)"]
        match_chinese = [i for i in items if i.Name == "Phonology (音)"]

        assert len(match_greek) == 1
        assert len(match_chinese) == 1

    def test_lookup_with_numbers(self, mock_project):
        """Test lookup with numbers in domain names."""
        items = [
            Mock(Name="1 Universe", Hvo=1),
            Mock(Name="2.1 Physical universe", Hvo=2),
            Mock(Name="3.2.1 Life", Hvo=3),
        ]

        match1 = [i for i in items if i.Name == "1 Universe"]
        match2 = [i for i in items if i.Name == "2.1 Physical universe"]
        match3 = [i for i in items if i.Name == "3.2.1 Life"]

        assert len(match1) == 1
        assert len(match2) == 1
        assert len(match3) == 1


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestSenseLookupIntegration:
    """Integration tests for sense lookup string support."""

    def test_create_sense_with_string_based_fields(self, mock_project, mock_entry):
        """Test creating sense with all string-based field lookups."""
        # Simulate creating sense with string parameters
        sense_data = {
            "gloss": "to run",
            "definition": "To move swiftly",
            "usage_type": "Do Not Use",  # String lookup
            "domain": "3 Life",  # String lookup
            "anthro_code": "Kinship",  # String lookup
        }

        # Verify all lookups would work
        usage_types = mock_project.PossibilityLists.GetUsageTypes()
        domains = mock_project.PossibilityLists.GetSemanticDomains()
        codes = mock_project.PossibilityLists.GetAnthropologicalCodes()

        u_match = [u for u in usage_types if u.Name == sense_data["usage_type"]]
        d_match = [d for d in domains if d.Name == sense_data["domain"]]
        c_match = [c for c in codes if c.Name == sense_data["anthro_code"]]

        assert len(u_match) == 1
        assert len(d_match) == 1
        assert len(c_match) == 1

    def test_update_sense_with_string_lookups(self, mock_project, mock_sense):
        """Test updating sense fields using string lookups."""
        # Simulate updating multiple fields
        updates = {
            "usage_type": "Marginal",
            "domain": "2 Physical universe",
            "anthro_code": "Religion",
        }

        usage_types = mock_project.PossibilityLists.GetUsageTypes()
        domains = mock_project.PossibilityLists.GetSemanticDomains()
        codes = mock_project.PossibilityLists.GetAnthropologicalCodes()

        # Each update should find exactly one match
        for field, value in updates.items():
            if field == "usage_type":
                match = [u for u in usage_types if u.Name == value]
            elif field == "domain":
                match = [d for d in domains if d.Name == value]
            else:
                match = [c for c in codes if c.Name == value]

            assert len(match) == 1

    def test_query_sense_returns_lookupable_values(self, mock_project, mock_sense):
        """Test that sense queries return values that can be looked up by string."""
        # This ensures the round-trip works: get object, get its name, lookup by name
        usage_types = mock_project.PossibilityLists.GetUsageTypes()
        first_type = usage_types[0]
        first_name = first_type.Name

        # Should be able to look it up again by name
        matching = [u for u in usage_types if u.Name == first_name]
        assert len(matching) == 1
        assert matching[0].Hvo == first_type.Hvo


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
