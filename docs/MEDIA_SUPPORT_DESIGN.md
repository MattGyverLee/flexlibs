# Media Support Enhancement Design

**Date**: 2025-12-04
**Status**: Design Phase
**Purpose**: Complete media file management for lexical data (audio, images, pictures)

---

## Problem Statement

Current media support in flexlibs is incomplete and architecturally misplaced:

### Current Issues:

1. **MediaOperations in wrong module** - In TextsWords, should be shared/lexicon
2. **Missing operations**:
   - LexSense: Has `GetPictures()` but no `AddPicture()` or `RemovePicture()`
   - Example: Has `GetMediaFiles()` but no `AddMediaFile()` or `RemoveMediaFile()`
3. **No LinkedFiles directory access** - Users can't get project's LinkedFiles path
4. **No rename functionality** - Can't rename files and update references atomically
5. **No audio writing system support** - Can't work with voice recordings in fields

### What Users Need:

From the user's description:
> "Every field can have an audio writing system with a recorded or linked audio file.
> The pronunciation section in the lexicon can record or import a pronunciation.
> Images can be added to entries [senses]. We need access to the linkedfiles directory
> and a function to rename the linked file and update the reference."

---

## Current Implementation Status

### ✅ Already Implemented:

**PronunciationOperations** (COMPLETE):
- `MediaFilesOS` collection
- `AddMediaFile(pronunciation, file_path, label=None)` - Add audio
- `GetMediaFiles(pronunciation)` - Get all audio files
- `GetMediaCount(pronunciation)` - Count files
- `RemoveMediaFile(pronunciation, media)` - Remove audio

**LexSenseOperations** (PARTIAL - Read-only):
- `PicturesOS` collection
- `GetPictures(sense)` - Get pictures ✅
- `GetPictureCount(sense)` - Count pictures ✅
- ❌ Missing: `AddPicture()`, `RemovePicture()`, `SetPictureCaption()`

**ExampleOperations** (PARTIAL - Read-only):
- `MediaFilesOS` collection
- `GetMediaFiles(example)` - Get media ✅
- `GetMediaCount(example)` - Count media ✅
- ❌ Missing: `AddMediaFile()`, `RemoveMediaFile()`

**MediaOperations** (File management - misplaced):
- `GetInternalPath(media)` - Get path relative to LinkedFiles
- `GetExternalPath(media)` - Get absolute file path
- `SetInternalPath(media, path)` - Update path
- `CopyToProject(external_path, internal_subdir="AudioVisual")` - Copy file to LinkedFiles
- Uses `project.project.LinkedFilesRootDir` internally (lines 645-646, 1142-1147)

---

## Design: What to Add

### 1. FLExProject.GetLinkedFilesDir()

**Purpose**: Provide easy access to the project's LinkedFiles directory.

**Location**: Add to `FLExProject` class

**Implementation**:
```python
def GetLinkedFilesDir(self):
    """
    Get the full path to the project's LinkedFiles directory.

    Returns:
        str: Absolute path to LinkedFiles directory

    Example:
        >>> project = FLExProject()
        >>> project.OpenProject("MyProject")
        >>> linked_dir = project.GetLinkedFilesDir()
        >>> print(linked_dir)
        C:/Users/Me/Documents/FieldWorks/Projects/MyProject/LinkedFiles

        >>> # Access audio subdirectory
        >>> audio_dir = os.path.join(linked_dir, "AudioVisual")
        >>> print(audio_dir)
        C:/Users/Me/Documents/FieldWorks/Projects/MyProject/LinkedFiles/AudioVisual

    Notes:
        - Returns the LinkedFilesRootDir from LangProject
        - If not explicitly set, defaults to ProjectFolder/LinkedFiles
        - Common subdirectories:
          - AudioVisual/: Audio and video files
          - Pictures/: Image files
          - Others/: Other linked files

    See Also:
        Media.GetExternalPath, Media.CopyToProject
    """
    if hasattr(self.project, 'LinkedFilesRootDir'):
        return self.project.LinkedFilesRootDir
    # Fallback: construct default path
    import os
    return os.path.join(self.project.ProjectId.ProjectFolder, "LinkedFiles")
```

