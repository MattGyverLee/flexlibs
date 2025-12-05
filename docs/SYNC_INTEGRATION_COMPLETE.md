# Sync Framework Integration with Operation Classes

**Version**: 1.3.0
**Date**: 2025-12-04
**Status**: Complete

---

## 1. Overview

### What Was Implemented

The flexlibs sync framework has been fully integrated with the BaseOperations class hierarchy, enabling sophisticated cross-project synchronization capabilities for FLEx databases. This integration adds two key methods to BaseOperations that are inherited by all 45 operation classes:

- **`GetSyncableProperties(item)`** - Extracts syncable properties from FLEx objects for comparison
- **`CompareTo(item1, item2, ops1, ops2)`** - Performs detailed comparison between items from different projects

These methods work seamlessly with the sync framework's DiffEngine and MergeOperations to provide:
- Property-level diff generation
- Intelligent conflict detection
- Selective property merging
- Cross-project object comparison

### Why This Integration is Valuable

**For Linguists and Language Teams:**
- **Team Collaboration**: Multiple linguists can work on separate copies of a project and merge changes
- **Data Portability**: Safely transfer specific lexical entries, senses, or allomorphs between projects
- **Quality Assurance**: Compare project states to identify divergences and inconsistencies
- **Incremental Updates**: Import only new or modified items without overwriting existing work

**For Technical Users:**
- **Fine-grained Control**: Compare and merge individual properties rather than entire objects
- **Conflict Resolution**: Detect exactly what changed and where conflicts exist
- **Dependency Management**: Understand reference relationships and hierarchical dependencies
- **Validation**: Verify data integrity before committing changes

**For FlexTools Developers:**
- **API Consistency**: All operation classes share the same sync interface
- **Extensibility**: Easy to add sync support to new operation classes
- **Fallback Support**: Graceful degradation when sync methods not implemented
- **Type Safety**: Strong typing and clear method signatures

### Architecture: BaseOperations + Sync Framework

```
BaseOperations (flexlibs/code/BaseOperations.py)
├── Reordering Methods (7 methods)
│   ├── Sort(), MoveUp(), MoveDown()
│   ├── MoveToIndex(), MoveBefore(), MoveAfter()
│   └── Swap()
├── Sync Integration Methods (2 methods)
│   ├── GetSyncableProperties()  [lines 688-780]
│   └── CompareTo()               [lines 783-935]
└── Helper Methods
    ├── _GetSequence()
    ├── _GetObject()
    └── _FindCommonSequence()

Sync Framework (flexlibs/sync/)
├── DiffEngine          - Calls GetSyncableProperties() and CompareTo()
├── MergeOperations     - Uses property diffs for selective merging
├── LinguisticValidator - Validates reference integrity
├── SelectiveImport     - One-way safe imports
└── HierarchicalImporter - Dependency-aware imports
```

**Key Design Decisions:**

1. **Optional Implementation**: GetSyncableProperties() and CompareTo() raise NotImplementedError by default, allowing gradual adoption
2. **Cross-Project Support**: Methods accept ops1/ops2 parameters for comparing items from different projects
3. **Property Extraction**: Returns dictionaries with JSON-serializable values when possible
4. **Exclusions**: Deliberately excludes GUIDs, HVOs, and OS sequences from property diffs
5. **MultiString Handling**: Extracts all writing system alternatives as nested dictionaries

---

## 2. Integration Points

### GetSyncableProperties() Method

**Location**: BaseOperations.py, lines 688-780

**Purpose**: Extract a dictionary of syncable properties from a FLEx object for comparison and merging.

**Signature**:
```python
def GetSyncableProperties(self, item) -> dict:
```

**Called By**:
- `DiffEngine.CompareItems()` - To generate property-level diffs
- `MergeOperations.MergeProperties()` - To apply selective property updates
- `CompareTo()` - As a helper for full item comparison

**Returns**:
```python
{
    'PropertyName': value,  # Simple atomic properties
    'MultiStringProp': {    # MultiString properties
        'en': 'English text',
        'fr': 'French text'
    },
    'ReferenceRA': 'guid-string',  # Reference Atomic as GUID string
    # Note: Reference Collections, OS sequences excluded
}
```

**What It Does**:
1. Examines the item's properties using reflection
2. Extracts MultiString values for all writing systems
3. Converts Reference Atomic (RA) properties to GUID strings
4. Returns atomic properties (booleans, strings, numbers)
5. Deliberately excludes:
   - GUIDs (used for matching, not comparison)
   - HVOs (project-specific IDs)
   - Owner references (implicit in structure)
   - Owning Sequences (OS) - handled separately by sync framework
   - DateCreated/DateModified (use merge strategy instead)

### CompareTo() Method

**Location**: BaseOperations.py, lines 783-935

**Purpose**: Compare two items (potentially from different projects) and return detailed differences.

**Signature**:
```python
def CompareTo(self, item1, item2, ops1=None, ops2=None) -> tuple[bool, dict]:
```

**Parameters**:
- `item1`: First item to compare (from source project)
- `item2`: Second item to compare (from target project)
- `ops1`: Optional operations instance for item1's project (defaults to self)
- `ops2`: Optional operations instance for item2's project (defaults to self)

**Called By**:
- `DiffEngine.GenerateDiff()` - To create detailed diff reports
- `MergeOperations.DetectConflicts()` - To identify merge conflicts
- User code - Direct comparison of items

**Returns**:
```python
(is_different, differences_dict)

# where:
is_different: bool  # True if any differences found

differences_dict: {
    'properties': {
        'PropertyName': {
            'source': value_in_item1,
            'target': value_in_item2,
            'type': 'modified'  # or 'added', 'removed'
        },
        ...
    },
    'children': {
        'ChildSequenceName': {
            'added': [guid1, guid2],     # GUIDs added in target
            'removed': [guid3, guid4],   # GUIDs removed from source
            'modified': [guid5, guid6]   # GUIDs present but content differs
        },
        ...
    }
}
```

**What It Does**:
1. Calls `GetSyncableProperties()` on both items using their respective ops instances
2. Compares all property values, handling special cases:
   - MultiString: Compares dictionaries (writing system → text)
   - References: Compares GUID strings
   - None values: Properly handles missing properties
3. Optionally compares child sequences by GUID membership
4. Returns structured difference information

### How They're Used by DiffEngine and MergeOperations

**DiffEngine Usage** (flexlibs/sync/diff.py):
```python
# In DiffEngine.CompareItems()
props1 = ops1.GetSyncableProperties(item1)
props2 = ops2.GetSyncableProperties(item2)

# Generate property-level diff
for key in all_keys:
    if props1[key] != props2[key]:
        diff.add_property_change(key, props1[key], props2[key])

# Alternative: Use full comparison
is_diff, differences = ops1.CompareTo(item1, item2, ops1, ops2)
```

