#
#   LexSenseOperations.py
#
#   Class: LexSenseOperations
#          Lexical sense operations for FieldWorks Language Explorer
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
    ILexSense,
    ILexSenseFactory,
    ILexEntry,
    ILexExampleSentenceFactory,
    ICmSemanticDomain,
    ICmPicture,
    IReversalIndexEntry,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils
from SIL.LCModel.Utils import ReflectionHelper

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class LexSenseOperations(BaseOperations):
    """
    This class provides operations for managing lexical senses in a FieldWorks project.

    Lexical senses represent the different meanings or uses of a lexical entry.
    Each sense can have glosses, definitions, grammatical information, semantic
    domains, example sentences, pictures, and more.

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Access via FLExProject.Senses property (recommended)
        entry = list(project.LexiconAllEntries())[0]

        # Get all senses
        for sense in project.Senses.GetAll(entry):
            gloss = project.Senses.GetGloss(sense)
            print(f"Sense: {gloss}")

        # Create a new sense
        sense = project.Senses.Create(entry, "to run", "en")

        # Set definition
        project.Senses.SetDefinition(sense, "To move swiftly on foot", "en")

        # Add semantic domain
        domains = project.GetAllSemanticDomains(flat=True)
        if domains:
            project.Senses.AddSemanticDomain(sense, domains[0])

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize LexSenseOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)


    def _GetSequence(self, parent):
        """
        Specify which sequence to reorder for senses.
        For LexSense, we reorder entry.SensesOS
        """
        return parent.SensesOS


    # --- Core CRUD Operations ---

    def GetAll(self, entry_or_hvo=None):
        """
        Get senses for an entry or all senses in the project.

        Args:
            entry_or_hvo: Optional ILexEntry object or HVO.
                         If provided, returns senses for that entry only.
                         If None, returns ALL senses in the entire project.

        Yields:
            ILexSense: Each sense.

        Example:
            >>> # Get senses for a specific entry
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> for sense in project.Senses.GetAll(entry):
            ...     gloss = project.Senses.GetGloss(sense)
            ...     defn = project.Senses.GetDefinition(sense)
            ...     print(f"{gloss}: {defn}")
            run: to move swiftly on foot
            run: to flow or extend
            >>>
            >>> # Get ALL senses in entire project
            >>> for sense in project.Senses.GetAll():
            ...     gloss = project.Senses.GetGloss(sense)
            ...     print(f"Sense: {gloss}")

        Notes:
            - When called with no argument, iterates all senses in project
            - When called with entry, returns only that entry's senses
            - Returns senses in order they appear in FLEx
            - Does not include subsenses (use GetSubsenses for those)
            - Returns empty generator if no senses exist

        See Also:
            Create, GetSubsenses, GetOwningEntry
        """
        if entry_or_hvo is None:
            # Iterate ALL senses in entire project
            for entry in self.project.lexDB.Entries:
                for sense in entry.AllSenses:  # Includes subsenses
                    yield sense
        else:
            # Iterate senses for specific entry
            entry = self.__GetEntryObject(entry_or_hvo)
            for sense in entry.SensesOS:
                yield sense


    def Create(self, entry_or_hvo, gloss, wsHandle=None):
        """
        Create a new sense for a lexical entry.

        Args:
            entry_or_hvo: The ILexEntry object or HVO.
            gloss (str): The gloss text for the sense.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ILexSense: The newly created sense object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If entry_or_hvo or gloss is None.
            FP_ParameterError: If gloss is empty.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> sense = project.Senses.Create(entry, "to run")
            >>> print(project.Senses.GetGloss(sense))
            to run

            >>> # Create with specific writing system
            >>> sense_fr = project.Senses.Create(entry, "courir",
            ...                                   project.WSHandle('fr'))

        Notes:
            - The new sense is added at the end of the entry's sense list
            - Gloss is set in the specified writing system (default: analysis)
            - Use SetDefinition, SetPartOfSpeech, etc. to add more information
            - Sense number is automatically assigned

        See Also:
            Delete, SetGloss, SetDefinition, CreateSubsense
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()
        if gloss is None:
            raise FP_NullParameterError()

        if not gloss or not gloss.strip():
            raise FP_ParameterError("Gloss cannot be empty")

        entry = self.__GetEntryObject(entry_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        # Create the new sense using the factory
        factory = self.project.project.ServiceLocator.GetService(ILexSenseFactory)
        new_sense = factory.Create()

        # Add to entry (must be done before setting properties)
        entry.SensesOS.Add(new_sense)

        # Set gloss
        mkstr = TsStringUtils.MakeString(gloss, wsHandle)
        new_sense.Gloss.set_String(wsHandle, mkstr)

        return new_sense


    def Delete(self, sense_or_hvo):
        """
        Delete a sense from its owning entry.

        Args:
            sense_or_hvo: The ILexSense object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if len(senses) > 1:
            ...     # Delete the last sense
            ...     project.Senses.Delete(senses[-1])

        Warning:
            - Deletion is permanent and cannot be undone
            - All subsenses, examples, and other related data are also deleted
            - Consider backing up data before deletion
            - Analyses in texts that reference this sense will be affected

        Notes:
            - Sense numbers are automatically recalculated
            - If deleting a sense with subsenses, subsenses are also removed

        See Also:
            Create, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)

        # Get the owning entry or parent sense
        owner = sense.Owner

        # Check if this is a top-level sense or subsense
        if hasattr(owner, 'SensesOS'):
            # Top-level sense owned by entry
            owner.SensesOS.Remove(sense)
        elif hasattr(owner, 'SensesOS'):
            # Subsense owned by another sense
            owner.SensesOS.Remove(sense)


    def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
        """
        Duplicate a sense, creating a new copy with a new GUID.

        Args:
            item_or_hvo: The ILexSense object or HVO to duplicate.
            insert_after (bool): If True (default), insert after the source sense.
                                If False, insert at end of parent's sense list.
            deep (bool): If True, also duplicate owned objects (subsenses, examples, pictures).
                        If False (default), only copy simple properties and references.

        Returns:
            ILexSense: The newly created duplicate sense with a new GUID.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     # Shallow duplicate (no examples/subsenses)
            ...     dup = project.Senses.Duplicate(senses[0])
            ...     print(f"Original: {project.Senses.GetGuid(senses[0])}")
            ...     print(f"Duplicate: {project.Senses.GetGuid(dup)}")
            Original: 12345678-1234-1234-1234-123456789abc
            Duplicate: 87654321-4321-4321-4321-cba987654321
            ...
            ...     # Deep duplicate (includes all owned objects)
            ...     deep_dup = project.Senses.Duplicate(senses[0], deep=True)
            ...     print(f"Examples: {project.Senses.GetExampleCount(deep_dup)}")

        Notes:
            - Factory.Create() automatically generates a new GUID
            - insert_after=True preserves the original sense's position/priority
            - Simple properties copied: Gloss, Definition, etc.
            - Reference properties copied: MSA, Status, SenseType, SemanticDomainsRC
            - Owned objects (deep=True): ExamplesOS, SensesOS (subsenses), PicturesOS
            - ImportResidue and LiftResidue are not copied (import-specific data)
            - ReferringReversalIndexEntries are not copied (back-references)

        See Also:
            Create, Delete, GetGuid
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not item_or_hvo:
            raise FP_NullParameterError()

        # Get source sense and parent
        source = self.__GetSenseObject(item_or_hvo)
        parent = source.Owner

        # Create new sense using factory (auto-generates new GUID)
        factory = self.project.project.ServiceLocator.GetService(ILexSenseFactory)
        duplicate = factory.Create()

        # Determine insertion position
        if insert_after:
            # Insert after source sense
            if hasattr(parent, 'SensesOS'):
                source_index = parent.SensesOS.IndexOf(source)
                parent.SensesOS.Insert(source_index + 1, duplicate)
        else:
            # Insert at end
            if hasattr(parent, 'SensesOS'):
                parent.SensesOS.Add(duplicate)

        # Copy simple MultiString properties (AFTER adding to parent)
        duplicate.Gloss.CopyAlternatives(source.Gloss)
        duplicate.Definition.CopyAlternatives(source.Definition)
        duplicate.Bibliography.CopyAlternatives(source.Bibliography)
        duplicate.DiscourseNote.CopyAlternatives(source.DiscourseNote)
        duplicate.EncyclopedicInfo.CopyAlternatives(source.EncyclopedicInfo)
        duplicate.GeneralNote.CopyAlternatives(source.GeneralNote)
        duplicate.GrammarNote.CopyAlternatives(source.GrammarNote)
        duplicate.PhonologyNote.CopyAlternatives(source.PhonologyNote)
        duplicate.Restrictions.CopyAlternatives(source.Restrictions)
        duplicate.SemanticsNote.CopyAlternatives(source.SemanticsNote)
        duplicate.SocioLinguisticsNote.CopyAlternatives(source.SocioLinguisticsNote)
        duplicate.Source.CopyAlternatives(source.Source)

        # Copy Reference Atomic (RA) properties
        duplicate.MorphoSyntaxAnalysisRA = source.MorphoSyntaxAnalysisRA
        duplicate.StatusRA = source.StatusRA
        duplicate.SenseTypeRA = source.SenseTypeRA

        # Copy Reference Collection (RC) properties
        for domain in source.SemanticDomainsRC:
            duplicate.SemanticDomainsRC.Add(domain)

        for anthro in source.AnthroCodesRC:
            duplicate.AnthroCodesRC.Add(anthro)

        for domain_q in source.DomainTypesRC:
            duplicate.DomainTypesRC.Add(domain_q)

        for usage in source.UsageTypesRC:
            duplicate.UsageTypesRC.Add(usage)

        # Handle owned objects if deep=True
        if deep:
            # Duplicate examples
            for example in source.ExamplesOS:
                self.project.Examples.Duplicate(example, insert_after=False)

            # Duplicate subsenses
            for subsense in source.SensesOS:
                self.Duplicate(subsense, insert_after=False, deep=True)

            # Duplicate pictures
            for picture in source.PicturesOS:
                # Pictures require special handling - factory type varies
                from SIL.LCModel import ICmPictureFactory
                pic_factory = self.project.project.ServiceLocator.GetService(ICmPictureFactory)
                new_pic = pic_factory.Create()
                duplicate.PicturesOS.Add(new_pic)

                # Copy picture properties
                new_pic.Caption.CopyAlternatives(picture.Caption)
                new_pic.PictureFileRA = picture.PictureFileRA
                new_pic.LayoutPos = picture.LayoutPos
                new_pic.ScaleFactor = picture.ScaleFactor

        return duplicate


    # ========== SYNC INTEGRATION METHODS ==========

    def GetSyncableProperties(self, item):
        """
        Get all syncable properties of a lexical sense for comparison.

        Args:
            item: The ILexSense object.

        Returns:
            dict: Dictionary mapping property names to their values.
        """
        props = {}

        # MultiString properties
        # Gloss - short definition
        gloss_dict = {}
        if hasattr(item, 'Gloss'):
            for ws_handle in self.project.GetAllWritingSystems():
                from SIL.LCModel.Core.KernelInterfaces import ITsString
                text = ITsString(item.Gloss.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    gloss_dict[ws_tag] = text
        props['Gloss'] = gloss_dict

        # Definition - longer definition
        definition_dict = {}
        if hasattr(item, 'Definition'):
            for ws_handle in self.project.GetAllWritingSystems():
                from SIL.LCModel.Core.KernelInterfaces import ITsString
                text = ITsString(item.Definition.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    definition_dict[ws_tag] = text
        props['Definition'] = definition_dict

        # DiscourseNote - discourse function notes
        discourse_dict = {}
        if hasattr(item, 'DiscourseNote'):
            for ws_handle in self.project.GetAllWritingSystems():
                from SIL.LCModel.Core.KernelInterfaces import ITsString
                text = ITsString(item.DiscourseNote.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    discourse_dict[ws_tag] = text
        props['DiscourseNote'] = discourse_dict

        # EncyclopedicInfo - encyclopedic information
        encyclo_dict = {}
        if hasattr(item, 'EncyclopedicInfo'):
            for ws_handle in self.project.GetAllWritingSystems():
                from SIL.LCModel.Core.KernelInterfaces import ITsString
                text = ITsString(item.EncyclopedicInfo.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    encyclo_dict[ws_tag] = text
        props['EncyclopedicInfo'] = encyclo_dict

        # GeneralNote - general notes
        general_dict = {}
        if hasattr(item, 'GeneralNote'):
            for ws_handle in self.project.GetAllWritingSystems():
                from SIL.LCModel.Core.KernelInterfaces import ITsString
                text = ITsString(item.GeneralNote.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    general_dict[ws_tag] = text
        props['GeneralNote'] = general_dict

        # GrammarNote - grammatical notes
        grammar_dict = {}
        if hasattr(item, 'GrammarNote'):
            for ws_handle in self.project.GetAllWritingSystems():
                from SIL.LCModel.Core.KernelInterfaces import ITsString
                text = ITsString(item.GrammarNote.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    grammar_dict[ws_tag] = text
        props['GrammarNote'] = grammar_dict

        # PhonologyNote - phonology notes
        phonology_dict = {}
        if hasattr(item, 'PhonologyNote'):
            for ws_handle in self.project.GetAllWritingSystems():
                from SIL.LCModel.Core.KernelInterfaces import ITsString
                text = ITsString(item.PhonologyNote.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    phonology_dict[ws_tag] = text
        props['PhonologyNote'] = phonology_dict

        # SemanticsNote - semantics notes
        semantics_dict = {}
        if hasattr(item, 'SemanticsNote'):
            for ws_handle in self.project.GetAllWritingSystems():
                from SIL.LCModel.Core.KernelInterfaces import ITsString
                text = ITsString(item.SemanticsNote.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    semantics_dict[ws_tag] = text
        props['SemanticsNote'] = semantics_dict

        # SocioLinguisticsNote - sociolinguistics notes
        socio_dict = {}
        if hasattr(item, 'SocioLinguisticsNote'):
            for ws_handle in self.project.GetAllWritingSystems():
                from SIL.LCModel.Core.KernelInterfaces import ITsString
                text = ITsString(item.SocioLinguisticsNote.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    socio_dict[ws_tag] = text
        props['SocioLinguisticsNote'] = socio_dict

        # Source - bibliographic source
        source_dict = {}
        if hasattr(item, 'Source'):
            for ws_handle in self.project.GetAllWritingSystems():
                from SIL.LCModel.Core.KernelInterfaces import ITsString
                text = ITsString(item.Source.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    source_dict[ws_tag] = text
        props['Source'] = source_dict

        # Restrictions - usage restrictions
        restrictions_dict = {}
        if hasattr(item, 'Restrictions'):
            for ws_handle in self.project.GetAllWritingSystems():
                from SIL.LCModel.Core.KernelInterfaces import ITsString
                text = ITsString(item.Restrictions.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    restrictions_dict[ws_tag] = text
        props['Restrictions'] = restrictions_dict

        # Bibliography - bibliographic reference
        bibliography_dict = {}
        if hasattr(item, 'Bibliography'):
            for ws_handle in self.project.GetAllWritingSystems():
                from SIL.LCModel.Core.KernelInterfaces import ITsString
                text = ITsString(item.Bibliography.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    bibliography_dict[ws_tag] = text
        props['Bibliography'] = bibliography_dict

        # Reference Atomic (RA) properties
        # MorphoSyntaxAnalysisRA - grammatical info
        if hasattr(item, 'MorphoSyntaxAnalysisRA') and item.MorphoSyntaxAnalysisRA:
            props['MorphoSyntaxAnalysisRA'] = str(item.MorphoSyntaxAnalysisRA.Guid)
        else:
            props['MorphoSyntaxAnalysisRA'] = None

        # StatusRA - status (e.g., confirmed, tentative)
        if hasattr(item, 'StatusRA') and item.StatusRA:
            props['StatusRA'] = str(item.StatusRA.Guid)
        else:
            props['StatusRA'] = None

        # Atomic properties
        # ImportResidue - import residue from LIFT files
        if hasattr(item, 'ImportResidue'):
            props['ImportResidue'] = item.ImportResidue

        return props


    def CompareTo(self, item1, item2, ops1=None, ops2=None):
        """
        Compare two lexical senses and return their differences.

        Args:
            item1: The first ILexSense object.
            item2: The second ILexSense object.
            ops1: Optional LexSenseOperations instance for item1.
            ops2: Optional LexSenseOperations instance for item2.

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


    def Reorder(self, entry_or_hvo, sense_list):
        """
        Reorder senses for a lexical entry.

        Args:
            entry_or_hvo: The ILexEntry object or HVO.
            sense_list: List of ILexSense objects or HVOs in desired order.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If entry_or_hvo or sense_list is None.
            FP_ParameterError: If sense_list is empty or contains invalid senses.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if len(senses) > 1:
            ...     # Reverse the order
            ...     project.Senses.Reorder(entry, reversed(senses))
            ...     # Verify new order
            ...     for sense in project.Senses.GetAll(entry):
            ...         print(project.Senses.GetGloss(sense))

        Notes:
            - All senses in sense_list must belong to the entry
            - Sense numbers are automatically updated
            - Any senses not in sense_list remain at the end in original order

        See Also:
            GetAll, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()
        if sense_list is None:
            raise FP_NullParameterError()

        if not sense_list:
            raise FP_ParameterError("Sense list cannot be empty")

        entry = self.__GetEntryObject(entry_or_hvo)

        # Resolve HVOs to sense objects
        resolved_senses = []
        for sense_or_hvo in sense_list:
            sense = self.__GetSenseObject(sense_or_hvo)
            resolved_senses.append(sense)

        # Clear current senses
        entry.SensesOS.Clear()

        # Add in new order
        for sense in resolved_senses:
            entry.SensesOS.Add(sense)


    # --- Gloss & Definition Operations ---

    def GetGloss(self, sense_or_hvo, wsHandle=None):
        """
        Get the gloss for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The gloss text, or empty string if not set.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     gloss = project.Senses.GetGloss(senses[0])
            ...     print(gloss)
            to run

            >>> # Get gloss in specific writing system
            >>> gloss_fr = project.Senses.GetGloss(senses[0],
            ...                                     project.WSHandle('fr'))
            >>> print(gloss_fr)
            courir

        Notes:
            - Returns empty string if gloss not set in specified writing system
            - Glosses are typically shorter than definitions
            - Default writing system is the default analysis WS

        See Also:
            SetGloss, GetDefinition
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        gloss = ITsString(sense.Gloss.get_String(wsHandle)).Text
        return gloss or ""


    def SetGloss(self, sense_or_hvo, text, wsHandle=None):
        """
        Set the gloss for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            text (str): The new gloss text.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo or text is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     project.Senses.SetGloss(senses[0], "to run quickly")
            ...     print(project.Senses.GetGloss(senses[0]))
            to run quickly

            >>> # Set gloss in multiple writing systems
            >>> project.Senses.SetGloss(senses[0], "courir",
            ...                         project.WSHandle('fr'))
            >>> project.Senses.SetGloss(senses[0], "correr",
            ...                         project.WSHandle('es'))

        Notes:
            - Empty string is allowed (clears the gloss)
            - Gloss is typically a short translation or identifier
            - Can be set independently in multiple writing systems

        See Also:
            GetGloss, SetDefinition
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not sense_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        # set_String handles building a tss for us
        sense.Gloss.set_String(wsHandle, text)


    def GetDefinition(self, sense_or_hvo, wsHandle=None):
        """
        Get the definition for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The definition text, or empty string if not set.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     defn = project.Senses.GetDefinition(senses[0])
            ...     print(defn)
            To move swiftly on foot by alternately setting each foot forward

        Notes:
            - Returns empty string if definition not set in specified writing system
            - Definitions are typically longer and more detailed than glosses
            - Default writing system is the default analysis WS

        See Also:
            SetDefinition, GetGloss
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        # Definition is a MultiString
        defn = ITsString(sense.Definition.get_String(wsHandle)).Text
        return defn or ""


    def SetDefinition(self, sense_or_hvo, text, wsHandle=None):
        """
        Set the definition for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            text (str): The new definition text.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo or text is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     defn = "To move swiftly on foot by alternately setting each foot forward"
            ...     project.Senses.SetDefinition(senses[0], defn)
            ...     print(project.Senses.GetDefinition(senses[0]))
            To move swiftly on foot by alternately setting each foot forward

        Notes:
            - Empty string is allowed (clears the definition)
            - Definition is typically more detailed than gloss
            - Can be set independently in multiple writing systems
            - May include formatting in ITsString format

        See Also:
            GetDefinition, SetGloss
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not sense_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        # Definition is a MultiString - set_String handles building tss
        sense.Definition.set_String(wsHandle, text)


    # --- Grammatical Information Operations ---

    def GetPartOfSpeech(self, sense_or_hvo):
        """
        Get the part of speech abbreviation for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            str: The POS abbreviation, or empty string if not set.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     pos = project.Senses.GetPartOfSpeech(senses[0])
            ...     print(f"Part of Speech: {pos}")
            Part of Speech: v

        Notes:
            - Returns the interlinear abbreviation from the MSA
            - Returns empty string if no MSA is set
            - MSA (Morphosyntactic Analysis) includes POS and other gram info

        See Also:
            SetPartOfSpeech, GetGrammaticalInfo
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)

        if sense.MorphoSyntaxAnalysisRA is not None:
            return sense.MorphoSyntaxAnalysisRA.InterlinearAbbr
        else:
            return ""


    def SetPartOfSpeech(self, sense_or_hvo, pos):
        """
        Set the part of speech for a sense.

        Creates or updates the MSA (Morphosyntactic Analysis) for the sense
        with the specified part of speech category.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            pos: The IPartOfSpeech object or HVO to set.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo or pos is None.
            FP_ParameterError: If pos is invalid.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     # Get verb POS
            ...     verb_pos = project.POS.Find("Verb")
            ...     if verb_pos:
            ...         project.Senses.SetPartOfSpeech(senses[0], verb_pos)

        Notes:
            - Creates IMoStemMsa (stem MSA) if sense has no MSA
            - Updates existing MSA Category if already exists
            - POS must be from the project's parts of speech list
            - Setting POS affects grammatical analysis and parsing
            - MSA is stored in the LexDb.MorphoSyntaxAnalysesOC collection

        See Also:
            GetPartOfSpeech, SetGrammaticalInfo
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not sense_or_hvo:
            raise FP_NullParameterError()
        if pos is None:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)

        # Get POS object (handle both HVO and object)
        if isinstance(pos, int):
            pos_obj = self.project.project.ServiceLocator.GetObject(pos)
        else:
            pos_obj = pos

        # Check if sense already has an MSA
        if sense.MorphoSyntaxAnalysisRA is not None:
            # Update existing MSA's Category
            msa = sense.MorphoSyntaxAnalysisRA
            if hasattr(msa, 'PartOfSpeechRA'):
                msa.PartOfSpeechRA = pos_obj
            else:
                # If existing MSA is not a stem MSA, create new one
                from SIL.LCModel import IMoStemMsaFactory
                factory = self.project.project.ServiceLocator.GetService(IMoStemMsaFactory)
                new_msa = factory.Create()
                new_msa.PartOfSpeechRA = pos_obj
                sense.MorphoSyntaxAnalysisRA = new_msa
        else:
            # Create new stem MSA
            from SIL.LCModel import IMoStemMsaFactory
            factory = self.project.project.ServiceLocator.GetService(IMoStemMsaFactory)
            msa = factory.Create()
            msa.PartOfSpeechRA = pos_obj
            sense.MorphoSyntaxAnalysisRA = msa


    def GetGrammaticalInfo(self, sense_or_hvo):
        """
        Get the full grammatical information (MSA) for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            IMoMorphSynAnalysis or None: The MSA object, or None if not set.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     msa = project.Senses.GetGrammaticalInfo(senses[0])
            ...     if msa:
            ...         print(f"MSA: {msa.InterlinearAbbr}")

        Notes:
            - MSA (Morphosyntactic Analysis) contains POS and other features
            - Returns None if no grammatical information is set
            - MSA type varies (stem, affix, etc.)

        See Also:
            SetGrammaticalInfo, GetPartOfSpeech
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        return sense.MorphoSyntaxAnalysisRA


    def SetGrammaticalInfo(self, sense_or_hvo, msa):
        """
        Set the full grammatical information (MSA) for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            msa: The IMoMorphSynAnalysis object to set.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses and len(senses) > 1:
            ...     # Copy MSA from another sense
            ...     msa = project.Senses.GetGrammaticalInfo(senses[0])
            ...     if msa:
            ...         project.Senses.SetGrammaticalInfo(senses[1], msa)

        Notes:
            - MSA must be a valid morphosyntactic analysis object
            - Setting to None clears grammatical information
            - MSA is shared across entries/senses in the database

        See Also:
            GetGrammaticalInfo, SetPartOfSpeech
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        sense.MorphoSyntaxAnalysisRA = msa


    # --- Semantic Domain Operations ---

    def GetSemanticDomains(self, sense_or_hvo):
        """
        Get all semantic domains for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            list: List of ICmSemanticDomain objects.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     domains = project.Senses.GetSemanticDomains(senses[0])
            ...     for domain in domains:
            ...         ws = project.project.DefaultAnalWs
            ...         name = ITsString(domain.Name.get_String(ws)).Text
            ...         print(f"Domain: {name}")
            Domain: 7.2.1 Walk

        Notes:
            - Returns empty list if no semantic domains are set
            - Semantic domains categorize word meanings
            - Multiple domains can be assigned to one sense

        See Also:
            AddSemanticDomain, RemoveSemanticDomain
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        return list(sense.SemanticDomainsRC)


    def AddSemanticDomain(self, sense_or_hvo, domain_or_hvo):
        """
        Add a semantic domain to a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            domain_or_hvo: The ICmSemanticDomain object or HVO to add.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo or domain_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     # Get semantic domains
            ...     all_domains = project.GetAllSemanticDomains(flat=True)
            ...     if all_domains:
            ...         # Add first domain
            ...         project.Senses.AddSemanticDomain(senses[0], all_domains[0])

        Notes:
            - If domain already exists in the list, it's still added
              (duplicates are allowed but not recommended)
            - Semantic domains help organize the lexicon by meaning
            - Use project.GetAllSemanticDomains() to get available domains

        See Also:
            GetSemanticDomains, RemoveSemanticDomain
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not sense_or_hvo:
            raise FP_NullParameterError()
        if not domain_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        domain = self.__GetSemanticDomainObject(domain_or_hvo)

        sense.SemanticDomainsRC.Add(domain)


    def RemoveSemanticDomain(self, sense_or_hvo, domain_or_hvo):
        """
        Remove a semantic domain from a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            domain_or_hvo: The ICmSemanticDomain object or HVO to remove.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo or domain_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     domains = project.Senses.GetSemanticDomains(senses[0])
            ...     if domains:
            ...         # Remove first domain
            ...         project.Senses.RemoveSemanticDomain(senses[0], domains[0])

        Notes:
            - If domain not in list, this is a no-op (no error)
            - Only removes one instance if duplicates exist

        See Also:
            GetSemanticDomains, AddSemanticDomain
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not sense_or_hvo:
            raise FP_NullParameterError()
        if not domain_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        domain = self.__GetSemanticDomainObject(domain_or_hvo)

        # Only remove if it's actually in the collection
        if domain in sense.SemanticDomainsRC:
            sense.SemanticDomainsRC.Remove(domain)


    # --- Example Sentence Operations ---

    def GetExamples(self, sense_or_hvo):
        """
        Get all example sentences for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            list: List of ILexExampleSentence objects.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     examples = project.Senses.GetExamples(senses[0])
            ...     for ex in examples:
            ...         ws = project.project.DefaultVernWs
            ...         text = ITsString(ex.Example.get_String(ws)).Text
            ...         print(f"Example: {text}")
            Example: She runs every morning.

        Notes:
            - Returns empty list if no examples are set
            - Examples demonstrate usage of the sense
            - Each example can have translations and references

        See Also:
            GetExampleCount, AddExample
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        return list(sense.ExamplesOS)


    def GetExampleCount(self, sense_or_hvo):
        """
        Get the count of example sentences for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            int: Number of examples.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     count = project.Senses.GetExampleCount(senses[0])
            ...     print(f"This sense has {count} examples")
            This sense has 3 examples

        Notes:
            - More efficient than len(GetExamples()) for counting
            - Returns 0 if no examples

        See Also:
            GetExamples, AddExample
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        return sense.ExamplesOS.Count


    def AddExample(self, sense_or_hvo, text, wsHandle=None):
        """
        Add a new example sentence to a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            text (str): The example sentence text.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            ILexExampleSentence: The newly created example object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo or text is None.
            FP_ParameterError: If text is empty.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     ex = project.Senses.AddExample(senses[0], "She runs every morning.")
            ...     # Add translation (would need additional code)
            ...     print(f"Added example: {ex.Hvo}")

        Notes:
            - Example is added at the end of the examples list
            - Text is set in the specified writing system (default: vernacular)
            - Use the returned object to add translations and references
            - This is a basic implementation - translations require additional work

        See Also:
            GetExamples, GetExampleCount
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not sense_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        if not text or not text.strip():
            raise FP_ParameterError("Example text cannot be empty")

        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleVernacular(wsHandle)

        # Create the new example using the factory
        factory = self.project.project.ServiceLocator.GetService(
            ILexExampleSentenceFactory
        )
        new_example = factory.Create()

        # Add to sense (must be done before setting properties)
        sense.ExamplesOS.Add(new_example)

        # Set example text
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        new_example.Example.set_String(wsHandle, mkstr)

        return new_example


    # --- Subsense Operations ---

    def GetSubsenses(self, sense_or_hvo):
        """
        Get all subsenses (child senses) of a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            list: List of ILexSense objects that are subsenses.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     subsenses = project.Senses.GetSubsenses(senses[0])
            ...     for subsense in subsenses:
            ...         gloss = project.Senses.GetGloss(subsense)
            ...         print(f"  Subsense: {gloss}")
              Subsense: to run (of water)
              Subsense: to run (a program)

        Notes:
            - Returns empty list if no subsenses exist
            - Subsenses represent more specific meanings
            - Subsenses can have their own subsenses (nested hierarchy)

        See Also:
            CreateSubsense, GetParentSense
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        return list(sense.SensesOS)


    def CreateSubsense(self, parent_sense_or_hvo, gloss, wsHandle=None):
        """
        Create a new subsense under a parent sense.

        Args:
            parent_sense_or_hvo: The parent ILexSense object or HVO.
            gloss (str): The gloss text for the subsense.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ILexSense: The newly created subsense object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If parent_sense_or_hvo or gloss is None.
            FP_ParameterError: If gloss is empty.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     subsense = project.Senses.CreateSubsense(senses[0], "to run (of water)")
            ...     print(project.Senses.GetGloss(subsense))
            to run (of water)

        Notes:
            - The subsense is added at the end of parent's subsense list
            - Subsense inherits some properties from parent
            - Subsense numbers are formatted with parent number (e.g., 1.1, 1.2)

        See Also:
            GetSubsenses, GetParentSense
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not parent_sense_or_hvo:
            raise FP_NullParameterError()
        if gloss is None:
            raise FP_NullParameterError()

        if not gloss or not gloss.strip():
            raise FP_ParameterError("Gloss cannot be empty")

        parent_sense = self.__GetSenseObject(parent_sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        # Create the new subsense using the factory
        factory = self.project.project.ServiceLocator.GetService(ILexSenseFactory)
        new_subsense = factory.Create()

        # Add to parent sense (must be done before setting properties)
        parent_sense.SensesOS.Add(new_subsense)

        # Set gloss
        mkstr = TsStringUtils.MakeString(gloss, wsHandle)
        new_subsense.Gloss.set_String(wsHandle, mkstr)

        return new_subsense


    def GetParentSense(self, sense_or_hvo):
        """
        Get the parent sense if this is a subsense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            ILexSense or None: The parent sense, or None if top-level sense.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     subsenses = project.Senses.GetSubsenses(senses[0])
            ...     if subsenses:
            ...         parent = project.Senses.GetParentSense(subsenses[0])
            ...         if parent:
            ...             parent_gloss = project.Senses.GetGloss(parent)
            ...             print(f"Parent: {parent_gloss}")
            Parent: to run

        Notes:
            - Returns None if this is a top-level sense owned by entry
            - Returns the parent ILexSense if this is a subsense
            - Use to navigate sense hierarchy

        See Also:
            GetSubsenses, CreateSubsense, GetOwningEntry
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        owner = sense.Owner

        # Check if owner is a sense (subsense) or entry (top-level)
        if hasattr(owner, 'ClassName') and owner.ClassName == 'LexSense':
            return owner
        else:
            return None


    # --- Status & Type Operations ---

    def GetStatus(self, sense_or_hvo):
        """
        Get the status of a sense (e.g., approved, tentative).

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            ICmPossibility or None: The status object, or None if not set.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     status = project.Senses.GetStatus(senses[0])
            ...     if status:
            ...         ws = project.project.DefaultAnalWs
            ...         name = ITsString(status.Name.get_String(ws)).Text
            ...         print(f"Status: {name}")
            Status: Approved

        Notes:
            - Returns None if no status is set
            - Status values are from the project's status possibility list
            - Common statuses: Approved, Tentative, Pending

        See Also:
            SetStatus
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        return sense.StatusRA


    def SetStatus(self, sense_or_hvo, status):
        """
        Set the status of a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            status: The ICmPossibility status object to set.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     # Get status possibilities
            ...     flid = project.GetFieldID("LexSense", "Status")
            ...     statuses = project.ListFieldPossibilities(senses[0], flid)
            ...     if statuses:
            ...         # Set to first status (e.g., Approved)
            ...         project.Senses.SetStatus(senses[0], statuses[0])

        Notes:
            - Status must be from the project's status possibility list
            - Setting to None clears the status
            - Status affects editorial workflow and publishing

        See Also:
            GetStatus
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        sense.StatusRA = status


    def GetSenseType(self, sense_or_hvo):
        """
        Get the sense type (e.g., literal, figurative, idiom).

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            ICmPossibility or None: The sense type object, or None if not set.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     sense_type = project.Senses.GetSenseType(senses[0])
            ...     if sense_type:
            ...         ws = project.project.DefaultAnalWs
            ...         name = ITsString(sense_type.Name.get_String(ws)).Text
            ...         print(f"Type: {name}")
            Type: Figurative

        Notes:
            - Returns None if no sense type is set
            - Sense types categorize the nature of the meaning
            - Common types: Literal, Figurative, Idiom, Metaphor

        See Also:
            SetSenseType
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        return sense.SenseTypeRA


    def SetSenseType(self, sense_or_hvo, sense_type):
        """
        Set the sense type for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            sense_type: The ICmPossibility sense type object to set.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     # Get sense type possibilities
            ...     flid = project.GetFieldID("LexSense", "SenseType")
            ...     types = project.ListFieldPossibilities(senses[0], flid)
            ...     if types:
            ...         # Set to a specific type (e.g., Figurative)
            ...         project.Senses.SetSenseType(senses[0], types[1])

        Notes:
            - Sense type must be from the project's sense type possibility list
            - Setting to None clears the sense type
            - Helps categorize different kinds of meanings

        See Also:
            GetSenseType
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        sense.SenseTypeRA = sense_type


    # --- Reversal Entry Operations ---

    def GetReversalEntries(self, sense_or_hvo, reversal_index_ws=None):
        """
        Get reversal entries for a sense in a specific reversal index.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            reversal_index_ws: Optional writing system for reversal index.
                If None, returns entries from all reversal indexes.

        Returns:
            list: List of IReversalIndexEntry objects.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     # Get English reversal entries
            ...     rev_entries = project.Senses.GetReversalEntries(senses[0], "en")
            ...     for rev in rev_entries:
            ...         ws = project.WSHandle("en")
            ...         form = ITsString(rev.ReversalForm.get_String(ws)).Text
            ...         print(f"Reversal: {form}")
            Reversal: run

        Notes:
            - Returns empty list if no reversal entries exist
            - If reversal_index_ws is None, returns from all indexes
            - Reversal entries allow finding vernacular words from analysis language

        See Also:
            GetReversalCount
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)

        # Get all referring reversal entries
        reversal_entries = list(sense.ReferringReversalIndexEntries)

        # Filter by writing system if specified
        if reversal_index_ws:
            ws_normalized = reversal_index_ws.replace("-", "_").lower()
            filtered = []
            for rev_entry in reversal_entries:
                rev_index = rev_entry.ReversalIndex
                if rev_index:
                    rev_ws = rev_index.WritingSystem.replace("-", "_").lower()
                    if rev_ws == ws_normalized:
                        filtered.append(rev_entry)
            return filtered

        return reversal_entries


    def GetReversalCount(self, sense_or_hvo):
        """
        Get the count of reversal entries for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            int: Number of reversal entries.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     count = project.Senses.GetReversalCount(senses[0])
            ...     print(f"This sense has {count} reversal entries")
            This sense has 2 reversal entries

        Notes:
            - Counts entries across all reversal indexes
            - More efficient than len(GetReversalEntries())

        See Also:
            GetReversalEntries
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        return len(list(sense.ReferringReversalIndexEntries))


    # --- Picture Operations ---

    def GetPictures(self, sense_or_hvo):
        """
        Get all pictures associated with a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            list: List of ICmPicture objects.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     pictures = project.Senses.GetPictures(senses[0])
            ...     for pic in pictures:
            ...         caption = ITsString(pic.Caption.BestAnalysisAlternative).Text
            ...         print(f"Picture: {caption}")
            Picture: A person running

        Notes:
            - Returns empty list if no pictures are associated
            - Pictures can have captions in multiple writing systems
            - Picture files are stored in the project's Pictures folder

        See Also:
            GetPictureCount
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        return list(sense.PicturesOS)


    def GetPictureCount(self, sense_or_hvo):
        """
        Get the count of pictures for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            int: Number of pictures.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     count = project.Senses.GetPictureCount(senses[0])
            ...     print(f"This sense has {count} pictures")
            This sense has 1 pictures

        Notes:
            - More efficient than len(GetPictures()) for counting
            - Returns 0 if no pictures

        See Also:
            GetPictures
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        return sense.PicturesOS.Count


    # --- Additional Utility Operations ---

    def GetGuid(self, sense_or_hvo):
        """
        Get the GUID (Global Unique Identifier) for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            System.Guid: The GUID of the sense.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     guid = project.Senses.GetGuid(senses[0])
            ...     print(f"Sense GUID: {guid}")
            Sense GUID: 12345678-1234-1234-1234-123456789abc

        Notes:
            - GUID is unique across all projects
            - GUID remains constant even if object moves
            - Useful for cross-referencing between projects
            - HVO is project-specific, GUID is universal

        See Also:
            GetOwningEntry
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)
        return sense.Guid


    def GetOwningEntry(self, sense_or_hvo):
        """
        Get the lexical entry that owns this sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            ILexEntry: The owning entry.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     owner = project.Senses.GetOwningEntry(senses[0])
            ...     headword = project.LexiconGetHeadword(owner)
            ...     print(f"Entry: {headword}")
            Entry: run

        Notes:
            - Returns the ultimate owning entry even for subsenses
            - Climbs the ownership chain to the top-level entry
            - Different from GetParentSense which returns immediate parent

        See Also:
            GetParentSense, GetAll
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)

        # Climb the ownership chain to find the entry
        owner = sense.Owner
        while owner is not None:
            if hasattr(owner, 'ClassName'):
                if owner.ClassName == 'LexEntry':
                    return owner
                elif owner.ClassName == 'LexSense':
                    # Keep climbing
                    owner = owner.Owner
                else:
                    break
            else:
                break

        # Shouldn't reach here, but return owner if we do
        return owner


    def GetSenseNumber(self, sense_or_hvo):
        """
        Get the sense number string for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            str: The sense number (e.g., "1", "2.1", "2.1.1").

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     num = project.Senses.GetSenseNumber(senses[0])
            ...     gloss = project.Senses.GetGloss(senses[0])
            ...     print(f"{num}. {gloss}")
            1. to run

        Notes:
            - Sense number is automatically calculated by FLEx
            - Subsenses have hierarchical numbering (e.g., 2.1, 2.1.1)
            - Not directly accessible from ILexSense - uses reflection
            - Number changes if senses are reordered

        See Also:
            Reorder, GetSubsenses
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)

        # SenseNumber is not part of the interface ILexSense, but it
        # is a public member of LexSense, which we can access by reflection.
        sense_number = ReflectionHelper.GetProperty(sense, "SenseNumber")
        return sense_number


    def GetAnalysesCount(self, sense_or_hvo):
        """
        Get the count of analyses in texts that reference this sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Returns:
            int: Number of analyses referencing this sense.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     count = project.Senses.GetAnalysesCount(senses[0])
            ...     print(f"This sense is used {count} times in texts")
            This sense is used 15 times in texts

        Notes:
            - Counts occurrences in parsed/analyzed texts
            - Useful for frequency analysis
            - Not directly accessible from ILexSense - uses reflection
            - May differ from actual word count (same analysis can appear multiple times)

        See Also:
            GetGloss, GetOwningEntry
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)

        # SenseAnalysesCount is not part of the interface ILexSense, but it
        # is a public member of LexSense, which we can access by reflection.
        count = ReflectionHelper.GetProperty(sense, "SenseAnalysesCount")
        return count


    # --- Private Helper Methods ---

    def __GetEntryObject(self, entry_or_hvo):
        """
        Resolve HVO or object to ILexEntry.

        Args:
            entry_or_hvo: Either an ILexEntry object or an HVO (int).

        Returns:
            ILexEntry: The resolved entry object.
        """
        if isinstance(entry_or_hvo, int):
            return self.project.Object(entry_or_hvo)
        return entry_or_hvo


    def __GetSenseObject(self, sense_or_hvo):
        """
        Resolve HVO or object to ILexSense.

        Args:
            sense_or_hvo: Either an ILexSense object or an HVO (int).

        Returns:
            ILexSense: The resolved sense object.
        """
        if isinstance(sense_or_hvo, int):
            return self.project.Object(sense_or_hvo)
        return sense_or_hvo


    def __GetSemanticDomainObject(self, domain_or_hvo):
        """
        Resolve HVO or object to ICmSemanticDomain.

        Args:
            domain_or_hvo: Either an ICmSemanticDomain object or an HVO (int).

        Returns:
            ICmSemanticDomain: The resolved semantic domain object.
        """
        if isinstance(domain_or_hvo, int):
            return self.project.Object(domain_or_hvo)
        return domain_or_hvo


    def __WSHandleAnalysis(self, wsHandle):
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


    def __WSHandleVernacular(self, wsHandle):
        """
        Get writing system handle, defaulting to vernacular WS.

        Args:
            wsHandle: Optional writing system handle.

        Returns:
            int: The writing system handle.
        """
        if wsHandle is None:
            return self.project.project.DefaultVernWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultVernWs)