**File**: `flexlibs/code/FLExProject.py`
**Line**: ~1000-1020 (utility methods section)

---

### 2. MediaOperations.RenameMediaFile()

**Purpose**: Rename a media file on disk AND update all database references atomically.

**Location**: Add to `MediaOperations` class

**Implementation**:
```python
def RenameMediaFile(self, media_or_hvo, new_filename):
    """
    Rename a media file on disk and update the database reference.

    This is an atomic operation that:
    1. Renames the physical file in LinkedFiles directory
    2. Updates the InternalPath in the database
    3. Handles filename conflicts (adds suffix if needed)

    Args:
        media_or_hvo: ICmFile object or HVO
        new_filename: New filename (without path, just filename.ext)

    Returns:
        str: The actual new internal path (may differ if conflict occurred)

    Raises:
        FP_ReadOnlyError: If project not writable
        FP_ParameterError: If media doesn't exist or file not found
        OSError: If file rename fails

    Example:
        >>> # Rename an audio file
        >>> media = project.Media.Find("LinkedFiles/AudioVisual/old_name.wav")
        >>> new_path = project.Media.RenameMediaFile(media, "new_name.wav")
        >>> print(new_path)
        LinkedFiles/AudioVisual/new_name.wav

        >>> # Handles conflicts automatically
        >>> media2 = project.Media.Find("LinkedFiles/AudioVisual/temp.wav")
        >>> new_path = project.Media.RenameMediaFile(media2, "new_name.wav")
        >>> print(new_path)
        LinkedFiles/AudioVisual/new_name_1.wav

    Warning:
        - Renames the physical file on disk
        - If multiple references point to same file, ALL references are updated
        - Creates backup before rename (can be configured)

    Notes:
        - Preserves the subdirectory (AudioVisual, Pictures, etc.)
        - Only changes the filename, not the path
        - Handles filename conflicts by adding _1, _2, etc.
        - Updates InternalPath in database automatically
        - File extension should match original (warned if different)

    See Also:
        SetInternalPath, CopyToProject, GetExternalPath
    """
    if not self.project.writeEnabled:
        raise FP_ReadOnlyError()

    # Get media object
    media = self._GetObject(media_or_hvo) if isinstance(media_or_hvo, int) else media_or_hvo

    # Get current paths
    old_internal_path = self.GetInternalPath(media)
    old_external_path = self.GetExternalPath(media)

    if not os.path.exists(old_external_path):
        raise FP_ParameterError(f"File not found: {old_external_path}")

    # Construct new path (preserve directory)
    dir_name = os.path.dirname(old_internal_path)
    new_internal_path = os.path.join(dir_name, new_filename)
    new_external_path = os.path.join(
        self.project.project.LinkedFilesRootDir,
        new_internal_path.replace("LinkedFiles/", "").replace("LinkedFiles\\", "")
    )

    # Handle conflicts
    if os.path.exists(new_external_path):
        base, ext = os.path.splitext(new_filename)
        counter = 1
        while os.path.exists(new_external_path):
            new_filename_conflict = f"{base}_{counter}{ext}"
            new_internal_path = os.path.join(dir_name, new_filename_conflict)
            new_external_path = os.path.join(
                self.project.project.LinkedFilesRootDir,
                new_internal_path.replace("LinkedFiles/", "").replace("LinkedFiles\\", "")
            )
            counter += 1

    # Rename the physical file
    os.rename(old_external_path, new_external_path)

    # Update database reference
    self.SetInternalPath(media, new_internal_path)

    logger.info(f"Renamed media file: {old_internal_path} -> {new_internal_path}")

    return new_internal_path
```

**File**: `flexlibs/code/Shared/MediaOperations.py`
**Line**: After `SetInternalPath()` (~700-800)

---

### 3. LexSenseOperations Picture Methods

**Purpose**: Add, remove, and manage pictures attached to senses.