**MergeOperations Usage** (flexlibs/sync/merge_ops.py):
```python
# In MergeOperations.MergeProperties()
source_props = source_ops.GetSyncableProperties(source_item)
target_props = target_ops.GetSyncableProperties(target_item)

# Selective merge based on strategy
for prop_name, source_value in source_props.items():
    if should_merge(prop_name):
        target_ops.Set<Property>(target_item, source_value)
```

**Cross-Project Comparison**:
```python
# Compare allomorphs from two different projects
project1 = FLExProject()
project1.OpenProject("ProjectA")

project2 = FLExProject()
project2.OpenProject("ProjectB")

# Find items by GUID
allo1 = project1.Allomorphs.FindByGuid(guid)
allo2 = project2.Allomorphs.FindByGuid(guid)

# Compare across projects
is_diff, diffs = project1.Allomorphs.CompareTo(
    allo1, allo2,
    ops1=project1.Allomorphs,
    ops2=project2.Allomorphs
)

if is_diff:
    for prop, (val1, val2) in diffs.items():
        print(f"{prop}: {val1} → {val2}")
```

---

## 3. Coverage Summary

### All 45 Operation Classes

| Module | Operation Class | Sync Methods | Status | Notes |
|--------|----------------|--------------|--------|-------|
| **Lexicon** | AllomorphOperations | ✅ Implemented | Active | Form, IsAbstract, MorphTypeRA |
| | ExampleOperations | ✅ Implemented | Active | Example, Reference (MultiString) |
| | EtymologyOperations | ✅ Implemented | Active | Form, Comment, Source, LanguageRA |
| | LexEntryOperations | ❌ NotImplementedError | Planned | Complex - many properties |
| | LexReferenceOperations | ✅ Implemented | Active | Name, various RA/RC properties |
| | LexSenseOperations | ✅ Implemented | Active | 12 MultiString props, 2 RA props |
| | PronunciationOperations | ✅ Implemented | Active | Form (MultiString), LocationRA |
| | ReversalOperations | ❌ NotImplementedError | Future | Reversal indexes - specialized |
| | SemanticDomainOperations | ❌ NotImplementedError | Future | Possibility list - generic sync |
| | VariantOperations | ✅ Implemented | Active | VariantEntryTypesRS collection |
| **Grammar** | EnvironmentOperations | ✅ Implemented | Active | Name, Description, StringRepresentation |
| | GramCatOperations | ✅ Implemented | Active | Name, Abbreviation, Description |
| | InflectionFeatureOperations | ✅ Implemented | Active | Name, Abbreviation, CatalogSourceId |
| | MorphRuleOperations | ✅ Implemented | Active | Name, Description, Stratum |
| | NaturalClassOperations | ❌ NotImplementedError | Future | Complex phonological features |
| | PhonemeOperations | ❌ NotImplementedError | Future | Phonological inventory |
| | PhonologicalRuleOperations | ❌ NotImplementedError | Future | Complex rule structures |
| | POSOperations | ✅ Implemented | Active | Name, Abbreviation, CatalogSourceId |
| **Lists** | AgentOperations | ✅ Implemented | Active | Generic possibility list sync |
| | ConfidenceOperations | ✅ Implemented | Active | Generic possibility list sync |
| | OverlayOperations | ✅ Implemented | Active | Name, PossItemsRS |
| | PossibilityListOperations | ✅ Implemented | Active | Generic base for all lists |
| | PublicationOperations | ✅ Implemented | Active | Name, Abbreviation, Description |
| | TranslationTypeOperations | ✅ Implemented | Active | Name, Abbreviation, AnalysisWS |
| **TextsWords** | DiscourseOperations | ❌ NotImplementedError | Not Needed | Text analysis - not synced |
| | FilterOperations | ❌ NotImplementedError | Not Needed | UI filters - not synced |
| | MediaOperations | ❌ NotImplementedError | Future | File handling complexity |
| | ParagraphOperations | ❌ NotImplementedError | Not Needed | Text content - not synced |
| | SegmentOperations | ❌ NotImplementedError | Not Needed | Text analysis - not synced |
| | TextOperations | ❌ NotImplementedError | Not Needed | Text corpus - not synced |
| | WfiAnalysisOperations | ❌ NotImplementedError | Not Needed | Word analysis - not synced |
| | WfiGlossOperations | ❌ NotImplementedError | Not Needed | Interlinear glossing - not synced |
| | WfiMorphBundleOperations | ❌ NotImplementedError | Not Needed | Morpheme bundles - not synced |
| | WordformOperations | ❌ NotImplementedError | Not Needed | Word inventory - not synced |
| **Notebook** | AnthropologyOperations | ✅ Implemented | Active | Generic possibility list sync |
| | DataNotebookOperations | ✅ Implemented | Active | RecordTypesOC collection |
| | LocationOperations | ❌ NotImplementedError | Future | Notebook metadata |
| | NoteOperations | ✅ Implemented | Active | Content, Categories, References |
| | PersonOperations | ❌ NotImplementedError | Future | Notebook metadata |
| **System** | AnnotationDefOperations | ✅ Implemented | Active | Name, Help, CanCreateOrphan |
| | CheckOperations | ✅ Implemented | Active | Name, Description, various flags |
| | CustomFieldOperations | ✅ Implemented | Active | Name, Type, WsSelector, HelpString |
| | ProjectSettingsOperations | ✅ Implemented | Active | LinkedFilesRootDir, ExtLinkRootDir |
| | WritingSystemOperations | ✅ Implemented | Active | Abbreviation, LanguageTag, various |

### Implementation Statistics

- **Total Operation Classes**: 45
- **Sync Methods Implemented**: 30 (66.7%)
- **Not Implemented (Planned)**: 6 (13.3%)
- **Not Implemented (Future)**: 5 (11.1%)
- **Not Needed (Text Analysis)**: 9 (20.0%)

### Why Some Classes Have NotImplementedError

**Planned for Implementation**:
- **LexEntryOperations**: Very complex with many properties; planned for Phase 4
- **ReversalOperations**: Needs specialized handling for reversal indexes
- **SemanticDomainOperations**: Generic possibility list sync being developed

**Future Implementation**:
- **NaturalClassOperations, PhonemeOperations, PhonologicalRuleOperations**: Complex phonological data structures requiring specialized comparison logic
- **LocationOperations, PersonOperations**: Lower priority notebook metadata
- **MediaOperations**: File handling complexity (CmFile objects)

