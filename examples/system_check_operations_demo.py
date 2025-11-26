#!/usr/bin/env python3
"""
Demonstration of CheckOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_check():
    """Demonstrate CheckOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("CheckOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        checks = project.Check.GetAll()
        count = 0
        for check in checks:
            try:
                name = project.Check.GetName(check)
                desc = project.Check.GetDescription(check)
                info = f"{name} - Desc: {desc[:30] if desc else '(none)'}..."
                print(f"   Check: {info}")
            except UnicodeEncodeError:
                print(f"   Check: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_name = "Demo Consistency Check"
        if not project.Check.Exists(test_name):
            check = project.Check.Create(test_name)
            print(f"   Created: {project.Check.GetName(check)}")
        else:
            check = project.Check.Find(test_name)
            print(f"   Check already exists: {test_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        check = project.Check.Find("Demo Consistency Check")
        if check:
            print(f"   Found by name: {project.Check.GetName(check)}")
            guid = project.Check.GetGuid(check)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        if check:
            # Test description
            project.Check.SetDescription(check, "Demo consistency check for testing")
            desc = project.Check.GetDescription(check)
            print(f"   Description: {desc[:50]}...")

            # Test enabled status
            is_enabled = project.Check.IsEnabled(check)
            print(f"   Is enabled: {is_enabled}")

            # Test check type
            check_type = project.Check.GetCheckType(check)
            print(f"   Check type: {check_type if check_type else '(none)'}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test check execution
    print("\n5. Testing check execution:")
    try:
        if check:
            # Run the check (this might take time)
            print("   Running check...")
            result = project.Check.RunCheck(check)
            print(f"   Check completed with {len(result)} issues found")
    except Exception as e:
        print(f"   ERROR (check execution may not be supported): {e}")

    # Test check status operations
    print("\n6. Testing check status:")
    try:
        if check:
            # Get last run date
            last_run = project.Check.GetLastRunDate(check)
            print(f"   Last run: {last_run if last_run else 'Never'}")

            # Get issue count
            issue_count = project.Check.GetIssueCount(check)
            print(f"   Issue count: {issue_count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n7. Testing Metadata operations:")
    try:
        if check:
            created = project.Check.GetDateCreated(check)
            modified = project.Check.GetDateModified(check)
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
    demo_check()
