"""
Wordform Operations Module

This module provides comprehensive CRUD and advanced operations for wordforms
in FLEx (FieldWorks Language Explorer) projects.

Modules:
    wordform_crud: Basic CRUD operations (Cluster 1.6)
    wordform_advanced: Advanced operations (Cluster 1.7)
"""

from .wordform_crud import (
    wordform_get_all,
    wordform_create,
    wordform_delete,
    wordform_exists,
    wordform_find,
    wordform_get_form,
    wordform_set_form,
    wordform_get_spelling_status,
    wordform_set_spelling_status,
    wordform_get_analyses,
    SpellingStatusStates,
)

from .wordform_advanced import (
    wordform_get_occurrence_count,
    wordform_get_occurrences,
    wordform_get_checksum,
    wordform_get_all_with_status,
    wordform_get_all_unapproved,
    wordform_approve_spelling,
)

__all__ = [
    # CRUD operations (Cluster 1.6)
    'wordform_get_all',
    'wordform_create',
    'wordform_delete',
    'wordform_exists',
    'wordform_find',
    'wordform_get_form',
    'wordform_set_form',
    'wordform_get_spelling_status',
    'wordform_set_spelling_status',
    'wordform_get_analyses',
    'SpellingStatusStates',
    # Advanced operations (Cluster 1.7)
    'wordform_get_occurrence_count',
    'wordform_get_occurrences',
    'wordform_get_checksum',
    'wordform_get_all_with_status',
    'wordform_get_all_unapproved',
    'wordform_approve_spelling',
]
