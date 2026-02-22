#
#   ReversalOperations.py
#
#   Class: ReversalOperations
#          Reversal entry operations for FieldWorks Language Explorer
#          projects via SIL Language and Culture Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

# Import BaseOperations parent class
from ..BaseOperations import BaseOperations

# Import FLEx LCM types
from SIL.LCModel import (
    IReversalIndex,
    IReversalIndexEntry,
    IReversalIndexEntryFactory,
    ILexSense,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)

class ReversalOperations(BaseOperations):
    """
    This class provides operations for managing reversal entries in a
    FieldWorks project.

    Reversal entries allow users to look up vernacular words from analysis
    language glosses. Each reversal index corresponds to a specific writing
    system (e.g., English, French) and contains entries that link back to
    lexical senses.

    This class should be accessed via FLExProject.Reversal property.

    Usage::

        from flexlibs2 import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get all reversal indexes
        for index in project.Reversal.GetAllIndexes():
            ws = index.WritingSystem
            print(f"Reversal index: {ws}")

        # Get English reversal index
        en_index = project.Reversal.GetIndex("en")
        if en_index:
            # Get all entries in this index
            for entry in project.Reversal.GetAll(en_index):
                form = project.Reversal.GetForm(entry)
                print(f"Reversal: {form}")

            # Create a new reversal entry
            entry = project.Reversal.Create(en_index, "run", "en")

            # Link to a sense
            lexentry = project.LexEntry.Find("run")
            if lexentry:
                senses = project.LexEntry.GetSenses(lexentry)
                if senses:
                    project.Reversal.AddSense(entry, senses[0])

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize ReversalOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)

    # --- Reversal Index Management ---

    def GetAllIndexes(self):
        """
        Get all reversal indexes in the project.

        A reversal index allows looking up vernacular words from analysis
        language glosses. Each index is tied to a specific writing system
        (e.g., English, French, Spanish).

        Returns:
            list: List of IReversalIndex objects.

        Example:
            >>> for index in project.Reversal.GetAllIndexes():
            ...     ws = index.WritingSystem
            ...     count = index.EntriesOC.Count
            ...     print(f"{ws}: {count} entries")
            en: 245 entries
            fr: 132 entries

        Notes:
            - Returns empty list if no reversal indexes exist
            - Each index corresponds to one analysis writing system
            - Indexes are created in FLEx UI via Tools > Configure > Reversal Indexes
            - Returns all indexes regardless of whether they have entries

        See Also:
            GetIndex, FindIndex
        """
        return list(self.project.lexDB.ReversalIndexesOC)

    def GetIndex(self, ws):
        """
        Get the reversal index for a specific writing system.

        Args:
            ws (str): The writing system language tag (e.g., "en", "fr", "es").

        Returns:
            IReversalIndex or None: The reversal index object if found, None otherwise.

        Raises:
            FP_NullParameterError: If ws is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> if en_index:
            ...     print(f"English reversal index has {en_index.EntriesOC.Count} entries")
            English reversal index has 245 entries

            >>> # Check if index exists
            >>> fr_index = project.Reversal.GetIndex("fr")
            >>> if not fr_index:
            ...     print("No French reversal index")

        Notes:
            - Returns None if no reversal index exists for this writing system
            - Language tags are case-insensitive
            - Ignores '-' vs '_' differences in language tags
            - Use GetAllIndexes() to see all available indexes

        See Also:
            GetAllIndexes, FindIndex
        """
        self._ValidateParam(ws, "ws")

        ws_normalized = self.__NormalizeLangTag(ws)

        for ri in self.project.lexDB.ReversalIndexesOC:
            if self.__NormalizeLangTag(ri.WritingSystem) == ws_normalized:
                return ri

        return None

    def FindIndex(self, ws):
        """
        Find a reversal index by writing system (alias for GetIndex).

        Args:
            ws (str): The writing system language tag (e.g., "en", "fr", "es").

        Returns:
            IReversalIndex or None: The reversal index object if found, None otherwise.

        Raises:
            FP_NullParameterError: If ws is None.

        Example:
            >>> index = project.Reversal.FindIndex("en")
            >>> if index:
            ...     print(f"Found index for {index.WritingSystem}")

        Notes:
            - This is an alias for GetIndex() for consistency with other operations
            - See GetIndex() for full documentation

        See Also:
            GetIndex, GetAllIndexes
        """
        return self.GetIndex(ws)

    # --- Entry CRUD Operations ---

    def GetAll(self, reversal_index):
        """
        Get all reversal entries in a reversal index.

        Args:
            reversal_index: The IReversalIndex object.

        Returns:
            list: List of IReversalIndexEntry objects.

        Raises:
            FP_NullParameterError: If reversal_index is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> if en_index:
            ...     for entry in project.Reversal.GetAll(en_index):
            ...         form = project.Reversal.GetForm(entry)
            ...         senses = project.Reversal.GetSenses(entry)
            ...         print(f"{form}: {len(senses)} senses")
            run: 3 senses
            walk: 2 senses
            house: 1 senses

        Notes:
            - Returns empty list if index has no entries
            - Entries are returned in database order (not alphabetical)
            - Includes both top-level entries and subentries
            - Use GetForm() to access the reversal form text

        See Also:
            Create, Find, GetForm
        """
        self._ValidateParam(reversal_index, "reversal_index")

        return list(reversal_index.EntriesOC)

    def Create(self, reversal_index, form, ws=None):
        """
        Create a new reversal entry in a reversal index.

        Args:
            reversal_index: The IReversalIndex object to add the entry to.
            form (str): The reversal form text (e.g., "run", "walk").
            ws (str or int): Optional writing system tag or handle. If None,
                uses the reversal index's writing system.

        Returns:
            IReversalIndexEntry: The newly created reversal entry object.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled.
            FP_NullParameterError: If reversal_index or form is None.
            FP_ParameterError: If form is empty.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> if en_index:
            ...     # Create a reversal entry
            ...     entry = project.Reversal.Create(en_index, "run")
            ...     print(f"Created: {project.Reversal.GetForm(entry)}")
            Created: run

            >>> # Create with explicit writing system
            >>> entry2 = project.Reversal.Create(en_index, "walk", "en")

        Notes:
            - The entry is added to the reversal index
            - No senses are linked automatically - use AddSense()
            - Does not check for duplicates - use Find() or Exists() first
            - Entry GUID is auto-generated
            - Default writing system is the reversal index's writing system

        See Also:
            Delete, Exists, Find, AddSense
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(reversal_index, "reversal_index")
        self._ValidateParam(form, "form")

        self._ValidateStringNotEmpty(form, "form")

        # Use reversal index's writing system if not specified
        if ws is None:
            ws = reversal_index.WritingSystem

        wsHandle = self.__WSHandleAnalysis(ws)

        # Create the new reversal entry using the factory
        factory = self.project.project.ServiceLocator.GetService(
            IReversalIndexEntryFactory
        )
        new_entry = factory.Create()

        # Add entry to reversal index (must be done before setting properties)
        reversal_index.EntriesOC.Add(new_entry)

        # Set the reversal form text
        mkstr = TsStringUtils.MakeString(form, wsHandle)
        new_entry.ReversalForm.set_String(wsHandle, mkstr)

        return new_entry

    def Delete(self, reversal_entry):
        """
        Delete a reversal entry from its reversal index.

        Args:
            reversal_entry: The IReversalIndexEntry object to delete.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled.
            FP_NullParameterError: If reversal_entry is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> entry = project.Reversal.Find(en_index, "obsolete")
            >>> if entry:
            ...     project.Reversal.Delete(entry)

        Warning:
            - This is a destructive operation
            - All subentries will also be deleted
            - Links to senses will be removed
            - Cannot be undone

        Notes:
            - Deletion cascades to all owned objects (subentries)
            - Sense links are automatically cleaned up
            - If entry has parent, it's removed from parent's subentries
            - Consider unlinking senses first if needed

        See Also:
            Create, RemoveSense
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(reversal_entry, "reversal_entry")

        # Get the reversal index
        reversal_index = reversal_entry.ReversalIndex

        # Remove from reversal index
        if reversal_index:
            reversal_index.EntriesOC.Remove(reversal_entry)

    def Find(self, reversal_index, form, ws=None):
        """
        Find a reversal entry by its form text.

        Args:
            reversal_index: The IReversalIndex object to search in.
            form (str): The reversal form text to search for.
            ws (str or int): Optional writing system tag or handle. If None,
                uses the reversal index's writing system.

        Returns:
            IReversalIndexEntry or None: The entry object if found, None otherwise.

        Raises:
            FP_NullParameterError: If reversal_index or form is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> entry = project.Reversal.Find(en_index, "run")
            >>> if entry:
            ...     senses = project.Reversal.GetSenses(entry)
            ...     print(f"Found 'run' with {len(senses)} senses")
            Found 'run' with 3 senses

        Notes:
            - Returns first match only
            - Search is case-sensitive
            - Search is writing-system specific
            - Returns None if not found (doesn't raise exception)
            - Searches only top-level entries, not subentries

        See Also:
            Exists, GetAll, Create
        """
        self._ValidateParam(reversal_index, "reversal_index")
        self._ValidateParam(form, "form")

        if not form or not form.strip():
            return None

        # Use reversal index's writing system if not specified
        if ws is None:
            ws = reversal_index.WritingSystem

        wsHandle = self.__WSHandleAnalysis(ws)

        # Search through all entries
        for entry in reversal_index.EntriesOC:
            entry_form = ITsString(entry.ReversalForm.get_String(wsHandle)).Text
            if entry_form == form:
                return entry

        return None

    def Exists(self, reversal_index, form, ws=None):
        """
        Check if a reversal entry with the given form exists.

        Args:
            reversal_index: The IReversalIndex object to search in.
            form (str): The reversal form text to check.
            ws (str or int): Optional writing system tag or handle. If None,
                uses the reversal index's writing system.

        Returns:
            bool: True if an entry exists with this form, False otherwise.

        Raises:
            FP_NullParameterError: If reversal_index or form is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> if not project.Reversal.Exists(en_index, "run"):
            ...     entry = project.Reversal.Create(en_index, "run")
            >>> else:
            ...     print("Entry already exists")

        Notes:
            - Search is case-sensitive
            - Search is writing-system specific
            - Returns False for empty or whitespace-only forms
            - Use Find() to get the actual entry object

        See Also:
            Find, Create
        """
        self._ValidateParam(reversal_index, "reversal_index")
        self._ValidateParam(form, "form")

        if not form or not form.strip():
            return False

        return self.Find(reversal_index, form, ws) is not None

    # --- Form Management ---

    def GetForm(self, reversal_entry, ws=None):
        """
        Get the reversal form text of a reversal entry.

        Args:
            reversal_entry: The IReversalIndexEntry object.
            ws (str or int): Optional writing system tag or handle. If None,
                uses the entry's reversal index writing system.

        Returns:
            str: The reversal form text (empty string if not set).

        Raises:
            FP_NullParameterError: If reversal_entry is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> for entry in project.Reversal.GetAll(en_index):
            ...     form = project.Reversal.GetForm(entry)
            ...     print(f"Reversal: {form}")
            Reversal: run
            Reversal: walk
            Reversal: house

            >>> # Get in specific writing system
            >>> form_en = project.Reversal.GetForm(entry, "en")

        Notes:
            - Returns empty string if form not set in specified writing system
            - Default writing system is the reversal index's writing system
            - This is the primary display form of the reversal entry
            - Equivalent to FLExProject.ReversalGetForm()

        See Also:
            SetForm, Find
        """
        self._ValidateParam(reversal_entry, "reversal_entry")

        # Use reversal index's writing system if not specified
        if ws is None:
            reversal_index = reversal_entry.ReversalIndex
            if reversal_index:
                ws = reversal_index.WritingSystem
            else:
                # Fall back to default analysis WS
                ws = None

        wsHandle = self.__WSHandleAnalysis(ws)

        form = ITsString(reversal_entry.ReversalForm.get_String(wsHandle)).Text
        return form or ""

    def SetForm(self, reversal_entry, text, ws=None):
        """
        Set the reversal form text of a reversal entry.

        Args:
            reversal_entry: The IReversalIndexEntry object.
            text (str): The new reversal form text.
            ws (str or int): Optional writing system tag or handle. If None,
                uses the entry's reversal index writing system.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled.
            FP_NullParameterError: If reversal_entry or text is None.
            FP_ParameterError: If text is empty.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> entry = project.Reversal.Find(en_index, "runing")  # typo
            >>> if entry:
            ...     project.Reversal.SetForm(entry, "running")
            ...     print(f"Updated: {project.Reversal.GetForm(entry)}")
            Updated: running

        Notes:
            - Default writing system is the reversal index's writing system
            - Changes the primary display form
            - Does not check for duplicates
            - Equivalent to FLExProject.ReversalSetForm()

        See Also:
            GetForm, Create
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(reversal_entry, "reversal_entry")
        self._ValidateParam(text, "text")

        self._ValidateStringNotEmpty(text, "text")

        # Use reversal index's writing system if not specified
        if ws is None:
            reversal_index = reversal_entry.ReversalIndex
            if reversal_index:
                ws = reversal_index.WritingSystem
            else:
                # Fall back to default analysis WS
                ws = None

        wsHandle = self.__WSHandleAnalysis(ws)

        # Set the reversal form
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        reversal_entry.ReversalForm.set_String(wsHandle, mkstr)

    # --- Sense Linking ---

    def GetSenses(self, reversal_entry):
        """
        Get all senses linked to a reversal entry.

        Reversal entries link to lexical senses, allowing users to find
        vernacular words from analysis language glosses.

        Args:
            reversal_entry: The IReversalIndexEntry object.

        Returns:
            list: List of ILexSense objects linked to this reversal entry.

        Raises:
            FP_NullParameterError: If reversal_entry is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> entry = project.Reversal.Find(en_index, "run")
            >>> if entry:
            ...     senses = project.Reversal.GetSenses(entry)
            ...     for sense in senses:
            ...         gloss = project.LexiconGetSenseGloss(sense)
            ...         print(f"Sense: {gloss}")
            Sense: to move rapidly on foot
            Sense: to operate or function

        Notes:
            - Returns empty list if no senses are linked
            - Senses are returned in database order
            - Multiple senses can be linked to one reversal entry
            - Each sense represents a distinct meaning

        See Also:
            AddSense, RemoveSense, GetSenseCount
        """
        self._ValidateParam(reversal_entry, "reversal_entry")

        return list(reversal_entry.SensesRS)

    def AddSense(self, reversal_entry, sense):
        """
        Link a lexical sense to a reversal entry.

        This creates a bidirectional link between the reversal entry and
        the lexical sense, allowing lookup in both directions.

        Args:
            reversal_entry: The IReversalIndexEntry object.
            sense: The ILexSense object to link.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled.
            FP_NullParameterError: If reversal_entry or sense is None.

        Example:
            >>> # Create reversal entry and link to sense
            >>> en_index = project.Reversal.GetIndex("en")
            >>> entry = project.Reversal.Create(en_index, "run")
            >>>
            >>> # Find lexical entry and get its sense
            >>> lexentry = project.LexEntry.Find("run")
            >>> if lexentry:
            ...     senses = project.LexEntry.GetSenses(lexentry)
            ...     if senses:
            ...         project.Reversal.AddSense(entry, senses[0])
            ...         print(f"Linked {len(project.Reversal.GetSenses(entry))} senses")
            Linked 1 senses

        Notes:
            - Creates a bidirectional link (sense.ReferringReversalIndexEntries)
            - Does not check for duplicates - link can be added multiple times
            - Use GetSenses() to check if sense is already linked
            - Link persists until removed with RemoveSense()

        See Also:
            RemoveSense, GetSenses, GetSenseCount
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(reversal_entry, "reversal_entry")
        self._ValidateParam(sense, "sense")

        # Add sense to reversal entry's sense collection
        reversal_entry.SensesRS.Add(sense)

    def RemoveSense(self, reversal_entry, sense):
        """
        Unlink a lexical sense from a reversal entry.

        This removes the bidirectional link between the reversal entry
        and the lexical sense.

        Args:
            reversal_entry: The IReversalIndexEntry object.
            sense: The ILexSense object to unlink.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled.
            FP_NullParameterError: If reversal_entry or sense is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> entry = project.Reversal.Find(en_index, "run")
            >>> if entry:
            ...     senses = project.Reversal.GetSenses(entry)
            ...     if senses:
            ...         # Remove first sense
            ...         project.Reversal.RemoveSense(entry, senses[0])
            ...         print(f"{len(project.Reversal.GetSenses(entry))} senses remain")

        Notes:
            - Removes the bidirectional link
            - Does nothing if sense is not linked (no error raised)
            - Does not delete the sense - only removes the link
            - Reversal entry remains even if all senses are removed

        See Also:
            AddSense, GetSenses, GetSenseCount
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(reversal_entry, "reversal_entry")
        self._ValidateParam(sense, "sense")

        # Remove sense from reversal entry's sense collection
        reversal_entry.SensesRS.Remove(sense)

    def GetSenseCount(self, reversal_entry):
        """
        Get the count of senses linked to a reversal entry.

        Args:
            reversal_entry: The IReversalIndexEntry object.

        Returns:
            int: The number of senses linked to this entry (0 if none).

        Raises:
            FP_NullParameterError: If reversal_entry is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> entry = project.Reversal.Find(en_index, "run")
            >>> if entry:
            ...     count = project.Reversal.GetSenseCount(entry)
            ...     print(f"Entry has {count} linked senses")
            Entry has 3 linked senses

            >>> # Check if entry has senses
            >>> if project.Reversal.GetSenseCount(entry) == 0:
            ...     print("Entry has no linked senses - add one!")

        Notes:
            - Returns 0 if entry has no linked senses
            - More efficient than len(GetSenses()) for large entries
            - Includes all linked senses (no filtering)

        See Also:
            GetSenses, AddSense, RemoveSense
        """
        self._ValidateParam(reversal_entry, "reversal_entry")

        return reversal_entry.SensesRS.Count

    # --- Subentries ---

    def GetSubentries(self, reversal_entry):
        """
        Get all subentries of a reversal entry.

        Subentries are nested reversal entries that represent compounds,
        phrases, or related terms under a main entry.

        Args:
            reversal_entry: The IReversalIndexEntry object (parent).

        Returns:
            list: List of IReversalIndexEntry objects (children).

        Raises:
            FP_NullParameterError: If reversal_entry is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> entry = project.Reversal.Find(en_index, "run")
            >>> if entry:
            ...     subentries = project.Reversal.GetSubentries(entry)
            ...     for subentry in subentries:
            ...         form = project.Reversal.GetForm(subentry)
            ...         print(f"  Subentry: {form}")
            Subentry: run away
            Subentry: run into
            Subentry: run out

        Notes:
            - Returns empty list if entry has no subentries
            - Subentries are ordered as they appear in the entry
            - Subentries can have their own subentries (nested)
            - Use CreateSubentry() to add new subentries

        See Also:
            CreateSubentry, GetParentEntry
        """
        self._ValidateParam(reversal_entry, "reversal_entry")

        return list(reversal_entry.SubentriesOS)

    def CreateSubentry(self, parent_entry, form, ws=None):
        """
        Create a new subentry under a parent reversal entry.

        Args:
            parent_entry: The IReversalIndexEntry object (parent).
            form (str): The reversal form text for the subentry.
            ws (str or int): Optional writing system tag or handle. If None,
                uses the parent entry's reversal index writing system.

        Returns:
            IReversalIndexEntry: The newly created subentry object.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled.
            FP_NullParameterError: If parent_entry or form is None.
            FP_ParameterError: If form is empty.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> parent = project.Reversal.Find(en_index, "run")
            >>> if parent:
            ...     # Create subentry for "run away"
            ...     subentry = project.Reversal.CreateSubentry(parent, "run away")
            ...     print(f"Created subentry: {project.Reversal.GetForm(subentry)}")
            Created subentry: run away

            >>> # Subentries can have their own senses
            >>> lexentry = project.LexEntry.Find("run away")
            >>> if lexentry:
            ...     senses = project.LexEntry.GetSenses(lexentry)
            ...     if senses:
            ...         project.Reversal.AddSense(subentry, senses[0])

        Notes:
            - Subentry is added to parent's subentries collection
            - No senses are linked automatically - use AddSense()
            - Subentries can have their own subentries (nested)
            - Default writing system is the reversal index's writing system

        See Also:
            GetSubentries, GetParentEntry, Create
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(parent_entry, "parent_entry")
        self._ValidateParam(form, "form")

        self._ValidateStringNotEmpty(form, "form")

        # Use parent's reversal index writing system if not specified
        if ws is None:
            reversal_index = parent_entry.ReversalIndex
            if reversal_index:
                ws = reversal_index.WritingSystem
            else:
                # Fall back to default analysis WS
                ws = None

        wsHandle = self.__WSHandleAnalysis(ws)

        # Create the new reversal entry using the factory
        factory = self.project.project.ServiceLocator.GetService(
            IReversalIndexEntryFactory
        )
        new_subentry = factory.Create()

        # Add subentry to parent's subentries collection (must be done before setting properties)
        parent_entry.SubentriesOS.Add(new_subentry)

        # Set the reversal form text
        mkstr = TsStringUtils.MakeString(form, wsHandle)
        new_subentry.ReversalForm.set_String(wsHandle, mkstr)

        return new_subentry

    def GetParentEntry(self, reversal_entry):
        """
        Get the parent reversal entry of a subentry.

        Args:
            reversal_entry: The IReversalIndexEntry object (subentry).

        Returns:
            IReversalIndexEntry or None: The parent entry if this is a subentry,
                None if this is a top-level entry.

        Raises:
            FP_NullParameterError: If reversal_entry is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> subentry = project.Reversal.Find(en_index, "run away")
            >>> if subentry:
            ...     parent = project.Reversal.GetParentEntry(subentry)
            ...     if parent:
            ...         form = project.Reversal.GetForm(parent)
            ...         print(f"Parent: {form}")
            ...     else:
            ...         print("This is a top-level entry")
            Parent: run

        Notes:
            - Returns None for top-level entries (not subentries)
            - Parent-child relationship is maintained in parent's SubentriesOS
            - Subentries inherit reversal index from parent
            - Use GetSubentries() to navigate down the hierarchy

        See Also:
            GetSubentries, CreateSubentry
        """
        self._ValidateParam(reversal_entry, "reversal_entry")

        # Check if this entry has an owner
        owner = reversal_entry.Owner
        if owner and isinstance(owner, IReversalIndexEntry):
            return owner

        return None

    # --- Parts of Speech ---

    def GetPartsOfSpeech(self, reversal_entry):
        """
        Get all parts of speech associated with a reversal entry.

        Parts of speech can be specified for reversal entries to provide
        grammatical information.

        Args:
            reversal_entry: The IReversalIndexEntry object.

        Returns:
            list: List of part of speech objects (IPartOfSpeech).

        Raises:
            FP_NullParameterError: If reversal_entry is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> entry = project.Reversal.Find(en_index, "run")
            >>> if entry:
            ...     pos_list = project.Reversal.GetPartsOfSpeech(entry)
            ...     for pos in pos_list:
            ...         from SIL.LCModel.Core.KernelInterfaces import ITsString
            ...         name = ITsString(pos.Name.BestAnalysisAlternative).Text
            ...         print(f"POS: {name}")
            POS: Verb
            POS: Noun

        Notes:
            - Returns empty list if no parts of speech are specified
            - Multiple POS can be associated with one reversal entry
            - POS are defined in the project's grammatical categories
            - This is useful for disambiguation in reversal indexes

        See Also:
            GetSenses, GetForm
        """
        self._ValidateParam(reversal_entry, "reversal_entry")

        return list(reversal_entry.PartsOfSpeechRC)

    def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
        """
        Duplicate a reversal entry, creating a new copy with a new GUID.

        Args:
            item_or_hvo: The IReversalIndexEntry object or HVO to duplicate.
            insert_after (bool): If True (default), insert after the source entry.
                                If False, insert at end of parent's entry list.
            deep (bool): If True, also duplicate owned objects (subentries).
                        If False (default), only copy simple properties and references.

        Returns:
            IReversalIndexEntry: The newly created duplicate entry with a new GUID.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> en_index = project.Reversal.GetIndex("en")
            >>> entry = project.Reversal.Find(en_index, "run")
            >>> if entry:
            ...     # Shallow duplicate (no subentries)
            ...     dup = project.Reversal.Duplicate(entry)
            ...     form = project.Reversal.GetForm(dup)
            ...     print(f"Duplicate form: {form}")
            Duplicate form: run
            ...
            ...     # Deep duplicate (includes all subentries)
            ...     deep_dup = project.Reversal.Duplicate(entry, deep=True)
            ...     subentries = project.Reversal.GetSubentries(deep_dup)
            ...     print(f"Subentries: {len(subentries)}")
            Subentries: 3

        Notes:
            - Factory.Create() automatically generates a new GUID
            - insert_after=True preserves the original entry's position
            - Simple properties copied: ReversalForm
            - Reference properties copied: SensesRS, PartsOfSpeechRC
            - Owned objects (deep=True): SubentriesOS (subentries)
            - After duplication, you may want to modify the ReversalForm
            - Duplicates maintain links to the same senses as the original

        See Also:
            Create, Delete, CreateSubentry
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(item_or_hvo, "item_or_hvo")

        # Get source entry
        if isinstance(item_or_hvo, int):
            source = self.project.Object(item_or_hvo)
        else:
            source = item_or_hvo

        # Determine parent (could be reversal index or parent entry)
        parent = source.Owner
        parent_entry = self.GetParentEntry(source)

        # Create new reversal entry using factory (auto-generates new GUID)
        factory = self.project.project.ServiceLocator.GetService(
            IReversalIndexEntryFactory
        )
        duplicate = factory.Create()

        # Determine insertion position - ADD TO PARENT FIRST
        if parent_entry:
            # This is a subentry - add to parent entry's subentries
            if insert_after:
                source_index = parent_entry.SubentriesOS.IndexOf(source)
                parent_entry.SubentriesOS.Insert(source_index + 1, duplicate)
            else:
                parent_entry.SubentriesOS.Add(duplicate)
        else:
            # This is a top-level entry - add to reversal index
            reversal_index = source.ReversalIndex
            if reversal_index:
                if insert_after:
                    source_index = reversal_index.EntriesOC.IndexOf(source)
                    reversal_index.EntriesOC.Insert(source_index + 1, duplicate)
                else:
                    reversal_index.EntriesOC.Add(duplicate)

        # Copy simple MultiString properties (AFTER adding to parent)
        duplicate.ReversalForm.CopyAlternatives(source.ReversalForm)

        # Copy Reference Sequence (RS) properties - senses
        for sense in source.SensesRS:
            duplicate.SensesRS.Add(sense)

        # Copy Reference Collection (RC) properties - parts of speech
        for pos in source.PartsOfSpeechRC:
            duplicate.PartsOfSpeechRC.Add(pos)

        # Handle owned objects if deep=True
        if deep:
            # Duplicate subentries recursively
            for subentry in source.SubentriesOS:
                self.Duplicate(subentry, insert_after=False, deep=True)

        return duplicate

    # ========== SYNC INTEGRATION METHODS ==========

    def GetSyncableProperties(self, item):
        """
        Get all syncable properties of a reversal entry for comparison.

        Args:
            item: The IReversalIndexEntry object.

        Returns:
            dict: Dictionary mapping property names to their values.
        """
        props = {}

        # MultiString properties
        # ReversalForm - the reversal form text
        form_dict = {}
        if hasattr(item, 'ReversalForm'):
            for ws_handle in self.project.GetAllWritingSystems():
                text = ITsString(item.ReversalForm.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    form_dict[ws_tag] = text
        props['ReversalForm'] = form_dict

        # Note: SensesRS is a Reference Sequence (complex relationships) - not included
        # Note: SubentriesOS is an Owning Sequence (OS) - not included
        # Note: PartsOfSpeechRC is a Reference Collection (complex) - not included

        return props

    def CompareTo(self, item1, item2, ops1=None, ops2=None):
        """
        Compare two reversal entries and return their differences.

        Args:
            item1: The first IReversalIndexEntry object.
            item2: The second IReversalIndexEntry object.
            ops1: Optional ReversalOperations instance for item1.
            ops2: Optional ReversalOperations instance for item2.

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

    # --- Private Helper Methods ---

    def __WSHandleAnalysis(self, wsHandleOrTag):
        """
        Get writing system handle, defaulting to analysis WS.

        Args:
            wsHandleOrTag: Optional writing system handle or tag.

        Returns:
            int: The writing system handle.
        """
        if wsHandleOrTag is None:
            return self.project.project.DefaultAnalWs

        if isinstance(wsHandleOrTag, str):
            return self.project.WSHandle(wsHandleOrTag)

        return wsHandleOrTag

    def __NormalizeLangTag(self, languageTag):
        """
        Normalize language tag for comparison (case-insensitive, - vs _).

        Args:
            languageTag (str): The language tag to normalize.

        Returns:
            str: Normalized language tag (lowercase, underscores).
        """
        return languageTag.replace("-", "_").lower()
