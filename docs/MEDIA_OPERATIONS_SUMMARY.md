# Media Operations - Complete Implementation Summary

**Date**: 2025-12-04
**Status**: Design Complete - Ready for Implementation
**Total Methods**: 13 new methods + 1 utility

---

## Quick Reference

### New Methods by Component

| Component | New Methods | Count |
|-----------|-------------|-------|
| **FLExProject** | GetLinkedFilesDir() | 1 |
| **MediaOperations** | RenameMediaFile() | 1 |
| **LexSenseOperations** | AddPicture(), RemovePicture(), MovePicture()<br>SetPictureCaption(), GetPictureCaption(), RenamePicture() | 6 |
| **ExampleOperations** | AddMediaFile(), RemoveMediaFile(), MoveMediaFile() | 3 |
| **PronunciationOperations** | MoveMediaFile() | 1 |
| **TOTAL** | | **12** |

---

## Complete Method Signatures

### FLExProject

```python
def GetLinkedFilesDir(self) -> str:
    """Get the full path to the project's LinkedFiles directory."""
```

### MediaOperations

```python
def RenameMediaFile(self, media_or_hvo, new_filename) -> str:
    """Rename a media file on disk and update all database references."""
```

### LexSenseOperations

```python
def AddPicture(self, sense_or_hvo, image_path, caption=None, wsHandle=None) -> ICmPicture:
    """Add a picture (image) to a lexical sense."""

def RemovePicture(self, sense_or_hvo, picture, delete_file=False):
    """Remove a picture from a lexical sense."""

def MovePicture(self, picture, from_sense_or_hvo, to_sense_or_hvo) -> bool:
    """Move a picture from one sense to another sense."""

def SetPictureCaption(self, picture, caption, wsHandle=None):
    """Set or update the caption for a picture."""

def GetPictureCaption(self, picture, wsHandle=None) -> str:
    """Get the caption for a picture."""

def RenamePicture(self, picture, new_filename) -> str:
    """Rename the image file for a picture and update the reference."""
```

### ExampleOperations

```python
def AddMediaFile(self, example_or_hvo, file_path, label=None) -> ICmFile:
    """Add a media file (audio/video) to an example sentence."""

def RemoveMediaFile(self, example_or_hvo, media, delete_file=False):
    """Remove a media file from an example sentence."""

def MoveMediaFile(self, media, from_example_or_hvo, to_example_or_hvo) -> bool:
    """Move a media file from one example to another example."""
```

### PronunciationOperations

```python
def MoveMediaFile(self, media, from_pronunciation_or_hvo, to_pronunciation_or_hvo) -> bool:
    """Move a media file from one pronunciation to another pronunciation."""
```

---

## Usage Examples

### Basic Workflow: Adding Pictures to Senses

```python
from flexlibs2 import FLExProject

project = FLExProject()
project.OpenProject("MyDictionary", writeEnabled=True)

# Get an entry
entry = list(project.LexiconAllEntries())[0]
sense = entry.SensesOS[0]

# Add a picture to illustrate the sense
picture = project.Senses.AddPicture(
    sense,
    "/path/to/images/dog.jpg",
    caption="A friendly dog"
)

# Later, update the caption
project.Senses.SetPictureCaption(picture, "A brown dog", "en")

# Rename the image file
new_path = project.Senses.RenamePicture(picture, "brown_dog.jpg")
print(f"Picture renamed to: {new_path}")

project.CloseProject()
```

### Moving Pictures Between Senses

```python
# Scenario: You added a picture to the wrong sense
entry = list(project.LexiconAllEntries())[0]
sense1 = entry.SensesOS[0]  # "to run (move fast)"
sense2 = entry.SensesOS[1]  # "to run (operate a machine)"

# Get the picture (it's on sense1 but should be on sense2)
pictures = project.Senses.GetPictures(sense1)
running_person_pic = pictures[0]

# Move it to the correct sense
project.Senses.MovePicture(running_person_pic, sense1, sense2)

# Verify
print(f"Sense 1 pictures: {project.Senses.GetPictureCount(sense1)}")  # 0
print(f"Sense 2 pictures: {project.Senses.GetPictureCount(sense2)}")  # 1
```

### Adding Audio to Examples

