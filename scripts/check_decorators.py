#!/usr/bin/env python3
"""
Pre-commit hook to detect duplicate @OperationsMethod decorators.

This prevents the 'OperationsMethod object is not callable' errors
that occur when decorators are accidentally duplicated.

Usage:
  python scripts/check_decorators.py file1.py file2.py ...
"""

import sys
from pathlib import Path


def check_file(filepath):
    """Check a single file for duplicate decorators.

    Returns:
        list: List of error messages (empty if file is OK)
    """
    errors = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (IOError, OSError) as e:
        return [f"{filepath}: {e}"]

    for i in range(len(lines) - 1):
        line = lines[i].strip()
        next_line = lines[i + 1].strip()

        # Check for consecutive duplicate decorators
        if line == "@OperationsMethod" and next_line == "@OperationsMethod":
            line_num = i + 1
            errors.append(
                f"{filepath}:{line_num}: " f"Duplicate @OperationsMethod decorator (also at line {line_num + 1})"
            )

        # Check for triple decorator pattern
        if i < len(lines) - 3:
            third = lines[i + 2].strip()
            fourth = lines[i + 3].strip() if i + 3 < len(lines) else ""

            if (
                line == "@OperationsMethod"
                and next_line == "@OperationsMethod"
                and third == "@wrap_enumerable"
                and fourth == "@OperationsMethod"
            ):
                line_num = i + 1
                errors.append(
                    f"{filepath}:{line_num}: " f"Triple/quadruple decorator stack - remove duplicate @OperationsMethod"
                )

    return errors


def main():
    """Check all provided files."""
    if not sys.argv[1:]:
        print("Usage: check_decorators.py <file1> <file2> ...", file=sys.stderr)
        return 1

    all_errors = []

    for filepath in sys.argv[1:]:
        # Only check operation files
        if not filepath.endswith("Operations.py"):
            continue

        errors = check_file(filepath)
        all_errors.extend(errors)

    if all_errors:
        for error in all_errors:
            print(error)
        print(f"\n[ERROR] Found {len(all_errors)} decorator issue(s)", file=sys.stderr)
        return 1

    print("[OK] No duplicate decorators found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
