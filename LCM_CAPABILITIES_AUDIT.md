# FlexLibs2 LCM Capabilities Audit

**Date:** 2025-03-16
**Scope:** Analysis of SIL.LCModel (Language and Culture Model) capabilities imported into flexlibs2, their exposure via the public API, and internal usage patterns.
**Codebase:** flexlibs2/code directory (101 Python files, 64 Operations classes)

---

## Executive Summary

This audit reveals a **well-designed abstraction layer** that intentionally hides the complexity of the LCM API while providing comprehensive access through a user-friendly public interface. The project imports **25+ distinct SIL modules** encompassing:

- **Repository pattern** for data access (collections/queries)
- **Factory pattern** for object creation
- **Manager/Service interfaces** for metadata and system operations
- **Utility classes** for text handling and reflection
- **Exception types** for consistent error handling

### Key Findings

- **Fully exposed:** 57 data domain operations (POS, LexEntry, Texts, etc.)
- **Partially exposed:** Advanced features (undo/redo, caching, metadata)
- **Not exposed:** Low-level LCM infrastructure and developer-only services
- **Low risk exposure:** The abstraction prevents direct access to internal FW infrastructure
- **Recommended:** Document advanced access patterns for power users

---

## Import Statistics

### Summary
- **Total SIL Modules Imported:** 25
- **Total Python Files with SIL Imports:** 72
- **Total Classes/Interfaces Imported:** 90+
- **Operations Classes in API:** 57 (exposed via FLExProject properties)
- **Helper Classes:** 7 (CastingOperations, PythonicWrapper, etc.)

### Distribution by Module

| Module Category | Count | Files | Status |
|---|---|---|---|
| **SIL.LCModel** (core data types) | 45+ | 70 | Fully integrated |
| **SIL.LCModel.Core.KernelInterfaces** | 4 | 50+ | Heavily used for text |
| **SIL.LCModel.Core.Text** | 1 | 50+ | String handling |
| **SIL.LCModel.Infrastructure** | 2 | 3 | Advanced/internal |
| **SIL.LCModel.Core.Cellar** | 2 | 3 | Property type system |
| **SIL.LCModel.Utils** | 2 | 2 | Reflection/threading |
| **SIL.FieldWorks.*** | 10+ | 8 | Project/UI integration |
| **SIL.WritingSystems** | 2 | 2 | Language data |

---

## Detailed Import Audit

### Category 1: Repository Interfaces (Data Access)

**Status:** [OK] Exposed through Operations classes, internal access only

#### Repositories Used
```
ICmObjectRepository          - Generic object lookup by ID
ILexEntryRepository          - Lexicon entry access (POSOperations, LexEntryOperations)
ILexRefTypeRepository        - Reference type definitions
IWfiWordformRepository       - Wordform inventory
IWfiAnalysisRepository       - Wordform analysis access
ICmPossibilityRepository     - POS, semantic domains, lists
ITextRepository              - Text/document access
ISegmentRepository           - Text segment lookup
IReversalIndex, IReversalIndexEntry - Reversal index access
```

**Exposure:**
- **Public API:** Users access these through `.GetAll()`, `.Find()`, `.Create()` methods in Operations classes
- **Files:** 70+ files (nearly all Operations classes)
- **Risk Level:** MINIMAL - repositories accessed through safe wrapper methods
- **Usage Pattern:** `ICmObjectRepository(IHvo)` used in:
  - `Grammar/EnvironmentOperations.py` - lookup by Hvo
  - `Grammar/POSOperations.py` - reference resolution
  - Multiple Lexicon operations

**Example Usage:**
```python
# NOT exposed to users - internal only
from SIL.LCModel import ICmObjectRepository
repo = project.ObjectRepository(ICmObjectRepository)
obj = repo.GetObject(hvo)

# Users get this instead:
pos_list = project.POS.GetAll()
```

---

### Category 2: Factory Interfaces (Object Creation)

**Status:** [OK] Fully wrapped in Create/Update methods

#### Factories Used
```
ICmPossibilityListFactory    - Create POS lists, semantic domains, lists
IPartOfSpeechFactory         - Create parts of speech
IPhEnvironmentFactory        - Create phonological environments
IMoStemAllomorphFactory      - Create stem allomorphs
IMoAffixAllomorphFactory     - Create affix allomorphs
IStTextFactory               - Create text blocks
IStTxtParaFactory            - Create paragraphs
ILexEntryRefFactory          - Create lexical references
IScrBookAnnotationsFactory   - Scripture annotations
IDsDiscourseFactory          - Discourse structures
IMoStemMsaFactory            - Create stem MSAs
IMoAffixAllomorphFactory     - Affix allomorphs
```