```python
# Add an audio recording to an example sentence
entry = list(project.LexiconAllEntries())[0]
sense = entry.SensesOS[0]
example = sense.ExamplesOS[0]

# Add audio recording of the example being spoken
media = project.Examples.AddMediaFile(
    example,
    "/path/to/recordings/example_sentence.wav",
    label="Native speaker recording"
)

# Get all media files for the example
media_files = project.Examples.GetMediaFiles(example)
print(f"Example has {len(media_files)} audio files")
```

### Moving Media Between Examples

```python
# Move an audio file from one example to another
example1 = sense.ExamplesOS[0]
example2 = sense.ExamplesOS[1]

media_files = project.Examples.GetMediaFiles(example1)
# Move the first audio file to example2
project.Examples.MoveMediaFile(media_files[0], example1, example2)
```

### Working with LinkedFiles Directory

```python
# Get the LinkedFiles directory path
linked_files = project.GetLinkedFilesDir()
print(f"LinkedFiles: {linked_files}")
# Output: C:/Users/Me/Documents/FieldWorks/Projects/MyDict/LinkedFiles

# Access subdirectories
import os
audio_dir = os.path.join(linked_files, "AudioVisual")
pictures_dir = os.path.join(linked_files, "Pictures")

# List all picture files
for filename in os.listdir(pictures_dir):
    print(f"Picture file: {filename}")
```

### Renaming Media Files

```python
# Rename a media file and update all references
media = project.Media.Find("LinkedFiles/AudioVisual/temp_recording.wav")
if media:
    new_path = project.Media.RenameMediaFile(media, "pronunciation_run.wav")
    print(f"Renamed to: {new_path}")
    # Output: LinkedFiles/AudioVisual/pronunciation_run.wav

# If name conflicts, automatically adds suffix
media2 = project.Media.Find("LinkedFiles/AudioVisual/recording.wav")
new_path = project.Media.RenameMediaFile(media2, "pronunciation_run.wav")
print(new_path)
# Output: LinkedFiles/AudioVisual/pronunciation_run_1.wav (conflict avoided)
```

### Moving Pronunciation Audio

```python
# Move audio recording from one pronunciation variant to another
entry = list(project.LexiconAllEntries())[0]
pron1 = entry.PronunciationsOS[0]  # IPA: [rʌn]
pron2 = entry.PronunciationsOS[1]  # IPA: [ɹʌn] (different dialect)

# Get audio files
media_files = project.Pronunciations.GetMediaFiles(pron1)

# Move audio to the correct pronunciation variant
project.Pronunciations.MoveMediaFile(media_files[0], pron1, pron2)
```

---

## Common Workflows

### Workflow 1: Bulk Import Pictures for Senses

```python
import os
from pathlib import Path

project.OpenProject("MyDictionary", writeEnabled=True)

# Directory with images named after glosses
image_dir = Path("/path/to/sense_images/")

for entry in project.LexiconAllEntries():
    for sense in entry.SensesOS:
        gloss = project.Senses.GetGloss(sense, "en")

        # Look for matching image file
        image_file = image_dir / f"{gloss}.jpg"

        if image_file.exists():
            # Add picture to sense
            picture = project.Senses.AddPicture(
                sense,
                str(image_file),
                caption=gloss
            )
            print(f"Added picture for: {gloss}")

project.CloseProject()
```

### Workflow 2: Reorganize Misplaced Pictures

```python
# Find all senses with multiple pictures and let user choose which to keep
project.OpenProject("MyDictionary", writeEnabled=True)

for entry in project.LexiconAllEntries():
    if entry.SensesOS.Count > 1:
        # Check each sense
        for i, sense in enumerate(entry.SensesOS):
            pictures = project.Senses.GetPictures(sense)

            if len(pictures) > 1:
                gloss = project.Senses.GetGloss(sense, "en")
                print(f"\nSense {i+1}: '{gloss}' has {len(pictures)} pictures")

                # User could review and move pictures to other senses
                # For demo, move extra pictures to first sense
                if i > 0:
                    for pic in pictures[1:]:  # Keep first, move others
                        target_sense = entry.SensesOS[0]
                        project.Senses.MovePicture(pic, sense, target_sense)
                        print(f"  Moved picture to main sense")

project.CloseProject()
```

### Workflow 3: Add Audio to All Pronunciations

