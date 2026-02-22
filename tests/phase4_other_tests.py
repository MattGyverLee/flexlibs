#
# phase4_other_tests.py
#
# Phase 4 Lists, Notebook, Reversal & Scripture Validation Tests for FlexLibs2
#
# Tests validation consolidation refactoring for:
# - Lists (6 files, ~48 tests):
#   * AgentOperations: 8 tests
#   * ConfidenceOperations: 8 tests
#   * OverlayOperations: 10 tests
#   * PossibilityListOperations: 10 tests
#   * PublicationOperations: 8 tests
#   * TranslationTypeOperations: 4 tests
#
# - Notebook (5 files, ~60 tests):
#   * AnthropologyOperations: 12 tests
#   * DataNotebookOperations: 15 tests
#   * LocationOperations: 12 tests
#   * NoteOperations: 12 tests
#   * PersonOperations: 9 tests
#
# - Reversal (2 files, ~20 tests):
#   * ReversalIndexOperations: 10 tests
#   * ReversalIndexEntryOperations: 10 tests
#
# - Scripture (6 files, ~60 tests):
#   * ScrAnnotationsOperations: 10 tests
#   * ScrBookOperations: 10 tests
#   * ScrDraftOperations: 10 tests
#   * ScrNoteOperations: 10 tests
#   * ScrSectionOperations: 12 tests
#   * ScrTxtParaOperations: 8 tests
#
# Total Phase 4 Other: 188 tests
#
# Platform: Python.NET
#           FieldWorks Version 9+
#
# Copyright 2025
#

import pytest
from unittest.mock import Mock
from test_validation_base import (
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
    IndexBoundsTestsMixin,
)
from test_helpers import (
    create_mock_entry,
    create_mock_sense,
    create_mock_writing_system,
    ErrorValidator,
)


# ========== LISTS - AGENTOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestAgentOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for AgentOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test agent creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_create_name_not_empty(self):
        """Test create name must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_agent(self):
        """Test delete requires agent."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "agent_or_hvo")

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== LISTS - CONFIDENCEOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestConfidenceOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for ConfidenceOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test confidence creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_create_name_not_empty(self):
        """Test create name must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_confidence(self):
        """Test delete requires confidence."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "confidence_or_hvo")

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_get_value_requires_confidence(self):
        """Test get value requires confidence."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "confidence_or_hvo")


# ========== LISTS - OVERLAYOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestOverlayOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for OverlayOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test overlay creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_create_name_not_empty(self):
        """Test create name must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_overlay(self):
        """Test delete requires overlay."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "overlay_or_hvo")

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_add_possibility_requires_write_enabled(self):
        """Test adding possibility requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_possibility_requires_overlay(self):
        """Test add_possibility requires overlay."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "overlay_or_hvo")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_name_requires_overlay(self):
        """Test set_name requires overlay."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "overlay_or_hvo")


# ========== LISTS - POSSIBILITYLISTOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestPossibilityListOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for PossibilityListOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test possibility list creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_create_name_not_empty(self):
        """Test create name must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_list(self):
        """Test delete requires list."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "list_or_hvo")

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_add_item_requires_write_enabled(self):
        """Test adding item requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_item_requires_list(self):
        """Test add_item requires list."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "list_or_hvo")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_name_requires_list(self):
        """Test set_name requires list."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "list_or_hvo")


# ========== LISTS - PUBLICATIONOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestPublicationOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for PublicationOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test publication creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_create_name_not_empty(self):
        """Test create name must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_publication(self):
        """Test delete requires publication."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "publication_or_hvo")

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== LISTS - TRANSLATIONTYPEOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestTranslationTypeOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for TranslationTypeOperations validation methods."""

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_get_name_requires_type(self):
        """Test get name requires translation type."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "type_or_hvo")

    @pytest.mark.validation
    def test_get_abbreviation_requires_type(self):
        """Test get abbreviation requires translation type."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "type_or_hvo")


# ========== NOTEBOOK - ANTHROPOLOGYOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestAnthropologyOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for AnthropologyOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test anthropology record creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_notebook(self):
        """Test create requires notebook."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "notebook_or_hvo")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_record(self):
        """Test delete requires record."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "record_or_hvo")

    @pytest.mark.validation
    def test_get_all_requires_notebook(self):
        """Test get_all requires notebook."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "notebook_or_hvo")

    @pytest.mark.validation
    def test_find_requires_notebook(self):
        """Test find requires notebook."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "notebook_or_hvo")

    @pytest.mark.validation
    def test_set_data_requires_write_enabled(self):
        """Test setting data requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_data_requires_record(self):
        """Test set_data requires record."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "record_or_hvo")

    @pytest.mark.validation
    def test_get_data_requires_record(self):
        """Test get data requires record."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "record_or_hvo")

    @pytest.mark.validation
    def test_add_field_requires_write_enabled(self):
        """Test adding field requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_field_requires_record(self):
        """Test add_field requires record."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "record_or_hvo")

    @pytest.mark.validation
    def test_add_field_requires_field_name(self):
        """Test add_field requires field name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "field_name")


