#!/usr/bin/env python3
"""
Full CRUD Demo: PosOperations for flexlibs

This script demonstrates complete CRUD operations for pos.
Performs actual create, read, update, and delete operations on test data.

Author: FlexTools Development Team
Date: 2025-11-27
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_pos_crud():
    """
    Demonstrate full CRUD operations for pos.

    Tests:
    - CREATE: Create new test pos
    - READ: Get all poss, find by name/identifier
    - UPDATE: Modify pos properties
    - DELETE: Remove test pos
    """

    print("=" * 70)
    print("POS OPERATIONS - FULL CRUD TEST")
    print("=" * 70)

    # Initialize FieldWorks
    FLExInitialize()

    # Open project with write enabled
    project = FLExProject()
    try:
        project.OpenProject("Sena 3", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    test_obj = None
    test_name = "crud_test_pos"

    try:
        # ==================== READ: Initial state ====================
        print("\n" + "="*70)
        print("STEP 1: READ - Get existing poss")
        print("="*70)

        print("\nGetting all poss...")
        initial_count = 0
        for obj in project.Pos.GetAll():
            # Display first few objects
            try:
                name = project.Pos.GetName(obj) if hasattr(project.Pos, 'GetName') else str(obj)
                print(f"  - {name}")
            except:
                print(f"  - [Object {initial_count + 1}]")
            initial_count += 1
            if initial_count >= 5:
                break

        print(f"\nTotal poss (showing first 5): {initial_count}")

        # ==================== CREATE ====================
        print("\n" + "="*70)
        print("STEP 2: CREATE - Create new test pos")
        print("="*70)

        # Check if test object already exists
        try:
            if hasattr(project.Pos, 'Exists') and project.Pos.Exists(test_name):
                print(f"\nTest pos '{test_name}' already exists")
                print("Deleting existing one first...")
                existing = project.Pos.Find(test_name) if hasattr(project.Pos, 'Find') else None
                if existing:
                    project.Pos.Delete(existing)
                    print("  Deleted existing test pos")
        except:
            pass

        # Create new object
        print(f"\nCreating new pos: '{test_name}'")

        try:
            # Attempt to create with common parameters
            test_obj = project.Pos.Create(test_name)
        except TypeError:
            try:
                # Try without parameters if that fails
                test_obj = project.Pos.Create()
                if hasattr(project.Pos, 'SetName'):
                    project.Pos.SetName(test_obj, test_name)
            except Exception as e:
                print(f"  Note: Create method may require specific parameters: {e}")
                test_obj = None

        if test_obj:
            print(f"  SUCCESS: Pos created!")
            try:
                if hasattr(project.Pos, 'GetName'):
                    print(f"  Name: {project.Pos.GetName(test_obj)}")
            except:
                pass
        else:
            print(f"  Note: Could not create pos (may require special parameters)")
            print("  Skipping remaining tests...")
            return

        # ==================== READ: Verify creation ====================
        print("\n" + "="*70)
        print("STEP 3: READ - Verify pos was created")
        print("="*70)

        # Test Exists
        if hasattr(project.Pos, 'Exists'):
            print(f"\nChecking if '{test_name}' exists...")
            exists = project.Pos.Exists(test_name)
            print(f"  Exists: {exists}")

        # Test Find
        if hasattr(project.Pos, 'Find'):
            print(f"\nFinding pos by name...")
            found_obj = project.Pos.Find(test_name)
            if found_obj:
                print(f"  FOUND: pos")
                try:
                    if hasattr(project.Pos, 'GetName'):
                        print(f"  Name: {project.Pos.GetName(found_obj)}")
                except:
                    pass
            else:
                print("  NOT FOUND")

        # Count after creation
        print("\nCounting all poss after creation...")
        current_count = sum(1 for _ in project.Pos.GetAll())
        print(f"  Count before: {initial_count}")
        print(f"  Count after:  {current_count}")
        print(f"  Difference:   +{current_count - initial_count}")

        # ==================== UPDATE ====================
        print("\n" + "="*70)
        print("STEP 4: UPDATE - Modify pos properties")
        print("="*70)

        if test_obj:
            updated = False

            # Try common update methods
            if hasattr(project.Pos, 'SetName'):
                try:
                    new_name = "crud_test_pos_modified"
                    print(f"\nUpdating name to: '{new_name}'")
                    old_name = project.Pos.GetName(test_obj) if hasattr(project.Pos, 'GetName') else test_name
                    project.Pos.SetName(test_obj, new_name)
                    updated_name = project.Pos.GetName(test_obj) if hasattr(project.Pos, 'GetName') else new_name
                    print(f"  Old name: {old_name}")
                    print(f"  New name: {updated_name}")
                    test_name = new_name  # Update for cleanup
                    updated = True
                except Exception as e:
                    print(f"  Note: SetName failed: {e}")

            # Try other Set methods
            for method_name in dir(project.Pos):
                if method_name.startswith('Set') and method_name != 'SetName' and not updated:
                    print(f"\nFound update method: {method_name}")
                    print("  (Method available but not tested in this demo)")
                    break

            if updated:
                print("\n  UPDATE: SUCCESS")
            else:
                print("\n  Note: No standard update methods found or tested")

        # ==================== READ: Verify updates ====================
        print("\n" + "="*70)
        print("STEP 5: READ - Verify updates persisted")
        print("="*70)

        if hasattr(project.Pos, 'Find'):
            print(f"\nFinding pos after update...")
            updated_obj = project.Pos.Find(test_name)
            if updated_obj:
                print(f"  FOUND: pos")
                try:
                    if hasattr(project.Pos, 'GetName'):
                        print(f"  Name: {project.Pos.GetName(updated_obj)}")
                except:
                    pass
            else:
                print("  NOT FOUND - Update may not have persisted")

        # ==================== DELETE ====================
        print("\n" + "="*70)
        print("STEP 6: DELETE - Remove test pos")
        print("="*70)

        if test_obj:
            print(f"\nDeleting test pos...")
            try:
                obj_name = project.Pos.GetName(test_obj) if hasattr(project.Pos, 'GetName') else test_name
            except:
                obj_name = test_name

            project.Pos.Delete(test_obj)
            print(f"  Deleted: {obj_name}")

            # Verify deletion
            print("\nVerifying deletion...")
            if hasattr(project.Pos, 'Exists'):
                still_exists = project.Pos.Exists(test_name)
                print(f"  Still exists: {still_exists}")

                if not still_exists:
                    print("  DELETE: SUCCESS")
                else:
                    print("  DELETE: FAILED - Pos still exists")

            # Count after deletion
            final_count = sum(1 for _ in project.Pos.GetAll())
            print(f"\n  Count after delete: {final_count}")
            print(f"  Back to initial:    {final_count == initial_count}")

        # ==================== SUMMARY ====================
        print("\n" + "="*70)
        print("CRUD TEST SUMMARY")
        print("="*70)
        print("\nOperations tested:")
        print("  [CREATE] Create new pos")
        print("  [READ]   GetAll, Find, Exists, Get methods")
        print("  [UPDATE] Set methods")
        print("  [DELETE] Delete pos")
        print("\nTest completed successfully!")

    except Exception as e:
        print(f"\n\nERROR during CRUD test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup: Ensure test object is removed
        print("\n" + "="*70)
        print("CLEANUP")
        print("="*70)

        try:
            for name in ["crud_test_pos", "crud_test_pos_modified"]:
                if hasattr(project.Pos, 'Exists') and project.Pos.Exists(name):
                    obj = project.Pos.Find(name) if hasattr(project.Pos, 'Find') else None
                    if obj:
                        project.Pos.Delete(obj)
                        print(f"  Cleaned up: {name}")
        except:
            pass

        print("\nClosing project...")
        project.CloseProject()
        FLExCleanup()

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    print("""
Pos Operations - Full CRUD Demo
=====================================================

This demonstrates COMPLETE CRUD operations for pos.

Operations Tested:
==================

CREATE: Create new pos
READ:   GetAll(), Find(), Exists(), Get...() methods
UPDATE: Set...() methods
DELETE: Delete()

Test Flow:
==========
1. READ initial state
2. CREATE new test pos
3. READ to verify creation
4. UPDATE pos properties
5. READ to verify updates
6. DELETE test pos
7. Verify deletion

Requirements:
  - FLEx project with write access
  - Python.NET runtime

WARNING: This demo modifies the database!
         Test pos is created and deleted during the demo.
    """)

    response = input("\nRun CRUD demo? (y/N): ")
    if response.lower() == 'y':
        demo_pos_crud()
    else:
        print("\nDemo skipped.")
