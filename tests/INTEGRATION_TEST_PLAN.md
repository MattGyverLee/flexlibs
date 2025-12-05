# flexlibs Integration Test Plan - Scripture, Discourse, Reversal & Wordform Operations

## Overview

**Project**: flexlibs - FLEx Python Library
**Test Scope**: 18 new Operations classes across 4 feature areas
**Test Period**: Ongoing during development
**QA Agent**: Assigned
**Test Approach**: Unit tests + Integration tests + Demo validation

### Success Criteria

- All CRUD+ methods work correctly across 18 Operations classes
- No data corruption when creating/modifying FLEx objects
- Objects created by flexlibs display correctly in FLEx GUI
- All demo scripts execute without errors
- Parent-child relationships maintained correctly
- Cascade deletes work as expected
- Writing system handling consistent across all classes
- No regression in existing flexlibs functionality

### Test Coverage Goals

- **Unit Tests**: 100% coverage of public CRUD methods
- **Integration Tests**: All parent-child relationships validated
- **Demo Scripts**: All 4 demo scripts pass manual validation
- **FLEx GUI Verification**: Objects viewable and editable in FLEx
- **Error Handling**: All error conditions handled gracefully

---

## Test Matrices

### Work Stream 1: Scripture Operations (6 Classes)

| Class | Create | Find | GetAll | Delete | Properties | Parent-Child | Demo | Status |
|-------|--------|------|--------|--------|-----------|--------------|------|--------|
| **ScrBookOperations** | | | | | | Book contains Sections | | Not Started |
| **ScrSectionOperations** | | | | | | Section contains Paragraphs | | Not Started |
| **ScrSectionHeadOperations** | | | | | | SectionHead part of Section | | Not Started |
| **ScrBookRefOperations** | | | | | | BookRef references canon | | Not Started |
| **ScrImportSetOperations** | | | | | | ImportSet owns mappings | | Not Started |
| **ScrMarkerMappingOperations** | | | | | | Mapping in ImportSet | | Not Started |

**Key Integration Tests:**
- Book → Section → Paragraph hierarchy
- Section heading creation and linking
- Canonical book number validation
- Scripture import mapping workflows
- Cross-reference handling

### Work Stream 2: Discourse Operations (6 Classes)

| Class | Create | Find | GetAll | Delete | Properties | Parent-Child | Demo | Status |
|-------|--------|------|--------|--------|-----------|--------------|------|--------|
| **ConstituentChartOperations** | | | | | | Chart owns Rows | | Not Started |
| **ChartRowOperations** | | | | | | Row owns WordGroups | | Not Started |
| **WordGroupOperations** | | | | | | WordGroup refs Segments | | Not Started |
| **MovedTextMarkerOperations** | | | | | | Marker in chart structure | | Not Started |
| **ClauseMarkerOperations** | | | | | | Marker in chart structure | | Not Started |
| **ChartTemplateOperations** | | | | | | Template for chart types | | Not Started |

**Key Integration Tests:**
- Chart → Row → WordGroup hierarchy
- Text segment linking from chart
- Moved text marker positioning
- Clause marker creation and display
- Template-based chart creation

### Work Stream 3: Reversal & Wordform Operations (6 Classes)

| Class | Create | Find | GetAll | Delete | Properties | Parent-Child | Demo | Status |
|-------|--------|------|--------|--------|-----------|--------------|------|--------|
| **ReversalIndexOperations** | | | | | | Index owns Entries | | Partial (exists) |
| **ReversalEntryOperations** | | | | | | Entry links to Senses | | Partial (exists) |
| **ReversalSubentryOperations** | | | | | | Subentry under Entry | | Not Started |
| **WfiAnalysisOperations** | | | | | | Analysis owns MorphBundles | | Partial (exists) |
| **WfiMorphBundleOperations** | | | | | | Bundle links to Senses | | Partial (exists) |
| **WfiGlossOperations** | | | | | | Gloss part of Analysis | | Partial (exists) |

