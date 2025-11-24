"""
Phonological Environment Operations

This module provides operations for phonological environments in FLEx.

Phonological environments specify the context in which phonological rules apply.
They describe what precedes and follows a segment, using notation like:
- V_V (between vowels)
- #_ (word-initially)
- _# (word-finally)
- C_C (between consonants)

Author: FlexTools Development Team - Phase 2
Date: 2025-11-22
"""

from typing import Generator, Optional
from flexlibs_dev.core.types import (
    IPhEnvironment,
    HVO,
    WritingSystemHandle,
)
from flexlibs_dev.core.resolvers import resolve_environment
from flexlibs_dev.core.validators import validate_non_empty_string, validate_object_exists
from flexlibs_dev.core.exceptions import (
    ObjectNotFoundError,
    DuplicateObjectError,
    InvalidParameterError,
    NotImplementedYetError,
)


def PhonEnvGetAll() -> Generator[IPhEnvironment, None, None]:
    """
    Get all phonological environments in the project.

    Yields:
        IPhEnvironment: Each phonological environment

    Example:
        >>> for env in PhonEnvGetAll():
        ...     name = PhonEnvGetName(env)
        ...     repr = PhonEnvGetStringRepresentation(env)
        ...     print(f"{name}: {repr}")
        Word Initial: #_
        Word Final: _#
        Between Vowels: V_V
        Before Consonant: _C
        After Consonant: C_
        Syllable Initial: $_
        Syllable Final: _$

    Notes:
        - Returns environments in their defined order
        - Environments are reusable across phonological rules
        - Empty if no environments defined

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonEnvGetAll requires FLEx API integration. "
        "Will iterate over project.PhonologicalDataOA.EnvironmentsOS"
    )
    # FLEx integration:
    # phon_data = project.PhonologicalDataOA
    # if phon_data:
    #     for env in phon_data.EnvironmentsOS:
    #         yield env


def PhonEnvCreate(
    name: str,
    description: Optional[str] = None
) -> IPhEnvironment:
    """
    Create a new phonological environment.

    Args:
        name: The name of the environment (e.g., "Word Initial", "Between Vowels")
        description: Optional description of when this environment applies

    Returns:
        IPhEnvironment: The newly created environment object

    Raises:
        InvalidParameterError: If name is empty
        DuplicateObjectError: If an environment with this name already exists

    Example:
        >>> # Create basic word boundary environments
        >>> word_initial = PhonEnvCreate("Word Initial", "At the beginning of a word")
        >>> PhonEnvSetStringRepresentation(word_initial, "#_")

        >>> word_final = PhonEnvCreate("Word Final", "At the end of a word")
        >>> PhonEnvSetStringRepresentation(word_final, "_#")

        >>> # Create vowel context environments
        >>> between_vowels = PhonEnvCreate("Between Vowels", "Intervocalic position")
        >>> PhonEnvSetStringRepresentation(between_vowels, "V_V")

        >>> after_nasal = PhonEnvCreate("After Nasal", "Following a nasal consonant")
        >>> PhonEnvSetStringRepresentation(after_nasal, "N_")

        >>> # Create syllable boundary environments
        >>> syll_initial = PhonEnvCreate("Syllable Initial")
        >>> PhonEnvSetStringRepresentation(syll_initial, "$._")

        >>> syll_final = PhonEnvCreate("Syllable Final")
        >>> PhonEnvSetStringRepresentation(syll_final, "_.$")

    Notes:
        - Name should be descriptive of the phonological context
        - Use PhonEnvSetStringRepresentation() to set the formal notation
        - Environments can reference natural classes (V, C, N, etc.)
        - Description is optional but helpful for documentation

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")

    raise NotImplementedYetError(
        "PhonEnvCreate requires FLEx API integration. "
        "Will create new IPhEnvironment in PhonologicalDataOA.EnvironmentsOS"
    )
    # FLEx integration:
    # from SIL.LCModel import IPhEnvironment, UndoableUnitOfWork
    # phon_data = project.PhonologicalDataOA
    # if not phon_data:
    #     raise OperationFailedError("No phonological data in project")
    #
    # with UndoableUnitOfWork(project, "Create Phonological Environment"):
    #     env = project.ServiceLocator.GetInstance(IPhEnvironmentFactory).Create()
    #     ws_handle = project.DefaultAnalysisWs
    #     env.Name.set_String(ws_handle, name)
    #     if description:
    #         env.Description.set_String(ws_handle, description)
    #     phon_data.EnvironmentsOS.Append(env)
    #     return env


