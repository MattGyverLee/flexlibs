flexlibs
========

flexlibs is a library for accessing FieldWorks Language Explorer 
(FLEx) [1]_ projects.

flexlibs handles the necessary initialisation of the FLEx engine, and 
provides a class (FLExProject) for opening a FLEx project and working 
with its contents.

For the GUI application that runs Python scripts/plugins
on FLEx databases see FLExTools [2]_, which is built on flexlibs.


Requirements
------------

Python 3.8 - 3.13.

Python for .NET [3]_ version 3.0.3+.

FieldWorks Language Explorer 9.0.17 - 9.3.1.


32-bit vs 64-bit
^^^^^^^^^^^^^^^^
The Python architecture must match that of FieldWorks. I.e. Install 
32-bit Python for 32-bit Fieldworks, and 64-bit Python for 64-bit 
Fieldworks.

Installation
------------
Run:
``pip install flexlibs``

Usage
-----

.. code-block:: python


  import flexlibs
  flexlibs.FLExInitialize()
  p = flexlibs.FLExProject()
  p.OpenProject('parser-experiments')
  p.GetPartsOfSpeech()
  # ['Adverb', 'Noun', 'Pro-form', 'Pronoun', 'Verb', 'Copulative verb', 'Ditransitive verb', 'Intransitive verb', 'Transitive verb', 'Coordinating connective']

  # The API documentation is an HTML file
  os.startfile(flexlibs.APIHelpFile)
  ...
  p.CloseProject()
  flexlibs.FLExCleanup()


Advanced Operations (v2.0+)
----------------------------

flexlibs 2.0 introduces comprehensive CRUD operations for FLEx data through
specialized operation classes:

.. code-block:: python

  import flexlibs

  flexlibs.FLExInitialize()
  project = flexlibs.FLExProject()
  project.OpenProject('my-project', writeEnabled=True)

  # Parts of Speech operations
  for pos in project.POS.GetAll():
      name = project.POS.GetName(pos)
      abbr = project.POS.GetAbbreviation(pos)
      print(f"{name} ({abbr})")

  # Create new POS
  noun = project.POS.Create("Noun", "N")

  # Text operations
  text = project.Texts.Create("Genesis")
  project.Texts.SetName(text, "Genesis Chapter 1")

  # Wordform operations
  wf = project.Wordforms.Create("running")
  project.Wordforms.SetSpellingStatus(wf, flexlibs.SpellingStatusStates.CORRECT)

  # Get wordform analyses
  for analysis in project.Wordforms.GetAnalyses(wf):
      print(f"Analysis: {analysis}")

  project.CloseProject()
  flexlibs.FLExCleanup()

**Available Operations:**

**Phase 1: Core CRUD Operations** (28 methods)

- **project.POS** - Parts of Speech management (10 methods)

  - GetAll, Create, Delete, Exists, Find
  - GetName, SetName, GetAbbreviation, SetAbbreviation
  - GetSubcategories

- **project.Texts** - Text corpus management (14 methods)

  - Core: Create, Delete, Exists, GetAll, GetName, SetName, GetGenre, SetGenre
  - Advanced: GetContents, GetParagraphs, GetParagraphCount, GetMediaFiles, AddMediaFile, GetAbbreviation

- **project.Wordforms** - Wordform management (10 methods)

  - GetAll, Create, Delete, Exists, Find
  - GetForm, SetForm
  - GetSpellingStatus, SetSpellingStatus
  - GetAnalyses

**Phase 2: Interlinear Text Operations** (28 methods)

- **project.Paragraphs** - Paragraph management (13 methods)

  - Core: Create, Delete, GetAll, GetText, SetText, GetSegments, GetSegmentCount, InsertAt
  - Advanced: GetTranslations, SetTranslation, GetNotes, AddNote, GetStyleName