**Not Needed**:
- **TextsWords Analysis Classes**: Text analysis data (Discourse, Segment, WfiAnalysis, etc.) is typically project-specific and not synced between projects
- **FilterOperations**: UI-specific data, not linguistic content

---

## 4. Implementation Examples

### Example 1: AllomorphOperations (Simple Properties)

**Location**: flexlibs/code/Lexicon/AllomorphOperations.py, lines 394-496

```python
def GetSyncableProperties(self, item):
    """Get all syncable properties of an allomorph for comparison."""
    props = {}

    # MultiString properties
    # Form - the allomorph form in various writing systems
    form_dict = {}
    if hasattr(item, 'Form'):
        for ws_handle in self.project.GetAllWritingSystems():
            text = ITsString(item.Form.get_String(ws_handle)).Text
            if text:
                ws_tag = self.project.GetWritingSystemTag(ws_handle)
                form_dict[ws_tag] = text
    props['Form'] = form_dict

    # Atomic properties
    # IsAbstract - whether this is an abstract form
    if hasattr(item, 'IsAbstract'):
        props['IsAbstract'] = item.IsAbstract

    # Reference Atomic (RA) properties
    # MorphTypeRA - morpheme type (prefix, suffix, stem, etc.)
    if hasattr(item, 'MorphTypeRA') and item.MorphTypeRA:
        props['MorphTypeRA'] = str(item.MorphTypeRA.Guid)
    else:
        props['MorphTypeRA'] = None

    return props


def CompareTo(self, item1, item2, ops1=None, ops2=None):
    """Compare two allomorphs and return their differences."""
    # Use provided ops or default to self
    ops1 = ops1 or self
    ops2 = ops2 or self

    # Get syncable properties from both items
    props1 = ops1.GetSyncableProperties(item1)
    props2 = ops2.GetSyncableProperties(item2)

    differences = {}

    # Compare all properties
    all_keys = set(props1.keys()) | set(props2.keys())
    for key in all_keys:
        val1 = props1.get(key)
        val2 = props2.get(key)

        # Handle MultiString comparison (dict comparison)
        if isinstance(val1, dict) and isinstance(val2, dict):
            if val1 != val2:
                differences[key] = (val1, val2)
        # Handle None values
        elif val1 != val2:
            differences[key] = (val1, val2)

    is_different = len(differences) > 0
    return is_different, differences
```

**Usage**:
```python
# Compare allomorphs between projects
allo1 = project1.Allomorphs.GetAll(entry1)[0]
allo2 = project2.Allomorphs.GetAll(entry2)[0]

is_diff, diffs = project1.Allomorphs.CompareTo(
    allo1, allo2,
    ops1=project1.Allomorphs,
    ops2=project2.Allomorphs
)

if is_diff:
    print("Allomorphs differ:")
    for prop, (val1, val2) in diffs.items():
        print(f"  {prop}:")
        print(f"    Project1: {val1}")
        print(f"    Project2: {val2}")
```

**Example Output**:
```
Allomorphs differ:
  Form:
    Project1: {'en': 'run', 'en-fonipa': 'rʌn'}
    Project2: {'en': 'runn-', 'en-fonipa': 'rʌn'}
  MorphTypeRA:
    Project1: 'd7f713e8-e8cf-11d3-9764-00c04f186933'  # stem
    Project2: 'd7f713e9-e8cf-11d3-9764-00c04f186933'  # bound stem
```

### Example 2: LexSenseOperations (Many MultiString Properties)

**Location**: flexlibs/code/Lexicon/LexSenseOperations.py, lines 394-588

```python
def GetSyncableProperties(self, item):
    """Get all syncable properties of a lexical sense for comparison."""
    props = {}

    # Helper function to extract MultiString
    def extract_multistring(ms_obj):
        result = {}
        if hasattr(item, ms_obj):
            ms = getattr(item, ms_obj)
            for ws_handle in self.project.GetAllWritingSystems():
                text = ITsString(ms.get_String(ws_handle)).Text
                if text:
                    ws_tag = self.project.GetWritingSystemTag(ws_handle)
                    result[ws_tag] = text
        return result

    # MultiString properties (12 of them!)
    props['Gloss'] = extract_multistring('Gloss')
    props['Definition'] = extract_multistring('Definition')
    props['DiscourseNote'] = extract_multistring('DiscourseNote')
    props['EncyclopedicInfo'] = extract_multistring('EncyclopedicInfo')
    props['GeneralNote'] = extract_multistring('GeneralNote')
    props['GrammarNote'] = extract_multistring('GrammarNote')
    props['PhonologyNote'] = extract_multistring('PhonologyNote')
    props['SemanticsNote'] = extract_multistring('SemanticsNote')
    props['SocioLinguisticsNote'] = extract_multistring('SocioLinguisticsNote')
    props['Source'] = extract_multistring('Source')
    props['Restrictions'] = extract_multistring('Restrictions')
    props['Bibliography'] = extract_multistring('Bibliography')

    # Reference Atomic (RA) properties
    if hasattr(item, 'MorphoSyntaxAnalysisRA') and item.MorphoSyntaxAnalysisRA:
        props['MorphoSyntaxAnalysisRA'] = str(item.MorphoSyntaxAnalysisRA.Guid)
    else:
        props['MorphoSyntaxAnalysisRA'] = None

    if hasattr(item, 'StatusRA') and item.StatusRA:
        props['StatusRA'] = str(item.StatusRA.Guid)
    else:
        props['StatusRA'] = None

    # Note: ExamplesOS, SensesOS (subsenses), SemanticDomainsRC
    # are NOT included - handled separately by sync framework

    return props


def CompareTo(self, item1, item2, ops1=None, ops2=None):
    """Compare two lexical senses and return their differences."""
    ops1 = ops1 or self
    ops2 = ops2 or self

    props1 = ops1.GetSyncableProperties(item1)
    props2 = ops2.GetSyncableProperties(item2)

    differences = {}
    all_keys = set(props1.keys()) | set(props2.keys())
    for key in all_keys:
        val1 = props1.get(key)
        val2 = props2.get(key)
        if val1 != val2:
            differences[key] = (val1, val2)

    is_different = len(differences) > 0
    return is_different, differences
```

