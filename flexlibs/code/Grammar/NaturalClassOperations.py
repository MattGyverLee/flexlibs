#
#   NaturalClassOperations.py
#
#   Class: NaturalClassOperations
#          Natural class operations for FieldWorks Language Explorer
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
    IPhNaturalClass,
    IPhNCSegments,
    IPhNCSegmentsFactory,
    IPhPhoneme,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class NaturalClassOperations(BaseOperations):
    """
    This class provides operations for managing natural classes in a
    FieldWorks project.

    Natural classes are groups of phonemes that share common phonological
    features and pattern together in phonological rules. For example,
    voiceless stops {/p/, /t/, /k/} or vowels {/a/, /e/, /i/, /o/, /u/}.

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get all natural classes
        for nc in project.NaturalClasses.GetAll():
            name = project.NaturalClasses.GetName(nc)
            abbr = project.NaturalClasses.GetAbbreviation(nc)
            phonemes = project.NaturalClasses.GetPhonemes(nc)
            print(f"{name} ({abbr}): {len(phonemes)} phonemes")

        # Create a new natural class
        stops = project.NaturalClasses.Create("Voiceless Stops", "VLS")

        # Add phonemes to the class
        p_phoneme = project.Phonemes.Find("/p/")
        if p_phoneme:
            project.NaturalClasses.AddPhoneme(stops, p_phoneme)

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize NaturalClassOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)


    def _GetSequence(self, parent):
        """
        Specify which sequence to reorder for natural classes.
        For NaturalClass, we reorder parent.SubPossibilitiesOS
        """
        return parent.SubPossibilitiesOS

    def __WSHandle(self, wsHandle):
        """
        Internal helper for writing system handles (analysis).

        Args:
            wsHandle: Writing system handle or None for default analysis WS.

        Returns:
            int: The writing system handle to use.
        """
        if wsHandle is None:
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultAnalWs)

    def __GetNaturalClassObject(self, nc_or_hvo):
        """
        Internal helper to get natural class object from HVO or object.

        Args:
            nc_or_hvo: IPhNaturalClass object or HVO integer.

        Returns:
            IPhNaturalClass: The natural class object.
        """
        if isinstance(nc_or_hvo, int):
            return self.project.Object(nc_or_hvo)
        return nc_or_hvo

    def __GetPhonemeObject(self, phoneme_or_hvo):
        """
        Internal helper to get phoneme object from HVO or object.

        Args:
            phoneme_or_hvo: IPhPhoneme object or HVO integer.

        Returns:
            IPhPhoneme: The phoneme object.
        """
        if isinstance(phoneme_or_hvo, int):
            return self.project.Object(phoneme_or_hvo)
        return phoneme_or_hvo

    def GetAll(self):
        """
        Get all natural classes in the phonological inventory.

        Yields:
            IPhNaturalClass: Each natural class in the project.

        Example:
            >>> for nc in project.NaturalClasses.GetAll():
            ...     name = project.NaturalClasses.GetName(nc)
            ...     abbr = project.NaturalClasses.GetAbbreviation(nc)
            ...     phonemes = project.NaturalClasses.GetPhonemes(nc)
            ...     print(f"{name} ({abbr}): {len(phonemes)} phonemes")
            Voiceless Stops (VLS): 3 phonemes
            Voiced Stops (VCD): 3 phonemes
            Nasals (N): 3 phonemes
            Vowels (V): 5 phonemes

        Notes:
            - Returns natural classes in their defined order
            - Includes both segment-based and feature-based classes
            - Empty if no natural classes defined

        See Also:
            Create, GetName, GetPhonemes
        """
        phon_data = self.project.lp.PhonologicalDataOA
        if phon_data:
            natural_classes = list(phon_data.NaturalClassesOS)
            for nc in natural_classes:
                yield nc

    def Create(self, name, abbreviation=None):
        """
        Create a new natural class.

        Args:
            name (str): The name of the natural class (e.g., "Voiceless Stops").
            abbreviation (str, optional): Short abbreviation (e.g., "VLS", "V", "C").
                If None, defaults to empty string.

        Returns:
            IPhNCSegments: The newly created natural class object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> # Create basic consonant classes
            >>> stops = project.NaturalClasses.Create("Stops", "P")
            >>> fricatives = project.NaturalClasses.Create("Fricatives", "F")
            >>> nasals = project.NaturalClasses.Create("Nasals", "N")

            >>> # Create vowel classes
            >>> vowels = project.NaturalClasses.Create("Vowels", "V")
            >>> high_vowels = project.NaturalClasses.Create("High Vowels", "HV")

            >>> # Create without abbreviation
            >>> custom_class = project.NaturalClasses.Create("Custom Class")

        Notes:
            - Name should be descriptive of the phonological property
            - Abbreviation is used in rule notation (e.g., V → Ø / _C#)
            - After creation, use AddPhoneme() to add members
            - Creates a segment-based natural class (IPhNCSegments)

        See Also:
            Delete, AddPhoneme, SetName, SetAbbreviation
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        # Get the writing system handle
        wsHandle = self.project.project.DefaultAnalWs

        # Create the new natural class using the factory
        factory = self.project.project.ServiceLocator.GetService(IPhNCSegmentsFactory)
        nc = factory.Create()

        # Add to the natural classes collection (must be done before setting properties)
        phon_data = self.project.lp.PhonologicalDataOA
        phon_data.NaturalClassesOS.Add(nc)

        # Set name
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        nc.Name.set_String(wsHandle, mkstr_name)

        # Set abbreviation if provided
        if abbreviation:
            mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
            nc.Abbreviation.set_String(wsHandle, mkstr_abbr)

        return nc

    def Delete(self, nc_or_hvo):
        """
        Delete a natural class.

        Args:
            nc_or_hvo: The IPhNaturalClass object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If nc_or_hvo is None.

        Example:
            >>> obsolete = project.NaturalClasses.Create("Obsolete", "OBS")
            >>> # ... realize it's not needed
            >>> project.NaturalClasses.Delete(obsolete)

        Warning:
            - Deleting a natural class that is in use may cause errors
            - This includes natural classes used in:
              - Phonological rules
              - Phonological environments
              - Other natural class definitions
            - Deletion is permanent and cannot be undone
            - Does not delete the phonemes in the class, only the class itself

        See Also:
            Create, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not nc_or_hvo:
            raise FP_NullParameterError()

        # Resolve to natural class object
        nc = self.__GetNaturalClassObject(nc_or_hvo)

        # Remove from the natural classes collection
        phon_data = self.project.lp.PhonologicalDataOA
        phon_data.NaturalClassesOS.Remove(nc)


    def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
        """
        Duplicate a natural class, creating a new copy with a new GUID.

        Args:
            item_or_hvo: The IPhNaturalClass object or HVO to duplicate.
            insert_after (bool): If True (default), insert after the source natural class.
                                If False, insert at end of natural classes list.
            deep (bool): If True, also duplicate owned objects (if any exist).
                        If False (default), only copy simple properties and references.
                        Note: NaturalClass has no owned objects, so deep has no effect.

        Returns:
            IPhNCSegments: The newly created duplicate natural class with a new GUID.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> ncOps = NaturalClassOperations(project)
            >>> stops = ncOps.Create("Voiceless Stops", "VLS")
            >>> # Add some phonemes...
            >>> # Now duplicate it to create "Voiced Stops"
            >>> voiced = ncOps.Duplicate(stops)
            >>> ncOps.SetName(voiced, "Voiced Stops")
            >>> ncOps.SetAbbreviation(voiced, "VCD")
            >>> print(f"Original: {ncOps.GetGuid(stops)}")
            >>> print(f"Duplicate: {ncOps.GetGuid(voiced)}")
            Original: 12345678-1234-1234-1234-123456789abc
            Duplicate: 87654321-4321-4321-4321-cba987654321

        Notes:
            - Factory.Create() automatically generates a new GUID
            - insert_after=True preserves the original class's position
            - Simple properties copied: Name, Abbreviation, Description
            - Reference properties copied: SegmentsRC (phoneme members)
            - NaturalClass has no owned objects, so deep parameter has no effect
            - Useful for creating similar natural classes (e.g., voiced/voiceless pairs)
            - Segment references are shallow copied - both classes reference same phonemes

        See Also:
            Create, Delete, GetGuid, AddPhoneme
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not item_or_hvo:
            raise FP_NullParameterError()

        # Get source natural class
        source = self.__GetNaturalClassObject(item_or_hvo)
        phon_data = self.project.lp.PhonologicalDataOA

        # Create new natural class using factory (auto-generates new GUID)
        factory = self.project.project.ServiceLocator.GetService(IPhNCSegmentsFactory)
        duplicate = factory.Create()

        # Determine insertion position
        if insert_after:
            # Insert after source natural class
            source_index = list(phon_data.NaturalClassesOS).index(source)
            phon_data.NaturalClassesOS.Insert(source_index + 1, duplicate)
        else:
            # Insert at end
            phon_data.NaturalClassesOS.Add(duplicate)

        # Copy simple MultiString properties
        duplicate.Name.CopyAlternatives(source.Name)
        duplicate.Abbreviation.CopyAlternatives(source.Abbreviation)
        duplicate.Description.CopyAlternatives(source.Description)

        # Copy Reference Collection (RC) properties - phoneme members
        if hasattr(source, 'SegmentsRC'):
            for phoneme in source.SegmentsRC:
                duplicate.SegmentsRC.Add(phoneme)

        # Note: NaturalClass has no owned objects (OS collections), so deep has no effect

        return duplicate

    def GetName(self, nc_or_hvo, wsHandle=None):
        """
        Get the name of a natural class.

        Args:
            nc_or_hvo: The IPhNaturalClass object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The natural class name, or empty string if not set.

        Raises:
            FP_NullParameterError: If nc_or_hvo is None.

        Example:
            >>> for nc in project.NaturalClasses.GetAll():
            ...     name = project.NaturalClasses.GetName(nc)
            ...     print(name)
            Voiceless Stops
            Voiced Stops
            Fricatives
            Nasals
            Vowels

        See Also:
            SetName, GetAbbreviation
        """
        if not nc_or_hvo:
            raise FP_NullParameterError()

        nc = self.__GetNaturalClassObject(nc_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(nc.Name.get_String(wsHandle)).Text
        return name or ""

    def SetName(self, nc_or_hvo, name, wsHandle=None):
        """
        Set the name of a natural class.

        Args:
            nc_or_hvo: The IPhNaturalClass object or HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If nc_or_hvo or name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> nc = project.NaturalClasses.Create("Plosives", "P")
            >>> # Prefer linguistic standard terminology
            >>> project.NaturalClasses.SetName(nc, "Stops")

        Notes:
            - Use standard phonological terminology
            - Name should reflect the shared phonological property

        See Also:
            GetName, SetAbbreviation
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not nc_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        nc = self.__GetNaturalClassObject(nc_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        nc.Name.set_String(wsHandle, mkstr)

    def GetAbbreviation(self, nc_or_hvo, wsHandle=None):
        """
        Get the abbreviation of a natural class.

        Args:
            nc_or_hvo: The IPhNaturalClass object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The natural class abbreviation, or empty string if not set.

        Raises:
            FP_NullParameterError: If nc_or_hvo is None.

        Example:
            >>> nc = project.NaturalClasses.Create("Voiceless Stops", "VLS")
            >>> abbr = project.NaturalClasses.GetAbbreviation(nc)
            >>> print(abbr)
            VLS

            >>> # Print rule using abbreviations
            >>> # Rule: VLS → VCD / V_V (voicing between vowels)
            >>> vls = project.NaturalClasses.Find("Voiceless Stops")
            >>> vcd = project.NaturalClasses.Find("Voiced Stops")
            >>> v = project.NaturalClasses.Find("Vowels")
            >>> if vls and vcd and v:
            ...     vls_abbr = project.NaturalClasses.GetAbbreviation(vls)
            ...     vcd_abbr = project.NaturalClasses.GetAbbreviation(vcd)
            ...     v_abbr = project.NaturalClasses.GetAbbreviation(v)
            ...     print(f"{vls_abbr} → {vcd_abbr} / {v_abbr}_{v_abbr}")
            VLS → VCD / V_V

        Notes:
            - Abbreviations are used in phonological rule notation
            - Standard abbreviations: V (vowel), C (consonant), N (nasal), etc.
            - Keep abbreviations short and mnemonic

        See Also:
            GetName, SetAbbreviation
        """
        if not nc_or_hvo:
            raise FP_NullParameterError()

        nc = self.__GetNaturalClassObject(nc_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        abbr = ITsString(nc.Abbreviation.get_String(wsHandle)).Text
        return abbr or ""

    def GetPhonemes(self, nc_or_hvo):
        """
        Get all phonemes in a natural class.

        Args:
            nc_or_hvo: The IPhNaturalClass object or HVO.

        Returns:
            list: List of IPhPhoneme objects in the class (empty list if none).

        Raises:
            FP_NullParameterError: If nc_or_hvo is None.

        Example:
            >>> # Get members of voiceless stops
            >>> for nc in project.NaturalClasses.GetAll():
            ...     name = project.NaturalClasses.GetName(nc)
            ...     if name == "Voiceless Stops":
            ...         phonemes = project.NaturalClasses.GetPhonemes(nc)
            ...         for phoneme in phonemes:
            ...             print(project.Phonemes.GetRepresentation(phoneme))
            /p/
            /t/
            /k/

            >>> # Print all natural classes with their members
            >>> for nc in project.NaturalClasses.GetAll():
            ...     name = project.NaturalClasses.GetName(nc)
            ...     phonemes = project.NaturalClasses.GetPhonemes(nc)
            ...     count = len(phonemes)
            ...     print(f"{name}: {count} phonemes")
            Voiceless Stops: 3 phonemes
            Voiced Stops: 3 phonemes
            Nasals: 3 phonemes

        Notes:
            - Returns empty list if class is feature-based without explicit segments
            - For segment-based classes (IPhNCSegments), returns SegmentsRC
            - Order is as defined in the natural class
            - Changes to returned list do not affect the natural class

        See Also:
            AddPhoneme, RemovePhoneme
        """
        if not nc_or_hvo:
            raise FP_NullParameterError()

        nc = self.__GetNaturalClassObject(nc_or_hvo)

        # Check if it's a segment-based natural class
        if hasattr(nc, 'SegmentsRC'):
            return list(nc.SegmentsRC)
        return []

    def AddPhoneme(self, nc_or_hvo, phoneme_or_hvo):
        """
        Add a phoneme to a natural class.

        Args:
            nc_or_hvo: The IPhNaturalClass object or HVO.
            phoneme_or_hvo: The IPhPhoneme object or HVO to add.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If nc_or_hvo or phoneme_or_hvo is None.
            FP_ParameterError: If the natural class is feature-based (cannot add segments).

        Example:
            >>> # Create voiceless stops class
            >>> nc = project.NaturalClasses.Create("Voiceless Stops", "VLS")
            >>> p = project.Phonemes.Find("/p/")
            >>> t = project.Phonemes.Find("/t/")
            >>> k = project.Phonemes.Find("/k/")
            >>> if p:
            ...     project.NaturalClasses.AddPhoneme(nc, p)
            >>> if t:
            ...     project.NaturalClasses.AddPhoneme(nc, t)
            >>> if k:
            ...     project.NaturalClasses.AddPhoneme(nc, k)

            >>> # Create vowel class
            >>> vowels = project.NaturalClasses.Create("Vowels", "V")
            >>> for repr in ["/a/", "/e/", "/i/", "/o/", "/u/"]:
            ...     phoneme = project.Phonemes.Find(repr)
            ...     if phoneme:
            ...         project.NaturalClasses.AddPhoneme(vowels, phoneme)

        Notes:
            - Only works with segment-based natural classes (IPhNCSegments)
            - A phoneme can belong to multiple natural classes
            - Duplicate additions are typically ignored
            - For feature-based classes, define features instead

        See Also:
            RemovePhoneme, GetPhonemes, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not nc_or_hvo:
            raise FP_NullParameterError()
        if not phoneme_or_hvo:
            raise FP_NullParameterError()

        nc = self.__GetNaturalClassObject(nc_or_hvo)
        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)

        # Check if it's a segment-based natural class
        if not hasattr(nc, 'SegmentsRC'):
            raise FP_ParameterError(
                "Cannot add phoneme to feature-based natural class"
            )

        # Add the phoneme if not already present
        if phoneme not in nc.SegmentsRC:
            nc.SegmentsRC.Add(phoneme)

    def RemovePhoneme(self, nc_or_hvo, phoneme_or_hvo):
        """
        Remove a phoneme from a natural class.

        Args:
            nc_or_hvo: The IPhNaturalClass object or HVO.
            phoneme_or_hvo: The IPhPhoneme object or HVO to remove.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If nc_or_hvo or phoneme_or_hvo is None.
            FP_ParameterError: If the natural class is feature-based or if
                the phoneme is not in the natural class.

        Example:
            >>> # Remove /q/ from uvular stops if reclassified
            >>> for nc in project.NaturalClasses.GetAll():
            ...     if project.NaturalClasses.GetName(nc) == "Uvular Stops":
            ...         q_phoneme = project.Phonemes.Find("/q/")
            ...         if q_phoneme and q_phoneme in project.NaturalClasses.GetPhonemes(nc):
            ...             project.NaturalClasses.RemovePhoneme(nc, q_phoneme)

            >>> # Clean up natural class
            >>> for nc in project.NaturalClasses.GetAll():
            ...     if project.NaturalClasses.GetName(nc) == "Obsolete Phonemes":
            ...         phonemes = project.NaturalClasses.GetPhonemes(nc)
            ...         for phoneme in phonemes:
            ...             project.NaturalClasses.RemovePhoneme(nc, phoneme)

        Notes:
            - Only works with segment-based natural classes
            - Phoneme must be in the class's SegmentsRC collection
            - Use GetPhonemes() to check membership first

        See Also:
            AddPhoneme, GetPhonemes
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not nc_or_hvo:
            raise FP_NullParameterError()
        if not phoneme_or_hvo:
            raise FP_NullParameterError()

        nc = self.__GetNaturalClassObject(nc_or_hvo)
        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)

        # Check if it's a segment-based natural class
        if not hasattr(nc, 'SegmentsRC'):
            raise FP_ParameterError(
                "Cannot remove phoneme from feature-based natural class"
            )

        # Check if phoneme is in the collection
        if phoneme not in nc.SegmentsRC:
            raise FP_ParameterError("Phoneme not found in natural class")

        # Remove the phoneme
        nc.SegmentsRC.Remove(phoneme)
