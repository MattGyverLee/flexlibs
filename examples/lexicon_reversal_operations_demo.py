#!/usr/bin/env python3
"""
Demonstration of ReversalOperations for flexlibs

This script demonstrates the comprehensive ReversalOperations class
for managing reversal entries in a FLEx project.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_reversal_operations():
    """Demonstrate ReversalOperations functionality."""

    # Initialize FieldWorks
    FLExInitialize()

    # Open project
    project = FLExProject()
    try:
        project.OpenProject(r"C:\ProgramData\SIL\FieldWorks\Projects\Kenyang-M\Kenyang-M.fwdata", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("ReversalOperations Demonstration")
    print("=" * 60)

    # --- 1. GetAllIndexes - List all reversal indexes ---
    print("\n1. Getting all reversal indexes:")
    try:
        indexes = project.Reversal.GetAllIndexes()
        print(f"   Total reversal indexes: {len(indexes)}")
        for idx in indexes:
            ws = idx.WritingSystem
            count = idx.EntriesOC.Count
            print(f"   - {ws}: {count} entries")
    except Exception as e:
        print(f"   ERROR in GetAllIndexes: {e}")

    # --- 2. GetIndex - Get specific reversal index ---
    print("\n2. Getting English reversal index:")
    en_index = None
    try:
        en_index = project.Reversal.GetIndex("en")
        if en_index:
            print(f"   Found English reversal index")
            print(f"   Writing system: {en_index.WritingSystem}")
            print(f"   Entry count: {en_index.EntriesOC.Count}")
        else:
            print("   English reversal index not found")
    except Exception as e:
        print(f"   ERROR in GetIndex: {e}")

    # --- 3. GetAll - Get all entries in an index ---
    print("\n3. Getting reversal entries:")
    try:
        if en_index:
            entries = project.Reversal.GetAll(en_index)
            print(f"   Total entries in English index: {len(entries)}")
            count = 0
            for entry in entries:
                form = project.Reversal.GetForm(entry)
                sense_count = project.Reversal.GetSenseCount(entry)
                try:
                    print(f"   - {form} ({sense_count} senses)")
                except UnicodeEncodeError:
                    print(f"   - [Unicode entry] ({sense_count} senses)")
                count += 1
                if count >= 5:  # Show first 5 only
                    print("   ...")
                    break
    except Exception as e:
        print(f"   ERROR in GetAll: {e}")

    # --- 4. Create - Create a new reversal entry ---
    print("\n4. Creating a new reversal entry:")
    test_entry = None
    try:
        if en_index:
            # Check if it exists first
            if not project.Reversal.Exists(en_index, "test_walk"):
                test_entry = project.Reversal.Create(en_index, "test_walk", "en")
                form = project.Reversal.GetForm(test_entry)
                print(f"   Created reversal entry: {form}")
            else:
                print("   'test_walk' already exists")
                test_entry = project.Reversal.Find(en_index, "test_walk")
    except Exception as e:
        print(f"   ERROR in Create: {e}")

    # --- 5. Find - Find a reversal entry ---
    print("\n5. Finding reversal entries:")
    try:
        if en_index:
            found = project.Reversal.Find(en_index, "test_walk")
            if found:
                form = project.Reversal.GetForm(found)
                print(f"   Found entry: {form}")
            else:
                print("   Entry 'test_walk' not found")
    except Exception as e:
        print(f"   ERROR in Find: {e}")

    # --- 6. GetForm/SetForm - Get and set reversal form ---
    print("\n6. Getting and setting reversal form:")
    try:
        if test_entry:
            current_form = project.Reversal.GetForm(test_entry)
            print(f"   Current form: {current_form}")

            # Set it to same value to demonstrate
            project.Reversal.SetForm(test_entry, current_form)
            print(f"   Form preserved: {project.Reversal.GetForm(test_entry)}")
    except Exception as e:
        print(f"   ERROR in GetForm/SetForm: {e}")

    # --- 7. AddSense - Link a sense to reversal entry ---
    print("\n7. Linking senses to reversal entry:")
    try:
        if test_entry:
            # Try to find a lexical entry with senses
            lex_entry = project.LexEntry.Find("walk")
            if not lex_entry:
                # Try to find any entry with senses
                all_entries = list(project.LexEntry.GetAll())
                for entry in all_entries[:10]:  # Check first 10
                    senses = project.LexEntry.GetSenses(entry)
                    if senses:
                        lex_entry = entry
                        break

            if lex_entry:
                headword = project.LexEntry.GetHeadword(lex_entry)
                try:
                    print(f"   Found lexical entry: {headword}")
                except UnicodeEncodeError:
                    print(f"   Found lexical entry: [Unicode]")

                senses = project.LexEntry.GetSenses(lex_entry)
                if senses:
                    # Check if sense is already linked
                    linked_senses = project.Reversal.GetSenses(test_entry)
                    if senses[0] not in linked_senses:
                        project.Reversal.AddSense(test_entry, senses[0])
                        print(f"   Linked sense to reversal entry")
                    else:
                        print(f"   Sense already linked")

                    # Show all linked senses
                    linked = project.Reversal.GetSenses(test_entry)
                    print(f"   Total linked senses: {len(linked)}")
    except Exception as e:
        print(f"   ERROR in AddSense: {e}")

    # --- 8. GetSenses - Get all linked senses ---
    print("\n8. Getting linked senses:")
    try:
        if test_entry:
            senses = project.Reversal.GetSenses(test_entry)
            print(f"   Senses linked to reversal entry: {len(senses)}")
            for sense in senses[:3]:  # Show first 3
                gloss = project.LexiconGetSenseGloss(sense)
                try:
                    print(f"   - {gloss}")
                except UnicodeEncodeError:
                    print(f"   - [Unicode gloss]")
    except Exception as e:
        print(f"   ERROR in GetSenses: {e}")

    # --- 9. CreateSubentry - Create a subentry ---
    print("\n9. Creating a reversal subentry:")
    test_subentry = None
    try:
        if test_entry:
            # Check if subentry exists
            existing_subs = project.Reversal.GetSubentries(test_entry)
            has_test_sub = False
            for sub in existing_subs:
                if project.Reversal.GetForm(sub) == "test_walk_away":
                    has_test_sub = True
                    test_subentry = sub
                    break

            if not has_test_sub:
                test_subentry = project.Reversal.CreateSubentry(test_entry, "test_walk_away")
                form = project.Reversal.GetForm(test_subentry)
                print(f"   Created subentry: {form}")
            else:
                print("   Subentry 'test_walk_away' already exists")
    except Exception as e:
        print(f"   ERROR in CreateSubentry: {e}")

    # --- 10. GetSubentries - Get all subentries ---
    print("\n10. Getting subentries:")
    try:
        if test_entry:
            subentries = project.Reversal.GetSubentries(test_entry)
            print(f"   Subentries of 'test_walk': {len(subentries)}")
            for subentry in subentries:
                form = project.Reversal.GetForm(subentry)
                try:
                    print(f"   - {form}")
                except UnicodeEncodeError:
                    print(f"   - [Unicode subentry]")
    except Exception as e:
        print(f"   ERROR in GetSubentries: {e}")

    # --- 11. GetParentEntry - Get parent of subentry ---
    print("\n11. Getting parent entry:")
    try:
        if test_subentry:
            parent = project.Reversal.GetParentEntry(test_subentry)
            if parent:
                parent_form = project.Reversal.GetForm(parent)
                print(f"   Parent of 'test_walk_away': {parent_form}")
            else:
                print("   This is a top-level entry")
    except Exception as e:
        print(f"   ERROR in GetParentEntry: {e}")

    # --- 12. RemoveSense - Unlink a sense ---
    print("\n12. Unlinking senses:")
    try:
        if test_entry:
            senses = project.Reversal.GetSenses(test_entry)
            if senses:
                print(f"   Senses before removal: {len(senses)}")
                # Remove the first sense
                project.Reversal.RemoveSense(test_entry, senses[0])
                remaining = project.Reversal.GetSenses(test_entry)
                print(f"   Senses after removal: {len(remaining)}")
    except Exception as e:
        print(f"   ERROR in RemoveSense: {e}")

    # --- 13. Cleanup demonstration ---
    print("\n13. Cleanup (cleaning up test entries):")
    try:
        if test_subentry:
            project.Reversal.Delete(test_subentry)
            print("   Deleted test subentry")

        if test_entry:
            # Remove all remaining senses
            for sense in project.Reversal.GetSenses(test_entry):
                project.Reversal.RemoveSense(test_entry, sense)

            project.Reversal.Delete(test_entry)
            print("   Deleted test entry")
    except Exception as e:
        print(f"   ERROR in Cleanup: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    print("""
ReversalOperations Demo
=======================

This demonstrates the comprehensive ReversalOperations class with 20+ methods:

Reversal Index Management:
  - GetAllIndexes()        - Get all reversal indexes
  - GetIndex()             - Get reversal index for writing system
  - FindIndex()            - Find index by writing system (alias)

Entry CRUD Operations:
  - GetAll()               - Get all entries in an index
  - Create()               - Create new reversal entry
  - Delete()               - Remove a reversal entry
  - Find()                 - Find entry by form
  - Exists()               - Check if entry exists

Form Management:
  - GetForm()              - Get reversal entry form
  - SetForm()              - Set reversal entry form

Sense Linking:
  - GetSenses()            - Get all linked senses
  - AddSense()             - Link a sense to entry
  - RemoveSense()          - Unlink a sense from entry
  - GetSenseCount()        - Count linked senses

Subentries:
  - GetSubentries()        - Get all subentries
  - CreateSubentry()       - Create a subentry
  - GetParentEntry()       - Get parent of subentry

Parts of Speech:
  - GetPartsOfSpeech()     - Get associated parts of speech

Note: Actual execution requires a FLEx project and Python.NET runtime.
    """)
    demo_reversal_operations()
