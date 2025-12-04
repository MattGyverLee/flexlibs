# Phase 3: Hierarchical Import - User Guide

**Version**: 1.3.0
**Date**: 2025-11-27

---

## Overview

Phase 3 adds **intelligent dependency management** to the FLEx Sync Framework. Instead of manually importing objects one by one, you can now import complete hierarchies with automatic dependency resolution.

### What's New in Phase 3

✅ **Hierarchical Cascade**: Import entries with all senses, examples, allomorphs
✅ **Automatic Dependency Resolution**: Referenced POS/domains imported automatically
✅ **Smart Import Order**: Objects imported in correct sequence
✅ **Cycle Detection**: Detects and handles circular dependencies
✅ **Batch Operations**: Import multiple entries in one operation
✅ **Bidirectional Relationships**: Import object and all objects that reference it

---

## Quick Start

### Basic Usage

```python
from flexlibs.sync import HierarchicalImporter
from flexlibs import FLExProject

# Open projects
source = FLExProject("consultant_work.fwdata", writeEnabled=False)
target = FLExProject("main_project.fwdata", writeEnabled=True)

# Create importer
importer = HierarchicalImporter(source, target)

# Import entry with all its content
result = importer.import_with_dependencies(
    object_type="LexEntry",
    guids=["entry-guid-12345"],
    dry_run=True  # Preview first!
)

print(result.summary())
```

---

## Core Concepts

### 1. Dependency Types

Phase 3 recognizes three types of dependencies:

#### Ownership Dependencies
Parent objects own children - **must import parent first**.

| Parent | Children |
|--------|----------|
| LexEntry | Senses, Allomorphs, Pronunciations, Etymologies |
| LexSense | Examples, Subsenses |
| MoForm | Phonological Environments |

#### Reference Dependencies
Objects reference other objects - **referenced object should exist first**.

| Object | References |
|--------|------------|
| LexSense | PartOfSpeech, SemanticDomains |
| MoForm | MorphType |
| LexEntry | Variant entries |

#### Cross-References (Bidirectional)
Objects reference each other - **special handling needed**.

- Variant relationships (main ↔ variant)
- Reversal entries
- Sense relations
- Etymology links

### 2. Dependency Graph

Phase 3 builds a **directed acyclic graph (DAG)** of all objects and their dependencies, then uses **topological sorting** to determine the correct import order.

```
Example hierarchy:
  LexEntry (entry-1)
  ├─→ PartOfSpeech (pos-1)      [reference - import first]
  ├─→ LexSense (sense-1)         [owned - import after entry]
  │   ├─→ PartOfSpeech (pos-1)  [reference - shared]
  │   └─→ LexExampleSentence     [owned - import after sense]
  └─→ MoForm (allomorph-1)       [owned - import after entry]
      └─→ MoMorphType (type-1)   [reference - import first]

Import order:
  1. pos-1 (PartOfSpeech)
  2. type-1 (MoMorphType)
  3. entry-1 (LexEntry)
  4. sense-1 (LexSense)
  5. example-1 (LexExampleSentence)
  6. allomorph-1 (MoForm)
```

### 3. Configuration

Control dependency resolution with `DependencyConfig`:

```python
from flexlibs.sync import DependencyConfig

config = DependencyConfig(
    # What to include
    include_owned=True,              # Import owned objects
    resolve_references=True,         # Import referenced objects

    # Depth limits
    max_owned_depth=10,              # How deep to traverse
    max_reference_depth=2,           # Reference chain limit

    # Filtering
    owned_types=["LexSense", "LexExampleSentence"],  # Filter types

    # Behavior
    skip_existing=True,              # Skip objects in target
    validate_all=True,               # Validate before import
    allow_cycles=False               # Error on circular deps
)
```

---

## Common Workflows

### Import Entry with All Content

**Use case**: Import a complete lexical entry with senses, examples, and allomorphs.

```python
from flexlibs.sync import HierarchicalImporter, DependencyConfig

importer = HierarchicalImporter(source, target)

config = DependencyConfig(
    include_owned=True,          # Get all owned objects
    resolve_references=True,     # Get POS, domains, etc.
    max_owned_depth=10          # Full hierarchy
)

# Always preview first
result = importer.import_with_dependencies(
    object_type="LexEntry",
    guids=["entry-guid"],
    config=config,
    dry_run=True
)

print(f"Will import {result.num_skipped} objects:")
for change in result.changes:
    print(f"  - {change.object_type}")

# If good, proceed
if result.success:
    result = importer.import_with_dependencies(
        object_type="LexEntry",
        guids=["entry-guid"],
        config=config,
        dry_run=False
    )
```

### Import Multiple Entries (Batch)

**Use case**: Import several entries at once, sharing common references.

```python
entry_guids = ["entry-1", "entry-2", "entry-3"]

result = importer.import_with_dependencies(
    object_type="LexEntry",
    guids=entry_guids,
    dry_run=False
)

# Shared POS/domains imported only once
print(f"Imported {result.num_created} objects total")
```

### Import with Filtered Owned Objects

