#
#   WfiWordformOperations.py
#
#   Class: WfiWordformOperations
#          Wordform inventory operations for FieldWorks Language Explorer
#          projects via SIL Language and Culture Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

import logging
logger = logging.getLogger(__name__)

# Import BaseOperations parent class
from ..BaseOperations import BaseOperations

# Import FLEx LCM types
from SIL.LCModel import (
    IWfiWordform,
    IWfiWordformFactory,
    IWfiWordformRepository,
    IWfiAnalysis,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class WfiWordformOperations(BaseOperations):
    """
    This class provides operations for managing wordforms in the Wordform Inventory.

    The Wordform Inventory stores unique word forms encountered in interlinear texts.
    Each wordform can have multiple analyses representing different morphological
    breakdowns. This is the MOST ACTIVE area of FLEx (727+ commits in 2024).

    Wordforms bridge texts and lexicon, enabling:
    - Parser training and improvement
    - Interlinear text analysis
    - Concordance generation
    - Word frequency analysis

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Find or create wordform
        vern_ws = project.project.DefaultVernWs
        wordform = project.Wordforms.FindOrCreate("hlauka", vern_ws)

        # Get all analyses
        for analysis in project.Wordforms.GetAnalyses(wordform):
            gloss = project.WfiAnalyses.GetGlosses(analysis)
            print(f"Analysis: {gloss}")

        # Set approved analysis
        if wordform.AnalysesOC.Count > 0:
            best = wordform.AnalysesOC[0]
            project.Wordforms.SetApprovedAnalysis(wordform, best)

        # Get occurrence count
        count = project.Wordforms.GetOccurrences(wordform)
        print(f"Occurs {count} times in texts")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize WfiWordformOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)


    # --- Core CRUD Operations ---

    def GetAll(self):
        """
        Get all wordforms in the Wordform Inventory.

        Yields:
            IWfiWordform: Each wordform object in the inventory

        Example:
            >>> for wordform in project.Wordforms.GetAll():
            ...     form = project.Wordforms.GetForm(wordform)
            ...     analyses = wordform.AnalysesOC.Count
            ...     print(f"{form}: {analyses} analyses")
            hlauka: 3 analyses
            gula: 2 analyses
            zwane: 1 analysis

        Notes:
            - Returns an iterator for memory efficiency
            - Wordforms are returned in database order
            - Each wordform represents a unique surface form from texts
            - Use GetForm() to access the text representation
            - Large inventories (10,000+ wordforms) are common

        See Also:
            Find, FindOrCreate, Create
        """
        return self.project.ObjectsIn(IWfiWordformRepository)


    def Create(self, form, wsHandle=None):
        """
        Create a new wordform in the Wordform Inventory.

        Args:
            form (str): The wordform text
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            IWfiWordform: The newly created wordform

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If form is None
            FP_ParameterError: If form is empty

        Example:
            >>> wordform = project.Wordforms.Create("hlauka")
            >>> print(project.Wordforms.GetForm(wordform))
            hlauka

            >>> # Create with specific writing system
            >>> wordform = project.Wordforms.Create("hello", project.WSHandle('en'))

        Notes:
            - Wordform is added to the Wordform Inventory
            - Usually you want FindOrCreate() instead of Create()
            - Create() doesn't check for duplicates
            - New wordform has zero analyses initially
            - Writing system should match text source

        See Also:
            FindOrCreate, Find, Delete
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if form is None:
            raise FP_NullParameterError()

        if not form or not form.strip():
            raise FP_ParameterError("Wordform cannot be empty")

        wsHandle = self.__WSHandle(wsHandle)

        # Create the wordform using factory
        factory = self.project.project.ServiceLocator.GetService(IWfiWordformFactory)
        new_wordform = factory.Create()

        # Set the form
        mkstr = TsStringUtils.MakeString(form, wsHandle)
        new_wordform.Form.set_String(wsHandle, mkstr)

        return new_wordform


    def Delete(self, wordform_or_hvo):
        """
        Delete a wordform from the Wordform Inventory.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If wordform_or_hvo is None

        Example:
            >>> wordform = project.Wordforms.Find("obsolete")
            >>> if wordform:
            ...     project.Wordforms.Delete(wordform)

        Warning:
            - This is a destructive operation
            - All analyses for this wordform will be deleted
            - Text occurrences may become unlinked
            - Cannot be undone
            - Use with caution - wordforms are typically managed automatically

        Notes:
            - Deletion cascades to all analyses, glosses, and morph bundles
            - References from texts may become invalid
            - Consider leaving orphaned wordforms for historical data

        See Also:
            Create, FindOrCreate
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not wordform_or_hvo:
            raise FP_NullParameterError()

        wordform = self.__ResolveObject(wordform_or_hvo)

        # Delete the wordform (LCM handles removal from repository)
        wordform.Delete()


    def Find(self, form, wsHandle=None):
        """
        Find a wordform by its form text.

        Args:
            form (str): The wordform text to search for
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            IWfiWordform or None: The wordform object if found, None otherwise

        Raises:
            FP_NullParameterError: If form is None

        Example:
            >>> wordform = project.Wordforms.Find("hlauka")
            >>> if wordform:
            ...     analyses = wordform.AnalysesOC.Count
            ...     print(f"Found wordform with {analyses} analyses")
            Found wordform with 3 analyses

            >>> # Search in specific writing system
            >>> wordform = project.Wordforms.Find("hello", project.WSHandle('en'))

        Notes:
            - Returns first match only
            - Search is case-sensitive
            - Search is writing-system specific
            - Returns None if not found (doesn't raise exception)
            - For guaranteed result, use FindOrCreate()

        See Also:
            FindOrCreate, Exists, GetAll
        """
        if form is None:
            raise FP_NullParameterError()

        if not form or not form.strip():
            return None

        wsHandle = self.__WSHandle(wsHandle)

        # Search through all wordforms
        for wordform in self.GetAll():
            wf_form = ITsString(wordform.Form.get_String(wsHandle)).Text
            if wf_form == form:
                return wordform

        return None


    def FindOrCreate(self, form, wsHandle=None):
        """
        Find an existing wordform or create a new one.

        This is the most common pattern for working with the Wordform Inventory.
        It ensures a wordform exists without creating duplicates.

        Args:
            form (str): The wordform text
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            IWfiWordform: The found or created wordform

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled (for create)
            FP_NullParameterError: If form is None
            FP_ParameterError: If form is empty

        Example:
            >>> # Safe pattern - always returns a wordform
            >>> wordform = project.Wordforms.FindOrCreate("hlauka")
            >>> print(project.Wordforms.GetForm(wordform))
            hlauka

            >>> # Use when processing interlinear texts
            >>> for word_text in text_words:
            ...     wf = project.Wordforms.FindOrCreate(word_text)
            ...     # Add analysis, gloss, etc.

        Notes:
            - This is the recommended method for inventory management
            - Avoids duplicate wordforms
            - Creates only if necessary
            - Common pattern for parser and text processing
            - Returns existing wordform without modification

        See Also:
            Find, Create, Exists
        """
        if form is None:
            raise FP_NullParameterError()

        if not form or not form.strip():
            raise FP_ParameterError("Wordform cannot be empty")

        # Try to find existing wordform
        existing = self.Find(form, wsHandle)
        if existing:
            return existing

        # Create new wordform if not found
        return self.Create(form, wsHandle)


    def FindByHvo(self, hvo):
        """
        Find a wordform by its HVO (database ID).

        Args:
            hvo (int): The HVO of the wordform

        Returns:
            IWfiWordform or None: The wordform object if found, None otherwise

        Raises:
            FP_NullParameterError: If hvo is None

        Example:
            >>> wordform = project.Wordforms.FindByHvo(12345)
            >>> if wordform:
            ...     form = project.Wordforms.GetForm(wordform)
            ...     print(f"Found wordform: {form}")

        Notes:
            - Direct HVO lookup is faster than searching by form
            - Returns None if HVO doesn't exist or isn't a wordform
            - HVO is the internal database identifier

        See Also:
            Find, GetAll
        """
        if hvo is None:
            raise FP_NullParameterError()

        try:
            obj = self.project.Object(hvo)
            if isinstance(obj, IWfiWordform):
                return obj
        except:
            pass

        return None


    # --- Property Access ---

    def GetForm(self, wordform_or_hvo, wsHandle=None):
        """
        Get the text form of a wordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            str: The wordform text (empty string if not set)

        Raises:
            FP_NullParameterError: If wordform_or_hvo is None

        Example:
            >>> wordform = project.Wordforms.FindOrCreate("hlauka")
            >>> form = project.Wordforms.GetForm(wordform)
            >>> print(form)
            hlauka

        See Also:
            Find, FindOrCreate
        """
        if not wordform_or_hvo:
            raise FP_NullParameterError()

        wordform = self.__ResolveObject(wordform_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        form = ITsString(wordform.Form.get_String(wsHandle)).Text
        return form or ""


    # --- Analysis Management ---

    def GetAnalyses(self, wordform_or_hvo):
        """
        Get all analyses for a wordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Returns:
            list: List of IWfiAnalysis objects

        Raises:
            FP_NullParameterError: If wordform_or_hvo is None

        Example:
            >>> wordform = project.Wordforms.Find("hlauka")
            >>> analyses = project.Wordforms.GetAnalyses(wordform)
            >>> for analysis in analyses:
            ...     approved = project.WfiAnalyses.IsHumanApproved(analysis)
            ...     status = "approved" if approved else "parser guess"
            ...     print(f"Analysis: {status}")
            Analysis: approved
            Analysis: parser guess
            Analysis: parser guess

        Notes:
            - Returns empty list if no analyses
            - Analyses can be human-approved or parser-generated
            - Multiple analyses represent ambiguity
            - Use GetApprovedAnalysis() for the preferred analysis

        See Also:
            GetApprovedAnalysis, SetApprovedAnalysis
        """
        if not wordform_or_hvo:
            raise FP_NullParameterError()

        wordform = self.__ResolveObject(wordform_or_hvo)

        return list(wordform.AnalysesOC)


    def GetApprovedAnalysis(self, wordform_or_hvo):
        """
        Get the human-approved analysis for a wordform.

        The approved analysis is the linguist's preferred morphological breakdown,
        distinguishing it from parser guesses.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Returns:
            IWfiAnalysis or None: The approved analysis, or None if not set

        Raises:
            FP_NullParameterError: If wordform_or_hvo is None

        Example:
            >>> wordform = project.Wordforms.Find("hlauka")
            >>> approved = project.Wordforms.GetApprovedAnalysis(wordform)
            >>> if approved:
            ...     glosses = project.WfiAnalyses.GetGlosses(approved)
            ...     print(f"Approved analysis: {glosses}")
            ... else:
            ...     print("No approved analysis yet")
            Approved analysis: run

        Notes:
            - Returns None if no analysis is approved
            - Only one analysis can be approved at a time
            - Approval indicates human verification
            - Parser uses approved analyses for training

        See Also:
            SetApprovedAnalysis, GetAnalyses
        """
        if not wordform_or_hvo:
            raise FP_NullParameterError()

        wordform = self.__ResolveObject(wordform_or_hvo)

        # Check if there's a human-approved analysis
        for analysis in wordform.AnalysesOC:
            if wordform.HumanApprovedAnalysesRS.Contains(analysis):
                return analysis

        return None


    def SetApprovedAnalysis(self, wordform_or_hvo, analysis):
        """
        Set the human-approved analysis for a wordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO
            analysis: IWfiAnalysis object to approve (or None to clear approval)

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If wordform_or_hvo is None
            FP_ParameterError: If analysis doesn't belong to this wordform

        Example:
            >>> wordform = project.Wordforms.Find("hlauka")
            >>> analyses = project.Wordforms.GetAnalyses(wordform)
            >>> if analyses:
            ...     # Approve first analysis
            ...     project.Wordforms.SetApprovedAnalysis(wordform, analyses[0])

            >>> # Clear approval
            >>> project.Wordforms.SetApprovedAnalysis(wordform, None)

        Notes:
            - Only one analysis can be approved at a time
            - Previous approval is automatically cleared
            - Pass None to clear approval
            - Analysis must belong to this wordform
            - Approved analyses train the parser

        See Also:
            GetApprovedAnalysis, GetAnalyses
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not wordform_or_hvo:
            raise FP_NullParameterError()

        wordform = self.__ResolveObject(wordform_or_hvo)

        # Clear existing approval
        wordform.HumanApprovedAnalysesRS.Clear()

        # Set new approval if provided
        if analysis:
            # Verify analysis belongs to this wordform
            if analysis not in wordform.AnalysesOC:
                raise FP_ParameterError("Analysis does not belong to this wordform")

            wordform.HumanApprovedAnalysesRS.Add(analysis)


    def GetOccurrences(self, wordform_or_hvo):
        """
        Get the number of times this wordform occurs in texts.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Returns:
            int: The occurrence count

        Raises:
            FP_NullParameterError: If wordform_or_hvo is None

        Example:
            >>> wordform = project.Wordforms.Find("hlauka")
            >>> count = project.Wordforms.GetOccurrences(wordform)
            >>> print(f"'hlauka' occurs {count} times in texts")
            'hlauka' occurs 15 times in texts

        Notes:
            - Count is maintained automatically by FLEx
            - Includes occurrences in all interlinear texts
            - Useful for frequency analysis
            - May not reflect deleted or modified texts

        See Also:
            GetForm, GetAnalyses
        """
        if not wordform_or_hvo:
            raise FP_NullParameterError()

        wordform = self.__ResolveObject(wordform_or_hvo)

        # Count occurrences from segments
        # Note: This is a simplified count - actual implementation may be more complex
        return wordform.OccurrencesInTexts.Count


    # --- Private Helper Methods ---

    def __ResolveObject(self, wordform_or_hvo):
        """
        Resolve HVO or object to IWfiWordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or an HVO (int)

        Returns:
            IWfiWordform: The resolved wordform object

        Raises:
            FP_ParameterError: If HVO doesn't refer to a wordform
        """
        if isinstance(wordform_or_hvo, int):
            obj = self.project.Object(wordform_or_hvo)
            if not isinstance(obj, IWfiWordform):
                raise FP_ParameterError("HVO does not refer to a wordform")
            return obj
        return wordform_or_hvo


    def __WSHandle(self, wsHandle):
        """
        Get writing system handle, defaulting to vernacular WS.

        Args:
            wsHandle: Optional writing system handle

        Returns:
            int: The writing system handle
        """
        if wsHandle is None:
            return self.project.project.DefaultVernWs
        return self.project._FLExProject__WSHandle(
            wsHandle,
            self.project.project.DefaultVernWs
        )
