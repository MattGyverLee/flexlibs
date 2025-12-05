# flexlibs Implementation Plan - Scripture, Discourse, Reversal & Wordform Operations

## Project Overview

**Objective**: Implement full CRUD+ operations for 4 major FLEx feature areas based on the FIELDWORKS_FEATURE_AUDIT findings.

**Timeline**: Estimated 4 parallel work streams

**Team Structure**:
- **Project Lead**: Coordination and architecture review
- **Programmer Agent 1**: Scripture Import Operations
- **Programmer Agent 2**: Discourse Analysis Operations
- **Programmer Agent 3**: Reversal Index & Wordform Operations
- **QA Agent**: Test plans, validation, integration testing

---

## Work Stream 1: Scripture Import Operations (Programmer Agent 1)

### Scope
Implement operations for importing and analyzing Scripture from Paratext.

### Interfaces to Implement (Priority Order)

#### 1.1 **IScrBook** (HIGH)
**File**: `flexlibs/code/Scripture/ScrBookOperations.py`

**CRUD Methods**:
- `GetAll()` → All Scripture books in project
- `Find(book_id)` → Find by canonical book ID (e.g., "GEN", "MAT")
- `GetName(book)` → Get book name
- `GetCanonicalNum(book)` → Get canonical number (1-66)
- `GetTitle(book)` → Get book title
- `GetAbbreviation(book)` → Get book abbreviation
- `GetSections(book)` → Get all sections in book
- `GetFootnotes(book)` → Get book footnotes collection

**No Create/Delete**: Scripture books imported from Paratext, not created in FLEx

**Dependencies**: IScrSection, IStText

#### 1.2 **IScrSection** (HIGH)
**File**: `flexlibs/code/Scripture/ScrSectionOperations.py`

**CRUD Methods**:
- `GetAll(book)` → All sections in book
- `GetHeading(section)` → Section heading text
- `GetContent(section)` → Section content (StText)
- `GetStartRef(section)` → Start verse reference
- `GetEndRef(section)` → End verse reference
- `GetParagraphs(section)` → Paragraphs in section

**No Create/Delete**: Sections imported from Paratext

**Dependencies**: IScrTxtPara, IStText, IScrBook

#### 1.3 **IScrTxtPara** (MEDIUM)
**File**: `flexlibs/code/Scripture/ScrTxtParaOperations.py`

**Methods** (extends StTxtPara):
- Inherit from existing `ParagraphOperations` where possible
- `GetVerseNumbers(para)` → Extract verse numbers
- `GetText(para)` → Get paragraph text
- Scripture-specific: Handle verse number markers

**Dependencies**: Existing ParagraphOperations

#### 1.4 **IScrDraft** (LOW)
**File**: `flexlibs/code/Scripture/ScrDraftOperations.py`

**Methods**:
- `GetAll()` → All archived drafts
- `GetBooks(draft)` → Books in draft
- `GetDescription(draft)` → Draft description
- Used for import undo/comparison

**Dependencies**: IScrBook

#### 1.5 **IScrBookAnnotations** (LOW)
**File**: `flexlibs/code/Scripture/ScrAnnotationsOperations.py`

**Methods**:
- `GetAll(book)` → Annotations for book
- `GetNotes(annotations)` → Notes collection
- Container for IScrScriptureNote

#### 1.6 **IScrScriptureNote** (LOW)
**File**: `flexlibs/code/Scripture/ScrNoteOperations.py`

**Methods**:
- `GetText(note)` → Note text
- `GetType(note)` → Note type (consultant, translator, check)
- `GetReference(note)` → Scripture reference

**Deliverables**:
- 6 new Operations classes
- Demo script: `examples/scripture_import_demo.py`
- Unit tests: `tests/test_scripture_operations.py`
- Documentation: `docs/operations/Scripture_README.md`

---

## Work Stream 2: Discourse Analysis Operations (Programmer Agent 2)

### Scope
Implement operations for Constituent Chart discourse analysis.

### Interfaces to Implement (Priority Order)