```python
# Batch add audio files to pronunciations
audio_dir = Path("/path/to/pronunciation_audio/")

project.OpenProject("MyDictionary", writeEnabled=True)

for entry in project.LexiconAllEntries():
    headword = project.LexEntry.GetHeadword(entry)

    # Look for audio file matching headword
    audio_file = audio_dir / f"{headword}.wav"

    if audio_file.exists():
        # Get first pronunciation (or create one)
        if entry.PronunciationsOS.Count > 0:
            pron = entry.PronunciationsOS[0]
        else:
            # Get IPA from somewhere, or skip
            continue

        # Add audio
        media = project.Pronunciations.AddMediaFile(
            pron,
            str(audio_file),
            label=f"Pronunciation of '{headword}'"
        )
        print(f"Added audio for: {headword}")

project.CloseProject()
```

### Workflow 4: Clean Up LinkedFiles Directory

```python
# Find orphaned media files (not referenced in database)
import os

project.OpenProject("MyDictionary", writeEnabled=False)

linked_dir = project.GetLinkedFilesDir()
audio_dir = os.path.join(linked_dir, "AudioVisual")
pictures_dir = os.path.join(linked_dir, "Pictures")

# Get all media files in database
db_files = set()
for media in project.Media.GetAll():
    internal_path = project.Media.GetInternalPath(media)
    db_files.add(internal_path)

# Check filesystem
fs_files = set()
for subdir in ["AudioVisual", "Pictures", "Others"]:
    dir_path = os.path.join(linked_dir, subdir)
    if os.path.exists(dir_path):
        for filename in os.listdir(dir_path):
            rel_path = f"LinkedFiles/{subdir}/{filename}"
            fs_files.add(rel_path)

# Find orphans
orphans = fs_files - db_files
print(f"\nOrphaned files (not in database): {len(orphans)}")
for orphan in sorted(orphans):
    print(f"  - {orphan}")

# Find missing
missing = db_files - fs_files
print(f"\nMissing files (in database but not on disk): {len(missing)}")
for miss in sorted(missing):
    print(f"  - {miss}")

project.CloseProject()
```

---

## Implementation Files

### Files to Modify:

1. **flexlibs/code/FLExProject.py**
   - Add `GetLinkedFilesDir()` (~line 1000)

2. **flexlibs/code/Shared/MediaOperations.py**
   - Add `RenameMediaFile()` (~line 700)

3. **flexlibs/code/Lexicon/LexSenseOperations.py**
   - Add `AddPicture()` (~line 1770)
   - Add `RemovePicture()` (~line 1850)
   - Add `MovePicture()` (~line 1900)
   - Add `SetPictureCaption()` (~line 1950)
   - Add `GetPictureCaption()` (~line 1980)
   - Add `RenamePicture()` (~line 2000)

4. **flexlibs/code/Lexicon/ExampleOperations.py**
   - Add `AddMediaFile()` (~line 995)
   - Add `RemoveMediaFile()` (~line 1050)
   - Add `MoveMediaFile()` (~line 1100)

5. **flexlibs/code/Lexicon/PronunciationOperations.py**
   - Add `MoveMediaFile()` (~line 770)

---

## Testing Checklist

For each method, verify:

### FLExProject.GetLinkedFilesDir()
- [ ] Returns correct path
- [ ] Works when LinkedFilesRootDir is set
- [ ] Works with default (ProjectFolder/LinkedFiles)
- [ ] Path exists on disk

### MediaOperations.RenameMediaFile()
- [ ] Renames file on disk
- [ ] Updates database InternalPath
- [ ] Handles filename conflicts (adds _1, _2, etc.)
- [ ] Preserves file extension
- [ ] Raises error if file doesn't exist
- [ ] Works with files in different subdirectories

### LexSenseOperations Picture Methods
- [ ] AddPicture: Copies file to Pictures folder
- [ ] AddPicture: Creates ICmPicture object
- [ ] AddPicture: Sets caption if provided
- [ ] AddPicture: Adds to PicturesOS collection
- [ ] RemovePicture: Removes from collection
- [ ] RemovePicture: Optionally deletes file
- [ ] MovePicture: Removes from source
- [ ] MovePicture: Adds to destination
- [ ] MovePicture: Preserves caption and file
- [ ] MovePicture: Handles same-sense (no-op)
- [ ] SetPictureCaption: Updates caption
- [ ] GetPictureCaption: Returns caption text
- [ ] RenamePicture: Calls Media.RenameMediaFile

