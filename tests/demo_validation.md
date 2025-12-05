# Demo Script Validation Procedures

## Overview

This document provides step-by-step manual validation procedures for all demo scripts related to Scripture, Discourse, Reversal, and Wordform Operations. Each demo script must be validated by running it and manually inspecting the results in the FLEx GUI.

**Purpose**: Ensure that objects created by flexlibs display correctly and are editable in FLEx.

**Validation Frequency**:
- After initial implementation
- After bug fixes
- Before each release
- After FLEx version updates

---

## Table of Contents

1. [demo_scripture_operations.py](#demo_scripture_operationspy)
2. [demo_discourse_operations.py](#demo_discourse_operationspy)
3. [demo_reversal_operations.py](#demo_reversal_operationspy)
4. [demo_wordform_operations.py](#demo_wordform_operationspy)
5. [Common Validation Steps](#common-validation-steps)
6. [Troubleshooting](#troubleshooting)

---

## demo_scripture_operations.py

### Demo Script Overview

**Purpose**: Demonstrate creating scripture books, sections, and paragraphs.

**Expected Output**:
- Creates Genesis (Book 1)
- Adds two sections with headings
- Adds paragraphs with Genesis 1:1-5 text

### Pre-Validation Setup

1. **Create Test Project** (if needed):
   - Open FLEx
   - Create new project: "TestProject_Scripture"
   - Add English as analysis language
   - Close project

2. **Backup Project**:
   - Make a backup before running demo
   - Location: `C:\ProgramData\SIL\FieldWorks\Projects\TestProject_Scripture\`

### Run Demo Script

```bash
cd D:\Github\flexlibs\demos
python demo_scripture_operations.py
```

**Expected Console Output**:
```
Opening project...
Creating Genesis book...
Book created: Genesis (Canonical 1)
Creating sections...
Section 1: Creation Account
Section 2: Light and Darkness
Adding paragraphs...
Paragraph 1: In the beginning, God created...
Paragraph 2: The earth was without form...
Scripture creation complete!
Closing project...
```

### Manual Validation Steps in FLEx GUI

#### Step 1: Open Project in FLEx

1. Open FLEx
2. Open "TestProject_Scripture"
3. Wait for project to load completely

**Verify**:
- [ ] Project opens without errors
- [ ] No validation error messages appear

#### Step 2: Navigate to Scripture View

1. Click on **Scripture** in the left navigation panel
2. Or: Use menu **View → Scripture**

**Verify**:
- [ ] Scripture view opens
- [ ] Genesis appears in book list

#### Step 3: Verify Book Properties

1. Right-click on Genesis in book list
2. Select **Properties** (or double-click book)

**Verify**:
- [ ] Book name: "Genesis"
- [ ] Canonical number: 1
- [ ] Book ID: "GEN" (or similar)
- [ ] Properties dialog displays correctly

#### Step 4: Verify Section Headings

1. Expand Genesis in book list
2. Look for section headings

**Verify**:
- [ ] Section 1 heading: "Creation Account"
- [ ] Section 2 heading: "Light and Darkness"
- [ ] Headings display in correct order
- [ ] Headings are readable and properly formatted

#### Step 5: Verify Paragraph Content

1. Click on first section
2. Read paragraph text in main editor

**Verify**:
- [ ] Paragraph 1 text displays correctly
- [ ] Paragraph 2 text displays correctly
- [ ] Text is editable (try typing)
- [ ] No garbled characters or encoding issues

#### Step 6: Test Editing in FLEx

1. Click in first paragraph
2. Add text: " (TEST)" at end of paragraph
3. Save (Ctrl+S)
4. Close project
5. Reopen project

**Verify**:
- [ ] Can edit text in FLEx
- [ ] Changes save successfully
- [ ] Changes persist after reopen
- [ ] No data corruption

#### Step 7: Test Navigation

1. Use arrow keys to navigate between paragraphs
2. Use Page Up/Down
3. Click on different sections

**Verify**:
- [ ] Navigation works smoothly
- [ ] No crashes or hangs
- [ ] Cursor position maintained correctly

#### Step 8: Test Section Editing

1. Right-click on section heading
2. Select **Edit** or double-click heading
3. Change heading text to "TEST EDIT"
4. Save and reopen

**Verify**:
- [ ] Section heading is editable
- [ ] Changes save correctly
- [ ] Changes persist after reopen

#### Step 9: Test Deletion

1. Create a new section (use FLEx GUI)
2. Add some text
3. Delete the section
4. Verify deletion works

**Verify**:
- [ ] Can delete sections created by flexlibs
- [ ] Deletion prompts for confirmation
- [ ] Section removed from book

#### Step 10: Export Test

1. Go to **File → Export**
2. Choose **USFM** format
3. Export Genesis
4. Open exported file in text editor

**Verify**:
- [ ] Export succeeds
- [ ] USFM file contains book markers
- [ ] Section headings present (\\s markers)
- [ ] Paragraph text present (\\p markers)
- [ ] No malformed USFM

### Validation Checklist Summary

**demo_scripture_operations.py**:

- [ ] Script runs without errors
- [ ] Genesis book appears in FLEx
- [ ] Section headings display correctly
- [ ] Paragraph text displays correctly
- [ ] Objects are editable in FLEx
- [ ] Changes persist after close/reopen
- [ ] No validation errors in FLEx
- [ ] Export to USFM works
- [ ] No data corruption

**Status**: ⬜ Pass | ⬜ Fail | ⬜ Not Tested

**Tester**: ________________  **Date**: __________

**Notes**:
```
(Any issues, observations, or special notes)
```

---

## demo_discourse_operations.py

### Demo Script Overview

**Purpose**: Demonstrate creating discourse constituent charts with rows and word groups.

**Expected Output**:
- Creates sample text
- Creates constituent chart
- Adds rows to chart
- Links word groups to text segments

### Pre-Validation Setup

1. Create test project: "TestProject_Discourse"
2. Ensure project has texts capability enabled
3. Backup project

### Run Demo Script

```bash
python demo_discourse_operations.py
```

**Expected Console Output**:
```
Opening project...
Creating sample text...
Text created: Discourse Sample Text
Adding paragraphs...
Creating constituent chart...
Chart created: Main Discourse Chart
Adding rows to chart...
Row 1 created
Row 2 created
Row 3 created
Linking word groups to segments...
Word group 1 linked
Word group 2 linked
Discourse chart complete!
```

### Manual Validation Steps in FLEx GUI

#### Step 1: Open Project and Navigate to Texts

1. Open "TestProject_Discourse" in FLEx
2. Navigate to **Texts & Words**
3. Click on **Texts** tab

**Verify**:
- [ ] Text "Discourse Sample Text" appears
- [ ] Text is accessible

#### Step 2: Verify Text Content

1. Double-click on text to open
2. View text content

**Verify**:
- [ ] Text has paragraphs
- [ ] Text is readable
- [ ] Text can be edited

#### Step 3: Navigate to Discourse View

1. Click on **Discourse** tab (or menu **View → Discourse**)
2. Look for chart

**Verify**:
- [ ] Discourse view opens
- [ ] Chart "Main Discourse Chart" appears
- [ ] Chart is associated with correct text

#### Step 4: Verify Chart Structure

1. Open chart in main editor
2. Examine chart rows

**Verify**:
- [ ] Chart displays in grid format
- [ ] 3 rows visible
- [ ] Rows have correct labels (if any)
- [ ] Chart structure looks correct

#### Step 5: Verify Word Groups

1. Look for word groups in chart cells
2. Hover over word groups

**Verify**:
- [ ] Word groups display in chart
- [ ] Word groups link to text (tooltip shows text)
- [ ] Word groups positioned correctly

#### Step 6: Test Chart Editing

1. Try adding a new row in FLEx
2. Try editing word group
3. Try deleting a row

**Verify**:
- [ ] Can add rows to flexlibs-created chart
- [ ] Can edit word groups
- [ ] Can delete rows
- [ ] Changes save correctly

#### Step 7: Test Chart Navigation

1. Use arrow keys to navigate cells
2. Click on different word groups
3. Try to jump to text from chart

**Verify**:
- [ ] Navigation works
- [ ] Chart responds to clicks
- [ ] Can navigate to linked text

#### Step 8: Close and Reopen

1. Save project
2. Close FLEx
3. Reopen project
4. Navigate back to discourse chart

**Verify**:
- [ ] Chart persists after reopen
- [ ] Chart structure intact
- [ ] Word group links maintained

### Validation Checklist Summary

**demo_discourse_operations.py**:

- [ ] Script runs without errors
- [ ] Text created successfully
- [ ] Chart appears in discourse view
- [ ] Rows display correctly
- [ ] Word groups link to text
- [ ] Chart is editable in FLEx
- [ ] Changes persist after close/reopen
- [ ] No validation errors

**Status**: ⬜ Pass | ⬜ Fail | ⬜ Not Tested

**Tester**: ________________  **Date**: __________

**Notes**:
```
```

---

## demo_reversal_operations.py

### Demo Script Overview

**Purpose**: Demonstrate creating reversal index, reversal entries, and linking to lexical senses.

**Expected Output**:
- Creates English reversal index (or uses existing)
- Creates reversal entries: "run", "walk", "house"
- Links reversal entries to lexical senses
- Creates subentries

### Pre-Validation Setup

1. Create test project: "TestProject_Reversal"
2. Add basic lexicon entries (run, walk, house)
3. Enable English as analysis language
4. Backup project

### Run Demo Script

```bash
python demo_reversal_operations.py
```

**Expected Console Output**:
```
Opening project...
Creating/getting English reversal index...
Reversal index: English (en)
Creating lexicon entries...
Entry: run
Entry: walk
Entry: house
Creating reversal entries...
Reversal: run → linked to sense "to move rapidly"
Reversal: walk → linked to sense "to move on foot"
Reversal: house → linked to sense "dwelling"
Creating subentries...
Subentry: running (under run)
Reversal index complete!
```

### Manual Validation Steps in FLEx GUI

#### Step 1: Navigate to Reversal Index

1. Open project in FLEx
2. Go to **Lexicon** area
3. Click on **Reversal Indexes** in left panel

**Verify**:
- [ ] Reversal Indexes node visible
- [ ] English reversal index appears

#### Step 2: Verify Reversal Index Properties

1. Right-click on English reversal index
2. Select **Properties**

**Verify**:
- [ ] Index name: "English" (or similar)
- [ ] Writing system: English (en)
- [ ] Properties display correctly

#### Step 3: Verify Reversal Entries

1. Expand English reversal index
2. Look for entries

**Verify**:
- [ ] "run" entry appears
- [ ] "walk" entry appears
- [ ] "house" entry appears
- [ ] Entries in alphabetical order

#### Step 4: Verify Entry-Sense Links

1. Click on "run" reversal entry
2. Look in main editor for linked senses

**Verify**:
- [ ] Reversal form displays: "run"
- [ ] Linked senses section shows sense(s)
- [ ] Sense gloss visible: "to move rapidly"
- [ ] Can click through to lexical sense

#### Step 5: Verify Bidirectional Link

1. Navigate to **Lexicon → Entries**
2. Find lexical entry "run"
3. Look for reversal references

**Verify**:
- [ ] Lexical entry shows reversal references
- [ ] "run" reversal entry listed
- [ ] Bidirectional link maintained

#### Step 6: Verify Subentries

1. Go back to English reversal index
2. Expand "run" entry
3. Look for subentries

**Verify**:
- [ ] "running" subentry appears under "run"
- [ ] Subentry indented/nested correctly
- [ ] Subentry has correct form

#### Step 7: Test Adding Entries in FLEx

1. Right-click on reversal index
2. Select **Add Entry**
3. Create new entry "test"
4. Link to a sense

**Verify**:
- [ ] Can add entries to flexlibs-created index
- [ ] New entry appears in list
- [ ] Can link to senses
- [ ] No errors

#### Step 8: Test Editing Reversal Forms

1. Click on "run" entry
2. Edit the reversal form (change to "RUN")
3. Save

**Verify**:
- [ ] Reversal form is editable
- [ ] Changes save correctly
- [ ] Entry updates in list

#### Step 9: Test Export to LIFT

1. Go to **File → Export**
2. Choose **LIFT** format
3. Export lexicon with reversals
4. Open LIFT XML in text editor

**Verify**:
- [ ] Export succeeds
- [ ] LIFT file contains reversal entries
- [ ] Reversal-sense links in XML
- [ ] XML is well-formed

#### Step 10: Test Deletion

1. Create a test reversal entry
2. Delete it
3. Verify sense still exists

**Verify**:
- [ ] Can delete reversal entries
- [ ] Deletion doesn't delete linked sense
- [ ] Sense no longer shows reversal reference

### Validation Checklist Summary

**demo_reversal_operations.py**:

- [ ] Script runs without errors
- [ ] Reversal index created/accessed
- [ ] Reversal entries appear in FLEx
- [ ] Entry-sense links work (bidirectional)
- [ ] Subentries display correctly
- [ ] Entries are editable in FLEx
- [ ] Changes persist after close/reopen
- [ ] LIFT export includes reversals
- [ ] No validation errors

**Status**: ⬜ Pass | ⬜ Fail | ⬜ Not Tested

**Tester**: ________________  **Date**: __________

**Notes**:
```
```

---

## demo_wordform_operations.py

### Demo Script Overview

**Purpose**: Demonstrate wordform analysis, morph bundles, and glossing.

**Expected Output**:
- Creates wordforms: "running", "walked", "houses"
- Adds analyses to wordforms
- Creates morph bundles (morpheme breakdown)
- Links bundles to lexicon
- Adds glosses
- Marks analyses as human-approved

### Pre-Validation Setup

1. Create test project: "TestProject_Wordform"
2. Add lexicon entries: run, -ing, walk, -ed, house, -s
3. Create a sample text (optional)
4. Backup project

### Run Demo Script

```bash
python demo_wordform_operations.py
```

**Expected Console Output**:
```
Opening project...
Creating lexicon entries for morphemes...
Created: run (stem)
Created: -ing (suffix)
Created: walk (stem)
Created: -ed (suffix)
Created: house (stem)
Created: -s (suffix)
Creating wordforms...
Wordform: running
Wordform: walked
Wordform: houses
Analyzing wordforms...
Analysis: running = run + -ing
Analysis: walked = walk + -ed
Analysis: houses = house + -s
Adding glosses...
Gloss: running
Gloss: walked
Gloss: houses
Wordform analysis complete!
```

### Manual Validation Steps in FLEx GUI

#### Step 1: Navigate to Wordform Inventory

1. Open project in FLEx
2. Go to **Texts & Words**
3. Click on **Word Forms** (or **Wordform Inventory**)

**Verify**:
- [ ] Wordform Inventory view opens
- [ ] Wordforms appear in list

#### Step 2: Verify Wordforms Exist

1. Look for created wordforms
2. Check spelling status

**Verify**:
- [ ] "running" wordform appears
- [ ] "walked" wordform appears
- [ ] "houses" wordform appears
- [ ] Wordforms show in correct column

#### Step 3: Verify Wordform Analyses

1. Click on "running" wordform
2. Look at analyses in lower panel

**Verify**:
- [ ] Analysis exists for "running"
- [ ] Analysis shows morpheme breakdown
- [ ] Breakdown shows: "run" + "-ing"
- [ ] Morphemes display correctly

#### Step 4: Verify Morph Bundle Links

1. Examine morph bundles in analysis
2. Check links to lexicon

**Verify**:
- [ ] "run" bundle links to lexicon entry "run"
- [ ] "-ing" bundle links to lexicon entry "-ing"
- [ ] Can click through to lexicon entries
- [ ] Links are bidirectional

#### Step 5: Verify Glosses

1. Look at gloss field for analysis
2. Check writing system

**Verify**:
- [ ] Gloss displays: "running"
- [ ] Gloss in correct language (English)
- [ ] Gloss is readable

#### Step 6: Verify Human Approval

1. Check if analysis marked as human-approved
2. Look for approval indicator (icon, color, etc.)

**Verify**:
- [ ] Analysis shows approval status
- [ ] Human-approved analyses indicated
- [ ] Can distinguish from parser analyses

#### Step 7: Test Editing Analyses

1. Click on analysis
2. Try to edit morph bundles
3. Try to change links

**Verify**:
- [ ] Can edit analyses created by flexlibs
- [ ] Can modify morph bundles
- [ ] Can change lexicon links
- [ ] Changes save correctly

#### Step 8: Test Adding Alternative Analysis

1. Select wordform "running"
2. Add new analysis (different breakdown)
3. Save

**Verify**:
- [ ] Can add multiple analyses to wordform
- [ ] Both analyses appear
- [ ] Can select different analyses
- [ ] No conflicts

#### Step 9: Test Wordform in Text Context

1. Go to **Texts & Words → Analyze**
2. Find wordform in a text (if available)
3. Apply analysis to wordform in text

**Verify**:
- [ ] Analysis applies to text occurrences
- [ ] Gloss appears in interlinear
- [ ] Morpheme breakdown visible
- [ ] Text updates correctly

#### Step 10: Test Export

1. Go to **File → Export**
2. Export analyzed text (if available) or wordform list
3. Check export file

**Verify**:
- [ ] Export succeeds
- [ ] Wordforms included
- [ ] Analyses included
- [ ] Glosses included

### Validation Checklist Summary

**demo_wordform_operations.py**:

- [ ] Script runs without errors
- [ ] Wordforms appear in inventory
- [ ] Analyses display correctly
- [ ] Morph bundles link to lexicon
- [ ] Glosses display correctly
- [ ] Human approval works
- [ ] Analyses are editable in FLEx
- [ ] Changes persist after close/reopen
- [ ] No validation errors

**Status**: ⬜ Pass | ⬜ Fail | ⬜ Not Tested

**Tester**: ________________  **Date**: __________

**Notes**:
```
```

---

## Common Validation Steps

### For All Demo Scripts

1. **Before Running**:
   - [ ] Backup test project
   - [ ] Close FLEx if open
   - [ ] Verify flexlibs installed correctly
   - [ ] Check Python environment

2. **During Script Execution**:
   - [ ] Watch for errors/exceptions
   - [ ] Verify console output matches expected
   - [ ] Check for warnings

3. **After Script Execution**:
   - [ ] Open project in FLEx
   - [ ] Verify objects created
   - [ ] Test editing in FLEx
   - [ ] Close and reopen project
   - [ ] Verify persistence

4. **Quality Checks**:
   - [ ] No data corruption
   - [ ] No validation errors
   - [ ] No crashes or hangs
   - [ ] Performance acceptable
   - [ ] Memory usage normal

5. **Documentation**:
   - [ ] Record test date
   - [ ] Record tester name
   - [ ] Note any issues
   - [ ] Attach screenshots if needed

---

## Troubleshooting

### Common Issues and Solutions

#### Script Fails to Run

**Symptoms**: Python error, import error, or script doesn't start

**Solutions**:
1. Check flexlibs installation: `pip show flexlibs`
2. Verify Python version compatibility
3. Check for missing dependencies
4. Review error traceback

#### FLEx Doesn't Show Created Objects

**Symptoms**: Objects missing in FLEx GUI after running demo

**Solutions**:
1. Verify script completed successfully (no errors)
2. Check if correct project opened in FLEx
3. Try closing and reopening project
4. Check FLEx version compatibility
5. Look in different view (e.g., Scripture vs Lexicon)

#### Data Corruption Errors

**Symptoms**: FLEx shows validation errors or corrupt data warnings

**Solutions**:
1. Stop immediately - do not save changes
2. Restore from backup
3. Report bug with full details
4. Do not proceed with testing until fixed

#### Objects Appear but Are Malformed

**Symptoms**: Objects display but have missing or incorrect properties

**Solutions**:
1. Document specific properties that are wrong
2. Compare to FLEx-created equivalent objects
3. File bug report with screenshots
4. Check LCM object structure in debugger

#### Performance Issues

**Symptoms**: Slow operation, high memory usage, or freezing

**Solutions**:
1. Check project size (may be too large for testing)
2. Monitor resource usage during script
3. Profile Python script if needed
4. Consider smaller test dataset

#### Script Hangs or Never Completes

**Symptoms**: Script runs but never finishes, no output

**Solutions**:
1. Wait longer (some operations are slow)
2. Check for infinite loops in script
3. Kill process and review code
4. Add debug logging to find bottleneck

---

## Validation Report Template

### Project Information
- **Project Name**: ______________________
- **FLEx Version**: ______________________
- **flexlibs Version**: ______________________
- **Python Version**: ______________________
- **OS**: ______________________

### Test Summary
- **Date**: __________
- **Tester**: __________
- **Duration**: __________ minutes

### Results
- **demo_scripture_operations.py**: ⬜ Pass | ⬜ Fail | ⬜ Not Tested
- **demo_discourse_operations.py**: ⬜ Pass | ⬜ Fail | ⬜ Not Tested
- **demo_reversal_operations.py**: ⬜ Pass | ⬜ Fail | ⬜ Not Tested
- **demo_wordform_operations.py**: ⬜ Pass | ⬜ Fail | ⬜ Not Tested

### Issues Found
| Demo Script | Issue Description | Severity | Status |
|-------------|------------------|----------|--------|
| | | | |
| | | | |

### Recommendations
```
(Overall assessment, recommendations for release, etc.)
```

### Screenshots
```
(Attach screenshots showing objects in FLEx GUI)
```

---

**Document Version**: 1.0
**Last Updated**: 2025-12-05
**Status**: Active - Ready for Use
