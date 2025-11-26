#!/usr/bin/env python3
"""
Demonstration of LexSenseOperations for flexlibs

This script demonstrates the comprehensive LexSenseOperations class
for managing lexical senses in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_sense_operations():
    """Demonstrate LexSenseOperations functionality."""

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
    print("LexSenseOperations Demonstration")
    print("=" * 60)

    # --- Test all methods ---
    print("\n1. Testing GetAll (if available):")
    try:
        if hasattr(project.Senses, 'GetAll'):
            count = 0
            for item in project.Senses.GetAll():
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
        if hasattr(project.Senses, 'Create'):
            print("   Create method available (not tested to preserve data)")
        else:
            print("   Create method not available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n3. Testing Find/Exists (if available):")
    try:
        if hasattr(project.Senses, 'Find'):
            print("   Find method available")
        if hasattr(project.Senses, 'Exists'):
            print("   Exists method available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n4. Available methods in LexSenseOperations:")
    methods = ['AddExample', 'AddSemanticDomain', 'Create', 'CreateSubsense', 'Delete', 'GetAll', 'GetAnalysesCount', 'GetDefinition', 'GetExampleCount', 'GetExamples', 'GetGloss', 'GetGrammaticalInfo', 'GetGuid', 'GetOwningEntry', 'GetParentSense', 'GetPartOfSpeech', 'GetPictureCount', 'GetPictures', 'GetReversalCount', 'GetReversalEntries', 'GetSemanticDomains', 'GetSenseNumber', 'GetSenseType', 'GetStatus', 'GetSubsenses', 'RemoveSemanticDomain', 'Reorder', 'SetDefinition', 'SetGloss', 'SetGrammaticalInfo', 'SetPartOfSpeech', 'SetSenseType', 'SetStatus']
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
LexSenseOperations Demo
========================

This demonstrates the LexSenseOperations class.

Available methods (33 total):

Create operations (4):
  - AddExample()
  - AddSemanticDomain()
  - Create()
  - CreateSubsense()


Read operations (20):
  - GetAll()
  - GetAnalysesCount()
  - GetDefinition()
  - GetExampleCount()
  - GetExamples()
  ...

Update operations (6):
  - SetDefinition()
  - SetGloss()
  - SetGrammaticalInfo()
  - SetPartOfSpeech()
  - SetSenseType()
  ...

Delete operations (2):
  - Delete()
  - RemoveSemanticDomain()


Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_sense_operations()
