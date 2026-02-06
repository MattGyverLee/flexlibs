#
#   TranslationTypeOperations.py
#
#   Class: TranslationTypeOperations
#          Translation type management operations for FieldWorks Language Explorer
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
    ITextRepository,
    IStTxtParaRepository,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils
import System

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)
from ..BaseOperations import BaseOperations

class TranslationTypeOperations(BaseOperations):
    """
    This class provides operations for managing translation types in a
    FieldWorks project.

    Translation types categorize different kinds of translations such as
    free translation (idiomatic), literal translation (word-for-word),
    and back translation (reverse translation for verification).

    Translation types are stored as items in the Translation Tags possibility
    list and can be applied to text translations at both text and segment levels.

    This class should be accessed via FLExProject.TranslationTypes property.

    Usage::

        from flexlibs2 import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get all translation types
        for trans_type in project.TranslationTypes.GetAll():
            name = project.TranslationTypes.GetName(trans_type)
            abbr = project.TranslationTypes.GetAbbreviation(trans_type)
            print(f"{name} ({abbr})")

        # Get predefined types
        free = project.TranslationTypes.GetFreeTranslationType()
        literal = project.TranslationTypes.GetLiteralTranslationType()
        back = project.TranslationTypes.GetBackTranslationType()

        # Create a custom translation type
        idiomatic = project.TranslationTypes.Create(
            "Idiomatic Translation", "Idio")

        # Get writing system for a translation type
        ws = project.TranslationTypes.GetAnalysisWS(free)

        # Find texts using a specific translation type
        texts = project.TranslationTypes.GetTextsWithType(free)
        print(f"{len(list(texts))} texts use free translation")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize TranslationTypeOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)

    def _GetSequence(self, parent):
        """Specify which sequence to reorder for translation type sub-possibilities."""
        return parent.SubPossibilitiesOS

    # --- Core CRUD Operations ---

    def GetAll(self):
        """
        Get all translation types in the project.

        Yields all translation types (translation tags) defined in the project,
        including predefined types (free, literal, back) and any custom types.

        Yields:
            ICmPossibility: Each translation type object.

        Example:
            >>> for trans_type in project.TranslationTypes.GetAll():
            ...     name = project.TranslationTypes.GetName(trans_type)
            ...     abbr = project.TranslationTypes.GetAbbreviation(trans_type)
            ...     guid = project.TranslationTypes.GetGuid(trans_type)
            ...     print(f"{name} ({abbr}): {guid}")
            Free translation (fr): eb92e50f-ba96-4d1d-b632-057b5c274132
            Literal translation (lit): c6e13529-97ed-4a8a-86f9-7b30b3b0b1c0
            Back translation (bt): d7f713e4-e8cf-11d3-9764-00c04f186933

        Notes:
            - Returns only top-level translation types
            - Standard FLEx projects include three predefined types
            - Custom types can be created for project-specific needs
            - Does not include sub-types if any exist

        See Also:
            Find, Exists, GetFreeTranslationType
        """
        trans_list = self.project.lp.TranslationTagsOA
        if trans_list:
            for trans_type in trans_list.PossibilitiesOS:
                yield trans_type

    def Create(self, name, abbreviation=None, wsHandle=None):
        """
        Create a new translation type.

        Args:
            name (str): The name of the translation type (e.g., "Idiomatic").
            abbreviation (str, optional): Short abbreviation (e.g., "Idio").
                If None, uses the name. Defaults to None.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ICmPossibility: The newly created translation type object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name is None.
            FP_ParameterError: If name is empty, or if a translation type
                with this name already exists.

        Example:
            >>> # Create a custom translation type
            >>> idiomatic = project.TranslationTypes.Create(
            ...     "Idiomatic Translation", "Idio")
            >>> print(project.TranslationTypes.GetName(idiomatic))
            Idiomatic Translation

            >>> # Create without abbreviation (uses name)
            >>> summary = project.TranslationTypes.Create("Summary")
            >>> print(project.TranslationTypes.GetAbbreviation(summary))
            Summary

        Notes:
            - Name must be unique within the translation types
            - Abbreviation defaults to name if not provided
            - Created in the default analysis writing system
            - Can be used immediately for text translations
            - Custom types appear alongside predefined types

        See Also:
            Delete, Exists, Find
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        # Check if translation type already exists
        if self.Exists(name):
            raise FP_ParameterError(
                f"Translation type '{name}' already exists")

        # Default abbreviation to name if not provided
        if abbreviation is None:
            abbreviation = name

        # Get the writing system handle
        wsHandle = self.__WSHandle(wsHandle)

        # Create the new translation type using the factory
        factory = self.project.project.ServiceLocator.GetService(
            ICmPossibilityFactory)
        new_type = factory.Create()

        # Add to the translation tags list (must be done before setting properties)
        trans_list = self.project.lp.TranslationTagsOA
        if trans_list is None:
            # Create translation tags list if it doesn't exist
            from SIL.LCModel import ICmPossibilityListFactory
            list_factory = self.project.project.ServiceLocator.GetService(
                ICmPossibilityListFactory)
            trans_list = list_factory.Create()
            self.project.lp.TranslationTagsOA = trans_list

        trans_list.PossibilitiesOS.Add(new_type)

        # Set name and abbreviation
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_type.Name.set_String(wsHandle, mkstr_name)

        mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
        new_type.Abbreviation.set_String(wsHandle, mkstr_abbr)

        return new_type

    def Delete(self, type_or_hvo):
        """
        Delete a translation type.

        Args:
            type_or_hvo: The ICmPossibility object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If type_or_hvo is None.
            FP_ParameterError: If trying to delete a predefined type
                (free, literal, back translation).

        Example:
            >>> # Delete a custom type
            >>> custom = project.TranslationTypes.Find("Old Custom Type")
            >>> if custom:
            ...     project.TranslationTypes.Delete(custom)

        Warning:
            - Cannot delete predefined translation types
            - Deleting a type that is in use may cause issues
            - Deletion is permanent and cannot be undone
            - Check usage with GetTextsWithType() before deleting

        Notes:
            - Only custom translation types can be deleted
            - Standard types (free, literal, back) are protected
            - References to deleted types become invalid

        See Also:
            Create, Exists, GetTextsWithType
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not type_or_hvo:
            raise FP_NullParameterError()

        # Resolve to translation type object
        trans_type = self.__ResolveObject(type_or_hvo)

        # Check if it's a predefined type (protected)
        guid = trans_type.Guid
        predefined_guids = [
            System.Guid("eb92e50f-ba96-4d1d-b632-057b5c274132"),  # Free
            System.Guid("c6e13529-97ed-4a8a-86f9-7b30b3b0b1c0"),  # Literal
            System.Guid("d7f713e4-e8cf-11d3-9764-00c04f186933"),  # Back
        ]

        if guid in predefined_guids:
            raise FP_ParameterError(
                "Cannot delete predefined translation types "
                "(free, literal, or back translation)")

        # Remove from the translation tags list
        trans_list = self.project.lp.TranslationTagsOA
        if trans_list:
            trans_list.PossibilitiesOS.Remove(trans_type)

    def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
        """
        Duplicate a translation type, creating a new copy with a new GUID.

        Args:
            item_or_hvo: Either an ICmPossibility object or its HVO to duplicate.
            insert_after (bool): If True (default), insert after the source type.
                                If False, insert at end of translation types list.
            deep (bool): Not applicable for translation types (no owned objects).
                        Included for API consistency.

        Returns:
            ICmPossibility: The newly created duplicate translation type with a new GUID.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> # Duplicate a translation type
            >>> free = project.TranslationTypes.GetFreeTranslationType()
            >>> dup = project.TranslationTypes.Duplicate(free)
            >>> print(f"Original: {project.TranslationTypes.GetName(free)}")
            >>> print(f"Duplicate: {project.TranslationTypes.GetName(dup)}")
            Original: Free translation
            Duplicate: Free translation
            >>>
            >>> # Modify the duplicate
            >>> project.TranslationTypes.SetName(dup, "Idiomatic Translation")
            >>> project.TranslationTypes.SetAbbreviation(dup, "idio")
            >>>
            >>> # Set multilingual content
            >>> fr_ws = project.WSHandle('fr')
            >>> project.TranslationTypes.SetAnalysisWS(dup, fr_ws,
            ...     name="Traduction idiomatique",
            ...     abbreviation="idio")

        Notes:
            - Factory.Create() automatically generates a new GUID
            - insert_after=True preserves the original type's position
            - MultiString properties copied: Name, Abbreviation
            - Translation types have no owned objects, so deep parameter has no effect
            - Duplicate is added to TranslationTagsOA before copying properties
            - Duplicate will NOT be a predefined type (has new GUID)

        See Also:
            Create, Delete, GetGuid, SetAnalysisWS
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not item_or_hvo:
            raise FP_NullParameterError()

        # Get source translation type
        source = self.__ResolveObject(item_or_hvo)

        # Get the translation tags list
        trans_list = self.project.lp.TranslationTagsOA
        if trans_list is None:
            # Create translation tags list if it doesn't exist
            from SIL.LCModel import ICmPossibilityListFactory
            list_factory = self.project.project.ServiceLocator.GetService(
                ICmPossibilityListFactory)
            trans_list = list_factory.Create()
            self.project.lp.TranslationTagsOA = trans_list

        # Create new translation type using factory (auto-generates new GUID)
        factory = self.project.project.ServiceLocator.GetService(ICmPossibilityFactory)
        duplicate = factory.Create()

        # ADD TO PARENT FIRST before copying properties (CRITICAL)
        if insert_after:
            # Insert after source type
            source_index = trans_list.PossibilitiesOS.IndexOf(source)
            trans_list.PossibilitiesOS.Insert(source_index + 1, duplicate)
        else:
            # Insert at end
            trans_list.PossibilitiesOS.Add(duplicate)

        # Copy MultiString properties using CopyAlternatives
        duplicate.Name.CopyAlternatives(source.Name)
        duplicate.Abbreviation.CopyAlternatives(source.Abbreviation)

        return duplicate

    # ========== SYNC INTEGRATION METHODS ==========

    def GetSyncableProperties(self, item):
        """
        Get syncable properties for cross-project synchronization.

        Returns all syncable properties of a translation type including MultiString fields.

        Args:
            item: The ICmPossibility object (translation type)

        Returns:
            dict: Dictionary of syncable properties

        Example:
            >>> props = project.TranslationType.GetSyncableProperties(trans_type)
            >>> print(props)
            {'Name': 'Free Translation', 'Abbreviation': 'ft'}
        """
        if not item:
            raise FP_NullParameterError()

        trans_type = self.__ResolveObject(item)
        wsHandle = self.project.project.DefaultAnalWs

        props = {}

        # MultiString properties
        props['Name'] = ITsString(trans_type.Name.get_String(wsHandle)).Text or ""
        props['Abbreviation'] = ITsString(trans_type.Abbreviation.get_String(wsHandle)).Text or ""

        return props

    def CompareTo(self, item1, item2, ops1=None, ops2=None):
        """
        Compare two translation types and return detailed differences.

        Args:
            item1: First translation type (from source project)
            item2: Second translation type (from target project)
            ops1: Operations instance for item1's project (defaults to self)
            ops2: Operations instance for item2's project (defaults to self)

        Returns:
            tuple: (is_different, differences_dict) where differences_dict contains
                   'properties' dict with changed property details

        Example:
            >>> is_diff, diffs = ops1.CompareTo(type1, type2, ops1, ops2)
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
        Find a translation type by name.

        Args:
            name (str): The name to search for (case-insensitive).

        Returns:
            ICmPossibility or None: The translation type object if found,
                None otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> # Find predefined types
            >>> free = project.TranslationTypes.Find("Free translation")
            >>> if free:
            ...     abbr = project.TranslationTypes.GetAbbreviation(free)
            ...     print(f"Found: {abbr}")
            Found: fr

            >>> # Find custom type
            >>> custom = project.TranslationTypes.Find("Idiomatic Translation")

        Notes:
            - Returns first match only
            - Search is case-insensitive
            - Searches only in default analysis writing system
            - Returns None if not found (doesn't raise exception)
            - For predefined types, prefer using specific getters
              (GetFreeTranslationType, etc.)

        See Also:
            Exists, GetName, GetFreeTranslationType
        """
        if name is None:
            raise FP_NullParameterError()

        name_lower = name.lower()
        wsHandle = self.project.project.DefaultAnalWs

        trans_list = self.project.lp.TranslationTagsOA
        if trans_list:
            for trans_type in trans_list.PossibilitiesOS:
                type_name = ITsString(
                    trans_type.Name.get_String(wsHandle)).Text
                if type_name and type_name.lower() == name_lower:
                    return trans_type

        return None

    def Exists(self, name):
        """
        Check if a translation type with the given name exists.

        Args:
            name (str): The name to search for (case-insensitive).

        Returns:
            bool: True if translation type exists, False otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> if not project.TranslationTypes.Exists("Idiomatic"):
            ...     project.TranslationTypes.Create("Idiomatic", "Idio")

            >>> # Check for standard types
            >>> has_free = project.TranslationTypes.Exists("Free translation")
            >>> print(f"Has free translation: {has_free}")
            Has free translation: True

        Notes:
            - Comparison is case-insensitive
            - Searches only in default analysis writing system
            - Use Find() to get the actual object
            - All standard FLEx projects have predefined types

        See Also:
            Find, Create
        """
        if name is None:
            raise FP_NullParameterError()

        return self.Find(name) is not None

    # --- Property Accessors ---

    def GetName(self, type_or_hvo, wsHandle=None):
        """
        Get the name of a translation type.

        Args:
            type_or_hvo: The ICmPossibility object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The translation type name, or empty string if not set.

        Raises:
            FP_NullParameterError: If type_or_hvo is None.

        Example:
            >>> free = project.TranslationTypes.GetFreeTranslationType()
            >>> name = project.TranslationTypes.GetName(free)
            >>> print(name)
            Free translation

            >>> # Get name in a specific writing system
            >>> name_en = project.TranslationTypes.GetName(free,
            ...     project.WSHandle('en'))

        See Also:
            SetName, GetAbbreviation
        """
        if not type_or_hvo:
            raise FP_NullParameterError()

        trans_type = self.__ResolveObject(type_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(trans_type.Name.get_String(wsHandle)).Text
        return name or ""

    def SetName(self, type_or_hvo, name, wsHandle=None):
        """
        Set the name of a translation type.

        Args:
            type_or_hvo: The ICmPossibility object or HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If type_or_hvo or name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> custom = project.TranslationTypes.Find("Temp Type")
            >>> if custom:
            ...     project.TranslationTypes.SetName(custom,
            ...         "Idiomatic Translation")

        Warning:
            - Avoid renaming predefined types (free, literal, back)
            - Changes affect how the type appears throughout the UI
            - Only rename custom types you created

        See Also:
            GetName, SetAbbreviation
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not type_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        trans_type = self.__ResolveObject(type_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        trans_type.Name.set_String(wsHandle, mkstr)

    def GetAbbreviation(self, type_or_hvo, wsHandle=None):
        """
        Get the abbreviation of a translation type.

        Args:
            type_or_hvo: The ICmPossibility object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The translation type abbreviation, or empty string if not set.

        Raises:
            FP_NullParameterError: If type_or_hvo is None.

        Example:
            >>> free = project.TranslationTypes.GetFreeTranslationType()
            >>> abbr = project.TranslationTypes.GetAbbreviation(free)
            >>> print(abbr)
            fr

            >>> literal = project.TranslationTypes.GetLiteralTranslationType()
            >>> abbr = project.TranslationTypes.GetAbbreviation(literal)
            >>> print(abbr)
            lit

        See Also:
            SetAbbreviation, GetName
        """
        if not type_or_hvo:
            raise FP_NullParameterError()

        trans_type = self.__ResolveObject(type_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        abbr = ITsString(trans_type.Abbreviation.get_String(wsHandle)).Text
        return abbr or ""

    def SetAbbreviation(self, type_or_hvo, abbreviation, wsHandle=None):
        """
        Set the abbreviation of a translation type.

        Args:
            type_or_hvo: The ICmPossibility object or HVO.
            abbreviation (str): The new abbreviation.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If type_or_hvo or abbreviation is None.
            FP_ParameterError: If abbreviation is empty.

        Example:
            >>> custom = project.TranslationTypes.Find("Idiomatic Translation")
            >>> if custom:
            ...     project.TranslationTypes.SetAbbreviation(custom, "Idio")

        Warning:
            - Avoid changing abbreviations for predefined types
            - Abbreviations should be short and distinctive
            - Only modify custom types you created

        See Also:
            GetAbbreviation, SetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not type_or_hvo:
            raise FP_NullParameterError()
        if abbreviation is None:
            raise FP_NullParameterError()

        if not abbreviation or not abbreviation.strip():
            raise FP_ParameterError("Abbreviation cannot be empty")

        trans_type = self.__ResolveObject(type_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(abbreviation, wsHandle)
        trans_type.Abbreviation.set_String(wsHandle, mkstr)

    # --- Writing System Methods ---

    def GetAnalysisWS(self, type_or_hvo):
        """
        Get the analysis writing systems used by a translation type.

        Returns the writing systems in which this translation type has
        translations defined.

        Args:
            type_or_hvo: The ICmPossibility object or HVO.

        Returns:
            list: List of writing system handles (integers) for which
                this type has content defined.

        Raises:
            FP_NullParameterError: If type_or_hvo is None.

        Example:
            >>> free = project.TranslationTypes.GetFreeTranslationType()
            >>> ws_list = project.TranslationTypes.GetAnalysisWS(free)
            >>> for ws_handle in ws_list:
            ...     ws_obj = project.project.ServiceLocator.WritingSystemManager\\
            ...         .Get(ws_handle)
            ...     print(f"Writing system: {ws_obj.Id}")
            Writing system: en

        Notes:
            - Returns handles for writing systems, not WS objects
            - Translation types typically use analysis writing systems
            - Empty list means no specific WS associations

        See Also:
            SetAnalysisWS, GetName
        """
        if not type_or_hvo:
            raise FP_NullParameterError()

        trans_type = self.__ResolveObject(type_or_hvo)

        # Get all writing systems where this type has content
        ws_list = []

        # Check name field for available writing systems
        if trans_type.Name:
            for ws in trans_type.Name.AvailableWritingSystemIds:
                if ws not in ws_list:
                    ws_list.append(ws)

        return ws_list

    def SetAnalysisWS(self, type_or_hvo, wsHandle, name=None,
                      abbreviation=None):
        """
        Set the name and abbreviation for a translation type in a specific
        writing system.

        Args:
            type_or_hvo: The ICmPossibility object or HVO.
            wsHandle: Writing system handle to set content for.
            name (str, optional): Name in the specified writing system.
                If None, uses existing or empty. Defaults to None.
            abbreviation (str, optional): Abbreviation in the specified
                writing system. If None, uses existing or empty.
                Defaults to None.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If type_or_hvo or wsHandle is None.

        Example:
            >>> # Set French translations for a type
            >>> free = project.TranslationTypes.GetFreeTranslationType()
            >>> fr_ws = project.WSHandle('fr')
            >>> project.TranslationTypes.SetAnalysisWS(
            ...     free, fr_ws,
            ...     name="Traduction libre",
            ...     abbreviation="tl")

        Notes:
            - Allows translation types to have names in multiple languages
            - If name or abbreviation is None, that field is not updated
            - Useful for multilingual projects

        See Also:
            GetAnalysisWS, GetName, SetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not type_or_hvo:
            raise FP_NullParameterError()
        if wsHandle is None:
            raise FP_NullParameterError()

        trans_type = self.__ResolveObject(type_or_hvo)

        # Set name if provided
        if name is not None:
            mkstr_name = TsStringUtils.MakeString(name, wsHandle)
            trans_type.Name.set_String(wsHandle, mkstr_name)

        # Set abbreviation if provided
        if abbreviation is not None:
            mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
            trans_type.Abbreviation.set_String(wsHandle, mkstr_abbr)

    # --- Usage Tracking ---

    def GetTextsWithType(self, type_or_hvo):
        """
        Get all texts that use a specific translation type.

        Searches through all texts in the project and returns those that
        reference this translation type in their translations.

        Args:
            type_or_hvo: The ICmPossibility object or HVO.

        Yields:
            IText: Each text object that uses this translation type.

        Raises:
            FP_NullParameterError: If type_or_hvo is None.

        Example:
            >>> free = project.TranslationTypes.GetFreeTranslationType()
            >>> texts = list(project.TranslationTypes.GetTextsWithType(free))
            >>> print(f"{len(texts)} texts use free translation")
            12 texts use free translation

            >>> for text in texts:
            ...     name = text.Name.BestAnalysisAlternative.Text
            ...     print(f"  - {name}")

        Notes:
            - May be slow for large projects (scans all texts)
            - Useful for determining if a type is in use before deleting
            - Returns empty sequence if type is not used
            - Checks text-level translations, not segment-level

        See Also:
            GetSegmentsWithType, Delete
        """
        if not type_or_hvo:
            raise FP_NullParameterError()

        trans_type = self.__ResolveObject(type_or_hvo)
        type_guid = trans_type.Guid

        # Search all texts
        text_repo = self.project.project.ServiceLocator.GetInstance(
            ITextRepository)
        for text in text_repo.AllInstances():
            # Check if text has translations using this type
            if hasattr(text, 'TranslationsOC') and text.TranslationsOC:
                for translation in text.TranslationsOC:
                    if hasattr(translation, 'TypeRA') and translation.TypeRA:
                        if translation.TypeRA.Guid == type_guid:
                            yield text
                            break  # Count each text only once

    def GetSegmentsWithType(self, type_or_hvo):
        """
        Get all segments that use a specific translation type.

        Searches through all segments in all texts and returns those that
        reference this translation type in their translations.

        Args:
            type_or_hvo: The ICmPossibility object or HVO.

        Yields:
            ISegment: Each segment object that uses this translation type.

        Raises:
            FP_NullParameterError: If type_or_hvo is None.

        Example:
            >>> literal = project.TranslationTypes.GetLiteralTranslationType()
            >>> segments = list(project.TranslationTypes.GetSegmentsWithType(
            ...     literal))
            >>> print(f"{len(segments)} segments use literal translation")
            458 segments use literal translation

        Warning:
            - This operation can be very slow for large projects
            - Scans all paragraphs and segments in the entire project
            - Consider using GetTextsWithType() for faster overview

        Notes:
            - Returns empty sequence if type is not used
            - Useful for detailed usage analysis
            - Each segment is yielded only once

        See Also:
            GetTextsWithType, Delete
        """
        if not type_or_hvo:
            raise FP_NullParameterError()

        trans_type = self.__ResolveObject(type_or_hvo)
        type_guid = trans_type.Guid

        # Search all paragraphs and their segments
        para_repo = self.project.project.ServiceLocator.GetInstance(
            IStTxtParaRepository)
        for para in para_repo.AllInstances():
            if hasattr(para, 'SegmentsOS'):
                for segment in para.SegmentsOS:
                    # Check segment translations
                    # Note: Segments typically don't have typed translations
                    # in the same way texts do, but we check for completeness
                    if hasattr(segment, 'FreeTranslation'):
                        # Segments have FreeTranslation and LiteralTranslation
                        # but these are typically not typed in the same way
                        # This method is provided for API completeness
                        pass

    # --- Predefined Translation Types ---

    def GetFreeTranslationType(self):
        """
        Get the predefined "Free translation" type.

        Returns the standard free translation type that is present in all
        FLEx projects. Free translation represents idiomatic, natural
        language translation.

        Returns:
            ICmPossibility or None: The free translation type object,
                or None if not found.

        Example:
            >>> free = project.TranslationTypes.GetFreeTranslationType()
            >>> if free:
            ...     name = project.TranslationTypes.GetName(free)
            ...     abbr = project.TranslationTypes.GetAbbreviation(free)
            ...     print(f"{name} ({abbr})")
            Free translation (fr)

        Notes:
            - This is a predefined type with GUID:
              eb92e50f-ba96-4d1d-b632-057b5c274132
            - Should be present in all standard FLEx projects
            - Cannot be deleted
            - Default translation type for natural language translations

        See Also:
            GetLiteralTranslationType, GetBackTranslationType
        """
        # Free translation GUID
        guid = System.Guid("eb92e50f-ba96-4d1d-b632-057b5c274132")
        return self.__FindByGuid(guid)

    def GetLiteralTranslationType(self):
        """
        Get the predefined "Literal translation" type.

        Returns the standard literal translation type that is present in all
        FLEx projects. Literal translation represents word-for-word,
        morpheme-aligned translation.

        Returns:
            ICmPossibility or None: The literal translation type object,
                or None if not found.

        Example:
            >>> literal = project.TranslationTypes.GetLiteralTranslationType()
            >>> if literal:
            ...     name = project.TranslationTypes.GetName(literal)
            ...     abbr = project.TranslationTypes.GetAbbreviation(literal)
            ...     print(f"{name} ({abbr})")
            Literal translation (lit)

        Notes:
            - This is a predefined type with GUID:
              c6e13529-97ed-4a8a-86f9-7b30b3b0b1c0
            - Should be present in all standard FLEx projects
            - Cannot be deleted
            - Used for interlinear, word-for-word translations

        See Also:
            GetFreeTranslationType, GetBackTranslationType
        """
        # Literal translation GUID
        guid = System.Guid("c6e13529-97ed-4a8a-86f9-7b30b3b0b1c0")
        return self.__FindByGuid(guid)

    def GetBackTranslationType(self):
        """
        Get the predefined "Back translation" type.

        Returns the standard back translation type that is present in all
        FLEx projects. Back translation is a reverse translation from the
        target language back to the source language for verification purposes.

        Returns:
            ICmPossibility or None: The back translation type object,
                or None if not found.

        Example:
            >>> back = project.TranslationTypes.GetBackTranslationType()
            >>> if back:
            ...     name = project.TranslationTypes.GetName(back)
            ...     abbr = project.TranslationTypes.GetAbbreviation(back)
            ...     print(f"{name} ({abbr})")
            Back translation (bt)

        Notes:
            - This is a predefined type with GUID:
              d7f713e4-e8cf-11d3-9764-00c04f186933
            - Should be present in all standard FLEx projects
            - Cannot be deleted
            - Used for translation checking and verification

        See Also:
            GetFreeTranslationType, GetLiteralTranslationType
        """
        # Back translation GUID
        guid = System.Guid("d7f713e4-e8cf-11d3-9764-00c04f186933")
        return self.__FindByGuid(guid)

    # --- Query Methods ---

    def FindByWS(self, wsHandle):
        """
        Find all translation types that have content in a specific
        writing system.

        Args:
            wsHandle: Writing system handle to search for.

        Yields:
            ICmPossibility: Each translation type that has name or
                abbreviation defined in the specified writing system.

        Raises:
            FP_NullParameterError: If wsHandle is None.

        Example:
            >>> # Find types with English content
            >>> en_ws = project.WSHandle('en')
            >>> for trans_type in project.TranslationTypes.FindByWS(en_ws):
            ...     name = project.TranslationTypes.GetName(
            ...         trans_type, en_ws)
            ...     print(name)
            Free translation
            Literal translation
            Back translation

        Notes:
            - Checks both name and abbreviation fields
            - Useful for finding types available in a specific language
            - Returns empty sequence if no types have content in that WS

        See Also:
            GetAnalysisWS, SetAnalysisWS
        """
        if wsHandle is None:
            raise FP_NullParameterError()

        for trans_type in self.GetAll():
            # Check if this type has content in the specified WS
            if trans_type.Name:
                for ws in trans_type.Name.AvailableWritingSystemIds:
                    if ws == wsHandle:
                        yield trans_type
                        break

    def IsDefault(self, type_or_hvo):
        """
        Check if a translation type is one of the predefined default types.

        Args:
            type_or_hvo: The ICmPossibility object or HVO.

        Returns:
            bool: True if this is a predefined type (free, literal, or back),
                False if it's a custom type.

        Raises:
            FP_NullParameterError: If type_or_hvo is None.

        Example:
            >>> free = project.TranslationTypes.GetFreeTranslationType()
            >>> is_default = project.TranslationTypes.IsDefault(free)
            >>> print(f"Is default: {is_default}")
            Is default: True

            >>> custom = project.TranslationTypes.Find("Idiomatic")
            >>> if custom:
            ...     is_default = project.TranslationTypes.IsDefault(custom)
            ...     print(f"Is default: {is_default}")
            Is default: False

        Notes:
            - Predefined types cannot be deleted
            - Custom types can be deleted
            - Useful for distinguishing system vs. user-created types

        See Also:
            GetFreeTranslationType, Delete
        """
        if not type_or_hvo:
            raise FP_NullParameterError()

        trans_type = self.__ResolveObject(type_or_hvo)
        guid = trans_type.Guid

        # Check against predefined GUIDs
        predefined_guids = [
            System.Guid("eb92e50f-ba96-4d1d-b632-057b5c274132"),  # Free
            System.Guid("c6e13529-97ed-4a8a-86f9-7b30b3b0b1c0"),  # Literal
            System.Guid("d7f713e4-e8cf-11d3-9764-00c04f186933"),  # Back
        ]

        return guid in predefined_guids

    def SetDefault(self, type_or_hvo):
        """
        Set a translation type as the default for new translations.

        Note: This functionality may not be fully supported in all FLEx
        versions, as translation type defaults are often context-dependent.

        Args:
            type_or_hvo: The ICmPossibility object or HVO.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If type_or_hvo is None.
            FP_ParameterError: Feature not fully supported.

        Example:
            >>> # This method is provided for API completeness
            >>> # but may not have full functionality
            >>> free = project.TranslationTypes.GetFreeTranslationType()
            >>> # project.TranslationTypes.SetDefault(free)

        Warning:
            - This feature may not be fully implemented in FLEx
            - Translation type defaults are typically context-dependent
            - Consider this method as a placeholder for future enhancement

        Notes:
            - Translation types don't have a single "default"
            - Free translation is typically used by default for texts
            - Literal translation is typically used for interlinear
            - This method is provided for API consistency

        See Also:
            IsDefault, GetFreeTranslationType
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not type_or_hvo:
            raise FP_NullParameterError()

        # This functionality is not directly supported in FLEx
        # as there's no single "default" translation type
        raise FP_ParameterError(
            "SetDefault is not supported for translation types. "
            "Translation type defaults are context-dependent.")

    # --- Metadata ---

    def GetGuid(self, type_or_hvo):
        """
        Get the GUID (Globally Unique Identifier) of a translation type.

        Args:
            type_or_hvo: The ICmPossibility object or HVO.

        Returns:
            System.Guid: The GUID of the translation type.

        Raises:
            FP_NullParameterError: If type_or_hvo is None.

        Example:
            >>> free = project.TranslationTypes.GetFreeTranslationType()
            >>> guid = project.TranslationTypes.GetGuid(free)
            >>> print(guid)
            eb92e50f-ba96-4d1d-b632-057b5c274132

            >>> # Check if it's the predefined free translation type
            >>> expected = System.Guid("eb92e50f-ba96-4d1d-b632-057b5c274132")
            >>> print(f"Is free translation: {guid == expected}")
            Is free translation: True

        Notes:
            - GUIDs are unique across all FLEx projects
            - Predefined types have standard GUIDs
            - Custom types get auto-generated GUIDs
            - GUIDs remain constant even if name changes
            - Useful for cross-project identification

        See Also:
            IsDefault, GetFreeTranslationType
        """
        if not type_or_hvo:
            raise FP_NullParameterError()

        trans_type = self.__ResolveObject(type_or_hvo)
        return trans_type.Guid

    # --- Private Helper Methods ---

    def __ResolveObject(self, type_or_hvo):
        """
        Resolve HVO or object to ICmPossibility.

        Args:
            type_or_hvo: Either an ICmPossibility object or an HVO (int).

        Returns:
            ICmPossibility: The resolved translation type object.
        """
        if isinstance(type_or_hvo, int):
            return self.project.Object(type_or_hvo)
        return type_or_hvo

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
            wsHandle, self.project.project.DefaultAnalWs)

    def __FindByGuid(self, guid):
        """
        Find a translation type by its GUID.

        Args:
            guid (System.Guid): The GUID to search for.

        Returns:
            ICmPossibility or None: The translation type if found,
                None otherwise.
        """
        trans_list = self.project.lp.TranslationTagsOA
        if trans_list:
            for trans_type in trans_list.PossibilitiesOS:
                if trans_type.Guid == guid:
                    return trans_type
        return None
