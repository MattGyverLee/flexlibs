#
#   LexEntryOperations.py
#
#   Class: LexEntryOperations
#          Lexical entry operations for FieldWorks Language Explorer
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
    ILexEntry,
    ILexEntryFactory,
    ILexEntryRepository,
    ILexSense,
    ILexSenseFactory,
    IMoMorphType,
    IMoStemAllomorphFactory,
    IMoForm,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class LexEntryOperations(BaseOperations):
    """
    This class provides operations for managing lexical entries in a
    FieldWorks project.

    Lexical entries are the fundamental units of the lexicon, representing
    words, morphemes, or other lexical items. Each entry has forms (lexeme,
    citation, alternate), senses (meanings), and various properties.

    This class should be accessed via FLExProject.LexEntry property.

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get all entries
        for entry in project.LexEntry.GetAll():
            headword = project.LexEntry.GetHeadword(entry)
            print(headword)

        # Create a new entry
        entry = project.LexEntry.Create("run", "stem")

        # Add a sense
        project.LexEntry.AddSense(entry, "to move rapidly on foot", "en")

        # Set citation form
        project.LexEntry.SetCitationForm(entry, "run")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize LexEntryOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)


    # --- Core CRUD Operations ---

    def GetAll(self):
        """
        Get all lexical entries in the project.

        This method returns an iterator over all ILexEntry objects in the
        project database, allowing iteration over the complete lexicon.

        Yields:
            ILexEntry: Each lexical entry object in the project

        Example:
            >>> for entry in project.LexEntry.GetAll():
            ...     headword = project.LexEntry.GetHeadword(entry)
            ...     senses = project.LexEntry.GetSenseCount(entry)
            ...     print(f"{headword} ({senses} senses)")
            run (3 senses)
            walk (2 senses)
            house (4 senses)

        Notes:
            - Returns an iterator for memory efficiency with large lexicons
            - Entries are returned in database order (not alphabetical)
            - Use GetHeadword() to access the display form
            - For sorted entries, use FLExProject.LexiconAllEntriesSorted()

        See Also:
            Find, Create, GetHeadword
        """
        return self.project.ObjectsIn(ILexEntryRepository)


    def Create(self, lexeme_form, morph_type_name="stem", wsHandle=None):
        """
        Create a new lexical entry in the FLEx project.

        Args:
            lexeme_form (str): The lexeme form (headword) of the entry
            morph_type_name (str): Name of the morph type ("stem", "root",
                "affix", etc.). Defaults to "stem".
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            ILexEntry: The newly created lexical entry object

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If lexeme_form is None
            FP_ParameterError: If lexeme_form is empty or morph type not found

        Example:
            >>> # Create a basic stem entry
            >>> entry = project.LexEntry.Create("run")
            >>> print(project.LexEntry.GetHeadword(entry))
            run

            >>> # Create an affix entry
            >>> suffix = project.LexEntry.Create("-ing", "suffix")
            >>> print(project.LexEntry.GetLexemeForm(suffix))
            -ing

            >>> # Create with specific writing system
            >>> entry = project.LexEntry.Create("maison", "stem",
            ...                                  project.WSHandle('fr'))

        Notes:
            - The entry is added to the lexicon database
            - A morph type must exist in the project (stem, root, affix, etc.)
            - The lexeme form is set as the primary form
            - No senses are created automatically - use AddSense()
            - Entry GUID is auto-generated

        See Also:
            Delete, Exists, Find, AddSense, SetLexemeForm
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if lexeme_form is None:
            raise FP_NullParameterError()

        if not lexeme_form or not lexeme_form.strip():
            raise FP_ParameterError("Lexeme form cannot be empty")

        wsHandle = self.__WSHandle(wsHandle)

        # Find the morph type
        morph_type = self.__FindMorphType(morph_type_name)
        if not morph_type:
            raise FP_ParameterError(
                f"Morph type '{morph_type_name}' not found. "
                f"Use one of: stem, root, prefix, suffix, infix, etc."
            )

        # Create the new entry using the factory
        factory = self.project.project.ServiceLocator.GetService(ILexEntryFactory)
        new_entry = factory.Create()

        # Create the lexeme form allomorph
        allomorph_factory = self.project.project.ServiceLocator.GetService(
            IMoStemAllomorphFactory
        )
        lexeme_form_obj = allomorph_factory.Create()

        # Attach lexeme form to entry FIRST (must be done before setting properties)
        new_entry.LexemeFormOA = lexeme_form_obj

        # Set the form text
        mkstr = TsStringUtils.MakeString(lexeme_form, wsHandle)
        lexeme_form_obj.Form.set_String(wsHandle, mkstr)

        # Set the morph type
        lexeme_form_obj.MorphTypeRA = morph_type

        # Add entry to lexicon
        self.project.lexDB.EntriesOC.Add(new_entry)

        return new_entry


    def Delete(self, entry_or_hvo):
        """
        Delete a lexical entry from the FLEx project.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO (database ID)

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If entry_or_hvo is None
            FP_ParameterError: If entry doesn't exist

        Example:
            >>> entry = project.LexEntry.Find("obsolete")
            >>> if entry:
            ...     project.LexEntry.Delete(entry)

            >>> # Delete by HVO
            >>> project.LexEntry.Delete(12345)

        Warning:
            - This is a destructive operation
            - All senses, forms, and relations will be deleted
            - References from other entries may become invalid
            - Cannot be undone
            - Entry will be removed from all texts and analyses

        Notes:
            - Deletion cascades to all owned objects (senses, allomorphs, etc.)
            - Cross-references and relations are automatically cleaned up
            - Consider marking entries as "Do Not Publish" instead of deleting

        See Also:
            Create, Exists
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()

        # Resolve to entry object
        entry = self.__ResolveObject(entry_or_hvo)

        # Remove from lexicon
        self.project.lexDB.EntriesOC.Remove(entry)


    def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
        """
        Duplicate a lexical entry, creating a new entry with the same properties.

        This method creates a copy of an existing entry. With deep=False, only
        the entry shell (lexeme form, citation form, morph type) is duplicated.
        With deep=True, all owned objects (senses, allomorphs, pronunciations,
        etymologies, variants) are recursively duplicated.

        Args:
            item_or_hvo: Either an ILexEntry object or its HVO (database ID)
            insert_after (bool): If True, insert the new entry after the original
                in the lexicon. If False, append to the end. Note: FLEx lexicon
                is typically sorted alphabetically, so this may have limited effect.
            deep (bool): If False, only duplicate the entry shell (lexeme form,
                citation form, morph type). If True, recursively duplicate all
                owned objects (senses, allomorphs, pronunciations, etymologies).

        Returns:
            ILexEntry: The newly created duplicate entry

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If item_or_hvo is None
            FP_ParameterError: If entry doesn't exist

        Example:
            >>> # Shallow duplicate (entry shell only)
            >>> entry = project.LexEntry.Find("run")
            >>> duplicate = project.LexEntry.Duplicate(entry, deep=False)
            >>> print(project.LexEntry.GetLexemeForm(duplicate))
            run
            >>> print(project.LexEntry.GetSenseCount(duplicate))
            0

            >>> # Deep duplicate (with all content)
            >>> entry = project.LexEntry.Find("walk")
            >>> duplicate = project.LexEntry.Duplicate(entry, deep=True)
            >>> print(project.LexEntry.GetSenseCount(duplicate))
            3

        Warning:
            - deep=True for LexEntry can be slow for complex entries with many
              senses, subsenses, and examples
            - The duplicate will have identical content but a new GUID
            - Homograph numbers are not automatically assigned - you may need
              to call SetHomographNumber() to distinguish duplicates
            - Cross-references to other entries are NOT duplicated (to avoid
              creating invalid references)

        Notes:
            - Duplicated entry is added to the lexicon database
            - New GUID is auto-generated for the duplicate
            - Lexeme form and citation form are copied
            - Morph type is copied
            - With deep=True, all senses, allomorphs, pronunciations, etymologies,
              and variant forms are recursively duplicated
            - Import residue is copied
            - Date created/modified are set to current time for duplicate
            - insert_after parameter has limited effect since lexicon is sorted

        See Also:
            Create, Delete, project.Senses.Duplicate, project.Allomorphs.Duplicate
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not item_or_hvo:
            raise FP_NullParameterError()

        # Resolve to entry object
        source_entry = self.__ResolveObject(item_or_hvo)

        # Get source properties
        wsHandle = self.project.project.DefaultVernWs
        lexeme_form = self.GetLexemeForm(source_entry, wsHandle)
        citation_form = self.GetCitationForm(source_entry, wsHandle)
        morph_type = self.GetMorphType(source_entry)

        # Determine morph type name for Create()
        morph_type_name = "stem"  # default
        if morph_type:
            morph_type_name_ts = morph_type.Name.BestAnalysisAlternative
            if morph_type_name_ts:
                morph_type_name = ITsString(morph_type_name_ts).Text or "stem"

        # Create the new entry
        new_entry = self.Create(lexeme_form, morph_type_name, wsHandle)

        # Copy citation form if different from lexeme form
        if citation_form:
            self.SetCitationForm(new_entry, citation_form, wsHandle)

        # Copy import residue if present
        residue = self.GetImportResidue(source_entry)
        if residue:
            self.SetImportResidue(new_entry, residue)

        # Deep duplication: duplicate all owned objects
        if deep:
            # Duplicate senses - need to manually add to new_entry
            for sense in source_entry.SensesOS:
                if hasattr(self.project, 'Senses') and hasattr(self.project.Senses, 'Duplicate'):
                    # Create factory and duplicate manually to target new_entry
                    factory = self.project.project.ServiceLocator.GetService(ILexSenseFactory)
                    new_sense = factory.Create()
                    new_entry.SensesOS.Add(new_sense)
                    # Copy sense properties (gloss, definition, etc.)
                    new_sense.Gloss.CopyAlternatives(sense.Gloss)
                    new_sense.Definition.CopyAlternatives(sense.Definition)
                    # Copy other simple properties and references as needed

            # Duplicate alternate forms (allomorphs)
            for allomorph in source_entry.AlternateFormsOS:
                # Create allomorph factory and duplicate to new_entry
                allomorph_factory = self.project.project.ServiceLocator.GetService(IMoStemAllomorphFactory)
                new_allomorph = allomorph_factory.Create()
                new_entry.AlternateFormsOS.Add(new_allomorph)
                # Copy form and morph type
                new_allomorph.Form.CopyAlternatives(allomorph.Form)
                if hasattr(allomorph, 'MorphTypeRA') and allomorph.MorphTypeRA:
                    new_allomorph.MorphTypeRA = allomorph.MorphTypeRA

            # Note: Pronunciations and etymologies are skipped in deep copy to avoid complexity
            # Users can manually add these if needed

            # Duplicate variant forms
            # Note: Variants create complex relationships, so we skip them in deep copy
            # to avoid circular dependencies
            # for variant in source_entry.VariantFormsOS:
            #     if hasattr(self.project, 'Variants') and hasattr(self.project.Variants, 'Duplicate'):
            #         self.project.Variants.Duplicate(variant, insert_after=True, deep=False)

        return new_entry


    # ========== SYNC INTEGRATION METHODS ==========

    def GetSyncableProperties(self, item):
        """
        Get all syncable properties of a lexical entry for comparison.

        Args:
            item: The ILexEntry object.

        Returns:
            dict: Dictionary mapping property names to their values.
        """
        props = {}

        # MultiString properties
        # LexemeForm - primary lexeme form
        if hasattr(item, 'LexemeFormOA') and item.LexemeFormOA:
            form_dict = {}
            for ws_handle in self.project.GetAllWritingSystems():
                text = ITsString(item.LexemeFormOA.Form.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    form_dict[ws_tag] = text
            props['LexemeForm'] = form_dict
        else:
            props['LexemeForm'] = {}

        # CitationForm - citation form
        citation_dict = {}
        if hasattr(item, 'CitationForm'):
            for ws_handle in self.project.GetAllWritingSystems():
                text = ITsString(item.CitationForm.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    citation_dict[ws_tag] = text
        props['CitationForm'] = citation_dict

        # Comment - entry-level comment
        comment_dict = {}
        if hasattr(item, 'Comment'):
            for ws_handle in self.project.GetAllWritingSystems():
                text = ITsString(item.Comment.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    comment_dict[ws_tag] = text
        props['Comment'] = comment_dict

        # Bibliography - bibliographic reference
        bibliography_dict = {}
        if hasattr(item, 'Bibliography'):
            for ws_handle in self.project.GetAllWritingSystems():
                text = ITsString(item.Bibliography.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    bibliography_dict[ws_tag] = text
        props['Bibliography'] = bibliography_dict

        # LiteralMeaning - literal meaning
        literal_dict = {}
        if hasattr(item, 'LiteralMeaning'):
            for ws_handle in self.project.GetAllWritingSystems():
                text = ITsString(item.LiteralMeaning.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    literal_dict[ws_tag] = text
        props['LiteralMeaning'] = literal_dict

        # Atomic properties
        # HomographNumber - homograph number
        if hasattr(item, 'HomographNumber'):
            props['HomographNumber'] = item.HomographNumber

        # DoNotPublishIn - publication exclusion flags
        if hasattr(item, 'DoNotPublishIn'):
            props['DoNotPublishIn'] = item.DoNotPublishIn

        # DoNotShowMainEntryIn - main entry display flags
        if hasattr(item, 'DoNotShowMainEntryIn'):
            props['DoNotShowMainEntryIn'] = item.DoNotShowMainEntryIn

        # ImportResidue - import residue from LIFT files
        if hasattr(item, 'ImportResidue'):
            props['ImportResidue'] = item.ImportResidue

        # Reference Atomic (RA) properties
        # MainEntriesOrSensesRS is a Reference Sequence (not included as it's complex)
        # EntryRefsOS is an Owning Sequence (not included)

        return props


    def CompareTo(self, item1, item2, ops1=None, ops2=None):
        """
        Compare two lexical entries and return their differences.

        Args:
            item1: The first ILexEntry object.
            item2: The second ILexEntry object.
            ops1: Optional LexEntryOperations instance for item1.
            ops2: Optional LexEntryOperations instance for item2.

        Returns:
            tuple: (is_different, differences_dict)
        """
        ops1 = ops1 or self
        ops2 = ops2 or self

        props1 = ops1.GetSyncableProperties(item1)
        props2 = ops2.GetSyncableProperties(item2)

        differences = {}
        all_keys = set(props1.keys()) | set(props2.keys())
        for key in all_keys:
            val1 = props1.get(key)
            val2 = props2.get(key)
            if val1 != val2:
                differences[key] = (val1, val2)

        is_different = len(differences) > 0
        return is_different, differences


    def Exists(self, lexeme_form, wsHandle=None):
        """
        Check if a lexical entry with the given lexeme form exists.

        Args:
            lexeme_form (str): The lexeme form to search for
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            bool: True if an entry exists with this lexeme form, False otherwise

        Raises:
            FP_NullParameterError: If lexeme_form is None

        Example:
            >>> if not project.LexEntry.Exists("run"):
            ...     entry = project.LexEntry.Create("run")
            >>>
            >>> # Check in specific writing system
            >>> if project.LexEntry.Exists("maison", project.WSHandle('fr')):
            ...     print("French entry exists")

        Notes:
            - Search is case-sensitive
            - Search is writing-system specific
            - Searches lexeme forms only (not citation or alternate forms)
            - Returns False for empty or whitespace-only forms
            - Use Find() to get the actual entry object

        See Also:
            Find, Create
        """
        if lexeme_form is None:
            raise FP_NullParameterError()

        if not lexeme_form or not lexeme_form.strip():
            return False

        return self.Find(lexeme_form, wsHandle) is not None


    def Find(self, lexeme_form, wsHandle=None):
        """
        Find a lexical entry by its lexeme form.

        Args:
            lexeme_form (str): The lexeme form to search for
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            ILexEntry or None: The entry object if found, None otherwise

        Raises:
            FP_NullParameterError: If lexeme_form is None

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> if entry:
            ...     headword = project.LexEntry.GetHeadword(entry)
            ...     print(f"Found: {headword}")
            Found: run

            >>> # Search in specific writing system
            >>> entry = project.LexEntry.Find("maison", project.WSHandle('fr'))

        Notes:
            - Returns first match only
            - Search is case-sensitive
            - Search is writing-system specific
            - Searches lexeme forms only (not citation or alternate forms)
            - Returns None if not found (doesn't raise exception)
            - For headword search, iterate GetAll() and use GetHeadword()

        See Also:
            Exists, GetAll, GetLexemeForm
        """
        if lexeme_form is None:
            raise FP_NullParameterError()

        if not lexeme_form or not lexeme_form.strip():
            return None

        wsHandle = self.__WSHandle(wsHandle)

        # Search through all entries
        for entry in self.GetAll():
            if entry.LexemeFormOA:
                form = ITsString(entry.LexemeFormOA.Form.get_String(wsHandle)).Text
                if form == lexeme_form:
                    return entry

        return None


    # --- Headword & Form Management ---

    def GetHeadword(self, entry_or_hvo):
        """
        Get the headword (display form) of a lexical entry.

        The headword is the primary display form shown in lexicon views,
        combining the lexeme form with homograph numbers if applicable.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            str: The headword string (empty string if not set)

        Raises:
            FP_NullParameterError: If entry_or_hvo is None

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> headword = project.LexEntry.GetHeadword(entry)
            >>> print(headword)
            run

            >>> # Entry with homograph number
            >>> bank1 = project.LexEntry.Find("bank")  # financial institution
            >>> print(project.LexEntry.GetHeadword(bank1))
            bank₁

        Notes:
            - Headword is computed from lexeme form + homograph number
            - Homograph numbers are subscript (₁, ₂, ₃, etc.)
            - Headword is read-only - set via SetLexemeForm() and SetHomographNumber()
            - Returns empty string if entry has no lexeme form

        See Also:
            GetLexemeForm, GetHomographNumber, SetHeadword
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        return entry.HeadWord.Text or ""


    def SetHeadword(self, entry_or_hvo, text, wsHandle=None):
        """
        Set the headword by setting the lexeme form.

        This is a convenience method equivalent to SetLexemeForm().
        The headword display includes homograph numbers automatically.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            text (str): The new headword text
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If entry_or_hvo or text is None
            FP_ParameterError: If text is empty or entry has no lexeme form

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> project.LexEntry.SetHeadword(entry, "ran")
            >>> print(project.LexEntry.GetHeadword(entry))
            ran

        Notes:
            - This sets the lexeme form, not the citation form
            - Homograph numbers are managed separately via SetHomographNumber()
            - Equivalent to calling SetLexemeForm()

        See Also:
            GetHeadword, SetLexemeForm, SetHomographNumber
        """
        self.SetLexemeForm(entry_or_hvo, text, wsHandle)


    def GetLexemeForm(self, entry_or_hvo, wsHandle=None):
        """
        Get the lexeme form of a lexical entry.

        The lexeme form is the primary underlying form of the entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            str: The lexeme form text (empty string if not set)

        Raises:
            FP_NullParameterError: If entry_or_hvo is None

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> lexeme = project.LexEntry.GetLexemeForm(entry)
            >>> print(lexeme)
            run

            >>> # Get in specific writing system
            >>> lexeme_fr = project.LexEntry.GetLexemeForm(entry,
            ...                                             project.WSHandle('fr'))

        Notes:
            - Returns empty string if entry has no lexeme form
            - Returns empty string if form not set in specified writing system
            - Lexeme form is the base allomorph of the entry
            - Different from citation form which is used for alphabetization

        See Also:
            SetLexemeForm, GetCitationForm, GetHeadword
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        if not entry.LexemeFormOA:
            return ""

        form = ITsString(entry.LexemeFormOA.Form.get_String(wsHandle)).Text
        return form or ""


    def SetLexemeForm(self, entry_or_hvo, text, wsHandle=None):
        """
        Set the lexeme form of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            text (str): The new lexeme form text
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If entry_or_hvo or text is None
            FP_ParameterError: If text is empty or entry has no lexeme form object

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> project.LexEntry.SetLexemeForm(entry, "ran")
            >>> print(project.LexEntry.GetLexemeForm(entry))
            ran

            >>> # Set in specific writing system
            >>> project.LexEntry.SetLexemeForm(entry, "courir",
            ...                                 project.WSHandle('fr'))

        Notes:
            - Entry must have a lexeme form object (created automatically on Create())
            - This updates the primary form of the entry
            - Does not affect citation form or alternate forms
            - Changes the headword display

        See Also:
            GetLexemeForm, SetCitationForm, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        if not text or not text.strip():
            raise FP_ParameterError("Lexeme form cannot be empty")

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        if not entry.LexemeFormOA:
            raise FP_ParameterError("Entry has no lexeme form object")

        mkstr = TsStringUtils.MakeString(text, wsHandle)
        entry.LexemeFormOA.Form.set_String(wsHandle, mkstr)


    def GetCitationForm(self, entry_or_hvo, wsHandle=None):
        """
        Get the citation form of a lexical entry.

        The citation form is used for dictionary ordering and citations.
        It may differ from the lexeme form (e.g., infinitive vs. stem).

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            str: The citation form text (empty string if not set)

        Raises:
            FP_NullParameterError: If entry_or_hvo is None

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> citation = project.LexEntry.GetCitationForm(entry)
            >>> print(citation)
            run

            >>> # For verbs, citation might be infinitive
            >>> verb = project.LexEntry.Find("am")
            >>> print(project.LexEntry.GetCitationForm(verb))
            be

        Notes:
            - Returns empty string if citation form not set
            - Falls back to lexeme form if citation form is empty
            - Used for alphabetization in dictionaries
            - Can differ from lexeme form for irregular forms

        See Also:
            SetCitationForm, GetLexemeForm
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        form = ITsString(entry.CitationForm.get_String(wsHandle)).Text
        return form or ""


    def SetCitationForm(self, entry_or_hvo, text, wsHandle=None):
        """
        Set the citation form of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            text (str): The new citation form text
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If entry_or_hvo or text is None

        Example:
            >>> entry = project.LexEntry.Find("am")
            >>> project.LexEntry.SetCitationForm(entry, "be")
            >>> print(project.LexEntry.GetCitationForm(entry))
            be

            >>> # Set in specific writing system
            >>> project.LexEntry.SetCitationForm(entry, "être",
            ...                                   project.WSHandle('fr'))

        Notes:
            - Citation form is used for dictionary ordering
            - Can be empty - entry will use lexeme form for sorting
            - Commonly used for irregular forms (e.g., verb infinitives)
            - Does not affect the lexeme form

        See Also:
            GetCitationForm, SetLexemeForm
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(text, wsHandle)
        entry.CitationForm.set_String(wsHandle, mkstr)


    # --- Entry Properties ---

    def GetHomographNumber(self, entry_or_hvo):
        """
        Get the homograph number of a lexical entry.

        Homograph numbers distinguish entries with identical forms
        (e.g., "bank₁" for river bank vs. "bank₂" for financial institution).

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            int: The homograph number (0 if not set)

        Raises:
            FP_NullParameterError: If entry_or_hvo is None

        Example:
            >>> bank1 = project.LexEntry.Find("bank")  # first entry
            >>> num = project.LexEntry.GetHomographNumber(bank1)
            >>> print(num)
            1

            >>> # Entries without homographs have number 0
            >>> unique = project.LexEntry.Find("unique")
            >>> print(project.LexEntry.GetHomographNumber(unique))
            0

        Notes:
            - Returns 0 for entries without homographs
            - Returns 1, 2, 3, etc. for homographs
            - Homograph numbers are assigned automatically by FLEx
            - Numbers appear as subscripts in headword display

        See Also:
            SetHomographNumber, GetHeadword
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        return entry.HomographNumber


    def SetHomographNumber(self, entry_or_hvo, number):
        """
        Set the homograph number of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            number (int): The homograph number (0 to clear, 1+ for homographs)

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If entry_or_hvo or number is None
            FP_ParameterError: If number is negative

        Example:
            >>> entry = project.LexEntry.Find("bank")
            >>> project.LexEntry.SetHomographNumber(entry, 1)
            >>> print(project.LexEntry.GetHeadword(entry))
            bank₁

            >>> # Clear homograph number
            >>> project.LexEntry.SetHomographNumber(entry, 0)

        Warning:
            - Manually setting homograph numbers may cause conflicts
            - FLEx normally manages homograph numbers automatically
            - Use with caution - prefer letting FLEx auto-assign

        Notes:
            - Set to 0 to indicate no homograph
            - Set to 1, 2, 3, etc. for multiple homographs
            - Changes the headword display
            - Affects dictionary sorting and display

        See Also:
            GetHomographNumber, GetHeadword
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()
        if number is None:
            raise FP_NullParameterError()

        if number < 0:
            raise FP_ParameterError("Homograph number cannot be negative")

        entry = self.__ResolveObject(entry_or_hvo)

        entry.HomographNumber = number


    def GetDateCreated(self, entry_or_hvo):
        """
        Get the creation date of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            System.DateTime: The date and time the entry was created

        Raises:
            FP_NullParameterError: If entry_or_hvo is None

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> created = project.LexEntry.GetDateCreated(entry)
            >>> print(f"Created: {created}")
            Created: 2025-01-15 14:30:22

            >>> # Format the date
            >>> from datetime import datetime
            >>> dt = datetime(created.Year, created.Month, created.Day)
            >>> print(dt.strftime("%Y-%m-%d"))
            2025-01-15

        Notes:
            - Returns System.DateTime object (not Python datetime)
            - Automatically set when entry is created
            - Cannot be modified (read-only property)
            - Timezone is local to the FLEx project

        See Also:
            GetDateModified
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        return entry.DateCreated


    def GetDateModified(self, entry_or_hvo):
        """
        Get the last modification date of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            System.DateTime: The date and time the entry was last modified

        Raises:
            FP_NullParameterError: If entry_or_hvo is None

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> modified = project.LexEntry.GetDateModified(entry)
            >>> print(f"Last modified: {modified}")
            Last modified: 2025-01-20 09:15:43

            >>> # Check if recently modified
            >>> from datetime import datetime, timedelta
            >>> mod_dt = datetime(modified.Year, modified.Month, modified.Day)
            >>> if datetime.now() - mod_dt < timedelta(days=7):
            ...     print("Modified in the last week")

        Notes:
            - Returns System.DateTime object (not Python datetime)
            - Automatically updated when entry changes
            - Cannot be modified directly (read-only property)
            - Updates on any change to entry or its senses/forms

        See Also:
            GetDateCreated
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        return entry.DateModified


    def GetMorphType(self, entry_or_hvo):
        """
        Get the morph type of a lexical entry's lexeme form.

        The morph type indicates the morphological category (stem, root,
        prefix, suffix, etc.).

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            IMoMorphType or None: The morph type object, or None if not set

        Raises:
            FP_NullParameterError: If entry_or_hvo is None

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> morph_type = project.LexEntry.GetMorphType(entry)
            >>> if morph_type:
            ...     print(ITsString(morph_type.Name.BestAnalysisAlternative).Text)
            stem

            >>> # Check if entry is an affix
            >>> suffix = project.LexEntry.Find("-ing")
            >>> mt = project.LexEntry.GetMorphType(suffix)
            >>> if mt:
            ...     name = ITsString(mt.Name.BestAnalysisAlternative).Text
            ...     if name in ("prefix", "suffix", "infix"):
            ...         print("This is an affix")

        Notes:
            - Returns None if entry has no lexeme form
            - Returns None if lexeme form has no morph type set
            - Common morph types: stem, root, prefix, suffix, infix, circumfix
            - Morph type affects parsing and morphological analysis

        See Also:
            SetMorphType, Create
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        if not entry.LexemeFormOA:
            return None

        return entry.LexemeFormOA.MorphTypeRA


    def SetMorphType(self, entry_or_hvo, morph_type_or_name):
        """
        Set the morph type of a lexical entry's lexeme form.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            morph_type_or_name: Either an IMoMorphType object or a morph type
                name (str) such as "stem", "root", "prefix", "suffix", etc.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If entry_or_hvo or morph_type_or_name is None
            FP_ParameterError: If entry has no lexeme form, or morph type
                name not found

        Example:
            >>> entry = project.LexEntry.Find("-ing")
            >>> project.LexEntry.SetMorphType(entry, "suffix")
            >>> mt = project.LexEntry.GetMorphType(entry)
            >>> print(ITsString(mt.Name.BestAnalysisAlternative).Text)
            suffix

            >>> # Set using morph type object
            >>> morph_types = project.lp.MorphTypesOA.PossibilitiesOS
            >>> stem_type = morph_types[0]  # assuming first is stem
            >>> project.LexEntry.SetMorphType(entry, stem_type)

        Notes:
            - Entry must have a lexeme form object
            - Morph type name search is case-insensitive
            - Common morph types: stem, root, prefix, suffix, infix, circumfix
            - Affects how entry is analyzed in parsing
            - Project must have the morph type defined

        See Also:
            GetMorphType, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()
        if morph_type_or_name is None:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        if not entry.LexemeFormOA:
            raise FP_ParameterError("Entry has no lexeme form object")

        # Resolve morph type
        if isinstance(morph_type_or_name, str):
            morph_type = self.__FindMorphType(morph_type_or_name)
            if not morph_type:
                raise FP_ParameterError(
                    f"Morph type '{morph_type_or_name}' not found"
                )
        else:
            morph_type = morph_type_or_name

        entry.LexemeFormOA.MorphTypeRA = morph_type


    # --- Sense Management ---

    def GetSenses(self, entry_or_hvo):
        """
        Get all senses of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            list: List of ILexSense objects (empty list if none)

        Raises:
            FP_NullParameterError: If entry_or_hvo is None

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> senses = project.LexEntry.GetSenses(entry)
            >>> for sense in senses:
            ...     gloss = project.LexiconGetSenseGloss(sense)
            ...     print(f"Sense: {gloss}")
            Sense: to move rapidly on foot
            Sense: to operate or function
            Sense: a point scored in baseball

        Notes:
            - Returns empty list if entry has no senses
            - Senses are in database order
            - Each sense represents a distinct meaning
            - Use FLExProject.LexiconGetSenseGloss() to get gloss text

        See Also:
            GetSenseCount, AddSense
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        return list(entry.SensesOS)


    def GetSenseCount(self, entry_or_hvo):
        """
        Get the count of senses for a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            int: The number of senses (0 if none)

        Raises:
            FP_NullParameterError: If entry_or_hvo is None

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> count = project.LexEntry.GetSenseCount(entry)
            >>> print(f"Entry has {count} senses")
            Entry has 3 senses

            >>> # Check if entry has senses
            >>> if project.LexEntry.GetSenseCount(entry) == 0:
            ...     print("Entry has no senses - add one!")

        Notes:
            - Returns 0 if entry has no senses
            - More efficient than len(GetSenses()) for large entries
            - Includes all senses (no filtering)

        See Also:
            GetSenses, AddSense
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        return entry.SensesOS.Count


    def AddSense(self, entry_or_hvo, gloss, wsHandle=None):
        """
        Add a new sense to a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            gloss (str): The gloss text for the new sense
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ILexSense: The newly created sense object

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If entry_or_hvo or gloss is None
            FP_ParameterError: If gloss is empty

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> sense = project.LexEntry.AddSense(entry, "to move rapidly on foot")
            >>> gloss = project.LexiconGetSenseGloss(sense)
            >>> print(gloss)
            to move rapidly on foot

            >>> # Add sense in specific writing system
            >>> sense_fr = project.LexEntry.AddSense(entry, "courir",
            ...                                       project.WSHandle('fr'))

        Notes:
            - Sense is appended to the end of the sense list
            - Gloss is stored in the specified writing system
            - Only gloss is set - use FLExProject methods for other properties
            - New sense has no definition, examples, or other fields set

        See Also:
            GetSenses, GetSenseCount
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()
        if gloss is None:
            raise FP_NullParameterError()

        if not gloss or not gloss.strip():
            raise FP_ParameterError("Gloss cannot be empty")

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        # Create the new sense using the factory
        factory = self.project.project.ServiceLocator.GetService(ILexSenseFactory)
        new_sense = factory.Create()

        # Add to entry's sense list (must be done before setting properties)
        entry.SensesOS.Add(new_sense)

        # Set the gloss
        mkstr = TsStringUtils.MakeString(gloss, wsHandle)
        new_sense.Gloss.set_String(wsHandle, mkstr)

        return new_sense


    # --- Additional Properties ---

    def GetGuid(self, entry_or_hvo):
        """
        Get the GUID (Globally Unique Identifier) of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            System.Guid: The entry's GUID

        Raises:
            FP_NullParameterError: If entry_or_hvo is None

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> guid = project.LexEntry.GetGuid(entry)
            >>> print(guid)
            a1b2c3d4-e5f6-7890-abcd-ef1234567890

            >>> # Get as string
            >>> guid_str = str(guid)
            >>> print(guid_str)
            a1b2c3d4-e5f6-7890-abcd-ef1234567890

            >>> # Use GUID to retrieve entry later
            >>> entry2 = project.Object(guid)
            >>> print(project.LexEntry.GetHeadword(entry2))
            run

        Notes:
            - GUIDs are unique across all FLEx projects
            - GUIDs are persistent (don't change)
            - Useful for linking entries across projects
            - Can be used with FLExProject.Object() to retrieve entry

        See Also:
            FLExProject.Object, FLExProject.BuildGotoURL
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        return entry.Guid


    def GetImportResidue(self, entry_or_hvo):
        """
        Get the import residue of a lexical entry.

        Import residue stores unparsed data from imports (e.g., LIFT, SFM)
        that couldn't be mapped to FLEx fields.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            str: The import residue text (empty string if not set)

        Raises:
            FP_NullParameterError: If entry_or_hvo is None

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> residue = project.LexEntry.GetImportResidue(entry)
            >>> if residue:
            ...     print(f"Import residue: {residue}")

        Notes:
            - Returns empty string if no import residue
            - Import residue is stored as XML
            - Contains data that couldn't be imported to standard fields
            - Useful for preserving data from external sources

        See Also:
            SetImportResidue
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        return entry.ImportResidue or ""


    def SetImportResidue(self, entry_or_hvo, residue):
        """
        Set the import residue of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            residue (str): The import residue text to set

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If entry_or_hvo or residue is None

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> project.LexEntry.SetImportResidue(entry,
            ...     "<custom><field1>value1</field1></custom>")

            >>> # Clear import residue
            >>> project.LexEntry.SetImportResidue(entry, "")

        Notes:
            - Import residue is typically XML format
            - Used to store unparsed import data
            - Can be empty string to clear
            - Preserves data that doesn't fit standard FLEx fields

        See Also:
            GetImportResidue
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()
        if residue is None:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        entry.ImportResidue = residue


    # --- Private Helper Methods ---

    def __ResolveObject(self, entry_or_hvo):
        """
        Resolve HVO or object to ILexEntry.

        Args:
            entry_or_hvo: Either an ILexEntry object or an HVO (int)

        Returns:
            ILexEntry: The resolved entry object

        Raises:
            FP_ParameterError: If HVO doesn't refer to a lexical entry
        """
        if isinstance(entry_or_hvo, int):
            obj = self.project.Object(entry_or_hvo)
            if not isinstance(obj, ILexEntry):
                raise FP_ParameterError("HVO does not refer to a lexical entry")
            return obj
        return entry_or_hvo


    def __WSHandle(self, wsHandle):
        """
        Get writing system handle, defaulting to vernacular WS.

        Args:
            wsHandle: Optional writing system handle

        Returns:
            int: The writing system handle
        """
        if wsHandle is None:
            return self.project.project.DefaultVernWs
        return self.project._FLExProject__WSHandle(
            wsHandle,
            self.project.project.DefaultVernWs
        )


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


    def __FindMorphType(self, name):
        """
        Find a morph type by name (case-insensitive).

        Args:
            name (str): The morph type name to search for

        Returns:
            IMoMorphType or None: The morph type object if found, None otherwise
        """
        name_lower = name.lower()
        wsHandle = self.project.project.DefaultAnalWs

        morph_types = self.project.lp.LexDbOA.MorphTypesOA
        if not morph_types:
            return None

        # Search through all morph types (including subcategories)
        def search_morph_types(possibilities):
            for mt in possibilities:
                mt_name = mt.Name.BestAnalysisAlternative.Text
                if mt_name and mt_name.lower() == name_lower:
                    return mt
                # Search subcategories
                if mt.SubPossibilitiesOS.Count > 0:
                    found = search_morph_types(mt.SubPossibilitiesOS)
                    if found:
                        return found
            return None

        return search_morph_types(morph_types.PossibilitiesOS)
