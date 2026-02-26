#
#   PhonemeOperations.py
#
#   Class: PhonemeOperations
#          Phoneme operations for FieldWorks Language Explorer
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
    IPhPhoneme,
    IPhPhonemeFactory,
    IPhCode,
    IPhCodeFactory,
    IFsFeatStruc,
    ICmObjectRepository,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils


# Import flexlibs exceptions
from ..FLExProject import (
    FP_ParameterError,
)

# Import string utilities
from ..Shared.string_utils import normalize_text

class PhonemeOperations(BaseOperations):
    """
    This class provides operations for managing Phonemes in a FieldWorks project.

    Phonemes are the minimal distinctive units of sound in a language. For example,
    in English, /p/ and /b/ are distinct phonemes because they distinguish words
    like "pat" and "bat".

    Usage::

        from flexlibs2 import FLExProject, PhonemeOperations

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        phonemeOps = PhonemeOperations(project)

        # Get all phonemes
        for phoneme in phonemeOps.GetAll():
            print(phonemeOps.GetRepresentation(phoneme))

        # Create a new phoneme
        p_phoneme = phonemeOps.Create("/p/")
        phonemeOps.SetDescription(p_phoneme, "voiceless bilabial stop")

        # Find and update
        b_phoneme = phonemeOps.Find("/b/")
        if b_phoneme:
            phonemeOps.SetDescription(b_phoneme, "voiced bilabial stop")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize PhonemeOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)

    def _GetSequence(self, parent):
        """
        Specify which sequence to reorder for phonemes.
        For Phoneme, we reorder parent.PhonemesOS
        """
        return parent.PhonemesOS

    def GetAll(self):
        """
        Get all phonemes in the project.

        Yields:
            IPhPhoneme: Each phoneme object in the project's phoneme inventory.

        Example:
            >>> phonemeOps = PhonemeOperations(project)
            >>> for phoneme in phonemeOps.GetAll():
            ...     representation = phonemeOps.GetRepresentation(phoneme)
            ...     description = phonemeOps.GetDescription(phoneme)
            ...     print(f"{representation}: {description}")
            /p/: voiceless bilabial stop
            /b/: voiced bilabial stop
            /t/: voiceless alveolar stop
            /d/: voiced alveolar stop

        Notes:
            - Returns phonemes from the first phoneme set
            - Returns empty if no phoneme sets exist
            - Most projects have only one phoneme set
            - Phonemes include both consonants and vowels

        See Also:
            Find, GetRepresentation
        """
        phon_data = self.project.lp.PhonologicalDataOA
        if phon_data and phon_data.PhonemeSetsOS.Count > 0:
            phoneme_set = phon_data.PhonemeSetsOS[0]
            for phoneme in phoneme_set.PhonemesOC:
                yield phoneme

    def Create(self, representation, wsHandle=None):
        """
        Create a new phoneme.

        Args:
            representation (str): The phonemic representation (e.g., "/p/", "/a/").
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            IPhPhoneme: The newly created phoneme object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If representation is None.
            FP_ParameterError: If representation is empty, or if a phoneme
                with this representation already exists, or if no phoneme set exists.

        Example:
            >>> phonemeOps = PhonemeOperations(project)
            >>> p_phoneme = phonemeOps.Create("/p/")
            >>> print(phonemeOps.GetRepresentation(p_phoneme))
            /p/

            >>> # Create with description
            >>> ch_phoneme = phonemeOps.Create("/tʃ/")
            >>> phonemeOps.SetDescription(ch_phoneme, "voiceless postalveolar affricate")

        Notes:
            - Representation should use IPA symbols
            - Standard convention is to enclose in slashes: /p/
            - Phoneme must be unique within the phoneme set
            - Requires at least one phoneme set to exist in the project

        See Also:
            Delete, Exists, Find
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(representation, "representation")

        if not representation or not representation.strip():
            raise FP_ParameterError("Representation cannot be empty")

        # Check if phoneme already exists
        if self.Exists(representation, wsHandle):
            raise FP_ParameterError(f"Phoneme '{representation}' already exists")

        # Get or create phoneme set
        phon_data = self.project.lp.PhonologicalDataOA
        if not phon_data:
            raise FP_ParameterError("No phonological data in project")

        if phon_data.PhonemeSetsOS.Count == 0:
            raise FP_ParameterError("No phoneme set exists in project")

        phoneme_set = phon_data.PhonemeSetsOS[0]

        # Get the writing system handle
        wsHandle = self.__WSHandle(wsHandle)

        # Create the new phoneme using the factory
        factory = self.project.project.ServiceLocator.GetService(IPhPhonemeFactory)
        new_phoneme = factory.Create()

        # Set representation
        mkstr = TsStringUtils.MakeString(representation, wsHandle)
        new_phoneme.Name.set_String(wsHandle, mkstr)

        # Add to the phoneme set
        phoneme_set.PhonemesOC.Add(new_phoneme)

        return new_phoneme

    def Delete(self, phoneme_or_hvo):
        """
        Delete a phoneme.

        Args:
            phoneme_or_hvo: The IPhPhoneme object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If phoneme_or_hvo is None.
            FP_ParameterError: If the phoneme is in use and cannot be deleted.

        Example:
            >>> phonemeOps = PhonemeOperations(project)
            >>> obsolete = phonemeOps.Find("/x/")
            >>> if obsolete:
            ...     phonemeOps.Delete(obsolete)

        Warning:
            - Deleting a phoneme that is in use may raise an error from FLEx
            - This includes phonemes used in:
              - Natural classes
              - Phonological rules
              - Allomorph environments
            - Deletion is permanent and cannot be undone
            - Consider updating references before deletion

        See Also:
            Create, Exists, Find
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(phoneme_or_hvo, "phoneme_or_hvo")

        # Resolve to phoneme object
        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)

        # Get phoneme set and remove
        phon_data = self.project.lp.PhonologicalDataOA
        if phon_data and phon_data.PhonemeSetsOS.Count > 0:
            phoneme_set = phon_data.PhonemeSetsOS[0]
            phoneme_set.PhonemesOC.Remove(phoneme)

    def Duplicate(self, item_or_hvo, insert_after=True, deep=True):
        """
        Duplicate a phoneme, creating a new copy with a new GUID.

        Args:
            item_or_hvo: The IPhPhoneme object or HVO to duplicate.
            insert_after (bool): If True (default), insert after the source phoneme.
                                If False, insert at end of phoneme set.
            deep (bool): If True (default), also duplicate owned objects (codes/allophones).
                        If False, only copy simple properties and references.

        Returns:
            IPhPhoneme: The newly created duplicate phoneme with a new GUID.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If no phoneme set exists.

        Example:
            >>> phonemeOps = PhonemeOperations(project)
            >>> p_phoneme = phonemeOps.Find("/p/")
            >>> if p_phoneme:
            ...     # Duplicate phoneme (deep - includes allophonic codes)
            ...     dup = phonemeOps.Duplicate(p_phoneme)
            ...     print(f"Original: {phonemeOps.GetGuid(dup)}")
            ...     print(f"Representation: {phonemeOps.GetRepresentation(dup)}")
            ...
            ...     # Shallow duplicate (no codes)
            ...     shallow_dup = phonemeOps.Duplicate(p_phoneme, deep=False)
            ...     codes = phonemeOps.GetCodes(deep_dup)
            ...     print(f"Codes: {len(codes)}")

        Notes:
            - Factory.Create() automatically generates a new GUID
            - insert_after=True preserves the original phoneme's position
            - Simple properties copied: Name (representation), Description, BasicIPASymbol
            - Reference properties copied: FeaturesOA (feature structure reference)
            - Owned objects (deep=True): CodesOS (allophonic representations)
            - Useful for creating similar phonemes or phoneme variants

        See Also:
            Create, Delete, GetGuid, GetCodes
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(item_or_hvo, "item_or_hvo")

        # Get source phoneme
        source = self.__GetPhonemeObject(item_or_hvo)

        # Get phoneme set
        phon_data = self.project.lp.PhonologicalDataOA
        if not phon_data or phon_data.PhonemeSetsOS.Count == 0:
            raise FP_ParameterError("No phoneme set exists in project")
        phoneme_set = phon_data.PhonemeSetsOS[0]

        # Create new phoneme using factory (auto-generates new GUID)
        factory = self.project.project.ServiceLocator.GetService(IPhPhonemeFactory)
        duplicate = factory.Create()

        # Add to phoneme set (OC types use Add only, no Insert)
        phoneme_set.PhonemesOC.Add(duplicate)

        # Copy simple MultiString properties
        duplicate.Name.CopyAlternatives(source.Name)
        duplicate.Description.CopyAlternatives(source.Description)
        if hasattr(source, 'BasicIPASymbol') and source.BasicIPASymbol:
            duplicate.BasicIPASymbol.CopyAlternatives(source.BasicIPASymbol)

        # Note: FeaturesOA is an owned atomic object (OA), NOT a reference.
        # Assigning it directly would TRANSFER ownership from source, corrupting it.
        # Feature structures are complex (recursive), so we skip them in shallow
        # copy and handle via deep copy below using LCM's SetCloneProperties.

        # Handle owned objects if deep=True
        if deep:
            # Deep copy FeaturesOA using SetCloneProperties
            if hasattr(source, 'FeaturesOA') and source.FeaturesOA:
                # Create new feature structure and copy all properties
                try:
                    source_features = source.FeaturesOA
                    # Create new object of same type
                    new_features = self.project.project.ServiceLocator.ObjectRepository.NewObject(
                        source_features.ClassID)

                    # Set as the feature structure for this phoneme
                    duplicate.FeaturesOA = new_features

                    # Copy all properties using SetCloneProperties if available
                    if hasattr(source_features, 'SetCloneProperties'):
                        source_features.SetCloneProperties(new_features)
                except Exception:
                    # Cannot copy complex feature structure - skip
                    pass

            # Duplicate codes (allophonic representations)
            for code in source.CodesOS:
                code_factory = self.project.project.ServiceLocator.GetService(IPhCodeFactory)
                new_code = code_factory.Create()
                duplicate.CodesOS.Add(new_code)
                # Copy code properties
                new_code.Representation.CopyAlternatives(code.Representation)

        return duplicate

    def Exists(self, representation, wsHandle=None):
        """
        Check if a phoneme with the given representation exists.

        Args:
            representation (str): The representation to search for (case-sensitive).
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            bool: True if phoneme exists, False otherwise.

        Raises:
            FP_NullParameterError: If representation is None.

        Example:
            >>> phonemeOps = PhonemeOperations(project)
            >>> if not phonemeOps.Exists("/ŋ/"):
            ...     phonemeOps.Create("/ŋ/")
            ...     phonemeOps.SetDescription(phonemeOps.Find("/ŋ/"), "velar nasal")

        Notes:
            - Comparison is case-sensitive (IPA is case-sensitive)
            - Use Find() to get the actual object

        See Also:
            Find, Create
        """
        self._ValidateParam(representation, "representation")

        return self.Find(representation, wsHandle) is not None

    def Find(self, representation, wsHandle=None):
        """
        Find a phoneme by representation.

        Args:
            representation (str): The representation to search for (case-sensitive).
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            IPhPhoneme or None: The phoneme object if found, None otherwise.

        Raises:
            FP_NullParameterError: If representation is None.

        Example:
            >>> phonemeOps = PhonemeOperations(project)
            >>> p_phoneme = phonemeOps.Find("/p/")
            >>> if p_phoneme:
            ...     desc = phonemeOps.GetDescription(p_phoneme)
            ...     print(f"/p/: {desc}")
            /p/: voiceless bilabial stop

        Notes:
            - Returns first match only
            - Search is case-sensitive (IPA is case-sensitive)
            - Returns None if not found (doesn't raise exception)

        See Also:
            Exists, GetRepresentation
        """
        self._ValidateParam(representation, "representation")

        wsHandle = self.__WSHandle(wsHandle)

        phon_data = self.project.lp.PhonologicalDataOA
        if not phon_data or phon_data.PhonemeSetsOS.Count == 0:
            return None

        phoneme_set = phon_data.PhonemeSetsOS[0]
        for phoneme in phoneme_set.PhonemesOC:
            phoneme_repr = normalize_text(ITsString(phoneme.Name.get_String(wsHandle)).Text)
            if phoneme_repr == representation:
                return phoneme

        return None

    def GetRepresentation(self, phoneme_or_hvo, wsHandle=None):
        """
        Get the representation of a phoneme.

        Args:
            phoneme_or_hvo: The IPhPhoneme object or HVO.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            str: The phoneme representation, or empty string if not set.

        Raises:
            FP_NullParameterError: If phoneme_or_hvo is None.

        Example:
            >>> phonemeOps = PhonemeOperations(project)
            >>> p_phoneme = phonemeOps.Find("/p/")
            >>> representation = phonemeOps.GetRepresentation(p_phoneme)
            >>> print(representation)
            /p/

            >>> # Iterate and print all phonemes
            >>> for phoneme in phonemeOps.GetAll():
            ...     print(phonemeOps.GetRepresentation(phoneme))

        See Also:
            SetRepresentation, GetDescription
        """
        self._ValidateParam(phoneme_or_hvo, "phoneme_or_hvo")

        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        representation = normalize_text(ITsString(phoneme.Name.get_String(wsHandle)).Text)
        return representation or ""

    def SetRepresentation(self, phoneme_or_hvo, representation, wsHandle=None):
        """
        Set the representation of a phoneme.

        Args:
            phoneme_or_hvo: The IPhPhoneme object or HVO.
            representation (str): The new representation.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If phoneme_or_hvo or representation is None.
            FP_ParameterError: If representation is empty.

        Example:
            >>> phonemeOps = PhonemeOperations(project)
            >>> phoneme = phonemeOps.Find("/ph/")  # non-standard notation
            >>> if phoneme:
            ...     phonemeOps.SetRepresentation(phoneme, "/pʰ/")  # fix to proper IPA

        Notes:
            - Use standard IPA symbols for cross-linguistic compatibility
            - Consider updating descriptions when changing representation

        See Also:
            GetRepresentation, SetDescription
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(phoneme_or_hvo, "phoneme_or_hvo")
        self._ValidateParam(representation, "representation")

        if not representation or not representation.strip():
            raise FP_ParameterError("Representation cannot be empty")

        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(representation, wsHandle)
        phoneme.Name.set_String(wsHandle, mkstr)

    def GetDescription(self, phoneme_or_hvo, wsHandle=None):
        """
        Get the description of a phoneme.

        Args:
            phoneme_or_hvo: The IPhPhoneme object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The phoneme description, or empty string if not set.

        Raises:
            FP_NullParameterError: If phoneme_or_hvo is None.

        Example:
            >>> phonemeOps = PhonemeOperations(project)
            >>> p_phoneme = phonemeOps.Find("/p/")
            >>> desc = phonemeOps.GetDescription(p_phoneme)
            >>> print(desc)
            voiceless bilabial stop

            >>> # Print phoneme inventory with descriptions
            >>> for phoneme in phonemeOps.GetAll():
            ...     repr = phonemeOps.GetRepresentation(phoneme)
            ...     desc = phonemeOps.GetDescription(phoneme)
            ...     print(f"{repr}: {desc}")
            /p/: voiceless bilabial stop
            /b/: voiced bilabial stop
            /t/: voiceless alveolar stop

        Notes:
            - Description typically includes articulatory features
            - Returns empty string if no description set
            - Uses analysis writing system by default (not vernacular)

        See Also:
            SetDescription, GetRepresentation
        """
        self._ValidateParam(phoneme_or_hvo, "phoneme_or_hvo")

        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)

        # Use analysis WS for description (not vernacular)
        if wsHandle is None:
            wsHandle = self.project.project.DefaultAnalWs
        else:
            wsHandle = self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultAnalWs)

        desc_str = ITsString(phoneme.Description.get_String(wsHandle)).Text
        return desc_str or ""

    def SetDescription(self, phoneme_or_hvo, description, wsHandle=None):
        """
        Set the description of a phoneme.

        Args:
            phoneme_or_hvo: The IPhPhoneme object or HVO.
            description (str): The new description.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If phoneme_or_hvo or description is None.

        Example:
            >>> phonemeOps = PhonemeOperations(project)
            >>> p_phoneme = phonemeOps.Create("/p/")
            >>> phonemeOps.SetDescription(p_phoneme, "voiceless bilabial stop")

            >>> # Add detailed articulatory description
            >>> tap = phonemeOps.Find("/ɾ/")
            >>> phonemeOps.SetDescription(
            ...     tap,
            ...     "voiced alveolar tap/flap - allophone of /r/ in intervocalic position"
            ... )

        Notes:
            - Description is optional but recommended for documentation
            - Use standard phonetic terminology
            - Can include information about allophones and distribution
            - Uses analysis writing system by default (not vernacular)
            - Description can be empty string to clear

        See Also:
            GetDescription, SetRepresentation
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(phoneme_or_hvo, "phoneme_or_hvo")
        self._ValidateParam(description, "description")

        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)

        # Use analysis WS for description (not vernacular)
        if wsHandle is None:
            wsHandle = self.project.project.DefaultAnalWs
        else:
            wsHandle = self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultAnalWs)

        mkstr = TsStringUtils.MakeString(description, wsHandle)
        phoneme.Description.set_String(wsHandle, mkstr)

    def GetFeatures(self, phoneme_or_hvo):
        """
        Get the feature structure of a phoneme.

        Args:
            phoneme_or_hvo: The IPhPhoneme object or HVO.

        Returns:
            IFsFeatStruc or None: The phoneme's feature structure, or None if not set.

        Raises:
            FP_NullParameterError: If phoneme_or_hvo is None.

        Example:
            >>> phonemeOps = PhonemeOperations(project)
            >>> p_phoneme = phonemeOps.Find("/p/")
            >>> features = phonemeOps.GetFeatures(p_phoneme)
            >>> if features:
            ...     print(f"Feature structure: {features.Hvo}")
            ... else:
            ...     print("No features defined")

        Notes:
            - Feature structures define distinctive phonological properties
            - Used in phonological rules and natural class definitions
            - Feature system must be defined in project settings
            - Returns None if no features are set
            - Returns the IFsFeatStruc object for further manipulation

        See Also:
            GetRepresentation, GetDescription
        """
        self._ValidateParam(phoneme_or_hvo, "phoneme_or_hvo")

        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)
        return phoneme.FeaturesOA if phoneme.FeaturesOA else None

    # --- Advanced Operations ---

    def GetCodes(self, phoneme_or_hvo):
        """
        Get all codes (allophonic representations) for a phoneme.

        Args:
            phoneme_or_hvo: The IPhPhoneme object or HVO.

        Returns:
            list: List of IPhCode objects (empty list if none).

        Raises:
            FP_NullParameterError: If phoneme_or_hvo is None.

        Example:
            >>> # Get allophones of /t/
            >>> phoneme = project.Phonemes.Find("/t/")
            >>> if phoneme:
            ...     codes = project.Phonemes.GetCodes(phoneme)
            ...     for code in codes:
            ...         ws = project.project.DefaultVernWs
            ...         repr = ITsString(code.Representation.get_String(ws)).Text
            ...         print(repr)
            [t]   # plain voiceless alveolar stop
            [tʰ]  # aspirated (word-initial)
            [ɾ]   # flap (intervocalic)

            >>> # Get vowel allophones
            >>> phoneme = project.Phonemes.Find("/i/")
            >>> if phoneme:
            ...     codes = project.Phonemes.GetCodes(phoneme)
            ...     print(f"Phoneme /i/ has {len(codes)} allophonic codes")

        Notes:
            - Codes represent allophones or context-specific realizations
            - Convention is to use square brackets [p] for phones
            - Slashes /p/ for phonemes
            - Empty list if no codes defined

        See Also:
            AddCode, RemoveCode
        """
        self._ValidateParam(phoneme_or_hvo, "phoneme_or_hvo")

        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)
        return list(phoneme.CodesOS)

    def AddCode(self, phoneme_or_hvo, representation, wsHandle=None):
        """
        Add a code (allophonic representation) to a phoneme.

        Args:
            phoneme_or_hvo: The IPhPhoneme object or HVO.
            representation: The code representation (e.g., "[tʰ]", "[ɾ]").
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            IPhCode: The newly created code object.

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If phoneme_or_hvo or representation is None.
            FP_ParameterError: If representation is empty.

        Example:
            >>> # Add aspiration allophone
            >>> phoneme = project.Phonemes.Find("/p/")
            >>> if phoneme:
            ...     code = project.Phonemes.AddCode(phoneme, "[pʰ]")

            >>> # Add multiple allophones for /t/
            >>> phoneme = project.Phonemes.Find("/t/")
            >>> if phoneme:
            ...     project.Phonemes.AddCode(phoneme, "[t]")   # plain
            ...     project.Phonemes.AddCode(phoneme, "[tʰ]")  # aspirated
            ...     project.Phonemes.AddCode(phoneme, "[ɾ]")   # flap

            >>> # Add vowel allophones
            >>> phoneme = project.Phonemes.Find("/a/")
            >>> if phoneme:
            ...     project.Phonemes.AddCode(phoneme, "[a]")   # open front
            ...     project.Phonemes.AddCode(phoneme, "[ɑ]")   # open back

        Notes:
            - Use square brackets [p] for phones (allophones)
            - Each code can have its own feature specifications
            - Codes are used in phonological rule environments
            - Duplicates are allowed (same code can be added multiple times)

        See Also:
            GetCodes, RemoveCode
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(phoneme_or_hvo, "phoneme_or_hvo")
        self._ValidateParam(representation, "representation")

        if not representation or not representation.strip():
            raise FP_ParameterError("Representation cannot be empty")

        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Create the new code using the factory
        factory = self.project.project.ServiceLocator.GetService(IPhCodeFactory)
        code = factory.Create()

        # Add to phoneme's codes (must be done before setting properties)
        phoneme.CodesOS.Add(code)

        # Set representation
        mkstr = TsStringUtils.MakeString(representation, wsHandle)
        code.Representation.set_String(wsHandle, mkstr)

        return code

    def RemoveCode(self, phoneme_or_hvo, code_or_hvo):
        """
        Remove a code from a phoneme.

        Args:
            phoneme_or_hvo: The IPhPhoneme object or HVO.
            code_or_hvo: The IPhCode object or HVO to remove.

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If phoneme_or_hvo or code_or_hvo is None.
            FP_ParameterError: If the code is not in the phoneme's code list.

        Example:
            >>> phoneme = project.Phonemes.Find("/t/")
            >>> if phoneme:
            ...     codes = project.Phonemes.GetCodes(phoneme)
            ...     # Remove the flap allophone
            ...     for code in codes:
            ...         ws = project.project.DefaultVernWs
            ...         repr = ITsString(code.Representation.get_String(ws)).Text
            ...         if repr == "[ɾ]":
            ...             project.Phonemes.RemoveCode(phoneme, code)
            ...             break

            >>> # Remove by HVO
            >>> phoneme = project.Phonemes.Find("/p/")
            >>> if phoneme:
            ...     codes = project.Phonemes.GetCodes(phoneme)
            ...     if codes:
            ...         project.Phonemes.RemoveCode(phoneme, codes[0].Hvo)

        Notes:
            - Code object must be from the phoneme's CodesOS collection
            - Use GetCodes() to find codes to remove
            - Accepts either IPhCode object or HVO

        See Also:
            GetCodes, AddCode
        """
        self._EnsureWriteEnabled()

        self._ValidateParam(phoneme_or_hvo, "phoneme_or_hvo")
        self._ValidateParam(code_or_hvo, "code_or_hvo")

        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)
        code = self.__GetCodeObject(code_or_hvo)

        # Check if code is in the phoneme's codes
        if code not in phoneme.CodesOS:
            raise FP_ParameterError("Code not found in phoneme's code list")

        phoneme.CodesOS.Remove(code)

    def GetBasicIPASymbol(self, phoneme_or_hvo, wsHandle=None):
        """
        Get the basic IPA symbol for a phoneme.

        Args:
            phoneme_or_hvo: The IPhPhoneme object or HVO.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            str: The basic IPA symbol, or empty string if not set.

        Raises:
            FP_NullParameterError: If phoneme_or_hvo is None.

        Example:
            >>> phoneme = project.Phonemes.Find("/p/")
            >>> if phoneme:
            ...     symbol = project.Phonemes.GetBasicIPASymbol(phoneme)
            ...     print(symbol)
            p

            >>> # Compare representation with basic IPA
            >>> phoneme = project.Phonemes.Find("/tʃ/")
            >>> if phoneme:
            ...     repr = project.Phonemes.GetRepresentation(phoneme)
            ...     ipa = project.Phonemes.GetBasicIPASymbol(phoneme)
            ...     print(f"Representation: {repr}, IPA: {ipa}")
            Representation: /tʃ/, IPA: tʃ

        Notes:
            - Returns the IPA symbol without slashes or diacritics
            - May differ from representation which can include slashes
            - Used for cross-linguistic phoneme identification
            - May be empty if not set
            - BasicIPASymbol property may not be available in all FLEx versions

        See Also:
            GetRepresentation
        """
        self._ValidateParam(phoneme_or_hvo, "phoneme_or_hvo")

        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        if hasattr(phoneme, 'BasicIPASymbol') and phoneme.BasicIPASymbol:
            ipa_str = ITsString(phoneme.BasicIPASymbol.get_String(wsHandle)).Text
            return ipa_str or ""
        return ""

    def IsVowel(self, phoneme_or_hvo):
        """
        Check if a phoneme is classified as a vowel.

        Args:
            phoneme_or_hvo: The IPhPhoneme object or HVO.

        Returns:
            bool: True if the phoneme is a vowel, False otherwise.

        Raises:
            FP_NullParameterError: If phoneme_or_hvo is None.

        Example:
            >>> # Filter vowels from phoneme inventory
            >>> vowels = []
            >>> for phoneme in project.Phonemes.GetAll():
            ...     if project.Phonemes.IsVowel(phoneme):
            ...         vowels.append(project.Phonemes.GetRepresentation(phoneme))
            >>> print("Vowels:", ", ".join(vowels))
            Vowels: /a/, /e/, /i/, /o/, /u/

            >>> # Count vowels vs consonants
            >>> vowel_count = 0
            >>> for phoneme in project.Phonemes.GetAll():
            ...     if project.Phonemes.IsVowel(phoneme):
            ...         vowel_count += 1
            >>> print(f"Total vowels: {vowel_count}")

        Notes:
            - Classification based on feature structure
            - Typically checks for [-consonantal, +sonorant] or [+syllabic] features
            - May return False if features not properly set
            - Feature analysis depends on project's feature system
            - Checks for common vowel feature indicators like 'syllabic', 'vocalic', 'vowel'

        See Also:
            IsConsonant, GetFeatures
        """
        self._ValidateParam(phoneme_or_hvo, "phoneme_or_hvo")

        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)

        # Check feature structure for vowel features
        if not hasattr(phoneme, 'FeaturesOA') or not phoneme.FeaturesOA:
            return False

        features = phoneme.FeaturesOA

        # Check for typical vowel features
        # Feature system varies by project, but common vowel features include:
        # [-consonantal], [+sonorant], [+syllabic]
        if hasattr(features, 'FeatureSpecsOC'):
            for spec in features.FeatureSpecsOC:
                if hasattr(spec, 'FeatureRA') and spec.FeatureRA:
                    feature_name = ""
                    if hasattr(spec.FeatureRA, 'Name'):
                        ws = self.project.project.DefaultAnalWs
                        feature_name = ITsString(spec.FeatureRA.Name.get_String(ws)).Text or ""

                    # Check for common vowel feature indicators
                    if feature_name.lower() in ['syllabic', 'vocalic', 'vowel']:
                        # Check if feature value is positive
                        if hasattr(spec, 'ValueRA') and spec.ValueRA:
                            return True

        return False

    def IsConsonant(self, phoneme_or_hvo):
        """
        Check if a phoneme is classified as a consonant.

        Args:
            phoneme_or_hvo: The IPhPhoneme object or HVO.

        Returns:
            bool: True if the phoneme is a consonant, False otherwise.

        Raises:
            FP_NullParameterError: If phoneme_or_hvo is None.

        Example:
            >>> # Filter consonants from phoneme inventory
            >>> consonants = []
            >>> for phoneme in project.Phonemes.GetAll():
            ...     if project.Phonemes.IsConsonant(phoneme):
            ...         consonants.append(project.Phonemes.GetRepresentation(phoneme))
            >>> print("Consonants:", ", ".join(consonants))
            Consonants: /p/, /t/, /k/, /b/, /d/, /g/, /m/, /n/

            >>> # Create consonant natural classes
            >>> for phoneme in project.Phonemes.GetAll():
            ...     if project.Phonemes.IsConsonant(phoneme):
            ...         desc = project.Phonemes.GetDescription(phoneme)
            ...         repr = project.Phonemes.GetRepresentation(phoneme)
            ...         print(f"{repr}: {desc}")

        Notes:
            - Classification based on feature structure
            - Typically checks for [+consonantal] or [-syllabic] features
            - May return False if features not properly set
            - Complementary to IsVowel() but not necessarily opposite
              (some sounds like glides may be neither or both)
            - Checks for common consonant feature indicators like 'consonantal', 'consonant'

        See Also:
            IsVowel, GetFeatures
        """
        self._ValidateParam(phoneme_or_hvo, "phoneme_or_hvo")

        phoneme = self.__GetPhonemeObject(phoneme_or_hvo)

        # Check feature structure for consonant features
        if not hasattr(phoneme, 'FeaturesOA') or not phoneme.FeaturesOA:
            return False

        features = phoneme.FeaturesOA

        # Check for typical consonant features
        # Feature system varies by project, but common consonant features include:
        # [+consonantal], [-syllabic]
        if hasattr(features, 'FeatureSpecsOC'):
            for spec in features.FeatureSpecsOC:
                if hasattr(spec, 'FeatureRA') and spec.FeatureRA:
                    feature_name = ""
                    if hasattr(spec.FeatureRA, 'Name'):
                        ws = self.project.project.DefaultAnalWs
                        feature_name = ITsString(spec.FeatureRA.Name.get_String(ws)).Text or ""

                    # Check for common consonant feature indicators
                    if feature_name.lower() in ['consonantal', 'consonant']:
                        # Check if feature value is positive
                        if hasattr(spec, 'ValueRA') and spec.ValueRA:
                            return True

        return False

    # --- Private Helper Methods ---

    def __GetPhonemeObject(self, phoneme_or_hvo):
        """
        Resolve HVO or object to IPhPhoneme.

        Args:
            phoneme_or_hvo: Either an IPhPhoneme object or an HVO (int).

        Returns:
            IPhPhoneme: The resolved phoneme object.
        """
        if isinstance(phoneme_or_hvo, int):
            return self.project.Object(phoneme_or_hvo)
        return phoneme_or_hvo

    def __GetCodeObject(self, code_or_hvo):
        """
        Resolve HVO or object to IPhCode.

        Args:
            code_or_hvo: Either an IPhCode object or an HVO (int).

        Returns:
            IPhCode: The resolved code object.
        """
        if isinstance(code_or_hvo, int):
            return self.project.Object(code_or_hvo)
        return code_or_hvo

    # ========== SYNC INTEGRATION METHODS ==========

    def GetSyncableProperties(self, item):
        """
        Get dictionary of syncable properties for cross-project synchronization.

        Args:
            item: The IPhPhoneme object.

        Returns:
            dict: Dictionary mapping property names to their values.
                Keys are property names, values are the property values.

        Example:
            >>> phonemeOps = PhonemeOperations(project)
            >>> phoneme = list(phonemeOps.GetAll())[0]
            >>> props = phonemeOps.GetSyncableProperties(phoneme)
            >>> print(props.keys())
            dict_keys(['Name', 'Description', 'BasicIPASymbol', 'FeaturesGuid'])

        Notes:
            - Returns all MultiString properties (all writing systems)
            - Returns FeaturesGuid as string (GUID of referenced feature structure)
            - Does not include CodesOS (owned allophonic codes)
            - Does not include GUID or HVO of the phoneme itself
        """
        phoneme = self.__GetPhonemeObject(item)

        # Get all writing systems for MultiString properties
        ws_factory = self.project.project.WritingSystemFactory
        all_ws = {ws.Id: ws.Handle for ws in ws_factory.WritingSystems}

        props = {}

        # MultiString properties (Name = representation)
        for prop_name in ['Name', 'Description', 'BasicIPASymbol']:
            if hasattr(phoneme, prop_name):
                prop_obj = getattr(phoneme, prop_name)
                if prop_obj:  # Check if property exists
                    ws_values = {}
                    for ws_id, ws_handle in all_ws.items():
                        text = ITsString(prop_obj.get_String(ws_handle)).Text
                        if text:  # Only include non-empty values
                            ws_values[ws_id] = text
                    if ws_values:  # Only include property if it has values
                        props[prop_name] = ws_values

        # Reference Atomic (RA) properties - return GUID as string
        if hasattr(phoneme, 'FeaturesOA') and phoneme.FeaturesOA:
            props['FeaturesGuid'] = str(phoneme.FeaturesOA.Guid)

        return props

    def CompareTo(self, item1, item2, ops1=None, ops2=None):
        """
        Compare two phonemes and return detailed differences.

        Args:
            item1: First phoneme to compare (from source project).
            item2: Second phoneme to compare (from target project).
            ops1: Optional PhonemeOperations instance for item1's project.
                 Defaults to self.
            ops2: Optional PhonemeOperations instance for item2's project.
                 Defaults to self.

        Returns:
            tuple: (is_different, differences) where:
                - is_different (bool): True if items differ
                - differences (dict): Maps property names to (value1, value2) tuples

        Example:
            >>> phoneme1 = project1_phonemeOps.Find("/p/")
            >>> phoneme2 = project2_phonemeOps.Find("/p/")
            >>> is_diff, diffs = project1_phonemeOps.CompareTo(
            ...     phoneme1, phoneme2,
            ...     ops1=project1_phonemeOps,
            ...     ops2=project2_phonemeOps
            ... )
            >>> if is_diff:
            ...     for prop, (val1, val2) in diffs.items():
            ...         print(f"{prop}: {val1} -> {val2}")

        Notes:
            - Compares all MultiString properties across all writing systems
            - Compares feature structure reference by GUID
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
        Get writing system handle, defaulting to vernacular WS for phoneme representations.

        Args:
            wsHandle: Optional writing system handle.

        Returns:
            int: The writing system handle.
        """
        if wsHandle is None:
            return self.project.project.DefaultVernWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultVernWs)
