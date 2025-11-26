#!/usr/bin/env python3
"""
Demonstration of MorphRuleOperations for flexlibs

This script demonstrates the MorphRuleOperations class for managing
morphological rules in a FLEx project.

**WARNING**: This Operations class has a critical import error and cannot be tested.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_morphrule_operations():
    """Demonstrate MorphRuleOperations functionality."""

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
    print("MorphRuleOperations Demonstration")
    print("=" * 60)

    print("\n**IMPORT ERROR DETECTED**")
    print("MorphRuleOperations.py has a critical import error:")
    print("  ImportError: cannot import name 'IMoMorphRule' from 'SIL.LCModel'")
    print("\nThis Operations class cannot be tested until the import is fixed.")
    print("The interface 'IMoMorphRule' may not exist in the FLEx LCM API,")
    print("or may have been renamed in newer versions of FieldWorks.")

    print("\n" + "=" * 60)
    print("Demonstration incomplete due to import error")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    print("""
MorphRuleOperations Demo
========================

**CRITICAL BUG**: This Operations class cannot be imported due to missing interface.

Error:
  ImportError: cannot import name 'IMoMorphRule' from 'SIL.LCModel'
  (Did you mean: 'IMoMorphType'?)

Location:
  D:\\Github\\flexlibs\\flexlibs\\code\\Grammar\\MorphRuleOperations.py
  Line 18: from SIL.LCModel import IMoMorphRule

This demo cannot be run until the import error is fixed.

See AGENT1_BUGS.md for full bug report.
    """)
    demo_morphrule_operations()
