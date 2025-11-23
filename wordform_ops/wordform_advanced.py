"""
Wordform Advanced Operations (Cluster 1.7)

This module provides advanced operations for working with wordforms in FLEx
(FieldWorks Language Explorer) projects.

These operations extend the basic CRUD functionality with features for:
- Counting and retrieving wordform occurrences in texts
- Computing wordform checksums for data integrity
- Filtering wordforms by spelling status
- Batch operations on wordforms
- Workflow automation (e.g., approving spellings)

Functions:
    wordform_get_occurrence_count: Count text occurrences of a wordform
    wordform_get_occurrences: Get all segment occurrences of a wordform
    wordform_get_checksum: Get the checksum for a wordform
    wordform_get_all_with_status: Get wordforms filtered by spelling status
    wordform_get_all_unapproved: Get all unapproved wordforms
    wordform_approve_spelling: Approve a wordform's spelling
"""

from typing import Generator, List, Union

from ..core import (
    IWfiWordform,
    ISegment,
    SpellingStatusStates,
    resolve_wordform,
    validate_enum_value,
    NotImplementedYetError,
)



def wordform_get_occurrence_count(wordform_or_hvo: Union[object, int]) -> int:
    """
    Get the number of times a wordform appears in texts.

    Args:
        wordform_or_hvo: Either an IWfiWordform object or its HVO

    Returns:
        int: The number of occurrences in all texts

    Raises:
        ValueError: If wordform doesn't exist

    Example:
        >>> wf = wordform_find("the", "en")
        >>> count = wordform_get_occurrence_count(wf)
        >>> print(f"'the' appears {count} times")
        'the' appears 1523 times

    Notes:
        - Count includes occurrences in all texts, whether parsed or not
        - Useful for frequency analysis and corpus statistics
        - Count is typically cached by FLEx for performance
        - Returns 0 for wordforms not found in any text

    Performance:
        - This is a fast operation (O(1)) as counts are cached
        - Safe to call repeatedly without performance concerns

    See Also:
        wordform_get_occurrences: Get the actual segment occurrences
        segment_get_all: Iterate over all segments
    """
    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # if isinstance(wordform_or_hvo, int):
    #     wordform = project.Cache.ServiceLocator.GetObject(wordform_or_hvo)
    # else:
    #     wordform = wordform_or_hvo
    # return wordform.OccurrenceCount
    raise NotImplementedYetError()


def wordform_get_occurrences(wordform_or_hvo: Union[object, int]) -> List:
    """
    Get all segment occurrences where this wordform appears.

    Args:
        wordform_or_hvo: Either an IWfiWordform object or its HVO

    Returns:
        List[ISegment]: List of segments containing this wordform

    Raises:
        ValueError: If wordform doesn't exist

    Example:
        >>> wf = wordform_find("important", "en")
        >>> segments = wordform_get_occurrences(wf)
        >>> for segment in segments:
        ...     baseline = segment_get_baseline_text(segment)
        ...     print(f"Context: {baseline}")

    Notes:
        - Returns segments in text order (by reference)
        - Each segment represents one occurrence of the wordform
        - Useful for concordance views and KWIC displays
        - May be memory-intensive for high-frequency wordforms

    Performance:
        - O(n) where n is the occurrence count
        - Consider using wordform_get_occurrence_count() first
        - For very frequent words, process incrementally

    See Also:
        wordform_get_occurrence_count: Get just the count
        segment_get_baseline_text: Get the text of a segment
        segment_get_analyses: Get analyses for each occurrence
    """
    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # if isinstance(wordform_or_hvo, int):
    #     wordform = project.Cache.ServiceLocator.GetObject(wordform_or_hvo)
    # else:
    #     wordform = wordform_or_hvo
    #
    # occurrences = []
    # for segment in project.LangProject.AllSegments():
    #     for analysis in segment.AnalysesRS:
    #         if hasattr(analysis, 'Wordform') and analysis.Wordform == wordform:
    #             occurrences.append(segment)
    #             break
    # return occurrences
    raise NotImplementedYetError()


def wordform_get_checksum(wordform_or_hvo: Union[object, int]) -> int:
    """
    Get the checksum value for a wordform.

    The checksum is used internally by FLEx for data integrity verification
    and change detection.

    Args:
        wordform_or_hvo: Either an IWfiWordform object or its HVO

    Returns:
        int: The checksum value

    Raises:
        ValueError: If wordform doesn't exist

    Example:
        >>> wf = wordform_find("data", "en")
        >>> checksum = wordform_get_checksum(wf)
        >>> print(f"Checksum: {checksum}")
        Checksum: 1234567890

    Notes:
        - Checksum changes when wordform data is modified
        - Used for detecting changes between sessions
        - Implementation-specific value (not standardized)
        - Useful for synchronization and caching

    Technical:
        - Checksum is computed over wordform properties
        - May include form, analyses, spelling status, etc.
        - Algorithm is FLEx version-specific

    See Also:
        wordform_set_form: Modifying form changes checksum
        wordform_set_spelling_status: May affect checksum
    """
    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # if isinstance(wordform_or_hvo, int):
    #     wordform = project.Cache.ServiceLocator.GetObject(wordform_or_hvo)
    # else:
    #     wordform = wordform_or_hvo
    # return wordform.Checksum
    raise NotImplementedYetError()


