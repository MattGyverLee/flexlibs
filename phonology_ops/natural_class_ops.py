"""
Natural Class Operations

This module provides operations for phonological natural classes in FLEx.

Natural classes are groups of phonemes that share common phonological features
and pattern together in phonological rules. For example, voiceless stops
{/p/, /t/, /k/} or vowels {/a/, /e/, /i/, /o/, /u/}.

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

from typing import Generator, List, Optional
from flexlibs_dev.core.types import (
    IPhNaturalClass,
    IPhPhoneme,
    HVO,
    WritingSystemHandle,
    OptionalNaturalClass,
)
from flexlibs_dev.core.resolvers import resolve_natural_class, resolve_phoneme
from flexlibs_dev.core.validators import validate_non_empty_string, validate_object_exists
from flexlibs_dev.core.exceptions import (
    ObjectNotFoundError,
    DuplicateObjectError,
    InvalidParameterError,
    NotImplementedYetError,
)


def NaturalClassGetAll() -> Generator[IPhNaturalClass, None, None]:
    """
    Get all natural classes in the phonological inventory.

    Yields:
        IPhNaturalClass: Each natural class in the project

    Example:
        >>> for nc in NaturalClassGetAll():
        ...     name = NaturalClassGetName(nc)
        ...     abbr = NaturalClassGetAbbreviation(nc)
        ...     phonemes = NaturalClassGetPhonemes(nc)
        ...     print(f"{name} ({abbr}): {len(phonemes)} phonemes")
        Voiceless Stops (VLS): 3 phonemes
        Voiced Stops (VCD): 3 phonemes
        Nasals (N): 3 phonemes
        Vowels (V): 5 phonemes
        High Vowels (HV): 2 phonemes

    Notes:
        - Returns natural classes in their defined order
        - Includes both segment-based and feature-based classes
        - Empty if no natural classes defined

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "NaturalClassGetAll requires FLEx API integration. "
        "Will iterate over project.PhonologicalDataOA.NaturalClassesOS"
    )
    # FLEx integration:
    # phon_data = project.PhonologicalDataOA
    # if phon_data:
    #     for nc in phon_data.NaturalClassesOS:
    #         yield nc


def NaturalClassCreate(name: str, abbreviation: str) -> IPhNaturalClass:
    """
    Create a new natural class.

    Args:
        name: The name of the natural class (e.g., "Voiceless Stops")
        abbreviation: Short abbreviation (e.g., "VLS", "V", "C")

    Returns:
        IPhNaturalClass: The newly created natural class object

    Raises:
        InvalidParameterError: If name or abbreviation is empty
        DuplicateObjectError: If a natural class with this name already exists

    Example:
        >>> # Create basic consonant classes
        >>> stops = NaturalClassCreate("Stops", "P")
        >>> fricatives = NaturalClassCreate("Fricatives", "F")
        >>> nasals = NaturalClassCreate("Nasals", "N")

        >>> # Create vowel classes
        >>> vowels = NaturalClassCreate("Vowels", "V")
        >>> high_vowels = NaturalClassCreate("High Vowels", "HV")
        >>> low_vowels = NaturalClassCreate("Low Vowels", "LV")

        >>> # Create feature-based classes
        >>> voiceless = NaturalClassCreate("Voiceless Consonants", "VLS")
        >>> voiced = NaturalClassCreate("Voiced Consonants", "VCD")

    Notes:
        - Name should be descriptive of the phonological property
        - Abbreviation used in rule notation (e.g., V → Ø / _C#)
        - After creation, use NaturalClassAddPhoneme() to add members
        - Can be segment-based or feature-based

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")
    validate_non_empty_string(abbreviation, "abbreviation")

    raise NotImplementedYetError(
        "NaturalClassCreate requires FLEx API integration. "
        "Will create new IPhNaturalClass in PhonologicalDataOA.NaturalClassesOS"
    )
    # FLEx integration:
    # from SIL.LCModel import IPhNCSegments, UndoableUnitOfWork
    # phon_data = project.PhonologicalDataOA
    # if not phon_data:
    #     raise OperationFailedError("No phonological data in project")
    #
    # with UndoableUnitOfWork(project, "Create Natural Class"):
    #     # Create segment-based natural class (most common)
    #     nc = project.ServiceLocator.GetInstance(IPhNCSegmentsFactory).Create()
    #     ws_handle = project.DefaultAnalysisWs
    #     nc.Name.set_String(ws_handle, name)
    #     nc.Abbreviation.set_String(ws_handle, abbreviation)
    #     phon_data.NaturalClassesOS.Append(nc)
    #     return nc


def NaturalClassDelete(nc_or_hvo: IPhNaturalClass | HVO) -> None:
    """
    Delete a natural class.

    Args:
        nc_or_hvo: The natural class object or its HVO to delete

    Raises:
        ObjectNotFoundError: If the natural class doesn't exist
        RuntimeError: If the natural class is in use and cannot be deleted

    Example:
        >>> nc = NaturalClassCreate("Obsolete", "OBS")
        >>> # ... realize it's not needed
        >>> NaturalClassDelete(nc)

    Warning:
        - Deleting a natural class that is in use will raise an error
        - This includes natural classes used in:
          - Phonological rules
          - Phonological environments
          - Other natural class definitions
        - Consider checking usage before deletion

    Notes:
        - Deletion is permanent and cannot be undone outside a transaction
        - Does not delete the phonemes in the class, only the class itself

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "NaturalClassDelete requires FLEx API integration. "
        "Will remove natural class from PhonologicalDataOA.NaturalClassesOS"
    )
    # FLEx integration:
    # nc_obj = resolve_natural_class(nc_or_hvo, project)
    # validate_object_exists(nc_obj, f"Natural Class {nc_or_hvo}")
    # phon_data = project.PhonologicalDataOA
    # with UndoableUnitOfWork(project, "Delete Natural Class"):
    #     phon_data.NaturalClassesOS.Remove(nc_obj)


