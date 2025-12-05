# flexlibs API Surface Documentation

**Version:** 2.0.0
**Generated:** 2025-12-05
**Analysis Tool:** `tools/extract_api_usage.py`

## Executive Summary

This document provides a comprehensive analysis of the flexlibs dependency on the SIL FieldWorks LCM (Language and Culture Model) API. Understanding this API surface is critical for:

- **Maintenance**: Tracking which LCM APIs we depend on
- **Compatibility**: Understanding version dependencies
- **Migration Planning**: Identifying areas requiring updates when LCM changes
- **Risk Assessment**: Highlighting critical dependencies used across many files

### Key Metrics

- **Total SIL.* Imports**: 527 import statements
- **Unique Classes Used**: 194 unique LCM classes/interfaces
- **SIL Namespaces Used**: 12 namespaces
- **Files Analyzed**: 66 Python files in flexlibs/code/
- **Critical Dependencies**: 14 classes used in 5+ files

---

## SIL Namespace Overview

flexlibs depends on 12 SIL namespaces from the FieldWorks LCM API:

| Namespace | Description | Files | Classes | Imports |
|-----------|-------------|-------|---------|---------|
| SIL.LCModel | Core LCModel classes and interfaces | 64 | 169 | 350 |
| SIL.LCModel.Core.KernelInterfaces | Kernel interfaces (ITsString, etc.) | 59 | 5 | 89 |
| SIL.LCModel.Core.Text | Text utilities (TsStringUtils) | 59 | 1 | 62 |
| SIL.LCModel.Core.Cellar | Cellar infrastructure | 3 | 2 | 5 |
| SIL.LCModel.Infrastructure | Infrastructure classes | 2 | 2 | 3 |
| SIL.LCModel.Utils | Utility classes | 2 | 2 | 3 |
| SIL.FieldWorks.Common.FwUtils | FieldWorks utilities | 4 | 7 | 8 |
| SIL.WritingSystems | Writing system definitions | 3 | 2 | 3 |
| SIL.FieldWorks | FieldWorks core | 1 | 1 | 1 |
| SIL.FieldWorks.Common.Controls | UI controls | 1 | 1 | 1 |
| SIL.FieldWorks.FdoUi | FDO UI components | 1 | 1 | 1 |
| SIL.FieldWorks.FwCoreDlgs | Core dialogs | 1 | 1 | 1 |

---

## Critical Dependencies (5+ Files)

These classes are used in 5 or more files and represent critical dependencies:

| Class | Usage Count | Type | Description |
|-------|-------------|------|-------------|
| **ITsString** | 84 | Interface | Multilingual string interface (CRITICAL) |
| **TsStringUtils** | 62 | Utility | Text string manipulation utilities (CRITICAL) |
| ICmPossibility | 15 | Interface | Possibility list items |
| ILexEntry | 11 | Interface | Lexical entry interface |
| ILexSense | 10 | Interface | Lexical sense interface |
| IWfiAnalysis | 8 | Interface | Wordform analysis interface |
| ICmPossibilityFactory | 8 | Factory | Creates possibility items |
| ICmPossibilityRepository | 7 | Repository | Accesses possibility items |
| IWfiWordform | 6 | Interface | Wordform interface |
| IText | 6 | Interface | Text interface |
| ICmPossibilityListFactory | 6 | Factory | Creates possibility lists |
| IDsConstChart | 6 | Interface | Discourse chart interface |
| IStTextFactory | 5 | Factory | Creates structured text |
| IStTxtParaFactory | 5 | Factory | Creates text paragraphs |

**Note**: ITsString and TsStringUtils are used virtually everywhere and represent the most critical dependencies.

---

## API Surface by Category

### 1. Repositories (Data Access)

Repositories provide read-only access to collections of objects.

**Total Repositories Used**: 15

