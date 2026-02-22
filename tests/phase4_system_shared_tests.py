#
# phase4_system_shared_tests.py
#
# Phase 4 System & Shared Validation Tests for FlexLibs2
#
# Tests validation consolidation refactoring for System & Shared operations:
# - AnnotationDefOperations: 10 tests
# - CheckOperations: 10 tests
# - CustomFieldOperations: 10 tests
# - ProjectSettingsOperations: 10 tests
# - WritingSystemOperations: 10 tests
# - FilterOperations: 12 tests
# - MediaOperations: 12 tests
#
# Total Phase 4 System & Shared: 74 tests
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


# ========== SYSTEM - ANNOTATIONDEFOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestAnnotationDefOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for AnnotationDefOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test annotation definition creation requires write enabled."""
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
    def test_delete_requires_annotation_def(self):
        """Test delete requires annotation definition."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "annotation_def_or_hvo")

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
    def test_set_name_requires_annotation_def(self):
        """Test set_name requires annotation definition."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "annotation_def_or_hvo")

    @pytest.mark.validation
    def test_set_name_not_empty(self):
        """Test set_name requires non-empty name."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")


# ========== SYSTEM - CHECKOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestCheckOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for CheckOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test check creation requires write enabled."""
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
    def test_delete_requires_check(self):
        """Test delete requires check."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "check_or_hvo")

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_run_requires_check(self):
        """Test run requires check."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "check_or_hvo")

    @pytest.mark.validation
    def test_get_name_requires_check(self):
        """Test get name requires check."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "check_or_hvo")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_name_requires_check(self):
        """Test set_name requires check."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "check_or_hvo")


# ========== SYSTEM - CUSTOMFIELDOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestCustomFieldOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for CustomFieldOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test custom field creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_create_requires_class_id(self):
        """Test create requires class ID."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "class_id")

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
    def test_delete_requires_field(self):
        """Test delete requires field."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "field_or_hvo")

    @pytest.mark.validation
    def test_find_requires_name(self):
        """Test find requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_get_name_requires_field(self):
        """Test get name requires field."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "field_or_hvo")

    @pytest.mark.validation
    def test_get_class_requires_field(self):
        """Test get class requires field."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "field_or_hvo")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== SYSTEM - PROJECTSETTINGSOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestProjectSettingsOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for ProjectSettingsOperations validation methods."""

    @pytest.mark.validation
    def test_modify_requires_write_enabled(self):
        """Test modification requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_project_name_requires_write_enabled(self):
        """Test setting project name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_project_name_not_empty(self):
        """Test project name must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")

    @pytest.mark.validation
    def test_get_project_name_works(self):
        """Test getting project name works."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_set_default_language_requires_write_enabled(self):
        """Test setting default language requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_default_language_requires_writing_system(self):
        """Test set_default_language requires writing system."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "writing_system")

    @pytest.mark.validation
    def test_get_default_language_works(self):
        """Test getting default language works."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_set_analysis_language_requires_write_enabled(self):
        """Test setting analysis language requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_get_analysis_language_works(self):
        """Test getting analysis language works."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_add_feature_requires_write_enabled(self):
        """Test adding feature requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== SYSTEM - WRITINGSYSTEMOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestWritingSystemOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for WritingSystemOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test writing system creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_language_tag(self):
        """Test create requires language tag."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "language_tag")

    @pytest.mark.validation
    def test_create_language_tag_not_empty(self):
        """Test language tag must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "language_tag")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_writing_system(self):
        """Test delete requires writing system."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "writing_system_or_tag")

    @pytest.mark.validation
    def test_find_requires_language_tag(self):
        """Test find requires language tag."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "language_tag")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_set_abbreviation_requires_write_enabled(self):
        """Test setting abbreviation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_abbreviation_requires_writing_system(self):
        """Test set_abbreviation requires writing system."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "writing_system_or_tag")

    @pytest.mark.validation
    def test_get_language_tag_requires_writing_system(self):
        """Test get_language_tag requires writing system."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "writing_system_or_tag")


# ========== SHARED - FILTEROPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestFilterOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for FilterOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test filter creation requires write enabled."""
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
    def test_delete_requires_filter(self):
        """Test delete requires filter."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "filter_or_hvo")

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
    def test_add_criterion_requires_write_enabled(self):
        """Test adding criterion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_criterion_requires_filter(self):
        """Test add_criterion requires filter."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "filter_or_hvo")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_name_requires_filter(self):
        """Test set_name requires filter."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "filter_or_hvo")

    @pytest.mark.validation
    def test_set_name_not_empty(self):
        """Test set_name requires non-empty name."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")


# ========== SHARED - MEDIAOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestMediaOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for MediaOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test media creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_file_path(self):
        """Test create requires file path."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "file_path")

    @pytest.mark.validation
    def test_create_file_path_not_empty(self):
        """Test file path must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "file_path")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_media(self):
        """Test delete requires media."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "media_or_hvo")

    @pytest.mark.validation
    def test_find_requires_path(self):
        """Test find requires path."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "file_path")

    @pytest.mark.validation
    def test_get_file_path_requires_media(self):
        """Test get file path requires media."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "media_or_hvo")

    @pytest.mark.validation
    def test_set_file_path_requires_write_enabled(self):
        """Test setting file path requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_file_path_requires_media(self):
        """Test set_file_path requires media."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "media_or_hvo")

    @pytest.mark.validation
    def test_set_file_path_not_empty(self):
        """Test set_file_path requires non-empty path."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "file_path")

    @pytest.mark.validation
    def test_get_all_returns_list(self):
        """Test get_all returns a list."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")
