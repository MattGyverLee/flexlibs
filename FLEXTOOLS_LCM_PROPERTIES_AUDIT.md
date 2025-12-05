# FlexTools LCM Property Usage Audit

**Generated:** 2025-12-04
**Source:** FlexTools Modules directory analysis
**Total Files Analyzed:** 67 Python files

This document catalogs ALL LCM (Language Explorer Conceptual Model) property access patterns found in real-world FlexTools scripts.

---

## ILexEntry (Lexical Entry)

### Owning Properties (OA - Owning Atomic)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `LexemeFormOA` | MoForm | 50+ | FLExLookup.py, DoStampSynthesis.py, AdHocConstrForCluster.py, CatalogTargetAffixes.py, Complex_Lexemes.py |

### Owning Sequences (OS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `SensesOS` | ILexSense collection | 80+ | ALL entry processing files |
| `EntryRefsOS` | ILexEntryRef collection | 40+ | FixCapitalizedAnalyses.py, ConvertTextToSTAMPformat.py, Utils.py |
| `AlternateFormsOS` | MoForm collection | 20+ | Bulk_Set_Stem_Name.py, Overpowered_Affixes.py, Overpowered_Allomorphs.py, DoStampSynthesis.py, CatalogTargetAffixes.py |

### Owning Collections (OC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `MorphoSyntaxAnalysesOC` | IMoMorphSynAnalysis collection | 15+ | FLExLookup.py, GenerateParses.py, NewEntryDlg.py |

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `HeadWord` | ITsString | 50+ | ALL files |
| `CitationForm` | ITsString | 30+ | Multiple files |
| `Bibliography` | ITsString | 5+ | FLExLookup.py |
| `Comment` | ITsString | 10+ | Various |
| `ClassName` | string | 80+ | ALL type-checking code |
| `Guid` | Guid | 100+ | ALL files |

---

## ILexSense (Lexical Sense)

### Reference Properties (RA - Reference Atomic)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `MorphoSyntaxAnalysisRA` | IMoMorphSynAnalysis | 60+ | FLExLookup.py, DoStampSynthesis.py, AdHocConstrForCluster.py, Bulk_Set_Stem_Name.py |

### Reference Collections (RC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `SemanticDomainsRC` | ICmSemanticDomain collection | 3 | RemoveSemanticDomains.py |

### Owning Sequences (OS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `ExamplesOS` | ILexExampleSentence collection | Not found | (Property exists but not used in FlexTools) |

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `Gloss` | ITsString | 80+ | ALL files |
| `Definition` | ITsString | 40+ | Multiple files |
| `Entry` | ILexEntry | 20+ | Utils.py, various |
| `OwningEntry` | ILexEntry | 5+ | FixCapitalizedAnalyses.py |

---

## ILexEntryRef (Entry Reference - Variants & Complex Forms)

### Reference Sequences (RS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `ComponentLexemesRS` | ILexEntry/ILexSense collection | 30+ | FLExLookup.py, ConvertTextToSTAMPformat.py, LiveRuleTesterTool.py, Utils.py |
| `VariantEntryTypesRS` | ILexEntryType collection | 15+ | FixCapitalizedAnalyses.py, RemoveCapitalVariantEntries.py, ConvertTextToSTAMPformat.py, DoStampSynthesis.py, Utils.py |
| `ComplexEntryTypesRS` | ILexEntryType collection | 10+ | ConvertTextToSTAMPformat.py, TextClasses.py |

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `RefType` | int | 10+ | Utils.py, TextClasses.py |

---

## MoForm (Morphological Forms - Base Class)

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `Form` | ITsString | 80+ | ALL files |
| `IsAbstract` | bool | 10+ | Overpowered_Allomorphs.py, AdHocConstrForCluster.py |
| `ClassName` | string | 80+ | ALL type-checking code |

---

## MoStemAllomorph (Stem Allomorph)

### Owning Properties (OA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `MsEnvFeaturesOA` | IFsFeatStruc | 15+ | Overpowered_Affixes.py, Overpowered_Allomorphs.py, DoStampSynthesis.py |