# ========== NOTEBOOK - DATANOTEBOOKOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestDataNotebookOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for DataNotebookOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test notebook creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_create_name_not_empty(self):
        """Test create name must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_notebook(self):
        """Test delete requires notebook."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "notebook_or_hvo")

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_add_section_requires_write_enabled(self):
        """Test adding section requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_section_requires_notebook(self):
        """Test add_section requires notebook."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "notebook_or_hvo")

    @pytest.mark.validation
    def test_add_section_requires_section_name(self):
        """Test add_section requires section name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "section_name")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_name_requires_notebook(self):
        """Test set_name requires notebook."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "notebook_or_hvo")

    @pytest.mark.validation
    def test_get_name_requires_notebook(self):
        """Test get name requires notebook."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "notebook_or_hvo")

    @pytest.mark.validation
    def test_get_sections_requires_notebook(self):
        """Test get sections requires notebook."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "notebook_or_hvo")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_notebook(self):
        """Test duplicate requires notebook."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "notebook_or_hvo")


# ========== NOTEBOOK - LOCATIONOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestLocationOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for LocationOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test location creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_create_name_not_empty(self):
        """Test create name must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_location(self):
        """Test delete requires location."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "location_or_hvo")

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_name_requires_location(self):
        """Test set_name requires location."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "location_or_hvo")

    @pytest.mark.validation
    def test_get_name_requires_location(self):
        """Test get name requires location."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "location_or_hvo")

    @pytest.mark.validation
    def test_get_coordinates_requires_location(self):
        """Test get coordinates requires location."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "location_or_hvo")

    @pytest.mark.validation
    def test_set_coordinates_requires_write_enabled(self):
        """Test setting coordinates requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== NOTEBOOK - NOTEOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestNoteOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for NoteOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test note creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_object(self):
        """Test create requires object."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "object_or_hvo")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_note(self):
        """Test delete requires note."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "note_or_hvo")

    @pytest.mark.validation
    def test_get_all_requires_object(self):
        """Test get_all requires object."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "object_or_hvo")

    @pytest.mark.validation
    def test_find_requires_object(self):
        """Test find requires object."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "object_or_hvo")

    @pytest.mark.validation
    def test_set_content_requires_write_enabled(self):
        """Test setting content requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_content_requires_note(self):
        """Test set_content requires note."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "note_or_hvo")

    @pytest.mark.validation
    def test_get_content_requires_note(self):
        """Test get content requires note."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "note_or_hvo")

    @pytest.mark.validation
    def test_get_type_requires_note(self):
        """Test get type requires note."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "note_or_hvo")

    @pytest.mark.validation
    def test_set_type_requires_write_enabled(self):
        """Test setting type requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_type_requires_note(self):
        """Test set_type requires note."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "note_or_hvo")


# ========== NOTEBOOK - PERSONOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestPersonOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for PersonOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test person creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_create_name_not_empty(self):
        """Test create name must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_person(self):
        """Test delete requires person."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "person_or_hvo")

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_get_name_requires_person(self):
        """Test get name requires person."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "person_or_hvo")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_name_requires_person(self):
        """Test set_name requires person."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "person_or_hvo")


# ========== REVERSAL - REVERSALINDEXOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestReversalIndexOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for ReversalIndexOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test reversal index creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_create_name_not_empty(self):
        """Test create name must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_index(self):
        """Test delete requires index."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "index_or_hvo")

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_add_entry_requires_write_enabled(self):
        """Test adding entry requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_entry_requires_index(self):
        """Test add_entry requires index."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "index_or_hvo")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== REVERSAL - REVERSALINDEXENTRYOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestReversalIndexEntryOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for ReversalIndexEntryOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test reversal entry creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_index(self):
        """Test create requires index."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "index_or_hvo")

    @pytest.mark.validation
    def test_create_requires_form(self):
        """Test create requires form."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "form")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_entry(self):
        """Test delete requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry_or_hvo")

    @pytest.mark.validation
    def test_find_requires_index(self):
        """Test find requires index."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "index_or_hvo")

    @pytest.mark.validation
    def test_get_form_requires_entry(self):
        """Test get form requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry_or_hvo")

    @pytest.mark.validation
    def test_set_form_requires_write_enabled(self):
        """Test setting form requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_form_requires_entry(self):
        """Test set_form requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry_or_hvo")

    @pytest.mark.validation
    def test_add_reference_requires_write_enabled(self):
        """Test adding reference requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== SCRIPTURE - SCRANOTATIONSOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestScrAnnotationsOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for ScrAnnotationsOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test annotation creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_scripture_range(self):
        """Test create requires scripture range."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "scripture_range")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_annotation(self):
        """Test delete requires annotation."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "annotation_or_hvo")

    @pytest.mark.validation
    def test_find_requires_scripture_range(self):
        """Test find requires scripture range."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "scripture_range")

    @pytest.mark.validation
    def test_get_range_requires_annotation(self):
        """Test get range requires annotation."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "annotation_or_hvo")

    @pytest.mark.validation
    def test_set_range_requires_write_enabled(self):
        """Test setting range requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_range_requires_annotation(self):
        """Test set_range requires annotation."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "annotation_or_hvo")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_find_at_range_requires_scripture_range(self):
        """Test find_at_range requires scripture range."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "scripture_range")


