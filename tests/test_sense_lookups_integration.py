#!/usr/bin/env python3
"""
Integration Test: Sense Lookup Methods with Real Project Data

Tests sense lookup methods using actual possibility list items from the
Test FLEx project. This ensures the feature works with real data, not
assumed test data.

Author: Claude Code
Date: 2026-02-21
"""

import sys
import os
import traceback
from typing import List, Dict, Tuple, Optional

# Add project root to path
_test_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_test_dir)
sys.path.insert(0, _project_root)

# Import FLEx modules
try:
    from flexlibs2 import FLExProject, FLExInitialize, FLExCleanup
except ImportError as e:
    print(f"[ERROR] Failed to import flexlibs2: {e}")
    sys.exit(1)


def discover_possibility_lists(project: FLExProject) -> Dict[str, List[str]]:
    """
    Discover all available possibility lists and their items in the project.

    Returns:
        Dict mapping list names to lists of available item names
    """
    discovered = {}

    try:
        poss_lists = list(project.PossibilityLists.GetAllLists())
        print(f"[INFO] Found {len(poss_lists)} possibility lists")

        for poss_list in poss_lists:
            # Use GetListName to properly get the list name
            list_name = project.PossibilityLists.GetListName(poss_list)
            if not list_name:
                continue  # Skip lists with no name

            # Get items from this list
            items = []
            try:
                all_items = list(project.PossibilityLists.GetItems(poss_list, flat=True))
                for item in all_items:
                    # Use GetItemName to properly get the item name
                    item_name = project.PossibilityLists.GetItemName(item)
                    if item_name:
                        items.append(item_name)
            except Exception as e:
                print(f"  [WARN] Failed to get items from {list_name}: {e}")
                continue

            if items:
                discovered[list_name] = items
                print(f"  [OK] {list_name}: {len(items)} items")
                if len(items) <= 5:
                    for item in items:
                        print(f"       - {item}")
                else:
                    for item in items[:3]:
                        print(f"       - {item}")
                    print(f"       ... and {len(items) - 3} more")

    except Exception as e:
        print(f"[ERROR] Failed to discover possibility lists: {e}")
        traceback.print_exc()

    return discovered


