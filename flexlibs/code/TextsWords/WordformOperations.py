#
#   WordformOperations.py
#
#   Class: WordformOperations
#          Wordform operations for FieldWorks Language Explorer projects
#          via SIL Language and Culture Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright Craig Farrow, 2008 - 2024
#

import logging
logger = logging.getLogger(__name__)

import clr
clr.AddReference("System")

from SIL.LCModel import (
    IWfiWordformRepository,
    IWfiWordformFactory,
    IWfiWordform,
)

from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


# --- Spelling Status Enum ---

class SpellingStatusStates:
    """Spelling status values for wordforms."""
    UNDECIDED = 0
    INCORRECT = 1
    CORRECT = 2


# --- WordformOperations Class ---

class WordformOperations:
    """
    Provides operations for managing wordforms in a FLEx project.

    Wordforms represent surface forms of words as they appear in texts.
    Each wordform can have multiple analyses and a spelling status.

    This class should be accessed via FLExProject.Wordforms property.

    Example:
        >>> project = FLExProject()
        >>> project.OpenProject("MyProject")
        >>> # Get all wordforms
        >>> for wf in project.Wordforms.GetAll():
        ...     print(project.Wordforms.GetForm(wf))
        >>> # Create a new wordform
        >>> wf = project.Wordforms.Create("running")
        >>> # Set spelling status
        >>> project.Wordforms.SetSpellingStatus(wf, SpellingStatusStates.CORRECT)
    """

    def __init__(self, project):
        """
        Initialize WordformOperations.

        Args:
            project: FLExProject instance
        """
        self.project = project

    def __WSHandle(self, wsHandle):
        """
        Internal helper to resolve writing system handle.

        Args:
            wsHandle: Writing system handle (language tag or ID), or None for default

        Returns:
            int: Resolved writing system handle
        """
        if wsHandle is None:
            return self.project.project.DefaultVernWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultVernWs)

    def GetAll(self):
        """
        Retrieve all wordforms in the FLEx project.

        This method returns an iterator over all IWfiWordform objects in the
        project database, allowing iteration over the complete wordform inventory.

        Yields:
            IWfiWordform: Each wordform object in the project

        Example:
            >>> for wordform in project.Wordforms.GetAll():
            ...     form = project.Wordforms.GetForm(wordform)
            ...     print(form)

        Notes:
            - Returns an iterator for memory efficiency with large projects
            - Wordforms are returned in database order (not alphabetical)
            - Use GetForm() to access the surface text

        See Also:
            Find, Create, GetForm
        """
        return self.project.ObjectsIn(IWfiWordformRepository)

    def Create(self, form, wsHandle=None):
        """
        Create a new wordform in the FLEx project.

        Args:
            form: The surface text form of the wordform
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            IWfiWordform: The newly created wordform object

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If form is empty or None

        Example:
            >>> wf = project.Wordforms.Create("running")
            >>> print(project.Wordforms.GetForm(wf))
            running
            >>> # Create in specific writing system
            >>> wf_fr = project.Wordforms.Create("courir", "fr")

        Notes:
            - New wordforms have UNDECIDED spelling status by default
            - The form is stored in the specified writing system
            - Does not check if wordform already exists - use Find() or Exists() first

        See Also:
            Exists, Find, Delete
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not form or not form.strip():
            raise FP_NullParameterError()

        wsHandle = self.__WSHandle(wsHandle)

        # Get the factory and create the wordform
        factory = self.project.project.ServiceLocator.GetService(IWfiWordformFactory)
        new_wf = factory.Create()

        # Add to wordform inventory (must be done before setting properties)
        wordform_inventory = self.project.lp.WordformInventoryOA
        wordform_inventory.WordformsOC.Add(new_wf)

        # Set the form
        mkstr = TsStringUtils.MakeString(form, wsHandle)
        new_wf.Form.set_String(wsHandle, mkstr)

        return new_wf

    def Delete(self, wordform_or_hvo):
        """
        Delete a wordform from the FLEx project.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO (database ID)

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_ParameterError: If wordform doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("obsolete")
            >>> if wf:
            ...     project.Wordforms.Delete(wf)

        Warning:
            - This is a destructive operation
            - All analyses associated with the wordform will also be deleted
            - Consider setting spelling status to INCORRECT instead of deleting

        See Also:
            Create, SetSpellingStatus
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        # Resolve to wordform object
        if isinstance(wordform_or_hvo, int):
            wordform = self.project.Object(wordform_or_hvo)
            if not isinstance(wordform, IWfiWordform):
                raise FP_ParameterError("HVO does not refer to a wordform")
        else:
            wordform = wordform_or_hvo

        # Remove from wordform inventory
        wordform_inventory = self.project.lp.WordformInventoryOA
        wordform_inventory.WordformsOC.Remove(wordform)

    def Exists(self, form, wsHandle=None):
        """
        Check if a wordform exists in the FLEx project.

        Args:
            form: The surface text form to check
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            bool: True if the wordform exists, False otherwise

        Example:
            >>> if project.Wordforms.Exists("running"):
            ...     wf = project.Wordforms.Find("running")
            ... else:
            ...     wf = project.Wordforms.Create("running")

        Notes:
            - Search is case-sensitive
            - Search is writing-system specific
            - Returns False for empty or whitespace-only forms

        See Also:
            Find, Create
        """
        if not form or not form.strip():
            return False

        return self.Find(form, wsHandle) is not None

    def Find(self, form, wsHandle=None):
        """
        Find and return a wordform by its surface form.

        Args:
            form: The surface text form to find
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            IWfiWordform or None: The wordform object if found, None otherwise

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> if wf:
            ...     status = project.Wordforms.GetSpellingStatus(wf)
            ...     print(f"Spelling status: {status}")

        Notes:
            - Search is case-sensitive
            - Search is writing-system specific
            - Returns None if wordform doesn't exist
            - Use Exists() for simple existence check

        See Also:
            Exists, GetAll, Create
        """
        if not form or not form.strip():
            return None

        wsHandle = self.__WSHandle(wsHandle)

        # Search through all wordforms
        for wf in self.GetAll():
            wf_form = ITsString(wf.Form.get_String(wsHandle)).Text
            if wf_form == form:
                return wf

        return None

    def GetForm(self, wordform_or_hvo, wsHandle=None):
        """
        Get the surface text form of a wordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            str: The text form of the wordform (empty string if not set)

        Raises:
            FP_ParameterError: If wordform doesn't exist

        Example:
            >>> for wf in project.Wordforms.GetAll():
            ...     form = project.Wordforms.GetForm(wf)
            ...     print(form)

        Notes:
            - Returns empty string if form not set in specified writing system
            - Default writing system is the default vernacular WS
            - Multi-string forms may exist in multiple writing systems

        See Also:
            SetForm, Find
        """
        # Resolve to wordform object
        if isinstance(wordform_or_hvo, int):
            wordform = self.project.Object(wordform_or_hvo)
            if not isinstance(wordform, IWfiWordform):
                raise FP_ParameterError("HVO does not refer to a wordform")
        else:
            wordform = wordform_or_hvo

        wsHandle = self.__WSHandle(wsHandle)

        # Get the form string
        form = ITsString(wordform.Form.get_String(wsHandle)).Text
        return form or ""

    def SetForm(self, wordform_or_hvo, form, wsHandle=None):
        """
        Set the surface text form of a wordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO
            form: The new text form to set
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If form is empty or None
            FP_ParameterError: If wordform doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("runing")  # misspelled
            >>> if wf:
            ...     project.Wordforms.SetForm(wf, "running")  # correct it

        Warning:
            - Changing a wordform's text may affect text parsing
            - May create duplicate if another wordform has same form
            - Use carefully - consider creating new wordform instead

        See Also:
            GetForm, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not form or not form.strip():
            raise FP_NullParameterError()

        # Resolve to wordform object
        if isinstance(wordform_or_hvo, int):
            wordform = self.project.Object(wordform_or_hvo)
            if not isinstance(wordform, IWfiWordform):
                raise FP_ParameterError("HVO does not refer to a wordform")
        else:
            wordform = wordform_or_hvo

        wsHandle = self.__WSHandle(wsHandle)

        # Set the form string
        mkstr = TsStringUtils.MakeString(form, wsHandle)
        wordform.Form.set_String(wsHandle, mkstr)

    def GetSpellingStatus(self, wordform_or_hvo):
        """
        Get the spelling status of a wordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Returns:
            int: The current spelling status (0=UNDECIDED, 1=INCORRECT, 2=CORRECT)

        Raises:
            FP_ParameterError: If wordform doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> status = project.Wordforms.GetSpellingStatus(wf)
            >>> if status == SpellingStatusStates.UNDECIDED:
            ...     project.Wordforms.SetSpellingStatus(wf, SpellingStatusStates.CORRECT)

        Notes:
            - New wordforms default to UNDECIDED status (0)
            - Status affects spell-checking and analysis suggestions
            - CORRECT status (2) indicates approved wordforms
            - INCORRECT status (1) marks known misspellings

        See Also:
            SetSpellingStatus, SpellingStatusStates
        """
        # Resolve to wordform object
        if isinstance(wordform_or_hvo, int):
            wordform = self.project.Object(wordform_or_hvo)
            if not isinstance(wordform, IWfiWordform):
                raise FP_ParameterError("HVO does not refer to a wordform")
        else:
            wordform = wordform_or_hvo

        return wordform.SpellingStatus

    def SetSpellingStatus(self, wordform_or_hvo, status):
        """
        Set the spelling status of a wordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO
            status: The new spelling status (0, 1, or 2 from SpellingStatusStates)

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_ParameterError: If wordform doesn't exist or status is invalid

        Example:
            >>> wf = project.Wordforms.Find("colour")
            >>> project.Wordforms.SetSpellingStatus(wf, SpellingStatusStates.CORRECT)
            >>>
            >>> typo = project.Wordforms.Find("teh")
            >>> project.Wordforms.SetSpellingStatus(typo, SpellingStatusStates.INCORRECT)

        Notes:
            - Use SpellingStatusStates enum for status values:
              - UNDECIDED (0): Not yet reviewed
              - INCORRECT (1): Known misspelling
              - CORRECT (2): Approved spelling

        See Also:
            GetSpellingStatus, SpellingStatusStates
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if status not in (SpellingStatusStates.UNDECIDED,
                         SpellingStatusStates.INCORRECT,
                         SpellingStatusStates.CORRECT):
            raise FP_ParameterError(f"Invalid spelling status: {status}. Must be 0, 1, or 2.")

        # Resolve to wordform object
        if isinstance(wordform_or_hvo, int):
            wordform = self.project.Object(wordform_or_hvo)
            if not isinstance(wordform, IWfiWordform):
                raise FP_ParameterError("HVO does not refer to a wordform")
        else:
            wordform = wordform_or_hvo

        wordform.SpellingStatus = status

    def GetAnalyses(self, wordform_or_hvo):
        """
        Get all analyses associated with a wordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Returns:
            list: List of IWfiAnalysis objects for this wordform

        Raises:
            FP_ParameterError: If wordform doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> for analysis in analyses:
            ...     # Process each analysis
            ...     print(f"Analysis HVO: {analysis.Hvo}")

        Notes:
            - Returns empty list if wordform has no analyses
            - Analyses may be human-created or parser-generated
            - Each analysis represents a possible linguistic interpretation

        See Also:
            GetAll, Find
        """
        # Resolve to wordform object
        if isinstance(wordform_or_hvo, int):
            wordform = self.project.Object(wordform_or_hvo)
            if not isinstance(wordform, IWfiWordform):
                raise FP_ParameterError("HVO does not refer to a wordform")
        else:
            wordform = wordform_or_hvo

        return list(wordform.AnalysesOC)

    def GetOccurrenceCount(self, wordform_or_hvo):
        """
        Get the count of occurrences of a wordform in texts.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Returns:
            int: Number of times this wordform appears in project texts

        Raises:
            FP_ParameterError: If wordform doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> count = project.Wordforms.GetOccurrenceCount(wf)
            >>> print(f"'running' appears {count} times in texts")

        Notes:
            - Counts segment occurrences across all texts in the project
            - Returns 0 if wordform has no occurrences
            - Each occurrence represents a token in a text segment

        See Also:
            GetOccurrences, GetAll
        """
        # Resolve to wordform object
        if isinstance(wordform_or_hvo, int):
            wordform = self.project.Object(wordform_or_hvo)
            if not isinstance(wordform, IWfiWordform):
                raise FP_ParameterError("HVO does not refer to a wordform")
        else:
            wordform = wordform_or_hvo

        return wordform.OccurrencesRS.Count

    def GetOccurrences(self, wordform_or_hvo):
        """
        Get all segment occurrences of a wordform in texts.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Returns:
            list: List of segment objects where this wordform appears

        Raises:
            FP_ParameterError: If wordform doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> occurrences = project.Wordforms.GetOccurrences(wf)
            >>> for segment in occurrences:
            ...     # Process each text segment containing this wordform
            ...     print(f"Segment HVO: {segment.Hvo}")

        Notes:
            - Returns empty list if wordform has no occurrences
            - Each segment represents a location where the wordform appears
            - Segments belong to texts (paragraphs/sentences)

        See Also:
            GetOccurrenceCount, GetAll
        """
        # Resolve to wordform object
        if isinstance(wordform_or_hvo, int):
            wordform = self.project.Object(wordform_or_hvo)
            if not isinstance(wordform, IWfiWordform):
                raise FP_ParameterError("HVO does not refer to a wordform")
        else:
            wordform = wordform_or_hvo

        return list(wordform.OccurrencesRS)

    def GetChecksum(self, wordform_or_hvo):
        """
        Get the checksum of a wordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Returns:
            int: The wordform's checksum value

        Raises:
            FP_ParameterError: If wordform doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> checksum = project.Wordforms.GetChecksum(wf)
            >>> print(f"Checksum: {checksum}")

        Notes:
            - Checksum is used for data integrity and change detection
            - The checksum value changes when wordform properties are modified
            - Useful for tracking modifications and synchronization

        See Also:
            GetForm, GetSpellingStatus
        """
        # Resolve to wordform object
        if isinstance(wordform_or_hvo, int):
            wordform = self.project.Object(wordform_or_hvo)
            if not isinstance(wordform, IWfiWordform):
                raise FP_ParameterError("HVO does not refer to a wordform")
        else:
            wordform = wordform_or_hvo

        return wordform.Checksum

    def GetAllWithStatus(self, status):
        """
        Retrieve all wordforms with a specific spelling status.

        Args:
            status: The spelling status to filter by (from SpellingStatusStates)

        Yields:
            IWfiWordform: Each wordform object with the specified status

        Raises:
            FP_ParameterError: If status is invalid

        Example:
            >>> # Get all correctly spelled wordforms
            >>> correct_wfs = list(project.Wordforms.GetAllWithStatus(SpellingStatusStates.CORRECT))
            >>> print(f"Found {len(correct_wfs)} approved wordforms")
            >>>
            >>> # Get all misspellings
            >>> for wf in project.Wordforms.GetAllWithStatus(SpellingStatusStates.INCORRECT):
            ...     form = project.Wordforms.GetForm(wf)
            ...     print(f"Misspelling: {form}")

        Notes:
            - Returns an iterator for memory efficiency with large projects
            - Valid status values (from SpellingStatusStates):
              - UNDECIDED (0): Not yet reviewed
              - INCORRECT (1): Known misspelling
              - CORRECT (2): Approved spelling
            - Use list() to convert to a list if needed

        See Also:
            GetAllUnapproved, GetSpellingStatus, SpellingStatusStates
        """
        if status not in (SpellingStatusStates.UNDECIDED,
                         SpellingStatusStates.INCORRECT,
                         SpellingStatusStates.CORRECT):
            raise FP_ParameterError(f"Invalid spelling status: {status}. Must be 0, 1, or 2.")

        for wf in self.GetAll():
            if wf.SpellingStatus == status:
                yield wf

    def GetAllUnapproved(self):
        """
        Retrieve all wordforms that are not approved (not CORRECT status).

        Yields:
            IWfiWordform: Each wordform object with UNDECIDED or INCORRECT status

        Example:
            >>> # Get all unapproved wordforms
            >>> for wf in project.Wordforms.GetAllUnapproved():
            ...     form = project.Wordforms.GetForm(wf)
            ...     status = project.Wordforms.GetSpellingStatus(wf)
            ...     print(f"{form}: status={status}")
            >>>
            >>> # Count unapproved wordforms
            >>> unapproved_count = sum(1 for _ in project.Wordforms.GetAllUnapproved())
            >>> print(f"Total unapproved: {unapproved_count}")

        Notes:
            - Returns an iterator for memory efficiency with large projects
            - Includes both UNDECIDED (0) and INCORRECT (1) statuses
            - Excludes only CORRECT (2) status wordforms
            - Useful for spell-checking and wordform review workflows

        See Also:
            GetAllWithStatus, ApproveSpelling, GetSpellingStatus
        """
        for wf in self.GetAll():
            if wf.SpellingStatus != SpellingStatusStates.CORRECT:
                yield wf

    def ApproveSpelling(self, wordform_or_hvo):
        """
        Approve the spelling of a wordform by setting status to CORRECT.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_ParameterError: If wordform doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("colour")
            >>> project.Wordforms.ApproveSpelling(wf)
            >>>
            >>> # Approve multiple wordforms
            >>> for wf in project.Wordforms.GetAllWithStatus(SpellingStatusStates.UNDECIDED):
            ...     if should_approve(wf):
            ...         project.Wordforms.ApproveSpelling(wf)

        Notes:
            - This is equivalent to SetSpellingStatus(wf, SpellingStatusStates.CORRECT)
            - Approved wordforms are marked as correctly spelled
            - Affects spell-checking and analysis suggestions
            - Convenience method for common approval workflow

        See Also:
            SetSpellingStatus, GetAllUnapproved, GetSpellingStatus
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        # Resolve to wordform object
        if isinstance(wordform_or_hvo, int):
            wordform = self.project.Object(wordform_or_hvo)
            if not isinstance(wordform, IWfiWordform):
                raise FP_ParameterError("HVO does not refer to a wordform")
        else:
            wordform = wordform_or_hvo

        wordform.SpellingStatus = SpellingStatusStates.CORRECT
