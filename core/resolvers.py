"""
Core Resolver Functions

This module provides shared resolver functions that convert HVO references
to FLEx objects. These are used across all modules to handle parameters
that can be either objects or integer HVOs.

Author: FlexTools Development Team
Date: 2025-11-22
"""

from typing import Union, Any, Optional
import clr
clr.AddReference("System")
import System

from .types import HVO


def resolve_object(obj_or_hvo: Union[Any, HVO], project: Any) -> Optional[Any]:
    """
    Resolve a reference to a FLEx object.

    This is a generic resolver that works with any FLEx object type.

    Handles both direct object parameters (returns as-is) and integer HVO (Heap Variable
    Object) IDs by looking them up via the FLEx API.

    Args:
        obj_or_hvo: Either a FLEx object or its HVO (integer identifier)
        project: The FLExProject instance for object lookups

    Returns:
        The FLEx object, or None if obj_or_hvo is None

    Raises:
        ValueError: If HVO not found in project
        TypeError: If obj_or_hvo is neither object nor int, or project doesn't have Object method

    Example:
        >>> obj = resolve_object(text_or_hvo, self.project)
        >>> if obj is None:
        ...     raise ValueError("Object not found")
    """
    # Handle None case
    if obj_or_hvo is None:
        return None

    # If not an integer, assume it's already an object
    if not isinstance(obj_or_hvo, int):
        return obj_or_hvo

    # If integer HVO, look up via FLEx API
    try:
        return project.Object(obj_or_hvo)
    except (KeyError, System.Collections.Generic.KeyNotFoundException) as e:
        raise ValueError(f"Object with HVO {obj_or_hvo} not found: {e}")
    except AttributeError as e:
        raise TypeError(f"project.Object() not available: {e}")


def resolve_text(text_or_hvo: Union[Any, HVO], project: Any) -> Optional[Any]:
    """
    Resolve a text reference to an IText object.

    Args:
        text_or_hvo: Either an IText object or its HVO (integer identifier)
        project: The FLExProject instance

    Returns:
        IText object or None if not found

    Example:
        >>> text_obj = resolve_text(text_or_hvo, self.project)
        >>> if text_obj is None:
        ...     raise ValueError(f"Text not found: {text_or_hvo}")
    """
    return resolve_object(text_or_hvo, project)


def resolve_paragraph(para_or_hvo: Union[Any, HVO], project: Any) -> Optional[Any]:
    """
    Resolve a paragraph reference to an IStTxtPara object.

    Args:
        para_or_hvo: Either an IStTxtPara object or its HVO (integer identifier)
        project: The FLExProject instance

    Returns:
        IStTxtPara object or None if not found

    Example:
        >>> para_obj = resolve_paragraph(para_or_hvo, self.project)
        >>> if para_obj is None:
        ...     raise ValueError(f"Paragraph not found: {para_or_hvo}")
    """
    return resolve_object(para_or_hvo, project)


def resolve_segment(segment_or_hvo: Union[Any, HVO], project: Any) -> Optional[Any]:
    """
    Resolve a segment reference to an ISegment object.

    Args:
        segment_or_hvo: Either an ISegment object or its HVO (integer identifier)
        project: The FLExProject instance

    Returns:
        ISegment object or None if not found

    Example:
        >>> segment_obj = resolve_segment(segment_or_hvo, self.project)
        >>> if segment_obj is None:
        ...     raise ValueError(f"Segment not found: {segment_or_hvo}")
    """
    return resolve_object(segment_or_hvo, project)


def resolve_wordform(wordform_or_hvo: Union[Any, HVO], project: Any) -> Optional[Any]:
    """
    Resolve a wordform reference to an IWfiWordform object.

    Args:
        wordform_or_hvo: Either an IWfiWordform object or its HVO (integer identifier)
        project: The FLExProject instance

    Returns:
        IWfiWordform object or None if not found

    Example:
        >>> wordform_obj = resolve_wordform(wordform_or_hvo, self.project)
        >>> if wordform_obj is None:
        ...     raise ValueError(f"Wordform not found: {wordform_or_hvo}")
    """
    return resolve_object(wordform_or_hvo, project)


def resolve_analysis(analysis_or_hvo: Union[Any, HVO], project: Any) -> Optional[Any]:
    """
    Resolve an analysis reference to an IWfiAnalysis object.

    Args:
        analysis_or_hvo: Either an IWfiAnalysis object or its HVO (integer identifier)
        project: The FLExProject instance

    Returns:
        IWfiAnalysis object or None if not found

    Example:
        >>> analysis_obj = resolve_analysis(analysis_or_hvo, self.project)
        >>> if analysis_obj is None:
        ...     raise ValueError(f"Analysis not found: {analysis_or_hvo}")
    """
    return resolve_object(analysis_or_hvo, project)


# Phase 2 Resolvers

def resolve_pos(pos_or_hvo: Union[Any, HVO], project: Any) -> Optional[Any]:
    """
    Resolve a part of speech reference to an IPartOfSpeech object.

    Args:
        pos_or_hvo: Either an IPartOfSpeech object or its HVO
        project: The FLExProject instance

    Returns:
        IPartOfSpeech object or None if not found
    """
    return resolve_object(pos_or_hvo, project)


def resolve_phoneme(phoneme_or_hvo: Union[Any, HVO], project: Any) -> Optional[Any]:
    """
    Resolve a phoneme reference to an IPhPhoneme object.

    Args:
        phoneme_or_hvo: Either an IPhPhoneme object or its HVO
        project: The FLExProject instance

    Returns:
        IPhPhoneme object or None if not found
    """
    return resolve_object(phoneme_or_hvo, project)


def resolve_natural_class(nc_or_hvo: Union[Any, HVO], project: Any) -> Optional[Any]:
    """
    Resolve a natural class reference to an IPhNaturalClass object.

    Args:
        nc_or_hvo: Either an IPhNaturalClass object or its HVO
        project: The FLExProject instance

    Returns:
        IPhNaturalClass object or None if not found
    """
    return resolve_object(nc_or_hvo, project)


def resolve_environment(env_or_hvo: Union[Any, HVO], project: Any) -> Optional[Any]:
    """
    Resolve a phonological environment reference to an IPhEnvironment object.

    Args:
        env_or_hvo: Either an IPhEnvironment object or its HVO
        project: The FLExProject instance

    Returns:
        IPhEnvironment object or None if not found
    """
    return resolve_object(env_or_hvo, project)


def resolve_allomorph(allomorph_or_hvo: Union[Any, HVO], project: Any) -> Optional[Any]:
    """
    Resolve an allomorph reference to an IMoForm object.

    Args:
        allomorph_or_hvo: Either an IMoForm object or its HVO
        project: The FLExProject instance

    Returns:
        IMoForm object or None if not found
    """
    return resolve_object(allomorph_or_hvo, project)


def resolve_possibility(poss_or_hvo: Union[Any, HVO], project: Any) -> Optional[Any]:
    """
    Resolve a possibility list item reference to an ICmPossibility object.

    Args:
        poss_or_hvo: Either an ICmPossibility object or its HVO
        project: The FLExProject instance

    Returns:
        ICmPossibility object or None if not found
    """
    return resolve_object(poss_or_hvo, project)


__all__ = [
    # Phase 1 resolvers
    'resolve_object',
    'resolve_text',
    'resolve_paragraph',
    'resolve_segment',
    'resolve_wordform',
    'resolve_analysis',

    # Phase 2 resolvers
    'resolve_pos',
    'resolve_phoneme',
    'resolve_natural_class',
    'resolve_environment',
    'resolve_allomorph',
    'resolve_possibility',
]
