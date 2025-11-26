#!/usr/bin/env python3
"""
Demonstration of POSOperations for flexlibs

This script demonstrates the comprehensive POSOperations class
for managing Parts of Speech in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_pos_operations():
    """Demonstrate POSOperations functionality."""

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
    print("POSOperations Demonstration")
    print("=" * 60)

    # --- 1. GetAll - List all parts of speech ---
    print("\n1. Getting all parts of speech:")
    try:
        count = 0
        for pos in project.POS.GetAll():
            name = project.POS.GetName(pos)
            abbr = project.POS.GetAbbreviation(pos)
            try:
                print(f"   {name} ({abbr})")
            except UnicodeEncodeError:
                print(f"   [Unicode POS] ({abbr})")
            count += 1
            if count >= 5:  # Show first 5 only
                print("   ...")
                break
        print(f"   Total POS categories shown: {count}")
    except Exception as e:
        print(f"   ERROR in GetAll: {e}")

    # --- 2. Create - Create a new POS ---
    print("\n2. Creating a new part of speech:")
    try:
        if not project.POS.Exists("Verb"):
            verb = project.POS.Create("Verb", "V")
            print(f"   Created POS: {project.POS.GetName(verb)} ({project.POS.GetAbbreviation(verb)})")
        else:
            print("   'Verb' already exists")
            verb = project.POS.Find("Verb")
    except Exception as e:
        print(f"   ERROR in Create: {e}")
        verb = None

    # --- 3. Find - Find a POS by name ---
    print("\n3. Finding parts of speech:")
    try:
        found_verb = project.POS.Find("Verb")
        if found_verb:
            print(f"   Found: {project.POS.GetName(found_verb)}")
            print(f"   Abbreviation: {project.POS.GetAbbreviation(found_verb)}")
    except Exception as e:
        print(f"   ERROR in Find: {e}")

    # --- 4. Exists - Check existence ---
    print("\n4. Checking existence:")
    try:
        print(f"   'Verb' exists: {project.POS.Exists('Verb')}")
        print(f"   'Superlative' exists: {project.POS.Exists('Superlative')}")
    except Exception as e:
        print(f"   ERROR in Exists: {e}")

    # --- 5. Create additional POS for testing ---
    print("\n5. Creating additional parts of speech:")
    noun = None
    adjective = None
    try:
        if not project.POS.Exists("Noun"):
            noun = project.POS.Create("Noun", "N", "GOLD:Noun")
            print(f"   Created: {project.POS.GetName(noun)} ({project.POS.GetAbbreviation(noun)})")
            catalog_id = project.POS.GetCatalogSourceId(noun)
            if catalog_id:
                print(f"   Catalog ID: {catalog_id}")
        else:
            noun = project.POS.Find("Noun")
            print(f"   'Noun' already exists")

        if not project.POS.Exists("Adjective"):
            adjective = project.POS.Create("Adjective", "Adj")
            print(f"   Created: {project.POS.GetName(adjective)} ({project.POS.GetAbbreviation(adjective)})")
        else:
            adjective = project.POS.Find("Adjective")
            print(f"   'Adjective' already exists")
    except Exception as e:
        print(f"   ERROR in Create: {e}")

    # --- 6. SetName - Update POS name ---
    print("\n6. Updating POS name:")
    try:
        if adjective:
            original_name = project.POS.GetName(adjective)
            # Don't actually change it, just demonstrate
            print(f"   Current name: {original_name}")
            print(f"   (SetName available but not demonstrated to preserve data)")
    except Exception as e:
        print(f"   ERROR in SetName: {e}")

    # --- 7. SetAbbreviation - Update abbreviation ---
    print("\n7. Updating POS abbreviation:")
    try:
        if adjective:
            original_abbr = project.POS.GetAbbreviation(adjective)
            print(f"   Current abbreviation: {original_abbr}")
            # Test by setting to same value
            project.POS.SetAbbreviation(adjective, original_abbr)
            print(f"   Abbreviation preserved: {project.POS.GetAbbreviation(adjective)}")
    except Exception as e:
        print(f"   ERROR in SetAbbreviation: {e}")

    # --- 8. Subcategories - Add and retrieve subcategories ---
    print("\n8. Working with subcategories:")
    try:
        if noun:
            # Check existing subcategories
            subcats = project.POS.GetSubcategories(noun)
            print(f"   Current subcategories of 'Noun': {len(subcats)}")

            # Add a subcategory if it doesn't exist
            has_proper = False
            for subcat in subcats:
                subcat_name = project.POS.GetName(subcat)
                if subcat_name.lower() == "proper noun":
                    has_proper = True
                    print(f"   Found subcategory: {subcat_name}")

            if not has_proper:
                proper_noun = project.POS.AddSubcategory(noun, "Proper Noun", "PN")
                print(f"   Added subcategory: {project.POS.GetName(proper_noun)} ({project.POS.GetAbbreviation(proper_noun)})")

            # List all subcategories
            subcats = project.POS.GetSubcategories(noun)
            print(f"   Total subcategories: {len(subcats)}")
            for subcat in subcats[:3]:  # Show first 3
                try:
                    print(f"     - {project.POS.GetName(subcat)} ({project.POS.GetAbbreviation(subcat)})")
                except UnicodeEncodeError:
                    print(f"     - [Unicode subcategory]")
    except Exception as e:
        print(f"   ERROR in Subcategories: {e}")

    # --- 9. GetCatalogSourceId - Retrieve catalog ID ---
    print("\n9. Catalog source IDs:")
    try:
        if noun:
            catalog_id = project.POS.GetCatalogSourceId(noun)
            if catalog_id:
                print(f"   Noun catalog ID: {catalog_id}")
            else:
                print(f"   Noun has no catalog ID")

        if verb:
            catalog_id = project.POS.GetCatalogSourceId(verb)
            if catalog_id:
                print(f"   Verb catalog ID: {catalog_id}")
            else:
                print(f"   Verb has no catalog ID")
    except Exception as e:
        print(f"   ERROR in GetCatalogSourceId: {e}")

    # --- 10. GetInflectionClasses - Get inflection classes ---
    print("\n10. Inflection classes:")
    try:
        if verb:
            infl_classes = project.POS.GetInflectionClasses(verb)
            print(f"   Verb inflection classes: {len(infl_classes)}")
            for infl_class in infl_classes[:3]:  # Show first 3
                try:
                    print(f"     - {infl_class.Name}")
                except:
                    print(f"     - [Cannot display name]")
    except Exception as e:
        print(f"   ERROR in GetInflectionClasses: {e}")

    # --- 11. GetAffixSlots - Get affix slots ---
    print("\n11. Affix slots:")
    try:
        if verb:
            slots = project.POS.GetAffixSlots(verb)
            print(f"   Verb affix slots: {len(slots)}")
            for slot in slots[:3]:  # Show first 3
                try:
                    print(f"     - {slot.Name}")
                except:
                    print(f"     - [Cannot display name]")
    except Exception as e:
        print(f"   ERROR in GetAffixSlots: {e}")

    # --- 12. GetEntryCount - Count entries using this POS ---
    print("\n12. Entry counts:")
    try:
        if noun:
            count = project.POS.GetEntryCount(noun)
            print(f"   Entries using 'Noun': {count}")

        if verb:
            count = project.POS.GetEntryCount(verb)
            print(f"   Entries using 'Verb': {count}")
    except Exception as e:
        print(f"   ERROR in GetEntryCount: {e}")

    # --- 13. Cleanup demonstration ---
    print("\n13. Cleanup (optional):")
    print("   (Demo preserves all created POS - they can be deleted manually)")
    # Uncomment to test deletion:
    # try:
    #     if adjective and project.POS.GetEntryCount(adjective) == 0:
    #         project.POS.Delete(adjective)
    #         print("   Deleted 'Adjective'")
    # except Exception as e:
    #     print(f"   ERROR in Delete: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    print("""
POSOperations Demo
==================

This demonstrates the comprehensive POSOperations class with 18 methods:

Core CRUD Operations:
  - GetAll()              - Iterate all parts of speech
  - Create()              - Create new POS with name, abbreviation, catalog ID
  - Delete()              - Remove a POS
  - Exists()              - Check if POS exists
  - Find()                - Find POS by name

Properties:
  - GetName()             - Get POS name
  - SetName()             - Set POS name
  - GetAbbreviation()     - Get POS abbreviation
  - SetAbbreviation()     - Set POS abbreviation
  - GetCatalogSourceId()  - Get catalog source ID (e.g., GOLD:Noun)

Hierarchy:
  - GetSubcategories()    - Get all subcategories
  - AddSubcategory()      - Add a subcategory
  - RemoveSubcategory()   - Remove a subcategory

Morphology:
  - GetInflectionClasses() - Get inflection classes for this POS
  - GetAffixSlots()        - Get affix slots for this POS

Usage:
  - GetEntryCount()       - Count lexical entries using this POS

Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_pos_operations()
