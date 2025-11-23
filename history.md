# flexlibs History

## Known Issues

None

## History

### 2.0.0 - 23 Nov 2025

**Major Release: Advanced Operations**

+ **Phase 1: Core CRUD Operations** (28 methods)
    + **POSOperations** - Parts of Speech management (10 methods)
        + GetAll(), Create(), Delete(), Exists(), Find()
        + GetName(), SetName(), GetAbbreviation(), SetAbbreviation()
        + GetSubcategories()
    + **TextOperations** - Text corpus management (14 methods)
        + Core: Create(), Delete(), Exists(), GetAll(), GetName(), SetName(), GetGenre(), SetGenre()
        + Advanced: GetContents(), GetParagraphs(), GetParagraphCount(), GetMediaFiles(), AddMediaFile(), GetAbbreviation()
    + **WordformOperations** - Wordform management (10 methods)
        + GetAll(), Create(), Delete(), Exists(), Find()
        + GetForm(), SetForm()
        + GetSpellingStatus(), SetSpellingStatus()
        + GetAnalyses()

+ **Phase 2: Interlinear Text Operations** (28 methods)
    + **ParagraphOperations** - Paragraph management (13 methods)
        + Core: Create(), Delete(), GetAll(), GetText(), SetText(), GetSegments(), GetSegmentCount(), InsertAt()
        + Advanced: GetTranslations(), SetTranslation(), GetNotes(), AddNote(), GetStyleName()
    + **SegmentOperations** - Segment operations (9 methods)
        + GetAll(), GetAnalyses()
        + GetBaselineText(), SetBaselineText()
        + GetFreeTranslation(), SetFreeTranslation()
        + GetLiteralTranslation(), SetLiteralTranslation()
        + GetNotes()

+ **Phase 3: Phonology Operations** (32 methods)
    + **PhonemeOperations** - Phoneme management (16 methods)
        + Core: GetAll(), Create(), Delete(), Exists(), Find()
        + Properties: GetRepresentation(), SetRepresentation(), GetDescription(), SetDescription()
        + Advanced: GetCodes(), AddCode(), RemoveCode(), IsVowel(), IsConsonant(), GetFeatures(), SetFeatures()
    + **NaturalClassOperations** - Natural class management (9 methods)
        + Core: GetAll(), Create(), Delete(), Exists(), Find()
        + Properties: GetName(), SetName()
        + Phonemes: GetPhonemes(), AddPhoneme(), RemovePhoneme()
    + **EnvironmentOperations** - Phonological environments (7 methods)
        + Core: GetAll(), Create(), Delete(), Exists()
        + Properties: GetName(), SetName(), GetStringRepresentation()

+ **Phase 4: Morphology & Grammar Operations** (46 methods)
    + **AllomorphOperations** - Allomorph management (10 methods)
        + Core: GetAll(), Create(), Delete(), Exists()
        + Properties: GetForm(), SetForm(), GetMorphType(), SetMorphType()
        + Environment: GetPhoneEnv(), AddPhoneEnv()
    + **MorphRuleOperations** - Morphological rules (11 methods)
        + Core: GetAll(), Create(), Delete(), Exists(), Find()
        + Properties: GetName(), SetName(), GetDescription(), SetDescription()
        + Control: IsActive(), SetActive(), GetStratum()
    + **InflectionFeatureOperations** - Inflection features (12 methods)
        + Classes: GetAllClasses(), CreateClass(), DeleteClass(), GetClassName(), SetClassName()
        + Structures: GetAllStructures(), CreateStructure(), DeleteStructure()
        + Features: GetAllFeatures(), CreateFeature(), GetFeatureName(), SetFeatureName()
    + **POSOperations** - Extended POS operations (16 methods total, 6 new)
        + Advanced: GetInflectionClasses(), AddInflectionClass(), GetAffixSlots(), AddAffixSlot(), GetDefaultFeatures(), SetDefaultFeatures()
    + **GramCatOperations** - Grammatical categories (7 methods)
        + Core: GetAll(), Create(), Delete(), Exists()
        + Properties: GetName(), SetName()
        + Hierarchy: GetSubcategories(), GetParent()

+ **Phase 5: Wordform Advanced Operations** (6 new methods)
    + **WordformOperations** - Extended wordform operations (16 methods total, 6 new)
        + Advanced: GetOccurrenceCount(), GetAllUnapproved(), ApproveSpelling(), GetChecksum(), FindByForm(), GetAnalysisGlosses()

