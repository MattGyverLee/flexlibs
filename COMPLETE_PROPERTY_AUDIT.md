# Complete Property Coverage Audit

## Summary

This document identifies **every property** in the main lexicon objects and shows which have get/set methods.

---

## ILexEntry - Entry Properties

### Current Coverage: 8/20 editable properties (40%)

#### ✅ COVERED - Text Properties:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| LexemeForm | IMoForm.Form | GetLexemeForm() | SetLexemeForm() | Via AllomorphOperations |
| CitationForm | MultiUnicode | GetCitationForm() | SetCitationForm() | ✅ |

#### ❌ MISSING - Text Properties:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **Bibliography** | MultiUnicode | ❌ | ❌ | HIGH |
| **Comment** | MultiString | ❌ | ❌ | HIGH |
| **LiteralMeaning** | MultiString | ❌ | ❌ | MEDIUM |
| **Restrictions** | MultiString | ❌ | ❌ | MEDIUM |
| **SummaryDefinition** | MultiString | ❌ | ❌ | MEDIUM |

#### ✅ COVERED - Metadata Properties:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| DateCreated | GenDate | GetDateCreated() | Read-only | ✅ |
| DateModified | GenDate | GetDateModified() | Read-only | ✅ |
| Guid | Guid | GetGuid() | Read-only | ✅ |
| HomographNumber | Integer | GetHomographNumber() | SetHomographNumber() | ✅ |
| ImportResidue | String | GetImportResidue() | SetImportResidue() | ✅ |

#### ❌ MISSING - Metadata Properties:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **DoNotPublishIn** | Collection<CmPossibility> | ❌ | ❌ | HIGH |
| **DoNotShowMainEntryIn** | Collection<CmPossibility> | ❌ | ❌ | MEDIUM |
| **DoNotUseForParsing** | Boolean | ❌ | ❌ | HIGH |
| **ExcludeAsHeadword** | Boolean | ❌ | ❌ | MEDIUM |
| **MainEntriesOrSensesRS** | Collection (ref) | ❌ | ❌ | MEDIUM |

#### ✅ COVERED - Computed Properties:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| HeadWord | String | GetHeadword() | SetHeadword() | ✅ |
| MorphType | IMoMorphType | GetMorphType() | SetMorphType() | ✅ |

#### ❌ MISSING - Computed Properties:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **MLHeadWord** | MultiString | ❌ | N/A | MEDIUM |

---

## ILexSense - Sense Properties

### Current Coverage: 7/25 editable properties (28%)

#### ✅ COVERED - Text Properties:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| Gloss | MultiString | GetGloss() | SetGloss() | ✅ |
| Definition | MultiString | GetDefinition() | SetDefinition() | ✅ |

#### ❌ MISSING - Text Properties (CRITICAL!):
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **AnthroNote** | MultiString | ❌ | ❌ | MEDIUM |
| **Bibliography** | MultiString | ❌ | ❌ | HIGH |
| **DiscourseNote** | MultiString | ❌ | ❌ | MEDIUM |
| **EncyclopedicInfo** | MultiString | ❌ | ❌ | MEDIUM |
| **GeneralNote** | MultiString | ❌ | ❌ | HIGH |
| **GrammarNote** | MultiString | ❌ | ❌ | MEDIUM |
| **PhonologyNote** | MultiString | ❌ | ❌ | MEDIUM |
| **Restrictions** | MultiString | ❌ | ❌ | MEDIUM |
| **ScientificName** | String | ❌ | ❌ | LOW |
| **SemanticsNote** | MultiString | ❌ | ❌ | MEDIUM |
| **SocioLinguisticsNote** | MultiString | ❌ | ❌ | MEDIUM |
| **Source** | String | ❌ | ❌ | MEDIUM |

#### ✅ COVERED - Reference Properties:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| MorphoSyntaxAnalysisRA | IMoMorphSynAnalysis | GetGrammaticalInfo() | SetGrammaticalInfo() | ✅ |
| SenseTypeRA | ICmPossibility | GetSenseType() | SetSenseType() | ✅ |
| StatusRA | ICmPossibility | GetStatus() | SetStatus() | ✅ |

