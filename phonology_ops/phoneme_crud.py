"""
Phoneme CRUD Operations

This module provides Create, Read, Update, and Delete operations for
Phonemes in FLEx.

Phonemes are the minimal distinctive units of sound in a language. For example,
in English, /p/ and /b/ are distinct phonemes because they distinguish words
like "pat" and "bat".

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

from typing import Generator, Optional
from flexlibs_dev.core.types import (
    IPhPhoneme,
    IFsFeatStruc,
    HVO,
    WritingSystemHandle,
    OptionalPhoneme,
)
from flexlibs_dev.core.resolvers import resolve_phoneme
from flexlibs_dev.core.validators import validate_non_empty_string, validate_object_exists
from flexlibs_dev.core.exceptions import (
    ObjectNotFoundError,
    DuplicateObjectError,
    InvalidParameterError,
    NotImplementedYetError,
)


def PhonemeGetAll() -> Generator[IPhPhoneme, None, None]:
    """
    Get all phonemes in the phonological inventory.

    Yields:
        IPhPhoneme: Each phoneme in the project's phoneme inventory

    Example:
        >>> for phoneme in PhonemeGetAll():
        ...     print(PhonemeGetRepresentation(phoneme))
        /p/
        /t/
        /k/
        /b/
        /d/
        /g/
        /m/
        /n/
        /a/
        /i/
        /u/
        ...

    Notes:
        - Returns phonemes in their defined order
        - Includes both consonants and vowels
        - Use PhonemeIsVowel() or PhonemeIsConsonant() to filter by type

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonemeGetAll requires FLEx API integration. "
        "Will iterate over project.PhonologicalDataOA.PhonemeSetsOS[0].PhonemesOC"
    )
    # FLEx integration:
    # phon_data = project.PhonologicalDataOA
    # if phon_data and phon_data.PhonemeSetsOS.Count > 0:
    #     phoneme_set = phon_data.PhonemeSetsOS[0]
    #     for phoneme in phoneme_set.PhonemesOC:
    #         yield phoneme