def NaturalClassGetName(
    nc_or_hvo: IPhNaturalClass | HVO,
    wsHandle: Optional[WritingSystemHandle] = None
) -> str:
    """
    Get the name of a natural class.

    Args:
        nc_or_hvo: The natural class object or its HVO
        wsHandle: Optional writing system (defaults to analysis WS)

    Returns:
        str: The natural class name

    Raises:
        ObjectNotFoundError: If the natural class doesn't exist

    Example:
        >>> for nc in NaturalClassGetAll():
        ...     name = NaturalClassGetName(nc)
        ...     print(name)
        Voiceless Stops
        Voiced Stops
        Fricatives
        Nasals
        Vowels

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "NaturalClassGetName requires FLEx API integration. "
        "Will read nc.Name.get_String(ws_handle)"
    )
    # FLEx integration:
    # nc_obj = resolve_natural_class(nc_or_hvo, project)
    # validate_object_exists(nc_obj, f"Natural Class {nc_or_hvo}")
    # if wsHandle is None:
    #     wsHandle = project.DefaultAnalysisWs
    # return nc_obj.Name.get_String(wsHandle).Text


def NaturalClassSetName(
    nc_or_hvo: IPhNaturalClass | HVO,
    name: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> None:
    """
    Set the name of a natural class.

    Args:
        nc_or_hvo: The natural class object or its HVO
        name: The new name
        wsHandle: Optional writing system (defaults to analysis WS)

    Raises:
        InvalidParameterError: If name is empty
        ObjectNotFoundError: If the natural class doesn't exist

    Example:
        >>> nc = NaturalClassCreate("Plosives", "P")
        >>> # Prefer linguistic standard terminology
        >>> NaturalClassSetName(nc, "Stops")

    Notes:
        - Use standard phonological terminology
        - Name should reflect the shared phonological property

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")

    raise NotImplementedYetError(
        "NaturalClassSetName requires FLEx API integration. "
        "Will write to nc.Name.set_String(ws_handle, name)"
    )
    # FLEx integration:
    # nc_obj = resolve_natural_class(nc_or_hvo, project)
    # validate_object_exists(nc_obj, f"Natural Class {nc_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Natural Class Name"):
    #     if wsHandle is None:
    #         wsHandle = project.DefaultAnalysisWs
    #     nc_obj.Name.set_String(wsHandle, name)


