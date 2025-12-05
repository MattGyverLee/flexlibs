#----------------------------------------------------------------------------
# Name:         flexlibs
# Purpose:      This package provides a Python interface to FLEx project data 
#               via the Fieldworks Language and Culture Model (LCM).
#----------------------------------------------------------------------------

version = "2.0.0"

# Define exported classes, etc. at the top level of the package

from .code.FLExInit import (
    FLExInitialize, 
    FLExCleanup,
    )
    
from .code.FLExGlobals import (
    FWCodeDir, 
    FWProjectsDir, 
    FWExecutable,
    FWShortVersion, 
    FWLongVersion,
    APIHelpFile,
    )

from .code.FLExProject import (
    AllProjectNames,
    OpenProjectInFW,
    FLExProject,
    FP_FileLockedError,
    FP_FileNotFoundError,
    FP_MigrationRequired,
    FP_NullParameterError,
    FP_ParameterError,
    FP_ProjectError,
    FP_ReadOnlyError,
    FP_RuntimeError,
    FP_WritingSystemError,
    )

# Advanced Operations (v2.0+)

# Grammar Operations
from .code.Grammar.POSOperations import (
    POSOperations,
    )

from .code.Grammar.PhonemeOperations import (
    PhonemeOperations,
    )

from .code.Grammar.NaturalClassOperations import (
    NaturalClassOperations,
    )

from .code.Grammar.EnvironmentOperations import (
    EnvironmentOperations,
    )

from .code.Grammar.MorphRuleOperations import (
    MorphRuleOperations,
    )

from .code.Grammar.InflectionFeatureOperations import (
    InflectionFeatureOperations,
    )

from .code.Grammar.GramCatOperations import (
    GramCatOperations,
    )

from .code.Grammar.PhonologicalRuleOperations import (
    PhonologicalRuleOperations,
    )

# Lexicon Operations
from .code.Lexicon.LexEntryOperations import (
    LexEntryOperations,
    )

from .code.Lexicon.LexSenseOperations import (
    LexSenseOperations,
    )

from .code.Lexicon.ExampleOperations import (
    ExampleOperations,
    )

from .code.Lexicon.LexReferenceOperations import (
    LexReferenceOperations,
    )

from .code.Lexicon.VariantOperations import (
    VariantOperations,
    )

from .code.Lexicon.PronunciationOperations import (
    PronunciationOperations,
    )

from .code.Lexicon.SemanticDomainOperations import (
    SemanticDomainOperations,
    )

from .code.Lexicon.ReversalOperations import (
    ReversalOperations,
    )

from .code.Lexicon.EtymologyOperations import (
    EtymologyOperations,
    )

from .code.Lexicon.AllomorphOperations import (
    AllomorphOperations,
    )

# TextsWords Operations
from .code.TextsWords.TextOperations import (
    TextOperations,
    )

from .code.TextsWords.WordformOperations import (
    WordformOperations,
    SpellingStatusStates,
    )

from .code.TextsWords.WfiAnalysisOperations import (
    WfiAnalysisOperations,
    ApprovalStatusTypes,
    )

from .code.TextsWords.ParagraphOperations import (
    ParagraphOperations,
    )

from .code.TextsWords.SegmentOperations import (
    SegmentOperations,
    )

from .code.TextsWords.WfiGlossOperations import (
    WfiGlossOperations,
    )

from .code.TextsWords.WfiMorphBundleOperations import (
    WfiMorphBundleOperations,
    )

from .code.Shared.MediaOperations import (
    MediaOperations,
    MediaType,
    )

from .code.Shared.FilterOperations import (
    FilterOperations,
    )

from .code.TextsWords.DiscourseOperations import (
    DiscourseOperations,
    )

# Notebook Operations
from .code.Notebook.NoteOperations import (
    NoteOperations,
    )

from .code.Notebook.PersonOperations import (
    PersonOperations,
    )

from .code.Notebook.LocationOperations import (
    LocationOperations,
    )

from .code.Notebook.AnthropologyOperations import (
    AnthropologyOperations,
    )

from .code.Notebook.DataNotebookOperations import (
    DataNotebookOperations,
    )

# Lists Operations
from .code.Lists.PublicationOperations import (
    PublicationOperations,
    )

from .code.Lists.AgentOperations import (
    AgentOperations,
    )

from .code.Lists.ConfidenceOperations import (
    ConfidenceOperations,
    )

from .code.Lists.OverlayOperations import (
    OverlayOperations,
    )

from .code.Lists.TranslationTypeOperations import (
    TranslationTypeOperations,
    )

from .code.Lists.PossibilityListOperations import (
    PossibilityListOperations,
    )

# System Operations
from .code.System.WritingSystemOperations import (
    WritingSystemOperations,
    )

from .code.System.ProjectSettingsOperations import (
    ProjectSettingsOperations,
    )

from .code.System.AnnotationDefOperations import (
    AnnotationDefOperations,
    )

from .code.System.CheckOperations import (
    CheckOperations,
    )

from .code.System.CustomFieldOperations import (
    CustomFieldOperations,
    )
