# FlexLibs2 LCM Capabilities - Code References

This document provides specific file and line references for each LCM capability mentioned in the main audit.

---

## Repository Interfaces

### ICmObjectRepository
- **Import:** `FLExProject.py:29`
- **Usage:** Generic object lookup by ID (Hvo)
- **Files using it:**
  - `Grammar/EnvironmentOperations.py` - lookup by Hvo
  - `Grammar/POSOperations.py` - reference resolution
  - Base usage pattern in Operations classes

### ILexEntryRepository
- **Import:** `FLExProject.py:30`
- **Usage:** Lexicon entry access, query operations
- **Files:** Multiple lexicon operations

### IWfiWordformRepository
- **Import:** `FLExProject.py:32`
- **Usage:** Wordform inventory queries
- **Files:** `Wordform/WfiWordformOperations.py`

### IWfiAnalysisRepository
- **Import:** `FLExProject.py:34`
- **Usage:** Wordform analysis access
- **Files:** `Wordform/WfiAnalysisOperations.py`

### ICmPossibilityRepository
- **Import:** `FLExProject.py:39`
- **Usage:** POS, semantic domains, list items
- **Files:** `Grammar/POSOperations.py`, `Lexicon/LexEntryOperations.py`, etc.

### ITextRepository
- **Import:** `FLExProject.py:43`
- **Usage:** Text document access
- **Files:** `TextsWords/TextOperations.py`

### ISegmentRepository
- **Import:** `FLExProject.py:45`
- **Usage:** Text segment lookup
- **Files:** `TextsWords/SegmentOperations.py`

### ILexRefTypeRepository
- **Import:** `FLExProject.py:38`
- **Usage:** Reference type definitions
- **Files:** `Lexicon/LexReferenceOperations.py`

---

## Factory Interfaces

### ICmPossibilityListFactory
- **Import:** `Grammar/GramCatOperations.py:19`
- **Conditional:** `Lexicon/LexReferenceOperations.py:120` (local import)
- **Usage:** Create POS lists, semantic domains
- **Usage Pattern:**
  ```python
  from SIL.LCModel import ICmPossibilityListFactory
  factory = self.project.ObjectFactory(ICmPossibilityListFactory)
  new_list = factory.Create()
  ```

### IPartOfSpeechFactory
- **Import:** `Grammar/POSOperations.py:15`
- **Usage:** Create parts of speech
- **Pattern:** Conditional import in Create() method
- **Location:** `Grammar/POSOperations.py:60-75`

### IPhEnvironmentFactory
- **Import:** `Grammar/EnvironmentOperations.py:15`
- **Usage:** Create phonological environments
- **Location:** `Grammar/EnvironmentOperations.py:85-100`

### IMoStemAllomorphFactory
- **Import:** `Lexicon/AllomorphOperations.py` (line ~130, local)
- **Usage:** Create stem allomorphs
- **Location:** Conditional import in Create method

### IMoAffixAllomorphFactory
- **Import:** `Lexicon/AllomorphOperations.py` (line ~150, local)
- **Usage:** Create affix allomorphs
- **Location:** Conditional import in Create method

### IStTextFactory / IStTxtParaFactory
- **Imports:** `TextsWords/ParagraphOperations.py` (local conditional)
- **Usage:** Create text and paragraph objects
- **Location:** In Create() methods for text/paragraph operations

### IScrBookAnnotationsFactory
- **Import:** Scripture operations (if implemented)
- **Usage:** Scripture annotation creation
- **Status:** Minimal coverage in current codebase

### IDsDiscourseFactory
- **Import:** `Discourse/ConstChartOperations.py` (line ~220, conditional)
- **Usage:** Create discourse structures
- **Location:** Conditional import in Create method

### ILexEntryRefFactory
- **Import:** `FLExProject.py:430` (conditional in method)
- **Usage:** Create lexical references
- **Location:** Internal method for reference creation

---

## Manager/Service Interfaces

### IUndoStackManager
- **Import:** `FLExProject.py:53`
- **Usage:** Save changes, undo/redo stack
- **Called:** `FLExProject.py:273` in `CloseProject()`
  ```python
  def CloseProject(self):
      if self.writeEnabled:
          usm = self.ObjectRepository(IUndoStackManager)
          usm.Save()
  ```
- **Status:** Internal, not exposed to users
- **Note:** Automatic save-on-close, no manual control

