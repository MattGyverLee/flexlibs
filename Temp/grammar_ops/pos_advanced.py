"""
Parts of Speech Advanced Operations

This module provides advanced operations for Parts of Speech (POS) in FLEx,
including subcategory management, catalog linking, and morphological relationships.

These operations extend the basic CRUD operations with functionality for
managing POS hierarchies, inflection classes, affix slots, and usage statistics.

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

from typing import List, Union
from flexlibs_dev.core.types import (
    IPartOfSpeech,
    IMoInflClass,
    IMoInflAffixSlot,
    HVO,
)
from flexlibs_dev.core.resolvers import resolve_pos
from flexlibs_dev.core.validators import validate_non_empty_string, validate_object_exists
from flexlibs_dev.core.exceptions import (
    ObjectNotFoundError,
    DuplicateObjectError,
    InvalidParameterError,
    NotImplementedYetError,
)


def POSAddSubcategory(
    pos_or_hvo: IPartOfSpeech | HVO,
    name: str,
    abbreviation: str
) -> IPartOfSpeech:
    """
    Add a subcategory to a Part of Speech.

    Args:
        pos_or_hvo: The parent POS object or its HVO
        name: Name of the subcategory (e.g., "Proper Noun")
        abbreviation: Short abbreviation (e.g., "PN")

    Returns:
        IPartOfSpeech: The newly created subcategory POS object

    Raises:
        ObjectNotFoundError: If the parent POS doesn't exist
        InvalidParameterError: If name or abbreviation is empty
        DuplicateObjectError: If subcategory with this name already exists

    Example:
        >>> noun = POSFind("Noun")
        >>> proper = POSAddSubcategory(noun, "Proper Noun", "PN")
        >>> print(POSGetName(proper))
        Proper Noun

        >>> # Add multiple subcategories
        >>> common = POSAddSubcategory(noun, "Common Noun", "CN")
        >>> count = POSAddSubcategory(common, "Count Noun", "CntN")

    Notes:
        - Subcategories inherit properties from their parent
        - Names must be unique within the parent's subcategories
        - Creates hierarchical classification for fine-grained analysis
        - Subcategories can have their own subcategories (nested hierarchy)

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")
    validate_non_empty_string(abbreviation, "abbreviation")

    raise NotImplementedYetError(
        "POSAddSubcategory requires FLEx API integration. "
        "Will create subcategory in pos.SubPossibilitiesOS"
    )
    # FLEx integration:
    # pos_obj = resolve_pos(pos_or_hvo, project)
    # validate_object_exists(pos_obj, f"POS {pos_or_hvo}")
    #
    # # Check for duplicate
    # for subcat in pos_obj.SubPossibilitiesOS:
    #     if subcat.Name.BestAnalysisAlternative.Text.lower() == name.lower():
    #         raise DuplicateObjectError(f"Subcategory '{name}' already exists")
    #
    # with UndoableUnitOfWork(project, "Add POS Subcategory"):
    #     subcat = project.ServiceLocator.GetInstance(IPartOfSpeechFactory).Create()
    #     subcat.Name.set_String(ws_handle, name)
    #     subcat.Abbreviation.set_String(ws_handle, abbreviation)
    #     pos_obj.SubPossibilitiesOS.Append(subcat)
    #     return subcat


