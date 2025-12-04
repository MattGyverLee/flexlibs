#
#   PronunciationOperations.py
#
#   Class: PronunciationOperations
#          Pronunciation operations for FieldWorks Language Explorer
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
from SIL.LCModel import (
    ILexEntry,
    ILexPronunciation,
    ILexPronunciationFactory,
    ICmFile,
    ICmFileFactory,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class PronunciationOperations:
    """
    This class provides operations for managing pronunciations in a FieldWorks project.

    Pronunciations represent the phonetic representation of lexical entries, typically
    using IPA (International Phonetic Alphabet) notation. Each pronunciation can have
    forms in multiple writing systems (e.g., en-fonipa for IPA), associated audio files,
    and optional CV (consonant-vowel) pattern location information.

    This class should be accessed via FLExProject.Pronunciations property.

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get all pronunciations for an entry
        entry = list(project.LexiconAllEntries())[0]
        for pron in project.Pronunciations.GetAll(entry):
            ipa = project.Pronunciations.GetForm(pron, "en-fonipa")
            print(f"IPA: {ipa}")

        # Create a new pronunciation
        pron = project.Pronunciations.Create(entry, "rʌn", "en-fonipa")

        # Add audio file
        project.Pronunciations.AddMediaFile(pron, "/path/to/audio.wav")

        # Get media files
        media = project.Pronunciations.GetMediaFiles(pron)
        print(f"Audio files: {len(media)}")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize PronunciationOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    # --- Core CRUD Operations ---

    def GetAll(self, entry_or_hvo=None):
        """
        Get all pronunciations for a lexical entry, or all pronunciations in the entire project.

        Args:
            entry_or_hvo: The ILexEntry object or HVO. If None, iterates all pronunciations
                         in the entire project.

        Yields:
            ILexPronunciation: Each pronunciation for the entry (or project).

        Example:
            >>> # Get pronunciations for specific entry
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> for pron in project.Pronunciations.GetAll(entry):
            ...     ipa = project.Pronunciations.GetForm(pron, "en-fonipa")
            ...     print(f"IPA: {ipa}")
            IPA: rʌn
            IPA: ɹʌn

            >>> # Get ALL pronunciations in entire project
            >>> for pron in project.Pronunciations.GetAll():
            ...     ipa = project.Pronunciations.GetForm(pron, "en-fonipa")
            ...     print(f"IPA: {ipa}")

        Notes:
            - When entry_or_hvo is provided:
              - Returns pronunciations in the order they appear in FLEx
              - Returns empty generator if entry has no pronunciations
              - Pronunciations are ordered collections (can be reordered)
            - When entry_or_hvo is None:
              - Iterates ALL entries in the project
              - For each entry, yields all pronunciations
              - Useful for project-wide pronunciation operations

        See Also:
            Create, Delete, Reorder
        """
        if entry_or_hvo is None:
            # Iterate ALL pronunciations in entire project
            for entry in self.project.lexDB.Entries:
                if hasattr(entry, 'PronunciationsOS'):
                    for pronunciation in entry.PronunciationsOS:
                        yield pronunciation
        else:
            # Iterate pronunciations for specific entry
            entry = self.__GetEntryObject(entry_or_hvo)

            if hasattr(entry, 'PronunciationsOS'):
                for pronunciation in entry.PronunciationsOS:
                    yield pronunciation


    def Create(self, entry_or_hvo, form, wsHandle=None):
        """
        Create a new pronunciation for a lexical entry.

        Args:
            entry_or_hvo: The ILexEntry object or HVO.
            form (str): The pronunciation form (typically IPA notation).
            wsHandle: Optional writing system handle. Use "en-fonipa" for IPA,
                     or defaults to vernacular WS.

        Returns:
            ILexPronunciation: The newly created pronunciation object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If entry_or_hvo or form is None.
            FP_ParameterError: If form is empty.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> # Create IPA pronunciation
            >>> pron = project.Pronunciations.Create(entry, "rʌn", "en-fonipa")
            >>> print(project.Pronunciations.GetForm(pron, "en-fonipa"))
            rʌn

            >>> # Create with default WS
            >>> pron = project.Pronunciations.Create(entry, "run")

        Notes:
            - The pronunciation is added to the end of the entry's pronunciations list
            - For IPA notation, use "en-fonipa" writing system (English IPA)
            - Other IPA writing systems follow pattern: "{lang}-fonipa" (e.g., "fr-fonipa")
            - Audio files can be added after creation using AddMediaFile()
            - Pronunciation form is set immediately

        See Also:
            Delete, SetForm, AddMediaFile
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()
        if form is None:
            raise FP_NullParameterError()

        if not form or not form.strip():
            raise FP_ParameterError("Pronunciation form cannot be empty")

        entry = self.__GetEntryObject(entry_or_hvo)
        wsHandle = self.__WSHandleVern(wsHandle)

        # Create the new pronunciation using the factory
        factory = self.project.project.ServiceLocator.GetService(ILexPronunciationFactory)
        pronunciation = factory.Create()

        # Add to entry's pronunciations collection (must be done before setting properties)
        if hasattr(entry, 'PronunciationsOS'):
            entry.PronunciationsOS.Add(pronunciation)
        else:
            raise FP_ParameterError("Entry does not support pronunciations")

        # Set pronunciation form
        mkstr = TsStringUtils.MakeString(form, wsHandle)
        pronunciation.Form.set_String(wsHandle, mkstr)

        return pronunciation


    def Delete(self, pronunciation_or_hvo):
        """
        Delete a pronunciation.

        Args:
            pronunciation_or_hvo: The ILexPronunciation object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If pronunciation_or_hvo is None.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> pronunciations = list(project.Pronunciations.GetAll(entry))
            >>> if pronunciations:
            ...     project.Pronunciations.Delete(pronunciations[0])

        Notes:
            - Permanently removes the pronunciation from the database
            - Associated media files are NOT automatically deleted from disk
            - Cannot be undone
            - The pronunciation is removed from the owning entry's collection

        See Also:
            Create, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not pronunciation_or_hvo:
            raise FP_NullParameterError()

        pronunciation = self.__GetPronunciationObject(pronunciation_or_hvo)

        # Get owning entry and remove from collection
        entry = pronunciation.Owner
        if hasattr(entry, 'PronunciationsOS'):
            entry.PronunciationsOS.Remove(pronunciation)


    def Reorder(self, entry_or_hvo, pronunciation_list):
        """
        Reorder pronunciations for a lexical entry.

        Args:
            entry_or_hvo: The ILexEntry object or HVO.
            pronunciation_list: List of ILexPronunciation objects in desired order.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If entry_or_hvo or pronunciation_list is None.
            FP_ParameterError: If pronunciation_list is invalid or contains
                              pronunciations not owned by this entry.

        Example:
            >>> entry = list(project.LexiconAllEntries())[0]
            >>> prons = list(project.Pronunciations.GetAll(entry))
            >>> if len(prons) > 1:
            ...     # Reverse the order
            ...     project.Pronunciations.Reorder(entry, list(reversed(prons)))

        Notes:
            - All pronunciations in the list must belong to the entry
            - The list must contain all current pronunciations (no partial reordering)
            - Useful for prioritizing preferred pronunciations
            - Order affects display in FLEx UI

        See Also:
            GetAll, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()
        if pronunciation_list is None:
            raise FP_NullParameterError()

        entry = self.__GetEntryObject(entry_or_hvo)

        if not hasattr(entry, 'PronunciationsOS'):
            raise FP_ParameterError("Entry does not support pronunciations")

        # Validate that all pronunciations belong to this entry
        current_count = entry.PronunciationsOS.Count
        if len(pronunciation_list) != current_count:
            raise FP_ParameterError(
                f"Pronunciation list must contain all {current_count} pronunciations"
            )

        # Clear and re-add in new order
        entry.PronunciationsOS.Clear()
        for pron in pronunciation_list:
            entry.PronunciationsOS.Add(pron)


    # --- Form Management ---

    def GetForm(self, pronunciation_or_hvo, wsHandle=None):
        """
        Get the pronunciation form (e.g., IPA transcription).

        Args:
            pronunciation_or_hvo: The ILexPronunciation object or HVO.
            wsHandle: Optional writing system handle or tag (e.g., "en-fonipa" for IPA).
                     Defaults to vernacular WS.

        Returns:
            str: The pronunciation form text, or empty string if not set.

        Raises:
            FP_NullParameterError: If pronunciation_or_hvo is None.

        Example:
            >>> pron = list(project.Pronunciations.GetAll(entry))[0]
            >>> # Get IPA form
            >>> ipa = project.Pronunciations.GetForm(pron, "en-fonipa")
            >>> print(f"IPA: {ipa}")
            IPA: rʌn

            >>> # Get default WS form
            >>> form = project.Pronunciations.GetForm(pron)

        Notes:
            - For IPA notation, use "{lang}-fonipa" writing system (e.g., "en-fonipa")
            - Returns empty string if form is not set for the specified WS
            - Can retrieve forms in multiple writing systems if set
            - Pronunciation forms are typically phonetic transcriptions

        See Also:
            SetForm, Create
        """
        if not pronunciation_or_hvo:
            raise FP_NullParameterError()

        pronunciation = self.__GetPronunciationObject(pronunciation_or_hvo)
        wsHandle = self.__WSHandleVern(wsHandle)

        # MultiUnicodeAccessor
        form = ITsString(pronunciation.Form.get_String(wsHandle)).Text
        return form or ""


    def SetForm(self, pronunciation_or_hvo, text, wsHandle=None):
        """
        Set the pronunciation form (e.g., IPA transcription).

        Args:
            pronunciation_or_hvo: The ILexPronunciation object or HVO.
            text (str): The pronunciation form text (typically IPA notation).
            wsHandle: Optional writing system handle or tag (e.g., "en-fonipa" for IPA).
                     Defaults to vernacular WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If pronunciation_or_hvo or text is None.

        Example:
            >>> pron = list(project.Pronunciations.GetAll(entry))[0]
            >>> # Set IPA form
            >>> project.Pronunciations.SetForm(pron, "ɹʌn", "en-fonipa")

            >>> # Update default WS form
            >>> project.Pronunciations.SetForm(pron, "run")

        Notes:
            - For IPA notation, use "{lang}-fonipa" writing system (e.g., "en-fonipa")
            - Can set forms in multiple writing systems
            - Empty string clears the form for that writing system
            - Forms can contain Unicode IPA characters

        See Also:
            GetForm, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not pronunciation_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        pronunciation = self.__GetPronunciationObject(pronunciation_or_hvo)
        wsHandle = self.__WSHandleVern(wsHandle)

        # MultiUnicodeAccessor
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        pronunciation.Form.set_String(wsHandle, mkstr)


    # --- Media Files ---

    def GetMediaFiles(self, pronunciation_or_hvo):
        """
        Get all media files (typically audio) associated with a pronunciation.

        Args:
            pronunciation_or_hvo: The ILexPronunciation object or HVO.

        Returns:
            list: List of media file objects (empty list if none).

        Raises:
            FP_NullParameterError: If pronunciation_or_hvo is None.

        Example:
            >>> pron = list(project.Pronunciations.GetAll(entry))[0]
            >>> media = project.Pronunciations.GetMediaFiles(pron)
            >>> for m in media:
            ...     print(f"Media: {m}")
            Media: audio_recording.wav

        Notes:
            - Returns media file objects from MediaFilesOS collection
            - Media files are typically audio recordings of pronunciation
            - Can also include video or other media types
            - File objects contain path and metadata information
            - Empty list if no media files attached

        See Also:
            GetMediaCount, AddMediaFile, RemoveMediaFile
        """
        if not pronunciation_or_hvo:
            raise FP_NullParameterError()

        pronunciation = self.__GetPronunciationObject(pronunciation_or_hvo)

        if hasattr(pronunciation, 'MediaFilesOS'):
            return list(pronunciation.MediaFilesOS)
        return []


    def GetMediaCount(self, pronunciation_or_hvo):
        """
        Get the count of media files associated with a pronunciation.

        Args:
            pronunciation_or_hvo: The ILexPronunciation object or HVO.

        Returns:
            int: The number of media files.

        Raises:
            FP_NullParameterError: If pronunciation_or_hvo is None.

        Example:
            >>> pron = list(project.Pronunciations.GetAll(entry))[0]
            >>> count = project.Pronunciations.GetMediaCount(pron)
            >>> print(f"This pronunciation has {count} audio files")
            This pronunciation has 2 audio files

        Notes:
            - More efficient than len(GetMediaFiles()) for just counting
            - Returns 0 if no media files attached
            - Includes all media types (audio, video, etc.)

        See Also:
            GetMediaFiles, AddMediaFile
        """
        if not pronunciation_or_hvo:
            raise FP_NullParameterError()

        pronunciation = self.__GetPronunciationObject(pronunciation_or_hvo)

        if hasattr(pronunciation, 'MediaFilesOS'):
            return pronunciation.MediaFilesOS.Count
        return 0


    def AddMediaFile(self, pronunciation_or_hvo, file_path, label=None):
        """
        Add a media file (typically audio) to a pronunciation.

        Copies the file to the project's LinkedFiles directory and creates
        a media reference linked to the pronunciation.

        Args:
            pronunciation_or_hvo: The ILexPronunciation object or HVO.
            file_path (str): Path to the external media file to import.
            label (str, optional): Descriptive label for the media file.

        Returns:
            ICmFile: The created media file object with proper path.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If pronunciation_or_hvo or file_path is None.
            FP_ParameterError: If file_path is empty or file doesn't exist.

        Example:
            >>> pron = list(project.Pronunciations.GetAll(entry))[0]
            >>> # Add audio recording
            >>> media = project.Pronunciations.AddMediaFile(
            ...     pron,
            ...     "/path/to/audio.wav",
            ...     label="Speaker pronunciation"
            ... )
            >>> print(f"Added media file")
            Added media file

        Notes:
            - File is copied to LinkedFiles/AudioVisual directory
            - Unique filename generated if collision occurs (audio_1.wav, etc.)
            - Creates ICmFile object with proper LinkedFiles path
            - Supported formats: WAV, MP3, OGG, WMA (audio), MP4, AVI (video)
            - Multiple media files can be added to one pronunciation

        See Also:
            RemoveMediaFile, GetMediaFiles, GetMediaCount, project.Media.CopyToProject
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not pronunciation_or_hvo:
            raise FP_NullParameterError()
        if file_path is None:
            raise FP_NullParameterError()

        if not file_path or not file_path.strip():
            raise FP_ParameterError("File path cannot be empty")

        pronunciation = self.__GetPronunciationObject(pronunciation_or_hvo)

        # Use MediaOperations to properly copy file and create ICmFile
        # Copy file to project and get ICmFile reference
        media_file = self.project.Media.CopyToProject(
            file_path,
            internal_subdir="AudioVisual",
            label=label
        )

        # Add to pronunciation's media collection
        if hasattr(pronunciation, 'MediaFilesOS'):
            pronunciation.MediaFilesOS.Add(media_file)
        else:
            raise FP_ParameterError("Pronunciation does not support media files")

        return media_file


    def RemoveMediaFile(self, pronunciation_or_hvo, media_or_hvo):
        """
        Remove a media file from a pronunciation.

        Args:
            pronunciation_or_hvo: The ILexPronunciation object or HVO.
            media_or_hvo: The ICmFile object or HVO to remove.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If pronunciation_or_hvo or media_or_hvo is None.

        Example:
            >>> pron = list(project.Pronunciations.GetAll(entry))[0]
            >>> media_files = project.Pronunciations.GetMediaFiles(pron)
            >>> if media_files:
            ...     project.Pronunciations.RemoveMediaFile(pron, media_files[0])

        Notes:
            - Removes the media file reference from the pronunciation
            - Does NOT delete the actual file from disk
            - The media file object is deleted from the database
            - Cannot be undone

        See Also:
            AddMediaFile, GetMediaFiles
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not pronunciation_or_hvo:
            raise FP_NullParameterError()
        if media_or_hvo is None:
            raise FP_NullParameterError()

        pronunciation = self.__GetPronunciationObject(pronunciation_or_hvo)

        # Resolve media object
        if isinstance(media_or_hvo, int):
            media = self.project.Object(media_or_hvo)
        else:
            media = media_or_hvo

        # Remove from collection
        if hasattr(pronunciation, 'MediaFilesOS'):
            pronunciation.MediaFilesOS.Remove(media)


    # --- CV Pattern/Location ---

    def GetLocation(self, pronunciation_or_hvo):
        """
        Get the CV pattern location for the pronunciation.

        The location refers to where in a CV (consonant-vowel) pattern analysis
        this pronunciation applies. This is used in phonological analysis.

        Args:
            pronunciation_or_hvo: The ILexPronunciation object or HVO.

        Returns:
            object: The location object, or None if not set.

        Raises:
            FP_NullParameterError: If pronunciation_or_hvo is None.

        Example:
            >>> pron = list(project.Pronunciations.GetAll(entry))[0]
            >>> location = project.Pronunciations.GetLocation(pron)
            >>> if location:
            ...     print(f"CV Location: {location}")

        Notes:
            - Location is used for phonological CV pattern analysis
            - Returns None if no location is set
            - Location objects reference phonological environments
            - Not commonly used in basic pronunciation entry

        See Also:
            SetLocation
        """
        if not pronunciation_or_hvo:
            raise FP_NullParameterError()

        pronunciation = self.__GetPronunciationObject(pronunciation_or_hvo)

        if hasattr(pronunciation, 'LocationRA'):
            return pronunciation.LocationRA
        return None


    def SetLocation(self, pronunciation_or_hvo, location):
        """
        Set the CV pattern location for the pronunciation.

        Args:
            pronunciation_or_hvo: The ILexPronunciation object or HVO.
            location: The location object (phonological environment) to set,
                     or None to clear.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If pronunciation_or_hvo is None.

        Example:
            >>> pron = list(project.Pronunciations.GetAll(entry))[0]
            >>> # Set location (requires a valid phonological environment object)
            >>> # env = project.Environments.Find("word-final")
            >>> # project.Pronunciations.SetLocation(pron, env)

            >>> # Clear location
            >>> project.Pronunciations.SetLocation(pron, None)

        Notes:
            - Location must be a valid phonological environment object
            - Pass None to clear the location
            - Used for phonological CV pattern analysis
            - Not commonly used in basic pronunciation entry

        See Also:
            GetLocation
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not pronunciation_or_hvo:
            raise FP_NullParameterError()

        pronunciation = self.__GetPronunciationObject(pronunciation_or_hvo)

        if hasattr(pronunciation, 'LocationRA'):
            pronunciation.LocationRA = location


    # --- Utilities ---

    def GetOwningEntry(self, pronunciation_or_hvo):
        """
        Get the lexical entry that owns this pronunciation.

        Args:
            pronunciation_or_hvo: The ILexPronunciation object or HVO.

        Returns:
            ILexEntry: The owning entry object.

        Raises:
            FP_NullParameterError: If pronunciation_or_hvo is None.

        Example:
            >>> pron = list(project.Pronunciations.GetAll(entry))[0]
            >>> owner = project.Pronunciations.GetOwningEntry(pron)
            >>> headword = project.LexEntry.GetHeadword(owner)
            >>> print(f"Pronunciation belongs to: {headword}")
            Pronunciation belongs to: run

        Notes:
            - Returns the ILexEntry that contains this pronunciation
            - Useful when you have a pronunciation object without context
            - The owner is determined by the LCM ownership hierarchy

        See Also:
            GetGuid, GetAll
        """
        if not pronunciation_or_hvo:
            raise FP_NullParameterError()

        pronunciation = self.__GetPronunciationObject(pronunciation_or_hvo)
        return pronunciation.Owner


    def GetGuid(self, pronunciation_or_hvo):
        """
        Get the GUID of a pronunciation.

        Args:
            pronunciation_or_hvo: The ILexPronunciation object or HVO.

        Returns:
            System.Guid: The GUID of the pronunciation.

        Raises:
            FP_NullParameterError: If pronunciation_or_hvo is None.

        Example:
            >>> pron = list(project.Pronunciations.GetAll(entry))[0]
            >>> guid = project.Pronunciations.GetGuid(pron)
            >>> print(f"Pronunciation GUID: {guid}")
            Pronunciation GUID: 12345678-1234-1234-1234-123456789abc

        Notes:
            - GUIDs are globally unique identifiers
            - Persistent across project versions
            - Use for external references and tracking
            - Same GUID across different copies of the project

        See Also:
            GetOwningEntry
        """
        if not pronunciation_or_hvo:
            raise FP_NullParameterError()

        pronunciation = self.__GetPronunciationObject(pronunciation_or_hvo)
        return pronunciation.Guid


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


    def __GetPronunciationObject(self, pronunciation_or_hvo):
        """
        Resolve HVO or object to ILexPronunciation.

        Args:
            pronunciation_or_hvo: Either an ILexPronunciation object or an HVO (int).

        Returns:
            ILexPronunciation: The resolved pronunciation object.
        """
        if isinstance(pronunciation_or_hvo, int):
            return self.project.Object(pronunciation_or_hvo)
        return pronunciation_or_hvo


    def __WSHandle(self, wsHandle):
        """
        Get writing system handle, defaulting to vernacular WS.

        Args:
            wsHandle: Optional writing system handle or tag.

        Returns:
            int: The writing system handle.
        """
        if wsHandle is None:
            return self.project.project.DefaultVernWs

        # If it's a string (like "en-fonipa"), convert to handle
        if isinstance(wsHandle, str):
            handle = self.project.WSHandle(wsHandle)
            if handle is None:
                # Fallback to default vernacular if WS not found
                return self.project.project.DefaultVernWs
            return handle

        return wsHandle


    def __WSHandleVern(self, wsHandle):
        """
        Get writing system handle, defaulting to vernacular WS for pronunciation forms.

        Args:
            wsHandle: Optional writing system handle or tag (e.g., "en-fonipa").

        Returns:
            int: The writing system handle.
        """
        return self.__WSHandle(wsHandle)