### IFwMetaDataCacheManaged
- **Import:** `FLExProject.py:62`
- **Usage:** Metadata cache access (not actively used)
- **Status:** Imported but not utilized
- **Recommendation:** Could enable schema introspection

---

## Text/String Interfaces

### ITsString
- **Import:** Multiple files
  - `FLExProject.py:65`
  - `Grammar/GramCatOperations.py:18`
  - `Lexicon/AllomorphOperations.py:18`
  - Plus 40+ more files
- **Usage:** Immutable multi-lingual text
- **Wrapped by:** `BestStr()` in FLExProject.py:1831
- **Example usage in wrapper:** `FLExProject.py:166-192`
  ```python
  from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr
  lexEntryValue = ITsString(lexForm.Form.get_String(WSHandle)).Text
  newValue = convert_headword(lexEntryValue)
  mkstr = TsStringUtils.MakeString(newValue, WSHandle)
  lexForm.Form.set_String(WSHandle, mkstr)
  ```

### ITsStrBldr
- **Import:** `FLExProject.py:65`
- **Usage:** String builder for mutable text
- **Status:** Imported but hidden from users
- **Recommendation:** Document as power-user feature

### TsStringUtils
- **Import:** `FLExProject.py:66`
- **Usage:** Text utility functions (MakeString, GetText)
- **Used in:** 50+ files for text manipulation
- **Common calls:** `TsStringUtils.MakeString(text, ws_handle)`

### IMultiUnicode / IMultiString
- **Import:** Infrastructure, not direct user imports
- **Usage:** Multi-language string containers
- **Wrapped by:** Multi-lingual property access methods

---

## Exception Types

### LcmInvalidClassException
- **Import:** `FLExProject.py:49`
- **Handling:** Not exposed, internal only
- **Usage:** Validate object types during casting

### LcmInvalidFieldException
- **Import:** `FLExProject.py:50`
- **Handling:** Not exposed, internal only
- **Usage:** Validate field access

### LcmFileLockedException
- **Import:** `FLExProject.py:51`
- **Caught:** `FLExProject.py:230-231`
  ```python
  except LcmFileLockedException as e:
      raise FP_FileLockedError()
  ```
- **Wrapped as:** `FP_FileLockedError` (user-friendly)

### LcmDataMigrationForbiddenException
- **Import:** `FLExProject.py:52`
- **Caught:** `FLExProject.py:233-241`
  ```python
  except (LcmDataMigrationForbiddenException, WorkerThreadException) as e:
      raise FP_MigrationRequired()
  ```
- **Wrapped as:** `FP_MigrationRequired` (user-friendly)

### WorkerThreadException
- **Import:** `FLExProject.py:67`
- **Handling:** Caught with `LcmDataMigrationForbiddenException`
- **Usage:** Background task errors

---

## Data Type Tags

### LexEntryTags
- **Import:** `FLExProject.py:30`
- **Usage:** Field name constants for lexical entries
- **Example:** Navigate entry properties by name
- **Status:** Never exposed to users

### LexSenseTags
- **Import:** `FLExProject.py:31`
- **Usage:** Field name constants for senses
- **Status:** Internal only

### WfiWordformTags
- **Import:** `FLExProject.py:32`
- **Usage:** Wordform property names
- **Status:** Internal only

### WfiAnalysisTags
- **Import:** `FLExProject.py:34`
- **Usage:** Analysis property names
- **Status:** Internal only

### MoFormTags / LexExampleSentenceTags / TextTags / ReversalIndexEntryTags
- **Imports:** `FLExProject.py` (lines 31-46)
- **Usage:** Domain-specific property constants
- **Status:** All internal only

---

## Cellar (Property Type System)

### CellarPropertyType
- **Import:**
  - `FLExProject.py:57`
  - `FLExLCM.py:34`
  - `lcm_casting.py`
- **Usage:** Property type enumeration
- **Example in FLExLCM.py:46-48:**
  ```python
  CellarStringTypes = {CellarPropertyType.String, }
  CellarMultiStringTypes = {CellarPropertyType.MultiUnicode,
                            CellarPropertyType.MultiString}
  ```
- **Status:** Internal property introspection only

### CellarPropertyTypeFilter
- **Import:** `FLExProject.py:58`
- **Usage:** Filter properties by type
- **Status:** Internal only

---

## Utility Classes

### ReflectionHelper
- **Import:**
  - `FLExProject.py:67`
  - `lcm_casting.py` (implicit usage)
- **Usage:** .NET reflection for type casting
- **Location:** Used in casting operations for polymorphic types

