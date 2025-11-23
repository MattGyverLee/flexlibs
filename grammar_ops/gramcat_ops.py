"""
Grammatical Categories Operations

This module provides operations for working with Grammatical Categories
in FLEx, which are used to classify and describe grammatical properties.

Grammatical categories include features like person, number, gender, tense,
aspect, mood, case, and other morphosyntactic properties used in linguistic
analysis.

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

from typing import Generator, Optional, List
from flexlibs_dev.core.types import (
    ICmPossibility,
    HVO,
    WritingSystemHandle,
)
from flexlibs_dev.core.resolvers import resolve_possibility
from flexlibs_dev.core.validators import validate_non_empty_string, validate_object_exists
from flexlibs_dev.core.exceptions import (
    ObjectNotFoundError,
    DuplicateObjectError,
    InvalidParameterError,
    NotImplementedYetError,
)


def GramCatGetAll() -> Generator[ICmPossibility, None, None]:
    """
    Get all grammatical categories in the project.

    Yields grammatical categories from the project's grammatical category
    possibility list, which includes person, number, gender, tense, etc.

    Yields:
        ICmPossibility: Each grammatical category in the project

    Example:
        >>> for cat in GramCatGetAll():
        ...     print(GramCatGetName(cat))
        person
        number
        gender
        tense
        aspect
        mood

    Notes:
        - Returns top-level categories only (use GramCatGetSubcategories for children)
        - Categories are returned in their defined order
        - Each category can have subcategories (e.g., person → 1st, 2nd, 3rd)
        - Empty if no categories defined in project

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "GramCatGetAll requires FLEx API integration. "
        "Will iterate over project.MsFeatureSystemOA.TypesOC or similar list"
    )
    # FLEx integration:
    # for cat in project.MsFeatureSystemOA.TypesOC:
    #     yield cat


def GramCatCreate(
    name: str,
    parent: Optional[ICmPossibility | HVO] = None
) -> ICmPossibility:
    """
    Create a new grammatical category.

    Args:
        name: Name of the category (e.g., "person", "1st person")
        parent: Optional parent category (for creating subcategories)

    Returns:
        ICmPossibility: The newly created grammatical category

    Raises:
        InvalidParameterError: If name is empty
        DuplicateObjectError: If category with this name already exists
        ObjectNotFoundError: If parent doesn't exist

    Example:
        >>> # Create top-level category
        >>> person = GramCatCreate("person")
        >>> print(GramCatGetName(person))
        person

        >>> # Create subcategories
        >>> first = GramCatCreate("1st person", parent=person)
        >>> second = GramCatCreate("2nd person", parent=person)
        >>> third = GramCatCreate("3rd person", parent=person)

        >>> # Create nested hierarchy
        >>> number = GramCatCreate("number")
        >>> singular = GramCatCreate("singular", parent=number)
        >>> plural = GramCatCreate("plural", parent=number)

    Notes:
        - If parent is None, creates a top-level category
        - If parent is provided, creates a subcategory
        - Names should be unique within the same level
        - Used for linguistic feature analysis

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")

    raise NotImplementedYetError(
        "GramCatCreate requires FLEx API integration. "
        "Will create new ICmPossibility in grammatical categories list"
    )
    # FLEx integration:
    # parent_obj = None
    # if parent is not None:
    #     parent_obj = resolve_possibility(parent, project)
    #     validate_object_exists(parent_obj, f"Parent category {parent}")
    #
    # # Check for duplicate
    # target_list = parent_obj.SubPossibilitiesOS if parent_obj else project.MsFeatureSystemOA.TypesOC
    # for cat in target_list:
    #     if cat.Name.BestAnalysisAlternative.Text.lower() == name.lower():
    #         raise DuplicateObjectError(f"Grammatical category '{name}' already exists")
    #
    # with UndoableUnitOfWork(project, "Create Grammatical Category"):
    #     cat = project.ServiceLocator.GetInstance(ICmPossibilityFactory).Create()
    #     cat.Name.set_String(ws_handle, name)
    #     if parent_obj:
    #         parent_obj.SubPossibilitiesOS.Append(cat)
    #     else:
    #         project.MsFeatureSystemOA.TypesOC.Add(cat)
    #     return cat


def GramCatDelete(cat_or_hvo: ICmPossibility | HVO) -> None:
    """
    Delete a grammatical category.

    Args:
        cat_or_hvo: The grammatical category object or its HVO

    Raises:
        ObjectNotFoundError: If the category doesn't exist
        RuntimeError: If the category is in use and cannot be deleted

    Example:
        >>> obsolete = GramCatCreate("obsolete_feature")
        >>> # Later, if not needed...
        >>> GramCatDelete(obsolete)

    Warning:
        - Deleting a category in use will raise an error
        - All subcategories will also be deleted recursively
        - Morphological rules or entries using this may be affected

    Notes:
        - Check usage before deletion
        - Deletion is permanent (unless in a transaction)
        - Also removes all child subcategories

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "GramCatDelete requires FLEx API integration. "
        "Will remove category from possibility list"
    )
    # FLEx integration:
    # cat_obj = resolve_possibility(cat_or_hvo, project)
    # validate_object_exists(cat_obj, f"Grammatical category {cat_or_hvo}")
    #
    # with UndoableUnitOfWork(project, "Delete Grammatical Category"):
    #     # Remove from parent's subcategories or from main list
    #     if cat_obj.Owner:
    #         cat_obj.Owner.SubPossibilitiesOS.Remove(cat_obj)
    #     else:
    #         project.MsFeatureSystemOA.TypesOC.Remove(cat_obj)


