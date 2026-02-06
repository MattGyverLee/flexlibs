#!/usr/bin/env python3
"""
Check if a FLEx Collection is Safe to Reorder

Determines whether a collection is:
- OS (Owning Sequence) - Order matters, DON'T sort
- OC (Owning Collection) - Unordered, safe to sort
- RC (Reference Collection) - References, usually safe
- RA (Reference Atomic) - Single reference, N/A

Author: FlexTools Development Team
Date: 2025-12-04
"""

from flexlibs2 import FLExProject, FLExInitialize, FLExCleanup

def check_property_type(obj, property_name):
    """
    Check if a property is a sequence (ordered) or collection (unordered).

    Args:
        obj: The FLEx object
        property_name: Name of the property to check

    Returns:
        str: Type of collection (OS, OC, RC, RA, or Unknown)
    """
    prop_info = obj.GetType().GetProperty(property_name)
    if not prop_info:
        return "Unknown"

    prop_type_name = prop_info.PropertyType.Name

    if "Sequence" in prop_type_name or property_name.endswith("OS"):
        return "OS (Owning Sequence) - ORDER MATTERS - DON'T SORT!"
    elif "Collection" in property_name or property_name.endswith("OC"):
        return "OC (Owning Collection) - Unordered - Safe to sort"
    elif property_name.endswith("RC"):
        return "RC (Reference Collection) - Usually safe to sort"
    elif property_name.endswith("RA"):
        return "RA (Reference Atomic) - Single reference, not sortable"
    else:
        return f"Unknown type: {prop_type_name}"


def demo_safety_check():
    """Demonstrate checking collection types for safety."""

    print("="*70)
    print("FLEX COLLECTION SAFETY CHECKER")
    print("="*70)

    FLExInitialize()
    project = FLExProject()

    try:
        project.OpenProject("Sena 3", writeEnabled=False)

        # Get a sample entry to check
        entries = list(project.LexEntry.GetAll())
        if not entries:
            print("No entries found in project")
            return

        entry = entries[0]

        print("\nChecking common FLEx collections:")
        print("-"*70)

        # Check various collection types
        collections_to_check = [
            ("SensesOS", entry),
            ("AlternateFormsOS", entry),
            # Can add more as needed
        ]

        for prop_name, obj in collections_to_check:
            if hasattr(obj, prop_name):
                result = check_property_type(obj, prop_name)
                print(f"\n{prop_name}:")
                print(f"  {result}")

                # Show example
                collection = getattr(obj, prop_name)
                if collection and collection.Count > 0:
                    print(f"  Count: {collection.Count} items")
                    if "DON'T SORT" in result:
                        print(f"  ⚠️  WARNING: Reordering will change meaning!")
                    else:
                        print(f"  ✅ Safe to reorder if needed")

        print("\n" + "="*70)
        print("GENERAL RULES:")
        print("="*70)
        print()
        print("✅ SAFE to sort (OC - Owning Collections):")
        print("  - Lexicon entries (unordered database)")
        print("  - Texts (unordered corpus)")
        print("  - Custom lists")
        print()
        print("❌ NEVER sort (OS - Owning Sequences):")
        print("  - Senses on an entry (ordered by importance)")
        print("  - Allomorphs on an entry (default first)")
        print("  - Paragraphs in a text (narrative order)")
        print("  - Morphemes in an analysis (morpheme order)")
        print("  - Examples on a sense (ordered by preference)")
        print()
        print("💡 TIP: Property names ending in 'OS' are sequences")
        print("        Property names ending in 'OC' are collections")
        print()

    finally:
        project.CloseProject()
        FLExCleanup()


if __name__ == "__main__":
    demo_safety_check()
