#!/usr/bin/env python3
"""
Demonstration of WordformOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup
from flexlibs.code.TextsWords.WordformOperations import SpellingStatusStates

def demo_wordforms():
    """Demonstrate WordformOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("WordformOperations Demonstration")
    print("=" * 60)

    # Test Read operations (GetAll, GetForm, GetSpellingStatus, GetAnalyses, GetOccurrenceCount)
    print("\n1. Testing Read operations:")
    try:
        # GetAll example
        wordforms = project.Wordforms.GetAll()
        count = 0
        for wf in wordforms:
            # Display wordform info with Unicode error handling
            try:
                form = project.Wordforms.GetForm(wf)
                status = project.Wordforms.GetSpellingStatus(wf)
                status_names = {0: "UNDECIDED", 1: "INCORRECT", 2: "CORRECT"}
                status_str = status_names.get(status, "UNKNOWN")

                # Get occurrence count
                occ_count = project.Wordforms.GetOccurrenceCount(wf)

                # Get analysis count
                analyses = project.Wordforms.GetAnalyses(wf)

                print(f"   Wordform: {form} [{status_str}] - {len(analyses)} analyses, {occ_count} occurrences")
            except UnicodeEncodeError:
                print(f"   Wordform: [Unicode]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")

        # Test Find/Exists
        if count > 0:
            first_wf = list(project.Wordforms.GetAll())[0]
            first_form = project.Wordforms.GetForm(first_wf)
            exists = project.Wordforms.Exists(first_form)
            found = project.Wordforms.Find(first_form)
            print(f"   Wordform '{first_form}' exists: {exists}")
            print(f"   Wordform '{first_form}' can be found: {found is not None}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test filtering by status
    print("\n   Testing status filtering:")
    try:
        correct_wfs = list(project.Wordforms.GetAllWithStatus(SpellingStatusStates.CORRECT))
        print(f"   Found {len(correct_wfs)} CORRECT wordforms")

        undecided_wfs = list(project.Wordforms.GetAllWithStatus(SpellingStatusStates.UNDECIDED))
        print(f"   Found {len(undecided_wfs)} UNDECIDED wordforms")

        unapproved_wfs = list(project.Wordforms.GetAllUnapproved())
        print(f"   Found {len(unapproved_wfs)} UNAPPROVED wordforms (UNDECIDED + INCORRECT)")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operations (Create - check existence first)
    print("\n2. Testing Create operations:")
    print("   NOTE: Not creating wordforms to preserve data")
    print("   Create() would add a new wordform to the inventory")

    # Test Update operations (SetForm, SetSpellingStatus, ApproveSpelling)
    print("\n3. Testing Update operations:")
    print("   NOTE: Not modifying wordforms to preserve data")
    print("   SetForm() would change wordform text")
    print("   SetSpellingStatus() would change spelling status")
    print("   ApproveSpelling() would set status to CORRECT")

    # Test Delete operations (NOT demonstrated to preserve data)
    print("\n4. Delete operations available but not demonstrated")
    print("   Delete() available but skipped for safety")

    # Test Utility operations
    print("\n5. Testing Utility operations:")
    try:
        wordforms = list(project.Wordforms.GetAll())
        if wordforms:
            wordform = wordforms[0]

            # GetChecksum
            checksum = project.Wordforms.GetChecksum(wordform)
            print(f"   First wordform checksum: {checksum}")

            # GetOccurrences
            occurrences = project.Wordforms.GetOccurrences(wordform)
            print(f"   First wordform occurrence count: {len(occurrences)}")

            # Get detailed occurrence info
            if occurrences:
                segment = occurrences[0]
                print(f"   First occurrence segment HVO: {segment.Hvo}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_wordforms()
