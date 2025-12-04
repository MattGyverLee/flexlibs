# Phase 3: Dependency Management - Design Document

**Version**: 1.3.0
**Date**: 2025-11-27
**Status**: Design Phase

---

## Overview

Phase 3 adds **intelligent dependency management** to handle complex linguistic data relationships. This addresses the final gaps identified in domain expert review.

### Goals

1. **Hierarchical Cascade**: Import objects with all owned children
2. **Cross-Reference Preservation**: Maintain relationships between objects
3. **Dependency Resolution**: Automatically import prerequisite objects
4. **Order of Operations**: Import in correct sequence to satisfy dependencies

---

## Use Cases

### 1. Import Entry with All Content
**Scenario**: Linguist wants to import a lexical entry with all its senses, examples, allomorphs, and pronunciations.

**Current Problem**: Must import each piece separately in correct order

**Phase 3 Solution**: Single operation imports entire hierarchy

```python
importer.import_with_dependencies(
    object_type="LexEntry",
    guids=["entry-guid-123"],
    include_owned=True  # Bring all senses, examples, allomorphs
)
```

### 2. Preserve Variant Relationships
**Scenario**: Import variant entry that references main entry

**Current Problem**: Variant links break if main entry doesn't exist

**Phase 3 Solution**: Automatically import referenced main entry first

```python
importer.import_with_dependencies(
    object_type="LexEntry",
    guids=["variant-guid"],
    resolve_references=True  # Auto-import main entry
)
```

### 3. Import Semantic Domain with All Entries
**Scenario**: Import all entries tagged with specific semantic domain

**Current Problem**: Must manually filter and import entries

**Phase 3 Solution**: Import domain and all entries that reference it

```python
importer.import_related(
    object_type="CmSemanticDomain",
    guid="domain-guid",
    include_referring_objects=["LexSense"]  # Import all senses using this domain
)
```

---

## Architecture

### New Components

#### 1. `DependencyGraph` Class
**Purpose**: Model object dependencies and determine import order

```python
class DependencyGraph:
    """
    Directed acyclic graph of object dependencies.
    """

    def add_object(self, obj: Any, object_type: str):
        """Add object to graph."""

    def add_dependency(self, from_guid: str, to_guid: str, dep_type: str):
        """Add dependency relationship."""

    def get_import_order(self) -> List[Tuple[str, str]]:
        """Return topologically sorted import order."""

    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies."""
```

#### 2. `DependencyResolver` Class
**Purpose**: Discover and resolve object dependencies

```python
class DependencyResolver:
    """
    Analyzes objects and discovers all dependencies.
    """

    def resolve_dependencies(
        self,
        obj: Any,
        object_type: str,
        include_owned: bool = True,
        resolve_references: bool = True,
        max_depth: int = 10
    ) -> DependencyGraph:
        """Build dependency graph for object."""

    def get_owned_objects(self, obj: Any, object_type: str) -> List[Tuple[Any, str]]:
        """Get all objects owned by this object."""

    def get_referenced_objects(self, obj: Any, object_type: str) -> List[Tuple[Any, str]]:
        """Get all objects referenced by this object."""
```

#### 3. `HierarchicalImporter` Class
**Purpose**: Import objects with their full dependency trees

```python
class HierarchicalImporter:
    """
    Import objects with dependency resolution.
    """

    def import_with_dependencies(
        self,
        object_type: str,
        guids: List[str],
        include_owned: bool = True,
        resolve_references: bool = True,
        validate_references: bool = True,
        dry_run: bool = False
    ) -> SyncResult:
        """Import objects with full dependency trees."""

    def import_related(
        self,
        object_type: str,
        guid: str,
        include_referring_objects: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> SyncResult:
        """Import object and all objects that refer to it."""
```

---

## Dependency Types

### 1. Ownership Dependencies (Parent → Child)
**Must import parent before child**

| Parent | Child | Example |
|--------|-------|---------|
| LexEntry | LexSense | Entry owns senses |
| LexSense | LexExampleSentence | Sense owns examples |
| LexEntry | MoForm (Allomorph) | Entry owns allomorphs |
| LexEntry | LexPronunciation | Entry owns pronunciations |
| LexSense | LexSense (subsense) | Sense owns subsenses |

**Implementation**: Check `Owner` property, import from root down

### 2. Reference Dependencies
**Referenced object should exist first**

| Object | Reference | Property |
|--------|-----------|----------|
| LexSense | PartOfSpeech | MorphoSyntaxAnalysisRA |
| LexSense | CmSemanticDomain | SemanticDomainsRC |
| MoForm | MoMorphType | MorphTypeRA |
| LexEntry | LexEntry (variant) | VariantEntryTypesRS |
| LexSense | LexSense (relation) | LexSenseReferences |

