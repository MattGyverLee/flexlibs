#!/usr/bin/env python3
"""
Demonstration of WfiGlossOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_wfiglosses():
    """Demonstrate WfiGlossOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("WfiGlossOperations Demonstration")
    print("=" * 60)

    # Test Read operations (GetAll, GetForm, GetAllForms, GetCount)
    print("\n1. Testing Read operations:")
    try:
        # Get a wordform and analysis to work with
        wordforms = list(project.Wordforms.GetAll())
        if wordforms:
            wordform = wordforms[0]
            try:
                wf_form = project.Wordforms.GetForm(wordform)
                print(f"   Working with wordform: {wf_form}")
            except UnicodeEncodeError:
                print(f"   Working with wordform: [Unicode]")

            # Get analyses for wordform
            analyses = project.WfiAnalyses.GetAll(wordform)
            if analyses:
                analysis = analyses[0]
                print(f"   Working with first analysis")

                # GetAll glosses for analysis
                glosses = list(project.WfiGlosses.GetAll(analysis))
                gloss_count = project.WfiGlosses.GetCount(analysis)
                print(f"   Found {gloss_count} gloss(es)")

                # Display gloss info
                count = 0
                for gloss in glosses:
                    try:
                        form = project.WfiGlosses.GetForm(gloss)
                        best_form = project.WfiGlosses.GetBestForm(gloss)
                        print(f"   Gloss: {form}")
                        print(f"      Best form: {best_form}")

                        # Get all forms across writing systems
                        all_forms = project.WfiGlosses.GetAllForms(gloss)
                        print(f"      Available in {len(all_forms)} writing system(s)")
                    except UnicodeEncodeError:
                        print(f"   Gloss: [Unicode]")
                    count += 1
                    if count >= 3:
                        break
            else:
                print("   No analyses found for wordform")
        else:
            print("   No wordforms found in project")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operations (Create - check existence first)
    print("\n2. Testing Create operations:")
    print("   NOTE: Not creating glosses to preserve data")
    print("   Create() would add a new gloss to an analysis")
    print("   CopyGloss() would copy gloss to another analysis")

    # Test Update operations (SetForm, ClearForm)
    print("\n3. Testing Update operations:")
    print("   NOTE: Not modifying glosses to preserve data")
    print("   SetForm() would update gloss text")
    print("   ClearForm() would clear gloss in specific writing system")
    print("   Reorder() would change gloss order")

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
                glosses = list(project.WfiGlosses.GetAll(analysis))
                if glosses:
                    gloss = glosses[0]

                    # GetOwningAnalysis
                    owner = project.WfiGlosses.GetOwningAnalysis(gloss)
                    print(f"   Gloss belongs to analysis: HVO {owner.Hvo}")

                    # GetGuid
                    guid = project.WfiGlosses.GetGuid(gloss)
                    print(f"   Gloss GUID: {guid}")

                    # Find/Exists
                    form = project.WfiGlosses.GetForm(gloss)
                    if form:
                        found = project.WfiGlosses.Find(analysis, form)
                        exists = project.WfiGlosses.Exists(analysis, form)
                        print(f"   Gloss '{form}' can be found: {found is not None}")
                        print(f"   Gloss '{form}' exists: {exists}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_wfiglosses()
