#!/usr/bin/env python3
"""
Demonstration of ParagraphOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_paragraphs():
    """Demonstrate ParagraphOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("ParagraphOperations Demonstration")
    print("=" * 60)

    # Test Read operations (GetAll, GetText, GetSegments, GetSegmentCount)
    print("\n1. Testing Read operations:")
    try:
        # Get a text to work with
        texts = list(project.Texts.GetAll())
        if texts:
            text = texts[0]
            try:
                text_name = text.Name.BestAnalysisAlternative.Text
                print(f"   Working with text: {text_name}")
            except UnicodeEncodeError:
                print(f"   Working with text: [Unicode]")

            # GetAll paragraphs
            paragraphs = list(project.Paragraphs.GetAll(text))
            print(f"   Found {len(paragraphs)} paragraph(s)")

            # Display paragraph info
            count = 0
            for para in paragraphs:
                try:
                    para_text = project.Paragraphs.GetText(para)
                    if len(para_text) > 50:
                        para_text = para_text[:50] + "..."
                    print(f"   Paragraph: {para_text}")

                    # Get segment count
                    seg_count = project.Paragraphs.GetSegmentCount(para)
                    print(f"      Segments: {seg_count}")
                except UnicodeEncodeError:
                    print(f"   Paragraph: [Unicode]")
                count += 1
                if count >= 3:
                    break
        else:
            print("   No texts found in project")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operations (Create - check existence first)
    print("\n2. Testing Create operations:")
    print("   NOTE: Not creating paragraphs to preserve data")
    print("   Create() would append a new paragraph to text")
    print("   InsertAt() would insert paragraph at specific position")

    # Test Update operations (SetText)
    print("\n3. Testing Update operations:")
    print("   NOTE: Not modifying paragraphs to preserve data")
    print("   SetText() would update paragraph content")

    # Test Delete operations (NOT demonstrated to preserve data)
    print("\n4. Delete operations available but not demonstrated")
    print("   Delete() available but skipped for safety")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_paragraphs()
