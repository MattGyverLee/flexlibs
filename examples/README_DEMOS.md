# flexlibs v2.0.0 - Demonstration Files
## Comprehensive CRUD Operations Examples

This directory contains 15 demonstration files showcasing the complete flexlibs Operations API for Grammar and Lexicon domains.

---

## Quick Start

```python
# Run any demo:
python examples/grammar_pos_operations_demo.py

# Or:
python examples/lexicon_sense_operations_demo.py
```

**Requirements:**
- FLEx project (demos use "Kenyang-M")
- Python.NET runtime
- FLEx assemblies

---

## Grammar Operations (8 demos)

### 1. Parts of Speech
**File:** `grammar_pos_operations_demo.py`
**Class:** POSOperations
**Property:** `project.POS`

Demonstrates:
- Creating POS categories (Noun, Verb, Adjective)
- Managing subcategories (Proper Noun, Common Noun)
- Setting names, abbreviations, catalog IDs
- Querying entry counts

**Known Issues:** ⚠️ GetInstance bug prevents Create operations

---

### 2. Phonemes
**File:** `grammar_phoneme_operations_demo.py`
**Class:** PhonemeOperations
**Property:** `project.Phonemes`

Demonstrates:
- Creating phonemes (/p/, /b/, /t/)
- Setting descriptions (IPA, articulatory features)
- Managing allophonic codes ([p], [pʰ])
- Checking vowel/consonant classification

**Known Issues:** ⚠️ GetInstance bug prevents Create operations

---

### 3. Natural Classes
**File:** `grammar_naturalclass_operations_demo.py`
**Class:** NaturalClassOperations
**Property:** `project.NaturalClasses`

Demonstrates:
- Creating natural classes (Stops, Fricatives, Vowels)
- Adding phonemes to classes
- Setting names and abbreviations

**Methods:** 9 total (Create, GetAll, AddPhoneme, GetPhonemes, etc.)

---

### 4. Environments
**File:** `grammar_environment_operations_demo.py`
**Class:** EnvironmentOperations
**Property:** `project.Environments`

