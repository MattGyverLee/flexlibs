#
# test_helpers.py
#
# Utility functions and factory classes for FlexLibs2 validation tests
#
# Provides:
# - Factory functions for creating test objects
# - Error message validators
# - Exception type checkers
# - Common test patterns and utilities
#
# Platform: Python.NET
#           FieldWorks Version 9+
#
# Copyright 2025
#

from unittest.mock import Mock
import re


# ========== FACTORY FUNCTIONS ==========

def create_mock_entry(entry_id="test-entry", num_senses=3, num_allomorphs=2):
    """
    Create a mock ILexEntry object with specified properties.

    Args:
        entry_id: Entry identifier string
        num_senses: Number of senses to mock
        num_allomorphs: Number of allomorphs to mock

    Returns:
        Mock ILexEntry with SensesOS and AlternateFormsOS collections
    """
    entry = Mock()
    entry.Id = entry_id
    entry.Hvo = 1001
    entry.SensesOS = Mock()
    entry.SensesOS.Count = num_senses
    entry.AlternateFormsOS = Mock()
    entry.AlternateFormsOS.Count = num_allomorphs
    entry.Owner = None
    return entry


def create_mock_sense(sense_id="test-sense", owner=None, num_examples=2):
    """
    Create a mock ILexSense object with specified properties.

    Args:
        sense_id: Sense identifier string
        owner: Owner entry (ILexEntry mock)
        num_examples: Number of examples to mock

    Returns:
        Mock ILexSense with ExamplesOS collection
    """
    sense = Mock()
    sense.Id = sense_id
    sense.Hvo = 1002
    sense.Owner = owner
    sense.Gloss = Mock()
    sense.Definition = Mock()
    sense.ExamplesOS = Mock()
    sense.ExamplesOS.Count = num_examples
    return sense


def create_mock_writing_system(lang_tag="en", language_name="English", handle=1):
    """
    Create a mock IWritingSystemDefinition object.

    Args:
        lang_tag: BCP 47 language tag (e.g., "en", "fr")
        language_name: Display name for the writing system
        handle: Writing system handle

    Returns:
        Mock IWritingSystemDefinition
    """
    ws = Mock()
    ws.Id = lang_tag
    ws.LanguageName = language_name
    ws.Handle = handle
    return ws


def create_mock_allomorph(allo_id="test-allo", owner=None):
    """
    Create a mock IMoAllomorph object.

    Args:
        allo_id: Allomorph identifier string
        owner: Owner entry (ILexEntry mock)

    Returns:
        Mock IMoAllomorph
    """
    allo = Mock()
    allo.Id = allo_id
    allo.Hvo = 1003
    allo.Owner = owner
    allo.Form = Mock()
    return allo


def create_mock_example(example_id="test-example", owner=None):
    """
    Create a mock IExample object.

    Args:
        example_id: Example identifier string
        owner: Owner sense (ILexSense mock)

    Returns:
        Mock IExample
    """
    example = Mock()
    example.Id = example_id
    example.Hvo = 1004
    example.Owner = owner
    example.Example = Mock()
    return example


# ========== ERROR VALIDATORS ==========

