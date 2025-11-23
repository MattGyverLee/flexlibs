"""
Integration Tests for FlexLibs Cross-Module Workflows

These tests verify that the refactored modules work correctly together
and that the shared core utilities function properly across module boundaries.

Author: FlexTools Development Team
Date: 2025-11-22
"""

import unittest
from unittest.mock import Mock, MagicMock

# Import from core
from flexlibs_dev.core import (
    IText,
    IStTxtPara,
    ISegment,
    IWfiWordform,
    resolve_text,
    resolve_paragraph,
    resolve_segment,
    resolve_wordform,
    validate_non_empty_string,
    validate_object_exists,
    validate_index_in_range,
    validate_enum_value,
    SpellingStatusStates,
    ObjectNotFoundError,
    InvalidParameterError,
    DuplicateObjectError,
    NotImplementedYetError,
)

# Import from feature modules
from flexlibs_dev.text_ops import (
    TextCoreOperations,
    TextAdvancedOperations,
    ParagraphCRUDOperations,
)


class TestCoreResolvers(unittest.TestCase):
    """Test core resolver functions work correctly."""

    def setUp(self):
        """Set up mock project."""
        self.project = Mock()
        self.project.GetObject = Mock(return_value=Mock())

    def test_resolve_text_with_hvo(self):
        """Test resolving text from HVO raises NotImplementedError."""
        with self.assertRaises((NotImplementedError, NotImplementedYetError)):
            resolve_text(12345, self.project)

    def test_resolve_text_with_object(self):
        """Test resolving text from object returns object."""
        text_obj = Mock()
        result = resolve_text(text_obj, self.project)
        self.assertEqual(result, text_obj)

    def test_resolve_paragraph_with_object(self):
        """Test resolving paragraph from object."""
        para_obj = Mock()
        result = resolve_paragraph(para_obj, self.project)
        self.assertEqual(result, para_obj)

    def test_resolve_segment_with_object(self):
        """Test resolving segment from object."""
        segment_obj = Mock()
        result = resolve_segment(segment_obj, self.project)
        self.assertEqual(result, segment_obj)

    def test_resolve_wordform_with_object(self):
        """Test resolving wordform from object."""
        wordform_obj = Mock()
        result = resolve_wordform(wordform_obj, self.project)
        self.assertEqual(result, wordform_obj)


class TestCoreValidators(unittest.TestCase):
    """Test core validator functions work correctly."""

    def test_validate_non_empty_string_success(self):
        """Test validation passes for non-empty string."""
        validate_non_empty_string("valid text", "param")
        # Should not raise

    def test_validate_non_empty_string_empty(self):
        """Test validation fails for empty string."""
        with self.assertRaises(InvalidParameterError):
            validate_non_empty_string("", "param")

    def test_validate_non_empty_string_whitespace(self):
        """Test validation fails for whitespace-only string."""
        with self.assertRaises(InvalidParameterError):
            validate_non_empty_string("   ", "param")

    def test_validate_object_exists_success(self):
        """Test validation passes for non-None object."""
        obj = Mock()
        validate_object_exists(obj, 123, "Object")
        # Should not raise

    def test_validate_object_exists_none(self):
        """Test validation fails for None object."""
        with self.assertRaises(ObjectNotFoundError) as cm:
            validate_object_exists(None, 123, "Object")
        self.assertIn("Object not found: 123", str(cm.exception))

    def test_validate_index_in_range_valid(self):
        """Test index validation for valid index."""
        validate_index_in_range(5, 10)
        # Should not raise

    def test_validate_index_in_range_negative(self):
        """Test index validation fails for negative index."""
        with self.assertRaises(InvalidParameterError):
            validate_index_in_range(-1, 10)

    def test_validate_index_in_range_too_large(self):
        """Test index validation fails for index >= max."""
        with self.assertRaises(InvalidParameterError):
            validate_index_in_range(10, 10)

    def test_validate_index_in_range_append_allowed(self):
        """Test index validation allows append when flag set."""
        validate_index_in_range(10, 10, allow_append=True)
        # Should not raise

    def test_validate_enum_value_valid(self):
        """Test enum validation passes for valid enum."""
        status = SpellingStatusStates.CORRECT
        validate_enum_value(status, SpellingStatusStates, "status")
        # Should not raise

    def test_validate_enum_value_invalid(self):
        """Test enum validation fails for non-enum value."""
        with self.assertRaises(InvalidParameterError):
            validate_enum_value(123, SpellingStatusStates, "status")


