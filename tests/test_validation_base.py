#
# test_validation_base.py
#
# Base test class template for all FlexLibs2 validation tests
#
# Provides:
# - Base test class (BaseValidationTest) for all validation tests
# - Setup/teardown for each operation type
# - Helper methods: assert_write_enabled_error(), assert_param_error(), etc.
# - Markers for test categorization (@pytest.mark.validation, etc.)
#
# Platform: Python.NET
#           FieldWorks Version 9+
#
# Copyright 2025
#

import pytest
from unittest.mock import Mock, MagicMock
import logging

logger = logging.getLogger(__name__)


class BaseValidationTest:
    """
    Base class for all FlexLibs2 validation tests.

    Provides common setup, teardown, and helper methods for testing
    validation patterns across all operation classes.

    Usage::

        @pytest.mark.validation
        @pytest.mark.phase2
        class TestMyOperations(BaseValidationTest):

            def test_ensure_write_enabled_passes_when_writable(self):
                '''Test that _EnsureWriteEnabled passes when project is writable.'''
                # Arrange
                ops = self.create_operations()

                # Act & Assert - should not raise
                ops._EnsureWriteEnabled()

            def test_ensure_write_enabled_fails_when_read_only(self):
                '''Test that _EnsureWriteEnabled fails when project is read-only.'''
                # Arrange
                ops = self.create_operations(write_enabled=False)

                # Act & Assert
                self.assert_write_enabled_error(ops._EnsureWriteEnabled)

            def test_validate_param_passes_with_valid_object(self):
                '''Test that _ValidateParam passes with valid object.'''
                # Arrange
                ops = self.create_operations()
                test_obj = Mock()

                # Act & Assert - should not raise
                ops._ValidateParam(test_obj, "test_object")

            def test_validate_param_fails_with_none(self):
                '''Test that _ValidateParam fails with None.'''
                # Arrange
                ops = self.create_operations()

                # Act & Assert
                self.assert_param_error(ops._ValidateParam, None, "test_param")
    """

    # ========== SETUP/TEARDOWN ==========

    def setup_method(self):
        """Setup called before each test method."""
        self.project = None
        self.operations = None
        self.test_objects = {}

    def teardown_method(self):
        """Cleanup called after each test method."""
        self.project = None
        self.operations = None
        self.test_objects.clear()

    # ========== FACTORY METHODS ==========

    def create_project(self, write_enabled=True):
        """
        Create a mock FLExProject instance.

        Args:
            write_enabled: If True, project can be modified

        Returns:
            Mock FLExProject
        """
        from conftest import MockFLExProject
        return MockFLExProject(write_enabled=write_enabled)

    def create_operations(self, write_enabled=True, operations_class=None):
        """
        Create an operations instance for testing.

        Args:
            write_enabled: If True, project can be modified
            operations_class: Class to instantiate. If None, creates
                            a mock class with validation methods.

        Returns:
            Operations instance
        """
        project = self.create_project(write_enabled=write_enabled)

        if operations_class is None:
            # Create mock operations class with validation methods
            class MockOperations:
                def __init__(self, proj):
                    self.project = proj

                def _EnsureWriteEnabled(self):
                    if not self.project.CanModify():
                        raise Exception(
                            "Project is read-only or not open. "
                            "Cannot perform modifications. "
                            "Open the project with writeEnabled=True."
                        )

                def _ValidateParam(self, param, param_name="parameter"):
                    if param is None:
                        raise Exception(f"{param_name} cannot be None")

                def _ValidateParamNotEmpty(self, param, param_name="parameter"):
                    if param is None:
                        raise Exception(f"{param_name} cannot be None")
                    if len(param) == 0:
                        raise Exception(f"{param_name} cannot be empty")

                def _ValidateInstanceOf(self, obj, expected_type, param_name="object"):
                    if not isinstance(obj, expected_type):
                        if isinstance(expected_type, tuple):
                            type_names = " or ".join(t.__name__ for t in expected_type)
                        else:
                            type_names = expected_type.__name__
                        raise TypeError(
                            f"{param_name} must be {type_names}, "
                            f"got {type(obj).__name__}"
                        )

                def _ValidateStringNotEmpty(self, text, param_name="text"):
                    if not isinstance(text, str):
                        raise TypeError(
                            f"{param_name} must be a string, got {type(text).__name__}"
                        )
                    if len(text.strip()) == 0:
                        raise Exception(
                            f"{param_name} cannot be empty or contain only whitespace"
                        )

                def _ValidateIndexBounds(self, index, max_count, param_name="index"):
                    if not isinstance(index, int):
                        raise TypeError(
                            f"{param_name} must be an integer, got {type(index).__name__}"
                        )
                    if index < 0:
                        raise ValueError(
                            f"{param_name} cannot be negative, got {index}"
                        )
                    if index >= max_count:
                        raise IndexError(
                            f"{param_name} out of bounds: {index} >= {max_count} "
                            f"(valid range: 0-{max_count - 1})"
                        )

                def _ValidateOwner(self, obj, expected_owner, param_name="object"):
                    if not hasattr(obj, "Owner"):
                        raise AttributeError(
                            f"{param_name} does not have Owner property"
                        )
                    if obj.Owner != expected_owner:
                        raise ValueError(
                            f"{param_name} owner does not match expected owner."
                        )

                def _NormalizeMultiString(self, value):
                    if value is None:
                        return None
                    if value == "***":
                        return ""
                    return value

            operations = MockOperations(project)
        else:
            operations = operations_class(project)

        self.project = project
        self.operations = operations
        return operations

    # ========== ASSERTION HELPERS ==========

    def assert_write_enabled_error(self, func, *args, **kwargs):
        """
        Assert that function raises exception for read-only project.

        Args:
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func

        Raises:
            AssertionError: If function does not raise appropriate error
        """
        with pytest.raises(Exception) as exc_info:
            func(*args, **kwargs)

        error_msg = str(exc_info.value).lower()
        assert "read-only" in error_msg, (
            f"Expected read-only error, got: {exc_info.value}"
        )

    def assert_param_error(self, func, *args, **kwargs):
        """
        Assert that function raises error for None parameter.

        Args:
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func

        Raises:
            AssertionError: If function does not raise appropriate error
        """
        with pytest.raises(Exception) as exc_info:
            func(*args, **kwargs)

        error_msg = str(exc_info.value)
        assert "cannot be None" in error_msg, (
            f"Expected 'cannot be None' error, got: {exc_info.value}"
        )

    def assert_empty_error(self, func, *args, **kwargs):
        """
        Assert that function raises error for empty parameter.

        Args:
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func

        Raises:
            AssertionError: If function does not raise appropriate error
        """
        with pytest.raises(Exception) as exc_info:
            func(*args, **kwargs)

        error_msg = str(exc_info.value)
        assert "cannot be empty" in error_msg, (
            f"Expected 'cannot be empty' error, got: {exc_info.value}"
        )

    def assert_type_error(self, func, *args, **kwargs):
        """
        Assert that function raises TypeError.

        Args:
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func

        Returns:
            The exception message

        Raises:
            AssertionError: If function does not raise TypeError
        """
        with pytest.raises(TypeError) as exc_info:
            func(*args, **kwargs)

        return str(exc_info.value)

    def assert_index_error(self, func, *args, **kwargs):
        """
        Assert that function raises IndexError.

        Args:
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func

        Returns:
            The exception message

        Raises:
            AssertionError: If function does not raise IndexError
        """
        with pytest.raises(IndexError) as exc_info:
            func(*args, **kwargs)

        error_msg = str(exc_info.value)
        assert "out of bounds" in error_msg, (
            f"Expected 'out of bounds' error, got: {exc_info.value}"
        )
        return error_msg

    def assert_value_error(self, func, *args, **kwargs):
        """
        Assert that function raises ValueError.

        Args:
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func

        Returns:
            The exception message

        Raises:
            AssertionError: If function does not raise ValueError
        """
        with pytest.raises(ValueError) as exc_info:
            func(*args, **kwargs)

        return str(exc_info.value)

    def assert_attribute_error(self, func, *args, **kwargs):
        """
        Assert that function raises AttributeError.

        Args:
            func: Callable to execute
            *args, **kwargs: Arguments to pass to func

        Returns:
            The exception message

        Raises:
            AssertionError: If function does not raise AttributeError
        """
        with pytest.raises(AttributeError) as exc_info:
            func(*args, **kwargs)

        return str(exc_info.value)

    # ========== MOCK OBJECT CREATION ==========

    def create_mock_entry(self, entry_id="test-entry"):
        """
        Create a mock ILexEntry object.

        Args:
            entry_id: Entry identifier

        Returns:
            Mock ILexEntry
        """
        entry = Mock()
        entry.Id = entry_id
        entry.Hvo = 1001
        entry.SensesOS = Mock()
        entry.SensesOS.Count = 3
        return entry

    def create_mock_sense(self, sense_id="test-sense", owner=None):
        """
        Create a mock ILexSense object.

        Args:
            sense_id: Sense identifier
            owner: Owner entry (optional)

        Returns:
            Mock ILexSense
        """
        sense = Mock()
        sense.Id = sense_id
        sense.Hvo = 1002
        sense.Owner = owner
        return sense

    def create_mock_writing_system(self, lang_tag="en"):
        """
        Create a mock IWritingSystemDefinition object.

        Args:
            lang_tag: Language tag (e.g., "en", "fr")

        Returns:
            Mock IWritingSystemDefinition
        """
        ws = Mock()
        ws.Id = lang_tag
        ws.Handle = 1
        return ws

    # ========== TEST DATA MANAGEMENT ==========

    def store_test_object(self, name, obj):
        """
        Store test object for later reference.

        Args:
            name: Name to store object under
            obj: Object to store
        """
        self.test_objects[name] = obj

    def get_test_object(self, name):
        """
        Retrieve stored test object.

        Args:
            name: Name of stored object

        Returns:
            Stored object or None
        """
        return self.test_objects.get(name)


