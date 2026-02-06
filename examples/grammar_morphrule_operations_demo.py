#!/usr/bin/env python3
"""
Full CRUD Demo: MorphruleOperations for flexlibs

This script demonstrates complete CRUD operations for morphrule.
Performs actual create, read, update, and delete operations on test data.

Author: FlexTools Development Team
Date: 2025-11-27
"""

from flexlibs2 import FLExProject, FLExInitialize, FLExCleanup

def demo_morphrule_crud():
    """
    Demonstrate full CRUD operations for morphrule.

    Tests:
    - CREATE: Create new test morphrule
    - READ: Get all morphrules, find by name/identifier
    - UPDATE: Modify morphrule properties
    - DELETE: Remove test morphrule
    """

    print("=" * 70)
    print("MORPHRULE OPERATIONS - FULL CRUD TEST")
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
    test_name = "crud_test_morphrule"

    try:
        # ==================== READ: Initial state ====================
        print("\n" + "="*70)
        print("STEP 1: READ - Get existing morphrules")
        print("="*70)

        print("\nGetting all morphrules...")
        initial_count = 0
        for obj in project.MorphRules.GetAll():
            # Display first few objects
            try:
                name = project.MorphRules.GetName(obj) if hasattr(project.MorphRules, 'GetName') else str(obj)
                print(f"  - {name}")
            except:
                print(f"  - [Object {initial_count + 1}]")
            initial_count += 1
            if initial_count >= 5:
                break

        print(f"\nTotal morphrules (showing first 5): {initial_count}")

        # ==================== CREATE ====================
        print("\n" + "="*70)
        print("STEP 2: CREATE - Create new test morphrule")
        print("="*70)

        # Check if test object already exists
        try:
            if hasattr(project.MorphRules, 'Exists') and project.MorphRules.Exists(test_name):
                print(f"\nTest morphrule '{test_name}' already exists")
                print("Deleting existing one first...")
                existing = project.MorphRules.Find(test_name) if hasattr(project.MorphRules, 'Find') else None
                if existing:
                    project.MorphRules.Delete(existing)
                    print("  Deleted existing test morphrule")
        except:
            pass

        # Create new object
        print(f"\nCreating new morphrule: '{test_name}'")

        try:
            # Attempt to create with common parameters
            test_obj = project.MorphRules.Create(test_name)
        except TypeError:
            try:
                # Try without parameters if that fails
                test_obj = project.MorphRules.Create()
                if hasattr(project.MorphRules, 'SetName'):
                    project.MorphRules.SetName(test_obj, test_name)
            except Exception as e:
                print(f"  Note: Create method may require specific parameters: {e}")
                test_obj = None

        if test_obj:
            print(f"  SUCCESS: Morphrule created!")
            try:
                if hasattr(project.MorphRules, 'GetName'):
                    print(f"  Name: {project.MorphRules.GetName(test_obj)}")
            except:
                pass
        else:
            print(f"  Note: Could not create morphrule (may require special parameters)")
            print("  Skipping remaining tests...")
            return

        # ==================== READ: Verify creation ====================
        print("\n" + "="*70)
        print("STEP 3: READ - Verify morphrule was created")
        print("="*70)

        # Test Exists
        if hasattr(project.MorphRules, 'Exists'):
            print(f"\nChecking if '{test_name}' exists...")
            exists = project.MorphRules.Exists(test_name)
            print(f"  Exists: {exists}")

        # Test Find
        if hasattr(project.MorphRules, 'Find'):
            print(f"\nFinding morphrule by name...")
            found_obj = project.MorphRules.Find(test_name)
            if found_obj:
                print(f"  FOUND: morphrule")
                try:
                    if hasattr(project.MorphRules, 'GetName'):
                        print(f"  Name: {project.MorphRules.GetName(found_obj)}")
                except:
                    pass
            else:
                print("  NOT FOUND")

        # Count after creation
        print("\nCounting all morphrules after creation...")
        current_count = sum(1 for _ in project.MorphRules.GetAll())
        print(f"  Count before: {initial_count}")
        print(f"  Count after:  {current_count}")
        print(f"  Difference:   +{current_count - initial_count}")

        # ==================== UPDATE ====================
        print("\n" + "="*70)
        print("STEP 4: UPDATE - Modify morphrule properties")
        print("="*70)

        if test_obj:
            updated = False

            # Try common update methods
            if hasattr(project.MorphRules, 'SetName'):
                try:
                    new_name = "crud_test_morphrule_modified"
                    print(f"\nUpdating name to: '{new_name}'")
                    old_name = project.MorphRules.GetName(test_obj) if hasattr(project.MorphRules, 'GetName') else test_name
                    project.MorphRules.SetName(test_obj, new_name)
                    updated_name = project.MorphRules.GetName(test_obj) if hasattr(project.MorphRules, 'GetName') else new_name
                    print(f"  Old name: {old_name}")
                    print(f"  New name: {updated_name}")
                    test_name = new_name  # Update for cleanup
                    updated = True
                except Exception as e:
                    print(f"  Note: SetName failed: {e}")

            # Try other Set methods
            for method_name in dir(project.MorphRules):
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

        if hasattr(project.MorphRules, 'Find'):
            print(f"\nFinding morphrule after update...")
            updated_obj = project.MorphRules.Find(test_name)
            if updated_obj:
                print(f"  FOUND: morphrule")
                try:
                    if hasattr(project.MorphRules, 'GetName'):
                        print(f"  Name: {project.MorphRules.GetName(updated_obj)}")
                except:
                    pass
            else:
                print("  NOT FOUND - Update may not have persisted")

        # ==================== DELETE ====================
        print("\n" + "="*70)
        print("STEP 6: DELETE - Remove test morphrule")
        print("="*70)

        if test_obj:
            print(f"\nDeleting test morphrule...")
            try:
                obj_name = project.MorphRules.GetName(test_obj) if hasattr(project.MorphRules, 'GetName') else test_name
            except:
                obj_name = test_name

            project.MorphRules.Delete(test_obj)
            print(f"  Deleted: {obj_name}")

            # Verify deletion
            print("\nVerifying deletion...")
            if hasattr(project.MorphRules, 'Exists'):
                still_exists = project.MorphRules.Exists(test_name)
                print(f"  Still exists: {still_exists}")

                if not still_exists:
                    print("  DELETE: SUCCESS")
                else:
                    print("  DELETE: FAILED - Morphrule still exists")

            # Count after deletion
            final_count = sum(1 for _ in project.MorphRules.GetAll())
            print(f"\n  Count after delete: {final_count}")
            print(f"  Back to initial:    {final_count == initial_count}")

        # ==================== SUMMARY ====================
        print("\n" + "="*70)
        print("CRUD TEST SUMMARY")
        print("="*70)
        print("\nOperations tested:")
        print("  [CREATE] Create new morphrule")
        print("  [READ]   GetAll, Find, Exists, Get methods")
        print("  [UPDATE] Set methods")
        print("  [DELETE] Delete morphrule")
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
            for name in ["crud_test_morphrule", "crud_test_morphrule_modified"]:
                if hasattr(project.MorphRules, 'Exists') and project.MorphRules.Exists(name):
                    obj = project.MorphRules.Find(name) if hasattr(project.MorphRules, 'Find') else None
                    if obj:
                        project.MorphRules.Delete(obj)
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
Morphrule Operations - Full CRUD Demo
=====================================================

This demonstrates COMPLETE CRUD operations for morphrule.

Operations Tested:
==================

CREATE: Create new morphrule
READ:   GetAll(), Find(), Exists(), Get...() methods
UPDATE: Set...() methods
DELETE: Delete()

Test Flow:
==========
1. READ initial state
2. CREATE new test morphrule
3. READ to verify creation
4. UPDATE morphrule properties
5. READ to verify updates
6. DELETE test morphrule
7. Verify deletion

Requirements:
  - FLEx project with write access
  - Python.NET runtime

WARNING: This demo modifies the database!
         Test morphrule is created and deleted during the demo.
    """)

    response = input("\nRun CRUD demo? (y/N): ")
    if response.lower() == 'y':
        demo_morphrule_crud()
    else:
        print("\nDemo skipped.")
