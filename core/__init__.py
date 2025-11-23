"""
Core Utilities Module

This module provides shared utilities used across all flexlibs modules:
- Type definitions and type aliases
- Resolver functions for converting HVOs to objects
- Validation utilities
- Custom exception classes
- Shared constants and enums

Author: FlexTools Development Team
Date: 2025-11-22
"""

from .types import (
    IText,
    IStText,
    IStTxtPara,
    ISegment,
    IAnalysis,
    IWfiWordform,
    IWfiAnalysis,
    IWfiGloss,
    ICmMedia,
    ICmFile,
    INote,
    ICmBaseAnnotation,
    ICmTranslation,
    ObjectOrHVO,
    WritingSystemHandle,
    HVO,
    FlexObject,
    FlexProject,
    OptionalText,
    OptionalParagraph,
    OptionalSegment,
    OptionalWordform,
)

from .resolvers import (
    resolve_object,
    resolve_text,
    resolve_paragraph,
    resolve_segment,
    resolve_wordform,
    resolve_analysis,
)

from .validators import (
    validate_non_empty_string,
    validate_object_exists,
    validate_index_in_range,
    validate_writing_system,
    validate_enum_value,
)

from .exceptions import (
    FlexLibsError,
    ObjectNotFoundError,
    InvalidParameterError,
    DuplicateObjectError,
    OperationFailedError,
    ObjectInUseError,
    WritingSystemError,
    NotImplementedYetError,
)

from .constants import (
    SpellingStatusStates,
    API_INTEGRATION_STATUS,
    CORE_VERSION,
)


__all__ = [
    # Types
    'IText',
    'IStText',
    'IStTxtPara',
    'ISegment',
    'IAnalysis',
    'IWfiWordform',
    'IWfiAnalysis',
    'IWfiGloss',
    'ICmMedia',
    'ICmFile',
    'INote',
    'ICmBaseAnnotation',
    'ICmTranslation',
    'ObjectOrHVO',
    'WritingSystemHandle',
    'HVO',
    'FlexObject',
    'FlexProject',
    'OptionalText',
    'OptionalParagraph',
    'OptionalSegment',
    'OptionalWordform',

    # Resolvers
    'resolve_object',
    'resolve_text',
    'resolve_paragraph',
    'resolve_segment',
    'resolve_wordform',
    'resolve_analysis',

    # Validators
    'validate_non_empty_string',
    'validate_object_exists',
    'validate_index_in_range',
    'validate_writing_system',
    'validate_enum_value',

    # Exceptions
    'FlexLibsError',
    'ObjectNotFoundError',
    'InvalidParameterError',
    'DuplicateObjectError',
    'OperationFailedError',
    'ObjectInUseError',
    'WritingSystemError',
    'NotImplementedYetError',

    # Constants
    'SpellingStatusStates',
    'API_INTEGRATION_STATUS',
    'CORE_VERSION',
]

__version__ = CORE_VERSION