class ErrorValidator:
    """Validator for exception messages and types."""

    @staticmethod
    def contains_text(error_msg, text, case_sensitive=False):
        """
        Check if error message contains specific text.

        Args:
            error_msg: Error message string
            text: Text to search for
            case_sensitive: If False, comparison is case-insensitive

        Returns:
            bool: True if text is found in error_msg
        """
        if case_sensitive:
            return text in error_msg
        else:
            return text.lower() in error_msg.lower()

    @staticmethod
    def matches_pattern(error_msg, pattern):
        """
        Check if error message matches regex pattern.

        Args:
            error_msg: Error message string
            pattern: Regular expression pattern

        Returns:
            bool: True if pattern matches
        """
        return re.search(pattern, error_msg) is not None

    @staticmethod
    def is_read_only_error(error_msg):
        """
        Check if error is about read-only project.

        Args:
            error_msg: Error message string

        Returns:
            bool: True if error mentions read-only
        """
        return ErrorValidator.contains_text(error_msg, "read-only")

    @staticmethod
    def is_none_error(error_msg):
        """
        Check if error is about None parameter.

        Args:
            error_msg: Error message string

        Returns:
            bool: True if error mentions None
        """
        return ErrorValidator.contains_text(error_msg, "cannot be None")

    @staticmethod
    def is_empty_error(error_msg):
        """
        Check if error is about empty parameter.

        Args:
            error_msg: Error message string

        Returns:
            bool: True if error mentions empty
        """
        return ErrorValidator.contains_text(error_msg, "cannot be empty")

    @staticmethod
    def is_type_error(error_msg):
        """
        Check if error is about type mismatch.

        Args:
            error_msg: Error message string

        Returns:
            bool: True if error mentions type
        """
        return ErrorValidator.contains_text(error_msg, "must be")

    @staticmethod
    def is_bounds_error(error_msg):
        """
        Check if error is about index bounds.

        Args:
            error_msg: Error message string

        Returns:
            bool: True if error mentions bounds
        """
        return ErrorValidator.contains_text(error_msg, "out of bounds")

    @staticmethod
    def is_owner_error(error_msg):
        """
        Check if error is about object ownership.

        Args:
            error_msg: Error message string

        Returns:
            bool: True if error mentions owner
        """
        return ErrorValidator.contains_text(error_msg, "owner")


# ========== EXCEPTION TYPE CHECKERS ==========

class ExceptionChecker:
    """Helper for checking exception types and properties."""

    @staticmethod
    def is_read_only_exception(exc):
        """
        Check if exception is for read-only project.

        Args:
            exc: Exception instance

        Returns:
            bool: True if exception is read-only error
        """
        error_msg = str(exc).lower()
        return "read-only" in error_msg or "writeenabled" in error_msg

    @staticmethod
    def is_parameter_exception(exc):
        """
        Check if exception is for invalid parameter.

        Args:
            exc: Exception instance

        Returns:
            bool: True if exception is parameter error
        """
        error_msg = str(exc)
        return "cannot be None" in error_msg or "cannot be empty" in error_msg

    @staticmethod
    def is_type_exception(exc):
        """
        Check if exception is TypeError.

        Args:
            exc: Exception instance

        Returns:
            bool: True if exception is TypeError
        """
        return isinstance(exc, TypeError)

    @staticmethod
    def is_index_exception(exc):
        """
        Check if exception is IndexError.

        Args:
            exc: Exception instance

        Returns:
            bool: True if exception is IndexError
        """
        return isinstance(exc, IndexError)

    @staticmethod
    def is_value_exception(exc):
        """
        Check if exception is ValueError.

        Args:
            exc: Exception instance

        Returns:
            bool: True if exception is ValueError
        """
        return isinstance(exc, ValueError)

    @staticmethod
    def is_attribute_exception(exc):
        """
        Check if exception is AttributeError.

        Args:
            exc: Exception instance

        Returns:
            bool: True if exception is AttributeError
        """
        return isinstance(exc, AttributeError)

    @staticmethod
    def get_exception_chain(exc):
        """
        Get chain of exceptions from __cause__.

        Args:
            exc: Exception instance

        Returns:
            List of exceptions in chain
        """
        chain = [exc]
        current = exc
        while current.__cause__ is not None:
            current = current.__cause__
            chain.append(current)
        return chain


# ========== TEST DATA BUILDERS ==========