**Exposure:**
- **Public API:** Never exposed directly - wrapped in `Create()` methods
- **Files:** Conditional imports in 12 Operations classes
- **Risk Level:** MINIMAL - factory calls wrapped in validation logic
- **Usage Pattern:** Imported locally within Create methods:

```python
# File: Lexicon/AllomorphOperations.py (line ~90)
def Create(self, allomorph_form, allomorph_type, lexeme=None):
    if self.project.WriteEnabled:
        try:
            from SIL.LCModel import IMoStemAllomorphFactory
            factory = self.project.ObjectFactory(IMoStemAllomorphFactory)
            # Create wrapped in error handling
```

**Design Pattern:** Local imports inside methods to avoid import-time dependencies

---

### Category 3: Manager/Service Interfaces

**Status:** [PARTIAL] Some exposed, most not exposed

#### Managers Imported
```
IUndoStackManager           - Undo/redo stack (save operations)
IFwMetaDataCacheManaged     - Metadata cache access
```

**IUndoStackManager Usage:**
- **Location:** `FLExProject.py` line 273
- **Exposure:** NOT exposed in public API
- **Purpose:** Called during `CloseProject()` to save changes
- **Risk:** LOW - only called internally by framework

```python
# FLExProject.py - internal only
usm = self.ObjectRepository(IUndoStackManager)
usm.Save()
```

**IFwMetaDataCacheManaged Usage:**
- **Location:** `FLExProject.py` import only
- **Exposure:** NOT exposed
- **Purpose:** Field metadata and type information
- **Recommendation:** Could be exposed for schema introspection

---

### Category 4: Text/String Interfaces

**Status:** [OK] Core text handling well-wrapped

#### Text Interfaces
```
ITsString               - Immutable multi-lingual text
ITsStrBldr              - String builder (mutable)
IMultiUnicode           - Unicode string collection
IMultiString            - Multi-language strings
TsStringUtils           - Text utilities (MakeString, GetText)
```

**Exposure:**
- **Public API:** NOT exposed to users - hidden behind `BestStr()` and helper methods
- **Files:** 50+ files (nearly all)
- **Usage Pattern:** Wrapped in convenience methods:

```python
# FLExProject.py (line 1831)
def BestStr(self, stringObj):
    """Generic string function for MultiUnicode and MultiString"""
    # Users never see ITsString directly

# Grammar/GramCatOperations.py - example internal use
from SIL.LCModel.Core.Text import TsStringUtils
from SIL.LCModel.Core.KernelInterfaces import ITsString
ws_handle = self.project.WSHandle('en')
ts = TsStringUtils.MakeString(text_value, ws_handle)
```

**Recommendation:** Document text handling as advanced topic for power users who need `ITsString` directly

---

### Category 5: Exception Types

**Status:** [OK] Standard exceptions imported and wrapped

#### Exception Types
```
LcmInvalidClassException         - Invalid object type
LcmInvalidFieldException         - Invalid field access
LcmFileLockedException           - Project locked by another process
LcmDataMigrationForbiddenException - Project needs FW migration
WorkerThreadException            - Background task failure
```

**Exposure:**
- **Public API:** Custom wrapper exceptions (FP_ReadOnlyError, FP_ParameterError)
- **Files:** `FLExProject.py` imports and handles
- **Usage Pattern:** Caught and re-raised as more user-friendly exceptions:

```python
# FLExProject.py (line 230-241)
except LcmFileLockedException as e:
    raise FP_FileLockedError()  # User-friendly message

except LcmDataMigrationForbiddenException as e:
    raise FP_MigrationRequired()  # Clear action required
```

**Risk:** LOW - exceptions used correctly for error handling

---

### Category 6: Data Type Tags/Constants

**Status:** [OK] Used internally for field navigation

#### Tag Classes (Property Names)
```
LexEntryTags            - Lexicon entry field names
LexSenseTags            - Sense field names
WfiWordformTags         - Wordform field names
WfiGlossTags            - Gloss field names
WfiAnalysisTags         - Analysis field names
WfiMorphBundleTags      - Morpheme bundle field names
MoFormTags              - Morpheme form field names
LexExampleSentenceTags  - Example sentence field names
TextTags                - Text field names
ReversalIndexEntryTags  - Reversal entry field names
CellarPropertyType      - Type system for properties (String, MultiUnicode, etc.)
```

**Exposure:**
- **Not exposed:** Users never reference these directly
- **Files:** Used in `lcm_casting.py` and Operations classes
- **Purpose:** Navigate LCM object properties by name
- **Risk:** LOW - internal use only