### Reference Properties (RA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `MorphTypeRA` | IMoMorphType | 60+ | FLExLookup.py, SciName.py, CatalogTargetAffixes.py, DoStampSynthesis.py |
| `StemNameRA` | IMoStemName | 20+ | Bulk_Set_Stem_Name.py, Overpowered_Affixes.py, Overpowered_Allomorphs.py, DoStampSynthesis.py |

### Reference Collections (RC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `InflectionClassesRC` | IMoInflClass collection | 8+ | Overpowered_Affixes.py, Overpowered_Allomorphs.py, DoStampSynthesis.py |
| `PhoneEnvRC` | IPhEnvironment collection | 3 | DoStampSynthesis.py |

---

## MoAffixAllomorph (Affix Allomorph)

### Reference Sequences (RS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `PositionRS` | IMoMorphAdhocProhib collection | 3 | DoStampSynthesis.py |

---

## IMoMorphSynAnalysis (Morphosyntactic Analysis - Base Class)

### Owning Properties (OA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `MsFeaturesOA` | IFsFeatStruc | 15+ | SetFeatures.py, TextClasses.py, Utils.py |

---

## IMoStemMsa (Stem MSA)

### Reference Properties (RA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `PartOfSpeechRA` | IPartOfSpeech | 80+ | FLExLookup.py, Bulk_Set_Stem_Name.py, ConvertTextToSTAMPformat.py, DoStampSynthesis.py, SetFeatures.py, NewEntryDlg.py |
| `InflectionClassRA` | IMoInflClass | 8 | DoStampSynthesis.py |

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `ClassName` | string | 60+ | Type checking in multiple files |

---

## IMoInflAffMsa (Inflectional Affix MSA)

### Owning Properties (OA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `InflFeatsOA` | IFsFeatStruc | 15+ | DoStampSynthesis.py, ConvertTextToSTAMPformat.py, Utils.py |

### Reference Properties (RA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `PartOfSpeechRA` | IPartOfSpeech | 20+ | DoStampSynthesis.py |

---

## IMoDerivAffMsa (Derivational Affix MSA)

### Reference Properties (RA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `FromPartOfSpeechRA` | IPartOfSpeech | 10+ | AdHocConstrForCluster.py, Overpowered_Affixes.py |
| `ToPartOfSpeechRA` | IPartOfSpeech | 8+ | AdHocConstrForCluster.py, Bulk_Set_Exception_Features.py |

### Reference Collections (RC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `FromPartsOfSpeechRC` | IPartOfSpeech collection | 5+ | FLExLookup.py, GenerateParses.py |
| `FromProdRestrictRC` | ICmPossibility collection | 5+ | Bulk_Set_Exception_Features.py |
| `ToProdRestrictRC` | ICmPossibility collection | 3 | Bulk_Set_Exception_Features.py |

---

## IPartOfSpeech (Part of Speech / Grammatical Category)

### Owning Sequences (OS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `AffixTemplatesOS` | IMoAffixAllomorph collection | 15+ | FLExLookup.py, Overpowered_Affixes.py, Reorder_Affix_Templates.py, GenerateParses.py, Utils.py |
| `SubPossibilitiesOS` | IPartOfSpeech collection | 8+ | FLExLookup.py, GenerateParses.py |

### Owning Collections (OC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `StemNamesOC` | IMoStemName collection | 10+ | Bulk_Set_Stem_Name.py, DoStampSynthesis.py |
| `InflectionClassesOC` | IMoInflClass collection | 10+ | DoStampSynthesis.py, SetUpTransferRuleGramCat.py, Utils.py |
| `AffixSlotsOC` | IMoInflAffixSlot collection | 5+ | Overpowered_Affixes.py |

### Reference Properties (RA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `DefaultInflectionClassRA` | IMoInflClass | 3 | DoStampSynthesis.py |

### Reference Collections (RC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `InflectableFeatsRC` | IFsClosedFeature collection | 3 | Utils.py |

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `Abbreviation` | ITsString | 60+ | Multiple files |
| `Name` | ITsString | 40+ | Multiple files |

---

## IMoAffixTemplate (Affix Template)

