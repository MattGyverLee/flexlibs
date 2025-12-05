# FlexLibs Missing Features - Organized by Category & Type

**Document Purpose:** Comprehensive list of missing FlexLibs features organized by LCM category and operation type, rather than by priority level.

**Total Missing:** 31 methods across 5 LCM sections

---

## CATEGORY 1: LEXICON OBJECTS

**Status:** ✅ COMPLETE - No missing features

All lexicon operations are fully implemented with 100% property coverage.

---

## CATEGORY 2: GRAMMAR & MORPHOLOGY OBJECTS

**Status:** 95% Complete - 9 missing methods

### Phonological Rules (IPhRegularRule)

**Operations Class:** `PhonologicalRuleOperations`

#### Text Field Operations (MultiString)
1. `GetDescription(rule, wsHandle=None)` - Get rule description text
2. `SetDescription(rule, text, wsHandle=None)` - Set rule description text

#### Enumeration Operations
3. `GetDirection(rule)` - Get rule direction (forward/backward enum value)
4. `SetDirection(rule, direction)` - Set rule direction (forward/backward)

#### Reference Operations
5. `GetStratum(rule)` - Get stratum reference (RA property)
6. `SetStratum(rule, stratum)` - Set stratum reference

---

### Phonological Environments (IPhEnvironment)

**Operations Class:** `EnvironmentOperations`

#### Computed Property Operations
1. `GetStringRepresentation(environment)` - Get textual representation (read-only, computed)
2. `GetLeftContextPattern(environment)` - Get pattern for left context (read-only)

---

### Feature Systems (IFsFeatureSystem)

**Operations Class:** `InflectionFeatureOperations`

#### Collection Operations (Complex)
1. `GetTypes(feature_system)` - Get feature types collection (read-only)

---

## CATEGORY 3: TEXT & DISCOURSE OBJECTS

**Status:** 90% Complete - 3 missing methods

### Texts (IText)

**Operations Class:** `TextOperations`

#### Boolean Flag Operations
1. `GetIsTranslated(text)` - Check if text translation is complete
2. `SetIsTranslated(text, value)` - Mark text as translated/untranslated

---

### Word Analyses (IWfiAnalysis)

**Operations Class:** `WfiAnalysisOperations`

#### Collection Operations (Reference)
1. `GetEvaluations(analysis)` - Get agent evaluations collection (RC property, read-only)

---

## CATEGORY 4: NOTEBOOK & ANTHROPOLOGY OBJECTS

**Status:** 95% Complete - 6 missing methods

### Notebook Records (IRnGenericRec)

**Operations Class:** `DataNotebookOperations`

#### Location Operations (Reference Collection - RC)
1. `GetLocations(record)` - Get locations where data was collected
2. `AddLocation(record, location)` - Link location to notebook record
3. `RemoveLocation(record, location)` - Unlink location from notebook record

#### Source/Bibliography Operations (Reference Collection - RC)
4. `GetSources(record)` - Get bibliographic sources linked to record
5. `AddSource(record, source)` - Link source/reference to record
6. `RemoveSource(record, source)` - Unlink source/reference from record

---

## CATEGORY 5: SYSTEM & PROJECT OBJECTS

**Status:** 90% Complete - 13 missing methods

### Project Settings (ILangProject)

**Operations Class:** `ProjectSettingsOperations`

#### Path Configuration Operations (String)
1. `GetExtLinkRootDir()` - Get external link root directory path
2. `SetExtLinkRootDir(path)` - Set external link root directory path
3. `GetLinkedFilesRootDir()` - Get linked files root directory path
4. `SetLinkedFilesRootDir(path)` - Set linked files root directory path

#### Writing System List Operations (String - comma-separated)
5. `GetAnalysisWritingSystems()` - Get list of analysis writing systems (read-only)
6. `GetVernacularWritingSystems()` - Get list of vernacular writing systems (read-only)

---

### Publications (IPublication)

**Operations Class:** `PublicationOperations`

#### Layout Property Operations (Boolean)
1. `GetIsLandscape(publication)` - Check if publication uses landscape orientation

---

### Morpheme Bundles (IWfiMorphBundle)

**Operations Class:** `WfiMorphBundleOperations`

#### Reference Operations (RA)
1. `GetInflType(bundle)` - Get inflection type reference
2. `SetInflType(bundle, type)` - Set inflection type reference

---

### Phonological Environments (Advanced)

**Operations Class:** `EnvironmentOperations`

#### Pattern Operations (String - Read-only)
1. `GetLeftContextPattern(environment)` - Get left context pattern string
2. `GetRightContextPattern(environment)` - Get right context pattern string

---

### Feature Systems (Advanced)

**Operations Class:** `InflectionFeatureOperations`

#### Collection Operations (Complex - Read-only)
1. `GetFeatures(feature_system)` - Get features collection
2. `GetFeatureConstraints(feature_system)` - Get feature constraints collection

---

## SUMMARY BY OPERATION TYPE

### Get Operations (Read-Only)
**Total: 18 methods**

| Category | Count | Methods |
|----------|-------|---------|
| Grammar/Morphology | 5 | GetDescription, GetDirection, GetStratum, GetStringRepresentation, GetTypes |
| Texts/Discourse | 2 | GetIsTranslated, GetEvaluations |
| Notebook | 2 | GetLocations, GetSources |
| System | 9 | GetExtLinkRootDir, GetLinkedFilesRootDir, GetAnalysisWritingSystems, GetVernacularWritingSystems, GetIsLandscape, GetInflType, GetLeftContextPattern, GetFeatures, GetFeatureConstraints |

