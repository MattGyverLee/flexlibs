"""
Core Exception Classes

This module provides custom exception classes used across flexlibs modules.

Author: FlexTools Development Team
Date: 2025-11-22
"""


class FlexLibsError(Exception):
    """Base exception for all flexlibs errors."""
    pass


class ObjectNotFoundError(FlexLibsError, ValueError):
    """
    Raised when a FLEx object cannot be found.

    This combines FlexLibsError with ValueError for backwards compatibility.
    """

    def __init__(self, obj_type: str, identifier):
        self.obj_type = obj_type
        self.identifier = identifier
        super().__init__(f"{obj_type} not found: {identifier}")


class InvalidParameterError(FlexLibsError, ValueError):
    """
    Raised when a parameter has an invalid value.

    This combines FlexLibsError with ValueError for backwards compatibility.
    """
    pass


class DuplicateObjectError(FlexLibsError, RuntimeError):
    """
    Raised when attempting to create an object that already exists.

    This combines FlexLibsError with RuntimeError for backwards compatibility.
    """

    def __init__(self, obj_type: str, identifier):
        self.obj_type = obj_type
        self.identifier = identifier
        super().__init__(f"{obj_type} already exists: {identifier}")


class OperationFailedError(FlexLibsError, RuntimeError):
    """
    Raised when a FLEx operation fails.

    This combines FlexLibsError with RuntimeError for backwards compatibility.
    """
    pass


class ObjectInUseError(FlexLibsError, RuntimeError):
    """
    Raised when attempting to delete an object that is in use.

    This combines FlexLibsError with RuntimeError for backwards compatibility.
    """

    def __init__(self, obj_type: str, reason: str):
        self.obj_type = obj_type
        self.reason = reason
        super().__init__(f"Cannot delete {obj_type}: {reason}")


class WritingSystemError(FlexLibsError, ValueError):
    """
    Raised when a writing system operation fails.

    This combines FlexLibsError with ValueError for backwards compatibility.
    """
    pass


class NotImplementedYetError(FlexLibsError, NotImplementedError):
    """
    Raised when a feature is not yet implemented.

    This is temporary and should be removed as FLEx API integration is completed.
    """

    def __init__(self, feature: str = "FLEx API integration"):
        super().__init__(f"{feature} is not yet implemented")


__all__ = [
    'FlexLibsError',
    'ObjectNotFoundError',
    'InvalidParameterError',
    'DuplicateObjectError',
    'OperationFailedError',
    'ObjectInUseError',
    'WritingSystemError',
    'NotImplementedYetError',
]