#### 2.1 **IDsConstChart** (HIGH)
**File**: `flexlibs/code/Discourse/ConstChartOperations.py`

**CRUD Methods**:
- `GetAll(text)` → All charts for text
- `Create(text, template)` → Create new chart
- `Delete(chart)` → Delete chart
- `GetRows(chart)` → Get all rows
- `GetTemplate(chart)` → Get chart template
- `SetTemplate(chart, template)` → Change template
- `GetBasedOn(chart)` → Get source text
- `AddRow(chart, position)` → Add row

**Dependencies**: IConstChartRow, IText

#### 2.2 **IConstChartRow** (HIGH) - MOST USED
**File**: `flexlibs/code/Discourse/ConstChartRowOperations.py`

**CRUD Methods**:
- `GetAll(chart)` → All rows in chart
- `Create(chart, after_row)` → Create new row
- `Delete(row)` → Delete row
- `Move(row, new_position)` → Reorder rows
- `GetCells(row)` → Get cell contents
- `GetLabel(row)` → Row label/number
- `GetClauseType(row)` → Clause type
- `AddWordGroup(row, column, wordform)` → Add word group to cell
- `AddMovedTextMarker(row, column, target)` → Add moved text marker
- `AddClauseMarker(row)` → Add clause marker
- `AddTag(row, column, tag)` → Add cell tag

**Dependencies**: IConstChartWordGroup, IConstChartMovedTextMarker, etc.

#### 2.3 **IConstChartWordGroup** (HIGH)
**File**: `flexlibs/code/Discourse/ConstChartWordGroupOperations.py`

**CRUD Methods**:
- `GetAll(row)` → All word groups in row
- `Create(row, column, begin_seg, end_seg)` → Create word group
- `Delete(wordgroup)` → Delete word group
- `GetColumn(wordgroup)` → Get column index
- `SetColumn(wordgroup, column)` → Move to column
- `GetSegmentRange(wordgroup)` → Get begin/end segments
- `GetText(wordgroup)` → Get displayed text

**Dependencies**: ISegment (from Texts)

#### 2.4 **IConstChartMovedTextMarker** (MEDIUM)
**File**: `flexlibs/code/Discourse/ConstChartMovedTextOperations.py`

**CRUD Methods**:
- `GetAll(row)` → All moved text markers
- `Create(row, column, wordgroup, preposed)` → Create marker
- `Delete(marker)` → Delete marker
- `GetWordGroup(marker)` → Get target word group
- `IsPreposed(marker)` → Check if preposed
- `GetColumn(marker)` → Get marker column

#### 2.5 **IConstChartTag** (MEDIUM)
**File**: `flexlibs/code/Discourse/ConstChartTagOperations.py`

**CRUD Methods**:
- `GetAll(row)` → All tags
- `Create(row, column, tag_text)` → Create tag
- `Delete(tag)` → Delete tag
- `GetTag(tag)` → Get tag text
- `SetTag(tag, text)` → Update tag

#### 2.6 **IConstChartClauseMarker** (LOW)
**File**: `flexlibs/code/Discourse/ConstChartClauseMarkerOperations.py`

**CRUD Methods**:
- `GetAll(row)` → All clause markers
- `Create(row, dependent_clauses)` → Create marker
- `Delete(marker)` → Delete marker
- `GetDependentClauses(marker)` → Get dependent clause refs

**Deliverables**:
- 6 new Operations classes
- Demo script: `examples/discourse_chart_demo.py`
- Unit tests: `tests/test_discourse_operations.py`
- Documentation: `docs/operations/Discourse_README.md`

---

## Work Stream 3: Reversal & Wordform Operations (Programmer Agent 3)

### Scope
Implement Reversal Index operations AND Wordform Inventory operations.

### Part A: Reversal Index Operations

#### 3.1 **IReversalIndex** (HIGH)
**File**: `flexlibs/code/Lexicon/ReversalIndexOperations.py`

