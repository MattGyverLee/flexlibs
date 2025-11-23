# FlexLibs Development Architecture

## Overview

This document describes the modular architecture of the FlexLibs development module, which provides ~290 Pythonic wrapper methods for complete CRUD access to the FLEx data model.

**Date**: 2025-11-22
**Version**: 2.4.0-dev
**Status**: Development (Post-Synthesis Refactoring)

---

## Module Structure

```
flexlibs_dev/
├── core/                          # Shared utilities (NEW)
│   ├── __init__.py               # Core module exports
│   ├── types.py                  # Type definitions and aliases
│   ├── resolvers.py              # HVO-to-object resolver functions
│   ├── validators.py             # Input validation utilities
│   ├── exceptions.py             # Custom exception classes
│   └── constants.py              # Shared constants and enums
│
├── text_ops/                      # Text operations (Cluster 1.1-1.3)
│   ├── __init__.py
│   ├── text_core.py              # Core CRUD operations (1.1)
│   ├── text_advanced.py          # Advanced operations (1.2)
│   └── paragraph_crud.py         # Paragraph CRUD (1.3)
│
├── paragraph_segment_ops/         # Paragraph/Segment operations (Cluster 1.4-1.5)
│   ├── __init__.py
│   ├── paragraph_advanced.py     # Advanced paragraph ops (1.4)
│   └── segment_ops.py            # Segment operations (1.5)
│
├── wordform_ops/                  # Wordform operations (Cluster 1.6-1.7)
│   ├── __init__.py
│   ├── wordform_crud.py          # Wordform CRUD (1.6)
│   └── wordform_advanced.py      # Advanced wordform ops (1.7)
│
└── tests/                         # Test suite
    ├── __init__.py
    ├── test_text_core.py
    ├── test_text_advanced.py
    ├── test_paragraph_crud.py
    └── test_integration.py        # Integration tests (NEW)
```

---

## Core Module (`core/`)

The core module provides shared utilities that eliminate code duplication across all feature modules.

### Components

#### 1. `types.py` - Type Definitions
- **Purpose**: Centralized type aliases and protocols
- **Exports**:
  - FLEx object types: `IText`, `IStTxtPara`, `ISegment`, `IWfiWordform`, etc.
  - Generic types: `ObjectOrHVO`, `WritingSystemHandle`, `HVO`
  - Protocols: `FlexObject`, `FlexProject`
  - Optional types: `OptionalText`, `OptionalParagraph`, etc.

#### 2. `resolvers.py` - Object Resolution
- **Purpose**: Convert HVO references to FLEx objects
- **Pattern**: All resolvers follow the same signature:
  ```python
  def resolve_X(obj_or_hvo: Union[IObject, int], project: FlexProject) -> Optional[IObject]
  ```
- **Exports**:
  - `resolve_object()` - Generic resolver
  - `resolve_text()` - Text-specific resolver
  - `resolve_paragraph()` - Paragraph-specific resolver
  - `resolve_segment()` - Segment-specific resolver
  - `resolve_wordform()` - Wordform-specific resolver
  - `resolve_analysis()` - Analysis-specific resolver

#### 3. `validators.py` - Input Validation
- **Purpose**: Consistent parameter validation
- **Exports**:
  - `validate_non_empty_string()` - String validation
  - `validate_object_exists()` - Null checks
  - `validate_index_in_range()` - Index bounds checking
  - `validate_writing_system()` - WS handle validation
  - `validate_enum_value()` - Enum validation

#### 4. `exceptions.py` - Custom Exceptions
- **Purpose**: Unified error handling
- **Hierarchy**:
  ```
  FlexLibsError (base)
  ├── ObjectNotFoundError
  ├── InvalidParameterError
  ├── DuplicateObjectError
  ├── OperationFailedError
  ├── ObjectInUseError
  ├── WritingSystemError
  └── NotImplementedYetError
  ```
- **Design**: All custom exceptions inherit from both `FlexLibsError` and a standard exception (e.g., `ValueError`, `RuntimeError`) for backwards compatibility

#### 5. `constants.py` - Shared Constants
- **Purpose**: Centralized enumerations and constants
- **Exports**:
  - `SpellingStatusStates` - Wordform spelling status enum
  - `API_INTEGRATION_STATUS` - Integration status flag
  - `CORE_VERSION` - Core module version

---

## Dependency Graph

```
┌─────────────────────────────────────────┐
│           Feature Modules               │
│  (text_ops, paragraph_segment_ops,      │
│   wordform_ops)                         │
└────────────────┬────────────────────────┘
                 │
                 │ imports
                 ▼
┌─────────────────────────────────────────┐
│            core/                        │
│  (types, resolvers, validators,         │
│   exceptions, constants)                │
└─────────────────────────────────────────┘
```