def PhonemeCreate(
    representation: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> IPhPhoneme:
    """
    Create a new phoneme.

    Args:
        representation: The phonemic representation (e.g., "/p/", "/a/", "/tʃ/")
        wsHandle: Optional writing system (defaults to vernacular WS)

    Returns:
        IPhPhoneme: The newly created phoneme object

    Raises:
        InvalidParameterError: If representation is empty
        DuplicateObjectError: If a phoneme with this representation already exists

    Example:
        >>> phoneme = PhonemeCreate("/p/")
        >>> print(PhonemeGetRepresentation(phoneme))
        /p/

        >>> # Create with description
        >>> phoneme = PhonemeCreate("/tʃ/")
        >>> PhonemeSetDescription(phoneme, "voiceless postalveolar affricate")

        >>> # Create vowel
        >>> vowel = PhonemeCreate("/æ/")
        >>> PhonemeSetDescription(vowel, "near-open front unrounded vowel")

    Notes:
        - Representation should use IPA symbols
        - Standard convention is to enclose in slashes: /p/
        - Use PhonemeAddCode() to add allophonic codes
        - Use PhonemeGetFeatures() to set distinctive features

    TODO: FLEx API integration required
    """
    validate_non_empty_string(representation, "representation")

    # Check if phoneme already exists
    if PhonemeExists(representation, wsHandle):
        raise DuplicateObjectError(
            "Phoneme",
            representation
        )

    raise NotImplementedYetError(
        "PhonemeCreate requires FLEx API integration. "
        "Will create new IPhPhoneme in phoneme set"
    )
    # FLEx integration:
    # from SIL.LCModel import IPhPhoneme, UndoableUnitOfWork
    # phon_data = project.PhonologicalDataOA
    # if not phon_data:
    #     raise OperationFailedError("No phonological data in project")
    # if phon_data.PhonemeSetsOS.Count == 0:
    #     # Create default phoneme set if needed
    #     phoneme_set = project.ServiceLocator.GetInstance(IPhPhonemeSetFactory).Create()
    #     phon_data.PhonemeSetsOS.Append(phoneme_set)
    # else:
    #     phoneme_set = phon_data.PhonemeSetsOS[0]
    #
    # with UndoableUnitOfWork(project, "Create Phoneme"):
    #     phoneme = project.ServiceLocator.GetInstance(IPhPhonemeFactory).Create()
    #     if wsHandle is None:
    #         wsHandle = project.DefaultVernacularWs
    #     phoneme.Name.set_String(wsHandle, representation)
    #     phoneme_set.PhonemesOC.Add(phoneme)
    #     return phoneme


def PhonemeDelete(phoneme_or_hvo: IPhPhoneme | HVO) -> None:
    """
    Delete a phoneme.

    Args:
        phoneme_or_hvo: The phoneme object or its HVO to delete

    Raises:
        ObjectNotFoundError: If the phoneme doesn't exist
        RuntimeError: If the phoneme is in use and cannot be deleted

    Example:
        >>> phoneme = PhonemeFind("/x/")  # obsolete phoneme
        >>> PhonemeDelete(phoneme)

    Warning:
        - Deleting a phoneme that is in use will raise an error
        - This includes phonemes used in:
          - Natural classes
          - Phonological rules
          - Allomorph environments
        - Consider updating references before deletion

    Notes:
        - Deletion is permanent and cannot be undone outside a transaction
        - All associated codes will also be deleted

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonemeDelete requires FLEx API integration. "
        "Will remove phoneme from phoneme set"
    )
    # FLEx integration:
    # phoneme_obj = resolve_phoneme(phoneme_or_hvo, project)
    # validate_object_exists(phoneme_obj, f"Phoneme {phoneme_or_hvo}")
    # phon_data = project.PhonologicalDataOA
    # phoneme_set = phon_data.PhonemeSetsOS[0]
    # with UndoableUnitOfWork(project, "Delete Phoneme"):
    #     phoneme_set.PhonemesOC.Remove(phoneme_obj)


def PhonemeExists(
    representation: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> bool:
    """
    Check if a phoneme with the given representation exists.

    Args:
        representation: The phonemic representation to search for
        wsHandle: Optional writing system (defaults to vernacular WS)

    Returns:
        bool: True if phoneme exists, False otherwise

    Example:
        >>> if not PhonemeExists("/ŋ/"):
        ...     PhonemeCreate("/ŋ/")
        ...     PhonemeSetDescription(PhonemeFind("/ŋ/"), "velar nasal")

    Notes:
        - Comparison is case-sensitive (IPA is case-sensitive)
        - Use PhonemeFind() to get the actual object

    TODO: FLEx API integration required
    """
    validate_non_empty_string(representation, "representation")

    raise NotImplementedYetError(
        "PhonemeExists requires FLEx API integration. "
        "Will search phoneme set for matching representation"
    )
    # FLEx integration:
    # if wsHandle is None:
    #     wsHandle = project.DefaultVernacularWs
    # phon_data = project.PhonologicalDataOA
    # if not phon_data or phon_data.PhonemeSetsOS.Count == 0:
    #     return False
    # phoneme_set = phon_data.PhonemeSetsOS[0]
    # for phoneme in phoneme_set.PhonemesOC:
    #     if phoneme.Name.get_String(wsHandle).Text == representation:
    #         return True
    # return False


def PhonemeFind(
    representation: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> OptionalPhoneme:
    """
    Find a phoneme by its representation.

    Args:
        representation: The phonemic representation to search for
        wsHandle: Optional writing system (defaults to vernacular WS)

    Returns:
        IPhPhoneme | None: The phoneme object if found, None otherwise

    Example:
        >>> phoneme = PhonemeFind("/p/")
        >>> if phoneme:
        ...     desc = PhonemeGetDescription(phoneme)
        ...     print(f"/p/: {desc}")
        /p/: voiceless bilabial stop

        >>> # Check if phoneme exists before operations
        >>> voiceless_stops = PhonemeFind("/p/"), PhonemeFind("/t/"), PhonemeFind("/k/")
        >>> if all(voiceless_stops):
        ...     nc = NaturalClassCreate("VoicelessStops", "VLS")
        ...     for phoneme in voiceless_stops:
        ...         NaturalClassAddPhoneme(nc, phoneme)

    Notes:
        - Returns first match only
        - Search is case-sensitive (IPA is case-sensitive)
        - Returns None if not found (doesn't raise exception)

    TODO: FLEx API integration required
    """
    validate_non_empty_string(representation, "representation")

    raise NotImplementedYetError(
        "PhonemeFind requires FLEx API integration. "
        "Will search phoneme set for matching representation"
    )
    # FLEx integration:
    # if wsHandle is None:
    #     wsHandle = project.DefaultVernacularWs
    # phon_data = project.PhonologicalDataOA
    # if not phon_data or phon_data.PhonemeSetsOS.Count == 0:
    #     return None
    # phoneme_set = phon_data.PhonemeSetsOS[0]
    # for phoneme in phoneme_set.PhonemesOC:
    #     if phoneme.Name.get_String(wsHandle).Text == representation:
    #         return phoneme
    # return None


def PhonemeGetRepresentation(
    phoneme_or_hvo: IPhPhoneme | HVO,
    wsHandle: Optional[WritingSystemHandle] = None
) -> str:
    """
    Get the representation of a phoneme.

    Args:
        phoneme_or_hvo: The phoneme object or its HVO
        wsHandle: Optional writing system (defaults to vernacular WS)

    Returns:
        str: The phoneme representation

    Raises:
        ObjectNotFoundError: If the phoneme doesn't exist

    Example:
        >>> phoneme = PhonemeFind("/p/")
        >>> repr = PhonemeGetRepresentation(phoneme)
        >>> print(repr)
        /p/

        >>> # Iterate and print all phonemes
        >>> for phoneme in PhonemeGetAll():
        ...     print(PhonemeGetRepresentation(phoneme))

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonemeGetRepresentation requires FLEx API integration. "
        "Will read phoneme.Name.get_String(ws_handle)"
    )
    # FLEx integration:
    # phoneme_obj = resolve_phoneme(phoneme_or_hvo, project)
    # validate_object_exists(phoneme_obj, f"Phoneme {phoneme_or_hvo}")
    # if wsHandle is None:
    #     wsHandle = project.DefaultVernacularWs
    # return phoneme_obj.Name.get_String(wsHandle).Text


def PhonemeSetRepresentation(
    phoneme_or_hvo: IPhPhoneme | HVO,
    repr: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> None:
    """
    Set the representation of a phoneme.

    Args:
        phoneme_or_hvo: The phoneme object or its HVO
        repr: The new representation
        wsHandle: Optional writing system (defaults to vernacular WS)

    Raises:
        InvalidParameterError: If representation is empty
        ObjectNotFoundError: If the phoneme doesn't exist

    Example:
        >>> phoneme = PhonemeFind("/ph/")  # non-standard notation
        >>> PhonemeSetRepresentation(phoneme, "/pʰ/")  # fix to proper IPA

    Notes:
        - Use standard IPA symbols for cross-linguistic compatibility
        - Consider updating codes and descriptions when changing representation

    TODO: FLEx API integration required
    """
    validate_non_empty_string(repr, "representation")

    raise NotImplementedYetError(
        "PhonemeSetRepresentation requires FLEx API integration. "
        "Will write to phoneme.Name.set_String(ws_handle, repr)"
    )
    # FLEx integration:
    # phoneme_obj = resolve_phoneme(phoneme_or_hvo, project)
    # validate_object_exists(phoneme_obj, f"Phoneme {phoneme_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Phoneme Representation"):
    #     if wsHandle is None:
    #         wsHandle = project.DefaultVernacularWs
    #     phoneme_obj.Name.set_String(wsHandle, repr)


def PhonemeGetDescription(
    phoneme_or_hvo: IPhPhoneme | HVO,
    wsHandle: Optional[WritingSystemHandle] = None
) -> str:
    """
    Get the description of a phoneme.

    Args:
        phoneme_or_hvo: The phoneme object or its HVO
        wsHandle: Optional writing system (defaults to analysis WS)

    Returns:
        str: The phoneme description (empty string if not set)

    Raises:
        ObjectNotFoundError: If the phoneme doesn't exist

    Example:
        >>> phoneme = PhonemeFind("/p/")
        >>> desc = PhonemeGetDescription(phoneme)
        >>> print(desc)
        voiceless bilabial stop

        >>> # Print phoneme inventory with descriptions
        >>> for phoneme in PhonemeGetAll():
        ...     repr = PhonemeGetRepresentation(phoneme)
        ...     desc = PhonemeGetDescription(phoneme)
        ...     print(f"{repr}: {desc}")
        /p/: voiceless bilabial stop
        /b/: voiced bilabial stop
        /t/: voiceless alveolar stop
        ...

    Notes:
        - Description typically includes articulatory features
        - Returns empty string if no description set

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonemeGetDescription requires FLEx API integration. "
        "Will read phoneme.Description.get_String(ws_handle)"
    )
    # FLEx integration:
    # phoneme_obj = resolve_phoneme(phoneme_or_hvo, project)
    # validate_object_exists(phoneme_obj, f"Phoneme {phoneme_or_hvo}")
    # if wsHandle is None:
    #     wsHandle = project.DefaultAnalysisWs
    # desc = phoneme_obj.Description.get_String(wsHandle)
    # return desc.Text if desc else ""


def PhonemeSetDescription(
    phoneme_or_hvo: IPhPhoneme | HVO,
    desc: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> None:
    """
    Set the description of a phoneme.

    Args:
        phoneme_or_hvo: The phoneme object or its HVO
        desc: The new description
        wsHandle: Optional writing system (defaults to analysis WS)

    Raises:
        ObjectNotFoundError: If the phoneme doesn't exist

    Example:
        >>> phoneme = PhonemeCreate("/p/")
        >>> PhonemeSetDescription(phoneme, "voiceless bilabial stop")

        >>> # Add detailed articulatory description
        >>> phoneme = PhonemeFind("/ɾ/")
        >>> PhonemeSetDescription(
        ...     phoneme,
        ...     "voiced alveolar tap/flap - allophone of /r/ in intervocalic position"
        ... )

    Notes:
        - Description is optional but recommended for documentation
        - Use standard phonetic terminology
        - Can include information about allophones and distribution

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonemeSetDescription requires FLEx API integration. "
        "Will write to phoneme.Description.set_String(ws_handle, desc)"
    )
    # FLEx integration:
    # phoneme_obj = resolve_phoneme(phoneme_or_hvo, project)
    # validate_object_exists(phoneme_obj, f"Phoneme {phoneme_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Phoneme Description"):
    #     if wsHandle is None:
    #         wsHandle = project.DefaultAnalysisWs
    #     phoneme_obj.Description.set_String(wsHandle, desc)


def PhonemeGetFeatures(phoneme_or_hvo: IPhPhoneme | HVO) -> IFsFeatStruc:
    """
    Get the feature structure of a phoneme.

    Args:
        phoneme_or_hvo: The phoneme object or its HVO

    Returns:
        IFsFeatStruc: The phoneme's feature structure

    Raises:
        ObjectNotFoundError: If the phoneme doesn't exist

    Example:
        >>> phoneme = PhonemeFind("/p/")
        >>> features = PhonemeGetFeatures(phoneme)
        >>> # Features typically include:
        >>> # - [+consonantal]
        >>> # - [-sonorant]
        >>> # - [-voice]
        >>> # - [+labial]
        >>> # - [-continuant]

        >>> vowel = PhonemeFind("/i/")
        >>> features = PhonemeGetFeatures(vowel)
        >>> # Vowel features:
        >>> # - [-consonantal]
        >>> # - [+sonorant]
        >>> # - [+high]
        >>> # - [-back]
        >>> # - [-round]

    Notes:
        - Feature structures define distinctive phonological properties
        - Used in phonological rules and natural class definitions
        - Feature system must be defined in project settings
        - Returns the feature structure object for manipulation

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonemeGetFeatures requires FLEx API integration. "
        "Will read phoneme.FeaturesOA"
    )
    # FLEx integration:
    # phoneme_obj = resolve_phoneme(phoneme_or_hvo, project)
    # validate_object_exists(phoneme_obj, f"Phoneme {phoneme_or_hvo}")
    # return phoneme_obj.FeaturesOA


__all__ = [
    'PhonemeGetAll',
    'PhonemeCreate',
    'PhonemeDelete',
    'PhonemeExists',
    'PhonemeFind',
    'PhonemeGetRepresentation',
    'PhonemeSetRepresentation',
    'PhonemeGetDescription',
    'PhonemeSetDescription',
    'PhonemeGetFeatures',
]
