#!/usr/bin/env python3
"""
Demonstration of AnthropologyOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_anthropology():
    """Demonstrate AnthropologyOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("AnthropologyOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        items = project.Anthropology.GetAll(flat=True)
        count = 0
        for item in items:
            try:
                name = project.Anthropology.GetName(item)
                code = project.Anthropology.GetAnthroCode(item)
                info = f"{name} - Code: {code if code else '(none)'}"
                print(f"   Item: {info}")
            except UnicodeEncodeError:
                print(f"   Item: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_name = "Demo_Anthropology_Item"
        if not project.Anthropology.Exists(test_name):
            item = project.Anthropology.Create(test_name, "DEMO", "999")
            print(f"   Created: {project.Anthropology.GetName(item)}")
            print(f"   Code: {project.Anthropology.GetAnthroCode(item)}")
        else:
            item = project.Anthropology.Find(test_name)
            print(f"   Item already exists: {test_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        item = project.Anthropology.Find("Demo_Anthropology_Item")
        if item:
            print(f"   Found by name: {project.Anthropology.GetName(item)}")
            guid = project.Anthropology.GetGuid(item)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        if item:
            project.Anthropology.SetDescription(item, "Demo anthropology item for testing")
            desc = project.Anthropology.GetDescription(item)
            print(f"   Description: {desc[:50]}...")

            # Test abbreviation
            abbr = project.Anthropology.GetAbbreviation(item)
            print(f"   Abbreviation: {abbr}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Hierarchy operations
    print("\n5. Testing Hierarchy operations:")
    try:
        if item:
            subitem_name = "Demo_Sub_Item"
            if not any(project.Anthropology.GetName(s) == subitem_name
                      for s in project.Anthropology.GetSubitems(item)):
                subitem = project.Anthropology.CreateSubitem(item, subitem_name, "SUB")
                print(f"   Created subitem: {project.Anthropology.GetName(subitem)}")

            subs = project.Anthropology.GetSubitems(item)
            print(f"   Subitems count: {len(subs)}")

            if subs:
                parent = project.Anthropology.GetParent(subs[0])
                if parent:
                    print(f"   Parent of subitem: {project.Anthropology.GetName(parent)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test FindByCode operation
    print("\n6. Testing FindByCode operation:")
    try:
        code_item = project.Anthropology.FindByCode("999")
        if code_item:
            print(f"   Found by code: {project.Anthropology.GetName(code_item)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n7. Testing Metadata operations:")
    try:
        if item:
            created = project.Anthropology.GetDateCreated(item)
            modified = project.Anthropology.GetDateModified(item)
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
    demo_anthropology()
