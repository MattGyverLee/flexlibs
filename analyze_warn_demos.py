#!/usr/bin/env python3
"""
Analyze all WARN status demos and categorize their error messages.
"""

import subprocess
import os
from collections import defaultdict

examples_dir = r"d:\Github\flexlibs\examples"

warn_demos = [
    "grammar_morphrule_operations_demo.py",
    "grammar_phoneme_operations_demo.py",
    "grammar_pos_operations_demo.py",
    "lexicon_allomorph_operations_demo.py",
    "lexicon_etymology_operations_demo.py",
    "lexicon_example_operations_demo.py",
    "lexicon_lexreference_operations_demo.py",
    "lexicon_pronunciation_operations_demo.py",
    "lexicon_sense_operations_demo.py",
    "lexicon_variant_operations_demo.py",
    "textswords_media_operations_demo.py",
    "notebook_datanotebook_operations_demo.py",
    "notebook_location_operations_demo.py",
    "notebook_note_operations_demo.py",
    "notebook_person_operations_demo.py",
    "lists_agent_operations_demo.py",
    "lists_confidence_operations_demo.py",
    "lists_overlay_operations_demo.py",
    "lists_possibilitylist_operations_demo.py",
    "lists_publication_operations_demo.py",
    "lists_translationtype_operations_demo.py",
    "system_annotationdef_operations_demo.py",
    "system_check_operations_demo.py",
    "system_customfield_operations_demo.py",
    "system_projectsettings_operations_demo.py",
    "system_writingsystem_operations_demo.py",
    "lexicon_reversal_operations_demo.py",
    "lexicon_semanticdomain_operations_demo.py",
]

print("=" * 80)
print("ANALYZING WARN STATUS DEMOS - ERROR CATEGORIZATION")
print("=" * 80)
print()

# Categories
categories = {
    "Import Error": [],
    "Missing Required Argument": [],
    "Missing Attribute": [],
    "Unicode Display Error": [],
    "Other": []
}

for demo in warn_demos:
    filepath = os.path.join(examples_dir, demo)

    try:
        result = subprocess.run(
            ["python", filepath],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout + result.stderr

        # Extract error lines
        error_lines = [line.strip() for line in output.split('\n') if 'ERROR' in line or 'Error:' in line]

        if not error_lines:
            continue

        # Categorize errors
        for line in error_lines:
            categorized = False

            if 'ImportError' in line or 'cannot import' in line:
                categories["Import Error"].append((demo, line))
                categorized = True
            elif 'missing 1 required positional argument' in line or 'missing required' in line:
                categories["Missing Required Argument"].append((demo, line))
                categorized = True
            elif 'has no attribute' in line or 'object has no attribute' in line:
                categories["Missing Attribute"].append((demo, line))
                categorized = True
            elif 'UnicodeEncodeError' in line or 'Cannot display' in line:
                categories["Unicode Display Error"].append((demo, line))
                categorized = True

            if not categorized:
                categories["Other"].append((demo, line))

    except Exception as e:
        print(f"[SKIP] {demo}: {e}")

# Print results
print("\n" + "=" * 80)
print("CATEGORY 1: IMPORT ERRORS")
print("=" * 80)
print("Severity: CRITICAL - Operations class cannot be used at all")
print()
if categories["Import Error"]:
    seen = set()
    for demo, error in categories["Import Error"]:
        if error not in seen:
            print(f"  {demo}")
            print(f"    {error}")
            seen.add(error)
else:
    print("  None")

print("\n" + "=" * 80)
print("CATEGORY 2: MISSING REQUIRED ARGUMENT")
print("=" * 80)
print("Severity: MEDIUM - Method signature requires parameters (Bug #4)")
print()
if categories["Missing Required Argument"]:
    seen = set()
    for demo, error in categories["Missing Required Argument"]:
        key = error
        if key not in seen:
            print(f"  {demo}")
            print(f"    {error}")
            seen.add(key)
else:
    print("  None")

print("\n" + "=" * 80)
print("CATEGORY 3: MISSING ATTRIBUTE (Wrong Interface)")
print("=" * 80)
print("Severity: MEDIUM - Object returned as generic interface (Bug #2)")
print()
if categories["Missing Attribute"]:
    # Group by error type
    by_attribute = defaultdict(list)
    for demo, error in categories["Missing Attribute"]:
        by_attribute[error].append(demo)

    for error, demos in sorted(by_attribute.items()):
        print(f"  {error}")
        for demo in demos:
            print(f"    - {demo}")
        print()
else:
    print("  None")

print("=" * 80)
print("CATEGORY 4: UNICODE DISPLAY ERRORS")
print("=" * 80)
print("Severity: LOW - Windows console limitation (expected)")
print()
if categories["Unicode Display Error"]:
    demo_count = len(set(demo for demo, _ in categories["Unicode Display Error"]))
    print(f"  {demo_count} demos have Unicode characters that cannot display")
    print("  This is expected for linguistic data (IPA symbols, tone markers, etc.)")
else:
    print("  None")

print("\n" + "=" * 80)
print("CATEGORY 5: OTHER ERRORS")
print("=" * 80)
if categories["Other"]:
    seen = set()
    for demo, error in categories["Other"]:
        if error not in seen:
            print(f"  {demo}")
            print(f"    {error}")
            seen.add(error)
else:
    print("  None")

print("\n" + "=" * 80)
print("SUMMARY BY CATEGORY")
print("=" * 80)
print(f"Import Errors:            {len(set(demo for demo, _ in categories['Import Error']))}")
print(f"Missing Required Args:    {len(set(demo for demo, _ in categories['Missing Required Argument']))}")
print(f"Missing Attributes:       {len(set(demo for demo, _ in categories['Missing Attribute']))}")
print(f"Unicode Display Errors:   {len(set(demo for demo, _ in categories['Unicode Display Error']))}")
print(f"Other:                    {len(set(demo for demo, _ in categories['Other']))}")
print()
print(f"Total WARN demos analyzed: {len(warn_demos)}")
print("=" * 80)