**Key Principle**: Feature modules depend on `core`, but `core` has no dependencies on feature modules. This creates a clean, unidirectional dependency flow.

---

## Design Patterns

### 1. Resolver Pattern
**Problem**: Methods accept either FLEx objects or HVOs (integer IDs)
**Solution**: Centralized resolver functions

**Before (Duplicated)**:
```python
# In text_core.py
def _resolve_text(self, text_or_hvo):
    if isinstance(text_or_hvo, int):
        return self.project.GetObject(text_or_hvo)
    return text_or_hvo

# Same code duplicated in paragraph_crud.py, text_advanced.py...
```

**After (Shared)**:
```python
# In core/resolvers.py
def resolve_text(text_or_hvo, project):
    if isinstance(text_or_hvo, int):
        return project.GetObject(text_or_hvo)
    return text_or_hvo

# Used everywhere
text_obj = resolve_text(text_or_hvo, self.project)
```

### 2. Validation Pattern
**Problem**: Repeated validation logic
**Solution**: Reusable validation functions

**Before**:
```python
# Scattered across modules
if not form or not form.strip():
    raise ValueError("Wordform text cannot be empty")

if obj is None:
    raise ValueError(f"Object not found: {identifier}")
```

**After**:
```python
# In core/validators.py
validate_non_empty_string(form, "wordform text")
validate_object_exists(obj, identifier, "Object")
```

### 3. Exception Pattern
**Problem**: Inconsistent error types
**Solution**: Custom exception hierarchy

**Benefits**:
- Consistent error messages
- Easy to catch specific error types
- Backwards compatible with standard exceptions

---

## Refactoring Impact

### Code Duplication Eliminated

| Component | Before | After | Reduction |
|-----------|--------|-------|-----------|
| Resolver functions | 6 copies × ~15 lines | 1 implementation | ~90 lines |
| Type definitions | 3 modules × ~10 types | 1 module | ~30 lines |
| Validation logic | ~25 instances | 5 functions | ~100 lines |
| Exception definitions | Inline ValueError/RuntimeError | 8 custom classes | N/A |

**Total estimated reduction**: ~220 lines of duplicated code

### Module Coupling

**Before**: Each module was self-contained but duplicated utilities
**After**: Modules share `core` utilities (DRY principle)

**Trade-off**: Slightly increased coupling, but with clear benefits:
- Single source of truth for common patterns
- Easier to maintain and extend
- Consistent behavior across all modules

---

## Cross-Module Workflows

### Example: Text → Paragraph → Segment → Wordform

```python
from flexlibs_dev.text_ops import TextCoreOperations
from flexlibs_dev.paragraph_segment_ops import segment_ops
from flexlibs_dev.wordform_ops import wordform_crud

# Get a text
text_ops = TextCoreOperations(project)
my_text = text_ops.text_create("Story 1")

# Get paragraphs
paragraphs = text_ops.text_get_paragraphs(my_text)

# Get segments from first paragraph
segments = segment_ops.segment_get_all(paragraphs[0])

# Get wordform from segment analysis
analyses = segment_ops.segment_get_analyses(segments[0])
wordform = wordform_crud.wordform_find("running", "en")
```

**Key**: All modules use the same core types and patterns, making cross-module operations seamless.

---

## Future Extensions

### Planned Additions
1. **More clusters**: Lexicon, Grammar, etc. (Phase 2)
2. **Async operations**: Support for background processing
3. **Caching layer**: Performance optimization for large projects
4. **Query builders**: Fluent API for complex searches

### Extension Pattern
New feature modules should:
1. Import from `core` for common utilities
2. Follow the same patterns (resolvers, validators, exceptions)
3. Add tests to `tests/test_<module>.py`
4. Export public API through `__init__.py`

---

## Integration Notes

### Current Status
- **Phase**: Development (Post-Synthesis)
- **FLEx API**: Not yet integrated (uses `NotImplementedYetError`)
- **Testing**: Unit tests exist, integration pending

### Next Steps
1. Integrate with FLEx API
2. Replace `NotImplementedYetError` with actual implementations
3. Add integration tests with real FLEx projects
4. Performance profiling and optimization

---

## References

- **PROJECT_BOARD.md**: Complete initiative overview
- **REFACTORING_LOG.md**: Detailed refactoring changes
- **QC_CHECKLIST.md**: Quality assurance guidelines
- **TESTING_GUIDELINES.md**: Testing standards
