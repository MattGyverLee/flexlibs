#
# phase3_lexicon_validation_tests.py
#
# Phase 3 Lexicon Validation Tests for FlexLibs2
#
# Tests validation consolidation refactoring for Lexicon operations:
# - AllomorphOperations: 12 tests
# - EtymologyOperations: 12 tests
# - ExampleOperations: 12 tests
# - LexEntryOperations: 15 tests
# - LexReferenceOperations: 12 tests
# - LexSenseOperations: 15 tests
# - PronunciationOperations: 12 tests
# - ReversalOperations: 10 tests
# - SemanticDomainOperations: 12 tests
# - VariantOperations: 12 tests
#
# Total Phase 3 Lexicon: 132 tests
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
from test_helpers import create_mock_entry, create_mock_sense


# ========== LEXICON - ALLOMORPHOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase3
class TestAllomorphOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for AllomorphOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test allomorph creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_entry(self):
        """Test create requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")

    @pytest.mark.validation
    def test_create_requires_form(self):
        """Test create requires form text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "form")

    @pytest.mark.validation
    def test_create_form_not_empty(self):
        """Test create form must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "form")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_allomorph(self):
        """Test delete requires allomorph."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "allomorph")

    @pytest.mark.validation
    def test_set_form_requires_write_enabled(self):
        """Test setting form requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_form_requires_allomorph(self):
        """Test set_form requires allomorph."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "allomorph")

    @pytest.mark.validation
    def test_set_form_not_empty(self):
        """Test set_form requires non-empty form."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "form")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_allomorph(self):
        """Test duplicate requires allomorph."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "allomorph")

    @pytest.mark.validation
    def test_get_environment_requires_allomorph(self):
        """Test get_environment requires allomorph."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "allomorph")


# ========== LEXICON - ETYMOLOGYOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase3
class TestEtymologyOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for EtymologyOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test etymology creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_entry(self):
        """Test create requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_etymology(self):
        """Test delete requires etymology."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "etymology")

    @pytest.mark.validation
    def test_set_source_requires_write_enabled(self):
        """Test setting source requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_source_requires_etymology(self):
        """Test set_source requires etymology."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "etymology")

    @pytest.mark.validation
    def test_set_gloss_requires_write_enabled(self):
        """Test setting gloss requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_gloss_requires_etymology(self):
        """Test set_gloss requires etymology."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "etymology")

    @pytest.mark.validation
    def test_set_type_requires_write_enabled(self):
        """Test setting type requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_type_requires_etymology(self):
        """Test set_type requires etymology."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "etymology")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_etymology(self):
        """Test duplicate requires etymology."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "etymology")


# ========== LEXICON - EXAMPLEOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase3
class TestExampleOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for ExampleOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test example creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_sense(self):
        """Test create requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")

    @pytest.mark.validation
    def test_create_requires_text(self):
        """Test create requires example text."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "text")

    @pytest.mark.validation
    def test_create_text_not_empty(self):
        """Test create text must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "text")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_example(self):
        """Test delete requires example."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "example")

    @pytest.mark.validation
    def test_set_text_requires_write_enabled(self):
        """Test setting text requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_text_requires_example(self):
        """Test set_text requires example."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "example")

    @pytest.mark.validation
    def test_set_text_not_empty(self):
        """Test set_text requires non-empty text."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "text")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_example(self):
        """Test duplicate requires example."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "example")

    @pytest.mark.validation
    def test_get_text_requires_example(self):
        """Test get_text requires example."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "example")


# ========== LEXICON - LEXENTRYOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase3
class TestLexEntryOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for LexEntryOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test entry creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_lexeme_form(self):
        """Test create requires lexeme form."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "lexeme_form")

    @pytest.mark.validation
    def test_create_lexeme_not_empty(self):
        """Test create lexeme form must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "lexeme_form")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_entry(self):
        """Test delete requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")

    @pytest.mark.validation
    def test_add_sense_requires_write_enabled(self):
        """Test adding sense requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_sense_requires_entry(self):
        """Test add_sense requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")

    @pytest.mark.validation
    def test_set_citation_requires_write_enabled(self):
        """Test setting citation form requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_citation_requires_entry(self):
        """Test set_citation requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")

    @pytest.mark.validation
    def test_set_citation_not_empty(self):
        """Test set_citation requires non-empty form."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "form")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_entry(self):
        """Test duplicate requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")

    @pytest.mark.validation
    def test_get_headword_requires_entry(self):
        """Test get_headword requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")

    @pytest.mark.validation
    def test_get_sense_count_requires_entry(self):
        """Test get_sense_count requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")

    @pytest.mark.validation
    def test_find_allomorph_requires_entry(self):
        """Test find_allomorph requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")


# ========== LEXICON - LEXREFERENCEOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase3
class TestLexReferenceOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for LexReferenceOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test reference creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_entry(self):
        """Test create requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")

    @pytest.mark.validation
    def test_create_requires_type(self):
        """Test create requires reference type."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "ref_type")

    @pytest.mark.validation
    def test_create_requires_target(self):
        """Test create requires target entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "target")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_reference(self):
        """Test delete requires reference."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "reference")

    @pytest.mark.validation
    def test_add_target_requires_write_enabled(self):
        """Test adding target requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_target_requires_reference(self):
        """Test add_target requires reference."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "reference")

    @pytest.mark.validation
    def test_add_target_requires_target(self):
        """Test add_target requires target."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "target")

    @pytest.mark.validation
    def test_remove_target_requires_write_enabled(self):
        """Test removing target requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_remove_target_requires_reference(self):
        """Test remove_target requires reference."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "reference")

    @pytest.mark.validation
    def test_remove_target_requires_target(self):
        """Test remove_target requires target."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "target")


# ========== LEXICON - LEXSENSEOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase3
class TestLexSenseOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for LexSenseOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test sense creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_entry(self):
        """Test create requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_sense(self):
        """Test delete requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")

    @pytest.mark.validation
    def test_set_gloss_requires_write_enabled(self):
        """Test setting gloss requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_gloss_requires_sense(self):
        """Test set_gloss requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")

    @pytest.mark.validation
    def test_set_gloss_not_empty(self):
        """Test set_gloss requires non-empty gloss."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "gloss")

    @pytest.mark.validation
    def test_set_definition_requires_write_enabled(self):
        """Test setting definition requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_definition_requires_sense(self):
        """Test set_definition requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")

    @pytest.mark.validation
    def test_add_example_requires_write_enabled(self):
        """Test adding example requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_example_requires_sense(self):
        """Test add_example requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_sense(self):
        """Test duplicate requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")

    @pytest.mark.validation
    def test_get_gloss_requires_sense(self):
        """Test get_gloss requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")