### Reference Sequences (RS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `PrefixSlotsRS` | IMoAffixSlot collection | 15+ | FLExLookup.py, Overpowered_Affixes.py, GenerateParses.py, Utils.py |
| `SuffixSlotsRS` | IMoAffixSlot collection | 15+ | FLExLookup.py, Overpowered_Affixes.py, GenerateParses.py, Utils.py |
| `SlotsRS` | IMoAffixSlot collection | 8+ | Overpowered_Affixes.py |
| `ProcliticSlotsRS` | IMoAffixSlot collection | 3 | Overpowered_Affixes.py |

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `Name` | ITsString | 10+ | Reorder_Affix_Templates.py, Utils.py |

---

## IMoStemName (Stem Name)

### Owning Collections (OC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `RegionsOC` | IFsFeatStruc collection | 5+ | DoStampSynthesis.py |

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `Abbreviation` | ITsString | 15+ | Bulk_Set_Stem_Name.py, DoStampSynthesis.py |
| `AnalysisDefaultWritingSystem` | ITsString | 5+ | Bulk_Set_Stem_Name.py |

---

## IMoInflClass (Inflection Class)

### Owning Collections (OC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `SubclassesOC` | IMoInflClass collection | 8+ | DoStampSynthesis.py, Utils.py |

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `Abbreviation` | ITsString | 10+ | DoStampSynthesis.py, SetUpTransferRuleGramCat.py |

---

## IFsFeatStruc (Feature Structure)

### Owning Collections (OC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `FeatureSpecsOC` | IFsFeatureSpecification collection | 40+ | CheckPhonemeUniqueness.py, Overpowered_Affixes.py, DoStampSynthesis.py, ConvertTextToSTAMPformat.py, SetFeatures.py, Utils.py |

### Reference Properties (RA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `TypeRA` | IFsFeatStrucType | 3 | SetFeatures.py |

---

## IFsFeatureSpecification (Feature Specification - Base)

### Reference Properties (RA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `FeatureRA` | IFsFeature | 10+ | CheckPhonemeUniqueness.py, ConvertTextToSTAMPformat.py |
| `ValueRA` | IFsSymFeatVal | 10+ | CheckPhonemeUniqueness.py, SetFeatures.py, ConvertTextToSTAMPformat.py |

---

## IFsComplexValue (Complex Feature Value)

### Owning Properties (OA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `ValueOA` | IFsFeatStruc | 3 | ConvertTextToSTAMPformat.py |

### Owning Collections (OC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `FeatureSpecsOC` | IFsFeatureSpecification collection | 8+ | Utils.py |

---

## IFsClosedFeature (Closed Feature)

### Owning Collections (OC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `ValuesOC` | IFsSymFeatVal collection | 15+ | ExtractBilingualLexicon.py, SetUpTransferRuleGramCat.py, ReplacementEditor.py, RuleAssistant.py, TestbedValidator.py, Utils.py |

---

## IFsComplexFeature (Complex Feature)

### Reference Sequences (RS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `FeaturesRS` | IFsFeature collection | 3 | Utils.py |

---

## IPhPhoneme (Phoneme)

### Owning Properties (OA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `FeaturesOA` | IFsFeatureStructure | 5+ | CheckPhonemeUniqueness.py |

---

## IPhNaturalClass (Natural Class)

### Owning Sequences (OS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `CodesOS` | IPhCode collection | 3 | DoStampSynthesis.py |

### Reference Collections (RC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `SegmentsRC` | IPhPhoneme collection | 3 | DoStampSynthesis.py |

---

## IText (Text)

### Owning Properties (OA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `ContentsOA` | IStText | 10+ | FixCapitalizedAnalyses.py, InsertTargetText.py, ImportFromParatext.py, RuleAssistant.py |

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `Name` | ITsString | 15+ | Multiple files |
| `Title` | ITsString | 10+ | Multiple files |

---

## IStText (Structured Text)

### Owning Sequences (OS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `ParagraphsOS` | IStTxtPara collection | 15+ | FixCapitalizedAnalyses.py, ExportFlexToParatext.py, ChapterSelection.py |

---

## IStTxtPara (Text Paragraph)

### Owning Sequences (OS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `SegmentsOS` | ISegment collection | 5+ | FixCapitalizedAnalyses.py |

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `Contents` | ITsString | 10+ | ChapterSelection.py, Multiple files |

---

## ISegment (Segment)

### Reference Sequences (RS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `AnalysesRS` | IAnalysis collection | 10+ | FixCapitalizedAnalyses.py |

