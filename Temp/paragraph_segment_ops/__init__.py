"""
Paragraph and Segment Operations Module

This module provides advanced operations for paragraphs and segments in FLEx projects.

Includes:
- Cluster 1.4: Paragraph Advanced Operations (translations, notes, styles)
- Cluster 1.5: Segment Operations (baseline text, translations, analyses, notes)

Author: FlexTools Development Team
Date: 2025-11-22
"""

from .paragraph_advanced import (
    paragraph_get_translations,
    paragraph_set_translation,
    paragraph_get_notes,
    paragraph_add_note,
    paragraph_get_style_name,
)

from .segment_ops import (
    segment_get_all,
    segment_get_analyses,
    segment_get_baseline_text,
    segment_set_baseline_text,
    segment_get_free_translation,
    segment_set_free_translation,
    segment_get_literal_translation,
    segment_set_literal_translation,
    segment_get_notes,
)

__all__ = [
    # Paragraph Advanced Operations
    'paragraph_get_translations',
    'paragraph_set_translation',
    'paragraph_get_notes',
    'paragraph_add_note',
    'paragraph_get_style_name',
    # Segment Operations
    'segment_get_all',
    'segment_get_analyses',
    'segment_get_baseline_text',
    'segment_set_baseline_text',
    'segment_get_free_translation',
    'segment_set_free_translation',
    'segment_get_literal_translation',
    'segment_set_literal_translation',
    'segment_get_notes',
]
