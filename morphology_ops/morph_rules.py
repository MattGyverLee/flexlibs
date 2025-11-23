"""
Morphological Rule Operations

This module provides operations for managing morphological rules in FLEx.

Morphological rules define phonological, morphological, or orthographic changes
that apply during word formation. Examples include vowel harmony, consonant
mutation, assimilation, metathesis, and other morphophonemic processes.

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

from typing import Generator, Optional
from flexlibs_dev.core.types import (
    IMoMorphRule,
    IMoStratum,
    HVO,
    WritingSystemHandle,
)
from flexlibs_dev.core.resolvers import resolve_object
from flexlibs_dev.core.validators import validate_non_empty_string, validate_object_exists
from flexlibs_dev.core.exceptions import (
    ObjectNotFoundError,
    DuplicateObjectError,
    InvalidParameterError,
    NotImplementedYetError,
)


def MorphRuleGetAll() -> Generator[IMoMorphRule, None, None]:
    """
    Get all morphological rules in the project.

    Yields:
        IMoMorphRule: Each morphological rule

    Example:
        >>> for rule in MorphRuleGetAll():
        ...     name = MorphRuleGetName(rule)
        ...     active = MorphRuleIsActive(rule)
        ...     print(f"Rule: {name} (active: {active})")
        Rule: Vowel Harmony (active: True)
        Rule: Nasal Assimilation (active: True)
        Rule: Final Devoicing (active: False)

    Notes:
        - Includes both active and inactive rules
        - Order follows FLEx database order
        - Rules may be organized by stratum

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "MorphRuleGetAll requires FLEx API integration. "
        "Will iterate over project.MorphologicalDataOA.ProdRestrictOA (or similar)"
    )
    # FLEx integration:
    # for rule in project.MorphologicalDataOA.MorphRulesOA:
    #     yield rule


def MorphRuleCreate(
    name: str,
    description: Optional[str] = None
) -> IMoMorphRule:
    """
    Create a new morphological rule.

    Args:
        name: The name of the rule (e.g., "Vowel Harmony", "Final Devoicing")
        description: Optional description of the rule's application

    Returns:
        IMoMorphRule: The newly created morphological rule

    Raises:
        InvalidParameterError: If name is empty
        DuplicateObjectError: If a rule with this name already exists

    Example:
        >>> # Create a vowel harmony rule
        >>> rule = MorphRuleCreate(
        ...     "Vowel Harmony",
        ...     "Back vowels cause following vowels to become back"
        ... )
        >>> print(MorphRuleGetName(rule))
        Vowel Harmony

        >>> # Create an assimilation rule
        >>> rule = MorphRuleCreate("Nasal Assimilation")
        >>> MorphRuleSetDescription(rule, "Nasals assimilate to following stops")

    Notes:
        - Rules are initially created as inactive
        - Use MorphRuleSetActive() to enable
        - Rule logic must be defined separately in FLEx

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")

    raise NotImplementedYetError(
        "MorphRuleCreate requires FLEx API integration. "
        "Will create new IMoMorphRule"
    )
    # FLEx integration:
    # from SIL.LCModel import IMoMorphRule, UndoableUnitOfWork
    # with UndoableUnitOfWork(project, "Create Morph Rule"):
    #     rule = project.ServiceLocator.GetInstance(IMoMorphRuleFactory).Create()
    #     ws_handle = project.DefaultAnalysisWs
    #     rule.Name.set_String(ws_handle, name)
    #     if description:
    #         rule.Description.set_String(ws_handle, description)
    #     # Add to appropriate collection
    #     return rule


def MorphRuleDelete(rule_or_hvo: IMoMorphRule | HVO) -> None:
    """
    Delete a morphological rule.

    Args:
        rule_or_hvo: The rule object or its HVO to delete

    Raises:
        ObjectNotFoundError: If the rule doesn't exist
        RuntimeError: If the rule is in use and cannot be deleted

    Example:
        >>> rule = MorphRuleFind("Obsolete Rule")
        >>> if rule:
        ...     MorphRuleDelete(rule)

    Warning:
        - Deleting a rule in use may affect parsing
        - Check dependencies before deletion
        - Deletion is permanent and cannot be undone outside a transaction

    Notes:
        - Consider deactivating instead of deleting
        - Parser should be rerun after rule deletion

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "MorphRuleDelete requires FLEx API integration. "
        "Will remove rule from collection"
    )
    # FLEx integration:
    # rule_obj = resolve_object(rule_or_hvo, project)
    # validate_object_exists(rule_obj, f"Rule {rule_or_hvo}")
    # with UndoableUnitOfWork(project, "Delete Morph Rule"):
    #     # Remove from appropriate collection
    #     pass


