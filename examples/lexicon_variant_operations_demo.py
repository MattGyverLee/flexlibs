#!/usr/bin/env python3
"""
Demonstration of VariantOperations for flexlibs

This script demonstrates the comprehensive VariantOperations class
for managing variant forms in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_variant_operations():
    """Demonstrate VariantOperations functionality."""

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
    print("VariantOperations Demonstration")
    print("=" * 60)

    # --- Test all methods ---
    print("\n1. Testing GetAll (if available):")
    try:
        if hasattr(project.Variants, 'GetAll'):
            count = 0
            for item in project.Variants.GetAll():
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
        if hasattr(project.Variants, 'Create'):
            print("   Create method available (not tested to preserve data)")
        else:
            print("   Create method not available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n3. Testing Find/Exists (if available):")
    try:
        if hasattr(project.Variants, 'Find'):
            print("   Find method available")
        if hasattr(project.Variants, 'Exists'):
            print("   Exists method available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n4. Available methods in VariantOperations:")
    methods = ['AddComponentLexeme', 'Create', 'Delete', 'FindType', 'GetAll', 'GetAllTypes', 'GetComponentLexemes', 'GetForm', 'GetOwningEntry', 'GetType', 'GetTypeDescription', 'GetTypeName', 'GetVariantCount', 'RemoveComponentLexeme', 'SetForm', 'SetType']
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
VariantOperations Demo
=======================

This demonstrates the VariantOperations class.

Available methods (16 total):

Create operations (2):
  - AddComponentLexeme()
  - Create()


Read operations (9):
  - GetAll()
  - GetAllTypes()
  - GetComponentLexemes()
  - GetForm()
  - GetOwningEntry()
  ...

Update operations (2):
  - SetForm()
  - SetType()


Delete operations (2):
  - Delete()
  - RemoveComponentLexeme()


Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_variant_operations()
