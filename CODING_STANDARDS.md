# Coding Standards

## Complete Data Access Initiative - Python Coding Standards

**Version**: 1.0  
**Last Updated**: 2025-11-22

See full version in Git history for complete details.

## Key Standards

1. **Python Version**: 3.7+ (Target: 3.11+)
2. **Formatter**: Black (line length 88)
3. **Linting**: Flake8
4. **Type Checking**: Mypy

## Naming
- Methods: PascalCase (FlexTools API)
- Variables: snake_case  
- Constants: UPPER_SNAKE_CASE
- HVO parameters: `text_or_hvo`, `para_or_hvo`

## Type Hints (Required)
```python
def TextCreate(self, name: str, genre: Optional[str] = None) -> IText:
    pass
```

## Docstrings (Google Style Required)
```python
def TextCreate(self, name: str) -> IText:
    """
    Create a new text.
    
    Args:
        name: Text name (must be unique).
        
    Returns:
        IText: Created text object.
        
    Raises:
        ValueError: If name is empty.
    """
```

## Error Handling
- Use specific exceptions
- Clear error messages
- No bare `except:`

## COM Interop
- Null checks required
- UndoableUnitOfWork for writes
- PropChanged after modifications

For complete standards, see CODING_STANDARDS.md in documentation.
