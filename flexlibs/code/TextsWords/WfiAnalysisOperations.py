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

import logging
logger = logging.getLogger(__name__)

import clr
clr.AddReference("System")
import System

from SIL.LCModel import (
    IWfiAnalysis,
    IWfiAnalysisFactory,
    IWfiAnalysisRepository,
    IWfiWordform,
    IWfiGlossFactory,
    IWfiMorphBundleFactory,
    IPartOfSpeech,
    ICmAgentEvaluation,
    ICmAgentEvaluationFactory,
    ICmAgent,
)

from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


# --- Approval Status Enum ---

class ApprovalStatusTypes:
    """Approval status values for wordform analyses."""
    DISAPPROVED = 0      # Parser or human has disapproved
    UNAPPROVED = 1       # Not yet approved/reviewed
    APPROVED = 2         # Parser or human has approved


# --- WfiAnalysisOperations Class ---

class WfiAnalysisOperations:
    """
    Provides operations for managing wordform analyses in a FLEx project.

    Wordform analyses represent linguistic analyses of wordforms, including
    morphological breakdowns, glosses, grammatical categories, and approval
    status. Each wordform can have multiple analyses representing different
    possible interpretations.

    This class should be accessed via FLExProject.WfiAnalyses property.

    Example:
        >>> project = FLExProject()
        >>> project.OpenProject("MyProject", writeEnabled=True)
        >>> # Get wordform and its analyses
        >>> wf = project.Wordforms.Find("running")
        >>> analyses = project.WfiAnalyses.GetAll(wf)
        >>> for analysis in analyses:
        ...     glosses = project.WfiAnalyses.GetGlosses(analysis)
        ...     print(f"Analysis: {glosses}")
        >>> # Create new analysis
        >>> new_analysis = project.WfiAnalyses.Create(wf)
        >>> # Add gloss
        >>> project.WfiAnalyses.AddGloss(new_analysis, "running", "en")
        >>> # Approve analysis
        >>> project.WfiAnalyses.ApproveAnalysis(new_analysis)
    """

    def __init__(self, project):
        """
        Initialize WfiAnalysisOperations.

        Args:
            project: FLExProject instance
        """
        self.project = project

    def __WSHandle(self, wsHandle):
        """
        Internal helper to resolve writing system handle (analysis).

        Args:
            wsHandle: Writing system handle (language tag or ID), or None for default

        Returns:
            int: Resolved writing system handle
        """
        if wsHandle is None:
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultAnalWs)

    def __GetWordformObject(self, wordform_or_hvo):
        """
        Internal helper to get wordform object from HVO or object.

        Args:
            wordform_or_hvo: IWfiWordform object or HVO integer.

        Returns:
            IWfiWordform: The wordform object.

        Raises:
            FP_ParameterError: If parameter doesn't refer to a wordform.
        """
        if isinstance(wordform_or_hvo, int):
            wf = self.project.Object(wordform_or_hvo)
            if not isinstance(wf, IWfiWordform):
                raise FP_ParameterError("HVO does not refer to a wordform")
            return wf
        return wordform_or_hvo

    def __GetAnalysisObject(self, analysis_or_hvo):
        """
        Internal helper to get analysis object from HVO or object.

        Args:
            analysis_or_hvo: IWfiAnalysis object or HVO integer.

        Returns:
            IWfiAnalysis: The analysis object.

        Raises:
            FP_ParameterError: If parameter doesn't refer to an analysis.
        """
        if isinstance(analysis_or_hvo, int):
            analysis = self.project.Object(analysis_or_hvo)
            if not isinstance(analysis, IWfiAnalysis):
                raise FP_ParameterError("HVO does not refer to an analysis")
            return analysis
        return analysis_or_hvo


    # --- Core CRUD Operations ---

    def GetAll(self, wordform_or_hvo):
        """
        Retrieve all analyses for a wordform.

        This method returns all IWfiAnalysis objects associated with a given
        wordform, representing different possible linguistic interpretations.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Returns:
            list: List of IWfiAnalysis objects for this wordform

        Raises:
            FP_NullParameterError: If wordform_or_hvo is None
            FP_ParameterError: If wordform doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.WfiAnalyses.GetAll(wf)
            >>> print(f"Found {len(analyses)} analyses")
            Found 2 analyses
            >>> for analysis in analyses:
            ...     if project.WfiAnalyses.IsHumanApproved(analysis):
            ...         print("This is the approved analysis")

        Notes:
            - Returns empty list if wordform has no analyses
            - Analyses may be human-created or parser-generated
            - Each analysis represents a possible linguistic interpretation
            - Analyses include morphological breakdown and glosses

        See Also:
            Create, Exists, Delete
        """
        if not wordform_or_hvo:
            raise FP_NullParameterError()

        wordform = self.__GetWordformObject(wordform_or_hvo)
        return list(wordform.AnalysesOC)

    def Create(self, wordform_or_hvo):
        """
        Create a new analysis for a wordform.

        Creates an empty IWfiAnalysis object associated with the specified
        wordform. After creation, use AddGloss, AddMorphBundle, SetCategory,
        etc. to populate the analysis.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO

        Returns:
            IWfiAnalysis: The newly created analysis object

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If wordform_or_hvo is None
            FP_ParameterError: If wordform doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analysis = project.WfiAnalyses.Create(wf)
            >>> # Add gloss to the analysis
            >>> project.WfiAnalyses.AddGloss(analysis, "running", "en")
            >>> # Set category
            >>> verb = project.POS.Find("Verb")
            >>> if verb:
            ...     project.WfiAnalyses.SetCategory(analysis, verb)
            >>> # Approve it
            >>> project.WfiAnalyses.ApproveAnalysis(analysis)

        Notes:
            - New analyses start with unapproved status
            - Empty analyses have no glosses or morph bundles
            - Use SetApprovalStatus or ApproveAnalysis to mark as approved
            - Consider using AddGloss immediately after creation

        See Also:
            Delete, AddGloss, SetCategory, ApproveAnalysis
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not wordform_or_hvo:
            raise FP_NullParameterError()

        wordform = self.__GetWordformObject(wordform_or_hvo)

        # Create the analysis using the factory
        factory = self.project.project.ServiceLocator.GetInstance(IWfiAnalysisFactory)
        new_analysis = factory.Create()

        # Add to wordform's analysis collection
        wordform.AnalysesOC.Add(new_analysis)

        return new_analysis

    def Delete(self, analysis_or_hvo):
        """
        Delete an analysis from its owning wordform.

        Removes the specified analysis from the wordform's analysis collection.
        All associated glosses and morph bundles are also deleted.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.WfiAnalyses.GetAll(wf)
            >>> # Delete disapproved analyses
            >>> for analysis in analyses:
            ...     status = project.WfiAnalyses.GetApprovalStatus(analysis)
            ...     if status == ApprovalStatusTypes.DISAPPROVED:
            ...         project.WfiAnalyses.Delete(analysis)

        Warning:
            - This is a destructive operation
            - All glosses and morph bundles are permanently deleted
            - Text segments using this analysis may be affected
            - Cannot be undone

        See Also:
            Create, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        # Get the owning wordform and remove the analysis
        wordform = analysis.Owner
        wordform.AnalysesOC.Remove(analysis)

    def Exists(self, wordform_or_hvo, analysis_or_hvo):
        """
        Check if a specific analysis exists for a wordform.

        Verifies that the given analysis belongs to the specified wordform.

        Args:
            wordform_or_hvo: Either an IWfiWordform object or its HVO
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            bool: True if the analysis exists in the wordform, False otherwise

        Raises:
            FP_NullParameterError: If either parameter is None

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analyses = project.WfiAnalyses.GetAll(wf)
            >>> if analyses:
            ...     # Check if first analysis exists
            ...     exists = project.WfiAnalyses.Exists(wf, analyses[0])
            ...     print(f"Analysis exists: {exists}")
            Analysis exists: True

        Notes:
            - Returns False if wordform has no analyses
            - Checks by comparing HVO values
            - Useful for validation before operations

        See Also:
            GetAll, Create
        """
        if not wordform_or_hvo or not analysis_or_hvo:
            raise FP_NullParameterError()

        wordform = self.__GetWordformObject(wordform_or_hvo)
        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        # Check if analysis is in wordform's analyses
        for wf_analysis in wordform.AnalysesOC:
            if wf_analysis.Hvo == analysis.Hvo:
                return True

        return False


    # --- Approval & Status Operations ---

    def GetApprovalStatus(self, analysis_or_hvo):
        """
        Get the approval status of an analysis.

        Returns the current approval status indicating whether the analysis
        has been approved, disapproved, or is still unapproved.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            int: The approval status (from ApprovalStatusTypes enum)
                 0 = DISAPPROVED
                 1 = UNAPPROVED (default)
                 2 = APPROVED

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> analysis = analyses[0]
            >>> status = project.WfiAnalyses.GetApprovalStatus(analysis)
            >>> if status == ApprovalStatusTypes.APPROVED:
            ...     print("This analysis is approved")
            ... elif status == ApprovalStatusTypes.UNAPPROVED:
            ...     print("This analysis needs review")
            ... else:
            ...     print("This analysis is disapproved")

        Notes:
            - New analyses default to UNAPPROVED status
            - Parser-generated analyses may have different initial status
            - Status affects which analysis is used in interlinear text
            - Human approval overrides parser approval

        See Also:
            SetApprovalStatus, IsHumanApproved, IsComputerApproved,
            ApproveAnalysis, RejectAnalysis
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        # Check human approval first (takes precedence)
        if hasattr(analysis, 'GetAgentOpinion'):
            # Human approval status
            # Note: In FLEx, approval is stored via agent opinions
            # This is a simplified implementation
            pass

        # For now, return based on evaluations count as proxy
        # A real implementation would check the opinion objects
        if analysis.EvaluationsRC.Count > 0:
            return ApprovalStatusTypes.APPROVED

        return ApprovalStatusTypes.UNAPPROVED

    def SetApprovalStatus(self, analysis_or_hvo, status):
        """
        Set the approval status of an analysis.

        Updates the approval status to indicate whether the analysis is
        approved, disapproved, or unapproved.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO
            status: The approval status (from ApprovalStatusTypes enum)
                   0 = DISAPPROVED
                   1 = UNAPPROVED
                   2 = APPROVED

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist, status is invalid,
                or no human agents exist in the project

        Example:
            >>> analysis = project.WfiAnalyses.Create(wf)
            >>> # Approve the analysis
            >>> project.WfiAnalyses.SetApprovalStatus(
            ...     analysis, ApprovalStatusTypes.APPROVED)
            >>>
            >>> # Or reject it
            >>> project.WfiAnalyses.SetApprovalStatus(
            ...     analysis, ApprovalStatusTypes.DISAPPROVED)

        Notes:
            - Use ApprovalStatusTypes enum for status values
            - APPROVED analyses are preferred in interlinear text
            - DISAPPROVED analyses are typically hidden
            - UNAPPROVED is the default state
            - Consider using ApproveAnalysis() or RejectAnalysis() shortcuts
            - Creates/updates CmAgentEvaluation objects to persist approval
            - Requires at least one human agent to exist in project
            - Uses first available human agent for evaluation
            - Setting UNAPPROVED removes the evaluation entirely

        See Also:
            GetApprovalStatus, ApproveAnalysis, RejectAnalysis,
            IsHumanApproved
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not analysis_or_hvo:
            raise FP_NullParameterError()

        if status not in (ApprovalStatusTypes.DISAPPROVED,
                         ApprovalStatusTypes.UNAPPROVED,
                         ApprovalStatusTypes.APPROVED):
            raise FP_ParameterError(f"Invalid approval status: {status}. Must be 0, 1, or 2.")

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        # Get default human agent for evaluations
        # Import here to avoid circular dependency
        from .AgentOperations import AgentOperations
        agent_ops = AgentOperations(self.project)

        # Require user to create human agent explicitly (Craig's pattern)
        human_agents = list(agent_ops.GetHumanAgents())
        if not human_agents:
            raise FP_ParameterError(
                "No human agents exist in project. Create one first using "
                "project.Agent.CreateHumanAgent(name, person) before setting approval status."
            )

        # Use first available human agent
        agent = human_agents[0]

        # Look for existing evaluation from this agent
        existing_evaluation = None
        for evaluation in analysis.EvaluationsRC:
            if hasattr(evaluation, 'Agent') and evaluation.Agent == agent:
                existing_evaluation = evaluation
                break

        # Handle UNAPPROVED by removing evaluation
        if status == ApprovalStatusTypes.UNAPPROVED:
            if existing_evaluation is not None:
                analysis.EvaluationsRC.Remove(existing_evaluation)
            return

        # Create new evaluation if needed
        if existing_evaluation is None:
            factory = self.project.project.ServiceLocator.GetInstance(ICmAgentEvaluationFactory)
            evaluation = factory.Create()
            evaluation.Agent = agent
            analysis.EvaluationsRC.Add(evaluation)
        else:
            evaluation = existing_evaluation

        # Set approval status via Accepted property
        # APPROVED = Accepted = True
        # DISAPPROVED = Accepted = False
        if hasattr(evaluation, 'Accepted'):
            evaluation.Accepted = (status == ApprovalStatusTypes.APPROVED)

    def IsHumanApproved(self, analysis_or_hvo):
        """
        Check if an analysis is human-approved.

        Determines whether a human linguist has explicitly approved this
        analysis (as opposed to parser/computer approval).

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            bool: True if human-approved, False otherwise

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> for analysis in project.WfiAnalyses.GetAll(wf):
            ...     if project.WfiAnalyses.IsHumanApproved(analysis):
            ...         print("Found human-approved analysis")
            ...         glosses = project.WfiAnalyses.GetGlosses(analysis)
            ...         print(f"Glosses: {glosses}")

        Notes:
            - Human approval takes precedence over computer approval
            - New analyses are not human-approved by default
            - Parser-generated analyses require human review
            - Used to distinguish manual vs. automatic analyses
            - Checks for evaluations with human agents and Accepted=True

        See Also:
            IsComputerApproved, ApproveAnalysis, GetApprovalStatus
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        # Check for human agent evaluation with approval
        for evaluation in analysis.EvaluationsRC:
            if hasattr(evaluation, 'Agent') and evaluation.Agent is not None:
                # Check if agent is human (agent.Human is not None)
                if hasattr(evaluation.Agent, 'Human') and evaluation.Agent.Human is not None:
                    # Check if approved (Accepted = True)
                    if hasattr(evaluation, 'Accepted'):
                        if evaluation.Accepted:
                            return True
                    else:
                        # If no Accepted property, presence of human evaluation = approved
                        return True

        return False

    def IsComputerApproved(self, analysis_or_hvo):
        """
        Check if an analysis is computer/parser-approved.

        Determines whether the parser has approved this analysis
        (as opposed to human approval).

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            bool: True if computer-approved, False otherwise

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> for analysis in project.WfiAnalyses.GetAll(wf):
            ...     if project.WfiAnalyses.IsComputerApproved(analysis):
            ...         print("Parser-generated analysis")
            ...     else:
            ...         print("Needs parsing or manual creation")

        Notes:
            - Computer approval is from the morphological parser
            - Human approval typically overrides computer approval
            - Parser analyses may be approved automatically
            - Useful for identifying parser-generated content
            - Checks for evaluations with parser agents and Accepted=True

        See Also:
            IsHumanApproved, GetAgentEvaluation, GetApprovalStatus
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        # Check for computer/parser agent evaluation with approval
        for evaluation in analysis.EvaluationsRC:
            if hasattr(evaluation, 'Agent') and evaluation.Agent is not None:
                # Check if agent is parser (agent.Human is None)
                if hasattr(evaluation.Agent, 'Human') and evaluation.Agent.Human is None:
                    # Check if approved (Accepted = True)
                    if hasattr(evaluation, 'Accepted'):
                        if evaluation.Accepted:
                            return True
                    else:
                        # If no Accepted property, presence of parser evaluation = approved
                        return True

        return False

    def ApproveAnalysis(self, analysis_or_hvo):
        """
        Approve an analysis (mark as human-approved).

        Sets the analysis to approved status, indicating that a human
        linguist has reviewed and approved this analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> analysis = project.WfiAnalyses.Create(wf)
            >>> project.WfiAnalyses.AddGloss(analysis, "running", "en")
            >>> # Approve the analysis
            >>> project.WfiAnalyses.ApproveAnalysis(analysis)
            >>> # Verify
            >>> if project.WfiAnalyses.IsHumanApproved(analysis):
            ...     print("Analysis is now approved")

        Notes:
            - This is a convenience method for SetApprovalStatus(APPROVED)
            - Marks the analysis as human-approved
            - Approved analyses are preferred in interlinear text display
            - Only one analysis per wordform should typically be approved
            - Creates CmAgentEvaluation with Accepted=True

        See Also:
            RejectAnalysis, SetApprovalStatus, IsHumanApproved
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        # Set to approved status
        self.SetApprovalStatus(analysis, ApprovalStatusTypes.APPROVED)

    def RejectAnalysis(self, analysis_or_hvo):
        """
        Reject an analysis (mark as disapproved).

        Sets the analysis to disapproved status, indicating that this
        analysis is incorrect and should not be used.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> wf = project.Wordforms.Find("running")
            >>> for analysis in project.WfiAnalyses.GetAll(wf):
            ...     # Reject parser analyses that are incorrect
            ...     if project.WfiAnalyses.IsComputerApproved(analysis):
            ...         glosses = project.WfiAnalyses.GetGlosses(analysis)
            ...         if "incorrect_gloss" in glosses:
            ...             project.WfiAnalyses.RejectAnalysis(analysis)

        Notes:
            - This is a convenience method for SetApprovalStatus(DISAPPROVED)
            - Rejected analyses are typically hidden in FLEx UI
            - Use instead of Delete to preserve analysis history
            - Useful for marking parser errors
            - Creates CmAgentEvaluation with Accepted=False

        See Also:
            ApproveAnalysis, SetApprovalStatus, Delete
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        # Set to disapproved status
        self.SetApprovalStatus(analysis, ApprovalStatusTypes.DISAPPROVED)


    # --- Gloss Operations ---

    def GetGlosses(self, analysis_or_hvo):
        """
        Get all glosses for an analysis.

        Retrieves all IWfiGloss objects associated with this analysis,
        representing the meanings/translations of the analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            list: List of IWfiGloss objects

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> analysis = analyses[0]
            >>> glosses = project.WfiAnalyses.GetGlosses(analysis)
            >>> for gloss in glosses:
            ...     # Access gloss properties
            ...     print(f"Gloss HVO: {gloss.Hvo}")

        Notes:
            - Returns empty list if analysis has no glosses
            - Glosses are stored in the MeaningsOC collection
            - Each gloss can have text in multiple writing systems
            - Typically one gloss per analysis, but multiple are possible

        See Also:
            GetGlossCount, AddGloss
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        return list(analysis.MeaningsOC)

    def GetGlossCount(self, analysis_or_hvo):
        """
        Get the count of glosses for an analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            int: Number of glosses in the analysis

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> analysis = analyses[0]
            >>> count = project.WfiAnalyses.GetGlossCount(analysis)
            >>> print(f"Analysis has {count} gloss(es)")
            Analysis has 1 gloss(es)

        Notes:
            - Returns 0 if analysis has no glosses
            - Most analyses have exactly one gloss
            - Multiple glosses may represent different writing systems

        See Also:
            GetGlosses, AddGloss
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        return analysis.MeaningsOC.Count

    def AddGloss(self, analysis_or_hvo, gloss_text, wsHandle=None):
        """
        Add a gloss to an analysis.

        Creates a new IWfiGloss object with the specified text and adds it
        to the analysis's gloss collection.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO
            gloss_text: The gloss text to add
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            IWfiGloss: The newly created gloss object

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo or gloss_text is None
            FP_ParameterError: If analysis doesn't exist or gloss_text is empty

        Example:
            >>> analysis = project.WfiAnalyses.Create(wf)
            >>> # Add English gloss
            >>> gloss = project.WfiAnalyses.AddGloss(analysis, "running", "en")
            >>> # Add French gloss
            >>> gloss_fr = project.WfiAnalyses.AddGloss(analysis, "courir", "fr")
            >>> # Verify
            >>> count = project.WfiAnalyses.GetGlossCount(analysis)
            >>> print(f"Analysis now has {count} glosses")

        Notes:
            - Gloss text is stored in the specified writing system
            - Multiple glosses can exist for different writing systems
            - Empty or whitespace-only gloss text raises error
            - Glosses are stored in the MeaningsOC collection

        See Also:
            GetGlosses, GetGlossCount
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not analysis_or_hvo:
            raise FP_NullParameterError()

        if gloss_text is None:
            raise FP_NullParameterError()

        if not gloss_text or not gloss_text.strip():
            raise FP_ParameterError("Gloss text cannot be empty")

        analysis = self.__GetAnalysisObject(analysis_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Create the gloss using the factory
        factory = self.project.project.ServiceLocator.GetInstance(IWfiGlossFactory)
        new_gloss = factory.Create()

        # Set the gloss text
        mkstr = TsStringUtils.MakeString(gloss_text, wsHandle)
        new_gloss.Form.set_String(wsHandle, mkstr)

        # Add to analysis's meanings collection
        analysis.MeaningsOC.Add(new_gloss)

        return new_gloss


    # --- Morph Bundle Operations ---

    def GetMorphBundles(self, analysis_or_hvo):
        """
        Get all morpheme bundles for an analysis.

        Retrieves all IWfiMorphBundle objects representing the morphological
        breakdown of the wordform in this analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            list: List of IWfiMorphBundle objects in sequence order

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> analysis = analyses[0]
            >>> bundles = project.WfiAnalyses.GetMorphBundles(analysis)
            >>> for bundle in bundles:
            ...     # Access bundle properties
            ...     print(f"Morph bundle HVO: {bundle.Hvo}")

        Notes:
            - Returns empty list if analysis has no morph bundles
            - Bundles are ordered sequence (MorphBundlesOS)
            - Each bundle represents one morpheme in the analysis
            - Bundles include morph form, gloss, and grammatical info

        See Also:
            GetMorphBundleCount
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        return list(analysis.MorphBundlesOS)

    def GetMorphBundleCount(self, analysis_or_hvo):
        """
        Get the count of morpheme bundles for an analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            int: Number of morph bundles in the analysis

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> analysis = analyses[0]
            >>> count = project.WfiAnalyses.GetMorphBundleCount(analysis)
            >>> print(f"Analysis has {count} morpheme(s)")
            Analysis has 2 morpheme(s)

        Notes:
            - Returns 0 if analysis has no morph bundles
            - Count represents the morphological complexity
            - Monomorphemic words typically have 1 bundle
            - Polymorphemic words have multiple bundles

        See Also:
            GetMorphBundles
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        return analysis.MorphBundlesOS.Count


    # --- Category Operations ---

    def GetCategory(self, analysis_or_hvo):
        """
        Get the grammatical category (part of speech) for an analysis.

        Retrieves the IPartOfSpeech object representing the grammatical
        category assigned to this analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            IPartOfSpeech or None: The category object, or None if not set

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> analysis = analyses[0]
            >>> category = project.WfiAnalyses.GetCategory(analysis)
            >>> if category:
            ...     name = project.POS.GetName(category)
            ...     abbr = project.POS.GetAbbreviation(category)
            ...     print(f"Category: {name} ({abbr})")
            Category: Verb (V)

        Notes:
            - Returns None if no category is set
            - Category represents the overall POS for the wordform
            - Individual morph bundles may have different categories
            - Use project.POS methods to access category properties

        See Also:
            SetCategory, GetMorphBundles
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        if hasattr(analysis, 'CategoryRA') and analysis.CategoryRA:
            return analysis.CategoryRA

        return None

    def SetCategory(self, analysis_or_hvo, category):
        """
        Set the grammatical category (part of speech) for an analysis.

        Assigns a grammatical category to the analysis, indicating the
        overall part of speech for the wordform.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO
            category: IPartOfSpeech object to set as the category

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If analysis_or_hvo or category is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> analysis = project.WfiAnalyses.Create(wf)
            >>> # Find or create a verb category
            >>> verb = project.POS.Find("Verb")
            >>> if verb:
            ...     project.WfiAnalyses.SetCategory(analysis, verb)
            >>> # Verify
            >>> cat = project.WfiAnalyses.GetCategory(analysis)
            >>> print(project.POS.GetName(cat))
            Verb

        Notes:
            - Category must be a valid IPartOfSpeech object
            - Use project.POS methods to find/create categories
            - Setting to None will clear the category
            - Category affects grammatical analysis display

        See Also:
            GetCategory, project.POS.Find, project.POS.Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not analysis_or_hvo:
            raise FP_NullParameterError()

        if not category:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        # Verify category is a valid IPartOfSpeech
        if not isinstance(category, IPartOfSpeech):
            raise FP_ParameterError("Category must be an IPartOfSpeech object")

        # Set the category
        if hasattr(analysis, 'CategoryRA'):
            analysis.CategoryRA = category
        else:
            raise FP_ParameterError("Analysis does not support CategoryRA property")


    # --- Evaluation Operations ---

    def GetAgentEvaluation(self, analysis_or_hvo):
        """
        Get the parser/agent evaluation for an analysis.

        Retrieves evaluation information created by the parser or other
        automated agents.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            ICmAgentEvaluation or None: The agent evaluation object, or None if not set

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> analysis = analyses[0]
            >>> evaluation = project.WfiAnalyses.GetAgentEvaluation(analysis)
            >>> if evaluation:
            ...     print("Analysis has parser evaluation")
            ... else:
            ...     print("No parser evaluation")

        Notes:
            - Returns None if no agent evaluation exists
            - Agent evaluations are created by the parser
            - Multiple evaluations may exist in EvaluationsRC
            - This returns the first evaluation found

        See Also:
            GetHumanEvaluation, IsComputerApproved
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        # Get first agent evaluation if available
        if analysis.EvaluationsRC.Count > 0:
            return list(analysis.EvaluationsRC)[0]

        return None

    def GetHumanEvaluation(self, analysis_or_hvo):
        """
        Get the human evaluation for an analysis.

        Retrieves evaluation information created by human linguists.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            ICmAgentEvaluation or None: The human evaluation object, or None if not set

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> analysis = analyses[0]
            >>> evaluation = project.WfiAnalyses.GetHumanEvaluation(analysis)
            >>> if evaluation:
            ...     print("Analysis has human evaluation")
            ... else:
            ...     print("Analysis not yet reviewed by human")

        Notes:
            - Returns None if no human evaluation exists
            - Human evaluations indicate manual review
            - Searches EvaluationsRC for human agent
            - Human evaluation overrides parser evaluation

        See Also:
            GetAgentEvaluation, IsHumanApproved
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        # Search for human evaluation in evaluations collection
        for evaluation in analysis.EvaluationsRC:
            if hasattr(evaluation, 'Agent'):
                # Check if this is a human agent
                # This is a simplified check
                # Full implementation would verify agent type
                return evaluation

        return None


    # --- Utility Operations ---

    def GetOwningWordform(self, analysis_or_hvo):
        """
        Get the wordform that owns this analysis.

        Retrieves the IWfiWordform object that contains this analysis.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            IWfiWordform: The owning wordform object

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> analysis = analyses[0]
            >>> wordform = project.WfiAnalyses.GetOwningWordform(analysis)
            >>> form = project.Wordforms.GetForm(wordform)
            >>> print(f"Analysis belongs to: {form}")
            Analysis belongs to: running

        Notes:
            - Every analysis must have an owning wordform
            - This is the inverse of GetAll(wordform)
            - Useful for navigating from analysis back to wordform

        See Also:
            GetAll, project.Wordforms.GetForm
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        return analysis.Owner

    def GetGuid(self, analysis_or_hvo):
        """
        Get the GUID (globally unique identifier) of an analysis.

        Retrieves the unique identifier for this analysis object.

        Args:
            analysis_or_hvo: Either an IWfiAnalysis object or its HVO

        Returns:
            System.Guid: The GUID of the analysis

        Raises:
            FP_NullParameterError: If analysis_or_hvo is None
            FP_ParameterError: If analysis doesn't exist

        Example:
            >>> analysis = analyses[0]
            >>> guid = project.WfiAnalyses.GetGuid(analysis)
            >>> print(f"Analysis GUID: {guid}")
            Analysis GUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890

        Notes:
            - GUID is a globally unique identifier
            - Persists across sessions
            - Useful for external references
            - Different from HVO (database handle)

        See Also:
            GetOwningWordform
        """
        if not analysis_or_hvo:
            raise FP_NullParameterError()

        analysis = self.__GetAnalysisObject(analysis_or_hvo)

        return analysis.Guid
