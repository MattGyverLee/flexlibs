# Team Delegation Plan: Complete Craig's Methods

## Team Structure

### **Team Lead (TL)**
- Create detailed work plan
- Coordinate agent activities
- Track progress
- Final review and approval

### **Programmer Agent 1 (P1)**
- Delegate Example operations
- Delegate Pronunciation operations
- Delegate Text operations

### **Programmer Agent 2 (P2)**
- Delegate CustomField operations
- Delegate Reversal operations
- Delegate System operations (POS, SemanticDomains, WritingSystems)

### **Verification Agent (V1)**
- Verify all methods delegated correctly
- Check for missed methods
- Validate syntax
- Test both APIs work

### **QC Agent (Q1)**
- Review code quality
- Check error handling preserved
- Verify return types match
- Check documentation accuracy

### **Master Linguist Agent (L1)**
- Verify linguistic terminology correct
- Check conceptual hierarchy makes sense
- Validate operations match linguistic workflows
- Review from field linguist perspective

### **Craig Agent (C1)**
- Review for Pythonic style
- Check simplicity maintained
- Verify no unnecessary complexity
- Assess backward compatibility

### **Synthesis Agent (S1)**
- Identify repeated patterns in delegations
- Extract common helper functions if found
- Document delegation pattern
- Recommend improvements

---

## Complete Method Inventory

### ✅ Already Delegated (9 methods)
- `LexiconGetHeadword()` → `LexEntry.GetHeadword()`
- `LexiconGetLexemeForm()` → `LexEntry.GetLexemeForm()`
- `LexiconSetLexemeForm()` → `LexEntry.SetLexemeForm()`
- `LexiconGetCitationForm()` → `LexEntry.GetCitationForm()`
- `LexiconGetSenseGloss()` → `Senses.GetGloss()`
- `LexiconSetSenseGloss()` → `Senses.SetGloss()`
- `LexiconGetSenseDefinition()` → `Senses.GetDefinition()`
- `LexiconGetSensePOS()` → `Senses.GetPartOfSpeech()`
- `LexiconGetSenseSemanticDomains()` → `Senses.GetSemanticDomains()`

### 🔲 Remaining to Delegate (24 methods)

#### **Group 1: Example Operations (3 methods)** - Agent P1
- `LexiconGetExample(example, ws)` → `Examples.GetExample(example, ws)`
- `LexiconSetExample(example, text, ws)` → `Examples.SetExample(example, text, ws)`
- `LexiconGetExampleTranslation(trans, ws)` → `Examples.GetTranslation(trans, ws)`

#### **Group 2: Pronunciation Operations (1 method)** - Agent P1
- `LexiconGetPronunciation(pron, ws)` → `Pronunciations.GetForm(pron, ws)`

#### **Group 3: Analysis Count Operations (2 methods)** - Keep as-is (complex reflection)
- `LexiconEntryAnalysesCount(entry)` - Uses reflection, keep original
- `LexiconSenseAnalysesCount(sense)` - Uses reflection, keep original

#### **Group 4: Text Operations (2 methods)** - Agent P1
- `TextsGetAll(supplyName, supplyText)` → `Texts.GetAll()` with params
- `TextsNumberOfTexts()` → `len(list(Texts.GetAll()))`

