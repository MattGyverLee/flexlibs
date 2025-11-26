#!/usr/bin/env python3
"""
Demonstration of PhonologicalRuleOperations for flexlibs

This script demonstrates the comprehensive PhonologicalRuleOperations class
for managing phonological rules in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_phonrule_operations():
    """Demonstrate PhonologicalRuleOperations functionality."""

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
    print("PhonologicalRuleOperations Demonstration")
    print("=" * 60)

    # --- Test all methods ---
    print("\n1. Testing GetAll (if available):")
    try:
        if hasattr(project.PhonRules, 'GetAll'):
            count = 0
            for item in project.PhonRules.GetAll():
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
        if hasattr(project.PhonRules, 'Create'):
            print("   Create method available (not tested to preserve data)")
        else:
            print("   Create method not available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n3. Testing Find/Exists (if available):")
    try:
        if hasattr(project.PhonRules, 'Find'):
            print("   Find method available")
        if hasattr(project.PhonRules, 'Exists'):
            print("   Exists method available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n4. Available methods in PhonologicalRuleOperations:")
    methods = ['AddInputSegment', 'AddOutputSegment', 'Create', 'Delete', 'Exists', 'Find', 'GetAll', 'GetDescription', 'GetDirection', 'GetName', 'GetStratum', 'SetDescription', 'SetDirection', 'SetLeftContext', 'SetName', 'SetRightContext', 'SetStratum']
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
PhonologicalRuleOperations Demo
================================

This demonstrates the PhonologicalRuleOperations class.

Available methods (17 total):

Create operations (3):
  - AddInputSegment()
  - AddOutputSegment()
  - Create()


Read operations (7):
  - Exists()
  - Find()
  - GetAll()
  - GetDescription()
  - GetDirection()
  ...

Update operations (6):
  - SetDescription()
  - SetDirection()
  - SetLeftContext()
  - SetName()
  - SetRightContext()
  ...

Delete operations (1):
  - Delete()


Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_phonrule_operations()
