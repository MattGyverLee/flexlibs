#!/usr/bin/env python3
"""
Comprehensive API Name Fix for CRUD Demos

The template conversion used incorrect API attribute names.
This script fixes all demos to use the correct FLExProject API names.

Author: FlexTools Development Team
Date: 2025-12-04
"""

from pathlib import Path
import re

# Mapping: filename pattern -> correct API name
# Based on actual FLExProject.py property definitions
FILENAME_TO_API_MAP = {
    'grammar_environment': 'Environments',
    'grammar_gramcat': 'GramCat',
    'grammar_inflection': 'InflectionFeatures',  # Note: inflection -> InflectionFeatures
    'grammar_morphrule': 'MorphRules',
    'grammar_naturalclass': 'NaturalClasses',
    'grammar_phoneme': 'Phonemes',
    'grammar_phonrule': 'PhonRules',
    'grammar_pos': 'POS',

    'lexentry': 'LexEntry',
    'lexicon_allomorph': 'Allomorphs',
    'lexicon_etymology': 'Etymology',
    'lexicon_example': 'Examples',
    'lexicon_lexreference': 'LexReferences',
    'lexicon_pronunciation': 'Pronunciations',
    'lexicon_reversal': 'Reversal',
    'lexicon_semanticdomain': 'SemanticDomains',
    'lexicon_sense': 'Senses',
    'lexicon_variant': 'Variants',

    'lists_agent': 'Agents',
    'lists_confidence': 'Confidence',
    'lists_overlay': 'Overlays',
    'lists_possibilitylist': 'PossibilityLists',
    'lists_publication': 'Publications',
    'lists_translationtype': 'TranslationTypes',

    'notebook_anthropology': 'Anthropology',
    'notebook_datanotebook': 'DataNotebook',
    'notebook_location': 'Location',
    'notebook_note': 'Notes',
    'notebook_person': 'Person',

    'system_annotationdef': 'AnnotationDefs',
    'system_check': 'Checks',
    'system_customfield': 'CustomFields',
    'system_projectsettings': 'ProjectSettings',
    'system_writingsystem': 'WritingSystems',

    'textswords_discourse': 'Discourse',
    'textswords_media': 'Media',
    'textswords_paragraph': 'Paragraphs',
    'textswords_segment': 'Segments',
    'textswords_text': 'Texts',
    'textswords_wfianalysis': 'WfiAnalyses',
    'textswords_wfigloss': 'WfiGlosses',
    'textswords_wfimorphbundle': 'WfiMorphBundles',
    'textswords_wordform': 'Wordforms',
}


def get_api_name(filename):
    """
    Get correct API name for a demo file.

    Args:
        filename: Name of the demo file (e.g., 'grammar_pos_operations_demo.py')

    Returns:
        Correct API name from the mapping, or None if not found
    """
    # Remove _operations_demo.py suffix
    base = filename.replace('_operations_demo.py', '')

    # Look up in map
    if base in FILENAME_TO_API_MAP:
        return FILENAME_TO_API_MAP[base]

    # Fallback: shouldn't happen
    return None


def fix_api_names_in_file(filepath):
    """
    Fix API attribute names in a demo file.

    Args:
        filepath: Path to the demo file to fix

    Returns:
        True if changes were made, False otherwise
    """
    print(f"Fixing {filepath.name}...")

    correct_api_name = get_api_name(filepath.name)
    if not correct_api_name:
        print(f"  ERROR: No API mapping found for {filepath.name}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all project.XXXXX references and replace with correct API name
    # Pattern: project.<CapitalizedWord>
    pattern = r'project\.([A-Z][a-z]+)'

    # Count occurrences of incorrect names
    matches = re.findall(pattern, content)
    if not matches:
        print("  No project.XXX references found")
        return False

    # Get unique incorrect names
    unique_incorrect = set(matches)

    # Replace each incorrect name with the correct one
    changes_made = 0
    for incorrect_name in unique_incorrect:
        if incorrect_name != correct_api_name:
            # Replace project.IncorrectName with project.CorrectName
            old_ref = f'project.{incorrect_name}'
            new_ref = f'project.{correct_api_name}'

            count_before = content.count(old_ref)
            content = content.replace(old_ref, new_ref)
            count_after = content.count(new_ref)

            if count_before > 0:
                print(f"  Replaced {count_before} occurrences of '{old_ref}' with '{new_ref}'")
                changes_made += count_before

    if changes_made > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Total changes: {changes_made}")
        return True
    else:
        print("  No changes needed (already correct)")
        return False


def main():
    """
    Fix all demo files in the examples directory.

    Scans for files matching *_operations_demo.py and corrects
    their project.XXX API references.
    """
    examples_dir = Path(__file__).parent

    demo_files = sorted(examples_dir.glob('*_operations_demo.py'))

    print("=" * 70)
    print("COMPREHENSIVE API NAME FIXER")
    print("="*70)
    print(f"\nFound {len(demo_files)} demo files\n")

    fixed_count = 0
    error_count = 0

    for filepath in demo_files:
        try:
            if fix_api_names_in_file(filepath):
                fixed_count += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            error_count += 1

    print("\n" + "=" * 70)
    print(f"\nFixed: {fixed_count} files")
    print(f"Errors: {error_count} files")
    print("=" * 70)


if __name__ == "__main__":
    main()
