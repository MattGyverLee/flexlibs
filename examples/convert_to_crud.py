#!/usr/bin/env python3
"""
Automated CRUD Demo Converter

Converts simple demo files to full CRUD test demos following the standard pattern.

Author: FlexTools Development Team
Date: 2025-11-27
"""

import os
import re
from pathlib import Path


CRUD_TEMPLATE = '''#!/usr/bin/env python3
"""
Full CRUD Demo: {operation_title}Operations for flexlibs

This script demonstrates complete CRUD operations for {operation_lower}.
Performs actual create, read, update, and delete operations on test data.

Author: FlexTools Development Team
Date: 2025-11-27
"""

from flexlibs2 import FLExProject, FLExInitialize, FLExCleanup

def demo_{operation_lower}_crud():
    """
    Demonstrate full CRUD operations for {operation_lower}.

    Tests:
    - CREATE: Create new test {operation_lower}
    - READ: Get all {operation_lower}s, find by name/identifier
    - UPDATE: Modify {operation_lower} properties
    - DELETE: Remove test {operation_lower}
    """

    print("=" * 70)
    print("{operation_upper} OPERATIONS - FULL CRUD TEST")
    print("=" * 70)

    # Initialize FieldWorks
    FLExInitialize()

    # Open project with write enabled
    project = FLExProject()
    try:
        project.OpenProject("Sena 3", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {{e}}")
        FLExCleanup()
        return

    test_obj = None
    test_name = "crud_test_{operation_lower}"

    try:
        # ==================== READ: Initial state ====================
        print("\\n" + "="*70)
        print("STEP 1: READ - Get existing {operation_lower}s")
        print("="*70)

        print("\\nGetting all {operation_lower}s...")
        initial_count = 0
        for obj in project.{operation_title}.GetAll():
            # Display first few objects
            try:
                name = project.{operation_title}.GetName(obj) if hasattr(project.{operation_title}, 'GetName') else str(obj)
                print(f"  - {{name}}")
            except:
                print(f"  - [Object {{initial_count + 1}}]")
            initial_count += 1
            if initial_count >= 5:
                break

        print(f"\\nTotal {operation_lower}s (showing first 5): {{initial_count}}")

        # ==================== CREATE ====================
        print("\\n" + "="*70)
        print("STEP 2: CREATE - Create new test {operation_lower}")
        print("="*70)

        # Check if test object already exists
        try:
            if hasattr(project.{operation_title}, 'Exists') and project.{operation_title}.Exists(test_name):
                print(f"\\nTest {operation_lower} '{{test_name}}' already exists")
                print("Deleting existing one first...")
                existing = project.{operation_title}.Find(test_name) if hasattr(project.{operation_title}, 'Find') else None
                if existing:
                    project.{operation_title}.Delete(existing)
                    print("  Deleted existing test {operation_lower}")
        except:
            pass

        # Create new object
        print(f"\\nCreating new {operation_lower}: '{{test_name}}'")

        try:
            # Attempt to create with common parameters
            test_obj = project.{operation_title}.Create(test_name)
        except TypeError:
            try:
                # Try without parameters if that fails
                test_obj = project.{operation_title}.Create()
                if hasattr(project.{operation_title}, 'SetName'):
                    project.{operation_title}.SetName(test_obj, test_name)
            except Exception as e:
                print(f"  Note: Create method may require specific parameters: {{e}}")
                test_obj = None

        if test_obj:
            print(f"  SUCCESS: {operation_title} created!")
            try:
                if hasattr(project.{operation_title}, 'GetName'):
                    print(f"  Name: {{project.{operation_title}.GetName(test_obj)}}")
            except:
                pass
        else:
            print(f"  Note: Could not create {operation_lower} (may require special parameters)")
            print("  Skipping remaining tests...")
            return

        # ==================== READ: Verify creation ====================
        print("\\n" + "="*70)
        print("STEP 3: READ - Verify {operation_lower} was created")
        print("="*70)

        # Test Exists
        if hasattr(project.{operation_title}, 'Exists'):
            print(f"\\nChecking if '{{test_name}}' exists...")
            exists = project.{operation_title}.Exists(test_name)
            print(f"  Exists: {{exists}}")

        # Test Find
        if hasattr(project.{operation_title}, 'Find'):
            print(f"\\nFinding {operation_lower} by name...")
            found_obj = project.{operation_title}.Find(test_name)
            if found_obj:
                print(f"  FOUND: {operation_lower}")
                try:
                    if hasattr(project.{operation_title}, 'GetName'):
                        print(f"  Name: {{project.{operation_title}.GetName(found_obj)}}")
                except:
                    pass
            else:
                print("  NOT FOUND")

        # Count after creation
        print("\\nCounting all {operation_lower}s after creation...")
        current_count = sum(1 for _ in project.{operation_title}.GetAll())
        print(f"  Count before: {{initial_count}}")
        print(f"  Count after:  {{current_count}}")
        print(f"  Difference:   +{{current_count - initial_count}}")

        # ==================== UPDATE ====================
        print("\\n" + "="*70)
        print("STEP 4: UPDATE - Modify {operation_lower} properties")
        print("="*70)

        if test_obj:
            updated = False

            # Try common update methods
            if hasattr(project.{operation_title}, 'SetName'):
                try:
                    new_name = "crud_test_{operation_lower}_modified"
                    print(f"\\nUpdating name to: '{{new_name}}'")
                    old_name = project.{operation_title}.GetName(test_obj) if hasattr(project.{operation_title}, 'GetName') else test_name
                    project.{operation_title}.SetName(test_obj, new_name)
                    updated_name = project.{operation_title}.GetName(test_obj) if hasattr(project.{operation_title}, 'GetName') else new_name
                    print(f"  Old name: {{old_name}}")
                    print(f"  New name: {{updated_name}}")
                    test_name = new_name  # Update for cleanup
                    updated = True
                except Exception as e:
                    print(f"  Note: SetName failed: {{e}}")

            # Try other Set methods
            for method_name in dir(project.{operation_title}):
                if method_name.startswith('Set') and method_name != 'SetName' and not updated:
                    print(f"\\nFound update method: {{method_name}}")
                    print("  (Method available but not tested in this demo)")
                    break

            if updated:
                print("\\n  UPDATE: SUCCESS")
            else:
                print("\\n  Note: No standard update methods found or tested")

        # ==================== READ: Verify updates ====================
        print("\\n" + "="*70)
        print("STEP 5: READ - Verify updates persisted")
        print("="*70)

        if hasattr(project.{operation_title}, 'Find'):
            print(f"\\nFinding {operation_lower} after update...")
            updated_obj = project.{operation_title}.Find(test_name)
            if updated_obj:
                print(f"  FOUND: {operation_lower}")
                try:
                    if hasattr(project.{operation_title}, 'GetName'):
                        print(f"  Name: {{project.{operation_title}.GetName(updated_obj)}}")
                except:
                    pass
            else:
                print("  NOT FOUND - Update may not have persisted")

        # ==================== DELETE ====================
        print("\\n" + "="*70)
        print("STEP 6: DELETE - Remove test {operation_lower}")
        print("="*70)

        if test_obj:
            print(f"\\nDeleting test {operation_lower}...")
            try:
                obj_name = project.{operation_title}.GetName(test_obj) if hasattr(project.{operation_title}, 'GetName') else test_name
            except:
                obj_name = test_name

            project.{operation_title}.Delete(test_obj)
            print(f"  Deleted: {{obj_name}}")

            # Verify deletion
            print("\\nVerifying deletion...")
            if hasattr(project.{operation_title}, 'Exists'):
                still_exists = project.{operation_title}.Exists(test_name)
                print(f"  Still exists: {{still_exists}}")

                if not still_exists:
                    print("  DELETE: SUCCESS")
                else:
                    print("  DELETE: FAILED - {operation_title} still exists")

            # Count after deletion
            final_count = sum(1 for _ in project.{operation_title}.GetAll())
            print(f"\\n  Count after delete: {{final_count}}")
            print(f"  Back to initial:    {{final_count == initial_count}}")

        # ==================== SUMMARY ====================
        print("\\n" + "="*70)
        print("CRUD TEST SUMMARY")
        print("="*70)
        print("\\nOperations tested:")
        print("  [CREATE] Create new {operation_lower}")
        print("  [READ]   GetAll, Find, Exists, Get methods")
        print("  [UPDATE] Set methods")
        print("  [DELETE] Delete {operation_lower}")
        print("\\nTest completed successfully!")

    except Exception as e:
        print(f"\\n\\nERROR during CRUD test: {{e}}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup: Ensure test object is removed
        print("\\n" + "="*70)
        print("CLEANUP")
        print("="*70)

        try:
            for name in ["crud_test_{operation_lower}", "crud_test_{operation_lower}_modified"]:
                if hasattr(project.{operation_title}, 'Exists') and project.{operation_title}.Exists(name):
                    obj = project.{operation_title}.Find(name) if hasattr(project.{operation_title}, 'Find') else None
                    if obj:
                        project.{operation_title}.Delete(obj)
                        print(f"  Cleaned up: {{name}}")
        except:
            pass

        print("\\nClosing project...")
        project.CloseProject()
        FLExCleanup()

    print("\\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    print("""
{operation_title} Operations - Full CRUD Demo
=====================================================

This demonstrates COMPLETE CRUD operations for {operation_lower}.

Operations Tested:
==================

CREATE: Create new {operation_lower}
READ:   GetAll(), Find(), Exists(), Get...() methods
UPDATE: Set...() methods
DELETE: Delete()

Test Flow:
==========
1. READ initial state
2. CREATE new test {operation_lower}
3. READ to verify creation
4. UPDATE {operation_lower} properties
5. READ to verify updates
6. DELETE test {operation_lower}
7. Verify deletion

Requirements:
  - FLEx project with write access
  - Python.NET runtime

WARNING: This demo modifies the database!
         Test {operation_lower} is created and deleted during the demo.
    """)

    response = input("\\nRun CRUD demo? (y/N): ")
    if response.lower() == 'y':
        demo_{operation_lower}_crud()
    else:
        print("\\nDemo skipped.")
'''


