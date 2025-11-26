#!/usr/bin/env python3
"""
Demonstration of EtymologyOperations for flexlibs

This script demonstrates the comprehensive EtymologyOperations class
for managing etymologies in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_etymology_operations():
    """Demonstrate EtymologyOperations functionality."""

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
    print("EtymologyOperations Demonstration")
    print("=" * 60)

    # --- Test all methods ---
    print("\n1. Testing GetAll (if available):")
    try:
        if hasattr(project.Etymology, 'GetAll'):
            count = 0
            for item in project.Etymology.GetAll():
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
        if hasattr(project.Etymology, 'Create'):
            print("   Create method available (not tested to preserve data)")
        else:
            print("   Create method not available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n3. Testing Find/Exists (if available):")
    try:
        if hasattr(project.Etymology, 'Find'):
            print("   Find method available")
        if hasattr(project.Etymology, 'Exists'):
            print("   Exists method available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n4. Available methods in EtymologyOperations:")
    methods = ['Create', 'Delete', 'GetAll', 'GetBibliography', 'GetComment', 'GetForm', 'GetGloss', 'GetGuid', 'GetOwningEntry', 'GetSource', 'Reorder', 'SetBibliography', 'SetComment', 'SetForm', 'SetGloss', 'SetSource']
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
EtymologyOperations Demo
=========================

This demonstrates the EtymologyOperations class.

Available methods (16 total):

Create operations (1):
  - Create()


Read operations (8):
  - GetAll()
  - GetBibliography()
  - GetComment()
  - GetForm()
  - GetGloss()
  ...

Update operations (5):
  - SetBibliography()
  - SetComment()
  - SetForm()
  - SetGloss()
  - SetSource()


Delete operations (1):
  - Delete()


Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_etymology_operations()
