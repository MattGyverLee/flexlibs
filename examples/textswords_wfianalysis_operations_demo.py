#!/usr/bin/env python3
"""
Demonstration of WfiAnalysisOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_wfianalyses():
    """Demonstrate WfiAnalysisOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("WfiAnalysisOperations Demonstration")
    print("=" * 60)

    # Test Read operations (GetAll, GetGlosses, GetMorphBundles, GetCategory, GetApprovalStatus)
    print("\n1. Testing Read operations:")
    try:
        # Get a wordform to work with
        wordforms = list(project.Wordforms.GetAll())
        if wordforms:
            wordform = wordforms[0]
            try:
                wf_form = project.Wordforms.GetForm(wordform)
                print(f"   Working with wordform: {wf_form}")
            except UnicodeEncodeError:
                print(f"   Working with wordform: [Unicode]")

            # GetAll analyses for wordform
            analyses = project.WfiAnalyses.GetAll(wordform)
            print(f"   Found {len(analyses)} analysis/analyses")

            # Display analysis info
            count = 0
            for analysis in analyses:
                print(f"   Analysis {count + 1}:")

                # Get glosses
                glosses = project.WfiAnalyses.GetGlosses(analysis)
                print(f"      Glosses: {len(glosses)}")

                # Get morph bundles
                bundles = project.WfiAnalyses.GetMorphBundles(analysis)
                print(f"      Morph bundles: {len(bundles)}")

                # Get category
                category = project.WfiAnalyses.GetCategory(analysis)
                if category:
                    try:
                        cat_name = category.Name.BestAnalysisAlternative.Text
                        print(f"      Category: {cat_name}")
                    except:
                        print(f"      Category: [Unicode]")

                # Get approval status
                try:
                    is_human_approved = project.WfiAnalyses.IsHumanApproved(analysis)
                    is_computer_approved = project.WfiAnalyses.IsComputerApproved(analysis)
                    print(f"      Human approved: {is_human_approved}")
                    print(f"      Computer approved: {is_computer_approved}")
                except:
                    print(f"      Approval status: [Error checking]")

                count += 1
                if count >= 3:
                    break
        else:
            print("   No wordforms found in project")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operations (Create - check existence first)
    print("\n2. Testing Create operations:")
    print("   NOTE: Not creating analyses to preserve data")
    print("   Create() would add a new analysis to a wordform")
    print("   AddGloss() would add a gloss to an analysis")

    # Test Update operations (SetCategory, ApproveAnalysis, RejectAnalysis)
    print("\n3. Testing Update operations:")
    print("   NOTE: Not modifying analyses to preserve data")
    print("   SetCategory() would assign part of speech")
    print("   ApproveAnalysis() would mark analysis as approved")
    print("   RejectAnalysis() would mark analysis as rejected")
    print("   SetApprovalStatus() would set specific approval status")

    # Test Delete operations (NOT demonstrated to preserve data)
    print("\n4. Delete operations available but not demonstrated")
    print("   Delete() available but skipped for safety")

    # Test Utility operations
    print("\n5. Testing Utility operations:")
    try:
        wordforms = list(project.Wordforms.GetAll())
        if wordforms:
            wordform = wordforms[0]
            analyses = project.WfiAnalyses.GetAll(wordform)
            if analyses:
                analysis = analyses[0]
                # GetOwningWordform
                owner = project.WfiAnalyses.GetOwningWordform(analysis)
                owner_form = project.Wordforms.GetForm(owner)
                print(f"   Analysis belongs to wordform: {owner_form}")

                # GetGuid
                guid = project.WfiAnalyses.GetGuid(analysis)
                print(f"   Analysis GUID: {guid}")

                # GetGlossCount
                gloss_count = project.WfiAnalyses.GetGlossCount(analysis)
                print(f"   Gloss count: {gloss_count}")

                # GetMorphBundleCount
                bundle_count = project.WfiAnalyses.GetMorphBundleCount(analysis)
                print(f"   Morph bundle count: {bundle_count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_wfianalyses()
