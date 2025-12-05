# LCM API Dependency Matrix

**Version:** 2.0.0
**Generated:** 2025-12-05
**Analysis Tool:** `tools/extract_api_usage.py`

## Overview

This document provides a comprehensive matrix showing the LCM API dependencies for each operations class in flexlibs. Understanding these dependencies is critical for:

- **Risk Assessment**: Identifying which operations are most coupled to LCM
- **Refactoring Planning**: Understanding the scope of changes needed
- **Version Compatibility**: Tracking which LCM APIs are used where
- **Maintenance**: Knowing the complexity of each operations class

### Dependency Categories

Each operations class uses four types of LCM dependencies:

- **R** (Repositories): Data access interfaces (e.g., ILexEntryRepository)
- **F** (Factories): Object creation interfaces (e.g., ILexEntryFactory)
- **I** (Interfaces): Data model interfaces (e.g., ILexEntry, ILexSense)
- **T** (Tags): Field ID constants (e.g., LexEntryTags)

**Note**: All operations classes also use ITsString and TsStringUtils, which are universal dependencies not counted in the totals below.

### Risk Levels

- **HIGH**: 10+ total dependencies - Complex operations with high LCM coupling
- **MEDIUM**: 6-9 dependencies - Moderate coupling
- **LOW**: 0-5 dependencies - Minimal coupling

---

## Summary Statistics

- **Total Operations Classes**: 63
- **HIGH Risk Classes**: 8 (13%)
- **MEDIUM Risk Classes**: 21 (33%)
- **LOW Risk Classes**: 34 (54%)

### High-Risk Operations (10+ Dependencies)

These operations have the highest coupling to LCM and would be most impacted by API changes:

| Operations Class | Repos | Factories | Interfaces | Tags | Total | Module |
|------------------|-------|-----------|------------|------|-------|--------|
| **LexEntry** | 1 | 5 | 6 | 2 | **14** | Lexicon |
| **CustomField** | 3 | 3 | 7 | 0 | **13** | System |
| **Discourse** | 3 | 2 | 8 | 0 | **13** | TextsWords |
| **Filter** | 3 | 3 | 4 | 0 | **10** | Shared |
| **LexReference** | 1 | 3 | 5 | 1 | **10** | Lexicon |
| **LexSense** | 0 | 4 | 6 | 0 | **10** | Lexicon |
| **DataNotebook** | 2 | 2 | 6 | 0 | **10** | Notebook |
| **WfiAnalysis (TextsWords)** | 2 | 3 | 5 | 0 | **10** | TextsWords |

---

## Complete Dependency Matrix

### Lexicon Operations

| Class | R | F | I | T | Total | Risk | Key Dependencies |
|-------|---|---|---|---|-------|------|------------------|
| **LexEntry** | 1 | 5 | 6 | 2 | **14** | HIGH | ILexEntry, ILexSense, ILexEntryFactory, IMoStemAllomorphFactory, IMoAffixAllomorphFactory |
| **LexSense** | 0 | 4 | 6 | 0 | **10** | HIGH | ILexSense, ILexEntry, ILexSenseFactory, ILexExampleSentenceFactory |
| **LexReference** | 1 | 3 | 5 | 1 | **10** | HIGH | ILexReference, ILexReferenceFactory, ILexRefType, ILexRefTypeRepository |
| **Allomorph** | 0 | 2 | 4 | 1 | **7** | MED | IMoForm, IMoStemAllomorphFactory, IMoAffixAllomorphFactory |
| **Variant** | 1 | 1 | 5 | 0 | **7** | MED | ILexEntry, ILexEntryRef, IVariantComponentLexeme |
| **Example** | 0 | 2 | 4 | 0 | **6** | MED | ILexExampleSentence, ILexExampleSentenceFactory, ICmPicture |
| **Pronunciation** | 0 | 2 | 4 | 0 | **6** | MED | ILexPronunciation, ILexPronunciationFactory, ICmMedia |
| **Reversal** | 0 | 1 | 4 | 0 | **5** | LOW | IReversalIndexEntry, ILexSense |
| **Etymology** | 0 | 1 | 3 | 0 | **4** | LOW | ILexEtymology, ILexEtymologyFactory |
| **SemanticDomain** | 1 | 1 | 2 | 0 | **4** | LOW | ICmSemanticDomain, ICmSemanticDomainFactory |

