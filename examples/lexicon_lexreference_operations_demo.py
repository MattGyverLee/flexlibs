#!/usr/bin/env python3
"""
Demonstration of LexReferenceOperations for flexlibs

This script demonstrates the comprehensive LexReferenceOperations class
for managing lexical references in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_lexreference_operations():
    """Demonstrate LexReferenceOperations functionality."""

    # Initialize FieldWorks
    FLExInitialize()

    # Open project
    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("LexReferenceOperations Demonstration")
    print("=" * 60)

    # --- Test all methods ---
    print("\n1. Testing GetAll (if available):")
    try:
        if hasattr(project.LexReferences, 'GetAll'):
            count = 0
            for item in project.LexReferences.GetAll():
                count += 1
                if count >= 5:
                    print(f"   ... (showing first 5 of {count}+ items)")
                    break
            print(f"   Total items: {count}")
        else:
            print("   GetAll method not available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n2. Testing Create (if available):")
    try:
        if hasattr(project.LexReferences, 'Create'):
            print("   Create method available (not tested to preserve data)")
        else:
            print("   Create method not available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n3. Testing Find/Exists (if available):")
    try:
        if hasattr(project.LexReferences, 'Find'):
            print("   Find method available")
        if hasattr(project.LexReferences, 'Exists'):
            print("   Exists method available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n4. Available methods in LexReferenceOperations:")
    methods = ['AddTarget', 'Create', 'CreateType', 'Delete', 'DeleteType', 'FindType', 'GetAll', 'GetAllTypes', 'GetComplexFormEntries', 'GetComponentEntries', 'GetMappingType', 'GetReferencesOfType', 'GetTargets', 'GetType', 'GetTypeName', 'GetTypeReverseName', 'RemoveTarget', 'SetTypeName', 'SetTypeReverseName', 'ShowComplexFormsIn']
    for method in methods[:10]:  # Show first 10
        print(f"   - {method}()")
    if len(methods) > 10:
        print(f"   ... and {len(methods) - 10} more")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    print("""
LexReferenceOperations Demo
============================

This demonstrates the LexReferenceOperations class.

Available methods (20 total):

Create operations (3):
  - AddTarget()
  - Create()
  - CreateType()


Read operations (10):
  - GetAll()
  - GetAllTypes()
  - GetComplexFormEntries()
  - GetComponentEntries()
  - GetMappingType()
  ...

Update operations (2):
  - SetTypeName()
  - SetTypeReverseName()


Delete operations (3):
  - Delete()
  - DeleteType()
  - RemoveTarget()


Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_lexreference_operations()