**CRUD Methods**:
- `GetAll()` → All reversal indexes
- `Create(writing_system)` → Create reversal index for WS
- `Delete(index)` → Delete reversal index
- `Find(writing_system)` → Find by WS
- `GetEntries(index)` → Get all entries
- `GetWritingSystem(index)` → Get WS
- `GetName(index)` → Get index name
- `GetEntriesCount(index)` → Count entries

**Dependencies**: IReversalIndexEntry

#### 3.2 **IReversalIndexEntry** (HIGH)
**File**: `flexlibs/code/Lexicon/ReversalIndexEntryOperations.py`

**CRUD Methods**:
- `GetAll(index)` → All entries in index
- `Create(index, form)` → Create entry
- `Delete(entry)` → Delete entry
- `Find(index, form)` → Find by form
- `GetForm(entry)` → Get reversal form
- `SetForm(entry, form)` → Set form
- `GetDefinition(entry)` → Get definition
- `SetDefinition(entry, definition)` → Set definition
- `GetPartOfSpeech(entry)` → Get POS
- `SetPartOfSpeech(entry, pos)` → Set POS
- `GetSenses(entry)` → Get linked senses
- `AddSense(entry, sense)` → Link to sense
- `RemoveSense(entry, sense)` → Unlink sense
- `GetSubentries(entry)` → Get subentries
- `AddSubentry(entry, subentry)` → Add subentry
- `Merge(entry1, entry2)` → Merge entries

**Dependencies**: ILexSense, IPartOfSpeech

### Part B: Wordform Inventory Operations

#### 3.3 **IWfiWordform** (HIGH)
**File**: `flexlibs/code/TextsWords/WfiWordformOperations.py`

**CRUD Methods**:
- `GetAll()` → All wordforms
- `Find(form, ws)` → Find by form text
- `GetForm(wordform)` → Get form text
- `GetAnalyses(wordform)` → Get analyses
- `GetAnalysisCount(wordform)` → Count analyses
- `GetOccurrences(wordform)` → Get text occurrences
- `GetSpellingStatus(wordform)` → Correct/incorrect
- `SetSpellingStatus(wordform, status)` → Set status

**Dependencies**: IWfiAnalysis, ISegment

#### 3.4 **IWfiAnalysis** (HIGH)
**File**: `flexlibs/code/TextsWords/WfiAnalysisOperations.py`

**CRUD Methods**:
- `GetAll(wordform)` → All analyses for wordform
- `Create(wordform)` → Create analysis
- `Delete(analysis)` → Delete analysis
- `GetMorphBundles(analysis)` → Get morph bundles
- `AddMorphBundle(analysis, morph, sense)` → Add bundle
- `GetCategory(analysis)` → Get POS
- `SetCategory(analysis, pos)` → Set POS
- `GetMeanings(analysis)` → Get meanings
- `IsApproved(analysis)` → Check approval
- `SetApproved(analysis, approved)` → Approve/disapprove

**Dependencies**: IWfiMorphBundle, IWfiGloss

#### 3.5 **IWfiGloss** (MEDIUM)
**File**: `flexlibs/code/TextsWords/WfiGlossOperations.py`

**CRUD Methods**:
- `GetAll(analysis)` → All glosses for analysis
- `Create(analysis, form)` → Create gloss
- `Delete(gloss)` → Delete gloss
- `GetForm(gloss)` → Get gloss text
- `SetForm(gloss, text)` → Set gloss text

#### 3.6 **IWfiMorphBundle** (MEDIUM)
**File**: `flexlibs/code/TextsWords/WfiMorphBundleOperations.py`

**CRUD Methods**:
- `GetAll(analysis)` → All bundles
- `Create(analysis, morph, sense)` → Create bundle
- `Delete(bundle)` → Delete bundle
- `GetMorph(bundle)` → Get morph
- `SetMorph(bundle, morph)` → Set morph
- `GetSense(bundle)` → Get sense
- `SetSense(bundle, sense)` → Set sense
- `GetMsa(bundle)` → Get MSA
- `SetMsa(bundle, msa)` → Set MSA

