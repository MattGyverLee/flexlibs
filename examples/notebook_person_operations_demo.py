#!/usr/bin/env python3
"""
Demonstration of PersonOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_person():
    """Demonstrate PersonOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("PersonOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        people = project.Person.GetAll(flat=True)
        count = 0
        for person in people:
            try:
                name = project.Person.GetName(person)
                abbr = project.Person.GetAbbreviation(person)
                info = f"{name} - Abbr: {abbr if abbr else '(none)'}"
                print(f"   Person: {info}")
            except UnicodeEncodeError:
                print(f"   Person: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_name = "Demo Person"
        if not project.Person.Exists(test_name):
            person = project.Person.Create(test_name, "DP")
            print(f"   Created: {project.Person.GetName(person)}")
        else:
            person = project.Person.Find(test_name)
            print(f"   Person already exists: {test_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        person = project.Person.Find("Demo Person")
        if person:
            print(f"   Found by name: {project.Person.GetName(person)}")
            guid = project.Person.GetGuid(person)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        if person:
            # Test abbreviation
            abbr = project.Person.GetAbbreviation(person)
            print(f"   Abbreviation: {abbr}")

            # Test description
            project.Person.SetDescription(person, "Demo person for testing purposes")
            desc = project.Person.GetDescription(person)
            print(f"   Description: {desc[:50]}...")

            # Test education
            project.Person.SetEducation(person, "Ph.D. in Linguistics")
            edu = project.Person.GetEducation(person)
            print(f"   Education: {edu}")

            # Test date of birth
            project.Person.SetDateOfBirth(person, "1985-06-15")
            dob = project.Person.GetDateOfBirth(person)
            print(f"   Date of Birth: {dob}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Contact information
    print("\n5. Testing Contact operations:")
    try:
        if person:
            # Set email
            project.Person.SetEmail(person, "demo@example.com")
            email = project.Person.GetEmail(person)
            print(f"   Email: {email}")

            # Set phone
            project.Person.SetPhone(person, "+1-555-0100")
            phone = project.Person.GetPhone(person)
            print(f"   Phone: {phone}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Position operations
    print("\n6. Testing Position operations:")
    try:
        positions = project.Person.GetAllPositions()
        print(f"   Available positions: {len(positions)}")
        if positions and person:
            project.Person.SetPosition(person, positions[0])
            pos = project.Person.GetPosition(person)
            print(f"   Position set successfully")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n7. Testing Metadata operations:")
    try:
        if person:
            created = project.Person.GetDateCreated(person)
            modified = project.Person.GetDateModified(person)
            print(f"   Created: {created}")
            print(f"   Modified: {modified}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Gender operations
    print("\n8. Testing Gender operations:")
    try:
        if person:
            gender = project.Person.GetGender(person)
            print(f"   Gender: {gender if gender else '(not set)'}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_person()