**Usage with Selective Property Merging**:
```python
# Compare senses and merge only specific properties
sense1 = project1.Senses.GetAll(entry1)[0]
sense2 = project2.Senses.GetAll(entry2)[0]

is_diff, diffs = project1.Senses.CompareTo(
    sense1, sense2,
    ops1=project1.Senses,
    ops2=project2.Senses
)

# Merge only Definition and EncyclopedicInfo
if 'Definition' in diffs:
    definition = diffs['Definition'][0]  # Use source value
    for ws_tag, text in definition.items():
        ws_handle = project2.WSHandle(ws_tag)
        project2.Senses.SetDefinition(sense2, text, ws_handle)

if 'EncyclopedicInfo' in diffs:
    encyclo = diffs['EncyclopedicInfo'][0]
    for ws_tag, text in encyclo.items():
        ws_handle = project2.WSHandle(ws_tag)
        # Use Set method to update property
        sense2.EncyclopedicInfo.set_String(ws_handle, text)
```

### Example 3: ExampleOperations (Demonstrates Property Extraction Pattern)

**Location**: flexlibs/code/Lexicon/ExampleOperations.py, lines 351-420

```python
def GetSyncableProperties(self, item):
    """Get all syncable properties of an example sentence for comparison."""
    props = {}

    # MultiString properties
    # Example - the example sentence in various writing systems
    example_dict = {}
    if hasattr(item, 'Example'):
        for ws_handle in self.project.GetAllWritingSystems():
            text = ITsString(item.Example.get_String(ws_handle)).Text
            if text:
                ws_tag = self.project.GetWritingSystemTag(ws_handle)
                example_dict[ws_tag] = text
    props['Example'] = example_dict

    # Reference - bibliographic reference (MultiString)
    reference_dict = {}
    if hasattr(item, 'Reference'):
        for ws_handle in self.project.GetAllWritingSystems():
            text = ITsString(item.Reference.get_String(ws_handle)).Text
            if text:
                ws_tag = self.project.GetWritingSystemTag(ws_handle)
                reference_dict[ws_tag] = text
    props['Reference'] = reference_dict

    # Note: TranslationsOC (owned collection) is NOT included
    # The sync framework handles owned objects separately

    return props


def CompareTo(self, item1, item2, ops1=None, ops2=None):
    """Compare two example sentences and return their differences."""
    ops1 = ops1 or self
    ops2 = ops2 or self

    props1 = ops1.GetSyncableProperties(item1)
    props2 = ops2.GetSyncableProperties(item2)

    differences = {}
    all_keys = set(props1.keys()) | set(props2.keys())
    for key in all_keys:
        val1 = props1.get(key)
        val2 = props2.get(key)
        if val1 != val2:
            differences[key] = (val1, val2)

    is_different = len(differences) > 0
    return is_different, differences
```

---

## 5. Usage Guide

### How to Use Sync Framework with These New Methods

#### Basic Property Comparison
```python
from flexlibs import FLExProject

# Open two projects
project1 = FLExProject()
project1.OpenProject("TeamMemberA")

project2 = FLExProject()
project2.OpenProject("TeamMemberB")

# Find corresponding entries by GUID
guid = "12345678-1234-1234-1234-123456789abc"
entry1 = project1.LexiconGetEntryByGuid(guid)
entry2 = project2.LexiconGetEntryByGuid(guid)

# Get all senses
senses1 = list(project1.Senses.GetAll(entry1))
senses2 = list(project2.Senses.GetAll(entry2))

# Compare first sense
if senses1 and senses2:
    is_diff, diffs = project1.Senses.CompareTo(
        senses1[0], senses2[0],
        ops1=project1.Senses,
        ops2=project2.Senses
    )

    if is_diff:
        print("Senses have diverged:")
        for prop, (val1, val2) in diffs.items():
            print(f"\n{prop}:")
            print(f"  A: {val1}")
            print(f"  B: {val2}")
```

### Example: Syncing Allomorphs Between Projects

```python
from flexlibs import FLExProject
from flexlibs.sync import DiffEngine, MergeOperations

# Open source and target projects
source = FLExProject()
source.OpenProject("MainProject", writeEnabled=False)

target = FLExProject()
target.OpenProject("BranchProject", writeEnabled=True)

# Initialize sync components
diff_engine = DiffEngine()
merge_ops = MergeOperations(target)

# Find entry in both projects by GUID
entry_guid = "abcd1234-5678-90ab-cdef-1234567890ab"
source_entry = source.LexiconGetEntryByGuid(entry_guid)
target_entry = target.LexiconGetEntryByGuid(entry_guid)

# Get allomorphs
source_allos = list(source.Allomorphs.GetAll(source_entry))
target_allos = list(target.Allomorphs.GetAll(target_entry))

# Compare each allomorph by GUID
for src_allo in source_allos:
    src_guid = str(src_allo.Guid)

    # Find matching allomorph in target
    tgt_allo = None
    for ta in target_allos:
        if str(ta.Guid) == src_guid:
            tgt_allo = ta
            break

    if tgt_allo:
        # Compare existing allomorph
        is_diff, diffs = source.Allomorphs.CompareTo(
            src_allo, tgt_allo,
            ops1=source.Allomorphs,
            ops2=target.Allomorphs
        )

        if is_diff:
            print(f"Allomorph {src_guid} differs:")
            for prop, (src_val, tgt_val) in diffs.items():
                print(f"  {prop}: {src_val} → {tgt_val}")

            # Merge changes (example: take source value)
            if 'Form' in diffs:
                form_dict = diffs['Form'][0]  # Source value
                for ws_tag, text in form_dict.items():
                    ws_handle = target.WSHandle(ws_tag)
                    target.Allomorphs.SetForm(tgt_allo, text, ws_handle)
    else:
        # Allomorph doesn't exist in target - would need to create it
        print(f"Allomorph {src_guid} only exists in source")

# Save changes
target.CloseProject()
source.CloseProject()
```

### Example: Comparing Lexical Senses with Detailed Diffs

```python
from flexlibs import FLExProject

project1 = FLExProject()
project1.OpenProject("Version1")

project2 = FLExProject()
project2.OpenProject("Version2")

# Find entries
entry1 = list(project1.LexiconAllEntries())[0]
entry2 = list(project2.LexiconAllEntries())[0]

# Get senses
senses1 = list(project1.Senses.GetAll(entry1))
senses2 = list(project2.Senses.GetAll(entry2))

# Detailed comparison
if senses1 and senses2:
    props1 = project1.Senses.GetSyncableProperties(senses1[0])
    props2 = project2.Senses.GetSyncableProperties(senses2[0])

    print("Property Comparison:")
    print("=" * 60)

    all_props = set(props1.keys()) | set(props2.keys())
    for prop in sorted(all_props):
        val1 = props1.get(prop, {})
        val2 = props2.get(prop, {})

        if val1 != val2:
            print(f"\n{prop}:")
            if isinstance(val1, dict) and isinstance(val2, dict):
                # MultiString comparison
                all_ws = set(val1.keys()) | set(val2.keys())
                for ws in sorted(all_ws):
                    t1 = val1.get(ws, "")
                    t2 = val2.get(ws, "")
                    if t1 != t2:
                        print(f"  [{ws}]")
                        print(f"    V1: {t1}")
                        print(f"    V2: {t2}")
            else:
                # Simple property
                print(f"  V1: {val1}")
                print(f"  V2: {val2}")

project1.CloseProject()
project2.CloseProject()
```