- **project.Segments** - Segment operations (9 methods)

  - GetAll, GetAnalyses
  - GetBaselineText, SetBaselineText
  - GetFreeTranslation, SetFreeTranslation
  - GetLiteralTranslation, SetLiteralTranslation
  - GetNotes

**Phase 3: Phonology Operations** (32 methods)

- **project.Phonemes** - Phoneme management (16 methods)

  - Core: GetAll, Create, Delete, Exists, Find
  - Properties: GetRepresentation, SetRepresentation, GetDescription, SetDescription
  - Advanced: GetCodes, AddCode, RemoveCode, IsVowel, IsConsonant, GetFeatures, SetFeatures

- **project.NaturalClasses** - Natural class management (9 methods)

  - Core: GetAll, Create, Delete, Exists, Find
  - Properties: GetName, SetName
  - Phonemes: GetPhonemes, AddPhoneme, RemovePhoneme

- **project.Environments** - Phonological environments (7 methods)

  - Core: GetAll, Create, Delete, Exists
  - Properties: GetName, SetName, GetStringRepresentation

**Phase 4: Morphology & Grammar Operations** (46 methods)

- **project.Allomorphs** - Allomorph management (10 methods)

  - Core: GetAll, Create, Delete, Exists
  - Properties: GetForm, SetForm, GetMorphType, SetMorphType
  - Environment: GetPhoneEnv, AddPhoneEnv

- **project.MorphRules** - Morphological rules (11 methods)

  - Core: GetAll, Create, Delete, Exists, Find
  - Properties: GetName, SetName, GetDescription, SetDescription
  - Control: IsActive, SetActive, GetStratum

- **project.InflectionFeatures** - Inflection features (12 methods)

  - Classes: GetAllClasses, CreateClass, DeleteClass, GetClassName, SetClassName
  - Structures: GetAllStructures, CreateStructure, DeleteStructure
  - Features: GetAllFeatures, CreateFeature, GetFeatureName, SetFeatureName

- **project.POS** - Extended POS operations (16 methods total, 6 new)

  - Advanced: GetInflectionClasses, AddInflectionClass, GetAffixSlots, AddAffixSlot, GetDefaultFeatures, SetDefaultFeatures

- **project.GramCat** - Grammatical categories (7 methods)

  - Core: GetAll, Create, Delete, Exists
  - Properties: GetName, SetName
  - Hierarchy: GetSubcategories, GetParent

**Phase 5: Wordform Advanced Operations** (6 new methods)

- **project.Wordforms** - Extended wordform operations (16 methods total, 6 new)

  - Advanced: GetOccurrenceCount, GetAllUnapproved, ApproveSpelling, GetChecksum, FindByForm, GetAnalysisGlosses

**Phase 6: Phonological Rule Components** (18 methods)

- **project.PhonRules** - Phonological rule management with components (18 methods)

  - Core: GetAll, Create, Delete, Exists, Find
  - Properties: GetName, SetName, GetDescription, SetDescription
  - Control: GetStratum, SetStratum, GetDirection, SetDirection
  - Components: AddInputSegment, AddOutputSegment, SetLeftContext, SetRightContext

**Phase 7: Lexicon Core Operations** (71 methods)

- **project.LexEntry** - Lexical entry management (23 methods)

  - Core: GetAll, Create, Delete, Exists, Find
  - Headword: GetHeadword, SetHeadword, GetLexemeForm, SetLexemeForm
  - Citation: GetCitationForm, SetCitationForm
  - Properties: GetHomographNumber, SetHomographNumber, GetDateCreated, GetDateModified
  - Morph Type: GetMorphType, SetMorphType
  - Senses: GetSenses, GetSenseCount, AddSense
  - Additional: GetGuid, GetImportResidue, SetImportResidue