**Key Integration Tests:**
- ReversalIndex → Entry → Subentry hierarchy
- Reversal entry to lexical sense bidirectional linking
- Wordform → Analysis → MorphBundle → LexSense linking
- Human vs. Parser analysis approval workflow
- Gloss creation and multilingual handling

---

## Test Categories

### 1. Unit Tests (Per Operations Class)

#### Create Tests
- **Test_Create_Minimal**: Create with minimal required parameters
- **Test_Create_WithOptionalParams**: Create with all optional parameters
- **Test_Create_NullParam**: Verify FP_NullParameterError raised
- **Test_Create_EmptyString**: Verify FP_ParameterError for empty strings
- **Test_Create_WritingSystem**: Test multiple writing systems
- **Test_Create_ReadOnly**: Verify FP_ReadOnlyError when project read-only

#### Find Tests
- **Test_Find_Existing**: Find existing object by identifier
- **Test_Find_NonExistent**: Returns None (not error) for missing objects
- **Test_Find_NullParam**: Verify FP_NullParameterError raised
- **Test_Find_CaseSensitivity**: Test case-sensitive search behavior
- **Test_Find_WritingSystem**: Find in specific writing system

#### GetAll Tests
- **Test_GetAll_Empty**: Returns empty iterator for empty collection
- **Test_GetAll_Multiple**: Returns all items when multiple exist
- **Test_GetAll_Iterator**: Verify iterator behavior (not list)
- **Test_GetAll_Count**: Count matches expected number

#### Delete Tests
- **Test_Delete_Existing**: Successfully delete existing object
- **Test_Delete_CascadeChildren**: Verify child objects deleted
- **Test_Delete_NullParam**: Verify FP_NullParameterError raised
- **Test_Delete_NonExistent**: Handle gracefully or raise appropriate error
- **Test_Delete_ReadOnly**: Verify FP_ReadOnlyError when project read-only

#### Property Tests
- **Test_GetProperty_Basic**: Get property returns correct value
- **Test_GetProperty_MultiString**: Get MultiString in various WS
- **Test_GetProperty_NullObject**: Verify FP_NullParameterError raised
- **Test_SetProperty_Basic**: Set property updates correctly
- **Test_SetProperty_MultiString**: Set MultiString in various WS
- **Test_SetProperty_NullParam**: Verify FP_NullParameterError raised
- **Test_SetProperty_ReadOnly**: Verify FP_ReadOnlyError when applicable

### 2. Integration Tests (Cross-Class)

#### Parent-Child Relationships
```python
def test_scripture_book_section_hierarchy():
    """Test Book → Section → Paragraph hierarchy."""
    book = project.ScrBooks.Create(1)  # Genesis
    section = project.ScrSections.Create(book, "Creation")
    para = project.ScrParagraphs.Create(section, "In the beginning...")

    # Verify hierarchy
    assert section.Owner == book
    assert para.Owner == section
    assert section in book.SectionsOS
    assert para in section.ContentOA.ParagraphsOS
```

#### Chart Workflows
```python
def test_discourse_chart_row_wordgroup():
    """Test Chart → Row → WordGroup structure."""
    text = project.Texts.Create("Sample Text")
    chart = project.Charts.Create(text, "Main Chart")
    row = project.ChartRows.Create(chart)
    wordgroup = project.WordGroups.Create(row, segment_ref)

    # Verify structure
    assert row.Owner == chart
    assert wordgroup.Owner == row
    assert chart.RowsOS.Count == 1
```

#### Reversal Linking
```python
def test_reversal_sense_bidirectional_linking():
    """Test ReversalEntry ↔ LexSense bidirectional links."""
    # Create reversal entry
    index = project.ReversalIndexes.GetIndex("en")
    rev_entry = project.ReversalEntries.Create(index, "run")

    # Link to lexical sense
    lex_entry = project.LexEntry.Find("run")
    sense = lex_entry.SensesOS[0]
    project.ReversalEntries.AddSense(rev_entry, sense)

    # Verify bidirectional link
    assert sense in rev_entry.SensesRS
    assert rev_entry in sense.ReferringReversalIndexEntries
```