| Repository | Usage | Namespace |
|------------|-------|-----------|
| ICmPossibilityRepository | 7 | SIL.LCModel |
| ILexEntryRepository | 3 | SIL.LCModel |
| IWfiWordformRepository | 3 | SIL.LCModel |
| IWfiAnalysisRepository | 3 | SIL.LCModel |
| ITextRepository | 3 | SIL.LCModel |
| ICmObjectRepository | 4 | SIL.LCModel |
| ILexRefTypeRepository | 2 | SIL.LCModel |
| ICmAnnotationDefnRepository | 1 | SIL.LCModel |
| IDsConstChartRepository | 1 | SIL.LCModel |
| ICmPersonRepository | 1 | SIL.LCModel |
| IReversalIndexRepository | 1 | SIL.LCModel |
| IScrBookRepository | 1 | SIL.LCModel |
| ISegmentRepository | 1 | SIL.LCModel |
| ILexSenseRepository | 1 | SIL.LCModel |
| IRnResearchNbkRepository | 1 | SIL.LCModel |

### 2. Factories (Object Creation)

Factories create new instances of LCM objects.

**Total Factories Used**: 42

#### High-Usage Factories (3+ uses):
| Factory | Usage | Purpose |
|---------|-------|---------|
| ICmPossibilityFactory | 8 | Create possibility list items |
| ICmPossibilityListFactory | 6 | Create possibility lists |
| IStTextFactory | 5 | Create structured text objects |
| IStTxtParaFactory | 5 | Create text paragraphs |
| IMoStemAllomorphFactory | 4 | Create stem allomorphs |
| ILexEntryRefFactory | 3 | Create entry references |
| ICmFileFactory | 3 | Create file objects |
| IWfiGlossFactory | 3 | Create wordform glosses |
| IWfiMorphBundleFactory | 3 | Create morph bundles |
| IMoAffixAllomorphFactory | 3 | Create affix allomorphs |

#### Other Factories (alphabetical):
- ICmAgentEvaluationFactory
- ICmAgentFactory
- ICmAnnotationDefnFactory
- ICmAnthroItemFactory
- ICmBaseAnnotationFactory
- ICmFilterFactory
- ICmFolderFactory
- ICmLocationFactory
- ICmMediaFactory
- ICmPersonFactory
- ICmPictureFactory
- ICmSemanticDomainFactory
- ICmTranslationFactory
- IConstChartClauseMarkerFactory
- IConstChartMovedTextMarkerFactory
- IConstChartRowFactory
- IConstChartTagFactory
- IConstChartWordGroupFactory
- IDsConstChartFactory
- IDsDiscourseFactory
- IFsFeatStrucFactory
- ILexEntryFactory
- ILexEtymologyFactory
- ILexExampleSentenceFactory
- ILexPronunciationFactory
- ILexReferenceFactory
- ILexRefTypeFactory
- ILexSenseFactory
- IMoAffixProcessFactory
- IMoInflClassFactory
- IMoStemMsaFactory
- IPartOfSpeechFactory
- IPhCodeFactory
- IPhEnvironmentFactory
- IPhNCSegmentsFactory
- IPhPhonemeFactory
- IPhRegularRuleFactory
- IReversalIndexEntryFactory
- IReversalIndexFactory
- IRnGenericRecFactory
- IScrBookAnnotationsFactory
- IScrBookFactory
- IScrDraftFactory
- IScrScriptureNoteFactory
- IScrSectionFactory
- IScrTxtParaFactory
- ISegmentFactory
- ITextFactory
- IWfiAnalysisFactory
- IWfiWordformFactory

### 3. Interfaces (Data Objects)

These interfaces represent the core data model objects.

**Total Interfaces Used**: 95

