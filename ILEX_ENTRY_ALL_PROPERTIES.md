# Complete ILexEntry Properties (from FLEx 9+ LCM Model)

Based on the FLEx Language & Culture Model (LCM), here are ALL ILexEntry properties:

## Owning Collections (OS)
1. **AlternateFormsOS** - Collection<IMoForm> - Alternate allomorphs
2. **EntryRefsOS** - Collection<ILexEntryRef> - Entry references (variants, complex forms)
3. **EtymologyOS** - Collection<ILexEtymology> - Etymology entries
4. **PronunciationsOS** - Collection<ILexPronunciation> - Pronunciations
5. **SensesOS** - Collection<ILexSense> - Senses

## Owning Atomic (OA)
6. **LexemeFormOA** - IMoForm - Primary lexeme form/allomorph

## Reference Sequences (RS)
7. **MainEntriesOrSensesRS** - Collection - Main entries or senses
8. **VisibleComplexFormBackRefs** - Collection - Complex form back references (computed)

## Reference Collections (RC)
9. **ReversalEntriesRC** - Collection - Reversal entries

## MultiString Properties
10. **Bibliography** - MultiUnicode - Bibliographic references
11. **CitationForm** - MultiUnicode - Citation form
12. **Comment** - MultiString - General comments
13. **LiteralMeaning** - MultiString - Literal meaning
14. **Restrictions** - MultiString - Usage restrictions
15. **SummaryDefinition** - MultiString - Summary definition

## Simple Properties
16. **DateCreated** - GenDate - Creation date (read-only)
17. **DateModified** - GenDate - Last modification date (read-only)
18. **DoNotPublishIn** - Collection<CmPossibility> - Publications to exclude from
19. **DoNotShowMainEntryIn** - Collection<CmPossibility> - Where not to show as main entry
20. **DoNotUseForParsing** - Boolean - Exclude from parser
21. **ExcludeAsHeadword** - Boolean - Exclude as headword
22. **Guid** - Guid - Unique identifier (read-only)
23. **HomographNumber** - Integer - Homograph number
24. **ImportResidue** - String - Import residue data

## Computed/Virtual Properties
25. **HeadWord** - ITsString - Computed headword (from LexemeForm or CitationForm)
26. **MLHeadWord** - MultiString - Multi-lingual headword (virtual)
27. **MorphType** - IMoMorphType - Morph type (from LexemeFormOA.MorphTypeRA)

## Total: 27 properties

---

# Complete ILexSense Properties

## Owning Collections (OS)
1. **ExamplesOS** - Collection<ILexExampleSentence> - Example sentences
2. **PicturesOS** - Collection<CmPicture> - Pictures
3. **SensesOS** - Collection<ILexSense> - Subsenses

## Reference Collections (RC)
4. **AnthroCodesRC** - Collection<CmAnthroItem> - Anthropology codes
5. **DomainTypesRC** - Collection<CmPossibility> - Domain types
6. **ReversalEntriesRC** - Collection<IReversalIndexEntry> - Reversal entries
7. **SemanticDomainsRC** - Collection<CmSemanticDomain> - Semantic domains
8. **ThesaurusItemsRC** - Collection<ICmPossibility> - Thesaurus items
9. **UsageTypesRC** - Collection<CmPossibility> - Usage types

## Reference Sequences (RS)
10. **AppendixesRS** - Collection<ILexAppendix> - Appendix references

## Reference Atomic (RA)
11. **MorphoSyntaxAnalysisRA** - IMoMorphSynAnalysis - Grammatical info
12. **SenseTypeRA** - ICmPossibility - Sense type
13. **StatusRA** - ICmPossibility - Status

## MultiString Properties
14. **AnthroNote** - MultiString - Anthropology notes
15. **Bibliography** - MultiString - Bibliography
16. **Definition** - MultiString - Definition
17. **DiscourseNote** - MultiString - Discourse notes
18. **EncyclopedicInfo** - MultiString - Encyclopedic information
19. **GeneralNote** - MultiString - General notes
20. **Gloss** - MultiString - Gloss
21. **GrammarNote** - MultiString - Grammar notes
22. **PhonologyNote** - MultiString - Phonology notes
23. **Restrictions** - MultiString - Restrictions
24. **SemanticsNote** - MultiString - Semantics notes
25. **SocioLinguisticsNote** - MultiString - Socio-linguistics notes

## Simple Properties
26. **Guid** - Guid - Unique identifier (read-only)
27. **ImportResidue** - String - Import residue
28. **ScientificName** - String - Scientific name
29. **SenseNumber** - String - Sense number (computed)
30. **Source** - String - Source

## Total: 30 properties

---

# Complete ILexExampleSentence Properties

## Owning Collections (OC)
1. **TranslationsOC** - Collection<CmTranslation> - Translations

## Reference Collections (RC)
2. **DoNotPublishIn** - Collection<CmPossibility> - Publications to exclude from

## MultiString/MultiUnicode Properties
3. **Example** - MultiString - Example text
4. **LiteralTranslation** - MultiString - Literal translation
5. **Reference** - MultiUnicode - Reference

## Simple Properties
6. **Guid** - Guid - Unique identifier (read-only)

## Total: 6 properties

---

# Complete IMoForm (Allomorph) Properties

## Reference Collections (RC)
1. **PhoneEnvRC** - Collection<IPhEnvironment> - Phonological environments

## Reference Atomic (RA)
2. **MorphTypeRA** - IMoMorphType - Morph type

## MultiUnicode Properties
3. **Form** - MultiUnicode - Allomorph form

## Simple Properties
4. **Guid** - Guid - Unique identifier (read-only)
5. **IsAbstract** - Boolean - Is abstract form

## Total: 5 properties

---

# Complete ILexPronunciation Properties

## Owning Collections (OS)
1. **MediaFilesOS** - Collection<CmMedia> - Media files

## MultiUnicode/String Properties
2. **CVPattern** - String - CV pattern
3. **Form** - MultiUnicode - Pronunciation form
4. **Location** - MultiUnicode - Location where used
5. **Tone** - String - Tone

## Simple Properties
6. **Guid** - Guid - Unique identifier (read-only)

## Total: 6 properties

---

# Complete ILexEtymology Properties

## Reference Atomic (RA)
1. **LanguageRA** - ICmPossibility - Source language

## MultiString/MultiUnicode Properties
2. **Bibliography** - MultiUnicode - Bibliography
3. **Comment** - MultiString - Comment
4. **Form** - MultiUnicode - Etymological form
5. **Gloss** - MultiUnicode - Gloss
6. **Source** - MultiUnicode - Source

## Simple Properties
7. **Guid** - Guid - Unique identifier (read-only)

## Total: 7 properties

---

# Summary

| Object | Total Properties | Collections | Text Fields | Simple Fields |
|--------|------------------|-------------|-------------|---------------|
| ILexEntry | 27 | 9 | 6 | 12 |
| ILexSense | 30 | 10 | 12 | 8 |
| ILexExampleSentence | 6 | 2 | 3 | 1 |
| IMoForm | 5 | 1 | 1 | 3 |
| ILexPronunciation | 6 | 1 | 4 | 1 |
| ILexEtymology | 7 | 0 | 5 | 2 |
| **TOTAL** | **81** | **23** | **31** | **27** |

This is the COMPLETE set of properties you need get/set methods for!
