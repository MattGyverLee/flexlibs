#!/usr/bin/env python3
"""
Demonstration of PronunciationOperations for flexlibs

This script demonstrates the comprehensive PronunciationOperations class
for managing pronunciations in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_pronunciation_operations():
    """Demonstrate PronunciationOperations functionality."""

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
    print("PronunciationOperations Demonstration")
    print("=" * 60)

    # --- Test all methods ---
    print("\n1. Testing GetAll (if available):")
    try:
        if hasattr(project.Pronunciations, 'GetAll'):
            count = 0
            for item in project.Pronunciations.GetAll():
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
        if hasattr(project.Pronunciations, 'Create'):
            print("   Create method available (not tested to preserve data)")
        else:
            print("   Create method not available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n3. Testing Find/Exists (if available):")
    try:
        if hasattr(project.Pronunciations, 'Find'):
            print("   Find method available")
        if hasattr(project.Pronunciations, 'Exists'):
            print("   Exists method available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n4. Available methods in PronunciationOperations:")
    methods = ['AddMediaFile', 'Create', 'Delete', 'GetAll', 'GetForm', 'GetGuid', 'GetLocation', 'GetMediaCount', 'GetMediaFiles', 'GetOwningEntry', 'RemoveMediaFile', 'Reorder', 'SetForm', 'SetLocation']
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
PronunciationOperations Demo
=============================

This demonstrates the PronunciationOperations class.

Available methods (14 total):

Create operations (2):
  - AddMediaFile()
  - Create()


Read operations (7):
  - GetAll()
  - GetForm()
  - GetGuid()
  - GetLocation()
  - GetMediaCount()
  ...

Update operations (2):
  - SetForm()
  - SetLocation()


Delete operations (2):
  - Delete()
  - RemoveMediaFile()


Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_pronunciation_operations()
