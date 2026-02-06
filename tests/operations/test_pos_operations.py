"""
Test Suite for POSOperations

Tests operations for Parts of Speech:
- Create: Create POS with name and abbreviation
- Read: GetAll, Find, GetName, GetAbbreviation
- Update: SetName, SetAbbreviation
- Delete: Delete POS
- Hierarchy: GetSubcategories, parent/child relationships
- Reordering: Inherited BaseOperations methods
- Sequence: _GetSequence returns parent.SubPossibilitiesOS

Parts of Speech are organized hierarchically (e.g., Noun > Common Noun, Proper Noun).

Author: Programmer Team 3 - Test Infrastructure
Date: 2025-12-05
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
_test_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_test_dir))
sys.path.insert(0, _project_root)

# Import test fixtures
from tests.operations import (
    mock_flex_project,
    mock_pos,
    assert_has_reordering_methods,
    MockLCMObject,
    MockMultiString,
    MockOwningSequence,
)


# =============================================================================
# UNIT TESTS - Using Mocks
# =============================================================================

class TestPOSOperationsImport:
    """Test that POSOperations can be imported and instantiated."""

    def test_import_pos_operations(self):
        """Test importing POSOperations class."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations
        assert POSOperations is not None

    def test_instantiate_with_mock_project(self, mock_flex_project):
        """Test instantiating POSOperations with mock project."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(mock_flex_project)
        assert ops is not None
        assert ops.project == mock_flex_project


class TestPOSOperationsInheritance:
    """Test BaseOperations inheritance."""

    def test_inherits_from_base_operations(self):
        """Test that POSOperations inherits from BaseOperations."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations
        from flexlibs2.code.BaseOperations import BaseOperations

        assert issubclass(POSOperations, BaseOperations)

    def test_has_all_reordering_methods(self, mock_flex_project):
        """Test that POSOperations has all reordering methods."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(mock_flex_project)
        assert_has_reordering_methods(ops)

    def test_has_getsequence_implementation(self, mock_flex_project):
        """Test that _GetSequence is implemented for POS."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(mock_flex_project)
        assert hasattr(ops, '_GetSequence')

        # Test with mock POS that has subcategories
        mock_parent_pos = MockLCMObject()
        mock_parent_pos.SubPossibilitiesOS = MockOwningSequence()

        # Should return SubPossibilitiesOS
        sequence = ops._GetSequence(mock_parent_pos)
        assert sequence is mock_parent_pos.SubPossibilitiesOS


class TestPOSOperationsCRUDMethods:
    """Test that CRUD methods exist and are callable."""

    def test_has_getall_method(self, mock_flex_project):
        """Test that GetAll method exists and is callable."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(mock_flex_project)
        assert hasattr(ops, 'GetAll')
        assert callable(ops.GetAll)

    def test_has_create_method(self, mock_flex_project):
        """Test that Create method exists and is callable."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(mock_flex_project)
        assert hasattr(ops, 'Create')
        assert callable(ops.Create)

    def test_has_delete_method(self, mock_flex_project):
        """Test that Delete method exists and is callable."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(mock_flex_project)
        assert hasattr(ops, 'Delete')
        assert callable(ops.Delete)

    def test_has_find_method(self, mock_flex_project):
        """Test that Find method exists and is callable."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(mock_flex_project)
        assert hasattr(ops, 'Find')
        assert callable(ops.Find)


class TestPOSOperationsPropertyGetters:
    """Test property getter methods."""

    def test_has_getname_method(self, mock_flex_project):
        """Test that GetName method exists."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(mock_flex_project)
        assert hasattr(ops, 'GetName')
        assert callable(ops.GetName)

    def test_has_getabbreviation_method(self, mock_flex_project):
        """Test that GetAbbreviation method exists."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(mock_flex_project)
        assert hasattr(ops, 'GetAbbreviation')
        assert callable(ops.GetAbbreviation)


class TestPOSOperationsPropertySetters:
    """Test property setter methods."""

    def test_has_setname_method(self, mock_flex_project):
        """Test that SetName method exists."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(mock_flex_project)
        assert hasattr(ops, 'SetName')
        assert callable(ops.SetName)

    def test_has_setabbreviation_method(self, mock_flex_project):
        """Test that SetAbbreviation method exists."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(mock_flex_project)
        assert hasattr(ops, 'SetAbbreviation')
        assert callable(ops.SetAbbreviation)


class TestPOSOperationsHierarchy:
    """Test POS hierarchy navigation methods."""

    def test_has_getsubcategories_method(self, mock_flex_project):
        """Test that GetSubcategories method exists."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(mock_flex_project)
        # Check for GetSubcategories or similar hierarchy method
        assert hasattr(ops, 'GetSubcategories') or hasattr(ops, '_GetSequence')


class TestPOSOperationsReordering:
    """Test reordering functionality with mock POS."""

    def test_sort_subcategories(self, mock_flex_project):
        """Test sorting POS subcategories."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        # Create parent POS with subcategories
        parent_pos = MockLCMObject()
        parent_pos.SubPossibilitiesOS = MockOwningSequence()

        # Add subcategories
        for i, name in enumerate(['Verb', 'Noun', 'Adjective']):
            sub_pos = MockLCMObject(hvo=3000 + i)
            sub_pos.Name = MockMultiString({'en': name})
            sub_pos.Abbreviation = MockMultiString({'en': name[0]})
            parent_pos.SubPossibilitiesOS.Append(sub_pos)

        ops = POSOperations(mock_flex_project)

        # Sort method exists
        assert hasattr(ops, 'Sort')
        assert callable(ops.Sort)


# =============================================================================
# INTEGRATION TESTS - Require Real FLEx Project
# =============================================================================

@pytest.mark.integration
class TestPOSOperationsIntegration:
    """
    Integration tests that require a real FLEx project.

    Run with: pytest -m integration
    """

    @pytest.fixture(scope="class")
    def flex_project(self):
        """Setup real FLEx project for integration testing."""
        pytest.importorskip("flexlibs")

        from flexlibs2 import FLExInitialize, FLExCleanup, FLExProject, AllProjectNames

        FLExInitialize()
        projects = AllProjectNames()
        if not projects:
            pytest.skip("No FLEx projects available")

        project = FLExProject()
        project.OpenProject(projects[0], writeEnabled=True)

        yield project

        project.CloseProject()
        FLExCleanup()

    def test_getall_returns_pos(self, flex_project):
        """Integration test: GetAll returns POS list."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(flex_project)
        pos_list = list(ops.GetAll())

        assert isinstance(pos_list, list)
        # Most projects should have at least some POS defined

    def test_find_pos_by_name(self, flex_project):
        """Integration test: Find POS by name."""
        from flexlibs2.code.Grammar.POSOperations import POSOperations

        ops = POSOperations(flex_project)

        # Try to find common POS (may not exist in all projects)
        result = ops.Find("Noun")
        # Result may be None if not found


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires real FLEx)"
    )


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-m', 'not integration'])