**Location**: Add to `LexSenseOperations` class

**Implementation**:

#### AddPicture()

```python
def AddPicture(self, sense_or_hvo, image_path, caption=None, wsHandle=None):
    """
    Add a picture (image) to a lexical sense.

    Pictures illustrate the meaning of a sense. The image file is copied into
    the project's LinkedFiles/Pictures directory and a reference is created.

    Args:
        sense_or_hvo: ILexSense object or HVO
        image_path: Path to image file (will be copied to project)
        caption: Optional caption text
        wsHandle: Writing system for caption (default: vernacular)

    Returns:
        ICmPicture: The newly created picture object

    Raises:
        FP_ReadOnlyError: If project not writable
        FP_ParameterError: If image file doesn't exist

    Example:
        >>> # Add picture to sense
        >>> sense = entry.SensesOS[0]
        >>> picture = project.Senses.AddPicture(
        ...     sense,
        ...     "/path/to/dog.jpg",
        ...     caption="A friendly dog"
        ... )

        >>> # Add picture without caption
        >>> picture = project.Senses.AddPicture(sense, "/path/to/cat.jpg")

        >>> # Get all pictures
        >>> pictures = project.Senses.GetPictures(sense)
        >>> print(f"Sense has {len(pictures)} pictures")

    Notes:
        - Image file is copied to LinkedFiles/Pictures/
        - Supported formats: JPG, PNG, GIF, BMP, TIFF
        - Caption can be edited later with SetPictureCaption()
        - Pictures are stored in PicturesOS collection
        - Uses ICmPictureFactory to create ICmPicture object

    See Also:
        RemovePicture, GetPictures, SetPictureCaption, RenamePicture
    """
    if not self.project.writeEnabled:
        raise FP_ReadOnlyError()

    sense = self._GetObject(sense_or_hvo) if isinstance(sense_or_hvo, int) else sense_or_hvo

    if not os.path.exists(image_path):
        raise FP_ParameterError(f"Image file not found: {image_path}")

    # Copy image to Pictures folder using Media operations
    media_file = self.project.Media.CopyToProject(image_path, internal_subdir="Pictures")

    # Create ICmPicture object
    from SIL.LCModel import ICmPictureFactory
    factory = self.project.project.ServiceLocator.GetService(ICmPictureFactory)
    picture = factory.Create()

    # Add to sense
    sense.PicturesOS.Add(picture)

    # Set the picture file reference
    picture.PictureFileRA = media_file

    # Set caption if provided
    if caption:
        wsHandle = self.__WSHandle(wsHandle)
        picture.Caption.set_String(wsHandle, TsStringUtils.MakeString(caption, wsHandle))

    logger.info(f"Added picture to sense: {os.path.basename(image_path)}")

    return picture
```

#### RemovePicture()

```python
def RemovePicture(self, sense_or_hvo, picture, delete_file=False):
    """
    Remove a picture from a lexical sense.

    Args:
        sense_or_hvo: ILexSense object or HVO
        picture: ICmPicture object to remove
        delete_file: If True, also delete the physical image file (default: False)

    Raises:
        FP_ReadOnlyError: If project not writable
        FP_ParameterError: If picture not in sense's collection

    Example:
        >>> # Remove picture but keep file
        >>> pictures = project.Senses.GetPictures(sense)
        >>> project.Senses.RemovePicture(sense, pictures[0])

        >>> # Remove picture AND delete file
        >>> project.Senses.RemovePicture(sense, pictures[0], delete_file=True)

    Warning:
        - With delete_file=True, the image is permanently deleted from disk
        - Other senses referencing the same file will lose access
        - Cannot be undone

    See Also:
        AddPicture, GetPictures
    """
    if not self.project.writeEnabled:
        raise FP_ReadOnlyError()

    sense = self._GetObject(sense_or_hvo) if isinstance(sense_or_hvo, int) else sense_or_hvo

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
```

#### SetPictureCaption()