#### **Group 5: Custom Field Operations (~15 methods)** - Agent P2
- `GetFieldID(className, fieldName)` → `CustomFields.FindField()`
- `GetCustomFieldValue(obj, fieldID, ws)` → `CustomFields.GetValue()`
- `LexiconFieldIsStringType(fieldID)` → `CustomFields.GetFieldType()` check
- `LexiconFieldIsMultiType(fieldID)` → `CustomFields.IsMultiString()`
- `LexiconFieldIsAnyStringType(fieldID)` → `CustomFields` method
- `LexiconGetFieldText(obj, fieldID, ws)` → `CustomFields.GetValue()`
- `LexiconSetFieldText(obj, fieldID, text, ws)` → `CustomFields.SetValue()`
- `LexiconClearField(obj, fieldID)` → `CustomFields.ClearValue()`
- `LexiconSetFieldInteger(obj, fieldID, int)` → `CustomFields.SetValue()`
- `LexiconAddTagToField(obj, fieldID, tag)` → `CustomFields.AddListValue()`
- `ListFieldPossibilityList(obj, fieldID)` → Keep as-is (no direct equiv)
- `ListFieldPossibilities(obj, fieldID)` → `CustomFields.GetListValues()`
- `ListFieldLookup(obj, fieldID, value)` → Keep as-is (no direct equiv)
- `LexiconSetListFieldSingle(obj, fieldID, val)` → `CustomFields.SetListFieldSingle()`
- `LexiconClearListFieldSingle(obj, fieldID)` → `CustomFields.ClearValue()`
- `LexiconSetListFieldMultiple(obj, fieldID, vals)` → `CustomFields.SetListFieldMultiple()`
- `LexiconGetEntryCustomFields()` → `CustomFields.GetAllFields()` filtered
- `LexiconGetSenseCustomFields()` → `CustomFields.GetAllFields()` filtered
- `LexiconGetExampleCustomFields()` → `CustomFields.GetAllFields()` filtered
- `LexiconGetAllomorphCustomFields()` → `CustomFields.GetAllFields()` filtered
- `LexiconGetEntryCustomFieldNamed(name)` → `CustomFields.FindField('LexEntry', name)`
- `LexiconGetSenseCustomFieldNamed(name)` → `CustomFields.FindField('LexSense', name)`

#### **Group 6: Reversal Operations (4 methods)** - Agent P2
- `ReversalIndex(languageTag)` → `Reversal.GetIndex(languageTag)`
- `ReversalEntries(languageTag)` → `Reversal.GetAll(languageTag)`
- `ReversalGetForm(entry, ws)` → `Reversal.GetForm(entry, ws)`
- `ReversalSetForm(entry, form, ws)` → `Reversal.SetForm(entry, form, ws)`

#### **Group 7: System/List Operations (5 methods)** - Agent P2
- `GetPartsOfSpeech()` → `list(POS.GetAll())`
- `GetAllSemanticDomains(flat)` → `list(SemanticDomains.GetAll())` + UnpackNestedPossibilityList if needed
- `GetLexicalRelationTypes()` → `list(LexReferences.GetAllTypes())`
- `GetPublications()` → `list(Publications.GetAll())`
- `PublicationType(name)` → `Publications.Find(name)`

#### **Group 8: Writing System Operations (keep most as-is - core functionality)**
- Keep existing implementations (already optimized)

---

## Detailed Work Plan

### **Phase 1: Agent P1 - Example, Pronunciation, Text Operations**

#### Checklist for Agent P1:

**1. Example Operations (lines ~2044-2095 in FLExProject.py)**
- [ ] Read current `LexiconGetExample()` implementation
- [ ] Verify `ExampleOperations.GetExample()` exists and matches
- [ ] Update `LexiconGetExample()` to delegate
- [ ] Read current `LexiconSetExample()` implementation
- [ ] Verify `ExampleOperations.SetExample()` exists and matches
- [ ] Update `LexiconSetExample()` to delegate
- [ ] Read current `LexiconGetExampleTranslation()` implementation
- [ ] Verify `ExampleOperations.GetTranslation()` exists and matches
- [ ] Update `LexiconGetExampleTranslation()` to delegate

**2. Pronunciation Operations (line ~2032)**
- [ ] Read current `LexiconGetPronunciation()` implementation
- [ ] Verify `PronunciationOperations.GetForm()` exists and matches
- [ ] Update `LexiconGetPronunciation()` to delegate

**3. Text Operations (lines ~2856-2890)**
- [ ] Read current `TextsGetAll()` implementation
- [ ] Verify `TextOperations.GetAll()` exists and matches signature
- [ ] Update `TextsGetAll()` to delegate (handle parameters)
- [ ] Read current `TextsNumberOfTexts()` implementation
- [ ] Update to use `Texts.GetAll()` with len()

**4. Documentation**
- [ ] Add delegation notes to each method docstring
- [ ] Verify examples still accurate

---

