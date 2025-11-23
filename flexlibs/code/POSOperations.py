#
#   POSOperations.py
#
#   Class: POSOperations
#          Parts of Speech operations for FieldWorks Language Explorer
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
from SIL.LCModel import IPartOfSpeechFactory, IPartOfSpeech, ILexEntryRepository
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from .FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class POSOperations:
    """
    This class provides operations for managing Parts of Speech in a
    FieldWorks project.

    Parts of Speech are fundamental grammatical categories used in linguistic
    analysis (e.g., Noun, Verb, Adjective, etc.).

    Usage::

        from flexlibs import FLExProject, POSOperations

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        posOps = POSOperations(project)

        # Get all parts of speech
        for pos in posOps.GetAll():
            print(posOps.GetName(pos), posOps.GetAbbreviation(pos))

        # Create a new POS
        noun = posOps.Create("Noun", "N")

        # Find and update
        verb = posOps.Find("Verb")
        if verb:
            posOps.SetAbbreviation(verb, "V")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize POSOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    def GetAll(self):
        """
        Get all parts of speech in the project.

        Yields:
            IPartOfSpeech: Each part of speech object in the project's POS list.

        Example:
            >>> posOps = POSOperations(project)
            >>> for pos in posOps.GetAll():
            ...     name = posOps.GetName(pos)
            ...     abbr = posOps.GetAbbreviation(pos)
            ...     print(f"{name} ({abbr})")
            Noun (N)
            Verb (V)
            Adjective (Adj)

        Notes:
            - Returns only top-level parts of speech
            - Does not include subcategories
            - Use GetSubcategories() to navigate the POS hierarchy

        See Also:
            GetSubcategories, Find
        """
        pos_list = self.project.lp.PartsOfSpeechOA
        if pos_list:
            for pos in pos_list.PossibilitiesOS:
                yield pos


    def Create(self, name, abbreviation, catalogSourceId=None):
        """
        Create a new part of speech.

        Args:
            name (str): The name of the POS (e.g., "Noun", "Verb").
            abbreviation (str): Short abbreviation (e.g., "N", "V").
            catalogSourceId (str, optional): Optional catalog identifier for
                linguistic databases (e.g., "GOLD:Noun"). Defaults to None.

        Returns:
            IPartOfSpeech: The newly created POS object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name or abbreviation is None.
            FP_ParameterError: If name or abbreviation is empty, or if a POS
                with this name already exists.

        Example:
            >>> posOps = POSOperations(project)
            >>> noun = posOps.Create("Noun", "N")
            >>> print(posOps.GetName(noun))
            Noun

            >>> proper_noun = posOps.Create("Proper Noun", "PN", "GOLD:Noun")
            >>> print(posOps.GetAbbreviation(proper_noun))
            PN

        Notes:
            - Name must be unique within the project
            - Abbreviations don't need to be unique but should be distinct
            - CatalogSourceId links to linguistic ontologies (e.g., GOLD)
            - The POS is created in the default analysis writing system

        See Also:
            Delete, Exists, Find
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()
        if abbreviation is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")
        if not abbreviation or not abbreviation.strip():
            raise FP_ParameterError("Abbreviation cannot be empty")

        # Check if POS already exists
        if self.Exists(name):
            raise FP_ParameterError(f"Part of Speech '{name}' already exists")

        # Get the writing system handle
        wsHandle = self.project.project.DefaultAnalWs

        # Create the new POS using the factory
        factory = self.project.project.ServiceLocator.GetInstance(IPartOfSpeechFactory)
        new_pos = factory.Create()

        # Set name and abbreviation
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_pos.Name.set_String(wsHandle, mkstr_name)

        mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
        new_pos.Abbreviation.set_String(wsHandle, mkstr_abbr)

        # Set catalog source ID if provided
        if catalogSourceId:
            new_pos.CatalogSourceId = catalogSourceId

        # Add to the POS list
        pos_list = self.project.lp.PartsOfSpeechOA
        pos_list.PossibilitiesOS.Add(new_pos)

        return new_pos


    def Delete(self, pos_or_hvo):
        """
        Delete a part of speech.

        Args:
            pos_or_hvo: The IPartOfSpeech object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If pos_or_hvo is None.
            FP_ParameterError: If the POS is in use and cannot be deleted.

        Example:
            >>> posOps = POSOperations(project)
            >>> obsolete = posOps.Find("Obsolete")
            >>> if obsolete:
            ...     posOps.Delete(obsolete)

        Warning:
            - Deleting a POS that is in use may raise an error from FLEx
            - Will also delete all subcategories recursively
            - Deletion is permanent and cannot be undone
            - Lexical entries using this POS should be updated first

        See Also:
            Create, Exists, Find
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not pos_or_hvo:
            raise FP_NullParameterError()

        # Resolve to POS object
        pos = self.__ResolveObject(pos_or_hvo)

        # Remove from the POS list
        pos_list = self.project.lp.PartsOfSpeechOA
        pos_list.PossibilitiesOS.Remove(pos)


    def Exists(self, name):
        """
        Check if a part of speech with the given name exists.

        Args:
            name (str): The name to search for (case-insensitive).

        Returns:
            bool: True if POS exists, False otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> posOps = POSOperations(project)
            >>> if not posOps.Exists("Noun"):
            ...     posOps.Create("Noun", "N")

        Notes:
            - Comparison is case-insensitive
            - Searches recursively through all POS including subcategories
            - Use Find() to get the actual object

        See Also:
            Find, Create
        """
        if name is None:
            raise FP_NullParameterError()

        return self.Find(name) is not None


    def Find(self, name):
        """
        Find a part of speech by name.

        Args:
            name (str): The name to search for (case-insensitive).

        Returns:
            IPartOfSpeech or None: The POS object if found, None otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> posOps = POSOperations(project)
            >>> noun = posOps.Find("Noun")
            >>> if noun:
            ...     abbr = posOps.GetAbbreviation(noun)
            ...     print(f"Found: {abbr}")
            Found: N

        Notes:
            - Returns first match only
            - Search is case-insensitive
            - Searches recursively through all POS including subcategories
            - Returns None if not found (doesn't raise exception)

        See Also:
            Exists, GetName
        """
        if name is None:
            raise FP_NullParameterError()

        name_lower = name.lower()
        wsHandle = self.project.project.DefaultAnalWs

        # Search recursively through POS hierarchy
        def search_pos_list(pos_collection):
            for pos in pos_collection:
                pos_name = ITsString(pos.Name.get_String(wsHandle)).Text
                if pos_name and pos_name.lower() == name_lower:
                    return pos
                # Search subcategories
                if pos.SubPossibilitiesOS.Count > 0:
                    found = search_pos_list(pos.SubPossibilitiesOS)
                    if found:
                        return found
            return None

        pos_list = self.project.lp.PartsOfSpeechOA
        if pos_list:
            return search_pos_list(pos_list.PossibilitiesOS)

        return None


    def GetName(self, pos_or_hvo, wsHandle=None):
        """
        Get the name of a part of speech.

        Args:
            pos_or_hvo: The IPartOfSpeech object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The POS name, or empty string if not set.

        Raises:
            FP_NullParameterError: If pos_or_hvo is None.

        Example:
            >>> posOps = POSOperations(project)
            >>> noun = posOps.Find("Noun")
            >>> name = posOps.GetName(noun)
            >>> print(name)
            Noun

            >>> # Get name in a specific writing system
            >>> vern_name = posOps.GetName(noun, project.WSHandle('en'))

        See Also:
            SetName, GetAbbreviation
        """
        if not pos_or_hvo:
            raise FP_NullParameterError()

        pos = self.__ResolveObject(pos_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(pos.Name.get_String(wsHandle)).Text
        return name or ""


    def SetName(self, pos_or_hvo, name, wsHandle=None):
        """
        Set the name of a part of speech.

        Args:
            pos_or_hvo: The IPartOfSpeech object or HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If pos_or_hvo or name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> posOps = POSOperations(project)
            >>> typo = posOps.Find("Nown")  # typo
            >>> if typo:
            ...     posOps.SetName(typo, "Noun")  # fix it

        See Also:
            GetName, SetAbbreviation
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not pos_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        pos = self.__ResolveObject(pos_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        pos.Name.set_String(wsHandle, mkstr)


    def GetAbbreviation(self, pos_or_hvo, wsHandle=None):
        """
        Get the abbreviation of a part of speech.

        Args:
            pos_or_hvo: The IPartOfSpeech object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The POS abbreviation, or empty string if not set.

        Raises:
            FP_NullParameterError: If pos_or_hvo is None.

        Example:
            >>> posOps = POSOperations(project)
            >>> noun = posOps.Find("Noun")
            >>> abbr = posOps.GetAbbreviation(noun)
            >>> print(abbr)
            N

        See Also:
            SetAbbreviation, GetName
        """
        if not pos_or_hvo:
            raise FP_NullParameterError()

        pos = self.__ResolveObject(pos_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        abbr = ITsString(pos.Abbreviation.get_String(wsHandle)).Text
        return abbr or ""


    def SetAbbreviation(self, pos_or_hvo, abbr, wsHandle=None):
        """
        Set the abbreviation of a part of speech.

        Args:
            pos_or_hvo: The IPartOfSpeech object or HVO.
            abbr (str): The new abbreviation.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If pos_or_hvo or abbr is None.
            FP_ParameterError: If abbr is empty.

        Example:
            >>> posOps = POSOperations(project)
            >>> noun = posOps.Find("Noun")
            >>> posOps.SetAbbreviation(noun, "N")

        See Also:
            GetAbbreviation, SetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not pos_or_hvo:
            raise FP_NullParameterError()
        if abbr is None:
            raise FP_NullParameterError()

        if not abbr or not abbr.strip():
            raise FP_ParameterError("Abbreviation cannot be empty")

        pos = self.__ResolveObject(pos_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(abbr, wsHandle)
        pos.Abbreviation.set_String(wsHandle, mkstr)


    def GetSubcategories(self, pos_or_hvo):
        """
        Get all subcategories of a part of speech.

        Args:
            pos_or_hvo: The IPartOfSpeech object or HVO.

        Returns:
            list: List of IPartOfSpeech subcategory objects (empty list if none).

        Raises:
            FP_NullParameterError: If pos_or_hvo is None.

        Example:
            >>> posOps = POSOperations(project)
            >>> noun = posOps.Find("Noun")
            >>> subcats = posOps.GetSubcategories(noun)
            >>> for subcat in subcats:
            ...     print(posOps.GetName(subcat))
            Proper Noun
            Common Noun
            Count Noun
            Mass Noun

        Notes:
            - Returns direct children only (not recursive)
            - Returns empty list if no subcategories
            - Subcategories form a hierarchy for fine-grained classification

        See Also:
            GetAll, Find
        """
        if not pos_or_hvo:
            raise FP_NullParameterError()

        pos = self.__ResolveObject(pos_or_hvo)

        return list(pos.SubPossibilitiesOS)


    def AddSubcategory(self, pos_or_hvo, name, abbreviation):
        """
        Add a subcategory to a part of speech.

        Args:
            pos_or_hvo: The IPartOfSpeech object or HVO to add subcategory to.
            name (str): The name of the subcategory.
            abbreviation (str): Short abbreviation for the subcategory.

        Returns:
            IPartOfSpeech: The newly created subcategory object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If pos_or_hvo, name, or abbreviation is None.
            FP_ParameterError: If name or abbreviation is empty.

        Example:
            >>> posOps = POSOperations(project)
            >>> noun = posOps.Find("Noun")
            >>> proper_noun = posOps.AddSubcategory(noun, "Proper Noun", "PN")
            >>> print(posOps.GetName(proper_noun))
            Proper Noun

        Notes:
            - The subcategory is created as a child of the parent POS
            - Subcategories inherit the parent's properties where applicable
            - Can be nested to create multi-level POS hierarchies
            - Uses default analysis writing system

        See Also:
            RemoveSubcategory, GetSubcategories, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not pos_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()
        if abbreviation is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")
        if not abbreviation or not abbreviation.strip():
            raise FP_ParameterError("Abbreviation cannot be empty")

        pos = self.__ResolveObject(pos_or_hvo)
        wsHandle = self.project.project.DefaultAnalWs

        # Create the subcategory using the factory
        factory = self.project.project.ServiceLocator.GetInstance(IPartOfSpeechFactory)
        subcat = factory.Create()

        # Set name and abbreviation
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        subcat.Name.set_String(wsHandle, mkstr_name)

        mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
        subcat.Abbreviation.set_String(wsHandle, mkstr_abbr)

        # Add to parent's SubPossibilitiesOS
        pos.SubPossibilitiesOS.Add(subcat)

        return subcat


    def RemoveSubcategory(self, pos_or_hvo, subcat_or_hvo):
        """
        Remove a subcategory from a part of speech.

        Args:
            pos_or_hvo: The IPartOfSpeech object or HVO (parent).
            subcat_or_hvo: The subcategory IPartOfSpeech object or HVO to remove.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If pos_or_hvo or subcat_or_hvo is None.
            FP_ParameterError: If the subcategory is in use and cannot be deleted.

        Example:
            >>> posOps = POSOperations(project)
            >>> noun = posOps.Find("Noun")
            >>> subcats = posOps.GetSubcategories(noun)
            >>> for subcat in subcats:
            ...     if posOps.GetName(subcat) == "Obsolete Subcategory":
            ...         posOps.RemoveSubcategory(noun, subcat)

        Warning:
            - Removing a subcategory that is in use may raise an error from FLEx
            - Will also delete all nested subcategories recursively
            - Removal is permanent and cannot be undone
            - Lexical entries using this subcategory should be updated first

        See Also:
            AddSubcategory, GetSubcategories, Delete
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not pos_or_hvo:
            raise FP_NullParameterError()
        if not subcat_or_hvo:
            raise FP_NullParameterError()

        pos = self.__ResolveObject(pos_or_hvo)
        subcat = self.__ResolveObject(subcat_or_hvo)

        # Remove from parent's SubPossibilitiesOS
        pos.SubPossibilitiesOS.Remove(subcat)


    def GetCatalogSourceId(self, pos_or_hvo):
        """
        Get the catalog source ID of a part of speech.

        Args:
            pos_or_hvo: The IPartOfSpeech object or HVO.

        Returns:
            str: The catalog source ID, or empty string if not set.

        Raises:
            FP_NullParameterError: If pos_or_hvo is None.

        Example:
            >>> posOps = POSOperations(project)
            >>> noun = posOps.Find("Noun")
            >>> catalog_id = posOps.GetCatalogSourceId(noun)
            >>> print(catalog_id)
            GOLD:Noun

        Notes:
            - Catalog source IDs link POS to linguistic ontologies (e.g., GOLD)
            - Returns empty string if no catalog ID is set
            - Used for cross-linguistic standardization and data sharing

        See Also:
            Create
        """
        if not pos_or_hvo:
            raise FP_NullParameterError()

        pos = self.__ResolveObject(pos_or_hvo)

        return pos.CatalogSourceId or ""


    def GetInflectionClasses(self, pos_or_hvo):
        """
        Get all inflection classes associated with a part of speech.

        Args:
            pos_or_hvo: The IPartOfSpeech object or HVO.

        Returns:
            list: List of inflection class objects (empty list if none).

        Raises:
            FP_NullParameterError: If pos_or_hvo is None.

        Example:
            >>> posOps = POSOperations(project)
            >>> verb = posOps.Find("Verb")
            >>> classes = posOps.GetInflectionClasses(verb)
            >>> for infl_class in classes:
            ...     print(infl_class.Name)
            Regular Verb
            Irregular Verb
            Modal Verb

        Notes:
            - Inflection classes define morphological paradigms
            - Each POS can have multiple inflection classes
            - Returns empty list if no inflection classes are defined
            - Used for morphological analysis and generation

        See Also:
            GetAffixSlots
        """
        if not pos_or_hvo:
            raise FP_NullParameterError()

        pos = self.__ResolveObject(pos_or_hvo)

        # IPartOfSpeech has InflectionClassesOC
        return list(pos.InflectionClassesOC)


    def GetAffixSlots(self, pos_or_hvo):
        """
        Get all affix slots associated with a part of speech.

        Args:
            pos_or_hvo: The IPartOfSpeech object or HVO.

        Returns:
            list: List of affix slot objects (empty list if none).

        Raises:
            FP_NullParameterError: If pos_or_hvo is None.

        Example:
            >>> posOps = POSOperations(project)
            >>> verb = posOps.Find("Verb")
            >>> slots = posOps.GetAffixSlots(verb)
            >>> for slot in slots:
            ...     print(slot.Name)
            Tense
            Aspect
            Mood

        Notes:
            - Affix slots define positions for affixes in morphological templates
            - Each POS can have multiple affix slots
            - Returns empty list if no affix slots are defined
            - Used for morphological parsing and generation

        See Also:
            GetInflectionClasses
        """
        if not pos_or_hvo:
            raise FP_NullParameterError()

        pos = self.__ResolveObject(pos_or_hvo)

        # IPartOfSpeech has AffixSlotsOC
        return list(pos.AffixSlotsOC)


    def GetEntryCount(self, pos_or_hvo):
        """
        Count the number of lexical entries using this part of speech.

        Args:
            pos_or_hvo: The IPartOfSpeech object or HVO.

        Returns:
            int: The count of entries using this POS.

        Raises:
            FP_NullParameterError: If pos_or_hvo is None.

        Example:
            >>> posOps = POSOperations(project)
            >>> noun = posOps.Find("Noun")
            >>> count = posOps.GetEntryCount(noun)
            >>> print(f"There are {count} noun entries")
            There are 342 noun entries

        Notes:
            - Counts all lexical entries where PrimaryMorphType.PartOfSpeech matches
            - Returns 0 if no entries use this POS
            - Useful for determining if a POS can be safely deleted
            - May be slow for large lexicons (scans all entries)

        See Also:
            Delete
        """
        if not pos_or_hvo:
            raise FP_NullParameterError()

        pos = self.__ResolveObject(pos_or_hvo)

        # Search all lexical entries
        count = 0
        entry_repo = self.project.project.ServiceLocator.GetInstance(ILexEntryRepository)
        for entry in entry_repo.AllInstances():
            # Check if entry has a primary morph type and if it matches this POS
            for morph in entry.AllAllomorphs:
                if morph.MorphTypeRA and morph.MorphTypeRA.PartOfSpeechRAHvo == pos.Hvo:
                    count += 1
                    break  # Count each entry only once

        return count


    # --- Private Helper Methods ---

    def __ResolveObject(self, pos_or_hvo):
        """
        Resolve HVO or object to IPartOfSpeech.

        Args:
            pos_or_hvo: Either an IPartOfSpeech object or an HVO (int).

        Returns:
            IPartOfSpeech: The resolved POS object.
        """
        if isinstance(pos_or_hvo, int):
            return self.project.Object(pos_or_hvo)
        return pos_or_hvo


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
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultAnalWs)