#### Core Lexicon Interfaces (High Usage):
| Interface | Usage | Description |
|-----------|-------|-------------|
| ILexEntry | 11 | Lexical entry |
| ILexSense | 10 | Sense of lexical entry |
| ILexExampleSentence | 2 | Example sentence |
| ILexEntryRef | 2 | Lexical entry reference (variant, complex form) |
| ILexEtymology | 1 | Etymology information |
| ILexPronunciation | 1 | Pronunciation |
| ILexReference | 1 | Lexical reference (relation) |
| ILexRefType | 1 | Type of lexical reference |
| ILexEntryType | 1 | Type of lexical entry |

#### Core Wordform/Analysis Interfaces:
| Interface | Usage | Description |
|-----------|-------|-------------|
| IWfiAnalysis | 8 | Wordform analysis |
| IWfiWordform | 6 | Wordform |
| IWfiGloss | 2 | Wordform gloss |
| IWfiMorphBundle | 3 | Morpheme bundle |

#### Core Text Interfaces:
| Interface | Usage | Description |
|-----------|-------|-------------|
| IText | 6 | Text object |
| IStTxtPara | 3 | Structured text paragraph |
| ISegment | 2 | Text segment |
| IStText | 1 | Structured text |

#### Possibility List Interfaces:
| Interface | Usage | Description |
|-----------|-------|-------------|
| ICmPossibility | 15 | Generic possibility item |
| ICmPossibilityList | 3 | List of possibilities |
| ICmSemanticDomain | 3 | Semantic domain |

#### Discourse Chart Interfaces:
| Interface | Usage | Description |
|-----------|-------|-------------|
| IDsConstChart | 6 | Discourse constituent chart |
| IConstChartRow | 4 | Chart row |
| IConstChartWordGroup | 4 | Word group in chart |
| IConstChartTag | 1 | Chart tag |
| IConstChartClauseMarker | 1 | Clause marker |
| IConstChartMovedTextMarker | 1 | Moved text marker |
| IDsDiscourse | 1 | Discourse data |

#### Morphology Interfaces:
| Interface | Usage | Description |
|-----------|-------|-------------|
| IMoMorphType | 4 | Morpheme type |
| IMoForm | 3 | Morphological form |
| IMoMorphSynAnalysis | 1 | Morph-syntactic analysis |
| IMoInflClass | 2 | Inflection class |

#### Grammar/Phonology Interfaces:
| Interface | Usage | Description |
|-----------|-------|-------------|
| IPartOfSpeech | 3 | Part of speech |
| IPhEnvironment | 2 | Phonological environment |
| IPhPhoneme | 2 | Phoneme |
| IFsFeatStruc | 2 | Feature structure |
| IPhNaturalClass | 1 | Natural class |
| IPhNCSegments | 1 | Natural class segments |
| IPhCode | 1 | Phonological code |
| IFsFeatDefn | 1 | Feature definition |
| IFsClosedFeature | 1 | Closed feature |

#### Scripture Interfaces:
| Interface | Usage | Description |
|-----------|-------|-------------|
| IScrBook | 4 | Scripture book |
| IScrScriptureNote | 3 | Scripture note |
| IScrSection | 3 | Scripture section |
| IScrTxtPara | 3 | Scripture text paragraph |
| IScripture | 2 | Scripture |
| IScrBookAnnotations | 2 | Book annotations |
| IScrDraft | 1 | Scripture draft |

#### Notebook/Anthropology Interfaces:
| Interface | Usage | Description |
|-----------|-------|-------------|
| ICmPerson | 4 | Person |
| ICmLocation | 2 | Location |
| IRnGenericRec | 1 | Generic notebook record |
| ICmAnthroItem | 1 | Anthropology item |

#### Reversal Index Interfaces:
| Interface | Usage | Description |
|-----------|-------|-------------|
| IReversalIndex | 4 | Reversal index |
| IReversalIndexEntry | 4 | Reversal index entry |

