#!/usr/bin/env python3
"""
Script to automatically fix common code quality issues.
"""

import os
import re
from pathlib import Path

def fix_unused_logger(content):
    """Remove unused logger imports."""
    # Check if logger is used
    if not re.search(r'\blogger\.', content):
        # Remove logger import lines
        content = re.sub(r'^import logging\s*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^logger = logging\.getLogger\(__name__\)\s*\n', '', content, flags=re.MULTILINE)
        # Clean up extra blank lines that might result
        content = re.sub(r'\n\n\n+', '\n\n', content)
    return content

def fix_bare_except(content):
    """Fix bare except clauses."""
    # Replace bare except: with except Exception:
    # But be careful not to replace in docstrings or comments
    lines = content.split('\n')
    result_lines = []
    in_docstring = False

    for line in lines:
        # Track docstrings
        if '"""' in line or "'''" in line:
            in_docstring = not in_docstring

        # Fix bare except if not in docstring
        if not in_docstring and re.match(r'^(\s*)except:\s*$', line):
            indent = re.match(r'^(\s*)except:\s*$', line).group(1)
            result_lines.append(f'{indent}except Exception:')
        else:
            result_lines.append(line)

    return '\n'.join(result_lines)

def fix_excess_blank_lines(content):
    """Remove excess blank lines (more than 2 consecutive)."""
    return re.sub(r'\n\n\n+', '\n\n', content)

def fix_file(filepath):
    """Fix issues in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Apply fixes
    content = fix_unused_logger(content)
    content = fix_bare_except(content)
    content = fix_excess_blank_lines(content)

    # Only write if changed
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all Python files in the code directory."""
    code_dir = Path('/home/user/flexlibs/flexlibs/code')

    all_py_files = sorted(code_dir.rglob('*.py'))

    fixed_files = []
    for pyfile in all_py_files:
        if '__pycache__' in str(pyfile) or '__init__.py' in str(pyfile):
            continue

        if fix_file(pyfile):
            fixed_files.append(str(pyfile))

    print(f"Fixed {len(fixed_files)} files:")
    for f in fixed_files:
        rel_path = f.replace('/home/user/flexlibs/flexlibs/code/', '')
        print(f"  - {rel_path}")

if __name__ == '__main__':
    main()
