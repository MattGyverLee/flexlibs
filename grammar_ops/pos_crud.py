"""
Parts of Speech CRUD Operations

This module provides Create, Read, Update, and Delete operations for
Parts of Speech (POS) in FLEx.

Parts of Speech are fundamental grammatical categories used in linguistic
analysis (e.g., Noun, Verb, Adjective, etc.).

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

from typing import Generator, Optional, List
from flexlibs_dev.core.types import (
    IPartOfSpeech,
    HVO,
    WritingSystemHandle,
    OptionalPOS,
)
from flexlibs_dev.core.resolvers import resolve_pos
from flexlibs_dev.core.validators import validate_non_empty_string, validate_object_exists
from flexlibs_dev.core.exceptions import (
    ObjectNotFoundError,
    DuplicateObjectError,
    InvalidParameterError,
    NotImplementedYetError,
)


def POSGetAll() -> Generator[IPartOfSpeech, None, None]:
    """
    Get all Parts of Speech in the project.

    Yields:
        IPartOfSpeech: Each part of speech in the project's POS list

    Example:
        >>> for pos in POSGetAll():
        ...     print(POSGetName(pos))
        Noun
        Verb
        Adjective
        ...

    Notes:
        - Returns parts of speech in hierarchical order
        - Includes both top-level and subcategory POS
        - Use POSGetSubcategories() to navigate hierarchy

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "POSGetAll requires FLEx API integration. "
        "Will iterate over project.PartsOfSpeechOA.PossibilitiesOS"
    )
    # FLEx integration:
    # for pos in project.PartsOfSpeechOA.PossibilitiesOS:
    #     yield pos


def POSCreate(
    name: str,
    abbreviation: str,
    catalogSourceId: Optional[str] = None
) -> IPartOfSpeech:
    """
    Create a new Part of Speech.

    Args:
        name: The name of the POS (e.g., "Noun", "Verb")
        abbreviation: Short abbreviation (e.g., "N", "V")
        catalogSourceId: Optional catalog identifier for linguistic databases

    Returns:
        IPartOfSpeech: The newly created POS object

    Raises:
        InvalidParameterError: If name or abbreviation is empty
        DuplicateObjectError: If a POS with this name already exists

    Example:
        >>> pos = POSCreate("Noun", "N")
        >>> print(POSGetName(pos))
        Noun

        >>> proper_noun = POSCreate("Proper Noun", "PN", "GOLD:Noun")
        >>> print(POSGetAbbreviation(proper_noun))
        PN

    Notes:
        - Name must be unique within the project
        - Abbreviations don't need to be unique but should be distinct
        - CatalogSourceId links to linguistic ontologies (e.g., GOLD)

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")
    validate_non_empty_string(abbreviation, "abbreviation")

    # Check if POS already exists
    if POSExists(name):
        raise DuplicateObjectError(f"Part of Speech '{name}' already exists")

    raise NotImplementedYetError(
        "POSCreate requires FLEx API integration. "
        "Will create new IPartOfSpeech in project.PartsOfSpeechOA.PossibilitiesOS"
    )
    # FLEx integration:
    # from SIL.LCModel import IPartOfSpeech, UndoableUnitOfWork
    # with UndoableUnitOfWork(project, "Create POS"):
    #     pos = project.ServiceLocator.GetInstance(IPartOfSpeechFactory).Create()
    #     pos.Name.set_String(ws_handle, name)
    #     pos.Abbreviation.set_String(ws_handle, abbreviation)
    #     if catalogSourceId:
    #         pos.CatalogSourceId = catalogSourceId
    #     project.PartsOfSpeechOA.PossibilitiesOS.Append(pos)
    #     return pos


def POSDelete(pos_or_hvo: IPartOfSpeech | HVO) -> None:
    """
    Delete a Part of Speech.

    Args:
        pos_or_hvo: The POS object or its HVO to delete

    Raises:
        ObjectNotFoundError: If the POS doesn't exist
        RuntimeError: If the POS is in use and cannot be deleted

    Example:
        >>> pos = POSFind("Obsolete")
        >>> POSDelete(pos)

    Warning:
        - Deleting a POS that is in use will raise an error
        - Consider checking usage before deletion
        - Deletion is permanent and cannot be undone outside a transaction

    Notes:
        - Will also delete all subcategories recursively
        - Lexical entries using this POS must be updated first

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "POSDelete requires FLEx API integration. "
        "Will remove POS from project.PartsOfSpeechOA.PossibilitiesOS"
    )
    # FLEx integration:
    # pos_obj = resolve_pos(pos_or_hvo, project)
    # validate_object_exists(pos_obj, f"POS {pos_or_hvo}")
    # with UndoableUnitOfWork(project, "Delete POS"):
    #     project.PartsOfSpeechOA.PossibilitiesOS.Remove(pos_obj)