def POSRemoveSubcategory(
    pos_or_hvo: IPartOfSpeech | HVO,
    subcat: IPartOfSpeech | HVO
) -> None:
    """
    Remove a subcategory from a Part of Speech.

    Args:
        pos_or_hvo: The parent POS object or its HVO
        subcat: The subcategory POS to remove (object or HVO)

    Raises:
        ObjectNotFoundError: If parent POS or subcategory doesn't exist
        InvalidParameterError: If subcategory is not a child of the parent
        RuntimeError: If subcategory is in use and cannot be removed

    Example:
        >>> noun = POSFind("Noun")
        >>> obsolete = POSFind("Obsolete Noun")
        >>> POSRemoveSubcategory(noun, obsolete)

    Warning:
        - Removing a subcategory in use will raise an error
        - All nested subcategories will also be removed
        - Lexical entries using this subcategory must be updated first

    Notes:
        - Validates that subcat is actually a child of pos_or_hvo
        - Recursive deletion of sub-subcategories
        - Use POSGetEntryCount() to check usage before removal

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "POSRemoveSubcategory requires FLEx API integration. "
        "Will remove from pos.SubPossibilitiesOS"
    )
    # FLEx integration:
    # pos_obj = resolve_pos(pos_or_hvo, project)
    # validate_object_exists(pos_obj, f"POS {pos_or_hvo}")
    #
    # subcat_obj = resolve_pos(subcat, project)
    # validate_object_exists(subcat_obj, f"Subcategory {subcat}")
    #
    # # Verify subcat is actually a child of pos
    # if subcat_obj not in pos_obj.SubPossibilitiesOS:
    #     raise InvalidParameterError(
    #         f"Subcategory {subcat} is not a child of POS {pos_or_hvo}"
    #     )
    #
    # with UndoableUnitOfWork(project, "Remove POS Subcategory"):
    #     pos_obj.SubPossibilitiesOS.Remove(subcat_obj)


def POSGetCatalogSourceId(pos_or_hvo: IPartOfSpeech | HVO) -> str:
    """
    Get the catalog source identifier for a Part of Speech.

    The catalog source ID links a POS to external linguistic ontologies
    and databases such as GOLD (General Ontology for Linguistic Description).

    Args:
        pos_or_hvo: The POS object or its HVO

    Returns:
        str: The catalog source identifier (empty string if not set)

    Raises:
        ObjectNotFoundError: If the POS doesn't exist

    Example:
        >>> noun = POSFind("Noun")
        >>> catalog_id = POSGetCatalogSourceId(noun)
        >>> print(catalog_id)
        GOLD:Noun

        >>> # Check if linked to external catalog
        >>> if POSGetCatalogSourceId(pos):
        ...     print("Linked to linguistic database")

    Notes:
        - Returns empty string if no catalog ID is set
        - Common catalogs: GOLD, ISOcat, etc.
        - Used for interoperability with linguistic databases
        - Format is typically "SOURCE:Identifier" (e.g., "GOLD:Verb")

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "POSGetCatalogSourceId requires FLEx API integration. "
        "Will read pos.CatalogSourceId"
    )
    # FLEx integration:
    # pos_obj = resolve_pos(pos_or_hvo, project)
    # validate_object_exists(pos_obj, f"POS {pos_or_hvo}")
    # return pos_obj.CatalogSourceId if pos_obj.CatalogSourceId else ""


