#!/usr/bin/env python3
"""
Demonstration of TextOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_texts():
    """Demonstrate TextOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("TextOperations Demonstration")
    print("=" * 60)

    # Test Read operations (GetAll, GetName, GetContents, GetParagraphs, GetParagraphCount)
    print("\n1. Testing Read operations:")
    try:
        # GetAll example
        texts = project.Texts.GetAll()
        count = 0
        for text in texts:
            # Display text info with Unicode error handling
            try:
                name = project.Texts.GetName(text)
                abbr = project.Texts.GetAbbreviation(text)
                para_count = project.Texts.GetParagraphCount(text)
                print(f"   Text: {name} ({abbr}) - {para_count} paragraphs")

                # Get genre if available
                genre = project.Texts.GetGenre(text)
                if genre:
                    try:
                        genre_name = genre.Name.BestAnalysisAlternative.Text
                        print(f"      Genre: {genre_name}")
                    except:
                        print(f"      Genre: [Unicode]")

                # Get media files
                media_files = project.Texts.GetMediaFiles(text)
                print(f"      Media files: {len(media_files)}")
            except UnicodeEncodeError:
                print(f"   Text: [Unicode]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")

        # Test Exists
        if count > 0:
            first_text = list(project.Texts.GetAll())[0]
            first_name = project.Texts.GetName(first_text)
            exists = project.Texts.Exists(first_name)
            print(f"   Text '{first_name}' exists: {exists}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operations (Create - check existence first)
    print("\n2. Testing Create operations:")
    print("   NOTE: Not creating texts to preserve data")
    print("   Create() would add a new text to the project")
    print("   AddMediaFile() would attach media to a text")

    # Test Update operations (SetName, SetGenre)
    print("\n3. Testing Update operations:")
    print("   NOTE: Not modifying texts to preserve data")
    print("   SetName() would update text name")
    print("   SetGenre() would assign genre to text")

    # Test Delete operations (NOT demonstrated to preserve data)
    print("\n4. Delete operations available but not demonstrated")
    print("   Delete() available but skipped for safety")

    # Test Utility operations
    print("\n5. Testing Utility operations:")
    try:
        texts = list(project.Texts.GetAll())
        if texts:
            text = texts[0]
            # Get contents
            contents = project.Texts.GetContents(text)
            if contents:
                print(f"   Text has StText contents: Yes")
            else:
                print(f"   Text has StText contents: No")

            # Get paragraphs
            paragraphs = project.Texts.GetParagraphs(text)
            print(f"   Paragraph count (via GetParagraphs): {len(paragraphs)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_texts()
