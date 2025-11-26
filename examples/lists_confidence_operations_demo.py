#!/usr/bin/env python3
"""
Demonstration of ConfidenceOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_confidence():
    """Demonstrate ConfidenceOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("ConfidenceOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        levels = project.Confidence.GetAll(flat=True)
        count = 0
        for level in levels:
            try:
                name = project.Confidence.GetName(level)
                abbr = project.Confidence.GetAbbreviation(level)
                info = f"{name} - Abbr: {abbr if abbr else '(none)'}"
                print(f"   Confidence Level: {info}")
            except UnicodeEncodeError:
                print(f"   Confidence Level: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_name = "Demo Confidence"
        if not project.Confidence.Exists(test_name):
            level = project.Confidence.Create(test_name, "DC")
            print(f"   Created: {project.Confidence.GetName(level)}")
        else:
            level = project.Confidence.Find(test_name)
            print(f"   Confidence level already exists: {test_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        level = project.Confidence.Find("Demo Confidence")
        if level:
            print(f"   Found by name: {project.Confidence.GetName(level)}")
            guid = project.Confidence.GetGuid(level)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        if level:
            # Test abbreviation
            abbr = project.Confidence.GetAbbreviation(level)
            print(f"   Abbreviation: {abbr}")

            # Test description
            project.Confidence.SetDescription(level, "Demo confidence level for testing")
            desc = project.Confidence.GetDescription(level)
            print(f"   Description: {desc[:50]}...")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Hierarchy operations
    print("\n5. Testing Hierarchy operations:")
    try:
        if level:
            sublevel_name = "Demo Sub-Level"
            existing_subs = [project.Confidence.GetName(s)
                           for s in project.Confidence.GetSubitems(level)]
            if sublevel_name not in existing_subs:
                sublevel = project.Confidence.CreateSubitem(level, sublevel_name, "DSL")
                print(f"   Created subitem: {project.Confidence.GetName(sublevel)}")

            subs = project.Confidence.GetSubitems(level)
            print(f"   Subitems count: {len(subs)}")

            if subs:
                parent = project.Confidence.GetParent(subs[0])
                if parent:
                    print(f"   Parent of subitem: {project.Confidence.GetName(parent)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test standard confidence levels
    print("\n6. Testing standard confidence levels:")
    try:
        # Common confidence levels: High, Medium, Low, Uncertain
        for name in ["High", "Medium", "Low"]:
            conf = project.Confidence.Find(name)
            if conf:
                print(f"   Found standard level: {name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n7. Testing Metadata operations:")
    try:
        if level:
            created = project.Confidence.GetDateCreated(level)
            modified = project.Confidence.GetDateModified(level)
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
    demo_confidence()
