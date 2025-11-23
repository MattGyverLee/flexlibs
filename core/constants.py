"""
Core Constants and Enums

This module provides shared constants and enumerations used across flexlibs modules.

Author: FlexTools Development Team
Date: 2025-11-22
"""

from enum import IntEnum


class SpellingStatusStates(IntEnum):
    """
    Enumeration of possible spelling status states for wordforms.

    These correspond to the FLEx SpellingStatusStates enumeration.
    """
    UNDECIDED = 0
    INCORRECT = 1
    CORRECT = 2


# API integration status
API_INTEGRATION_STATUS = "pending"

# Version information
CORE_VERSION = "0.1.0"


__all__ = [
    'SpellingStatusStates',
    'API_INTEGRATION_STATUS',
    'CORE_VERSION',
]
