#!/usr/bin/env python3
"""
Demonstration of TranslationTypeOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_translationtype():
    """Demonstrate TranslationTypeOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("TranslationTypeOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        types = project.TranslationType.GetAll(flat=True)
        count = 0
        for trans_type in types:
            try:
                name = project.TranslationType.GetName(trans_type)
                abbr = project.TranslationType.GetAbbreviation(trans_type)
                info = f"{name} - Abbr: {abbr if abbr else '(none)'}"
                print(f"   Translation Type: {info}")
            except UnicodeEncodeError:
                print(f"   Translation Type: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_name = "Demo Translation Type"
        if not project.TranslationType.Exists(test_name):
            trans_type = project.TranslationType.Create(test_name, "DTT")
            print(f"   Created: {project.TranslationType.GetName(trans_type)}")
        else:
            trans_type = project.TranslationType.Find(test_name)
            print(f"   Translation type already exists: {test_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        trans_type = project.TranslationType.Find("Demo Translation Type")
        if trans_type:
            print(f"   Found by name: {project.TranslationType.GetName(trans_type)}")
            guid = project.TranslationType.GetGuid(trans_type)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        if trans_type:
            # Test abbreviation
            abbr = project.TranslationType.GetAbbreviation(trans_type)
            print(f"   Abbreviation: {abbr}")

            # Test description
            project.TranslationType.SetDescription(trans_type, "Demo translation type for testing")
            desc = project.TranslationType.GetDescription(trans_type)
            print(f"   Description: {desc[:50]}...")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Hierarchy operations
    print("\n5. Testing Hierarchy operations:")
    try:
        if trans_type:
            subtype_name = "Demo Sub-Type"
            existing_subs = [project.TranslationType.GetName(s)
                           for s in project.TranslationType.GetSubitems(trans_type)]
            if subtype_name not in existing_subs:
                subtype = project.TranslationType.CreateSubitem(trans_type, subtype_name, "DST")
                print(f"   Created subitem: {project.TranslationType.GetName(subtype)}")

            subs = project.TranslationType.GetSubitems(trans_type)
            print(f"   Subitems count: {len(subs)}")

            if subs:
                parent = project.TranslationType.GetParent(subs[0])
                if parent:
                    print(f"   Parent of subitem: {project.TranslationType.GetName(parent)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test standard translation types
    print("\n6. Testing standard translation types:")
    try:
        # Common types: Free Translation, Literal Translation, Back Translation
        for name in ["Free Translation", "Literal Translation", "Back Translation"]:
            tt = project.TranslationType.Find(name)
            if tt:
                print(f"   Found standard type: {name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n7. Testing Metadata operations:")
    try:
        if trans_type:
            created = project.TranslationType.GetDateCreated(trans_type)
            modified = project.TranslationType.GetDateModified(trans_type)
            print(f"   Created: {created}")
            print(f"   Modified: {modified}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_translationtype()