#### Wordform Analysis
```python
def test_wordform_analysis_morphbundle_chain():
    """Test Wordform → Analysis → MorphBundle → LexSense."""
    # Create wordform
    wf = project.Wordforms.Create("running")

    # Add analysis
    analysis = project.WfiAnalyses.Create(wf)

    # Add morph bundle
    bundle = project.WfiMorphBundles.Create(analysis)

    # Link to sense
    sense = lex_entry.SensesOS[0]
    project.WfiMorphBundles.SetSense(bundle, sense)

    # Verify chain
    assert analysis.Owner == wf
    assert bundle.Owner == analysis
    assert bundle.SenseRA == sense
```

### 3. Error Handling Tests

#### Invalid Parameters
- **Null Objects**: All methods handle None gracefully with FP_NullParameterError
- **Empty Strings**: Methods requiring non-empty strings raise FP_ParameterError
- **Invalid Types**: Type checking for parameters
- **Out of Range**: Index and number validation

#### Non-Existent Objects
- **Find Returns None**: Find methods return None (not exception) for missing objects
- **Delete Missing**: Delete handles missing objects appropriately
- **Get Missing Property**: Property access on invalid object raises appropriate error

#### Permission/Lock Issues
- **Read-Only Project**: All write operations raise FP_ReadOnlyError
- **Locked Objects**: Handle concurrent access gracefully

#### Data Validation
- **Canonical Numbers**: Scripture book numbers must be valid (1-66 or expanded)
- **Writing Systems**: Invalid WS tags handled gracefully
- **Required Fields**: Missing required fields raise FP_ParameterError

### 4. Data Integrity Tests

#### Object Structure Validation
```python
def test_object_not_emaciated():
    """Verify created objects have proper LCM structure."""
    entry = project.LexEntry.Create("test")

    # Check for required properties
    assert hasattr(entry, 'LexemeFormOA')
    assert entry.LexemeFormOA is not None
    assert hasattr(entry, 'SensesOS')

    # Check GUID assigned
    assert entry.Guid is not None
    assert entry.Guid != System.Guid.Empty
```

#### No Orphaned Objects
```python
def test_cascade_delete_no_orphans():
    """Verify deletion removes all child objects."""
    book = project.ScrBooks.Create(1)
    section = project.ScrSections.Create(book, "Test")
    section_guid = section.Guid

    # Delete book
    project.ScrBooks.Delete(book)

    # Verify section also deleted
    try:
        orphan = project.Object(section_guid)
        assert False, "Section should have been deleted"
    except:
        pass  # Expected - section no longer exists
```

#### Factory vs Manual Creation
```python
def test_factory_creation_vs_manual():
    """Compare factory-created objects to manually-created ones."""
    # Create using factory
    factory_entry = project.LexEntry.Create("test1")

    # Create manually (if supported)
    from SIL.LCModel import ILexEntryFactory
    factory = project.project.ServiceLocator.GetService(ILexEntryFactory)
    manual_entry = factory.Create()

    # Compare structure
    assert type(factory_entry) == type(manual_entry)
    assert hasattr(factory_entry, 'LexemeFormOA')
    assert hasattr(manual_entry, 'LexemeFormOA')
```

#### FLEx GUI Compatibility
- **Manual Verification**: Open project in FLEx GUI after creation
- **Edit Test**: Verify objects can be edited in GUI
- **Display Test**: Verify objects display correctly
- **No Validation Errors**: FLEx shows no data validation errors
- **Round-Trip Test**: Edit in GUI, verify changes persist

---

## Test Scenarios

### Scripture Import Scenario

**Objective**: Test complete scripture book creation and management workflow.

**Steps**:
1. Create book (IScrBook) with canonical number 1 (Genesis)
2. Verify book appears in scripture view
3. Add section to book with heading "Creation Account"
4. Add paragraph to section with verse text
5. Verify structure in FLEx GUI (manually)
6. Add second section
7. Delete first section
8. Verify cascade deletion (paragraph also removed)
9. Export to USFM (if supported)
10. Close and reopen project
11. Verify book structure persists

**Expected Results**:
- Book created with correct canonical number
- Sections appear in correct order
- Paragraphs display under sections
- Deletion cascades properly
- No validation errors in FLEx
- Structure survives close/reopen