def PhonEnvDelete(env_or_hvo: IPhEnvironment | HVO) -> None:
    """
    Delete a phonological environment.

    Args:
        env_or_hvo: The environment object or its HVO to delete

    Raises:
        ObjectNotFoundError: If the environment doesn't exist
        RuntimeError: If the environment is in use and cannot be deleted

    Example:
        >>> env = PhonEnvCreate("Obsolete Environment")
        >>> # ... realize it's not needed
        >>> PhonEnvDelete(env)

    Warning:
        - Deleting an environment that is in use will raise an error
        - This includes environments used in:
          - Phonological rules
          - Allomorph conditions
          - Other phonological specifications
        - Consider checking usage before deletion

    Notes:
        - Deletion is permanent and cannot be undone outside a transaction
        - Only the environment definition is deleted, not referenced items

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonEnvDelete requires FLEx API integration. "
        "Will remove environment from PhonologicalDataOA.EnvironmentsOS"
    )
    # FLEx integration:
    # env_obj = resolve_environment(env_or_hvo, project)
    # validate_object_exists(env_obj, f"Environment {env_or_hvo}")
    # phon_data = project.PhonologicalDataOA
    # with UndoableUnitOfWork(project, "Delete Phonological Environment"):
    #     phon_data.EnvironmentsOS.Remove(env_obj)


def PhonEnvGetName(
    env_or_hvo: IPhEnvironment | HVO,
    wsHandle: Optional[WritingSystemHandle] = None
) -> str:
    """
    Get the name of a phonological environment.

    Args:
        env_or_hvo: The environment object or its HVO
        wsHandle: Optional writing system (defaults to analysis WS)

    Returns:
        str: The environment name

    Raises:
        ObjectNotFoundError: If the environment doesn't exist

    Example:
        >>> for env in PhonEnvGetAll():
        ...     name = PhonEnvGetName(env)
        ...     print(name)
        Word Initial
        Word Final
        Between Vowels
        Before Consonant
        After Consonant

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonEnvGetName requires FLEx API integration. "
        "Will read env.Name.get_String(ws_handle)"
    )
    # FLEx integration:
    # env_obj = resolve_environment(env_or_hvo, project)
    # validate_object_exists(env_obj, f"Environment {env_or_hvo}")
    # if wsHandle is None:
    #     wsHandle = project.DefaultAnalysisWs
    # return env_obj.Name.get_String(wsHandle).Text


def PhonEnvSetName(
    env_or_hvo: IPhEnvironment | HVO,
    name: str,
    wsHandle: Optional[WritingSystemHandle] = None
) -> None:
    """
    Set the name of a phonological environment.

    Args:
        env_or_hvo: The environment object or its HVO
        name: The new name
        wsHandle: Optional writing system (defaults to analysis WS)

    Raises:
        InvalidParameterError: If name is empty
        ObjectNotFoundError: If the environment doesn't exist

    Example:
        >>> env = PhonEnvCreate("Intervocalic")
        >>> # Use more standard terminology
        >>> PhonEnvSetName(env, "Between Vowels")

    Notes:
        - Use clear, descriptive names
        - Standard terminology aids cross-linguistic comparison

    TODO: FLEx API integration required
    """
    validate_non_empty_string(name, "name")

    raise NotImplementedYetError(
        "PhonEnvSetName requires FLEx API integration. "
        "Will write to env.Name.set_String(ws_handle, name)"
    )
    # FLEx integration:
    # env_obj = resolve_environment(env_or_hvo, project)
    # validate_object_exists(env_obj, f"Environment {env_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Environment Name"):
    #     if wsHandle is None:
    #         wsHandle = project.DefaultAnalysisWs
    #     env_obj.Name.set_String(wsHandle, name)


