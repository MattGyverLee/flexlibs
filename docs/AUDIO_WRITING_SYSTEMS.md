# Audio Writing Systems - Implementation Guide

**Date**: 2025-12-04
**Status**: Research Complete - Implementation Design
**Complexity**: Medium (requires ITsString manipulation)

---

## Overview

FLEx supports **audio writing systems** where text fields can contain audio file references instead of typed text. This is distinct from attaching media files to objects.

### Key Concepts:

**Audio Writing System**:
- Special writing system with `Zxxx` script code (ISO 15924 for "no written form")
- Tag format: `{lang}-Zxxx-x-audio` (e.g., `en-Zxxx-x-audio`, `fr-Zxxx-x-audio`)
- Display label shows as "English (Audio)", "French (Audio)", etc.

**How It Works**:
1. Field has audio WS variant (e.g., Form in `en-Zxxx-x-audio`)
2. Instead of text, field contains embedded file path
3. File path stored as ORC (Object Replacement Character) in ITsString
4. ORC type: `kodtExternalPathName` (external file path reference)

**Use Cases**:
- Recording pronunciation directly in Form field for non-literate speakers
- Voice notes instead of typed comments
- Alternative representation for unwritten languages
- Audio glosses for language learning

---

## Technical Implementation

### 1. Audio WS Detection

Audio writing systems are identified by:
- Script code `Zxxx` (no written form)
- Private use tag `-x-audio`
- Full pattern: `{languageCode}-Zxxx-x-audio`

### 2. File Path Embedding

Audio files are embedded in ITsString using:
- **ORC**: Object Replacement Character (Unicode U+FFFC)
- **ktptObjData**: Text property containing file path
- **Format**: `(char)FwObjDataTypes.kodtExternalPathName` + file path

### 3. LCM Types Needed

```python
from SIL.LCModel.Core.Text import TsStringUtils
from SIL.LCModel.Core.KernelInterfaces import (
    ITsString,
    ITsStrBldr,
    FwObjDataTypes,  # Enum for object data types
    FwTextPropType,   # Enum for text properties
)
```

---

## Research Findings

### From LCM Source Code:

**CoreWritingSystemDefinition.cs** (line 209):
```csharp
if (Script != null && !IsVoice)
```
→ Writing systems have an `IsVoice` property

**Test Case** (CoreWritingSystemDefinitionTests.cs, line 32):
```csharp
[TestCase("en-Zxxx-x-audio", "English \\(Audio\\)")]
```
→ Confirms `{lang}-Zxxx-x-audio` pattern

**TsStringUtils.cs** (line 858, 883):
```csharp
if (!String.IsNullOrEmpty(sProp) && sProp[0] == Convert.ToChar((int)FwObjDataTypes.kodtExternalPathName))
{
    string sRef = sProp.Substring(1);
    // ...
}
```
→ File paths are stored as `kodtExternalPathName` + path string

**kodtExternalPathName**:
- First character is the type code (FwObjDataTypes.kodtExternalPathName)
- Remaining characters are the file path
- Path is typically relative to LinkedFiles directory

---

## Implementation Design for Flexlibs

### Phase 1: Writing System Detection

Add to **FLExProject** class:

```python
def IsAudioWritingSystem(self, wsHandle):
    """
    Check if a writing system is an audio writing system.

    Audio writing systems use the Zxxx script code (no written form) and
    are typically used for voice recordings instead of typed text.

    Args:
        wsHandle: Writing system handle (int) or tag (str)

    Returns:
        bool: True if writing system is for audio recordings

    Example:
        >>> # Check by handle
        >>> ws_handle = project.GetWritingSystemHandle("en-Zxxx-x-audio")
        >>> is_audio = project.IsAudioWritingSystem(ws_handle)
        >>> print(is_audio)
        True

        >>> # Check vernacular WS
        >>> is_audio = project.IsAudioWritingSystem(project.project.DefaultVernWs)
        >>> print(is_audio)
        False

    Notes:
        - Audio WS tags follow pattern: {languageCode}-Zxxx-x-audio
        - "Zxxx" is ISO 15924 script code for "no written form"
        - Returns False for regular text writing systems
        - Used to determine if field contains audio file path vs text

    See Also:
        GetAudioPath, SetAudioPath, GetWritingSystemTag
    """
    # Resolve WS handle
    if isinstance(wsHandle, str):
        wsHandle = self.GetWritingSystemHandle(wsHandle)

    # Get writing system object
    try:
        ws = self.project.WritingSystemFactory.get_EngineOrNull(wsHandle)
        if ws is None:
            return False

        # Check the writing system tag
        ws_tag = ws.Id
        return "-Zxxx-" in ws_tag and "audio" in ws_tag.lower()

    except:
        return False
```