### WorkerThreadException
- **Already covered above** (under Exceptions)

### VersionInfoProvider
- **Import:** `FLExGlobals.py:159`
- **Usage:** Get FieldWorks version information
- **Location:** `FLExGlobals.py:159-164`
  ```python
  from SIL.FieldWorks.Common.FwUtils import VersionInfoProvider
  vip = VersionInfoProvider(Assembly.GetAssembly(VersionInfoProvider), False)
  FWShortVersion = System.Version(vip.ShortNumericAppVersion)
  ```

### FwUtils / FwDirectoryFinder / FwRegistryHelper
- **Imports:** `FLExInit.py:24-25`, `FLExLCM.py:38-40`
- **Usage:** File paths, registry access, utility functions
- **Status:** Infrastructure initialization only

---

## FieldWorks UI/Infrastructure

### FwLcmUI
- **Import:** `FLExLCM.py:41`
- **Usage:** LCM user interface integration
- **Location:** `FLExLCM.py:84`
  ```python
  ui = FwLcmUI(None, th)  # IHelpTopicProvider, ISynchronizeInvoke
  ```
- **Status:** Project initialization only

### ChooseLangProjectDialog
- **Import:** `FLExLCM.py:42`
- **Usage:** FW project selection dialog
- **Status:** Not used (TODO in FLExLCM.py:53)
- **Reference:** `FLExLCM.py:53-54`
  ```python
  # TODO: Use FW Project Chooser (ChooseLangProjectDialog())
  #       and handle network drives
  ```

### ThreadHelper
- **Import:** `FLExLCM.py:38`
- **Usage:** Thread synchronization for UI operations
- **Location:** `FLExLCM.py:83`
  ```python
  th = ThreadHelper()
  ui = FwLcmUI(None, th)
  ```

### ProgressDialogWithTask
- **Import:** `FLExLCM.py:37`
- **Usage:** Show progress dialog during project opening
- **Location:** `FLExLCM.py:90`
  ```python
  dlg = ProgressDialogWithTask(th)
  ```

### ProjectId
- **Import:** `FLExLCM.py:36`
- **Usage:** Project identifier for opening
- **Location:** `FLExLCM.py:81`
  ```python
  projId = ProjectId(projectFileName)
  ```

### FwDirectoryFinder
- **Import:** `FLExLCM.py:39`
- **Usage:** Find FW installation directories
- **Location:** `FLExLCM.py:85`
  ```python
  dirs = FwDirectoryFinder.LcmDirectories
  ```

---

## Writing Systems

### WritingSystemDefinition
- **Import:** `FLExInit.py:15`
- **Note:** Comment says "Fixed: was IWritingSystemDefinition"
- **Usage:** Writing system configuration
- **Status:** Initialized but minimal direct use

### Sldr
- **Import:** `FLExInit.py:16`
- **Usage:** SLDR (Script Library Database Reference) integration
- **Location:** `FLExInit.py`
- **Status:** Initialization only

### SpecialWritingSystemCodes
- **Import:** `FLExProject.py:48`
- **Usage:** Special WS codes (e.g., for audio)
- **Example:** `en-Zxxx-x-audio` for audio content
- **Location:** Used in `AllomorphOperations.py` for audio allomorphs

---

## Casting Operations

### lcm_casting.py Module
- **Location:** `/d/Github/_Projects/_LEX/flexlibs2/flexlibs2/code/lcm_casting.py`
- **Purpose:** Type casting for polymorphic LCM objects
- **Key Function:** `cast_to_concrete()` - convert base interface to concrete type
- **Imports from SIL.LCModel (lines 104-150):**

```python
# MSA types
IMoStemMsa, IMoDerivAffMsa, IMoInflAffMsa, IMoUnclassifiedAffixMsa

# Allomorph types
IMoStemAllomorph, IMoAffixAllomorph, IMoAffixForm

# Phonological rule types
IPhRegularRule, IPhMetathesisRule, IPhReduplicationRule
IPhSimpleContextSeg, IPhSimpleContextNC, IPhSegRuleRHS

# Compound rule types
IMoEndoCompound, IMoExoCompound

# Morphosyntactic prohibition types
(MoAdhocProhibGr, MoAdhocProhibMorph, MoAdhocProhibAllomorph - partially listed)
```

**Usage Pattern:**
```python
from flexlibs2.code.lcm_casting import cast_to_concrete

for msa in entry.MorphoSyntaxAnalysesOC:
    concrete = cast_to_concrete(msa)  # Returns actual type (MoStemMsa, etc.)
```