def GramCatGetName(
    cat_or_hvo: ICmPossibility | HVO,
    wsHandle: Optional[WritingSystemHandle] = None
) -> str:
    """
    Get the name of a grammatical category.

    Args:
        cat_or_hvo: The category object or its HVO
        wsHandle: Optional writing system (defaults to analysis WS)

    Returns:
        str: The category name in the specified writing system

    Raises:
        ObjectNotFoundError: If the category doesn't exist

    Example:
        >>> person = GramCatCreate("person")
        >>> name = GramCatGetName(person)
        >>> print(name)
        person

        >>> # Get name in vernacular WS
        >>> vern_name = GramCatGetName(person, project.DefaultVernacularWs)

        >>> # List all categories
        >>> for cat in GramCatGetAll():
        ...     print(GramCatGetName(cat))

    Notes:
        - Returns best analysis alternative if wsHandle is None
        - Different writing systems may have different names
        - Commonly lowercase in linguistic notation

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "GramCatGetName requires FLEx API integration. "
        "Will read cat.Name.get_String(ws_handle)"
    )
    # FLEx integration:
    # cat_obj = resolve_possibility(cat_or_hvo, project)
    # validate_object_exists(cat_obj, f"Grammatical category {cat_or_hvo}")
    # if wsHandle is None:
    #     return cat_obj.Name.BestAnalysisAlternative.Text
    # return cat_obj.Name.get_String(wsHandle).Text


def GramCatSetName(
    cat_or_hvo: ICmPossibility | HVO,
    name: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> None:
    """
    Set the name of a grammatical category.

    Args:
        cat_or_hvo: The category object or its HVO
        name: The new name
        wsHandle: Optional writing system (defaults to analysis WS)

    Raises:
        InvalidParameterError: If name is empty
        ObjectNotFoundError: If the category doesn't exist

    Example:
        >>> cat = GramCatCreate("prson")  # typo
        >>> GramCatSetName(cat, "person")  # fix it

        >>> # Set name in vernacular WS
        >>> GramCatSetName(cat, "persona", project.DefaultVernacularWs)

    Notes:
        - Updates the name in the specified writing system
        - Use with caution as it may affect linguistic consistency
        - Changes are immediately visible in the UI

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")

    raise NotImplementedYetError(
        "GramCatSetName requires FLEx API integration. "
        "Will write to cat.Name.set_String(ws_handle, name)"
    )
    # FLEx integration:
    # cat_obj = resolve_possibility(cat_or_hvo, project)
    # validate_object_exists(cat_obj, f"Grammatical category {cat_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Grammatical Category Name"):
    #     if wsHandle is None:
    #         wsHandle = project.DefaultAnalysisWs
    #     cat_obj.Name.set_String(wsHandle, name)