class TestDataBuilder:
    """Builder for creating complex test data structures."""

    def __init__(self):
        """Initialize builder."""
        self.entries = []
        self.senses = []
        self.writing_systems = []

    def add_entry(self, entry_id=None, num_senses=3):
        """
        Add entry to test data.

        Args:
            entry_id: Entry ID (auto-generated if None)
            num_senses: Number of senses to create

        Returns:
            self (for chaining)
        """
        if entry_id is None:
            entry_id = f"entry-{len(self.entries)}"

        entry = create_mock_entry(entry_id, num_senses)
        self.entries.append(entry)
        return self

    def add_sense(self, sense_id=None, owner_idx=0):
        """
        Add sense to test data.

        Args:
            sense_id: Sense ID (auto-generated if None)
            owner_idx: Index of entry owner

        Returns:
            self (for chaining)
        """
        if sense_id is None:
            sense_id = f"sense-{len(self.senses)}"

        owner = self.entries[owner_idx] if owner_idx < len(self.entries) else None
        sense = create_mock_sense(sense_id, owner)
        self.senses.append(sense)
        return self

    def add_writing_system(self, lang_tag=None):
        """
        Add writing system to test data.

        Args:
            lang_tag: Language tag

        Returns:
            self (for chaining)
        """
        tags = ["en", "fr", "es", "pt", "de"]
        if lang_tag is None:
            lang_tag = tags[len(self.writing_systems) % len(tags)]

        ws = create_mock_writing_system(lang_tag)
        self.writing_systems.append(ws)
        return self

    def build(self):
        """
        Build and return test data.

        Returns:
            Dict with entries, senses, writing_systems
        """
        return {
            "entries": self.entries,
            "senses": self.senses,
            "writing_systems": self.writing_systems,
        }

    def reset(self):
        """Reset builder state."""
        self.entries.clear()
        self.senses.clear()
        self.writing_systems.clear()
        return self


# ========== ASSERTION HELPERS ==========

class AssertionHelper:
    """Helper methods for common test assertions."""

    @staticmethod
    def assert_error_contains(exc, expected_text, case_sensitive=False):
        """
        Assert that exception message contains expected text.

        Args:
            exc: Exception instance
            expected_text: Text that should be in error message
            case_sensitive: If False, comparison is case-insensitive

        Raises:
            AssertionError: If text not found in error message
        """
        error_msg = str(exc)
        validator = ErrorValidator()
        assert validator.contains_text(error_msg, expected_text, case_sensitive), (
            f"Expected '{expected_text}' in error message, got: {error_msg}"
        )

    @staticmethod
    def assert_valid_object_at_index(obj, index, expected_id=None):
        """
        Assert that object at index has valid properties.

        Args:
            obj: Object to check
            index: Index of object
            expected_id: Optional expected ID

        Raises:
            AssertionError: If object is invalid
        """
        assert obj is not None, f"Object at index {index} is None"
        assert hasattr(obj, "Hvo"), f"Object at index {index} missing Hvo"
        if expected_id:
            assert obj.Id == expected_id, (
                f"Object at index {index} has Id {obj.Id}, "
                f"expected {expected_id}"
            )

    @staticmethod
    def assert_collection_size(collection, expected_size):
        """
        Assert that collection has expected size.

        Args:
            collection: Collection to check
            expected_size: Expected number of items

        Raises:
            AssertionError: If size does not match
        """
        actual_size = len(collection)
        assert actual_size == expected_size, (
            f"Collection size {actual_size} does not match expected {expected_size}"
        )


# ========== TEST RESULT REPORTERS ==========

class TestResultReporter:
    """Helper for reporting test results and coverage."""

    def __init__(self):
        """Initialize reporter."""
        self.results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
        }

    def record_pass(self):
        """Record a passed test."""
        self.results["passed"] += 1

    def record_fail(self, error_msg):
        """Record a failed test."""
        self.results["failed"] += 1
        self.results["errors"].append(error_msg)

    def record_skip(self):
        """Record a skipped test."""
        self.results["skipped"] += 1

    def get_summary(self):
        """Get summary of test results."""
        total = (
            self.results["passed"]
            + self.results["failed"]
            + self.results["skipped"]
        )
        return {
            "total": total,
            "passed": self.results["passed"],
            "failed": self.results["failed"],
            "skipped": self.results["skipped"],
            "pass_rate": (
                (self.results["passed"] / total * 100) if total > 0 else 0
            ),
        }

    def print_summary(self):
        """Print summary to console."""
        summary = self.get_summary()
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        print(f"Total:  {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        if self.results["errors"]:
            print("\nErrors:")
            for error in self.results["errors"]:
                print(f"  - {error}")
        print("=" * 50 + "\n")