**Implementation**: Check reference properties, optionally import referenced objects

### 3. Cross-References (Bidirectional)
**Special handling needed**

| Type | Objects | Properties |
|------|---------|------------|
| Variants | Main ↔ Variant | VariantEntryTypesRS, VariantFormEntryBackRefs |
| Reversals | Entry ↔ Reversal | ReversalEntriesRC |
| Relations | Sense ↔ Sense | LexSenseReferences (bidirectional) |
| Etymology | Entry ↔ Entry | Etymology source/target |

**Implementation**: Import both sides of relationship, update references after both exist

---

## FLEx Object Hierarchies

### LexEntry Hierarchy
```
LexEntry
├── LexemeFormOA (MoForm - allomorph)
│   ├── Form (MultiString)
│   ├── MorphTypeRA → MoMorphType
│   └── PhonEnvironmentsRC → PhEnvironment
├── AlternateFormsOS[] (MoForm)
├── PronunciationsOS[] (LexPronunciation)
│   └── Form (MultiString)
├── SensesOS[] (LexSense)
│   ├── Gloss (MultiString)
│   ├── Definition (MultiString)
│   ├── MorphoSyntaxAnalysisRA → PartOfSpeech
│   ├── SemanticDomainsRC[] → CmSemanticDomain
│   ├── ExamplesOS[] (LexExampleSentence)
│   │   ├── Example (MultiString)
│   │   └── Translations (MultiString)
│   └── SensesOS[] (subsenses - recursive)
├── EtymologyOS[] (LexEtymology)
│   └── Source → LexEntry
├── VariantEntryTypesRS[] → LexEntryRef
│   └── ComponentLexemesRS[] → LexEntry
└── ReversalEntriesRC[] → ReversalIndexEntry
```

### Owned Objects (Must Import with Parent)
- **LexEntry**:
  - LexemeFormOA (single owned allomorph)
  - AlternateFormsOS (collection of allomorphs)
  - PronunciationsOS
  - SensesOS
  - EtymologyOS
  - VariantEntryTypesRS

- **LexSense**:
  - ExamplesOS
  - SensesOS (subsenses)

- **MoForm (Allomorph)**:
  - PhonEnvironmentsRC (phonological environments)

### Referenced Objects (Should Exist First)
- PartOfSpeech (from LexSense.MorphoSyntaxAnalysisRA)
- CmSemanticDomain (from LexSense.SemanticDomainsRC)
- MoMorphType (from MoForm.MorphTypeRA)
- PhEnvironment (from MoForm.PhonEnvironmentsRC)

---

## Import Algorithm

### Phase 1: Discovery
```
1. Start with root object(s)
2. If include_owned:
   - Recursively discover all owned objects
3. If resolve_references:
   - Discover all referenced objects
   - Check if they exist in target
   - If not, add to import queue
4. Build dependency graph
5. Detect cycles (error if found)
6. Topologically sort for import order
```

### Phase 2: Validation
```
1. For each object in import order:
   - Validate references exist (or will be imported)
   - Check for conflicts
   - Validate data quality
2. If any critical issues:
   - Report all issues
   - Stop if not dry_run
```

### Phase 3: Import
```
1. For each object in dependency order:
   - Check if already exists in target
   - If exists: skip or update (based on policy)
   - If not exists: create
   - Track created GUIDs for reference updates
2. Update cross-references:
   - For bidirectional relationships
   - Update back-references
```

---

## Edge Cases

### 1. Circular References
**Problem**: Entry A references Entry B which references Entry A

**Solution**:
- Detect cycles in dependency graph
- Allow breaking cycle at weakest link (e.g., cross-references)
- Import objects first, then update cross-references

### 2. Partial Hierarchies
**Problem**: Sense exists but parent entry doesn't

**Solution**:
- Always import from root (entry level)
- Validate parent exists before importing child
- Option to auto-create stub parents

### 3. Shared References
**Problem**: Multiple objects reference same POS/domain

**Solution**:
- Import referenced object once
- All referring objects use same reference
- Track imported references in cache

### 4. Large Dependency Trees
**Problem**: Entry has 100+ senses with examples

**Solution**:
- Set max_depth limit
- Provide progress callbacks
- Support batch operations
- Optional filtering of owned objects

---

## Configuration Options

