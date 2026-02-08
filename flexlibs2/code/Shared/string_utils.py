# -*- coding: utf-8 -*-
#
#   flexlibs2.code.Shared.string_utils
#
#   String utility functions for FlexLibs2.
#
#   FLEx/LCM uses '***' as a placeholder when multilingual string fields
#   have no value set. This module provides utilities to normalize these
#   values to empty strings, matching the behavior of FlexLibs stable.
#

# FLEx's null marker for empty multilingual string fields
FLEX_NULL_MARKER = "***"


def normalize_text(text):
    """
    Normalize a text value from LCM, converting FLEx's null marker to empty string.

    FLEx/LCM uses '***' as a placeholder when multilingual string fields
    (IMultiString, IMultiUnicode) have no value set. This function normalizes
    such values to empty strings for consistent handling.

    Args:
        text: A string value from an LCM text field, or None

    Returns:
        The original text if it has content, or "" if None/empty/'***'

    Example:
        >>> from flexlibs2.code.Shared.string_utils import normalize_text
        >>> normalize_text("***")
        ''
        >>> normalize_text(None)
        ''
        >>> normalize_text("hello")
        'hello'
        >>> normalize_text("")
        ''
    """
    if text is None:
        return ""
    if text == FLEX_NULL_MARKER:
        return ""
    return text


def is_empty_text(text):
    """
    Check if a text value from LCM is empty (None, empty string, or '***').

    Args:
        text: A string value from an LCM text field, or None

    Returns:
        True if the text represents an empty/unset value

    Example:
        >>> from flexlibs2.code.Shared.string_utils import is_empty_text
        >>> is_empty_text("***")
        True
        >>> is_empty_text(None)
        True
        >>> is_empty_text("")
        True
        >>> is_empty_text("hello")
        False
    """
    if text is None:
        return True
    if not text or text == FLEX_NULL_MARKER:
        return True
    return False


def best_analysis_text(multi_obj):
    """
    Get the best analysis alternative text from an IMultiString/IMultiUnicode,
    normalized to empty string if unset.

    This combines accessing .BestAnalysisAlternative.Text with null marker handling.

    Args:
        multi_obj: An IMultiString or IMultiUnicode object, or None

    Returns:
        The text content, or "" if None/empty/'***'

    Example:
        >>> text = best_analysis_text(sense.Definition)
        >>> text = best_analysis_text(pos.Name)
    """
    if multi_obj is None:
        return ""
    text = multi_obj.BestAnalysisAlternative.Text
    return normalize_text(text)


def best_vernacular_text(multi_obj):
    """
    Get the best vernacular alternative text from an IMultiString/IMultiUnicode,
    normalized to empty string if unset.

    This combines accessing .BestVernacularAlternative.Text with null marker handling.

    Args:
        multi_obj: An IMultiString or IMultiUnicode object, or None

    Returns:
        The text content, or "" if None/empty/'***'

    Example:
        >>> text = best_vernacular_text(entry.LexemeFormOA.Form)
    """
    if multi_obj is None:
        return ""
    text = multi_obj.BestVernacularAlternative.Text
    return normalize_text(text)


def best_text(multi_obj):
    """
    Get the best analysis-or-vernacular alternative text from an IMultiString/IMultiUnicode,
    normalized to empty string if unset.

    This combines accessing .BestAnalysisVernacularAlternative.Text with null marker handling.
    Prefers analysis writing system, falls back to vernacular.

    Args:
        multi_obj: An IMultiString or IMultiUnicode object, or None

    Returns:
        The text content, or "" if None/empty/'***'

    Example:
        >>> text = best_text(sense.Gloss)
    """
    if multi_obj is None:
        return ""
    text = multi_obj.BestAnalysisVernacularAlternative.Text
    return normalize_text(text)