#### ❌ MISSING - Reference Properties:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **AnthroCodesRC** | Collection<CmAnthroItem> | ❌ | ❌ | LOW |
| **DomainTypesRC** | Collection<CmPossibility> | ❌ | ❌ | MEDIUM |
| **UsageTypesRC** | Collection<CmPossibility> | ❌ | ❌ | HIGH |

#### ✅ COVERED - Collections:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| ExamplesOS | Collection<ILexExampleSentence> | GetExamples() | AddExample() | ✅ |
| PicturesOS | Collection<CmPicture> | GetPictures() | AddPicture() | ✅ |
| SensesOS | Collection<ILexSense> | GetSubsenses() | CreateSubsense() | ✅ |
| SemanticDomainsRC | Collection<CmSemanticDomain> | GetSemanticDomains() | Add/Remove | ✅ |
| ReversalEntriesRC | Collection | GetReversalEntries() | - | ✅ |

#### ✅ COVERED - Metadata:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| Guid | Guid | GetGuid() | Read-only | ✅ |
| SenseNumber | String | GetSenseNumber() | Computed | ✅ |

#### ❌ MISSING - Metadata:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **ImportResidue** | String | ❌ | ❌ | MEDIUM |

---

## ILexExampleSentence - Example Properties

### Current Coverage: 3/6 editable properties (50%)

#### ✅ COVERED - Text Properties:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| Example | MultiString | GetExample() | SetExample() | ✅ |
| Reference | MultiUnicode | GetReference() | SetReference() | ✅ |

#### ❌ MISSING - Text Properties:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **LiteralTranslation** | MultiString | ❌ | ❌ | HIGH |

#### ✅ COVERED - Collections:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| TranslationsOC | CmTranslation | GetTranslation() | SetTranslation() | ✅ |

#### ❌ MISSING - Collections:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **DoNotPublishIn** | Collection<CmPossibility> | ❌ | ❌ | MEDIUM |

#### ❌ MISSING - Metadata:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **Guid** | Guid | ❌ | N/A | LOW (can access directly) |

---

## IMoForm - Allomorph Properties

### Current Coverage: 3/5 editable properties (60%)

#### ✅ COVERED - Text Properties:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| Form | MultiUnicode | GetForm() | SetForm() | ✅ |

#### ✅ COVERED - Reference Properties:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| MorphTypeRA | IMoMorphType | GetMorphType() | SetMorphType() | ✅ |

#### ✅ COVERED - Collections:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| PhoneEnvRC | Collection<IPhEnvironment> | GetPhoneEnv() | Add/Remove | ✅ |

#### ✅ COVERED - Metadata:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| IsAbstract | Boolean | GetIsAbstract() | SetIsAbstract() | ✅ |

#### ❌ MISSING - Metadata:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **Guid** | Guid | ❌ | N/A | LOW |

---

## ILexPronunciation - Pronunciation Properties

### Current Coverage: 4/6 editable properties (67%)

#### ✅ COVERED - Text Properties:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| Form | MultiUnicode | GetForm() | SetForm() | ✅ |
| CVPattern | String | GetCVPattern() | SetCVPattern() | ✅ |
| Tone | String | GetTone() | SetTone() | ✅ |

#### ❌ MISSING - Text Properties:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **Location** | MultiUnicode | GetLocation() | SetLocation() | Actually EXISTS! ✅ |

#### ✅ COVERED - Collections:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| MediaFilesOS | Collection<CmMedia> | GetMediaFiles() | Add/Remove | ✅ |

#### ❌ MISSING - Metadata:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **Guid** | Guid | ❌ | N/A | LOW |

**CORRECTION**: Pronunciation is actually 5/6 (83%)! Location methods exist.

---

## ILexEtymology - Etymology Properties

### Current Coverage: 5/6 editable properties (83%)

