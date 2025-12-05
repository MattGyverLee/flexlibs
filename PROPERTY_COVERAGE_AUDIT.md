# Property Coverage Audit

## ILexEntry Properties

### Analyzed Properties from LCM Model:

#### Form Properties (MultiString/MultiUnicode):
| Property | Type | Get Method | Set Method | Status |
|----------|------|------------|------------|--------|
| **LexemeForm** | IMoForm (object) | GetLexemeForm() | SetLexemeForm() | ✅ Full |
| **CitationForm** | MultiUnicode | GetCitationForm() | SetCitationForm() | ✅ Full |
| **Bibliography** | MultiUnicode | ❌ Missing | ❌ Missing | ⚠️ **NEED** |
| **Comment** | MultiString | ❌ Missing | ❌ Missing | ⚠️ **NEED** |
| **LiteralMeaning** | MultiString | ❌ Missing | ❌ Missing | ⚠️ **NEED** |
| **Restrictions** | MultiString | ❌ Missing | ❌ Missing | ⚠️ **NEED** |
| **SummaryDefinition** | MultiString | ❌ Missing | ❌ Missing | ⚠️ **NEED** |

#### Metadata Properties:
| Property | Type | Get Method | Set Method | Status |
|----------|------|------------|------------|--------|
| **DateCreated** | GenDate | GetDateCreated() | Read-only | ✅ Full |
| **DateModified** | GenDate | GetDateModified() | Read-only | ✅ Full |
| **DoNotPublishIn** | Collection | ❌ Missing | ❌ Missing | ⚠️ **NEED** |
| **DoNotShowMainEntryIn** | Collection | ❌ Missing | ❌ Missing | ⚠️ **NEED** |
| **DoNotUseForParsing** | Boolean | ❌ Missing | ❌ Missing | ⚠️ **NEED** |
| **ExcludeAsHeadword** | Boolean | ❌ Missing | ❌ Missing | ⚠️ **NEED** |
| **Guid** | Guid | GetGuid() | Read-only | ✅ Full |
| **HomographNumber** | Integer | GetHomographNumber() | SetHomographNumber() | ✅ Full |
| **ImportResidue** | String | GetImportResidue() | SetImportResidue() | ✅ Full |

#### Derived/Computed Properties:
| Property | Type | Get Method | Set Method | Status |
|----------|------|------------|------------|--------|
| **HeadWord** | String (computed) | GetHeadword() | SetHeadword() | ✅ Full |
| **MLHeadWord** | MultiString (computed) | ❌ Missing | N/A | ⚠️ **NEED** |
| **ReversalEntriesRC** | Collection (ref) | Direct access | N/A | ✅ OK |
| **VisibleComplexFormBackRefs** | Collection (computed) | Direct access | N/A | ✅ OK |

#### Reference Properties:
| Property | Type | Get Method | Set Method | Status |
|----------|------|------------|------------|--------|
| **MainEntriesOrSensesRS** | Collection | Direct access | Direct access | ✅ OK |
| **LexemeFormOA** | IMoForm | Direct access | Via AllomorphOps | ✅ OK |

**Current Coverage: 8/17 properties (47%)** ⚠️

**Missing: 9 properties!**

---

## ILexSense Properties

Let me analyze...
