"""
Inflection Class and Feature Structure Operations

This module provides operations for managing inflection classes and feature
structures in FLEx.

Inflection classes group lexical items that inflect similarly (e.g., Latin
noun declensions, Spanish verb conjugations). Feature structures represent
grammatical features like person, number, gender, tense, aspect, etc.

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

from typing import Generator, Optional, List, Any
from flexlibs_dev.core.types import (
    IMoInflClass,
    IFsFeatStruc,
    IFsFeatureDefn,
    IFsSymFeatVal,
    IPartOfSpeech,
    HVO,
    WritingSystemHandle,
)
from flexlibs_dev.core.resolvers import resolve_object, resolve_pos
from flexlibs_dev.core.validators import validate_non_empty_string, validate_object_exists
from flexlibs_dev.core.exceptions import (
    ObjectNotFoundError,
    DuplicateObjectError,
    InvalidParameterError,
    NotImplementedYetError,
)


def InflectionClassGetAll() -> Generator[IMoInflClass, None, None]:
    """
    Get all inflection classes in the project.

    Yields:
        IMoInflClass: Each inflection class

    Example:
        >>> for infl_class in InflectionClassGetAll():
        ...     name = InflectionClassGetName(infl_class)
        ...     print(f"Class: {name}")
        Class: First Declension
        Class: Second Declension
        Class: Irregular Verb
        Class: Regular Verb

    Notes:
        - Returns classes for all parts of speech
        - Order follows FLEx database order
        - Classes organize lexical items by inflectional pattern

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "InflectionClassGetAll requires FLEx API integration. "
        "Will iterate over project.MorphologicalDataOA.InflectionClassesOA"
    )
    # FLEx integration:
    # for infl_class in project.MorphologicalDataOA.InflectionClassesOA.PossibilitiesOS:
    #     yield infl_class


def InflectionClassCreate(
    name: str,
    pos: IPartOfSpeech
) -> IMoInflClass:
    """
    Create a new inflection class.

    Args:
        name: The name of the inflection class (e.g., "First Declension")
        pos: The part of speech this class applies to

    Returns:
        IMoInflClass: The newly created inflection class

    Raises:
        InvalidParameterError: If name is empty or pos is None
        DuplicateObjectError: If a class with this name already exists for this POS

    Example:
        >>> # Create Latin noun declension classes
        >>> noun = POSFind("Noun")
        >>> first_decl = InflectionClassCreate("First Declension", noun)
        >>> second_decl = InflectionClassCreate("Second Declension", noun)
        >>> print(InflectionClassGetName(first_decl))
        First Declension

        >>> # Create Spanish verb conjugation classes
        >>> verb = POSFind("Verb")
        >>> ar_verbs = InflectionClassCreate("AR Verbs", verb)
        >>> er_verbs = InflectionClassCreate("ER Verbs", verb)
        >>> ir_verbs = InflectionClassCreate("IR Verbs", verb)

    Notes:
        - Inflection classes group entries that inflect the same way
        - Each POS can have multiple classes
        - Classes can define templates for affixes and features

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")
    if pos is None:
        raise InvalidParameterError("pos cannot be None")

    raise NotImplementedYetError(
        "InflectionClassCreate requires FLEx API integration. "
        "Will create new IMoInflClass"
    )
    # FLEx integration:
    # from SIL.LCModel import IMoInflClass, UndoableUnitOfWork
    # with UndoableUnitOfWork(project, "Create Inflection Class"):
    #     infl_class = project.ServiceLocator.GetInstance(IMoInflClassFactory).Create()
    #     ws_handle = project.DefaultAnalysisWs
    #     infl_class.Name.set_String(ws_handle, name)
    #     infl_class.PartOfSpeechRA = pos
    #     project.MorphologicalDataOA.InflectionClassesOA.PossibilitiesOS.Append(infl_class)
    #     return infl_class


def InflectionClassDelete(class_or_hvo: IMoInflClass | HVO) -> None:
    """
    Delete an inflection class.

    Args:
        class_or_hvo: The inflection class object or its HVO to delete

    Raises:
        ObjectNotFoundError: If the class doesn't exist
        RuntimeError: If the class is in use and cannot be deleted

    Example:
        >>> infl_class = InflectionClassFind("Obsolete Class")
        >>> if infl_class:
        ...     InflectionClassDelete(infl_class)

    Warning:
        - Cannot delete if lexical entries reference this class
        - Check usage before deletion
        - Deletion is permanent and cannot be undone outside a transaction

    Notes:
        - Entries must be reassigned to another class first
        - Or the class reference must be cleared

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "InflectionClassDelete requires FLEx API integration. "
        "Will remove class from InflectionClassesOA.PossibilitiesOS"
    )
    # FLEx integration:
    # class_obj = resolve_object(class_or_hvo, project)
    # validate_object_exists(class_obj, f"Inflection Class {class_or_hvo}")
    # with UndoableUnitOfWork(project, "Delete Inflection Class"):
    #     project.MorphologicalDataOA.InflectionClassesOA.PossibilitiesOS.Remove(class_obj)