**Deliverables**:
- 6 new Operations classes (3 Reversal + 3 Wordform)
- Demo scripts:
  - `examples/reversal_index_demo.py`
  - `examples/wordform_inventory_demo.py`
- Unit tests:
  - `tests/test_reversal_operations.py`
  - `tests/test_wordform_operations.py`
- Documentation:
  - `docs/operations/ReversalIndex_README.md`
  - `docs/operations/WordformInventory_README.md`

---

## Work Stream 4: QA & Integration Testing (QA Agent)

### Scope
Create comprehensive test plans and validate all implementations.

### Deliverables

#### 4.1 **Test Plans**
**File**: `tests/INTEGRATION_TEST_PLAN.md`

For each Operations class:
- CRUD operation test matrix
- Edge case testing
- Error handling validation
- Performance benchmarks
- Integration points with existing operations

#### 4.2 **Integration Tests**
**File**: `tests/test_integration_scripture_discourse_reversal_wordform.py`

Test cross-feature workflows:
- Import Scripture → Create Discourse Chart
- Wordform → Reversal Index linkage
- Scripture Text → Wordform Inventory
- Reversal Entry → Lexicon Sense linking

#### 4.3 **Demo Validation**
Validate all demo scripts:
- Run each demo script
- Verify output correctness
- Check error handling
- Performance profiling

#### 4.4 **Documentation Review**
Review all README files:
- Accuracy of examples
- Completeness of API documentation
- Consistency with existing docs
- Code snippet validation

#### 4.5 **Compatibility Testing**
- Test against multiple FLEx versions (if applicable)
- Test with different project types
- Verify read-only vs write-enabled behavior
- Test exception handling

**Deliverables**:
- Test plan document
- Integration test suite
- Demo validation report
- Documentation review report
- Bug/issue tracking document

---

## Architecture Guidelines (All Programmers)

### 1. **File Organization**

```
flexlibs/
├── code/
│   ├── Scripture/              # NEW - Work Stream 1
│   │   ├── __init__.py
│   │   ├── ScrBookOperations.py
│   │   ├── ScrSectionOperations.py
│   │   ├── ScrTxtParaOperations.py
│   │   ├── ScrDraftOperations.py
│   │   ├── ScrAnnotationsOperations.py
│   │   └── ScrNoteOperations.py
│   ├── Discourse/              # NEW - Work Stream 2
│   │   ├── __init__.py
│   │   ├── ConstChartOperations.py
│   │   ├── ConstChartRowOperations.py
│   │   ├── ConstChartWordGroupOperations.py
│   │   ├── ConstChartMovedTextOperations.py
│   │   ├── ConstChartTagOperations.py
│   │   └── ConstChartClauseMarkerOperations.py
│   └── TextsWords/             # NEW - Work Stream 3 (Wordform)
│       ├── WfiWordformOperations.py
│       ├── WfiAnalysisOperations.py
│       ├── WfiGlossOperations.py
│       └── WfiMorphBundleOperations.py
├── examples/                    # Demo scripts
└── tests/                       # Test suites
```

### 2. **Code Standards**

**Follow Existing Patterns**:
- Inherit from `BaseOperations`
- Use `__ResolveObject()` for HVO/object resolution
- Use `__WSHandle()` for writing system handling
- Raise appropriate exceptions: `FP_ReadOnlyError`, `FP_NullParameterError`, `FP_ParameterError`

**Documentation**:
- Complete docstrings with Args, Returns, Raises, Example, Notes, See Also
- Follow existing docstring format (see LexEntryOperations as model)

**Error Handling**:
- Check `writeEnabled` for Create/Delete/Update operations
- Validate null parameters
- Provide helpful error messages

**Testing**:
- Unit tests for each method
- Edge case coverage
- Integration tests with related operations

### 3. **Import Structure**

```python
# Standard pattern for Operations classes
import logging
logger = logging.getLogger(__name__)

from ..BaseOperations import BaseOperations

# Import FLEx LCM types
from SIL.LCModel import (
    IInterfaceName,
    IInterfaceNameFactory,
    IInterfaceNameRepository,
    # ... other interfaces
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)
```

