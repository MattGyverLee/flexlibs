# CRUD Demo Conversion Plan

**Date**: 2025-11-27
**Status**: In Progress
**Total Files**: 43 operation demos to convert

---

## Overview

Convert all 43 operation demo files from simple method listing to **full CRUD test demos** that perform actual create, read, update, and delete operations on test data.

---

## Conversion Pattern (Template)

### Standard CRUD Flow

Each demo should follow this pattern:

```python
#!/usr/bin/env python3
"""
Full CRUD Demo: [OperationName]Operations for flexlibs

Performs actual create, read, update, and delete operations on test data.
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_[operation]_crud():
    """Demonstrate full CRUD operations."""

    print("=" * 70)
    print("[OPERATION] FULL CRUD TEST")
    print("=" * 70)

    FLExInitialize()
    project = FLExProject()

    try:
        project.OpenProject("Sena 3", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo: {e}")
        FLExCleanup()
        return

    test_obj = None
    test_name = "crud_test_[operation]"

    try:
        # STEP 1: READ - Initial state
        print("\nSTEP 1: READ - Get existing objects")
        initial_count = 0
        for obj in project.[Operation].GetAll():
            # Display object info
            initial_count += 1
            if initial_count >= 5:
                break

        # STEP 2: CREATE
        print("\nSTEP 2: CREATE - Create new test object")
        # Check if exists, delete if needed
        if project.[Operation].Exists(test_name):
            existing = project.[Operation].Find(test_name)
            project.[Operation].Delete(existing)

        # Create new object
        test_obj = project.[Operation].Create(...)
        print(f"  SUCCESS: Created {test_name}")

        # STEP 3: READ - Verify creation
        print("\nSTEP 3: READ - Verify object was created")
        exists = project.[Operation].Exists(test_name)
        found = project.[Operation].Find(test_name)
        current_count = sum(1 for _ in project.[Operation].GetAll())
        print(f"  Count: {initial_count} -> {current_count}")

        # STEP 4: UPDATE
        print("\nSTEP 4: UPDATE - Modify object properties")
        # Update various properties
        project.[Operation].SetProperty(test_obj, new_value)
        print("  UPDATE: SUCCESS")

        # STEP 5: READ - Verify updates
        print("\nSTEP 5: READ - Verify updates persisted")
        updated_obj = project.[Operation].Find(test_name)
        # Verify properties changed

        # STEP 6: DELETE
        print("\nSTEP 6: DELETE - Remove test object")
        project.[Operation].Delete(test_obj)
        still_exists = project.[Operation].Exists(test_name)
        final_count = sum(1 for _ in project.[Operation].GetAll())
        print(f"  DELETE: {'SUCCESS' if not still_exists else 'FAILED'}")

        # SUMMARY
        print("\nCRUD TEST SUMMARY")
        print("  [CREATE] Created test object")
        print("  [READ]   GetAll, Find, Exists, Get methods")
        print("  [UPDATE] Set methods")
        print("  [DELETE] Removed test object")
        print("Test completed successfully!")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # CLEANUP
        print("\nCLEANUP")
        try:
            if project.[Operation].Exists(test_name):
                obj = project.[Operation].Find(test_name)
                project.[Operation].Delete(obj)
                print(f"  Cleaned up: {test_name}")
        except:
            pass

        project.CloseProject()
        FLExCleanup()

    print("\nDEMO COMPLETE")

if __name__ == "__main__":
    print("""
[Operation] Operations - Full CRUD Demo
========================================

Operations Tested:
==================
CREATE: Create(...)
READ:   GetAll(), Find(), Exists(), Get...() methods
UPDATE: Set...() methods
DELETE: Delete()

WARNING: This demo modifies the database!
    """)

    response = input("\nRun CRUD demo? (y/N): ")
    if response.lower() == 'y':
        demo_[operation]_crud()
```

---

## Files to Convert (43 total)

### Category 1: Grammar (9 files)

