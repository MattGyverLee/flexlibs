#!/usr/bin/env python3
"""
Demo: Reversal Index Operations (Work Stream 3)

This script demonstrates how to work with reversal indexes and entries
in a FieldWorks project using the flexlibs library.

Reversal indexes provide reverse dictionaries (e.g., English to vernacular),
enabling users to look up words in an analysis language and find corresponding
vernacular entries. Core dictionary feature with LIFT import/export (753 occurrences).

Usage:
    python demo_reversal_operations.py [project_name]

Features demonstrated:
    - Creating and managing reversal indexes
    - Creating reversal entries
    - Linking reversal entries to lexical senses
    - Navigating reversal hierarchies
    - Querying reversal indexes

Author: flexlibs Work Stream 3
Date: 2025
"""

import sys
from flexlibs2 import FLExProject


def demo_reversal_indexes(project):
    """Demonstrate reversal index operations."""
    print("\n=== Reversal Index Operations ===\n")

    # Get all reversal indexes
    print("1. List all reversal indexes:")
    for idx in project.ReversalIndexes.GetAll():
        name = project.ReversalIndexes.GetName(idx)
        ws = project.ReversalIndexes.GetWritingSystem(idx)
        entry_count = len(list(project.ReversalIndexes.GetEntries(idx)))
        print(f"   - {name} ({ws}): {entry_count} entries")

    # Find or create English reversal index
    print("\n2. Find or create English reversal index:")
    en_ws = project.WSHandle('en')
    en_idx = project.ReversalIndexes.FindByWritingSystem(en_ws)

    if not en_idx:
        print("   Creating new English reversal index...")
        en_idx = project.ReversalIndexes.Create("English", en_ws)
        print(f"   Created: {project.ReversalIndexes.GetName(en_idx)}")
    else:
        print(f"   Found existing: {project.ReversalIndexes.GetName(en_idx)}")

    return en_idx


def demo_reversal_entries(project, rev_index):
    """Demonstrate reversal entry operations."""
    print("\n=== Reversal Entry Operations ===\n")

    # List existing entries
    print("1. List existing reversal entries:")
    entries = list(project.ReversalEntries.GetAll(rev_index))
    for i, entry in enumerate(entries[:10], 1):  # Show first 10
        form = project.ReversalEntries.GetForm(entry)
        sense_count = len(project.ReversalEntries.GetSenses(entry))
        print(f"   {i}. {form} ({sense_count} senses)")

    if len(entries) > 10:
        print(f"   ... and {len(entries) - 10} more entries")

    # Create a new reversal entry
    print("\n2. Create new reversal entry:")
    test_form = "example-reversal"

    existing = project.ReversalEntries.Find(rev_index, test_form)
    if existing:
        print(f"   Entry '{test_form}' already exists")
        rev_entry = existing
    else:
        rev_entry = project.ReversalEntries.Create(rev_index, test_form)
        print(f"   Created entry: {project.ReversalEntries.GetForm(rev_entry)}")

    return rev_entry


def demo_sense_linking(project, rev_entry):
    """Demonstrate linking reversal entries to lexical senses."""
    print("\n=== Sense Linking Operations ===\n")

    # Show current linked senses
    print("1. Current linked senses:")
    senses = project.ReversalEntries.GetSenses(rev_entry)
    if senses:
        for i, sense in enumerate(senses, 1):
            gloss = project.Senses.GetGloss(sense)
            entry = sense.Entry
            headword = project.LexEntry.GetHeadword(entry)
            print(f"   {i}. {headword}: {gloss}")
    else:
        print("   No senses linked yet")

    # Link to a lexical sense
    print("\n2. Link to lexical sense:")
    # Find first lexical entry with a sense
    for lex_entry in project.LexEntry.GetAll():
        if lex_entry.SensesOS.Count > 0:
            sense = lex_entry.SensesOS[0]
            headword = project.LexEntry.GetHeadword(lex_entry)
            gloss = project.Senses.GetGloss(sense)

            # Check if already linked
            if sense not in senses:
                project.ReversalEntries.AddSense(rev_entry, sense)
                print(f"   Linked to: {headword} ({gloss})")
                break
            else:
                print(f"   Already linked to: {headword} ({gloss})")
                break
    else:
        print("   No lexical entries found to link")

    # Show updated linked senses
    print("\n3. Updated linked senses:")
    updated_senses = project.ReversalEntries.GetSenses(rev_entry)
    for i, sense in enumerate(updated_senses, 1):
        gloss = project.Senses.GetGloss(sense)
        entry = sense.Entry
        headword = project.LexEntry.GetHeadword(entry)
        print(f"   {i}. {headword}: {gloss}")


def demo_reversal_hierarchy(project, rev_index):
    """Demonstrate hierarchical reversal structure."""
    print("\n=== Reversal Hierarchy Operations ===\n")

    print("1. Check for entries with subentries:")
    found_parent = False
    for entry in project.ReversalEntries.GetAll(rev_index):
        subentries = project.ReversalEntries.GetSubentries(entry)
        if subentries:
            form = project.ReversalEntries.GetForm(entry)
            print(f"   Parent: {form}")
            for sub in subentries:
                sub_form = project.ReversalEntries.GetForm(sub)
                print(f"      - {sub_form}")
            found_parent = True
            break

    if not found_parent:
        print("   No hierarchical entries found")
        print("   (Hierarchical entries are common for phrasal verbs, compounds, etc.)")


def demo_reversal_queries(project, rev_index):
    """Demonstrate querying reversal indexes."""
    print("\n=== Reversal Query Operations ===\n")

    print("1. Statistics:")
    total_entries = len(list(project.ReversalEntries.GetAll(rev_index)))
    print(f"   Total entries: {total_entries}")

    # Count entries with/without sense links
    with_senses = 0
    without_senses = 0
    for entry in project.ReversalEntries.GetAll(rev_index):
        senses = project.ReversalEntries.GetSenses(entry)
        if senses:
            with_senses += 1
        else:
            without_senses += 1

    print(f"   Entries with sense links: {with_senses}")
    print(f"   Entries without sense links: {without_senses}")

    if total_entries > 0:
        print(f"   Coverage: {with_senses / total_entries * 100:.1f}%")


def main():
    """Main demo function."""
    # Get project name from command line or use default
    project_name = sys.argv[1] if len(sys.argv) > 1 else "Sena 3"

    print(f"===================================================")
    print(f"Reversal Index & Entry Operations Demo")
    print(f"Project: {project_name}")
    print(f"===================================================")

    # Initialize project
    project = FLExProject()

    try:
        # Open project with write access
        print(f"\nOpening project: {project_name}...")
        project.OpenProject(project_name, writeEnabled=True)
        print("Project opened successfully!")

        # Run demonstrations
        rev_index = demo_reversal_indexes(project)

        if rev_index:
            rev_entry = demo_reversal_entries(project, rev_index)

            if rev_entry:
                demo_sense_linking(project, rev_entry)

            demo_reversal_hierarchy(project, rev_index)
            demo_reversal_queries(project, rev_index)

        print("\n=== Demo Complete ===\n")
        print("Key Operations Demonstrated:")
        print("  ✓ Creating/finding reversal indexes")
        print("  ✓ Creating reversal entries")
        print("  ✓ Linking entries to lexical senses")
        print("  ✓ Navigating hierarchical structures")
        print("  ✓ Querying reversal statistics")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Close project
        if project.project:
            print("\nClosing project...")
            project.CloseProject()
            print("Project closed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