def InflectionClassGetName(
    class_or_hvo: IMoInflClass | HVO,
    wsHandle: Optional[WritingSystemHandle] = None
) -> str:
    """
    Get the name of an inflection class.

    Args:
        class_or_hvo: The inflection class object or its HVO
        wsHandle: Optional writing system (defaults to analysis WS)

    Returns:
        str: The inflection class name

    Raises:
        ObjectNotFoundError: If the class doesn't exist

    Example:
        >>> infl_class = InflectionClassCreate("First Declension", noun)
        >>> name = InflectionClassGetName(infl_class)
        >>> print(name)
        First Declension

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "InflectionClassGetName requires FLEx API integration. "
        "Will read infl_class.Name.get_String(ws_handle)"
    )
    # FLEx integration:
    # class_obj = resolve_object(class_or_hvo, project)
    # validate_object_exists(class_obj, f"Inflection Class {class_or_hvo}")
    # if wsHandle is None:
    #     return class_obj.Name.BestAnalysisAlternative.Text
    # return class_obj.Name.get_String(wsHandle).Text


def InflectionClassSetName(
    class_or_hvo: IMoInflClass | HVO,
    name: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> None:
    """
    Set the name of an inflection class.

    Args:
        class_or_hvo: The inflection class object or its HVO
        name: The new name
        wsHandle: Optional writing system (defaults to analysis WS)

    Raises:
        InvalidParameterError: If name is empty
        ObjectNotFoundError: If the class doesn't exist

    Example:
        >>> infl_class = InflectionClassCreate("1st Decl", noun)
        >>> InflectionClassSetName(infl_class, "First Declension")
        >>> print(InflectionClassGetName(infl_class))
        First Declension

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")

    raise NotImplementedYetError(
        "InflectionClassSetName requires FLEx API integration. "
        "Will write to infl_class.Name.set_String(ws_handle, name)"
    )
    # FLEx integration:
    # class_obj = resolve_object(class_or_hvo, project)
    # validate_object_exists(class_obj, f"Inflection Class {class_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Inflection Class Name"):
    #     if wsHandle is None:
    #         wsHandle = project.DefaultAnalysisWs
    #     class_obj.Name.set_String(wsHandle, name)


