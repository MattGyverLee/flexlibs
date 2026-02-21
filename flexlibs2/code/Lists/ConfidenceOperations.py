#
#   ConfidenceOperations.py
#
#   Class: ConfidenceOperations
#          Confidence level operations for FieldWorks Language Explorer
#          projects via SIL Language and Culture Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

# Import FLEx LCM types
from SIL.LCModel import (
    ICmPossibility,
    ICmPossibilityFactory,
    IWfiAnalysisRepository,
    IWfiGlossRepository,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)
from ..BaseOperations import BaseOperations

class ConfidenceOperations(BaseOperations):
    """
    This class provides operations for managing confidence levels (quality
    ratings) in a FieldWorks project.

    Confidence levels are used to rate the quality or certainty of linguistic
    analyses and glosses. They provide a standardized way to indicate how
    confident a linguist or parser is about a particular analysis or gloss.
    Confidence levels are implemented as a possibility list using ICmPossibility.

    Common confidence levels might include:
    - High Confidence (for well-established analyses)
    - Medium Confidence (for probable but uncertain analyses)
    - Low Confidence (for tentative analyses)
    - Unconfirmed (for machine-generated or unverified analyses)

    This class should be accessed via FLExProject.Confidence property.

    Usage::

        from flexlibs2 import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get all confidence levels
        for level in project.Confidence.GetAll():
            name = project.Confidence.GetName(level)
            desc = project.Confidence.GetDescription(level)
            print(f"{name}: {desc}")

        # Find a specific confidence level
        high = project.Confidence.Find("High Confidence")
        if high:
            # Get analyses using this confidence level
            analyses = project.Confidence.GetAnalysesWithConfidence(high)
            print(f"{len(analyses)} analyses have high confidence")

        # Create a custom confidence level
        custom = project.Confidence.Create("Verified", "en")
        project.Confidence.SetDescription(custom,
            "Analysis verified by native speaker")

        # Find the default confidence level
        default = project.Confidence.GetDefault()
        if default:
            print(f"Default: {project.Confidence.GetName(default)}")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize ConfidenceOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)

    def _GetSequence(self, parent):
        """Specify which sequence to reorder for confidence level sub-possibilities."""
        return parent.SubPossibilitiesOS

    # --- Core CRUD Operations ---

    def GetAll(self):
        """
        Get all confidence levels in the project.

        Returns:
            list: List of ICmPossibility objects representing confidence levels.

        Example:
            >>> # Get all confidence levels
            >>> for level in project.Confidence.GetAll():
            ...     name = project.Confidence.GetName(level)
            ...     desc = project.Confidence.GetDescription(level)
            ...     print(f"{name}: {desc}")
            High Confidence: Analysis confirmed by multiple sources
            Medium Confidence: Analysis likely but needs verification
            Low Confidence: Tentative analysis requiring review
            Unconfirmed: Machine-generated, not reviewed

            >>> # Count confidence levels
            >>> levels = project.Confidence.GetAll()
            >>> print(f"Project has {len(levels)} confidence levels")
            Project has 4 confidence levels

        Notes:
            - Returns flat list of all confidence levels
            - Confidence levels are not hierarchical (no sublevels)
            - Returns empty list if no confidence levels exist
            - Standard FLEx projects may have predefined levels
            - Custom levels can be added as needed

        See Also:
            Find, Create, Exists
        """
        confidence_list = self.project.lp.ConfidenceLevelsOA
        if not confidence_list:
            return []

        return list(confidence_list.PossibilitiesOS)

    def Create(self, name, wsHandle=None):
        """
        Create a new confidence level.

        Args:
            name (str): The name of the new confidence level.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ICmPossibility: The newly created confidence level object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name is None.
            FP_ParameterError: If name is empty or confidence level list doesn't exist.

        Example:
            >>> # Create a new confidence level
            >>> verified = project.Confidence.Create("Verified by Speaker", "en")
            >>> print(project.Confidence.GetName(verified))
            Verified by Speaker

            >>> # Create with description
            >>> custom = project.Confidence.Create("Provisional", "en")
            >>> project.Confidence.SetDescription(custom,
            ...     "Provisional analysis pending further research")

            >>> # Create multilingual confidence level
            >>> level = project.Confidence.Create("High", "en")
            >>> project.Confidence.SetName(level, "Haute", "fr")
            >>> project.Confidence.SetName(level, "Alta", "es")

        Notes:
            - New confidence level is added to the end of the list
            - Name is set in specified writing system
            - Use SetName() to add names in other writing systems
            - Use SetDescription() to add explanatory text
            - GUID is auto-generated
            - New level can be used immediately with analyses/glosses

        See Also:
            Delete, SetName, SetDescription, Find
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        # Get the confidence levels list
        confidence_list = self.project.lp.ConfidenceLevelsOA
        if not confidence_list:
            raise FP_ParameterError("Confidence levels list not found in project")

        wsHandle = self.__WSHandle(wsHandle)

        # Create the new confidence level using the factory
        factory = self.project.project.ServiceLocator.GetService(
            ICmPossibilityFactory
        )
        new_level = factory.Create()

        # Add to the confidence levels list (must be done before setting properties)
        confidence_list.PossibilitiesOS.Add(new_level)

        # Set name
        mkstr = TsStringUtils.MakeString(name, wsHandle)
        new_level.Name.set_String(wsHandle, mkstr)

        return new_level

    def Delete(self, level_or_hvo):
        """
        Delete a confidence level from the project.

        Args:
            level_or_hvo: Either an ICmPossibility object or its HVO.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If level_or_hvo is None.

        Example:
            >>> # Delete an unused confidence level
            >>> level = project.Confidence.Find("Obsolete Level")
            >>> if level:
            ...     # Check if it's being used
            ...     analyses = project.Confidence.GetAnalysesWithConfidence(level)
            ...     if not analyses:
            ...         project.Confidence.Delete(level)
            ...     else:
            ...         print(f"Cannot delete: used by {len(analyses)} analyses")

            >>> # Delete by HVO
            >>> project.Confidence.Delete(12345)

        Warning:
            - This is a destructive operation
            - Deletion is permanent and cannot be undone
            - Analyses and glosses using this level will lose the confidence reference
            - Check usage with GetAnalysesWithConfidence() before deleting
            - DO NOT delete standard confidence levels used throughout the project
            - Consider setting a different confidence level on referencing objects first

        Notes:
            - Deletion removes the level from the confidence list
            - References from analyses/glosses are automatically cleaned up
            - Best practice: only delete custom levels that are no longer needed
            - Use with caution on shared projects

        See Also:
            Create, GetAnalysesWithConfidence, GetGlossesWithConfidence
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if level_or_hvo is None:
            raise FP_NullParameterError()

        level = self.__ResolveObject(level_or_hvo)

        # Get the confidence levels list and remove the level
        confidence_list = self.project.lp.ConfidenceLevelsOA
        if confidence_list and level in confidence_list.PossibilitiesOS:
            confidence_list.PossibilitiesOS.Remove(level)

    def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
        """
        Duplicate a confidence level, creating a new copy with a new GUID.

        Args:
            item_or_hvo: Either an ICmPossibility object or its HVO to duplicate.
            insert_after (bool): If True (default), insert after the source level.
                                If False, insert at end of confidence levels list.
            deep (bool): Not applicable for confidence levels (no owned objects).
                        Included for API consistency.

        Returns:
            ICmPossibility: The newly created duplicate confidence level with a new GUID.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> # Duplicate a confidence level
            >>> high = project.Confidence.Find("High Confidence")
            >>> dup = project.Confidence.Duplicate(high)
            >>> print(f"Original: {project.Confidence.GetName(high)}")
            >>> print(f"Duplicate: {project.Confidence.GetName(dup)}")
            Original: High Confidence
            Duplicate: High Confidence
            >>>
            >>> # Modify the duplicate
            >>> project.Confidence.SetName(dup, "Very High Confidence")
            >>> project.Confidence.SetDescription(dup,
            ...     "Analysis confirmed by multiple expert sources")

        Notes:
            - Factory.Create() automatically generates a new GUID
            - insert_after=True preserves the original level's position
            - MultiString properties copied: Name, Description
            - Confidence levels have no owned objects, so deep parameter has no effect
            - Duplicate is added to ConfidenceLevelsOA before copying properties

        See Also:
            Create, Delete, GetGuid
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if item_or_hvo is None:
            raise FP_NullParameterError()

        # Get source confidence level
        source = self.__ResolveObject(item_or_hvo)

        # Get the confidence levels list
        confidence_list = self.project.lp.ConfidenceLevelsOA
        if not confidence_list:
            raise FP_ParameterError("Confidence levels list not found in project")

        # Create new confidence level using factory (auto-generates new GUID)
        factory = self.project.project.ServiceLocator.GetService(ICmPossibilityFactory)
        duplicate = factory.Create()

        # ADD TO PARENT FIRST before copying properties (CRITICAL)
        if insert_after:
            # Insert after source level
            source_index = confidence_list.PossibilitiesOS.IndexOf(source)
            confidence_list.PossibilitiesOS.Insert(source_index + 1, duplicate)
        else:
            # Insert at end
            confidence_list.PossibilitiesOS.Add(duplicate)

        # Copy MultiString properties using CopyAlternatives
        duplicate.Name.CopyAlternatives(source.Name)
        duplicate.Description.CopyAlternatives(source.Description)

        return duplicate

    # ========== SYNC INTEGRATION METHODS ==========

    def GetSyncableProperties(self, item):
        """
        Get syncable properties for cross-project synchronization.

        Returns all syncable properties of a confidence level including
        MultiString fields.

        Args:
            item: The ICmPossibility object (confidence level)

        Returns:
            dict: Dictionary of syncable properties

        Example:
            >>> props = project.Confidence.GetSyncableProperties(level)
            >>> print(props)
            {'Name': 'High Confidence', 'Description': 'Verified analysis'}
        """
        if not item:
            raise FP_NullParameterError()

        level = self.__ResolveObject(item)
        wsHandle = self.project.project.DefaultAnalWs

        props = {}

        # MultiString properties
        props['Name'] = ITsString(level.Name.get_String(wsHandle)).Text or ""
        props['Description'] = ITsString(level.Description.get_String(wsHandle)).Text or ""

        return props

    def CompareTo(self, item1, item2, ops1=None, ops2=None):
        """
        Compare two confidence levels and return detailed differences.

        Args:
            item1: First confidence level (from source project)
            item2: Second confidence level (from target project)
            ops1: Operations instance for item1's project (defaults to self)
            ops2: Operations instance for item2's project (defaults to self)

        Returns:
            tuple: (is_different, differences_dict) where differences_dict contains
                   'properties' dict with changed property details

        Example:
            >>> is_diff, diffs = ops1.CompareTo(level1, level2, ops1, ops2)
            >>> if is_diff:
            ...     for prop, details in diffs['properties'].items():
            ...         print(f"{prop}: {details['source']} -> {details['target']}")
        """
        if ops1 is None:
            ops1 = self
        if ops2 is None:
            ops2 = self

        is_different = False
        differences = {'properties': {}}

        # Get syncable properties from both items
        props1 = ops1.GetSyncableProperties(item1)
        props2 = ops2.GetSyncableProperties(item2)

        # Compare each property
        for key in set(props1.keys()) | set(props2.keys()):
            val1 = props1.get(key)
            val2 = props2.get(key)

            if val1 != val2:
                is_different = True
                differences['properties'][key] = {
                    'source': val1,
                    'target': val2,
                    'type': 'modified'
                }

        return is_different, differences

    def Find(self, name):
        """
        Find a confidence level by its name.

        Args:
            name (str): The confidence level name to search for (case-insensitive).

        Returns:
            ICmPossibility or None: The confidence level object if found, None otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> # Find by name
            >>> high = project.Confidence.Find("High Confidence")
            >>> if high:
            ...     desc = project.Confidence.GetDescription(high)
            ...     print(f"Found: {desc}")
            Found: Analysis confirmed by multiple sources

            >>> # Case-insensitive search
            >>> level = project.Confidence.Find("high confidence")
            >>> print(level is not None)
            True

            >>> # Not found
            >>> missing = project.Confidence.Find("Nonexistent Level")
            >>> print(missing)
            None

        Notes:
            - Search is case-insensitive
            - Searches in default analysis writing system
            - Returns first match only
            - Returns None if not found (doesn't raise exception)
            - For multilingual searches, iterate GetAll() manually
            - Common standard names: "High", "Medium", "Low", "Unconfirmed"

        See Also:
            Exists, GetAll, GetName
        """
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            return None

        name_lower = name.strip().lower()
        wsHandle = self.project.project.DefaultAnalWs

        # Search through all confidence levels
        for level in self.GetAll():
            level_name = ITsString(level.Name.get_String(wsHandle)).Text
            if level_name and level_name.lower() == name_lower:
                return level

        return None

    def Exists(self, name):
        """
        Check if a confidence level with the given name exists.

        Args:
            name (str): The confidence level name to check.

        Returns:
            bool: True if confidence level exists, False otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> if project.Confidence.Exists("High Confidence"):
            ...     print("High confidence level exists")
            High confidence level exists

            >>> if not project.Confidence.Exists("Custom Level"):
            ...     level = project.Confidence.Create("Custom Level")

        Notes:
            - Search is case-insensitive
            - Returns False for empty or whitespace-only names
            - More efficient than Find() when you only need existence check
            - Use Find() if you need the actual confidence level object

        See Also:
            Find, Create
        """
        if name is None:
            raise FP_NullParameterError()

        return self.Find(name) is not None

    # --- Name and Description Operations ---

    def GetName(self, level_or_hvo, wsHandle=None):
        """
        Get the name of a confidence level.

        Args:
            level_or_hvo: Either an ICmPossibility object or its HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The confidence level name, or empty string if not set.

        Raises:
            FP_NullParameterError: If level_or_hvo is None.

        Example:
            >>> level = project.Confidence.Find("High Confidence")
            >>> name = project.Confidence.GetName(level)
            >>> print(name)
            High Confidence

            >>> # Get name in specific writing system
            >>> name_fr = project.Confidence.GetName(level, project.WSHandle('fr'))
            >>> print(name_fr)
            Haute Confiance

            >>> # Iterate all levels
            >>> for level in project.Confidence.GetAll():
            ...     name = project.Confidence.GetName(level)
            ...     print(f"Level: {name}")

        Notes:
            - Returns empty string if name not set in specified writing system
            - Names can be set in multiple writing systems
            - Default writing system is the default analysis WS
            - Use for display in UI, reports, and exports

        See Also:
            SetName, GetDescription, Find
        """
        if level_or_hvo is None:
            raise FP_NullParameterError()

        level = self.__ResolveObject(level_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(level.Name.get_String(wsHandle)).Text
        return name or ""

    def SetName(self, level_or_hvo, name, wsHandle=None):
        """
        Set the name of a confidence level.

        Args:
            level_or_hvo: Either an ICmPossibility object or its HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If level_or_hvo or name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> level = project.Confidence.Find("Old Name")
            >>> if level:
            ...     project.Confidence.SetName(level, "New Name")
            ...     print(project.Confidence.GetName(level))
            New Name

            >>> # Set multilingual names
            >>> level = project.Confidence.Create("High")
            >>> project.Confidence.SetName(level, "High", "en")
            >>> project.Confidence.SetName(level, "Haute", "fr")
            >>> project.Confidence.SetName(level, "Alta", "es")

        Notes:
            - Name cannot be empty (raises FP_ParameterError)
            - Name is stored in the specified writing system
            - Does not affect names in other writing systems
            - Use different writing systems for multilingual projects
            - Renaming does not affect references from analyses/glosses

        See Also:
            GetName, SetDescription
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if level_or_hvo is None:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        level = self.__ResolveObject(level_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        level.Name.set_String(wsHandle, mkstr)

    def GetDescription(self, level_or_hvo, wsHandle=None):
        """
        Get the description of a confidence level.

        Args:
            level_or_hvo: Either an ICmPossibility object or its HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The confidence level description, or empty string if not set.

        Raises:
            FP_NullParameterError: If level_or_hvo is None.

        Example:
            >>> level = project.Confidence.Find("High Confidence")
            >>> desc = project.Confidence.GetDescription(level)
            >>> print(desc)
            Analysis confirmed by multiple sources and verified
            by native speaker consultation.

            >>> # Display all levels with descriptions
            >>> for level in project.Confidence.GetAll():
            ...     name = project.Confidence.GetName(level)
            ...     desc = project.Confidence.GetDescription(level)
            ...     if desc:
            ...         print(f"{name}: {desc}")

        Notes:
            - Returns empty string if description not set in specified writing system
            - Descriptions provide guidance on when to use each level
            - Can be lengthy (multiple sentences or paragraphs)
            - Useful for training materials and documentation
            - Can be multilingual

        See Also:
            SetDescription, GetName
        """
        if level_or_hvo is None:
            raise FP_NullParameterError()

        level = self.__ResolveObject(level_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        desc = ITsString(level.Description.get_String(wsHandle)).Text
        return desc or ""

    def SetDescription(self, level_or_hvo, description, wsHandle=None):
        """
        Set the description of a confidence level.

        Args:
            level_or_hvo: Either an ICmPossibility object or its HVO.
            description (str): The new description text.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If level_or_hvo or description is None.

        Example:
            >>> level = project.Confidence.Find("High Confidence")
            >>> desc = ("Analysis confirmed by multiple sources including:\\n"
            ...         "- Native speaker consultation\\n"
            ...         "- Published dictionary references\\n"
            ...         "- Cross-linguistic comparison")
            >>> project.Confidence.SetDescription(level, desc)

            >>> # Set multilingual descriptions
            >>> project.Confidence.SetDescription(level, desc_en, "en")
            >>> project.Confidence.SetDescription(level, desc_fr, "fr")

            >>> # Clear description
            >>> project.Confidence.SetDescription(level, "")

        Notes:
            - Empty string is allowed (clears the description)
            - Description is stored in the specified writing system
            - Use newlines for formatting if needed
            - Good place for usage guidelines and examples
            - Helps ensure consistent confidence level assignment

        See Also:
            GetDescription, SetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if level_or_hvo is None:
            raise FP_NullParameterError()
        if description is None:
            raise FP_NullParameterError()

        level = self.__ResolveObject(level_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(description, wsHandle)
        level.Description.set_String(wsHandle, mkstr)

    # --- Usage Query Operations ---

    def GetAnalysesWithConfidence(self, level_or_hvo):
        """
        Get all wordform analyses that use this confidence level.

        Args:
            level_or_hvo: Either an ICmPossibility object or its HVO.

        Returns:
            list: List of IWfiAnalysis objects that reference this confidence level.

        Raises:
            FP_NullParameterError: If level_or_hvo is None.

        Example:
            >>> high = project.Confidence.Find("High Confidence")
            >>> analyses = project.Confidence.GetAnalysesWithConfidence(high)
            >>> print(f"Found {len(analyses)} high-confidence analyses")
            Found 127 high-confidence analyses

            >>> # Show analyses for each confidence level
            >>> for level in project.Confidence.GetAll():
            ...     name = project.Confidence.GetName(level)
            ...     analyses = project.Confidence.GetAnalysesWithConfidence(level)
            ...     print(f"{name}: {len(analyses)} analyses")

            >>> # Find analyses that need review
            >>> low = project.Confidence.Find("Low Confidence")
            >>> if low:
            ...     review_list = project.Confidence.GetAnalysesWithConfidence(low)
            ...     for analysis in review_list:
            ...         # Process analyses needing review
            ...         pass

        Notes:
            - Searches through all wordform analyses in the project
            - Returns empty list if no analyses use this confidence level
            - May be slow for large lexicons (searches entire repository)
            - Useful for quality control and validation workflows
            - Use before deleting a confidence level

        See Also:
            GetGlossesWithConfidence, Delete
        """
        if level_or_hvo is None:
            raise FP_NullParameterError()

        level = self.__ResolveObject(level_or_hvo)
        level_hvo = level.Hvo

        analyses = []
        analysis_repo = self.project.project.ServiceLocator.GetInstance(
            IWfiAnalysisRepository
        )

        # Search through all analyses
        for analysis in analysis_repo.AllInstances():
            # Check if this analysis has this confidence level
            # Note: IWfiAnalysis may have Confidence property as reference
            if hasattr(analysis, 'ConfidenceRA') and analysis.ConfidenceRA:
                if analysis.ConfidenceRA.Hvo == level_hvo:
                    analyses.append(analysis)

        return analyses

    def GetGlossesWithConfidence(self, level_or_hvo):
        """
        Get all wordform glosses that use this confidence level.

        Args:
            level_or_hvo: Either an ICmPossibility object or its HVO.

        Returns:
            list: List of IWfiGloss objects that reference this confidence level.

        Raises:
            FP_NullParameterError: If level_or_hvo is None.

        Example:
            >>> high = project.Confidence.Find("High Confidence")
            >>> glosses = project.Confidence.GetGlossesWithConfidence(high)
            >>> print(f"Found {len(glosses)} high-confidence glosses")
            Found 89 high-confidence glosses

            >>> # Show glosses for each confidence level
            >>> for level in project.Confidence.GetAll():
            ...     name = project.Confidence.GetName(level)
            ...     glosses = project.Confidence.GetGlossesWithConfidence(level)
            ...     print(f"{name}: {len(glosses)} glosses")

            >>> # Find glosses that need verification
            >>> unconfirmed = project.Confidence.Find("Unconfirmed")
            >>> if unconfirmed:
            ...     pending = project.Confidence.GetGlossesWithConfidence(unconfirmed)
            ...     for gloss in pending:
            ...         # Process glosses needing verification
            ...         pass

        Notes:
            - Searches through all wordform glosses in the project
            - Returns empty list if no glosses use this confidence level
            - May be slow for large projects (searches entire repository)
            - Useful for tracking translation quality
            - Use before deleting a confidence level

        See Also:
            GetAnalysesWithConfidence, Delete
        """
        if level_or_hvo is None:
            raise FP_NullParameterError()

        level = self.__ResolveObject(level_or_hvo)
        level_hvo = level.Hvo

        glosses = []
        gloss_repo = self.project.project.ServiceLocator.GetInstance(
            IWfiGlossRepository
        )

        # Search through all glosses
        for gloss in gloss_repo.AllInstances():
            # Check if this gloss has this confidence level
            # Note: IWfiGloss may have Confidence property as reference
            if hasattr(gloss, 'ConfidenceRA') and gloss.ConfidenceRA:
                if gloss.ConfidenceRA.Hvo == level_hvo:
                    glosses.append(gloss)

        return glosses

    # --- Special Query Operations ---

    def GetDefault(self):
        """
        Get the default confidence level for the project.

        The default confidence level is typically used for new analyses when
        no specific confidence level is assigned.

        Returns:
            ICmPossibility or None: The default confidence level, or None if not set.

        Example:
            >>> # Get default confidence level
            >>> default = project.Confidence.GetDefault()
            >>> if default:
            ...     name = project.Confidence.GetName(default)
            ...     print(f"Default confidence level: {name}")
            Default confidence level: Medium Confidence

            >>> # Use default for new analysis
            >>> default = project.Confidence.GetDefault()
            >>> if default:
            ...     # Apply to new analysis
            ...     pass

        Notes:
            - Returns None if no default is configured
            - Default is typically the first confidence level in the list
            - Some FLEx configurations may not have a default set
            - Default can be project-specific
            - Consider the first level or "Medium" as conventional defaults

        See Also:
            GetAll, Find
        """
        levels = self.GetAll()
        if not levels:
            return None

        # In FLEx, the first item is often the default
        # Some lists may have an IsDefault flag, but typically use first item
        return levels[0] if levels else None

    # --- Metadata Operations ---

    def GetGuid(self, level_or_hvo):
        """
        Get the GUID (Globally Unique Identifier) of a confidence level.

        Args:
            level_or_hvo: Either an ICmPossibility object or its HVO.

        Returns:
            System.Guid: The confidence level's GUID.

        Raises:
            FP_NullParameterError: If level_or_hvo is None.

        Example:
            >>> level = project.Confidence.Find("High Confidence")
            >>> guid = project.Confidence.GetGuid(level)
            >>> print(guid)
            a1b2c3d4-e5f6-7890-abcd-ef1234567890

            >>> # Use GUID to retrieve level later
            >>> level2 = project.Object(guid)
            >>> print(project.Confidence.GetName(level2))
            High Confidence

            >>> # Store GUID for cross-project references
            >>> import System
            >>> guid_str = str(guid)
            >>> # Later: retrieve using System.Guid.Parse(guid_str)

        Notes:
            - GUIDs are unique across all FLEx projects
            - GUIDs are persistent (don't change across sessions)
            - Useful for linking confidence levels across projects
            - Can be used with FLExProject.Object() to retrieve level
            - Store GUIDs for external references and exports

        See Also:
            FLExProject.Object
        """
        if level_or_hvo is None:
            raise FP_NullParameterError()

        level = self.__ResolveObject(level_or_hvo)
        return level.Guid

    # --- Private Helper Methods ---

    def __ResolveObject(self, level_or_hvo):
        """
        Resolve HVO or object to ICmPossibility.

        Args:
            level_or_hvo: Either an ICmPossibility object or an HVO (int).

        Returns:
            ICmPossibility: The resolved confidence level object.

        Raises:
            FP_ParameterError: If HVO doesn't refer to a confidence level.
        """
        if isinstance(level_or_hvo, int):
            obj = self.project.Object(level_or_hvo)
            if not isinstance(obj, ICmPossibility):
                raise FP_ParameterError(
                    "HVO does not refer to a confidence level (ICmPossibility)"
                )
            return obj
        return level_or_hvo

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
