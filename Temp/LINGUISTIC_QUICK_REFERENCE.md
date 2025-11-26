# LINGUISTIC QUICK REFERENCE FOR DEMO FILES

**Quick checklist for programmer agents creating flexlibs demo files**

---

## 1. Test Data Naming Conventions

### ✅ DO USE:
- **Real words:** "run", "house", "dog", "tree"
- **Real morphemes:** "-ing", "un-", "-s", "√cur"
- **Standard POS:** "Verb", "Noun", "Adjective"
- **Real phonemes:** "p", "b", "t", "d" (with IPA)
- **Meaningful glosses:** "to move rapidly", "dwelling"

### ❌ DON'T USE:
- "foo", "bar", "baz"
- "test", "test1", "test2"
- "entry", "entry1", "thing"
- "word", "word1", "item"
- "x", "y", "z" (as phonemes)

---

## 2. Linguistic Terminology

### Morph Types
```python
"stem"      # Free morpheme, independent word
"root"      # Core morpheme, may be bound
"prefix"    # Before root (un-, pre-, re-)
"suffix"    # After root (-ing, -ed, -s)
"infix"     # Inside root
"circumfix" # Around root
```

### POS Labels (Standard)
```python
"Noun", "Verb", "Adjective", "Adverb"
"Pronoun", "Preposition", "Conjunction"
"Determiner", "Interjection"

# Subcategories
"Transitive Verb", "Intransitive Verb"
"Proper Noun", "Common Noun"
```

### Grammatical Categories
```python
"Number"    # Singular, Plural, Dual
"Person"    # 1st, 2nd, 3rd
"Tense"     # Past, Present, Future
"Aspect"    # Perfective, Imperfective, Progressive
"Mood"      # Indicative, Subjunctive, Imperative
"Case"      # Nominative, Accusative, Genitive, etc.
"Gender"    # Masculine, Feminine, Neuter
```

### Phonetic Features
```python
# Consonants
"voiced" / "voiceless"
"bilabial", "labiodental", "dental", "alveolar", "palatal", "velar", "glottal"
"stop", "fricative", "affricate", "nasal", "liquid", "glide"

# Vowels
"high", "mid", "low"
"front", "central", "back"
"rounded", "unrounded"
```

---

## 3. Glossing Conventions (Leipzig Rules)

### Case Usage
```python
# LOWERCASE = lexical morphemes
"run", "house", "dog", "cat"

# UPPERCASE = grammatical morphemes
"PROG", "PST", "PL", "1SG", "ACC"

# Hyphens separate morphemes
"run-PROG-PST"  # running (in past)
```

### Common Abbreviations
```
1, 2, 3        = 1st, 2nd, 3rd person
SG, PL, DU     = singular, plural, dual
PST, PRS, FUT  = past, present, future
PROG, PERF     = progressive, perfective
NOM, ACC, GEN  = nominative, accusative, genitive
M, F, N        = masculine, feminine, neuter
```

---

## 4. IPA Notation

### Brackets
```python
# [square brackets] = phonetic (surface form)
"[ɹʌn]"   # Phonetic pronunciation of "run"

# /slashes/ = phonemic (underlying form)
"/rʌn/"   # Phonemic representation
```

### Common IPA Symbols
```
Consonants:
p, b       = voiceless/voiced bilabial stops
t, d       = voiceless/voiced alveolar stops
k, g       = voiceless/voiced velar stops
m, n, ŋ    = bilabial, alveolar, velar nasals
f, v       = voiceless/voiced labiodental fricatives
s, z       = voiceless/voiced alveolar fricatives
ʃ, ʒ       = voiceless/voiced postalveolar fricatives
θ, ð       = voiceless/voiced dental fricatives
ɹ          = alveolar approximant (English "r")

Vowels:
i, u       = high front/back vowels
e, o       = mid front/back vowels
ɛ, ɔ       = mid-low front/back vowels
a          = low central vowel
ə          = schwa (mid central)
ʌ          = mid-back unrounded
```

---

## 5. Object Relationship Rules

### Dependency Order
```python
# ALWAYS create in this order:

# Lexicon
entry → sense → example
entry → allomorph
entry → etymology
entry → variant

# Grammar
POS → subcategories
grammatical_category → inflection_features
phoneme → natural_class → environment → rule

# Texts
text → paragraph → segment → wordform → analysis → morph_bundle

# System
writing_system → custom_field
```