def MorphRuleGetName(
    rule_or_hvo: IMoMorphRule | HVO,
    wsHandle: Optional[WritingSystemHandle] = None
) -> str:
    """
    Get the name of a morphological rule.

    Args:
        rule_or_hvo: The rule object or its HVO
        wsHandle: Optional writing system (defaults to analysis WS)

    Returns:
        str: The rule name

    Raises:
        ObjectNotFoundError: If the rule doesn't exist

    Example:
        >>> rule = MorphRuleCreate("Vowel Harmony")
        >>> name = MorphRuleGetName(rule)
        >>> print(name)
        Vowel Harmony

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "MorphRuleGetName requires FLEx API integration. "
        "Will read rule.Name.get_String(ws_handle)"
    )
    # FLEx integration:
    # rule_obj = resolve_object(rule_or_hvo, project)
    # validate_object_exists(rule_obj, f"Rule {rule_or_hvo}")
    # if wsHandle is None:
    #     return rule_obj.Name.BestAnalysisAlternative.Text
    # return rule_obj.Name.get_String(wsHandle).Text


def MorphRuleSetName(
    rule_or_hvo: IMoMorphRule | HVO,
    name: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> None:
    """
    Set the name of a morphological rule.

    Args:
        rule_or_hvo: The rule object or its HVO
        name: The new name
        wsHandle: Optional writing system (defaults to analysis WS)

    Raises:
        InvalidParameterError: If name is empty
        ObjectNotFoundError: If the rule doesn't exist

    Example:
        >>> rule = MorphRuleCreate("Harmony")
        >>> MorphRuleSetName(rule, "Vowel Harmony")
        >>> print(MorphRuleGetName(rule))
        Vowel Harmony

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")

    raise NotImplementedYetError(
        "MorphRuleSetName requires FLEx API integration. "
        "Will write to rule.Name.set_String(ws_handle, name)"
    )
    # FLEx integration:
    # rule_obj = resolve_object(rule_or_hvo, project)
    # validate_object_exists(rule_obj, f"Rule {rule_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Rule Name"):
    #     if wsHandle is None:
    #         wsHandle = project.DefaultAnalysisWs
    #     rule_obj.Name.set_String(wsHandle, name)


def MorphRuleGetDescription(
    rule_or_hvo: IMoMorphRule | HVO,
    wsHandle: Optional[WritingSystemHandle] = None
) -> str:
    """
    Get the description of a morphological rule.

    Args:
        rule_or_hvo: The rule object or its HVO
        wsHandle: Optional writing system (defaults to analysis WS)

    Returns:
        str: The rule description (empty string if not set)

    Raises:
        ObjectNotFoundError: If the rule doesn't exist

    Example:
        >>> rule = MorphRuleCreate("Vowel Harmony", "Back/front harmony")
        >>> desc = MorphRuleGetDescription(rule)
        >>> print(desc)
        Back/front harmony

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "MorphRuleGetDescription requires FLEx API integration. "
        "Will read rule.Description.get_String(ws_handle)"
    )
    # FLEx integration:
    # rule_obj = resolve_object(rule_or_hvo, project)
    # validate_object_exists(rule_obj, f"Rule {rule_or_hvo}")
    # if wsHandle is None:
    #     return rule_obj.Description.BestAnalysisAlternative.Text
    # return rule_obj.Description.get_String(wsHandle).Text


def MorphRuleSetDescription(
    rule_or_hvo: IMoMorphRule | HVO,
    desc: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> None:
    """
    Set the description of a morphological rule.

    Args:
        rule_or_hvo: The rule object or its HVO
        desc: The new description
        wsHandle: Optional writing system (defaults to analysis WS)

    Raises:
        ObjectNotFoundError: If the rule doesn't exist

    Example:
        >>> rule = MorphRuleCreate("Nasal Assimilation")
        >>> MorphRuleSetDescription(
        ...     rule,
        ...     "Nasals assimilate to the place of articulation of following stops"
        ... )

    Notes:
        - Empty string is valid (clears description)
        - Description is for documentation only

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "MorphRuleSetDescription requires FLEx API integration. "
        "Will write to rule.Description.set_String(ws_handle, desc)"
    )
    # FLEx integration:
    # rule_obj = resolve_object(rule_or_hvo, project)
    # validate_object_exists(rule_obj, f"Rule {rule_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Rule Description"):
    #     if wsHandle is None:
    #         wsHandle = project.DefaultAnalysisWs
    #     rule_obj.Description.set_String(wsHandle, desc)