**Use case**: Import entry but only senses (no pronunciations, etymologies).

```python
config = DependencyConfig(
    include_owned=True,
    owned_types=["LexSense", "LexExampleSentence"],  # Only these
    resolve_references=True
)

result = importer.import_with_dependencies(
    object_type="LexEntry",
    guids=["entry-guid"],
    config=config
)
```

### Import Semantic Domain with All Entries

**Use case**: Import a semantic domain and all entries/senses that use it.

```python
result = importer.import_related(
    object_type="CmSemanticDomain",
    guid="domain-guid",
    include_referring_objects=["LexSense"],  # Import senses using this
    dry_run=False
)

print(f"Imported domain + {result.num_created - 1} senses")
```

### Track Progress for Large Imports

**Use case**: Monitor progress when importing large hierarchies.

```python
def show_progress(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

result = importer.import_with_dependencies(
    object_type="LexEntry",
    guids=["large-entry-guid"],
    progress_callback=show_progress,
    dry_run=False
)
```

---

## Error Handling

### Validation Errors

If imported objects have missing references:

```python
from flexlibs.sync.validation import ValidationError

try:
    result = importer.import_with_dependencies(
        object_type="LexEntry",
        guids=["entry-guid"],
        validate_references=True,
        dry_run=False
    )
except ValidationError as e:
    print("❌ Validation failed:")
    print(e.result.detailed_report())

    # Resolution options:
    # 1. Fix issues in source project
    # 2. Import required references first
    # 3. Set validate_references=False (not recommended)
```

### Circular Dependencies

If objects have circular references:

```python
from flexlibs.sync import CircularDependencyError, DependencyConfig

try:
    result = importer.import_with_dependencies(
        object_type="LexEntry",
        guids=["entry-guid"],
        dry_run=False
    )
except CircularDependencyError as e:
    print(f"❌ Circular dependency: {e}")

    # Option 1: Allow framework to break cycles
    config = DependencyConfig(allow_cycles=True)
    result = importer.import_with_dependencies(
        object_type="LexEntry",
        guids=["entry-guid"],
        config=config,
        dry_run=False
    )
    print("✓ Imported by breaking weak links")
    print("⚠️ Some cross-references may need manual update")
```

---

## Advanced Features

### Custom Dependency Resolution

For complete control over what gets imported:

```python
from flexlibs.sync import DependencyResolver

resolver = DependencyResolver(source, target)

# Build dependency graph for specific object
entry = source.LexEntry.Object("entry-guid")

config = DependencyConfig(
    include_owned=True,
    owned_types=["LexSense"],  # Only senses
    resolve_references=False    # Don't follow references
)

graph = resolver.resolve_dependencies(entry, "LexEntry", config)

# Examine graph
print(graph.summary())
print(f"Import order:")
for guid, obj_type in graph.get_import_order():
    print(f"  {obj_type}: {guid[:8]}...")
```

### Working with Dependency Graph

Directly manipulate the dependency graph:

```python
from flexlibs.sync import DependencyGraph, DependencyType

graph = DependencyGraph()

# Add objects
graph.add_object("entry-1", "LexEntry")
graph.add_object("sense-1", "LexSense")
graph.add_object("pos-1", "PartOfSpeech")

# Add dependencies
graph.add_dependency("sense-1", "entry-1", DependencyType.OWNERSHIP)
graph.add_dependency("sense-1", "pos-1", DependencyType.REFERENCE)

# Analyze
print(f"Roots: {graph.get_roots()}")
print(f"Leaves: {graph.get_leaves()}")

# Get import order
order = graph.get_import_order()
# -> [("pos-1", "PartOfSpeech"), ("entry-1", "LexEntry"), ("sense-1", "LexSense")]

# Detect cycles
cycles = graph.detect_cycles()
if cycles:
    print(f"Found cycle: {cycles[0]}")
```

---

## Best Practices

### ✅ DO

1. **Always dry-run first**
   ```python
   result = importer.import_with_dependencies(..., dry_run=True)
   # Review result.summary() before proceeding
   ```

2. **Use progress callbacks for large imports**
   ```python
   def progress(msg): print(msg)
   result = importer.import_with_dependencies(..., progress_callback=progress)
   ```

3. **Enable validation**
   ```python
   result = importer.import_with_dependencies(..., validate_references=True)
   ```

4. **Limit depth for safety**
   ```python
   config = DependencyConfig(max_owned_depth=5, max_reference_depth=2)
   ```

5. **Filter owned types when appropriate**
   ```python
   config = DependencyConfig(owned_types=["LexSense", "LexExampleSentence"])
   ```

### ❌ DON'T

1. **Don't skip dry-run for production data**
   - Always preview first!

2. **Don't disable validation without good reason**
   - Validation prevents corrupt data

3. **Don't allow cycles without understanding implications**
   - Broken cross-references may need manual fixing

4. **Don't set unlimited depth**
   - Use reasonable limits to prevent runaway imports

5. **Don't import without backups**
   - Always backup before large import operations

---

## Performance Considerations

### Optimize Large Imports