**Lexicon Summary**: 10 classes, 3 HIGH risk, 4 MEDIUM, 3 LOW

---

### Grammar Operations

| Class | R | F | I | T | Total | Risk | Key Dependencies |
|-------|---|---|---|---|-------|------|------------------|
| **InflectionFeature** | 0 | 2 | 4 | 0 | **6** | MED | IFsFeatStruc, IFsFeatDefn, IMoInflClass |
| **Phoneme** | 0 | 2 | 4 | 0 | **6** | MED | IPhPhoneme, IPhPhonemeFactory, IPhCode |
| **NaturalClass** | 0 | 1 | 4 | 0 | **5** | LOW | IPhNaturalClass, IPhNCSegments, IPhPhoneme |
| **POS** | 1 | 1 | 2 | 0 | **4** | LOW | IPartOfSpeech, IPartOfSpeechFactory, ILexEntryRepository |
| **Environment** | 0 | 1 | 2 | 0 | **3** | LOW | IPhEnvironment, IPhEnvironmentFactory |
| **GramCat** | 0 | 1 | 2 | 0 | **3** | LOW | ICmPossibility, ICmPossibilityFactory |
| **MorphRule** | 0 | 1 | 1 | 0 | **2** | LOW | IMoAffixProcessFactory |
| **PhonologicalRule** | 0 | 1 | 1 | 0 | **2** | LOW | IPhRegularRuleFactory |

**Grammar Summary**: 8 classes, 0 HIGH risk, 2 MEDIUM, 6 LOW

---

### TextsWords Operations

| Class | R | F | I | T | Total | Risk | Key Dependencies |
|-------|---|---|---|---|-------|------|------------------|
| **Discourse** | 3 | 2 | 8 | 0 | **13** | HIGH | IDsConstChart, IDsDiscourse, IConstChartRow, IText, IStTxtPara |
| **WfiAnalysis** | 2 | 3 | 5 | 0 | **10** | HIGH | IWfiAnalysis, IWfiWordform, IWfiGloss, IWfiMorphBundle |
| **Text** | 2 | 2 | 2 | 0 | **6** | MED | IText, ITextFactory, IStText, IStTextFactory |
| **Paragraph** | 1 | 1 | 3 | 0 | **5** | LOW | IStTxtPara, IStTxtParaFactory, IStText |
| **Segment** | 1 | 1 | 2 | 0 | **4** | LOW | ISegment, ISegmentFactory |
| **Wordform** | 1 | 1 | 2 | 0 | **4** | LOW | IWfiWordform, IWfiWordformFactory |
| **WfiGloss** | 1 | 1 | 2 | 0 | **4** | LOW | IWfiGloss, IWfiGlossFactory |
| **WfiMorphBundle** | 0 | 1 | 3 | 0 | **4** | LOW | IWfiMorphBundle, IWfiMorphBundleFactory, IMoForm |

**TextsWords Summary**: 8 classes, 2 HIGH risk, 1 MEDIUM, 5 LOW

---

### Discourse (Charts) Operations

| Class | R | F | I | T | Total | Risk | Key Dependencies |
|-------|---|---|---|---|-------|------|------------------|
| **ConstChart** | 1 | 2 | 5 | 0 | **8** | MED | IDsConstChart, IDsConstChartFactory, IConstChartRow |
| **ConstChartTag** | 0 | 2 | 4 | 0 | **6** | MED | IConstChartTag, IConstChartTagFactory, ICmPossibility |
| **ConstChartRow** | 0 | 1 | 4 | 0 | **5** | LOW | IConstChartRow, IConstChartRowFactory, IConstChartWordGroup |
| **ConstChartWordGroup** | 0 | 1 | 4 | 0 | **5** | LOW | IConstChartWordGroup, IConstChartWordGroupFactory |
| **ConstChartClauseMarker** | 0 | 1 | 3 | 0 | **4** | LOW | IConstChartClauseMarker, IConstChartClauseMarkerFactory |
| **ConstChartMovedText** | 0 | 1 | 3 | 0 | **4** | LOW | IConstChartMovedTextMarker, IConstChartMovedTextMarkerFactory |

