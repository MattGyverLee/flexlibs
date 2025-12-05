# FieldWorks Feature Audit - What's Still in Use?

## Executive Summary

This audit examined which features from the COMPREHENSIVE_MISSING_FEATURES_REPORT are still actively used in FieldWorks (as of 2024), focusing on distinguishing between:
- **Scripture editing** (moved to Paratext)
- **Text/Words import and analysis** (still in FLEx)
- **Deprecated features** (removed)
- **Active features** (maintained)

---

## 1. SCRIPTURE & DRAFT FEATURES

### Status: ✅ **ALL ACTIVELY USED** - for Text/Words, NOT Scripture Editing

| Interface | Status | Usage | Purpose in FLEx |
|-----------|--------|-------|-----------------|
| **IScrBook** | ✅ Active | Heavy (ParatextImport, Interlinear) | Import Scripture books from Paratext for analysis |
| **IScrSection** | ✅ Active | Moderate (ParatextImport, xWorks) | Scripture section structure for concordance |
| **IScrTxtPara** | ✅ Active | Moderate (Text/Words) | Specialized paragraph type for Scripture text |
| **IScrDraft** | ✅ Active | Moderate (ParatextImport) | Archived versions for undo/comparison |
| **IScrBookAnnotations** | ✅ Active | Light (ParatextImport) | Container for imported notes |
| **IScrScriptureNote** | ✅ Active | Moderate (ParatextImport) | Consultant/translator notes from Paratext |
| **IScrCheckRun** | ✅ Active | Light (Repository) | Scripture checking history records |
| **IScripture** | ✅ Active | Container access | Base Scripture container object |

**Key Finding**: Scripture editing was moved to Paratext, but FLEx still imports Scripture books for:
- Interlinear text analysis
- Concordance searches
- Lexical analysis of Scripture vocabulary
- Merging updated Paratext imports