### 4. **Method Naming Conventions**

- `GetAll()` → Retrieve collections
- `Find()` → Search operations
- `Create()` → Create new objects
- `Delete()` → Delete objects
- `Get<Property>()` → Get property value
- `Set<Property>()` → Set property value
- `Add<Item>()` → Add to collection
- `Remove<Item>()` → Remove from collection

### 5. **FLExProject Integration**

Update `FLExProject.py` to expose new operations:

```python
class FLExProject:
    def __init__(self):
        # ... existing code ...

        # NEW - Scripture Operations
        self.ScrBook = None
        self.ScrSection = None
        # ... etc

        # NEW - Discourse Operations
        self.ConstChart = None
        self.ConstChartRow = None
        # ... etc

        # NEW - Wordform Operations
        self.Wordforms = None
        self.WfiAnalysis = None
        # ... etc
```

---

## Coordination & Dependencies

### Critical Path
1. **Scripture** → Depends on existing Text/Paragraph operations
2. **Discourse** → Depends on Text and Segment operations
3. **Reversal** → Depends on existing Lexicon operations
4. **Wordform** → Depends on Text and Segment operations

### Parallel Work Possible
- All 3 programmer streams can work independently
- QA can start test planning immediately
- Integration happens after individual operations complete

### Integration Points
**Week 1-2**: Individual operations development
**Week 3**: Integration and cross-testing
**Week 4**: QA validation and documentation finalization

---

## Success Criteria

### Completion Checklist

**For Each Operations Class**:
- ✅ All CRUD+ methods implemented
- ✅ Complete docstrings
- ✅ Unit tests with >80% coverage
- ✅ Demo script showing usage
- ✅ README documentation
- ✅ Integration with FLExProject
- ✅ Error handling tested
- ✅ QA validation passed

**Overall Project**:
- ✅ 18 new Operations classes
- ✅ 6 demo scripts
- ✅ 4 test suites
- ✅ 4 README documents
- ✅ Integration test suite
- ✅ QA validation report
- ✅ All existing tests still pass

---

## Risk Management

### Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Interface definitions unclear | Reference FieldWorks source code, use LCModel docs |
| Dependencies between features | Clear API contracts, stub methods if needed |
| Complex LCM object hierarchies | Start with simple Get methods, build up to CRUD |
| Test data availability | Use existing test project (Sena 3), create minimal fixtures |
| Performance issues | Profile early, optimize hot paths, use generators |

---

## Timeline Estimate

**Phase 1: Setup & High-Priority** (Week 1)
- Scripture: IScrBook, IScrSection
- Discourse: IDsConstChart, IConstChartRow
- Reversal: IReversalIndex, IReversalIndexEntry
- Wordform: IWfiWordform, IWfiAnalysis

**Phase 2: Medium-Priority** (Week 2)
- Scripture: IScrTxtPara
- Discourse: IConstChartWordGroup, IConstChartMovedTextMarker
- Wordform: IWfiGloss, IWfiMorphBundle

**Phase 3: Low-Priority & Integration** (Week 3)
- Scripture: IScrDraft, IScrBookAnnotations, IScrScriptureNote
- Discourse: IConstChartTag, IConstChartClauseMarker
- Integration testing

**Phase 4: QA & Documentation** (Week 4)
- Full QA validation
- Documentation finalization
- Performance optimization
- Release preparation

---

## Next Steps

**Immediate Actions**:
1. ✅ Create this implementation plan
2. 🔄 Launch 4 parallel agents:
   - Programmer Agent 1: Scripture Operations
   - Programmer Agent 2: Discourse Operations
   - Programmer Agent 3: Reversal & Wordform Operations
   - QA Agent: Test Planning
3. ⏳ Monitor progress and coordinate integration
4. ⏳ Review deliverables and provide feedback

**Agent Kickoff**: Ready to launch in parallel!