- **project.Senses** - Lexical sense management (31 methods)

  - Core: GetAll, Create, Delete, Reorder
  - Gloss & Definition: GetGloss, SetGloss, GetDefinition, SetDefinition
  - Grammatical: GetPartOfSpeech, SetPartOfSpeech, GetGrammaticalInfo, SetGrammaticalInfo
  - Semantic Domains: GetSemanticDomains, AddSemanticDomain, RemoveSemanticDomain
  - Examples: GetExamples, GetExampleCount, AddExample
  - Subsenses: GetSubsenses, CreateSubsense, GetParentSense
  - Status: GetStatus, SetStatus, GetSenseType, SetSenseType
  - Reversal: GetReversalEntries, GetReversalCount
  - Pictures: GetPictures, GetPictureCount
  - Additional: GetGuid, GetOwningEntry, GetSenseNumber, GetAnalysesCount

- **project.Examples** - Example sentence management (17 methods)

  - Core: GetAll, Create, Delete, Reorder
  - Text: GetExample, SetExample
  - Translations: GetTranslations, GetTranslation, SetTranslation, AddTranslation, RemoveTranslation
  - Reference: GetReference, SetReference
  - Media: GetMediaFiles, GetMediaCount
  - Additional: GetOwningSense, GetGuid

**Phase 8: Advanced Lexicon Operations** (102 methods)

- **project.LexReferences** - Cross-references and lexical relations (26 methods)

  - Type Management: GetAllTypes, CreateType, DeleteType, FindType, GetTypeName, SetTypeName, GetTypeReverseName, SetTypeReverseName, GetMappingType
  - Reference Management: GetAll, Create, Delete, GetTargets, AddTarget, RemoveTarget, GetType, GetReferencesOfType
  - Complex Forms: ShowComplexFormsIn, GetComplexFormEntries, GetComponentEntries

- **project.Variants** - Variant form management (16 methods)

  - Type Management: GetAllTypes, FindType, GetTypeName, GetTypeDescription
  - Variant Management: GetAll, Create, Delete, GetForm, SetForm, GetType, SetType
  - Components: GetComponentLexemes, AddComponentLexeme, RemoveComponentLexeme
  - Utilities: GetOwningEntry, GetVariantCount

- **project.Pronunciations** - Pronunciation with IPA/audio (14 methods)

  - Core: GetAll, Create, Delete, Reorder
  - Form: GetForm, SetForm
  - Media: GetMediaFiles, GetMediaCount, AddMediaFile, RemoveMediaFile
  - Location: GetLocation, SetLocation
  - Utilities: GetOwningEntry, GetGuid

- **project.SemanticDomains** - Semantic domain management (19 methods)

  - Core: GetAll, Find, FindByName, Exists
  - Properties: GetName, SetName, GetDescription, SetDescription, GetAbbreviation, GetNumber, GetQuestions, GetOcmCodes
  - Hierarchy: GetSubdomains, GetParent, GetDepth
  - Usage: GetSensesInDomain, GetSenseCount
  - Custom: Create, Delete

- **project.Reversal** - Reversal entry CRUD (18 methods)

  - Index: GetAllIndexes, GetIndex, FindIndex
  - Entry CRUD: GetAll, Create, Delete, Find, Exists
  - Form: GetForm, SetForm
  - Sense Linking: GetSenses, AddSense, RemoveSense, GetSenseCount
  - Subentries: GetSubentries, CreateSubentry, GetParentEntry
  - POS: GetPartsOfSpeech

- **project.Etymology** - Etymology tracking (16 methods)

  - Core: GetAll, Create, Delete, Reorder
  - Source: GetSource, SetSource
  - Form & Gloss: GetForm, SetForm, GetGloss, SetGloss
  - Comment & Bibliography: GetComment, SetComment, GetBibliography, SetBibliography
  - Utilities: GetOwningEntry, GetGuid

**Phase 9: Interlinear Analysis Operations** (54 methods)