---

## Object Access Methods in FLExProject

### ObjectFactory()
- **Location:** `FLExProject.py` (inherited from BaseOperations)
- **Usage:** Get factory for creating objects
- **Example:**
  ```python
  factory = project.ObjectFactory(ICmPossibilityListFactory)
  ```

### ObjectRepository()
- **Location:** `FLExProject.py` (inherited from BaseOperations)
- **Usage:** Get repository for querying objects
- **Example:**
  ```python
  repo = project.ObjectRepository(ILexEntryRepository)
  ```

### WSHandle()
- **Location:** `FLExProject.py:1870+`
- **Usage:** Get writing system handle for text operations
- **Example:**
  ```python
  ws_handle = project.WSHandle('en')
  text = TsStringUtils.MakeString(value, ws_handle)
  ```

---

## Known TODOs with Code References

### 1. Linux Flatpak Support
- **File:** `/d/Github/_Projects/_LEX/flexlibs2/flexlibs2/code/FLExGlobals.py`
- **Lines:** 102-105
- **Issue:** FW now uses flatpak on Linux, old path logic doesn't work
- **Current:** Only Windows/macOS supported

### 2. Project Chooser Dialog
- **File:** `/d/Github/_Projects/_LEX/flexlibs2/flexlibs2/code/FLExLCM.py`
- **Line:** 53-54
- **Issue:** Using simple file listing instead of FW native dialog
- **Enhancement:** Would use `ChooseLangProjectDialog()` and support network drives

---

## Summary Statistics

**Total Files with SIL Imports:** 72
**Total Code Lines with SIL References:** 500+
**Repositories Imported:** 9
**Factories Imported:** 12
**Manager/Services:** 2
**Text Interfaces:** 4
**Exception Types:** 5
**Tag Classes:** 11
**Cellar Classes:** 2
**Utility Classes:** 7+
**UI/Infrastructure:** 10+
**Writing System Classes:** 2
**Casting/Helper Modules:** 3 (lcm_casting.py, CastingOperations.py, PythonicWrapper.py)

---

## Cross-Reference: By Domain

### Grammar Domain Files
- `Grammar/GramCatOperations.py` - ICmPossibility, ICmPossibilityFactory
- `Grammar/POSOperations.py` - IPartOfSpeechFactory, IPartOfSpeech, ILexEntryRepository
- `Grammar/EnvironmentOperations.py` - IPhEnvironmentFactory, IPhEnvironment, ICmObjectRepository
- `Grammar/PhonologicalRuleOperations.py` - Uses casting for polymorphic rules
- `Grammar/NaturalClassOperations.py` - References and properties
- `Grammar/InflectionFeatureOperations.py` - Grammatical features
- `Grammar/MorphRuleOperations.py` - Morphological rules

### Lexicon Domain Files
- `Lexicon/LexEntryOperations.py` - Core lexical operations
- `Lexicon/AllomorphOperations.py` - IMoStemAllomorphFactory, IMoAffixAllomorphFactory
- `Lexicon/LexReferenceOperations.py` - ICmPossibilityListFactory
- `Lexicon/ExampleOperations.py` - Example sentences
- `Lexicon/EtymologyOperations.py` - Etymology references

### TextsWords Domain
- `TextsWords/TextOperations.py` - ITextRepository
- `TextsWords/ParagraphOperations.py` - IStTextFactory, IStTxtParaFactory
- `TextsWords/SegmentOperations.py` - ISegmentRepository

### Notebook Domain
- `Notebook/*.py` - Uses ICmObjectRepository for person/location lookups

### Discourse Domain
- `Discourse/ConstChartOperations.py` - IDsDiscourseFactory

---

## How to Use This Reference

1. **Finding where something is imported:**
   - Search this document for the interface/class name
   - Get the file path and line number
   - Use `Read` tool with that path to see context

2. **Understanding usage patterns:**
   - Check "Usage Pattern" sections
   - Look at code examples provided
   - Follow cross-references to see how operations use imports

3. **Checking for missing functionality:**
   - Review "Partially Exposed" and "Not Exposed" sections
   - Check "Known TODOs" for planned improvements
   - Use "Recommendation" sections to decide if something should be wrapped

4. **Adding new Operations classes:**
   - Find similar operation in "Cross-Reference: By Domain"
   - Check what imports it uses
   - Follow the local import pattern from `AllomorphOperations.py` for factories
   - See `lcm_casting.py` for casting examples if dealing with polymorphic types

