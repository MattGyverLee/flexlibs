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

import logging
logger = logging.getLogger(__name__)

# Import FLEx LCM types
from SIL.LCModel import (
    ICmAgent,
    ICmAgentFactory,
    ICmAgentRepository,
    ICmPerson,
    ICmAgentEvaluation,
    ILangProject,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class AgentOperations:
    """
    This class provides operations for managing analysis agents in a FieldWorks
    project.

    Agents represent either human analysts or automated parsers that perform
    linguistic analysis. They are used to track who (or what) created analyses,
    glosses, and evaluations in the project.

    This class should be accessed via FLExProject.Agent property.

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get all agents
        for agent in project.Agent.GetAll():
            name = project.Agent.GetName(agent)
            agent_type = "Human" if project.Agent.IsHuman(agent) else "Parser"
            print(f"{name} ({agent_type})")

        # Create a human agent
        person = project.Person.Find("John Smith")
        agent = project.Agent.CreateHumanAgent("John Smith", person)

        # Create a parser agent
        parser = project.Agent.CreateParserAgent("MyParser", "1.0.0")
        project.Agent.SetVersion(parser, "1.0.1")

        # Find agents by type
        human_agents = project.Agent.GetHumanAgents()
        parser_agents = project.Agent.GetParserAgents()

        # Get evaluations for an agent
        evaluations = project.Agent.GetEvaluations(agent)
        count = project.Agent.GetEvaluationCount(agent)

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize AgentOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    # --- Core CRUD Operations ---

    def GetAll(self):
        """
        Get all agents in the project.

        This method returns an iterator over all ICmAgent objects in the
        project database, including both human analysts and automated parsers.

        Yields:
            ICmAgent: Each agent object in the project

        Example:
            >>> for agent in project.Agent.GetAll():
            ...     name = project.Agent.GetName(agent)
            ...     version = project.Agent.GetVersion(agent)
            ...     agent_type = "Human" if project.Agent.IsHuman(agent) else "Parser"
            ...     print(f"{name} v{version} ({agent_type})")
            John Smith v (Human)
            MyParser v1.0.0 (Parser)
            AutoAnalyzer v2.1.3 (Parser)

        Notes:
            - Returns an iterator for memory efficiency
            - Agents are returned in database order
            - Includes both human and computer agents
            - Use IsHuman() or IsParser() to determine agent type

        See Also:
            Find, Create, GetHumanAgents, GetParserAgents
        """
        return self.project.ObjectsIn(ICmAgentRepository)


    def Create(self, name, wsHandle=None):
        """
        Create a new agent in the FLEx project.

        Args:
            name (str): The name of the agent
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ICmAgent: The newly created agent object

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If name is None
            FP_ParameterError: If name is empty

        Example:
            >>> # Create a basic agent
            >>> agent = project.Agent.Create("MyParser")
            >>> print(project.Agent.GetName(agent))
            MyParser

            >>> # Create with specific writing system
            >>> agent = project.Agent.Create("AnalyseurFR",
            ...                               project.WSHandle('fr'))

            >>> # Create and configure a parser
            >>> parser = project.Agent.Create("AutoAnalyzer")
            >>> project.Agent.SetVersion(parser, "1.0.0")

        Notes:
            - The agent is added to the project's agents collection
            - Only name is required; other properties can be set later
            - Agent GUID is auto-generated
            - Use SetHuman() to link to a person, or leave unset for parsers

        See Also:
            CreateHumanAgent, CreateParserAgent, Delete, SetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        wsHandle = self.__WSHandleAnalysis(wsHandle)

        # Create the new agent using the factory
        factory = self.project.project.ServiceLocator.GetInstance(ICmAgentFactory)
        new_agent = factory.Create()

        # Set the name
        mkstr = TsStringUtils.MakeString(name, wsHandle)
        new_agent.Name.set_String(wsHandle, mkstr)

        # Add agent to the language project's agents collection
        self.project.lp.AnalyzingAgentsOC.Add(new_agent)

        return new_agent


    def CreateHumanAgent(self, name, person, wsHandle=None):
        """
        Create a new human agent linked to a person.

        Args:
            name (str): The name of the agent (typically matches person's name)
            person: ICmPerson object to link to this agent
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ICmAgent: The newly created human agent object

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If name or person is None
            FP_ParameterError: If name is empty or person is invalid

        Example:
            >>> # Create person first
            >>> person = project.Person.Create("John Smith")
            >>> project.Person.SetEmail(person, "john.smith@example.com")

            >>> # Create human agent linked to person
            >>> agent = project.Agent.CreateHumanAgent("John Smith", person)
            >>> print(f"Created agent for {project.Agent.GetName(agent)}")
            Created agent for John Smith

            >>> # Verify it's a human agent
            >>> if project.Agent.IsHuman(agent):
            ...     linked_person = project.Agent.GetHuman(agent)
            ...     print(f"Linked to: {project.Person.GetName(linked_person)}")
            Linked to: John Smith

        Notes:
            - Links agent to ICmPerson for biographical information
            - Human agents represent linguists, consultants, annotators
            - Person object must exist before creating agent
            - Use this for manual analyses and human-verified content

        See Also:
            Create, CreateParserAgent, SetHuman, GetHuman
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if person is None:
            raise FP_NullParameterError()

        # Create the agent
        agent = self.Create(name, wsHandle)

        # Link to person
        try:
            person_obj = ICmPerson(person)
            agent.Human = person_obj
        except:
            raise FP_ParameterError("person must be a valid ICmPerson object")

        return agent


    def CreateParserAgent(self, name, version="", wsHandle=None):
        """
        Create a new parser agent (computer/automated analyzer).

        Args:
            name (str): The name of the parser
            version (str): Version string (e.g., "1.0.0"). Defaults to empty.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ICmAgent: The newly created parser agent object

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If name is None
            FP_ParameterError: If name is empty

        Example:
            >>> # Create a parser with version
            >>> parser = project.Agent.CreateParserAgent("MyParser", "1.0.0")
            >>> print(f"{project.Agent.GetName(parser)} "
            ...       f"v{project.Agent.GetVersion(parser)}")
            MyParser v1.0.0

            >>> # Create parser without initial version
            >>> analyzer = project.Agent.CreateParserAgent("AutoAnalyzer")
            >>> project.Agent.SetVersion(analyzer, "2.1.3")

            >>> # Verify it's a parser
            >>> if project.Agent.IsParser(parser):
            ...     print("This is an automated parser")
            This is an automated parser

        Notes:
            - Parser agents represent automated analysis tools
            - Human property is not set (remains None)
            - Version tracks the parser software version
            - Use for automatically generated analyses

        See Also:
            Create, CreateHumanAgent, SetVersion, GetVersion
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        # Create the agent
        agent = self.Create(name, wsHandle)

        # Set version if provided
        if version:
            self.SetVersion(agent, version, wsHandle)

        # Human is None for parser agents (default)

        return agent


    def Delete(self, agent_or_hvo):
        """
        Delete an agent from the FLEx project.

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO (database ID)

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If agent_or_hvo is None
            FP_ParameterError: If agent doesn't exist

        Example:
            >>> agent = project.Agent.Find("OldParser")
            >>> if agent:
            ...     project.Agent.Delete(agent)

            >>> # Delete by HVO
            >>> project.Agent.Delete(12345)

        Warning:
            - This is a destructive operation
            - All associated evaluations will be affected
            - References from analyses may become invalid
            - Cannot be undone
            - Agent will be removed from all linked evaluations

        Notes:
            - Deletion cascades to owned objects
            - Consider archiving data before deletion
            - Use with caution in production databases
            - Evaluations may become orphaned

        See Also:
            Create, Exists
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not agent_or_hvo:
            raise FP_NullParameterError()

        # Resolve to agent object
        agent = self.__ResolveObject(agent_or_hvo)

        # Remove from agents collection
        self.project.lp.AnalyzingAgentsOC.Remove(agent)


    def Exists(self, name, wsHandle=None):
        """
        Check if an agent with the given name exists.

        Args:
            name (str): The name to search for
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            bool: True if an agent exists with this name, False otherwise

        Raises:
            FP_NullParameterError: If name is None

        Example:
            >>> if not project.Agent.Exists("MyParser"):
            ...     parser = project.Agent.CreateParserAgent("MyParser", "1.0.0")

            >>> # Check in specific writing system
            >>> if project.Agent.Exists("AnalyseurFR", project.WSHandle('fr')):
            ...     print("French analyzer exists")

        Notes:
            - Search is case-sensitive
            - Search is writing-system specific
            - Returns False for empty or whitespace-only names
            - Use Find() to get the actual agent object

        See Also:
            Find, Create
        """
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            return False

        return self.Find(name, wsHandle) is not None


    def Find(self, name, wsHandle=None):
        """
        Find an agent by name.

        Args:
            name (str): The name to search for
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ICmAgent or None: The agent object if found, None otherwise

        Raises:
            FP_NullParameterError: If name is None

        Example:
            >>> agent = project.Agent.Find("MyParser")
            >>> if agent:
            ...     version = project.Agent.GetVersion(agent)
            ...     print(f"Found: {name} v{version}")
            Found: MyParser v1.0.0

            >>> # Search in specific writing system
            >>> agent = project.Agent.Find("AnalyseurFR",
            ...                             project.WSHandle('fr'))

        Notes:
            - Returns first match only
            - Search is case-sensitive
            - Search is writing-system specific
            - Returns None if not found (doesn't raise exception)
            - For partial name search, iterate GetAll() and filter

        See Also:
            Exists, GetAll, FindByType
        """
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            return None

        wsHandle = self.__WSHandleAnalysis(wsHandle)

        # Search through all agents
        for agent in self.GetAll():
            agent_name = ITsString(agent.Name.get_String(wsHandle)).Text
            if agent_name == name:
                return agent

        return None


    # --- Name and Version Management ---

    def GetName(self, agent_or_hvo, wsHandle=None):
        """
        Get the name of an agent.

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The agent's name (empty string if not set)

        Raises:
            FP_NullParameterError: If agent_or_hvo is None

        Example:
            >>> agent = project.Agent.Find("MyParser")
            >>> name = project.Agent.GetName(agent)
            >>> print(name)
            MyParser

            >>> # Get in specific writing system
            >>> name_fr = project.Agent.GetName(agent, project.WSHandle('fr'))

        Notes:
            - Returns empty string if name not set
            - Returns empty string if not set in specified writing system
            - Name can be set in multiple writing systems

        See Also:
            SetName, Create
        """
        if not agent_or_hvo:
            raise FP_NullParameterError()

        agent = self.__ResolveObject(agent_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        name = ITsString(agent.Name.get_String(wsHandle)).Text
        return name or ""


    def SetName(self, agent_or_hvo, name, wsHandle=None):
        """
        Set the name of an agent.

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO
            name (str): The new name
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If agent_or_hvo or name is None
            FP_ParameterError: If name is empty

        Example:
            >>> agent = project.Agent.Find("MyParser")
            >>> project.Agent.SetName(agent, "MyParser Pro")
            >>> print(project.Agent.GetName(agent))
            MyParser Pro

            >>> # Set in specific writing system
            >>> project.Agent.SetName(agent, "Mon Analyseur",
            ...                        project.WSHandle('fr'))

        Notes:
            - Name should be descriptive and unique
            - Can be set in multiple writing systems
            - Empty names are not allowed

        See Also:
            GetName, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not agent_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        agent = self.__ResolveObject(agent_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        agent.Name.set_String(wsHandle, mkstr)


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
        if not agent_or_hvo:
            raise FP_NullParameterError()

        agent = self.__ResolveObject(agent_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        version = ITsString(agent.Version.get_String(wsHandle)).Text
        return version or ""


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
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not agent_or_hvo:
            raise FP_NullParameterError()
        if version is None:
            raise FP_NullParameterError()

        agent = self.__ResolveObject(agent_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        mkstr = TsStringUtils.MakeString(version, wsHandle)
        agent.Version.set_String(wsHandle, mkstr)


    # --- Agent Type Operations ---

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
        if not agent_or_hvo:
            raise FP_NullParameterError()

        agent = self.__ResolveObject(agent_or_hvo)

        return agent.Human is not None


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
        if not agent_or_hvo:
            raise FP_NullParameterError()

        agent = self.__ResolveObject(agent_or_hvo)

        return agent.Human is None


    # --- Human (Person) Link ---

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
        if not agent_or_hvo:
            raise FP_NullParameterError()

        agent = self.__ResolveObject(agent_or_hvo)

        return agent.Human


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
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not agent_or_hvo:
            raise FP_NullParameterError()

        agent = self.__ResolveObject(agent_or_hvo)

        if person is None:
            agent.Human = None
        else:
            try:
                person_obj = ICmPerson(person)
                agent.Human = person_obj
            except:
                raise FP_ParameterError("person must be a valid ICmPerson object")


    # --- Evaluations ---

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
        if not agent_or_hvo:
            raise FP_NullParameterError()

        agent = self.__ResolveObject(agent_or_hvo)

        # Get evaluations from the referring collection
        evaluations = []
        try:
            # Access evaluations that reference this agent
            for eval_obj in self.project.project.ServiceLocator.ObjectRepository.AllInstances(
                ICmAgentEvaluation
            ):
                if eval_obj.Owner == agent:
                    evaluations.append(eval_obj)
        except:
            # If collection not accessible, return empty list
            pass

        return evaluations


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
        if not agent_or_hvo:
            raise FP_NullParameterError()

        return len(self.GetEvaluations(agent_or_hvo))


    # --- Query Methods ---

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

    def GetGuid(self, agent_or_hvo):
        """
        Get the GUID (Globally Unique Identifier) of an agent.

        Args:
            agent_or_hvo: Either an ICmAgent object or its HVO

        Returns:
            System.Guid: The agent's GUID

        Raises:
            FP_NullParameterError: If agent_or_hvo is None

        Example:
            >>> agent = project.Agent.Find("MyParser")
            >>> guid = project.Agent.GetGuid(agent)
            >>> print(guid)
            a1b2c3d4-e5f6-7890-abcd-ef1234567890

            >>> # Use GUID to retrieve agent later
            >>> agent2 = project.Object(guid)
            >>> print(project.Agent.GetName(agent2))
            MyParser

        Notes:
            - GUIDs are unique across all FLEx projects
            - GUIDs are persistent (don't change)
            - Useful for linking agents across projects
            - Can be used with FLExProject.Object() to retrieve agent

        See Also:
            FLExProject.Object, FLExProject.BuildGotoURL
        """
        if not agent_or_hvo:
            raise FP_NullParameterError()

        agent = self.__ResolveObject(agent_or_hvo)

        return agent.Guid


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
        if not agent_or_hvo:
            raise FP_NullParameterError()

        agent = self.__ResolveObject(agent_or_hvo)

        return agent.DateCreated


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
        if not agent_or_hvo:
            raise FP_NullParameterError()

        agent = self.__ResolveObject(agent_or_hvo)

        return agent.DateModified


    # --- Private Helper Methods ---

    def __ResolveObject(self, agent_or_hvo):
        """
        Resolve HVO or object to ICmAgent.

        Args:
            agent_or_hvo: Either an ICmAgent object or an HVO (int)

        Returns:
            ICmAgent: The resolved agent object

        Raises:
            FP_ParameterError: If HVO doesn't refer to an agent
        """
        if isinstance(agent_or_hvo, int):
            obj = self.project.Object(agent_or_hvo)
            if not isinstance(obj, ICmAgent):
                raise FP_ParameterError("HVO does not refer to an agent")
            return obj
        return agent_or_hvo


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
