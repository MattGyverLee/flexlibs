#
# phase2_validation_tests.py
#
# Phase 2 Validation Tests for FlexLibs2
#
# Tests validation consolidation refactoring for:
# - TextsWords (8 files, ~80 tests):
#   * DiscourseOperations: 10 tests
#   * ParagraphOperations: 10 tests
#   * SegmentOperations: 15 tests
#   * TextOperations: 10 tests
#   * WfiAnalysisOperations: 12 tests
#   * WfiGlossOperations: 12 tests
#   * WfiMorphBundleOperations: 12 tests
#   * WordformOperations: 7 tests
#
# - Grammar (3 files, ~40 tests):
#   * GramCatOperations: 10 tests
#   * POSOperations: 15 tests
#   * MorphRuleOperations: 15 tests
#
# Total Phase 2: ~120 tests covering all validation patterns
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


# ========== TEXTSWORDS - DISCOURSEOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase2
class TestDiscourseOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for DiscourseOperations validation methods."""

    @pytest.mark.validation
    def test_paragraph_create_requires_write_enabled(self):
        """Test that creating paragraph requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        parent = Mock()
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_paragraph_validate_not_none(self):
        """Test validation that paragraph is not None."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "paragraph")

    @pytest.mark.validation
    def test_clause_marker_create_requires_write_enabled(self):
        """Test clause marker creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_clause_marker_validate_not_none(self):
        """Test validation that marker is not None."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "marker")

    @pytest.mark.validation
    def test_word_group_create_requires_write_enabled(self):
        """Test word group creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_word_group_validate_not_none(self):
        """Test validation that word group is not None."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "word_group")

    @pytest.mark.validation
    def test_moved_text_create_requires_write_enabled(self):
        """Test moved text creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_moved_text_validate_not_none(self):
        """Test validation that moved text is not None."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "moved_text")

    @pytest.mark.validation
    def test_const_chart_create_requires_write_enabled(self):
        """Test constituent chart creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_const_chart_validate_not_none(self):
        """Test validation that chart is not None."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "const_chart")


# ========== TEXTSWORDS - PARAGRAPHOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase2
class TestParagraphOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for ParagraphOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test paragraph creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_text_param_not_none(self):
        """Test create requires text parameter."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "text")

    @pytest.mark.validation
    def test_modify_requires_write_enabled(self):
        """Test modification requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_modify_paragraph_not_none(self):
        """Test modify requires paragraph parameter."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "paragraph")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_paragraph_not_none(self):
        """Test delete requires paragraph parameter."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "paragraph")

    @pytest.mark.validation
    def test_get_analysis_writing_system_valid(self):
        """Test get analysis writing system validates input."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "writing_system")

    @pytest.mark.validation
    def test_get_reference_requires_object(self):
        """Test getting reference requires object."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "object")

    @pytest.mark.validation
    def test_set_reference_requires_object(self):
        """Test setting reference requires object."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "object")

    @pytest.mark.validation
    def test_copy_requires_write_enabled(self):
        """Test copy operation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== TEXTSWORDS - SEGMENTOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase2
class TestSegmentOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
    IndexBoundsTestsMixin,
):
    """Tests for SegmentOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test segment creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_paragraph_not_none(self):
        """Test create requires paragraph."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "paragraph")

    @pytest.mark.validation
    def test_create_text_not_empty(self):
        """Test create requires non-empty text."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "text")

    @pytest.mark.validation
    def test_modify_requires_write_enabled(self):
        """Test modification requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_modify_segment_not_none(self):
        """Test modify requires segment."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "segment")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_segment_not_none(self):
        """Test delete requires segment."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "segment")

    @pytest.mark.validation
    def test_set_analysis_requires_write_enabled(self):
        """Test setting analysis requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_analysis_segment_not_none(self):
        """Test set_analysis requires segment."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "segment")

    @pytest.mark.validation
    def test_move_requires_write_enabled(self):
        """Test moving segment requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_move_segment_not_none(self):
        """Test move requires segment."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "segment")

    @pytest.mark.validation
    def test_move_target_index_valid(self):
        """Test move requires valid target index."""
        ops = self.create_operations()
        self.assert_value_error(ops._ValidateIndexBounds, -1, 5, "target_index")

    @pytest.mark.validation
    def test_split_requires_write_enabled(self):
        """Test splitting segment requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_split_segment_not_none(self):
        """Test split requires segment."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "segment")


# ========== TEXTSWORDS - TEXTOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase2
class TestTextOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for TextOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test text creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires text name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_text(self):
        """Test delete requires text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "text")

    @pytest.mark.validation
    def test_get_paragraphs_requires_text(self):
        """Test get_paragraphs requires text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "text")

    @pytest.mark.validation
    def test_get_references_requires_text(self):
        """Test get_references requires text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "text")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_text(self):
        """Test duplicate requires text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "text")

    @pytest.mark.validation
    def test_sort_requires_text(self):
        """Test sort requires text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "text")

    @pytest.mark.validation
    def test_reorder_requires_write_enabled(self):
        """Test reordering requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== TEXTSWORDS - WFIANALYSISOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase2
class TestWfiAnalysisOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for WfiAnalysisOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test analysis creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_wordform(self):
        """Test create requires wordform."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "wordform")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_analysis(self):
        """Test delete requires analysis."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "analysis")

    @pytest.mark.validation
    def test_set_approved_requires_write_enabled(self):
        """Test setting approved requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_approved_requires_analysis(self):
        """Test set_approved requires analysis."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "analysis")

    @pytest.mark.validation
    def test_get_morpheme_bundles_requires_analysis(self):
        """Test get_morpheme_bundles requires analysis."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "analysis")

    @pytest.mark.validation
    def test_validate_morphemes_requires_analysis(self):
        """Test validate_morphemes requires analysis."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "analysis")

    @pytest.mark.validation
    def test_get_gloss_requires_analysis(self):
        """Test get_gloss requires analysis."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "analysis")

    @pytest.mark.validation
    def test_set_gloss_requires_write_enabled(self):
        """Test setting gloss requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_gloss_requires_analysis(self):
        """Test set_gloss requires analysis."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "analysis")