def POSGetInflectionClasses(pos_or_hvo: IPartOfSpeech | HVO) -> List[IMoInflClass]:
    """
    Get all inflection classes associated with a Part of Speech.

    Inflection classes define patterns of morphological inflection
    (e.g., verb conjugation classes, noun declension classes).

    Args:
        pos_or_hvo: The POS object or its HVO

    Returns:
        List[IMoInflClass]: List of inflection classes (empty if none)

    Raises:
        ObjectNotFoundError: If the POS doesn't exist

    Example:
        >>> verb = POSFind("Verb")
        >>> classes = POSGetInflectionClasses(verb)
        >>> for infl_class in classes:
        ...     print(infl_class.Name.BestAnalysisAlternative.Text)
        Strong Verb
        Weak Verb
        Irregular Verb

        >>> # Check if POS has inflection classes
        >>> if POSGetInflectionClasses(noun):
        ...     print("This POS has inflection paradigms")

    Notes:
        - Returns empty list if no inflection classes defined
        - Inflection classes are used in morphological parsing
        - Each class defines a pattern of affixation
        - Different languages have different inflection systems

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "POSGetInflectionClasses requires FLEx API integration. "
        "Will read inflection classes from morphology system"
    )
    # FLEx integration:
    # pos_obj = resolve_pos(pos_or_hvo, project)
    # validate_object_exists(pos_obj, f"POS {pos_or_hvo}")
    #
    # # Get all inflection classes that reference this POS
    # infl_classes = []
    # for infl_class in project.MorphologicalDataOA.ProdRestrictOA.PossibilitiesOS:
    #     if isinstance(infl_class, IMoInflClass) and infl_class.PartOfSpeech == pos_obj:
    #         infl_classes.append(infl_class)
    # return infl_classes


def POSGetAffixSlots(pos_or_hvo: IPartOfSpeech | HVO) -> List[IMoInflAffixSlot]:
    """
    Get all affix slots (template positions) for a Part of Speech.

    Affix slots define the positions where affixes can occur in relation
    to stems of this POS (e.g., prefix slots, suffix slots).

    Args:
        pos_or_hvo: The POS object or its HVO

    Returns:
        List[IMoInflAffixSlot]: List of affix slots (empty if none)

    Raises:
        ObjectNotFoundError: If the POS doesn't exist

    Example:
        >>> verb = POSFind("Verb")
        >>> slots = POSGetAffixSlots(verb)
        >>> for slot in slots:
        ...     print(f"{slot.Name.BestAnalysisAlternative.Text}: {slot.Optional}")
        Tense: False
        Aspect: True
        Mood: True

        >>> # Check template complexity
        >>> slot_count = len(POSGetAffixSlots(pos))
        >>> print(f"This POS has {slot_count} affix slots")

    Notes:
        - Returns empty list if no affix template defined
        - Slots are ordered according to the morphological template
        - Each slot can be required or optional
        - Used in morphological parsing and generation
        - Position templates vary by language

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "POSGetAffixSlots requires FLEx API integration. "
        "Will read affix slots from morphology templates"
    )
    # FLEx integration:
    # pos_obj = resolve_pos(pos_or_hvo, project)
    # validate_object_exists(pos_obj, f"POS {pos_or_hvo}")
    #
    # # Get affix slots from the POS's affix template
    # affix_slots = []
    # if hasattr(pos_obj, 'AffixTemplatesOS'):
    #     for template in pos_obj.AffixTemplatesOS:
    #         for slot in template.SlotsRS:
    #             affix_slots.append(slot)
    # return affix_slots


def POSGetEntryCount(pos_or_hvo: IPartOfSpeech | HVO) -> int:
    """
    Get the number of lexical entries using this Part of Speech.

    This count includes entries that use this POS in any of their senses,
    useful for determining if a POS can be safely deleted.

    Args:
        pos_or_hvo: The POS object or its HVO

    Returns:
        int: Number of lexical entries using this POS

    Raises:
        ObjectNotFoundError: If the POS doesn't exist

    Example:
        >>> noun = POSFind("Noun")
        >>> count = POSGetEntryCount(noun)
        >>> print(f"Noun is used by {count} entries")
        Noun is used by 1523 entries

        >>> # Check if safe to delete
        >>> obsolete = POSFind("Obsolete Category")
        >>> if POSGetEntryCount(obsolete) == 0:
        ...     POSDelete(obsolete)
        ... else:
        ...     print("Cannot delete - POS is in use")

    Notes:
        - Count includes all senses of all entries
        - Includes entries where POS is set on any MSA
        - Zero count means safe to delete
        - Recursive: includes subcategories' usage
        - May be slow for large lexicons

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "POSGetEntryCount requires FLEx API integration. "
        "Will count lexical entries referencing this POS"
    )
    # FLEx integration:
    # pos_obj = resolve_pos(pos_or_hvo, project)
    # validate_object_exists(pos_obj, f"POS {pos_or_hvo}")
    #
    # count = 0
    # for entry in project.LexiconOA.EntriesOC:
    #     for sense in entry.AllSenses:
    #         if hasattr(sense, 'MorphoSyntaxAnalysisRA'):
    #             msa = sense.MorphoSyntaxAnalysisRA
    #             if hasattr(msa, 'PartOfSpeechRA') and msa.PartOfSpeechRA == pos_obj:
    #                 count += 1
    #                 break  # Count each entry only once
    # return count


__all__ = [
    'POSAddSubcategory',
    'POSRemoveSubcategory',
    'POSGetCatalogSourceId',
    'POSGetInflectionClasses',
    'POSGetAffixSlots',
    'POSGetEntryCount',
]