- **project.WfiAnalyses** - Wordform analysis management (21 methods)

  - Core: GetAll, Create, Delete, Exists
  - Status: ApproveAnalysis, DisapproveAnalysis, GetApprovalStatus, SetApprovalStatus
  - Components: GetGlosses, GetGlossCount, GetMorphBundles, GetMorphBundleCount
  - Properties: GetCategory, SetCategory, GetAgent, SetAgent
  - Navigation: GetWordform, GetAnalysesForWordform
  - Queries: GetUnapprovedAnalyses, GetApprovedAnalyses, GetHumanApprovedAnalyses
  - Utilities: CopyAnalysis, GetGuid

- **project.WfiGlosses** - Wordform gloss management (15 methods)

  - Core: GetAll, Create, Delete, Exists
  - Form: GetForm, SetForm, GetAllForms
  - Navigation: GetAnalysis, GetWordform
  - Queries: GetGlossesForForm, FindByForm
  - Utilities: CopyGloss, GetGuid

- **project.WfiMorphBundles** - Morpheme bundle management (18 methods)

  - Core: GetAll, Create, Delete, Exists
  - Form: GetForm, SetForm
  - Sense Linking: GetSense, SetSense, GetEntry
  - Morphology: GetMorphType, SetMorphType, GetMSA, SetMSA
  - Navigation: GetAnalysis, GetWordform, GetPosition, SetPosition
  - Utilities: GetGuid

**Phase 10: System Configuration Operations** (24 methods)

- **project.Media** - Media file management (24 methods)

  - Core: GetAll, Create, Delete, Exists, Find
  - File Operations: GetFilename, SetFilename, GetFilePath, CopyToProject
  - Properties: GetMediaType, GetDescription, SetDescription, GetLabel, SetLabel
  - Internal Path: GetInternalPath, SetInternalPath
  - Folder Management: GetFolder, SetFolder, GetFolderName
  - Queries: GetOrphanedMedia, FindByFilename, FindByPath
  - Utilities: GetGuid, IsOrphaned

**Phase 11: Advanced Features** (85 methods)

- **project.PossibilityLists** - Generic possibility list management (24 methods)

  - List Management: GetAllLists, FindList, CreateList, DeleteList, GetListName, GetListOwner
  - Item Management: GetItems, CreateItem, DeleteItem, GetItemName, SetItemName
  - Hierarchy: GetParent, GetChildren, GetDepth, MoveItem, ReorderItem
  - Navigation: FindItem, FindByGuid, GetAbbreviation, SetAbbreviation
  - Queries: GetAllItemsFlat, GetItemCount
  - Utilities: GetGuid

- **project.Notes** - Note and annotation management (16 methods)

  - Core: GetAll, Create, Delete, Exists
  - Content: GetContent, SetContent, GetPlainText
  - Threading: AddReply, GetReplies, GetReplyCount, GetParentNote
  - Properties: GetNoteType, SetNoteType, GetAuthor, GetDateCreated
  - Utilities: GetAnnotatedObject

- **project.Segments** - Enhanced segment operations (21 methods total, 12 new)

  - NEW Core: Create, Delete
  - NEW Advanced: SplitSegment, MergeSegments, GetWordforms, GetWordformCount
  - NEW Validation: ValidateSegments, RebuildSegments, GetInvalidSegments
  - NEW Queries: FindSegmentsByText, GetSegmentIndex
  - Existing: GetAll, GetAnalyses, GetBaselineText, SetBaselineText, GetFreeTranslation, SetFreeTranslation, GetLiteralTranslation, SetLiteralTranslation, GetNotes

- **project.Filters** - Filter and query management (18 methods)

  - Core: GetAll, Create, Delete, Exists, Find
  - Filter Operations: ApplyFilter, GetFilterResults, ClearFilterCache
  - Properties: GetName, SetName, GetDescription, SetDescription
  - Definition: GetFilterDefinition, SetFilterDefinition
  - Import/Export: ExportFilter, ImportFilter, GetFilterJSON
  - Utilities: ValidateFilter, GetGuid

