# Deep Clone Analysis for FlexLibs2 Operations

**Date:** 2026-02-28
**Purpose:** Determine which operations should use `deep=True` for duplication based on owned vs referenced relationships

## Key Principles

From the LCM (Language and Culture Model) API, all object relationships follow a naming convention:

| Code | Type | Ownership | Duplication Strategy |
|------|------|-----------|----------------------|
| **OA** | Owned Atomic | Single owned child | **DEEP COPY** (create new) |
| **OS** | Owned Sequence | Ordered owned children | **DEEP COPY** (create new) |
| **OC** | Owned Collection | Unordered owned children | **DEEP COPY** (create new) |
| **RA** | Reference Atomic | Single reference | **REFERENCE** (share) |
| **RS** | Reference Sequence | Ordered references | **REFERENCE** (share) |
| **RC** | Reference Collection | Unordered references | **REFERENCE** (share) |

### Duplication Logic
- **When duplicating an object:** Create new instances of all **owned** children (OS/OA/OC), but **share references** to other objects (RA/RS/RC)
- **1:1 relationships (OA/RA):** Can always safely be referenced or copied without major consequence
- **Many-to-one or one-to-many (OS/OC/RC/RS):** Can definitely be referenced—a copied phoneme can reference the same phonological environments without issues
- **Simple properties:** Always copy (names, descriptions, booleans, enums)

---

## Current Status (Before Changes)

### **deep=True** (3 operations)
1. **EnvironmentOperations** - Owns LeftContextOA, RightContextOA (complex nested structures)
2. **PhonemeOperations** - Owns FeaturesOA, CodesOS (feature structures, phonetic codes)
3. **PhonologicalRuleOperations** - Owns LeftContextOA, RightContextOA, RHSObjects (complex rule structures)

### **deep=False** (37 operations)
All others default to shallow copy, regardless of owned properties.

---

## Recommended Changes by Domain

### LEXICON DOMAIN

#### **LexEntryOperations** ⚠️ SHOULD BE deep=True
**Current:** `deep=False`
**Reason:** LexEntry owns multiple complex structures:
- **SensesOS** (OS) - Ordered sequence of senses (meanings)
  - Each sense owns **ExamplesOS** (OS), **SensesOS** (subsenses)
- **AllomorphsOS** (OS) - Alternate forms
- **AlternativeFormsOS** (OS) - Additional forms
- **PronunciationsOS** (OS) - Pronunciation variants
- **EtymologiesOS** (OS) - Etymology information

**Current Behavior:** When duplicating an entry, you get just the lexeme form—empty of senses, allomorphs, pronunciations, etc. This is often not useful.

**Recommendation:** Change to `deep=True` by default.
**Note:** Users can still do shallow copies if they create the entry with `create_blank_sense=True` and skip the deep duplication.

#### **LexSenseOperations** ⚠️ COULD BE deep=True
**Current:** `deep=False`
**Owns:**
- **ExamplesOS** (OS) - Examples with translations
- **SensesOS** (OS) - Subsenses
- **PicturesOS** (OS) - Pictures with captions

