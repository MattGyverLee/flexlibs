"""
Allomorph Operations

This module provides operations for managing allomorphs (morphological forms)
in FLEx lexical entries.

Allomorphs are variant forms of morphemes that appear in different phonological
or morphological contexts. For example, the English plural morpheme has
allomorphs "-s", "-es", and "-en" (ox/oxen).

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

from typing import Generator, Optional, List
from flexlibs_dev.core.types import (
    IMoForm,
    IMoMorphType,
    IPhEnvironment,
    ILexEntry,
    HVO,
    WritingSystemHandle,
)
from flexlibs_dev.core.resolvers import resolve_allomorph, resolve_environment, resolve_object
from flexlibs_dev.core.validators import validate_non_empty_string, validate_object_exists
from flexlibs_dev.core.exceptions import (
    ObjectNotFoundError,
    InvalidParameterError,
    NotImplementedYetError,
)


def AllomorphGetAll(entry_or_hvo: ILexEntry | HVO) -> Generator[IMoForm, None, None]:
    """
    Get all allomorphs for a lexical entry.

    Args:
        entry_or_hvo: The lexical entry object or its HVO

    Yields:
        IMoForm: Each allomorph of the entry

    Raises:
        ObjectNotFoundError: If the entry doesn't exist

    Example:
        >>> entry = LexiconFindEntry("run")
        >>> for allomorph in AllomorphGetAll(entry):
        ...     form = AllomorphGetForm(allomorph)
        ...     print(f"Allomorph: {form}")
        Allomorph: run
        Allomorph: ran
        Allomorph: runn-

    Notes:
        - Includes all allomorph types (stem, affix, etc.)
        - Order follows FLEx database order
        - Returns empty generator if entry has no allomorphs

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "AllomorphGetAll requires FLEx API integration. "
        "Will iterate over entry.AlternateFormsOS and entry.LexemeFormOA"
    )
    # FLEx integration:
    # entry_obj = resolve_object(entry_or_hvo, project)
    # validate_object_exists(entry_obj, f"Entry {entry_or_hvo}")
    # if entry_obj.LexemeFormOA:
    #     yield entry_obj.LexemeFormOA
    # for allomorph in entry_obj.AlternateFormsOS:
    #     yield allomorph


def AllomorphCreate(
    entry_or_hvo: ILexEntry | HVO,
    form: str,
    morphType: IMoMorphType,
    wsHandle: Optional[WritingSystemHandle] = None
) -> IMoForm:
    """
    Create a new allomorph for a lexical entry.

    Args:
        entry_or_hvo: The lexical entry object or its HVO
        form: The allomorph form (e.g., "-ing", "walk", "pre-")
        morphType: The morpheme type (stem, prefix, suffix, etc.)
        wsHandle: Optional writing system (defaults to vernacular WS)

    Returns:
        IMoForm: The newly created allomorph object

    Raises:
        InvalidParameterError: If form is empty
        ObjectNotFoundError: If the entry doesn't exist

    Example:
        >>> entry = LexiconFindEntry("walk")
        >>> morphType = MorphTypeFind("stem")
        >>> allomorph = AllomorphCreate(entry, "walk", morphType)
        >>> print(AllomorphGetForm(allomorph))
        walk

        >>> # Create a prefix allomorph
        >>> entry = LexiconFindEntry("pre")
        >>> prefix_type = MorphTypeFind("prefix")
        >>> allomorph = AllomorphCreate(entry, "pre-", prefix_type)

    Notes:
        - The allomorph is added to the entry's alternate forms list
        - First allomorph becomes the lexeme form
        - Subsequent allomorphs are added as alternates
        - MorphType determines how the allomorph is analyzed

    TODO: FLEx API integration required
    """
    validate_non_empty_string(form, "form")

    raise NotImplementedYetError(
        "AllomorphCreate requires FLEx API integration. "
        "Will create new IMoForm in entry.AlternateFormsOS"
    )
    # FLEx integration:
    # entry_obj = resolve_object(entry_or_hvo, project)
    # validate_object_exists(entry_obj, f"Entry {entry_or_hvo}")
    # from SIL.LCModel import IMoStemAllomorph, UndoableUnitOfWork
    # with UndoableUnitOfWork(project, "Create Allomorph"):
    #     allomorph = project.ServiceLocator.GetInstance(IMoStemAllomorphFactory).Create()
    #     if wsHandle is None:
    #         wsHandle = project.DefaultVernacularWs
    #     allomorph.Form.set_String(wsHandle, form)
    #     allomorph.MorphTypeRA = morphType
    #     entry_obj.AlternateFormsOS.Append(allomorph)
    #     return allomorph