**Primary Code Locations**:
- `D:\Github\FieldWorks\Src\ParatextImport\` (22+ files) - Import functionality
- `D:\Github\FieldWorks\Src\LexText\Interlinear\` - Interlinear display
- `D:\Github\FieldWorks\Src\xWorks\` - Text selection and filtering

**Recommendation for flexlibs**: ✅ **IMPLEMENT** - Essential for Scripture text import and analysis workflows

---

## 2. DISCOURSE ANALYSIS FEATURES

### Status: ✅ **FULLY ACTIVE** - Core FLEx Feature

| Interface | Status | Usage Count | Purpose |
|-----------|--------|-------------|---------|
| **IDsConstChart** | ✅ Active | 30 occurrences, 9 files | Main constituent chart object |
| **IConstChartRow** | ✅ Active | 143 occurrences, 8 files | Chart rows (most heavily used) |
| **IConstChartWordGroup** | ✅ Active | 100 occurrences, 4 files | Word groups in cells |
| **IConstChartMovedTextMarker** | ✅ Active | 35 occurrences, 2 files | Moved/preposed text markers |
| **IConstChartTag** | ✅ Active | 24 occurrences, 3 files | Cell annotations/tags |
| **IConstChartClauseMarker** | ✅ Active | 14 occurrences, 1 file | Clause boundaries |
| **IDsChart** | ✅ Active | Minimal (base interface) | Base chart interface |
| **IDsDiscourseData** | ❌ Not Found | 0 occurrences | Does not exist |

**Evidence of Active Maintenance**:
- 69 commits to Discourse folder since 2020, including 2024 activity
- Full UI implementation: `ConstituentChart.cs` (1,976 lines)
- Massive business logic: `ConstituentChartLogic.cs`
- Export functionality to XML, MS Word, XLingPaper formats
- RTL (Right-to-Left) script support
- Template system for different chart layouts

**Primary Code Locations**:
- `D:\Github\FieldWorks\Src\LexText\Discourse\` (19 non-test files)
- `D:\Github\FieldWorks\DistFiles\Language Explorer\Export Templates\Discourse\`

**Recommendation for flexlibs**: ✅ **IMPLEMENT** - Active, maintained discourse analysis feature

---

## 3. REVERSAL INDEX FEATURES

### Status: ✅ **CORE FLEX FEATURE** - Heavily Used

| Interface | Status | Usage Count | Purpose |
|-----------|--------|-------------|---------|
| **IReversalIndex** | ✅ Active | 753 occurrences, 98 files | Reversal index container |
| **IReversalIndexEntry** | ✅ Active | 323 occurrences, 53 files | Reversal entries |
| **IPartOfSpeech** (reversal) | ✅ Active | Used in reversal context | POS for reversal entries |

**Evidence of Core Feature Status**:
- Dedicated tools: `reversalToolEditComplete`, `reversalToolBulkEditReversalEntries`
- Configuration system per writing system (`ReversalIndexServices.cs`)
- Full UI implementation: `ReversalIndexEntrySlice.cs` (1,613 lines)
- Merging, bulk editing, subentry management
- LIFT import/export integration
- Dictionary export and Webonary upload integration
- 19+ test files including `AllReversalEntriesRecordListTests.cs`

**Primary Code Locations**:
- `D:\Github\FieldWorks\Src\xWorks\ReversalIndexServices.cs`
- `D:\Github\FieldWorks\Src\LexText\Lexicon\ReversalIndexEntrySlice.cs`
- `D:\Github\FieldWorks\Src\FdoUi\ReversalIndexEntryUi.cs`

**Recommendation for flexlibs**: ✅ **IMPLEMENT** - Critical dictionary feature

---

## 4. PUBLICATION FEATURES

### Status: ⚠️ **PARTIAL** - Different Architecture

| Feature | Status | Implementation | Purpose |
|---------|--------|----------------|---------|
| **Publication Types** | ✅ Active | Via `ICmPossibility` | Filtering mechanism |
| **DictionaryPublicationDecorator** | ✅ Active | Main filtering engine | Entry/sense filtering |
| **DoNotPublishInRC** | ✅ Active | 111 occurrences | Exclusion property |
| **IPublicationType** | ⚠️ Concept only | Data model, not interface | Stored as `ICmPossibility` |
| **IPublication** | ⚠️ Abstraction | `PublicationInterfaces.cs` | View interface, not data |
| **IPubDivision** | ❌ Not Found | 0 occurrences | Not implemented |
| **IPubHeader** | ❌ Not Found | 0 occurrences | Not implemented |
| **IPubPageLayout** | ❌ Not Found | 0 occurrences | Not implemented |

**Active Publication Features**:
- Publication types stored as `LexDbOA.PublicationTypesOA` (ICmPossibility hierarchy)
- Default "Main Dictionary" publication auto-created
- `DictionaryPublicationDecorator.cs` (719 lines) - filters by publication
- Homograph number adjustment per publication
- Dictionary export respects publication filtering

**NOT Implemented** (Translation Editor heritage):
- Traditional page layout objects (were TE concepts, not adopted for lexicon)

**Primary Code Locations**:
- `D:\Github\FieldWorks\Src\xWorks\DictionaryPublicationDecorator.cs`
- `D:\Github\FieldWorks\Src\Common\Framework\PublicationInterfaces.cs`

**Recommendation for flexlibs**:
- ✅ **IMPLEMENT** publication filtering via `ICmPossibility` and exclusion properties
- ❌ **SKIP** traditional page layout interfaces (not used)

---

## 5. WORDFORM INVENTORY & ANALYSIS FEATURES

### Status: ✅ **CORE FLEX FEATURE** - Extensively Used

| Interface | Status | Usage Count | Purpose |
|-----------|--------|-------------|---------|
| **IWfiWordform** | ✅ Active | 307 occurrences, 60 files | Wordforms in inventory |
| **IWfiAnalysis** | ✅ Active | 234 occurrences, 48 files | Morphological analyses |
| **IWfiGloss** | ✅ Active | 125 occurrences, 29 files | Analysis glosses |
| **IWfiMorphBundle** | ✅ Active | Extensive use | Morph bundles (no interface def found) |
| **IWordformInventory** | ❌ Not Found | 0 occurrences | Does not exist |

**Evidence of Active Development** (2023-2024):
- LT-18987: Allow interlinear notes to have translations (2024)
- LT-22290: Crash on deleting disapproved wordform analysis (2024)
- LT-22249: Don't modify existing analysis on flextext import (2024)
- LT-22267: Slow response in interlinear combos (2024)
- LT-22162: Sandbox focus shifts when switching interlinear mode (2024)
- LT-5408: Show which parses are valid in chooser (2024)
- LT-21988: Improve Hermit Crab performance (2023)
- **727+ commits in 2024 alone**

**Active Parser Implementations**:
- XAmple Parser (default): `XAmpleParser.cs`
- HermitCrab.NET Parser: `HCParser.cs`
- `IParser` interface: Core abstraction

**Key Features**:
- Interlinear text analysis and glossing
- Morphological parsing (XAmple and HermitCrab)
- Word analysis approval/disapproval workflow
- Concordance functionality
- BIRD format import/export
- Paratext integration

**Primary Code Locations**:
- `D:\Github\FieldWorks\Src\LexText\Interlinear\` (20+ files)
- `D:\Github\FieldWorks\Src\LexText\ParserCore\` (parser engines)
- `D:\Github\FieldWorks\Src\LexText\ParserUI\` (parser UI)
- `D:\Github\FieldWorks\Src\LexText\Morphology\` (10+ files)

**Recommendation for flexlibs**: ✅ **IMPLEMENT** - Essential for Text & Words functionality

---

## 6. PARSER INTERFACES

### Status: ⚠️ **MIXED** - Some Don't Exist as Interfaces

| Name | Status | Type | Purpose |
|------|--------|------|---------|
| **IParser** | ✅ Active | Interface | Base parser abstraction |
| **IParserParameter** | ❌ Not Found | N/A | Does not exist as interface |
| **ParserParametersBase** | ✅ Active | Class | UI for parser parameters |
| **IParserPriority** | ❌ Wrong Type | Enum | Priority levels (not interface) |

**ParserPriority Enum** (actual implementation):
```csharp
public enum ParserPriority {
    ReloadGrammarAndLexicon = 0,
    TryAWord = 1,
    High = 2,
    Medium = 3,
    Low = 4
}
```

**Recommendation for flexlibs**:
- ✅ **IMPLEMENT** `IParser` if wrapping parser functionality
- ❌ **SKIP** IParserParameter (doesn't exist)
- ℹ️ **NOTE** ParserPriority is an enum, not an interface

---

## 7. AGENT & EVALUATION FEATURES

### Status: ❌ **COMPLETELY MIGRATED** - Old Interfaces Gone

| Old Interface | Status | Replacement |
|---------------|--------|-------------|
| **IAgent** | ❌ Not Found | Migrated to new architecture |
| **IAgentEvaluation** | ❌ Not Found | Migrated to new architecture |
| **IChkRef** | ❌ Not Found | Not used |
| **IChkRendering** | ❌ Not Found | Not used |
| **IChkTerm** | ❌ Not Found | Not used |
| **IScrCheckRun** | ❌ Not Found | Replaced by IScriptureCheck |

**Modern Checking System** (✅ ACTIVE):

| New Interface | Location | Purpose |
|---------------|----------|---------|
| **IScriptureCheck** | `FwUtils/IScriptureCheck.cs` | Base check interface |
| **IScrCheckInventory** | Same file | Inventory-based checks |
| **IChecksDataSource** | `FwUtils/IChecksDataSource.cs` | Data provider |
| **IBookVersionAgent** | `ParatextImport/IBookVersionAgent.cs` | Book backup for imports |

**Active Check Implementations** (all in `Lib/src/ScrChecks/`):
1. CharactersCheck - Character validation
2. RepeatedWordsCheck - Duplicate word detection
3. CapitalizationCheck - Capitalization patterns
4. MixedCapitalizationCheck - Mixed case detection
5. PunctuationCheck - Punctuation validation
6. MatchedPairsCheck - Paired markers (quotes, brackets)
7. QuotationCheck - Quotation mark validation
8. ChapterVerseCheck - Chapter/verse numbering

**Spell-Checking** (✅ ACTIVE):
- `SpellCheckHelper.cs` - Full spell-check integration
- Uses `ISpellEngine` from SIL.LCModel.Core
- Hunspell engine integration
- Multi-writing system support

**Recommendation for flexlibs**:
- ❌ **SKIP** old Agent/Evaluation interfaces (don't exist)
- ⚠️ **CONSIDER** new IScriptureCheck system if adding checking features
- ✅ **NOTE** Spell-checking available via separate system

---

## 8. SUMMARY TABLE - WHAT TO IMPLEMENT

| Category | Implement? | Priority | Reason |
|----------|------------|----------|--------|
| **Scripture Import** (IScrBook, IScrSection, etc.) | ✅ Yes | High | Essential for Text/Words import from Paratext |
| **Discourse Charts** (IDsConstChart, IConstChartRow, etc.) | ✅ Yes | Medium | Active discourse analysis feature |
| **Reversal Indexes** (IReversalIndex, IReversalIndexEntry) | ✅ Yes | High | Core dictionary feature |
| **Publication Filtering** (via ICmPossibility) | ✅ Yes | Medium | Dictionary export/filtering |
| **Wordform Inventory** (IWfiWordform, IWfiAnalysis, IWfiGloss) | ✅ Yes | High | Essential for interlinear/parsing |
| **Parser Interfaces** (IParser) | ⚠️ Maybe | Low | Only if wrapping parser functionality |
| **Old Agent/Checking** (IAgent, IChkRef, etc.) | ❌ No | N/A | Don't exist anymore |
| **Page Layout** (IPubDivision, IPubHeader, etc.) | ❌ No | N/A | Never implemented in FLEx |

---

## 9. KEY INSIGHTS

### Scripture Features: Import vs. Editing
- **Editing**: Moved to Paratext (not in FLEx)
- **Import & Analysis**: Still in FLEx - users import Scripture from Paratext for:
  - Interlinear glossing
  - Concordance building
  - Lexical analysis
  - Word frequency studies

### Maintained vs. Deprecated
**NOT A SINGLE DEPRECATED INTERFACE FOUND** in the queried list!
- All Scripture interfaces: Active (for import/analysis)
- All Discourse interfaces: Active (core feature)
- All Reversal interfaces: Active (core feature)
- All Wordform interfaces: Active (core feature)
- Old checking interfaces: Replaced (not deprecated, completely migrated)

### Recent Activity (2024 Commits)
- Interlinear features: Very active (727+ commits in 2024)
- Discourse charts: Maintained (template fixes, infrastructure)
- Reversal indexes: Active (configuration updates)
- Scripture import: Active (Paratext integration updates)

---

## 10. RECOMMENDATIONS FOR FLEXLIBS

### High Priority (Core Features)
1. ✅ **IWfiWordform, IWfiAnalysis, IWfiGloss** - Text & Words analysis
2. ✅ **IScrBook, IScrSection** - Scripture import support
3. ✅ **IReversalIndex, IReversalIndexEntry** - Reversal dictionaries

### Medium Priority (Important Features)
4. ✅ **IDsConstChart, IConstChartRow** - Discourse analysis
5. ✅ **Publication filtering** (ICmPossibility-based) - Export control

### Low Priority (Specialized)
6. ⚠️ **IParser** - Only if wrapping parser engines
7. ⚠️ **Discourse details** (IConstChartWordGroup, etc.) - If full discourse support needed

### Skip (Don't Exist or Not Used)
8. ❌ **IAgent, IAgentEvaluation, IChkRef** - Replaced by new system
9. ❌ **IPubDivision, IPubHeader, IPubPageLayout** - Never implemented
10. ❌ **IWordformInventory** - Doesn't exist
11. ❌ **IDsDiscourseData** - Doesn't exist

---

## 11. CONCLUSION

**The "missing features" in COMPREHENSIVE_MISSING_FEATURES_REPORT are NOT missing!**

Most are **actively used, core features** of FieldWorks:
- Scripture interfaces: Active for Text/Words import
- Discourse: Active, maintained feature
- Reversal: Core dictionary feature
- Wordform/Analysis: Most active area (727+ commits in 2024)

**Only exceptions**:
- Old checking interfaces: Completely migrated to new system (still functional)
- Some specific interfaces (IWordformInventory, IDsDiscourseData): Never existed

**For flexlibs**: Implement the core interfaces (Scripture, Wordform, Reversal) to provide full Text & Words and dictionary functionality. Discourse is optional but active if you want discourse analysis support.