```python
def SetPictureCaption(self, picture, caption, wsHandle=None):
    """
    Set or update the caption for a picture.

    Args:
        picture: ICmPicture object
        caption: Caption text
        wsHandle: Writing system (default: vernacular)

    Example:
        >>> pictures = project.Senses.GetPictures(sense)
        >>> project.Senses.SetPictureCaption(pictures[0], "A brown dog")
    """
    if not self.project.writeEnabled:
        raise FP_ReadOnlyError()

    wsHandle = self.__WSHandle(wsHandle)
    picture.Caption.set_String(wsHandle, TsStringUtils.MakeString(caption, wsHandle))
```

#### GetPictureCaption()

```python
def GetPictureCaption(self, picture, wsHandle=None):
    """
    Get the caption for a picture.

    Args:
        picture: ICmPicture object
        wsHandle: Writing system (default: best available)

    Returns:
        str: Caption text

    Example:
        >>> pictures = project.Senses.GetPictures(sense)
        >>> caption = project.Senses.GetPictureCaption(pictures[0])
    """
    wsHandle = self.__WSHandle(wsHandle) if wsHandle else self.project.project.DefaultVernWs
    return ITsString(picture.Caption.get_String(wsHandle)).Text or ""
```

#### RenamePicture()

```python
def RenamePicture(self, picture, new_filename):
    """
    Rename the image file for a picture and update the reference.

    Args:
        picture: ICmPicture object
        new_filename: New filename for the image

    Returns:
        str: New internal path

    Example:
        >>> pictures = project.Senses.GetPictures(sense)
        >>> new_path = project.Senses.RenamePicture(pictures[0], "dog_brown.jpg")

    See Also:
        Media.RenameMediaFile
    """
    if not self.project.writeEnabled:
        raise FP_ReadOnlyError()

    if not hasattr(picture, 'PictureFileRA') or not picture.PictureFileRA:
        raise FP_ParameterError("Picture has no associated file")

    # Use Media.RenameMediaFile to handle the rename
    return self.project.Media.RenameMediaFile(picture.PictureFileRA, new_filename)
```

#### MovePicture()

```python
def MovePicture(self, picture, from_sense_or_hvo, to_sense_or_hvo):
    """
    Move a picture from one sense to another sense.

    This is useful when reorganizing sense structure or correcting misplaced pictures.
    The picture object itself is moved (not copied), preserving its caption and file reference.

    Args:
        picture: ICmPicture object to move
        from_sense_or_hvo: Source ILexSense object or HVO
        to_sense_or_hvo: Destination ILexSense object or HVO

    Raises:
        FP_ReadOnlyError: If project not writable
        FP_ParameterError: If picture not in source sense's collection

    Example:
        >>> # Move picture from one sense to another
        >>> sense1 = entry.SensesOS[0]  # "to run (move fast)"
        >>> sense2 = entry.SensesOS[1]  # "to run (operate a machine)"
        >>> pictures = project.Senses.GetPictures(sense1)
        >>>
        >>> # Move the picture of a person running to the correct sense
        >>> project.Senses.MovePicture(pictures[0], sense1, sense2)
        >>>
        >>> # Verify the move
        >>> print(f"Sense 1 pictures: {project.Senses.GetPictureCount(sense1)}")
        >>> print(f"Sense 2 pictures: {project.Senses.GetPictureCount(sense2)}")

        >>> # Can also move between entries
        >>> entry2 = list(project.LexiconAllEntries())[1]
        >>> other_sense = entry2.SensesOS[0]
        >>> project.Senses.MovePicture(pictures[1], sense1, other_sense)

    Notes:
        - Picture is removed from source PicturesOS and added to destination PicturesOS
        - Caption and file reference are preserved
        - The physical image file is NOT moved/copied
        - Cannot move to the same sense (no-op, returns False)
        - Picture object's GUID remains the same

    Warning:
        - Moving pictures between entries is allowed but should be done carefully
        - Ensure the picture is semantically appropriate for the target sense
        - The picture will appear in the new sense's illustration area

    See Also:
        AddPicture, RemovePicture, GetPictures
    """
    if not self.project.writeEnabled:
        raise FP_ReadOnlyError()

    from_sense = self._GetObject(from_sense_or_hvo) if isinstance(from_sense_or_hvo, int) else from_sense_or_hvo
    to_sense = self._GetObject(to_sense_or_hvo) if isinstance(to_sense_or_hvo, int) else to_sense_or_hvo

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
```