def AllomorphDelete(allomorph_or_hvo: IMoForm | HVO) -> None:
    """
    Delete an allomorph.

    Args:
        allomorph_or_hvo: The allomorph object or its HVO to delete

    Raises:
        ObjectNotFoundError: If the allomorph doesn't exist
        RuntimeError: If attempting to delete the only allomorph

    Example:
        >>> entry = LexiconFindEntry("walk")
        >>> allomorphs = list(AllomorphGetAll(entry))
        >>> if len(allomorphs) > 1:
        ...     AllomorphDelete(allomorphs[-1])

    Warning:
        - Cannot delete the only allomorph of an entry
        - Deletion is permanent and cannot be undone outside a transaction
        - Check usage in texts before deletion

    Notes:
        - If deleting the lexeme form, the first alternate becomes the lexeme
        - All references to this allomorph in analyses are affected

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "AllomorphDelete requires FLEx API integration. "
        "Will remove allomorph from entry.AlternateFormsOS or entry.LexemeFormOA"
    )
    # FLEx integration:
    # allomorph_obj = resolve_allomorph(allomorph_or_hvo, project)
    # validate_object_exists(allomorph_obj, f"Allomorph {allomorph_or_hvo}")
    # with UndoableUnitOfWork(project, "Delete Allomorph"):
    #     owner = allomorph_obj.Owner
    #     if hasattr(owner, 'AlternateFormsOS'):
    #         owner.AlternateFormsOS.Remove(allomorph_obj)


def AllomorphGetForm(
    allomorph_or_hvo: IMoForm | HVO,
    wsHandle: Optional[WritingSystemHandle] = None
) -> str:
    """
    Get the form (text) of an allomorph.

    Args:
        allomorph_or_hvo: The allomorph object or its HVO
        wsHandle: Optional writing system (defaults to vernacular WS)

    Returns:
        str: The allomorph form

    Raises:
        ObjectNotFoundError: If the allomorph doesn't exist

    Example:
        >>> allomorph = AllomorphCreate(entry, "walk", stem_type)
        >>> form = AllomorphGetForm(allomorph)
        >>> print(form)
        walk

        >>> # Get form in specific writing system
        >>> form_ipa = AllomorphGetForm(allomorph, project.DefaultPronunciationWs)
        >>> print(form_ipa)
        wɔk

    Notes:
        - Returns empty string if form not set in specified WS
        - Use BestVernacularAlternative for automatic fallback

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "AllomorphGetForm requires FLEx API integration. "
        "Will read allomorph.Form.get_String(ws_handle)"
    )
    # FLEx integration:
    # allomorph_obj = resolve_allomorph(allomorph_or_hvo, project)
    # validate_object_exists(allomorph_obj, f"Allomorph {allomorph_or_hvo}")
    # if wsHandle is None:
    #     return allomorph_obj.Form.BestVernacularAlternative.Text
    # return allomorph_obj.Form.get_String(wsHandle).Text