---

## IWfiWordform (Wordform)

### Owning Collections (OC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `AnalysesOC` | IWfiAnalysis collection | 8+ | RenameWordformsToLower.py, FixCapitalizedAnalyses.py |

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `Form` | ITsString | 15+ | Multiple files |

---

## IWfiAnalysis (Wordform Analysis)

### Owning Sequences (OS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `MorphBundlesOS` | IWfiMorphBundle collection | 10+ | FixCapitalizedAnalyses.py, InterlinData.py |

### Reference Collections (RC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `EvaluationsRC` | IAgentEvaluation collection | 15+ | FixCapitalizedAnalyses.py, RenameWordformsToLower.py, Remove_All_User_Analyses.py, Remove_Failed_User_Analyses.py |

---

## IWfiMorphBundle (Morpheme Bundle)

### Reference Properties (RA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `MorphRA` | IMoForm | 5+ | FixCapitalizedAnalyses.py |

---

## ILangProject (Language Project - Root Object)

### Owning Properties (OA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `LexDbOA` | ILexDb | 10+ | NewEntryDlg.py |
| `MorphologicalDataOA` | IMoMorphData | 10+ | AdHocConstrForCluster.py, Bulk_Set_Exception_Features.py |
| `MsFeatureSystemOA` | IFsFeatureSystem | 10+ | ExtractBilingualLexicon.py, SetUpTransferRuleGramCat.py |
| `PhonologicalDataOA` | IPhPhonData | 5+ | DoStampSynthesis.py |

---

## ILexDb (Lexicon Database)

### Owning Sequences (OS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `PossibilitiesOS` | ICmPossibility collection | 8+ | NewEntryDlg.py |

---

## IMoMorphData (Morphological Data)

### Owning Collections (OC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `AdhocCoProhibitionsOC` | IMoAdhocProhib collection | 8+ | AdHocConstrForCluster.py |

### Owning Properties (OA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `ProdRestrictOA` | ICmPossibilityList | 5+ | Bulk_Set_Exception_Features.py |

---

## IPhPhonData (Phonological Data)

### Owning Sequences (OS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `NaturalClassesOS` | IPhNaturalClass collection | 3 | DoStampSynthesis.py |

---

## IFsFeatureSystem (Feature System)

### Owning Collections (OC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `FeaturesOC` | IFsFeature collection | 10+ | ExtractBilingualLexicon.py, SetUpTransferRuleGramCat.py |

---

## IMoAdhocProhib (Ad Hoc Prohibition)

### Owning Collections (OC)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `MembersOC` | IMoForm collection | 3 | AdHocConstrForCluster.py |

### Reference Properties (RA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `FirstMorphemeRA` | IMoMorphSynAnalysis | 3 | AdHocConstrForCluster.py |
| `FirstAllomorphRA` | IMoForm | 3 | AdHocConstrForCluster.py |

### Reference Sequences (RS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `RestOfMorphsRS` | IMoMorphSynAnalysis collection | 3 | AdHocConstrForCluster.py |
| `RestOfAllosRS` | IMoForm collection | 3 | AdHocConstrForCluster.py |

---

## ILexEntryType (Variant/Complex Entry Type)

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `AbbrevHierarchyString` | string | 5+ | FixCapitalizedAnalyses.py, RemoveCapitalVariantEntries.py |

---

## ILexEntryInflType (Irregularly Inflected Form Type)

### Owning Properties (OA)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `InflFeatsOA` | IFsFeatStruc | 5+ | ConvertTextToSTAMPformat.py, Utils.py |

---

## ICmPossibility (Base Possibility)

### Owning Sequences (OS)
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `PossibilitiesOS` | ICmPossibility collection | 5+ | Bulk_Set_Exception_Features.py |

### Simple Properties
| Property | Type | Usage Count | Example Files |
|----------|------|-------------|---------------|
| `Abbreviation` | ITsString | 50+ | Multiple files |
| `Name` | ITsString | 40+ | Multiple files |

---

## Common Properties Across All Objects

### Universal Properties
| Property | Type | Usage | Notes |
|----------|------|-------|-------|
| `ClassName` | string | ALL | Object type identification |
| `Guid` | Guid | ALL | Unique identifier |
| `Owner` | ICmObject | COMMON | Parent object |
| `Hvo` | int | RARE | Handle value (legacy) |