**File**: `flexlibs/code/Lexicon/LexSenseOperations.py`
**Line**: After existing `GetPictureCount()` (~1770-2000)

---

### 4. ExampleOperations Media Methods

**Purpose**: Add and remove media files (audio/video) from example sentences.

**Location**: Add to `ExampleOperations` class

**Implementation**:

#### AddMediaFile()

```python
def AddMediaFile(self, example_or_hvo, file_path, label=None):
    """
    Add a media file (audio/video) to an example sentence.

    Args:
        example_or_hvo: ILexExampleSentence object or HVO
        file_path: Path to media file (will be copied to project)
        label: Optional label/description

    Returns:
        ICmFile: The newly created media file reference

    Example:
        >>> example = sense.ExamplesOS[0]
        >>> media = project.Examples.AddMediaFile(
        ...     example,
        ...     "/path/to/example_audio.wav",
        ...     label="Speaker pronunciation"
        ... )

    See Also:
        RemoveMediaFile, GetMediaFiles
    """
    if not self.project.writeEnabled:
        raise FP_ReadOnlyError()

    example = self._GetObject(example_or_hvo) if isinstance(example_or_hvo, int) else example_or_hvo

    if not os.path.exists(file_path):
        raise FP_ParameterError(f"File not found: {file_path}")

    # Copy file to AudioVisual folder
    media_file = self.project.Media.CopyToProject(file_path, internal_subdir="AudioVisual")

    # Set label if provided
    if label:
        wsHandle = self.project.project.DefaultAnalWs
        media_file.Description.set_String(wsHandle, TsStringUtils.MakeString(label, wsHandle))

    # Add to example's media collection
    example.MediaFilesOS.Add(media_file)

    logger.info(f"Added media file to example: {os.path.basename(file_path)}")

    return media_file
```

#### RemoveMediaFile()

```python
def RemoveMediaFile(self, example_or_hvo, media, delete_file=False):
    """
    Remove a media file from an example sentence.

    Args:
        example_or_hvo: ILexExampleSentence object or HVO
        media: ICmFile object to remove
        delete_file: If True, also delete the physical file

    Example:
        >>> media_files = project.Examples.GetMediaFiles(example)
        >>> project.Examples.RemoveMediaFile(example, media_files[0])

    See Also:
        AddMediaFile, GetMediaFiles
    """
    if not self.project.writeEnabled:
        raise FP_ReadOnlyError()

    example = self._GetObject(example_or_hvo) if isinstance(example_or_hvo, int) else example_or_hvo

    if media not in example.MediaFilesOS:
        raise FP_ParameterError("Media file not found in example's collection")

    # Get file path for optional deletion
    file_path = None
    if delete_file:
        file_path = self.project.Media.GetExternalPath(media)

    # Remove from collection
    example.MediaFilesOS.Remove(media)

    # Delete physical file if requested
    if delete_file and file_path and os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"Deleted file: {file_path}")

    logger.info("Removed media file from example")
```

#### MoveMediaFile()