#### Other Data Interfaces:
| Interface | Usage | Description |
|-----------|-------|-------------|
| ICmAnnotationDefn | 2 | Annotation definition |
| ICmFile | 3 | File object |
| ICmMedia | 1 | Media object |
| ICmPicture | 1 | Picture |
| ICmAgent | 2 | Agent |
| ICmAgentEvaluation | 2 | Agent evaluation |
| ICmFilter | 1 | Filter |
| ICmFolder | 1 | Folder |
| ICmTranslation | 1 | Translation |
| ICmBaseAnnotation | 1 | Base annotation |
| IVariantComponentLexeme | 1 | Variant component |
| IAnalysis | 1 | Analysis |
| IStStyle | 1 | Style |

#### Special Interfaces:
| Interface | Usage | Description |
|-----------|-------|-------------|
| ILangProject | 4 | The root project object |
| IUndoStackManager | 1 | Undo/redo management |

### 4. Tags Classes (Field IDs)

Tags provide integer constants for accessing object fields.

**Total Tags Used**: 11

| Tags Class | Usage | Description |
|------------|-------|-------------|
| LexEntryTags | 2 | Field IDs for LexEntry |
| LexSenseTags | 2 | Field IDs for LexSense |
| LexExampleSentenceTags | 2 | Field IDs for example sentences |
| MoFormTags | 2 | Field IDs for MoForm |
| MoMorphTypeTags | 2 | Field IDs for morph types |
| LexEntryRefTags | 1 | Field IDs for entry refs |
| LexRefTypeTags | 1 | Field IDs for ref types |
| WfiWordformTags | 1 | Field IDs for wordforms |
| WfiGlossTags | 1 | Field IDs for glosses |
| WfiAnalysisTags | 1 | Field IDs for analyses |
| WfiMorphBundleTags | 1 | Field IDs for morph bundles |
| TextTags | 1 | Field IDs for Text |
| ReversalIndexEntryTags | 1 | Field IDs for reversal entries |

### 5. Utility Classes

**Total Utilities Used**: 16

#### Text/String Utilities (CRITICAL):
| Utility | Usage | Namespace | Description |
|---------|-------|-----------|-------------|
| **TsStringUtils** | 62 | SIL.LCModel.Core.Text | String manipulation (CRITICAL) |
| ITsString | 84 | SIL.LCModel.Core.KernelInterfaces | Multilingual string (CRITICAL) |
| ITsStrBldr | 2 | SIL.LCModel.Core.KernelInterfaces | String builder |

#### Multi-String Interfaces:
| Utility | Usage | Namespace | Description |
|---------|-------|-----------|-------------|
| IMultiUnicode | 1 | SIL.LCModel.Core.KernelInterfaces | Multi-Unicode string |
| IMultiString | 1 | SIL.LCModel.Core.KernelInterfaces | Multi-string |

#### Reflection/Metadata:
| Utility | Usage | Namespace | Description |
|---------|-------|-----------|-------------|
| ReflectionHelper | 2 | SIL.LCModel.Utils | Reflection utilities |
| IFwMetaDataCacheManaged | 2 | SIL.LCModel.Infrastructure | Metadata cache |
| IDataReader | 1 | SIL.LCModel.Infrastructure | Data reader |

#### Writing Systems:
| Utility | Usage | Namespace | Description |
|---------|-------|-----------|-------------|
| WritingSystemDefinition | 2 | SIL.WritingSystems | Writing system |
| SpecialWritingSystemCodes | 2 | SIL.LCModel | Special WS codes |
| Sldr | 1 | SIL.WritingSystems | SLDR (writing systems) |

#### FieldWorks Utilities:
| Utility | Usage | Namespace | Description |
|---------|-------|-----------|-------------|
| FwUtils | 2 | SIL.FieldWorks.Common.FwUtils | General FW utilities |
| FwDirectoryFinder | 1 | SIL.FieldWorks.Common.FwUtils | Directory locator |
| FwRegistryHelper | 1 | SIL.FieldWorks.Common.FwUtils | Registry access |
| ThreadHelper | 1 | SIL.FieldWorks.Common.FwUtils | Threading utilities |
| FwAppArgs | 1 | SIL.FieldWorks.Common.FwUtils | Application arguments |
| VersionInfoProvider | 1 | SIL.FieldWorks.Common.FwUtils | Version information |