def PhonEnvGetStringRepresentation(env_or_hvo: IPhEnvironment | HVO) -> str:
    """
    Get the string representation of a phonological environment.

    Args:
        env_or_hvo: The environment object or its HVO

    Returns:
        str: The environment's string representation (e.g., "V_V", "#_", "_#")

    Raises:
        ObjectNotFoundError: If the environment doesn't exist

    Example:
        >>> # Display all environments with their notation
        >>> for env in PhonEnvGetAll():
        ...     name = PhonEnvGetName(env)
        ...     repr = PhonEnvGetStringRepresentation(env)
        ...     print(f"{name:20} {repr}")
        Word Initial         #_
        Word Final           _#
        Between Vowels       V_V
        After Nasal          N_
        Before Stop          _P

        >>> # Use in rule description
        >>> env = PhonEnvCreate("Intervocalic")
        >>> PhonEnvSetStringRepresentation(env, "V_V")
        >>> repr = PhonEnvGetStringRepresentation(env)
        >>> print(f"Voicing occurs in environment: {repr}")
        Voicing occurs in environment: V_V

    Notes:
        - String representation uses formal phonological notation
        - Underscore (_) marks the position of the target segment
        - # marks word boundaries
        - $ marks syllable boundaries
        - Capital letters (V, C, N, etc.) reference natural classes
        - Multiple contexts can be specified with disjunction (|)

    Common Environment Notation:
        #_      - Word-initial (e.g., #_at → "at")
        _#      - Word-final (e.g., ca_# → "cat")
        V_V     - Between vowels (intervocalic)
        C_C     - Between consonants
        N_      - After nasal
        _P      - Before stop
        $._     - Syllable-initial
        _.$     - Syllable-final
        V_#     - After vowel, word-finally
        #_C     - Word-initially, before consonant

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonEnvGetStringRepresentation requires FLEx API integration. "
        "Will read env.StringRepresentation"
    )
    # FLEx integration:
    # env_obj = resolve_environment(env_or_hvo, project)
    # validate_object_exists(env_obj, f"Environment {env_or_hvo}")
    # return env_obj.StringRepresentation if hasattr(env_obj, 'StringRepresentation') else ""


def PhonEnvSetStringRepresentation(
    env_or_hvo: IPhEnvironment | HVO,
    repr: str
) -> None:
    """
    Set the string representation of a phonological environment.

    Args:
        env_or_hvo: The environment object or its HVO
        repr: The environment representation (e.g., "V_V", "#_", "_#")

    Raises:
        ObjectNotFoundError: If the environment doesn't exist

    Example:
        >>> # Create and define common environments
        >>> word_initial = PhonEnvCreate("Word Initial")
        >>> PhonEnvSetStringRepresentation(word_initial, "#_")

        >>> word_final = PhonEnvCreate("Word Final")
        >>> PhonEnvSetStringRepresentation(word_final, "_#")

        >>> between_vowels = PhonEnvCreate("Between Vowels")
        >>> PhonEnvSetStringRepresentation(between_vowels, "V_V")

        >>> # Complex environment: after nasal, before stop
        >>> env = PhonEnvCreate("Nasal-Stop Cluster")
        >>> PhonEnvSetStringRepresentation(env, "N_P")

        >>> # Environment with word boundary: stressed vowel word-finally
        >>> env = PhonEnvCreate("Stressed Final")
        >>> PhonEnvSetStringRepresentation(env, "ˈV_#")

        >>> # Disjunctive environment: word boundaries or between vowels
        >>> env = PhonEnvCreate("Boundaries or Intervocalic")
        >>> PhonEnvSetStringRepresentation(env, "#_|_#|V_V")

    Notes:
        - Use standard phonological environment notation
        - Underscore (_) marks the target position
        - Reference natural classes using their abbreviations
        - Can specify complex environments with multiple contexts
        - Empty string is allowed for unrestricted environment

    Notation Guide:
        _       - Target position (required)
        #       - Word boundary
        $       - Syllable boundary
        V       - Vowel (natural class)
        C       - Consonant (natural class)
        N       - Nasal (natural class)
        P       - Stop (natural class)
        |       - Disjunction (or)
        /p/     - Specific phoneme
        [p]     - Specific phone/allophone

    TODO: FLEx API integration required
    """
    raise NotImplementedYetError(
        "PhonEnvSetStringRepresentation requires FLEx API integration. "
        "Will write to env.StringRepresentation"
    )
    # FLEx integration:
    # env_obj = resolve_environment(env_or_hvo, project)
    # validate_object_exists(env_obj, f"Environment {env_or_hvo}")
    # with UndoableUnitOfWork(project, "Set Environment String Representation"):
    #     env_obj.StringRepresentation = repr


__all__ = [
    'PhonEnvGetAll',
    'PhonEnvCreate',
    'PhonEnvDelete',
    'PhonEnvGetName',
    'PhonEnvSetName',
    'PhonEnvGetStringRepresentation',
    'PhonEnvSetStringRepresentation',
]