# ========== COMMON TEST PATTERNS ==========

class WriteEnabledTestsMixin:
    """Mixin with write-enabled test patterns."""

    @pytest.mark.validation
    @pytest.mark.write_enabled
    def test_ensure_write_enabled_passes_when_writable(self):
        """Test that _EnsureWriteEnabled passes when project is writable."""
        ops = self.create_operations(write_enabled=True)
        # Should not raise
        ops._EnsureWriteEnabled()

    @pytest.mark.validation
    @pytest.mark.write_enabled
    def test_ensure_write_enabled_fails_when_read_only(self):
        """Test that _EnsureWriteEnabled fails when project is read-only."""
        ops = self.create_operations(write_enabled=False)
        self.assert_write_enabled_error(ops._EnsureWriteEnabled)


class ParameterValidationTestsMixin:
    """Mixin with parameter validation test patterns."""

    @pytest.mark.validation
    @pytest.mark.parameter_validation
    def test_validate_param_passes_with_valid_object(self):
        """Test that _ValidateParam passes with valid object."""
        ops = self.create_operations()
        test_obj = Mock()
        # Should not raise
        ops._ValidateParam(test_obj, "test_object")

    @pytest.mark.validation
    @pytest.mark.parameter_validation
    def test_validate_param_fails_with_none(self):
        """Test that _ValidateParam fails with None."""
        ops = self.create_operations()
        self.assert_param_error(ops._ValidateParam, None, "test_param")


