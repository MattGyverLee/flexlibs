#!/usr/bin/env python3
"""
Run All CRUD Demos - Test Suite Runner

Executes all 43 CRUD operation demos sequentially and reports results.
Each demo is run in the same process to share FLEx initialization.

Author: FlexTools Development Team
Date: 2025-12-04
"""

import sys
import traceback
from pathlib import Path
from datetime import datetime

# Import all demo modules
demo_modules = [
    # Grammar module
    'grammar_environment_operations_demo',
    'grammar_gramcat_operations_demo',
    'grammar_inflection_operations_demo',
    'grammar_morphrule_operations_demo',
    'grammar_naturalclass_operations_demo',
    'grammar_phoneme_operations_demo',
    'grammar_phonrule_operations_demo',
    'grammar_pos_operations_demo',

    # Lexicon module
    'lexentry_operations_demo',
    'lexicon_allomorph_operations_demo',
    'lexicon_etymology_operations_demo',
    'lexicon_example_operations_demo',
    'lexicon_lexreference_operations_demo',
    'lexicon_pronunciation_operations_demo',
    'lexicon_reversal_operations_demo',
    'lexicon_semanticdomain_operations_demo',
    'lexicon_sense_operations_demo',
    'lexicon_variant_operations_demo',

    # Lists module
    'lists_agent_operations_demo',
    'lists_confidence_operations_demo',
    'lists_overlay_operations_demo',
    'lists_possibilitylist_operations_demo',
    'lists_publication_operations_demo',
    'lists_translationtype_operations_demo',

    # Notebook module
    'notebook_anthropology_operations_demo',
    'notebook_datanotebook_operations_demo',
    'notebook_location_operations_demo',
    'notebook_note_operations_demo',
    'notebook_person_operations_demo',

    # System module
    'system_annotationdef_operations_demo',
    'system_check_operations_demo',
    'system_customfield_operations_demo',
    'system_projectsettings_operations_demo',
    'system_writingsystem_operations_demo',

    # Texts/Words module
    'textswords_discourse_operations_demo',
    'textswords_media_operations_demo',
    'textswords_paragraph_operations_demo',
    'textswords_segment_operations_demo',
    'textswords_text_operations_demo',
    'textswords_wfianalysis_operations_demo',
    'textswords_wfigloss_operations_demo',
    'textswords_wfimorphbundle_operations_demo',
    'textswords_wordform_operations_demo',
]


def extract_operation_name(module_name):
    """Extract display name from module name."""
    name = module_name.replace('_operations_demo', '')
    # Capitalize each part
    parts = name.split('_')
    return ' '.join(p.capitalize() for p in parts)


def run_single_demo(module_name):
    """Run a single CRUD demo and return result."""
    operation_name = extract_operation_name(module_name)

    print("\n" + "="*80)
    print(f"TESTING: {operation_name}")
    print("="*80)

    try:
        # Import the module
        module = __import__(module_name)

        # Extract operation short name for function
        # e.g., "grammar_pos_operations_demo" -> "pos"
        short_name = module_name.replace('_operations_demo', '')
        if '_' in short_name:
            parts = short_name.split('_', 1)
            if len(parts) > 1:
                short_name = parts[1]

        # Get the CRUD function
        func_name = f"demo_{short_name}_crud"

        if hasattr(module, func_name):
            func = getattr(module, func_name)

            # Run the demo
            func()

            print(f"\n[SUCCESS] {operation_name} demo completed")
            return {
                'module': module_name,
                'operation': operation_name,
                'status': 'SUCCESS',
                'error': None
            }
        else:
            print(f"\n[SKIP] Function {func_name} not found in module")
            return {
                'module': module_name,
                'operation': operation_name,
                'status': 'SKIP',
                'error': f"Function {func_name} not found"
            }

    except Exception as e:
        error_msg = str(e)
        print(f"\n[FAILED] {operation_name} demo failed: {error_msg}")
        traceback.print_exc()

        return {
            'module': module_name,
            'operation': operation_name,
            'status': 'FAILED',
            'error': error_msg
        }