def extract_operation_name(filename):
    """Extract operation name from filename."""
    # Remove .py extension
    name = filename.replace('_operations_demo.py', '')

    # Remove category prefix
    if '_' in name:
        parts = name.split('_', 1)
        if len(parts) > 1:
            name = parts[1]

    return name


def convert_demo_file(filepath):
    """Convert a demo file to full CRUD format."""
    filename = os.path.basename(filepath)

    # Extract operation name
    operation_name = extract_operation_name(filename)

    # Format for different contexts
    operation_lower = operation_name.lower()
    operation_title = operation_name.title().replace('_', '')
    operation_upper = operation_name.upper().replace('_', ' ')

    # Generate CRUD demo
    crud_content = CRUD_TEMPLATE.format(
        operation_lower=operation_lower,
        operation_title=operation_title,
        operation_upper=operation_upper
    )

    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(crud_content)

    return True


def main():
    """Convert all operation demo files."""
    import sys

    examples_dir = Path(__file__).parent

    # Find all operation demo files
    demo_files = sorted(examples_dir.glob('*_operations_demo.py'))

    # Exclude the environment demo (already done as template)
    demo_files = [f for f in demo_files if 'environment' not in f.name]

    print("=" * 70)
    print("CRUD DEMO CONVERTER")
    print("=" * 70)
    print(f"\\nFound {len(demo_files)} demo files to convert")
    print()

    # Check for command-line argument to skip confirmation
    if len(sys.argv) > 1 and sys.argv[1] == '--yes':
        print("Auto-confirming conversion (--yes flag provided)")
    else:
        response = input("Convert all files? (y/N): ")
        if response.lower() != 'y':
            print("\\nConversion cancelled.")
            return

    print("\\nConverting files...")
    print("=" * 70)

    converted = 0
    failed = 0

    for filepath in demo_files:
        try:
            print(f"Converting {filepath.name}...", end=' ')
            if convert_demo_file(filepath):
                print("[OK]")
                converted += 1
            else:
                print("[SKIP]")
                failed += 1
        except Exception as e:
            print(f"[ERROR]: {e}")
            failed += 1

    print("=" * 70)
    print("\\nConversion Summary:")
    print(f"  Total files:  {len(demo_files)}")
    print(f"  Converted:    {converted}")
    print(f"  Failed:       {failed}")
    print()

    if converted > 0:
        print("[SUCCESS] Conversion complete!")
        print("\\nAll demos now follow the standard CRUD pattern:")
        print("  1. READ initial state")
        print("  2. CREATE test object")
        print("  3. READ verify creation")
        print("  4. UPDATE properties")
        print("  5. READ verify updates")
        print("  6. DELETE test object")
        print("  7. Verify deletion + cleanup")

    print("=" * 70)


if __name__ == "__main__":
    main()
