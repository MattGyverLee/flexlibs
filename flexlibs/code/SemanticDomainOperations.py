#
#   SemanticDomainOperations.py
#
#   Class: SemanticDomainOperations
#          Semantic domain operations for FieldWorks Language Explorer
#          projects via SIL Language and Culture Model (LCM) API.
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
    ICmSemanticDomain,
    ICmSemanticDomainFactory,
    ILexSenseRepository,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from .FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class SemanticDomainOperations:
    """
    This class provides operations for managing semantic domains in a
    FieldWorks project.

    Semantic domains are hierarchical categorizations of word meanings used
    to organize the lexicon semantically. Most projects use predefined domain
    lists (e.g., from SIL), but custom domains can also be created.

    This class should be accessed via FLExProject.SemanticDomains property.

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get all semantic domains (flat list)
        for domain in project.SemanticDomains.GetAll(flat=True):
            number = project.SemanticDomains.GetNumber(domain)
            name = project.SemanticDomains.GetName(domain)
            print(f"{number} - {name}")

        # Find a specific domain by number
        domain = project.SemanticDomains.Find("7.2.1")
        if domain:
            name = project.SemanticDomains.GetName(domain)
            desc = project.SemanticDomains.GetDescription(domain)
            print(f"{name}: {desc}")

        # Get all senses in a domain
        senses = project.SemanticDomains.GetSensesInDomain(domain)
        print(f"Found {len(senses)} senses in this domain")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize SemanticDomainOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    # --- Core Read Operations ---

    def GetAll(self, flat=True):
        """
        Get all semantic domains in the project.

        Args:
            flat (bool): If True, returns a flat list of all domains including
                subdomains. If False, returns only top-level domains (use
                GetSubdomains to navigate hierarchy). Defaults to True.

        Returns:
            list: List of ICmSemanticDomain objects.

        Example:
            >>> # Get all domains in a flat list
            >>> for domain in project.SemanticDomains.GetAll(flat=True):
            ...     number = project.SemanticDomains.GetNumber(domain)
            ...     name = project.SemanticDomains.GetName(domain)
            ...     print(f"{number} - {name}")
            1 - Universe, creation
            1.1 - Sky
            1.1.1 - Sun
            1.1.1.1 - Moon
            ...

            >>> # Get only top-level domains
            >>> top_level = project.SemanticDomains.GetAll(flat=False)
            >>> for domain in top_level:
            ...     print(project.SemanticDomains.GetName(domain))
            Universe, creation
            Person
            Language and thought
            ...

        Notes:
            - Returns list, not iterator (consistent with FLExProject.GetAllSemanticDomains)
            - Flat list is useful for searching and iteration
            - Hierarchical list is useful for tree display
            - Most projects use standard SIL semantic domain lists
            - Domains are ordered by domain number

        See Also:
            Find, FindByName, GetSubdomains
        """
        domain_list = self.project.lp.SemanticDomainListOA
        if not domain_list:
            return []

        return list(self.project.UnpackNestedPossibilityList(
            domain_list.PossibilitiesOS,
            ICmSemanticDomain,
            flat
        ))


    def Find(self, number):
        """
        Find a semantic domain by its number.

        Args:
            number (str): The domain number to search for (e.g., "3.5.1.1").

        Returns:
            ICmSemanticDomain or None: The domain object if found, None otherwise.

        Raises:
            FP_NullParameterError: If number is None.

        Example:
            >>> # Find a specific domain
            >>> domain = project.SemanticDomains.Find("7.2.1")
            >>> if domain:
            ...     name = project.SemanticDomains.GetName(domain)
            ...     print(f"Found: {name}")
            Found: Walk

            >>> # Try to find non-existent domain
            >>> missing = project.SemanticDomains.Find("999.999")
            >>> print(missing)
            None

        Notes:
            - Number format is hierarchical (e.g., "1.2.3.4")
            - Search is exact match on the abbreviation field
            - Returns first match only (should be unique)
            - Returns None if not found (doesn't raise exception)
            - Number comparison is string-based, not numeric

        See Also:
            FindByName, Exists, GetNumber
        """
        if number is None:
            raise FP_NullParameterError()

        if not number or not number.strip():
            return None

        number = number.strip()
        wsHandle = self.project.project.DefaultAnalWs

        # Search through all domains (flat)
        for domain in self.GetAll(flat=True):
            domain_num = self.GetNumber(domain)
            if domain_num == number:
                return domain

        return None


    def FindByName(self, name):
        """
        Find a semantic domain by its name.

        Args:
            name (str): The domain name to search for (case-insensitive).

        Returns:
            ICmSemanticDomain or None: The domain object if found, None otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> # Find by English name
            >>> domain = project.SemanticDomains.FindByName("Walk")
            >>> if domain:
            ...     number = project.SemanticDomains.GetNumber(domain)
            ...     print(f"Domain number: {number}")
            Domain number: 7.2.1

            >>> # Case-insensitive search
            >>> domain = project.SemanticDomains.FindByName("walk")
            >>> print(domain is not None)
            True

        Notes:
            - Search is case-insensitive
            - Searches in default analysis writing system
            - Returns first match only
            - Returns None if not found (doesn't raise exception)
            - For multilingual searches, iterate GetAll() manually

        See Also:
            Find, Exists, GetName
        """
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            return None

        name_lower = name.strip().lower()
        wsHandle = self.project.project.DefaultAnalWs

        # Search through all domains
        for domain in self.GetAll(flat=True):
            domain_name = ITsString(domain.Name.get_String(wsHandle)).Text
            if domain_name and domain_name.lower() == name_lower:
                return domain

        return None


    def Exists(self, number):
        """
        Check if a semantic domain with the given number exists.

        Args:
            number (str): The domain number to check (e.g., "3.5.1.1").

        Returns:
            bool: True if domain exists, False otherwise.

        Raises:
            FP_NullParameterError: If number is None.

        Example:
            >>> if project.SemanticDomains.Exists("7.2.1"):
            ...     print("Walk domain exists")
            Walk domain exists

            >>> if not project.SemanticDomains.Exists("999.999"):
            ...     print("Custom domain 999.999 does not exist")
            Custom domain 999.999 does not exist

        Notes:
            - Returns False for empty or whitespace-only numbers
            - More efficient than Find() when you only need existence check
            - Use Find() if you need the actual domain object

        See Also:
            Find, FindByName
        """
        if number is None:
            raise FP_NullParameterError()

        return self.Find(number) is not None


    # --- Domain Properties ---

    def GetName(self, domain_or_hvo, wsHandle=None):
        """
        Get the name of a semantic domain.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The domain name, or empty string if not set.

        Raises:
            FP_NullParameterError: If domain_or_hvo is None.

        Example:
            >>> domain = project.SemanticDomains.Find("7.2.1")
            >>> name = project.SemanticDomains.GetName(domain)
            >>> print(name)
            Walk

            >>> # Get name in a specific writing system
            >>> name_fr = project.SemanticDomains.GetName(domain,
            ...                                            project.WSHandle('fr'))
            >>> print(name_fr)
            Marcher

        Notes:
            - Returns empty string if name not set in specified writing system
            - Names are typically set in multiple writing systems
            - Default writing system is the default analysis WS

        See Also:
            SetName, GetDescription, GetAbbreviation
        """
        if not domain_or_hvo:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(domain.Name.get_String(wsHandle)).Text
        return name or ""


    def SetName(self, domain_or_hvo, name, wsHandle=None):
        """
        Set the name of a semantic domain.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If domain_or_hvo or name is None.

        Example:
            >>> domain = project.SemanticDomains.Find("900.1")  # custom domain
            >>> project.SemanticDomains.SetName(domain, "Custom Category")
            >>> print(project.SemanticDomains.GetName(domain))
            Custom Category

        Warning:
            - Modifying standard semantic domains (e.g., SIL domains) may
              cause compatibility issues with other projects
            - Consider creating custom domains instead of modifying standard ones

        See Also:
            GetName, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not domain_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        domain.Name.set_String(wsHandle, mkstr)


    def GetDescription(self, domain_or_hvo, wsHandle=None):
        """
        Get the description of a semantic domain.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The domain description, or empty string if not set.

        Raises:
            FP_NullParameterError: If domain_or_hvo is None.

        Example:
            >>> domain = project.SemanticDomains.Find("7.2.1")
            >>> desc = project.SemanticDomains.GetDescription(domain)
            >>> print(desc)
            Use this domain for words related to walking.

        Notes:
            - Description provides guidance on domain usage
            - Often includes examples of words that belong in the domain
            - Returns empty string if not set in specified writing system
            - Descriptions can be quite lengthy

        See Also:
            SetDescription, GetName, GetQuestions
        """
        if not domain_or_hvo:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Description is a MultiString
        desc = ITsString(domain.Description.get_String(wsHandle)).Text
        return desc or ""


    def SetDescription(self, domain_or_hvo, description, wsHandle=None):
        """
        Set the description of a semantic domain.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.
            description (str): The new description text.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If domain_or_hvo or description is None.

        Example:
            >>> domain = project.SemanticDomains.Find("900.1")  # custom domain
            >>> project.SemanticDomains.SetDescription(domain,
            ...     "Use this domain for words related to modern technology.")

        See Also:
            GetDescription, SetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not domain_or_hvo:
            raise FP_NullParameterError()
        if description is None:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Description is a MultiString
        domain.Description.set_String(wsHandle, description)


    def GetAbbreviation(self, domain_or_hvo, wsHandle=None):
        """
        Get the abbreviation of a semantic domain.

        The abbreviation typically contains the domain number.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The domain abbreviation, or empty string if not set.

        Raises:
            FP_NullParameterError: If domain_or_hvo is None.

        Example:
            >>> domain = project.SemanticDomains.Find("7.2.1")
            >>> abbr = project.SemanticDomains.GetAbbreviation(domain)
            >>> print(abbr)
            7.2.1

        Notes:
            - Abbreviation usually equals the domain number
            - Returns empty string if not set in specified writing system
            - For domain number specifically, use GetNumber()

        See Also:
            GetNumber, GetName
        """
        if not domain_or_hvo:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        abbr = ITsString(domain.Abbreviation.get_String(wsHandle)).Text
        return abbr or ""


    def GetNumber(self, domain_or_hvo):
        """
        Get the domain number of a semantic domain.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.

        Returns:
            str: The domain number (e.g., "7.2.1"), or empty string if not set.

        Raises:
            FP_NullParameterError: If domain_or_hvo is None.

        Example:
            >>> domain = project.SemanticDomains.FindByName("Walk")
            >>> number = project.SemanticDomains.GetNumber(domain)
            >>> print(number)
            7.2.1

            >>> # Use number to navigate hierarchy
            >>> parent_num = ".".join(number.split(".")[:-1])
            >>> parent = project.SemanticDomains.Find(parent_num)
            >>> print(project.SemanticDomains.GetName(parent))
            Move

        Notes:
            - Domain number is stored in the abbreviation field
            - Numbers are hierarchical (e.g., 1.2.3.4)
            - Returns abbreviation from default analysis writing system
            - Returns empty string if domain has no number

        See Also:
            GetAbbreviation, Find, GetDepth
        """
        if not domain_or_hvo:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)
        wsHandle = self.project.project.DefaultAnalWs

        # Domain number is stored in the abbreviation
        number = ITsString(domain.Abbreviation.get_String(wsHandle)).Text
        return number or ""


    def GetQuestions(self, domain_or_hvo, wsHandle=None):
        """
        Get elicitation questions for a semantic domain.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The elicitation questions, or empty string if not set.

        Raises:
            FP_NullParameterError: If domain_or_hvo is None.

        Example:
            >>> domain = project.SemanticDomains.Find("7.2.1")
            >>> questions = project.SemanticDomains.GetQuestions(domain)
            >>> print(questions)
            (1) What words refer to walking?
            (2) What words refer to the way a person walks?
            (3) What words refer to walking a long distance?
            ...

        Notes:
            - Questions are used for elicitation during fieldwork
            - Questions help speakers think of words in the domain
            - Returns empty string if no questions are defined
            - Questions may be numbered or bulleted
            - Standard SIL domains include comprehensive question sets

        See Also:
            GetDescription, GetName
        """
        if not domain_or_hvo:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Questions is a MultiString
        questions = ITsString(domain.Questions.get_String(wsHandle)).Text
        return questions or ""


    def GetOcmCodes(self, domain_or_hvo):
        """
        Get OCM (Outline of Cultural Materials) codes for a semantic domain.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.

        Returns:
            str: The OCM codes, or empty string if not set.

        Raises:
            FP_NullParameterError: If domain_or_hvo is None.

        Example:
            >>> domain = project.SemanticDomains.Find("7.2.1")
            >>> ocm = project.SemanticDomains.GetOcmCodes(domain)
            >>> print(ocm)
            484

        Notes:
            - OCM codes link to the Outline of Cultural Materials
            - OCM is a standard anthropological classification system
            - Returns empty string if no OCM codes are assigned
            - Multiple codes may be separated by spaces or commas
            - Uses default analysis writing system

        See Also:
            GetNumber, GetDescription
        """
        if not domain_or_hvo:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)
        wsHandle = self.project.project.DefaultAnalWs

        # OcmCodes is a MultiUnicode
        ocm = ITsString(domain.OcmCodes.get_String(wsHandle)).Text
        return ocm or ""


    # --- Hierarchy Operations ---

    def GetSubdomains(self, domain_or_hvo):
        """
        Get all direct child subdomains of a semantic domain.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.

        Returns:
            list: List of ICmSemanticDomain child objects (empty list if none).

        Raises:
            FP_NullParameterError: If domain_or_hvo is None.

        Example:
            >>> # Get subdomains of "Universe, creation"
            >>> top_domain = project.SemanticDomains.Find("1")
            >>> subdomains = project.SemanticDomains.GetSubdomains(top_domain)
            >>> for subdomain in subdomains:
            ...     number = project.SemanticDomains.GetNumber(subdomain)
            ...     name = project.SemanticDomains.GetName(subdomain)
            ...     print(f"{number} - {name}")
            1.1 - Sky
            1.2 - World
            1.3 - Water
            ...

        Notes:
            - Returns direct children only (not recursive)
            - Returns empty list if domain has no subdomains
            - Subdomains are ordered by domain number
            - For full tree, recursively call GetSubdomains on each child

        See Also:
            GetParent, GetAll, GetDepth
        """
        if not domain_or_hvo:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)

        return list(domain.SubPossibilitiesOS)


    def GetParent(self, domain_or_hvo):
        """
        Get the parent domain of a semantic domain.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.

        Returns:
            ICmSemanticDomain or None: The parent domain, or None if top-level.

        Raises:
            FP_NullParameterError: If domain_or_hvo is None.

        Example:
            >>> # Get parent of "Walk" (7.2.1)
            >>> walk = project.SemanticDomains.Find("7.2.1")
            >>> parent = project.SemanticDomains.GetParent(walk)
            >>> if parent:
            ...     number = project.SemanticDomains.GetNumber(parent)
            ...     name = project.SemanticDomains.GetName(parent)
            ...     print(f"Parent: {number} - {name}")
            Parent: 7.2 - Move

            >>> # Top-level domains have no parent
            >>> top = project.SemanticDomains.Find("1")
            >>> parent = project.SemanticDomains.GetParent(top)
            >>> print(parent)
            None

        Notes:
            - Returns None for top-level domains
            - Parent is determined by ownership hierarchy
            - Use GetNumber() and string parsing for alternative navigation
            - Parent-child relationships form a tree structure

        See Also:
            GetSubdomains, GetDepth, GetNumber
        """
        if not domain_or_hvo:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)
        owner = domain.Owner

        # Check if owner is a semantic domain (subdomain) or the list (top-level)
        if owner and hasattr(owner, 'ClassName'):
            if owner.ClassName == 'CmSemanticDomain':
                return owner

        return None


    def GetDepth(self, domain_or_hvo):
        """
        Get the depth of a semantic domain in the hierarchy.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.

        Returns:
            int: The depth (0 for top-level, 1 for first level subdomains, etc.).

        Raises:
            FP_NullParameterError: If domain_or_hvo is None.

        Example:
            >>> # Top-level domain
            >>> universe = project.SemanticDomains.Find("1")
            >>> depth = project.SemanticDomains.GetDepth(universe)
            >>> print(depth)
            0

            >>> # Third-level domain
            >>> walk = project.SemanticDomains.Find("7.2.1")
            >>> depth = project.SemanticDomains.GetDepth(walk)
            >>> print(depth)
            2

        Notes:
            - Depth is 0-based (top-level = 0)
            - Depth equals the number of dots in domain number
            - Calculated by traversing parent chain
            - Useful for indentation in tree displays

        See Also:
            GetParent, GetNumber, GetSubdomains
        """
        if not domain_or_hvo:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)

        # Count parents by traversing ownership chain
        depth = 0
        current = domain
        while True:
            parent = self.GetParent(current)
            if parent is None:
                break
            depth += 1
            current = parent

        return depth


    # --- Usage Operations ---

    def GetSensesInDomain(self, domain_or_hvo):
        """
        Get all lexical senses that belong to this semantic domain.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.

        Returns:
            list: List of ILexSense objects that reference this domain.

        Raises:
            FP_NullParameterError: If domain_or_hvo is None.

        Example:
            >>> domain = project.SemanticDomains.Find("7.2.1")
            >>> senses = project.SemanticDomains.GetSensesInDomain(domain)
            >>> for sense in senses:
            ...     entry = sense.Entry
            ...     headword = project.LexiconGetHeadword(entry)
            ...     gloss = project.LexiconGetSenseGloss(sense)
            ...     print(f"{headword}: {gloss}")
            walk: to move on foot
            stroll: to walk leisurely
            march: to walk in formation
            ...

        Notes:
            - Searches all senses in the lexicon
            - Returns empty list if no senses use this domain
            - May be slow for large lexicons
            - Senses can belong to multiple domains
            - Use GetSenseCount() for just the count

        See Also:
            GetSenseCount, GetSubdomains
        """
        if not domain_or_hvo:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)
        domain_hvo = domain.Hvo

        # Search all senses for this domain
        senses = []
        sense_repo = self.project.project.ServiceLocator.GetInstance(ILexSenseRepository)

        for sense in sense_repo.AllInstances():
            # Check if this sense has this domain in its SemanticDomainsRC
            if domain in sense.SemanticDomainsRC:
                senses.append(sense)

        return senses


    def GetSenseCount(self, domain_or_hvo):
        """
        Get the count of lexical senses that belong to this semantic domain.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO.

        Returns:
            int: The number of senses using this domain.

        Raises:
            FP_NullParameterError: If domain_or_hvo is None.

        Example:
            >>> domain = project.SemanticDomains.Find("7.2.1")
            >>> count = project.SemanticDomains.GetSenseCount(domain)
            >>> print(f"Domain 7.2.1 (Walk) has {count} senses")
            Domain 7.2.1 (Walk) has 15 senses

            >>> # Find empty domains
            >>> for domain in project.SemanticDomains.GetAll(flat=True):
            ...     count = project.SemanticDomains.GetSenseCount(domain)
            ...     if count == 0:
            ...         number = project.SemanticDomains.GetNumber(domain)
            ...         name = project.SemanticDomains.GetName(domain)
            ...         print(f"Empty: {number} - {name}")

        Notes:
            - More efficient than len(GetSensesInDomain())
            - May still be slow for large lexicons
            - Returns 0 for domains with no senses
            - Useful for coverage analysis

        See Also:
            GetSensesInDomain
        """
        if not domain_or_hvo:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)

        # Count senses
        count = 0
        sense_repo = self.project.project.ServiceLocator.GetInstance(ILexSenseRepository)

        for sense in sense_repo.AllInstances():
            if domain in sense.SemanticDomainsRC:
                count += 1

        return count


    # --- Custom Domain Management ---

    def Create(self, name, number, parent=None, wsHandle=None):
        """
        Create a new custom semantic domain.

        Args:
            name (str): The name of the new domain.
            number (str): The domain number (e.g., "900.1").
            parent: Optional parent ICmSemanticDomain object or HVO. If None,
                creates a top-level domain.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ICmSemanticDomain: The newly created domain object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name or number is None.
            FP_ParameterError: If name or number is empty, or domain number
                already exists.

        Example:
            >>> # Create a top-level custom domain
            >>> custom = project.SemanticDomains.Create("Technology", "900")
            >>> print(project.SemanticDomains.GetName(custom))
            Technology

            >>> # Create a subdomain
            >>> computers = project.SemanticDomains.Create(
            ...     "Computers", "900.1", parent=custom)
            >>> print(project.SemanticDomains.GetNumber(computers))
            900.1

        Warning:
            - Custom domain numbers should not conflict with standard domains
            - Standard SIL domains use numbers 1-9
            - Consider using 900+ for custom domains
            - Creating many custom domains may impact performance

        Notes:
            - Domain is added to parent's subdomains or to top level
            - Number must be unique across all domains
            - Name is set in specified writing system
            - Use SetDescription() and GetQuestions() to add more details

        See Also:
            Delete, SetName, SetDescription, GetSubdomains
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()
        if number is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")
        if not number or not number.strip():
            raise FP_ParameterError("Number cannot be empty")

        # Check if domain number already exists
        if self.Exists(number):
            raise FP_ParameterError(f"Semantic domain '{number}' already exists")

        wsHandle = self.__WSHandle(wsHandle)

        # Create the new domain using the factory
        factory = self.project.project.ServiceLocator.GetInstance(
            ICmSemanticDomainFactory
        )
        new_domain = factory.Create()

        # Set name
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_domain.Name.set_String(wsHandle, mkstr_name)

        # Set abbreviation (domain number)
        mkstr_num = TsStringUtils.MakeString(number, wsHandle)
        new_domain.Abbreviation.set_String(wsHandle, mkstr_num)

        # Add to parent or top-level list
        if parent:
            parent_obj = self.__ResolveObject(parent)
            parent_obj.SubPossibilitiesOS.Add(new_domain)
        else:
            domain_list = self.project.lp.SemanticDomainListOA
            domain_list.PossibilitiesOS.Add(new_domain)

        return new_domain


    def Delete(self, domain_or_hvo):
        """
        Delete a semantic domain.

        Args:
            domain_or_hvo: The ICmSemanticDomain object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If domain_or_hvo is None.

        Example:
            >>> # Delete a custom domain
            >>> custom = project.SemanticDomains.Find("900.1")
            >>> if custom:
            ...     project.SemanticDomains.Delete(custom)

        Warning:
            - DO NOT delete standard semantic domains (1-9)
            - Deletion is permanent and cannot be undone
            - Deletes all subdomains recursively
            - Senses using this domain will lose the domain reference
            - Consider removing from senses first

        Notes:
            - Best practice: only delete custom domains (900+)
            - Deletion cascades to all subdomains
            - Domain references in senses are automatically cleaned up
            - Use with caution on shared projects

        See Also:
            Create, GetSensesInDomain
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not domain_or_hvo:
            raise FP_NullParameterError()

        domain = self.__ResolveObject(domain_or_hvo)

        # Get the parent or top-level list
        parent = self.GetParent(domain)

        if parent:
            # Remove from parent's subdomains
            parent.SubPossibilitiesOS.Remove(domain)
        else:
            # Remove from top-level list
            domain_list = self.project.lp.SemanticDomainListOA
            domain_list.PossibilitiesOS.Remove(domain)


    # --- Private Helper Methods ---

    def __ResolveObject(self, domain_or_hvo):
        """
        Resolve HVO or object to ICmSemanticDomain.

        Args:
            domain_or_hvo: Either an ICmSemanticDomain object or an HVO (int).

        Returns:
            ICmSemanticDomain: The resolved domain object.

        Raises:
            FP_ParameterError: If HVO doesn't refer to a semantic domain.
        """
        if isinstance(domain_or_hvo, int):
            obj = self.project.Object(domain_or_hvo)
            if not isinstance(obj, ICmSemanticDomain):
                raise FP_ParameterError("HVO does not refer to a semantic domain")
            return obj
        return domain_or_hvo


    def __WSHandle(self, wsHandle):
        """
        Get writing system handle, defaulting to analysis WS.

        Args:
            wsHandle: Optional writing system handle.

        Returns:
            int: The writing system handle.
        """
        if wsHandle is None:
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(
            wsHandle,
            self.project.project.DefaultAnalWs
        )