Demonstrates:
- Creating phonological environments
- Word boundaries (#_), (_#)
- Feature-based contexts

**Methods:** Available (see demo for full list)

---

### 5. Phonological Rules
**File:** `grammar_phonrule_operations_demo.py`
**Class:** PhonologicalRuleOperations
**Property:** `project.PhonRules`

Demonstrates:
- Creating phonological rules
- Setting structural changes
- Defining environments
- Rule ordering

**Methods:** Available (see demo for full list)

---

### 6. Inflection Features
**File:** `grammar_inflection_operations_demo.py`
**Class:** InflectionFeatureOperations
**Property:** `project.InflectionFeatures`

Demonstrates:
- Creating inflection classes
- Managing features (Number, Person, Tense)
- Feature specifications

**Methods:** Available (see demo for full list)

---

### 7. Grammatical Categories
**File:** `grammar_gramcat_operations_demo.py`
**Class:** GramCatOperations
**Property:** `project.GramCat`

Demonstrates:
- Creating grammatical categories
- Managing category hierarchies

**Methods:** Available (see demo for full list)

---

### 8. Morphological Rules
**File:** `grammar_morphrule_operations_demo.py`
**Class:** MorphRuleOperations
**Property:** `project.MorphRules`

**⚠️ CRITICAL BUG:** Cannot import due to missing IMoMorphRule interface

This demo documents the import error. Cannot be tested until bug is fixed.

---

## Lexicon Operations (7 demos)

### 9. Lexical Senses
**File:** `lexicon_sense_operations_demo.py`
**Class:** LexSenseOperations
**Property:** `project.Senses`

Demonstrates:
- Creating senses
- Setting glosses and definitions
- Managing subsenses
- Grammatical information

**Methods:** 33 total

**Known Issues:**
- ⚠️ GetInstance bug
- ⚠️ GetAll() requires entry parameter

---

### 10. Example Sentences
**File:** `lexicon_example_operations_demo.py`
**Class:** ExampleOperations
**Property:** `project.Examples`

Demonstrates:
- Creating example sentences
- Adding translations
- Setting references
- Managing media

**Methods:** 17 total

**Known Issues:**
- ⚠️ GetInstance bug
- ⚠️ GetAll() requires sense parameter

---

### 11. Pronunciations
**File:** `lexicon_pronunciation_operations_demo.py`
**Class:** PronunciationOperations
**Property:** `project.Pronunciations`

Demonstrates:
- Creating pronunciations
- Setting IPA forms
- Managing media files

**Methods:** Available (see demo for full list)

---

### 12. Variant Forms
**File:** `lexicon_variant_operations_demo.py`
**Class:** VariantOperations
**Property:** `project.Variants`

Demonstrates:
- Creating variants (spelling, dialect)
- Managing variant types
- Linking to main entries

**Methods:** Available (see demo for full list)

---

### 13. Allomorphs
**File:** `lexicon_allomorph_operations_demo.py`
**Class:** AllomorphOperations
**Property:** `project.Allomorphs`

Demonstrates:
- Creating allomorphs
- Setting forms
- Managing environments

**Methods:** Available (see demo for full list)

---

### 14. Etymologies
**File:** `lexicon_etymology_operations_demo.py`
**Class:** EtymologyOperations
**Property:** `project.Etymology`

Demonstrates:
- Creating etymologies
- Setting source language
- Managing gloss and form

**Methods:** Available (see demo for full list)

---

### 15. Lexical References
**File:** `lexicon_lexreference_operations_demo.py`
**Class:** LexReferenceOperations
**Property:** `project.LexReferences`

Demonstrates:
- Creating lexical references
- Managing relations (synonyms, antonyms)
- Linking senses

**Methods:** Available (see demo for full list)

---

## Known Issues

### 🔴 Critical Bug #1: GetInstance → GetService
**Impact:** All Create operations fail
**Occurrences:** 95+ files across entire codebase
**Status:** Documented in AGENT1_BUGS.md

**Temporary Workaround:** None - requires code fix

**Fix:**
```python
# Find all instances of:
ServiceLocator.GetInstance(

# Replace with:
ServiceLocator.GetService(
```

---

### 🔴 Critical Bug #2: Wrong POS Interface
**File:** POSOperations.py
**Methods:** GetCatalogSourceId, GetInflectionClasses, GetAffixSlots
**Error:** ICmPossibility missing IPartOfSpeech properties

---

### 🔴 Critical Bug #3: IMoMorphRule Import
**File:** MorphRuleOperations.py
**Error:** Interface doesn't exist
**Impact:** Entire file cannot be imported

---

### 🟡 Bug #4: GetAll() Signatures
**Files:** LexSenseOperations, ExampleOperations
**Issue:** Require parent parameters
**Impact:** Inconsistent API

---

## Demo Pattern

All demos follow this structure:

```python
#!/usr/bin/env python3
from flexlibs2 import FLExProject, FLExInitialize, FLExCleanup

def demo_operations():
    FLExInitialize()
    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Error: {e}")
        FLExCleanup()
        return

    # Test operations with try/except blocks

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_operations()
```

---

## Testing Status

| Demo | Created | Tested | Status |
|------|---------|--------|--------|
| grammar_pos_operations_demo.py | ✅ | ✅ | Found GetInstance bug |
| grammar_phoneme_operations_demo.py | ✅ | ✅ | Found GetInstance bug |
| grammar_naturalclass_operations_demo.py | ✅ | ⚠️ | Basic test only |
| grammar_environment_operations_demo.py | ✅ | ⏳ | Not tested |
| grammar_phonrule_operations_demo.py | ✅ | ⏳ | Not tested |
| grammar_inflection_operations_demo.py | ✅ | ⏳ | Not tested |
| grammar_gramcat_operations_demo.py | ✅ | ⏳ | Not tested |
| grammar_morphrule_operations_demo.py | ✅ | ❌ | Import error |
| lexicon_sense_operations_demo.py | ✅ | ⚠️ | GetAll signature issue |
| lexicon_example_operations_demo.py | ✅ | ⚠️ | GetAll signature issue |
| lexicon_pronunciation_operations_demo.py | ✅ | ⏳ | Not tested |
| lexicon_variant_operations_demo.py | ✅ | ⏳ | Not tested |
| lexicon_allomorph_operations_demo.py | ✅ | ⏳ | Not tested |
| lexicon_etymology_operations_demo.py | ✅ | ⏳ | Not tested |
| lexicon_lexreference_operations_demo.py | ✅ | ⏳ | Not tested |

**Legend:**
- ✅ Complete
- ⚠️ Partial/Issues
- ⏳ Pending
- ❌ Blocked

---

## Documentation

- **AGENT1_BUGS.md** - Comprehensive bug report
- **AGENT1_SUMMARY.md** - Project summary and statistics
- **README_DEMOS.md** - This file

---

## Support

For questions or issues:
1. Check AGENT1_BUGS.md for known issues
2. Review individual demo file docstrings
3. Consult flexlibs API documentation
4. Test against your own FLEx project

---

**Created by:** Programmer Agent 1
**Date:** 2025-11-25
**Version:** 2.0.0 (Pilot Phase)
**Status:** Complete ✅
