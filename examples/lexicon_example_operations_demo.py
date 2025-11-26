#!/usr/bin/env python3
"""
Demonstration of ExampleOperations for flexlibs

This script demonstrates the comprehensive ExampleOperations class
for managing example sentences in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_example_operations():
    """Demonstrate ExampleOperations functionality."""

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
    print("ExampleOperations Demonstration")
    print("=" * 60)

    # --- Test all methods ---
    print("\n1. Testing GetAll (if available):")
    try:
        if hasattr(project.Examples, 'GetAll'):
            count = 0
            for item in project.Examples.GetAll():
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
        if hasattr(project.Examples, 'Create'):
            print("   Create method available (not tested to preserve data)")
        else:
            print("   Create method not available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n3. Testing Find/Exists (if available):")
    try:
        if hasattr(project.Examples, 'Find'):
            print("   Find method available")
        if hasattr(project.Examples, 'Exists'):
            print("   Exists method available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n4. Available methods in ExampleOperations:")
    methods = ['AddTranslation', 'Create', 'Delete', 'GetAll', 'GetExample', 'GetGuid', 'GetMediaCount', 'GetMediaFiles', 'GetOwningSense', 'GetReference', 'GetTranslation', 'GetTranslations', 'RemoveTranslation', 'Reorder', 'SetExample', 'SetReference', 'SetTranslation']
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
ExampleOperations Demo
=======================

This demonstrates the ExampleOperations class.

Available methods (17 total):

Create operations (2):
  - AddTranslation()
  - Create()


Read operations (9):
  - GetAll()
  - GetExample()
  - GetGuid()
  - GetMediaCount()
  - GetMediaFiles()
  ...

Update operations (3):
  - SetExample()
  - SetReference()
  - SetTranslation()


Delete operations (2):
  - Delete()
  - RemoveTranslation()


Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_example_operations()