### Valid Links
```python
# ✅ CORRECT
sense.POS = verb_pos              # Sense links to POS
sense.semantic_domain = domain    # Sense links to domain
example.sense = sense             # Example links to sense
analysis.wordform = wordform      # Analysis links to wordform
bundle.morph = entry              # Bundle links to entry
bundle.sense = sense              # Bundle links to sense

# ❌ WRONG
entry.POS = verb_pos              # Entry doesn't have POS (sense does!)
entry.semantic_domain = domain    # Entry doesn't have domain (sense does!)
example.entry = entry             # Example links to SENSE, not entry
```

---

## 6. Common Example Patterns

### Create Lexical Entry with Sense
```python
# Create entry
entry = project.LexEntry.Create("run", "stem")

# Add sense
sense = project.Senses.Create(entry, "to move rapidly on foot")

# Set definition
project.Senses.SetDefinition(sense,
    "To move at a speed faster than a walk by advancing each foot alternately")

# Set POS
verb = project.POS.Find("Verb")
project.Senses.SetPOS(sense, verb)

# Add example
example = project.Examples.Create(sense,
    vernacular="The dog runs in the park.",
    translation="The dog runs in the park.")
```

### Create Phoneme with Features
```python
p = project.Phonemes.Create("p", ["voiceless", "bilabial", "stop"])
b = project.Phonemes.Create("b", ["voiced", "bilabial", "stop"])
m = project.Phonemes.Create("m", ["voiced", "bilabial", "nasal"])
```

### Create Text with Analysis
```python
# Create text
text = project.Texts.Create("Genesis Creation Story", genre="narrative")

# Add paragraph
para = project.Paragraphs.Create(text,
    "In the beginning God created the heavens and the earth.")

# Add segment
segment = project.Segments.Create(para,
    vernacular="Mù kɛ́ mbɔ̀k.",
    translation="I went home.")

# Find wordform
wordform = project.Wordforms.Find("kɛ́")

# Create analysis
analysis = project.WfiAnalyses.Create(wordform)

# Add morph bundles
bundle = project.WfiMorphBundle.Create(analysis,
    morph=go_entry,
    sense=go_sense,
    gloss="go")
```

---

## 7. Semantic Domains (DDP)

### Standard Top-Level Domains
```
1. Universe, creation
   1.1 Sky
   1.2 World
   1.3 Water
   1.4 Living things

2. Person
   2.1 Body
   2.2 Body functions
   2.3 Sense, perceive
   2.4 Body condition
   2.5 Health
   2.6 Life

3. Language and thought
   3.1 Soul, spirit
   3.2 Think
   3.3 Want
   3.4 Emotion
   3.5 Communication

4. Social behavior
   4.1 Relationships
   4.2 Social activity
   4.3 Behavior
   4.4 Conflict

5. Daily life
   5.1 Household equipment
   5.2 Food
   5.3 Clothing
   5.4 Adornment

6. Work and occupation
   6.1 Work
   6.2 Agriculture
   6.3 Animal husbandry
   6.4 Hunt and fish

7. Physical actions
   7.1 Posture
   7.2 Move
   7.3 Move something
   7.4 Have, be with

8. States
   8.1 Quantity
   8.2 Big
   8.3 Quality
   8.4 Time
   8.5 Location

9. Grammar
```

---

## 8. Text Genres

### Common Genres
```python
"narrative"       # Stories
"procedural"      # How-to instructions
"conversation"    # Dialogue
"song"            # Musical texts
"riddle"          # Traditional riddles
"proverb"         # Folk sayings
"folk_tale"       # Traditional stories
"legend"          # Historical narratives
"myth"            # Origin stories
"recipe"          # Cooking instructions
"interview"       # Structured conversation
```

---

## 9. Quality Checklist

Before submitting demo file, verify:

### Linguistic Authenticity
- [ ] No "foo", "bar", "test" in data
- [ ] Real linguistic terminology used
- [ ] Glosses follow Leipzig conventions
- [ ] IPA notation correct (if used)
- [ ] Examples are complete sentences
- [ ] POS labels are standard
- [ ] Grammatical categories are standard

### Data Model Validity
- [ ] Objects created in dependency order
- [ ] All required fields set
- [ ] Links point to existing objects
- [ ] Relationships are valid types
- [ ] Writing systems configured correctly

### Workflow Correctness
- [ ] Entry created before senses
- [ ] Senses created before examples
- [ ] Phonemes defined before rules
- [ ] Text created before paragraphs
- [ ] Wordform exists before analysis

### Code Quality
- [ ] Operations methods used correctly
- [ ] Error handling appropriate
- [ ] Comments explain linguistic context
- [ ] Variable names descriptive
- [ ] Demo cleanup performed

---

## 10. Writing System Tags