| File | Status | Priority | Notes |
|------|--------|----------|-------|
| grammar_environment_operations_demo.py | ✅ DONE | High | Template created |
| grammar_gramcat_operations_demo.py | ⏳ TODO | High | Grammatical categories |
| grammar_inflection_operations_demo.py | ⏳ TODO | High | Inflection classes |
| grammar_morphrule_operations_demo.py | ⏳ TODO | Medium | Morph rules |
| grammar_naturalclass_operations_demo.py | ⏳ TODO | Medium | Natural classes |
| grammar_phoneme_operations_demo.py | ⏳ TODO | High | Phoneme inventory |
| grammar_phonrule_operations_demo.py | ⏳ TODO | Medium | Phonological rules |
| grammar_pos_operations_demo.py | ⏳ TODO | High | Parts of speech |

### Category 2: Lexicon (10 files)

| File | Status | Priority | Notes |
|------|--------|----------|-------|
| lexentry_operations_demo.py | ⏳ TODO | High | Already partially done |
| lexicon_allomorph_operations_demo.py | ⏳ TODO | High | Allomorphs |
| lexicon_etymology_operations_demo.py | ⏳ TODO | Low | Etymology |
| lexicon_example_operations_demo.py | ⏳ TODO | High | Example sentences |
| lexicon_lexreference_operations_demo.py | ⏳ TODO | Medium | Lexical relations |
| lexicon_pronunciation_operations_demo.py | ⏳ TODO | Medium | Pronunciations |
| lexicon_reversal_operations_demo.py | ⏳ TODO | Low | Reversal entries |
| lexicon_semanticdomain_operations_demo.py | ⏳ TODO | High | Semantic domains |
| lexicon_sense_operations_demo.py | ⏳ TODO | High | Lexical senses |
| lexicon_variant_operations_demo.py | ⏳ TODO | Medium | Variants |

### Category 3: Lists (6 files)

| File | Status | Priority | Notes |
|------|--------|----------|-------|
| lists_agent_operations_demo.py | ⏳ TODO | Low | Agents |
| lists_confidence_operations_demo.py | ⏳ TODO | Low | Confidence levels |
| lists_overlay_operations_demo.py | ⏳ TODO | Low | Overlays |
| lists_possibilitylist_operations_demo.py | ⏳ TODO | Medium | Possibility lists |
| lists_publication_operations_demo.py | ⏳ TODO | Low | Publications |
| lists_translationtype_operations_demo.py | ⏳ TODO | Low | Translation types |

### Category 4: Notebook (5 files)

| File | Status | Priority | Notes |
|------|--------|----------|-------|
| notebook_anthropology_operations_demo.py | ⏳ TODO | Low | Anthropology |
| notebook_datanotebook_operations_demo.py | ⏳ TODO | Low | Data notebooks |
| notebook_location_operations_demo.py | ⏳ TODO | Low | Locations |
| notebook_note_operations_demo.py | ⏳ TODO | Medium | Notes |
| notebook_person_operations_demo.py | ⏳ TODO | Low | People |

### Category 5: Texts/Words (9 files)

| File | Status | Priority | Notes |
|------|--------|----------|-------|
| textswords_discourse_operations_demo.py | ⏳ TODO | Low | Discourse |
| textswords_media_operations_demo.py | ⏳ TODO | Low | Media |
| textswords_paragraph_operations_demo.py | ⏳ TODO | Medium | Paragraphs |
| textswords_segment_operations_demo.py | ⏳ TODO | Medium | Segments |
| textswords_text_operations_demo.py | ⏳ TODO | High | Texts |
| textswords_wfianalysis_operations_demo.py | ⏳ TODO | Medium | Word analyses |
| textswords_wfigloss_operations_demo.py | ⏳ TODO | Medium | Word glosses |
| textswords_wfimorphbundle_operations_demo.py | ⏳ TODO | Medium | Morph bundles |
| textswords_wordform_operations_demo.py | ⏳ TODO | High | Word forms |

### Category 6: System (5 files)