def GramCatGetSubcategories(cat_or_hvo: ICmPossibility | HVO) -> List[ICmPossibility]:
    """
    Get all subcategories of a grammatical category.

    Args:
        cat_or_hvo: The category object or its HVO

    Returns:
        List[ICmPossibility]: List of subcategories (empty if none)

    Raises:
        ObjectNotFoundError: If the category doesn't exist

    Example:
        >>> person = GramCatCreate("person")
        >>> first = GramCatCreate("1st person", parent=person)
        >>> second = GramCatCreate("2nd person", parent=person)
        >>> third = GramCatCreate("3rd person", parent=person)
        >>>
        >>> subcats = GramCatGetSubcategories(person)
        >>> for subcat in subcats:
        ...     print(GramCatGetName(subcat))
        1st person
        2nd person
        3rd person

        >>> # Check if category has subcategories
        >>> if GramCatGetSubcategories(cat):
        ...     print("This category has subcategories")

    Notes:
        - Returns direct children only (not recursive)
        - Empty list if no subcategories
        - Order matches the defined hierarchy
        - Use recursively to traverse full tree

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "GramCatGetSubcategories requires FLEx API integration. "
        "Will read cat.SubPossibilitiesOS"
    )
    # FLEx integration:
    # cat_obj = resolve_possibility(cat_or_hvo, project)
    # validate_object_exists(cat_obj, f"Grammatical category {cat_or_hvo}")
    # return list(cat_obj.SubPossibilitiesOS)


def GramCatGetParent(cat_or_hvo: ICmPossibility | HVO) -> Optional[ICmPossibility]:
    """
    Get the parent category of a grammatical category.

    Args:
        cat_or_hvo: The category object or its HVO

    Returns:
        ICmPossibility | None: Parent category, or None if top-level

    Raises:
        ObjectNotFoundError: If the category doesn't exist

    Example:
        >>> person = GramCatCreate("person")
        >>> first = GramCatCreate("1st person", parent=person)
        >>>
        >>> parent = GramCatGetParent(first)
        >>> print(GramCatGetName(parent))
        person
        >>>
        >>> # Top-level categories have no parent
        >>> print(GramCatGetParent(person))
        None

        >>> # Traverse up the hierarchy
        >>> cat = first
        >>> while cat:
        ...     print(GramCatGetName(cat))
        ...     cat = GramCatGetParent(cat)
        1st person
        person

    Notes:
        - Returns None for top-level categories
        - Use to traverse hierarchy upward
        - Useful for determining category depth
        - Parent-child relationships define category taxonomy

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "GramCatGetParent requires FLEx API integration. "
        "Will read cat.Owner or parent reference"
    )
    # FLEx integration:
    # cat_obj = resolve_possibility(cat_or_hvo, project)
    # validate_object_exists(cat_obj, f"Grammatical category {cat_or_hvo}")
    #
    # # Check if this category has a parent
    # if hasattr(cat_obj, 'Owner') and isinstance(cat_obj.Owner, ICmPossibility):
    #     return cat_obj.Owner
    # return None


__all__ = [
    'GramCatGetAll',
    'GramCatCreate',
    'GramCatDelete',
    'GramCatGetName',
    'GramCatSetName',
    'GramCatGetSubcategories',
    'GramCatGetParent',
]