+ **Phase 6: Phonological Rule Components** (18 methods)
    + **PhonologicalRuleOperations** - Phonological rule management with full component support (18 methods)
        + Core: GetAll(), Create(), Delete(), Exists(), Find()
        + Properties: GetName(), SetName(), GetDescription(), SetDescription()
        + Control: GetStratum(), SetStratum(), GetDirection(), SetDirection()
        + Components: AddInputSegment(), AddOutputSegment(), SetLeftContext(), SetRightContext()

+ **Phase 7: Lexicon Core Operations** (71 methods)
    + **LexEntryOperations** - Lexical entry management (23 methods)
        + Core: GetAll(), Create(), Delete(), Exists(), Find()
        + Headword: GetHeadword(), SetHeadword(), GetLexemeForm(), SetLexemeForm()
        + Citation: GetCitationForm(), SetCitationForm()
        + Properties: GetHomographNumber(), SetHomographNumber(), GetDateCreated(), GetDateModified()
        + Morph Type: GetMorphType(), SetMorphType()
        + Senses: GetSenses(), GetSenseCount(), AddSense()
        + Additional: GetGuid(), GetImportResidue(), SetImportResidue()
    + **LexSenseOperations** - Lexical sense management (31 methods)
        + Core: GetAll(), Create(), Delete(), Reorder()
        + Gloss & Definition: GetGloss(), SetGloss(), GetDefinition(), SetDefinition()
        + Grammatical: GetPartOfSpeech(), SetPartOfSpeech(), GetGrammaticalInfo(), SetGrammaticalInfo()
        + Semantic Domains: GetSemanticDomains(), AddSemanticDomain(), RemoveSemanticDomain()
        + Examples: GetExamples(), GetExampleCount(), AddExample()
        + Subsenses: GetSubsenses(), CreateSubsense(), GetParentSense()
        + Status: GetStatus(), SetStatus(), GetSenseType(), SetSenseType()
        + Reversal: GetReversalEntries(), GetReversalCount()
        + Pictures: GetPictures(), GetPictureCount()
        + Additional: GetGuid(), GetOwningEntry(), GetSenseNumber(), GetAnalysesCount()
    + **ExampleOperations** - Example sentence management (17 methods)
        + Core: GetAll(), Create(), Delete(), Reorder()
        + Text: GetExample(), SetExample()
        + Translations: GetTranslations(), GetTranslation(), SetTranslation(), AddTranslation(), RemoveTranslation()
        + Reference: GetReference(), SetReference()
        + Media: GetMediaFiles(), GetMediaCount()
        + Additional: GetOwningSense(), GetGuid()

+ **Phase 8: Advanced Lexicon Operations** (102 methods)
    + **LexReferenceOperations** - Cross-references and lexical relations (26 methods)
        + Type Management: GetAllTypes(), CreateType(), DeleteType(), FindType(), GetTypeName(), SetTypeName(), GetTypeReverseName(), SetTypeReverseName(), GetMappingType()
        + Reference Management: GetAll(), Create(), Delete(), GetTargets(), AddTarget(), RemoveTarget(), GetType(), GetReferencesOfType()
        + Complex Forms: ShowComplexFormsIn(), GetComplexFormEntries(), GetComponentEntries()
    + **VariantOperations** - Variant form management (16 methods)
        + Type Management: GetAllTypes(), FindType(), GetTypeName(), GetTypeDescription()
        + Variant Management: GetAll(), Create(), Delete(), GetForm(), SetForm(), GetType(), SetType()
        + Components: GetComponentLexemes(), AddComponentLexeme(), RemoveComponentLexeme()
        + Utilities: GetOwningEntry(), GetVariantCount()
    + **PronunciationOperations** - Pronunciation with IPA/audio (14 methods)
        + Core: GetAll(), Create(), Delete(), Reorder()
        + Form: GetForm(), SetForm()
        + Media: GetMediaFiles(), GetMediaCount(), AddMediaFile(), RemoveMediaFile()
        + Location: GetLocation(), SetLocation()
        + Utilities: GetOwningEntry(), GetGuid()
    + **SemanticDomainOperations** - Semantic domain management (19 methods)
        + Core: GetAll(), Find(), FindByName(), Exists()
        + Properties: GetName(), SetName(), GetDescription(), SetDescription(), GetAbbreviation(), GetNumber(), GetQuestions(), GetOcmCodes()
        + Hierarchy: GetSubdomains(), GetParent(), GetDepth()
        + Usage: GetSensesInDomain(), GetSenseCount()
        + Custom: Create(), Delete()
    + **ReversalOperations** - Reversal entry CRUD (18 methods)
        + Index: GetAllIndexes(), GetIndex(), FindIndex()
        + Entry CRUD: GetAll(), Create(), Delete(), Find(), Exists()
        + Form: GetForm(), SetForm()
        + Sense Linking: GetSenses(), AddSense(), RemoveSense(), GetSenseCount()
        + Subentries: GetSubentries(), CreateSubentry(), GetParentEntry()
        + POS: GetPartsOfSpeech()
    + **EtymologyOperations** - Etymology tracking (16 methods)
        + Core: GetAll(), Create(), Delete(), Reorder()
        + Source: GetSource(), SetSource()
        + Form & Gloss: GetForm(), SetForm(), GetGloss(), SetGloss()
        + Comment & Bibliography: GetComment(), SetComment(), GetBibliography(), SetBibliography()
        + Utilities: GetOwningEntry(), GetGuid()

