#!/usr/bin/env python3
"""
Demonstration of ProjectSettingsOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_projectsettings():
    """Demonstrate ProjectSettingsOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("ProjectSettingsOperations Demonstration")
    print("=" * 60)

    # Test Project Name operations
    print("\n1. Testing Project Name operations:")
    try:
        name = project.ProjectSettings.GetProjectName()
        print(f"   Project name: {name}")

        # Note: We typically don't change project name in demos
        # project.ProjectSettings.SetProjectName("New Name")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Analysis Writing System
    print("\n2. Testing Analysis Writing System:")
    try:
        aws = project.ProjectSettings.GetAnalysisWritingSystem()
        print(f"   Analysis WS: {aws}")

        aws_name = project.ProjectSettings.GetAnalysisWritingSystemName()
        print(f"   Analysis WS Name: {aws_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Vernacular Writing System
    print("\n3. Testing Vernacular Writing System:")
    try:
        vws = project.ProjectSettings.GetVernacularWritingSystem()
        print(f"   Vernacular WS: {vws}")

        vws_name = project.ProjectSettings.GetVernacularWritingSystemName()
        print(f"   Vernacular WS Name: {vws_name}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Writing System Lists
    print("\n4. Testing Writing System Lists:")
    try:
        aws_list = project.ProjectSettings.GetAnalysisWritingSystems()
        print(f"   Analysis WS count: {len(aws_list)}")
        for i, ws in enumerate(aws_list[:3]):
            try:
                print(f"     WS {i+1}: {ws}")
            except:
                pass

        vws_list = project.ProjectSettings.GetVernacularWritingSystems()
        print(f"   Vernacular WS count: {len(vws_list)}")
        for i, ws in enumerate(vws_list[:3]):
            try:
                print(f"     WS {i+1}: {ws}")
            except:
                pass
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Project Properties
    print("\n5. Testing Project Properties:")
    try:
        # Get various project properties
        external_link = project.ProjectSettings.GetExternalLink()
        print(f"   External link: {external_link if external_link else '(none)'}")

        project_type = project.ProjectSettings.GetProjectType()
        print(f"   Project type: {project_type if project_type else '(unknown)'}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Project Description
    print("\n6. Testing Project Description:")
    try:
        desc = project.ProjectSettings.GetProjectDescription()
        if desc:
            print(f"   Description: {desc[:60]}...")
        else:
            print("   Description: (not set)")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Project Status
    print("\n7. Testing Project Status:")
    try:
        status = project.ProjectSettings.GetProjectStatus()
        print(f"   Status: {status if status else '(not set)'}")

        # Test if project is active
        is_active = project.ProjectSettings.IsActive()
        print(f"   Is active: {is_active}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Project Dates
    print("\n8. Testing Project Dates:")
    try:
        created = project.ProjectSettings.GetDateCreated()
        modified = project.ProjectSettings.GetDateModified()
        print(f"   Created: {created}")
        print(f"   Modified: {modified}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Project Metadata
    print("\n9. Testing Project Metadata:")
    try:
        guid = project.ProjectSettings.GetProjectGuid()
        print(f"   Project GUID: {guid}")

        version = project.ProjectSettings.GetProjectVersion()
        print(f"   Project version: {version if version else '(unknown)'}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_projectsettings()