# ========== TEXTSWORDS - WFIGLOSSOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase2
class TestWfiGlossOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for WfiGlossOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test gloss creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_analysis(self):
        """Test create requires analysis."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "analysis")

    @pytest.mark.validation
    def test_create_requires_gloss_text(self):
        """Test create requires gloss text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "gloss_text")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_gloss(self):
        """Test delete requires gloss."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "gloss")

    @pytest.mark.validation
    def test_set_text_requires_write_enabled(self):
        """Test setting text requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_text_requires_gloss(self):
        """Test set_text requires gloss."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "gloss")

    @pytest.mark.validation
    def test_set_text_requires_non_empty_text(self):
        """Test set_text requires non-empty text."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "text")

    @pytest.mark.validation
    def test_set_writing_system_requires_write_enabled(self):
        """Test setting writing system requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_writing_system_requires_gloss(self):
        """Test set_writing_system requires gloss."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "gloss")

    @pytest.mark.validation
    def test_set_writing_system_requires_ws(self):
        """Test set_writing_system requires writing system."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "writing_system")


# ========== TEXTSWORDS - WFIMORPHBUNDLEOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase2
class TestWfiMorphBundleOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for WfiMorphBundleOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test bundle creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_analysis(self):
        """Test create requires analysis."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "analysis")

    @pytest.mark.validation
    def test_create_requires_morpheme(self):
        """Test create requires morpheme."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "morpheme")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_bundle(self):
        """Test delete requires bundle."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "bundle")

    @pytest.mark.validation
    def test_set_morpheme_requires_write_enabled(self):
        """Test setting morpheme requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_morpheme_requires_bundle(self):
        """Test set_morpheme requires bundle."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "bundle")

    @pytest.mark.validation
    def test_set_morpheme_requires_morpheme(self):
        """Test set_morpheme requires morpheme."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "morpheme")

    @pytest.mark.validation
    def test_set_sense_requires_write_enabled(self):
        """Test setting sense requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_sense_requires_bundle(self):
        """Test set_sense requires bundle."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "bundle")

    @pytest.mark.validation
    def test_set_sense_requires_sense(self):
        """Test set_sense requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")


