#!/usr/bin/env python3
"""
Demonstration of InflectionFeatureOperations for flexlibs

This script demonstrates the comprehensive InflectionFeatureOperations class
for managing inflection features in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_inflection_operations():
    """Demonstrate InflectionFeatureOperations functionality."""

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
    print("InflectionFeatureOperations Demonstration")
    print("=" * 60)

    # --- Test all methods ---
    print("\n1. Testing GetAll (if available):")
    try:
        if hasattr(project.InflectionFeatures, 'GetAll'):
            count = 0
            for item in project.InflectionFeatures.GetAll():
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
        if hasattr(project.InflectionFeatures, 'Create'):
            print("   Create method available (not tested to preserve data)")
        else:
            print("   Create method not available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n3. Testing Find/Exists (if available):")
    try:
        if hasattr(project.InflectionFeatures, 'Find'):
            print("   Find method available")
        if hasattr(project.InflectionFeatures, 'Exists'):
            print("   Exists method available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n4. Available methods in InflectionFeatureOperations:")
    methods = ['FeatureCreate', 'FeatureDelete', 'FeatureGetAll', 'FeatureGetValues', 'FeatureStructureCreate', 'FeatureStructureDelete', 'FeatureStructureGetAll', 'InflectionClassCreate', 'InflectionClassDelete', 'InflectionClassGetAll', 'InflectionClassGetName', 'InflectionClassSetName']
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
InflectionFeatureOperations Demo
=================================

This demonstrates the InflectionFeatureOperations class.

Available methods (12 total):

Create operations (0):



Read operations (0):



Update operations (0):



Delete operations (0):



Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_inflection_operations()