+ **Phase 9: Interlinear Analysis Operations** (54 methods)
    + **WfiAnalysisOperations** - Wordform analysis management (21 methods)
        + Core: GetAll(), Create(), Delete(), Exists()
        + Status: ApproveAnalysis(), DisapproveAnalysis(), GetApprovalStatus(), SetApprovalStatus()
        + Components: GetGlosses(), GetGlossCount(), GetMorphBundles(), GetMorphBundleCount()
        + Properties: GetCategory(), SetCategory(), GetAgent(), SetAgent()
        + Navigation: GetWordform(), GetAnalysesForWordform()
        + Queries: GetUnapprovedAnalyses(), GetApprovedAnalyses(), GetHumanApprovedAnalyses()
        + Utilities: CopyAnalysis(), GetGuid()
    + **WfiGlossOperations** - Wordform gloss management (15 methods)
        + Core: GetAll(), Create(), Delete(), Exists()
        + Form: GetForm(), SetForm(), GetAllForms()
        + Navigation: GetAnalysis(), GetWordform()
        + Queries: GetGlossesForForm(), FindByForm()
        + Utilities: CopyGloss(), GetGuid()
    + **WfiMorphBundleOperations** - Morpheme bundle management (18 methods)
        + Core: GetAll(), Create(), Delete(), Exists()
        + Form: GetForm(), SetForm()
        + Sense Linking: GetSense(), SetSense(), GetEntry()
        + Morphology: GetMorphType(), SetMorphType(), GetMSA(), SetMSA()
        + Navigation: GetAnalysis(), GetWordform(), GetPosition(), SetPosition()
        + Utilities: GetGuid()

+ **Phase 10: System Configuration Operations** (24 methods)
    + **MediaOperations** - Media file management (24 methods)
        + Core: GetAll(), Create(), Delete(), Exists(), Find()
        + File Operations: GetFilename(), SetFilename(), GetFilePath(), CopyToProject()
        + Properties: GetMediaType(), GetDescription(), SetDescription(), GetLabel(), SetLabel()
        + Internal Path: GetInternalPath(), SetInternalPath()
        + Folder Management: GetFolder(), SetFolder(), GetFolderName()
        + Queries: GetOrphanedMedia(), FindByFilename(), FindByPath()
        + Utilities: GetGuid(), IsOrphaned()