**Example:**
```python
# Users don't need to know about these:
from SIL.LCModel import LexEntryTags
# Internal access pattern:
entry.MorphoSyntaxAnalysesOC  # Navigate via properties, not tags
```

---

### Category 7: Cellar (Property Type System)

**Status:** [OK] Low-level property system, wrapped

#### Cellar Classes
```
CellarPropertyType          - Enum: String, MultiUnicode, MultiString, Reference, etc.
CellarPropertyTypeFilter    - Property filtering
```

**Exposure:**
- **Not exposed:** Internal property introspection only
- **Files:** 3 files (FLExProject.py, FLExLCM.py, lcm_casting.py)
- **Purpose:** Determine field types for validation
- **Risk:** LOW - only for internal type checking

```python
# FLExLCM.py - internal use
from SIL.LCModel.Core.Cellar import CellarPropertyType

CellarStringTypes = {CellarPropertyType.String,}
CellarMultiStringTypes = {CellarPropertyType.MultiUnicode, CellarPropertyType.MultiString}
```

---

### Category 8: Utility Classes

**Status:** [OK] Minimal exposure, used internally

#### Utility Imports
```
ReflectionHelper        - .NET reflection utilities for casting
WorkerThreadException   - Thread exception handling
VersionInfoProvider     - Get FieldWorks version info
FwUtils, FwDirectoryFinder, etc. - File/registry operations
```

**Exposure:**
- **Not exposed:** Internal utilities only
- **Files:** Centralized in FLExProject.py and FLExLCM.py
- **Risk:** LOW - wrapper functions insulate users

---

### Category 9: FieldWorks UI/Infrastructure

**Status:** [MINIMAL] Intentionally excluded from user API

#### UI/Infrastructure Classes
```
FwLcmUI                     - LCM user interface integration
ChooseLangProjectDialog     - Project selection dialog
ThreadHelper                - Thread synchronization
ProgressDialogWithTask      - Progress reporting dialog
ProjectId                   - Project identifier
FwDirectoryFinder          - FW installation paths
FwRegistryHelper           - Registry access
```

**Exposure:**
- **Not exposed:** Project initialization only (FLExLCM.py, FLExInit.py)
- **Files:** 8 files (mostly initialization)
- **Purpose:** Open projects, find FieldWorks installation
- **Risk:** MINIMAL - infrastructure, not data

**TODO Found:** Line 53 of FLExLCM.py
```python
# TODO: Use FW Project Chooser (ChooseLangProjectDialog())
#       and handle network drives
```
This suggests future enhancement to use native FW project selection dialog.

---

### Category 10: Writing Systems

**Status:** [OK] Minimal exposure

#### Writing System Classes
```
WritingSystemDefinition     - Writing system properties
Sldr                        - SLDR (Script Library Database Reference) integration
SpecialWritingSystemCodes   - Special codes (e.g., for audio)
```

**Exposure:**
- **Not exposed:** Only used internally for writing system lookup
- **Files:** Initialization and some Lexicon operations
- **Risk:** LOW - read-only usage

```python
# FLExInit.py
from SIL.WritingSystems import Sldr
# Internally used to initialize writing systems
```

---

## Exposed vs. Unexposed Capabilities

### Fully Exposed (57 Operations)

All accessed through `project.DOMAIN.METHOD()` pattern:

**Grammar Domain (13 ops)**
- POS, Phonemes, NaturalClasses, Environments, Allomorphs
- MorphRules, InflectionFeatures, GramCat, PhonRules, AffixTemplates
- CompoundRules, AdHocProhibitions

**Lexicon Domain (11 ops)**
- LexEntry, Senses, Examples, LexReferences, Etymology
- Variants, Pronunciations, Confidence, Filters

**TextsWords Domain (5 ops)**
- Texts, Wordforms, WfiAnalyses, Paragraphs, Segments

**Notebook Domain (5 ops)**
- DataNotebook, Notes, Annotations, Person, Location

**Lists Domain (6 ops)**
- Agents, PossibilityLists, SemanticDomains, TranslationTypes
- Publications, Media

**System Domain (7 ops)**
- WritingSystems, CustomFields, AnnotationDefs, Checks
- ProjectSettings, Anthropology, Discourse

**Discourse Domain (8 ops)**
- ConstCharts, ConstChartRows, ConstChartWordGroups
- ConstChartMovedText, ConstChartTags, ConstChartClauseMarkers
- (Plus Reversal/ReversalIndexes)

### Partially Exposed

**Undo/Redo Stack**
- `IUndoStackManager` imported in FLExProject.py
- Called only in `CloseProject()` for automatic save
- NOT exposed in public API - saves are automatic
- **Recommendation:** Document that changes auto-save on `CloseProject()`

