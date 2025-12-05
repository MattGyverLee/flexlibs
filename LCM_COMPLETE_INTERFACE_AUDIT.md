# Complete LCM C# Interface Structure Analysis

**Date:** December 4, 2025  
**Purpose:** Understand the complete structure of all LCM interfaces to identify why property audits keep finding gaps

---

## EXECUTIVE SUMMARY

The LCM codebase defines **81 core domain interfaces** + **49 Factory interfaces** + **33 Repository interfaces** = **163 total public interfaces**.

These interfaces are spread across 3 main files in the SIL.LCModel namespace:
- InterfaceAdditions.cs (6,028 lines) - Core domain object interfaces
- FactoryInterfaceAdditions.cs (1,139 lines) - Factory interfaces for creating objects
- RepositoryInterfaceAdditions.cs (644 lines) - Repository interfaces for querying/accessing objects

---

## INTERFACE COUNT BREAKDOWN

### By Category:

| Category | Count | File | Purpose |
|----------|-------|------|---------|
| Core Domain Objects | 81 | InterfaceAdditions.cs | Main business objects |
| Factory Interfaces | 49 | FactoryInterfaceAdditions.cs | Object creation |
| Repository Interfaces | 33 | RepositoryInterfaceAdditions.cs | Query/access |
| **TOTAL** | **163** | | Complete object model |

---

## CORE DOMAIN INTERFACES BY FEATURE AREA

### Lexicon Objects (12)
ILexEntry, ILexSense, ILexExampleSentence, ILexReference, ILexEntryRef, ILexEntryType, ILexDb, ILexPronunciation, IReversalIndex, IReversalIndexEntry, IPunctuationForm, IVariantComponentLexeme

### Morphology & Grammar (20)
IMoForm, IMoMorphSynAnalysis, IMoStemMsa, IMoAffixProcess, IMoInflAffixTemplate, IMoInflAffixSlot, IMoMorphType, IMoMorphData, IPartOfSpeech, IPhPhoneme, IPhEnvironment, IPhRegularRule, IPhMetathesisRule, IPhSegmentRule, IPhSegRuleRHS, IPhContextOrVar, IPhPhonData, IFsFeatureSystem, IFsFeatStruc, IFsFeatStrucType

### Feature System Objects (7)
IFsAbstractStructure, IFsClosedFeature, IFsClosedValue, IFsComplexValue, IFsSymFeatVal, IFsFeatureSpecification

### Text & Discourse (11)
IText, IStText, IStTxtPara, IStPara, ISegment, IWfiWordform, IWfiAnalysis, IWfiGloss, IWfiMorphBundle, ITextTag, IStFootnote

### Scripture Objects (11)
IScripture, IScrBook, IScrSection, IScrTxtPara, IScrFootnote, IScrDraft, IScrBookRef, IScrImportSet, IScrMarkerMapping, IScrScriptureNote, IScrBookAnnotations

### Constituent Chart (5)
IConstChartClauseMarker, IConstChartMovedTextMarker, IConstChartWordGroup

### Anthropology & Research (5)
IRnResearchNbk, IRnGenericRec, ICmAgent, ICmAgentEvaluation, IPublication

### System & Project (8)
ILangProject, ICmPossibility, ICmPossibilityList, ICmFilter, ICmFile, ICmPicture, ICmCell, ICmTranslation, ICmBaseAnnotation, IPubHFSet

### Infrastructure (1)
ICmObject, ICmMajorObject, IAnalysis

---

## PROPERTY TYPES SYSTEMATICALLY MISSED IN AUDITS

### 1. COMPUTED/VIRTUAL PROPERTIES
These are read-only, calculated from base properties:
- ITsString ShortNameTSS { get; }
- ITsString DeletionTextTSS { get; }
- ITsString ChooserNameTS { get; }
- string SortKey { get; }
- int SortKey2 { get; }
- string SortKey2Alpha { get; }

### 2. BACK-REFERENCE PROPERTIES
Virtual properties that point backward in the object graph:
- IEnumerable<ICmObject> OwnedObjects { get; }
- IEnumerable<ICmObject> AllOwnedObjects { get; }
- HashSet<ICmObject> ReferringObjects { get; }
- IEnumerable<ILexEntryRef> VisibleComplexFormBackRefs { get; }
- IEnumerable<ILexReference> LexSenseReferences { get; }

### 3. GENERIC/PARAMETERIZED COLLECTION TYPES
Using generics, requiring special handling:
- ILcmReferenceSequence<ICmPossibility> DialectLabels { get; }
- ILcmOwningSequence<ICmPossibility> ScriptureAnnotationDfns { get; }
- IEnumerable<T> (various with type parameters)

### 4. WRITING SYSTEM-DEPENDENT PROPERTIES
Methods requiring writing system parameters:
- ITsString GetDefinitionOrGloss(string wsName, out int wsActual);
- ITsString OwnerOutlineNameForWs(int wsVern);
- ITsString ReversalNameForWs(int wsVern);

### 5. CONCATENATED COLLECTION PROPERTIES
Properties combining multiple collections:
- IEnumerable<ILexEntryType> EntryTypes (VariantEntryTypesRS + ComplexEntryTypesRS)
- IEnumerable<ILexEntry> NonTrivialEntryRoots (subset of PrimaryEntryRoots)

### 6. FACTORY-ONLY INTERFACES & SPECIAL CREATIONS
Factory methods with parameters not stored as properties:
- Create(Guid guid, int hvo, bool isHuman, string version)
- Create(IStTxtPara owner, ICmPossibility translationType)

---

## KNOWN GAPS IN FLEXLIBS COVERAGE

From MISSING_FEATURES_BY_CATEGORY.md:

### Grammar Operations (9 missing)
- IPhRegularRule: Description, Direction, Stratum
- IPhEnvironment: StringRepresentation, Patterns
- IFsFeatureSystem: Types, Features, Constraints

### Text Operations (3 missing)
- IText: IsTranslated
- IWfiAnalysis: Evaluations

### Notebook Operations (6 missing)
- IRnGenericRec: Locations, Sources (with add/remove operations)

### System Operations (13 missing)
- ILangProject: ExtLinkRootDir, LinkedFilesRootDir, WritingSystems
- IPublication: IsLandscape
- IWfiMorphBundle: InflType
- IPhEnvironment: Pattern operations

**Total documented gaps: 31 methods**

---

## WHY AUDITS KEEP FINDING NEW GAPS

1. **Computed properties not easily identified** from interface signatures
2. **Virtual back-references** don't appear in base data model
3. **Collection properties with filtering/concatenation** logic
4. **Special accessor methods** for different access patterns
5. **Multi-string variants** (both string and ITsString forms exist)
6. **Method operations** (non-properties) often overlooked
7. **Generic type parameters** requiring type-specific implementation

---

## RECOMMENDATIONS

1. **Systematically audit all 81 core interfaces**
   - For each interface, list ALL properties (including computed)
   - Identify which are simple, reference, collection, or virtual
   - Flag read-only vs read-write properties

2. **Create type-specific wrappers**
   - For ILcmReferenceSequence<T> collections
   - For ILcmOwningSequence<T> collections
   - For generic method overloads

3. **Document factory creation patterns**
   - Map all factory methods to domain objects
   - Identify required parameters vs optional
   - Create specialized factory operations

4. **Add computed property support**
   - ITsString properties need special handling
   - Virtual properties need documentation
   - Back-references need reverse-lookup support

5. **Complete collection operation coverage**
   - Add/remove operations for all RC/RS properties
   - Support filtered access patterns
   - Provide enumeration support