+ **Phase 11: Advanced Features** (85 methods)
    + **PossibilityListOperations** - Generic possibility list management (24 methods)
        + List Management: GetAllLists(), FindList(), CreateList(), DeleteList(), GetListName(), GetListOwner()
        + Item Management: GetItems(), CreateItem(), DeleteItem(), GetItemName(), SetItemName()
        + Hierarchy: GetParent(), GetChildren(), GetDepth(), MoveItem(), ReorderItem()
        + Navigation: FindItem(), FindByGuid(), GetAbbreviation(), SetAbbreviation()
        + Queries: GetAllItemsFlat(), GetItemCount()
        + Utilities: GetGuid()
    + **NoteOperations** - Note and annotation management (16 methods)
        + Core: GetAll(), Create(), Delete(), Exists()
        + Content: GetContent(), SetContent(), GetPlainText()
        + Threading: AddReply(), GetReplies(), GetReplyCount(), GetParentNote()
        + Properties: GetNoteType(), SetNoteType(), GetAuthor(), GetDateCreated()
        + Utilities: GetAnnotatedObject()
    + **SegmentOperations** - Enhanced segment operations (21 methods total, 12 new)
        + NEW Core: Create(), Delete()
        + NEW Advanced: SplitSegment(), MergeSegments(), GetWordforms(), GetWordformCount()
        + NEW Validation: ValidateSegments(), RebuildSegments(), GetInvalidSegments()
        + NEW Queries: FindSegmentsByText(), GetSegmentIndex()
        + Existing: GetAll(), GetAnalyses(), GetBaselineText(), SetBaselineText(), GetFreeTranslation(), SetFreeTranslation(), GetLiteralTranslation(), SetLiteralTranslation(), GetNotes()
    + **FilterOperations** - Filter and query management (18 methods)
        + Core: GetAll(), Create(), Delete(), Exists(), Find()
        + Filter Operations: ApplyFilter(), GetFilterResults(), ClearFilterCache()
        + Properties: GetName(), SetName(), GetDescription(), SetDescription()
        + Definition: GetFilterDefinition(), SetFilterDefinition()
        + Import/Export: ExportFilter(), ImportFilter(), GetFilterJSON()
        + Utilities: ValidateFilter(), GetGuid()
    + **DiscourseOperations** - Discourse chart management (15 methods)
        + Chart Management: GetAllCharts(), CreateChart(), DeleteChart(), GetChartName(), SetChartName()
        + Row Operations: GetRows(), AddRow(), DeleteRow(), GetRowCount()
        + Cell Operations: GetCellContent(), SetCellContent(), ClearCell()
        + Template: GetChartTemplate(), SetChartTemplate()
        + Utilities: GetText()

+ **Phase 12: Anthropology & Cultural Data** (92 methods)
    + **PersonOperations** - People management for consultants, speakers, researchers (30 methods)
        + Core: GetAll(), Create(), Delete(), Exists(), Find()
        + Name: GetName(), SetName()
        + Personal Info: GetGender(), SetGender(), GetDateOfBirth(), SetDateOfBirth()
        + Contact: GetEmail(), SetEmail(), GetPhone(), SetPhone(), GetAddress(), SetAddress()
        + Academic: GetEducation(), SetEducation(), GetPositions(), AddPosition()
        + Relationships: GetResidences(), AddResidence(), GetLanguages(), AddLanguage()
        + Notes: GetNotes(), AddNote()
        + Metadata: GetGuid(), GetDateCreated(), GetDateModified()
    + **LocationOperations** - Geographic location management (28 methods)
        + Core: GetAll(), Create(), Delete(), Exists(), Find()
        + Name & Alias: GetName(), SetName(), GetAlias(), SetAlias()
        + Geographic: GetCoordinates(), SetCoordinates(), GetElevation(), SetElevation()
        + Description: GetDescription(), SetDescription()
        + Hierarchy: GetRegion(), SetRegion(), GetSublocations(), CreateSublocation()
        + Metadata: GetGuid(), GetDateCreated(), GetDateModified()
        + Queries: FindByCoordinates(), GetNearby()
    + **AnthropologyOperations** - Cultural/ethnographic data management (34 methods)
        + Core: GetAll(), Create(), CreateSubitem(), Delete(), Exists(), Find()
        + Properties: GetName(), SetName(), GetAbbreviation(), SetAbbreviation()
        + Description: GetDescription(), SetDescription()
        + Categories: GetAnthroCode(), SetAnthroCode(), GetCategory(), SetCategory()
        + Hierarchy: GetSubitems(), GetParent()
        + Queries: FindByCode(), FindByCategory(), GetItemsForText()
        + Text Linking: GetTexts(), AddText(), RemoveText(), GetTextCount()
        + Researchers: GetResearchers(), AddResearcher(), RemoveResearcher()
        + Metadata: GetGuid(), GetDateCreated(), GetDateModified()