def NaturalClassGetAbbreviation(
    nc_or_hvo: IPhNaturalClass | HVO,
    wsHandle: Optional[WritingSystemHandle] = None
) -> str:
    """
    Get the abbreviation of a natural class.

    Args:
        nc_or_hvo: The natural class object or its HVO
        wsHandle: Optional writing system (defaults to analysis WS)

    Returns:
        str: The natural class abbreviation

    Raises:
        ObjectNotFoundError: If the natural class doesn't exist

    Example:
        >>> nc = NaturalClassCreate("Voiceless Stops", "VLS")
        >>> abbr = NaturalClassGetAbbreviation(nc)
        >>> print(abbr)
        VLS

        >>> # Print rule using abbreviations
        >>> # Rule: VLS → VCD / V_V (voicing between vowels)
        >>> vls = NaturalClassFind("Voiceless Stops")
        >>> vcd = NaturalClassFind("Voiced Stops")
        >>> v = NaturalClassFind("Vowels")
        >>> print(f"{NaturalClassGetAbbreviation(vls)} → "
        ...       f"{NaturalClassGetAbbreviation(vcd)} / "
        ...       f"{NaturalClassGetAbbreviation(v)}_{NaturalClassGetAbbreviation(v)}")
        VLS → VCD / V_V

    Notes:
        - Abbreviations used in phonological rule notation
        - Standard abbreviations: V (vowel), C (consonant), N (nasal), etc.
        - Keep abbreviations short and mnemonic

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "NaturalClassGetAbbreviation requires FLEx API integration. "
        "Will read nc.Abbreviation.get_String(ws_handle)"
    )
    # FLEx integration:
    # nc_obj = resolve_natural_class(nc_or_hvo, project)
    # validate_object_exists(nc_obj, f"Natural Class {nc_or_hvo}")
    # if wsHandle is None:
    #     wsHandle = project.DefaultAnalysisWs
    # return nc_obj.Abbreviation.get_String(wsHandle).Text


def NaturalClassGetPhonemes(nc_or_hvo: IPhNaturalClass | HVO) -> List[IPhPhoneme]:
    """
    Get all phonemes in a natural class.

    Args:
        nc_or_hvo: The natural class object or its HVO

    Returns:
        List[IPhPhoneme]: List of phoneme objects in the class (empty if none)

    Raises:
        ObjectNotFoundError: If the natural class doesn't exist

    Example:
        >>> # Get members of voiceless stops
        >>> nc = NaturalClassFind("Voiceless Stops")
        >>> phonemes = NaturalClassGetPhonemes(nc)
        >>> for phoneme in phonemes:
        ...     print(PhonemeGetRepresentation(phoneme))
        /p/
        /t/
        /k/

        >>> # Print all natural classes with their members
        >>> for nc in NaturalClassGetAll():
        ...     name = NaturalClassGetName(nc)
        ...     phonemes = NaturalClassGetPhonemes(nc)
        ...     members = [PhonemeGetRepresentation(p) for p in phonemes]
        ...     print(f"{name}: {{{', '.join(members)}}}")
        Voiceless Stops: {/p/, /t/, /k/}
        Voiced Stops: {/b/, /d/, /g/}
        Nasals: {/m/, /n/, /ŋ/}
        Vowels: {/a/, /e/, /i/, /o/, /u/}

    Notes:
        - Returns empty list if class is feature-based without explicit segments
        - For segment-based classes (IPhNCSegments), returns SegmentsRC
        - Order is as defined in the natural class
        - Changes to returned list don't affect the natural class

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "NaturalClassGetPhonemes requires FLEx API integration. "
        "Will read nc.SegmentsRC if segment-based class"
    )
    # FLEx integration:
    # nc_obj = resolve_natural_class(nc_or_hvo, project)
    # validate_object_exists(nc_obj, f"Natural Class {nc_or_hvo}")
    # # Check if it's a segment-based natural class
    # if hasattr(nc_obj, 'SegmentsRC'):
    #     return list(nc_obj.SegmentsRC)
    # return []


