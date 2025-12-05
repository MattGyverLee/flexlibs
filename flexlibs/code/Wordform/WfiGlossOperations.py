#
#   WfiGlossOperations.py
#
#   Class: WfiGlossOperations
#          Wordform gloss operations for FieldWorks Language Explorer
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
    IWfiGloss,
    IWfiGlossFactory,
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


class WfiGlossOperations(BaseOperations):
    """
    This class provides operations for managing wordform glosses.

    A WfiGloss represents a word-level gloss (translation) for a wordform analysis.
    Glosses provide the meaning of the entire word, not individual morphemes.
    Multiple glosses can exist for different analysis languages.

    Glosses distinguish between:
    - Human-approved glosses (verified translations)
    - Parser-generated glosses (computational guesses)

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get analysis
        wordform = project.Wordforms.FindOrCreate("hlauka")
        analysis = project.WfiAnalyses.Create(wordform)

        # Create gloss
        gloss = project.WfiGlosses.Create(analysis, "run", project.WSHandle('en'))

        # Mark as human-approved
        project.WfiGlosses.Approve(gloss)

        # Get all glosses
        for g in project.WfiGlosses.GetAll(analysis):
            text = project.WfiGlosses.GetForm(g)
            approved = project.WfiGlosses.IsHumanApproved(g)
            print(f"Gloss: {text} ({'approved' if approved else 'guess'})")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize WfiGlossOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)


    # --- Core CRUD Operations ---

    def GetAll(self, analysis_or_hvo):
        """
        Get all glosses for a wordform analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Yields:
            IWfiGloss: Each gloss object for the analysis

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None

        Example:
            >>> analysis = project.WfiAnalyses.Find(wordform, 0)
            >>> for gloss in project.WfiGlosses.GetAll(analysis):
            ...     text = project.WfiGlosses.GetForm(gloss)
            ...     approved = project.WfiGlosses.IsHumanApproved(gloss)
            ...     print(f"{text} ({'✓' if approved else '?'})")
            run (✓)
            to run (?)

        Notes:
            - Returns empty generator if no glosses
            - Glosses ordered by creation (oldest first)
            - Multiple glosses represent different translations
            - Use IsHumanApproved() to distinguish verified glosses

        See Also:
            Create, Find, Delete
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        for gloss in analysis.MeaningsOC:
            yield gloss


    def Create(self, analysis_or_hvo, gloss_text, wsHandle=None):
        """
        Create a new gloss for a wordform analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO
            gloss_text (str): The gloss translation text
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            IWfiGloss: The newly created gloss

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo or gloss_text is None
            FP_ParameterError: If gloss_text is empty

        Example:
            >>> analysis = project.WfiAnalyses.Create(wordform)
            >>> gloss = project.WfiGlosses.Create(analysis, "run", project.WSHandle('en'))
            >>> print(project.WfiGlosses.GetForm(gloss))
            run

            >>> # Create gloss in different language
            >>> gloss_fr = project.WfiGlosses.Create(analysis, "courir", project.WSHandle('fr'))

        Notes:
            - Gloss is added to the analysis's meanings collection
            - Not marked as human-approved initially
            - Multiple glosses can exist for different languages
            - Gloss represents word-level meaning, not morpheme-level

        See Also:
            Delete, Approve, SetForm
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if analysis_or_hvo is None:
            raise FP_NullParameterError()
        if gloss_text is None:
            raise FP_NullParameterError()

        if not gloss_text or not gloss_text.strip():
            raise FP_ParameterError("Gloss text cannot be empty")

        analysis = self.__GetAnalysisObject(analysis_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        # Create the gloss using factory
        factory = self.project.project.ServiceLocator.GetService(IWfiGlossFactory)
        new_gloss = factory.Create()

        # Add to analysis's meanings collection
        analysis.MeaningsOC.Add(new_gloss)

        # Set the gloss form
        mkstr = TsStringUtils.MakeString(gloss_text, wsHandle)
        new_gloss.Form.set_String(wsHandle, mkstr)

        return new_gloss


    def Delete(self, gloss_or_hvo):
        """
        Delete a wordform gloss.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If gloss_or_hvo is None

        Example:
            >>> analysis = project.WfiAnalyses.Find(wordform, 0)
            >>> glosses = list(project.WfiGlosses.GetAll(analysis))
            >>> if len(glosses) > 1:
            ...     # Delete duplicate or incorrect gloss
            ...     project.WfiGlosses.Delete(glosses[1])

        Warning:
            - This is a destructive operation
            - Cannot be undone
            - If this was an approved gloss, approval is cleared

        Notes:
            - Safe to delete parser-generated glosses
            - Be careful deleting human-approved glosses
            - Analysis can exist without glosses

        See Also:
            Create, IsHumanApproved
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not gloss_or_hvo:
            raise FP_NullParameterError()

        gloss = self.__ResolveObject(gloss_or_hvo)

        # Delete the gloss (LCM handles removal from collections)
        gloss.Delete()


    def Find(self, analysis_or_hvo, index):
        """
        Find a gloss by its index in the analysis's glosses.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO
            index (int): Zero-based index of the gloss

        Returns:
            IWfiGloss or None: The gloss object if found, None otherwise

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None

        Example:
            >>> analysis = project.WfiAnalyses.Find(wordform, 0)
            >>> # Get first gloss
            >>> first_gloss = project.WfiGlosses.Find(analysis, 0)
            >>> if first_gloss:
            ...     print(project.WfiGlosses.GetForm(first_gloss))

        Notes:
            - Returns None if index out of range
            - Index 0 is typically the primary gloss
            - Use GetAll() to iterate all glosses

        See Also:
            GetAll, Create
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        if index < 0 or index >= analysis.MeaningsOC.Count:
            return None

        return analysis.MeaningsOC[index]


    # --- Property Access ---

    def GetForm(self, gloss_or_hvo, wsHandle=None):
        """
        Get the text form of a gloss.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The gloss text (empty string if not set)

        Raises:
            FP_NullParameterError: If gloss_or_hvo is None

        Example:
            >>> gloss = project.WfiGlosses.Find(analysis, 0)
            >>> text = project.WfiGlosses.GetForm(gloss)
            >>> print(text)
            run

            >>> # Get in specific writing system
            >>> text_fr = project.WfiGlosses.GetForm(gloss, project.WSHandle('fr'))

        See Also:
            SetForm, Create
        """
        if not gloss_or_hvo:
            raise FP_NullParameterError()

        gloss = self.__ResolveObject(gloss_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        form = ITsString(gloss.Form.get_String(wsHandle)).Text
        return form or ""


    def SetForm(self, gloss_or_hvo, text, wsHandle=None):
        """
        Set the text form of a gloss.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO
            text (str): The new gloss text
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If gloss_or_hvo or text is None
            FP_ParameterError: If text is empty

        Example:
            >>> gloss = project.WfiGlosses.Find(analysis, 0)
            >>> project.WfiGlosses.SetForm(gloss, "to run")
            >>> print(project.WfiGlosses.GetForm(gloss))
            to run

        See Also:
            GetForm
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not gloss_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        if not text or not text.strip():
            raise FP_ParameterError("Gloss text cannot be empty")

        gloss = self.__ResolveObject(gloss_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        mkstr = TsStringUtils.MakeString(text, wsHandle)
        gloss.Form.set_String(wsHandle, mkstr)


    # --- Human Approval ---

    def IsHumanApproved(self, gloss_or_hvo):
        """
        Check if a gloss is human-approved.

        Human approval distinguishes verified translations from parser guesses.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO

        Returns:
            bool: True if human-approved, False otherwise

        Raises:
            FP_NullParameterError: If gloss_or_hvo is None

        Example:
            >>> for gloss in project.WfiGlosses.GetAll(analysis):
            ...     if project.WfiGlosses.IsHumanApproved(gloss):
            ...         print("Verified gloss")
            ...     else:
            ...         print("Parser guess")

        Notes:
            - Approved glosses are verified by linguist
            - Unapproved glosses are parser hypotheses
            - Use Approve() to set human approval
            - Only approved glosses should be used in publications

        See Also:
            Approve
        """
        if not gloss_or_hvo:
            raise FP_NullParameterError()

        gloss = self.__ResolveObject(gloss_or_hvo)

        # Check if owning wordform has this gloss as approved
        # Note: Approval is tracked at the wordform level
        analysis = gloss.Owner
        if isinstance(analysis, IWfiAnalysis):
            wordform = analysis.Owner
            if hasattr(wordform, 'HumanApprovedAnalysesRS'):
                # If the analysis is approved, its glosses are implicitly approved
                return wordform.HumanApprovedAnalysesRS.Contains(analysis)

        return False


    def Approve(self, gloss_or_hvo):
        """
        Mark a gloss as human-approved.

        This implicitly approves the owning analysis as well.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If gloss_or_hvo is None

        Example:
            >>> gloss = project.WfiGlosses.Create(analysis, "run")
            >>> project.WfiGlosses.Approve(gloss)
            >>>
            >>> # Check approval
            >>> if project.WfiGlosses.IsHumanApproved(gloss):
            ...     print("Gloss is now approved")

        Notes:
            - Approving a gloss also approves its owning analysis
            - Only one analysis per wordform should be approved
            - Previous approval is automatically cleared
            - Approved glosses are verified translations

        See Also:
            IsHumanApproved, project.WfiAnalyses.Approve
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not gloss_or_hvo:
            raise FP_NullParameterError()

        gloss = self.__ResolveObject(gloss_or_hvo)

        # Get owning analysis and wordform
        analysis = gloss.Owner
        if not isinstance(analysis, IWfiAnalysis):
            raise FP_ParameterError("Gloss does not have an analysis owner")

        wordform = analysis.Owner
        if not hasattr(wordform, 'HumanApprovedAnalysesRS'):
            raise FP_ParameterError("Analysis does not have a wordform owner")

        # Approve the analysis (which implicitly approves the gloss)
        wordform.HumanApprovedAnalysesRS.Clear()
        wordform.HumanApprovedAnalysesRS.Add(analysis)


    # --- Private Helper Methods ---

    def __ResolveObject(self, gloss_or_hvo):
        """
        Resolve HVO or object to IWfiGloss.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or an HVO (int)

        Returns:
            IWfiGloss: The resolved gloss object

        Raises:
            FP_ParameterError: If HVO doesn't refer to a gloss
        """
        if isinstance(gloss_or_hvo, int):
            obj = self.project.Object(gloss_or_hvo)
            if not isinstance(obj, IWfiGloss):
                raise FP_ParameterError("HVO does not refer to a wordform gloss")
            return obj
        return gloss_or_hvo


    def __GetAnalysisObject(self, analysis_or_hvo):
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


    def __WSHandleAnalysis(self, wsHandle):
        """
        Get writing system handle, defaulting to analysis WS.

        Args:
            wsHandle: Optional writing system handle

        Returns:
            int: The writing system handle
        """
        if wsHandle is None:
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(
            wsHandle,
            self.project.project.DefaultAnalWs
        )