| File | Status | Priority | Notes |
|------|--------|----------|-------|
| system_annotationdef_operations_demo.py | ⏳ TODO | Low | Annotation defs |
| system_check_operations_demo.py | ⏳ TODO | Low | Checks |
| system_customfield_operations_demo.py | ⏳ TODO | Medium | Custom fields |
| system_projectsettings_operations_demo.py | ⏳ TODO | Low | Project settings |
| system_writingsystem_operations_demo.py | ⏳ TODO | High | Writing systems |

---

## Conversion Strategy

### Phase 1: High-Priority Conversions (12 files)
**Goal**: Convert most commonly used operations first

1. **Grammar** (4 files):
   - grammar_pos_operations_demo.py
   - grammar_phoneme_operations_demo.py
   - grammar_gramcat_operations_demo.py
   - grammar_inflection_operations_demo.py

2. **Lexicon** (5 files):
   - lexicon_sense_operations_demo.py
   - lexicon_example_operations_demo.py
   - lexicon_allomorph_operations_demo.py
   - lexicon_semanticdomain_operations_demo.py
   - lexentry_operations_demo.py (update existing)

3. **Texts** (2 files):
   - textswords_text_operations_demo.py
   - textswords_wordform_operations_demo.py

4. **System** (1 file):
   - system_writingsystem_operations_demo.py

### Phase 2: Medium-Priority Conversions (12 files)
**Goal**: Convert secondary operations

1. **Grammar** (3 files):
   - grammar_morphrule_operations_demo.py
   - grammar_naturalclass_operations_demo.py
   - grammar_phonrule_operations_demo.py

2. **Lexicon** (3 files):
   - lexicon_variant_operations_demo.py
   - lexicon_lexreference_operations_demo.py
   - lexicon_pronunciation_operations_demo.py

3. **Texts** (5 files):
   - textswords_paragraph_operations_demo.py
   - textswords_segment_operations_demo.py
   - textswords_wfianalysis_operations_demo.py
   - textswords_wfigloss_operations_demo.py
   - textswords_wfimorphbundle_operations_demo.py

4. **Lists** (1 file):
   - lists_possibilitylist_operations_demo.py

5. **Notebook** (1 file):
   - notebook_note_operations_demo.py

6. **System** (1 file):
   - system_customfield_operations_demo.py

### Phase 3: Low-Priority Conversions (19 files)
**Goal**: Complete remaining operations

1. **Lexicon** (2 files):
   - lexicon_etymology_operations_demo.py
   - lexicon_reversal_operations_demo.py

2. **Lists** (5 files):
   - lists_agent_operations_demo.py
   - lists_confidence_operations_demo.py
   - lists_overlay_operations_demo.py
   - lists_publication_operations_demo.py
   - lists_translationtype_operations_demo.py

3. **Notebook** (4 files):
   - notebook_anthropology_operations_demo.py
   - notebook_datanotebook_operations_demo.py
   - notebook_location_operations_demo.py
   - notebook_person_operations_demo.py

4. **Texts** (2 files):
   - textswords_discourse_operations_demo.py
   - textswords_media_operations_demo.py

5. **System** (3 files):
   - system_annotationdef_operations_demo.py
   - system_check_operations_demo.py
   - system_projectsettings_operations_demo.py

---

## Implementation Plan

### Step-by-Step Process

For each file:

1. **Analyze Original**
   - Read original demo file
   - Identify available methods
   - Note method signatures (Create, Get, Set, Delete)

2. **Convert to CRUD Pattern**
   - Follow template structure
   - Implement 6 steps: READ → CREATE → READ → UPDATE → READ → DELETE
   - Add proper error handling
   - Include cleanup in finally block

3. **Add Test Logic**
   - Verify each operation succeeded
   - Count objects before/after
   - Check existence with Find/Exists
   - Validate property updates

4. **Add Documentation**
   - List all methods tested
   - Document test flow
   - Add warnings about database modification
   - Include usage examples

5. **Test Execution**
   - Run on test project
   - Verify all steps pass
   - Check cleanup works
   - Document any issues

---

## Automation Script

Create a conversion script to speed up the process:

```python
#!/usr/bin/env python3
"""
Automated CRUD Demo Converter

Converts simple demo files to full CRUD test demos.
"""

import re
import os

def convert_demo_file(input_file, output_file):
    """Convert a demo file to CRUD format."""

    # Read original
    with open(input_file, 'r') as f:
        content = f.read()

    # Extract operation name
    match = re.search(r'(\w+)_operations_demo\.py', input_file)
    if not match:
        return False

    operation_name = match.group(1).title()

    # Generate CRUD demo from template
    crud_demo = generate_crud_demo(operation_name, content)

    # Write output
    with open(output_file, 'w') as f:
        f.write(crud_demo)

    return True

def generate_crud_demo(operation_name, original_content):
    """Generate CRUD demo code."""
    # Extract methods from original
    methods = extract_methods(original_content)

    # Use template and fill in operation-specific details
    template = load_crud_template()

    return template.format(
        operation=operation_name,
        methods=methods,
        # ... other placeholders
    )

# Run conversion for all files
if __name__ == "__main__":
    for file in get_demo_files():
        print(f"Converting {file}...")
        convert_demo_file(file, file)
```

---

## Testing Plan

### Test Matrix

For each converted demo:

| Test | Description | Expected Result |
|------|-------------|-----------------|
| **Syntax** | Python syntax valid | No syntax errors |
| **Import** | Module imports work | No import errors |
| **Connect** | Connects to FLEx | Opens project |
| **CREATE** | Creates test object | Object created |
| **READ** | Finds created object | Object found |
| **UPDATE** | Modifies properties | Changes persist |
| **DELETE** | Removes object | Object deleted |
| **Cleanup** | Removes test data | Database clean |

### Test Execution

```bash
# Test individual demo
cd examples
python grammar_environment_operations_demo.py

# Test all demos (automated)
python run_all_crud_demos.py

# Generate test report
python generate_crud_test_report.py > CRUD_TEST_RESULTS.md
```

---

## Progress Tracking

### Current Status

- **Total Files**: 43
- **Completed**: 1 (2.3%)
- **In Progress**: 0
- **Remaining**: 42 (97.7%)

### Completion Targets

- **Phase 1**: 12 files (27.9%) - Target: 1-2 days
- **Phase 2**: 12 files (27.9%) - Target: 1-2 days
- **Phase 3**: 19 files (44.2%) - Target: 2-3 days

**Total Estimated Time**: 4-7 days for all conversions and testing

---

## Quality Checklist

For each converted demo:

- [ ] Follows standard CRUD pattern
- [ ] Has all 6 steps (READ → CREATE → READ → UPDATE → READ → DELETE)
- [ ] Includes error handling
- [ ] Has cleanup in finally block
- [ ] Counts objects before/after
- [ ] Verifies operations succeeded
- [ ] Documents all methods tested
- [ ] Includes usage warning
- [ ] Has user prompt before running
- [ ] Tested on actual FLEx project
- [ ] Cleanup verified to work
- [ ] No test data left behind

---

## Benefits of Full CRUD Demos

### For Users
- **Confidence**: See operations actually work
- **Learning**: Understand proper usage patterns
- **Testing**: Verify their installation works
- **Examples**: Copy/paste working code

### For Developers
- **Validation**: Ensure API works correctly
- **Regression**: Catch breaking changes
- **Documentation**: Live code examples
- **Coverage**: Test all methods

### For Project
- **Quality**: Higher code quality
- **Trust**: Users trust tested code
- **Support**: Fewer support issues
- **Adoption**: More likely to use

---

## Next Steps

1. **Complete Phase 1 conversions** (12 high-priority files)
2. **Test all Phase 1 demos** on test project
3. **Document any issues** found during testing
4. **Create automation script** to speed up remaining conversions
5. **Complete Phase 2 conversions** (12 medium-priority files)
6. **Complete Phase 3 conversions** (19 low-priority files)
7. **Create comprehensive test suite** to run all demos
8. **Generate test report** showing all demos pass

---

**Document Version**: 1.0
**Last Updated**: 2025-11-27
**Status**: Plan Complete, Ready for Implementation
