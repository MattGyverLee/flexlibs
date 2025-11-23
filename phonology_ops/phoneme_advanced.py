"""
Phoneme Advanced Operations

This module provides advanced operations for phonemes in FLEx, including
code management, IPA symbols, and phoneme classification.

Phoneme codes represent alternative representations or allophones of a phoneme.
For example, the phoneme /t/ might have codes for [t], [tʰ], [ɾ], [ʔ] depending
on phonological context.

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

from typing import List, Optional
from flexlibs_dev.core.types import (
    IPhPhoneme,
    IPhCode,
    HVO,
    WritingSystemHandle,
)
from flexlibs_dev.core.resolvers import resolve_phoneme
from flexlibs_dev.core.validators import validate_non_empty_string, validate_object_exists
from flexlibs_dev.core.exceptions import (
    ObjectNotFoundError,
    InvalidParameterError,
    NotImplementedYetError,
)


def PhonemeGetCodes(phoneme_or_hvo: IPhPhoneme | HVO) -> List[IPhCode]:
    """
    Get all codes (allophonic representations) for a phoneme.

    Args:
        phoneme_or_hvo: The phoneme object or its HVO

    Returns:
        List[IPhCode]: List of code objects (empty if none)

    Raises:
        ObjectNotFoundError: If the phoneme doesn't exist

    Example:
        >>> # Get allophones of /t/
        >>> phoneme = PhonemeFind("/t/")
        >>> codes = PhonemeGetCodes(phoneme)
        >>> for code in codes:
        ...     print(code.Representation.VernacularDefaultWritingSystem.Text)
        [t]   # plain voiceless alveolar stop
        [tʰ]  # aspirated (word-initial)
        [ɾ]   # flap (intervocalic)
        [ʔ]   # glottal stop (syllable-final)

        >>> # Get vowel allophones
        >>> phoneme = PhonemeFind("/i/")
        >>> codes = PhonemeGetCodes(phoneme)
        >>> for code in codes:
        ...     print(code.Representation.VernacularDefaultWritingSystem.Text)
        [i]   # close front unrounded
        [ɪ]   # near-close near-front unrounded (unstressed)

    Notes:
        - Codes represent allophones or context-specific realizations
        - Convention is to use square brackets [p] for phones
        - Slashes /p/ for phonemes
        - Empty list if no codes defined

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonemeGetCodes requires FLEx API integration. "
        "Will read phoneme.CodesOS"
    )
    # FLEx integration:
    # phoneme_obj = resolve_phoneme(phoneme_or_hvo, project)
    # validate_object_exists(phoneme_obj, f"Phoneme {phoneme_or_hvo}")
    # return list(phoneme_obj.CodesOS)


