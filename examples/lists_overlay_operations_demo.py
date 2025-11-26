#!/usr/bin/env python3
"""
Demonstration of OverlayOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_overlay():
    """Demonstrate OverlayOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("OverlayOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        overlays = project.Overlay.GetAll(flat=True)
        count = 0
        for overlay in overlays:
            try:
                name = project.Overlay.GetName(overlay)
                abbr = project.Overlay.GetAbbreviation(overlay)
                info = f"{name} - Abbr: {abbr if abbr else '(none)'}"
                print(f"   Overlay: {info}")
            except UnicodeEncodeError:
                print(f"   Overlay: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_name = "Demo Overlay"
        if not project.Overlay.Exists(test_name):
            overlay = project.Overlay.Create(test_name, "DO")
            print(f"   Created: {project.Overlay.GetName(overlay)}")
        else:
            overlay = project.Overlay.Find(test_name)
            print(f"   Overlay already exists: {test_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        overlay = project.Overlay.Find("Demo Overlay")
        if overlay:
            print(f"   Found by name: {project.Overlay.GetName(overlay)}")
            guid = project.Overlay.GetGuid(overlay)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        if overlay:
            # Test abbreviation
            abbr = project.Overlay.GetAbbreviation(overlay)
            print(f"   Abbreviation: {abbr}")

            # Test description
            project.Overlay.SetDescription(overlay, "Demo chart overlay for testing")
            desc = project.Overlay.GetDescription(overlay)
            print(f"   Description: {desc[:50]}...")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Hierarchy operations
    print("\n5. Testing Hierarchy operations:")
    try:
        if overlay:
            suboverlay_name = "Demo Sub-Overlay"
            existing_subs = [project.Overlay.GetName(s)
                           for s in project.Overlay.GetSubitems(overlay)]
            if suboverlay_name not in existing_subs:
                suboverlay = project.Overlay.CreateSubitem(overlay, suboverlay_name, "DSO")
                print(f"   Created subitem: {project.Overlay.GetName(suboverlay)}")

            subs = project.Overlay.GetSubitems(overlay)
            print(f"   Subitems count: {len(subs)}")

            if subs:
                parent = project.Overlay.GetParent(subs[0])
                if parent:
                    print(f"   Parent of subitem: {project.Overlay.GetName(parent)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n6. Testing Metadata operations:")
    try:
        if overlay:
            created = project.Overlay.GetDateCreated(overlay)
            modified = project.Overlay.GetDateModified(overlay)
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
    demo_overlay()