**File**: `flexlibs/code/FLExProject.py`
**Line**: After GetWritingSystemHandle() (~600-650)

---

### Phase 2: Audio Path Get/Set

Add to **FLExProject** class:

```python
def GetAudioPath(self, multistring_field, wsHandle):
    """
    Get the audio file path from a MultiString field in an audio writing system.

    For fields with audio writing systems, this extracts the embedded file path
    instead of text content.

    Args:
        multistring_field: The MultiString field (ITsMultiString)
        wsHandle: Audio writing system handle

    Returns:
        str: File path to audio file, or None if no audio set

    Raises:
        FP_ParameterError: If wsHandle is not an audio writing system

    Example:
        >>> # Get audio from Form field
        >>> audio_ws = project.GetWritingSystemHandle("en-Zxxx-x-audio")
        >>> allomorph = list(project.Allomorphs.GetAll())[0]
        >>>
        >>> audio_path = project.GetAudioPath(allomorph.Form, audio_ws)
        >>> if audio_path:
        ...     print(f"Audio file: {audio_path}")
        ... else:
        ...     print("No audio recording")

        >>> # Get audio from Gloss field
        >>> sense = entry.SensesOS[0]
        >>> audio_path = project.GetAudioPath(sense.Gloss, audio_ws)

    Notes:
        - Only works with audio writing systems (Zxxx-x-audio)
        - Returns None if no audio file embedded
        - Path is typically relative to LinkedFiles directory
        - Use GetLinkedFilesDir() to construct full path

    See Also:
        SetAudioPath, IsAudioWritingSystem, GetLinkedFilesDir
    """
    if not self.IsAudioWritingSystem(wsHandle):
        raise FP_ParameterError(
            "Writing system is not an audio writing system. "
            "Use IsAudioWritingSystem() to check first."
        )

    # Get ITsString for this WS
    ts_string = ITsString(multistring_field.get_String(wsHandle))

    if ts_string is None or ts_string.Length == 0:
        return None

    # Check if string contains embedded file path
    # Audio paths are embedded as ORC with kodtExternalPathName
    from SIL.LCModel.Core.KernelInterfaces import FwTextPropType

    try:
        # Get the properties of the first run
        if ts_string.RunCount > 0:
            props = ts_string.get_Properties(0)
            obj_data = props.GetStrPropValue(int(FwTextPropType.ktptObjData))

            if obj_data and len(obj_data) > 1:
                # First character should be kodtExternalPathName
                from SIL.LCModel.Core.KernelInterfaces import FwObjDataTypes
                if ord(obj_data[0]) == int(FwObjDataTypes.kodtExternalPathName):
                    # Remaining characters are the file path
                    file_path = obj_data[1:]
                    return file_path

    except Exception as e:
        logger.debug(f"Could not extract audio path: {e}")

    return None
```