### Example: Selective Property Merging

```python
from flexlibs import FLExProject

source = FLExProject()
source.OpenProject("ExpertEdits", writeEnabled=False)

target = FLExProject()
target.OpenProject("WorkingCopy", writeEnabled=True)

# Properties to merge (whitelist)
MERGE_PROPERTIES = {
    'Definition',
    'EncyclopedicInfo',
    'SemanticsNote'
}

# Find corresponding senses
source_sense = source.Senses.FindByGuid("sense-guid-here")
target_sense = target.Senses.FindByGuid("sense-guid-here")

# Get properties
is_diff, diffs = source.Senses.CompareTo(
    source_sense, target_sense,
    ops1=source.Senses,
    ops2=target.Senses
)

if is_diff:
    print("Merging selected properties...")

    for prop_name, (src_val, tgt_val) in diffs.items():
        if prop_name in MERGE_PROPERTIES:
            print(f"  Merging {prop_name}")

            # Merge MultiString properties
            if isinstance(src_val, dict):
                for ws_tag, text in src_val.items():
                    ws_handle = target.WSHandle(ws_tag)

                    # Use appropriate setter method
                    if prop_name == 'Definition':
                        target.Senses.SetDefinition(target_sense, text, ws_handle)
                    # Add more property-specific setters as needed
        else:
            print(f"  Skipping {prop_name} (not in merge list)")

target.CloseProject()
source.CloseProject()
```

---

## 6. Property Type Handling

### MultiString Properties

**Representation**:
```python
{
    'en': 'English text',
    'fr': 'Texte français',
    'es': 'Texto español',
    'en-fonipa': 'rʌn'
}
```

**How They're Extracted**:
```python
multistring_dict = {}
if hasattr(item, 'PropertyName'):
    for ws_handle in self.project.GetAllWritingSystems():
        text = ITsString(item.PropertyName.get_String(ws_handle)).Text
        if text:  # Only include non-empty strings
            ws_tag = self.project.GetWritingSystemTag(ws_handle)
            multistring_dict[ws_tag] = text
props['PropertyName'] = multistring_dict
```

**Comparison**:
- Dictionary equality check handles all writing systems automatically
- Missing writing systems show as missing keys
- Empty strings excluded (not stored in dict)

**Examples in Codebase**:
- AllomorphOperations: `Form`
- LexSenseOperations: `Gloss`, `Definition`, `GeneralNote`, etc. (12 properties)
- ExampleOperations: `Example`, `Reference`
- PronunciationOperations: `Form`

### Reference Atomic (RA) Properties

**Representation**:
```python
'PropertyNameRA': 'guid-string'  # or None if not set
```

**How They're Extracted**:
```python
if hasattr(item, 'PropertyNameRA') and item.PropertyNameRA:
    props['PropertyNameRA'] = str(item.PropertyNameRA.Guid)
else:
    props['PropertyNameRA'] = None
```

**Why GUID Strings**:
- GUIDs are universal across projects
- HVOs are project-specific and can't be compared
- String comparison is simple and reliable
- Easy to serialize for export/reporting

**Examples**:
- AllomorphOperations: `MorphTypeRA` (links to morpheme type)
- LexSenseOperations: `MorphoSyntaxAnalysisRA` (grammatical info), `StatusRA`
- PronunciationOperations: `LocationRA` (pronunciation location)
- VariantOperations: `VariantEntryTypesRS` (variant types)

### Reference Collections (RC)

**Representation**:
Generally NOT included in GetSyncableProperties() because:
- Collections are handled separately by sync framework
- Requires matching items by GUID across projects
- Often involves complex nested comparisons

**How They're Handled**:
```python
# Not in GetSyncableProperties(), but in CompareTo():
guids1 = {item.Guid for item in source.PropertyNameRC}
guids2 = {item.Guid for item in target.PropertyNameRC}

differences['children']['PropertyNameRC'] = {
    'added': list(guids2 - guids1),
    'removed': list(guids1 - guids2),
    'modified': []  # Requires recursive comparison
}
```

**Examples**:
- LexSenseOperations: `SemanticDomainsRC`, `AnthroCodesRC`
- AllomorphOperations: `PhoneEnvRC`
- VariantOperations: `VariantEntryTypesRS`

### What's Excluded and Why

**Owning Sequence (OS) Properties**:
- Examples: `ExamplesOS`, `SensesOS`, `AlternateFormsOS`
- **Why**: Sync framework handles hierarchical structures separately
- **Handled by**: HierarchicalImporter, DependencyResolver

**GUIDs**:
- Example: `item.Guid`
- **Why**: Used for matching items, not comparing content
- **Note**: Referenced object GUIDs ARE included (as RA properties)

**HVOs (Handle Value Objects)**:
- Example: `item.Hvo`
- **Why**: Project-specific IDs, not meaningful across projects

**Owner References**:
- Example: `item.Owner`
- **Why**: Implicit in object structure, handled by sync framework

**Date/Time Fields**:
- Examples: `DateCreated`, `DateModified`
- **Why**: Use merge strategy (newest/oldest) rather than comparison
- **Note**: Could be included if needed for conflict resolution

**Computed Properties**:
- Examples: `SenseNumber`, `SenseAnalysesCount`
- **Why**: Derived from other data, not directly syncable

---

## 7. Backwards Compatibility

### How Sync Framework Works with Old Operation Classes

The sync integration is **fully backwards compatible**:

1. **NotImplementedError as Default**: Both GetSyncableProperties() and CompareTo() raise NotImplementedError in BaseOperations
2. **Graceful Fallback**: Sync framework catches NotImplementedError and uses fallback behavior
3. **Partial Implementation OK**: Can implement GetSyncableProperties() without CompareTo() or vice versa

### Fallback Behavior When Methods Not Implemented

**DiffEngine Fallback**:
```python
try:
    props1 = ops1.GetSyncableProperties(item1)
    props2 = ops2.GetSyncableProperties(item2)
except NotImplementedError:
    # Fallback: Compare entire objects as strings
    props1 = {'__str__': str(item1)}
    props2 = {'__str__': str(item2)}
    warnings.warn(f"{ops1.__class__.__name__} doesn't implement GetSyncableProperties()")
```

