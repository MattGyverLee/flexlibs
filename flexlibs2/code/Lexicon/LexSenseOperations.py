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
import os
import System
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
    ICmPictureFactory,
    ICmTranslationFactory,
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

# Import LCM casting utilities for pythonnet interface casting
from ..lcm_casting import cast_to_concrete

# Import string utilities
from ..Shared.string_utils import best_analysis_text

class LexSenseOperations(BaseOperations):
    """
    This class provides operations for managing lexical senses in a FieldWorks project.

    Lexical senses represent the different meanings or uses of a lexical entry.
    Each sense can have glosses, definitions, grammatical information, semantic
    domains, example sentences, pictures, and more.

    Usage::

        from flexlibs2 import FLExProject

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
        self._EnsureWriteEnabled()

        self._ValidateParam(entry_or_hvo, "entry_or_hvo")
        self._ValidateParam(gloss, "gloss")

        self._ValidateStringNotEmpty(gloss, "gloss")

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
        self._EnsureWriteEnabled()

        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._EnsureWriteEnabled()

        self._ValidateParam(item_or_hvo, "item_or_hvo")

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

        # Copy all content from source to duplicate (including owned objects if deep)
        self._copy_sense_content(source, duplicate, deep)

        return duplicate

    def _deep_copy_sense_to(self, source, target_parent):
        """
        Create a deep copy of a sense as a child of target_parent.

        This is used by LexEntryOperations.Duplicate to copy senses into a
        new entry, and internally for recursive subsense duplication.

        Args:
            source: The source ILexSense to copy from.
            target_parent: The parent object (ILexEntry or ILexSense) that
                          owns the new sense via its SensesOS collection.

        Returns:
            ILexSense: The newly created deep copy sense.
        """
        factory = self.project.project.ServiceLocator.GetService(ILexSenseFactory)
        duplicate = factory.Create()
        target_parent.SensesOS.Add(duplicate)
        self._copy_sense_content(source, duplicate, deep=True)
        return duplicate

    def _copy_sense_content(self, source, duplicate, deep=False):
        """
        Copy all sense content from source to duplicate.

        Args:
            source: The source ILexSense to copy from.
            duplicate: The target ILexSense to copy into.
            deep (bool): If True, also copy owned objects (examples, subsenses, pictures).
        """
        # Copy simple MultiString properties
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
            # Deep copy examples — targeting the duplicate sense, not source's parent
            for example in source.ExamplesOS:
                ex_factory = self.project.project.ServiceLocator.GetService(ILexExampleSentenceFactory)
                new_example = ex_factory.Create()
                duplicate.ExamplesOS.Add(new_example)
                new_example.Example.CopyAlternatives(example.Example)
                new_example.Reference.CopyAlternatives(example.Reference)
                # Deep copy translations
                for translation in example.TranslationsOC:
                    trans_factory = self.project.project.ServiceLocator.GetService(ICmTranslationFactory)
                    new_trans = trans_factory.Create()
                    new_example.TranslationsOC.Add(new_trans)
                    new_trans.Translation.CopyAlternatives(translation.Translation)
                    new_trans.TypeRA = translation.TypeRA

            # Deep copy subsenses — recursively targeting the duplicate sense
            for subsense in source.SensesOS:
                self._deep_copy_sense_to(subsense, duplicate)

            # Deep copy pictures
            for picture in source.PicturesOS:
                pic_factory = self.project.project.ServiceLocator.GetService(ICmPictureFactory)
                new_pic = pic_factory.Create()
                duplicate.PicturesOS.Add(new_pic)
                new_pic.Caption.CopyAlternatives(picture.Caption)
                new_pic.PictureFileRA = picture.PictureFileRA
                new_pic.LayoutPos = picture.LayoutPos
                new_pic.ScaleFactor = picture.ScaleFactor

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
        self._EnsureWriteEnabled()

        self._ValidateParam(entry_or_hvo, "entry_or_hvo")
        self._ValidateParam(sense_list, "sense_list")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        gloss = ITsString(sense.Gloss.get_String(wsHandle)).Text
        return self._NormalizeMultiString(gloss)

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
        self._EnsureWriteEnabled()

        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        self._ValidateParam(text, "text")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        # Definition is a MultiString
        defn = ITsString(sense.Definition.get_String(wsHandle)).Text
        return self._NormalizeMultiString(defn)

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
        self._EnsureWriteEnabled()

        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        self._ValidateParam(text, "text")

        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        # Definition is a MultiString - set_String handles building tss
        sense.Definition.set_String(wsHandle, text)

    def GetDefinitionOrGloss(self, sense_or_hvo, wsHandle=None):
        """
        Get definition if available, otherwise fallback to gloss (Pattern 5).

        This is a common FLEx pattern that returns the definition if it exists,
        otherwise returns the gloss. Useful for display where either is acceptable.

        Args:
            sense_or_hvo: The ILexSense object or HVO
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The definition if available, otherwise the gloss, or empty string

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> sense = entry.SensesOS[0]
            >>> # Returns definition if set, otherwise gloss
            >>> text = project.Senses.GetDefinitionOrGloss(sense)
            >>> print(text)
            to run

        Notes:
            - Common FLEx pattern for display purposes
            - Tries definition first (more detailed)
            - Falls back to gloss (shorter)
            - Returns empty string if both are empty
            - Based on FLEx LCM GetDefinitionOrGloss method

        See Also:
            GetDefinition, GetGloss
        """
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)

        # Try definition first
        definition = ITsString(sense.Definition.get_String(wsHandle)).Text
        if definition:
            return definition

        # Fallback to gloss
        gloss = ITsString(sense.Gloss.get_String(wsHandle)).Text
        return self._NormalizeMultiString(gloss)

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._EnsureWriteEnabled()

        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        self._ValidateParam(pos, "pos")

        sense = self.__GetSenseObject(sense_or_hvo)

        # Get POS object (handle both HVO and object)
        if isinstance(pos, int):
            pos_obj = self.project.project.ServiceLocator.GetObject(pos)
        else:
            pos_obj = pos

        # Check if sense already has an MSA
        if sense.MorphoSyntaxAnalysisRA is not None:
            # Update existing MSA's Category
            # Use cast_to_concrete() to handle pythonnet interface casting
            msa = cast_to_concrete(sense.MorphoSyntaxAnalysisRA)
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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._EnsureWriteEnabled()

        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
            - If domain already exists in the list, it is not added again
              (duplicates are prevented)
            - Semantic domains help organize the lexicon by meaning
            - Use project.GetAllSemanticDomains() to get available domains

        See Also:
            GetSemanticDomains, RemoveSemanticDomain
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        self._ValidateParam(domain_or_hvo, "domain_or_hvo")

        sense = self.__GetSenseObject(sense_or_hvo)
        domain = self.__GetSemanticDomainObject(domain_or_hvo)

        if domain not in sense.SemanticDomainsRC:
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
        self._EnsureWriteEnabled()

        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        self._ValidateParam(domain_or_hvo, "domain_or_hvo")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._EnsureWriteEnabled()

        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        self._ValidateParam(text, "text")

        self._ValidateStringNotEmpty(text, "text")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._EnsureWriteEnabled()

        self._ValidateParam(parent_sense_or_hvo, "parent_sense_or_hvo")
        self._ValidateParam(gloss, "gloss")

        self._ValidateStringNotEmpty(gloss, "gloss")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._EnsureWriteEnabled()

        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._EnsureWriteEnabled()

        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

        sense = self.__GetSenseObject(sense_or_hvo)
        return sense.PicturesOS.Count

    def AddPicture(self, sense_or_hvo, image_path, caption=None, wsHandle=None):
        """
        Add a picture (image) to a lexical sense.

        Pictures illustrate the meaning of a sense. The image file is copied into
        the project's LinkedFiles/Pictures directory and a reference is created.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            image_path (str): Path to the image file (will be copied to project).
            caption (str): Optional caption text for the picture.
            wsHandle: Optional writing system handle for caption. Defaults to vernacular WS.

        Returns:
            ICmPicture: The newly created picture object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo or image_path is None.
            FP_ParameterError: If image file doesn't exist.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     # Add picture to sense
            ...     picture = project.Senses.AddPicture(
            ...         senses[0],
            ...         "/path/to/dog.jpg",
            ...         caption="A friendly dog"
            ...     )
            ...     print(f"Added picture with caption: {project.Senses.GetCaption(picture)}")
            Added picture with caption: A friendly dog

            >>> # Add picture without caption
            >>> picture = project.Senses.AddPicture(senses[0], "/path/to/cat.jpg")

            >>> # Get all pictures
            >>> pictures = project.Senses.GetPictures(senses[0])
            >>> print(f"Sense has {len(pictures)} pictures")
            Sense has 2 pictures

        Notes:
            - Image file is copied to LinkedFiles/Pictures/ directory
            - Supported formats: JPG, PNG, GIF, BMP, TIFF
            - Caption can be edited later with SetCaption()
            - Pictures are stored in the sense's PicturesOS collection
            - Uses ICmPictureFactory to create ICmPicture object
            - The physical file is copied to preserve the original

        See Also:
            RemovePicture, GetPictures, SetCaption, RenamePicture, MovePicture
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        self._ValidateParam(image_path, "image_path")

        sense = self.__GetSenseObject(sense_or_hvo)

        # Verify image file exists
        if not os.path.exists(image_path):
            raise FP_ParameterError(f"Image file not found: {image_path}")

        # Copy image to Pictures folder using Media operations
        media_file = self.project.Media.CopyToProject(image_path, internal_subdir="Pictures")

        # Create ICmPicture object
        factory = self.project.project.ServiceLocator.GetService(ICmPictureFactory)
        picture = factory.Create()

        # Add to sense (must be done before setting properties)
        sense.PicturesOS.Add(picture)

        # Set the picture file reference
        picture.PictureFileRA = media_file

        # Set caption if provided
        if caption:
            wsHandle = self.__WSHandleVernacular(wsHandle)
            mkstr = TsStringUtils.MakeString(caption, wsHandle)
            picture.Caption.set_String(wsHandle, mkstr)

        logger.info(f"Added picture to sense: {os.path.basename(image_path)}")

        return picture

    def RemovePicture(self, sense_or_hvo, picture, delete_file=False):
        """
        Remove a picture from a lexical sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            picture: The ICmPicture object to remove.
            delete_file (bool): If True, also delete the physical image file (default: False).

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo or picture is None.
            FP_ParameterError: If picture not in sense's collection.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     pictures = project.Senses.GetPictures(senses[0])
            ...     if pictures:
            ...         # Remove picture but keep file
            ...         project.Senses.RemovePicture(senses[0], pictures[0])
            ...
            ...         # Remove picture AND delete file
            ...         project.Senses.RemovePicture(senses[0], pictures[1], delete_file=True)

        Warning:
            - With delete_file=True, the image is permanently deleted from disk
            - Other senses or objects referencing the same file will lose access
            - Deletion cannot be undone
            - Use delete_file=True with caution

        Notes:
            - Picture is removed from the sense's PicturesOS collection
            - By default, the physical file is preserved in LinkedFiles/Pictures
            - If delete_file=True, the file is deleted from the file system
            - No error if picture is not in collection (silently ignored)

        See Also:
            AddPicture, GetPictures, MovePicture
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        self._ValidateParam(picture, "picture")

        sense = self.__GetSenseObject(sense_or_hvo)

        # Verify picture is in collection
        if picture not in sense.PicturesOS:
            raise FP_ParameterError("Picture not found in sense's picture collection")

        # Get file path before removing (for optional deletion)
        file_path = None
        if delete_file and hasattr(picture, 'PictureFileRA') and picture.PictureFileRA:
            file_path = self.project.Media.GetExternalPath(picture.PictureFileRA)

        # Remove from collection
        sense.PicturesOS.Remove(picture)

        # Delete physical file if requested
        if delete_file and file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted image file: {file_path}")

        logger.info("Removed picture from sense")

    def MovePicture(self, picture, from_sense_or_hvo, to_sense_or_hvo):
        """
        Move a picture from one sense to another sense.

        This is useful when reorganizing sense structure or correcting misplaced pictures.
        The picture object itself is moved (not copied), preserving its caption and file reference.

        Args:
            picture: The ICmPicture object to move.
            from_sense_or_hvo: Source ILexSense object or HVO.
            to_sense_or_hvo: Destination ILexSense object or HVO.

        Returns:
            bool: True if move was successful, False if source and destination are the same.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If any parameter is None.
            FP_ParameterError: If picture not in source sense's collection.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if len(senses) >= 2:
            ...     # Move picture from one sense to another
            ...     sense1 = senses[0]  # "to run (move fast)"
            ...     sense2 = senses[1]  # "to run (operate a machine)"
            ...     pictures = project.Senses.GetPictures(sense1)
            ...
            ...     if pictures:
            ...         # Move the picture of a person running to the correct sense
            ...         success = project.Senses.MovePicture(pictures[0], sense1, sense2)
            ...
            ...         # Verify the move
            ...         print(f"Move successful: {success}")
            ...         print(f"Sense 1 pictures: {project.Senses.GetPictureCount(sense1)}")
            ...         print(f"Sense 2 pictures: {project.Senses.GetPictureCount(sense2)}")
            Move successful: True
            Sense 1 pictures: 0
            Sense 2 pictures: 1

            >>> # Can also move between entries
            >>> entry2 = list(project.LexiconAllEntries())[1]
            >>> other_sense = entry2.SensesOS[0]
            >>> project.Senses.MovePicture(pictures[1], sense1, other_sense)

        Notes:
            - Picture is removed from source PicturesOS and added to destination PicturesOS
            - Caption and file reference are preserved
            - The physical image file is NOT moved/copied
            - Cannot move to the same sense (returns False)
            - Picture object's GUID remains the same
            - The picture will appear in the new sense's illustration area

        Warning:
            - Moving pictures between entries is allowed but should be done carefully
            - Ensure the picture is semantically appropriate for the target sense
            - The picture will no longer be associated with the source sense

        See Also:
            AddPicture, RemovePicture, GetPictures
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(picture, "picture")
        self._ValidateParam(from_sense_or_hvo, "from_sense_or_hvo")
        self._ValidateParam(to_sense_or_hvo, "to_sense_or_hvo")

        from_sense = self.__GetSenseObject(from_sense_or_hvo)
        to_sense = self.__GetSenseObject(to_sense_or_hvo)

        # Can't move to same sense
        if from_sense == to_sense:
            logger.warning("Source and destination are the same sense")
            return False

        # Verify picture is in source collection
        if picture not in from_sense.PicturesOS:
            raise FP_ParameterError("Picture not found in source sense's picture collection")

        # Move the picture (remove from source, add to destination)
        from_sense.PicturesOS.Remove(picture)
        to_sense.PicturesOS.Add(picture)

        logger.info(f"Moved picture from sense {from_sense.Guid} to sense {to_sense.Guid}")

        return True

    def SetCaption(self, picture, caption, wsHandle=None):
        """
        Set or update the caption for a picture.

        Args:
            picture: The ICmPicture object.
            caption (str): The caption text to set.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If picture or caption is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     pictures = project.Senses.GetPictures(senses[0])
            ...     if pictures:
            ...         # Set caption in default vernacular
            ...         project.Senses.SetCaption(pictures[0], "A brown dog")
            ...
            ...         # Set caption in specific writing system
            ...         project.Senses.SetCaption(pictures[0], "Un chien brun",
            ...                                   project.WSHandle('fr'))
            ...
            ...         # Verify
            ...         caption = project.Senses.GetCaption(pictures[0])
            ...         print(f"Caption: {caption}")
            Caption: A brown dog

        Notes:
            - Captions can be set in multiple writing systems
            - Empty string is allowed (clears the caption)
            - Caption is stored in the picture's Caption multistring field
            - Captions help describe the image content

        See Also:
            GetCaption, AddPicture
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(picture, "picture")
        self._ValidateParam(caption, "caption")

        wsHandle = self.__WSHandleVernacular(wsHandle)
        mkstr = TsStringUtils.MakeString(caption, wsHandle)
        picture.Caption.set_String(wsHandle, mkstr)

    def GetCaption(self, picture, wsHandle=None):
        """
        Get the caption for a picture.

        Args:
            picture: The ICmPicture object.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            str: The caption text, or empty string if not set.

        Raises:
            FP_NullParameterError: If picture is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     pictures = project.Senses.GetPictures(senses[0])
            ...     if pictures:
            ...         caption = project.Senses.GetCaption(pictures[0])
            ...         print(f"Picture caption: {caption}")
            Picture caption: A friendly dog
            ...
            ...         # Get caption in specific writing system
            ...         caption_fr = project.Senses.GetCaption(pictures[0],
            ...                                                project.WSHandle('fr'))
            ...         print(f"French caption: {caption_fr}")
            French caption: Un chien amical

        Notes:
            - Returns empty string if caption not set in specified writing system
            - Captions can be stored in multiple writing systems
            - Default writing system is the default vernacular WS

        See Also:
            SetCaption, AddPicture, GetPictures
        """
        self._ValidateParam(picture, "picture")

        wsHandle = self.__WSHandleVernacular(wsHandle)
        caption = ITsString(picture.Caption.get_String(wsHandle)).Text
        return self._NormalizeMultiString(caption)

    def RenamePicture(self, picture, new_filename):
        """
        Rename the image file for a picture and update the reference.

        This renames the physical file in the LinkedFiles/Pictures directory
        and updates the ICmFile reference to point to the new filename.

        Args:
            picture: The ICmPicture object.
            new_filename (str): The new filename for the image (e.g., "dog_brown.jpg").

        Returns:
            str: The new internal path to the renamed file.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If picture or new_filename is None.
            FP_ParameterError: If picture has no associated file, or rename fails.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> senses = list(project.Senses.GetAll(entry))
            >>> if senses:
            ...     pictures = project.Senses.GetPictures(senses[0])
            ...     if pictures:
            ...         # Rename the picture file
            ...         new_path = project.Senses.RenamePicture(pictures[0], "dog_brown.jpg")
            ...         print(f"Renamed to: {new_path}")
            Renamed to: Pictures/dog_brown.jpg

        Notes:
            - Renames the physical file in the file system
            - Updates the ICmFile object's InternalPath
            - File extension should match the original file type
            - New filename must be valid for the file system
            - The file remains in the same directory (Pictures/)

        Warning:
            - Ensure new_filename is unique to avoid conflicts
            - File extension should match the image type
            - Other objects referencing the same file are also affected

        See Also:
            AddPicture, GetPictures, MediaOperations.RenameMediaFile
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(picture, "picture")
        self._ValidateParam(new_filename, "new_filename")

        # Verify picture has an associated file
        if not hasattr(picture, 'PictureFileRA') or not picture.PictureFileRA:
            raise FP_ParameterError("Picture has no associated file")

        # Get the current file object
        file_obj = picture.PictureFileRA

        # Get current internal path
        current_path = self.project.Media.GetInternalPath(file_obj)
        if not current_path:
            raise FP_ParameterError("Cannot determine current file path")

        # Get the directory part (e.g., "Pictures")
        path_parts = current_path.replace('\\', '/').split('/')
        if len(path_parts) > 1:
            directory = '/'.join(path_parts[:-1])
            new_internal_path = f"{directory}/{new_filename}"
        else:
            new_internal_path = new_filename

        # Get external paths
        old_external_path = self.project.Media.GetExternalPath(file_obj)

        # Construct new external path
        if old_external_path:
            old_dir = os.path.dirname(old_external_path)
            new_external_path = os.path.join(old_dir, new_filename)

            # Rename the physical file
            if os.path.exists(old_external_path):
                os.rename(old_external_path, new_external_path)
                logger.info(f"Renamed file: {old_external_path} -> {new_external_path}")
            else:
                raise FP_ParameterError(f"File not found: {old_external_path}")

        # Update the ICmFile internal path
        file_obj.InternalPath = new_internal_path

        logger.info(f"Updated picture reference to: {new_internal_path}")

        return new_internal_path

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

        sense = self.__GetSenseObject(sense_or_hvo)

        # SenseAnalysesCount is not part of the interface ILexSense, but it
        # is a public member of LexSense, which we can access by reflection.
        count = ReflectionHelper.GetProperty(sense, "SenseAnalysesCount")
        return count

    # --- Additional Text Properties ---

    def GetBibliography(self, sense_or_hvo, wsHandle=None):
        """Get the bibliography of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        return self._NormalizeMultiString(ITsString(sense.Bibliography.get_String(wsHandle)).Text)

    def SetBibliography(self, sense_or_hvo, text, wsHandle=None):
        """Set the bibliography of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        sense.Bibliography.set_String(wsHandle, mkstr)

    def GetGeneralNote(self, sense_or_hvo, wsHandle=None):
        """Get the general note of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        return self._NormalizeMultiString(ITsString(sense.GeneralNote.get_String(wsHandle)).Text)

    def SetGeneralNote(self, sense_or_hvo, text, wsHandle=None):
        """Set the general note of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        sense.GeneralNote.set_String(wsHandle, mkstr)

    def GetDiscourseNote(self, sense_or_hvo, wsHandle=None):
        """Get the discourse note of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        return self._NormalizeMultiString(ITsString(sense.DiscourseNote.get_String(wsHandle)).Text)

    def SetDiscourseNote(self, sense_or_hvo, text, wsHandle=None):
        """Set the discourse note of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        sense.DiscourseNote.set_String(wsHandle, mkstr)

    def GetEncyclopedicInfo(self, sense_or_hvo, wsHandle=None):
        """Get the encyclopedic info of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        return self._NormalizeMultiString(ITsString(sense.EncyclopedicInfo.get_String(wsHandle)).Text)

    def SetEncyclopedicInfo(self, sense_or_hvo, text, wsHandle=None):
        """Set the encyclopedic info of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        sense.EncyclopedicInfo.set_String(wsHandle, mkstr)

    def GetGrammarNote(self, sense_or_hvo, wsHandle=None):
        """Get the grammar note of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        return self._NormalizeMultiString(ITsString(sense.GrammarNote.get_String(wsHandle)).Text)

    def SetGrammarNote(self, sense_or_hvo, text, wsHandle=None):
        """Set the grammar note of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        sense.GrammarNote.set_String(wsHandle, mkstr)

    def GetPhonologyNote(self, sense_or_hvo, wsHandle=None):
        """Get the phonology note of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        return self._NormalizeMultiString(ITsString(sense.PhonologyNote.get_String(wsHandle)).Text)

    def SetPhonologyNote(self, sense_or_hvo, text, wsHandle=None):
        """Set the phonology note of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        sense.PhonologyNote.set_String(wsHandle, mkstr)

    def GetSemanticsNote(self, sense_or_hvo, wsHandle=None):
        """Get the semantics note of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        return self._NormalizeMultiString(ITsString(sense.SemanticsNote.get_String(wsHandle)).Text)

    def SetSemanticsNote(self, sense_or_hvo, text, wsHandle=None):
        """Set the semantics note of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        sense.SemanticsNote.set_String(wsHandle, mkstr)

    def GetSocioLinguisticsNote(self, sense_or_hvo, wsHandle=None):
        """Get the socio-linguistics note of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        return self._NormalizeMultiString(ITsString(sense.SocioLinguisticsNote.get_String(wsHandle)).Text)

    def SetSocioLinguisticsNote(self, sense_or_hvo, text, wsHandle=None):
        """Set the socio-linguistics note of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        sense.SocioLinguisticsNote.set_String(wsHandle, mkstr)

    def GetAnthroNote(self, sense_or_hvo, wsHandle=None):
        """Get the anthropology note of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        return self._NormalizeMultiString(ITsString(sense.AnthroNote.get_String(wsHandle)).Text)

    def SetAnthroNote(self, sense_or_hvo, text, wsHandle=None):
        """Set the anthropology note of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        sense.AnthroNote.set_String(wsHandle, mkstr)

    def GetRestrictions(self, sense_or_hvo, wsHandle=None):
        """Get the restrictions of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        return self._NormalizeMultiString(ITsString(sense.Restrictions.get_String(wsHandle)).Text)

    def SetRestrictions(self, sense_or_hvo, text, wsHandle=None):
        """Set the restrictions of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleAnalysis(wsHandle)
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        sense.Restrictions.set_String(wsHandle, mkstr)

    def GetSource(self, sense_or_hvo):
        """Get the source of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        return self._NormalizeMultiString(sense.Source)

    def SetSource(self, sense_or_hvo, text):
        """Set the source of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        sense.Source = text

    def GetScientificName(self, sense_or_hvo):
        """Get the scientific name of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        return self._NormalizeMultiString(sense.ScientificName)

    def SetScientificName(self, sense_or_hvo, text):
        """Set the scientific name of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        sense.ScientificName = text

    def GetImportResidue(self, sense_or_hvo):
        """Get the import residue of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        return self._NormalizeMultiString(sense.ImportResidue)

    def SetImportResidue(self, sense_or_hvo, text):
        """Set the import residue of a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or text is None:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        sense.ImportResidue = text

    # --- Reference Collection Properties ---

    def _find_possibility_by_name(self, list_name, item_name):
        """
        Helper to find a possibility item by name in a possibility list.

        Args:
            list_name (str): Name of the possibility list (e.g., "Usage Types", "Semantic Domains")
            item_name (str): Name of the item to find within the list

        Returns:
            The possibility item object if found, None otherwise
        """
        # Find the possibility list by name
        poss_list = None
        for plist in self.project.PossibilityLists.GetAllLists():
            plist_name = best_analysis_text(plist.Name) if plist.Name else None
            if plist_name == list_name:
                poss_list = plist
                break

        if not poss_list:
            return None

        # Search through items in the list for name match
        for item in self.project.PossibilityLists.GetItems(poss_list, flat=True):
            item_text = best_analysis_text(item.Name) if item.Name else None
            if item_text == item_name:
                return item

        return None

    def GetUsageTypes(self, sense_or_hvo):
        """Get the usage types of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        result = []
        for item in sense.UsageTypesRC:
            name = best_analysis_text(item.Name) if item.Name else str(item.Guid)
            result.append(name)
        return result

    def AddUsageType(self, sense_or_hvo, usage_type):
        """Add a usage type to a sense. Accepts string name or object."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or not usage_type:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)

        # If string, look it up
        if isinstance(usage_type, str):
            usage_type_name = usage_type
            # Try "Usages" (standard FLEx list name) first, then "Usage Types" for compatibility
            usage_type = self._find_possibility_by_name("Usages", usage_type_name)
            if not usage_type:
                usage_type = self._find_possibility_by_name("Usage Types", usage_type_name)
            if not usage_type:
                raise FP_ParameterError(f"Usage type '{usage_type_name}' not found")

        if usage_type not in sense.UsageTypesRC:
            sense.UsageTypesRC.Add(usage_type)

    def RemoveUsageType(self, sense_or_hvo, usage_type):
        """Remove a usage type from a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or not usage_type:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        if usage_type in sense.UsageTypesRC:
            sense.UsageTypesRC.Remove(usage_type)

    def GetDomainTypes(self, sense_or_hvo):
        """Get the domain types of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        result = []
        for item in sense.DomainTypesRC:
            name = best_analysis_text(item.Name) if item.Name else str(item.Guid)
            result.append(name)
        return result

    def AddDomainType(self, sense_or_hvo, domain_type):
        """Add a domain type to a sense. Accepts string name or object."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or not domain_type:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)

        # If string, look it up
        if isinstance(domain_type, str):
            domain_type_name = domain_type
            domain_type = self._find_possibility_by_name("Semantic Domains", domain_type_name)
            if not domain_type:
                raise FP_ParameterError(f"Domain type '{domain_type_name}' not found")

        if domain_type not in sense.DomainTypesRC:
            sense.DomainTypesRC.Add(domain_type)

    def RemoveDomainType(self, sense_or_hvo, domain_type):
        """Remove a domain type from a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or not domain_type:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        if domain_type in sense.DomainTypesRC:
            sense.DomainTypesRC.Remove(domain_type)

    def GetAnthroCodes(self, sense_or_hvo):
        """Get the anthropology codes of a sense."""
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")
        sense = self.__GetSenseObject(sense_or_hvo)
        result = []
        for item in sense.AnthroCodesRC:
            name = best_analysis_text(item.Name) if item.Name else str(item.Guid)
            result.append(name)
        return result

    def AddAnthroCode(self, sense_or_hvo, anthro_code):
        """Add an anthropology code to a sense. Accepts string name or object."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or not anthro_code:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)

        # If string, look it up
        if isinstance(anthro_code, str):
            anthro_code_name = anthro_code
            anthro_code = self._find_possibility_by_name("Anthropology Categories", anthro_code_name)
            if not anthro_code:
                raise FP_ParameterError(f"Anthropology code '{anthro_code_name}' not found")

        if anthro_code not in sense.AnthroCodesRC:
            sense.AnthroCodesRC.Add(anthro_code)

    def RemoveAnthroCode(self, sense_or_hvo, anthro_code):
        """Remove an anthropology code from a sense."""
        self._EnsureWriteEnabled()
        if not sense_or_hvo or not anthro_code:
            raise FP_NullParameterError()
        sense = self.__GetSenseObject(sense_or_hvo)
        if anthro_code in sense.AnthroCodesRC:
            sense.AnthroCodesRC.Remove(anthro_code)

    # --- Private Helper Methods ---

    # --- Back-Reference Methods (Pattern 3) ---

    def GetVisibleComplexFormBackRefs(self, sense_or_hvo):
        """
        Get all complex forms that reference this sense.

        Returns all LexEntryRef objects where this sense appears in
        ShowComplexFormsIn and RefType is ComplexForm.

        Args:
            sense_or_hvo: Either an ILexSense object or its HVO

        Returns:
            list: List of ILexEntryRef objects (complex forms referencing this sense)

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> sense = entry.SensesOS[0]
            >>> complex_forms = project.Senses.GetVisibleComplexFormBackRefs(sense)
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
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

        sense = self.__GetSenseObject(sense_or_hvo)

        # Use the LCM property directly
        try:
            back_refs = list(sense.VisibleComplexFormBackRefs)
            return back_refs
        except AttributeError:
            logger.warning("VisibleComplexFormBackRefs not available, returning empty list")
            return []

    def GetComplexFormsNotSubentries(self, sense_or_hvo):
        """
        Get complex forms that reference this sense, excluding subentries.

        Returns complex forms (compounds, idioms, etc.) but excludes any
        where the owner entry appears as a subentry (in PrimaryLexemesRS).

        Args:
            sense_or_hvo: Either an ILexSense object or its HVO

        Returns:
            list: List of ILexEntryRef objects (complex forms, excluding subentries)

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> sense = entry.SensesOS[0]
            >>> complex_forms = project.Senses.GetComplexFormsNotSubentries(sense)
            >>> for lex_ref in complex_forms:
            ...     cf_entry = lex_ref.OwningEntry
            ...     print(f"Complex form: {project.LexEntry.GetHeadword(cf_entry)}")

        Notes:
            - Filters out subentries from VisibleComplexFormBackRefs
            - A subentry is where the owner entry appears in PrimaryLexemesRS
            - Based on FLEx LCM ComplexFormsNotSubentries property

        See Also:
            GetVisibleComplexFormBackRefs
        """
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

        sense = self.__GetSenseObject(sense_or_hvo)

        # Get all complex form back refs
        all_complex_forms = self.GetVisibleComplexFormBackRefs(sense)

        # Filter out subentries (where owner entry is in PrimaryLexemesRS)
        result = []
        owner_entry = sense.OwnerOfClass(ILexEntry)
        if not owner_entry:
            return result

        for lex_ref in all_complex_forms:
            try:
                is_subentry = any(item.Hvo == owner_entry.Hvo for item in lex_ref.PrimaryLexemesRS)
                if not is_subentry:
                    result.append(lex_ref)
            except (AttributeError, System.NullReferenceException) as e:
                result.append(lex_ref)

        return result

    def GetMinimalLexReferences(self, sense_or_hvo):
        """
        Get essential lexical references for this sense.

        Returns only "minimal" lexical references - those that are multi-target
        or have specific mapping types (sequence types).

        Args:
            sense_or_hvo: Either an ILexSense object or its HVO

        Returns:
            list: List of ILexReference objects (minimal references)

        Example:
            >>> entry = project.LexEntry.Find("big")
            >>> sense = entry.SensesOS[0]
            >>> lex_refs = project.Senses.GetMinimalLexReferences(sense)
            >>> for lex_ref in lex_refs:
            ...     ref_type = lex_ref.Owner  # ILexRefType
            ...     print(f"Reference type: {ref_type.Name.BestAnalysisAlternative.Text}")
            ...     for target in lex_ref.TargetsRS:
            ...         if target.Hvo != sense.Hvo:
            ...             gloss = project.Senses.GetGloss(target)
            ...             print(f"  -> {gloss}")

        Notes:
            - Includes multi-target references (synonyms, antonyms, etc.)
            - Includes sequence-type references
            - Excludes single-target non-sequence references
            - Based on FLEx LCM MinimalLexReferences property

        See Also:
            GetVisibleComplexFormBackRefs
        """
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

        sense = self.__GetSenseObject(sense_or_hvo)

        # Use the LCM property directly
        try:
            lex_refs = list(sense.MinimalLexReferences)
            return lex_refs
        except AttributeError:
            logger.warning("MinimalLexReferences not available, returning empty list")
            return []

    def GetAllSenses(self, sense_or_hvo):
        """
        Get this sense and all its subsenses recursively.

        Returns all senses in a flattened list, including the sense itself
        and recursively including all subsenses at any depth.

        Args:
            sense_or_hvo: Either an ILexSense object or its HVO

        Returns:
            list: List of ILexSense objects (this sense + all subsenses)

        Example:
            >>> entry = project.LexEntry.Find("run")
            >>> sense = entry.SensesOS[0]
            >>> all_senses = project.Senses.GetAllSenses(sense)
            >>> print(f"Total (including subsenses): {len(all_senses)}")
            >>> for s in all_senses:
            ...     gloss = project.Senses.GetGloss(s)
            ...     depth = len(list(s.PathToRoot)) - 2
            ...     indent = "  " * depth
            ...     print(f"{indent}{gloss}")

        Notes:
            - Recursively collects all subsenses at any depth
            - INCLUDES the sense itself in the result (unlike LexEntry.AllSenses)
            - Based on FLEx LCM AllSenses property
            - For counting: use len(GetAllSenses(sense))

        See Also:
            GetSubsenses, CreateSubsense
        """
        self._ValidateParam(sense_or_hvo, "sense_or_hvo")

        sense = self.__GetSenseObject(sense_or_hvo)

        # Use the LCM property directly
        try:
            all_senses = list(sense.AllSenses)
            return all_senses
        except AttributeError:
            # Fallback: manually collect recursively
            result = [sense]  # Include self
            if sense.SensesOS and sense.SensesOS.Count > 0:
                for subsense in sense.SensesOS:
                    result.extend(self.GetAllSenses(subsense))
            return result

    # --- Pattern 7: MergeObject (Sense merging) ---

    def __GetSenseSignature(self, sense):
        """
        Generate a signature for sense duplicate detection.

        Two senses with identical signatures are considered duplicates and can be merged.
        Signature is based on:
        - Gloss values across all writing systems
        - Definition values across all writing systems
        - Semantic domain references

        Args:
            sense: The ILexSense object

        Returns:
            tuple: Hashable signature (gloss_dict, definition_dict, semantic_domains_tuple)
                  that uniquely identifies the sense content
        """
        try:
            # Get gloss across all writing systems
            gloss_dict = {}
            for ws in self.project.project.WritingSystemManager.AllWritingSystems:
                ws_handle = ws.Handle
                gloss_text = ITsString(sense.Gloss.get_String(ws_handle)).Text if sense.Gloss else ""
                if gloss_text:
                    gloss_dict[ws_handle] = gloss_text

            # Get definition across all writing systems
            definition_dict = {}
            for ws in self.project.project.WritingSystemManager.AllWritingSystems:
                ws_handle = ws.Handle
                def_text = ITsString(sense.Definition.get_String(ws_handle)).Text if sense.Definition else ""
                if def_text:
                    definition_dict[ws_handle] = def_text

            # Get semantic domains (as tuple of GUIDs for hashability)
            semantic_domains = tuple(
                sorted([str(domain.Guid) for domain in sense.SemanticDomainsRC])
            )

            # Create signature tuple
            sig = (
                frozenset(gloss_dict.items()),
                frozenset(definition_dict.items()),
                semantic_domains
            )

            return sig

        except Exception as e:
            logger.debug(f"Could not generate sense signature: {e}")
            return None

    def __FindDuplicateSensesInEntry(self, entry):
        """
        Find duplicate senses within an entry.

        Returns a list of (first_sense, [duplicate_senses]) tuples, where all senses
        in each group have identical signatures.

        Args:
            entry: The ILexEntry object

        Returns:
            list: List of tuples (master_sense, [duplicate_sense_list])
                  Empty list if no duplicates found
        """
        if not entry.SensesOS:
            return []

        # Build signature map
        sig_map = {}
        for sense in entry.SensesOS:
            sig = self.__GetSenseSignature(sense)
            if sig:
                if sig not in sig_map:
                    sig_map[sig] = []
                sig_map[sig].append(sense)

        # Find groups with duplicates (more than one sense with same signature)
        duplicates = []
        for sig, senses in sig_map.items():
            if len(senses) > 1:
                # Keep first sense, mark rest as duplicates
                master = senses[0]
                dupes = senses[1:]
                duplicates.append((master, dupes))
                logger.debug(
                    f"Found {len(dupes)} duplicate sense(s) with gloss/definition: "
                    f"{sig[0]} / {sig[1]}"
                )

        return duplicates

    def MergeObject(self, survivor_or_hvo, victim_or_hvo, fLoseNoStringData=True, auto_deduplicate=True):
        """
        Merge one sense into another (IRREVERSIBLE operation).

        This method delegates to the underlying LibLCM C# implementation, which handles
        all the complex merge logic with proper MultiString handling. Optionally, it can
        then deduplicate examples that result from the merge.

        Args:
            survivor_or_hvo: Sense that will receive merged data (HVO or ILexSense)
            victim_or_hvo: Sense that will be deleted after merge (HVO or ILexSense)
            fLoseNoStringData (bool): If True, concatenate strings (preserve both values);
                                      If False, overwrite strings (victim overwrites survivor)
                                      Default: True (data preservation)
            auto_deduplicate (bool): If True, automatically deduplicate examples after merge.
                                    Default: True

        Raises:
            FP_ReadOnlyError: If project not write-enabled
            FP_NullParameterError: If either parameter is None
            FP_ParameterError: If senses are not compatible for merging

        Example::

            >>> # Merge duplicate sense into main sense with auto-deduplication
            >>> keep = project.Senses.Find(...)
            >>> remove = project.Senses.Find(...)
            >>> project.Senses.MergeObject(keep, remove, fLoseNoStringData=True)
            >>> # 'remove' is deleted, data merged into 'keep'
            >>> # Any duplicate examples are also auto-removed

            >>> # Result with fLoseNoStringData=True:
            >>> # Definition: "defn 1; defn 2" (LibLCM uses SEMICOLON separator)
            >>> # Gloss: "gloss 1; gloss 2" (LibLCM uses SEMICOLON separator)

        Notes:
            - This operation is IRREVERSIBLE (victim is deleted)
            - Delegates to LibLCM's battle-tested ILexSense.MergeObject()
            - Definition and Gloss merging follows LibLCM's SEMICOLON separator convention
            - Back-references are automatically updated
            - Optionally deduplicates duplicate examples
            - Based on FLEx LexSense.MergeObject

        See Also:
            LexEntry.MergeObject - For merging entries
        """
        if not self.project.write_enabled:
            raise FP_ReadOnlyError()

        if not survivor_or_hvo or not victim_or_hvo:
            raise FP_NullParameterError()

        survivor = self.__GetSenseObject(survivor_or_hvo)
        victim = self.__GetSenseObject(victim_or_hvo)

        # Validate same class
        if survivor.ClassName != victim.ClassName:
            raise FP_ParameterError(f"Cannot merge different classes: {survivor.ClassName} vs {victim.ClassName}")

        # Don't merge a sense into itself
        if survivor.Hvo == victim.Hvo:
            raise FP_ParameterError("Cannot merge sense into itself")

        # Delegate to LibLCM's battle-tested merge implementation
        logger.info(f"Merging sense (HVO: {victim.Hvo}) into survivor (HVO: {survivor.Hvo})")
        survivor.MergeObject(victim, fLoseNoStringData)

        # Optional deduplication layer (NEW value added by FlexLibs2)
        if auto_deduplicate:
            logger.debug(f"Running auto-deduplication on merged sense (HVO: {survivor.Hvo})")
            self.__DeduplicateExamplesInSense(survivor)

    # --- Private Helper Methods for Deduplication ---

    def __GetExampleSignature(self, example):
        """
        Generate a signature for example duplicate detection.

        Two examples with identical signatures are considered duplicates.
        Signature is based on:
        - Example text across all writing systems
        - Reference text

        Args:
            example: The ILexExampleSentence object

        Returns:
            tuple: Hashable signature (example_dict, reference) that identifies the example
        """
        try:
            # Get example text across all writing systems
            example_dict = {}
            for ws in self.project.project.WritingSystemManager.AllWritingSystems:
                ws_handle = ws.Handle
                ex_text = ITsString(example.Example.get_String(ws_handle)).Text if example.Example else ""
                if ex_text:
                    example_dict[ws_handle] = ex_text

            # Get reference
            ref_text = ITsString(example.Reference.get_String(0)).Text if example.Reference else ""

            # Create signature tuple
            sig = (frozenset(example_dict.items()), ref_text)
            return sig

        except Exception as e:
            logger.debug(f"Could not generate example signature: {e}")
            return None

    def __FindDuplicateExamplesInSense(self, sense):
        """
        Find duplicate examples within a sense.

        Returns a list of (first_example, [duplicate_examples]) tuples, where all examples
        in each group have identical signatures.

        Args:
            sense: The ILexSense object

        Returns:
            list: List of tuples (master_example, [duplicate_example_list])
                  Empty list if no duplicates found
        """
        if not sense.ExamplesOS:
            return []

        # Build signature map
        sig_map = {}
        for example in sense.ExamplesOS:
            sig = self.__GetExampleSignature(example)
            if sig:
                if sig not in sig_map:
                    sig_map[sig] = []
                sig_map[sig].append(example)

        # Find groups with duplicates
        duplicates = []
        for sig, examples in sig_map.items():
            if len(examples) > 1:
                master = examples[0]
                dupes = examples[1:]
                duplicates.append((master, dupes))
                logger.debug(f"Found {len(dupes)} duplicate example(s) with text: {sig[0]}")

        return duplicates

    def __DeduplicateExamplesInSense(self, sense):
        """
        Detect and merge duplicate examples within a sense.

        This is called after merging senses to clean up any duplicate examples
        that resulted from the merge. Duplicates are detected by comparing:
        - Example text (per writing system)
        - Reference text

        Examples with identical signatures are deleted (duplicates removed, content preserved).

        Args:
            sense: The ILexSense to deduplicate

        Notes:
            - Keeps first occurrence, removes duplicates
            - Logs all removed duplicates
        """
        if not sense.ExamplesOS or len(sense.ExamplesOS) < 2:
            return  # No duplicates possible

        try:
            duplicates = self.__FindDuplicateExamplesInSense(sense)
            merged_count = 0

            for master, dupes in duplicates:
                for dupe in dupes:
                    try:
                        logger.info(
                            f"Auto-removing duplicate example in sense (HVO: {dupe.Hvo}) "
                            f"keeping master (HVO: {master.Hvo})"
                        )
                        # Simply remove the duplicate (don't merge content since they're identical)
                        dupe.OwningList.Remove(dupe)
                        merged_count += 1
                    except Exception as e:
                        logger.warning(f"Could not remove duplicate example (HVO: {dupe.Hvo}): {e}")

            if merged_count > 0:
                logger.info(f"Auto-deduplicated {merged_count} duplicate example(s) in sense (HVO: {sense.Hvo})")

        except Exception as e:
            logger.warning(f"Error during example deduplication: {e}")


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