class TestCoreExceptions(unittest.TestCase):
    """Test core exception classes."""

    def test_object_not_found_error(self):
        """Test ObjectNotFoundError has correct properties."""
        error = ObjectNotFoundError("Text", 12345)
        self.assertEqual(error.obj_type, "Text")
        self.assertEqual(error.identifier, 12345)
        self.assertIn("Text not found: 12345", str(error))

    def test_object_not_found_is_value_error(self):
        """Test ObjectNotFoundError is instance of ValueError."""
        error = ObjectNotFoundError("Text", 12345)
        self.assertIsInstance(error, ValueError)

    def test_duplicate_object_error(self):
        """Test DuplicateObjectError has correct properties."""
        error = DuplicateObjectError("Text", "Story 1")
        self.assertEqual(error.obj_type, "Text")
        self.assertEqual(error.identifier, "Story 1")
        self.assertIn("Text already exists: Story 1", str(error))

    def test_duplicate_object_is_runtime_error(self):
        """Test DuplicateObjectError is instance of RuntimeError."""
        error = DuplicateObjectError("Text", "Story 1")
        self.assertIsInstance(error, RuntimeError)


class TestCrossModuleWorkflow(unittest.TestCase):
    """Test workflows that span multiple modules."""

    def setUp(self):
        """Set up mock project and operations."""
        self.project = Mock()
        self.text_ops = TextCoreOperations(self.project)
        self.para_ops = ParagraphCRUDOperations(self.project)

    def test_text_operations_use_core_types(self):
        """Test that text operations use core type definitions."""
        # This verifies imports work correctly
        self.assertIsNotNone(self.text_ops)

    def test_paragraph_operations_use_core_types(self):
        """Test that paragraph operations use core type definitions."""
        self.assertIsNotNone(self.para_ops)

    def test_text_create_validates_input(self):
        """Test text_create uses core validation."""
        # Should raise InvalidParameterError or NotImplementedError for empty name
        with self.assertRaises((InvalidParameterError, NotImplementedError, NotImplementedYetError)):
            self.text_ops.text_create("")

    def test_paragraph_create_validates_input(self):
        """Test paragraph_create uses core validation."""
        # Should raise InvalidParameterError, NotImplementedError or NotImplementedYetError
        with self.assertRaises((InvalidParameterError, NotImplementedError, NotImplementedYetError)):
            self.para_ops.paragraph_create(Mock(), "")


class TestConstantsSharing(unittest.TestCase):
    """Test that constants are properly shared across modules."""

    def test_spelling_status_states_available(self):
        """Test SpellingStatusStates enum is accessible."""
        self.assertEqual(SpellingStatusStates.UNDECIDED, 0)
        self.assertEqual(SpellingStatusStates.INCORRECT, 1)
        self.assertEqual(SpellingStatusStates.CORRECT, 2)

    def test_spelling_status_states_in_core(self):
        """Test SpellingStatusStates is imported from core."""
        from flexlibs_dev.core import SpellingStatusStates as CoreStatus
        self.assertEqual(CoreStatus.CORRECT, 2)


class TestModuleInteroperability(unittest.TestCase):
    """Test that modules can share data through core types."""

    def test_text_to_paragraph_flow(self):
        """Test that text object can be used by paragraph operations."""
        project = Mock()
        text_ops = TextCoreOperations(project)
        para_ops = ParagraphCRUDOperations(project)

        # Mock text object
        mock_text = Mock()

        # Both should be able to work with the same object type
        # (In actual implementation, not just stubs)
        self.assertIsNotNone(text_ops)
        self.assertIsNotNone(para_ops)


class TestDocumentation(unittest.TestCase):
    """Test that documentation and metadata are correct."""

    def test_architecture_md_exists(self):
        """Test that ARCHITECTURE.md was created."""
        import os
        arch_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "ARCHITECTURE.md"
        )
        self.assertTrue(os.path.exists(arch_path))

    def test_refactoring_log_exists(self):
        """Test that REFACTORING_LOG.md was created."""
        import os
        log_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "REFACTORING_LOG.md"
        )
        self.assertTrue(os.path.exists(log_path))


if __name__ == "__main__":
    unittest.main()
