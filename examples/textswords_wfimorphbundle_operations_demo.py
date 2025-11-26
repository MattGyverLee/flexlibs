#!/usr/bin/env python3
"""
Demonstration of WfiMorphBundleOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_wfimorphbundles():
    """Demonstrate WfiMorphBundleOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("WfiMorphBundleOperations Demonstration")
    print("=" * 60)

    # Test Read operations (GetAll, GetForm, GetGloss, GetSense, GetMSA, GetMorphType)
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

                # GetAll morph bundles for analysis
                bundles = list(project.MorphBundles.GetAll(analysis))
                print(f"   Found {len(bundles)} morph bundle(s)")

                # Display bundle info
                count = 0
                for bundle in bundles:
                    try:
                        form = project.MorphBundles.GetForm(bundle)
                        gloss = project.MorphBundles.GetGloss(bundle)
                        print(f"   Bundle {count + 1}: {form} - {gloss}")

                        # Get sense
                        sense = project.MorphBundles.GetSense(bundle)
                        if sense:
                            print(f"      Has linked sense: Yes")
                        else:
                            print(f"      Has linked sense: No")

                        # Get MSA
                        msa = project.MorphBundles.GetMSA(bundle)
                        if msa:
                            print(f"      Has MSA: Yes ({msa.ClassName})")
                        else:
                            print(f"      Has MSA: No")

                        # Get morph type
                        morph_type = project.MorphBundles.GetMorphType(bundle)
                        if morph_type:
                            try:
                                type_name = morph_type.Name.BestAnalysisAlternative.Text
                                print(f"      Morph type: {type_name}")
                            except:
                                print(f"      Morph type: [Unicode]")

                        # Get inflection class
                        infl_class = project.MorphBundles.GetInflectionClass(bundle)
                        if infl_class:
                            print(f"      Has inflection class: Yes")
                    except UnicodeEncodeError:
                        print(f"   Bundle: [Unicode]")
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
    print("   NOTE: Not creating morph bundles to preserve data")
    print("   Create() would add a new morph bundle to an analysis")

    # Test Update operations (SetForm, SetGloss, SetSense, SetMSA, SetMorphType)
    print("\n3. Testing Update operations:")
    print("   NOTE: Not modifying morph bundles to preserve data")
    print("   SetForm() would update morpheme form")
    print("   SetGloss() would update morpheme gloss")
    print("   SetSense() would link to lexical sense")
    print("   SetMSA() would set morpho-syntactic analysis")
    print("   SetMorphType() would set morpheme type")
    print("   SetInflectionClass() would set inflection class")
    print("   Reorder() would change bundle order")

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
                bundles = list(project.MorphBundles.GetAll(analysis))
                if bundles:
                    bundle = bundles[0]

                    # GetOwningAnalysis
                    owner = project.MorphBundles.GetOwningAnalysis(bundle)
                    print(f"   Bundle belongs to analysis: HVO {owner.Hvo}")

                    # GetGuid
                    guid = project.MorphBundles.GetGuid(bundle)
                    print(f"   Bundle GUID: {guid}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_wfimorphbundles()
