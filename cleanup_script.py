#!/usr/bin/env python3
"""
Script to analyze and fix common code quality issues in Python files.
"""

import os
import re
from pathlib import Path

def analyze_file(filepath):
    """Analyze a file for common issues."""
    issues = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    # Check for unused logger
    has_logger_import = bool(re.search(r'^import logging\s*$', content, re.MULTILINE) or
                             re.search(r'^logger = logging\.getLogger', content, re.MULTILINE))
    has_logger_usage = bool(re.search(r'\blogger\.', content))

    if has_logger_import and not has_logger_usage:
        issues.append("unused_logger")

    # Check for bare except clauses
    bare_excepts = []
    for i, line in enumerate(lines, 1):
        if re.match(r'^\s*except:\s*$', line):
            bare_excepts.append(i)

    if bare_excepts:
        issues.append(f"bare_except_at_lines:{','.join(map(str, bare_excepts))}")

    # Check for commented-out code (excluding docstrings and meaningful comments)
    commented_code = []
    in_docstring = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Skip docstrings
        if '"""' in stripped or "'''" in stripped:
            in_docstring = not in_docstring
            continue
        if in_docstring:
            continue

        # Look for commented-out code patterns
        if stripped.startswith('#'):
            # Skip meaningful comments (those with text explanations)
            comment_content = stripped[1:].strip()
            # Check if it looks like code (has assignment, function calls, etc.)
            if any(pattern in comment_content for pattern in ['=', '()', 'import ', 'from ', 'def ', 'class ']):
                if not comment_content.startswith('TODO') and not comment_content.startswith('FIXME'):
                    commented_code.append(i)

    if commented_code:
        issues.append(f"commented_code_at_lines:{','.join(map(str, commented_code[:5]))}")  # First 5

    # Check for multiple blank lines
    blank_count = 0
    multi_blank_lines = []
    for i, line in enumerate(lines, 1):
        if not line.strip():
            blank_count += 1
            if blank_count > 2:
                multi_blank_lines.append(i)
        else:
            blank_count = 0

    if multi_blank_lines:
        issues.append(f"excess_blank_lines:{len(multi_blank_lines)}")

    return issues

def main():
    """Analyze all Python files in the code directory."""
    code_dir = Path('/home/user/flexlibs/flexlibs/code')

    all_py_files = sorted(code_dir.rglob('*.py'))

    results = {}
    for pyfile in all_py_files:
        if '__pycache__' in str(pyfile):
            continue
        issues = analyze_file(pyfile)
        if issues:
            results[str(pyfile)] = issues

    # Print summary
    print("=" * 80)
    print("CODE QUALITY ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"\nTotal files analyzed: {len(all_py_files)}")
    print(f"Files with issues: {len(results)}")
    print("\nISSUES BY FILE:")
    print("-" * 80)

    for filepath, issues in results.items():
        rel_path = filepath.replace('/home/user/flexlibs/flexlibs/code/', '')
        print(f"\n{rel_path}:")
        for issue in issues:
            print(f"  - {issue}")

    # Count by issue type
    print("\n" + "=" * 80)
    print("ISSUE TYPE COUNTS:")
    print("-" * 80)
    issue_types = {}
    for issues in results.values():
        for issue in issues:
            issue_type = issue.split(':')[0]
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

    for issue_type, count in sorted(issue_types.items()):
        print(f"{issue_type}: {count} files")

if __name__ == '__main__':
    main()
