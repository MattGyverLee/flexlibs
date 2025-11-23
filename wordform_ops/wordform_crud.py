"""
Wordform CRUD Operations (Cluster 1.6)

This module provides comprehensive CRUD (Create, Read, Update, Delete) operations
for wordforms in FLEx (FieldWorks Language Explorer) projects.

Wordforms represent surface forms of words as they appear in texts, and are the
foundation for linguistic analysis in FLEx. Each wordform can have multiple
analyses and a spelling status.

Classes:
    SpellingStatusStates: Enum for wordform spelling status values

Functions:
    wordform_get_all: Retrieve all wordforms in the project
    wordform_create: Create a new wordform
    wordform_delete: Delete a wordform
    wordform_exists: Check if a wordform exists
    wordform_find: Find a specific wordform
    wordform_get_form: Get the text form of a wordform
    wordform_set_form: Set the text form of a wordform
    wordform_get_spelling_status: Get the spelling status of a wordform
    wordform_set_spelling_status: Set the spelling status of a wordform
    wordform_get_analyses: Get all analyses for a wordform
"""

from typing import Generator, List, Optional, Union

from ..core import (
    IWfiWordform,
    IWfiAnalysis,
    WritingSystemHandle,
    SpellingStatusStates,
    resolve_wordform,
    validate_non_empty_string,
    validate_object_exists,
    validate_enum_value,
    NotImplementedYetError,
)


def wordform_get_all() -> Generator:
    """
    Retrieve all wordforms in the FLEx project.

    This function generates all IWfiWordform objects in the project database,
    allowing iteration over the complete wordform inventory.

    Yields:
        IWfiWordform: Each wordform object in the project

    Example:
        >>> for wordform in wordform_get_all():
        ...     print(wordform_get_form(wordform))

    Notes:
        - Returns a generator for memory efficiency with large projects
        - Wordforms are returned in database order (not alphabetical)
        - Use wordform_get_form() to access the surface text

    See Also:
        wordform_get_all_with_status: Get wordforms filtered by spelling status
        wordform_get_all_unapproved: Get only unapproved wordforms
    """
    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # for wordform in project.LangProject.WordformInventory.ReallyReallyAllPossibilities:
    #     yield wordform
    raise NotImplementedYetError()


def wordform_create(form: str, ws_handle: WritingSystemHandle) -> object:
    """
    Create a new wordform in the FLEx project.

    Args:
        form: The surface text form of the wordform
        ws_handle: Writing system handle (language tag like 'en' or ID)

    Returns:
        IWfiWordform: The newly created wordform object

    Raises:
        ValueError: If form is empty or ws_handle is invalid
        RuntimeError: If wordform already exists (use wordform_find instead)

    Example:
        >>> wf = wordform_create("running", "en")
        >>> print(wordform_get_form(wf))
        running

    Notes:
        - Check existence with wordform_exists() before creating
        - New wordforms have UNDECIDED spelling status by default
        - The form is stored in the specified writing system

    See Also:
        wordform_exists: Check if a wordform already exists
        wordform_find: Find an existing wordform
    """
    validate_non_empty_string(form, "wordform text")

    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # factory = project.Cache.ServiceLocator.GetInstance[IWfiWordformFactory]
    # ws = project.Cache.WritingSystemFactory.get_Engine(ws_handle)
    # wordform = factory.Create()
    # wordform.Form.set_String(ws.Handle, form)
    # return wordform
    raise NotImplementedYetError()


def wordform_delete(wordform_or_hvo: Union[object, int]) -> None:
    """
    Delete a wordform from the FLEx project.

    Args:
        wordform_or_hvo: Either an IWfiWordform object or its HVO (database ID)

    Raises:
        ValueError: If wordform doesn't exist
        RuntimeError: If wordform is in use and cannot be deleted

    Example:
        >>> wf = wordform_find("obsolete", "en")
        >>> wordform_delete(wf)

    Warning:
        - This is a destructive operation and cannot be undone
        - All analyses associated with the wordform will also be deleted
        - Wordforms used in texts cannot be deleted
        - Consider setting spelling status to INCORRECT instead

    See Also:
        wordform_set_spelling_status: Mark wordform as incorrect instead
    """
    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # if isinstance(wordform_or_hvo, int):
    #     wordform = project.Cache.ServiceLocator.GetObject(wordform_or_hvo)
    # else:
    #     wordform = wordform_or_hvo
    # if wordform.OccurrenceCount > 0:
    #     raise RuntimeError("Cannot delete wordform that appears in texts")
    # wordform.Delete()
    raise NotImplementedYetError()


