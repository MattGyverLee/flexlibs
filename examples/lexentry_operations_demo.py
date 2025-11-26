#!/usr/bin/env python3
"""
Demonstration of LexEntryOperations for flexlibs

This script demonstrates the comprehensive LexEntryOperations class
for managing lexical entries in a FLEx project.
"""

# Example usage - requires a FLEx project
# This is demonstration code showing the API

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_lexentry_operations():
    """
    Demonstrate LexEntryOperations functionality.

    Note: This is example code. Actual execution requires:
    - A valid FLEx project
    - Python.NET runtime with FLEx assemblies
    """

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
    print("LexEntryOperations Demonstration")
    print("=" * 60)

    # --- 1. GetAll - Iterate all entries ---
    print("\n1. Getting all entries:")
    count = 0
    for entry in project.LexEntry.GetAll():
        headword = project.LexEntry.GetHeadword(entry)
        sense_count = project.LexEntry.GetSenseCount(entry)
        try:
            print(f"   {headword} ({sense_count} senses)")
        except UnicodeEncodeError:
            # Handle Unicode characters that can't be displayed in console
            print(f"   [Unicode entry] ({sense_count} senses)")
        count += 1
        if count >= 5:  # Show first 5 only
            print("   ...")
            break

    # --- 2. Create - Create a new entry ---
    print("\n2. Creating a new entry:")
    if not project.LexEntry.Exists("test_entry_demo"):
        entry = project.LexEntry.Create("test_entry_demo", "stem")
        print(f"   Created entry: {project.LexEntry.GetHeadword(entry)}")

        # Add a sense
        sense = project.LexEntry.AddSense(entry, "a test entry for demonstration")
        print(f"   Added sense with gloss: {project.LexiconGetSenseGloss(sense)}")
    else:
        print("   Entry 'test_entry_demo' already exists")

    # --- 3. Find - Find an entry ---
    print("\n3. Finding entries:")
    entry = project.LexEntry.Find("test_entry_demo")
    if entry:
        print(f"   Found entry: {project.LexEntry.GetHeadword(entry)}")
        print(f"   GUID: {project.LexEntry.GetGuid(entry)}")
        print(f"   Created: {project.LexEntry.GetDateCreated(entry)}")
        print(f"   Modified: {project.LexEntry.GetDateModified(entry)}")

    # --- 4. Headword & Forms ---
    print("\n4. Working with forms:")
    if entry:
        # Lexeme form
        lexeme = project.LexEntry.GetLexemeForm(entry)
        print(f"   Lexeme form: {lexeme}")

        # Citation form
        citation = project.LexEntry.GetCitationForm(entry)
        print(f"   Citation form: {citation or '(not set)'}")

        # Set citation form
        project.LexEntry.SetCitationForm(entry, "test entry, demo")
        citation = project.LexEntry.GetCitationForm(entry)
        print(f"   Citation form (updated): {citation}")

    # --- 5. Homograph numbers ---
    print("\n5. Homograph numbers:")
    if entry:
        homograph_num = project.LexEntry.GetHomographNumber(entry)
        print(f"   Homograph number: {homograph_num}")
        if homograph_num == 0:
            print("   (0 means no homograph)")

    # --- 6. Morph type ---
    print("\n6. Morph type:")
    if entry:
        morph_type = project.LexEntry.GetMorphType(entry)
        if morph_type:
            from SIL.LCModel.Core.KernelInterfaces import ITsString
            mt_name = ITsString(morph_type.Name.BestAnalysisAlternative).Text
            print(f"   Morph type: {mt_name}")

    # --- 7. Sense management ---
    print("\n7. Sense management:")
    if entry:
        senses = project.LexEntry.GetSenses(entry)
        print(f"   Number of senses: {project.LexEntry.GetSenseCount(entry)}")
        for i, sense in enumerate(senses, 1):
            gloss = project.LexiconGetSenseGloss(sense)
            print(f"   Sense {i}: {gloss}")

        # Add another sense
        if project.LexEntry.GetSenseCount(entry) < 3:
            new_sense = project.LexEntry.AddSense(entry, "another meaning for testing")
            print(f"   Added new sense: {project.LexiconGetSenseGloss(new_sense)}")

    # --- 8. Import residue ---
    print("\n8. Import residue:")
    if entry:
        try:
            residue = project.LexEntry.GetImportResidue(entry)
            if residue:
                print(f"   Import residue: {residue}")
            else:
                print("   No import residue")
                # Set some test residue
                project.LexEntry.SetImportResidue(entry, "<test>demo residue</test>")
                residue = project.LexEntry.GetImportResidue(entry)
                if residue:
                    print(f"   Import residue (set): {residue}")
        except:
            print("   No import residue")

    # --- 9. Exists check ---
    print("\n9. Checking existence:")
    print(f"   'test_entry_demo' exists: {project.LexEntry.Exists('test_entry_demo')}")
    print(f"   'nonexistent_entry' exists: {project.LexEntry.Exists('nonexistent_entry')}")

    # --- 10. Cleanup demonstration ---
    print("\n10. Cleanup (optional):")
    if entry:
        # Uncomment to delete the demo entry:
        # project.LexEntry.Delete(entry)
        # print("   Deleted demo entry")
        print("   (Demo entry preserved - uncomment code to delete)")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    # Close project
    project.CloseProject()

    # Cleanup FieldWorks
    FLExCleanup()


if __name__ == "__main__":
    print("""
LexEntryOperations Demo
=======================

This demonstrates the comprehensive LexEntryOperations class with 23+ methods:

Core CRUD Operations:
  - GetAll()           - Iterate all lexical entries
  - Create()           - Create new entry with lexeme form and morph type
  - Delete()           - Remove an entry
  - Exists()           - Check if entry exists
  - Find()             - Find entry by lexeme form

Headword & Form Management:
  - GetHeadword()      - Get display headword
  - SetHeadword()      - Set headword (via lexeme form)
  - GetLexemeForm()    - Get lexeme form
  - SetLexemeForm()    - Set lexeme form
  - GetCitationForm()  - Get citation form
  - SetCitationForm()  - Set citation form

Entry Properties:
  - GetHomographNumber()   - Get homograph number
  - SetHomographNumber()   - Set homograph number
  - GetDateCreated()       - Get creation timestamp
  - GetDateModified()      - Get modification timestamp
  - GetMorphType()         - Get morph type (stem, root, etc.)
  - SetMorphType()         - Set morph type

Sense Management:
  - GetSenses()        - Get all senses
  - GetSenseCount()    - Count senses
  - AddSense()         - Add new sense with gloss

Additional:
  - GetGuid()          - Get entry GUID
  - GetImportResidue() - Get import residue
  - SetImportResidue() - Set import residue

Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)

    # Run the demo:
    demo_lexentry_operations()