```python
def MoveMediaFile(self, media, from_example_or_hvo, to_example_or_hvo):
    """
    Move a media file from one example to another example.

    This is useful when reorganizing examples or moving audio recordings to the
    correct example sentence.

    Args:
        media: ICmFile object to move
        from_example_or_hvo: Source ILexExampleSentence object or HVO
        to_example_or_hvo: Destination ILexExampleSentence object or HVO

    Raises:
        FP_ReadOnlyError: If project not writable
        FP_ParameterError: If media not in source example's collection

    Example:
        >>> # Move audio recording from one example to another
        >>> example1 = sense.ExamplesOS[0]
        >>> example2 = sense.ExamplesOS[1]
        >>>
        >>> media_files = project.Examples.GetMediaFiles(example1)
        >>> # Move the first audio file
        >>> project.Examples.MoveMediaFile(media_files[0], example1, example2)
        >>>
        >>> # Verify the move
        >>> print(f"Example 1 media: {project.Examples.GetMediaCount(example1)}")
        >>> print(f"Example 2 media: {project.Examples.GetMediaCount(example2)}")

        >>> # Can also move between different senses
        >>> other_sense = entry.SensesOS[1]
        >>> other_example = other_sense.ExamplesOS[0]
        >>> project.Examples.MoveMediaFile(media_files[1], example1, other_example)

    Notes:
        - Media is removed from source MediaFilesOS and added to destination
        - File reference and description are preserved
        - The physical media file is NOT moved/copied
        - Cannot move to the same example (no-op, returns False)
        - Media object's GUID remains the same

    Warning:
        - Moving media between different sense's examples is allowed
        - Ensure the media is semantically appropriate for the target example
        - The media will be associated with the new example

    See Also:
        AddMediaFile, RemoveMediaFile, GetMediaFiles
    """
    if not self.project.writeEnabled:
        raise FP_ReadOnlyError()

    from_example = self._GetObject(from_example_or_hvo) if isinstance(from_example_or_hvo, int) else from_example_or_hvo
    to_example = self._GetObject(to_example_or_hvo) if isinstance(to_example_or_hvo, int) else to_example_or_hvo

    # Can't move to same example
    if from_example == to_example:
        logger.warning("Source and destination are the same example")
        return False

    # Verify media is in source collection
    if media not in from_example.MediaFilesOS:
        raise FP_ParameterError("Media file not found in source example's media collection")

    # Move the media (remove from source, add to destination)
    from_example.MediaFilesOS.Remove(media)
    to_example.MediaFilesOS.Add(media)

    logger.info(f"Moved media from example {from_example.Guid} to example {to_example.Guid}")

    return True
```

**File**: `flexlibs/code/Lexicon/ExampleOperations.py`
**Line**: After existing `GetMediaCount()` (~995-1150)

---

### 5. PronunciationOperations Move Method

**Purpose**: Move media files between pronunciations for consistency with Examples.

**Location**: Add to `PronunciationOperations` class

**Note**: PronunciationOperations already has AddMediaFile() and RemoveMediaFile(). Adding MoveMediaFile() for completeness.

#### MoveMediaFile()

```python
def MoveMediaFile(self, media, from_pronunciation_or_hvo, to_pronunciation_or_hvo):
    """
    Move a media file from one pronunciation to another pronunciation.

    This is useful when reorganizing pronunciations or moving audio recordings to the
    correct pronunciation variant.

    Args:
        media: ICmFile object to move
        from_pronunciation_or_hvo: Source ILexPronunciation object or HVO
        to_pronunciation_or_hvo: Destination ILexPronunciation object or HVO

    Raises:
        FP_ReadOnlyError: If project not writable
        FP_ParameterError: If media not in source pronunciation's collection

    Example:
        >>> # Move audio from one pronunciation to another
        >>> entry = list(project.LexiconAllEntries())[0]
        >>> pron1 = entry.PronunciationsOS[0]  # IPA: [rʌn]
        >>> pron2 = entry.PronunciationsOS[1]  # IPA: [ɹʌn]
        >>>
        >>> media_files = project.Pronunciations.GetMediaFiles(pron1)
        >>> # Move the audio to the correct pronunciation variant
        >>> project.Pronunciations.MoveMediaFile(media_files[0], pron1, pron2)
        >>>
        >>> # Verify the move
        >>> print(f"Pron 1 media: {project.Pronunciations.GetMediaCount(pron1)}")
        >>> print(f"Pron 2 media: {project.Pronunciations.GetMediaCount(pron2)}")

        >>> # Can also move between different entries
        >>> entry2 = list(project.LexiconAllEntries())[1]
        >>> other_pron = entry2.PronunciationsOS[0]
        >>> project.Pronunciations.MoveMediaFile(media_files[1], pron1, other_pron)

    Notes:
        - Media is removed from source MediaFilesOS and added to destination
        - File reference and description are preserved
        - The physical media file is NOT moved/copied
        - Cannot move to the same pronunciation (no-op, returns False)
        - Media object's GUID remains the same

    Warning:
        - Moving media between different entries' pronunciations is allowed
        - Ensure the audio is appropriate for the target pronunciation
        - The media will be associated with the new pronunciation

    See Also:
        AddMediaFile, RemoveMediaFile, GetMediaFiles
    """
    if not self.project.writeEnabled:
        raise FP_ReadOnlyError()

    from_pron = self._GetObject(from_pronunciation_or_hvo) if isinstance(from_pronunciation_or_hvo, int) else from_pronunciation_or_hvo
    to_pron = self._GetObject(to_pronunciation_or_hvo) if isinstance(to_pronunciation_or_hvo, int) else to_pronunciation_or_hvo

    # Can't move to same pronunciation
    if from_pron == to_pron:
        logger.warning("Source and destination are the same pronunciation")
        return False

    # Verify media is in source collection
    if media not in from_pron.MediaFilesOS:
        raise FP_ParameterError("Media file not found in source pronunciation's media collection")

    # Move the media (remove from source, add to destination)
    from_pron.MediaFilesOS.Remove(media)
    to_pron.MediaFilesOS.Add(media)

    logger.info(f"Moved media from pronunciation {from_pron.Guid} to pronunciation {to_pron.Guid}")

    return True
```

