#!/usr/bin/env python3
"""
Demonstration of EnvironmentOperations for flexlibs

This script demonstrates the comprehensive EnvironmentOperations class
for managing environments in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_environment_operations():
    """Demonstrate EnvironmentOperations functionality."""

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
    print("EnvironmentOperations Demonstration")
    print("=" * 60)

    # --- Test all methods ---
    print("\n1. Testing GetAll (if available):")
    try:
        if hasattr(project.Environments, 'GetAll'):
            count = 0
            for item in project.Environments.GetAll():
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
        if hasattr(project.Environments, 'Create'):
            print("   Create method available (not tested to preserve data)")
        else:
            print("   Create method not available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n3. Testing Find/Exists (if available):")
    try:
        if hasattr(project.Environments, 'Find'):
            print("   Find method available")
        if hasattr(project.Environments, 'Exists'):
            print("   Exists method available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n4. Available methods in EnvironmentOperations:")
    methods = ['Create', 'Delete', 'GetAll', 'GetName', 'GetStringRepresentation', 'SetName', 'SetStringRepresentation']
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
EnvironmentOperations Demo
===========================

This demonstrates the EnvironmentOperations class.

Available methods (7 total):

Create operations (1):
  - Create()


Read operations (3):
  - GetAll()
  - GetName()
  - GetStringRepresentation()


Update operations (2):
  - SetName()
  - SetStringRepresentation()


Delete operations (1):
  - Delete()


Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_environment_operations()