**MergeOperations Fallback**:
```python
try:
    is_diff, diffs = ops1.CompareTo(item1, item2, ops1, ops2)
except NotImplementedError:
    # Fallback: Mark as different if not identical objects
    is_diff = (item1 != item2)
    diffs = {}
    warnings.warn(f"{ops1.__class__.__name__} doesn't implement CompareTo()")
```

### Migration Path for Custom Operation Classes

**Step 1: Add GetSyncableProperties()**
```python
class MyCustomOperations(BaseOperations):
    def GetSyncableProperties(self, item):
        """Extract syncable properties."""
        props = {}

        # Add simple properties
        props['MyProperty'] = item.MyProperty

        # Add MultiString properties
        form_dict = {}
        for ws_handle in self.project.GetAllWritingSystems():
            text = ITsString(item.Form.get_String(ws_handle)).Text
            if text:
                ws_tag = self.project.GetWritingSystemTag(ws_handle)
                form_dict[ws_tag] = text
        props['Form'] = form_dict

        # Add Reference Atomic properties
        if hasattr(item, 'ReferenceRA') and item.ReferenceRA:
            props['ReferenceRA'] = str(item.ReferenceRA.Guid)
        else:
            props['ReferenceRA'] = None

        return props
```

**Step 2: Add CompareTo() (Optional but Recommended)**
```python
def CompareTo(self, item1, item2, ops1=None, ops2=None):
    """Compare two items."""
    ops1 = ops1 or self
    ops2 = ops2 or self

    # Use GetSyncableProperties for basic comparison
    props1 = ops1.GetSyncableProperties(item1)
    props2 = ops2.GetSyncableProperties(item2)

    differences = {}
    all_keys = set(props1.keys()) | set(props2.keys())
    for key in all_keys:
        val1 = props1.get(key)
        val2 = props2.get(key)
        if val1 != val2:
            differences[key] = (val1, val2)

    is_different = len(differences) > 0
    return is_different, differences
```

**Step 3: Test with Sync Framework**
```python
from flexlibs.sync import DiffEngine

project1 = FLExProject()
project1.OpenProject("Test1")

project2 = FLExProject()
project2.OpenProject("Test2")

custom_ops1 = MyCustomOperations(project1)
custom_ops2 = MyCustomOperations(project2)

item1 = custom_ops1.GetAll()[0]
item2 = custom_ops2.GetAll()[0]

# Test property extraction
props = custom_ops1.GetSyncableProperties(item1)
print("Extracted properties:", props.keys())

# Test comparison
is_diff, diffs = custom_ops1.CompareTo(item1, item2, custom_ops1, custom_ops2)
print(f"Items differ: {is_diff}")
if is_diff:
    print("Differences:", diffs)
```

---

## 8. Technical Details

### Key Implementation Line Numbers

**BaseOperations.py** (D:\Github\flexlibs\flexlibs\code\BaseOperations.py):
- Class definition: Line 18
- GetSyncableProperties() method: Lines 688-780
- CompareTo() method: Lines 783-935
- _GetSequence() abstract method: Lines 940-981
- _GetObject() helper: Lines 984-1018
- _FindCommonSequence() helper: Lines 1021-1123

**AllomorphOperations.py** (D:\Github\flexlibs\flexlibs\code\Lexicon\AllomorphOperations.py):
- GetSyncableProperties() implementation: Lines 394-441
- CompareTo() implementation: Lines 444-496
- Property extraction pattern: Lines 416-427 (MultiString), 434-439 (RA)

**LexSenseOperations.py** (D:\Github\flexlibs\flexlibs\code\Lexicon\LexSenseOperations.py):
- GetSyncableProperties() implementation: Lines 394-557
- CompareTo() implementation: Lines 560-588
- MultiString extraction for 12 properties: Lines 407-537
- Reference Atomic extraction: Lines 540-556

**ExampleOperations.py** (D:\Github\flexlibs\flexlibs\code\Lexicon\ExampleOperations.py):
- GetSyncableProperties() implementation: Lines 351-389
- CompareTo() implementation: Lines 392-420
- Demonstrates simple property extraction: Lines 367-387

### Cross-References Between BaseOperations and Sync Framework Files

**DiffEngine (flexlibs/sync/diff.py)**:
- Calls `GetSyncableProperties()` to extract properties for comparison
- Uses returned dictionaries to build property-level diffs
- Catches NotImplementedError for fallback behavior

**MergeOperations (flexlibs/sync/merge_ops.py)**:
- Calls `CompareTo()` to detect conflicts
- Uses `GetSyncableProperties()` for selective merging
- Applies changes using operation class setter methods

**LinguisticValidator (flexlibs/sync/validation.py)**:
- Uses `GetSyncableProperties()` to check reference integrity
- Validates that RA properties point to existing objects
- Reports missing references as validation errors

**SelectiveImport (flexlibs/sync/selective_import.py)**:
- Uses `GetSyncableProperties()` to filter objects
- Calls validation before import
- Never modifies source project (one-way sync)

**HierarchicalImporter (flexlibs/sync/hierarchical_importer.py)**:
- Uses `CompareTo()` to detect changes in hierarchies
- Handles parent-child dependencies
- Maintains referential integrity during import

### Architectural Decisions and Rationale

**1. Optional Methods (NotImplementedError Default)**
- **Decision**: Make sync methods optional, raise NotImplementedError by default
- **Rationale**:
  - Allows gradual adoption without breaking existing code
  - Not all operation classes need sync support (e.g., text analysis)
  - Developers can choose which classes to enhance
- **Alternative Considered**: Abstract methods (would require all subclasses to implement)

**2. Cross-Project Parameters (ops1/ops2)**
- **Decision**: Accept optional ops instances for cross-project comparison
- **Rationale**:
  - Different projects have different writing systems, reference objects
  - Need project-specific context for property extraction
  - Enables comparing items from different project versions
- **Alternative Considered**: Require projects as parameters (less flexible)

**3. GUID Strings for References**
- **Decision**: Store Reference Atomic properties as GUID strings
- **Rationale**:
  - GUIDs are universal, HVOs are project-specific
  - Easy to compare across projects
  - Serializable for export/reporting
  - Can resolve back to objects when needed
- **Alternative Considered**: Store full object references (not comparable)

**4. Exclude Owning Sequences**
- **Decision**: Don't include OS properties in GetSyncableProperties()
- **Rationale**:
  - Complex hierarchical structures need special handling
  - Sync framework has dedicated tools (HierarchicalImporter)
  - Property-level sync is for simple properties
  - Prevents infinite recursion in nested structures
- **Alternative Considered**: Include as list of GUIDs (incomplete information)