### **Phase 2: Agent P2 - CustomField, Reversal, System Operations**

#### Checklist for Agent P2:

**1. Reversal Operations (lines ~2798-2856)**
- [ ] Read current reversal methods
- [ ] Verify `ReversalOperations` methods exist
- [ ] Delegate `ReversalIndex()` → `Reversal.GetIndex()`
- [ ] Delegate `ReversalEntries()` → `Reversal.GetAll()`
- [ ] Delegate `ReversalGetForm()` → `Reversal.GetForm()`
- [ ] Delegate `ReversalSetForm()` → `Reversal.SetForm()`

**2. System Operations (scattered throughout)**
- [ ] Delegate `GetPartsOfSpeech()` → `POS.GetAll()`
- [ ] Delegate `GetAllSemanticDomains()` → `SemanticDomains.GetAll()`
- [ ] Delegate `GetLexicalRelationTypes()` → `LexReferences.GetAllTypes()`
- [ ] Delegate `GetPublications()` → `Publications.GetAll()`
- [ ] Delegate `PublicationType()` → `Publications.Find()`

**3. Custom Field Operations (lines ~2217-2733)**
- [ ] Analyze which custom field methods can delegate
- [ ] For each method, verify Operations equivalent exists
- [ ] Delegate simple get/set methods
- [ ] Keep complex methods that have no direct equivalent (document why)
- [ ] Ensure custom field filtering methods work correctly

---

### **Phase 3: Agent V1 - Verification**

#### Verification Checklist:

**1. Completeness Check**
- [ ] Count total Craig methods in FLExProject.py
- [ ] Count total delegated methods
- [ ] List any methods intentionally not delegated (with reasons)
- [ ] Verify no methods accidentally skipped

**2. Syntax Validation**
- [ ] Python syntax check on FLExProject.py
- [ ] No undefined references
- [ ] All Operations classes imported correctly

**3. Delegation Pattern Check**
- [ ] All delegated methods follow same pattern
- [ ] All have delegation note in docstring
- [ ] Return statements delegate properly
- [ ] Parameters passed correctly

**4. API Compatibility**
- [ ] Craig's method signatures unchanged
- [ ] Return types unchanged
- [ ] Error handling preserved

**5. Test Both APIs**
- [ ] Write test showing Craig's API works
- [ ] Write test showing Operations API works
- [ ] Verify both return identical results

---

### **Phase 4: Agent Q1 - Quality Control**

#### QC Checklist:

**1. Code Quality**
- [ ] Delegation code is clean and consistent
- [ ] No copy-paste errors
- [ ] Docstrings updated appropriately
- [ ] Comments accurate

**2. Error Handling**
- [ ] FP_ReadOnlyError still raised where appropriate
- [ ] FP_NullParameterError still raised where appropriate
- [ ] FP_ParameterError still raised where appropriate
- [ ] Error messages unchanged

**3. Return Types**
- [ ] String methods return str or ""
- [ ] List methods return lists/iterators
- [ ] Object methods return C# objects
- [ ] No unexpected None returns

**4. Writing System Handling**
- [ ] wsHandle/languageTagOrHandle parameters handled correctly
- [ ] Defaults work as before
- [ ] Both vernacular and analysis WS methods correct

**5. Edge Cases**
- [ ] None parameters handled
- [ ] Empty strings handled
- [ ] Missing objects handled
- [ ] Unusual data types handled

---

### **Phase 5: Agent L1 - Linguistic Review**

#### Linguistic Review Checklist:

**1. Terminology**
- [ ] "Headword" vs "Lexeme form" vs "Citation form" usage correct
- [ ] "Gloss" vs "Definition" distinction clear
- [ ] "Sense" vs "Subsense" hierarchy logical
- [ ] "Example" vs "Pronunciation" clear

**2. Conceptual Hierarchy**
- [ ] Entry → Sense → Example flow natural
- [ ] Pronunciation belongs to Entry (not Sense) - correct
- [ ] Citation form vs Lexeme form distinction makes sense
- [ ] Reversal entries relationship clear

