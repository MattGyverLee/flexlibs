#!/usr/bin/env python3
"""
Demonstration of NaturalClassOperations for flexlibs

This script demonstrates the comprehensive NaturalClassOperations class
for managing natural classes in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_naturalclass_operations():
    """Demonstrate NaturalClassOperations functionality."""

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
    print("NaturalClassOperations Demonstration")
    print("=" * 60)

    # --- Test all methods ---
    print("\n1. Testing GetAll (if available):")
    try:
        if hasattr(project.NaturalClasses, 'GetAll'):
            count = 0
            for item in project.NaturalClasses.GetAll():
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
        if hasattr(project.NaturalClasses, 'Create'):
            print("   Create method available (not tested to preserve data)")
        else:
            print("   Create method not available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n3. Testing Find/Exists (if available):")
    try:
        if hasattr(project.NaturalClasses, 'Find'):
            print("   Find method available")
        if hasattr(project.NaturalClasses, 'Exists'):
            print("   Exists method available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n4. Available methods in NaturalClassOperations:")
    methods = ['AddPhoneme', 'Create', 'Delete', 'GetAbbreviation', 'GetAll', 'GetName', 'GetPhonemes', 'RemovePhoneme', 'SetName']
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
NaturalClassOperations Demo
============================

This demonstrates the NaturalClassOperations class.

Available methods (9 total):

Create operations (2):
  - AddPhoneme()
  - Create()


Read operations (4):
  - GetAbbreviation()
  - GetAll()
  - GetName()
  - GetPhonemes()


Update operations (1):
  - SetName()


Delete operations (2):
  - Delete()
  - RemovePhoneme()


Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_naturalclass_operations()
