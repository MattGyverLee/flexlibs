#!/usr/bin/env python3
"""
Demonstration of NoteOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_note():
    """Demonstrate NoteOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("NoteOperations Demonstration")
    print("=" * 60)

    # Test Read operations
    print("\n1. Testing GetAll operations:")
    try:
        notes = list(project.Note.GetAll())
        count = 0
        for note in notes:
            try:
                content = project.Note.GetContent(note)
                note_type = project.Note.GetNoteType(note)
                info = f"Content: {content[:50] if content else '(empty)'}... Type: {note_type if note_type else '(none)'}"
                print(f"   Note: {info}")
            except UnicodeEncodeError:
                print(f"   Note: [Unicode content]")
            except Exception as ex:
                print(f"   Note: [Error reading: {ex}]")
            count += 1
            if count >= 5:
                break
        print(f"   Total shown: {count}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operation (notes are typically annotations on other objects)
    print("\n2. Testing Note Type operations:")
    try:
        types = project.Note.GetAllNoteTypes()
        print(f"   Available note types: {len(types)}")
        for i, note_type in enumerate(types[:5]):
            try:
                print(f"     Type {i+1}: [Note type object]")
            except:
                pass
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test finding notes
    print("\n3. Testing note retrieval:")
    try:
        # Get a lexical entry to attach notes to
        entries = list(project.LexEntry.GetAll())
        if entries:
            entry = entries[0]
            headword = project.LexEntry.GetHeadword(entry)
            print(f"   Testing with entry: {headword[:30] if len(headword) > 30 else headword}")

            # Try to get notes for this entry
            notes = project.Note.GetNotesForObject(entry)
            print(f"   Notes on this entry: {len(notes)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test note properties
    print("\n4. Testing note properties:")
    try:
        all_notes = list(project.Note.GetAll())
        if all_notes:
            note = all_notes[0]
            try:
                content = project.Note.GetContent(note)
                print(f"   Content: {content[:60] if content else '(empty)'}...")

                guid = project.Note.GetGuid(note)
                print(f"   GUID: {guid}")
            except Exception as ex:
                print(f"   ERROR reading note properties: {ex}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test note categories/types
    print("\n5. Testing note categories:")
    try:
        categories = project.Note.GetAllNoteTypes()
        if categories:
            print(f"   Total categories: {len(categories)}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test metadata operations
    print("\n6. Testing Metadata operations:")
    try:
        all_notes = list(project.Note.GetAll())
        if all_notes:
            note = all_notes[0]
            try:
                created = project.Note.GetDateCreated(note)
                modified = project.Note.GetDateModified(note)
                print(f"   Created: {created}")
                print(f"   Modified: {modified}")
            except Exception as ex:
                print(f"   ERROR: {ex}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_note()
