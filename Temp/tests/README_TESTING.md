# Testing Guide for FlexLibs Delegation Refactoring

This document explains how to set up, run, and interpret the delegation compatibility tests for the FlexLibs refactoring project.

## Overview

The delegation compatibility tests verify that Craig's original methods and the new Operations classes return identical results, ensuring backward compatibility after the refactoring.

### Test Coverage

- **42 delegated methods** across 9 categories
- **Both APIs tested**: Craig's original API and new Operations API
- **Parameter variations**: Default parameters, specific writing systems, optional parameters
- **Edge cases**: Empty data, missing objects, None parameters
- **Error handling**: Proper exception behavior

### Test Categories

1. **LexEntry Operations** (5 tests): Headword, lexeme form, citation form, entry retrieval
2. **LexSense Operations** (7 tests): Gloss, definition, POS, semantic domains, sense numbers
3. **Example Operations** (2 tests): Get and set example sentences
4. **Pronunciation Operations** (1 test): Get pronunciation forms
5. **Text Operations** (2 tests): Get all texts, text count
6. **Reversal Operations** (4 tests): Reversal index, entries, get/set forms
7. **System Operations** (4 tests): POS, semantic domains, lexical relations, publications
8. **Writing System Operations** (7 tests): Best string, vernacular/analysis WS, UI names
9. **CustomField Operations** (9 tests): Field types, custom field retrieval

## Setup

### Prerequisites

1. **Python 3.x** with pytest installed:
   ```bash
   pip install pytest
   ```

2. **FieldWorks Language Explorer (FLEx)** installed on your system

3. **A test FLEx project** with sample data:
   - Lexical entries with headwords, lexeme forms, citation forms
   - Senses with glosses, definitions, POS, semantic domains
   - Example sentences
   - Pronunciations (optional)
   - Texts (optional)
   - Reversal indices (optional)
   - Custom fields (optional)

### Configuration

#### Option 1: Environment Variable (Recommended)

Set the `FLEX_TEST_PROJECT` environment variable to your test project name:

**Windows (Command Prompt):**
```cmd
set FLEX_TEST_PROJECT=MyTestProject
```

**Windows (PowerShell):**
```powershell
$env:FLEX_TEST_PROJECT = "MyTestProject"
```

**Linux/Mac:**
```bash
export FLEX_TEST_PROJECT=MyTestProject
```

#### Option 2: Edit Test File

Edit `test_delegation_compatibility.py` line 37:
```python
PROJECT_NAME = os.environ.get('FLEX_TEST_PROJECT', 'YourProjectName')
```

### Test Project Requirements

For comprehensive testing, your test project should have:

#### Minimum Requirements (Core Tests)
- At least 1 lexical entry
- At least 1 sense on an entry
- Basic POS list
- At least 1 writing system configured

#### Recommended Data (Full Test Coverage)
- Multiple lexical entries with varied data
- Entries with multiple senses
- Senses with glosses and definitions
- Senses with POS and semantic domains
- Example sentences on senses
- Pronunciations on entries
- At least 1 text
- At least 1 reversal index
- Custom fields defined at entry, sense, or example level

#### Creating a Test Project

If you don't have a test project, you can:

1. Open FLEx and create a new project
2. Use the "Sample Data" option if available
3. Or manually add a few entries with basic information
4. Close FLEx before running tests

## Running Tests

### Run All Tests

```bash
cd d:\Github\flexlibs
pytest tests/test_delegation_compatibility.py -v
```

### Run Specific Test Categories

Test only LexEntry operations:
```bash
pytest tests/test_delegation_compatibility.py -v -k "LexEntry"
```

Test only writing system operations:
```bash
pytest tests/test_delegation_compatibility.py -v -k "WritingSystem"
```

Test only read operations (skip setters):
```bash
pytest tests/test_delegation_compatibility.py -v -k "not set"
```

### Run with Detailed Output

Show full error tracebacks:
```bash
pytest tests/test_delegation_compatibility.py -v --tb=long
```

Show short tracebacks:
```bash
pytest tests/test_delegation_compatibility.py -v --tb=short
```

Show test output (print statements):
```bash
pytest tests/test_delegation_compatibility.py -v -s
```

### Run Specific Test Classes

```bash
pytest tests/test_delegation_compatibility.py::TestLexEntryOperations -v
pytest tests/test_delegation_compatibility.py::TestWritingSystemOperations -v
pytest tests/test_delegation_compatibility.py::TestCustomFieldOperations -v
```

### Run Specific Test Methods

```bash
pytest tests/test_delegation_compatibility.py::TestLexEntryOperations::test_lexicon_get_headword_compatibility -v
```

## Interpreting Test Results

### Success

```
test_delegation_compatibility.py::TestLexEntryOperations::test_lexicon_get_headword_compatibility PASSED
```

This means both Craig's API and the Operations API returned identical results. Backward compatibility is maintained.

### Skipped Tests

```
test_delegation_compatibility.py::TestExampleOperations::test_lexicon_get_example_compatibility SKIPPED (No examples available in sample sense)
```

Tests are skipped when the required test data is not available. This is expected if your test project doesn't have all types of data.

**Common skip reasons:**
- "No lexical entries in test project" - Project is empty
- "No senses available in sample entry" - Entry has no senses
- "No examples available in sample sense" - Sense has no examples
- "No custom fields defined for testing" - No custom fields in project

### Failures

```
FAILED test_delegation_compatibility.py::TestLexEntryOperations::test_lexicon_get_headword_compatibility
AssertionError: LexiconGetHeadword: APIs must return identical results.
  Craig's API:      'run'
  Operations API:   'running'
```

