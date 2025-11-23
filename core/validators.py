"""
Core Validation Functions

This module provides shared validation utilities used across all flexlibs modules.

Author: FlexTools Development Team
Date: 2025-11-22
"""

from typing import Any, Union
from .exceptions import InvalidParameterError, ObjectNotFoundError


def validate_non_empty_string(value: str, param_name: str = "text") -> None:
    """
    Validate that a string is not empty or whitespace-only.

    Args:
        value: The string to validate
        param_name: Name of the parameter for error messages

    Raises:
        ValueError: If the string is empty or contains only whitespace

    Example:
        >>> validate_non_empty_string(form, "wordform text")
        >>> # Raises ValueError if form is empty
    """
    if not value or not value.strip():
        raise InvalidParameterError(f"{param_name} cannot be empty")


def validate_object_exists(obj: Any, identifier: Union[str, int], obj_type: str = "Object") -> None:
    """
    Validate that an object exists (is not None).

    Args:
        obj: The object to check
        identifier: The identifier used to find the object (for error messages)
        obj_type: Type name for error messages (e.g., "Text", "Paragraph")

    Raises:
        ValueError: If the object is None

    Example:
        >>> text_obj = resolve_text(text_or_hvo, self.project)
        >>> validate_object_exists(text_obj, text_or_hvo, "Text")
    """
    if obj is None:
        raise ObjectNotFoundError(obj_type, identifier)


def validate_index_in_range(index: int, max_index: int, allow_append: bool = False) -> None:
    """
    Validate that an index is within a valid range.

    Args:
        index: The index to validate
        max_index: The maximum valid index (exclusive)
        allow_append: If True, allows index == max_index (for append operations)

    Raises:
        ValueError: If the index is out of range

    Example:
        >>> validate_index_in_range(position, para_count, allow_append=True)
    """
    upper_bound = max_index + 1 if allow_append else max_index

    if index < 0 or index >= upper_bound:
        range_str = f"0-{max_index}" if not allow_append else f"0-{max_index} (or {max_index} to append)"
        raise InvalidParameterError(f"Index {index} out of range ({range_str})")


def validate_writing_system(ws_handle: Union[str, int]) -> None:
    """
    Validate a writing system handle.

    Args:
        ws_handle: Writing system handle to validate (string tag or int ID)

    Raises:
        ValueError: If the writing system handle is invalid

    Example:
        >>> validate_writing_system(ws_handle)

    Note:
        Currently just checks for None. Full validation requires FLEx API integration.
    """
    if ws_handle is None:
        raise InvalidParameterError("Writing system handle cannot be None")


def validate_enum_value(value: Any, enum_class: type, param_name: str = "value") -> None:
    """
    Validate that a value is a valid enum member.

    Args:
        value: The value to validate
        enum_class: The enum class to check against
        param_name: Parameter name for error messages

    Raises:
        ValueError: If the value is not a member of the enum

    Example:
        >>> validate_enum_value(status, SpellingStatusStates, "status")
    """
    if not isinstance(value, enum_class):
        raise InvalidParameterError(f"{param_name} must be a {enum_class.__name__} enum value")


__all__ = [
    'validate_non_empty_string',
    'validate_object_exists',
    'validate_index_in_range',
    'validate_writing_system',
    'validate_enum_value',
]