### Discourse Analysis Scenario

**Objective**: Test constituent chart creation and management.

**Steps**:
1. Create or load text with segments
2. Create constituent chart for text
3. Add first row to chart
4. Add second row to chart
5. Add word group to first row (links to text segment)
6. Add moved text marker
7. Verify chart displays in FLEx GUI (manually)
8. Delete row
9. Verify word groups in row also deleted
10. Close and reopen project
11. Verify chart structure persists

**Expected Results**:
- Chart created and visible
- Rows appear in correct order
- Word groups link correctly to text
- Markers display properly
- Deletion cascades correctly
- Structure survives close/reopen

### Reversal Index Scenario

**Objective**: Test reversal index and entry creation with sense linking.

**Steps**:
1. Create or get English reversal index
2. Create reversal entry "run"
3. Find lexical entry "run" (create if needed)
4. Get first sense of "run"
5. Link reversal entry to sense
6. Verify bidirectional link (sense → reversal, reversal → sense)
7. Create second reversal entry "jog"
8. Link to same sense
9. Verify sense now has two referring reversal entries
10. Export to LIFT
11. Verify reversal entries in LIFT XML
12. Delete reversal entry
13. Verify sense no longer references deleted entry

**Expected Results**:
- Reversal index accessible
- Entries created with correct form
- Bidirectional links work
- Multiple reversal entries can link to one sense
- LIFT export includes reversal data
- Link cleanup on deletion

### Wordform Inventory Scenario

**Objective**: Test wordform, analysis, and morpheme breakdown workflow.

**Steps**:
1. Create wordform "running"
2. Create analysis for wordform
3. Create first morph bundle (root)
4. Link bundle to lexical entry "run"
5. Create second morph bundle (suffix)
6. Link bundle to lexical entry "-ing"
7. Set analysis as human-approved
8. Verify in FLEx Text & Words area (manually)
9. Create second analysis (alternative parse)
10. Verify wordform shows multiple analyses
11. Delete analysis
12. Verify morph bundles also deleted

**Expected Results**:
- Wordform created and findable
- Analyses appear under wordform
- Morph bundles link correctly to lexicon
- Human approval flag works
- Multiple analyses supported
- Deletion cascades properly

---

## Validation Criteria

### Per Operations Class

#### Code Quality
- [ ] All public methods have comprehensive docstrings
- [ ] Docstrings include Args, Returns, Raises sections
- [ ] Example usage provided in docstrings
- [ ] Error handling consistent with flexlibs patterns
- [ ] Follows BaseOperations architecture

#### Method Behavior
- [ ] Create() initializes required fields only (no "emaciation")
- [ ] Create() raises FP_ReadOnlyError if project read-only
- [ ] Create() raises FP_NullParameterError for None parameters
- [ ] Find() returns None (not error) if not found
- [ ] Find() raises FP_NullParameterError for None parameters
- [ ] GetAll() returns iterator (not list)
- [ ] GetAll() returns empty iterator for empty collection
- [ ] Delete() removes object from database
- [ ] Delete() cascades to owned children
- [ ] Delete() raises FP_ReadOnlyError if project read-only

#### Writing System Handling
- [ ] All methods handle ws=None default correctly
- [ ] Default WS is vernacular for lexicon objects
- [ ] Default WS is analysis for gloss/definition
- [ ] MultiString properties support all project WS
- [ ] WS handle vs. WS tag handled consistently

### Integration

#### Parent-Child Relationships
- [ ] Owner property set correctly on child creation
- [ ] Child appears in parent's owning sequence
- [ ] Parent's Count property reflects children
- [ ] Cascade delete removes all descendants

#### Cross-References
- [ ] Sense linking bidirectional (reversal ↔ sense)
- [ ] Reference collections updated on both sides
- [ ] Link removal cleans up both sides
- [ ] Invalid references handled gracefully

#### Writing System Parameters
- [ ] WS respected throughout operation chains
- [ ] MultiString properties preserve all WS alternatives
- [ ] WS switching doesn't corrupt data

### Compatibility

