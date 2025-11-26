#!/usr/bin/env python3
"""
Demonstration of SegmentOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_segments():
    """Demonstrate SegmentOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("SegmentOperations Demonstration")
    print("=" * 60)

    # Test Read operations (GetAll, GetBaselineText, GetFreeTranslation, GetLiteralTranslation)
    print("\n1. Testing Read operations:")
    try:
        # Get a text and paragraph to work with
        texts = list(project.Texts.GetAll())
        if texts:
            text = texts[0]
            paragraphs = list(project.Paragraphs.GetAll(text))
            if paragraphs:
                para = paragraphs[0]
                try:
                    para_text = project.Paragraphs.GetText(para)
                    if len(para_text) > 40:
                        para_text = para_text[:40] + "..."
                    print(f"   Working with paragraph: {para_text}")
                except UnicodeEncodeError:
                    print(f"   Working with paragraph: [Unicode]")

                # GetAll segments
                segments = list(project.Segments.GetAll(para))
                print(f"   Found {len(segments)} segment(s)")

                # Display segment info
                count = 0
                for segment in segments:
                    try:
                        baseline = project.Segments.GetBaselineText(segment)
                        if len(baseline) > 40:
                            baseline = baseline[:40] + "..."
                        print(f"   Segment baseline: {baseline}")

                        # Get translations
                        free_trans = project.Segments.GetFreeTranslation(segment)
                        if free_trans:
                            if len(free_trans) > 40:
                                free_trans = free_trans[:40] + "..."
                            print(f"      Free translation: {free_trans}")

                        literal_trans = project.Segments.GetLiteralTranslation(segment)
                        if literal_trans:
                            if len(literal_trans) > 40:
                                literal_trans = literal_trans[:40] + "..."
                            print(f"      Literal translation: {literal_trans}")

                        # Get analyses
                        analyses = project.Segments.GetAnalyses(segment)
                        print(f"      Analyses: {len(analyses)}")
                    except UnicodeEncodeError:
                        print(f"   Segment: [Unicode]")
                    count += 1
                    if count >= 3:
                        break
            else:
                print("   No paragraphs found in text")
        else:
            print("   No texts found in project")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operations (Create - check existence first)
    print("\n2. Testing Create operations:")
    print("   NOTE: Not creating segments to preserve data")
    print("   Create() would append a new segment to paragraph")
    print("   SplitSegment() would split a segment at position")
    print("   MergeSegments() would combine two adjacent segments")

    # Test Update operations (SetBaselineText, SetFreeTranslation, SetLiteralTranslation)
    print("\n3. Testing Update operations:")
    print("   NOTE: Not modifying segments to preserve data")
    print("   SetBaselineText() would update segment text")
    print("   SetFreeTranslation() would update free translation")
    print("   SetLiteralTranslation() would update literal translation")

    # Test Delete operations (NOT demonstrated to preserve data)
    print("\n4. Delete operations available but not demonstrated")
    print("   Delete() available but skipped for safety")

    # Test Utility operations
    print("\n5. Testing Utility operations:")
    try:
        texts = list(project.Texts.GetAll())
        if texts:
            text = texts[0]
            paragraphs = list(project.Paragraphs.GetAll(text))
            if paragraphs:
                para = paragraphs[0]
                # ValidateSegments
                result = project.Segments.ValidateSegments(para)
                print(f"   Segment validation: Valid={result['valid']}")
                print(f"      Segment count: {result['segment_count']}")
                print(f"      Errors: {len(result['errors'])}")
                print(f"      Warnings: {len(result['warnings'])}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_segments()
