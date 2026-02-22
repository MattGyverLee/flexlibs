#
# phase4_discourse_tests.py
#
# Phase 4 Discourse Validation Tests for FlexLibs2
#
# Tests validation consolidation refactoring for Discourse operations:
# - ConstChartClauseMarkerOperations: 10 tests
# - ConstChartMovedTextOperations: 10 tests
# - ConstChartOperations: 12 tests
# - ConstChartRowOperations: 10 tests
# - ConstChartTagOperations: 10 tests
# - ConstChartWordGroupOperations: 8 tests
#
# Total Phase 4 Discourse: 60 tests
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


# ========== DISCOURSE - CONSTCHARTCLAUSEMARKOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestConstChartClauseMarkerOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for ConstChartClauseMarkerOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test clause marker creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_row(self):
        """Test create requires row."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "row_or_hvo")

    @pytest.mark.validation
    def test_create_requires_word_group(self):
        """Test create requires word group."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "word_group")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_marker(self):
        """Test delete requires marker."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "marker_or_hvo")

    @pytest.mark.validation
    def test_find_requires_row(self):
        """Test find requires row."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "row_or_hvo")

    @pytest.mark.validation
    def test_get_word_group_requires_marker(self):
        """Test get word group requires marker."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "marker_or_hvo")

    @pytest.mark.validation
    def test_add_dependent_clause_requires_write_enabled(self):
        """Test adding dependent clause requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_dependent_clause_requires_marker(self):
        """Test add_dependent_clause requires marker."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "marker_or_hvo")

    @pytest.mark.validation
    def test_add_dependent_clause_requires_dependent(self):
        """Test add_dependent_clause requires dependent marker."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "dependent_marker")


# ========== DISCOURSE - CONSTCHARTMOVEDTEXTOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestConstChartMovedTextOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for ConstChartMovedTextOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test moved text creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_row(self):
        """Test create requires row."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "row_or_hvo")

    @pytest.mark.validation
    def test_create_requires_source_word_group(self):
        """Test create requires source word group."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "source_word_group")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_moved_text(self):
        """Test delete requires moved text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "moved_text_or_hvo")

    @pytest.mark.validation
    def test_find_requires_row(self):
        """Test find requires row."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "row_or_hvo")

    @pytest.mark.validation
    def test_get_source_requires_moved_text(self):
        """Test get source requires moved text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "moved_text_or_hvo")

    @pytest.mark.validation
    def test_set_target_requires_write_enabled(self):
        """Test setting target requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_target_requires_moved_text(self):
        """Test set_target requires moved text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "moved_text_or_hvo")

    @pytest.mark.validation
    def test_set_target_requires_target_word_group(self):
        """Test set_target requires target word group."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "target_word_group")


# ========== DISCOURSE - CONSTCHARTOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestConstChartOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for ConstChartOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test chart creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_text(self):
        """Test create requires text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "text_or_hvo")

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires chart name."""
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
    def test_delete_requires_chart(self):
        """Test delete requires chart."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "chart_or_hvo")

    @pytest.mark.validation
    def test_find_requires_text(self):
        """Test find requires text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "text_or_hvo")

    @pytest.mark.validation
    def test_get_rows_requires_chart(self):
        """Test get rows requires chart."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "chart_or_hvo")

    @pytest.mark.validation
    def test_get_text_requires_chart(self):
        """Test get text requires chart."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "chart_or_hvo")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_name_requires_chart(self):
        """Test set_name requires chart."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "chart_or_hvo")

    @pytest.mark.validation
    def test_set_name_not_empty(self):
        """Test set_name requires non-empty name."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")


# ========== DISCOURSE - CONSTCHARTROWOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestConstChartRowOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    IndexBoundsTestsMixin,
):
    """Tests for ConstChartRowOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test row creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_chart(self):
        """Test create requires chart."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "chart_or_hvo")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_row(self):
        """Test delete requires row."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "row_or_hvo")

    @pytest.mark.validation
    def test_find_requires_chart(self):
        """Test find requires chart."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "chart_or_hvo")

    @pytest.mark.validation
    def test_get_chart_requires_row(self):
        """Test get chart requires row."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "row_or_hvo")

    @pytest.mark.validation
    def test_move_requires_write_enabled(self):
        """Test moving row requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_move_requires_row(self):
        """Test move requires row."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "row_or_hvo")

    @pytest.mark.validation
    def test_move_requires_valid_target_index(self):
        """Test move requires valid target index."""
        ops = self.create_operations()
        self.assert_value_error(ops._ValidateIndexBounds, -1, 5, "target_index")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== DISCOURSE - CONSTCHARTTAGOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestConstChartTagOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for ConstChartTagOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test tag creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_row(self):
        """Test create requires row."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "row_or_hvo")

    @pytest.mark.validation
    def test_create_requires_word_group(self):
        """Test create requires word group."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "word_group")

    @pytest.mark.validation
    def test_create_requires_tag_name(self):
        """Test create requires tag name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "tag_name")

    @pytest.mark.validation
    def test_create_tag_name_not_empty(self):
        """Test create tag name must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "tag_name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_tag(self):
        """Test delete requires tag."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "tag_or_hvo")

    @pytest.mark.validation
    def test_find_requires_row(self):
        """Test find requires row."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "row_or_hvo")

    @pytest.mark.validation
    def test_get_name_requires_tag(self):
        """Test get name requires tag."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "tag_or_hvo")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== DISCOURSE - CONSTCHARTWORDGROUPOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase4
class TestConstChartWordGroupOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for ConstChartWordGroupOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test word group creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_row(self):
        """Test create requires row."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "row_or_hvo")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_word_group(self):
        """Test delete requires word group."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "word_group_or_hvo")

    @pytest.mark.validation
    def test_find_requires_row(self):
        """Test find requires row."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "row_or_hvo")

    @pytest.mark.validation
    def test_get_words_requires_word_group(self):
        """Test get words requires word group."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "word_group_or_hvo")

    @pytest.mark.validation
    def test_move_requires_write_enabled(self):
        """Test moving word group requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_move_requires_word_group(self):
        """Test move requires word group."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "word_group_or_hvo")