### 6. Core Infrastructure Classes

| Class | Usage | Namespace | Description |
|-------|-------|-----------|-------------|
| LcmCache | 1 | SIL.LCModel | The main cache object |
| LcmSettings | 1 | SIL.LCModel | LCM settings |
| LcmFileHelper | 1 | SIL.LCModel | File operations |
| CellarPropertyType | 3 | SIL.LCModel.Core.Cellar | Property type enum |
| CellarPropertyTypeFilter | 2 | SIL.LCModel.Core.Cellar | Property filtering |
| FwObjDataTypes | 1 | SIL.LCModel.Core.KernelInterfaces | Object data types |

### 7. UI Components (Used in FLExProject.py, FLExLCM.py)

| Class | Usage | Namespace | Description |
|-------|-------|-----------|-------------|
| ProgressDialogWithTask | 1 | SIL.FieldWorks.Common.Controls | Progress dialog |
| FwLcmUI | 1 | SIL.FieldWorks.FdoUi | LCM UI |
| ChooseLangProjectDialog | 1 | SIL.FieldWorks.FwCoreDlgs | Project chooser |
| ProjectId | 1 | SIL.FieldWorks | Project identifier |

### 8. Exception Classes

| Exception | Usage | Namespace | Description |
|-----------|-------|-----------|-------------|
| LcmInvalidClassException | 1 | SIL.LCModel | Invalid class error |
| LcmInvalidFieldException | 1 | SIL.LCModel | Invalid field error |
| LcmFileLockedException | 1 | SIL.LCModel | File locked error |
| LcmDataMigrationForbiddenException | 1 | SIL.LCModel | Migration forbidden |
| WorkerThreadException | 1 | SIL.LCModel.Utils | Worker thread error |
| StartupException | 1 | SIL.FieldWorks.Common.FwUtils | Startup error |

### 9. Other Classes

| Class | Usage | Namespace | Description |
|-------|-------|-----------|-------------|
| GenDate | 1 | SIL.LCModel | Generic date |

---

## Namespace Dependency Details

### SIL.LCModel (Core)

**Files**: 64 | **Classes**: 169 | **Imports**: 350

This is the primary namespace containing all LCM data model interfaces, repositories, and factories.

**Key Dependencies**:
- All Repository interfaces
- All Factory interfaces
- All data object interfaces (ILexEntry, IWfiWordform, etc.)
- All Tags classes
- Core exceptions and enums

**Risk Level**: **HIGH** - This is the core dependency. Changes to LCM interfaces directly impact flexlibs.

### SIL.LCModel.Core.KernelInterfaces

**Files**: 59 | **Classes**: 5 | **Imports**: 89

**Critical Classes**:
- ITsString (84 uses) - Multilingual string representation
- ITsStrBldr (2 uses) - String builder
- IMultiUnicode, IMultiString - Multi-language string interfaces

**Risk Level**: **CRITICAL** - ITsString is used everywhere. Any changes to this interface would require massive refactoring.

### SIL.LCModel.Core.Text

**Files**: 59 | **Classes**: 1 | **Imports**: 62

**Critical Classes**:
- TsStringUtils (62 uses) - Static utility methods for string manipulation

**Risk Level**: **CRITICAL** - Used in almost every file for string operations.

### SIL.LCModel.Core.Cellar

**Files**: 3 | **Classes**: 2 | **Imports**: 5

**Classes**:
- CellarPropertyType - Property type enumeration
- CellarPropertyTypeFilter - Property filtering

**Risk Level**: **LOW** - Used only in FLExProject.py and CustomFieldOperations.py.

### SIL.LCModel.Infrastructure

**Files**: 2 | **Classes**: 2 | **Imports**: 3

**Classes**:
- IFwMetaDataCacheManaged - Metadata cache access
- IDataReader - Data reading interface