def PhonemeAddCode(
    phoneme_or_hvo: IPhPhoneme | HVO,
    representation: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> IPhCode:
    """
    Add a code (allophonic representation) to a phoneme.

    Args:
        phoneme_or_hvo: The phoneme object or its HVO
        representation: The code representation (e.g., "[tʰ]", "[ɾ]")
        wsHandle: Optional writing system (defaults to vernacular WS)

    Returns:
        IPhCode: The newly created code object

    Raises:
        InvalidParameterError: If representation is empty
        ObjectNotFoundError: If the phoneme doesn't exist

    Example:
        >>> # Add aspiration allophone
        >>> phoneme = PhonemeFind("/p/")
        >>> code = PhonemeAddCode(phoneme, "[pʰ]")

        >>> # Add multiple allophones for /t/
        >>> phoneme = PhonemeFind("/t/")
        >>> PhonemeAddCode(phoneme, "[t]")   # plain
        >>> PhonemeAddCode(phoneme, "[tʰ]")  # aspirated
        >>> PhonemeAddCode(phoneme, "[ɾ]")   # flap
        >>> PhonemeAddCode(phoneme, "[ʔ]")   # glottalized

        >>> # Add vowel allophones
        >>> phoneme = PhonemeFind("/a/")
        >>> PhonemeAddCode(phoneme, "[a]")   # open front
        >>> PhonemeAddCode(phoneme, "[ɑ]")   # open back
        >>> PhonemeAddCode(phoneme, "[ə]")   # schwa (reduced)

    Notes:
        - Use square brackets [p] for phones (allophones)
        - Each code can have its own feature specifications
        - Codes are used in phonological rule environments
        - Duplicates are allowed (same code can be added multiple times)

    TODO: FLEx API integration required
    """
    validate_non_empty_string(representation, "representation")

    raise NotImplementedYetError(
        "PhonemeAddCode requires FLEx API integration. "
        "Will create new IPhCode and add to phoneme.CodesOS"
    )
    # FLEx integration:
    # from SIL.LCModel import IPhCode, UndoableUnitOfWork
    # phoneme_obj = resolve_phoneme(phoneme_or_hvo, project)
    # validate_object_exists(phoneme_obj, f"Phoneme {phoneme_or_hvo}")
    #
    # with UndoableUnitOfWork(project, "Add Phoneme Code"):
    #     code = project.ServiceLocator.GetInstance(IPhCodeFactory).Create()
    #     if wsHandle is None:
    #         wsHandle = project.DefaultVernacularWs
    #     code.Representation.set_String(wsHandle, representation)
    #     phoneme_obj.CodesOS.Append(code)
    #     return code


def PhonemeRemoveCode(
    phoneme_or_hvo: IPhPhoneme | HVO,
    code: IPhCode
) -> None:
    """
    Remove a code from a phoneme.

    Args:
        phoneme_or_hvo: The phoneme object or its HVO
        code: The code object to remove

    Raises:
        ObjectNotFoundError: If the phoneme doesn't exist
        ValueError: If the code is not in the phoneme's code list

    Example:
        >>> phoneme = PhonemeFind("/t/")
        >>> codes = PhonemeGetCodes(phoneme)
        >>> # Remove the flap allophone
        >>> for code in codes:
        ...     repr = code.Representation.VernacularDefaultWritingSystem.Text
        ...     if repr == "[ɾ]":
        ...         PhonemeRemoveCode(phoneme, code)
        ...         break

    Notes:
        - Code object must be from the phoneme's CodesOS collection
        - Use PhonemeGetCodes() to find codes to remove

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonemeRemoveCode requires FLEx API integration. "
        "Will remove code from phoneme.CodesOS"
    )
    # FLEx integration:
    # phoneme_obj = resolve_phoneme(phoneme_or_hvo, project)
    # validate_object_exists(phoneme_obj, f"Phoneme {phoneme_or_hvo}")
    #
    # with UndoableUnitOfWork(project, "Remove Phoneme Code"):
    #     if code not in phoneme_obj.CodesOS:
    #         raise ValueError("Code not found in phoneme's code list")
    #     phoneme_obj.CodesOS.Remove(code)


def PhonemeGetBasicIPASymbol(phoneme_or_hvo: IPhPhoneme | HVO) -> str:
    """
    Get the basic IPA symbol for a phoneme.

    Args:
        phoneme_or_hvo: The phoneme object or its HVO

    Returns:
        str: The basic IPA symbol

    Raises:
        ObjectNotFoundError: If the phoneme doesn't exist

    Example:
        >>> phoneme = PhonemeFind("/p/")
        >>> symbol = PhonemeGetBasicIPASymbol(phoneme)
        >>> print(symbol)
        p

        >>> # Compare representation with basic IPA
        >>> phoneme = PhonemeFind("/tʃ/")
        >>> repr = PhonemeGetRepresentation(phoneme)
        >>> ipa = PhonemeGetBasicIPASymbol(phoneme)
        >>> print(f"Representation: {repr}, IPA: {ipa}")
        Representation: /tʃ/, IPA: tʃ

    Notes:
        - Returns the IPA symbol without slashes or diacritics
        - May differ from representation which can include slashes
        - Used for cross-linguistic phoneme identification
        - May be empty if not set

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonemeGetBasicIPASymbol requires FLEx API integration. "
        "Will read phoneme.BasicIPASymbol"
    )
    # FLEx integration:
    # phoneme_obj = resolve_phoneme(phoneme_or_hvo, project)
    # validate_object_exists(phoneme_obj, f"Phoneme {phoneme_or_hvo}")
    # return phoneme_obj.BasicIPASymbol if hasattr(phoneme_obj, 'BasicIPASymbol') else ""