+ Access via FLExProject properties:
    + `project.POS` - Parts of Speech operations (extended in Phase 4)
    + `project.Texts` - Text operations
    + `project.Wordforms` - Wordform operations (extended in Phase 5)
    + `project.Paragraphs` - Paragraph operations
    + `project.Segments` - Segment operations
    + `project.Phonemes` - Phoneme operations
    + `project.NaturalClasses` - Natural class operations
    + `project.Environments` - Environment operations
    + `project.Allomorphs` - Allomorph operations
    + `project.MorphRules` - Morph rule operations
    + `project.InflectionFeatures` - Inflection feature operations
    + `project.GramCat` - Grammatical category operations
    + `project.PhonRules` - Phonological rule operations with components
    + `project.LexEntry` - Lexical entry operations
    + `project.Senses` - Lexical sense operations
    + `project.Examples` - Example sentence operations
    + `project.LexReferences` - Cross-reference operations (new)
    + `project.Variants` - Variant form operations (new)
    + `project.Pronunciations` - Pronunciation operations (new)
    + `project.SemanticDomains` - Semantic domain operations (new)
    + `project.Reversal` - Reversal entry operations (new)
    + `project.Etymology` - Etymology operations (new)
    + `project.WfiAnalyses` - Wordform analysis operations (Phase 9)
    + `project.WfiGlosses` - Wordform gloss operations (Phase 9)
    + `project.WfiMorphBundles` - Morpheme bundle operations (Phase 9)
    + `project.Media` - Media file operations (Phase 10)
    + `project.PossibilityLists` - Generic possibility list operations (Phase 11)
    + `project.Notes` - Note and annotation operations (Phase 11)
    + `project.Filters` - Filter and query operations (Phase 11)
    + `project.Discourse` - Discourse chart operations (Phase 11)
    + `project.Person` - People management operations (Phase 12)
    + `project.Location` - Geographic location operations (Phase 12)
    + `project.Anthropology` - Cultural/ethnographic data operations (Phase 12)
    + `project.ProjectSettings` - Project configuration operations (Phase 13)
    + `project.Publications` - Publication management operations (Phase 13)
    + `project.Agents` - Analysis agent operations (Phase 13)
    + `project.Confidence` - Confidence level operations (Phase 13)
    + `project.Overlays` - Discourse overlay operations (Phase 13)
    + `project.TranslationTypes` - Translation type operations (Phase 13)
    + `project.AnnotationDefs` - Annotation definition operations (Phase 13)
    + `project.Checks` - Consistency check operations (Phase 13)
    + `project.DataNotebook` - Data notebook operations (Phase 14)

+ New exports:
    + POSOperations, TextOperations, WordformOperations classes
    + ParagraphOperations, SegmentOperations classes
    + PhonemeOperations, NaturalClassOperations, EnvironmentOperations classes
    + AllomorphOperations, MorphRuleOperations, InflectionFeatureOperations classes
    + GramCatOperations, PhonologicalRuleOperations classes
    + LexEntryOperations, LexSenseOperations, ExampleOperations classes
    + LexReferenceOperations, VariantOperations, PronunciationOperations classes
    + SemanticDomainOperations, ReversalOperations, EtymologyOperations classes
    + WfiAnalysisOperations, WfiGlossOperations, WfiMorphBundleOperations classes (Phase 9)
    + MediaOperations class (Phase 10)
    + PossibilityListOperations, NoteOperations, FilterOperations, DiscourseOperations classes (Phase 11)
    + PersonOperations, LocationOperations, AnthropologyOperations classes (Phase 12)
    + ProjectSettingsOperations, PublicationOperations, AgentOperations, ConfidenceOperations classes (Phase 13)
    + OverlayOperations, TranslationTypeOperations, AnnotationDefOperations, CheckOperations classes (Phase 13)
    + DataNotebookOperations class (Phase 14)
    + SpellingStatusStates enumeration
    + ApprovalStatusTypes enumeration (Phase 9)
    + MediaType enumeration (Phase 10)

+ All new operations follow flexlibs conventions:
    + PascalCase method naming
    + Proper exception handling
    + Writing system support (vernacular for baseline, analysis for translations)
    + Comprehensive Google-style docstrings
    + Real FLEx LCM API integration

+ **Total: 793 methods** across 43 operation classes

+ Examples provided for all new operations

+ Maintains 100% backward compatibility with v1.2.8 API

### 1.2.8 - 10 Sep 2025

+ FLExProject functions:
    + Added LexiconClearListFieldSingle() 
    + Added LexiconSetLexemeForm()
    + Added LexiconGetExampleCustomFields()
    + Added LexiconGetAllomorphCustomFields()

### 1.2.7 - 25 Aug 2025

