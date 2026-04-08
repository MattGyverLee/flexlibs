#
#   AgentOperations.py
#
#   Class: AgentOperations
#          Agent operations for managing analysis agents (parsers, human analysts)
#          in FieldWorks Language Explorer projects via SIL Language and Culture
#          Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

# Import FLEx LCM types
from SIL.LCModel import (
    ICmAgent,
    ICmAgentFactory,
    ICmPerson,
    ICmAgentEvaluation,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils
import System

# Import flexlibs exceptions
from ..FLExProject import FP_ParameterError
from ..BaseOperations import OperationsMethod
from .possibility_item_base import PossibilityItemOperations


class AgentOperations(PossibilityItemOperations):
    """
    Agent operations for managing human analysts and automated parsers.

    Agents represent either human analysts or automated parsers that perform
    linguistic analysis. They track who (or what) created analyses, glosses,
    and evaluations in the project.

    Inherited CRUD Operations (from PossibilityItemOperations):
    - GetAll() - Get all agents
    - Create() - Create new agent
    - Delete() - Delete agent
    - Duplicate() - Clone agent
    - Find() - Find by name
    - Exists() - Check existence
    - GetName() / SetName() - Get/set name
    - GetDescription() / SetDescription() - Get/set description
    - GetGuid() - Get GUID
    - CompareTo() - Compare by name

    Domain-Specific Methods (AgentOperations):
    - CreateHumanAgent() - Create human agent linked to person
    - CreateParserAgent() - Create parser agent with version
    - GetVersion() / SetVersion() - Get/set parser version
    - IsHuman() / IsParser() - Check agent type
    - GetHuman() / SetHuman() - Link to ICmPerson
    - GetEvaluations() / GetEvaluationCount() - Get evaluations
    - FindByType() - Find by agent type
    - GetHumanAgents() / GetParserAgents() - Get all of type
    - GetDateCreated() / GetDateModified() - Get timestamps
    """

    def __init__(self, project):
        """
        Initialize AgentOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)

    def _get_item_class_name(self):
        """Get the item class name for error messages."""
        return "Agent"

    def _get_list_object(self):
        """Get the agents list container."""
        return self.project.lp.AnalyzingAgentsOC

    # --- Version and Type Management ---

    @OperationsMethod
    def GetVersion(self, agent_or_hvo, wsHandle=None):
        """
        Get the version string of an agent.

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The agent's version string (empty string if not set)

        Raises:
            FP_NullParameterError: If agent_or_hvo is None

        Example:
            >>> parser = project.Agent.Find("MyParser")
            >>> version = project.Agent.GetVersion(parser)
            >>> print(f"Version: {version}")
            Version: 1.0.0

            >>> # Human agents typically don't have versions
            >>> human = project.Agent.Find("John Smith")
            >>> version = project.Agent.GetVersion(human)
            >>> print(version)

        Notes:
            - Returns empty string if version not set
            - Typically used for parser agents
            - Human agents usually don't have version numbers
            - Can use any version format (e.g., "1.0", "2.1.3", "v3-beta")

        See Also:
            SetVersion, CreateParserAgent
        """
        self._ValidateParam(agent_or_hvo, "agent_or_hvo")

        agent = self._PossibilityItemOperations__ResolveObject(agent_or_hvo)
        wsHandle = self._PossibilityItemOperations__WSHandle(wsHandle)

        version = ITsString(agent.Version.get_String(wsHandle)).Text
        return version or ""

    @OperationsMethod
    def SetVersion(self, agent_or_hvo, version, wsHandle=None):
        """
        Set the version string of an agent.

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO
            version (str): The version string (e.g., "1.0.0")
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If agent_or_hvo or version is None

        Example:
            >>> parser = project.Agent.Find("MyParser")
            >>> project.Agent.SetVersion(parser, "1.0.1")
            >>> print(project.Agent.GetVersion(parser))
            1.0.1

            >>> # Update to new version
            >>> project.Agent.SetVersion(parser, "2.0.0")

            >>> # Clear version
            >>> project.Agent.SetVersion(parser, "")

        Notes:
            - Typically used for parser agents
            - Can be empty string to clear
            - Use semantic versioning (e.g., "1.0.0") recommended
            - Update when parser algorithm changes

        See Also:
            GetVersion, CreateParserAgent
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(agent_or_hvo, "agent_or_hvo")
        self._ValidateParam(version, "version")

        agent = self._PossibilityItemOperations__ResolveObject(agent_or_hvo)
        wsHandle = self._PossibilityItemOperations__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(version, wsHandle)
        agent.Version.set_String(wsHandle, mkstr)

    # --- Agent Type Operations ---

    @OperationsMethod
    def IsHuman(self, agent_or_hvo):
        """
        Check if an agent is a human analyst.

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO

        Returns:
            bool: True if agent has a linked human (ICmPerson), False otherwise

        Raises:
            FP_NullParameterError: If agent_or_hvo is None

        Example:
            >>> for agent in project.Agent.GetAll():
            ...     name = project.Agent.GetName(agent)
            ...     if project.Agent.IsHuman(agent):
            ...         person = project.Agent.GetHuman(agent)
            ...         email = project.Person.GetEmail(person)
            ...         print(f"Human: {name} ({email})")
            ...     else:
            ...         version = project.Agent.GetVersion(agent)
            ...         print(f"Parser: {name} v{version}")
            Human: John Smith (john.smith@example.com)
            Parser: MyParser v1.0.0

        Notes:
            - Returns True if agent.Human is set
            - Returns False for parser/computer agents
            - Human agents have associated ICmPerson objects

        See Also:
            IsParser, GetHuman, SetHuman, CreateHumanAgent
        """
        self._ValidateParam(agent_or_hvo, "agent_or_hvo")

        agent = self._PossibilityItemOperations__ResolveObject(agent_or_hvo)

        return agent.Human is not None

    @OperationsMethod
    def IsParser(self, agent_or_hvo):
        """
        Check if an agent is a parser (automated analyzer).

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO

        Returns:
            bool: True if agent has no linked human, False otherwise

        Raises:
            FP_NullParameterError: If agent_or_hvo is None

        Example:
            >>> parser = project.Agent.Find("MyParser")
            >>> if project.Agent.IsParser(parser):
            ...     version = project.Agent.GetVersion(parser)
            ...     print(f"Parser version: {version}")
            Parser version: 1.0.0

            >>> # Filter only parsers
            >>> parsers = [a for a in project.Agent.GetAll()
            ...            if project.Agent.IsParser(a)]
            >>> print(f"Found {len(parsers)} parsers")

        Notes:
            - Returns True if agent.Human is None
            - Opposite of IsHuman()
            - Parser agents represent automated analysis tools

        See Also:
            IsHuman, CreateParserAgent, GetVersion
        """
        self._ValidateParam(agent_or_hvo, "agent_or_hvo")

        agent = self._PossibilityItemOperations__ResolveObject(agent_or_hvo)

        return agent.Human is None

    # --- Human (Person) Link ---

    @OperationsMethod
    def GetHuman(self, agent_or_hvo):
        """
        Get the linked person for a human agent.

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO

        Returns:
            ICmPerson or None: The linked person object, or None if not set

        Raises:
            FP_NullParameterError: If agent_or_hvo is None

        Example:
            >>> agent = project.Agent.Find("John Smith")
            >>> if project.Agent.IsHuman(agent):
            ...     person = project.Agent.GetHuman(agent)
            ...     name = project.Person.GetName(person)
            ...     email = project.Person.GetEmail(person)
            ...     print(f"{name}: {email}")
            John Smith: john.smith@example.com

            >>> # Parser agents return None
            >>> parser = project.Agent.Find("MyParser")
            >>> person = project.Agent.GetHuman(parser)
            >>> print(person)
            None

        Notes:
            - Returns None for parser agents
            - Returns ICmPerson object for human agents
            - Person contains biographical and contact information

        See Also:
            SetHuman, IsHuman, CreateHumanAgent
        """
        self._ValidateParam(agent_or_hvo, "agent_or_hvo")

        agent = self._PossibilityItemOperations__ResolveObject(agent_or_hvo)

        return agent.Human

    @OperationsMethod
    def SetHuman(self, agent_or_hvo, person):
        """
        Set the linked person for an agent (making it a human agent).

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO
            person: ICmPerson object to link (or None to unlink)

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If agent_or_hvo is None
            FP_ParameterError: If person is not a valid ICmPerson (when not None)

        Example:
            >>> # Convert parser to human agent
            >>> agent = project.Agent.Find("MyAgent")
            >>> person = project.Person.Find("John Smith")
            >>> project.Agent.SetHuman(agent, person)

            >>> # Unlink person (convert to parser)
            >>> project.Agent.SetHuman(agent, None)

        Notes:
            - Set to ICmPerson to make human agent
            - Set to None to convert to parser agent
            - Person must exist before linking
            - Human agents can have biographical data

        See Also:
            GetHuman, CreateHumanAgent, IsHuman
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(agent_or_hvo, "agent_or_hvo")

        agent = self._PossibilityItemOperations__ResolveObject(agent_or_hvo)

        if person is None:
            agent.Human = None
        else:
            try:
                person_obj = ICmPerson(person)
                agent.Human = person_obj
            except (TypeError, System.InvalidCastException, AttributeError) as e:
                raise FP_ParameterError(f"person must be a valid ICmPerson object: {e}")

    # --- Evaluations ---

    @OperationsMethod
    def GetEvaluations(self, agent_or_hvo):
        """
        Get all evaluations created by an agent.

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO

        Returns:
            list: List of ICmAgentEvaluation objects (empty list if none)

        Raises:
            FP_NullParameterError: If agent_or_hvo is None

        Example:
            >>> agent = project.Agent.Find("MyParser")
            >>> evaluations = project.Agent.GetEvaluations(agent)
            >>> print(f"Parser created {len(evaluations)} evaluations")
            Parser created 145 evaluations

            >>> # Examine evaluations
            >>> for eval in evaluations[:5]:
            ...     # Access evaluation properties
            ...     print(f"Evaluation: {eval.Guid}")

        Notes:
            - Returns empty list if no evaluations
            - Evaluations link agents to analyses
            - Used to track who/what approved analyses
            - Both human and parser agents can have evaluations

        See Also:
            GetEvaluationCount
        """
        self._ValidateParam(agent_or_hvo, "agent_or_hvo")

        agent = self._PossibilityItemOperations__ResolveObject(agent_or_hvo)

        # Get evaluations from the referring collection
        evaluations = []
        try:
            # Access evaluations that reference this agent
            for eval_obj in self.project.project.ServiceLocator.ObjectRepository.AllInstances(ICmAgentEvaluation):
                if eval_obj.Owner == agent:
                    evaluations.append(eval_obj)
        except (AttributeError, System.NullReferenceException, RuntimeError) as e:
            # If collection not accessible, return empty list
            pass

        return evaluations

    @OperationsMethod
    def GetEvaluationCount(self, agent_or_hvo):
        """
        Get the number of evaluations created by an agent.

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO

        Returns:
            int: Number of evaluations (0 if none)

        Raises:
            FP_NullParameterError: If agent_or_hvo is None

        Example:
            >>> agent = project.Agent.Find("MyParser")
            >>> count = project.Agent.GetEvaluationCount(agent)
            >>> print(f"Parser has {count} evaluations")
            Parser has 145 evaluations

            >>> # Compare human vs parser evaluations
            >>> for agent in project.Agent.GetAll():
            ...     name = project.Agent.GetName(agent)
            ...     count = project.Agent.GetEvaluationCount(agent)
            ...     agent_type = "Human" if project.Agent.IsHuman(agent) else "Parser"
            ...     print(f"{name} ({agent_type}): {count} evaluations")

        Notes:
            - More efficient than len(GetEvaluations())
            - Returns 0 if no evaluations
            - Useful for statistics and reporting

        See Also:
            GetEvaluations
        """
        self._ValidateParam(agent_or_hvo, "agent_or_hvo")

        return len(self.GetEvaluations(agent_or_hvo))

    # --- Query Methods ---

    @OperationsMethod
    def FindByType(self, is_human):
        """
        Find all agents of a specific type (human or parser).

        Args:
            is_human (bool): True to find human agents, False for parsers

        Returns:
            list: List of ICmAgent objects matching the type

        Example:
            >>> # Get all human agents
            >>> humans = project.Agent.FindByType(True)
            >>> for agent in humans:
            ...     name = project.Agent.GetName(agent)
            ...     person = project.Agent.GetHuman(agent)
            ...     email = project.Person.GetEmail(person)
            ...     print(f"{name}: {email}")

            >>> # Get all parsers
            >>> parsers = project.Agent.FindByType(False)
            >>> for parser in parsers:
            ...     name = project.Agent.GetName(parser)
            ...     version = project.Agent.GetVersion(parser)
            ...     print(f"{name} v{version}")

        Notes:
            - Returns list, not iterator
            - Human agents have linked ICmPerson
            - Parser agents have no linked person
            - Empty list if none found

        See Also:
            GetHumanAgents, GetParserAgents, IsHuman, IsParser
        """
        agents = []
        for agent in self.GetAll():
            if is_human:
                if self.IsHuman(agent):
                    agents.append(agent)
            else:
                if self.IsParser(agent):
                    agents.append(agent)
        return agents

    @OperationsMethod
    def GetHumanAgents(self):
        """
        Get all human agents in the project.

        Returns:
            list: List of ICmAgent objects representing human analysts

        Example:
            >>> humans = project.Agent.GetHumanAgents()
            >>> print(f"Found {len(humans)} human agents")
            Found 3 human agents

            >>> for agent in humans:
            ...     name = project.Agent.GetName(agent)
            ...     person = project.Agent.GetHuman(agent)
            ...     email = project.Person.GetEmail(person)
            ...     print(f"Analyst: {name} ({email})")
            Analyst: John Smith (john.smith@example.com)
            Analyst: Maria Garcia (maria.garcia@example.com)
            Analyst: Ahmed Hassan (ahmed.hassan@example.com)

        Notes:
            - Returns only agents with linked ICmPerson
            - Useful for identifying human annotators
            - Returns list, not iterator
            - Empty list if no human agents

        See Also:
            GetParserAgents, FindByType, IsHuman
        """
        return self.FindByType(True)

    @OperationsMethod
    def GetParserAgents(self):
        """
        Get all parser agents in the project.

        Returns:
            list: List of ICmAgent objects representing automated parsers

        Example:
            >>> parsers = project.Agent.GetParserAgents()
            >>> print(f"Found {len(parsers)} parsers")
            Found 2 parsers

            >>> for parser in parsers:
            ...     name = project.Agent.GetName(parser)
            ...     version = project.Agent.GetVersion(parser)
            ...     count = project.Agent.GetEvaluationCount(parser)
            ...     print(f"{name} v{version}: {count} evaluations")
            MyParser v1.0.0: 145 evaluations
            AutoAnalyzer v2.1.3: 89 evaluations

        Notes:
            - Returns only agents without linked ICmPerson
            - Useful for identifying automated analysis tools
            - Returns list, not iterator
            - Empty list if no parser agents

        See Also:
            GetHumanAgents, FindByType, IsParser
        """
        return self.FindByType(False)

    # --- Metadata ---

    @OperationsMethod
    def GetDateCreated(self, agent_or_hvo):
        """
        Get the creation date of an agent record.

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO

        Returns:
            System.DateTime: The date and time the agent record was created

        Raises:
            FP_NullParameterError: If agent_or_hvo is None

        Example:
            >>> agent = project.Agent.Find("MyParser")
            >>> created = project.Agent.GetDateCreated(agent)
            >>> print(f"Created: {created}")
            Created: 2025-01-15 14:30:22

            >>> # Find oldest agent
            >>> agents = list(project.Agent.GetAll())
            >>> oldest = min(agents, key=lambda a: project.Agent.GetDateCreated(a))
            >>> print(f"Oldest: {project.Agent.GetName(oldest)}")

        Notes:
            - Returns System.DateTime object (not Python datetime)
            - Automatically set when agent is created
            - Cannot be modified (read-only property)
            - Timezone is local to the FLEx project

        See Also:
            GetDateModified
        """
        self._ValidateParam(agent_or_hvo, "agent_or_hvo")

        agent = self._PossibilityItemOperations__ResolveObject(agent_or_hvo)

        return agent.DateCreated

    @OperationsMethod
    def GetDateModified(self, agent_or_hvo):
        """
        Get the last modification date of an agent record.

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO

        Returns:
            System.DateTime: The date and time the agent record was last modified

        Raises:
            FP_NullParameterError: If agent_or_hvo is None

        Example:
            >>> agent = project.Agent.Find("MyParser")
            >>> modified = project.Agent.GetDateModified(agent)
            >>> print(f"Last modified: {modified}")
            Last modified: 2025-01-20 09:15:43

            >>> # Find recently modified agents
            >>> from datetime import datetime, timedelta
            >>> # Note: System.DateTime, not Python datetime
            >>> for agent in project.Agent.GetAll():
            ...     modified = project.Agent.GetDateModified(agent)
            ...     name = project.Agent.GetName(agent)
            ...     print(f"{name}: {modified}")

        Notes:
            - Returns System.DateTime object (not Python datetime)
            - Automatically updated when agent changes
            - Cannot be modified directly (read-only property)
            - Updates on any change to agent properties

        See Also:
            GetDateCreated
        """
        self._ValidateParam(agent_or_hvo, "agent_or_hvo")

        agent = self._PossibilityItemOperations__ResolveObject(agent_or_hvo)

        return agent.DateModified