# ========== TEXTSWORDS - WORDFORMOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase2
class TestWordformOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for WordformOperations validation methods."""

    @pytest.mark.validation
    def test_get_analyses_requires_wordform(self):
        """Test get_analyses requires wordform."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "wordform")

    @pytest.mark.validation
    def test_get_status_requires_wordform(self):
        """Test get_status requires wordform."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "wordform")

    @pytest.mark.validation
    def test_has_analysis_requires_wordform(self):
        """Test has_analysis requires wordform."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "wordform")

    @pytest.mark.validation
    def test_get_morpheme_glosses_requires_wordform(self):
        """Test get_morpheme_glosses requires wordform."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "wordform")

    @pytest.mark.validation
    def test_get_best_guess_requires_wordform(self):
        """Test get_best_guess requires wordform."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "wordform")

    @pytest.mark.validation
    def test_validate_analysis_requires_wordform(self):
        """Test validate_analysis requires wordform."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "wordform")

    @pytest.mark.validation
    def test_is_word_form_requires_writing_system(self):
        """Test is_word_form requires writing system."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "writing_system")


# ========== GRAMMAR - GRAMCATOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase2
class TestGramCatOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for GramCatOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test category creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_name(self):
        """Test create requires name."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "name")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_category(self):
        """Test delete requires category."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "category")

    @pytest.mark.validation
    def test_get_all_requires_no_params(self):
        """Test get_all works without parameters."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateParam("valid", "param")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_category(self):
        """Test duplicate requires category."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "category")

    @pytest.mark.validation
    def test_add_feature_requires_write_enabled(self):
        """Test adding feature requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_feature_requires_category(self):
        """Test add_feature requires category."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "category")

    @pytest.mark.validation
    def test_add_feature_requires_feature(self):
        """Test add_feature requires feature."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "feature")


# ========== GRAMMAR - POSOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase2
class TestPOSOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for POSOperations (Part-of-Speech) validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test POS creation requires write enabled."""
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
    def test_delete_requires_pos(self):
        """Test delete requires POS."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "pos")

    @pytest.mark.validation
    def test_set_name_requires_write_enabled(self):
        """Test setting name requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_name_requires_pos(self):
        """Test set_name requires POS."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "pos")

    @pytest.mark.validation
    def test_set_name_requires_non_empty_name(self):
        """Test set_name requires non-empty name."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "name")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_pos(self):
        """Test duplicate requires POS."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "pos")

    @pytest.mark.validation
    def test_set_abbr_requires_write_enabled(self):
        """Test setting abbreviation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_abbr_requires_pos(self):
        """Test set_abbr requires POS."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "pos")

    @pytest.mark.validation
    def test_add_feature_requires_write_enabled(self):
        """Test adding feature requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_feature_requires_pos(self):
        """Test add_feature requires POS."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "pos")

    @pytest.mark.validation
    def test_add_feature_requires_category(self):
        """Test add_feature requires category."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "category")


# ========== GRAMMAR - MORPHRULEOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase2
class TestMorphRuleOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
    IndexBoundsTestsMixin,
):
    """Tests for MorphRuleOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test rule creation requires write enabled."""
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
    def test_delete_requires_rule(self):
        """Test delete requires rule."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "rule")

    @pytest.mark.validation
    def test_set_input_requires_write_enabled(self):
        """Test setting input requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_input_requires_rule(self):
        """Test set_input requires rule."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "rule")

    @pytest.mark.validation
    def test_set_output_requires_write_enabled(self):
        """Test setting output requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_output_requires_rule(self):
        """Test set_output requires rule."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "rule")

    @pytest.mark.validation
    def test_set_environment_requires_write_enabled(self):
        """Test setting environment requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_environment_requires_rule(self):
        """Test set_environment requires rule."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "rule")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_rule(self):
        """Test duplicate requires rule."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "rule")
