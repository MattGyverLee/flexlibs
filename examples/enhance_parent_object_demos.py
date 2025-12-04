#!/usr/bin/env python3
"""
Enhance CRUD Demos with Parent Object Creation

Updates demos that require parent objects to actually create them.
This makes the demos fully functional instead of just noting the requirement.

Author: FlexTools Development Team
Date: 2025-12-04
"""

from pathlib import Path

# Demo-specific enhancements
ENHANCEMENTS = {
    'lexicon_allomorph_operations_demo.py': {
        'needs_parent': 'LexEntry',
        'create_code': '''
        # Create parent entry for allomorph testing
        print("\\nCreating parent entry for allomorph test...")
        parent_entry = None
        try:
            parent_entry = project.LexEntry.Create("crud_test_entry_for_allomorph", "stem")
            print(f"  Created parent entry: crud_test_entry_for_allomorph")
        except Exception as e:
            print(f"  ERROR creating parent entry: {e}")
            print("  Cannot test allomorph without parent entry")
            return

        # Get morph type (stem)
        morph_type = None
        try:
            # Get the first available morph type (usually "stem")
            from SIL.LCModel import ILcmOwningSequence, IMoMorphType
            morph_types = project.project.LexDb.MorphTypesOA.PossibilitiesOS
            for mt in morph_types:
                if "stem" in str(mt.Name.BestAnalysisAlternative.Text).lower():
                    morph_type = mt
                    break
            if not morph_type and morph_types.Count > 0:
                morph_type = morph_types[0]
        except:
            pass

        if not morph_type:
            print("  ERROR: Could not find morph type")
            print("  Cannot test allomorph without morph type")
            return

        print(f"\\nCreating new allomorph: '{test_name}'")

        try:
            # Create allomorph with parent entry
            test_obj = project.Allomorphs.Create(parent_entry, test_name, morph_type)
            print(f"  SUCCESS: Allomorph created!")
''',
        'cleanup_code': '''
        # Cleanup parent entry
        try:
            if parent_entry:
                project.LexEntry.Delete(parent_entry)
                print("  Cleaned up: parent entry")
        except:
            pass
'''
    },

    'lexicon_etymology_operations_demo.py': {
        'needs_parent': 'LexEntry',
        'create_code': '''
        # Create parent entry for etymology testing
        print("\\nCreating parent entry for etymology test...")
        parent_entry = None
        try:
            parent_entry = project.LexEntry.Create("crud_test_entry_for_etymology", "stem")
            print(f"  Created parent entry: crud_test_entry_for_etymology")
        except Exception as e:
            print(f"  ERROR creating parent entry: {e}")
            print("  Cannot test etymology without parent entry")
            return

        print(f"\\nCreating new etymology: '{test_name}'")

        try:
            # Create etymology with parent entry (not string)
            test_obj = project.Etymology.Create(parent_entry)
            print(f"  SUCCESS: Etymology created!")
''',
        'cleanup_code': '''
        # Cleanup parent entry
        try:
            if parent_entry:
                project.LexEntry.Delete(parent_entry)
                print("  Cleaned up: parent entry")
        except:
            pass
'''
    },

    'lexicon_example_operations_demo.py': {
        'needs_parent': 'LexSense',
        'create_code': '''
        # Create parent entry and sense for example testing
        print("\\nCreating parent entry and sense for example test...")
        parent_entry = None
        parent_sense = None
        try:
            parent_entry = project.LexEntry.Create("crud_test_entry_for_example", "stem")
            parent_sense = project.LexEntry.AddSense(parent_entry, "test sense")
            print(f"  Created parent entry and sense")
        except Exception as e:
            print(f"  ERROR creating parent objects: {e}")
            print("  Cannot test example without parent sense")
            return

        print(f"\\nCreating new example: '{test_name}'")

        try:
            # Create example with parent sense
            test_obj = project.Examples.Create(parent_sense, test_name)
            print(f"  SUCCESS: Example created!")
''',
        'cleanup_code': '''
        # Cleanup parent entry (sense will be deleted with it)
        try:
            if parent_entry:
                project.LexEntry.Delete(parent_entry)
                print("  Cleaned up: parent entry and sense")
        except:
            pass
'''
    },

    'lexicon_pronunciation_operations_demo.py': {
        'needs_parent': 'LexEntry',
        'create_code': '''
        # Create parent entry for pronunciation testing
        print("\\nCreating parent entry for pronunciation test...")
        parent_entry = None
        try:
            parent_entry = project.LexEntry.Create("crud_test_entry_for_pronunciation", "stem")
            print(f"  Created parent entry: crud_test_entry_for_pronunciation")
        except Exception as e:
            print(f"  ERROR creating parent entry: {e}")
            print("  Cannot test pronunciation without parent entry")
            return

        print(f"\\nCreating new pronunciation: '{test_name}'")

        try:
            # Create pronunciation with parent entry
            test_obj = project.Pronunciations.Create(parent_entry, test_name)
            print(f"  SUCCESS: Pronunciation created!")
''',
        'cleanup_code': '''
        # Cleanup parent entry
        try:
            if parent_entry:
                project.LexEntry.Delete(parent_entry)
                print("  Cleaned up: parent entry")
        except:
            pass
'''
    },

    'lexicon_sense_operations_demo.py': {
        'needs_parent': 'LexEntry',
        'create_code': '''
        # Create parent entry for sense testing
        print("\\nCreating parent entry for sense test...")
        parent_entry = None
        try:
            parent_entry = project.LexEntry.Create("crud_test_entry_for_sense", "stem")
            print(f"  Created parent entry: crud_test_entry_for_sense")
        except Exception as e:
            print(f"  ERROR creating parent entry: {e}")
            print("  Cannot test sense without parent entry")
            return

        print(f"\\nCreating new sense: '{test_name}'")

        try:
            # Create sense with parent entry
            test_obj = project.LexEntry.AddSense(parent_entry, test_name)
            print(f"  SUCCESS: Sense created!")
''',
        'cleanup_code': '''
        # Cleanup parent entry (sense will be deleted with it)
        try:
            if parent_entry:
                project.LexEntry.Delete(parent_entry)
                print("  Cleaned up: parent entry and sense")
        except:
            pass
'''
    },

    'lexicon_variant_operations_demo.py': {
        'needs_parent': 'LexEntry',
        'create_code': '''
        # Create parent entry for variant testing
        print("\\nCreating parent entry for variant test...")
        parent_entry = None
        try:
            parent_entry = project.LexEntry.Create("crud_test_entry_for_variant", "stem")
            print(f"  Created parent entry: crud_test_entry_for_variant")
        except Exception as e:
            print(f"  ERROR creating parent entry: {e}")
            print("  Cannot test variant without parent entry")
            return

        # Get variant type
        variant_type = None
        try:
            # Get first available variant type
            from SIL.LCModel import ILexEntryType
            variant_types = project.project.LexDb.VariantEntryTypesOA.PossibilitiesOS
            if variant_types.Count > 0:
                variant_type = variant_types[0]
        except:
            pass

        if not variant_type:
            print("  ERROR: Could not find variant type")
            print("  Cannot test variant without variant type")
            return

        print(f"\\nCreating new variant: '{test_name}'")

        try:
            # Create variant with parent entry
            test_obj = project.Variants.Create(parent_entry, test_name, variant_type)
            print(f"  SUCCESS: Variant created!")
''',
        'cleanup_code': '''
        # Cleanup parent entry
        try:
            if parent_entry:
                project.LexEntry.Delete(parent_entry)
                print("  Cleaned up: parent entry")
        except:
            pass
'''
    },
}


