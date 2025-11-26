#!/usr/bin/env python3
"""
Demonstration of MediaOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_media():
    """Demonstrate MediaOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("MediaOperations Demonstration")
    print("=" * 60)

    # Test Read operations (GetAll, GetInternalPath, GetLabel, GetMediaType)
    print("\n1. Testing Read operations:")
    try:
        # GetAll example
        media_files = project.Media.GetAll()
        count = 0
        for media in media_files:
            # Display media info with Unicode error handling
            try:
                path = project.Media.GetInternalPath(media)
                label = project.Media.GetLabel(media, "en")
                media_type = project.Media.GetMediaType(media)
                type_names = {0: "Unknown", 1: "Audio", 2: "Video", 3: "Image"}
                type_str = type_names.get(media_type, "Unknown")
                print(f"   Media: {path} ({type_str}) - {label}")
            except UnicodeEncodeError:
                print(f"   Media: [Unicode]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")

        # Test media type detection
        if count > 0:
            media = list(project.Media.GetAll())[0]
            is_audio = project.Media.IsAudio(media)
            is_video = project.Media.IsVideo(media)
            is_image = project.Media.IsImage(media)
            print(f"   First media: Audio={is_audio}, Video={is_video}, Image={is_image}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operations (Create - check existence first)
    print("\n2. Testing Create operations:")
    print("   NOTE: Not creating media files to preserve data")
    print("   Create() would add a new media file reference")
    print("   CopyToProject() would copy external file to project")

    # Test Update operations (SetLabel, SetInternalPath)
    print("\n3. Testing Update operations:")
    print("   NOTE: Not modifying media to preserve data")
    print("   SetLabel() would update media labels")
    print("   SetInternalPath() would update file paths")

    # Test Delete operations (NOT demonstrated to preserve data)
    print("\n4. Delete operations available but not demonstrated")
    print("   Delete() available but skipped for safety")

    # Test Utility operations
    print("\n5. Testing Utility operations:")
    try:
        media_files = list(project.Media.GetAll())
        if media_files:
            media = media_files[0]
            # Test IsValid
            is_valid = project.Media.IsValid(media)
            print(f"   First media file exists on disk: {is_valid}")

            # Test GetOwners
            owners = project.Media.GetOwners(media)
            owner_count = project.Media.GetOwnerCount(media)
            print(f"   Media has {owner_count} owner(s)")

            # Test GetFileSize
            size = project.Media.GetFileSize(media)
            if size >= 0:
                print(f"   File size: {size} bytes")
            else:
                print(f"   File size: Not available")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_media()