def print_summary(results):
    """Print test summary."""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed_count = sum(1 for r in results if r['status'] == 'FAILED')
    skip_count = sum(1 for r in results if r['status'] == 'SKIP')

    print(f"\nTotal Demos:    {len(results)}")
    print(f"Success:        {success_count} ({success_count/len(results)*100:.1f}%)")
    print(f"Failed:         {failed_count} ({failed_count/len(results)*100:.1f}%)")
    print(f"Skipped:        {skip_count} ({skip_count/len(results)*100:.1f}%)")

    # Show failures
    if failed_count > 0:
        print("\n" + "-"*80)
        print("FAILED DEMOS:")
        print("-"*80)
        for r in results:
            if r['status'] == 'FAILED':
                print(f"  - {r['operation']}")
                print(f"    Error: {r['error']}")

    # Show skipped
    if skip_count > 0:
        print("\n" + "-"*80)
        print("SKIPPED DEMOS:")
        print("-"*80)
        for r in results:
            if r['status'] == 'SKIP':
                print(f"  - {r['operation']}")
                print(f"    Reason: {r['error']}")

    print("\n" + "="*80)

    return success_count, failed_count, skip_count


def save_report(results, start_time, end_time):
    """Save detailed test report."""
    report_file = Path(__file__).parent.parent / 'docs' / 'CRUD_TEST_REPORT.md'

    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed_count = sum(1 for r in results if r['status'] == 'FAILED')
    skip_count = sum(1 for r in results if r['status'] == 'SKIP')

    duration = (end_time - start_time).total_seconds()

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# CRUD Demo Test Report\n\n")
        f.write(f"**Date**: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Duration**: {duration:.1f} seconds\n")
        f.write(f"**Total Demos**: {len(results)}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Success**: {success_count} ({success_count/len(results)*100:.1f}%)\n")
        f.write(f"- **Failed**: {failed_count} ({failed_count/len(results)*100:.1f}%)\n")
        f.write(f"- **Skipped**: {skip_count} ({skip_count/len(results)*100:.1f}%)\n\n")

        f.write("## Detailed Results\n\n")
        f.write("| Operation | Module | Status | Error |\n")
        f.write("|-----------|--------|--------|-------|\n")

        for r in results:
            error_str = r['error'] if r['error'] else '-'
            # Escape pipe characters in error messages
            error_str = error_str.replace('|', '\\|')
            status_icon = {
                'SUCCESS': '[OK]',
                'FAILED': '[FAIL]',
                'SKIP': '[SKIP]'
            }.get(r['status'], '?')

            f.write(f"| {r['operation']} | {r['module']} | {status_icon} {r['status']} | {error_str} |\n")

        f.write("\n## Failed Demos\n\n")
        if failed_count > 0:
            for r in results:
                if r['status'] == 'FAILED':
                    f.write(f"### {r['operation']}\n\n")
                    f.write(f"**Module**: `{r['module']}`\n\n")
                    f.write(f"**Error**: {r['error']}\n\n")
        else:
            f.write("No failures!\n\n")

        f.write("\n## Skipped Demos\n\n")
        if skip_count > 0:
            for r in results:
                if r['status'] == 'SKIP':
                    f.write(f"### {r['operation']}\n\n")
                    f.write(f"**Module**: `{r['module']}`\n\n")
                    f.write(f"**Reason**: {r['error']}\n\n")
        else:
            f.write("No skipped demos!\n\n")

    print(f"\nDetailed report saved to: {report_file}")


def main():
    """Run all CRUD demos."""
    print("="*80)
    print("CRUD DEMO TEST SUITE")
    print("="*80)
    print(f"\nTotal demos to run: {len(demo_modules)}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    start_time = datetime.now()
    results = []

    for i, module_name in enumerate(demo_modules, 1):
        print(f"\n[{i}/{len(demo_modules)}]", end=' ')
        result = run_single_demo(module_name)
        results.append(result)

    end_time = datetime.now()

    # Print summary
    success_count, failed_count, skip_count = print_summary(results)

    # Save report
    save_report(results, start_time, end_time)

    print(f"\nEnd time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {(end_time - start_time).total_seconds():.1f} seconds")

    # Exit with appropriate code
    if failed_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