### ISO 639-3 Language Codes
```python
"en"  # English
"fr"  # French
"es"  # Spanish
"de"  # German
"ken" # Kenyang (example)
```

### Script Codes
```python
"Latn"  # Latin script
"Cyrl"  # Cyrillic
"Arab"  # Arabic
"Deva"  # Devanagari
```

### Special Tags
```python
"en-fonipa"   # English in IPA
"ken-fonipa"  # Kenyang in IPA
"en-US"       # American English
"en-GB"       # British English
```

---

## 11. Error Handling Pattern

```python
try:
    # Create test data
    entry = project.LexEntry.Create("run", "stem")
    sense = project.Senses.Create(entry, "to move rapidly")

    # Demonstrate operations
    print(f"Created entry: {project.LexEntry.GetHeadword(entry)}")
    print(f"Gloss: {project.Senses.GetGloss(sense)}")

except Exception as e:
    print(f"Error in demo: {e}")

finally:
    # Cleanup test data
    if entry:
        project.LexEntry.Delete(entry)
```

---

## 12. Demo File Template

```python
#!/usr/bin/env python3
"""
Demo for [OperationsClass]

Demonstrates [brief description of functionality]
"""

from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_[operations]():
    """
    Demonstrate [OperationsClass] functionality.
    """

    # Initialize
    FLExInitialize()
    project = FLExProject()

    try:
        # Open project
        project.OpenProject("Kenyang-M", writeEnabled=True)

        print("=" * 60)
        print("[OperationsClass] Demonstration")
        print("=" * 60)

        # --- 1. Create test data ---
        print("\n1. Creating test data:")
        # [linguistically authentic test data]

        # --- 2. Demonstrate Read operations ---
        print("\n2. Reading data:")
        # [demonstrate Get/Find methods]

        # --- 3. Demonstrate Update operations ---
        print("\n3. Updating data:")
        # [demonstrate Set methods]

        # --- 4. Demonstrate relationships ---
        print("\n4. Working with relationships:")
        # [demonstrate links between objects]

        # --- 5. Cleanup ---
        print("\n5. Cleanup:")
        # [remove test data]

        print("\n" + "=" * 60)
        print("Demonstration complete!")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close project
        project.CloseProject()
        FLExCleanup()

if __name__ == "__main__":
    demo_[operations]()
```

---

## 13. Common Mistakes to Avoid

### ❌ Wrong Order
```python
# DON'T: Create example before sense
example = project.Examples.Create(sense, "text", "trans")
sense = project.Senses.Create(entry, "gloss")  # Too late!
```

### ✅ Correct Order
```python
# DO: Create sense first
sense = project.Senses.Create(entry, "gloss")
example = project.Examples.Create(sense, "text", "trans")
```

---

### ❌ Wrong Link
```python
# DON'T: Link POS to entry
project.LexEntry.SetPOS(entry, verb_pos)  # Entry doesn't have POS!
```

### ✅ Correct Link
```python
# DO: Link POS to sense
project.Senses.SetPOS(sense, verb_pos)  # Sense has POS
```

---

### ❌ Non-linguistic Data
```python
# DON'T: Use generic test data
entry = project.LexEntry.Create("test123", "stem")
sense = project.Senses.Create(entry, "foo bar")
```

### ✅ Linguistic Data
```python
# DO: Use real linguistic data
entry = project.LexEntry.Create("run", "stem")
sense = project.Senses.Create(entry, "to move rapidly on foot")
```

---

## 14. Resource Links

- **Full Guide:** `LINGUISTIC_VALIDATION_GUIDE.md`
- **Leipzig Glossing Rules:** https://www.eva.mpg.de/lingua/resources/glossing-rules.php
- **IPA Chart:** https://www.ipachart.com/
- **DDP Semantic Domains:** https://semdom.org/
- **FLEx Documentation:** https://software.sil.org/fieldworks/

---

## 15. Quick Glossary

| Term | Meaning | Example |
|------|---------|---------|
| **Gloss** | Brief translation | "to run" |
| **Definition** | Full explanation | "To move rapidly on foot..." |
| **Lexeme** | Abstract word | RUN (covers run, runs, ran) |
| **Morph** | Form of morpheme | "run-", "ran" |
| **Sense** | Individual meaning | run₁ (move), run₂ (operate) |
| **POS** | Part of speech | Verb, Noun, Adjective |
| **IPA** | Phonetic notation | [ɹʌn] |
| **IGT** | Interlinear text | Baseline + gloss + translation |

---

**Document Status:** ✅ QUICK REFERENCE
**Version:** 1.0
**Last Updated:** 2025-11-25
**Use With:** LINGUISTIC_VALIDATION_GUIDE.md (full details)
