# LINGUISTIC VALIDATION GUIDE FOR FLEXLIBS v2.0.0 DEMO FILES

**Version:** 1.0
**Date:** 2025-11-25
**Target Audience:** Programmer Agents creating demo files for 42 Operations classes
**Project Context:** Kenyang-M FLEx Project (Real linguistic database)
**Status:** AUTHORITATIVE REFERENCE

---

## Table of Contents

1. [Introduction & Purpose](#1-introduction--purpose)
2. [FLEx Data Model Overview](#2-flex-data-model-overview)
3. [Test Data Guidelines by Domain](#3-test-data-guidelines-by-domain)
4. [Linguistic Terminology Reference](#4-linguistic-terminology-reference)
5. [Workflow Validation](#5-workflow-validation)
6. [Quality Checklist](#6-quality-checklist)
7. [Common Pitfalls to Avoid](#7-common-pitfalls-to-avoid)
8. [Domain-Specific Guidance](#8-domain-specific-guidance)

---

## 1. Introduction & Purpose

### 1.1 What This Guide Does

This guide ensures that demo files for flexlibs v2.0.0 Operations classes are **linguistically authentic** and follow **real-world FLEx usage patterns**. It provides:

- **Valid test data** that linguists would actually create
- **Correct terminology** for morphology, phonology, syntax, and lexicon
- **Proper workflows** matching how FLEx is used in the field
- **Realistic examples** based on linguistic research standards

### 1.2 Why Linguistic Accuracy Matters

FLEx is used by field linguists working with endangered languages. Demo files must:

- **Model best practices** for linguistic analysis
- **Use authentic examples** (not "foo", "bar", "test")
- **Follow linguistic conventions** (IGT standards, IPA notation, etc.)
- **Represent valid object relationships** in the FLEx data model

### 1.3 The Kenyang-M Project Context

All demos execute against the **Kenyang-M FLEx project**, which contains real linguistic data. Demos should:

- **Read existing data** where appropriate (POS, semantic domains, etc.)
- **Create test entries** that fit linguistically with the project
- **Clean up test data** after demos run
- **Avoid corrupting** the existing linguistic database

---

## 2. FLEx Data Model Overview

### 2.1 Core Data Hierarchy

```
FLEx Project
│
├── Lexicon
│   ├── Lexical Entry (word/morpheme)
│   │   ├── Lexeme Form (base form)
│   │   ├── Citation Form (dictionary form)
│   │   ├── Morph Type (stem/root/affix)
│   │   ├── Allomorphs (variant forms)
│   │   └── Senses (meanings)
│   │       ├── Gloss (brief translation)
│   │       ├── Definition (full meaning)
│   │       ├── Part of Speech
│   │       ├── Semantic Domains
│   │       ├── Examples (sentences)
│   │       └── Subsenses (nested meanings)
│   │
│   ├── Lexical References (relations)
│   │   ├── Synonyms, Antonyms
│   │   ├── Hypernyms, Hyponyms
│   │   └── Whole/Part relations
│   │
│   └── Reversal Index (target language → vernacular)
│
├── Grammar
│   ├── Parts of Speech (hierarchical)
│   ├── Grammatical Categories (gender, number, tense, etc.)
│   ├── Inflection Features (person, case, aspect, etc.)
│   ├── Phonemes (segmental inventory)
│   ├── Natural Classes (phoneme groupings)
│   ├── Phonological Environments (contexts)
│   ├── Phonological Rules (sound changes)
│   └── Morphological Rules (word formation)
│
├── Texts & Words (Interlinear Glossed Text)
│   ├── Text (document)
│   │   ├── Paragraphs
│   │   │   └── Segments (phrases/sentences)
│   │   │       └── Wordforms (surface forms)
│   │   │           └── Analyses (linguistic parsing)
│   │   │               ├── Glosses (translations)
│   │   │               └── Morph Bundles (morpheme breakdown)
│   │   │                   ├── Morph (links to lexicon)
│   │   │                   ├── Sense (links to sense)
│   │   │                   └── MSA (morphosyntactic features)
│   │   └── Media (audio/video recordings)
│   │
│   ├── Wordform Inventory (all surface forms)
│   └── Discourse Charts (constituent structure)
│
├── Notebook
│   ├── Data Notebook (field notes)
│   ├── Notes (annotations)
│   ├── People (consultants, researchers)
│   ├── Locations (villages, regions)
│   └── Anthropology (cultural data)
│
├── Lists
│   ├── Possibility Lists (custom taxonomies)
│   ├── Semantic Domains (meaning categories)
│   ├── Publications (lexicon outputs)
│   ├── Translation Types (free, literal, etc.)
│   ├── Confidence Levels (data reliability)
│   └── Agents (parsers, annotators)
│
└── System
    ├── Writing Systems (orthographies)
    ├── Custom Fields (user-defined data)
    ├── Project Settings
    ├── Annotation Types
    └── Consistency Checks
```

### 2.2 Key Relationships

**Entry → Sense → Example**
- One entry can have multiple senses
- Each sense can have multiple examples
- Examples illustrate the sense in context

**Entry → Allomorph → Morph Type**
- Entries have a lexeme form (base allomorph)
- Additional allomorphs represent phonological variants
- Each allomorph has a morph type (stem, prefix, suffix, etc.)

**Sense → POS → Grammatical Categories**
- Each sense has a part of speech
- POS determines applicable grammatical categories
- Categories define inflectional features

**Wordform → Analysis → Gloss + Morph Bundles**
- Surface wordforms get analyzed morphologically
- Each analysis has a wordform-level gloss
- Morph bundles break down into individual morphemes

---

## 3. Test Data Guidelines by Domain

### 3.1 Grammar Domain

#### Parts of Speech (POSOperations)

**Linguistically Valid Examples:**
```python
# Major categories
pos = project.POS.Create("Verb", "V")
pos = project.POS.Create("Noun", "N")
pos = project.POS.Create("Adjective", "Adj")

# Subcategories (hierarchical)
verb = project.POS.Find("Verb")
transitive = project.POS.CreateSubcategory(verb, "Transitive Verb", "VT")
intransitive = project.POS.CreateSubcategory(verb, "Intransitive Verb", "VI")

# NOT: "Thing", "Word", "TestPOS", "Foo"
```

**Terminology:**
- Use standard linguistic POS labels (Noun, Verb, Adjective, Adverb, Pronoun, etc.)
- Abbreviations should be conventional (N, V, Adj, Adv, Pro, etc.)
- Subcategories follow hierarchical logic (Verb → Transitive/Intransitive)

**Workflow:**
1. Create major categories first (Noun, Verb, Adjective)
2. Add subcategories as needed (Common Noun → Proper Noun)
3. Link to grammatical categories
4. Use in sense assignment

---

#### Phonemes (PhonemeOperations)

**Linguistically Valid Examples:**
```python
# Consonants with proper phonetic features
p = project.Phonemes.Create("p", ["voiceless", "bilabial", "stop"])
b = project.Phonemes.Create("b", ["voiced", "bilabial", "stop"])
m = project.Phonemes.Create("m", ["voiced", "bilabial", "nasal"])

# Vowels with height, backness, rounding
i = project.Phonemes.Create("i", ["high", "front", "unrounded"])
u = project.Phonemes.Create("u", ["high", "back", "rounded"])
a = project.Phonemes.Create("a", ["low", "central", "unrounded"])

# NOT: "x", "q", "z" without proper features
# NOT: Generic features like "feature1", "test"
```

**Terminology:**
- **Segments** = individual speech sounds (phonemes)
- **IPA** = International Phonetic Alphabet (use proper symbols)
- **Features** = phonetic properties (voiced, bilabial, nasal, etc.)
- **Allophone** = phonetic variant of a phoneme

**Phonetic Features (Common):**
- **Place:** bilabial, labiodental, dental, alveolar, palatal, velar, glottal
- **Manner:** stop, fricative, affricate, nasal, liquid, glide
- **Voicing:** voiced, voiceless
- **Vowel Height:** high, mid, low
- **Vowel Backness:** front, central, back
- **Rounding:** rounded, unrounded

**Workflow:**
1. Define consonant inventory with features
2. Define vowel inventory with features
3. Group into natural classes
4. Define phonological rules using environments

---

#### Natural Classes (NaturalClassOperations)

**Linguistically Valid Examples:**
```python
# Group phonemes by shared features
stops = project.NaturalClass.Create("Stops", [p, b, t, d, k, g])
nasals = project.NaturalClass.Create("Nasals", [m, n, ŋ])
high_vowels = project.NaturalClass.Create("High Vowels", [i, u])

# NOT: Random groupings without phonetic basis
# NOT: "TestClass", "PhonemeGroup1"
```

**Terminology:**
- **Natural class** = phonemes sharing phonetic features
- Groups should have phonological motivation
- Used in phonological rule formulation

**Workflow:**
1. Create phoneme inventory first
2. Identify phonemes sharing features
3. Create natural classes for rule writing
4. Use in phonological environments

---

#### Phonological Environments (EnvironmentOperations)

**Linguistically Valid Examples:**
```python
# Word-initial position
env = project.Environment.Create("word-initial", "#_")

# Word-final position
env = project.Environment.Create("word-final", "_#")

# Before high vowels
env = project.Environment.Create("before high vowel", "_[+high, +vowel]")

# Between voiced consonants
env = project.Environment.Create("intervocalic", "[+voice]_[+voice]")

# NOT: "env1", "test_environment"
```

**Terminology:**
- **Environment** = phonological context where rule applies
- **#** = word boundary
- **_** = target segment position
- **[ ]** = feature bundle

**Workflow:**
1. Define phonemes and natural classes first
2. Create environments for rule contexts
3. Use in phonological rule definitions

---

#### Phonological Rules (PhonologicalRuleOperations)

**Linguistically Valid Examples:**
```python
# Nasal assimilation: n → m / _p,b
rule = project.PhonologicalRule.Create(
    name="Nasal Place Assimilation",
    input_segment="n",
    output_segment="m",
    environment="before bilabial"
)

# Vowel harmony: a → e / in front vowel word
# Final devoicing: b → p / _#

# NOT: "rule1", "test_rule", "change"
```

**Terminology:**
- **Input** = underlying form
- **Output** = surface form
- **Environment** = context of application
- **Ordered rules** = apply sequentially

**Workflow:**
1. Define phoneme inventory
2. Create natural classes
3. Define environments
4. Create rules with proper input/output/environment
5. Order rules if needed

---

#### Inflection Features (InflectionFeatureOperations)

**Linguistically Valid Examples:**
```python
# Number features
singular = project.InflectionFeature.Create("singular", "sg", "Number")
plural = project.InflectionFeature.Create("plural", "pl", "Number")

# Person features
first_person = project.InflectionFeature.Create("1st person", "1", "Person")
second_person = project.InflectionFeature.Create("2nd person", "2", "Person")
third_person = project.InflectionFeature.Create("3rd person", "3", "Person")

# Tense features
past = project.InflectionFeature.Create("past", "PST", "Tense")
present = project.InflectionFeature.Create("present", "PRS", "Tense")
future = project.InflectionFeature.Create("future", "FUT", "Tense")

# NOT: "feature1", "test", "thing"
```

**Terminology:**
- **Inflection** = grammatical modification (tense, number, person, etc.)
- **Feature** = grammatical property
- **Value** = specific realization (singular vs. plural)
- **Category** = feature group (Number, Person, Tense, etc.)

**Common Inflectional Categories:**
- **Number:** singular, plural, dual, trial, paucal
- **Person:** 1st, 2nd, 3rd
- **Gender:** masculine, feminine, neuter
- **Case:** nominative, accusative, genitive, dative, etc.
- **Tense:** past, present, future
- **Aspect:** perfective, imperfective, progressive
- **Mood:** indicative, subjunctive, imperative

**Workflow:**
1. Create grammatical categories
2. Define features within categories
3. Link to parts of speech
4. Use in morphological analysis

---

#### Grammatical Categories (GramCatOperations)

**Linguistically Valid Examples:**
```python
# Agreement categories
number = project.GramCat.Create("Number")
person = project.GramCat.Create("Person")
gender = project.GramCat.Create("Gender")

# Verbal categories
tense = project.GramCat.Create("Tense")
aspect = project.GramCat.Create("Aspect")
mood = project.GramCat.Create("Mood")

# Nominal categories
case = project.GramCat.Create("Case")
definiteness = project.GramCat.Create("Definiteness")

# NOT: "Category1", "TestCat", "Thing"
```

**Terminology:**
- **Grammatical category** = class of inflectional features
- Categories group related features
- Categories apply to specific POS

**Workflow:**
1. Define POS first
2. Create grammatical categories
3. Link categories to POS
4. Define inflection features within categories

---

### 3.2 Lexicon Domain

#### Lexical Entries (LexEntryOperations)

**Linguistically Valid Examples:**
```python
# Free morphemes (words)
entry = project.LexEntry.Create("run", "stem")
entry = project.LexEntry.Create("house", "stem")

# Bound morphemes (affixes)
entry = project.LexEntry.Create("-ing", "suffix")
entry = project.LexEntry.Create("un-", "prefix")

# Roots
entry = project.LexEntry.Create("√cur", "root")  # Latin "run"

# NOT: "test", "foo", "entry1", "thing"
```

**Terminology:**
- **Lexeme** = abstract lexical unit
- **Lexeme form** = citation/base form
- **Citation form** = dictionary headword form
- **Morph type** = morpheme category (stem, root, affix, etc.)

**Morph Types:**
- **stem** = free morpheme, independent word
- **root** = core morpheme, may be bound
- **prefix** = affix before root
- **suffix** = affix after root
- **infix** = affix inside root
- **circumfix** = discontinuous affix around root
- **clitic** = phonologically bound but syntactically independent

**Workflow:**
1. Create entry with lexeme form and morph type
2. Set citation form if different from lexeme
3. Add senses with glosses
4. Add allomorphs if needed
5. Link to etymologies, variants, etc.

---

#### Lexical Senses (LexSenseOperations)

**Linguistically Valid Examples:**
```python
# Polysemy (related meanings)
run_entry = project.LexEntry.Find("run")
sense1 = project.Senses.Create(run_entry, "to move rapidly on foot")
sense2 = project.Senses.Create(run_entry, "to operate or function")
sense3 = project.Senses.Create(run_entry, "a point scored in baseball")

# Homonymy (unrelated meanings - separate entries)
bank1 = project.LexEntry.Create("bank", "stem")  # financial
bank1_sense = project.Senses.Create(bank1, "financial institution")

bank2 = project.LexEntry.Create("bank", "stem")  # river
bank2_sense = project.Senses.Create(bank2, "land alongside river")

# NOT: "meaning1", "sense1", "test meaning"
```

**Terminology:**
- **Sense** = individual meaning of a lexeme
- **Gloss** = brief translation (1-5 words)
- **Definition** = full explanation of meaning
- **Polysemy** = one entry, multiple related senses
- **Homonymy** = separate entries, unrelated meanings

**Gloss vs. Definition:**
```python
# GLOSS: Brief, translational
sense.gloss = "to run"
sense.gloss = "house"

# DEFINITION: Full, explanatory
sense.definition = "To move at a speed faster than a walk by alternately advancing each foot"
sense.definition = "A building designed for people to live in"
```

**Workflow:**
1. Create entry first
2. Add senses with glosses
3. Set definitions (more detailed than glosses)
4. Assign part of speech to each sense
5. Link to semantic domains
6. Add examples illustrating usage

---

#### Examples (ExampleOperations)

**Linguistically Valid Examples:**
```python
# Complete sentence in vernacular
example = project.Examples.Create(
    sense,
    vernacular="The dog runs in the park.",
    translation="The dog runs in the park."
)

# From actual language data (better)
example = project.Examples.Create(
    sense,
    vernacular="Mù kɛ́ mbɔ̀k.",  # Kenyang
    translation="I went home."
)

# NOT: "Example sentence.", "Test.", "This is a test."
```

**Terminology:**
- **Example** = illustrative sentence showing usage
- **Vernacular** = language being documented
- **Translation** = target language (usually English)
- **Back translation** = literal word-for-word gloss

**IGT (Interlinear Glossed Text) Standards:**
```
Vernacular:    Mù    kɛ́    mbɔ̀k
Word-by-word:  I     went  home
Translation:   "I went home."
```

**Workflow:**
1. Create sense first
2. Add example sentences
3. Provide vernacular text
4. Provide free translation
5. Optionally link to text corpus

---

#### Pronunciations (PronunciationOperations)

**Linguistically Valid Examples:**
```python
# IPA pronunciation
pronunciation = project.Pronunciation.Create(
    entry,
    ipa="[ɹʌn]",  # IPA notation
    media_file="run_audio.wav"
)

# Dialectal variants
pronunciation1 = project.Pronunciation.Create(entry, "[tomɑto]")  # US
pronunciation2 = project.Pronunciation.Create(entry, "[təmɑːtəʊ]")  # UK

# NOT: "pronunciation1", "[test]", "sound"
```

**Terminology:**
- **Pronunciation** = phonetic realization
- **IPA** = International Phonetic Alphabet (use proper brackets)
- **[ ]** = phonetic notation (surface form)
- **/ /** = phonemic notation (underlying form)
- **Dialect** = regional/social variety

**IPA Conventions:**
- Use proper Unicode IPA characters
- Square brackets for phonetic: [ɹʌn]
- Slashes for phonemic: /rʌn/
- Include stress marks: [ˈtɑːmətoʊ]

**Workflow:**
1. Create entry first
2. Add IPA pronunciation
3. Link to audio media if available
4. Mark dialectal variants

---

#### Variants (VariantOperations)

**Linguistically Valid Examples:**
```python
# Dialectal variant
color_us = project.LexEntry.Find("color")
colour_uk = project.Variant.Create(color_us, "colour", "dialectal")

# Free variant (pronunciation/spelling)
variant = project.Variant.Create(entry, "alternate_form", "free")

# Inflectional variant
go = project.LexEntry.Find("go")
went = project.Variant.Create(go, "went", "past tense")

# NOT: "variant1", "alt", "other"
```

**Terminology:**
- **Variant** = alternate form of same lexeme
- **Variant type:**
  - **Dialectal** = regional/social variety
  - **Free** = interchangeable forms
  - **Spelling** = orthographic alternatives
  - **Inflectional** = grammatical forms
  - **Stem** = allostems

**Workflow:**
1. Create main entry first
2. Create variant linked to main entry
3. Specify variant type
4. Optionally note dialect/register

---

#### Allomorphs (AllomorphOperations)

**Linguistically Valid Examples:**
```python
# Phonologically conditioned allomorphs
entry = project.LexEntry.Find("-s")  # plural suffix

allomorph1 = project.Allomorph.Create(entry, "-s", "after voiceless")  # cats
allomorph2 = project.Allomorph.Create(entry, "-z", "after voiced")     # dogs
allomorph3 = project.Allomorph.Create(entry, "-ɪz", "after sibilants") # buses

# Suppletive allomorphs
go = project.LexEntry.Find("go")
allomorph1 = project.Allomorph.Create(go, "go", "present")
allomorph2 = project.Allomorph.Create(go, "went", "past")  # suppletive

# NOT: "form1", "allo1", "alternate"
```

**Terminology:**
- **Allomorph** = phonological variant of morpheme
- **Phonologically conditioned** = environment determines form
- **Morphologically conditioned** = grammatical context determines form
- **Suppletive** = unrelated forms (go/went)

**Workflow:**
1. Create entry with lexeme form
2. Add allomorphs for phonological variants
3. Specify conditioning environments
4. Link allomorphs to morph types

---

#### Etymology (EtymologyOperations)

**Linguistically Valid Examples:**
```python
# Borrowed word
etymology = project.Etymology.Create(
    entry,
    source_language="French",
    source_form="maison",
    etymology_type="borrowing",
    comment="Borrowed during Norman conquest"
)

# Cognate
etymology = project.Etymology.Create(
    entry,
    source_language="Proto-Indo-European",
    source_form="*h₂ster-",
    etymology_type="cognate"
)

# Compound
etymology = project.Etymology.Create(
    entry,
    etymology_type="compound",
    component1="black",
    component2="berry"
)

# NOT: "from language1", "etymology test"
```

**Terminology:**
- **Etymology** = word origin and history
- **Source language** = language of origin
- **Borrowing** = word taken from another language
- **Cognate** = genetically related word
- **Compound** = word formed from multiple roots
- **Derivation** = word formed with affixes

**Workflow:**
1. Create entry first
2. Add etymology information
3. Specify source language and form
4. Note etymology type
5. Add scholarly comments if needed

---

#### Lexical References (LexReferenceOperations)

**Linguistically Valid Examples:**
```python
# Synonyms
big = project.LexEntry.Find("big")
large = project.LexEntry.Find("large")
project.LexReference.Create("synonym", [big, large])

# Antonyms
hot = project.LexEntry.Find("hot")
cold = project.LexEntry.Find("cold")
project.LexReference.Create("antonym", [hot, cold])

# Hypernym/Hyponym (animal > dog)
animal = project.LexEntry.Find("animal")
dog = project.LexEntry.Find("dog")
project.LexReference.Create("hypernym", animal, dog)

# Part/Whole (tree > leaf)
tree = project.LexEntry.Find("tree")
leaf = project.LexEntry.Find("leaf")
project.LexReference.Create("part-whole", tree, leaf)

# NOT: "ref1", "relation", "link"
```

**Terminology:**
- **Synonym** = similar meaning
- **Antonym** = opposite meaning
- **Hypernym** = superordinate (animal for dog)
- **Hyponym** = subordinate (dog for animal)
- **Meronym** = part (leaf for tree)
- **Holonym** = whole (tree for leaf)

**Workflow:**
1. Create both entries first
2. Create lexical reference with type
3. Specify directionality if asymmetric
4. Document in lexicon views

---

#### Reversal Index (ReversalOperations)

**Linguistically Valid Examples:**
```python
# English → Vernacular reversal
reversal = project.Reversal.Create(
    target_language="English",
    headword="house",
    vernacular_entries=[house_entry1, house_entry2]
)

# Multiple vernacular entries for one English word
reversal = project.Reversal.Create(
    target_language="English",
    headword="go",
    vernacular_entries=[go_entry, walk_entry, leave_entry]
)

# NOT: "entry1", "test", "reversal1"
```

**Terminology:**
- **Reversal index** = target language → vernacular finder
- **Target language** = language of glosses (usually English)
- **Reversal entry** = headword in target language
- **Linked entries** = vernacular entries with this gloss

**Workflow:**
1. Create vernacular entries with glosses first
2. Create reversal entries for each gloss
3. Link reversal to vernacular entries
4. Generate reversal index for dictionary

---

#### Semantic Domains (SemanticDomainOperations)

**Linguistically Valid Examples:**
```python
# Use standard semantic domain taxonomy
# Typically DDP (Domain Driven Dictionary)

# Link sense to semantic domain
sense = project.Senses.Find("run")
domain = project.SemanticDomain.Find("7.2.1.1 Run")
project.Senses.AddSemanticDomain(sense, domain)

# Common domains:
# 1. Universe, creation
# 2. Person
# 3. Language and thought
# 4. Social behavior
# 5. Daily life
# 6. Work and occupation
# 7. Physical actions
# 8. States
# 9. Grammar

# NOT: "domain1", "category", "type"
```

**Terminology:**
- **Semantic domain** = meaning category/topic
- **DDP** = Dictionary Development Process taxonomy
- **Hierarchical** = nested categories (7 > 7.2 > 7.2.1)

**Standard Taxonomy (DDP):**
```
1. Universe, creation
  1.1 Sky
  1.2 World
  1.3 Water
2. Person
  2.1 Body
  2.2 Body functions
  2.3 Sense, perceive
3. Language and thought
  3.1 Soul, spirit
  3.2 Think
  3.3 Language
...
```

**Workflow:**
1. Use existing semantic domain list (DDP)
2. Link senses to appropriate domains
3. Multiple domains per sense allowed
4. Generate thematic lexicon view

---

### 3.3 Texts & Words Domain

#### Texts (TextOperations)

**Linguistically Valid Examples:**
```python
# Create text with genre
text = project.Texts.Create(
    name="Genesis Creation Story",
    genre="narrative"
)

# Multiple text types
text1 = project.Texts.Create("Riddle Collection", "riddles")
text2 = project.Texts.Create("Farming Procedures", "procedural")
text3 = project.Texts.Create("Interview with Elder", "conversation")

# NOT: "Text 1", "Test Text", "Document"
```

**Terminology:**
- **Text** = documented linguistic corpus
- **Genre** = text type (narrative, procedural, song, etc.)
- **Discourse** = connected speech/text
- **Corpus** = collection of texts

**Common Text Genres:**
- **Narrative** = story-telling
- **Procedural** = how-to instructions
- **Conversation** = dialogue
- **Song** = musical text
- **Riddle** = traditional riddles
- **Proverb** = folk sayings

**Workflow:**
1. Create text with name and genre
2. Add paragraphs to text
3. Add segments to paragraphs
4. Analyze wordforms in segments
5. Link to media files

---

#### Paragraphs (ParagraphOperations)

**Linguistically Valid Examples:**
```python
# Add paragraph to text
text = project.Texts.Find("Genesis Creation Story")
para1 = project.Paragraphs.Create(
    text,
    content="In the beginning God created the heavens and the earth."
)
para2 = project.Paragraphs.Create(
    text,
    content="Now the earth was formless and empty."
)

# NOT: "Paragraph 1", "Test paragraph"
```

**Terminology:**
- **Paragraph** = discourse unit (larger than sentence)
- **Text structure** = hierarchical organization
- **Discourse marker** = paragraph-linking elements

**Workflow:**
1. Create text first
2. Add paragraphs in order
3. Paragraphs contain segments
4. Mark discourse structure

---

#### Segments (SegmentOperations)

**Linguistically Valid Examples:**
```python
# Add segments (phrases/sentences) to paragraph
para = project.Paragraphs.Find(para_id)

segment1 = project.Segments.Create(
    para,
    vernacular="Mù kɛ́ mbɔ̀k.",
    free_translation="I went home."
)

segment2 = project.Segments.Create(
    para,
    vernacular="Ɛ̀ wú ɛ́nù.",
    free_translation="He is eating."
)

# NOT: "Segment 1", "Test segment"
```

**Terminology:**
- **Segment** = sentence or phrase unit
- **Baseline** = vernacular text
- **Free translation** = natural translation
- **Back translation** = literal translation

**Workflow:**
1. Create paragraph first
2. Add segments (sentences/phrases)
3. Provide vernacular baseline
4. Provide free translation
5. Analyze wordforms in segment

---

#### Wordforms (WordformOperations)

**Linguistically Valid Examples:**
```python
# Wordforms are surface forms in text
wordform = project.Wordforms.Find("running")
wordform = project.Wordforms.Find("went")

# Wordforms may have multiple analyses
# (ambiguity resolution)

# NOT: "word1", "test", "form"
```

**Terminology:**
- **Wordform** = surface form occurring in text
- **Token** = specific occurrence
- **Type** = abstract form (one type, many tokens)
- **Analysis** = linguistic parsing of wordform

**Workflow:**
1. Wordforms extracted from segments automatically
2. Find wordform in inventory
3. Add analyses to wordform
4. Approve correct analysis

---

#### Wordform Analyses (WfiAnalysisOperations)

**Linguistically Valid Examples:**
```python
# Analyze "running" as run + ing
wordform = project.Wordforms.Find("running")
analysis = project.WfiAnalyses.Create(wordform)

# Add morph bundles (morpheme breakdown)
run_bundle = project.WfiMorphBundle.Create(
    analysis,
    morph=run_entry,      # lexicon entry
    sense=run_sense,      # specific sense
    gloss="run"
)
ing_bundle = project.WfiMorphBundle.Create(
    analysis,
    morph=ing_entry,
    sense=ing_sense,
    gloss="PROG"          # progressive aspect
)

# Set wordform-level gloss
project.WfiAnalyses.AddGloss(analysis, "running", "en")

# NOT: "analysis1", "parse1"
```

**Terminology:**
- **Analysis** = morphological parsing
- **Morph bundle** = individual morpheme in analysis
- **Gloss** = brief translation/label
- **MSA** = morphosyntactic annotation

**Glossing Conventions (Leipzig Glossing Rules):**
- **Lexical morphemes:** lowercase (run, house, dog)
- **Grammatical morphemes:** UPPERCASE (PROG, PST, PL)
- **Person/Number:** 1SG, 2PL, 3SG, etc.
- **Hyphens:** separate morphemes (run-PROG-PST)

**Workflow:**
1. Create wordform first (extracted from text)
2. Create analysis for wordform
3. Add morph bundles (morpheme breakdown)
4. Link bundles to lexicon entries and senses
5. Add wordform-level gloss
6. Approve analysis if correct

---

#### Wordform Glosses (WfiGlossOperations)

**Linguistically Valid Examples:**
```python
# Add glosses to analysis
gloss = project.WfiGloss.Create(
    analysis,
    gloss_text="running",
    writing_system="en"
)

# Multiple language glosses
gloss_en = project.WfiGloss.Create(analysis, "running", "en")
gloss_fr = project.WfiGloss.Create(analysis, "courir", "fr")

# NOT: "gloss1", "translation", "test"
```

**Terminology:**
- **Gloss** = translation of wordform
- **Writing system** = language of gloss
- **Analysis-level** = whole wordform meaning

**Workflow:**
1. Create analysis first
2. Add gloss in target language(s)
3. Gloss reflects overall wordform meaning

---

#### Morph Bundles (WfiMorphBundleOperations)

**Linguistically Valid Examples:**
```python
# Morpheme-by-morpheme breakdown
analysis = project.WfiAnalyses.Find(analysis_id)

# Root morpheme
bundle1 = project.WfiMorphBundle.Create(
    analysis,
    morph=run_entry,
    sense=run_sense,
    gloss="run",
    msa=verb_stem_msa
)

# Affix morpheme
bundle2 = project.WfiMorphBundle.Create(
    analysis,
    morph=ing_entry,
    sense=ing_sense,
    gloss="PROG",
    msa=progressive_affix_msa
)

# NOT: "bundle1", "morph1", "part"
```

**Terminology:**
- **Morph bundle** = single morpheme in analysis
- **Morph** = links to lexicon entry
- **Sense** = specific meaning
- **MSA** = morphosyntactic annotation
- **Gloss** = morpheme-level translation/label

**Workflow:**
1. Create analysis first
2. Add morph bundle for each morpheme
3. Link to lexicon entry
4. Link to specific sense
5. Provide gloss
6. Specify MSA (grammatical info)

---

#### Media Files (MediaOperations)

**Linguistically Valid Examples:**
```python
# Link audio to text
media = project.Media.Create(
    file_path="path/to/genesis_story.wav",
    media_type="audio",
    description="Recording with Elder John, 2024-05-15"
)
project.Texts.LinkMedia(text, media)

# Link audio to segment
media = project.Media.Create(
    file_path="path/to/sentence_03.wav",
    media_type="audio"
)
project.Segments.LinkMedia(segment, media)

# Video file
media = project.Media.Create(
    file_path="path/to/interview.mp4",
    media_type="video",
    description="Interview with consultant Mary, discussing kinship terms"
)

# NOT: "file1.wav", "test.mp3", "media1"
```

**Terminology:**
- **Media file** = audio/video recording
- **Time-aligned** = linked to specific text position
- **Consultant** = native speaker providing data

**File Types:**
- **Audio:** .wav, .mp3, .flac
- **Video:** .mp4, .avi, .mov

**Workflow:**
1. Record linguistic data
2. Create media entry
3. Link to text, paragraph, or segment
4. Optionally time-align

---

#### Discourse Charts (DiscourseOperations)

**Linguistically Valid Examples:**
```python
# Create discourse chart for text
chart = project.Discourse.Create(
    text,
    chart_type="constituent_structure"
)

# Add discourse nodes
node1 = project.Discourse.AddNode(chart, "Introduction")
node2 = project.Discourse.AddNode(chart, "Body")
node3 = project.Discourse.AddNode(chart, "Conclusion")

# NOT: "chart1", "structure", "test"
```

**Terminology:**
- **Discourse chart** = structural analysis of text
- **Constituent structure** = hierarchical organization
- **Discourse markers** = linking elements

**Chart Types:**
- **Constituent structure** = hierarchical tree
- **Theme/Participant** = tracking across text

**Workflow:**
1. Create text first
2. Analyze discourse structure
3. Create chart
4. Add nodes and relationships

---

#### Filters (FilterOperations)

**Linguistically Valid Examples:**
```python
# Create text filter
filter = project.Filter.Create(
    name="Narrative Texts Only",
    filter_type="text",
    criteria={"genre": "narrative"}
)

# Filter wordforms by POS
filter = project.Filter.Create(
    name="Verbs Only",
    filter_type="wordform",
    criteria={"pos": "Verb"}
)

# NOT: "filter1", "test_filter"
```

**Terminology:**
- **Filter** = data subset specification
- **Criteria** = selection conditions

**Workflow:**
1. Define criteria
2. Create filter
3. Apply to views

---

### 3.4 Notebook Domain

#### Data Notebook (DataNotebookOperations)

**Linguistically Valid Examples:**
```python
# Field notes entry
notebook = project.DataNotebook.Create(
    title="Elicitation Session 2024-05-15",
    content="Discussed kinship terms with Mary. Discovered new term for 'cousin'.",
    date="2024-05-15",
    researcher="Jane Smith"
)

# NOT: "Note 1", "Test entry", "Notebook 1"
```

**Terminology:**
- **Field notes** = researcher observations
- **Elicitation** = structured data gathering
- **Consultant** = native speaker providing data

**Workflow:**
1. Create notebook entry
2. Link to relevant data (entries, texts, etc.)
3. Date and attribute to researcher

---

#### Notes (NoteOperations)

**Linguistically Valid Examples:**
```python
# Annotation on lexical entry
note = project.Note.Create(
    entry,
    content="Check pronunciation with second consultant - possible dialectal variation",
    note_type="researcher comment"
)

# Annotation on sense
note = project.Note.Create(
    sense,
    content="This sense is archaic, only used by elders",
    note_type="usage note"
)

# NOT: "Note 1", "Comment", "Test note"
```

**Terminology:**
- **Annotation** = comment on data
- **Note type** = category of note
- **Researcher comment** = analytical observation

**Note Types:**
- **Researcher comment** = analytical notes
- **Usage note** = contextual information
- **Grammar note** = grammatical observations
- **Phonology note** = pronunciation details

**Workflow:**
1. Create data object first (entry, sense, text, etc.)
2. Add note with content and type
3. Attribute to researcher

---

#### People (PersonOperations)

**Linguistically Valid Examples:**
```python
# Add consultant
person = project.Person.Create(
    name="Mary Ndifon",
    role="consultant",
    birth_year=1955,
    village="Mamfe"
)

# Add researcher
person = project.Person.Create(
    name="Dr. Jane Smith",
    role="researcher",
    institution="University of California"
)

# NOT: "Person 1", "Consultant 1", "Test"
```

**Terminology:**
- **Consultant** = native speaker/language expert
- **Researcher** = linguist/analyst
- **Speaker** = language user
- **Elder** = senior community member

**Workflow:**
1. Create person records
2. Link to recorded data
3. Track contributions
4. Respect privacy/permissions

---

#### Locations (LocationOperations)

**Linguistically Valid Examples:**
```python
# Add village location
location = project.Location.Create(
    name="Mamfe",
    location_type="village",
    region="Southwest Region",
    country="Cameroon",
    coordinates="5.75°N, 9.27°E"
)

# Hierarchical locations
country = project.Location.Create("Cameroon", "country")
region = project.Location.Create("Southwest Region", "region", parent=country)
village = project.Location.Create("Mamfe", "village", parent=region)

# NOT: "Place 1", "Location", "Test"
```

**Terminology:**
- **Location** = geographic place
- **Hierarchy** = country > region > village
- **Dialect area** = linguistic region

**Workflow:**
1. Create location hierarchy
2. Link people to locations
3. Link texts to locations
4. Track dialectal variation

---

#### Anthropology (AnthropologyOperations)

**Linguistically Valid Examples:**
```python
# Cultural domain entry
anthro = project.Anthropology.Create(
    category="Kinship Systems",
    title="Matrilineal Descent",
    content="Kenyang follows matrilineal descent. Children belong to mother's clan.",
    researcher="Dr. Jane Smith"
)

# Cultural practice
anthro = project.Anthropology.Create(
    category="Traditional Ceremonies",
    title="Harvest Festival",
    content="Annual celebration in October marking end of farming season."
)

# NOT: "Entry 1", "Cultural thing", "Test"
```

**Terminology:**
- **Anthropological data** = cultural information
- **Ethnography** = cultural description
- **Cultural domain** = topic area

**Common Categories:**
- Kinship systems
- Social organization
- Traditional ceremonies
- Material culture
- Belief systems

**Workflow:**
1. Document cultural context
2. Link to relevant linguistic data
3. Cross-reference with semantic domains

---

### 3.5 Lists Domain

#### Possibility Lists (PossibilityListOperations)

**Linguistically Valid Examples:**
```python
# Custom grammatical category list
list = project.PossibilityList.Create(
    name="Evidentiality",
    description="Source of information markers"
)
project.PossibilityList.AddItem(list, "Direct evidence", "DIR")
project.PossibilityList.AddItem(list, "Reported evidence", "REP")
project.PossibilityList.AddItem(list, "Inferential", "INF")

# Text genre list
genres = project.PossibilityList.Create("Text Genres")
project.PossibilityList.AddItem(genres, "Narrative", "NAR")
project.PossibilityList.AddItem(genres, "Procedural", "PROC")
project.PossibilityList.AddItem(genres, "Conversation", "CONV")

# NOT: "List 1", "Custom list", "Test"
```

**Terminology:**
- **Possibility list** = custom taxonomy
- **Hierarchical** = parent-child structure
- **Closed list** = finite set of options

**Workflow:**
1. Create list with name/description
2. Add items hierarchically
3. Use in project data

---

#### Publications (PublicationOperations)

**Linguistically Valid Examples:**
```python
# Dictionary publication
pub = project.Publication.Create(
    name="Kenyang-English Dictionary",
    publication_type="dictionary",
    date="2025-01-01",
    author="Jane Smith",
    publisher="SIL International"
)

# Grammar publication
pub = project.Publication.Create(
    name="Sketch Grammar of Kenyang",
    publication_type="grammar",
    date="2024-06-01"
)

# NOT: "Publication 1", "Book", "Test"
```

**Terminology:**
- **Publication** = output product
- **Dictionary** = lexicon in published form
- **Grammar** = grammatical description

**Publication Types:**
- Dictionary
- Grammar
- Text collection
- Word list

**Workflow:**
1. Define publication parameters
2. Configure output settings
3. Export data to publication format

---

#### Translation Types (TranslationTypeOperations)

**Linguistically Valid Examples:**
```python
# Translation type taxonomy
free_trans = project.TranslationType.Create(
    name="Free Translation",
    abbr="FT",
    description="Natural, idiomatic translation"
)

literal_trans = project.TranslationType.Create(
    name="Literal Translation",
    abbr="LT",
    description="Word-for-word rendering"
)

back_trans = project.TranslationType.Create(
    name="Back Translation",
    abbr="BT",
    description="Translation of morpheme glosses"
)

# NOT: "Type 1", "Translation", "Test"
```

**Terminology:**
- **Free translation** = natural, idiomatic
- **Literal translation** = word-for-word
- **Back translation** = from morpheme glosses

**Workflow:**
1. Define translation types
2. Use in text translations
3. Mark translation type on segments

---

#### Confidence Levels (ConfidenceOperations)

**Linguistically Valid Examples:**
```python
# Data reliability scale
conf_high = project.Confidence.Create(
    name="Confirmed",
    level=3,
    description="Verified with multiple consultants"
)

conf_med = project.Confidence.Create(
    name="Tentative",
    level=2,
    description="Needs additional verification"
)

conf_low = project.Confidence.Create(
    name="Uncertain",
    level=1,
    description="Requires checking"
)

# NOT: "Level 1", "Confidence", "Test"
```

**Terminology:**
- **Confidence level** = data reliability rating
- **Verification** = checking with consultants

**Workflow:**
1. Define confidence scale
2. Assign to data items
3. Track data quality

---

#### Agents (AgentOperations)

**Linguistically Valid Examples:**
```python
# Parser agent
agent = project.Agent.Create(
    name="HermitCrab Parser",
    version="1.0",
    agent_type="parser"
)

# Human annotator
agent = project.Agent.Create(
    name="Jane Smith",
    agent_type="human"
)

# NOT: "Agent 1", "Person", "Test"
```

**Terminology:**
- **Agent** = entity performing analysis
- **Parser** = automatic analyzer
- **Human** = manual annotator

**Workflow:**
1. Define agents
2. Track analysis provenance
3. Distinguish automatic vs. manual

---

### 3.6 System Domain

#### Writing Systems (WritingSystemOperations)

**Linguistically Valid Examples:**
```python
# Vernacular orthography
ws = project.WritingSystem.Create(
    tag="ken",  # ISO 639-3 code
    name="Kenyang",
    region="CM",  # Cameroon
    script="Latn",  # Latin script
    writing_system_type="vernacular"
)

# IPA phonetic
ws = project.WritingSystem.Create(
    tag="ken-fonipa",  # IPA notation
    name="Kenyang (IPA)",
    script="Latn",
    writing_system_type="pronunciation"
)

# Analysis language
ws = project.WritingSystem.Create(
    tag="en",
    name="English",
    region="US",
    script="Latn",
    writing_system_type="analysis"
)

# NOT: "ws1", "Writing System", "Test"
```

**Terminology:**
- **Writing system** = orthography
- **Vernacular** = language being documented
- **Analysis** = language of glosses/descriptions
- **IPA** = phonetic notation system
- **ISO 639-3** = three-letter language code

**Writing System Types:**
- **Vernacular** = primary writing system for language
- **Analysis** = gloss/description language
- **Pronunciation** = phonetic notation (IPA)

**Workflow:**
1. Define vernacular writing system first
2. Add analysis writing system (English, etc.)
3. Optionally add pronunciation (IPA)
4. Configure character sets and keyboards

---

#### Custom Fields (CustomFieldOperations)

**Linguistically Valid Examples:**
```python
# Field for dialectal information
field = project.CustomField.Create(
    name="Dialect",
    location="lexicon_entry",
    field_type="string",
    writing_system="en"
)

# Field for elicitation context
field = project.CustomField.Create(
    name="Elicitation Context",
    location="lexicon_sense",
    field_type="multistring",
    help_string="Note how this sense was elicited"
)

# Field for cultural notes
field = project.CustomField.Create(
    name="Cultural Note",
    location="lexicon_sense",
    field_type="formatted_text"
)

# NOT: "Field1", "Custom", "Test"
```

**Terminology:**
- **Custom field** = user-defined data field
- **Location** = where field appears (entry, sense, etc.)
- **Field type** = data type (string, list, etc.)

**Field Types:**
- **String** = single-line text
- **Multistring** = multi-language text
- **Integer** = number
- **GenDate** = date with flexibility (circa, before, etc.)
- **Formatted text** = styled text
- **Possibility list** = dropdown selection

**Common Custom Fields:**
- Dialect
- Register (formal/informal)
- Cultural notes
- Elicitation context
- Recording date
- Consultant

**Workflow:**
1. Define custom field with name, location, type
2. Use in data entry
3. Include in publications if needed

---

#### Project Settings (ProjectSettingsOperations)

**Linguistically Valid Examples:**
```python
# Configure project metadata
project.Settings.SetProjectName("Kenyang-M")
project.Settings.SetLanguageName("Kenyang")
project.Settings.SetISO639Code("ken")

# Configure default writing systems
project.Settings.SetDefaultVernacularWS("ken")
project.Settings.SetDefaultAnalysisWS("en")

# NOT: Generic settings, test values
```

**Terminology:**
- **Project settings** = configuration
- **Metadata** = project information
- **Default WS** = primary writing systems

**Workflow:**
1. Set project metadata
2. Configure writing systems
3. Set display preferences

---

#### Annotation Types (AnnotationDefOperations)

**Linguistically Valid Examples:**
```python
# Define annotation type
annot_type = project.AnnotationDef.Create(
    name="Phonetic Note",
    location="pronunciation",
    description="Detailed phonetic observations"
)

# Define text annotation
annot_type = project.AnnotationDef.Create(
    name="Discourse Marker",
    location="segment",
    description="Mark discourse-level function"
)

# NOT: "Type1", "Annotation", "Test"
```

**Terminology:**
- **Annotation type** = category of annotation
- **Location** = where annotation can be added

**Workflow:**
1. Define annotation types
2. Add annotations to data
3. Track analytical observations

---

#### Consistency Checks (CheckOperations)

**Linguistically Valid Examples:**
```python
# Define consistency check
check = project.Check.Create(
    name="Missing Glosses",
    check_type="lexicon",
    description="Find senses without glosses"
)

# Define phonology check
check = project.Check.Create(
    name="Invalid Phonemes",
    check_type="phonology",
    description="Detect characters not in phoneme inventory"
)

# NOT: "Check1", "Test", "Rule"
```

**Terminology:**
- **Consistency check** = data validation rule
- **Check type** = domain of checking

**Workflow:**
1. Define check rules
2. Run checks on data
3. Fix identified issues

---

## 4. Linguistic Terminology Reference

### 4.1 Morphology Terms

| Term | Definition | Example |
|------|------------|---------|
| **Morpheme** | Smallest meaningful unit | "un-" (not), "run" (move fast), "-ing" (progressive) |
| **Free morpheme** | Can stand alone | "cat", "run", "happy" |
| **Bound morpheme** | Must attach to another | "-ed", "-s", "un-" |
| **Root** | Core morpheme | "cur" in "current" |
| **Stem** | Base for affixation | "walk" in "walking" |
| **Affix** | Bound morpheme | "-ed", "pre-", "-tion" |
| **Prefix** | Before root | "un-" in "unhappy" |
| **Suffix** | After root | "-ness" in "happiness" |
| **Infix** | Inside root | "-um-" in Tagalog "s-um-ulat" |
| **Circumfix** | Around root | "ge-...-t" in German "ge-mach-t" |
| **Allomorph** | Variant of morpheme | "-s", "-z", "-ɪz" (plural) |
| **Portmanteau** | Fused morphemes | "don't" = do + not |
| **Clitic** | Syntactically independent, phonologically bound | "'s" in "John's" |

### 4.2 Phonology Terms

| Term | Definition | Example |
|------|------------|---------|
| **Phoneme** | Distinctive sound unit | /p/, /b/, /t/ |
| **Allophone** | Phonetic variant | [pʰ] vs. [p] in English |
| **IPA** | International Phonetic Alphabet | [ɹʌn] = "run" |
| **Feature** | Phonetic property | [+voice], [-nasal] |
| **Natural class** | Phonemes sharing features | Stops: /p, t, k, b, d, g/ |
| **Environment** | Phonological context | "_#" = word-final |
| **Assimilation** | Sound becomes like neighbor | "input" → [ɪmpʊt] |
| **Dissimilation** | Sound becomes unlike neighbor | Latin "peregrinus" → "pilgrim" |
| **Epenthesis** | Sound insertion | "hamster" → [hæmpstɚ] |
| **Deletion** | Sound removal | "handbag" → [hæmbæg] |
| **Metathesis** | Sound reordering | "ask" → "aks" |

### 4.3 Syntax/Grammar Terms

| Term | Definition | Example |
|------|------------|---------|
| **Part of Speech** | Grammatical category | Noun, Verb, Adjective |
| **Constituent** | Syntactic unit | Noun Phrase, Verb Phrase |
| **Phrase** | Multi-word syntactic unit | "the big dog" |
| **Clause** | Unit with subject + predicate | "when she arrived" |
| **Agreement** | Grammatical matching | Subject-verb agreement |
| **Government** | Syntactic dependency | Verb governs object case |
| **Head** | Central element | "dog" in "the big dog" |
| **Modifier** | Describes head | "big" in "the big dog" |
| **Complement** | Completes meaning | "home" in "go home" |
| **Adjunct** | Optional element | "yesterday" in "arrived yesterday" |

### 4.4 Lexicon Terms

| Term | Definition | Example |
|------|------------|---------|
| **Lexeme** | Abstract word unit | RUN (covers "run", "runs", "ran") |
| **Lexical entry** | Dictionary entry | Headword + senses |
| **Sense** | Individual meaning | "run"₁ (move), "run"₂ (operate) |
| **Gloss** | Brief translation | "to run" |
| **Definition** | Full meaning explanation | "To move rapidly on foot..." |
| **Citation form** | Dictionary headword | "be" for "am", "is", "are" |
| **Polysemy** | Multiple related senses | "head" (body part, leader, top) |
| **Homonymy** | Same form, different meanings | "bank" (river) vs. "bank" (financial) |
| **Synonym** | Similar meaning | "big" ≈ "large" |
| **Antonym** | Opposite meaning | "hot" ↔ "cold" |
| **Hypernym** | Superordinate | "animal" for "dog" |
| **Hyponym** | Subordinate | "dog" for "animal" |
| **Meronym** | Part | "wheel" for "car" |
| **Holonym** | Whole | "car" for "wheel" |

### 4.5 Text/Discourse Terms

| Term | Definition | Example |
|------|------------|---------|
| **Text** | Connected discourse | Story, conversation, etc. |
| **Discourse** | Language in context | Narrative, dialogue |
| **Genre** | Text type | Narrative, procedural, song |
| **Paragraph** | Discourse unit | Multi-sentence grouping |
| **Segment** | Phrase/sentence unit | "I went home." |
| **Baseline** | Original text | Vernacular text line |
| **IGT** | Interlinear Glossed Text | Line-by-line translation |
| **Free translation** | Natural translation | "I went home." |
| **Back translation** | Literal word-by-word | "I go-PST house" |
| **Wordform** | Surface word | "running", "went" |

---

## 5. Workflow Validation

### 5.1 Lexicon Workflow

**Standard workflow for creating lexical entries:**

```
1. Create Entry
   └─ Set lexeme form (headword)
   └─ Set morph type (stem/root/affix)
   └─ Optionally set citation form

2. Add Senses
   └─ Create sense with gloss
   └─ Set definition (fuller than gloss)
   └─ Assign part of speech
   └─ Link to semantic domains

3. Add Examples
   └─ Create example sentences
   └─ Provide vernacular baseline
   └─ Provide free translation

4. Add Linguistic Details
   └─ Add pronunciations (IPA + audio)
   └─ Add allomorphs (phonological variants)
   └─ Add variants (dialectal, spelling)
   └─ Add etymology

5. Add Lexical Relations
   └─ Link synonyms, antonyms
   └─ Link hypernyms/hyponyms
   └─ Link whole/part relations

6. Generate Outputs
   └─ Create reversal entries
   └─ Export to dictionary format
```

**Demo file should demonstrate steps 1-3 minimum.**

---

### 5.2 Grammar Workflow

**Standard workflow for phonology:**

```
1. Define Phoneme Inventory
   └─ List all consonants with features
   └─ List all vowels with features

2. Create Natural Classes
   └─ Group phonemes by shared features
   └─ E.g., stops, nasals, high vowels

3. Define Environments
   └─ Specify phonological contexts
   └─ E.g., word-initial, before high vowel

4. Create Phonological Rules
   └─ Specify input → output / environment
   └─ Order rules if needed
   └─ E.g., Nasal assimilation, vowel harmony

5. Test Rules
   └─ Apply to wordforms
   └─ Verify correct surface forms
```

**Demo file should show all steps.**

---

**Standard workflow for inflection:**

```
1. Define Grammatical Categories
   └─ Number, Person, Tense, etc.

2. Define Inflection Features
   └─ Singular, Plural, Dual
   └─ 1st, 2nd, 3rd person
   └─ Past, Present, Future

3. Link to Parts of Speech
   └─ Verbs: Tense, Aspect, Mood
   └─ Nouns: Number, Case, Gender

4. Create Inflectional Affixes
   └─ Add as lexical entries with affix type
   └─ Link to inflection features

5. Use in Analysis
   └─ Assign features to wordform analyses
   └─ Generate paradigm tables
```

**Demo file should demonstrate configuration.**

---

### 5.3 Texts Workflow

**Standard workflow for interlinear text:**

```
1. Create Text
   └─ Set name and genre
   └─ Optionally link media file

2. Add Paragraphs
   └─ Organize text into discourse units

3. Add Segments (Sentences/Phrases)
   └─ Enter vernacular baseline
   └─ Enter free translation

4. Parse Wordforms
   └─ Extract wordforms from segments
   └─ Or add manually

5. Analyze Wordforms
   └─ Create analysis
   └─ Add morph bundles
   └─ Link to lexicon entries
   └─ Link to senses
   └─ Add morpheme-level glosses

6. Approve Analysis
   └─ Review analyses
   └─ Approve correct one

7. Concordance & Export
   └─ Generate concordances
   └─ Export formatted text
```

**Demo file should show steps 1-5.**

---

### 5.4 Notebook Workflow

**Standard workflow for field notes:**

```
1. Create Notebook Entry
   └─ Date and title
   └─ Content/observations

2. Link to Data
   └─ Link to relevant entries, texts, etc.

3. Add People
   └─ Consultant records
   └─ Researcher attribution

4. Add Locations
   └─ Village/region information

5. Add Cultural Data
   └─ Anthropological observations
   └─ Cross-reference with lexicon
```

**Demo file should show metadata capture.**

---

### 5.5 System Workflow

**Standard workflow for project setup:**

```
1. Create/Open Project

2. Configure Writing Systems
   └─ Vernacular (language being documented)
   └─ Analysis (glossing language, usually English)
   └─ Pronunciation (IPA)

3. Define Custom Fields (if needed)
   └─ Additional data categories

4. Import Initial Data (if any)
   └─ Word lists
   └─ Existing texts

5. Define Grammatical Framework
   └─ POS hierarchy
   └─ Grammatical categories
   └─ Inflection features

6. Begin Data Entry
   └─ Lexicon, texts, etc.
```

**Demo file should show configuration steps.**

---

## 6. Quality Checklist

Use this checklist to validate demo files:

### 6.1 Linguistic Authenticity

- [ ] **Test data uses real linguistic terminology** (not "foo", "bar", "test")
- [ ] **Object relationships are linguistically valid** (e.g., sense belongs to entry)
- [ ] **Workflows match real FLEx usage patterns** (entry → sense → example)
- [ ] **Examples are meaningful** (not random text)
- [ ] **Glosses follow linguistic conventions** (lowercase lexical, UPPERCASE grammatical)
- [ ] **Phonetic representations use proper IPA** ([ɹʌn], not [run])
- [ ] **Semantic domains match standard taxonomies** (DDP if possible)
- [ ] **Text interlinearization follows IGT standards** (baseline, gloss, translation)
- [ ] **Morpheme analysis is coherent** (morphemes link to real entries)
- [ ] **Grammar structures are well-formed** (valid POS, features, rules)

### 6.2 FLEx Data Model

- [ ] **Entry has lexeme form** (required)
- [ ] **Entry has morph type** (stem, root, affix, etc.)
- [ ] **Sense has gloss** (brief translation)
- [ ] **Sense has part of speech** (from POS list)
- [ ] **Example has vernacular and translation**
- [ ] **Analysis links to lexicon entries**
- [ ] **Morph bundles link to senses**
- [ ] **Text has genre**
- [ ] **Segments have baseline and translation**
- [ ] **Writing systems properly configured**

### 6.3 Terminology Accuracy

- [ ] **Morph types correctly named** (stem, root, prefix, suffix, etc.)
- [ ] **POS labels standard** (Noun, Verb, Adjective, etc.)
- [ ] **Phoneme features accurate** (voiced, bilabial, stop, etc.)
- [ ] **Grammatical categories correct** (Number, Person, Tense, etc.)
- [ ] **Gloss conventions followed** (lowercase vs. UPPERCASE)
- [ ] **IPA notation proper** (brackets, Unicode characters)
- [ ] **Semantic domain labels standard** (DDP codes if available)
- [ ] **Text genres appropriate** (narrative, procedural, etc.)

### 6.4 Workflow Validity

- [ ] **Dependencies respected** (entry before sense before example)
- [ ] **Creation order logical** (phonemes before rules)
- [ ] **References valid** (linked objects exist)
- [ ] **Operations use correct methods** (from Operations classes)
- [ ] **Error handling appropriate** (try/except where needed)
- [ ] **Cleanup performed** (test data removed after demo)

### 6.5 Code Quality

- [ ] **Operations methods used correctly**
- [ ] **Parameters linguistically meaningful**
- [ ] **Comments explain linguistic context**
- [ ] **Variable names descriptive**
- [ ] **Demo documents workflow**
- [ ] **Output clear and informative**

---

## 7. Common Pitfalls to Avoid

### 7.1 Test Data Anti-Patterns

**❌ AVOID:**
```python
entry = project.LexEntry.Create("foo", "stem")
sense = project.Senses.Create(entry, "bar")
example = project.Examples.Create(sense, "This is a test.", "This is a test.")
```

**✅ INSTEAD:**
```python
entry = project.LexEntry.Create("run", "stem")
sense = project.Senses.Create(entry, "to move rapidly on foot")
example = project.Examples.Create(sense, "The dog runs in the park.", "The dog runs in the park.")
```

---

### 7.2 Terminology Errors

**❌ AVOID:**
```python
pos = project.POS.Create("Word Type 1", "WT1")  # Generic
phoneme = project.Phonemes.Create("x", ["feature1", "feature2"])  # Non-linguistic
```

**✅ INSTEAD:**
```python
pos = project.POS.Create("Verb", "V")  # Standard term
phoneme = project.Phonemes.Create("p", ["voiceless", "bilabial", "stop"])  # Real features
```

---

### 7.3 Glossing Errors

**❌ AVOID:**
```python
# Wrong case conventions
bundle1_gloss = "RUN"  # Should be lowercase (lexical)
bundle2_gloss = "prog" # Should be uppercase (grammatical)
```

**✅ INSTEAD:**
```python
# Leipzig Glossing Rules
bundle1_gloss = "run"    # Lowercase for lexical morphemes
bundle2_gloss = "PROG"   # Uppercase for grammatical morphemes
```

---

### 7.4 IPA Notation Errors

**❌ AVOID:**
```python
pronunciation = project.Pronunciation.Create(entry, "[run]")  # ASCII
pronunciation = project.Pronunciation.Create(entry, "/ran/")  # Wrong brackets
```

**✅ INSTEAD:**
```python
pronunciation = project.Pronunciation.Create(entry, "[ɹʌn]")  # Proper IPA with brackets
pronunciation = project.Pronunciation.Create(entry, "/rʌn/")  # Phonemic with slashes
```

---

### 7.5 Workflow Errors

**❌ AVOID:**
```python
# Creating example before sense
example = project.Examples.Create(None, "Text", "Translation")  # Sense is None!

# Creating analysis before wordform
analysis = project.WfiAnalyses.Create(None)  # Wordform is None!
```

**✅ INSTEAD:**
```python
# Correct order: entry → sense → example
entry = project.LexEntry.Create("run", "stem")
sense = project.Senses.Create(entry, "to move rapidly")
example = project.Examples.Create(sense, "She runs daily.", "She runs daily.")

# Correct order: text → segment → wordform → analysis
text = project.Texts.Create("Story")
para = project.Paragraphs.Create(text, "Content")
segment = project.Segments.Create(para, "She runs.", "She runs.")
wordform = project.Wordforms.Find("runs")
analysis = project.WfiAnalyses.Create(wordform)
```

---

### 7.6 Relationship Errors

**❌ AVOID:**
```python
# Linking objects that don't exist yet
project.Senses.SetPOS(sense, pos)  # pos hasn't been created!

# Linking incompatible objects
project.Senses.AddSemanticDomain(entry, domain)  # Should be sense, not entry!
```

**✅ INSTEAD:**
```python
# Create objects in dependency order
pos = project.POS.Create("Verb", "V")
entry = project.LexEntry.Create("run", "stem")
sense = project.Senses.Create(entry, "to move rapidly")
project.Senses.SetPOS(sense, pos)  # Now pos exists

# Link correct object types
project.Senses.AddSemanticDomain(sense, domain)  # Correct: sense, not entry
```

---

## 8. Domain-Specific Guidance

### 8.1 Grammar Domain Guidance

**POSOperations:**
- Use standard POS labels (Noun, Verb, Adjective, Adverb, etc.)
- Create hierarchies (Verb → Transitive Verb, Intransitive Verb)
- Abbreviations should be conventional (N, V, Adj)

**PhonemeOperations:**
- Use IPA symbols correctly
- Define proper phonetic features (place, manner, voicing)
- Group consonants and vowels separately

**NaturalClassOperations:**
- Natural classes must have phonological motivation
- Name by shared feature (e.g., "Stops", "Nasals", "High Vowels")

**EnvironmentOperations:**
- Use standard notation: # for boundary, _ for target position
- Name descriptively (e.g., "word-initial", "before high vowel")

**PhonologicalRuleOperations:**
- Format: input → output / environment
- Name reflects process (e.g., "Nasal Place Assimilation")
- Rules should be linguistically plausible

**InflectionFeatureOperations:**
- Use standard categories (Number, Person, Tense, Aspect, etc.)
- Features grouped by category
- Abbreviations follow glossing conventions (SG, PL, 1, 2, 3, PST, PRS)

**GramCatOperations:**
- Categories are classes of features (Number contains Singular, Plural)
- Link to appropriate POS
- Standard linguistic terminology

---

### 8.2 Lexicon Domain Guidance

**LexEntryOperations:**
- Lexeme forms should be meaningful words/morphemes
- Morph types accurate (stem, root, prefix, suffix, etc.)
- Citation forms set when different from lexeme form

**LexSenseOperations:**
- Glosses brief (1-5 words)
- Definitions fuller explanations
- Each sense has POS
- Link to semantic domains

**ExampleOperations:**
- Complete, grammatical sentences
- Vernacular + translation both provided
- Examples illustrate specific sense usage

**PronunciationOperations:**
- Use proper IPA notation
- Include audio files when available
- Mark dialectal variants

**VariantOperations:**
- Specify variant type (dialectal, free, inflectional)
- Link to main entry
- Document dialectal/register differences

**AllomorphOperations:**
- Phonologically motivated variants
- Specify conditioning environments
- Link to appropriate morph type

**EtymologyOperations:**
- Document source language and form
- Specify etymology type (borrowing, compound, cognate)
- Scholarly comments when available

**LexReferenceOperations:**
- Use standard relation types (synonym, antonym, etc.)
- Both entries must exist
- Directionality matters for asymmetric relations

**ReversalOperations:**
- Target language → vernacular mapping
- Useful for bilingual dictionaries
- Link all relevant vernacular entries

**SemanticDomainOperations:**
- Use standard taxonomy (DDP preferred)
- Hierarchical structure
- Multiple domains per sense allowed

---

### 8.3 Texts & Words Domain Guidance

**TextOperations:**
- Name texts descriptively
- Assign genre
- Link media files when available

**ParagraphOperations:**
- Paragraph boundaries mark discourse units
- Maintain order

**SegmentOperations:**
- Segments are sentences/phrases
- Baseline (vernacular) + free translation required
- IGT standards apply

**WordformOperations:**
- Wordforms extracted from segments
- Represent surface forms

**WfiAnalysisOperations:**
- Morphological parsing of wordforms
- Link to lexicon entries
- Multiple analyses allowed (ambiguity)

**WfiGlossOperations:**
- Wordform-level translation
- Multiple languages allowed

**WfiMorphBundleOperations:**
- Morpheme-by-morpheme breakdown
- Link to lexicon entry and sense
- Follow glossing conventions (lowercase lexical, UPPERCASE grammatical)

**MediaOperations:**
- Link audio/video to texts, segments
- Time-alignment when possible
- Document consultant and date

**DiscourseOperations:**
- Structural analysis of texts
- Constituent structure or thematic analysis

**FilterOperations:**
- Define useful data subsets
- Clear criteria

---

### 8.4 Notebook Domain Guidance

**DataNotebookOperations:**
- Field notes with dates
- Link to relevant data
- Attribute to researcher

**NoteOperations:**
- Annotations on data objects
- Specify note type
- Analytical observations

**PersonOperations:**
- Consultants and researchers
- Full names, roles
- Privacy considerations

**LocationOperations:**
- Hierarchical (country > region > village)
- Geographic coordinates when available
- Link to dialectal variation

**AnthropologyOperations:**
- Cultural context
- Standard anthropological categories
- Cross-reference with semantic domains

---

### 8.5 Lists Domain Guidance

**PossibilityListOperations:**
- Custom taxonomies
- Hierarchical structure
- Descriptive names

**PublicationOperations:**
- Dictionary, grammar, text collection
- Metadata (author, date, publisher)
- Configuration for output

**TranslationTypeOperations:**
- Free, literal, back translation
- Standard abbreviations (FT, LT, BT)

**ConfidenceOperations:**
- Data reliability scale
- Document verification level

**AgentOperations:**
- Track analysis provenance
- Distinguish automatic vs. manual

---

### 8.6 System Domain Guidance

**WritingSystemOperations:**
- Use ISO 639-3 language codes
- Define vernacular, analysis, pronunciation
- Configure character sets

**CustomFieldOperations:**
- User-defined data fields
- Specify location (entry, sense, etc.)
- Choose appropriate field type

**ProjectSettingsOperations:**
- Project metadata
- Default writing systems
- Display preferences

**AnnotationDefOperations:**
- Define annotation types
- Specify where annotations can be added

**CheckOperations:**
- Data validation rules
- Run on specific domains
- Identify data quality issues

---

## Conclusion

This guide provides the linguistic foundation for creating authentic, meaningful demo files for flexlibs v2.0.0 Operations classes. By following these guidelines, programmer agents will create demos that:

- **Model best practices** for linguistic analysis
- **Use authentic terminology** and examples
- **Follow real FLEx workflows**
- **Represent valid data structures**
- **Serve as learning resources** for future developers

**Key Principles:**

1. **Authenticity:** Use real linguistic data and terminology
2. **Validity:** Ensure object relationships match FLEx data model
3. **Workflow:** Follow logical operation sequences
4. **Conventions:** Adhere to linguistic and FLEx standards
5. **Meaningfulness:** Create examples linguists would actually use

**Next Steps:**

1. Programmer agents read this guide
2. Apply guidelines when creating demo files
3. Cross-reference with Operations class documentation
4. Test demos against Kenyang-M project
5. Verify linguistic accuracy before submission

---

**Document Status:** ✅ AUTHORITATIVE REFERENCE
**Version:** 1.0
**Last Updated:** 2025-11-25
**Maintained By:** Master Linguist (Domain Expert Agent)
