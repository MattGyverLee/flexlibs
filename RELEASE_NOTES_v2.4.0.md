# FlexLibs2 v2.4.0 Release Notes

**Release Date:** March 22, 2026
**Version:** 2.4.0
**Status:** Production Ready
**Branch:** feature/undo-stack-phase2 (merging to main)

---

## Release Summary

FlexLibs2 v2.4.0 introduces **transaction management and undo/redo capabilities**, along with enhanced security protections and comprehensive testing infrastructure. This is a significant feature release that enables safe, auditable modifications to FieldWorks lexicons.

### Key Highlights

- **Transaction & Undo/Redo Framework** - Phase 1 implementation for safe, reversible operations
- **Security Guards** - Write-enable protection on 7 untagged mutating methods
- **Decorator Bug Fixes** - Fixed `'OperationsMethod' object is not callable'` errors
- **Pre-commit Hooks** - Automated quality checks prevent common mistakes
- **Contract Testing** - Validates API compatibility across LibLCM versions
- **100% Backward Compatible** with v2.3.x APIs

---

## Major Features

### 1. Transaction & Undo/Redo Framework

FlexLibs2 v2.4.0 introduces Phase 1 of safe transaction management:

#### What's New
- **Automatic transaction tracking** - All mutations wrapped in LCM transactions
- **Rollback on failure** - Failed operations automatically revert state
- **Undo/redo testing** - Comprehensive test suite and documentation
- **Error recovery** - Clear patterns for handling transaction errors

#### Example Usage
```python
from flexlibs2 import FLExProject, LexEntryOperations

project = FLExProject('MyProject')
lex_ops = project.LexEntry

try:
    # Transaction automatically wrapped
    entry = lex_ops.Create("new_form", "new_gloss")
    entry_sense = entry.GetSenses()[0]
    entry_sense.SetGloss("updated_gloss")

    # If anything fails between Create and here, auto-rollback occurs
    project.SaveChanges()
except Exception as e:
    print(f"Operation failed and rolled back: {e}")
    # Database state unchanged
```

#### Documentation
- **docs/TESTING_UNDO_REDO.md** - Complete testing guide with unit test examples
- **docs/TRANSACTION_GUIDE.md** - Best practices for transaction-safe code
- Tests in `tests/test_undo_redo_mocked.py`

### 2. Security: Write-Enable Guards

#### What's Protected
Seven previously untagged mutating methods now have `_EnsureWriteEnabled()` guards:
- Prevent accidental modifications in read-only mode
- Clearly signal to users that write permission is required
- Consistent with all other mutating Operations methods

#### Methods Protected
- BestStr() - for string normalization
- Collection mutation operations
- Transaction state modifications
- (See commit cc1b2bc for complete list)

### 3. Bug Fixes: Duplicate Decorator Resolution

#### The Problem
31 methods across 3 Operations classes had duplicate `@OperationsMethod` decorators, causing:
```
TypeError: 'OperationsMethod' object is not callable
```

#### The Fix
- **BaseOperations.py** - 9 methods cleaned
- **POSOperations.py** - 17 methods cleaned (GetAll was triple-decorated!)
- **LexEntryOperations.py** - 5 methods cleaned
- **All 64 operation files** verified clean in post-release audit

### 4. Pre-commit Hooks

Automated quality checks run before each commit:

#### Included Hooks
- **Custom decorator validator** - Prevents duplicate decorators
- **Black** - Code formatting enforcement
- **Flake8** - Unused imports, complexity warnings
- **Detect-secrets** - Credential detection

#### Setup
See `docs/PRE_COMMIT_SETUP.md` for installation:
```bash
pip install pre-commit
pre-commit install
```

### 5. Contract Testing

Validates FlexLibs2 API against LibLCM C# interface across versions:
- Located in `tests/liblcm_contract_tests/`
- Auto-detects LibLCM version
- Ensures wrappers match underlying C# API

#### Documentation
- **docs/CONTRACT_TESTING.md** - How contract tests work
- Installable pre-commit hook for CI/CD

---

## Complete Changelog

### Added
- Transaction & undo/redo framework (Phase 1)
- Write-enable guards on 7 untagged methods
- Pre-commit hooks for code quality
- Contract testing suite for LibLCM compatibility
- TESTING_UNDO_REDO.md - Comprehensive testing guide
- TRANSACTION_GUIDE.md - Best practices guide
- CONTRACT_TESTING.md - API validation guide

### Fixed
- Duplicate `@OperationsMethod` decorators (31 methods, 3 files)
- Decorator validation in pre-commit hooks
- Test imports and circular dependencies

### Documentation
- 3 new comprehensive guides
- Updated README.md links
- Expanded API examples
- Testing patterns and best practices

---

## Backward Compatibility

**100% Maintained** - All v2.3.x APIs remain fully functional:
- No breaking changes
- All decorators fixed but functionality unchanged
- Guards are transparent (don't affect normal usage)
- New features are additive only

### Migration Path
If you're upgrading from v2.3.x:
1. No code changes required
2. Optional: Review docs/TRANSACTION_GUIDE.md for transaction patterns
3. Optional: Set up pre-commit hooks (docs/PRE_COMMIT_SETUP.md)

---

## Testing

### Test Coverage
- ✓ Unit tests for undo/redo operations
- ✓ Contract tests against LibLCM API
- ✓ Pre-commit hook validation
- ✓ Decorator duplicate detection

### Test Files
- `tests/test_undo_redo_mocked.py` - Comprehensive undo/redo test suite
- `tests/liblcm_contract_tests/` - API contract validation
- `scripts/check_decorators.py` - Decorator validator tool

---

## Known Limitations

### Transaction Support (Phase 1)
- Undo/redo queue not yet persistent across sessions
- Complex nested operations may require explicit transaction handling
- See docs/TESTING_UNDO_REDO.md for Phase 2 roadmap

### Pre-commit Hooks
- Requires manual setup (not automatic on clone)
- Some hooks (flake8) can be strict on legacy code
- Documentations in docs/PRE_COMMIT_SETUP.md

---

## Installation

### From PyPI
```bash
pip install flexlibs2==2.4.0
```

### From Source
```bash
git clone https://github.com/cdfarrow/flexlibs.git
cd flexlibs
git checkout v2.4.0
pip install -e .
```

---

## Support & Documentation

- **README.md** - Quick start and overview
- **docs/** - Comprehensive guides and API reference
- **examples/** - 40+ working code examples
- **tests/** - Test suite and patterns
- **GitHub Issues** - Report bugs and request features

---

## Contributors

- Core team (transaction & guards implementation)
- Matthew Lee (contract testing integration)
- Community testers and feedback

---

## What's Next

### v2.4.1 (Planned)
- Phase 2: Persistent undo/redo across sessions
- Enhanced transaction diagnostics
- Additional guard coverage

### Future Roadmap
- GUI undo/redo integration
- Multi-user transaction coordination
- Performance optimization for large projects

---