#### FLEx GUI Integration
- [ ] Objects created by flexlibs display correctly in FLEx GUI
- [ ] Objects can be edited in FLEx GUI
- [ ] Changes in GUI persist after close/reopen
- [ ] No data validation errors shown in FLEx
- [ ] Object properties match FLEx-created equivalents

#### Data Integrity
- [ ] No data corruption after operations
- [ ] GUIDs assigned and unique
- [ ] No "emaciated" objects (missing required fields)
- [ ] Proper LCM object structure maintained

#### Export/Import
- [ ] LIFT export includes new object types
- [ ] LIFT import round-trip successful
- [ ] USFM export (scripture) works correctly
- [ ] No data loss in export/import cycle

---

## Test Data Requirements

### Sample FLEx Project
- **Name**: TestProject_Scripture_Discourse_Reversal
- **Type**: Clean project with minimal lexicon (20-30 entries)
- **Writing Systems**:
  - Vernacular: "qaa-x-test" (test language)
  - Analysis: "en" (English)
  - Additional: "es" (Spanish) for multilingual testing
- **Lexicon**: Basic entries for common words (run, walk, house, dog, etc.)
- **Texts**: 1-2 short texts with 10-15 segments each

### Test Scripture Data
- **Book**: Genesis (canonical number 1)
- **Content**: Genesis 1:1-5 (5 verses, 2 sections)
- **Structure**:
  - Section 1: "Creation Account" (verses 1-3)
  - Section 2: "Light and Darkness" (verses 4-5)
- **Paragraphs**: 2 paragraphs per section

### Test Text for Discourse
- **Title**: "Sample Discourse Text"
- **Content**: 3-4 short sentences
- **Segments**: 10-15 segments (words/phrases)
- **Structure**: Clear clause boundaries for charting

### Test Reversal Data
- **Index**: English (en)
- **Entries**: 5-10 entries
- **Coverage**: Common words with multiple senses
- **Links**: Each entry links to 1-3 lexical senses

### Test Wordforms
- **Forms**: 10-15 wordforms
- **Analyses**: Mix of analyzed and unanalyzed
- **Breakdown**: Some with multiple morpheme bundles
- **Status**: Mix of human-approved and parser-generated

---

## Regression Tests

**Objective**: Ensure new Operations don't break existing functionality.

### Existing Operations Tests
- [ ] Run all existing test_*.py files in flexlibs/tests/
- [ ] Verify LexEntry, Sense, Example operations still work
- [ ] Verify writing system handling unchanged
- [ ] Verify FLExProject initialization unchanged

### Demo Scripts
- [ ] Run demo_lexicon.py - verify lexicon operations work
- [ ] Run demo_openproject.py - verify project opening works
- [ ] Run demo_pos_operations.py - verify POS operations work
- [ ] Run demo_writing_systems.py - verify WS operations work

### Performance Tests
- [ ] Measure GetAll() iteration time for large collections
- [ ] Verify no major slowdowns in lexicon access
- [ ] Check memory usage during bulk operations
- [ ] Ensure no memory leaks in object creation/deletion

### Backward Compatibility
- [ ] Old code using FLExProject.LexiconAddEntry() still works
- [ ] Old code using FLExProject.LexiconGetSenseGloss() still works
- [ ] Property access patterns unchanged
- [ ] Exception types unchanged

---

## Test Execution Workflow

### Phase 1: Development Testing (Ongoing)

**Programmer Agents**: Run tests as each method is implemented

1. Write new method
2. Write unit test for method
3. Run test - verify pass
4. Commit code + test
5. Move to next method

### Phase 2: Class Completion Testing

**QA Agent**: Test each complete Operations class

1. Review code for architecture compliance
2. Run all unit tests for class
3. Test error handling edge cases
4. Verify writing system handling
5. Test integration with related classes
6. Document any bugs found

### Phase 3: Integration Testing

**QA Agent**: Test cross-class workflows

1. Run parent-child relationship tests
2. Run cascade delete tests
3. Run cross-reference tests
4. Run complete workflow scenarios
5. Document integration issues

### Phase 4: Demo Validation

