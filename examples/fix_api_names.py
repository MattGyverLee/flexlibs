#!/usr/bin/env python3
"""
Fix API Attribute Names in CRUD Demos

The converted demos use incorrect API attribute names (title case).
This script fixes them to match the actual FLExProject API.

Author: FlexTools Development Team
Date: 2025-12-04
"""

from pathlib import Path
import re

# Mapping of incorrect names (used in demos) to correct names (actual API)
API_NAME_MAPPING = {
    # Grammar
    'project.Environment': 'project.Environments',
    'project.Gramcat': 'project.GramCat',
    'project.Inflection': 'project.InflectionClasses',  # or another correct name
    'project.Morphrule': 'project.MorphRules',
    'project.Naturalclass': 'project.NaturalClasses',
    'project.Phoneme': 'project.Phonemes',
    'project.Phonrule': 'project.PhonRules',
    'project.Pos': 'project.POS',

    # Lexicon
    'project.Lexentry': 'project.LexEntry',
    'project.Allomorph': 'project.Allomorphs',
    'project.Etymology': 'project.Etymologies',
    'project.Example': 'project.Examples',
    'project.Lexreference': 'project.LexReferences',
    'project.Pronunciation': 'project.Pronunciations',
    'project.Reversal': 'project.Reversals',
    'project.Semanticdomain': 'project.SemanticDomains',
    'project.Sense': 'project.LexSenses',
    'project.Variant': 'project.Variants',

    # Lists
    'project.Agent': 'project.Agents',
    'project.Confidence': 'project.Confidences',
    'project.Overlay': 'project.Overlays',
    'project.Possibilitylist': 'project.PossibilityLists',
    'project.Publication': 'project.Publications',
    'project.Translationtype': 'project.TranslationTypes',

    # Notebook
    'project.Anthropology': 'project.Anthropology',
    'project.Datanotebook': 'project.DataNotebook',
    'project.Location': 'project.Locations',
    'project.Note': 'project.Notes',
    'project.Person': 'project.Persons',

    # System
    'project.Annotationdef': 'project.AnnotationDefs',
    'project.Check': 'project.Checks',
    'project.Customfield': 'project.CustomFields',
    'project.Projectsettings': 'project.ProjectSettings',
    'project.Writingsystem': 'project.WritingSystems',

    # Texts/Words
    'project.Discourse': 'project.Discourses',
    'project.Media': 'project.MediaFiles',
    'project.Paragraph': 'project.Paragraphs',
    'project.Segment': 'project.Segments',
    'project.Text': 'project.Texts',
    'project.Wfianalysis': 'project.WfiAnalyses',
    'project.Wfigloss': 'project.WfiGlosses',
    'project.Wfimorphbundle': 'project.WfiMorphBundles',
    'project.Wordform': 'project.Wordforms',
}


def fix_api_names_in_file(filepath):
    """Fix API attribute names in a demo file."""
    print(f"Fixing {filepath.name}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes_made = 0

    # Apply each mapping
    for incorrect, correct in API_NAME_MAPPING.items():
        if incorrect in content:
            # Replace the API name
            content = content.replace(incorrect, correct)
            changes_made += content.count(correct) - original_content.count(correct)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Fixed {changes_made} occurrences")
        return True
    else:
        print("  No changes needed")
        return False


def main():
    """Fix all demo files."""
    examples_dir = Path(__file__).parent

    demo_files = sorted(examples_dir.glob('*_operations_demo.py'))

    print("="*70)
    print("API NAME FIXER")
    print("="*70)
    print(f"\nFound {len(demo_files)} demo files\n")

    fixed_count = 0
    for filepath in demo_files:
        if fix_api_names_in_file(filepath):
            fixed_count += 1

    print("\n" + "="*70)
    print(f"\nFixed {fixed_count} files")
    print("="*70)


if __name__ == "__main__":
    main()