```python
def SetAudioPath(self, multistring_field, wsHandle, file_path):
    """
    Set an audio file path in a MultiString field for an audio writing system.

    This embeds a file path as an ORC (Object Replacement Character) in the
    field, allowing FLEx to play the audio when viewing the field.

    Args:
        multistring_field: The MultiString field (ITsMultiString)
        wsHandle: Audio writing system handle
        file_path: Path to audio file (relative to LinkedFiles or absolute)

    Raises:
        FP_ReadOnlyError: If project not writable
        FP_ParameterError: If wsHandle is not an audio writing system

    Example:
        >>> # Set audio for Form field
        >>> audio_ws = project.GetWritingSystemHandle("en-Zxxx-x-audio")
        >>> allomorph = project.Allomorphs.Create(entry, "run")
        >>>
        >>> # Copy audio file to project
        >>> audio_file = project.Media.CopyToProject(
        ...     "/path/to/pronunciation.wav",
        ...     internal_subdir="AudioVisual"
        ... )
        >>> audio_path = project.Media.GetInternalPath(audio_file)
        >>>
        >>> # Set audio in Form field
        >>> project.SetAudioPath(allomorph.Form, audio_ws, audio_path)

        >>> # Later, retrieve it
        >>> retrieved_path = project.GetAudioPath(allomorph.Form, audio_ws)
        >>> print(retrieved_path)
        LinkedFiles/AudioVisual/pronunciation.wav

    Notes:
        - Only works with audio writing systems (Zxxx-x-audio)
        - File path should be relative to LinkedFiles directory
        - Use Media.CopyToProject() to copy file first
        - Creates ORC with kodtExternalPathName type
        - Field will display as playable audio in FLEx UI

    Warning:
        - Does not verify file exists
        - Does not copy file - use Media.CopyToProject() first
        - Overwrites any existing audio in this WS

    See Also:
        GetAudioPath, IsAudioWritingSystem, Media.CopyToProject
    """
    if not self.writeEnabled:
        raise FP_ReadOnlyError()

    if not self.IsAudioWritingSystem(wsHandle):
        raise FP_ParameterError(
            "Writing system is not an audio writing system. "
            "Use IsAudioWritingSystem() to check first."
        )

    from SIL.LCModel.Core.Text import TsStringUtils
    from SIL.LCModel.Core.KernelInterfaces import (
        ITsStrBldr,
        FwObjDataTypes,
        FwTextPropType,
    )

    # Create TsString with embedded file path
    bldr = TsStringUtils.MakeStrBldr()

    # Create ORC with external path
    # Format: (char)kodtExternalPathName + file_path
    obj_data = chr(int(FwObjDataTypes.kodtExternalPathName)) + file_path

    # Create properties with ObjData
    props_bldr = TsStringUtils.MakePropsBldr()
    props_bldr.SetIntPropValues(
        int(FwTextPropType.ktptWs),
        0,  # variation
        wsHandle
    )
    props_bldr.SetStrPropValue(
        int(FwTextPropType.ktptObjData),
        obj_data
    )

    # Insert ORC character (U+FFFC)
    ttp = props_bldr.GetTextProps()
    bldr.Replace(0, 0, "\ufffc", ttp)  # ORC character

    # Set the string in the multistring field
    multistring_field.set_String(wsHandle, bldr.GetString())

    logger.info(f"Set audio path in field: {file_path}")
```

**File**: `flexlibs/code/FLExProject.py`
**Line**: After IsAudioWritingSystem() (~650-750)

---

### Phase 3: Helper Methods for Operation Classes

Add convenience methods to operation classes that have MultiString fields.

**Example for AllomorphOperations**:

```python
def SetFormAudio(self, allomorph_or_hvo, file_path, wsHandle=None):
    """
    Set an audio recording for an allomorph's Form field.

    This is a convenience method for working with audio writing systems.
    The file is copied to LinkedFiles and embedded in the Form field.

    Args:
        allomorph_or_hvo: Allomorph object or HVO
        file_path: Path to audio file (will be copied to project)
        wsHandle: Audio writing system (default: first audio WS found)

    Returns:
        str: Internal path to the copied audio file

    Example:
        >>> # Create allomorph with audio
        >>> allo = project.Allomorphs.Create(entry, "run")
        >>>
        >>> # Add audio recording
        >>> audio_path = project.Allomorphs.SetFormAudio(
        ...     allo,
        ...     "/path/to/recordings/run.wav"
        ... )
        >>> print(f"Audio stored at: {audio_path}")

    See Also:
        GetFormAudio, project.SetAudioPath
    """
    if not self.project.writeEnabled:
        raise FP_ReadOnlyError()

    allomorph = self._GetObject(allomorph_or_hvo) if isinstance(allomorph_or_hvo, int) else allomorph_or_hvo

    # Find audio WS if not provided
    if wsHandle is None:
        # Get all writing systems
        for ws_handle in self.project.GetAllWritingSystems():
            if self.project.IsAudioWritingSystem(ws_handle):
                wsHandle = ws_handle
                break

        if wsHandle is None:
            raise FP_ParameterError(
                "No audio writing system found in project. "
                "Create one in FLEx first (e.g., en-Zxxx-x-audio)"
            )

    # Copy file to project
    media_file = self.project.Media.CopyToProject(
        file_path,
        internal_subdir="AudioVisual"
    )
    internal_path = self.project.Media.GetInternalPath(media_file)

    # Set audio in Form field
    self.project.SetAudioPath(allomorph.Form, wsHandle, internal_path)

    return internal_path
```