class StringValidationTestsMixin:
    """Mixin with string validation test patterns."""

    @pytest.mark.validation
    @pytest.mark.string_validation
    def test_validate_string_passes_with_text(self):
        """Test that _ValidateStringNotEmpty passes with valid text."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateStringNotEmpty("valid text", "test_string")

    @pytest.mark.validation
    @pytest.mark.string_validation
    def test_validate_string_fails_with_empty(self):
        """Test that _ValidateStringNotEmpty fails with empty string."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "", "test_string")

    @pytest.mark.validation
    @pytest.mark.string_validation
    def test_validate_string_fails_with_whitespace(self):
        """Test that _ValidateStringNotEmpty fails with whitespace-only."""
        ops = self.create_operations()
        self.assert_empty_error(ops._ValidateStringNotEmpty, "   ", "test_string")

    @pytest.mark.validation
    @pytest.mark.string_validation
    def test_validate_string_fails_with_none(self):
        """Test that _ValidateStringNotEmpty fails with None."""
        ops = self.create_operations()
        # This should raise TypeError for None (not a string)
        self.assert_type_error(ops._ValidateStringNotEmpty, None, "test_string")


class IndexBoundsTestsMixin:
    """Mixin with index bounds validation test patterns."""

    @pytest.mark.validation
    @pytest.mark.bounds_checking
    def test_validate_index_passes_with_valid_index(self):
        """Test that _ValidateIndexBounds passes with valid index."""
        ops = self.create_operations()
        # Should not raise
        ops._ValidateIndexBounds(0, 5, "test_index")
        ops._ValidateIndexBounds(2, 5, "test_index")
        ops._ValidateIndexBounds(4, 5, "test_index")

    @pytest.mark.validation
    @pytest.mark.bounds_checking
    def test_validate_index_fails_with_negative(self):
        """Test that _ValidateIndexBounds fails with negative index."""
        ops = self.create_operations()
        self.assert_value_error(ops._ValidateIndexBounds, -1, 5, "test_index")

    @pytest.mark.validation
    @pytest.mark.bounds_checking
    def test_validate_index_fails_with_out_of_bounds(self):
        """Test that _ValidateIndexBounds fails with index >= max_count."""
        ops = self.create_operations()
        self.assert_index_error(ops._ValidateIndexBounds, 5, 5, "test_index")
        self.assert_index_error(ops._ValidateIndexBounds, 10, 5, "test_index")