**References** (shared, don't copy):
- **SemanticDomainsRC** (RC) - Reference to semantic domain list
- **MorphoSyntaxAnalysisRA** (RA) - Reference to MSA object
- **StatusRA** (RA) - Reference to status object

**Recommendation:** Optional, depends on use case. Could add to `deep=True` if users want full sense duplication including examples and subsenses.

#### **AllomorphOperations** - deep=False is CORRECT
**Owns:** No complex owned objects (just Form text)
**References:**
- **MorphTypeRA** (RA) - Shared morph type reference
- **PhoneEnvRC** (RC) - Shared phonological environments

**Recommendation:** Keep `deep=False`. Allomorphs are simple containers with only simple properties and references.

#### **ExampleOperations** - deep=False is CORRECT
**Owns:** Only simple MultiString properties (Example, Reference)
**References:**
- Translations reference to translation objects

**Recommendation:** Keep `deep=False`.

#### **PronunciationOperations** - deep=False is CORRECT
**Owns:** Only simple MultiString properties (Media, Representation)
**References:** None of consequence

**Recommendation:** Keep `deep=False`.

#### **VariantOperations** - deep=False is CORRECT
**Owns:** No complex owned objects
**References:**
- **VariantFormEntryBackRefsRS** (RS) - Variant relationship refs

**Recommendation:** Keep `deep=False`.

#### **ReversalOperations** - deep=False is CORRECT
**Owns:** No complex owned objects
**References:** Reversal index entries

**Recommendation:** Keep `deep=False`.

#### **SemanticDomainOperations** - deep=False MIGHT NEED REVIEW
**Owns:**
- **SubPossibilitiesOS** (OS) - Hierarchical subcategories

**Recommendation:** Consider `deep=True` to preserve category hierarchy in duplicates.

#### **EtymologyOperations** - deep=False is CORRECT
**Owns:** Only simple properties
**References:** Etymology language references

**Recommendation:** Keep `deep=False`.

---

### GRAMMAR DOMAIN

#### **EnvironmentOperations** ✓ deep=True IS CORRECT
Already set to `deep=True`. Owns context objects.

#### **PhonemeOperations** ✓ deep=True IS CORRECT
Already set to `deep=True`. Owns feature structures and codes.

#### **PhonologicalRuleOperations** ✓ deep=True IS CORRECT
Already set to `deep=True`. Owns complex rule structures.

#### **POSOperations** - deep=False is CORRECT
**Owns:**
- **SubPossibilitiesOS** (OS) - Subcategories (hierarchical)

**Reasoning:** While it owns subcategories, POS (Parts of Speech) are typically shared structural elements. Duplicating a POS with all subcategories might not be the intended behavior—you'd create multiple independent POS trees.

**Recommendation:** Keep `deep=False`, but document that users should manually manage subcategories if needed.

#### **GramCatOperations** - deep=False is CORRECT
Same reasoning as POSOperations.

#### **MorphRuleOperations** - deep=False is CORRECT
**Owns:** Only simple properties
**References:** RHS elements

**Recommendation:** Keep `deep=False`.

#### **NaturalClassOperations** - deep=False is CORRECT
**Owns:** Only simple MultiString properties
**References:** Segment members via RC

**Recommendation:** Keep `deep=False`. Natural classes are typically shared resources, and a copy should reference the same segments, not duplicate them.

---

### TEXTWORDS DOMAIN

#### **SegmentOperations** - deep=False is CORRECT
**Owns:** No complex objects (just MultiStrings)
**References:**
- **AnalysesRS** (RS) - Analysis references

**Reasoning:** Segments are contained within paragraphs within texts. Copying a segment without its parent context doesn't make much sense. A shallow copy is appropriate.

**Recommendation:** Keep `deep=False`.

#### **TextOperations** - deep=False SHOULD BE deep=True
**Current:** `deep=False`
**Owns:**
- **ContentsOA** (OA) - Owned StText object
  - Contains **ParagraphsOS** (OS) - Ordered paragraphs
    - Each paragraph contains **SegmentsOS** (OS) - Segments
    - Each segment references analyses via **AnalysesRS** (RS)

**Reasoning:** When you duplicate a text, you typically want the entire text structure (paragraphs, segments) copied. References to analyses can be shared.

**Recommendation:** Change to `deep=True`.

#### **ParagraphOperations** - deep=False SHOULD BE deep=True
**Current:** `deep=False`
**Owns:**
- **SegmentsOS** (OS) - Segments in order

**Reasoning:** Paragraphs exist within texts. Duplicating a paragraph should include its segments.

**Recommendation:** Change to `deep=True`.

#### **WfiAnalysisOperations** - deep=False is CORRECT
**Owns:** Only simple properties (morpheme/POS info)
**References:** Gloss, MSA references

**Recommendation:** Keep `deep=False`.

#### **WfiGlossOperations** - deep=False is CORRECT
**Owns:** Only MultiString (sense gloss)
**References:** Semantic domain references

**Recommendation:** Keep `deep=False`.

#### **WfiMorphBundleOperations** - deep=False is CORRECT
**Owns:** Only simple properties
**References:** Morph and MSA references

**Recommendation:** Keep `deep=False`.

#### **WordformOperations** - deep=False is QUESTIONABLE
**Current:** `deep=False`
**Owns:**
- **AnalysesOS** (OS) - Analyses for this wordform
- **ChecksOS** (OS) - Consistency checks

**Reasoning:** If you duplicate a wordform, you might want its analyses duplicated. However, wordform duplication is unusual—typically you don't duplicate words.

**Recommendation:** Keep `deep=False` for now. If wordform duplication becomes common, reconsider.

#### **DiscourseOperations** - deep=False is QUESTIONABLE
**Owns:**
- **RowsOS** (OS) - Chart rows
  - Each row owns **CellsOS** (OS) and **ClauseMarkersOS** (OS)

**Reasoning:** Discourse charts have complex nested structures. Duplicating a chart probably means you want the structure (rows, cells, markers).

**Recommendation:** Consider `deep=True`.

---

### NOTEBOOK DOMAIN

#### **DataNotebookOperations** - deep=False is CORRECT
Records in notebooks are typically unique data points, not structures meant to be duplicated.

#### **LocationOperations** - deep=False is CORRECT
References (geographic data), not owned objects.

#### **PersonOperations** - deep=False is CORRECT
Person records are unique individuals.

#### **NoteOperations** - deep=False is CORRECT
Notes are informational, not structural duplicates.

#### **AnthropologyOperations** - deep=False is CORRECT
Categorical references, not owned structures.

---

### LISTS DOMAIN

#### **PossibilityListOperations** - deep=False is QUESTIONABLE
**Owns:**
- **PossibilitiesOS** (OS) - List items (hierarchical)

**Reasoning:** Lists are often reusable structures (status lists, confidence levels, etc.). But if you're duplicating a custom list, you might want items included.

**Recommendation:** Keep `deep=False` by default. Users can manually duplicate items if needed.

#### **AgentOperations** - deep=False is CORRECT
Agents (publishers, researchers) are unique entities, not structural duplicates.

#### **PublicationOperations** - deep=False is CORRECT
Publications are unique metadata, not meant for duplication.

#### **TranslationTypeOperations** - deep=False is CORRECT
Type definitions, not structural duplicates.

#### **ConfidenceOperations** - deep=False is CORRECT
Categorical values, not structures.

#### **OverlayOperations** - deep=False is CORRECT
Overlay definitions, typically shared/reused.

---

### SYSTEM DOMAIN

#### **WritingSystemOperations** - deep=False is CORRECT
Writing systems are configuration objects, not meant for structural duplication.

#### **CustomFieldOperations** - deep=False is CORRECT
Field definitions are project-wide metadata.

#### **AnnotationDefOperations** - deep=False is CORRECT
Annotation definitions are project-wide.

#### **CheckOperations** - deep=False is CORRECT
Check definitions are reusable rules.

#### **ProjectSettingsOperations** - deep=False is CORRECT
Project-level settings, not duplicable.

---

### SHARED DOMAIN

#### **FilterOperations** - deep=False is CORRECT
Filters are conditions/rules, not structural objects meant for duplication.

#### **MediaOperations** - deep=False is CORRECT
Media files are resources, not structures.

---

## Summary Table: Recommended Changes

| Operation | Current | Recommended | Reason |
|-----------|---------|-------------|--------|
| **LexEntryOperations** | `deep=False` | **deep=True** | Owns SensesOS, AllomorphsOS, PronunciationsOS, EtymologiesOS |
| **LexSenseOperations** | `deep=False` | Optional: **deep=True** | Owns ExamplesOS, SensesOS (subsenses), PicturesOS |
| **TextOperations** | `deep=False` | **deep=True** | Owns ContentsOA → ParagraphsOS → SegmentsOS |
| **ParagraphOperations** | `deep=False` | **deep=True** | Owns SegmentsOS |
| **DiscourseOperations** | `deep=False` | Consider **deep=True** | Owns RowsOS → CellsOS + ClauseMarkersOS (complex chart structure) |
| **SemanticDomainOperations** | `deep=False` | Consider **deep=True** | Owns SubPossibilitiesOS (hierarchical categories) |
| All others | `deep=False` | Keep `deep=False` | Either own no complex objects or are shared/reference-based structures |

---

## Implementation Priority

### High Priority (Breaking Changes if Ignored)
1. **LexEntryOperations** - Most frequently duplicated, currently unusable for deep copies
2. **TextOperations** - Complete structure ownership, currently broken for text duplication
3. **ParagraphOperations** - Closely related to TextOperations

### Medium Priority (Good to Have)
4. **LexSenseOperations** - Useful but optional, users can manually duplicate senses
5. **DiscourseOperations** - If discourse analysis features are important

### Low Priority (Nice to Have)
6. **SemanticDomainOperations** - Depends on workflow; hierarchies can be manually managed

---

## Testing Recommendations

For each change:
1. Test shallow duplicate (`deep=False`) still works
2. Test deep duplicate (`deep=True`) creates independent objects
3. Verify references (RA/RC/RS) are shared, not copied
4. Check that modifying duplicate doesn't affect original
5. Verify owned objects are recursively cloned

---

## Notes

- This analysis assumes the pattern you described: when relationships are many-to-one or one-to-many with references, they can be shared
- For example: a duplicated phonological rule can reference the same phonemes without creating duplicates
- 1:1 relationships (OA/RA) are always safe to either copy or reference
- The key discriminator is whether an object is **owned** (OS/OA/OC) or **referenced** (RA/RS/RC)