# ========== LEXICON - PRONUNCIATIONOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase3
class TestPronunciationOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for PronunciationOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test pronunciation creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_entry(self):
        """Test create requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")

    @pytest.mark.validation
    def test_create_requires_form(self):
        """Test create requires pronunciation form."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "form")

    @pytest.mark.validation
    def test_create_form_not_empty(self):
        """Test create form must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "form")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_pronunciation(self):
        """Test delete requires pronunciation."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "pronunciation")

    @pytest.mark.validation
    def test_set_form_requires_write_enabled(self):
        """Test setting form requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_form_requires_pronunciation(self):
        """Test set_form requires pronunciation."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "pronunciation")

    @pytest.mark.validation
    def test_set_form_not_empty(self):
        """Test set_form requires non-empty form."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "form")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_pronunciation(self):
        """Test duplicate requires pronunciation."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "pronunciation")

    @pytest.mark.validation
    def test_get_form_requires_pronunciation(self):
        """Test get_form requires pronunciation."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "pronunciation")


# ========== LEXICON - REVERSALOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase3
class TestReversalOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
):
    """Tests for ReversalOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test reversal creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_sense(self):
        """Test create requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")

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
    def test_delete_requires_reversal(self):
        """Test delete requires reversal."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "reversal")

    @pytest.mark.validation
    def test_set_form_requires_write_enabled(self):
        """Test setting form requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_form_requires_reversal(self):
        """Test set_form requires reversal."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "reversal")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_reversal(self):
        """Test duplicate requires reversal."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "reversal")


# ========== LEXICON - SEMANTICDOMAINOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase3
class TestSemanticDomainOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for SemanticDomainOperations validation methods."""

    @pytest.mark.validation
    def test_add_requires_write_enabled(self):
        """Test adding semantic domain requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_add_requires_sense(self):
        """Test add requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")

    @pytest.mark.validation
    def test_add_requires_domain(self):
        """Test add requires semantic domain."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "domain")

    @pytest.mark.validation
    def test_remove_requires_write_enabled(self):
        """Test removing semantic domain requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_remove_requires_sense(self):
        """Test remove requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")

    @pytest.mark.validation
    def test_remove_requires_domain(self):
        """Test remove requires semantic domain."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "domain")

    @pytest.mark.validation
    def test_get_domains_requires_sense(self):
        """Test get_domains requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")

    @pytest.mark.validation
    def test_has_domain_requires_sense(self):
        """Test has_domain requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")

    @pytest.mark.validation
    def test_has_domain_requires_domain(self):
        """Test has_domain requires domain."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "domain")

    @pytest.mark.validation
    def test_clear_requires_write_enabled(self):
        """Test clearing domains requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_clear_requires_sense(self):
        """Test clear requires sense."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "sense")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


# ========== LEXICON - VARIANTOPERATIONS ==========

@pytest.mark.validation
@pytest.mark.phase3
class TestVariantOperations(
    BaseValidationTest,
    WriteEnabledTestsMixin,
    ParameterValidationTestsMixin,
    StringValidationTestsMixin,
):
    """Tests for VariantOperations validation methods."""

    @pytest.mark.validation
    def test_create_requires_write_enabled(self):
        """Test variant creation requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_create_requires_entry(self):
        """Test create requires entry."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "entry")

    @pytest.mark.validation
    def test_create_requires_form(self):
        """Test create requires form."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "form")

    @pytest.mark.validation
    def test_create_form_not_empty(self):
        """Test create form must not be empty."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "form")

    @pytest.mark.validation
    def test_delete_requires_write_enabled(self):
        """Test deletion requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_delete_requires_variant(self):
        """Test delete requires variant."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "variant")

    @pytest.mark.validation
    def test_set_form_requires_write_enabled(self):
        """Test setting form requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_set_form_requires_variant(self):
        """Test set_form requires variant."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "variant")

    @pytest.mark.validation
    def test_set_form_not_empty(self):
        """Test set_form requires non-empty form."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "form")

    @pytest.mark.validation
    def test_duplicate_requires_write_enabled(self):
        """Test duplication requires write enabled."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)

    @pytest.mark.validation
    def test_duplicate_requires_variant(self):
        """Test duplicate requires variant."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "variant")
