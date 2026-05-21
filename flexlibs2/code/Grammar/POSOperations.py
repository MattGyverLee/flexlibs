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

# Import BaseOperations parent class and decorators
from ..BaseOperations import BaseOperations, OperationsMethod, wrap_enumerable

# Import FLEx LCM types
from SIL.LCModel import IPartOfSpeechFactory, IPartOfSpeech, ILexEntryRepository
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# .NET Guid for catalog-driven creation
import System

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ParameterError,
)

# Import LCM casting utilities for pythonnet interface casting
from ..lcm_casting import cast_to_concrete, get_pos_from_msa

# Import string utilities
from ..Shared.string_utils import normalize_text, normalize_match_key

# Catalog (GOLDEtic) parsing helpers
from ..Shared.catalog import (
    CatalogImportResult,
    find_catalog_entry,
    find_catalog_file,
    parse_etic_catalog,
)


class POSOperations(BaseOperations):
    """
    This class provides operations for managing Parts of Speech in a
    FieldWorks project.

    Parts of Speech are fundamental grammatical categories used in linguistic
    analysis (e.g., Noun, Verb, Adjective, etc.).

    Usage::

        from flexlibs2 import FLExProject, POSOperations

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
        super().__init__(project)

    def _GetSequence(self, parent):
        """
        Specify which sequence to reorder for POS.
        For POS, we reorder parent.SubPossibilitiesOS
        """
        return parent.SubPossibilitiesOS

    @wrap_enumerable
    @OperationsMethod
    def GetAll(self):
        """
        Get all parts of speech in the project.

        Can be called two ways:
            POSOperations.GetAll(project)         # Class-level, no instantiation
            POSOperations(project).GetAll()       # Instance-level, traditional

        Yields:
            IPartOfSpeech: Each part of speech object in the project's POS list.

        Example:
            >>> # Class-level usage (no instantiation needed)
            >>> for pos in POSOperations.GetAll(project):
            ...     name = POSOperations.GetName(project, pos)
            ...     print(name)

            >>> # Instance-level usage (traditional)
            >>> posOps = POSOperations(project)
            >>> for pos in posOps.GetAll():
            ...     name = posOps.GetName(pos)
            ...     print(name)

        Notes:
            - Returns only top-level parts of speech
            - Does not include subcategories
            - Use GetSubcategories() to navigate the POS hierarchy

        See Also:
            GetSubcategories, Find
        """
        pos_list = self.project.lp.PartsOfSpeechOA
        if pos_list:
            # PossibilitiesOS is typed ICmPossibility in C#; cast to
            # IPartOfSpeech so callers can access POS-specific properties.
            for pos in pos_list.PossibilitiesOS:
                yield IPartOfSpeech(pos)

    @OperationsMethod
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
        self._EnsureWriteEnabled()

        self._ValidateParam(name, "name")
        self._ValidateParam(abbreviation, "abbreviation")

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")
        if not abbreviation or not abbreviation.strip():
            raise FP_ParameterError("Abbreviation cannot be empty")

        # If the caller supplied a "GOLD:..." catalog id, defer to the
        # catalog path so the POS gets the canonical GUID and any extra
        # WS data the catalog provides. We then overlay the user's
        # name/abbreviation on top so explicit args still win.
        if catalogSourceId and catalogSourceId.upper().startswith("GOLD:"):
            wsHandle = self.project.project.DefaultAnalWs
            new_pos = self.CreateFromCatalog(catalogSourceId)
            # Overlay user-supplied name and abbreviation in the
            # analysis WS (catalog values stay in other WSes).
            mkstr_name = TsStringUtils.MakeString(name, wsHandle)
            new_pos.Name.set_String(wsHandle, mkstr_name)
            mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
            new_pos.Abbreviation.set_String(wsHandle, mkstr_abbr)
            return new_pos

        # Check if POS already exists
        if self.Exists(name):
            raise FP_ParameterError(f"Part of Speech '{name}' already exists")

        # Get the writing system handle
        wsHandle = self.project.project.DefaultAnalWs

        # Create the new POS using the factory
        factory = self.project.project.ServiceLocator.GetService(IPartOfSpeechFactory)
        new_pos = factory.Create()

        # Add to the POS list (must be done before setting properties)
        pos_list = self.project.lp.PartsOfSpeechOA
        pos_list.PossibilitiesOS.Add(new_pos)

        # Set name and abbreviation
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_pos.Name.set_String(wsHandle, mkstr_name)

        mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
        new_pos.Abbreviation.set_String(wsHandle, mkstr_abbr)

        # Set catalog source ID if provided
        if catalogSourceId:
            new_pos.CatalogSourceId = catalogSourceId

        return new_pos

    @OperationsMethod
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
        self._EnsureWriteEnabled()

        self._ValidateParam(pos_or_hvo, "pos_or_hvo")

        # Resolve to POS object
        pos = self.__ResolveObject(pos_or_hvo)

        # Remove from the POS list
        pos_list = self.project.lp.PartsOfSpeechOA
        pos_list.PossibilitiesOS.Remove(pos)

    @OperationsMethod
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
        self._ValidateParam(name, "name")

        return self.Find(name) is not None

    @OperationsMethod
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
        self._ValidateParam(name, "name")

        target = normalize_match_key(name, casefold=True)
        wsHandle = self.project.project.DefaultAnalWs

        # Search recursively through POS hierarchy
        def search_pos_list(pos_collection):
            for pos in pos_collection:
                pos_name = ITsString(pos.Name.get_String(wsHandle)).Text
                if normalize_match_key(pos_name, casefold=True) == target:
                    return pos
                # Search subcategories
                if pos.SubPossibilitiesOS.Count > 0:
                    found = search_pos_list(pos.SubPossibilitiesOS)
                    if found:
                        return found
            return None

        pos_list = self.project.lp.PartsOfSpeechOA
        if pos_list:
            found = search_pos_list(pos_list.PossibilitiesOS)
            # search_pos_list walks Possibilities/SubPossibilities collections
            # which are typed ICmPossibility; cast the result so callers can
            # access IPartOfSpeech-specific properties.
            return IPartOfSpeech(found) if found is not None else None

        return None

    @OperationsMethod
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
        self._ValidateParam(pos_or_hvo, "pos_or_hvo")

        pos = self.__ResolveObject(pos_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(pos.Name.get_String(wsHandle)).Text
        return name or ""

    @OperationsMethod
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
        self._EnsureWriteEnabled()

        self._ValidateParam(pos_or_hvo, "pos_or_hvo")
        self._ValidateParam(name, "name")

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        pos = self.__ResolveObject(pos_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        pos.Name.set_String(wsHandle, mkstr)

    @OperationsMethod
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
        self._ValidateParam(pos_or_hvo, "pos_or_hvo")

        pos = self.__ResolveObject(pos_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        abbr = ITsString(pos.Abbreviation.get_String(wsHandle)).Text
        return abbr or ""

    @OperationsMethod
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
        self._EnsureWriteEnabled()

        self._ValidateParam(pos_or_hvo, "pos_or_hvo")
        self._ValidateParam(abbr, "abbr")

        if not abbr or not abbr.strip():
            raise FP_ParameterError("Abbreviation cannot be empty")

        pos = self.__ResolveObject(pos_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(abbr, wsHandle)
        pos.Abbreviation.set_String(wsHandle, mkstr)

    @wrap_enumerable
    @OperationsMethod
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
        self._ValidateParam(pos_or_hvo, "pos_or_hvo")

        pos = self.__ResolveObject(pos_or_hvo)

        # SubPossibilitiesOS is typed ICmPossibility in C#; cast each child to
        # IPartOfSpeech so callers can access POS-specific properties without
        # needing to import from SIL.LCModel themselves.
        return [IPartOfSpeech(p) for p in pos.SubPossibilitiesOS]

    @OperationsMethod
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
        self._EnsureWriteEnabled()

        self._ValidateParam(pos_or_hvo, "pos_or_hvo")
        self._ValidateParam(name, "name")
        self._ValidateParam(abbreviation, "abbreviation")

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")
        if not abbreviation or not abbreviation.strip():
            raise FP_ParameterError("Abbreviation cannot be empty")

        pos = self.__ResolveObject(pos_or_hvo)
        wsHandle = self.project.project.DefaultAnalWs

        # Create the subcategory using the factory
        factory = self.project.project.ServiceLocator.GetService(IPartOfSpeechFactory)
        subcat = factory.Create()

        # Add to parent's SubPossibilitiesOS (must be done before setting properties)
        pos.SubPossibilitiesOS.Add(subcat)

        # Set name and abbreviation
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        subcat.Name.set_String(wsHandle, mkstr_name)

        mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
        subcat.Abbreviation.set_String(wsHandle, mkstr_abbr)

        return subcat

    @OperationsMethod
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
        self._EnsureWriteEnabled()

        self._ValidateParam(pos_or_hvo, "pos_or_hvo")
        self._ValidateParam(subcat_or_hvo, "subcat_or_hvo")

        pos = self.__ResolveObject(pos_or_hvo)
        subcat = self.__ResolveObject(subcat_or_hvo)

        # Remove from parent's SubPossibilitiesOS
        pos.SubPossibilitiesOS.Remove(subcat)

    @OperationsMethod
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
        self._ValidateParam(pos_or_hvo, "pos_or_hvo")

        pos = self.__ResolveObject(pos_or_hvo)

        return pos.CatalogSourceId or ""

    @wrap_enumerable
    @OperationsMethod
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
        self._ValidateParam(pos_or_hvo, "pos_or_hvo")

        pos = self.__ResolveObject(pos_or_hvo)

        # IPartOfSpeech has InflectionClassesOC
        return list(pos.InflectionClassesOC)

    @wrap_enumerable
    @OperationsMethod
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
        self._ValidateParam(pos_or_hvo, "pos_or_hvo")

        pos = self.__ResolveObject(pos_or_hvo)

        # IPartOfSpeech has AffixSlotsOC
        return list(pos.AffixSlotsOC)

    @OperationsMethod
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
        self._ValidateParam(pos_or_hvo, "pos_or_hvo")

        pos = self.__ResolveObject(pos_or_hvo)

        # Search all lexical entries
        # Check MSAs (Morpho-Syntactic Analyses) for PartOfSpeech reference
        # Note: MoMorphType does NOT have PartOfSpeechRA; MSAs do
        # Use get_pos_from_msa() to handle pythonnet interface casting
        count = 0
        entry_repo = self.project.project.ServiceLocator.GetService(ILexEntryRepository)
        for entry in entry_repo.AllInstances():
            # Check if any MSA on this entry references this POS
            for msa in entry.MorphoSyntaxAnalysesOC:
                msa_pos = get_pos_from_msa(msa)
                if msa_pos and msa_pos.Hvo == pos.Hvo:
                    count += 1
                    break  # Count each entry only once

        return count

    @OperationsMethod
    def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
        """
        Duplicate a part of speech, creating a new copy with a new GUID.

        Args:
            item_or_hvo: The IPartOfSpeech object or HVO to duplicate.
            insert_after (bool): If True (default), insert after the source POS.
                                If False, insert at end of parent's possibilities list.
            deep (bool): If True, recursively duplicate all subcategories.
                        If False (default), only duplicate the POS itself.

        Returns:
            IPartOfSpeech: The newly created duplicate POS with a new GUID.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> posOps = POSOperations(project)
            >>> noun = posOps.Find("Noun")
            >>> # Shallow copy (no subcategories)
            >>> noun_copy = posOps.Duplicate(noun)
            >>> print(posOps.GetName(noun_copy))
            Noun

            >>> # Deep copy (includes all subcategories)
            >>> verb = posOps.Find("Verb")
            >>> verb_copy = posOps.Duplicate(verb, deep=True)
            >>> orig_subs = posOps.GetSubcategories(verb)
            >>> copy_subs = posOps.GetSubcategories(verb_copy)
            >>> print(f"Original has {len(orig_subs)} subcategories")
            >>> print(f"Copy has {len(copy_subs)} subcategories")

        Notes:
            - Factory.Create() automatically generates a new GUID
            - insert_after=True preserves the original POS's position
            - Simple properties copied: Name, Abbreviation, Description (MultiString)
            - String property copied: CatalogSourceId
            - deep=True recursively duplicates SubPossibilitiesOS hierarchy
            - Inflection classes and affix slots are NOT copied (references)
            - Use after copying to create variants of existing categories

        See Also:
            Create, Delete, GetSubcategories
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(item_or_hvo, "item_or_hvo")

        # Get source POS and parent
        source = self.__ResolveObject(item_or_hvo)

        # Create new POS using factory (auto-generates new GUID)
        factory = self.project.project.ServiceLocator.GetService(IPartOfSpeechFactory)
        duplicate = factory.Create()

        # Determine parent and insertion position
        # Check if source is a subcategory or top-level
        parent_is_possibility = False
        try:
            parent_pos = IPartOfSpeech(source.Owner)
            parent_is_possibility = True
        except Exception:
            parent_is_possibility = False

        if parent_is_possibility:
            # Source is a subcategory
            parent_pos = IPartOfSpeech(source.Owner)
            if insert_after:
                source_index = parent_pos.SubPossibilitiesOS.IndexOf(source)
                parent_pos.SubPossibilitiesOS.Insert(source_index + 1, duplicate)
            else:
                parent_pos.SubPossibilitiesOS.Add(duplicate)
        else:
            # Source is top-level
            pos_list = self.project.lp.PartsOfSpeechOA
            if insert_after:
                source_index = pos_list.PossibilitiesOS.IndexOf(source)
                pos_list.PossibilitiesOS.Insert(source_index + 1, duplicate)
            else:
                pos_list.PossibilitiesOS.Add(duplicate)

        # Copy simple MultiString properties (AFTER adding to parent)
        duplicate.Name.CopyAlternatives(source.Name)
        duplicate.Abbreviation.CopyAlternatives(source.Abbreviation)
        duplicate.Description.CopyAlternatives(source.Description)

        # Copy string property
        if source.CatalogSourceId:
            duplicate.CatalogSourceId = source.CatalogSourceId

        # Deep copy: recursively duplicate subcategories
        if deep and source.SubPossibilitiesOS.Count > 0:
            for sub_pos in source.SubPossibilitiesOS:
                # Recursively duplicate each subcategory
                self.__DuplicateSubcategory(sub_pos, duplicate)

        return duplicate

    def __DuplicateSubcategory(self, source_sub, parent_duplicate):
        """
        Helper method to recursively duplicate a subcategory.

        Args:
            source_sub: The source IPartOfSpeech subcategory to duplicate.
            parent_duplicate: The parent IPartOfSpeech to add the duplicate to.

        Returns:
            IPartOfSpeech: The duplicated subcategory.
        """
        # Create new subcategory
        factory = self.project.project.ServiceLocator.GetService(IPartOfSpeechFactory)
        sub_duplicate = factory.Create()

        # Add to parent's SubPossibilitiesOS
        parent_duplicate.SubPossibilitiesOS.Add(sub_duplicate)

        # Copy properties
        sub_duplicate.Name.CopyAlternatives(source_sub.Name)
        sub_duplicate.Abbreviation.CopyAlternatives(source_sub.Abbreviation)
        sub_duplicate.Description.CopyAlternatives(source_sub.Description)

        if source_sub.CatalogSourceId:
            sub_duplicate.CatalogSourceId = source_sub.CatalogSourceId

        # Recursively duplicate nested subcategories
        if source_sub.SubPossibilitiesOS.Count > 0:
            for nested_sub in source_sub.SubPossibilitiesOS:
                self.__DuplicateSubcategory(nested_sub, sub_duplicate)

        return sub_duplicate

    # ========== CATALOG (GOLDEtic) IMPORT METHODS ==========
    #
    # These methods populate IPartOfSpeech from the FW GOLDEtic.xml catalog
    # (Templates/GOLDEtic.xml). The canonical FW pipeline lives in
    # SIL.FieldWorks.LexText.Controls.MasterCategory; we reimplement here so
    # we don't have to pull in the GUI-side LexTextControls.dll dependency.
    #
    # Phase 2 ownership-ordering lesson applies: attach via the 2-arg factory
    # overload (POS placed into its owning list at creation) THEN set the
    # multistring properties; never set properties on a free-floating POS.

    @OperationsMethod
    def ImportCatalog(self, progress=None):
        """
        Import the GOLDEtic POS catalog into this project, populating
        PartsOfSpeechOA with canonical GUIDs, abbreviations, terms, and
        definitions from `<FWCodeDir>/Templates/GOLDEtic.xml`.

        Idempotent: any catalog entry whose canonical GUID already exists
        in the project (anywhere in the POS list, top-level or nested) is
        skipped. Re-running the import never duplicates entries.

        Args:
            progress: Optional callable accepting (count, total, name)
                      for progress reporting. May be None.

        Returns:
            CatalogImportResult: Created/skipped counts, list of created
            GUIDs, and any human-readable warnings raised during import.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FileNotFoundError: If GOLDEtic.xml is not found under FWCodeDir.

        Notes:
            - Only catalog writing systems the project has handles for are
              copied; others are silently skipped and a single warning is
              recorded per missing WS tag.
            - Top-level catalog entries become top-level POSs; nested
              entries become SubPossibilitiesOS of their parent POS.
            - The CatalogSourceId is set to "GOLD:<id>" so future syncs
              and FixGuidsAgainstCatalog() can identify them.
        """
        self._EnsureWriteEnabled()

        path = find_catalog_file("GOLDEtic.xml")
        entries = parse_etic_catalog(path)

        # Index existing POSs by GUID (string form) for idempotency.
        existing_guids = self._GetAllPosGuids()

        result = CatalogImportResult()
        missing_ws_seen = set()
        pos_list = self.project.lp.PartsOfSpeechOA

        # Flat list for progress totals (count nested children too).
        total = self._FlattenedCatalogCount(entries)

        def _import_one(entry, parent_pos):
            """Create one catalog entry (and its children) into the project."""
            guid_str = entry.guid.lower() if entry.guid else ""
            existing = existing_guids.get(guid_str)
            if existing is not None:
                result.skipped_count += 1
                pos = existing
            else:
                pos = self._CreatePosFromEntry(entry, parent_pos, pos_list, missing_ws_seen, result.warnings)
                result.created_count += 1
                result.created_guids.append(guid_str)
                existing_guids[guid_str] = pos

            if progress:
                try:
                    progress(result.created_count + result.skipped_count, total, entry.id)
                except Exception:
                    pass  # Progress callbacks must never break the import.

            # Recurse into children: parent for them is the POS we just
            # created (or the existing one we matched).
            for child in entry.children:
                _import_one(child, pos)

        for top in entries:
            _import_one(top, None)

        return result

    @OperationsMethod
    def CreateFromCatalog(self, source_id, parent=None):
        """
        Create a single POS from the GOLDEtic catalog using the canonical
        GUID and all localized data available for the writing systems this
        project has.

        Idempotent: if a POS with the catalog's canonical GUID already
        exists in the project, that existing POS is returned unchanged.

        Args:
            source_id (str): Catalog id, with or without "GOLD:" prefix.
                             e.g. "GOLD:Adjective" or "Adjective".
            parent:   Optional IPartOfSpeech to graft the new POS under.
                      If None (default), the POS is created at the top
                      level of PartsOfSpeechOA.

        Returns:
            IPartOfSpeech: The created (or pre-existing) POS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_ParameterError: If source_id is not present in the catalog.
            FileNotFoundError: If GOLDEtic.xml is not found under FWCodeDir.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(source_id, "source_id")

        path = find_catalog_file("GOLDEtic.xml")
        entries = parse_etic_catalog(path)
        entry = find_catalog_entry(entries, source_id)
        if entry is None:
            raise FP_ParameterError(
                f"Catalog id '{source_id}' not found in GOLDEtic.xml"
            )

        # Idempotency: if the canonical GUID is already present, return it.
        existing = self._FindPosByGuid(entry.guid)
        if existing is not None:
            return existing

        warnings = []
        missing_ws_seen = set()
        pos_list = self.project.lp.PartsOfSpeechOA
        return self._CreatePosFromEntry(entry, parent, pos_list, missing_ws_seen, warnings)

    @OperationsMethod
    def FixGuidsAgainstCatalog(self):
        """
        Scan POSs in this project; for any whose CatalogSourceId matches
        a GOLDEtic catalog item but whose GUID differs from the catalog's
        canonical GUID, create a replacement with the correct GUID,
        transfer references via MergeObject, and remove the old POS.

        This is the recovery path for projects where POSs were created
        without the canonical GUID (e.g. via the plain Create() path or
        an older flexlibs version) but the user marked the catalog id.

        Returns:
            list[tuple]: One (old_name, old_guid, new_guid) tuple per
            POS that was repaired. Empty list if everything is already
            canonical.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
        """
        self._EnsureWriteEnabled()

        path = find_catalog_file("GOLDEtic.xml")
        entries = parse_etic_catalog(path)

        fixed = []
        # Collect candidates first; iterating + mutating the same
        # collection during merge would be unsafe.
        candidates = []
        for pos, _parent in self._WalkAllPos():
            cat_id = pos.CatalogSourceId or ""
            if not cat_id:
                continue
            entry = find_catalog_entry(entries, cat_id)
            if entry is None:
                continue
            current_guid = str(pos.Guid).lower()
            canonical_guid = entry.guid.lower()
            if current_guid == canonical_guid:
                continue
            candidates.append((pos, entry))

        for old_pos, entry in candidates:
            wsHandle = self.project.project.DefaultAnalWs
            old_name = ITsString(old_pos.Name.get_String(wsHandle)).Text or "(unnamed)"
            old_guid = str(old_pos.Guid).lower()

            # Determine the same owner the old POS had so the replacement
            # lives in the same hierarchical position.
            owner = old_pos.Owner
            try:
                parent_pos = IPartOfSpeech(owner)
            except Exception:
                parent_pos = None  # owner is the PartsOfSpeechOA list itself

            warnings = []
            missing_ws = set()
            pos_list = self.project.lp.PartsOfSpeechOA
            new_pos = self._CreatePosFromEntry(entry, parent_pos, pos_list, missing_ws, warnings)

            # Transfer references from old_pos to new_pos. IPartOfSpeech
            # inherits MergeObject from CmObject; this moves incoming
            # references (MSAs, etc.) and then deletes old_pos.
            try:
                old_pos.MergeObject(new_pos, True)
            except Exception as e:
                # MergeObject failure indicates a genuine LCM error
                # (transaction conflict, reference inconsistency, etc.).
                # Silently removing old_pos would orphan incoming references;
                # re-raise so the caller sees the real problem.
                raise FP_ParameterError(
                    f"Failed to merge POS '{old_name}' into canonical-GUID "
                    f"replacement (entry '{entry.id}'): {e}"
                ) from e

            fixed.append((old_name, old_guid, entry.guid.lower()))

        return fixed

    # --- Catalog helper methods (internal) ---

    def _CreatePosFromEntry(self, entry, parent_pos, pos_list, missing_ws_seen, warnings):
        """
        Internal: instantiate one IPartOfSpeech from a CatalogEntry,
        attach to the correct owner with the canonical GUID, then set
        per-WS Name/Abbreviation/Description.

        Applies the Phase 2 ownership-ordering rule: attach first
        (via the 2-arg factory overload, or fall back to Create+Add),
        then mutate properties.
        """
        factory = self.project.project.ServiceLocator.GetService(IPartOfSpeechFactory)
        guid = System.Guid(entry.guid)

        new_pos = None
        # Path A: explicit 2-arg interface overload (creates+attaches in one step).
        # Per issue #14, pythonnet may not expose the 2-arg overload on the
        # interface variable -- it's an explicit interface impl. Try, fall back.
        try:
            if parent_pos is not None:
                new_pos = factory.Create(guid, parent_pos)
            else:
                new_pos = factory.Create(guid, pos_list)
        except Exception:
            new_pos = None

        if new_pos is None:
            # Path B: implementation-side Create(Guid) followed by Add()
            # to the owning collection. cast_to_concrete defends against
            # interface-only views that hide Create(Guid).
            concrete_factory = cast_to_concrete(factory) if hasattr(factory, "ClassName") else factory
            try:
                new_pos = concrete_factory.Create(guid)
            except Exception as e:
                # No safe fallback: parameterless Create() would generate a
                # random GUID, defeating the entire point of CreateFromCatalog.
                # Fail loudly rather than silently degrade.
                raise FP_ParameterError(
                    f"Could not create POS '{entry.id}' with canonical GUID "
                    f"{entry.guid} via either Create(Guid, list) or Create(Guid) "
                    f"factory overloads. The catalog's canonical GUID cannot be applied "
                    f"in this LCM version; a manual factory.Create() workaround would "
                    f"produce a random GUID and is not acceptable here."
                ) from e

            # Attach to the chosen owner.
            if parent_pos is not None:
                parent_pos.SubPossibilitiesOS.Add(new_pos)
            else:
                pos_list.PossibilitiesOS.Add(new_pos)

        # Ensure we expose the IPartOfSpeech view back to callers.
        new_pos = IPartOfSpeech(new_pos)

        # Set per-writing-system multistring properties. Skip any WS the
        # project doesn't have a handle for; record one warning per tag.
        self._SetPosMultiString(new_pos.Name, entry.term, missing_ws_seen, warnings)
        self._SetPosMultiString(new_pos.Abbreviation, entry.abbrev, missing_ws_seen, warnings)
        self._SetPosMultiString(new_pos.Description, entry.def_, missing_ws_seen, warnings)

        # CatalogSourceId is a scalar string; tag with "GOLD:" prefix so
        # FixGuidsAgainstCatalog() can find it later.
        new_pos.CatalogSourceId = f"GOLD:{entry.id}"

        return new_pos

    def _SetPosMultiString(self, multistring, ws_to_text, missing_ws_seen, warnings):
        """
        Apply a {ws_tag: text} dict to an LCM multistring, mapping ws_tag
        to handle via project.WSHandle(). Missing handles are skipped;
        a warning is recorded once per missing tag.
        """
        for ws_tag, text in ws_to_text.items():
            handle = self.project.WSHandle(ws_tag)
            if handle is None:
                if ws_tag not in missing_ws_seen:
                    missing_ws_seen.add(ws_tag)
                    warnings.append(
                        f"Skipping catalog WS '{ws_tag}': "
                        "no matching writing system in project."
                    )
                continue
            tss = TsStringUtils.MakeString(text, handle)
            multistring.set_String(handle, tss)

    def _GetAllPosGuids(self):
        """
        Build a dict mapping lowercased GUID string -> IPartOfSpeech for
        every POS in the project (recursive over SubPossibilitiesOS).
        """
        guids = {}
        for pos, _parent in self._WalkAllPos():
            guids[str(pos.Guid).lower()] = pos
        return guids

    def _FindPosByGuid(self, guid_str):
        """Return the POS whose GUID matches `guid_str` (case-insensitive), or None."""
        target = guid_str.lower() if guid_str else ""
        if not target:
            return None
        for pos, _parent in self._WalkAllPos():
            if str(pos.Guid).lower() == target:
                return pos
        return None

    def _WalkAllPos(self):
        """
        Yield (IPartOfSpeech, parent_or_None) for every POS in the
        project, walking SubPossibilitiesOS recursively. parent is None
        for top-level POSs.
        """
        pos_list = self.project.lp.PartsOfSpeechOA
        if pos_list is None:
            return

        def _walk(collection, parent):
            for raw in collection:
                pos = IPartOfSpeech(raw)
                yield pos, parent
                if pos.SubPossibilitiesOS.Count > 0:
                    yield from _walk(pos.SubPossibilitiesOS, pos)

        yield from _walk(pos_list.PossibilitiesOS, None)

    def _FlattenedCatalogCount(self, entries):
        """Total catalog entries across the forest, including nested children."""
        n = 0
        for e in entries:
            n += 1 + self._FlattenedCatalogCount(e.children)
        return n

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

    # ========== SYNC INTEGRATION METHODS ==========

    @OperationsMethod
    def GetSyncableProperties(self, item):
        """
        Get dictionary of syncable properties for cross-project synchronization.

        Args:
            item: The IPartOfSpeech object.

        Returns:
            dict: Dictionary mapping property names to their values.
                Keys are property names, values are the property values.

        Example:
            >>> posOps = POSOperations(project)
            >>> pos = list(posOps.GetAll())[0]
            >>> props = posOps.GetSyncableProperties(pos)
            >>> print(props.keys())
            dict_keys(['Name', 'Abbreviation', 'Description', 'CatalogSourceId'])

        Notes:
            - Returns all MultiString properties (all writing systems)
            - Returns CatalogSourceId string property
            - Does not include SubPossibilitiesOS (subcategories)
            - Does not include InflectionClassesOC or AffixSlotsOC
            - Does not include GUID or HVO of the POS itself
        """
        pos = self.__ResolveObject(item)

        # Get all writing systems for MultiString properties
        ws_factory = self.project.project.WritingSystemFactory
        all_ws = {ws.Id: ws.Handle for ws in ws_factory.WritingSystems}

        props = {}

        # MultiString properties
        for prop_name in ["Name", "Abbreviation", "Description"]:
            if hasattr(pos, prop_name):
                prop_obj = getattr(pos, prop_name)
                ws_values = {}
                for ws_id, ws_handle in all_ws.items():
                    text = ITsString(prop_obj.get_String(ws_handle)).Text
                    if text:  # Only include non-empty values
                        ws_values[ws_id] = text
                if ws_values:  # Only include property if it has values
                    props[prop_name] = ws_values

        # String properties
        if hasattr(pos, "CatalogSourceId") and pos.CatalogSourceId:
            props["CatalogSourceId"] = pos.CatalogSourceId

        return props

    @OperationsMethod
    def CompareTo(self, item1, item2, ops1=None, ops2=None):
        """
        Compare two parts of speech and return detailed differences.

        Args:
            item1: First POS to compare (from source project).
            item2: Second POS to compare (from target project).
            ops1: Optional POSOperations instance for item1's project.
                 Defaults to self.
            ops2: Optional POSOperations instance for item2's project.
                 Defaults to self.

        Returns:
            tuple: (is_different, differences) where:
                - is_different (bool): True if items differ
                - differences (dict): Maps property names to (value1, value2) tuples

        Example:
            >>> pos1 = project1_posOps.Find("Noun")
            >>> pos2 = project2_posOps.Find("Noun")
            >>> is_diff, diffs = project1_posOps.CompareTo(
            ...     pos1, pos2,
            ...     ops1=project1_posOps,
            ...     ops2=project2_posOps
            ... )
            >>> if is_diff:
            ...     for prop, (val1, val2) in diffs.items():
            ...         print(f"{prop}: {val1} -> {val2}")

        Notes:
            - Compares all MultiString properties across all writing systems
            - Compares string properties
            - Returns empty dict if items are identical
            - Handles cross-project comparison via ops1/ops2
        """
        if ops1 is None:
            ops1 = self
        if ops2 is None:
            ops2 = self

        # Get syncable properties from both items
        props1 = ops1.GetSyncableProperties(item1)
        props2 = ops2.GetSyncableProperties(item2)

        is_different = False
        differences = {}

        # Compare each property
        all_keys = set(props1.keys()) | set(props2.keys())
        for key in all_keys:
            val1 = props1.get(key)
            val2 = props2.get(key)

            if val1 != val2:
                is_different = True
                differences[key] = (val1, val2)

        return (is_different, differences)

    # --- Private Helper Methods ---

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
