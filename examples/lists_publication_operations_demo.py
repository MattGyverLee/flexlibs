#!/usr/bin/env python3
"""
Demonstration of PublicationOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_publication():
    """Demonstrate PublicationOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("PublicationOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        publications = project.Publication.GetAll(flat=True)
        count = 0
        for publication in publications:
            try:
                name = project.Publication.GetName(publication)
                abbr = project.Publication.GetAbbreviation(publication)
                info = f"{name} - Abbr: {abbr if abbr else '(none)'}"
                print(f"   Publication: {info}")
            except UnicodeEncodeError:
                print(f"   Publication: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_name = "Demo Publication"
        if not project.Publication.Exists(test_name):
            publication = project.Publication.Create(test_name, "DP")
            print(f"   Created: {project.Publication.GetName(publication)}")
        else:
            publication = project.Publication.Find(test_name)
            print(f"   Publication already exists: {test_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        publication = project.Publication.Find("Demo Publication")
        if publication:
            print(f"   Found by name: {project.Publication.GetName(publication)}")
            guid = project.Publication.GetGuid(publication)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        if publication:
            # Test abbreviation
            abbr = project.Publication.GetAbbreviation(publication)
            print(f"   Abbreviation: {abbr}")

            # Test description
            project.Publication.SetDescription(publication, "Demo publication for testing")
            desc = project.Publication.GetDescription(publication)
            print(f"   Description: {desc[:50]}...")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Division operations
    print("\n5. Testing Division (Hierarchy) operations:")
    try:
        if publication:
            division_name = "Demo Division"
            existing_divs = [project.Publication.GetName(s)
                           for s in project.Publication.GetSubitems(publication)]
            if division_name not in existing_divs:
                division = project.Publication.CreateSubitem(publication, division_name, "DD")
                print(f"   Created division: {project.Publication.GetName(division)}")

            divs = project.Publication.GetSubitems(publication)
            print(f"   Divisions count: {len(divs)}")

            if divs:
                parent = project.Publication.GetParent(divs[0])
                if parent:
                    print(f"   Parent of division: {project.Publication.GetName(parent)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Publication types
    print("\n6. Testing publication types:")
    try:
        # Common publication types might include: Dictionary, Grammar, Text Collection
        all_pubs = project.Publication.GetAll(flat=False)
        print(f"   Top-level publications: {len(all_pubs)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n7. Testing Metadata operations:")
    try:
        if publication:
            created = project.Publication.GetDateCreated(publication)
            modified = project.Publication.GetDateModified(publication)
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
    demo_publication()