def AllomorphSetForm(
    allomorph_or_hvo: IMoForm | HVO,
    form: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> None:
    """
    Set the form (text) of an allomorph.

    Args:
        allomorph_or_hvo: The allomorph object or its HVO
        form: The new allomorph form
        wsHandle: Optional writing system (defaults to vernacular WS)

    Raises:
        InvalidParameterError: If form is empty
        ObjectNotFoundError: If the allomorph doesn't exist

    Example:
        >>> allomorph = AllomorphCreate(entry, "wlk", stem_type)
        >>> AllomorphSetForm(allomorph, "walk")  # fix typo
        >>> print(AllomorphGetForm(allomorph))
        walk

        >>> # Set IPA pronunciation
        >>> AllomorphSetForm(allomorph, "wɔk", project.DefaultPronunciationWs)

    Notes:
        - Changing the form affects all analyses using this allomorph
        - Parser may need to be rerun after form changes

    TODO: FLEx API integration required
    """
    validate_non_empty_string(form, "form")

    raise NotImplementedYetError(
        "AllomorphSetForm requires FLEx API integration. "
        "Will write to allomorph.Form.set_String(ws_handle, form)"
    )
    # FLEx integration:
    # allomorph_obj = resolve_allomorph(allomorph_or_hvo, project)
    # validate_object_exists(allomorph_obj, f"Allomorph {allomorph_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Allomorph Form"):
    #     if wsHandle is None:
    #         wsHandle = project.DefaultVernacularWs
    #     allomorph_obj.Form.set_String(wsHandle, form)


def AllomorphGetMorphType(allomorph_or_hvo: IMoForm | HVO) -> IMoMorphType:
    """
    Get the morpheme type of an allomorph.

    Args:
        allomorph_or_hvo: The allomorph object or its HVO

    Returns:
        IMoMorphType: The morpheme type (stem, prefix, suffix, etc.)

    Raises:
        ObjectNotFoundError: If the allomorph doesn't exist

    Example:
        >>> allomorph = AllomorphCreate(entry, "pre-", prefix_type)
        >>> morph_type = AllomorphGetMorphType(allomorph)
        >>> type_name = MorphTypeGetName(morph_type)
        >>> print(type_name)
        prefix

    Notes:
        - Morpheme types include: stem, root, bound root, prefix, suffix,
          infix, circumfix, clitic, proclitic, enclitic, simulfix, etc.
        - Type determines parsing behavior and template slots

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "AllomorphGetMorphType requires FLEx API integration. "
        "Will read allomorph.MorphTypeRA"
    )
    # FLEx integration:
    # allomorph_obj = resolve_allomorph(allomorph_or_hvo, project)
    # validate_object_exists(allomorph_obj, f"Allomorph {allomorph_or_hvo}")
    # return allomorph_obj.MorphTypeRA


def AllomorphSetMorphType(
    allomorph_or_hvo: IMoForm | HVO,
    morphType: IMoMorphType
) -> None:
    """
    Set the morpheme type of an allomorph.

    Args:
        allomorph_or_hvo: The allomorph object or its HVO
        morphType: The new morpheme type

    Raises:
        ObjectNotFoundError: If the allomorph doesn't exist
        InvalidParameterError: If morphType is invalid

    Example:
        >>> allomorph = AllomorphCreate(entry, "walk", stem_type)
        >>> # Change to bound root
        >>> bound_root = MorphTypeFind("bound root")
        >>> AllomorphSetMorphType(allomorph, bound_root)

    Notes:
        - Changing type affects parsing and morphological analysis
        - Incompatible changes may require template updates
        - Parser should be rerun after type changes

    TODO: FLEx API integration required
    """
    if morphType is None:
        raise InvalidParameterError("morphType cannot be None")

    raise NotImplementedYetError(
        "AllomorphSetMorphType requires FLEx API integration. "
        "Will write to allomorph.MorphTypeRA"
    )
    # FLEx integration:
    # allomorph_obj = resolve_allomorph(allomorph_or_hvo, project)
    # validate_object_exists(allomorph_obj, f"Allomorph {allomorph_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Allomorph Morph Type"):
    #     allomorph_obj.MorphTypeRA = morphType


def AllomorphGetPhoneEnv(allomorph_or_hvo: IMoForm | HVO) -> List[IPhEnvironment]:
    """
    Get the phonological environments for an allomorph.

    Args:
        allomorph_or_hvo: The allomorph object or its HVO

    Returns:
        List[IPhEnvironment]: List of phonological environments (empty if none)

    Raises:
        ObjectNotFoundError: If the allomorph doesn't exist

    Example:
        >>> # English plural "-s" appears after voiceless consonants
        >>> allomorph = AllomorphCreate(entry, "-s", suffix_type)
        >>> envs = AllomorphGetPhoneEnv(allomorph)
        >>> for env in envs:
        ...     print(EnvironmentGetName(env))
        After voiceless consonant

    Notes:
        - Phonological environments define distribution of allomorphs
        - Empty list means allomorph appears in all contexts
        - Multiple environments are OR'd (any match allows allomorph)

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "AllomorphGetPhoneEnv requires FLEx API integration. "
        "Will read allomorph.PhoneEnvRC"
    )
    # FLEx integration:
    # allomorph_obj = resolve_allomorph(allomorph_or_hvo, project)
    # validate_object_exists(allomorph_obj, f"Allomorph {allomorph_or_hvo}")
    # return list(allomorph_obj.PhoneEnvRC)


