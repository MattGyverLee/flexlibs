# Testing Guidelines

## Complete Data Access Initiative - Testing Standards

**Version**: 1.0
**Last Updated**: 2025-11-22  
**Framework**: pytest
**Coverage Target**: >90%

## Quick Reference

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=flexlibs_dev --cov-report=html

# Specific test
pytest tests/test_text_ops.py::test_text_create
```

### Test Structure (AAA Pattern)
```python
def test_text_create_with_genre(db):
    # Arrange
    name = "Genesis"
    genre = "Narrative"
    
    # Act
    text = db.TextCreate(name, genre=genre)
    
    # Assert
    assert text is not None
    assert db.TextGetName(text) == name
    
    # Cleanup
    db.TextDelete(text)
```

### Required Tests Per Cluster
1. **CRUD**: create, delete, exists, get_all
2. **Properties**: get/set pairs
3. **Errors**: invalid input, not found
4. **Integration**: realistic workflow

### Coverage Requirements
- Overall: >90%
- Per cluster: >90%
- Critical methods: 100%
- All error paths tested

### Test Categories
- **Unit Tests**: Individual methods
- **Integration Tests**: Methods working together
- **Error Tests**: Exception handling
- **Edge Cases**: Boundaries, Unicode, etc.

### Best Practices
✅ DO:
- Use descriptive test names
- Follow AAA pattern
- Test error conditions
- Clean up test data
- Use fixtures

❌ DON'T:
- Write dependent tests
- Hardcode paths
- Skip error testing
- Leave test data
- Write flaky tests

For complete guidelines, see full TESTING_GUIDELINES.md.