- **project.Discourse** - Discourse chart management (15 methods)

  - Chart Management: GetAllCharts, CreateChart, DeleteChart, GetChartName, SetChartName
  - Row Operations: GetRows, AddRow, DeleteRow, GetRowCount
  - Cell Operations: GetCellContent, SetCellContent, ClearCell
  - Template: GetChartTemplate, SetChartTemplate
  - Utilities: GetText

**Phase 12: Anthropology & Cultural Data** (92 methods)

- **project.Person** - People management for consultants, speakers, researchers (30 methods)

  - Core: GetAll, Create, Delete, Exists, Find
  - Name: GetName, SetName
  - Personal Info: GetGender, SetGender, GetDateOfBirth, SetDateOfBirth
  - Contact: GetEmail, SetEmail, GetPhone, SetPhone, GetAddress, SetAddress
  - Academic: GetEducation, SetEducation, GetPositions, AddPosition
  - Relationships: GetResidences, AddResidence, GetLanguages, AddLanguage
  - Notes: GetNotes, AddNote
  - Metadata: GetGuid, GetDateCreated, GetDateModified

- **project.Location** - Geographic location management (28 methods)

  - Core: GetAll, Create, Delete, Exists, Find
  - Name & Alias: GetName, SetName, GetAlias, SetAlias
  - Geographic: GetCoordinates, SetCoordinates, GetElevation, SetElevation
  - Description: GetDescription, SetDescription
  - Hierarchy: GetRegion, SetRegion, GetSublocations, CreateSublocation
  - Metadata: GetGuid, GetDateCreated, GetDateModified
  - Queries: FindByCoordinates, GetNearby

- **project.Anthropology** - Cultural/ethnographic data management (34 methods)

  - Core: GetAll, Create, CreateSubitem, Delete, Exists, Find
  - Properties: GetName, SetName, GetAbbreviation, SetAbbreviation
  - Description: GetDescription, SetDescription
  - Categories: GetAnthroCode, SetAnthroCode, GetCategory, SetCategory
  - Hierarchy: GetSubitems, GetParent
  - Queries: FindByCode, FindByCategory, GetItemsForText
  - Text Linking: GetTexts, AddText, RemoveText, GetTextCount
  - Researchers: GetResearchers, AddResearcher, RemoveResearcher
  - Metadata: GetGuid, GetDateCreated, GetDateModified

**Phase 13: Project Configuration & Specialized Metadata** (165 methods)

- **project.ProjectSettings** - Project configuration (18 methods)

  - Project Info: GetProjectName, SetProjectName, GetDescription, SetDescription
  - Language Settings: GetVernacularWSs, GetAnalysisWSs, SetDefaultVernacular, SetDefaultAnalysis
  - UI Settings: GetInterfaceLanguage, SetInterfaceLanguage
  - Default Fonts: GetDefaultFont, SetDefaultFont, GetDefaultFontSize, SetDefaultFontSize
  - Advanced: GetLinkedFilesRootDir, SetLinkedFilesRootDir, GetExtLinkRootDir
  - Metadata: GetDateCreated, GetDateModified

- **project.Publications** - Publication management (26 methods)

  - Core: GetAll, Create, Delete, Find, Exists
  - Properties: GetName, SetName, GetDescription, SetDescription
  - Publishing: GetPageLayout, SetPageLayout, GetIsDefault, SetIsDefault
  - Formatting: GetPageHeight, SetPageHeight, GetPageWidth, SetPageWidth
  - Structure: GetDivisions, AddDivision, GetHeaderFooter, GetSubPublications, GetParent
  - Metadata: GetGuid, GetDateCreated, GetDateModified

- **project.Agents** - Analysis agent tracking (26 methods)

  - Core: GetAll, Create, CreateHumanAgent, CreateParserAgent, Delete, Exists, Find
  - Properties: GetName, SetName, GetVersion, SetVersion
  - Type: IsHuman, IsParser
  - Person: GetHuman, SetHuman
  - Evaluations: GetEvaluations, GetEvaluationCount
  - Queries: FindByType, GetHumanAgents, GetParserAgents
  - Metadata: GetGuid, GetDateCreated, GetDateModified

