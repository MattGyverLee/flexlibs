#!/usr/bin/env python3
"""
Demonstration of AnnotationDefOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_annotationdef():
    """Demonstrate AnnotationDefOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("AnnotationDefOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        defs = project.AnnotationDef.GetAll()
        count = 0
        for ann_def in defs:
            try:
                name = project.AnnotationDef.GetName(ann_def)
                prompt = project.AnnotationDef.GetPrompt(ann_def)
                info = f"{name} - Prompt: {prompt[:30] if prompt else '(none)'}..."
                print(f"   Annotation Def: {info}")
            except UnicodeEncodeError:
                print(f"   Annotation Def: [Unicode name]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation
    print("\n2. Testing Create operation:")
    try:
        test_name = "Demo Annotation Type"
        if not project.AnnotationDef.Exists(test_name):
            ann_def = project.AnnotationDef.Create(test_name)
            print(f"   Created: {project.AnnotationDef.GetName(ann_def)}")
        else:
            ann_def = project.AnnotationDef.Find(test_name)
            print(f"   Annotation def already exists: {test_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Find operation
    print("\n3. Testing Find operations:")
    try:
        ann_def = project.AnnotationDef.Find("Demo Annotation Type")
        if ann_def:
            print(f"   Found by name: {project.AnnotationDef.GetName(ann_def)}")
            guid = project.AnnotationDef.GetGuid(ann_def)
            print(f"   GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Property operations
    print("\n4. Testing Property operations:")
    try:
        if ann_def:
            # Test prompt
            project.AnnotationDef.SetPrompt(ann_def, "Demo annotation prompt for testing")
            prompt = project.AnnotationDef.GetPrompt(ann_def)
            print(f"   Prompt: {prompt[:50]}...")

            # Test help info
            project.AnnotationDef.SetHelpInfo(ann_def, "Help information for demo annotation")
            help_info = project.AnnotationDef.GetHelpInfo(ann_def)
            print(f"   Help Info: {help_info[:50]}...")

            # Test instance count
            count = project.AnnotationDef.GetInstanceCount(ann_def)
            print(f"   Instance count: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test standard annotation types
    print("\n5. Testing standard annotation types:")
    try:
        # Common types: Comment, Translation, Consultant Note
        for name in ["Comment", "Translation", "Note"]:
            ann = project.AnnotationDef.Find(name)
            if ann:
                print(f"   Found annotation type: {name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test annotation permissions
    print("\n6. Testing annotation permissions:")
    try:
        if ann_def:
            # Check if user can create instances
            can_create = project.AnnotationDef.CanCreateInstance(ann_def)
            print(f"   Can create instance: {can_create}")

            # Check if user can delete instances
            can_delete = project.AnnotationDef.CanDeleteInstance(ann_def)
            print(f"   Can delete instance: {can_delete}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Metadata operations
    print("\n7. Testing Metadata operations:")
    try:
        if ann_def:
            created = project.AnnotationDef.GetDateCreated(ann_def)
            modified = project.AnnotationDef.GetDateModified(ann_def)
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
    demo_annotationdef()