def wordform_exists(form: str, ws_handle: WritingSystemHandle) -> bool:
    """
    Check if a wordform exists in the FLEx project.

    Args:
        form: The surface text form to check
        ws_handle: Writing system handle (language tag or ID)

    Returns:
        bool: True if the wordform exists, False otherwise

    Example:
        >>> if wordform_exists("running", "en"):
        ...     wf = wordform_find("running", "en")
        ... else:
        ...     wf = wordform_create("running", "en")

    Notes:
        - Search is case-sensitive
        - Search is writing-system specific
        - Returns False for empty or whitespace-only forms

    See Also:
        wordform_find: Get the existing wordform object
        wordform_create: Create a new wordform
    """
    if not form or not form.strip():
        return False

    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # ws = project.Cache.WritingSystemFactory.get_Engine(ws_handle)
    # for wf in project.LangProject.WordformInventory.ReallyReallyAllPossibilities:
    #     if wf.Form.get_String(ws.Handle).Text == form:
    #         return True
    # return False
    raise NotImplementedYetError()


def wordform_find(form: str, ws_handle: WritingSystemHandle) -> Optional[object]:
    """
    Find and return a wordform by its surface form.

    Args:
        form: The surface text form to find
        ws_handle: Writing system handle (language tag or ID)

    Returns:
        IWfiWordform or None: The wordform object if found, None otherwise

    Example:
        >>> wf = wordform_find("running", "en")
        >>> if wf:
        ...     status = wordform_get_spelling_status(wf)
        ...     print(f"Spelling status: {status}")

    Notes:
        - Search is case-sensitive
        - Search is writing-system specific
        - Returns None if wordform doesn't exist
        - Use wordform_exists() for simple existence check

    See Also:
        wordform_exists: Check existence without retrieving object
        wordform_get_all: Retrieve all wordforms
    """
    if not form or not form.strip():
        return None

    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # ws = project.Cache.WritingSystemFactory.get_Engine(ws_handle)
    # for wf in project.LangProject.WordformInventory.ReallyReallyAllPossibilities:
    #     if wf.Form.get_String(ws.Handle).Text == form:
    #         return wf
    # return None
    raise NotImplementedYetError()


def wordform_get_form(wordform_or_hvo: Union[object, int],
                      ws_handle: Optional[Union[str, int]] = None) -> str:
    """
    Get the surface text form of a wordform.

    Args:
        wordform_or_hvo: Either an IWfiWordform object or its HVO
        ws_handle: Writing system handle (uses default vernacular if None)

    Returns:
        str: The text form of the wordform

    Raises:
        ValueError: If wordform doesn't exist

    Example:
        >>> for wf in wordform_get_all():
        ...     form = wordform_get_form(wf, "en")
        ...     print(form)

    Notes:
        - Returns empty string if form not set in specified writing system
        - Default writing system is the default vernacular WS
        - Multi-string forms may exist in multiple writing systems

    See Also:
        wordform_set_form: Set the text form
        wordform_find: Find wordform by its form
    """
    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # if isinstance(wordform_or_hvo, int):
    #     wordform = project.Cache.ServiceLocator.GetObject(wordform_or_hvo)
    # else:
    #     wordform = wordform_or_hvo
    #
    # if ws_handle is None:
    #     ws_handle = project.Cache.DefaultVernWs
    # ws = project.Cache.WritingSystemFactory.get_Engine(ws_handle)
    # return wordform.Form.get_String(ws.Handle).Text or ""
    raise NotImplementedYetError()


def wordform_set_form(wordform_or_hvo: Union[object, int],
                      form: str,
                      ws_handle: WritingSystemHandle) -> None:
    """
    Set the surface text form of a wordform.

    Args:
        wordform_or_hvo: Either an IWfiWordform object or its HVO
        form: The new text form to set
        ws_handle: Writing system handle (language tag or ID)

    Raises:
        ValueError: If form is empty or wordform doesn't exist
        RuntimeError: If another wordform already has this form

    Example:
        >>> wf = wordform_find("runing", "en")  # misspelled
        >>> wordform_set_form(wf, "running", "en")  # correct it

    Warning:
        - Changing a wordform's text may affect text parsing
        - Creates duplicate if another wordform has same form
        - Use carefully - consider creating new wordform instead

    See Also:
        wordform_get_form: Get the current form
        wordform_create: Create a new wordform
    """
    validate_non_empty_string(form, "wordform text")

    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # if isinstance(wordform_or_hvo, int):
    #     wordform = project.Cache.ServiceLocator.GetObject(wordform_or_hvo)
    # else:
    #     wordform = wordform_or_hvo
    #
    # ws = project.Cache.WritingSystemFactory.get_Engine(ws_handle)
    # wordform.Form.set_String(ws.Handle, form)
    raise NotImplementedYetError()