```python
def GetFormAudio(self, allomorph_or_hvo, wsHandle=None):
    """
    Get the audio file path from an allomorph's Form field.

    Args:
        allomorph_or_hvo: Allomorph object or HVO
        wsHandle: Audio writing system (default: first audio WS found)

    Returns:
        str: Path to audio file, or None if no audio set

    Example:
        >>> allo = list(project.Allomorphs.GetAll())[0]
        >>> audio_path = project.Allomorphs.GetFormAudio(allo)
        >>> if audio_path:
        ...     full_path = os.path.join(
        ...         project.GetLinkedFilesDir(),
        ...         audio_path.replace("LinkedFiles/", "")
        ...     )
        ...     print(f"Audio file: {full_path}")
    """
    allomorph = self._GetObject(allomorph_or_hvo) if isinstance(allomorph_or_hvo, int) else allomorph_or_hvo

    # Find audio WS if not provided
    if wsHandle is None:
        for ws_handle in self.project.GetAllWritingSystems():
            if self.project.IsAudioWritingSystem(ws_handle):
                wsHandle = ws_handle
                break

        if wsHandle is None:
            return None  # No audio WS in project

    return self.project.GetAudioPath(allomorph.Form, wsHandle)
```

**Similar methods needed for**:
- LexSenseOperations: Gloss, Definition (audio glosses/definitions)
- ExampleOperations: Example (audio example sentences)
- PronunciationOperations: Form (audio pronunciation - though this is rare, usually uses MediaFilesOS)

---

## Implementation Priority

### Phase 1: Core Infrastructure (Must Have)
1. ✅ FLExProject.IsAudioWritingSystem() - Detection
2. ✅ FLExProject.GetAudioPath() - Extract audio file path
3. ✅ FLExProject.SetAudioPath() - Embed audio file path

### Phase 2: Convenience Methods (Nice to Have)
4. ⏳ AllomorphOperations.SetFormAudio() / GetFormAudio()
5. ⏳ LexSenseOperations.SetGlossAudio() / GetGlossAudio()
6. ⏳ LexSenseOperations.SetDefinitionAudio() / GetDefinitionAudio()
7. ⏳ ExampleOperations.SetExampleAudio() / GetExampleAudio()

### Phase 3: Documentation & Examples
8. ⏳ Create demo showing audio WS workflow
9. ⏳ Document in MEDIA_MANAGEMENT_GUIDE.md
10. ⏳ Add to FUNCTION_REFERENCE.md

---

## Usage Examples

### Example 1: Basic Audio WS Detection

```python
from flexlibs2 import FLExProject

project = FLExProject()
project.OpenProject("UnwrittenLanguage", writeEnabled=False)

# Check all writing systems for audio
print("Audio Writing Systems:")
for ws_handle in project.GetAllWritingSystems():
    if project.IsAudioWritingSystem(ws_handle):
        ws_tag = project.GetWritingSystemTag(ws_handle)
        print(f"  - {ws_tag}")

project.CloseProject()
```

### Example 2: Set Audio in Form Field

```python
project.OpenProject("MyDictionary", writeEnabled=True)

# Get or create audio writing system
audio_ws_tag = "en-Zxxx-x-audio"
try:
    audio_ws = project.GetWritingSystemHandle(audio_ws_tag)
except:
    print(f"Audio WS '{audio_ws_tag}' not found. Create it in FLEx first.")
    project.CloseProject()
    exit()

# Create allomorph
entry = list(project.LexiconAllEntries())[0]
allo = project.Allomorphs.Create(entry, "run")

# Copy audio file to project
audio_file = project.Media.CopyToProject(
    "/path/to/recordings/run_audio.wav",
    internal_subdir="AudioVisual"
)
audio_path = project.Media.GetInternalPath(audio_file)

# Embed audio in Form field
project.SetAudioPath(allo.Form, audio_ws, audio_path)

print(f"Audio embedded: {audio_path}")

project.CloseProject()
```

### Example 3: Extract Audio from Fields

```python
project.OpenProject("MyDictionary", writeEnabled=False)

# Find audio WS
audio_ws = None
for ws in project.GetAllWritingSystems():
    if project.IsAudioWritingSystem(ws):
        audio_ws = ws
        break

if not audio_ws:
    print("No audio writing systems in this project")
else:
    # Check all allomorphs for audio recordings
    print("Allomorphs with audio recordings:")
    for entry in project.LexiconAllEntries():
        for allo in project.Allomorphs.GetAll(entry):
            audio_path = project.GetAudioPath(allo.Form, audio_ws)
            if audio_path:
                form = project.Allomorphs.GetForm(allo)
                print(f"  {form}: {audio_path}")

project.CloseProject()
```