---

### Set Operations (Write)
**Total: 7 methods**

| Category | Count | Methods |
|----------|-------|---------|
| Grammar/Morphology | 3 | SetDescription, SetDirection, SetStratum |
| Texts/Discourse | 1 | SetIsTranslated |
| System | 3 | SetExtLinkRootDir, SetLinkedFilesRootDir, SetInflType |

---

### Collection Add Operations
**Total: 3 methods**

| Category | Count | Methods |
|----------|-------|---------|
| Notebook | 2 | AddLocation, AddSource |
| (None in other categories) | - | - |

---

### Collection Remove Operations
**Total: 3 methods**

| Category | Count | Methods |
|----------|-------|---------|
| Notebook | 2 | RemoveLocation, RemoveSource |
| (None in other categories) | - | - |

---

## SUMMARY BY PROPERTY TYPE

### MultiString Properties (Multilingual Text)
**Total: 2 methods (1 property)**
- PhonologicalRuleOperations: Description (Get/Set)

### Boolean Properties
**Total: 3 methods (2 properties)**
- TextOperations: IsTranslated (Get/Set)
- PublicationOperations: IsLandscape (Get only)

### Enumeration Properties
**Total: 2 methods (1 property)**
- PhonologicalRuleOperations: Direction (Get/Set)

### String Properties (Simple)
**Total: 4 methods (2 properties)**
- ProjectSettingsOperations: ExtLinkRootDir (Get/Set)
- ProjectSettingsOperations: LinkedFilesRootDir (Get/Set)

### String Properties (Read-Only/Computed)
**Total: 5 methods**
- EnvironmentOperations: StringRepresentation, LeftContextPattern, RightContextPattern
- ProjectSettingsOperations: AnalysisWritingSystems, VernacularWritingSystems

### Reference Atomic (RA) Properties
**Total: 4 methods (2 properties)**
- PhonologicalRuleOperations: Stratum (Get/Set)
- WfiMorphBundleOperations: InflType (Get/Set)

### Reference Collection (RC) Properties
**Total: 9 methods (3 properties)**
- DataNotebookOperations: Locations (Get/Add/Remove)
- DataNotebookOperations: Sources (Get/Add/Remove)
- WfiAnalysisOperations: Evaluations (Get only)

### Complex Collection Properties (Read-Only)
**Total: 2 methods**
- InflectionFeatureOperations: Types, Features, FeatureConstraints

---

## IMPLEMENTATION NOTES BY CATEGORY

### Grammar/Morphology (9 methods)
**Complexity:** Medium
- Most are standard Get/Set operations on existing objects
- Direction is an enum (requires enum mapping)
- StringRepresentation is computed (read-only)
- Collections are advanced features (low usage)

### Texts/Discourse (3 methods)
**Complexity:** Low
- Simple boolean flag operations
- Evaluations is read-only collection

### Notebook (6 methods)
**Complexity:** Low-Medium
- Standard RC collection operations (locations, sources)
- Pattern already established with Researchers/Participants
- LocationsRC and SourcesRC likely exist in LCM

### System (13 methods)
**Complexity:** Low-Medium
- Path operations are simple string Get/Set
- WS list getters return comma-separated strings
- IsLandscape is simple boolean getter
- InflType is standard RA reference

---

## PROPERTY FIELD MAPPINGS (LCM)

### IRnGenericRec (Notebook Records)
```
LocationsRC          : Reference Collection → ICmLocation
SourcesRC            : Reference Collection → ICmPossibility (or similar)
```

### IPhRegularRule (Phonological Rules)
```
Description          : MultiString
Direction            : Enum (forward/backward)
Stratum              : Reference Atomic → IMoStratum
```

### IText (Texts)
```
IsTranslated         : Boolean
```

### ILangProject (Project)
```
ExtLinkRootDir       : String
LinkedFilesRootDir   : String
AnalysisWss          : String (comma-separated)
CurVernWss           : String (comma-separated)
```

### IWfiMorphBundle (Morpheme Bundles)
```
InflType             : Reference Atomic → ICmPossibility
```

### IWfiAnalysis (Word Analysis)
```
Evaluations          : Reference Collection → IAgentEvaluation
```

### IPublication (Publications)
```
IsLandscape          : Boolean
```

### IPhEnvironment (Environments)
```
StringRepresentation : String (computed/virtual)
LeftContext.Pattern  : String (computed)
RightContext.Pattern : String (computed)
```

### IFsFeatureSystem (Feature Systems)
```
Types                : Owning Collection → complex
Features             : Owning Collection → complex
FeatureConstraints   : Owning Collection → complex
```

---

## ESTIMATED IMPLEMENTATION TIME

### By Category
- **Lexicon:** 0 hours (complete)
- **Grammar/Morphology:** 3-4 hours (9 methods)
- **Texts/Discourse:** 1 hour (3 methods)
- **Notebook:** 2 hours (6 methods)
- **System:** 3-4 hours (13 methods)

**Total: 9-11 hours** (~1.5 working days)

### By Complexity
- **Simple Get/Set (21 methods):** ~6 hours
- **Collection Operations (9 methods):** ~3 hours
- **Read-Only/Computed (2 methods):** ~0.5 hours

---

**Document Version:** 1.0
**Date:** December 5, 2025
**Source:** FLEXLIBS_COMPLETION_PRIORITIES.md
**Organization:** By LCM Category → Operation Type → Property Type