A failure indicates that the two APIs returned different results, meaning backward compatibility is broken. This requires investigation and fixing.

### Test Statistics

```
========================= 35 passed, 7 skipped in 5.23s =========================
```

- **Passed**: Number of tests where both APIs matched
- **Skipped**: Number of tests skipped due to missing data
- **Failed**: Number of tests where APIs returned different results (should be 0)

## Understanding Test Structure

### Test Pattern

Each test follows this pattern:

```python
def test_method_compatibility(self, project, sample_entry):
    """Verify Craig's API matches Operations API."""
    # Act - Call both APIs
    result_craig = project.OldMethod(sample_entry)
    result_operations = project.NewOperations.NewMethod(sample_entry)

    # Assert - Results must match
    compare_results(result_craig, result_operations, "MethodName")
```

### Fixtures

- `project`: Read-only project instance (used for getter tests)
- `writable_project`: Writable project instance (used for setter tests)
- `sample_entry`: First lexical entry in project
- `sample_sense`: First sense from sample entry
- `sample_example`: First example from sample sense
- `sample_pronunciation`: First pronunciation from sample entry
- `sample_text`: First text in project
- `sample_reversal_index`: First reversal index in project

### Test Decorators

- `@skip_if_no_data`: Gracefully skips test if required data is missing

## Writing System Tests

Many tests accept an optional `languageTagOrHandle` parameter to specify a writing system. Tests verify both:

1. **Default writing system** (parameter omitted)
2. **Specific writing system** (parameter provided)

Example:
```python
# Default WS
result = project.LexiconGetLexemeForm(entry)

# Specific WS
ws = project.GetDefaultVernacularWS()
result = project.LexiconGetLexemeForm(entry, ws)
```

## Setter Tests (Write Operations)

Setter tests (e.g., `test_lexicon_set_lexeme_form_compatibility`) require write access and:

1. Save the original value
2. Test setting with Craig's API
3. Test setting with Operations API
4. Restore the original value

These tests modify data temporarily but clean up afterward.

## Troubleshooting

### "Project file not found: TestProject"

- The specified project doesn't exist
- Check project name is correct
- Ensure project is in default FLEx projects location
- Set `FLEX_TEST_PROJECT` environment variable

### "This project is in use by another program"

- Close FLEx before running tests
- Close any other programs accessing the project
- Check for orphaned processes

### "This project needs to be opened in FieldWorks in order for it to be migrated"

- Open project in FLEx once to migrate it
- Close FLEx and run tests again

### Many Skipped Tests

- Your test project may not have comprehensive data
- Add more entries, senses, examples, etc. to your test project
- Some skips are normal (e.g., if you don't use reversal indices)

### Import Errors

```
ModuleNotFoundError: No module named 'flexlibs'
```

- Make sure you're running from the repository root directory
- Verify Python path includes the flexlibs directory
- Check that `flexlibs/code/__init__.py` exists

### Connection Issues

If tests hang or timeout:
- Check FLEx installation is working
- Try opening project manually in FLEx first
- Restart computer to clear any locked processes

## Test Maintenance

### Adding New Tests

When new delegated methods are added:

1. Add test method to appropriate test class
2. Follow existing test pattern
3. Add fixtures if needed for test data
4. Update test coverage count in `test_delegation_coverage()`
5. Update this README

### Modifying Tests

When updating tests:
- Maintain backward compatibility testing focus
- Keep test data requirements minimal
- Use `skip_if_no_data` for graceful handling
- Ensure setter tests clean up after themselves

## Best Practices

1. **Run tests before committing** refactoring changes
2. **All tests should pass** (0 failed tests)
3. **Skipped tests are okay** if test data is unavailable
4. **Keep test project small** but representative
5. **Don't commit test project** to repository
6. **Document any new test requirements** in this file

## Continuous Integration

For CI/CD pipelines:

1. Set up FLEx in CI environment
2. Create/restore test project
3. Set `FLEX_TEST_PROJECT` environment variable
4. Run tests with: `pytest tests/test_delegation_compatibility.py -v --tb=short`
5. Fail build if any tests fail (non-zero exit code)

Example GitHub Actions workflow:
```yaml
- name: Run delegation compatibility tests
  env:
    FLEX_TEST_PROJECT: TestProject
  run: |
    pytest tests/test_delegation_compatibility.py -v --tb=short
```

## Test Coverage Summary

### By Method Count
| Category | Methods Tested |
|----------|---------------|
| LexEntry Operations | 5 |
| LexSense Operations | 7 |
| Example Operations | 2 |
| Pronunciation Operations | 1 |
| Text Operations | 2 |
| Reversal Operations | 4 |
| System Operations | 4 |
| Writing System Operations | 7 |
| CustomField Operations | 9 |
| **Total** | **42** |

### By Operation Type
- **Read operations**: 35 tests
- **Write operations**: 7 tests
- **System operations**: 11 tests

## Contact and Support

For issues with tests:
1. Check this README first
2. Review test output carefully
3. Verify test project has required data
4. Check for environment issues (locked files, permissions)
5. Review test implementation for edge cases

## Version History

- **2025-11-24**: Initial test suite created with 42 tests across 9 categories
- Coverage: All delegated methods in FLExProject.py refactoring

## Related Documentation

- `ARCHITECTURE.md` - Overall refactoring architecture
- `REFACTORING_LOG.md` - Detailed refactoring progress
- `FUNCTION_REFERENCE.md` - Complete API reference
- `test_delegation_compatibility.py` - Test implementation

---

**Last Updated**: 2025-11-24
**Test Suite Version**: 1.0
**Total Tests**: 42 + 1 meta-test