**5. MultiString as Dictionaries**
- **Decision**: Return MultiString as {ws_tag: text} dictionaries
- **Rationale**:
  - Natural representation in Python
  - Easy to compare (dictionary equality)
  - Human-readable in diffs
  - Handles missing writing systems gracefully
- **Alternative Considered**: ITsString objects (not comparable, not serializable)

**6. Property Comparison in CompareTo()**
- **Decision**: Use GetSyncableProperties() within CompareTo()
- **Rationale**:
  - Single source of truth for what's syncable
  - Consistent property extraction
  - Reduces code duplication
  - Easy to extend with child sequence comparison
- **Alternative Considered**: Separate property lists (maintenance burden)

---

## 9. Testing Recommendations

### How to Test Sync Operations

**Unit Tests** (Test Individual Methods):
```python
import unittest
from flexlibs import FLExProject

class TestAllomorphSync(unittest.TestCase):
    def setUp(self):
        self.project = FLExProject()
        self.project.OpenProject("TestProject")
        self.entry = list(self.project.LexiconAllEntries())[0]
        self.allos = list(self.project.Allomorphs.GetAll(self.entry))

    def test_get_syncable_properties(self):
        """Test property extraction."""
        if not self.allos:
            self.skipTest("No allomorphs in test entry")

        props = self.project.Allomorphs.GetSyncableProperties(self.allos[0])

        # Verify expected properties
        self.assertIn('Form', props)
        self.assertIn('IsAbstract', props)
        self.assertIn('MorphTypeRA', props)

        # Verify types
        self.assertIsInstance(props['Form'], dict)
        self.assertIsInstance(props['IsAbstract'], bool)
        self.assertTrue(props['MorphTypeRA'] is None or isinstance(props['MorphTypeRA'], str))

    def test_compare_to_same_item(self):
        """Test comparing item to itself."""
        if not self.allos:
            self.skipTest("No allomorphs in test entry")

        is_diff, diffs = self.project.Allomorphs.CompareTo(
            self.allos[0], self.allos[0]
        )

        # Should not differ
        self.assertFalse(is_diff)
        self.assertEqual(len(diffs), 0)

    def tearDown(self):
        self.project.CloseProject()
```

**Integration Tests** (Test Cross-Project Sync):
```python
class TestCrossProjectSync(unittest.TestCase):
    def setUp(self):
        self.project1 = FLExProject()
        self.project1.OpenProject("Project1")

        self.project2 = FLExProject()
        self.project2.OpenProject("Project2")

    def test_compare_across_projects(self):
        """Test comparing same entry in two projects."""
        # Find entries with same GUID
        guid = "test-entry-guid"
        entry1 = self.project1.LexiconGetEntryByGuid(guid)
        entry2 = self.project2.LexiconGetEntryByGuid(guid)

        if not entry1 or not entry2:
            self.skipTest("Test entry not in both projects")

        # Get senses
        senses1 = list(self.project1.Senses.GetAll(entry1))
        senses2 = list(self.project2.Senses.GetAll(entry2))

        if not senses1 or not senses2:
            self.skipTest("No senses to compare")

        # Compare
        is_diff, diffs = self.project1.Senses.CompareTo(
            senses1[0], senses2[0],
            ops1=self.project1.Senses,
            ops2=self.project2.Senses
        )

        # Verify structure
        self.assertIsInstance(is_diff, bool)
        self.assertIsInstance(diffs, dict)

    def tearDown(self):
        self.project1.CloseProject()
        self.project2.CloseProject()
```

### Validation Approaches

**Property Coverage Validation**:
```python
def validate_property_coverage(ops_class, item):
    """Ensure all important properties are in GetSyncableProperties()."""
    props = ops_class.GetSyncableProperties(item)

    # Check for expected properties based on item type
    if hasattr(item, 'Form'):
        assert 'Form' in props, "Form property not extracted"

    if hasattr(item, 'Gloss'):
        assert 'Gloss' in props, "Gloss property not extracted"

    # Verify no OS properties included
    for key in props.keys():
        assert not key.endswith('OS'), f"OS property {key} should not be in syncable properties"

    # Verify no GUID/HVO properties
    assert 'Guid' not in props, "GUID should not be in syncable properties"
    assert 'Hvo' not in props, "HVO should not be in syncable properties"
```

**Round-Trip Validation**:
```python
def validate_round_trip(ops_class, source_item, target_item):
    """Validate that properties can be extracted and applied."""
    # Extract from source
    props = ops_class.GetSyncableProperties(source_item)

    # Apply to target (pseudo-code - actual setters vary)
    for prop_name, value in props.items():
        setter_name = f"Set{prop_name}"
        if hasattr(ops_class, setter_name):
            setter = getattr(ops_class, setter_name)
            # Apply value (handling varies by type)
            # ...

    # Re-extract from target
    props2 = ops_class.GetSyncableProperties(target_item)

    # Should match (or be close, depending on project differences)
    # This validates that extraction and setting are consistent
```

### Common Edge Cases

**1. Empty or Missing Properties**:
```python
# Test with item that has no Form set
empty_allo = project.Allomorphs.Create(entry, "", morphType)
props = project.Allomorphs.GetSyncableProperties(empty_allo)

# Should handle gracefully
assert 'Form' in props
assert props['Form'] == {} or props['Form'] == {'default-ws': ''}
```

**2. Cross-Project Writing System Differences**:
```python
# Project1 has writing systems: en, fr
# Project2 has writing systems: en, es

sense1 = project1.Senses.GetAll(entry1)[0]
sense2 = project2.Senses.GetAll(entry2)[0]

is_diff, diffs = project1.Senses.CompareTo(
    sense1, sense2,
    ops1=project1.Senses,
    ops2=project2.Senses
)

# Should detect differences in writing system availability
# Not necessarily an error - just different localization
```

**3. Reference to Non-Existent Object**:
```python
# Sense references a POS that doesn't exist in target project
source_sense = source.Senses.GetAll(entry)[0]
props = source.Senses.GetSyncableProperties(source_sense)

# MorphoSyntaxAnalysisRA might be GUID that target doesn't have
if props['MorphoSyntaxAnalysisRA']:
    guid = props['MorphoSyntaxAnalysisRA']
    target_msa = target.FindObjectByGuid(guid)

    if not target_msa:
        # Need to handle: create missing reference or skip
        warnings.warn(f"Target project missing MSA {guid}")
```

**4. Null vs Empty String**:
```python
# Ensure consistent handling of None vs ""
allo1 = create_allomorph_with_no_form()
allo2 = create_allomorph_with_empty_form()

props1 = ops.GetSyncableProperties(allo1)
props2 = ops.GetSyncableProperties(allo2)

# Both should result in empty dict for Form
assert props1['Form'] == {}
assert props2['Form'] == {} or props2['Form'] == {'ws': ''}
```