**Risk Level**: **LOW** - Limited usage in advanced scenarios.

### SIL.LCModel.Utils

**Files**: 2 | **Classes**: 2 | **Imports**: 3

**Classes**:
- ReflectionHelper - Reflection utilities
- WorkerThreadException - Exception type

**Risk Level**: **LOW** - Utility functions, minimal impact.

### SIL.FieldWorks.* (6 namespaces)

**Files**: 4 (mainly FLExProject.py, FLExLCM.py, FLExInit.py)
**Total Classes**: 14
**Total Imports**: 16

These provide FieldWorks-specific utilities, UI components, and initialization support.

**Risk Level**: **MEDIUM** - Used for project initialization and UI. Changes could affect startup.

### SIL.WritingSystems

**Files**: 3 | **Classes**: 2 | **Imports**: 3

**Classes**:
- WritingSystemDefinition - Writing system representation
- Sldr - SLDR (SIL Locale Data Repository) access

**Risk Level**: **LOW** - Used for writing system operations.

---

## Dependency Impact Analysis

### Files with Highest API Dependencies

Top 10 files with the most SIL.* imports:

1. **FLExProject.py** - 27 imports (Core infrastructure file)
2. **CustomFieldOperations.py** - 15+ imports (Complex custom fields)
3. **TextsWords/DiscourseOperations.py** - 15+ imports (Discourse analysis)
4. **Lexicon/LexEntryOperations.py** - 14 imports (Core lexicon)
5. **TextsWords/WfiAnalysisOperations.py** - 13 imports (Wordform analysis)
6. **Shared/FilterOperations.py** - 10+ imports (Filter management)
7. **Discourse/ConstChartOperations.py** - 10 imports (Discourse charts)
8. **Scripture/ScrAnnotationsOperations.py** - 8+ imports (Scripture notes)

### API Usage by Module Area

| Module Area | Files | Avg Imports/File |
|-------------|-------|------------------|
| Lexicon | 10 | 8.5 |
| TextsWords | 8 | 9.2 |
| Scripture | 7 | 7.8 |
| Discourse | 7 | 7.3 |
| Grammar | 8 | 7.1 |
| Lists | 6 | 7.5 |
| Notebook | 5 | 8.4 |
| System | 5 | 9.0 |
| Reversal | 3 | 8.0 |
| Wordform | 4 | 7.5 |
| Shared | 2 | 9.5 |

---

## Migration and Compatibility Considerations

### High-Risk Areas for LCM Changes

1. **ITsString / TsStringUtils** - Used in 84/62 files respectively
   - Any API changes here would require extensive refactoring
   - Consider creating wrapper/adapter layer

2. **Repository Interfaces** - Used throughout for data access
   - Changes to query methods would impact many files
   - Maintain backward compatibility where possible

3. **Factory Interfaces** - Used for all object creation
   - Changes to factory methods affect object creation patterns
   - May need factory adapters for version compatibility

### Recommended Mitigation Strategies

1. **Create Abstraction Layer**
   - Wrap critical dependencies (ITsString, TsStringUtils) in flexlibs helpers
   - Isolate LCM-specific code to minimize surface area

2. **Version Compatibility Testing**
   - Test against multiple FLEx/LCM versions
   - Document compatible version ranges

3. **Dependency Monitoring**
   - Regularly run `extract_api_usage.py` to track changes
   - Monitor for new dependencies or increased usage

4. **API Stability Tracking**
   - Track which LCM APIs are stable vs. experimental
   - Prefer stable APIs when alternatives exist

---

## Appendix: Complete Class List

See `api_usage_summary.json` for the complete list of all 194 classes used.

To regenerate this data:
```bash
python tools/extract_api_usage.py --summary
```

---

**Document Maintained By**: Programmer Team 1
**Last Updated**: 2025-12-05
**Tool**: `tools/extract_api_usage.py`
