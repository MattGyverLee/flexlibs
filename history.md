# flexlibs History

## Known Issues

None

## History

### 2.0.0 - 24 Nov 2025

**Major Release: Comprehensive CRUD Operations**

This release introduces a complete set of Operations classes providing intuitive, object-oriented access to all major FLEx data types. The new API significantly expands flexlibs capabilities while maintaining full backward compatibility with v1.x code.

**New Features:**

+ **44 Operations Classes** providing 793+ methods organized into 6 topic areas:
    + **Grammar** (8 classes): POSOperations, PhonemeOperations, GramCatOperations, NaturalClassOperations, EnvironmentOperations, PhonologicalRuleOperations, MorphRuleOperations, InflectionFeatureOperations
    + **Lexicon** (10 classes): LexEntryOperations, LexSenseOperations, ExampleOperations, PronunciationOperations, VariantOperations, AllomorphOperations, EtymologyOperations, LexReferenceOperations, ReversalOperations, SemanticDomainOperations
    + **Texts & Words** (10 classes): TextOperations, ParagraphOperations, SegmentOperations, WordformOperations, WfiAnalysisOperations, WfiGlossOperations, WfiMorphBundleOperations, MediaOperations, FilterOperations, DiscourseOperations
    + **Notebook** (5 classes): DataNotebookOperations, NoteOperations, PersonOperations, LocationOperations, AnthropologyOperations
    + **Lists** (6 classes): PossibilityListOperations, PublicationOperations, TranslationTypeOperations, OverlayOperations, ConfidenceOperations, AgentOperations
    + **System** (5 classes): WritingSystemOperations, CustomFieldOperations, ProjectSettingsOperations, AnnotationDefOperations, CheckOperations

+ **Organized Code Structure**: Operations files organized into topic folders matching FLEx's architecture:
    + `flexlibs/code/Grammar/`
    + `flexlibs/code/Lexicon/`
    + `flexlibs/code/TextsWords/`
    + `flexlibs/code/Notebook/`
    + `flexlibs/code/Lists/`
    + `flexlibs/code/System/`

+ **CRUD Operations**: Each Operations class provides comprehensive Create, Read, Update, and Delete methods for its data type

+ **Lazy Loading**: Operations classes are instantiated only when accessed via FLExProject properties (e.g., `project.POS`, `project.LexEntry`, `project.Texts`)

+ **Full Backward Compatibility**: All v1.x API methods remain available and unchanged. Existing code will continue to work without modification.

**Example Usage:**

```python
import flexlibs

flexlibs.FLExInitialize()
project = flexlibs.FLExProject()
project.OpenProject('MyProject', writeEnabled=True)

# Create a lexical entry with the new API
entry = project.LexEntry.Create("run", "stem")
sense = project.LexEntry.AddSense(entry, "to move rapidly on foot")
project.Senses.SetGloss(sense, "run", "en")

# Old v1.x API still works
allEntries = project.LexiconAllEntries()

project.CloseProject()
flexlibs.FLExCleanup()
```

**Breaking Changes:**

None. This release maintains 100% backward compatibility with v1.x.

### 1.2.8 - 10 Sep 2025

+ FLExProject functions:
    + Added LexiconClearListFieldSingle() 
    + Added LexiconSetLexemeForm()
    + Added LexiconGetExampleCustomFields()
    + Added LexiconGetAllomorphCustomFields()

### 1.2.7 - 25 Aug 2025

+ Supports Python 3.8 - 3.13
+ Supports FieldWorks 9.0.17 - 9.3.1

+ FLExProject functions:
    + Added GetFieldID()
    + Added support for Lists (single or multiple) in GetCustomFieldValue()
    + Added ListFieldPossibilityList()
    + Added ListFieldPossibilities()
    + Added ListFieldLookup()
    + Added LexiconSetListFieldSingle() 
    + Added LexiconSetListFieldMultiple() 

### 1.2.6 - 26 Jun 2025

+ Supports Python 3.8 - 3.13
+ Supports FieldWorks 9.0.17 - 9.2.8

### 1.2.5 - 13 Jun 2025

+ When generating the list of projects, check that the fwdata file 
  exists, not just the directory. [Issue #14]
+ New function:
    + OpenProjectInFW(projectName)
+ Tidied up the presentation of the API documentation.

### 1.2.4 - 14 Aug 2024

+ New FLExProject function:
    + ObjectRepository(repository)

### 1.2.3 - 9 Jul 2024

+ GetAllSemanticDomains() returns ICmSemanticDomain objects
+ New FLExProject functions:
    + Object(hvoOrGuid)
    + LexiconAllEntriesSorted()
    + GetLexicalRelationTypes()
    + GetPublications()
    + PublicationType(publicationName)

### 1.2.2 - 15 Nov 2023

+ Supports Python 3.8 - 3.12
+ Supports FieldWorks 9.0.4 - 9.1.25

### 1.2.1 - 29 Aug 2023

+ Supports Python 3.6 - 3.11
+ Supports FieldWorks 9.0.4 - 9.1.22

+ New FLExProject functions:
    + LexiconFieldIsMultiType() 
    + LexiconFieldIsAnyStringType()
    + LexiconGetSenseNumber()
    + LexiconSenseAnalysesCount()

### 1.2.0 - 16 Aug 2023

+ Moved to pythonnet 3.0.1, which supports FieldWorks 9.1.22

+ FieldWorks dlls no longer need to be included, so the package size 
  has been greatly reduced.

### 1.1.8 - 11 Apr 2023

+ Added LexiconClearField()
+ Updated Set/Get Field functions to handle MultiStrings and a WS 
  parameter (fully backward compatible).

### 1.1.6 - 24 Nov 2022

+ Added the DLLs needed to support FieldWorks 9.1.15/16
+ Added support for Texts to BuildGotoURL()

### 1.1.5 - 15 Oct 2022

+ Constrained pythonnet to < 3 since flexlibs breaks with the new v3.0.0 

### 1.1.3 - 24 Jun 2022

+ FLExProject now requires a CloseProject() call to save data and
  release the lock on the FLEx project.

### 1.1.2 - 20 Jun 2022

+ Configured as a package and published on PyPI
+ Includes .NET DLLs that are needed for compatibility with FLEx 9.0
  through to 9.1.9
  