def FeatureStructureGetAll() -> Generator[IFsFeatStruc, None, None]:
    """
    Get all feature structures in the project.

    Yields:
        IFsFeatStruc: Each feature structure

    Example:
        >>> for fs in FeatureStructureGetAll():
        ...     # Feature structures represent grammatical features
        ...     print(f"Feature structure: {fs.Hvo}")

    Notes:
        - Feature structures encode grammatical information
        - Used in morphosyntactic descriptions
        - Can represent person, number, gender, tense, aspect, etc.

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "FeatureStructureGetAll requires FLEx API integration. "
        "Will iterate over feature structures in project"
    )
    # FLEx integration:
    # for fs in project.MsFeatureSystemOA.FeaturesOS:
    #     yield fs


def FeatureStructureCreate(
    name: str,
    type: str
) -> IFsFeatStruc:
    """
    Create a new feature structure.

    Args:
        name: The name of the feature structure
        type: The type of feature structure (e.g., "inflectional", "phonological")

    Returns:
        IFsFeatStruc: The newly created feature structure

    Raises:
        InvalidParameterError: If name or type is empty

    Example:
        >>> # Create a feature structure for verb features
        >>> verb_fs = FeatureStructureCreate("Verb Features", "inflectional")
        >>> # Add features like tense, aspect, mood to this structure

        >>> # Create a feature structure for noun features
        >>> noun_fs = FeatureStructureCreate("Noun Features", "inflectional")
        >>> # Add features like number, gender, case to this structure

    Notes:
        - Feature structures organize related features
        - Types help categorize feature systems
        - Features are added separately after creation

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")
    validate_non_empty_string(type, "type")

    raise NotImplementedYetError(
        "FeatureStructureCreate requires FLEx API integration. "
        "Will create new IFsFeatStruc"
    )
    # FLEx integration:
    # from SIL.LCModel import IFsFeatStruc, UndoableUnitOfWork
    # with UndoableUnitOfWork(project, "Create Feature Structure"):
    #     fs = project.ServiceLocator.GetInstance(IFsFeatStrucFactory).Create()
    #     # Set properties
    #     return fs


def FeatureStructureDelete(fs_or_hvo: IFsFeatStruc | HVO) -> None:
    """
    Delete a feature structure.

    Args:
        fs_or_hvo: The feature structure object or its HVO to delete

    Raises:
        ObjectNotFoundError: If the feature structure doesn't exist
        RuntimeError: If the structure is in use

    Example:
        >>> fs = FeatureStructureCreate("Test FS", "test")
        >>> FeatureStructureDelete(fs)

    Warning:
        - Cannot delete if referenced by entries or rules
        - Check dependencies before deletion
        - Deletion is permanent

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "FeatureStructureDelete requires FLEx API integration. "
        "Will remove feature structure from collection"
    )
    # FLEx integration:
    # fs_obj = resolve_object(fs_or_hvo, project)
    # validate_object_exists(fs_obj, f"Feature Structure {fs_or_hvo}")
    # with UndoableUnitOfWork(project, "Delete Feature Structure"):
    #     # Remove from collection
    #     pass


def FeatureGetAll() -> Generator[IFsFeatureDefn, None, None]:
    """
    Get all feature definitions in the project.

    Yields:
        IFsFeatureDefn: Each feature definition

    Example:
        >>> for feature in FeatureGetAll():
        ...     # Features like person, number, tense, etc.
        ...     print(f"Feature: {feature.Hvo}")

    Notes:
        - Feature definitions describe grammatical categories
        - Each feature has a name and set of possible values
        - Examples: person (1st/2nd/3rd), number (sg/pl), tense (past/present/future)

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "FeatureGetAll requires FLEx API integration. "
        "Will iterate over feature definitions"
    )
    # FLEx integration:
    # for feature in project.MsFeatureSystemOA.FeaturesOS:
    #     yield feature


