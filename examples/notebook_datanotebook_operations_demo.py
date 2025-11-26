#!/usr/bin/env python3
"""
Demonstration of DataNotebookOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_datanotebook():
    """Demonstrate DataNotebookOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("DataNotebookOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        records = list(project.DataNotebook.GetAll())
        count = 0
        for record in records:
            try:
                title = project.DataNotebook.GetTitle(record)
                date = project.DataNotebook.GetDateOfEvent(record)
                info = f"{title} - Date: {date if date else '(none)'}"
                print(f"   Record: {info}")
            except UnicodeEncodeError:
                print(f"   Record: [Unicode title]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_title = "Demo Notebook Record"
        if not project.DataNotebook.Exists(test_title):
            record = project.DataNotebook.Create(
                test_title,
                "This is a demo notebook record for testing"
            )
            print(f"   Created: {project.DataNotebook.GetTitle(record)}")
        else:
            record = project.DataNotebook.Find(test_title)
            print(f"   Record already exists: {test_title}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        record = project.DataNotebook.Find("Demo Notebook Record")
        if record:
            print(f"   Found by title: {project.DataNotebook.GetTitle(record)}")
            guid = project.DataNotebook.GetGuid(record)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        if record:
            # Test content
            project.DataNotebook.SetContent(record, "Updated content for demonstration purposes")
            content = project.DataNotebook.GetContent(record)
            print(f"   Content: {content[:50]}...")

            # Test date
            project.DataNotebook.SetDateOfEvent(record, "2024-01-15")
            event_date = project.DataNotebook.GetDateOfEvent(record)
            print(f"   Event Date: {event_date}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Record Type operations
    print("\n5. Testing Record Type operations:")
    try:
        types = project.DataNotebook.GetAllRecordTypes()
        print(f"   Available record types: {len(types)}")
        if types and record:
            project.DataNotebook.SetRecordType(record, types[0])
            rec_type = project.DataNotebook.GetRecordType(record)
            print(f"   Record type set successfully")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Status operations
    print("\n6. Testing Status operations:")
    try:
        statuses = project.DataNotebook.GetAllStatuses()
        print(f"   Available statuses: {len(statuses)}")
        if statuses and record:
            project.DataNotebook.SetStatus(record, statuses[0])
            status = project.DataNotebook.GetStatus(record)
            print(f"   Status set successfully")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Hierarchy operations
    print("\n7. Testing Hierarchy operations:")
    try:
        if record:
            subrecord_title = "Demo Sub-Record"
            existing_subs = [project.DataNotebook.GetTitle(s)
                           for s in project.DataNotebook.GetSubRecords(record)]
            if subrecord_title not in existing_subs:
                subrecord = project.DataNotebook.CreateSubRecord(
                    record, subrecord_title, "Sub-record content"
                )
                print(f"   Created sub-record: {project.DataNotebook.GetTitle(subrecord)}")

            subs = project.DataNotebook.GetSubRecords(record)
            print(f"   Sub-records count: {len(subs)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n8. Testing Metadata operations:")
    try:
        if record:
            created = project.DataNotebook.GetDateCreated(record)
            modified = project.DataNotebook.GetDateModified(record)
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
    demo_datanotebook()