### Example 4: Using Convenience Methods

```python
project.OpenProject("MyDictionary", writeEnabled=True)

entry = list(project.LexiconAllEntries())[0]
allo = project.Allomorphs.Create(entry, "walk")

# Easy way - convenience method handles everything
audio_path = project.Allomorphs.SetFormAudio(
    allo,
    "/path/to/recordings/walk.wav"
)

# Later retrieve it
retrieved = project.Allomorphs.GetFormAudio(allo)
print(f"Audio: {retrieved}")

project.CloseProject()
```

---

## Testing Requirements

### Unit Tests Needed:

1. **IsAudioWritingSystem()**
   - [ ] Returns True for `en-Zxxx-x-audio`
   - [ ] Returns False for regular WS
   - [ ] Handles invalid WS handles
   - [ ] Case insensitive for "audio" part

2. **SetAudioPath()**
   - [ ] Embeds file path as ORC
   - [ ] Uses kodtExternalPathName type
   - [ ] Sets correct writing system
   - [ ] Raises error if not audio WS
   - [ ] Raises error if read-only

3. **GetAudioPath()**
   - [ ] Extracts embedded file path
   - [ ] Returns None if no audio
   - [ ] Handles empty fields
   - [ ] Raises error if not audio WS

4. **Convenience Methods**
   - [ ] SetFormAudio copies file
   - [ ] SetFormAudio finds audio WS
   - [ ] GetFormAudio returns correct path
   - [ ] Works with multiple audio WS

---

## Limitations & Caveats

### Current Limitations:

1. **Cannot create audio WS from flexlibs**
   - Audio WS must be created in FLEx UI first
   - flexlibs can only use existing audio WS

2. **No audio playback**
   - flexlibs can embed/extract paths
   - Actual playback requires FLEx UI or external player

3. **No file validation**
   - SetAudioPath doesn't verify file exists
   - User must ensure file is in LinkedFiles

4. **ITsString complexity**
   - Requires understanding FLEx text properties
   - More complex than simple string fields

### Known Issues:

- If audio file is deleted from LinkedFiles, reference becomes broken
- FLEx UI may show warnings for missing audio files
- Audio WS must have exact tag format (Zxxx-x-audio)

---

## Integration with Media Operations

Audio WS support integrates with media operations:

```python
# Workflow: Record pronunciation and embed in Form
def add_pronunciation_audio(project, entry, audio_file_path):
    """Add audio recording to entry's default allomorph."""

    # Step 1: Copy audio to LinkedFiles
    media = project.Media.CopyToProject(
        audio_file_path,
        internal_subdir="AudioVisual"
    )
    internal_path = project.Media.GetInternalPath(media)

    # Step 2: Get or create allomorph
    if entry.LexemeFormOA:
        allo = entry.LexemeFormOA
    else:
        # Create allomorph
        allo = project.Allomorphs.Create(entry, "")

    # Step 3: Find audio WS
    audio_ws = None
    for ws in project.GetAllWritingSystems():
        if project.IsAudioWritingSystem(ws):
            audio_ws = ws
            break

    if not audio_ws:
        raise Exception("No audio WS found - create one in FLEx first")

    # Step 4: Embed audio in Form field
    project.SetAudioPath(allo.Form, audio_ws, internal_path)

    return internal_path
```

---

## Summary

### What We're Adding:

| Method | Purpose |
|--------|---------|
| IsAudioWritingSystem() | Detect audio WS by Zxxx-x-audio tag |
| GetAudioPath() | Extract file path from audio WS field |
| SetAudioPath() | Embed file path in audio WS field |
| SetFormAudio() | Convenience for allomorphs |
| GetFormAudio() | Convenience for allomorphs |

### Key Insights:

1. **Audio WS** = Regular WS with `Zxxx-x-audio` tag format
2. **File embedding** = ORC with `kodtExternalPathName` + path
3. **Different from MediaFilesOS** = Files embedded in text fields, not attached objects
4. **Requires audio WS** = Must be created in FLEx first
5. **Works with LinkedFiles** = Use Media operations to copy files

### Estimated Effort:

- Phase 1 (core): ~3 hours
- Phase 2 (convenience): ~2 hours
- Phase 3 (docs/tests): ~2 hours
- **Total**: ~7 hours

This completes the audio writing system support design for flexlibs!
