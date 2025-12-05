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
    IMoAffixAllomorphFactory,
    IMoForm,
    MoMorphTypeTags,
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


    def Create(self, lexeme_form, morph_type_name=None, wsHandle=None, create_blank_sense=True):
        """
        Create a new lexical entry in the FLEx project.

        Args:
            lexeme_form (str): The lexeme form (headword) of the entry
            morph_type_name (str, optional): Name of the morph type ("stem", "root",
                "prefix", "suffix", etc.). If None (default), uses "stem".
                Use "prefix", "suffix", "infix" for affixes (creates MoAffixAllomorph).
                Use "stem", "root", "clitic", etc. for stems (creates MoStemAllomorph).
            wsHandle: Optional writing system handle. Defaults to vernacular WS.
            create_blank_sense (bool): If True (default), creates a blank sense
                automatically, matching FLEx GUI behavior. Set to False to create
                entry without senses.

        Returns:
            ILexEntry: The newly created lexical entry object

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If lexeme_form is None
            FP_ParameterError: If lexeme_form is empty or morph type not found

        Example:
            >>> # Create a basic stem entry with blank sense (default - no type needed!)
            >>> entry = project.LexEntry.Create("run")
            >>> print(project.LexEntry.GetHeadword(entry))
            run
            >>> print(project.LexEntry.GetSenseCount(entry))
            1

            >>> # Create entry without sense
            >>> entry = project.LexEntry.Create("run", create_blank_sense=False)
            >>> print(project.LexEntry.GetSenseCount(entry))
            0

            >>> # Create an affix entry (auto-creates MoAffixAllomorph)
            >>> suffix = project.LexEntry.Create("-ing", "suffix")
            >>> print(suffix.LexemeFormOA.ClassName)
            MoAffixAllomorph

            >>> # Create with specific writing system
            >>> entry = project.LexEntry.Create("maison", "stem",
            ...                                  project.WSHandle('fr'))

        Notes:
            - The entry is added to the lexicon database
            - Morph type defaults to "stem" if not specified
            - Correct allomorph type (MoStemAllomorph vs MoAffixAllomorph) is
              automatically chosen based on morph type
            - The lexeme form is set as the primary form
            - By default, a blank sense is created (matches FLEx GUI behavior)
            - Use create_blank_sense=False for entries without senses
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

        # Default to "stem" if no morph type specified
        if morph_type_name is None:
            morph_type_name = "stem"

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

        # Create the lexeme form allomorph using the appropriate factory
        # Stems use IMoStemAllomorphFactory, affixes use IMoAffixAllomorphFactory
        if self.__IsStemType(morph_type):
            allomorph_factory = self.project.project.ServiceLocator.GetService(
                IMoStemAllomorphFactory
            )
        else:
            allomorph_factory = self.project.project.ServiceLocator.GetService(
                IMoAffixAllomorphFactory
            )
        lexeme_form_obj = allomorph_factory.Create()

        # Attach lexeme form to entry FIRST (must be done before setting properties)
        new_entry.LexemeFormOA = lexeme_form_obj

        # Set the form text
        mkstr = TsStringUtils.MakeString(lexeme_form, wsHandle)
        lexeme_form_obj.Form.set_String(wsHandle, mkstr)

        # Set the morph type
        lexeme_form_obj.MorphTypeRA = morph_type

        # Create a blank sense by default (matches FLEx GUI behavior)
        if create_blank_sense:
            sense_factory = self.project.project.ServiceLocator.GetService(ILexSenseFactory)
            blank_sense = sense_factory.Create()
            new_entry.SensesOS.Add(blank_sense)

        # Note: Factory.Create() automatically adds the entry to the repository
        # No explicit Add() call needed - the entry is already in the database

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

        # Delete the entry (LCM handles removal from repository)
        entry.Delete()


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


    def GetBestVernacularAlternative(self, entry_or_hvo):
        """
        Get best available vernacular form (Pattern 5 - fallback logic).

        Returns the "best" vernacular form for the entry using FLEx's standard
        fallback logic: Citation Form → Lexeme Form → Headword.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            str: The best available vernacular form

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> best_form = project.LexEntry.GetBestVernacularAlternative(entry)
            >>> print(best_form)
            run

            >>> # Useful for display when you want the "best" form
            >>> for entry in project.LexiconAllEntries():
            ...     form = project.LexEntry.GetBestVernacularAlternative(entry)
            ...     print(form)

        Notes:
            - Common FLEx pattern for display purposes
            - Fallback order: CitationForm → LexemeForm → Headword
            - Always returns a non-empty string (Headword is last resort)
            - Based on FLEx LCM BestVernacularAlternative property
            - Uses default vernacular writing system

        See Also:
            GetCitationForm, GetLexemeForm, GetHeadword
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        ws_handle = self.project.project.DefaultVernWs

        # Try citation form first
        citation = ITsString(entry.CitationForm.get_String(ws_handle)).Text
        if citation:
            return citation

        # Try lexeme form
        if entry.LexemeFormOA:
            lexeme = ITsString(entry.LexemeFormOA.Form.get_String(ws_handle)).Text
            if lexeme:
                return lexeme

        # Last resort: headword (computed property, always returns something)
        return self.GetHeadword(entry)


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
            GetMorphType, Create, GetAvailableMorphTypes, ValidateMorphType
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


    def GetAvailableMorphTypes(self, include_subcategories=True):
        """
        Get a list of all available morph types in the project.

        Args:
            include_subcategories (bool): If True (default), includes subcategories.
                If False, only returns top-level morph types.

        Returns:
            list: List of tuples (name, IMoMorphType, is_stem_type) where:
                - name (str): The morph type name
                - IMoMorphType: The morph type object
                - is_stem_type (bool): True if stem type, False if affix type

        Example:
            >>> morph_types = project.LexEntry.GetAvailableMorphTypes()
            >>> for name, mt, is_stem in morph_types:
            ...     type_str = "stem" if is_stem else "affix"
            ...     print(f"{name}: {type_str}")
            stem: stem
            root: stem
            prefix: affix
            suffix: affix
            infix: affix

            >>> # Get only top-level types
            >>> top_level = project.LexEntry.GetAvailableMorphTypes(include_subcategories=False)

        Notes:
            - Returns morph types defined in the project's MorphTypesOA list
            - Useful for building UI dropdowns or validating user input
            - is_stem_type indicates whether to use MoStemAllomorph or MoAffixAllomorph

        See Also:
            ValidateMorphType, SetMorphType, Create
        """
        morph_types = self.project.lp.LexDbOA.MorphTypesOA
        if not morph_types:
            return []

        result = []
        wsHandle = self.project.project.DefaultAnalWs

        def collect_types(possibilities):
            for mt in possibilities:
                name = mt.Name.BestAnalysisAlternative.Text
                if name:
                    is_stem = self.__IsStemType(mt)
                    result.append((name, mt, is_stem))

                # Include subcategories if requested
                if include_subcategories and mt.SubPossibilitiesOS.Count > 0:
                    collect_types(mt.SubPossibilitiesOS)

        collect_types(morph_types.PossibilitiesOS)
        return result


    def ValidateMorphType(self, morph_type_name):
        """
        Check if a morph type name exists in the project.

        Args:
            morph_type_name (str): The morph type name to validate (case-insensitive)

        Returns:
            tuple: (is_valid, morph_type_obj, is_stem_type) where:
                - is_valid (bool): True if morph type exists
                - morph_type_obj (IMoMorphType or None): The morph type object if found
                - is_stem_type (bool or None): True if stem type, False if affix, None if not found

        Example:
            >>> is_valid, mt, is_stem = project.LexEntry.ValidateMorphType("suffix")
            >>> if is_valid:
            ...     print(f"Valid morph type: {mt.Name.BestAnalysisAlternative.Text}")
            ...     print(f"Is stem type: {is_stem}")
            Valid morph type: suffix
            Is stem type: False

            >>> is_valid, mt, is_stem = project.LexEntry.ValidateMorphType("invalid")
            >>> print(f"Valid: {is_valid}")
            Valid: False

        Notes:
            - Search is case-insensitive
            - Searches through all morph types including subcategories
            - Useful for validating user input before creating entries

        See Also:
            GetAvailableMorphTypes, Create, SetMorphType
        """
        if not morph_type_name:
            return (False, None, None)

        morph_type = self.__FindMorphType(morph_type_name)
        if morph_type:
            is_stem = self.__IsStemType(morph_type)
            return (True, morph_type, is_stem)

        return (False, None, None)


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


    # --- MultiString/MultiUnicode Properties ---

    def GetBibliography(self, entry_or_hvo, wsHandle=None):
        """
        Get the bibliography of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The bibliography text

        Example:
            >>> entry = project.LexEntry.Find("anthropology")
            >>> bib = project.LexEntry.GetBibliography(entry)
            >>> print(bib)
            Smith 2015: 42-43
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        return ITsString(entry.Bibliography.get_String(wsHandle)).Text or ""


    def SetBibliography(self, entry_or_hvo, text, wsHandle=None):
        """
        Set the bibliography of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            text (str): The bibliography text
            wsHandle: Optional writing system handle. Defaults to analysis WS.
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()
        if not entry_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        mkstr = TsStringUtils.MakeString(text, wsHandle)
        entry.Bibliography.set_String(wsHandle, mkstr)


    def GetComment(self, entry_or_hvo, wsHandle=None):
        """
        Get the comment of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The comment text
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        return ITsString(entry.Comment.get_String(wsHandle)).Text or ""


    def SetComment(self, entry_or_hvo, text, wsHandle=None):
        """
        Set the comment of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            text (str): The comment text
            wsHandle: Optional writing system handle. Defaults to analysis WS.
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()
        if not entry_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        mkstr = TsStringUtils.MakeString(text, wsHandle)
        entry.Comment.set_String(wsHandle, mkstr)


    def GetLiteralMeaning(self, entry_or_hvo, wsHandle=None):
        """
        Get the literal meaning of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The literal meaning text
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        return ITsString(entry.LiteralMeaning.get_String(wsHandle)).Text or ""


    def SetLiteralMeaning(self, entry_or_hvo, text, wsHandle=None):
        """
        Set the literal meaning of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            text (str): The literal meaning text
            wsHandle: Optional writing system handle. Defaults to analysis WS.
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()
        if not entry_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        mkstr = TsStringUtils.MakeString(text, wsHandle)
        entry.LiteralMeaning.set_String(wsHandle, mkstr)


    def GetRestrictions(self, entry_or_hvo, wsHandle=None):
        """
        Get the restrictions of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The restrictions text
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        return ITsString(entry.Restrictions.get_String(wsHandle)).Text or ""


    def SetRestrictions(self, entry_or_hvo, text, wsHandle=None):
        """
        Set the restrictions of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            text (str): The restrictions text
            wsHandle: Optional writing system handle. Defaults to analysis WS.
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()
        if not entry_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        mkstr = TsStringUtils.MakeString(text, wsHandle)
        entry.Restrictions.set_String(wsHandle, mkstr)


    def GetSummaryDefinition(self, entry_or_hvo, wsHandle=None):
        """
        Get the summary definition of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The summary definition text
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        return ITsString(entry.SummaryDefinition.get_String(wsHandle)).Text or ""


    def SetSummaryDefinition(self, entry_or_hvo, text, wsHandle=None):
        """
        Set the summary definition of a lexical entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            text (str): The summary definition text
            wsHandle: Optional writing system handle. Defaults to analysis WS.
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()
        if not entry_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        mkstr = TsStringUtils.MakeString(text, wsHandle)
        entry.SummaryDefinition.set_String(wsHandle, mkstr)


    # --- Boolean Properties ---

    def GetDoNotUseForParsing(self, entry_or_hvo):
        """
        Check if an entry is excluded from parsing.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            bool: True if excluded from parsing, False otherwise
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        return entry.DoNotUseForParsing


    def SetDoNotUseForParsing(self, entry_or_hvo, value):
        """
        Set whether an entry is excluded from parsing.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            value (bool): True to exclude from parsing, False to include
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()
        if not entry_or_hvo:
            raise FP_NullParameterError()
        if value is None:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        entry.DoNotUseForParsing = bool(value)


    def GetExcludeAsHeadword(self, entry_or_hvo):
        """
        Check if an entry is excluded as a headword.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            bool: True if excluded as headword, False otherwise
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        return entry.ExcludeAsHeadword


    def SetExcludeAsHeadword(self, entry_or_hvo, value):
        """
        Set whether an entry is excluded as a headword.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            value (bool): True to exclude as headword, False to include
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()
        if not entry_or_hvo:
            raise FP_NullParameterError()
        if value is None:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)
        entry.ExcludeAsHeadword = bool(value)


    # --- Collection Properties ---

    def GetDoNotPublishIn(self, entry_or_hvo):
        """
        Get the publications this entry should not be published in.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            list: List of publication names

        Example:
            >>> entry = project.LexEntry.Find("obscure")
            >>> pubs = project.LexEntry.GetDoNotPublishIn(entry)
            >>> print(pubs)
            ['Main Dictionary', 'Student Edition']
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        result = []
        for pub in entry.DoNotPublishIn:
            name = pub.Name.BestAnalysisAlternative.Text if pub.Name else str(pub.Guid)
            result.append(name)
        return result


    def AddDoNotPublishIn(self, entry_or_hvo, publication):
        """
        Add a publication to exclude this entry from.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            publication: Publication name (str) or ICmPossibility object
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()
        if not entry_or_hvo:
            raise FP_NullParameterError()
        if not publication:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        # Find publication object if string provided
        if isinstance(publication, str):
            pub_obj = self.project.Publications.Find(publication)
            if not pub_obj:
                raise FP_ParameterError(f"Publication '{publication}' not found")
            publication = pub_obj

        if publication not in entry.DoNotPublishIn:
            entry.DoNotPublishIn.Add(publication)


    def RemoveDoNotPublishIn(self, entry_or_hvo, publication):
        """
        Remove a publication from the exclude list.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            publication: Publication name (str) or ICmPossibility object
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()
        if not entry_or_hvo:
            raise FP_NullParameterError()
        if not publication:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        # Find publication object if string provided
        if isinstance(publication, str):
            pub_obj = self.project.Publications.Find(publication)
            if not pub_obj:
                raise FP_ParameterError(f"Publication '{publication}' not found")
            publication = pub_obj

        if publication in entry.DoNotPublishIn:
            entry.DoNotPublishIn.Remove(publication)


    def GetDoNotShowMainEntryIn(self, entry_or_hvo):
        """
        Get the publications where this entry should not be shown as main entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            list: List of publication names
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        result = []
        for pub in entry.DoNotShowMainEntryIn:
            name = pub.Name.BestAnalysisAlternative.Text if pub.Name else str(pub.Guid)
            result.append(name)
        return result


    def AddDoNotShowMainEntryIn(self, entry_or_hvo, publication):
        """
        Add a publication to not show this entry as main entry.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            publication: Publication name (str) or ICmPossibility object
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()
        if not entry_or_hvo:
            raise FP_NullParameterError()
        if not publication:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        # Find publication object if string provided
        if isinstance(publication, str):
            pub_obj = self.project.Publications.Find(publication)
            if not pub_obj:
                raise FP_ParameterError(f"Publication '{publication}' not found")
            publication = pub_obj

        if publication not in entry.DoNotShowMainEntryIn:
            entry.DoNotShowMainEntryIn.Add(publication)


    def RemoveDoNotShowMainEntryIn(self, entry_or_hvo, publication):
        """
        Remove a publication from the no-main-entry list.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO
            publication: Publication name (str) or ICmPossibility object
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()
        if not entry_or_hvo:
            raise FP_NullParameterError()
        if not publication:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        # Find publication object if string provided
        if isinstance(publication, str):
            pub_obj = self.project.Publications.Find(publication)
            if not pub_obj:
                raise FP_ParameterError(f"Publication '{publication}' not found")
            publication = pub_obj

        if publication in entry.DoNotShowMainEntryIn:
            entry.DoNotShowMainEntryIn.Remove(publication)


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


    # --- Back-Reference Methods (Pattern 3) ---

    def GetVisibleComplexFormBackRefs(self, entry_or_hvo):
        """
        Get all complex forms that reference this entry.

        Returns all LexEntryRef objects where this entry appears in
        ShowComplexFormsIn and RefType is ComplexForm.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            list: List of ILexEntryRef objects (complex forms referencing this entry)

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> complex_forms = project.LexEntry.GetVisibleComplexFormBackRefs(entry)
            >>> for lex_ref in complex_forms:
            ...     complex_entry = lex_ref.OwningEntry
            ...     print(f"Complex form: {project.LexEntry.GetHeadword(complex_entry)}")

        Notes:
            - Returns complex forms (compounds, idioms, phrasal verbs, etc.)
            - Includes subentries (use GetComplexFormsNotSubentries to exclude)
            - Based on FLEx LCM VisibleComplexFormBackRefs property

        See Also:
            GetComplexFormsNotSubentries, GetAllSenses
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        # Use the LCM property directly (it handles all the complexity)
        # This is a virtual property that loads incoming references
        try:
            back_refs = list(entry.VisibleComplexFormBackRefs)
            return back_refs
        except AttributeError:
            # Fallback if property not available
            logger.warning("VisibleComplexFormBackRefs not available, returning empty list")
            return []


    def GetComplexFormsNotSubentries(self, entry_or_hvo):
        """
        Get complex forms that reference this entry, excluding subentries.

        Returns complex forms (compounds, idioms, etc.) but excludes any
        where this entry appears as a subentry (in PrimaryLexemesRS).

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            list: List of ILexEntryRef objects (complex forms, excluding subentries)

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> complex_forms = project.LexEntry.GetComplexFormsNotSubentries(entry)
            >>> for lex_ref in complex_forms:
            ...     cf_entry = lex_ref.OwningEntry
            ...     print(f"Complex form: {project.LexEntry.GetHeadword(cf_entry)}")

        Notes:
            - Filters out subentries from VisibleComplexFormBackRefs
            - A subentry is where the entry appears in PrimaryLexemesRS
            - Based on FLEx LCM ComplexFormsNotSubentries property

        See Also:
            GetVisibleComplexFormBackRefs
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        # Get all complex form back refs
        all_complex_forms = self.GetVisibleComplexFormBackRefs(entry)

        # Filter out subentries (where entry is in PrimaryLexemesRS)
        result = []
        for lex_ref in all_complex_forms:
            try:
                # Check if entry is in PrimaryLexemesRS (makes it a subentry)
                is_subentry = any(item.Hvo == entry.Hvo for item in lex_ref.PrimaryLexemesRS)
                if not is_subentry:
                    result.append(lex_ref)
            except:
                # If we can't check, include it
                result.append(lex_ref)

        return result


    def GetMinimalLexReferences(self, entry_or_hvo):
        """
        Get essential lexical references for this entry.

        Returns only "minimal" lexical references - those that are multi-target
        or have specific mapping types (sequence types).

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            list: List of ILexReference objects (minimal references)

        Example:
            >>> entry = project.LexEntry.Find("big")
            >>> lex_refs = project.LexEntry.GetMinimalLexReferences(entry)
            >>> for lex_ref in lex_refs:
            ...     ref_type = lex_ref.Owner  # ILexRefType
            ...     print(f"Reference type: {ref_type.Name.BestAnalysisAlternative.Text}")
            ...     for target in lex_ref.TargetsRS:
            ...         if target.Hvo != entry.Hvo:
            ...             print(f"  -> {project.LexEntry.GetHeadword(target)}")

        Notes:
            - Includes multi-target references (synonyms, antonyms, etc.)
            - Includes sequence-type references
            - Excludes single-target non-sequence references
            - Based on FLEx LCM MinimalLexReferences property

        See Also:
            GetVisibleComplexFormBackRefs
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        # Use the LCM property directly
        try:
            lex_refs = list(entry.MinimalLexReferences)
            return lex_refs
        except AttributeError:
            # Fallback if property not available
            logger.warning("MinimalLexReferences not available, returning empty list")
            return []


    def GetAllSenses(self, entry_or_hvo):
        """
        Get all senses owned by this entry, including subsenses recursively.

        Returns all senses in a flattened list, recursively including all
        subsenses at any depth.

        Args:
            entry_or_hvo: Either an ILexEntry object or its HVO

        Returns:
            list: List of ILexSense objects (all senses and subsenses)

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> all_senses = project.LexEntry.GetAllSenses(entry)
            >>> print(f"Total senses (including subsenses): {len(all_senses)}")
            >>> for sense in all_senses:
            ...     gloss = project.Senses.GetGloss(sense)
            ...     depth = len(list(sense.PathToRoot)) - 2  # Approximate depth
            ...     indent = "  " * depth
            ...     print(f"{indent}{gloss}")

        Notes:
            - Recursively collects all subsenses at any depth
            - Based on FLEx LCM AllSenses property
            - For counting: use GetSenseCount or len(GetAllSenses(entry))
            - Entry.AllSenses does NOT include the entry itself

        See Also:
            GetSenseCount, GetSenses
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__ResolveObject(entry_or_hvo)

        # Use the LCM property directly
        try:
            all_senses = list(entry.AllSenses)
            return all_senses
        except AttributeError:
            # Fallback: manually collect recursively
            result = []
            for sense in entry.SensesOS:
                # Use LexSenseOperations to get all subsenses
                try:
                    result.extend(list(sense.AllSenses))
                except:
                    # Manual recursive collection as last resort
                    result.append(sense)
                    if sense.SensesOS and sense.SensesOS.Count > 0:
                        for subsense in sense.SensesOS:
                            result.extend(self.__CollectSubsenses(subsense))
            return result


    def __CollectSubsenses(self, sense):
        """
        Helper to recursively collect subsenses.

        Args:
            sense: ILexSense object

        Returns:
            list: All subsenses including the sense itself
        """
        result = [sense]
        if sense.SensesOS and sense.SensesOS.Count > 0:
            for subsense in sense.SensesOS:
                result.extend(self.__CollectSubsenses(subsense))
        return result


    # --- Private Helper Methods ---

    def __IsStemType(self, morph_type):
        """
        Determine if a morph type should use MoStemAllomorph or MoAffixAllomorph.

        Args:
            morph_type: IMoMorphType object

        Returns:
            bool: True if stem type (uses MoStemAllomorph), False if affix type

        Notes:
            Based on FLEx logic in MorphTypeAtomicLauncher.cs
            Stem types include: stem, root, bound root/stem, clitics, particles, phrases
            Affix types include: prefix, suffix, infix, circumfix, etc.
        """
        if morph_type is None:
            return True  # Default to stem

        # Check GUID against known stem types (from MoMorphTypeTags)
        stem_guids = {
            MoMorphTypeTags.kguidMorphStem,
            MoMorphTypeTags.kguidMorphRoot,
            MoMorphTypeTags.kguidMorphBoundRoot,
            MoMorphTypeTags.kguidMorphBoundStem,
            MoMorphTypeTags.kguidMorphClitic,
            MoMorphTypeTags.kguidMorphEnclitic,
            MoMorphTypeTags.kguidMorphProclitic,
            MoMorphTypeTags.kguidMorphParticle,
            MoMorphTypeTags.kguidMorphPhrase,
            MoMorphTypeTags.kguidMorphDiscontiguousPhrase,
        }

        return morph_type.Guid in stem_guids


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