**File**: `flexlibs/code/Lexicon/PronunciationOperations.py`
**Line**: After existing `RemoveMediaFile()` (~770-850)

---

## Audio Writing Systems

### What They Are:

FLEx supports special "audio" writing systems where instead of typing text, you record or link audio files. This is different from attaching media files to objects.

### How They Work:

1. **Writing System Type**: Special audio WS (like "en-Zxxx-x-audio")
2. **Field Content**: Instead of text, stores audio file reference
3. **Use Cases**:
   - Recording pronunciation in a field
   - Voice notes instead of typed comments
   - Alternative representation for non-literate speakers

### Current Gap:

Flexlibs doesn't handle audio writing systems. We need:

1. **Detect audio WS**: `IsAudioWritingSystem(wsHandle)`
2. **Get audio file**: `GetAudioFile(field, wsHandle)`
3. **Set audio file**: `SetAudioFile(field, wsHandle, file_path)`

### Recommended Approach:

**Add to Writing System utilities in FLExProject**:

```python
def IsAudioWritingSystem(self, wsHandle):
    """
    Check if a writing system is an audio writing system.

    Returns:
        bool: True if writing system is for audio
    """
    ws = self.project.WritingSystemFactory.get_EngineOrNull(wsHandle)
    if ws is None:
        return False
    # Check if it's an audio WS (typically has "audio" in the tag)
    return "audio" in ws.Id.lower() or ws.IsVoice

def GetAudioForField(self, obj, field_name, wsHandle):
    """
    Get audio file associated with a field in an audio writing system.

    Args:
        obj: Object containing the field
        field_name: Name of the field (e.g., "Form", "Gloss")
        wsHandle: Audio writing system handle

    Returns:
        str: Path to audio file, or None

    Example:
        >>> # Check if Form has audio in audio WS
        >>> audio_ws = project.GetWritingSystemHandle("en-Zxxx-x-audio")
        >>> if project.IsAudioWritingSystem(audio_ws):
        ...     audio_file = project.GetAudioForField(allomorph, "Form", audio_ws)
        ...     if audio_file:
        ...         print(f"Audio: {audio_file}")
    """
    # Implementation would access the ITsString and extract embedded audio reference
    # This is complex and requires understanding FLEx's audio WS format
    pass
```

**Recommendation**: Document audio WS as "advanced feature - TBD" for now. It requires deeper investigation into how FLEx stores audio references in ITsString objects.

---

## Implementation Priority