def test_sense_lookups_with_real_data():
    """
    Test sense lookup methods with real data from the Test project.
    """
    print("=" * 70)
    print("SENSE LOOKUP INTEGRATION TEST - Real Data from Test Project")
    print("=" * 70)
    print()

    try:
        # Initialize FLEx
        print("[INFO] Initializing FLEx...")
        FLExInitialize()

        # Open Test project in write mode
        print("[INFO] Opening Test FLEx project...")
        project = FLExProject()
        project.OpenProject("test", writeEnabled=True)
        print("[OK] Test project opened successfully")
        print()

        # Discover what possibility lists exist
        print("-" * 70)
        print("STEP 1: Discover Possibility Lists in Project")
        print("-" * 70)
        print()

        discovered = discover_possibility_lists(project)
        print()

        # Find the key lists we need for testing
        usage_types_list = None
        semantic_domains_list = None
        anthro_categories_list = None

        for list_name, items in discovered.items():
            if "usage" in list_name.lower() or "type" in list_name.lower():
                usage_types_list = (list_name, items)
                print(f"[OK] Found Usage Types list: {list_name}")
            if "semantic" in list_name.lower() or "domain" in list_name.lower():
                semantic_domains_list = (list_name, items)
                print(f"[OK] Found Semantic Domains list: {list_name}")
            if "anthro" in list_name.lower() or "categor" in list_name.lower():
                anthro_categories_list = (list_name, items)
                print(f"[OK] Found Anthropology Categories list: {list_name}")

        print()

        # Test sense lookups with real data
        print("-" * 70)
        print("STEP 2: Test Sense Lookups with Real Data")
        print("-" * 70)
        print()

        test_results = {
            'usage_type': None,
            'semantic_domain': None,
            'anthro_code': None
        }

        # Create a test entry
        test_entry = project.LexEntry.Create("test_sense_lookups")
        test_sense = project.Senses.Create(test_entry, "test_definition")

        print(f"Created test entry: {test_entry.Hvo}")
        print(f"Created test sense: {test_sense.Hvo}")
        print()

        # Test 1: Usage Type
        # Try to find "Usages" list which has the actual usage items in FLEx
        usages_list = discovered.get("Usages")
        if usages_list:
            list_name = "Usages"
            items = usages_list
            if items:
                test_item = items[0]
                print(f"TEST 1: AddUsageType with '{test_item}' from 'Usages' list")
                try:
                    project.Senses.AddUsageType(test_sense, test_item)
                    print(f"  [OK] Successfully added usage type '{test_item}' by string")
                    test_results['usage_type'] = True
                except Exception as e:
                    print(f"  [FAIL] Error: {e}")
                    # Try with the FLEx list name instead of "Usage Types"
                    try:
                        print(f"  [INFO] Implementation uses 'Usage Types' but project has 'Usages' - this is a configuration issue")
                        test_results['usage_type'] = False
                    except:
                        pass
                print()
        else:
            print("TEST 1: AddUsageType - SKIPPED (no Usages list found)")
            print()

        # Create another sense for next test
        test_sense2 = project.Senses.Create(test_entry, "test_definition_2")

        # Test 2: Semantic Domain
        # Use "Semantic Domains" list which is the standard FLEx semantic domain list
        sem_domains_list = discovered.get("Semantic Domains")
        if sem_domains_list:
            list_name = "Semantic Domains"
            items = sem_domains_list
            if items:
                test_item = items[0]
                print(f"TEST 2: AddDomainType with '{test_item}'")
                try:
                    project.Senses.AddDomainType(test_sense2, test_item)
                    print(f"  [OK] Successfully added semantic domain '{test_item}' by string")
                    test_results['semantic_domain'] = True
                except Exception as e:
                    print(f"  [FAIL] Error: {e}")
                    test_results['semantic_domain'] = False
                print()
        else:
            print("TEST 2: AddDomainType - SKIPPED (no Semantic Domains list found)")
            print()

        # Create another sense for next test
        test_sense3 = project.Senses.Create(test_entry, "test_definition_3")

        # Test 3: Anthropology Code
        if anthro_categories_list:
            list_name, items = anthro_categories_list
            if items:
                test_item = items[0]
                print(f"TEST 3: AddAnthroCode with '{test_item}'")
                try:
                    project.Senses.AddAnthroCode(test_sense3, test_item)
                    print(f"  [OK] Successfully added anthropology code '{test_item}' by string")
                    test_results['anthro_code'] = True
                except Exception as e:
                    print(f"  [FAIL] Error: {e}")
                    test_results['anthro_code'] = False
                print()
        else:
            print("TEST 3: AddAnthroCode - SKIPPED (no Anthropology Categories list found)")
            print()

        # Summary
        print("-" * 70)
        print("TEST RESULTS SUMMARY")
        print("-" * 70)
        print()

        passed = sum(1 for v in test_results.values() if v is True)
        total = sum(1 for v in test_results.values() if v is not None)
        skipped = sum(1 for v in test_results.values() if v is None)

        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Skipped: {skipped}")
        print()

        if passed == total and total > 0:
            print("[OK] All sense lookup tests PASSED!")
            exit_code = 0
        elif total == 0:
            print("[WARN] All tests skipped - project may not have required possibility lists")
            exit_code = 0
        else:
            print(f"[FAIL] {total - passed} test(s) failed")
            exit_code = 1

        # Cleanup
        print()
        print("[INFO] Cleaning up test data...")
        try:
            project.Senses.Delete(test_sense)
            project.Senses.Delete(test_sense2)
            project.Senses.Delete(test_sense3)
            project.LexEntry.Delete(test_entry)
            print("[OK] Test data cleaned up")
        except Exception as e:
            print(f"[WARN] Error during cleanup: {e}")

        return exit_code

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        traceback.print_exc()
        return 1

    finally:
        # Close project and cleanup
        try:
            if 'project' in locals():
                project.CloseProject()
                print("[OK] Test project closed")
        except Exception as e:
            print(f"[WARN] Error closing project: {e}")

        try:
            FLExCleanup()
            print("[OK] FLEx cleaned up")
        except Exception as e:
            print(f"[WARN] Error in FLEx cleanup: {e}")


if __name__ == "__main__":
    exit_code = test_sense_lookups_with_real_data()
    sys.exit(exit_code)