- **project.Confidence** - Confidence levels (14 methods)

  - Core: GetAll, Create, Delete, Find, Exists
  - Properties: GetName, SetName, GetDescription, SetDescription
  - Usage: GetAnalysesWithConfidence, GetGlossesWithConfidence
  - Queries: GetDefault
  - Metadata: GetGuid

- **project.Overlays** - Discourse overlays (20 methods)

  - Core: GetAll, Create, Delete, Find
  - Properties: GetName, SetName, GetDescription, SetDescription
  - Visibility: IsVisible, SetVisible, GetDisplayOrder, SetDisplayOrder
  - Elements: GetElements, AddElement, RemoveElement
  - Chart: GetChart, GetPossItems
  - Queries: FindByChart, GetVisibleOverlays
  - Metadata: GetGuid

- **project.TranslationTypes** - Translation type management (20 methods)

  - Core: GetAll, Create, Delete, Find, Exists
  - Properties: GetName, SetName, GetAbbreviation, SetAbbreviation
  - Writing System: GetAnalysisWS, SetAnalysisWS
  - Usage: GetTextsWithType, GetSegmentsWithType
  - Predefined: GetFreeTranslationType, GetLiteralTranslationType, GetBackTranslationType
  - Queries: FindByWS, IsDefault, SetDefault
  - Metadata: GetGuid

- **project.AnnotationDefs** - Annotation definitions (16 methods)

  - Core: GetAll, Create, Delete, Find, Exists
  - Properties: GetName, SetName, GetHelpString, SetHelpString
  - Type: GetAnnotationType, GetInstanceOf
  - Control: GetUserCanCreate, SetUserCanCreate, GetMultiple, SetMultiple
  - Prompts: GetPrompt, SetPrompt, GetCopyCutPasteAllowed
  - Queries: FindByType, GetUserCreatableTypes
  - Metadata: GetGuid, GetDateCreated

- **project.Checks** - Consistency checking (25 methods)

  - Core: GetAllCheckTypes, CreateCheckType, DeleteCheckType, FindCheckType
  - Properties: GetName, SetName, GetDescription, SetDescription
  - Execution: RunCheck, GetCheckStatus, GetLastRun
  - Results: GetCheckResults, GetErrorCount, GetWarningCount
  - Filters: GetEnabledChecks, EnableCheck, DisableCheck, IsEnabled
  - Queries: FindItemsWithIssues, GetIssuesForObject
  - Metadata: GetGuid

**Phase 14: Data Notebook** (42 methods)

- **project.DataNotebook** - Research notebook records (42 methods)

  - Core: GetAll, Create, Delete, Exists, Find
  - Properties: GetTitle, SetTitle, GetContent, SetContent
  - Type: GetRecordType, SetRecordType, GetAllRecordTypes, FindRecordTypeByName
  - Date/Time: GetDateCreated, GetDateModified, GetDateOfEvent, SetDateOfEvent
  - Hierarchy: GetSubRecords, CreateSubRecord, GetParentRecord
  - Researchers: GetResearchers, AddResearcher, RemoveResearcher
  - Participants: GetParticipants, AddParticipant, RemoveParticipant
  - Text Links: GetTexts, LinkToText, UnlinkFromText
  - Media: GetMediaFiles, AddMediaFile, RemoveMediaFile
  - Status: GetStatus, SetStatus, GetAllStatuses, FindStatusByName
  - Queries: FindByDate, FindByResearcher, FindByType
  - Metadata: GetGuid, GetConfidence, SetConfidence

**Total: 793 methods** across 43 operation classes

See the examples directory for detailed usage demonstrations.

--------------

.. [1] https://software.sil.org/fieldworks/
.. [2] https://github.com/cdfarrow/flextools/wiki/
.. [3] https://github.com/pythonnet/pythonnet/wiki