+ Supports Python 3.8 - 3.13
+ Supports FieldWorks 9.0.17 - 9.3.1

+ FLExProject functions:
    + Added GetFieldID()
    + Added support for Lists (single or multiple) in GetCustomFieldValue()
    + Added ListFieldPossibilityList()
    + Added ListFieldPossibilities()
    + Added ListFieldLookup()
    + Added LexiconSetListFieldSingle() 
    + Added LexiconSetListFieldMultiple() 

### 1.2.6 - 26 Jun 2025

+ Supports Python 3.8 - 3.13
+ Supports FieldWorks 9.0.17 - 9.2.8

### 1.2.5 - 13 Jun 2025

+ When generating the list of projects, check that the fwdata file 
  exists, not just the directory. [Issue #14]
+ New function:
    + OpenProjectInFW(projectName)
+ Tidied up the presentation of the API documentation.

### 1.2.4 - 14 Aug 2024

+ New FLExProject function:
    + ObjectRepository(repository)

### 1.2.3 - 9 Jul 2024

+ GetAllSemanticDomains() returns ICmSemanticDomain objects
+ New FLExProject functions:
    + Object(hvoOrGuid)
    + LexiconAllEntriesSorted()
    + GetLexicalRelationTypes()
    + GetPublications()
    + PublicationType(publicationName)

### 1.2.2 - 15 Nov 2023

+ Supports Python 3.8 - 3.12
+ Supports FieldWorks 9.0.4 - 9.1.25

### 1.2.1 - 29 Aug 2023

+ Supports Python 3.6 - 3.11
+ Supports FieldWorks 9.0.4 - 9.1.22

+ New FLExProject functions:
    + LexiconFieldIsMultiType() 
    + LexiconFieldIsAnyStringType()
    + LexiconGetSenseNumber()
    + LexiconSenseAnalysesCount()

### 1.2.0 - 16 Aug 2023

+ Moved to pythonnet 3.0.1, which supports FieldWorks 9.1.22

+ FieldWorks dlls no longer need to be included, so the package size 
  has been greatly reduced.

### 1.1.8 - 11 Apr 2023

+ Added LexiconClearField()
+ Updated Set/Get Field functions to handle MultiStrings and a WS 
  parameter (fully backward compatible).

### 1.1.6 - 24 Nov 2022

+ Added the DLLs needed to support FieldWorks 9.1.15/16
+ Added support for Texts to BuildGotoURL()

### 1.1.5 - 15 Oct 2022

+ Constrained pythonnet to < 3 since flexlibs breaks with the new v3.0.0 

### 1.1.3 - 24 Jun 2022

+ FLExProject now requires a CloseProject() call to save data and
  release the lock on the FLEx project.

### 1.1.2 - 20 Jun 2022

+ Configured as a package and published on PyPI
+ Includes .NET DLLs that are needed for compatibility with FLEx 9.0
  through to 9.1.9
  
+ **Phase 13: Project Configuration & Specialized Metadata** (165 methods)
    + **ProjectSettingsOperations** - Project configuration (18 methods)
        + Project Info: GetProjectName(), SetProjectName(), GetDescription(), SetDescription()
        + Language Settings: GetVernacularWSs(), GetAnalysisWSs(), SetDefaultVernacular(), SetDefaultAnalysis()
        + UI Settings: GetInterfaceLanguage(), SetInterfaceLanguage()
        + Default Fonts: GetDefaultFont(), SetDefaultFont(), GetDefaultFontSize(), SetDefaultFontSize()
        + Advanced: GetLinkedFilesRootDir(), SetLinkedFilesRootDir(), GetExtLinkRootDir()
        + Metadata: GetDateCreated(), GetDateModified()
    + **PublicationOperations** - Publication management (26 methods)
        + Core: GetAll(), Create(), Delete(), Find(), Exists()
        + Properties: GetName(), SetName(), GetDescription(), SetDescription()
        + Publishing: GetPageLayout(), SetPageLayout(), GetIsDefault(), SetIsDefault()
        + Formatting: GetPageHeight(), SetPageHeight(), GetPageWidth(), SetPageWidth()
        + Structure: GetDivisions(), AddDivision(), GetHeaderFooter(), GetSubPublications(), GetParent()
        + Metadata: GetGuid(), GetDateCreated(), GetDateModified()
    + **AgentOperations** - Analysis agent tracking (26 methods)
        + Core: GetAll(), Create(), CreateHumanAgent(), CreateParserAgent(), Delete(), Exists(), Find()
        + Properties: GetName(), SetName(), GetVersion(), SetVersion()
        + Type: IsHuman(), IsParser()
        + Person: GetHuman(), SetHuman()
        + Evaluations: GetEvaluations(), GetEvaluationCount()
        + Queries: FindByType(), GetHumanAgents(), GetParserAgents()
        + Metadata: GetGuid(), GetDateCreated(), GetDateModified()
    + **ConfidenceOperations** - Confidence levels (14 methods)
        + Core: GetAll(), Create(), Delete(), Find(), Exists()
        + Properties: GetName(), SetName(), GetDescription(), SetDescription()
        + Usage: GetAnalysesWithConfidence(), GetGlossesWithConfidence()
        + Queries: GetDefault()
        + Metadata: GetGuid()
    + **OverlayOperations** - Discourse overlays (20 methods)
        + Core: GetAll(), Create(), Delete(), Find()
        + Properties: GetName(), SetName(), GetDescription(), SetDescription()
        + Visibility: IsVisible(), SetVisible(), GetDisplayOrder(), SetDisplayOrder()
        + Elements: GetElements(), AddElement(), RemoveElement()
        + Chart: GetChart(), GetPossItems()
        + Queries: FindByChart(), GetVisibleOverlays()
        + Metadata: GetGuid()
    + **TranslationTypeOperations** - Translation type management (20 methods)
        + Core: GetAll(), Create(), Delete(), Find(), Exists()
        + Properties: GetName(), SetName(), GetAbbreviation(), SetAbbreviation()
        + Writing System: GetAnalysisWS(), SetAnalysisWS()
        + Usage: GetTextsWithType(), GetSegmentsWithType()
        + Predefined: GetFreeTranslationType(), GetLiteralTranslationType(), GetBackTranslationType()
        + Queries: FindByWS(), IsDefault(), SetDefault()
        + Metadata: GetGuid()
    + **AnnotationDefOperations** - Annotation definitions (16 methods)
        + Core: GetAll(), Create(), Delete(), Find(), Exists()
        + Properties: GetName(), SetName(), GetHelpString(), SetHelpString()
        + Type: GetAnnotationType(), GetInstanceOf()
        + Control: GetUserCanCreate(), SetUserCanCreate(), GetMultiple(), SetMultiple()
        + Prompts: GetPrompt(), SetPrompt(), GetCopyCutPasteAllowed()
        + Queries: FindByType(), GetUserCreatableTypes()
        + Metadata: GetGuid(), GetDateCreated()
    + **CheckOperations** - Consistency checking (25 methods)
        + Core: GetAllCheckTypes(), CreateCheckType(), DeleteCheckType(), FindCheckType()
        + Properties: GetName(), SetName(), GetDescription(), SetDescription()
        + Execution: RunCheck(), GetCheckStatus(), GetLastRun()
        + Results: GetCheckResults(), GetErrorCount(), GetWarningCount()
        + Filters: GetEnabledChecks(), EnableCheck(), DisableCheck(), IsEnabled()
        + Queries: FindItemsWithIssues(), GetIssuesForObject()
        + Metadata: GetGuid()


+ **Phase 14: Data Notebook** (42 methods)
    + **DataNotebookOperations** - Research notebook records (42 methods)
        + Core: GetAll(), Create(), Delete(), Exists(), Find()
        + Properties: GetTitle(), SetTitle(), GetContent(), SetContent()
        + Type: GetRecordType(), SetRecordType(), GetAllRecordTypes(), FindRecordTypeByName()
        + Date/Time: GetDateCreated(), GetDateModified(), GetDateOfEvent(), SetDateOfEvent()
        + Hierarchy: GetSubRecords(), CreateSubRecord(), GetParentRecord()
        + Researchers: GetResearchers(), AddResearcher(), RemoveResearcher()
        + Participants: GetParticipants(), AddParticipant(), RemoveParticipant()
        + Text Links: GetTexts(), LinkToText(), UnlinkFromText()
        + Media: GetMediaFiles(), AddMediaFile(), RemoveMediaFile()
        + Status: GetStatus(), SetStatus(), GetAllStatuses(), FindStatusByName()
        + Queries: FindByDate(), FindByResearcher(), FindByType()
        + Metadata: GetGuid(), GetConfidence(), SetConfidence()

