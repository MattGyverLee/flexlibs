#
#   WfiGlossOperations.py
#
#   Class: WfiGlossOperations
#          Wordform gloss operations for FieldWorks Language Explorer projects
#          via SIL Language and Culture Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

import logging
logger = logging.getLogger(__name__)

import clr
clr.AddReference("System")

from SIL.LCModel import (
    IWfiGloss,
    IWfiGlossFactory,
    IWfiAnalysis,
)

from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


# --- WfiGlossOperations Class ---

class WfiGlossOperations:
    """
    Provides operations for managing wordform glosses (WfiGloss) in a FLEx project.

    WfiGloss objects represent glosses (meanings/translations) for wordform analyses.
    Each WfiAnalysis can have multiple glosses in different writing systems.
    Glosses provide the semantic interpretation of an analyzed wordform.

    This class should be accessed via FLExProject.WfiGlosses property.

    Example:
        >>> project = FLExProject()
        >>> project.OpenProject("MyProject", writeEnabled=True)
        >>> # Get a wordform and its first analysis
        >>> wf = project.Wordforms.Find("running")
        >>> analyses = project.Wordforms.GetAnalyses(wf)
        >>> if analyses:
        ...     analysis = analyses[0]
        ...     # Get all glosses for the analysis
        ...     for gloss in project.WfiGlosses.GetAll(analysis):
        ...         form = project.WfiGlosses.GetForm(gloss)
        ...         print(f"Gloss: {form}")
        ...     # Create a new gloss
        ...     new_gloss = project.WfiGlosses.Create(analysis, "running", "en")
        ...     # Update gloss form
        ...     project.WfiGlosses.SetForm(new_gloss, "to run", "en")
        >>> project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize WfiGlossOperations.

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
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultAnalWs)

    # --- Core CRUD Operations ---

    def GetAll(self, analysis_or_hvo):
        """
        Retrieve all glosses for a wordform analysis.

        This method returns an iterator over all IWfiGloss objects associated with
        the specified analysis, allowing iteration over all meaning glosses.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Yields:
            IWfiGloss: Each gloss object for the analysis

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     for gloss in project.WfiGlosses.GetAll(analyses[0]):
            ...         form = project.WfiGlosses.GetForm(gloss)
            ...         print(form)

        Notes:
            - Returns an iterator for memory efficiency
            - Glosses are returned in the order they were added
            - Returns empty iterator if analysis has no glosses
            - Each gloss can have forms in multiple writing systems

        See Also:
            Create, Find, GetForm
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        # Resolve to analysis object
        if isinstance(analysis_or_hvo, int):
            analysis = self.project.Object(analysis_or_hvo)
            if not isinstance(analysis, IWfiAnalysis):
                raise FP_ParameterError("HVO does not refer to a wordform analysis")
        else:
            analysis = analysis_or_hvo

        # Yield all glosses from the Meanings collection
        for gloss in analysis.MeaningsOC:
            yield gloss

    def Create(self, analysis_or_hvo, form, wsHandle=None):
        """
        Create a new gloss for a wordform analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO
            form: The gloss text (meaning/translation)
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            IWfiGloss: The newly created gloss object

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo or form is None
            FP_ParameterError: If form is empty or analysis doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     gloss = project.WfiGlosses.Create(analyses[0], "to run")
            ...     print(project.WfiGlosses.GetForm(gloss))
            to run
            >>> # Create with specific writing system
            >>> gloss_fr = project.WfiGlosses.Create(analyses[0], "courir", "fr")

        Notes:
            - New gloss is added to the analysis's Meanings collection
            - The form is stored in the specified writing system
            - Duplicate glosses are allowed (no uniqueness check)
            - Gloss is added at the end of the collection

        See Also:
            Delete, SetForm, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not analysis_or_hvo:
            raise FP_NullParameterError()
        if form is None:
            raise FP_NullParameterError()

        if not form or not form.strip():
            raise FP_ParameterError("Gloss form cannot be empty")

        # Resolve to analysis object
        if isinstance(analysis_or_hvo, int):
            analysis = self.project.Object(analysis_or_hvo)
            if not isinstance(analysis, IWfiAnalysis):
                raise FP_ParameterError("HVO does not refer to a wordform analysis")
        else:
            analysis = analysis_or_hvo

        wsHandle = self.__WSHandle(wsHandle)

        # Get the factory and create the gloss
        factory = self.project.project.ServiceLocator.GetInstance(IWfiGlossFactory)
        new_gloss = factory.Create()

        # Set the form
        mkstr = TsStringUtils.MakeString(form, wsHandle)
        new_gloss.Form.set_String(wsHandle, mkstr)

        # Add to analysis's Meanings collection
        analysis.MeaningsOC.Add(new_gloss)

        return new_gloss

    def Delete(self, gloss_or_hvo):
        """
        Delete a gloss from its owning analysis.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If gloss_or_hvo is None
            FP_ParameterError: If gloss doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     glosses = list(project.WfiGlosses.GetAll(analyses[0]))
            ...     if len(glosses) > 1:
            ...         # Delete the last gloss
            ...         project.WfiGlosses.Delete(glosses[-1])

        Warning:
            - This is a destructive operation
            - Deletion is permanent and cannot be undone
            - Consider backing up data before deletion
            - Text segments that reference this gloss may be affected

        See Also:
            Create, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not gloss_or_hvo:
            raise FP_NullParameterError()

        # Resolve to gloss object
        if isinstance(gloss_or_hvo, int):
            gloss = self.project.Object(gloss_or_hvo)
            if not isinstance(gloss, IWfiGloss):
                raise FP_ParameterError("HVO does not refer to a wordform gloss")
        else:
            gloss = gloss_or_hvo

        # Get the owning analysis
        analysis = gloss.Owner

        # Remove from analysis's Meanings collection
        if hasattr(analysis, 'MeaningsOC'):
            analysis.MeaningsOC.Remove(gloss)

    def Reorder(self, analysis_or_hvo, gloss_list):
        """
        Reorder glosses for a wordform analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO
            gloss_list: List of IWfiGloss objects or HVOs in desired order

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo or gloss_list is None
            FP_ParameterError: If gloss_list is empty or contains invalid glosses

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     glosses = list(project.WfiGlosses.GetAll(analyses[0]))
            ...     if len(glosses) > 1:
            ...         # Reverse the order
            ...         project.WfiGlosses.Reorder(analyses[0], reversed(glosses))
            ...         # Verify new order
            ...         for gloss in project.WfiGlosses.GetAll(analyses[0]):
            ...             print(project.WfiGlosses.GetForm(gloss))

        Notes:
            - All glosses in gloss_list must belong to the analysis
            - Any glosses not in gloss_list remain at the end in original order
            - Use this to prioritize glosses for display or selection

        See Also:
            GetAll, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not analysis_or_hvo:
            raise FP_NullParameterError()
        if gloss_list is None:
            raise FP_NullParameterError()

        if not gloss_list:
            raise FP_ParameterError("Gloss list cannot be empty")

        # Resolve to analysis object
        if isinstance(analysis_or_hvo, int):
            analysis = self.project.Object(analysis_or_hvo)
            if not isinstance(analysis, IWfiAnalysis):
                raise FP_ParameterError("HVO does not refer to a wordform analysis")
        else:
            analysis = analysis_or_hvo

        # Resolve HVOs to gloss objects
        resolved_glosses = []
        for gloss_or_hvo in gloss_list:
            if isinstance(gloss_or_hvo, int):
                gloss = self.project.Object(gloss_or_hvo)
                if not isinstance(gloss, IWfiGloss):
                    raise FP_ParameterError("HVO does not refer to a wordform gloss")
            else:
                gloss = gloss_or_hvo
            resolved_glosses.append(gloss)

        # Clear current glosses
        analysis.MeaningsOC.Clear()

        # Add in new order
        for gloss in resolved_glosses:
            analysis.MeaningsOC.Add(gloss)

    # --- Form Management Operations ---

    def GetForm(self, gloss_or_hvo, wsHandle=None):
        """
        Get the gloss text form.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The gloss text (empty string if not set)

        Raises:
            FP_NullParameterError: If gloss_or_hvo is None
            FP_ParameterError: If gloss doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     for gloss in project.WfiGlosses.GetAll(analyses[0]):
            ...         form = project.WfiGlosses.GetForm(gloss)
            ...         print(form)

        Notes:
            - Returns empty string if form not set in specified writing system
            - Default writing system is the default analysis WS
            - Gloss can have different forms in multiple writing systems

        See Also:
            SetForm, GetAllForms
        """
        if not gloss_or_hvo:
            raise FP_NullParameterError()

        # Resolve to gloss object
        if isinstance(gloss_or_hvo, int):
            gloss = self.project.Object(gloss_or_hvo)
            if not isinstance(gloss, IWfiGloss):
                raise FP_ParameterError("HVO does not refer to a wordform gloss")
        else:
            gloss = gloss_or_hvo

        wsHandle = self.__WSHandle(wsHandle)

        # Get the form string
        form = ITsString(gloss.Form.get_String(wsHandle)).Text
        return form or ""

    def SetForm(self, gloss_or_hvo, text, wsHandle=None):
        """
        Set the gloss text form.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO
            text: The new gloss text
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If gloss_or_hvo or text is None
            FP_ParameterError: If gloss doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     glosses = list(project.WfiGlosses.GetAll(analyses[0]))
            ...     if glosses:
            ...         project.WfiGlosses.SetForm(glosses[0], "to run quickly")
            ...         print(project.WfiGlosses.GetForm(glosses[0]))
            to run quickly
            >>> # Set form in multiple writing systems
            >>> project.WfiGlosses.SetForm(glosses[0], "courir", "fr")
            >>> project.WfiGlosses.SetForm(glosses[0], "correr", "es")

        Notes:
            - Empty string is allowed (clears the gloss in that writing system)
            - Gloss can be set independently in multiple writing systems
            - Use this to provide translations in different languages

        See Also:
            GetForm, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not gloss_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        # Resolve to gloss object
        if isinstance(gloss_or_hvo, int):
            gloss = self.project.Object(gloss_or_hvo)
            if not isinstance(gloss, IWfiGloss):
                raise FP_ParameterError("HVO does not refer to a wordform gloss")
        else:
            gloss = gloss_or_hvo

        wsHandle = self.__WSHandle(wsHandle)

        # Set the form string
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        gloss.Form.set_String(wsHandle, mkstr)

    def GetAllForms(self, gloss_or_hvo):
        """
        Get all available forms for a gloss across all writing systems.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO

        Returns:
            dict: Dictionary mapping writing system handles to form text

        Raises:
            FP_NullParameterError: If gloss_or_hvo is None
            FP_ParameterError: If gloss doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     glosses = list(project.WfiGlosses.GetAll(analyses[0]))
            ...     if glosses:
            ...         forms = project.WfiGlosses.GetAllForms(glosses[0])
            ...         for ws_handle, form in forms.items():
            ...             print(f"WS {ws_handle}: {form}")

        Notes:
            - Returns only writing systems where form is set
            - Dictionary keys are writing system handles (integers)
            - Use project.GetWritingSystemName(ws) to get WS names
            - Empty forms are excluded from results

        See Also:
            GetForm, SetForm
        """
        if not gloss_or_hvo:
            raise FP_NullParameterError()

        # Resolve to gloss object
        if isinstance(gloss_or_hvo, int):
            gloss = self.project.Object(gloss_or_hvo)
            if not isinstance(gloss, IWfiGloss):
                raise FP_ParameterError("HVO does not refer to a wordform gloss")
        else:
            gloss = gloss_or_hvo

        forms = {}
        # Iterate through available writing systems
        for ws in gloss.Form.AvailableWritingSystemIds:
            form_text = ITsString(gloss.Form.get_String(ws)).Text
            if form_text:
                forms[ws] = form_text

        return forms

    # --- Utility Operations ---

    def GetOwningAnalysis(self, gloss_or_hvo):
        """
        Get the wordform analysis that owns this gloss.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO

        Returns:
            IWfiAnalysis: The owning analysis object

        Raises:
            FP_NullParameterError: If gloss_or_hvo is None
            FP_ParameterError: If gloss doesn't exist

        Example:
            >>> # Find a gloss and get its owning analysis
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     glosses = list(project.WfiGlosses.GetAll(analyses[0]))
            ...     if glosses:
            ...         analysis = project.WfiGlosses.GetOwningAnalysis(glosses[0])
            ...         print(f"Analysis HVO: {analysis.Hvo}")

        Notes:
            - Gloss is owned by exactly one analysis
            - Use this to navigate from gloss back to analysis
            - Useful for accessing other analysis properties

        See Also:
            GetAll, GetGuid
        """
        if not gloss_or_hvo:
            raise FP_NullParameterError()

        # Resolve to gloss object
        if isinstance(gloss_or_hvo, int):
            gloss = self.project.Object(gloss_or_hvo)
            if not isinstance(gloss, IWfiGloss):
                raise FP_ParameterError("HVO does not refer to a wordform gloss")
        else:
            gloss = gloss_or_hvo

        return gloss.Owner

    def GetGuid(self, gloss_or_hvo):
        """
        Get the GUID (Global Unique Identifier) for a gloss.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO

        Returns:
            System.Guid: The GUID of the gloss

        Raises:
            FP_NullParameterError: If gloss_or_hvo is None
            FP_ParameterError: If gloss doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     glosses = list(project.WfiGlosses.GetAll(analyses[0]))
            ...     if glosses:
            ...         guid = project.WfiGlosses.GetGuid(glosses[0])
            ...         print(f"Gloss GUID: {guid}")

        Notes:
            - GUID is unique across all projects
            - GUID remains constant even if object moves
            - Useful for cross-referencing between projects
            - HVO is project-specific, GUID is universal

        See Also:
            GetOwningAnalysis, Find
        """
        if not gloss_or_hvo:
            raise FP_NullParameterError()

        # Resolve to gloss object
        if isinstance(gloss_or_hvo, int):
            gloss = self.project.Object(gloss_or_hvo)
            if not isinstance(gloss, IWfiGloss):
                raise FP_ParameterError("HVO does not refer to a wordform gloss")
        else:
            gloss = gloss_or_hvo

        return gloss.Guid

    def Find(self, analysis_or_hvo, form, wsHandle=None):
        """
        Find and return a gloss by its form text.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO
            form: The gloss text to find
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            IWfiGloss or None: The gloss object if found, None otherwise

        Raises:
            FP_NullParameterError: If analysis_or_hvo or form is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     gloss = project.WfiGlosses.Find(analyses[0], "to run")
            ...     if gloss:
            ...         print(f"Found gloss: {gloss.Hvo}")
            ...     else:
            ...         print("Gloss not found")

        Notes:
            - Search is case-sensitive
            - Search is writing-system specific
            - Returns None if gloss doesn't exist
            - Returns first match if multiple glosses have same form
            - Use Exists() for simple existence check

        See Also:
            Exists, GetAll, Create
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()
        if form is None:
            raise FP_NullParameterError()

        if not form or not form.strip():
            return None

        # Resolve to analysis object
        if isinstance(analysis_or_hvo, int):
            analysis = self.project.Object(analysis_or_hvo)
            if not isinstance(analysis, IWfiAnalysis):
                raise FP_ParameterError("HVO does not refer to a wordform analysis")
        else:
            analysis = analysis_or_hvo

        wsHandle = self.__WSHandle(wsHandle)

        # Search through all glosses
        for gloss in self.GetAll(analysis):
            gloss_form = ITsString(gloss.Form.get_String(wsHandle)).Text
            if gloss_form == form:
                return gloss

        return None

    def Exists(self, analysis_or_hvo, form, wsHandle=None):
        """
        Check if a gloss with the specified form exists for an analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO
            form: The gloss text to check
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            bool: True if the gloss exists, False otherwise

        Raises:
            FP_NullParameterError: If analysis_or_hvo or form is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     if project.WfiGlosses.Exists(analyses[0], "to run"):
            ...         gloss = project.WfiGlosses.Find(analyses[0], "to run")
            ...     else:
            ...         gloss = project.WfiGlosses.Create(analyses[0], "to run")

        Notes:
            - Search is case-sensitive
            - Search is writing-system specific
            - Returns False for empty or whitespace-only forms
            - More efficient than Find() when you only need existence check

        See Also:
            Find, Create
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()
        if form is None:
            raise FP_NullParameterError()

        if not form or not form.strip():
            return False

        return self.Find(analysis_or_hvo, form, wsHandle) is not None

    def GetCount(self, analysis_or_hvo):
        """
        Get the count of glosses for a wordform analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            int: Number of glosses

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     count = project.WfiGlosses.GetCount(analyses[0])
            ...     print(f"This analysis has {count} glosses")

        Notes:
            - More efficient than len(list(GetAll())) for counting
            - Returns 0 if analysis has no glosses
            - Each gloss may have forms in multiple writing systems

        See Also:
            GetAll, Create
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        # Resolve to analysis object
        if isinstance(analysis_or_hvo, int):
            analysis = self.project.Object(analysis_or_hvo)
            if not isinstance(analysis, IWfiAnalysis):
                raise FP_ParameterError("HVO does not refer to a wordform analysis")
        else:
            analysis = analysis_or_hvo

        return analysis.MeaningsOC.Count

    def GetBestForm(self, gloss_or_hvo):
        """
        Get the best available form for a gloss.

        This method attempts to find a suitable gloss form by checking writing
        systems in order of preference: default analysis WS, then any available WS.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO

        Returns:
            str: The best available gloss form (empty string if none found)

        Raises:
            FP_NullParameterError: If gloss_or_hvo is None
            FP_ParameterError: If gloss doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     for gloss in project.WfiGlosses.GetAll(analyses[0]):
            ...         best = project.WfiGlosses.GetBestForm(gloss)
            ...         print(f"Best form: {best}")

        Notes:
            - Tries default analysis WS first
            - Falls back to first available WS if default not set
            - Returns empty string if no forms are set
            - Useful when you need any available form

        See Also:
            GetForm, GetAllForms
        """
        if not gloss_or_hvo:
            raise FP_NullParameterError()

        # Resolve to gloss object
        if isinstance(gloss_or_hvo, int):
            gloss = self.project.Object(gloss_or_hvo)
            if not isinstance(gloss, IWfiGloss):
                raise FP_ParameterError("HVO does not refer to a wordform gloss")
        else:
            gloss = gloss_or_hvo

        # Try default analysis WS first
        default_ws = self.project.project.DefaultAnalWs
        best_form = ITsString(gloss.Form.get_String(default_ws)).Text
        if best_form:
            return best_form

        # Try any available writing system
        for ws in gloss.Form.AvailableWritingSystemIds:
            form_text = ITsString(gloss.Form.get_String(ws)).Text
            if form_text:
                return form_text

        return ""

    def CopyGloss(self, gloss_or_hvo, target_analysis_or_hvo):
        """
        Copy a gloss to another analysis.

        Creates a new gloss in the target analysis with all forms from the source gloss.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO (source)
            target_analysis_or_hvo: Either an IWfiAnalysis object or its HVO (target)

        Returns:
            IWfiGloss: The newly created gloss in the target analysis

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If gloss_or_hvo or target_analysis_or_hvo is None
            FP_ParameterError: If gloss or analysis doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if len(analyses) > 1:
            ...     glosses = list(project.WfiGlosses.GetAll(analyses[0]))
            ...     if glosses:
            ...         # Copy first gloss from first analysis to second
            ...         new_gloss = project.WfiGlosses.CopyGloss(glosses[0], analyses[1])
            ...         print(f"Copied gloss: {project.WfiGlosses.GetForm(new_gloss)}")

        Notes:
            - Copies all writing system forms from source to target
            - Creates a new gloss object (not a reference)
            - Useful for sharing glosses between analyses

        See Also:
            Create, GetAllForms
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not gloss_or_hvo:
            raise FP_NullParameterError()
        if not target_analysis_or_hvo:
            raise FP_NullParameterError()

        # Resolve to gloss object
        if isinstance(gloss_or_hvo, int):
            source_gloss = self.project.Object(gloss_or_hvo)
            if not isinstance(source_gloss, IWfiGloss):
                raise FP_ParameterError("HVO does not refer to a wordform gloss")
        else:
            source_gloss = gloss_or_hvo

        # Resolve to target analysis object
        if isinstance(target_analysis_or_hvo, int):
            target_analysis = self.project.Object(target_analysis_or_hvo)
            if not isinstance(target_analysis, IWfiAnalysis):
                raise FP_ParameterError("HVO does not refer to a wordform analysis")
        else:
            target_analysis = target_analysis_or_hvo

        # Create new gloss
        factory = self.project.project.ServiceLocator.GetInstance(IWfiGlossFactory)
        new_gloss = factory.Create()

        # Copy all forms
        for ws in source_gloss.Form.AvailableWritingSystemIds:
            form_text = ITsString(source_gloss.Form.get_String(ws)).Text
            if form_text:
                mkstr = TsStringUtils.MakeString(form_text, ws)
                new_gloss.Form.set_String(ws, mkstr)

        # Add to target analysis
        target_analysis.MeaningsOC.Add(new_gloss)

        return new_gloss

    def ClearForm(self, gloss_or_hvo, wsHandle=None):
        """
        Clear the form for a gloss in a specific writing system.

        Args:
            gloss_or_hvo: Either an IWfiGloss object or its HVO
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If gloss_or_hvo is None
            FP_ParameterError: If gloss doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.Wordforms.GetAnalyses(wf)
            >>> if analyses:
            ...     glosses = list(project.WfiGlosses.GetAll(analyses[0]))
            ...     if glosses:
            ...         # Clear the English form
            ...         project.WfiGlosses.ClearForm(glosses[0], "en")

        Notes:
            - Only clears the form in the specified writing system
            - Forms in other writing systems are not affected
            - Equivalent to SetForm(gloss, "", ws)
            - Gloss object itself is not deleted

        See Also:
            SetForm, Delete
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not gloss_or_hvo:
            raise FP_NullParameterError()

        self.SetForm(gloss_or_hvo, "", wsHandle)