### ExampleOperations Media Methods
- [ ] AddMediaFile: Copies file to AudioVisual folder
- [ ] AddMediaFile: Creates ICmFile object
- [ ] AddMediaFile: Adds to MediaFilesOS collection
- [ ] RemoveMediaFile: Removes from collection
- [ ] RemoveMediaFile: Optionally deletes file
- [ ] MoveMediaFile: Removes from source
- [ ] MoveMediaFile: Adds to destination
- [ ] MoveMediaFile: Handles same-example (no-op)

### PronunciationOperations.MoveMediaFile()
- [ ] Removes from source MediaFilesOS
- [ ] Adds to destination MediaFilesOS
- [ ] Handles same-pronunciation (no-op)
- [ ] Preserves file reference

---

## Documentation Updates Needed

1. **FUNCTION_REFERENCE.md**
   - Add all 12 new methods
   - Include examples for each
   - Cross-reference related methods

2. **MEDIA_MANAGEMENT_GUIDE.md** (new file)
   - Overview of media in FLEx
   - Pictures vs MediaFiles distinction
   - LinkedFiles directory structure
   - Common workflows
   - Best practices
   - Troubleshooting

3. **README.md** (if applicable)
   - Add media management to feature list
   - Link to media guide

4. **Operation class docstrings**
   - Update with media examples
   - Document new methods

---

## Dependencies

### Python Standard Library:
- `os` - File operations
- `shutil` - File copying
- `pathlib` - Path manipulation (optional)

### FLEx LCM Types:
- `ICmFile` - Media file references
- `ICmFileFactory` - Create media objects
- `ICmPicture` - Picture objects
- `ICmPictureFactory` - Create picture objects
- `ITsString` - Text strings (for captions)

### Already Imported:
All required types are already imported in the respective operation classes.

---

## Implementation Priority

### Phase 1 - Core Functionality (Implement First):
1. FLExProject.GetLinkedFilesDir()
2. LexSenseOperations.AddPicture()
3. LexSenseOperations.RemovePicture()
4. LexSenseOperations.MovePicture()
5. ExampleOperations.AddMediaFile()
6. ExampleOperations.RemoveMediaFile()
7. ExampleOperations.MoveMediaFile()

### Phase 2 - Enhanced Features:
8. MediaOperations.RenameMediaFile()
9. LexSenseOperations.RenamePicture()
10. LexSenseOperations.SetPictureCaption()
11. LexSenseOperations.GetPictureCaption()
12. PronunciationOperations.MoveMediaFile()

---

## Estimated Implementation Time

| Task | Lines of Code | Time Estimate |
|------|---------------|---------------|
| GetLinkedFilesDir() | ~10 | 15 min |
| RenameMediaFile() | ~60 | 1 hour |
| AddPicture() | ~40 | 45 min |
| RemovePicture() | ~25 | 30 min |
| MovePicture() | ~25 | 30 min |
| SetPictureCaption() | ~10 | 15 min |
| GetPictureCaption() | ~10 | 15 min |
| RenamePicture() | ~10 | 15 min |
| AddMediaFile() | ~35 | 45 min |
| RemoveMediaFile() | ~25 | 30 min |
| MoveMediaFile() (Examples) | ~25 | 30 min |
| MoveMediaFile() (Pronunciations) | ~25 | 30 min |
| **TOTAL** | **~300** | **~6 hours** |

Plus testing, documentation, and demo scripts: ~4 hours

**Total project**: ~10 hours

---

## Success Criteria

Implementation is complete when:

1. ✅ All 12 methods implemented
2. ✅ All methods compile without errors
3. ✅ Unit tests written and passing
4. ✅ Demo scripts created
5. ✅ Documentation updated
6. ✅ User can:
   - Access LinkedFiles directory
   - Add/remove/move pictures on senses
   - Add/remove/move media on examples
   - Rename media files with auto-update
   - Work with captions

---

## Notes

- Media files are NOT duplicated - only references are managed
- Physical files remain in LinkedFiles directory
- Move operations are database-only (don't move files on disk)
- Rename is the only operation that modifies the file system
- All operations are atomic (database + file system together)
- Error handling ensures consistency between DB and filesystem

This completes the media support enhancement design for flexlibs2.