### DependencyResolution
```python
@dataclass
class DependencyConfig:
    """Configuration for dependency resolution."""

    # What to include
    include_owned: bool = True           # Import owned objects
    resolve_references: bool = True      # Import referenced objects
    include_referring: bool = False      # Import objects that refer to this

    # Depth limits
    max_owned_depth: int = 10           # How deep to traverse ownership
    max_reference_depth: int = 2        # How deep to follow references

    # Filtering
    owned_types: Optional[List[str]] = None      # Which owned types to include
    reference_types: Optional[List[str]] = None  # Which reference types to follow

    # Behavior
    skip_existing: bool = True          # Skip objects that exist in target
    update_existing: bool = False       # Update existing objects
    create_stub_parents: bool = False   # Create minimal parent objects if missing

    # Safety
    validate_all: bool = True           # Validate all objects before import
    allow_cycles: bool = False          # Allow circular dependencies
```

---

## API Design

### Basic Hierarchical Import
```python
from flexlibs.sync import HierarchicalImporter

importer = HierarchicalImporter(source_project, target_project)

# Import entry with all senses and examples
result = importer.import_with_dependencies(
    object_type="LexEntry",
    guids=["entry-guid-123"],
    include_owned=True,
    resolve_references=True,
    dry_run=True  # Preview first
)

# See what will be imported
print(f"Will import {result.num_created} objects:")
for change in result.changes:
    print(f"  - {change.object_type}: {change.object_guid}")
```

### Advanced Configuration
```python
from flexlibs.sync import HierarchicalImporter, DependencyConfig

config = DependencyConfig(
    include_owned=True,
    owned_types=["LexSense", "LexExampleSentence"],  # Only senses and examples
    resolve_references=True,
    max_owned_depth=5,
    skip_existing=True
)

result = importer.import_with_dependencies(
    object_type="LexEntry",
    guids=["entry-guid-123"],
    config=config,
    dry_run=False
)
```

### Import Related Objects
```python
# Import all entries that use a specific semantic domain
result = importer.import_related(
    object_type="CmSemanticDomain",
    guid="domain-guid",
    include_referring_objects=["LexSense"],  # Import senses using this domain
    dry_run=False
)
```

---

## Error Handling

### Dependency Errors
```python
class DependencyError(Exception):
    """Raised when dependency resolution fails."""
    pass

class CircularDependencyError(DependencyError):
    """Raised when circular dependency detected."""
    def __init__(self, cycle: List[str]):
        self.cycle = cycle
        super().__init__(f"Circular dependency: {' → '.join(cycle)}")
```

### Missing Dependencies
```python
class MissingDependencyError(DependencyError):
    """Raised when required dependency is missing."""
    def __init__(self, obj_guid: str, dep_guid: str, dep_type: str):
        self.obj_guid = obj_guid
        self.dep_guid = dep_guid
        self.dep_type = dep_type
```

---

## Testing Strategy

### Unit Tests
1. **DependencyGraph**: Graph construction, cycle detection, topological sort
2. **DependencyResolver**: Discovery of owned/referenced objects
3. **HierarchicalImporter**: Import operations with dependencies

### Integration Tests
1. **Simple Hierarchy**: Entry with senses
2. **Complex Hierarchy**: Entry with senses, examples, allomorphs
3. **Cross-References**: Variant entries
4. **Circular Dependencies**: Mutual sense relations
5. **Large Trees**: Entry with 50+ senses

### Edge Case Tests
1. **Missing References**: Referenced POS doesn't exist
2. **Partial Hierarchy**: Orphaned senses
3. **Duplicate GUIDs**: Object exists in both projects
4. **Empty Hierarchies**: Entry with no senses

---

## Performance Considerations

### Optimization Strategies

1. **Batch Operations**
   - Group object creation by type
   - Reduce database transactions

2. **Reference Caching**
   - Cache existence checks
   - Avoid repeated lookups

3. **Lazy Loading**
   - Load owned objects on demand
   - Don't traverse entire tree upfront

4. **Progress Reporting**
   - Report at object type level
   - Don't report every single object

---

## Implementation Phases

### Phase 3.1: Dependency Graph (Current)
- DependencyGraph class
- Cycle detection
- Topological sorting

### Phase 3.2: Dependency Resolution
- DependencyResolver class
- Owned object discovery
- Referenced object discovery

### Phase 3.3: Hierarchical Import
- HierarchicalImporter class
- Import with dependencies
- Cross-reference handling

### Phase 3.4: Testing & Documentation
- Comprehensive test suite
- User documentation
- Example workflows

---

## Success Criteria

✅ **Functional**:
- Import entry with all senses/examples in single operation
- Automatically resolve reference dependencies
- Detect and handle circular dependencies
- Preserve cross-references (variants, reversals)

✅ **Quality**:
- 90%+ test coverage
- All edge cases handled
- Clear error messages
- Performance acceptable (<1 sec per entry)

✅ **Usability**:
- Simple API for common cases
- Advanced configuration for complex cases
- Comprehensive documentation
- Clear examples

---

**Next Steps**: Begin implementation with DependencyGraph class.
