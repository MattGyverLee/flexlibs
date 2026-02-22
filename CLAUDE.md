# FlexLibs2 Claude Code Guidelines

This document outlines conventions and best practices for Claude Code when working on this project.

## Project Overview

FlexLibs2 is a Python library for accessing FieldWorks Language Explorer (FLEx) projects via the Language and Culture Model (LCM) API. It provides comprehensive CRUD operations for FLEx data types across Grammar, Lexicon, Texts & Words, Notebook, Lists, and System modules.

## Code Style & Standards

### File Headers
All Python files should include a header with:
- Module name
- Brief description
- Class/Component information
- Platform info (Python, FieldWorks version)
- Copyright notice

Example:
```python
#
#   LexEntryOperations.py
#
#   Class: LexEntryOperations
#          Lexical entry operations for FieldWorks Language Explorer
#          projects via SIL Language and Culture Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#
```

### Module Documentation
- Use docstrings with description, usage examples, and Args/Returns sections
- Include usage examples showing how to access classes via `FLExProject`
- Document important module-level constants

### Operations Classes
- All operations inherit from `BaseOperations`
- Follow the naming pattern: `[Domain]Operations.py` (e.g., `LexEntryOperations.py`)
- Organize by FLEx domain: Grammar, Lexicon, Texts & Words, Notebook, Lists, System
- Implement CRUD methods: Create, Read, Update, Delete patterns
- Use BaseOperations validation methods for consistency

### String Handling
- Use `normalize_text()` from `Shared.string_utils` for FLEx null marker ('***') handling
- Normalize empty multilingual string fields to empty strings
- Use `best_analysis_text()` and `best_vernacular_text()` utilities for language analysis

### Logging
- Use logging module with pattern: `logger = logging.getLogger(__name__)`
- Keep logging statements focused on debugging and issue diagnosis

## Project Structure

```
flexlibs2/
├── flexlibs2/
│   ├── code/
│   │   ├── BaseOperations.py          # Parent class for all operations
│   │   ├── FLExProject.py             # Main project interface
│   │   ├── Grammar/                   # POS, Phonemes, Rules, etc.
│   │   ├── Lexicon/                   # Entries, Senses, Examples, etc.
│   │   ├── TextsWords/                # Texts, Wordforms, Analyses, etc.
│   │   ├── Notebook/                  # Notes, People, Locations, etc.
│   │   ├── Lists/                     # Publications, Agents, etc.
│   │   ├── System/                    # Writing Systems, Custom Fields, etc.
│   │   └── Shared/                    # Utilities (string_utils, filters, etc.)
│   └── sync/                          # Sync engine and related utilities
├── tests/                             # Test suites
│   ├── operations/                    # Operation-specific tests
│   └── test_*.py                      # Integration and feature tests
└── docs/                              # API documentation and guides
```

## Testing

### Test Organization
- Use `tests/operations/` for operation-specific unit tests
- Use `tests/test_*.py` for integration tests
- Test files follow pattern: `test_[feature]_[aspect].py` or `test_[module].py`
- Tests in `flexlibs2/sync/tests/` for sync engine functionality

### Test Naming
- Test classes: `Test[FeatureName]`
- Test methods: `test_[what_is_being_tested]_[expected_result]`

### Testing Framework
- Use pytest for test execution
- Maintain `.coverage` for coverage tracking
- Check `.pytest_cache/` behavior before modifying test infrastructure

## Git Conventions

### Branches
- `main` - Production-ready code
- `master` - Current development (default branch)
- Feature branches should reference issues when applicable

### Commits
- Keep commits focused and logical
- Reference relevant changes and fixes
- Include `Co-Authored-By:` footer when appropriate

### Before Committing
- Verify code follows project style
- Check that operations use BaseOperations validation
- Ensure proper error handling with FLEx-specific exceptions

## FLEx-Specific Conventions

### Exception Handling
- Import custom exceptions from `FLExProject`:
  - `FP_ReadOnlyError` - Read-only project operations
  - `FP_NullParameterError` - Null/None parameters
  - `FP_ParameterError` - Invalid parameters

### LCM Imports
- Import FLEx types from `SIL.LCModel`
- Use factory and repository interfaces for object creation
- Handle ITsString properly for multilingual text

### Write Operations
- Only perform write operations if `project.WriteEnabled` is True
- Check write permissions before attempting Create/Update/Delete operations
- Use appropriate factories for object creation

## Documentation

### API Documentation
- HTML API documentation is generated and accessible via `flexlibs2.APIHelpFile`
- Keep docstrings accurate with parameter descriptions
- Update API_ISSUES_CATEGORIZED.md when API changes are made
- Document breaking changes in migration guides

### Code Comments
- Document non-obvious FLEx behavior
- Explain workarounds for LCM quirks (e.g., null marker handling)
- Include examples showing correct usage patterns

## Windows Environment

### No Emojis in Terminal Output
- Use `[OK]`, `[DONE]`, `[PASS]` instead of ✓ or ✅
- Use `[ERROR]`, `[FAIL]` instead of ✗ or ❌
- Use `[INFO]`, `[NOTE]` instead of ℹ️
- Use `[WARN]` instead of ⚠️
- Use asterisks or dashes for bullet points, not Unicode bullets

## When to Consult Claude

Before implementing changes that affect:
- BaseOperations validation methods (affects all operations)
- FLExProject core functionality (central interface)
- Module structure or organization
- API surface changes

## Key Files to Know

- `flexlibs2/code/BaseOperations.py` - Parent class with shared validation
- `flexlibs2/code/FLExProject.py` - Main project interface
- `flexlibs2/code/Shared/string_utils.py` - Text normalization utilities
- `docs/API_ISSUES_CATEGORIZED.md` - Known API issues and workarounds
- `README.rst` - User-facing documentation