### Phase 1 (High Priority - Do First):
1. ✅ `FLExProject.GetLinkedFilesDir()` - Simple, widely useful
2. ✅ `LexSenseOperations.AddPicture()` - Core functionality gap
3. ✅ `LexSenseOperations.RemovePicture()` - Pairs with Add
4. ✅ `LexSenseOperations.MovePicture()` - User requested, very practical
5. ✅ `ExampleOperations.AddMediaFile()` - Core functionality gap
6. ✅ `ExampleOperations.RemoveMediaFile()` - Pairs with Add
7. ✅ `ExampleOperations.MoveMediaFile()` - User requested, very practical

### Phase 2 (Medium Priority):
8. ✅ `MediaOperations.RenameMediaFile()` - User requested, very useful
9. ✅ `LexSenseOperations.RenamePicture()` - Wrapper around RenameMediaFile
10. ✅ `LexSenseOperations.SetPictureCaption()` - Nice to have
11. ✅ `LexSenseOperations.GetPictureCaption()` - Pairs with Set
12. ✅ `PronunciationOperations.MoveMediaFile()` - Consistency with Examples

### Phase 3 (Future/Advanced):
13. ⏳ Audio Writing Systems support - Complex, needs research
14. ⏳ Move MediaOperations to better location - Architectural cleanup
12. ⏳ Add media to other objects (Text, Notebook entries, etc.)

---

## Testing Requirements

For each new method, create tests that verify:

1. **Happy path**: Normal usage works
2. **File operations**: Files are actually copied/renamed/deleted
3. **Database updates**: References are correctly updated
4. **Error handling**: Proper exceptions for edge cases
5. **Cleanup**: Test data is removed after tests

### Example Test Cases:

```python
def test_add_picture_to_sense():
    """Test adding a picture to a sense."""
    # Create test image
    # Add picture to sense
    # Verify picture in PicturesOS
    # Verify file exists in LinkedFiles/Pictures/
    # Cleanup

def test_rename_media_file():
    """Test renaming a media file."""
    # Create media file
    # Rename it
    # Verify old file doesn't exist
    # Verify new file exists
    # Verify database reference updated
    # Cleanup
```

---

## Documentation Requirements

1. **Update FUNCTION_REFERENCE.md**:
   - Add all new methods
   - Include examples
   - Cross-reference related methods

2. **Create MEDIA_MANAGEMENT_GUIDE.md**:
   - Overview of media in FLEx
   - When to use Pictures vs MediaFiles
   - LinkedFiles directory structure
   - Audio writing systems (brief intro)
   - Common workflows
   - Best practices

3. **Update operation class docstrings**:
   - Add examples using new methods
   - Explain Picture vs Media distinction
   - Document file handling behavior

---

## Summary

### What's Being Added:

| Component | Methods | Purpose |
|-----------|---------|---------|
| FLExProject | GetLinkedFilesDir() | Access LinkedFiles path |
| MediaOperations | RenameMediaFile() | Rename file + update ref |
| LexSenseOperations | AddPicture()<br>RemovePicture()<br>MovePicture()<br>SetPictureCaption()<br>GetPictureCaption()<br>RenamePicture() | Full picture management |
| ExampleOperations | AddMediaFile()<br>RemoveMediaFile()<br>MoveMediaFile() | Media attachment support |
| PronunciationOperations | MoveMediaFile() | Move media between pronunciations |

### What's Complete Already:

- PronunciationOperations: Full media support ✅
- MediaOperations: File path management ✅
- LexSenseOperations: Picture reading ✅
- ExampleOperations: Media reading ✅

### What's Deferred:

- Audio writing systems (complex, needs research)
- MediaOperations reorganization (architectural)
- Media on other object types (future enhancement)

---

## Next Steps

1. Implement Phase 1 methods (high priority)
2. Create demo scripts showing usage
3. Write tests for each method
4. Update documentation
5. Get user feedback
6. Implement Phase 2 methods
7. Consider Phase 3 (audio WS research)

This design addresses the user's immediate needs (LinkedFiles access, rename functionality, picture/media management) while documenting the full scope of media support gaps.