def NaturalClassAddPhoneme(
    nc_or_hvo: IPhNaturalClass | HVO,
    phoneme: IPhPhoneme
) -> None:
    """
    Add a phoneme to a natural class.

    Args:
        nc_or_hvo: The natural class object or its HVO
        phoneme: The phoneme object to add

    Raises:
        ObjectNotFoundError: If the natural class or phoneme doesn't exist
        InvalidParameterError: If the natural class is feature-based (cannot add segments)

    Example:
        >>> # Create voiceless stops class
        >>> nc = NaturalClassCreate("Voiceless Stops", "VLS")
        >>> NaturalClassAddPhoneme(nc, PhonemeFind("/p/"))
        >>> NaturalClassAddPhoneme(nc, PhonemeFind("/t/"))
        >>> NaturalClassAddPhoneme(nc, PhonemeFind("/k/"))

        >>> # Create vowel class
        >>> vowels = NaturalClassCreate("Vowels", "V")
        >>> for repr in ["/a/", "/e/", "/i/", "/o/", "/u/"]:
        ...     phoneme = PhonemeFind(repr)
        ...     if phoneme:
        ...         NaturalClassAddPhoneme(vowels, phoneme)

        >>> # Create high vowels (subset of vowels)
        >>> high = NaturalClassCreate("High Vowels", "HV")
        >>> for repr in ["/i/", "/u/"]:
        ...     phoneme = PhonemeFind(repr)
        ...     if phoneme:
        ...         NaturalClassAddPhoneme(high, phoneme)

    Notes:
        - Only works with segment-based natural classes (IPhNCSegments)
        - Phoneme can belong to multiple natural classes
        - Duplicate additions are typically ignored or cause no error
        - For feature-based classes, define features instead

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "NaturalClassAddPhoneme requires FLEx API integration. "
        "Will add phoneme to nc.SegmentsRC"
    )
    # FLEx integration:
    # nc_obj = resolve_natural_class(nc_or_hvo, project)
    # validate_object_exists(nc_obj, f"Natural Class {nc_or_hvo}")
    # validate_object_exists(phoneme, "Phoneme")
    #
    # if not hasattr(nc_obj, 'SegmentsRC'):
    #     raise InvalidParameterError(
    #         "Cannot add phoneme to feature-based natural class"
    #     )
    #
    # with UndoableUnitOfWork(project, "Add Phoneme to Natural Class"):
    #     if phoneme not in nc_obj.SegmentsRC:
    #         nc_obj.SegmentsRC.Add(phoneme)


def NaturalClassRemovePhoneme(
    nc_or_hvo: IPhNaturalClass | HVO,
    phoneme: IPhPhoneme
) -> None:
    """
    Remove a phoneme from a natural class.

    Args:
        nc_or_hvo: The natural class object or its HVO
        phoneme: The phoneme object to remove

    Raises:
        ObjectNotFoundError: If the natural class doesn't exist
        ValueError: If the phoneme is not in the natural class

    Example:
        >>> # Remove /q/ from uvular stops if reclassified
        >>> nc = NaturalClassFind("Uvular Stops")
        >>> q_phoneme = PhonemeFind("/q/")
        >>> if q_phoneme in NaturalClassGetPhonemes(nc):
        ...     NaturalClassRemovePhoneme(nc, q_phoneme)

        >>> # Clean up natural class
        >>> nc = NaturalClassFind("Obsolete Phonemes")
        >>> for phoneme in NaturalClassGetPhonemes(nc):
        ...     NaturalClassRemovePhoneme(nc, phoneme)

    Notes:
        - Only works with segment-based natural classes
        - Phoneme must be in the class's SegmentsRC collection
        - Use NaturalClassGetPhonemes() to check membership first

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "NaturalClassRemovePhoneme requires FLEx API integration. "
        "Will remove phoneme from nc.SegmentsRC"
    )
    # FLEx integration:
    # nc_obj = resolve_natural_class(nc_or_hvo, project)
    # validate_object_exists(nc_obj, f"Natural Class {nc_or_hvo}")
    #
    # if not hasattr(nc_obj, 'SegmentsRC'):
    #     raise InvalidParameterError(
    #         "Cannot remove phoneme from feature-based natural class"
    #     )
    #
    # with UndoableUnitOfWork(project, "Remove Phoneme from Natural Class"):
    #     if phoneme not in nc_obj.SegmentsRC:
    #         raise ValueError("Phoneme not found in natural class")
    #     nc_obj.SegmentsRC.Remove(phoneme)


__all__ = [
    'NaturalClassGetAll',
    'NaturalClassCreate',
    'NaturalClassDelete',
    'NaturalClassGetName',
    'NaturalClassSetName',
    'NaturalClassGetAbbreviation',
    'NaturalClassGetPhonemes',
    'NaturalClassAddPhoneme',
    'NaturalClassRemovePhoneme',
]
