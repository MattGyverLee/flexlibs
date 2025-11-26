#!/usr/bin/env python3
"""
Demonstration of PhonemeOperations for flexlibs

This script demonstrates the comprehensive PhonemeOperations class
for managing phonemes in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_phoneme_operations():
    """Demonstrate PhonemeOperations functionality."""

    # Initialize FieldWorks
    FLExInitialize()

    # Open project
    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("PhonemeOperations Demonstration")
    print("=" * 60)

    # --- 1. GetAll - List all phonemes ---
    print("\n1. Getting all phonemes:")
    try:
        count = 0
        for phoneme in project.Phonemes.GetAll():
            repr = project.Phonemes.GetRepresentation(phoneme)
            desc = project.Phonemes.GetDescription(phoneme)
            try:
                if desc:
                    print(f"   {repr}: {desc}")
                else:
                    print(f"   {repr}")
            except UnicodeEncodeError:
                print(f"   [Unicode phoneme]")
            count += 1
            if count >= 10:  # Show first 10
                print("   ...")
                break
        print(f"   Total phonemes shown: {count}")
    except Exception as e:
        print(f"   ERROR in GetAll: {e}")

    # --- 2. Create - Create new phonemes ---
    print("\n2. Creating new phonemes:")
    p_phoneme = None
    b_phoneme = None
    try:
        if not project.Phonemes.Exists("/p/"):
            p_phoneme = project.Phonemes.Create("/p/")
            print(f"   Created phoneme: {project.Phonemes.GetRepresentation(p_phoneme)}")
        else:
            p_phoneme = project.Phonemes.Find("/p/")
            print("   Phoneme '/p/' already exists")

        if not project.Phonemes.Exists("/b/"):
            b_phoneme = project.Phonemes.Create("/b/")
            print(f"   Created phoneme: {project.Phonemes.GetRepresentation(b_phoneme)}")
        else:
            b_phoneme = project.Phonemes.Find("/b/")
            print("   Phoneme '/b/' already exists")
    except Exception as e:
        print(f"   ERROR in Create: {e}")

    # --- 3. Find - Find phonemes ---
    print("\n3. Finding phonemes:")
    try:
        found_p = project.Phonemes.Find("/p/")
        if found_p:
            print(f"   Found: {project.Phonemes.GetRepresentation(found_p)}")
        else:
            print("   Phoneme '/p/' not found")

        # Try finding a non-existent phoneme
        found_x = project.Phonemes.Find("/x/")
        if found_x:
            print(f"   Found: {project.Phonemes.GetRepresentation(found_x)}")
        else:
            print("   Phoneme '/x/' not found (as expected)")
    except Exception as e:
        print(f"   ERROR in Find: {e}")

    # --- 4. Exists - Check existence ---
    print("\n4. Checking existence:")
    try:
        print(f"   '/p/' exists: {project.Phonemes.Exists('/p/')}")
        print(f"   '/b/' exists: {project.Phonemes.Exists('/b/')}")
        print(f"   '/ʘ/' exists: {project.Phonemes.Exists('/ʘ/')}")  # Click consonant - unlikely
    except Exception as e:
        print(f"   ERROR in Exists: {e}")

    # --- 5. SetDescription - Add phonetic descriptions ---
    print("\n5. Setting phoneme descriptions:")
    try:
        if p_phoneme:
            project.Phonemes.SetDescription(p_phoneme, "voiceless bilabial stop")
            desc = project.Phonemes.GetDescription(p_phoneme)
            print(f"   /p/: {desc}")

        if b_phoneme:
            project.Phonemes.SetDescription(b_phoneme, "voiced bilabial stop")
            desc = project.Phonemes.GetDescription(b_phoneme)
            print(f"   /b/: {desc}")
    except Exception as e:
        print(f"   ERROR in SetDescription: {e}")

    # --- 6. GetDescription - Retrieve descriptions ---
    print("\n6. Getting phoneme descriptions:")
    try:
        if p_phoneme:
            desc = project.Phonemes.GetDescription(p_phoneme)
            print(f"   /p/ description: {desc}")
    except Exception as e:
        print(f"   ERROR in GetDescription: {e}")

    # --- 7. SetRepresentation - Update representation ---
    print("\n7. Updating phoneme representation:")
    try:
        if p_phoneme:
            original_repr = project.Phonemes.GetRepresentation(p_phoneme)
            print(f"   Current representation: {original_repr}")
            # Don't actually change it, just demonstrate the method exists
            print(f"   (SetRepresentation available but not changed to preserve data)")
    except Exception as e:
        print(f"   ERROR in SetRepresentation: {e}")

    # --- 8. Create vowel phonemes ---
    print("\n8. Creating vowel phonemes:")
    vowel_data = [
        ("/a/", "open front unrounded vowel"),
        ("/e/", "close-mid front unrounded vowel"),
        ("/i/", "close front unrounded vowel"),
        ("/o/", "close-mid back rounded vowel"),
        ("/u/", "close back rounded vowel")
    ]

    vowels = []
    for repr, desc in vowel_data:
        try:
            if not project.Phonemes.Exists(repr):
                vowel = project.Phonemes.Create(repr)
                project.Phonemes.SetDescription(vowel, desc)
                print(f"   Created: {repr} - {desc}")
                vowels.append(vowel)
            else:
                vowel = project.Phonemes.Find(repr)
                vowels.append(vowel)
                print(f"   '{repr}' already exists")
        except Exception as e:
            print(f"   ERROR creating {repr}: {e}")

    # --- 9. GetFeatures - Get feature structures ---
    print("\n9. Getting phoneme features:")
    try:
        if p_phoneme:
            features = project.Phonemes.GetFeatures(p_phoneme)
            if features:
                print(f"   /p/ has feature structure (HVO: {features.Hvo})")
            else:
                print(f"   /p/ has no feature structure defined")
    except Exception as e:
        print(f"   ERROR in GetFeatures: {e}")

    # --- 10. AddCode - Add allophonic codes ---
    print("\n10. Adding allophonic codes:")
    try:
        # Find or create /t/ for allophone demonstration
        t_phoneme = project.Phonemes.Find("/t/")
        if not t_phoneme:
            try:
                t_phoneme = project.Phonemes.Create("/t/")
                project.Phonemes.SetDescription(t_phoneme, "voiceless alveolar stop")
                print(f"   Created /t/ phoneme")
            except:
                pass

        if t_phoneme:
            # Check existing codes
            existing_codes = project.Phonemes.GetCodes(t_phoneme)
            print(f"   /t/ has {len(existing_codes)} existing code(s)")

            # Try to add allophones
            allophone_reprs = ["[t]", "[tʰ]", "[ɾ]"]
            for allophone_repr in allophone_reprs:
                try:
                    # Check if code already exists
                    has_code = False
                    for code in existing_codes:
                        # Can't easily check representation, so just skip
                        pass

                    # Try to add (may fail if already exists)
                    code = project.Phonemes.AddCode(t_phoneme, allophone_repr)
                    print(f"   Added allophone: {allophone_repr}")
                except Exception as e:
                    print(f"   Code {allophone_repr} might already exist or error: {type(e).__name__}")
    except Exception as e:
        print(f"   ERROR in AddCode: {e}")

    # --- 11. GetCodes - List allophonic codes ---
    print("\n11. Getting allophonic codes:")
    try:
        if t_phoneme:
            codes = project.Phonemes.GetCodes(t_phoneme)
            print(f"   /t/ has {len(codes)} code(s):")
            for code in codes[:5]:  # Show first 5
                try:
                    from SIL.LCModel.Core.KernelInterfaces import ITsString
                    ws = project.project.DefaultVernWs
                    repr = ITsString(code.Representation.get_String(ws)).Text
                    print(f"     - {repr}")
                except Exception as e:
                    print(f"     - [Cannot display: {type(e).__name__}]")
    except Exception as e:
        print(f"   ERROR in GetCodes: {e}")

    # --- 12. GetBasicIPASymbol - Get IPA symbols ---
    print("\n12. Getting basic IPA symbols:")
    try:
        if p_phoneme:
            ipa_symbol = project.Phonemes.GetBasicIPASymbol(p_phoneme)
            if ipa_symbol:
                print(f"   /p/ basic IPA: {ipa_symbol}")
            else:
                print(f"   /p/ has no basic IPA symbol set")
    except Exception as e:
        print(f"   ERROR in GetBasicIPASymbol: {e}")

    # --- 13. IsVowel - Check if phoneme is vowel ---
    print("\n13. Checking vowel classification:")
    try:
        test_phonemes = [p_phoneme, b_phoneme] + vowels[:2]
        for phoneme in test_phonemes:
            if phoneme:
                repr = project.Phonemes.GetRepresentation(phoneme)
                is_vowel = project.Phonemes.IsVowel(phoneme)
                print(f"   {repr} is vowel: {is_vowel}")
    except Exception as e:
        print(f"   ERROR in IsVowel: {e}")

    # --- 14. IsConsonant - Check if phoneme is consonant ---
    print("\n14. Checking consonant classification:")
    try:
        test_phonemes = [p_phoneme, b_phoneme] + vowels[:2]
        for phoneme in test_phonemes:
            if phoneme:
                repr = project.Phonemes.GetRepresentation(phoneme)
                is_consonant = project.Phonemes.IsConsonant(phoneme)
                print(f"   {repr} is consonant: {is_consonant}")
    except Exception as e:
        print(f"   ERROR in IsConsonant: {e}")

    # --- 15. Cleanup demonstration ---
    print("\n15. Cleanup (optional):")
    print("   (Demo preserves all phonemes - they can be deleted manually)")
    # Uncomment to test deletion:
    # try:
    #     if p_phoneme:
    #         project.Phonemes.Delete(p_phoneme)
    #         print("   Deleted /p/")
    # except Exception as e:
    #     print(f"   ERROR in Delete: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    print("""
PhonemeOperations Demo
======================

This demonstrates the comprehensive PhonemeOperations class with 17 methods:

Core CRUD Operations:
  - GetAll()              - Iterate all phonemes
  - Create()              - Create new phoneme with representation
  - Delete()              - Remove a phoneme
  - Exists()              - Check if phoneme exists
  - Find()                - Find phoneme by representation

Representation:
  - GetRepresentation()   - Get phoneme representation (e.g., /p/)
  - SetRepresentation()   - Set phoneme representation
  - GetBasicIPASymbol()   - Get basic IPA symbol

Description:
  - GetDescription()      - Get phonetic description
  - SetDescription()      - Set phonetic description

Features:
  - GetFeatures()         - Get feature structure

Allophones (Codes):
  - GetCodes()            - Get all allophonic codes
  - AddCode()             - Add allophonic code (e.g., [ph])
  - RemoveCode()          - Remove allophonic code

Classification:
  - IsVowel()             - Check if phoneme is a vowel
  - IsConsonant()         - Check if phoneme is a consonant

Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_phoneme_operations()