def FeatureCreate(
    name: str,
    type: str
) -> IFsFeatureDefn:
    """
    Create a new feature definition.

    Args:
        name: The name of the feature (e.g., "person", "number", "tense")
        type: The type of feature (e.g., "inflectional", "derivational")

    Returns:
        IFsFeatureDefn: The newly created feature definition

    Raises:
        InvalidParameterError: If name or type is empty
        DuplicateObjectError: If a feature with this name already exists

    Example:
        >>> # Create a person feature
        >>> person = FeatureCreate("person", "inflectional")
        >>> # Add values: 1st, 2nd, 3rd

        >>> # Create a number feature
        >>> number = FeatureCreate("number", "inflectional")
        >>> # Add values: singular, plural

        >>> # Create a tense feature
        >>> tense = FeatureCreate("tense", "inflectional")
        >>> # Add values: past, present, future

    Notes:
        - Features define grammatical categories
        - Values must be added separately
        - Features can be shared across multiple POSes

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")
    validate_non_empty_string(type, "type")

    raise NotImplementedYetError(
        "FeatureCreate requires FLEx API integration. "
        "Will create new IFsFeatureDefn"
    )
    # FLEx integration:
    # from SIL.LCModel import IFsFeatureDefn, UndoableUnitOfWork
    # with UndoableUnitOfWork(project, "Create Feature"):
    #     feature = project.ServiceLocator.GetInstance(IFsFeatureDefnFactory).Create()
    #     ws_handle = project.DefaultAnalysisWs
    #     # Set name and type
    #     return feature


def FeatureDelete(feature_or_hvo: IFsFeatureDefn | HVO) -> None:
    """
    Delete a feature definition.

    Args:
        feature_or_hvo: The feature definition object or its HVO to delete

    Raises:
        ObjectNotFoundError: If the feature doesn't exist
        RuntimeError: If the feature is in use

    Example:
        >>> feature = FeatureCreate("test_feature", "test")
        >>> FeatureDelete(feature)

    Warning:
        - Cannot delete if used in feature structures
        - Cannot delete if referenced by entries
        - Check dependencies before deletion

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "FeatureDelete requires FLEx API integration. "
        "Will remove feature from collection"
    )
    # FLEx integration:
    # feature_obj = resolve_object(feature_or_hvo, project)
    # validate_object_exists(feature_obj, f"Feature {feature_or_hvo}")
    # with UndoableUnitOfWork(project, "Delete Feature"):
    #     # Remove from collection
    #     pass


def FeatureGetValues(feature_or_hvo: IFsFeatureDefn | HVO) -> List[IFsSymFeatVal]:
    """
    Get all possible values for a feature.

    Args:
        feature_or_hvo: The feature definition object or its HVO

    Returns:
        List[IFsSymFeatVal]: List of symbolic feature values (empty if none)

    Raises:
        ObjectNotFoundError: If the feature doesn't exist

    Example:
        >>> person = FeatureCreate("person", "inflectional")
        >>> # After adding values 1st, 2nd, 3rd...
        >>> values = FeatureGetValues(person)
        >>> for val in values:
        ...     print(f"Value: {val}")  # 1st, 2nd, 3rd

        >>> number = FeatureCreate("number", "inflectional")
        >>> # After adding values singular, plural...
        >>> values = FeatureGetValues(number)
        >>> print(f"Number has {len(values)} values")  # 2

    Notes:
        - Returns symbolic values (named choices)
        - Empty list if no values defined yet
        - Values represent the possible settings for this feature
        - Example: person feature has values [1st, 2nd, 3rd]
        - Example: number feature has values [singular, plural, dual]

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "FeatureGetValues requires FLEx API integration. "
        "Will read feature.ValuesOC or similar"
    )
    # FLEx integration:
    # feature_obj = resolve_object(feature_or_hvo, project)
    # validate_object_exists(feature_obj, f"Feature {feature_or_hvo}")
    # if hasattr(feature_obj, 'ValuesOC'):
    #     return list(feature_obj.ValuesOC)
    # return []


__all__ = [
    'InflectionClassGetAll',
    'InflectionClassCreate',
    'InflectionClassDelete',
    'InflectionClassGetName',
    'InflectionClassSetName',
    'FeatureStructureGetAll',
    'FeatureStructureCreate',
    'FeatureStructureDelete',
    'FeatureGetAll',
    'FeatureCreate',
    'FeatureDelete',
    'FeatureGetValues',
]