def wordform_get_all_with_status(status: SpellingStatusStates) -> Generator:
    """
    Get all wordforms with a specific spelling status.

    Args:
        status: The spelling status to filter by (from SpellingStatusStates)

    Yields:
        IWfiWordform: Each wordform matching the specified status

    Raises:
        ValueError: If status is not a valid SpellingStatusStates value

    Example:
        >>> # Get all incorrect spellings
        >>> for wf in wordform_get_all_with_status(SpellingStatusStates.INCORRECT):
        ...     form = wordform_get_form(wf)
        ...     print(f"Misspelling: {form}")
        >>>
        >>> # Count undecided wordforms
        >>> undecided = list(wordform_get_all_with_status(SpellingStatusStates.UNDECIDED))
        >>> print(f"{len(undecided)} wordforms need review")

    Notes:
        - Returns a generator for memory efficiency
        - Useful for spell-checking workflows
        - Results are not sorted (database order)

    Use Cases:
        - Quality control: Review UNDECIDED wordforms
        - Cleanup: Process INCORRECT wordforms
        - Validation: Verify CORRECT wordforms

    See Also:
        wordform_get_all_unapproved: Shortcut for non-CORRECT wordforms
        wordform_set_spelling_status: Change a wordform's status
        wordform_approve_spelling: Mark wordform as CORRECT
    """
    validate_enum_value(status, SpellingStatusStates, "status")

    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # for wordform in project.LangProject.WordformInventory.ReallyReallyAllPossibilities:
    #     if SpellingStatusStates(wordform.SpellingStatus) == status:
    #         yield wordform
    raise NotImplementedYetError()


def wordform_get_all_unapproved() -> Generator:
    """
    Get all wordforms that have not been approved (spelling status != CORRECT).

    This is a convenience function that returns wordforms with UNDECIDED or
    INCORRECT spelling status.

    Yields:
        IWfiWordform: Each unapproved wordform

    Example:
        >>> # Review all unapproved wordforms
        >>> for wf in wordform_get_all_unapproved():
        ...     form = wordform_get_form(wf)
        ...     status = wordform_get_spelling_status(wf)
        ...     print(f"{form}: {status.name}")
        ...     # Manual review process here
        ...     if should_approve(form):
        ...         wordform_approve_spelling(wf)

    Notes:
        - Returns generator for memory efficiency
        - Includes both UNDECIDED and INCORRECT wordforms
        - Does not include CORRECT wordforms
        - Useful for batch review workflows

    Use Cases:
        - Spell-checking review queue
        - Data quality assessment
        - Pre-publication verification
        - Lexicon development workflow

    Performance:
        - Must check all wordforms in database
        - May be slow on large projects
        - Consider processing in batches

    See Also:
        wordform_get_all_with_status: Filter by specific status
        wordform_approve_spelling: Approve a wordform
        wordform_set_spelling_status: Set custom status
    """
    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # project = FlexProject.current
    # for wordform in project.LangProject.WordformInventory.ReallyReallyAllPossibilities:
    #     if SpellingStatusStates(wordform.SpellingStatus) != SpellingStatusStates.CORRECT:
    #         yield wordform
    raise NotImplementedYetError()


def wordform_approve_spelling(wordform_or_hvo: Union[object, int]) -> None:
    """
    Approve the spelling of a wordform by setting its status to CORRECT.

    This is a convenience function equivalent to:
    wordform_set_spelling_status(wordform, SpellingStatusStates.CORRECT)

    Args:
        wordform_or_hvo: Either an IWfiWordform object or its HVO

    Raises:
        ValueError: If wordform doesn't exist

    Example:
        >>> # Approve a single wordform
        >>> wf = wordform_find("colour", "en-GB")
        >>> wordform_approve_spelling(wf)
        >>>
        >>> # Batch approve all analyses with frequency > 10
        >>> for wf in wordform_get_all_unapproved():
        ...     if wordform_get_occurrence_count(wf) > 10:
        ...         wordform_approve_spelling(wf)

    Notes:
        - Sets spelling status to SpellingStatusStates.CORRECT
        - Marks wordform as validated and acceptable
        - Affects spell-checker behavior in FLEx
        - Irreversible through this function (use set_spelling_status to undo)

    Workflow:
        1. Review unapproved wordforms
        2. Verify spelling is correct
        3. Call this function to approve
        4. Wordform no longer appears in review queues

    See Also:
        wordform_set_spelling_status: Set any status value
        wordform_get_spelling_status: Check current status
        wordform_get_all_unapproved: Get wordforms needing review
    """
    # TODO: Implement FLEx API integration
    # from flexlibs import FlexProject
    # from .wordform_crud import wordform_set_spelling_status
    # wordform_set_spelling_status(wordform_or_hvo, SpellingStatusStates.CORRECT)
    raise NotImplementedYetError()