def PhonemeIsVowel(phoneme_or_hvo: IPhPhoneme | HVO) -> bool:
    """
    Check if a phoneme is classified as a vowel.

    Args:
        phoneme_or_hvo: The phoneme object or its HVO

    Returns:
        bool: True if the phoneme is a vowel, False otherwise

    Raises:
        ObjectNotFoundError: If the phoneme doesn't exist

    Example:
        >>> # Filter vowels from phoneme inventory
        >>> vowels = []
        >>> for phoneme in PhonemeGetAll():
        ...     if PhonemeIsVowel(phoneme):
        ...         vowels.append(PhonemeGetRepresentation(phoneme))
        >>> print("Vowels:", ", ".join(vowels))
        Vowels: /a/, /e/, /i/, /o/, /u/

        >>> # Create vowel natural class
        >>> vowel_class = NaturalClassCreate("Vowels", "V")
        >>> for phoneme in PhonemeGetAll():
        ...     if PhonemeIsVowel(phoneme):
        ...         NaturalClassAddPhoneme(vowel_class, phoneme)

    Notes:
        - Classification based on feature structure
        - Typically checks for [-consonantal, +sonorant] features
        - May return False if features not properly set
        - Use PhonemeGetFeatures() to examine feature values

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonemeIsVowel requires FLEx API integration. "
        "Will check phoneme feature structure for vowel features"
    )
    # FLEx integration:
    # phoneme_obj = resolve_phoneme(phoneme_or_hvo, project)
    # validate_object_exists(phoneme_obj, f"Phoneme {phoneme_or_hvo}")
    # # Check feature structure for vowel features
    # features = phoneme_obj.FeaturesOA
    # if not features:
    #     return False
    # # Typical vowel features: [-consonantal], [+sonorant], [+syllabic]
    # # Implementation depends on feature system
    # # This is a simplified check - actual implementation needs feature analysis
    # return False  # Placeholder


def PhonemeIsConsonant(phoneme_or_hvo: IPhPhoneme | HVO) -> bool:
    """
    Check if a phoneme is classified as a consonant.

    Args:
        phoneme_or_hvo: The phoneme object or its HVO

    Returns:
        bool: True if the phoneme is a consonant, False otherwise

    Raises:
        ObjectNotFoundError: If the phoneme doesn't exist

    Example:
        >>> # Filter consonants from phoneme inventory
        >>> consonants = []
        >>> for phoneme in PhonemeGetAll():
        ...     if PhonemeIsConsonant(phoneme):
        ...         consonants.append(PhonemeGetRepresentation(phoneme))
        >>> print("Consonants:", ", ".join(consonants))
        Consonants: /p/, /t/, /k/, /b/, /d/, /g/, /m/, /n/, /s/, /z/

        >>> # Create consonant natural classes
        >>> stops = NaturalClassCreate("Stops", "P")
        >>> fricatives = NaturalClassCreate("Fricatives", "F")
        >>> for phoneme in PhonemeGetAll():
        ...     if PhonemeIsConsonant(phoneme):
        ...         desc = PhonemeGetDescription(phoneme)
        ...         if "stop" in desc.lower():
        ...             NaturalClassAddPhoneme(stops, phoneme)
        ...         elif "fricative" in desc.lower():
        ...             NaturalClassAddPhoneme(fricatives, phoneme)

    Notes:
        - Classification based on feature structure
        - Typically checks for [+consonantal] or [-syllabic] features
        - May return False if features not properly set
        - Complementary to PhonemeIsVowel() but not necessarily opposite
          (some sounds like glides may be neither or both)

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonemeIsConsonant requires FLEx API integration. "
        "Will check phoneme feature structure for consonant features"
    )
    # FLEx integration:
    # phoneme_obj = resolve_phoneme(phoneme_or_hvo, project)
    # validate_object_exists(phoneme_obj, f"Phoneme {phoneme_or_hvo}")
    # # Check feature structure for consonant features
    # features = phoneme_obj.FeaturesOA
    # if not features:
    #     return False
    # # Typical consonant features: [+consonantal], [-syllabic]
    # # Implementation depends on feature system
    # # This is a simplified check - actual implementation needs feature analysis
    # return False  # Placeholder


__all__ = [
    'PhonemeGetCodes',
    'PhonemeAddCode',
    'PhonemeRemoveCode',
    'PhonemeGetBasicIPASymbol',
    'PhonemeIsVowel',
    'PhonemeIsConsonant',
]