1. **Batch related entries**
   ```python
   # Better: Import all at once (shares dependencies)
   result = importer.import_with_dependencies(
       object_type="LexEntry",
       guids=[...100 guids...],
       dry_run=False
   )

   # Worse: Import one at a time
   for guid in guids:
       result = importer.import_with_dependencies(...)
   ```

2. **Clear cache between operations**
   ```python
   importer.resolver.clear_cache()
   ```

3. **Use type filtering**
   ```python
   # Only import what you need
   config = DependencyConfig(owned_types=["LexSense"])
   ```

4. **Set appropriate depth limits**
   ```python
   # Don't traverse unnecessarily deep
   config = DependencyConfig(max_owned_depth=5)
   ```

---

## Comparison with Other Phases

| Feature | Phase 2 | Phase 2.5 | Phase 3 |
|---------|---------|-----------|---------|
| **Approach** | Bidirectional sync | One-way selective | Hierarchical cascade |
| **Use Case** | Technical sync | Date-filtered import | Complete hierarchies |
| **Safety** | Basic | High (validation) | High (validation + dependencies) |
| **Complexity** | Manual ordering | Single object | Automatic ordering |
| **Best For** | Experts | New objects | Complex objects |

### When to Use Each

**Phase 2 (SyncEngine)**:
- Expert users only
- Full database sync
- Understand FLEx internals

**Phase 2.5 (SelectiveImport)**:
- Import new objects by date
- Filter by custom criteria
- Independent objects
- Maximum safety

**Phase 3 (HierarchicalImporter)**:
- Import complete entries
- Complex dependencies
- Automatic reference resolution
- Batch operations

---

## Examples

See [hierarchical_import_demo.py](../examples/hierarchical_import_demo.py) for complete working examples:

- Import entry with all senses and examples
- Import with filtered owned objects
- Import semantic domain with referencing entries
- Batch import multiple entries
- Handle validation errors
- Handle circular dependencies
- Progress tracking

---

## API Reference

### HierarchicalImporter

```python
class HierarchicalImporter:
    def __init__(self, source_project, target_project)

    def import_with_dependencies(
        object_type: str,
        guids: List[str],
        config: Optional[DependencyConfig] = None,
        validate_references: bool = True,
        progress_callback: Optional[Callable] = None,
        dry_run: bool = False
    ) -> SyncResult

    def import_related(
        object_type: str,
        guid: str,
        include_referring_objects: Optional[List[str]] = None,
        validate_references: bool = True,
        progress_callback: Optional[Callable] = None,
        dry_run: bool = False
    ) -> SyncResult
```

### DependencyConfig

```python
@dataclass
class DependencyConfig:
    include_owned: bool = True
    resolve_references: bool = True
    include_referring: bool = False
    max_owned_depth: int = 10
    max_reference_depth: int = 2
    owned_types: Optional[List[str]] = None
    reference_types: Optional[List[str]] = None
    skip_existing: bool = True
    update_existing: bool = False
    create_stub_parents: bool = False
    validate_all: bool = True
    allow_cycles: bool = False
```

### DependencyGraph

```python
class DependencyGraph:
    def add_object(guid: str, object_type: str, obj: Any = None)
    def add_dependency(from_guid: str, to_guid: str, dep_type: DependencyType)
    def get_import_order() -> List[Tuple[str, str]]
    def detect_cycles() -> List[List[str]]
    def get_roots() -> List[str]
    def get_leaves() -> List[str]
    def summary() -> str
```

---

## Troubleshooting

### Issue: "Circular dependency detected"

**Cause**: Objects reference each other (variant entries, mutual sense relations)

**Solution**:
```python
config = DependencyConfig(allow_cycles=True)
result = importer.import_with_dependencies(..., config=config)
```

### Issue: "Validation failed: Referenced POS does not exist"

**Cause**: Sense references POS that doesn't exist in target

**Solutions**:
1. Import the POS first
2. Let hierarchical importer resolve it automatically (`resolve_references=True`)
3. Disable validation (not recommended)

### Issue: Import is very slow

**Causes**: Deep hierarchy, many objects, repeated lookups

**Solutions**:
1. Set lower `max_owned_depth`
2. Filter `owned_types`
3. Clear cache between operations
4. Batch multiple entries together

### Issue: "Too many objects imported"

**Cause**: Default settings include everything

**Solution**: Use filtering
```python
config = DependencyConfig(
    owned_types=["LexSense"],  # Only senses
    resolve_references=False    # Don't follow references
)
```

---

## What's Not Included (Future Work)

Phase 3 provides core dependency management, but some advanced features are deferred:

- **Automatic cross-reference updating**: Broken references need manual fixing
- **Paradigm completeness checking**: Doesn't verify all variant forms exist
- **Conflict resolution**: Assumes no conflicts (objects don't exist in target)
- **Incremental updates**: Always creates new objects, doesn't update existing

These may be added in future phases based on user needs.

---

**Document Version**: 1.0
**Framework Version**: 1.3.0 (Phase 3)
**Last Updated**: 2025-11-27
