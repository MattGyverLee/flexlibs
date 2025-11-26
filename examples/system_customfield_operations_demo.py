#!/usr/bin/env python3
"""
Demonstration of CustomFieldOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_customfield():
    """Demonstrate CustomFieldOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("CustomFieldOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        fields = project.CustomField.GetAll()
        count = 0
        for field in fields:
            try:
                name = project.CustomField.GetName(field)
                field_type = project.CustomField.GetFieldType(field)
                info = f"{name} - Type: {field_type if field_type else '(unknown)'}"
                print(f"   Custom Field: {info}")
            except UnicodeEncodeError:
                print(f"   Custom Field: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_name = "Demo_Custom_Field"
        if not project.CustomField.Exists(test_name):
            field = project.CustomField.Create(test_name, "String", "LexEntry")
            print(f"   Created: {project.CustomField.GetName(field)}")
        else:
            field = project.CustomField.Find(test_name)
            print(f"   Custom field already exists: {test_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        field = project.CustomField.Find("Demo_Custom_Field")
        if field:
            print(f"   Found by name: {project.CustomField.GetName(field)}")
            guid = project.CustomField.GetGuid(field)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        if field:
            # Test field type
            field_type = project.CustomField.GetFieldType(field)
            print(f"   Field type: {field_type}")

            # Test class name
            class_name = project.CustomField.GetClassName(field)
            print(f"   Class name: {class_name}")

            # Test help string
            project.CustomField.SetHelpString(field, "Demo custom field for testing")
            help_str = project.CustomField.GetHelpString(field)
            print(f"   Help string: {help_str[:50]}...")

            # Test label
            project.CustomField.SetLabel(field, "Demo Field")
            label = project.CustomField.GetLabel(field)
            print(f"   Label: {label}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test field types
    print("\n5. Testing field types:")
    try:
        all_fields = project.CustomField.GetAll()
        type_counts = {}
        for f in all_fields:
            try:
                ftype = project.CustomField.GetFieldType(f)
                type_counts[ftype] = type_counts.get(ftype, 0) + 1
            except:
                pass
        print("   Field type distribution:")
        for ftype, count in type_counts.items():
            print(f"     {ftype}: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test value operations (on actual entry if possible)
    print("\n6. Testing value operations:")
    try:
        if field:
            # Get a lexical entry to test with
            entries = list(project.LexEntry.GetAll())
            if entries:
                entry = entries[0]

                # Set custom field value
                project.CustomField.SetValue(field, entry, "Demo value for testing")
                value = project.CustomField.GetValue(field, entry)
                print(f"   Custom field value: {value}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n7. Testing Metadata operations:")
    try:
        if field:
            created = project.CustomField.GetDateCreated(field)
            modified = project.CustomField.GetDateModified(field)
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
    demo_customfield()