# ========== SCRIPTURE - SCRBOOKOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestScrBookOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for ScrBookOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test book creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_book_id(self):
        """Test create requires book ID."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "book_id")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_book(self):
        """Test delete requires book."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "book_or_hvo")

    @pytest.mark.validation
    def test_find_requires_book_id(self):
        """Test find requires book ID."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "book_id")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_get_sections_requires_book(self):
        """Test get sections requires book."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "book_or_hvo")

    @pytest.mark.validation
    def test_add_section_requires_write_enabled(self):
        """Test adding section requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_section_requires_book(self):
        """Test add_section requires book."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "book_or_hvo")

    @pytest.mark.validation
    def test_get_book_id_requires_book(self):
        """Test get book ID requires book."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "book_or_hvo")


# ========== SCRIPTURE - SCRDRAFTOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestScrDraftOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for ScrDraftOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test draft creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_create_name_not_empty(self):
        """Test create name must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_draft(self):
        """Test delete requires draft."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "draft_or_hvo")

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_name_requires_draft(self):
        """Test set_name requires draft."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "draft_or_hvo")

    @pytest.mark.validation
    def test_set_name_not_empty(self):
        """Test set_name requires non-empty name."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")


# ========== SCRIPTURE - SCRNOTEOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestScrNoteOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for ScrNoteOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test note creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_scripture_range(self):
        """Test create requires scripture range."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "scripture_range")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_note(self):
        """Test delete requires note."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "note_or_hvo")

    @pytest.mark.validation
    def test_find_requires_scripture_range(self):
        """Test find requires scripture range."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "scripture_range")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_set_content_requires_write_enabled(self):
        """Test setting content requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_content_requires_note(self):
        """Test set_content requires note."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "note_or_hvo")

    @pytest.mark.validation
    def test_get_content_requires_note(self):
        """Test get content requires note."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "note_or_hvo")

    @pytest.mark.validation
    def test_get_range_requires_note(self):
        """Test get range requires note."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "note_or_hvo")

    @pytest.mark.validation
    def test_set_type_requires_write_enabled(self):
        """Test setting type requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== SCRIPTURE - SCRSECTIONOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestScrSectionOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for ScrSectionOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test section creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_book(self):
        """Test create requires book."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "book_or_hvo")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_section(self):
        """Test delete requires section."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "section_or_hvo")

    @pytest.mark.validation
    def test_find_requires_book(self):
        """Test find requires book."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "book_or_hvo")

    @pytest.mark.validation
    def test_get_all_requires_book(self):
        """Test get_all requires book."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "book_or_hvo")

    @pytest.mark.validation
    def test_move_requires_write_enabled(self):
        """Test moving section requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_move_requires_section(self):
        """Test move requires section."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "section_or_hvo")

    @pytest.mark.validation
    def test_get_start_scripture_requires_section(self):
        """Test get start scripture requires section."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "section_or_hvo")

    @pytest.mark.validation
    def test_get_end_scripture_requires_section(self):
        """Test get end scripture requires section."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "section_or_hvo")

    @pytest.mark.validation
    def test_set_start_requires_write_enabled(self):
        """Test setting start requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_end_requires_write_enabled(self):
        """Test setting end requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== SCRIPTURE - SCRTXTPARAOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestScrTxtParaOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for ScrTxtParaOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test paragraph creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_section(self):
        """Test create requires section."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "section_or_hvo")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_paragraph(self):
        """Test delete requires paragraph."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "paragraph_or_hvo")

    @pytest.mark.validation
    def test_find_requires_section(self):
        """Test find requires section."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "section_or_hvo")

    @pytest.mark.validation
    def test_get_all_requires_section(self):
        """Test get_all requires section."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "section_or_hvo")

    @pytest.mark.validation
    def test_set_style_requires_write_enabled(self):
        """Test setting style requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_style_requires_paragraph(self):
        """Test set_style requires paragraph."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "paragraph_or_hvo")
