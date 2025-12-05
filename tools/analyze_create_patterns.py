#!/usr/bin/env python3
"""
Analyze factory.Create() patterns to identify object creation sequence bugs.

This script searches for patterns where:
1. factory.Create() is called
2. Properties are set on the new object
3. The object is added to a collection

The CORRECT sequence is:
1. factory.Create()
2. Add to collection
3. Set properties

Bug Pattern (WRONG):
    new_obj = factory.Create()
    new_obj.Property = value  # Setting before adding - FAILS
    collection.Add(new_obj)

Correct Pattern:
    new_obj = factory.Create()
    collection.Add(new_obj)   # Add first - object gets Services
    new_obj.Property = value  # Now can set properties
"""

import os
import re
import glob

operations_patterns = [
    "flexlibs/code/Grammar/*.py",
    "flexlibs/code/Lexicon/*.py",
    "flexlibs/code/TextsWords/*.py",
    "flexlibs/code/Notebook/*.py",
    "flexlibs/code/Lists/*.py",
    "flexlibs/code/System/*.py",
]


def analyze_file(filepath):
    """
    Analyze a file for potential object creation sequence bugs.

    Args:
        filepath: Path to the Python file to analyze

    Returns:
        List of issues found in the file
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all factory.Create() calls with context
    create_pattern = r'(\w+)\s*=\s*factory\.Create\(\)([^\n]*\n(?:.*?\n){0,20})'
    matches = re.finditer(create_pattern, content, re.MULTILINE)

    issues = []
    for match in matches:
        var_name = match.group(1)
        context = match.group(2)

        # Check if properties are set before Add()
        # Look for patterns like: var_name.Property = value OR var_name.Method()
        property_pattern = rf'{var_name}\.\w+[\.\(]'
        add_pattern = rf'\.Add\({var_name}\)'

        property_match = re.search(property_pattern, context)
        add_match = re.search(add_pattern, context)

        if property_match and add_match:
            # Check if property comes before Add
            if property_match.start() < add_match.start():
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'line': line_num,
                    'var': var_name,
                    'context': match.group(0)[:200]
                })

    return issues


def main():
    print("=" * 70)
    print("ANALYZING OBJECT CREATION SEQUENCE PATTERNS")
    print("=" * 70)
    print()

    total_files = 0
    files_with_issues = 0
    total_issues = 0

    for pattern in operations_patterns:
        for filepath in glob.glob(pattern):
            total_files += 1
            issues = analyze_file(filepath)

            if issues:
                files_with_issues += 1
                total_issues += len(issues)
                print(f"\n{os.path.basename(filepath)}:")
                print(f"  {len(issues)} potential issue(s)")

                for issue in issues[:3]:  # Show first 3
                    print(f"    Line {issue['line']}: {issue['var']}")

                if len(issues) > 3:
                    print(f"    ... and {len(issues) - 3} more")

    print("\n" + "=" * 70)
    print(f"SUMMARY:")
    print(f"  Files analyzed: {total_files}")
    print(f"  Files with potential issues: {files_with_issues}")
    print(f"  Total potential issues: {total_issues}")
    print("=" * 70)
    print()
    print("Note: This is a heuristic analysis. Manual review required.")
    print("Pattern: Setting properties BEFORE adding to collection likely fails.")


if __name__ == "__main__":
    main()