**QA Agent + Manual**: Validate demo scripts

1. Run each demo script
2. Open project in FLEx GUI
3. Verify objects display correctly
4. Try editing in FLEx GUI
5. Close and reopen project
6. Verify persistence

### Phase 5: Regression Testing

**QA Agent**: Ensure no breaking changes

1. Run all existing flexlibs tests
2. Run all existing demo scripts
3. Test backward compatibility
4. Check performance
5. Final code review

---

## Bug Tracking

### Bug Priority Levels

**Critical (Blocks Release)**:
- Data corruption
- Crash/exception in core methods
- Create/Delete completely broken
- Cannot open project after operations

**High (Major Functionality Broken)**:
- Find returns wrong object
- GetAll skips objects
- Properties not persisting
- Cascade delete fails

**Medium (Workaround Available)**:
- Error messages unclear
- Edge case handling
- Performance issues
- Missing docstrings

**Low (Cosmetic/Edge Case)**:
- Typos in docstrings
- Formatting issues
- Rare edge cases
- Optional features

### Bug Reporting Process

1. **Discovery**: QA Agent discovers bug during testing
2. **Documentation**: Create bug report using BUG_REPORT_TEMPLATE.md
3. **Assignment**: File bug in test_execution_log.md
4. **Notification**: Alert programmer agent responsible for that class
5. **Verification**: Verify bug is reproducible
6. **Fix**: Programmer agent fixes bug
7. **Re-test**: QA Agent verifies fix
8. **Close**: Mark bug as fixed in log

---

## Test Execution Log Location

**File**: D:\Github\flexlibs\tests\test_execution_log.md

All test results will be logged in this file with:
- Date of test
- Tester name
- Operations class tested
- Test case name
- Pass/Fail status
- Notes/issues

---

## Deliverables Checklist

- [ ] INTEGRATION_TEST_PLAN.md (this document)
- [ ] test_plans/scripture_operations_tests.md
- [ ] test_plans/discourse_operations_tests.md
- [ ] test_plans/reversal_wordform_operations_tests.md
- [ ] demo_validation.md
- [ ] test_execution_log.md
- [ ] BUG_REPORT_TEMPLATE.md
- [ ] All 18 Operations classes have test specifications
- [ ] All 4 demo scripts have validation procedures
- [ ] Bug tracking system operational

---

## Timeline

### Week 1: Test Infrastructure Setup
- [ ] Create all test plan documents
- [ ] Create test matrices
- [ ] Set up test data project
- [ ] Create bug tracking templates

### Week 2: Unit Test Development
- [ ] Write test specifications for all 18 classes
- [ ] Create test helper functions
- [ ] Begin unit test implementation

### Week 3: Integration Testing
- [ ] Run integration test scenarios
- [ ] Test parent-child relationships
- [ ] Test cross-references
- [ ] Demo script validation

### Week 4: Final Validation
- [ ] Regression testing
- [ ] FLEx GUI validation
- [ ] Bug resolution verification
- [ ] Final test report

---

## Contact & Coordination

**QA Agent Responsibilities**:
- Create and maintain test plans
- Execute tests as code is delivered
- File bugs promptly with reproduction steps
- Suggest fixes where possible
- Validate bug fixes
- Maintain test execution log
- Report status to project lead

**Programmer Agent Coordination**:
- Request early code reviews
- Provide test projects if needed
- Clarify expected behavior
- Fix bugs promptly
- Run tests before committing
- Update docstrings based on testing feedback

**Project Lead**:
- Review test plans
- Prioritize bug fixes
- Make architecture decisions
- Approve test scenarios
- Final sign-off on release

---

## Approval

**Test Plan Version**: 1.0
**Date**: 2025-12-05
**Status**: In Development
**Next Review**: After Work Stream 1 completion

---

## Notes

This test plan is a living document and will be updated as development progresses. All testers should check for the latest version before beginning test execution.

**Key Testing Principles**:
1. Test early and often
2. Automate where possible
3. Validate in FLEx GUI manually
4. Document all issues thoroughly
5. Communicate with development team
6. Focus on data integrity
7. Think like a user, test like a QA engineer