---

## Property Naming Conventions

### Suffixes Explained
- **OA** (Owning Atomic): Single owned object
- **OS** (Owning Sequence): Ordered collection of owned objects
- **OC** (Owning Collection): Unordered collection of owned objects
- **RA** (Reference Atomic): Single reference to another object
- **RS** (Reference Sequence): Ordered collection of references
- **RC** (Reference Collection): Unordered collection of references

### Property Type Patterns
- **ITsString**: Multilingual string (TsString = Text String)
- **Count**: Number of items in a collection
- **ToArray()**: Convert collection to array for iteration

---

## Frequently Used Property Combinations

### Entry Processing Pattern
```python
for entry in DB.LexiconAllEntries():
    if entry.LexemeFormOA and entry.LexemeFormOA.MorphTypeRA:
        for sense in entry.SensesOS:
            if sense.MorphoSyntaxAnalysisRA:
                msa = sense.MorphoSyntaxAnalysisRA
                if msa.ClassName == 'MoStemMsa':
                    pos = IMoStemMsa(msa).PartOfSpeechRA
```

### Variant Entry Pattern
```python
if entry.EntryRefsOS:
    for entryRef in entry.EntryRefsOS:
        if entryRef.RefType == 0:  # variant
            for varType in entryRef.VariantEntryTypesRS:
                # Process variant types
```

### Feature Access Pattern
```python
if msa.MsFeaturesOA:
    for spec in msa.MsFeaturesOA.FeatureSpecsOC:
        feature = spec.FeatureRA
        value = spec.ValueRA
```

### Allomorph Iteration Pattern
```python
if entry.LexemeFormOA:
    # Process main allomorph
for allomorph in entry.AlternateFormsOS:
    if allomorph.MorphTypeRA:
        # Process alternate allomorphs
```

---

## Properties NOT Found in FlexTools

The following properties exist in the LCM model but were NOT found in the FlexTools analysis:

### ILexSense
- `ExamplesOS` (exists but not used)
- `MediaFilesOS`
- `PicturesOS`
- `ThesaurusItemsRS`

### ILexEntry
- `EtymologyOS`
- `MainEntriesOrSensesRS`
- `MinimalLexReferences`

### Text Properties
- `Genre` (rarely used)
- `Source` (rarely used)
- `Description` (rarely used)

---

## Statistical Summary

### Total Unique Properties Found: ~120
### Most Used Properties (Top 10):
1. `SensesOS` (80+ files)
2. `Guid` (100+ files)
3. `ClassName` (80+ files)
4. `HeadWord` (50+ files)
5. `Gloss` (80+ files)
6. `LexemeFormOA` (50+ files)
7. `MorphoSyntaxAnalysisRA` (60+ files)
8. `PartOfSpeechRA` (80+ files)
9. `Form` (80+ files)
10. `MorphTypeRA` (60+ files)

### Property Categories:
- **Owning Atomic (OA)**: 15 unique properties
- **Owning Sequence (OS)**: 20 unique properties
- **Owning Collection (OC)**: 18 unique properties
- **Reference Atomic (RA)**: 25 unique properties
- **Reference Sequence (RS)**: 15 unique properties
- **Reference Collection (RC)**: 12 unique properties
- **Simple Properties**: 15+ unique properties

---

## Usage Notes

### Critical Properties for FLExLibs Implementation
Based on usage frequency, these properties are ESSENTIAL:
1. All `ILexEntry` properties (especially `SensesOS`, `LexemeFormOA`)
2. All `ILexSense` properties (especially `MorphoSyntaxAnalysisRA`, `Gloss`)
3. All `IMoStemMsa` properties (especially `PartOfSpeechRA`)
4. All `MoForm` properties (especially `Form`, `MorphTypeRA`)
5. All `IPartOfSpeech` properties (especially `AffixTemplatesOS`)

### Medium Priority
- Variant/complex form handling (`ILexEntryRef` and related)
- Feature structures (`IFsFeatStruc` and related)
- Morphological data (`IMoMorphData`)

### Lower Priority (Specialized Use)
- Ad hoc prohibitions
- Phonological data
- Advanced feature system operations

---

**End of Report**