def POSExists(name: str) -> bool:
    """
    Check if a Part of Speech with the given name exists.

    Args:
        name: The name to search for (case-insensitive)

    Returns:
        bool: True if POS exists, False otherwise

    Example:
        >>> if not POSExists("Noun"):
        ...     POSCreate("Noun", "N")

    Notes:
        - Comparison is case-insensitive
        - Only searches top-level POS, not subcategories
        - Use POSFind() to get the actual object

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")

    raise NotImplementedYetError(
        "POSExists requires FLEx API integration. "
        "Will search project.PartsOfSpeechOA.PossibilitiesOS"
    )
    # FLEx integration:
    # for pos in project.PartsOfSpeechOA.PossibilitiesOS:
    #     if pos.Name.BestAnalysisAlternative.Text.lower() == name.lower():
    #         return True
    # return False


def POSFind(name: str) -> OptionalPOS:
    """
    Find a Part of Speech by name.

    Args:
        name: The name to search for (case-insensitive)

    Returns:
        IPartOfSpeech | None: The POS object if found, None otherwise

    Example:
        >>> pos = POSFind("Noun")
        >>> if pos:
        ...     print(f"Found: {POSGetAbbreviation(pos)}")
        Found: N

    Notes:
        - Returns first match only
        - Search is case-insensitive
        - Returns None if not found (doesn't raise exception)
        - For subcategories, search from parent using POSGetSubcategories()

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")

    raise NotImplementedYetError(
        "POSFind requires FLEx API integration. "
        "Will search project.PartsOfSpeechOA.PossibilitiesOS"
    )
    # FLEx integration:
    # for pos in project.PartsOfSpeechOA.PossibilitiesOS:
    #     if pos.Name.BestAnalysisAlternative.Text.lower() == name.lower():
    #         return pos
    # return None


def POSGetName(
    pos_or_hvo: IPartOfSpeech | HVO,
    wsHandle: Optional[WritingSystemHandle] = None
) -> str:
    """
    Get the name of a Part of Speech.

    Args:
        pos_or_hvo: The POS object or its HVO
        wsHandle: Optional writing system (defaults to analysis WS)

    Returns:
        str: The POS name in the specified writing system

    Raises:
        ObjectNotFoundError: If the POS doesn't exist

    Example:
        >>> pos = POSFind("Noun")
        >>> name = POSGetName(pos)
        >>> print(name)
        Noun

        >>> # Get name in vernacular WS
        >>> vern_name = POSGetName(pos, project.DefaultVernacularWs)

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "POSGetName requires FLEx API integration. "
        "Will read pos.Name.get_String(ws_handle)"
    )
    # FLEx integration:
    # pos_obj = resolve_pos(pos_or_hvo, project)
    # validate_object_exists(pos_obj, f"POS {pos_or_hvo}")
    # if wsHandle is None:
    #     return pos_obj.Name.BestAnalysisAlternative.Text
    # return pos_obj.Name.get_String(wsHandle).Text


def POSSetName(
    pos_or_hvo: IPartOfSpeech | HVO,
    name: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> None:
    """
    Set the name of a Part of Speech.

    Args:
        pos_or_hvo: The POS object or its HVO
        name: The new name
        wsHandle: Optional writing system (defaults to analysis WS)

    Raises:
        InvalidParameterError: If name is empty
        ObjectNotFoundError: If the POS doesn't exist

    Example:
        >>> pos = POSFind("Nown")  # typo
        >>> POSSetName(pos, "Noun")  # fix it

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")

    raise NotImplementedYetError(
        "POSSetName requires FLEx API integration. "
        "Will write to pos.Name.set_String(ws_handle, name)"
    )
    # FLEx integration:
    # pos_obj = resolve_pos(pos_or_hvo, project)
    # validate_object_exists(pos_obj, f"POS {pos_or_hvo}")
    # with UndoableUnitOfWork(project, "Set POS Name"):
    #     if wsHandle is None:
    #         wsHandle = project.DefaultAnalysisWs
    #     pos_obj.Name.set_String(wsHandle, name)


def POSGetAbbreviation(
    pos_or_hvo: IPartOfSpeech | HVO,
    wsHandle: Optional[WritingSystemHandle] = None
) -> str:
    """
    Get the abbreviation of a Part of Speech.

    Args:
        pos_or_hvo: The POS object or its HVO
        wsHandle: Optional writing system (defaults to analysis WS)

    Returns:
        str: The POS abbreviation

    Raises:
        ObjectNotFoundError: If the POS doesn't exist

    Example:
        >>> pos = POSFind("Noun")
        >>> abbr = POSGetAbbreviation(pos)
        >>> print(abbr)
        N

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "POSGetAbbreviation requires FLEx API integration. "
        "Will read pos.Abbreviation.get_String(ws_handle)"
    )
    # FLEx integration:
    # pos_obj = resolve_pos(pos_or_hvo, project)
    # validate_object_exists(pos_obj, f"POS {pos_or_hvo}")
    # if wsHandle is None:
    #     return pos_obj.Abbreviation.BestAnalysisAlternative.Text
    # return pos_obj.Abbreviation.get_String(wsHandle).Text


def POSSetAbbreviation(
    pos_or_hvo: IPartOfSpeech | HVO,
    abbr: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> None:
    """
    Set the abbreviation of a Part of Speech.

    Args:
        pos_or_hvo: The POS object or its HVO
        abbr: The new abbreviation
        wsHandle: Optional writing system (defaults to analysis WS)

    Raises:
        InvalidParameterError: If abbreviation is empty
        ObjectNotFoundError: If the POS doesn't exist

    Example:
        >>> pos = POSFind("Noun")
        >>> POSSetAbbreviation(pos, "N")

    TODO: FLEx API integration required
    """
    validate_non_empty_string(abbr, "abbreviation")

    raise NotImplementedYetError(
        "POSSetAbbreviation requires FLEx API integration. "
        "Will write to pos.Abbreviation.set_String(ws_handle, abbr)"
    )
    # FLEx integration:
    # pos_obj = resolve_pos(pos_or_hvo, project)
    # validate_object_exists(pos_obj, f"POS {pos_or_hvo}")
    # with UndoableUnitOfWork(project, "Set POS Abbreviation"):
    #     if wsHandle is None:
    #         wsHandle = project.DefaultAnalysisWs
    #     pos_obj.Abbreviation.set_String(wsHandle, abbr)


def POSGetSubcategories(pos_or_hvo: IPartOfSpeech | HVO) -> List[IPartOfSpeech]:
    """
    Get all subcategories of a Part of Speech.

    Args:
        pos_or_hvo: The POS object or its HVO

    Returns:
        List[IPartOfSpeech]: List of subcategory POS objects (empty if none)

    Raises:
        ObjectNotFoundError: If the POS doesn't exist

    Example:
        >>> noun = POSFind("Noun")
        >>> subcats = POSGetSubcategories(noun)
        >>> for subcat in subcats:
        ...     print(POSGetName(subcat))
        Proper Noun
        Common Noun
        Count Noun
        Mass Noun

    Notes:
        - Returns direct children only (not recursive)
        - Empty list if no subcategories
        - Subcategories form a hierarchy for fine-grained classification

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "POSGetSubcategories requires FLEx API integration. "
        "Will read pos.SubPossibilitiesOS"
    )
    # FLEx integration:
    # pos_obj = resolve_pos(pos_or_hvo, project)
    # validate_object_exists(pos_obj, f"POS {pos_or_hvo}")
    # return list(pos_obj.SubPossibilitiesOS)


__all__ = [
    'POSGetAll',
    'POSCreate',
    'POSDelete',
    'POSExists',
    'POSFind',
    'POSGetName',
    'POSSetName',
    'POSGetAbbreviation',
    'POSSetAbbreviation',
    'POSGetSubcategories',
]