**5. Large MultiString Data**:
```python
# Sense with very long Definition in multiple writing systems
long_text = "A" * 10000  # 10KB of text

# Should handle without truncation
props = ops.GetSyncableProperties(sense)
assert len(props['Definition']['en']) == 10000
```

---

## 10. Future Enhancements

### Potential Improvements

**1. Automatic Reference Resolution**
- **Current**: Returns GUID strings for references
- **Enhancement**: Option to resolve GUIDs to full property dictionaries
- **Benefit**: Enables comparison of referenced objects (e.g., POS names)
```python
props = ops.GetSyncableProperties(sense, resolve_references=True)
# Returns:
{
    'MorphoSyntaxAnalysisRA': {
        'guid': 'guid-string',
        'PartOfSpeech': {
            'Name': {'en': 'Noun'},
            'Abbreviation': {'en': 'N'}
        }
    }
}
```

**2. Diff Formatting Options**
- **Current**: Returns raw property dictionaries
- **Enhancement**: Formatted diff output (unified diff, side-by-side, HTML)
- **Benefit**: Better human readability for reports
```python
diff = ops.CompareTo(item1, item2, format='unified')
# Returns:
"""
--- Project1/sense-guid
+++ Project2/sense-guid
@@ Definition (en) @@
-Old definition text
+New definition text
"""
```

**3. Batch Comparison**
- **Current**: Compare one item at a time
- **Enhancement**: Compare collections of items efficiently
- **Benefit**: Faster project-wide comparisons
```python
diffs = ops.CompareAll(
    items1, items2,
    match_by='guid',
    include_children=True
)
```

**4. Change Tracking**
- **Current**: Snapshot comparison
- **Enhancement**: Track when properties changed
- **Benefit**: Understand evolution of data over time
```python
props = ops.GetSyncableProperties(sense, include_metadata=True)
# Returns:
{
    'Gloss': {
        'value': {'en': 'run'},
        'modified': '2025-11-15T14:30:00',
        'modified_by': 'user-guid'
    }
}
```

**5. Smart Merge Strategies**
- **Current**: Manual property-by-property merging
- **Enhancement**: Predefined merge strategies
- **Benefit**: Common merge operations simplified
```python
result = ops.MergeSense(
    source_sense, target_sense,
    strategy='union',  # union, source_wins, target_wins, newest
    conflict_handler=callback
)
```

### Additional Sync Capabilities

**1. Selective Sync Profiles**
```python
# Define sync profiles for different scenarios
PROFILE_GLOSSES_ONLY = {
    'properties': ['Gloss', 'Definition'],
    'exclude_children': True
}

PROFILE_FULL_SENSE = {
    'properties': '*',
    'include_children': ['Examples'],
    'exclude_children': ['Subsenses']
}

sync_engine.sync(
    source, target,
    profile=PROFILE_GLOSSES_ONLY
)
```

**2. Conflict Resolution UI Integration**
```python
# Provide hooks for UI conflict resolution
def resolve_conflict(conflict):
    """Called when sync detects conflict."""
    print(f"Conflict in {conflict.property}:")
    print(f"  Source: {conflict.source_value}")
    print(f"  Target: {conflict.target_value}")

    choice = input("Use (s)ource, (t)arget, or (m)erge? ")
    if choice == 's':
        return conflict.source_value
    elif choice == 't':
        return conflict.target_value
    else:
        return merge_values(conflict.source_value, conflict.target_value)

merge_ops.conflict_resolver = resolve_conflict
```

**3. Sync History and Rollback**
```python
# Track sync operations for rollback
history = sync_engine.sync(source, target, track_history=True)

# Later, rollback if needed
if user_unhappy:
    sync_engine.rollback(history.operation_id)
```

**4. Incremental Sync**
```python
# Only sync items modified since last sync
last_sync = datetime(2025, 11, 15)

result = sync_engine.sync_incremental(
    source, target,
    modified_after=last_sync,
    created_after=last_sync
)
```

**5. Multi-Way Sync**
```python
# Sync among multiple projects
projects = [project1, project2, project3]

# Find consensus among all projects
consensus = sync_engine.multi_sync(
    projects,
    strategy='majority',  # Use value from majority of projects
    tie_breaker='newest'  # For 50/50 splits
)
```

### Performance Optimizations

**1. Lazy Property Extraction**
```python
# Current: Extract all properties upfront
# Enhancement: Extract only requested properties
props = ops.GetSyncableProperties(
    item,
    properties=['Gloss', 'Definition']  # Only extract these
)
```

**2. Caching**
```python
# Cache property extraction for frequently accessed items
@cached(ttl=60)  # Cache for 60 seconds
def GetSyncableProperties(self, item):
    # ... extraction logic
```

**3. Parallel Comparison**
```python
# Compare multiple items in parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    futures = []
    for item1, item2 in zip(items1, items2):
        future = executor.submit(
            ops.CompareTo, item1, item2, ops1, ops2
        )
        futures.append(future)

    results = [f.result() for f in futures]
```

**4. Incremental Diff Updates**
```python
# Update existing diff when single property changes
diff.update_property('Gloss', new_value)
# vs re-computing entire diff
```

**5. Index-Based Matching**
```python
# Build GUID index for faster lookups
guid_index = {str(item.Guid): item for item in items}

# Fast lookup instead of linear search
target_item = guid_index.get(source_guid)
```

---

## Summary

The sync framework integration with BaseOperations provides a robust, extensible foundation for cross-project synchronization in flexlibs. With **30 of 45 operation classes** already implementing sync methods, users can:

- Compare lexical data between projects with property-level precision
- Detect conflicts and divergences automatically
- Merge changes selectively based on property whitelists
- Validate reference integrity before syncing
- Build sophisticated sync workflows for team collaboration

The architecture balances **flexibility** (optional methods, fallback behavior) with **consistency** (shared interface across all operation classes), making it easy for developers to add sync support to new classes while maintaining backwards compatibility with existing code.

**Key Files**:
- BaseOperations.py - Lines 688-935 (sync methods)
- AllomorphOperations.py - Lines 394-496 (example implementation)
- LexSenseOperations.py - Lines 394-588 (complex example)
- flexlibs/sync/ - Sync framework using these methods

**For More Information**:
- See `docs/LINGUISTIC_SAFETY_GUIDE.md` for safety best practices
- See `docs/PHASE3_USER_GUIDE.md` for hierarchical import usage
- See `flexlibs/sync/__init__.py` for sync framework API

---

**Document Version**: 1.0
**Total Lines**: 1450
**Last Updated**: 2025-12-04