**Metadata Cache**
- `IFwMetaDataCacheManaged` imported but not used actively
- Could enable schema introspection if needed
- **Recommendation:** Consider exposing for "what fields does X object have?" queries

**Advanced Text Building**
- `ITsStrBldr` (string builder) imported but hidden
- Available via `FLExProject.project` for advanced users
- **Recommendation:** Document power-user access pattern

### Not Exposed (Low Priority)

**Project Service Layer**
- Core project cache and object factory accessed via `project.ObjectFactory()` and `project.ObjectRepository()`
- These are available but documented as "advanced use only"
- Users can access if needed but shouldn't normally need them

**Low-Level Casting**
- `lcm_casting.py` module provides `cast_to_concrete()` for polymorphic types
- Internal use only, but documented in module docstring
- Power users can import if they need to work with base interfaces

---

## Usage Patterns

### Pattern 1: Safe Repository Access
Most common pattern - wrapped in Operations classes:
```python
# Files: 70+ Operations classes
# Example: Grammar/POSOperations.py
repo = self.project.ObjectRepository(ILexEntryRepository)
entry = repo.GetObject(hvo)
```
**Risk:** LOW - limited to read access, wrapped with validation

### Pattern 2: Factory + Error Handling
Object creation wrapped with write checks:
```python
# Example: Lexicon/AllomorphOperations.py (line ~90)
def Create(self, form_text):
    if not self.project.WriteEnabled:
        raise FP_ReadOnlyError()
    from SIL.LCModel import IMoStemAllomorphFactory
    factory = self.project.ObjectFactory(IMoStemAllomorphFactory)
    # Create with validation...
```
**Risk:** MINIMAL - write permission checked before factory use

### Pattern 3: Direct Project Access (Advanced)
Available for power users but discouraged:
```python
# Example: Some operations use directly
lexDB = project.lexDB  # Direct access to LexDb object
# Then access properties directly
```
**Risk:** MEDIUM - bypasses wrapper validation, needs user understanding

### Pattern 4: ServiceLocator Pattern
Projects use `ObjectFactory()` and `ObjectRepository()` getters:
```python
# FLExProject.py (line 273)
usm = self.ObjectRepository(IUndoStackManager)
usm.Save()

# Grammar/EnvironmentOperations.py
repo = self.project.ObjectRepository(ICmObjectRepository)
```
**Risk:** LOW - contained in framework code, not user-facing

### Pattern 5: Local Imports (Dependency Injection)
Factories imported only when needed:
```python
# AllomorphOperations.py - conditional import
def Create(self, ...):
    from SIL.LCModel import IMoStemAllomorphFactory
    factory = self.project.ObjectFactory(IMoStemAllomorphFactory)
```
**Benefit:** Avoids circular imports, allows optional functionality
**Risk:** LOW - internal pattern only

---

## TODOs and Known Limitations

### Found in Codebase

**1. FLExGlobals.py (Lines 102-105) - LINUX SUPPORT**
```
TODO: First attempt at Linux support.
As of Apr2024, FW installation has changed to use flatpak
and this no longer works.
```
**Impact:** Linux support incomplete, requires FW flatpak support
**Priority:** MEDIUM - affects non-Windows users
**Workaround:** Windows/macOS only for now

**2. FLExLCM.py (Line 53) - PROJECT CHOOSER DIALOG**
```
TODO: Use FW Project Chooser (ChooseLangProjectDialog())
      and handle network drives
```
**Impact:** Simple file listing instead of FW dialog, no network support
**Priority:** LOW - functional workaround exists
**Enhancement:** Would improve UX with native FW dialog

### Implicit Limitations (Not Documented)

**1. No Direct Access to:**
- Undo stack manipulation (auto-save only)
- Cache invalidation (auto-managed)
- Background task management (single-threaded)

**2. Incomplete Domain Coverage:**
- Scripture domain has minimal operations
- Some discourse analysis features limited
- Constraint-based morphology not wrapped

---

## Risk Assessment

### Critical (Must Be Protected)
- [✓] `IUndoStackManager` - Protected, no user access
- [✓] Thread/cache management - Hidden in framework
- [✓] Direct cast operations - Wrapped in `lcm_casting.py`, internal only

### High (Should Limit Exposure)
- [OK] Factory interfaces - Wrapped, write-enabled only
- [OK] Repository access - Wrapped in Operations classes
- [OK] Exception types - Custom wrappers used

### Medium (Can Be Exposed with Documentation)
- [ ] `ITsStrBldr` - Advanced text building (document as power-user feature)
- [ ] `IFwMetaDataCacheManaged` - Schema introspection (expose as utility if needed)
- [ ] Direct `.project` access - Clearly mark as "use at own risk"