def MorphRuleGetStratum(rule_or_hvo: IMoMorphRule | HVO) -> IMoStratum:
    """
    Get the stratum of a morphological rule.

    Args:
        rule_or_hvo: The rule object or its HVO

    Returns:
        IMoStratum: The stratum containing this rule (or None)

    Raises:
        ObjectNotFoundError: If the rule doesn't exist

    Example:
        >>> rule = MorphRuleCreate("Vowel Harmony")
        >>> stratum = MorphRuleGetStratum(rule)
        >>> if stratum:
        ...     print(StratumGetName(stratum))
        Lexical Phonology

    Notes:
        - Strata organize rules into ordered layers
        - Common strata: lexical, post-lexical, phonological
        - Rules in earlier strata apply before later strata
        - Returns None if rule not assigned to a stratum

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "MorphRuleGetStratum requires FLEx API integration. "
        "Will read rule.StratumRA"
    )
    # FLEx integration:
    # rule_obj = resolve_object(rule_or_hvo, project)
    # validate_object_exists(rule_obj, f"Rule {rule_or_hvo}")
    # return rule_obj.StratumRA


def MorphRuleSetStratum(
    rule_or_hvo: IMoMorphRule | HVO,
    stratum: IMoStratum
) -> None:
    """
    Set the stratum of a morphological rule.

    Args:
        rule_or_hvo: The rule object or its HVO
        stratum: The stratum to assign (or None to unassign)

    Raises:
        ObjectNotFoundError: If the rule doesn't exist

    Example:
        >>> rule = MorphRuleCreate("Vowel Harmony")
        >>> lexical = StratumFind("Lexical")
        >>> MorphRuleSetStratum(rule, lexical)

    Notes:
        - Stratum determines rule ordering
        - Pass None to remove from stratum
        - Parser may need updating after stratum changes

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "MorphRuleSetStratum requires FLEx API integration. "
        "Will write to rule.StratumRA"
    )
    # FLEx integration:
    # rule_obj = resolve_object(rule_or_hvo, project)
    # validate_object_exists(rule_obj, f"Rule {rule_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Rule Stratum"):
    #     rule_obj.StratumRA = stratum


def MorphRuleIsActive(rule_or_hvo: IMoMorphRule | HVO) -> bool:
    """
    Check if a morphological rule is active.

    Args:
        rule_or_hvo: The rule object or its HVO

    Returns:
        bool: True if rule is active, False otherwise

    Raises:
        ObjectNotFoundError: If the rule doesn't exist

    Example:
        >>> rule = MorphRuleCreate("Vowel Harmony")
        >>> if not MorphRuleIsActive(rule):
        ...     MorphRuleSetActive(rule, True)
        >>> print(MorphRuleIsActive(rule))
        True

    Notes:
        - Only active rules are applied during parsing/generation
        - New rules default to inactive
        - Use MorphRuleSetActive() to enable/disable

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "MorphRuleIsActive requires FLEx API integration. "
        "Will read rule.Active (or similar property)"
    )
    # FLEx integration:
    # rule_obj = resolve_object(rule_or_hvo, project)
    # validate_object_exists(rule_obj, f"Rule {rule_or_hvo}")
    # return getattr(rule_obj, 'Active', False)


def MorphRuleSetActive(
    rule_or_hvo: IMoMorphRule | HVO,
    active: bool
) -> None:
    """
    Set whether a morphological rule is active.

    Args:
        rule_or_hvo: The rule object or its HVO
        active: True to activate, False to deactivate

    Raises:
        ObjectNotFoundError: If the rule doesn't exist
        InvalidParameterError: If active is not a boolean

    Example:
        >>> rule = MorphRuleCreate("Vowel Harmony")
        >>> MorphRuleSetActive(rule, True)
        >>> print(MorphRuleIsActive(rule))
        True

        >>> # Temporarily disable a rule
        >>> MorphRuleSetActive(rule, False)

    Notes:
        - Deactivating is safer than deleting (can be re-enabled)
        - Parser should be rerun after activation changes
        - Consider testing with rule active/inactive

    TODO: FLEx API integration required
    """
    if not isinstance(active, bool):
        raise InvalidParameterError("active must be a boolean")

    raise NotImplementedYetError(
        "MorphRuleSetActive requires FLEx API integration. "
        "Will write to rule.Active (or similar property)"
    )
    # FLEx integration:
    # rule_obj = resolve_object(rule_or_hvo, project)
    # validate_object_exists(rule_obj, f"Rule {rule_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Rule Active"):
    #     rule_obj.Active = active


__all__ = [
    'MorphRuleGetAll',
    'MorphRuleCreate',
    'MorphRuleDelete',
    'MorphRuleGetName',
    'MorphRuleSetName',
    'MorphRuleGetDescription',
    'MorphRuleSetDescription',
    'MorphRuleGetStratum',
    'MorphRuleSetStratum',
    'MorphRuleIsActive',
    'MorphRuleSetActive',
]