def wordform_get_spelling_status(wordform_or_hvo: Union[object, int]) -> SpellingStatusStates:
    """
    Get the spelling status of a wordform.

    Args:
        wordform_or_hvo: Either an IWfiWordform object or its HVO

    Returns:
        SpellingStatusStates: The current spelling status

    Raises:
        ValueError: If wordform doesn't exist

    Example:
        >>> wf = wordform_find("running", "en")
        >>> status = wordform_get_spelling_status(wf)
        >>> if status == SpellingStatusStates.UNDECIDED:
        ...     wordform_approve_spelling(wf)

    Notes:
        - New wordforms default to UNDECIDED status
        - Status affects spell-checking and analysis suggestions
        - CORRECT status indicates approved wordforms

    See Also:
        wordform_set_spelling_status: Set the spelling status
        wordform_approve_spelling: Set status to CORRECT
        wordform_get_all_with_status: Filter wordforms by status
    """
    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # if isinstance(wordform_or_hvo, int):
    #     wordform = project.Cache.ServiceLocator.GetObject(wordform_or_hvo)
    # else:
    #     wordform = wordform_or_hvo
    # return SpellingStatusStates(wordform.SpellingStatus)
    raise NotImplementedYetError()


def wordform_set_spelling_status(wordform_or_hvo: Union[object, int],
                                  status: SpellingStatusStates) -> None:
    """
    Set the spelling status of a wordform.

    Args:
        wordform_or_hvo: Either an IWfiWordform object or its HVO
        status: The new spelling status (from SpellingStatusStates enum)

    Raises:
        ValueError: If wordform doesn't exist or status is invalid

    Example:
        >>> wf = wordform_find("colour", "en-GB")
        >>> wordform_set_spelling_status(wf, SpellingStatusStates.CORRECT)
        >>>
        >>> typo = wordform_find("teh", "en")
        >>> wordform_set_spelling_status(typo, SpellingStatusStates.INCORRECT)

    Notes:
        - Use SpellingStatusStates enum for status values
        - CORRECT: Approved spelling
        - INCORRECT: Known misspelling
        - UNDECIDED: Not yet reviewed

    See Also:
        wordform_get_spelling_status: Get the current status
        wordform_approve_spelling: Shortcut to set status to CORRECT
    """
    validate_enum_value(status, SpellingStatusStates, "status")

    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # if isinstance(wordform_or_hvo, int):
    #     wordform = project.Cache.ServiceLocator.GetObject(wordform_or_hvo)
    # else:
    #     wordform = wordform_or_hvo
    # wordform.SpellingStatus = int(status)
    raise NotImplementedYetError()


def wordform_get_analyses(wordform_or_hvo: Union[object, int]) -> List:
    """
    Get all analyses associated with a wordform.

    Args:
        wordform_or_hvo: Either an IWfiWordform object or its HVO

    Returns:
        List[IWfiAnalysis]: List of analysis objects for this wordform

    Raises:
        ValueError: If wordform doesn't exist

    Example:
        >>> wf = wordform_find("running", "en")
        >>> analyses = wordform_get_analyses(wf)
        >>> for analysis in analyses:
        ...     gloss = analysis_get_gloss(analysis, "en")
        ...     print(f"Analysis: {gloss}")

    Notes:
        - Returns empty list if wordform has no analyses
        - Analyses may be human-created or parser-generated
        - Use analysis_is_approved() to filter for approved analyses

    See Also:
        analysis_create: Create a new analysis for a wordform
        analysis_get_all: Get analyses across all wordforms
        wordform_get_occurrence_count: Get number of text occurrences
    """
    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # if isinstance(wordform_or_hvo, int):
    #     wordform = project.Cache.ServiceLocator.GetObject(wordform_or_hvo)
    # else:
    #     wordform = wordform_or_hvo
    # return list(wordform.AnalysesOC)
    raise NotImplementedYetError()