### Low (Safe to Expose)
- [✓] Tag classes (LexEntryTags, etc.) - Already internal, safe
- [✓] Property type system - Read-only metadata
- [✓] Version info - Read-only constants

---

## Recommendations

### 1. Documentation Enhancements [Priority: HIGH]

**Suggestion:** Create `docs/ADVANCED_LCM_ACCESS.md`
- Document `.project`, `.lp`, `.lexDB` direct access patterns
- Show `ITsString` usage for users who need it
- Explain when to use raw LCM vs. Operations classes
- Provide examples of accessing data not yet wrapped

**Suggestion:** Document in CLAUDE.md under new section "Power User Access"
```
## Power User Access

For functionality not yet wrapped in Operations classes,
you can access the LCM API directly:

project.project        # Raw LcmCache
project.lp             # LangProject
project.lexDB          # LexDb

Use sparingly and document your usage!
```

### 2. Feature Completion [Priority: MEDIUM]

**Metadata Introspection:**
- Expose `IFwMetaDataCacheManaged` as optional utility
- Enable "schema discovery" for generated tools
- Useful for documentation generation

**Advanced Text Handling:**
- Create `TextBuilderOperations` wrapper for `ITsStrBldr`
- Document multi-lingual text patterns clearly
- Examples of handling field-specific writing systems

**Undo/Redo Control:**
- Document automatic save-on-close behavior
- Consider exposing `UndoStackManager` for batch operations
- Would enable "undo all changes" functionality

### 3. Infrastructure Improvements [Priority: LOW-MEDIUM]

**Linux Support:**
- Update flatpak path handling in FLExGlobals.py
- Add detection for flatpak environment variables
- Test with FW flatpak installation

**Project Selection:**
- Implement `ChooseLangProjectDialog()` as optional method
- Keep simple file-based listing as fallback
- Handle network/UNC paths properly

### 4. Testing & Validation [Priority: MEDIUM]

**Current:** Contract tests validate API compatibility
**Suggested:** Add tests for edge cases:
- Operations on polymorphic collections (casting)
- Text handling across multiple writing systems
- Exception handling with locked projects
- Concurrent access patterns

### 5. Architecture Documentation [Priority: HIGH]

**Create:** `docs/LCM_WRAPPER_ARCHITECTURE.md`
- Explain why repositories/factories are wrapped
- Document casting patterns for polymorphic types
- Show how to extend with new Operations classes
- Provide decision tree for when to wrap vs. expose

---

## Summary Table: All LCM Capabilities

| Category | Imported | Exposed | Files | Risk | Status |
|---|---|---|---|---|---|
| **Repositories** | 9 | Via Operations | 70+ | LOW | [OK] Wrapped |
| **Factories** | 12 | Via Create() | 12 | MINIMAL | [OK] Wrapped |
| **Managers** | 2 | 1/2 (UndoStackManager only) | 3 | LOW | [OK] Protected |
| **Text Interfaces** | 4 | Via BestStr() | 50+ | LOW | [OK] Wrapped |
| **Exceptions** | 5 | Custom wrappers | 1 | LOW | [OK] Wrapped |
| **Tags/Constants** | 11 | Never | 15 | LOW | [OK] Hidden |
| **Cellar System** | 2 | Never | 3 | LOW | [OK] Hidden |
| **Utilities** | 7+ | Never | 8 | LOW | [OK] Hidden |
| **UI/Infrastructure** | 10+ | Never | 8 | MINIMAL | [OK] Hidden |
| **Writing Systems** | 2 | Minimal | 3 | LOW | [OK] Safe |
| **Operations Classes** | N/A | 57 | 64 | MINIMAL | [OK] Public API |

---

## Conclusion

The FlexLibs2 architecture successfully **abstracts away LCM complexity** while maintaining full functionality through a clean, user-friendly API. The 90+ imported LCM classes are strategically hidden behind 57 Operations classes that provide safe, validated access to FieldWorks data.

**Strengths:**
- Consistent wrapper pattern across all domains
- Safe exception handling with custom error types
- Factory/repository access protected by write-enabled checks
- Low-level primitives (text, casting) well-hidden
- Good use of dependency injection for optional features

**Areas for Improvement:**
- Document power-user access patterns
- Expose metadata introspection if needed
- Add a few missing operations (Scripture domain)
- Complete Linux support for flatpak

**Overall Risk:** **MINIMAL** - The abstraction layer effectively isolates users from dangerous LCM operations while providing escape hatches for advanced use cases.

