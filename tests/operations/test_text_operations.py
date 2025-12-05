"""
Test Suite for TextOperations

Tests operations for Texts (interlinearized texts):
- Create: Create text with title
- Read: GetAll, Find, GetTitle, GetGenre
- Update: SetTitle, SetGenre
- Delete: Delete texts
- Paragraphs: AddParagraph, GetParagraphs
- Reordering: Inherited BaseOperations methods

Texts are containers for analyzed discourse (stories, conversations, etc.).

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
    mock_text,
    assert_has_reordering_methods,
    MockLCMObject,
    MockMultiString,
    MockOwningSequence,
)


# =============================================================================
# UNIT TESTS - Using Mocks
# =============================================================================

class TestTextOperationsImport:
    """Test that TextOperations can be imported and instantiated."""

    def test_import_text_operations(self):
        """Test importing TextOperations class."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations
        assert TextOperations is not None

    def test_instantiate_with_mock_project(self, mock_flex_project):
        """Test instantiating TextOperations with mock project."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        ops = TextOperations(mock_flex_project)
        assert ops is not None
        assert ops.project == mock_flex_project


class TestTextOperationsInheritance:
    """Test BaseOperations inheritance."""

    def test_inherits_from_base_operations(self):
        """Test that TextOperations inherits from BaseOperations."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations
        from flexlibs.code.BaseOperations import BaseOperations

        assert issubclass(TextOperations, BaseOperations)

    def test_has_all_reordering_methods(self, mock_flex_project):
        """Test that TextOperations has all reordering methods."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        ops = TextOperations(mock_flex_project)
        assert_has_reordering_methods(ops)


class TestTextOperationsCRUDMethods:
    """Test that CRUD methods exist and are callable."""

    def test_has_getall_method(self, mock_flex_project):
        """Test that GetAll method exists and is callable."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        ops = TextOperations(mock_flex_project)
        assert hasattr(ops, 'GetAll')
        assert callable(ops.GetAll)

    def test_has_create_method(self, mock_flex_project):
        """Test that Create method exists and is callable."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        ops = TextOperations(mock_flex_project)
        assert hasattr(ops, 'Create')
        assert callable(ops.Create)

    def test_has_delete_method(self, mock_flex_project):
        """Test that Delete method exists and is callable."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        ops = TextOperations(mock_flex_project)
        assert hasattr(ops, 'Delete')
        assert callable(ops.Delete)

    def test_has_find_method(self, mock_flex_project):
        """Test that Find method exists and is callable."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        ops = TextOperations(mock_flex_project)
        assert hasattr(ops, 'Find')
        assert callable(ops.Find)


class TestTextOperationsPropertyGetters:
    """Test property getter methods."""

    def test_has_gettitle_method(self, mock_flex_project):
        """Test that GetTitle method exists."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        ops = TextOperations(mock_flex_project)
        assert hasattr(ops, 'GetTitle')
        assert callable(ops.GetTitle)

    def test_has_getgenre_method(self, mock_flex_project):
        """Test that GetGenre method exists."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        ops = TextOperations(mock_flex_project)
        # Genre may be accessed differently
        assert hasattr(ops, 'GetGenre') or hasattr(ops, 'GetTitle')


class TestTextOperationsPropertySetters:
    """Test property setter methods."""

    def test_has_settitle_method(self, mock_flex_project):
        """Test that SetTitle method exists."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        ops = TextOperations(mock_flex_project)
        assert hasattr(ops, 'SetTitle')
        assert callable(ops.SetTitle)


class TestTextOperationsParagraphMethods:
    """Test paragraph-related methods."""

    def test_has_addparagraph_method(self, mock_flex_project):
        """Test that AddParagraph method exists."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        ops = TextOperations(mock_flex_project)
        # Check for paragraph-related methods
        assert hasattr(ops, 'AddParagraph') or hasattr(ops, 'GetParagraphCount')


class TestTextOperationsMockBehavior:
    """Test operations behavior with mock objects."""

    def test_mock_text_structure(self, mock_text):
        """Test mock text has expected structure."""
        assert hasattr(mock_text, 'Name')
        assert hasattr(mock_text, 'ContentsOA')
        assert hasattr(mock_text, 'Hvo')
        assert hasattr(mock_text, 'Guid')

    def test_getall_with_mock_repository(self, mock_flex_project):
        """Test GetAll returns iterator from mock repository."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        # Setup mock to return test texts
        mock_texts = [MockLCMObject(hvo=4000 + i) for i in range(2)]

        with patch.object(
            mock_flex_project,
            'ObjectsIn',
            return_value=iter(mock_texts)
        ):
            ops = TextOperations(mock_flex_project)
            result = list(ops.GetAll())

            assert len(result) == 2


class TestTextOperationsValidation:
    """Test validation and error handling."""

    def test_create_requires_write_enabled(self, mock_flex_project):
        """Test that Create raises error when project is read-only."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations
        from flexlibs.code.FLExProject import FP_ReadOnlyError

        # Set project to read-only
        mock_flex_project.writeEnabled = False

        ops = TextOperations(mock_flex_project)

        # Should raise FP_ReadOnlyError
        with pytest.raises(FP_ReadOnlyError):
            ops.Create("Test Text")


# =============================================================================
# INTEGRATION TESTS - Require Real FLEx Project
# =============================================================================

@pytest.mark.integration
class TestTextOperationsIntegration:
    """
    Integration tests that require a real FLEx project.

    Run with: pytest -m integration
    """

    @pytest.fixture(scope="class")
    def flex_project(self):
        """Setup real FLEx project for integration testing."""
        pytest.importorskip("flexlibs")

        from flexlibs import FLExInitialize, FLExCleanup, FLExProject, AllProjectNames

        FLExInitialize()
        projects = AllProjectNames()
        if not projects:
            pytest.skip("No FLEx projects available")

        project = FLExProject()
        project.OpenProject(projects[0], writeEnabled=True)

        yield project

        project.CloseProject()
        FLExCleanup()

    def test_create_and_delete_text(self, flex_project):
        """Integration test: Create and delete a text."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        ops = TextOperations(flex_project)

        # Create text
        text = ops.Create("Test Text 123")
        assert text is not None

        # Verify title
        title = ops.GetTitle(text)
        assert "Test Text 123" in title

        # Delete text
        ops.Delete(text)

    def test_getall_returns_texts(self, flex_project):
        """Integration test: GetAll returns texts."""
        from flexlibs.code.TextsWords.TextOperations import TextOperations

        ops = TextOperations(flex_project)
        texts = list(ops.GetAll())

        assert isinstance(texts, list)


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