**Discourse Summary**: 6 classes, 0 HIGH risk, 2 MEDIUM, 4 LOW

---

### Scripture Operations

| Class | R | F | I | T | Total | Risk | Key Dependencies |
|-------|---|---|---|---|-------|------|------------------|
| **ScrNote** | 1 | 2 | 4 | 0 | **7** | MED | IScrScriptureNote, IScrScriptureNoteFactory, IScrBook |
| **ScrBook** | 1 | 1 | 4 | 0 | **6** | MED | IScrBook, IScrBookFactory, IScripture |
| **ScrTxtPara** | 0 | 1 | 3 | 0 | **4** | LOW | IScrTxtPara, IScrTxtParaFactory, IStText |
| **ScrAnnotations** | 0 | 1 | 3 | 0 | **4** | LOW | IScrBookAnnotations, IScrBookAnnotationsFactory |
| **ScrDraft** | 0 | 1 | 3 | 0 | **4** | LOW | IScrDraft, IScrDraftFactory, IScripture |
| **ScrSection** | 1 | 1 | 2 | 0 | **4** | LOW | IScrSection, IScrSectionFactory |

**Scripture Summary**: 6 classes, 0 HIGH risk, 2 MEDIUM, 4 LOW

---

### Notebook Operations

| Class | R | F | I | T | Total | Risk | Key Dependencies |
|-------|---|---|---|---|-------|------|------------------|
| **DataNotebook** | 2 | 2 | 6 | 0 | **10** | HIGH | IRnGenericRec, IRnResearchNbkRepository, ICmFile, ICmFolder |
| **Person** | 2 | 1 | 5 | 0 | **8** | MED | ICmPerson, ICmPersonFactory, ICmPersonRepository |
| **Anthropology** | 0 | 2 | 5 | 0 | **7** | MED | ICmAnthroItem, ICmAnthroItemFactory, ICmPossibility |
| **Note** | 0 | 2 | 5 | 0 | **7** | MED | IRnGenericRec, IRnGenericRecFactory, ICmFile |
| **Location** | 1 | 1 | 2 | 0 | **4** | LOW | ICmLocation, ICmLocationFactory |

**Notebook Summary**: 5 classes, 1 HIGH risk, 3 MEDIUM, 1 LOW

---

### Lists Operations

| Class | R | F | I | T | Total | Risk | Key Dependencies |
|-------|---|---|---|---|-------|------|------------------|
| **Agent** | 1 | 1 | 5 | 0 | **7** | MED | ICmAgent, ICmAgentFactory, ICmAgentEvaluation |
| **TranslationType** | 2 | 2 | 2 | 0 | **6** | MED | ICmPossibility, ICmTranslation, ICmPossibilityRepository |
| **PossibilityList** | 1 | 2 | 3 | 0 | **6** | MED | ICmPossibilityList, ICmPossibilityListFactory, ICmPossibility |
| **Confidence** | 2 | 1 | 2 | 0 | **5** | LOW | ICmAgentEvaluation, ICmPossibility |
| **Overlay** | 0 | 2 | 3 | 0 | **5** | LOW | ICmPossibility, ICmPossibilityFactory |
| **Publication** | 1 | 1 | 2 | 0 | **4** | LOW | ICmPossibility, ICmPossibilityFactory |

**Lists Summary**: 6 classes, 0 HIGH risk, 3 MEDIUM, 3 LOW

---

### System Operations

| Class | R | F | I | T | Total | Risk | Key Dependencies |
|-------|---|---|---|---|-------|------|------------------|
| **CustomField** | 3 | 3 | 7 | 0 | **13** | HIGH | CellarPropertyType, IFwMetaDataCacheManaged, ICmPossibilityList |
| **Check** | 1 | 1 | 5 | 0 | **7** | MED | ICmAnnotationDefn, ICmBaseAnnotation, ICmPossibility |
| **AnnotationDef** | 1 | 1 | 2 | 0 | **4** | LOW | ICmAnnotationDefn, ICmAnnotationDefnFactory |
| **ProjectSettings** | 0 | 0 | 1 | 0 | **1** | LOW | WritingSystemDefinition (not LCM) |
| **WritingSystem** | 0 | 0 | 0 | 0 | **0** | LOW | WritingSystemDefinition, SpecialWritingSystemCodes |