def AllomorphAddPhoneEnv(
    allomorph_or_hvo: IMoForm | HVO,
    environment: IPhEnvironment
) -> None:
    """
    Add a phonological environment to an allomorph.

    Args:
        allomorph_or_hvo: The allomorph object or its HVO
        environment: The phonological environment to add

    Raises:
        ObjectNotFoundError: If the allomorph or environment doesn't exist
        InvalidParameterError: If environment is None

    Example:
        >>> # Define that "-es" appears after sibilants
        >>> allomorph = AllomorphCreate(entry, "-es", suffix_type)
        >>> sibilant_env = EnvironmentFind("After sibilant")
        >>> AllomorphAddPhoneEnv(allomorph, sibilant_env)

        >>> # Define that "a" (indefinite) appears before consonants
        >>> allomorph = AllomorphCreate(entry, "a", stem_type)
        >>> consonant_env = EnvironmentFind("Before consonant")
        >>> AllomorphAddPhoneEnv(allomorph, consonant_env)

    Notes:
        - Multiple environments can be added (OR logic)
        - If environment already exists, this is a no-op
        - Environments guide parser and synthesizer

    TODO: FLEx API integration required
    """
    if environment is None:
        raise InvalidParameterError("environment cannot be None")

    raise NotImplementedYetError(
        "AllomorphAddPhoneEnv requires FLEx API integration. "
        "Will add to allomorph.PhoneEnvRC"
    )
    # FLEx integration:
    # allomorph_obj = resolve_allomorph(allomorph_or_hvo, project)
    # validate_object_exists(allomorph_obj, f"Allomorph {allomorph_or_hvo}")
    # env_obj = resolve_environment(environment, project)
    # validate_object_exists(env_obj, f"Environment {environment}")
    # with UndoableUnitOfWork(project, "Add Phone Environment"):
    #     if env_obj not in allomorph_obj.PhoneEnvRC:
    #         allomorph_obj.PhoneEnvRC.Add(env_obj)


def AllomorphRemovePhoneEnv(
    allomorph_or_hvo: IMoForm | HVO,
    environment: IPhEnvironment
) -> None:
    """
    Remove a phonological environment from an allomorph.

    Args:
        allomorph_or_hvo: The allomorph object or its HVO
        environment: The phonological environment to remove

    Raises:
        ObjectNotFoundError: If the allomorph or environment doesn't exist
        InvalidParameterError: If environment is None

    Example:
        >>> allomorph = AllomorphCreate(entry, "-s", suffix_type)
        >>> env = EnvironmentFind("After vowel")
        >>> AllomorphAddPhoneEnv(allomorph, env)
        >>> # Later, remove it
        >>> AllomorphRemovePhoneEnv(allomorph, env)

    Notes:
        - If environment not in list, this is a no-op
        - Removing all environments means allomorph appears in all contexts

    TODO: FLEx API integration required
    """
    if environment is None:
        raise InvalidParameterError("environment cannot be None")

    raise NotImplementedYetError(
        "AllomorphRemovePhoneEnv requires FLEx API integration. "
        "Will remove from allomorph.PhoneEnvRC"
    )
    # FLEx integration:
    # allomorph_obj = resolve_allomorph(allomorph_or_hvo, project)
    # validate_object_exists(allomorph_obj, f"Allomorph {allomorph_or_hvo}")
    # env_obj = resolve_environment(environment, project)
    # validate_object_exists(env_obj, f"Environment {environment}")
    # with UndoableUnitOfWork(project, "Remove Phone Environment"):
    #     if env_obj in allomorph_obj.PhoneEnvRC:
    #         allomorph_obj.PhoneEnvRC.Remove(env_obj)


__all__ = [
    'AllomorphGetAll',
    'AllomorphCreate',
    'AllomorphDelete',
    'AllomorphGetForm',
    'AllomorphSetForm',
    'AllomorphGetMorphType',
    'AllomorphSetMorphType',
    'AllomorphGetPhoneEnv',
    'AllomorphAddPhoneEnv',
    'AllomorphRemovePhoneEnv',
]