#### ✅ COVERED - Text Properties:
| Property | Type | Get | Set | Notes |
|----------|------|-----|-----|-------|
| Form | MultiUnicode | GetForm() | SetForm() | ✅ |
| Gloss | MultiUnicode | GetGloss() | SetGloss() | ✅ |
| Source | MultiUnicode | GetSource() | SetSource() | ✅ |
| Comment | MultiString | GetComment() | SetComment() | ✅ |
| Bibliography | MultiUnicode | GetBibliography() | SetBibliography() | ✅ |

#### ❌ MISSING - Reference Properties:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **LanguageRA** | ICmPossibility | ❌ | ❌ | MEDIUM |

#### ❌ MISSING - Metadata:
| Property | Type | Get | Set | Priority |
|----------|------|-----|-----|----------|
| **Guid** | Guid | ❌ | N/A | LOW |

---

## SUMMARY OF MISSING PROPERTIES

### HIGH PRIORITY (Commonly Used):

#### ILexEntry (5 missing):
1. **Bibliography** (MultiUnicode) - Sources/references
2. **Comment** (MultiString) - General comments
3. **DoNotPublishIn** (Collection) - Publication control
4. **DoNotUseForParsing** (Boolean) - Parser control
5. **Restrictions** (MultiString) - Usage restrictions

#### ILexSense (16 missing!):
1. **Bibliography** (MultiString) - Sources
2. **GeneralNote** (MultiString) - General notes
3. **UsageTypesRC** (Collection) - Usage type references
4. **DomainTypesRC** (Collection) - Domain type references
5. **Restrictions** (MultiString) - Usage restrictions
6. **Source** (String) - Source information
7. **DiscourseNote** (MultiString) - Discourse notes
8. **EncyclopedicInfo** (MultiString) - Encyclopedia info
9. **GrammarNote** (MultiString) - Grammar notes
10. **PhonologyNote** (MultiString) - Phonology notes
11. **SemanticsNote** (MultiString) - Semantics notes
12. **SocioLinguisticsNote** (MultiString) - Sociolinguistics
13. **AnthroNote** (MultiString) - Anthropology notes
14. **AnthroCodesRC** (Collection) - Anthropology codes
15. **ScientificName** (String) - Scientific name
16. **ImportResidue** (String) - Import residue

#### ILexExampleSentence (2 missing):
1. **LiteralTranslation** (MultiString) - Literal translation
2. **DoNotPublishIn** (Collection) - Publication control

#### ILexEtymology (1 missing):
1. **LanguageRA** (ICmPossibility) - Source language

### MEDIUM PRIORITY:
- Various "Note" fields that are less commonly used
- Some reference collections for specialized use

### LOW PRIORITY:
- Guid getters (can access .Guid directly)
- Computed/virtual properties

---

## COVERAGE STATISTICS

| Class | Properties | Covered | Missing | % |
|-------|------------|---------|---------|---|
| **ILexEntry** | 20 | 8 | 12 | 40% |
| **ILexSense** | 25 | 9 | 16 | 36% |
| **ILexExampleSentence** | 6 | 3 | 3 | 50% |
| **IMoForm** | 5 | 4 | 1 | 80% |
| **ILexPronunciation** | 6 | 5 | 1 | 83% |
| **ILexEtymology** | 6 | 5 | 1 | 83% |
| **TOTAL** | **68** | **34** | **34** | **50%** |

---

## RECOMMENDATION

**You need to add get/set methods for 34 properties!**

**Priority Order:**
1. **ILexSense** - 16 properties (most critical - senses are heavily used)
2. **ILexEntry** - 12 properties (entries are core objects)
3. **ILexExampleSentence** - 3 properties
4. **ILexEtymology** - 1 property
5. **IMoForm** - 1 property (Guid - low priority)
6. **ILexPronunciation** - 1 property (Guid - low priority)

Most critical are the **text properties** (Bibliography, Comment, Notes, etc.) and **reference collections** (DoNotPublishIn, UsageTypesRC, DomainTypesRC).

Would you like me to add these missing get/set methods?
