"""Analyze test_duplicate_operations.py results"""

import subprocess
import re
from collections import defaultdict

# Run the tests
result = subprocess.run(
    ['python', 'flexlibs/sync/tests/test_duplicate_operations.py'],
    capture_output=True,
    text=True,
    cwd=r'D:\Github\flexlibs',
    timeout=300
)

output = result.stdout + result.stderr

# Parse results
test_pattern = re.compile(r'^test_(\w+) \((__main__\.Test\w+)\).*\.\.\. (ok|ERROR|FAIL|skipped)', re.MULTILINE)
matches = test_pattern.findall(output)

# Categorize by class
results_by_class = defaultdict(lambda: {'ok': 0, 'ERROR': 0, 'FAIL': 0, 'skipped': 0, 'total': 0})
error_details = defaultdict(list)

for test_name, class_name, status in matches:
    class_simple = class_name.replace('__main__.', '')
    results_by_class[class_simple][status] += 1
    results_by_class[class_simple]['total'] += 1

# Get error details
error_pattern = re.compile(r'^ERROR: test_\w+ \((__main__\.Test\w+)\).*?\n(.*?)(?=^======|^------|\Z)', re.MULTILINE | re.DOTALL)
error_matches = error_pattern.findall(output)

for class_name, error_text in error_matches:
    class_simple = class_name.replace('__main__.', '')
    # Extract the actual error message
    lines = error_text.strip().split('\n')
    # Get the last line which usually has the error
    for line in reversed(lines):
        if 'Error' in line or 'Exception' in line:
            error_details[class_simple].append(line.strip())
            break

# Parse summary line
summary_pattern = re.compile(r'Ran (\d+) tests.*?FAILED \(errors=(\d+)(?:, skipped=(\d+))?\)', re.MULTILINE)
summary_match = summary_pattern.search(output)

if summary_match:
    total_tests = int(summary_match.group(1))
    total_errors = int(summary_match.group(2))
    total_skipped = int(summary_match.group(3)) if summary_match.group(3) else 0
    total_passed = total_tests - total_errors - total_skipped
else:
    total_tests = total_errors = total_skipped = total_passed = 0

# Print report
print("=" * 80)
print("DUPLICATE() IMPLEMENTATION TEST RESULTS")
print("=" * 80)
print()
print(f"Total Tests: {total_tests}")
print(f"  Passed: {total_passed}")
print(f"  Errors: {total_errors}")
print(f"  Skipped: {total_skipped}")
print()
print("=" * 80)
print("RESULTS BY CLASS")
print("=" * 80)
print()

# Sort classes by tier
tier1 = ['TestLexSenseDuplicate', 'TestExampleDuplicate', 'TestAllomorphDuplicate',
         'TestPronunciationDuplicate', 'TestVariantDuplicate']
tier2 = ['TestLexEntryDuplicate', 'TestTextDuplicate', 'TestParagraphDuplicate',
         'TestSegmentDuplicate', 'TestMediaDuplicate']
tier3 = ['TestNoteDuplicate', 'TestEtymologyDuplicate', 'TestWfiAnalysisDuplicate',
         'TestWfiGlossDuplicate', 'TestWfiMorphBundleDuplicate', 'TestPhonemeDuplicate',
         'TestNaturalClassDuplicate']

def print_tier_results(tier_name, classes):
    print(f"{tier_name}:")
    print("-" * 80)
    for cls in classes:
        if cls in results_by_class:
            res = results_by_class[cls]
            status = "✓ PASS" if res['ERROR'] == 0 and res['FAIL'] == 0 and res['ok'] > 0 else "✗ FAIL"
            print(f"  {status} {cls:40} (P:{res['ok']:2} E:{res['ERROR']:2} S:{res['skipped']:2} T:{res['total']:2})")

            # Print unique errors for this class
            if cls in error_details and error_details[cls]:
                unique_errors = set(error_details[cls])
                for error in unique_errors:
                    print(f"       └─ {error[:100]}")
    print()

print_tier_results("TIER 1: LEXICON (5 classes)", tier1)
print_tier_results("TIER 2: MIXED (5 classes)", tier2)
print_tier_results("TIER 3: SPECIALIZED (7 classes)", tier3)

# Categorize issues
print("=" * 80)
print("ISSUE CATEGORIES")
print("=" * 80)
print()

all_errors = []
for errors in error_details.values():
    all_errors.extend(errors)

# Count error types
error_types = defaultdict(int)
for error in all_errors:
    if 'AttributeError' in error:
        if 'has no attribute' in error:
            attr_match = re.search(r"has no attribute '(\w+)'", error)
            if attr_match:
                error_types[f"Missing attribute: {attr_match.group(1)}"] += 1
        else:
            error_types["AttributeError (other)"] += 1
    elif 'TypeError' in error:
        error_types["TypeError"] += 1
    elif 'ValueError' in error:
        error_types["ValueError"] += 1
    elif 'NotImplementedError' in error:
        error_types["NotImplementedError"] += 1
    else:
        error_types["Other error"] += 1

for error_type, count in sorted(error_types.items(), key=lambda x: -x[1]):
    print(f"  {count:3} - {error_type}")

print()
print("=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print()
print("Based on the test results, the following issues need to be fixed:")
print()

# Identify common patterns
if any('has no attribute' in e for e in all_errors):
    print("1. ATTRIBUTE ACCESS ISSUES:")
    print("   - Several Duplicate() methods try to access parent object attributes")
    print("   - Parent returned as ICmObject doesn't expose OS properties directly")
    print("   - Need to use GetObject() helper or proper object retrieval")
    print()

if results_by_class['TestMediaDuplicate']['skipped'] == results_by_class['TestMediaDuplicate']['total']:
    print("2. TEST DATA AVAILABILITY:")
    print("   - Media tests all skipped due to no test data")
    print("   - Consider adding media files to test project")
    print()

passing_classes = [cls for cls, res in results_by_class.items()
                   if res['ERROR'] == 0 and res['FAIL'] == 0 and res['ok'] > 0]
if passing_classes:
    print("3. SUCCESSFUL IMPLEMENTATIONS:")
    for cls in passing_classes:
        print(f"   - {cls}: All tests passing")
    print()

print("=" * 80)
print("END OF REPORT")
print("=" * 80)