**3. Linguistic Workflows**
- [ ] Common workflows still supported
- [ ] Creating entry → adding sense → adding example works
- [ ] Searching and retrieving data intuitive
- [ ] Bulk operations practical

**4. Field Linguist Perspective**
- [ ] API understandable to non-programmers
- [ ] Method names match linguistic concepts
- [ ] Documentation uses field linguistics terminology
- [ ] Examples reflect real lexicography tasks

---

### **Phase 6: Agent C1 - Craig's Review**

#### Craig's Review Checklist:

**1. Pythonic Style**
- [ ] Delegation is simple and explicit
- [ ] No unnecessary complexity added
- [ ] No "magic" introduced
- [ ] Code remains readable

**2. Backward Compatibility**
- [ ] ALL original methods work unchanged
- [ ] Method signatures identical
- [ ] Return types identical
- [ ] No breaking changes whatsoever

**3. Simplicity**
- [ ] Delegation pattern is straightforward
- [ ] Easy to understand what's happening
- [ ] Easy to debug if issues arise
- [ ] No clever tricks

**4. Maintainability**
- [ ] Single source of truth achieved
- [ ] Bug fixes affect both APIs
- [ ] Easy to add new methods in future
- [ ] Clear pattern for others to follow

**5. Overall Assessment**
- [ ] Would Craig approve this approach?
- [ ] Is it better than the original?
- [ ] Are there any concerns?
- [ ] Recommendations for improvement?

---

### **Phase 7: Agent S1 - Synthesis**

#### Synthesis Checklist:

**1. Pattern Analysis**
- [ ] Identify common delegation patterns
- [ ] Count how many times each pattern used
- [ ] Look for opportunities to extract helpers

**2. Code Repetition**
- [ ] Check for repeated parameter conversion
- [ ] Check for repeated error handling
- [ ] Check for repeated object resolution

**3. Helper Function Candidates**
- [ ] Could `__delegate_to_operations()` helper be useful?
- [ ] Could parameter mapping be automated?
- [ ] Could error wrapping be centralized?

**4. Documentation Patterns**
- [ ] Standard delegation note format
- [ ] Consistent "See Also" references
- [ ] Consistent example patterns

**5. Recommendations**
- [ ] Suggest any refactoring improvements
- [ ] Propose helper utilities
- [ ] Recommend documentation standards
- [ ] Future enhancement ideas

---

## Execution Order

1. **Team Lead** creates plan (this document) ✅
2. **Agent P1** delegates Example/Pronunciation/Text operations
3. **Agent P2** delegates CustomField/Reversal/System operations
4. **Agent V1** verifies all delegations complete
5. **Agent Q1** QC review - identifies issues
6. **Agent P1/P2** fix any issues identified by Q1
7. **Agent Q1** re-check fixes
8. **Agent L1** linguistic review
9. **Agent C1** Craig's review
10. **Agent P1/P2** implement any feedback from L1/C1
11. **Agent Q1** final QC check
12. **Agent S1** synthesis and pattern extraction
13. **Team Lead** final review and sign-off

---

## Success Criteria

- ✅ All Craig methods that CAN delegate, DO delegate
- ✅ Methods that can't delegate are documented with reason
- ✅ Both APIs (Craig + Operations) work identically
- ✅ Zero breaking changes
- ✅ Single source of truth achieved
- ✅ Code quality maintained/improved
- ✅ Linguistic terminology correct
- ✅ Craig approves approach
- ✅ Patterns documented for future use

---

## Deliverables

1. **Updated FLExProject.py** - All delegations complete
2. **Verification Report** - Agent V1's findings
3. **QC Report** - Agent Q1's assessment
4. **Linguistic Review** - Agent L1's feedback
5. **Craig's Review** - Agent C1's comments
6. **Synthesis Report** - Agent S1's patterns and recommendations
7. **Final Summary** - Team Lead's sign-off document

---

## Estimated Metrics

- **Methods to delegate**: ~24
- **Lines to modify**: ~240-300
- **Code reduction**: ~60-70% per method (implementation → delegation)
- **Time estimate**: 2-3 hours for full team process
- **Risk level**: Low (pattern proven with LexEntry/LexSense)

Ready to execute!
