# Shared utilities module for flexlibs
# Contains cross-cutting infrastructure used by multiple modules

from .string_utils import (
    normalize_text,
    is_empty_text,
    best_analysis_text,
    best_vernacular_text,
    best_text,
    FLEX_NULL_MARKER,
)

__all__ = [
    'normalize_text',
    'is_empty_text',
    'best_analysis_text',
    'best_vernacular_text',
    'best_text',
    'FLEX_NULL_MARKER',
]
