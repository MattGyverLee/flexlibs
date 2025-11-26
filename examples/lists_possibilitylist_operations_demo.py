#!/usr/bin/env python3
"""
Demonstration of PossibilityListOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_possibilitylist():
    """Demonstrate PossibilityListOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("PossibilityListOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        lists = project.PossibilityList.GetAll(flat=True)
        count = 0
        for poss_list in lists:
            try:
                name = project.PossibilityList.GetName(poss_list)
                abbr = project.PossibilityList.GetAbbreviation(poss_list)
                info = f"{name} - Abbr: {abbr if abbr else '(none)'}"
                print(f"   Possibility: {info}")
            except UnicodeEncodeError:
                print(f"   Possibility: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_name = "Demo Possibility"
        if not project.PossibilityList.Exists(test_name):
            possibility = project.PossibilityList.Create(test_name, "DP")
            print(f"   Created: {project.PossibilityList.GetName(possibility)}")
        else:
            possibility = project.PossibilityList.Find(test_name)
            print(f"   Possibility already exists: {test_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        possibility = project.PossibilityList.Find("Demo Possibility")
        if possibility:
            print(f"   Found by name: {project.PossibilityList.GetName(possibility)}")
            guid = project.PossibilityList.GetGuid(possibility)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        if possibility:
            # Test abbreviation
            abbr = project.PossibilityList.GetAbbreviation(possibility)
            print(f"   Abbreviation: {abbr}")

            # Test description
            project.PossibilityList.SetDescription(possibility, "Demo possibility for testing")
            desc = project.PossibilityList.GetDescription(possibility)
            print(f"   Description: {desc[:50]}...")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Hierarchy operations
    print("\n5. Testing Hierarchy operations:")
    try:
        if possibility:
            subposs_name = "Demo Sub-Possibility"
            existing_subs = [project.PossibilityList.GetName(s)
                           for s in project.PossibilityList.GetSubitems(possibility)]
            if subposs_name not in existing_subs:
                subposs = project.PossibilityList.CreateSubitem(possibility, subposs_name, "DSP")
                print(f"   Created subitem: {project.PossibilityList.GetName(subposs)}")

            subs = project.PossibilityList.GetSubitems(possibility)
            print(f"   Subitems count: {len(subs)}")

            if subs:
                parent = project.PossibilityList.GetParent(subs[0])
                if parent:
                    print(f"   Parent of subitem: {project.PossibilityList.GetName(parent)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test list properties
    print("\n6. Testing list-specific properties:")
    try:
        all_lists = project.PossibilityList.GetAllLists()
        print(f"   Total possibility lists in project: {len(all_lists)}")
        for i, poss_list in enumerate(all_lists[:3]):
            try:
                name = project.PossibilityList.GetListName(poss_list)
                print(f"     List {i+1}: {name}")
            except:
                print(f"     List {i+1}: [Unable to read]")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n7. Testing Metadata operations:")
    try:
        if possibility:
            created = project.PossibilityList.GetDateCreated(possibility)
            modified = project.PossibilityList.GetDateModified(possibility)
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
    demo_possibilitylist()