**System Summary**: 5 classes, 1 HIGH risk, 1 MEDIUM, 3 LOW

---

### Shared Operations

| Class | R | F | I | T | Total | Risk | Key Dependencies |
|-------|---|---|---|---|-------|------|------------------|
| **Filter** | 3 | 3 | 4 | 0 | **10** | HIGH | ICmFilter, ICmFilterFactory, ICmFolder, ICmFile |
| **Media** | 0 | 3 | 4 | 0 | **7** | MED | ICmMedia, ICmFile, ICmFolder, ICmMediaFactory |

**Shared Summary**: 2 classes, 1 HIGH risk, 1 MEDIUM, 0 LOW

---

### Reversal Operations

| Class | R | F | I | T | Total | Risk | Key Dependencies |
|-------|---|---|---|---|-------|------|------------------|
| **ReversalIndexEntry** | 0 | 1 | 4 | 0 | **5** | LOW | IReversalIndexEntry, IReversalIndexEntryFactory, ILexSense |
| **ReversalIndex** | 1 | 1 | 3 | 0 | **5** | LOW | IReversalIndex, IReversalIndexFactory, IReversalIndexRepository |

**Reversal Summary**: 2 classes, 0 HIGH risk, 0 MEDIUM, 2 LOW

---

### Wordform Operations (Duplicate Module)

| Class | R | F | I | T | Total | Risk | Key Dependencies |
|-------|---|---|---|---|-------|------|------------------|
| **WfiAnalysis** | 2 | 1 | 3 | 0 | **6** | MED | IWfiAnalysis, IWfiAnalysisFactory, IWfiWordform |
| **WfiGloss** | 1 | 1 | 2 | 0 | **4** | LOW | IWfiGloss, IWfiGlossFactory |
| **WfiMorphBundle** | 0 | 1 | 3 | 0 | **4** | LOW | IWfiMorphBundle, IWfiMorphBundleFactory |
| **WfiWordform** | 1 | 1 | 2 | 0 | **4** | LOW | IWfiWordform, IWfiWordformFactory |

**Wordform Summary**: 4 classes, 0 HIGH risk, 1 MEDIUM, 3 LOW

---

## Risk Analysis by Module

| Module | Total Classes | HIGH | MEDIUM | LOW | Avg Dependencies |
|--------|---------------|------|--------|-----|------------------|
| Lexicon | 10 | 3 | 4 | 3 | 6.9 |
| System | 5 | 1 | 1 | 3 | 5.0 |
| TextsWords | 8 | 2 | 1 | 5 | 6.3 |
| Notebook | 5 | 1 | 3 | 1 | 7.2 |
| Shared | 2 | 1 | 1 | 0 | 8.5 |
| Scripture | 6 | 0 | 2 | 4 | 4.8 |
| Discourse | 6 | 0 | 2 | 4 | 5.3 |
| Grammar | 8 | 0 | 2 | 6 | 3.9 |
| Lists | 6 | 0 | 3 | 3 | 5.5 |
| Reversal | 2 | 0 | 0 | 2 | 5.0 |
| Wordform | 4 | 0 | 1 | 3 | 4.5 |

**Module Risk Assessment**:
- **Highest Risk**: Shared (50% HIGH), Lexicon (30% HIGH), System (20% HIGH)
- **Moderate Risk**: Notebook, TextsWords, Lists
- **Lower Risk**: Scripture, Discourse, Grammar, Reversal, Wordform

---

## Dependency Type Analysis

### Repository Usage (20 total unique repositories)

Top repositories used across operations:

| Repository | Operations Using It |
|------------|---------------------|
| ICmPossibilityRepository | 7 operations |
| ILexEntryRepository | 3 operations |
| IWfiWordformRepository | 3 operations |
| IWfiAnalysisRepository | 3 operations |
| ITextRepository | 3 operations |
| ICmObjectRepository | 4 operations |
| ICmPersonRepository | 2 operations |
| IRnResearchNbkRepository | 1 operation |

**Analysis**: Repository usage is relatively low, most operations use 0-2 repositories.

### Factory Usage (42 total unique factories)

Most commonly used factories:

| Factory | Operations Using It |
|---------|---------------------|
| ICmPossibilityFactory | 8 operations |
| ICmPossibilityListFactory | 6 operations |
| IStTextFactory | 5 operations |
| IStTxtParaFactory | 5 operations |
| IMoStemAllomorphFactory | 4 operations |
| ILexSenseFactory | 4 operations |
| ILexExampleSentenceFactory | 4 operations |

**Analysis**: Factory usage is moderate to high, especially for creating lexicon and possibility objects.

### Interface Usage (95 total unique interfaces)

Most critical interface dependencies:

| Interface | Operations Using It |
|-----------|---------------------|
| ICmPossibility | 15 operations |
| ILexEntry | 11 operations |
| ILexSense | 10 operations |
| IWfiAnalysis | 8 operations |
| IWfiWordform | 6 operations |
| IText | 6 operations |
| IDsConstChart | 6 operations |

**Analysis**: Interface usage is high, with core data model interfaces appearing in many operations.

### Tags Usage (11 total tag classes)

Tags are used less frequently:

| Tags | Operations Using It |
|------|---------------------|
| LexEntryTags | 2 operations |
| LexSenseTags | 2 operations |
| MoFormTags | 2 operations |
| (others) | 1 operation each |

**Analysis**: Tags usage is relatively low, primarily in lexicon operations.

---

## Migration Impact Assessment

### High-Priority Refactoring Targets

If reducing LCM coupling is a goal, focus on these high-dependency operations:

1. **LexEntryOperations** (14 deps) - Core lexicon, most critical
2. **CustomFieldOperations** (13 deps) - Custom fields, complex metadata
3. **DiscourseOperations** (13 deps) - Discourse analysis, multiple object types
4. **FilterOperations** (10 deps) - Filter management
5. **LexReferenceOperations** (10 deps) - Lexical relations
6. **LexSenseOperations** (10 deps) - Core lexicon
7. **DataNotebookOperations** (10 deps) - Notebook management
8. **WfiAnalysisOperations** (10 deps) - Wordform analysis

### Abstraction Layer Recommendations

Consider creating abstraction layers for:

1. **Lexicon Core** - Wrap ILexEntry, ILexSense, factories
2. **Wordform Analysis** - Wrap IWfiWordform, IWfiAnalysis, IWfiGloss
3. **Possibility Lists** - Wrap ICmPossibility, ICmPossibilityList
4. **Text/Paragraph** - Wrap IText, IStText, IStTxtPara
5. **Custom Fields** - Already complex, needs careful abstraction

### Version Compatibility Strategy

**Critical Dependencies** (require version testing):
- ITsString / TsStringUtils (used everywhere)
- ILexEntry / ILexSense (core lexicon)
- IWfiWordform / IWfiAnalysis (wordform analysis)
- ICmPossibility (lists and classification)

**Moderate Dependencies** (monitor for changes):
- Repository interfaces
- Factory interfaces
- Tags classes

**Low Dependencies** (less critical):
- UI components
- Specialized interfaces

---

## Recommendations

### For Maintenance

1. **Monitor High-Risk Operations**: Changes to LCM APIs will most impact the 8 HIGH-risk operations
2. **Test Coverage**: Ensure comprehensive tests for high-dependency operations
3. **Documentation**: Keep this matrix updated when adding new operations or dependencies

### For Development

1. **Minimize Dependencies**: When creating new operations, try to keep total dependencies under 6
2. **Reuse Patterns**: Follow patterns from LOW-risk operations where possible
3. **Abstraction**: Consider wrapping commonly used LCM interfaces

### For Version Migration

1. **Test High-Risk First**: When upgrading FLEx/LCM versions, test HIGH-risk operations first
2. **Incremental Updates**: Update operations module-by-module
3. **Compatibility Shims**: Create compatibility layers for breaking changes

---

## Appendix: Complete Dependency List

For complete dependency details by file, see:
- `api_usage_by_file.json` - Full dependency list per file
- `api_usage_summary.json` - Summary statistics
- `docs/API_SURFACE.md` - Detailed API documentation

To regenerate this matrix:
```bash
python tools/extract_api_usage.py --all
```

---

**Document Maintained By**: Programmer Team 1
**Last Updated**: 2025-12-05
**Analysis Tool**: `tools/extract_api_usage.py`
