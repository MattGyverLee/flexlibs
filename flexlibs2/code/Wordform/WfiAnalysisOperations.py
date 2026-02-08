#
#   WfiAnalysisOperations.py
#
#   Class: WfiAnalysisOperations
#          Wordform analysis operations for FieldWorks Language Explorer
#          projects via SIL Language and Culture Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

# Import BaseOperations parent class
from ..BaseOperations import BaseOperations

# Import FLEx LCM types
from SIL.LCModel import (
    IWfiAnalysis,
    IWfiAnalysisFactory,
    IWfiWordform,
    IWfiMorphBundle,
    IPartOfSpeech,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)

class WfiAnalysisOperations(BaseOperations):
    """
    This class provides operations for managing wordform analyses.

    A WfiAnalysis represents a morphological analysis of a wordform, breaking it down
    into morpheme bundles with glosses and grammatical categories. Each wordform can
    have multiple analyses representing different interpretations or parser hypotheses.

    Analyses distinguish between:
    - Human-approved analyses (verified by linguist)
    - Parser-generated analyses (computational guesses)

    Usage::

        from flexlibs2 import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get wordform
        wordform = project.Wordforms.FindOrCreate("hlauka")

        # Create analysis
        analysis = project.WfiAnalyses.Create(wordform)

        # Set category (part of speech)
        verb_pos = project.GetPartOfSpeech("verb")
        if verb_pos:
            project.WfiAnalyses.SetCategory(analysis, verb_pos)

        # Mark as human-approved
        project.WfiAnalyses.Approve(analysis)

        # Get morpheme bundles
        bundles = project.WfiAnalyses.GetMorphBundles(analysis)

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize WfiAnalysisOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)

    # --- Core CRUD Operations ---

    def GetAll(self, wordform_or_hvo):
        """
        Get all analyses for a wordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Yields:
            IWfiAnalysis: Each analysis object for the wordform

        Raises:
            FP_NullParameterError: If wordform_or_hvo is None

        Example:
            >>> wordform = project.Wordforms.Find("hlauka")
            >>> for analysis in project.WfiAnalyses.GetAll(wordform):
            ...     approved = project.WfiAnalyses.IsHumanApproved(analysis)
            ...     cat = project.WfiAnalyses.GetCategory(analysis)
            ...     status = "approved" if approved else "guess"
            ...     print(f"Analysis ({status}): {cat}")
            Analysis (approved): verb
            Analysis (guess): noun

        Notes:
            - Returns empty generator if no analyses
            - Analyses ordered by creation (oldest first)
            - First analysis is typically parser's best guess
            - Use IsHumanApproved() to distinguish verified analyses

        See Also:
            Create, Find, Delete
        """
        if not wordform_or_hvo:
            raise FP_NullParameterError()

        wordform = self.__GetWordformObject(wordform_or_hvo)

        for analysis in wordform.AnalysesOC:
            yield analysis

    def Create(self, wordform_or_hvo):
        """
        Create a new analysis for a wordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Returns:
            IWfiAnalysis: The newly created analysis

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If wordform_or_hvo is None

        Example:
            >>> wordform = project.Wordforms.FindOrCreate("hlauka")
            >>> analysis = project.WfiAnalyses.Create(wordform)
            >>>
            >>> # Set category
            >>> verb_pos = project.GetPartOfSpeech("verb")
            >>> project.WfiAnalyses.SetCategory(analysis, verb_pos)
            >>>
            >>> # Add morph bundles
            >>> bundle = project.WfiMorphBundles.Create(analysis, "hlauk-")
            >>> # ... set bundle properties

        Notes:
            - Analysis is added to the wordform's analyses collection
            - New analysis starts with no category, glosses, or morph bundles
            - Not marked as human-approved initially
            - Use SetCategory(), AddGloss(), etc. to populate

        See Also:
            Delete, Approve, SetCategory
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not wordform_or_hvo:
            raise FP_NullParameterError()

        wordform = self.__GetWordformObject(wordform_or_hvo)

        # Create the analysis using factory
        factory = self.project.project.ServiceLocator.GetService(IWfiAnalysisFactory)
        new_analysis = factory.Create()

        # Add to wordform's analyses collection
        wordform.AnalysesOC.Add(new_analysis)

        return new_analysis

    def Delete(self, analysis_or_hvo):
        """
        Delete a wordform analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo is None

        Example:
            >>> wordform = project.Wordforms.Find("hlauka")
            >>> analyses = list(project.WfiAnalyses.GetAll(wordform))
            >>> if len(analyses) > 1:
            ...     # Delete parser guess, keep human-approved
            ...     for analysis in analyses:
            ...         if not project.WfiAnalyses.IsHumanApproved(analysis):
            ...             project.WfiAnalyses.Delete(analysis)

        Warning:
            - This is a destructive operation
            - All morph bundles and glosses will be deleted
            - Cannot be undone
            - If this was the approved analysis, approval is cleared

        Notes:
            - Deletion cascades to morph bundles and glosses
            - Safe to delete parser guesses to clean up inventory
            - Be careful deleting human-approved analyses

        See Also:
            Create, IsHumanApproved
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__ResolveObject(analysis_or_hvo)

        # Delete the analysis (LCM handles removal from collections)
        analysis.Delete()

    def Find(self, wordform_or_hvo, index):
        """
        Find an analysis by its index in the wordform's analyses.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO
            index (int): Zero-based index of the analysis

        Returns:
            IWfiAnalysis or None: The analysis object if found, None otherwise

        Raises:
            FP_NullParameterError: If wordform_or_hvo is None

        Example:
            >>> wordform = project.Wordforms.Find("hlauka")
            >>> # Get first analysis (typically parser's best guess)
            >>> first_analysis = project.WfiAnalyses.Find(wordform, 0)
            >>> if first_analysis:
            ...     print("Found first analysis")

        Notes:
            - Returns None if index out of range
            - Index 0 is typically the parser's first/best guess
            - Use GetAll() to iterate all analyses

        See Also:
            GetAll, Create
        """
        if not wordform_or_hvo:
            raise FP_NullParameterError()

        wordform = self.__GetWordformObject(wordform_or_hvo)

        if index < 0 or index >= wordform.AnalysesOC.Count:
            return None

        return wordform.AnalysesOC[index]

    # --- Category (Part of Speech) ---

    def GetCategory(self, analysis_or_hvo):
        """
        Get the part of speech category for an analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            IPartOfSpeech or None: The category object, or None if not set

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None

        Example:
            >>> analysis = project.WfiAnalyses.Find(wordform, 0)
            >>> category = project.WfiAnalyses.GetCategory(analysis)
            >>> if category:
            ...     name = ITsString(category.Name.BestAnalysisAlternative).Text
            ...     print(f"Category: {name}")
            Category: verb

        Notes:
            - Returns None if no category set
            - Category represents the word-level part of speech
            - Different from morph-bundle categories (affix types, etc.)

        See Also:
            SetCategory
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__ResolveObject(analysis_or_hvo)

        return analysis.CategoryRA if hasattr(analysis, 'CategoryRA') else None

    def SetCategory(self, analysis_or_hvo, pos):
        """
        Set the part of speech category for an analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO
            pos: IPartOfSpeech object (or None to clear category)

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo is None

        Example:
            >>> analysis = project.WfiAnalyses.Create(wordform)
            >>> verb_pos = project.GetPartOfSpeech("verb")
            >>> if verb_pos:
            ...     project.WfiAnalyses.SetCategory(analysis, verb_pos)

            >>> # Clear category
            >>> project.WfiAnalyses.SetCategory(analysis, None)

        Notes:
            - Category represents word-level part of speech
            - Pass None to clear the category
            - Category should match the word's function in context

        See Also:
            GetCategory, project.GetPartOfSpeech
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__ResolveObject(analysis_or_hvo)

        if hasattr(analysis, 'CategoryRA'):
            analysis.CategoryRA = pos

    # --- Human Approval ---

    def IsHumanApproved(self, analysis_or_hvo):
        """
        Check if an analysis is human-approved.

        Human approval distinguishes verified linguistic analyses from parser guesses.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            bool: True if human-approved, False otherwise

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None

        Example:
            >>> wordform = project.Wordforms.Find("hlauka")
            >>> for analysis in project.WfiAnalyses.GetAll(wordform):
            ...     if project.WfiAnalyses.IsHumanApproved(analysis):
            ...         print("This analysis is verified")
            ...     else:
            ...         print("This is a parser guess")
            This analysis is verified
            This is a parser guess

        Notes:
            - Only one analysis per wordform should be approved
            - Approved analyses train the parser
            - Use Approve() to set human approval
            - Unapproved analyses are parser hypotheses

        See Also:
            Approve, project.Wordforms.SetApprovedAnalysis
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__ResolveObject(analysis_or_hvo)

        # Check if owning wordform has this analysis as approved
        wordform = analysis.Owner
        if isinstance(wordform, IWfiWordform):
            return wordform.HumanApprovedAnalyses.Contains(analysis)

        return False

    def Approve(self, analysis_or_hvo):
        """
        Mark an analysis as human-approved.

        This sets the analysis as the linguist-verified interpretation,
        distinguishing it from parser guesses.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo is None

        Example:
            >>> wordform = project.Wordforms.Find("hlauka")
            >>> analysis = project.WfiAnalyses.Create(wordform)
            >>> # ... set category, add morph bundles, etc.
            >>> project.WfiAnalyses.Approve(analysis)
            >>>
            >>> # Check approval
            >>> if project.WfiAnalyses.IsHumanApproved(analysis):
            ...     print("Analysis is now approved")

        Notes:
            - Only one analysis per wordform should be approved
            - Previous approval is automatically cleared
            - Approved analyses are used for parser training
            - This is equivalent to project.Wordforms.SetApprovedAnalysis()

        See Also:
            IsHumanApproved, project.Wordforms.SetApprovedAnalysis
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__ResolveObject(analysis_or_hvo)

        # Get owning wordform
        wordform = analysis.Owner
        if not isinstance(wordform, IWfiWordform):
            raise FP_ParameterError("Analysis does not have a wordform owner")

        # Clear existing approval and set new one
        wordform.HumanApprovedAnalyses.Clear()
        wordform.HumanApprovedAnalyses.Add(analysis)

    # --- Morph Bundles ---

    def GetMorphBundles(self, analysis_or_hvo):
        """
        Get all morpheme bundles for an analysis.

        Morph bundles represent the morphological breakdown of the wordform.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            list: List of IWfiMorphBundle objects

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None

        Example:
            >>> analysis = project.WfiAnalyses.Find(wordform, 0)
            >>> bundles = project.WfiAnalyses.GetMorphBundles(analysis)
            >>> for bundle in bundles:
            ...     form = project.WfiMorphBundles.GetForm(bundle)
            ...     print(f"Morpheme: {form}")
            Morpheme: hlauk-
            Morpheme: -a

        Notes:
            - Returns empty list if no morph bundles
            - Bundles are ordered left-to-right in the word
            - Each bundle represents one morpheme
            - Use project.WfiMorphBundles operations to manipulate

        See Also:
            project.WfiMorphBundles.Create, project.WfiMorphBundles.GetAll
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__ResolveObject(analysis_or_hvo)

        return list(analysis.MorphBundlesOS)

    # --- Glosses ---

    def GetGlosses(self, analysis_or_hvo):
        """
        Get all word-level glosses for an analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            list: List of IWfiGloss objects

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None

        Example:
            >>> analysis = project.WfiAnalyses.Find(wordform, 0)
            >>> glosses = project.WfiAnalyses.GetGlosses(analysis)
            >>> for gloss in glosses:
            ...     text = project.WfiGlosses.GetForm(gloss)
            ...     print(f"Gloss: {text}")
            Gloss: run

        Notes:
            - Returns empty list if no glosses
            - Glosses are word-level (not morpheme-level)
            - Multiple glosses represent translations in different languages
            - Use project.WfiGlosses operations to manipulate

        See Also:
            project.WfiGlosses.Create, project.WfiGlosses.GetAll
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__ResolveObject(analysis_or_hvo)

        return list(analysis.MeaningsOC)

    # --- Private Helper Methods ---

    def __ResolveObject(self, analysis_or_hvo):
        """
        Resolve HVO or object to IWfiAnalysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or an HVO (int)

        Returns:
            IWfiAnalysis: The resolved analysis object

        Raises:
            FP_ParameterError: If HVO doesn't refer to an analysis
        """
        if isinstance(analysis_or_hvo, int):
            obj = self.project.Object(analysis_or_hvo)
            if not isinstance(obj, IWfiAnalysis):
                raise FP_ParameterError("HVO does not refer to a wordform analysis")
            return obj
        return analysis_or_hvo

    def __GetWordformObject(self, wordform_or_hvo):
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