def enhance_demo(filepath):
    """Enhance a demo file to create parent objects."""
    filename = filepath.name

    if filename not in ENHANCEMENTS:
        return False

    enhancement = ENHANCEMENTS[filename]

    print(f"Enhancing {filename}...")
    print(f"  Needs parent: {enhancement['needs_parent']}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the generic CREATE section with parent-aware version
    # Find the CREATE section marker
    create_marker = "# Create new object"
    cleanup_marker = "print(\"\\nClosing project...\")"

    if create_marker not in content:
        print("  ERROR: Could not find CREATE section marker")
        return False

    if cleanup_marker not in content:
        print("  ERROR: Could not find cleanup section marker")
        return False

    # Split content at markers
    before_create = content[:content.index(create_marker)]
    after_create_start = content.index(create_marker)

    # Find the end of the CREATE section (before READ: Verify creation)
    verify_marker = "# ==================== READ: Verify creation ===================="
    if verify_marker not in content[after_create_start:]:
        print("  ERROR: Could not find verify section marker")
        return False

    after_create_section = content.index(verify_marker, after_create_start)
    after_verify = content[after_create_section:]

    # Build enhanced CREATE section
    new_create_section = enhancement['create_code']

    # Continue with the rest (but skip old create code)
    enhanced_content = before_create + new_create_section + "\n        " + after_verify

    # Add cleanup code for parent objects
    cleanup_before = enhanced_content[:enhanced_content.index(cleanup_marker)]
    cleanup_after = enhanced_content[enhanced_content.index(cleanup_marker):]

    enhanced_content = cleanup_before + enhancement['cleanup_code'] + "\n        " + cleanup_after

    # Write enhanced version
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)

    print(f"  Enhanced successfully!")
    return True


def main():
    """Enhance all relevant demo files."""
    examples_dir = Path(__file__).parent

    print("="*70)
    print("DEMO ENHANCEMENT - PARENT OBJECT CREATION")
    print("="*70)
    print(f"\nEnhancing {len(ENHANCEMENTS)} demos\n")

    enhanced_count = 0
    for filename in ENHANCEMENTS.keys():
        filepath = examples_dir / filename
        if filepath.exists():
            if enhance_demo(filepath):
                enhanced_count += 1
        else:
            print(f"ERROR: {filename} not found")

    print("\n" + "="*70)
    print(f"\nEnhanced: {enhanced_count}/{len(ENHANCEMENTS)} files")
    print("="*70)


if __name__ == "__main__":
    main()
