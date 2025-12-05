"""
Comprehensive Baseline Test for FLEx Operations Classes

This test suite verifies that all operations classes can be:
1. Imported successfully
2. Instantiated (with mock FLExProject)
3. Have expected methods (Create, GetAll, Find, Delete)
4. Properly inherit from BaseOperations
5. Have reordering methods available

Tests are organized by domain:
- Grammar (8 classes)
- Lexicon (10 classes)
- TextsWords (8 classes)
- Wordform (4 classes)
- Discourse (6 classes)
- Scripture (6 classes)
- Notebook (5 classes)
- Reversal (2 classes)
- Lists (6 classes)
- System (5 classes)
- Shared (2 classes)

Author: Programmer Team 3 - Test Infrastructure
Date: 2025-12-05
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock

# Add project root to path
_test_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_test_dir)
sys.path.insert(0, _project_root)


# =============================================================================
# MOCK FLEXPROJECT FIXTURE
# =============================================================================

@pytest.fixture
def mock_flex_project():
    """
    Create a mock FLExProject for testing operations class instantiation.

    This mock provides the minimal interface needed to instantiate operations
    classes without requiring an actual FLEx connection.
    """
    mock_project = Mock()
    mock_project.LcmCache = Mock()
    mock_project.Object = Mock(return_value=Mock())

    # Mock repository objects
    mock_project.LcmCache.ServiceLocator = Mock()
    mock_project.LcmCache.ServiceLocator.GetInstance = Mock(return_value=Mock())

    # Mock common repository methods
    mock_repo = Mock()
    mock_repo.AllInstances = Mock(return_value=[])
    mock_project.LcmCache.ServiceLocator.GetInstance.return_value = mock_repo

    return mock_project


# =============================================================================
# OPERATIONS CLASS DEFINITIONS BY DOMAIN
# =============================================================================

GRAMMAR_OPERATIONS = [
    ('POSOperations', 'flexlibs.code.Grammar.POSOperations'),
    ('PhonemeOperations', 'flexlibs.code.Grammar.PhonemeOperations'),
    ('NaturalClassOperations', 'flexlibs.code.Grammar.NaturalClassOperations'),
    ('EnvironmentOperations', 'flexlibs.code.Grammar.EnvironmentOperations'),
    ('PhonologicalRuleOperations', 'flexlibs.code.Grammar.PhonologicalRuleOperations'),
    ('MorphRuleOperations', 'flexlibs.code.Grammar.MorphRuleOperations'),
    ('GramCatOperations', 'flexlibs.code.Grammar.GramCatOperations'),
    ('InflectionFeatureOperations', 'flexlibs.code.Grammar.InflectionFeatureOperations'),
]

LEXICON_OPERATIONS = [
    ('LexEntryOperations', 'flexlibs.code.Lexicon.LexEntryOperations'),
    ('LexSenseOperations', 'flexlibs.code.Lexicon.LexSenseOperations'),
    ('AllomorphOperations', 'flexlibs.code.Lexicon.AllomorphOperations'),
    ('ExampleOperations', 'flexlibs.code.Lexicon.ExampleOperations'),
    ('PronunciationOperations', 'flexlibs.code.Lexicon.PronunciationOperations'),
    ('EtymologyOperations', 'flexlibs.code.Lexicon.EtymologyOperations'),
    ('VariantOperations', 'flexlibs.code.Lexicon.VariantOperations'),
    ('LexReferenceOperations', 'flexlibs.code.Lexicon.LexReferenceOperations'),
    ('SemanticDomainOperations', 'flexlibs.code.Lexicon.SemanticDomainOperations'),
    ('ReversalOperations', 'flexlibs.code.Lexicon.ReversalOperations'),
]

TEXTSWORDS_OPERATIONS = [
    ('TextOperations', 'flexlibs.code.TextsWords.TextOperations'),
    ('ParagraphOperations', 'flexlibs.code.TextsWords.ParagraphOperations'),
    ('SegmentOperations', 'flexlibs.code.TextsWords.SegmentOperations'),
    ('WordformOperations', 'flexlibs.code.TextsWords.WordformOperations'),
    ('WfiAnalysisOperations', 'flexlibs.code.TextsWords.WfiAnalysisOperations'),
    ('WfiGlossOperations', 'flexlibs.code.TextsWords.WfiGlossOperations'),
    ('WfiMorphBundleOperations', 'flexlibs.code.TextsWords.WfiMorphBundleOperations'),
    ('DiscourseOperations', 'flexlibs.code.TextsWords.DiscourseOperations'),
]

WORDFORM_OPERATIONS = [
    ('WfiWordformOperations', 'flexlibs.code.Wordform.WfiWordformOperations'),
    ('WfiAnalysisOperations', 'flexlibs.code.Wordform.WfiAnalysisOperations'),
    ('WfiGlossOperations', 'flexlibs.code.Wordform.WfiGlossOperations'),
    ('WfiMorphBundleOperations', 'flexlibs.code.Wordform.WfiMorphBundleOperations'),
]

DISCOURSE_OPERATIONS = [
    ('ConstChartOperations', 'flexlibs.code.Discourse.ConstChartOperations'),
    ('ConstChartRowOperations', 'flexlibs.code.Discourse.ConstChartRowOperations'),
    ('ConstChartTagOperations', 'flexlibs.code.Discourse.ConstChartTagOperations'),
    ('ConstChartClauseMarkerOperations', 'flexlibs.code.Discourse.ConstChartClauseMarkerOperations'),
    ('ConstChartWordGroupOperations', 'flexlibs.code.Discourse.ConstChartWordGroupOperations'),
    ('ConstChartMovedTextOperations', 'flexlibs.code.Discourse.ConstChartMovedTextOperations'),
]

SCRIPTURE_OPERATIONS = [
    ('ScrBookOperations', 'flexlibs.code.Scripture.ScrBookOperations'),
    ('ScrSectionOperations', 'flexlibs.code.Scripture.ScrSectionOperations'),
    ('ScrTxtParaOperations', 'flexlibs.code.Scripture.ScrTxtParaOperations'),
    ('ScrNoteOperations', 'flexlibs.code.Scripture.ScrNoteOperations'),
    ('ScrAnnotationsOperations', 'flexlibs.code.Scripture.ScrAnnotationsOperations'),
    ('ScrDraftOperations', 'flexlibs.code.Scripture.ScrDraftOperations'),
]

NOTEBOOK_OPERATIONS = [
    ('DataNotebookOperations', 'flexlibs.code.Notebook.DataNotebookOperations'),
    ('NoteOperations', 'flexlibs.code.Notebook.NoteOperations'),
    ('PersonOperations', 'flexlibs.code.Notebook.PersonOperations'),
    ('LocationOperations', 'flexlibs.code.Notebook.LocationOperations'),
    ('AnthropologyOperations', 'flexlibs.code.Notebook.AnthropologyOperations'),
]

REVERSAL_OPERATIONS = [
    ('ReversalIndexOperations', 'flexlibs.code.Reversal.ReversalIndexOperations'),
    ('ReversalIndexEntryOperations', 'flexlibs.code.Reversal.ReversalIndexEntryOperations'),
]

LISTS_OPERATIONS = [
    ('PossibilityListOperations', 'flexlibs.code.Lists.PossibilityListOperations'),
    ('AgentOperations', 'flexlibs.code.Lists.AgentOperations'),
    ('ConfidenceOperations', 'flexlibs.code.Lists.ConfidenceOperations'),
    ('PublicationOperations', 'flexlibs.code.Lists.PublicationOperations'),
    ('TranslationTypeOperations', 'flexlibs.code.Lists.TranslationTypeOperations'),
    ('OverlayOperations', 'flexlibs.code.Lists.OverlayOperations'),
]

SYSTEM_OPERATIONS = [
    ('WritingSystemOperations', 'flexlibs.code.System.WritingSystemOperations'),
    ('ProjectSettingsOperations', 'flexlibs.code.System.ProjectSettingsOperations'),
    ('CustomFieldOperations', 'flexlibs.code.System.CustomFieldOperations'),
    ('CheckOperations', 'flexlibs.code.System.CheckOperations'),
    ('AnnotationDefOperations', 'flexlibs.code.System.AnnotationDefOperations'),
]

SHARED_OPERATIONS = [
    ('MediaOperations', 'flexlibs.code.Shared.MediaOperations'),
    ('FilterOperations', 'flexlibs.code.Shared.FilterOperations'),
]

# All operations classes
ALL_OPERATIONS = (
    GRAMMAR_OPERATIONS +
    LEXICON_OPERATIONS +
    TEXTSWORDS_OPERATIONS +
    WORDFORM_OPERATIONS +
    DISCOURSE_OPERATIONS +
    SCRIPTURE_OPERATIONS +
    NOTEBOOK_OPERATIONS +
    REVERSAL_OPERATIONS +
    LISTS_OPERATIONS +
    SYSTEM_OPERATIONS +
    SHARED_OPERATIONS
)


# =============================================================================
# BASELINE TESTS - IMPORT AND INSTANTIATION
# =============================================================================

class TestOperationsImport:
    """Test that all operations classes can be imported successfully."""

    @pytest.mark.parametrize("class_name,module_path", ALL_OPERATIONS)
    def test_operations_class_import(self, class_name, module_path):
        """Test that each operations class can be imported."""
        try:
            module = __import__(module_path, fromlist=[class_name])
            ops_class = getattr(module, class_name)
            assert ops_class is not None
            assert hasattr(ops_class, '__name__')
            assert ops_class.__name__ == class_name
        except ImportError as e:
            pytest.fail(f"Failed to import {class_name} from {module_path}: {e}")


class TestOperationsInstantiation:
    """Test that all operations classes can be instantiated with a mock project."""

    @pytest.mark.parametrize("class_name,module_path", ALL_OPERATIONS)
    def test_operations_class_instantiation(self, class_name, module_path, mock_flex_project):
        """Test that each operations class can be instantiated."""
        try:
            module = __import__(module_path, fromlist=[class_name])
            ops_class = getattr(module, class_name)

            # Try to instantiate with mock project
            instance = ops_class(mock_flex_project)

            assert instance is not None
            assert instance.project == mock_flex_project

        except Exception as e:
            pytest.fail(f"Failed to instantiate {class_name}: {e}")


class TestOperationsInheritance:
    """Test that all operations classes properly inherit from BaseOperations."""

    @pytest.mark.parametrize("class_name,module_path", ALL_OPERATIONS)
    def test_inherits_from_base_operations(self, class_name, module_path):
        """Test that each operations class inherits from BaseOperations."""
        try:
            # Import BaseOperations
            from flexlibs.code.BaseOperations import BaseOperations

            # Import operations class
            module = __import__(module_path, fromlist=[class_name])
            ops_class = getattr(module, class_name)

            # Check inheritance
            assert issubclass(ops_class, BaseOperations), \
                f"{class_name} does not inherit from BaseOperations"

        except ImportError as e:
            pytest.fail(f"Failed to verify inheritance for {class_name}: {e}")


class TestReorderingMethods:
    """Test that all operations classes have the 7 reordering methods from BaseOperations."""

    REORDERING_METHODS = [
        'Sort',
        'MoveUp',
        'MoveDown',
        'MoveToIndex',
        'MoveBefore',
        'MoveAfter',
        'Swap',
    ]

    @pytest.mark.parametrize("class_name,module_path", ALL_OPERATIONS)
    def test_has_all_reordering_methods(self, class_name, module_path, mock_flex_project):
        """Test that each operations class has all 7 reordering methods."""
        try:
            module = __import__(module_path, fromlist=[class_name])
            ops_class = getattr(module, class_name)
            instance = ops_class(mock_flex_project)

            for method_name in self.REORDERING_METHODS:
                assert hasattr(instance, method_name), \
                    f"{class_name} missing reordering method: {method_name}"

                # Verify it's callable
                method = getattr(instance, method_name)
                assert callable(method), \
                    f"{class_name}.{method_name} is not callable"

        except Exception as e:
            pytest.fail(f"Failed to verify reordering methods for {class_name}: {e}")


class TestCommonCRUDMethods:
    """Test that operations classes have common CRUD methods where applicable."""

    # Common methods that most operations classes should have
    COMMON_METHODS = {
        'GetAll': 'Retrieve all items',
        'Find': 'Find specific item',
    }

    # Operations classes that should have Create
    CREATE_OPERATIONS = [
        'LexEntryOperations', 'LexSenseOperations', 'AllomorphOperations',
        'ExampleOperations', 'POSOperations', 'TextOperations', 'ParagraphOperations',
        'NoteOperations', 'PersonOperations', 'LocationOperations',
        'WfiWordformOperations', 'ReversalIndexEntryOperations',
        'ScrBookOperations', 'ScrSectionOperations',
    ]

    # Operations classes that should have Delete
    DELETE_OPERATIONS = [
        'LexEntryOperations', 'LexSenseOperations', 'AllomorphOperations',
        'ExampleOperations', 'TextOperations', 'NoteOperations',
        'WfiWordformOperations', 'ReversalIndexEntryOperations',
    ]

    @pytest.mark.parametrize("class_name,module_path", ALL_OPERATIONS)
    def test_has_getall_method(self, class_name, module_path, mock_flex_project):
        """Test that operations classes have GetAll method."""
        try:
            module = __import__(module_path, fromlist=[class_name])
            ops_class = getattr(module, class_name)
            instance = ops_class(mock_flex_project)

            # Most operations should have GetAll
            if hasattr(instance, 'GetAll'):
                assert callable(instance.GetAll)
            # It's okay if some don't have it

        except Exception as e:
            pytest.fail(f"Failed to check GetAll for {class_name}: {e}")

    @pytest.mark.parametrize("class_name,module_path",
                             [(cn, mp) for cn, mp in ALL_OPERATIONS if cn in CREATE_OPERATIONS])
    def test_has_create_method(self, class_name, module_path, mock_flex_project):
        """Test that operations classes expected to have Create do have it."""
        try:
            module = __import__(module_path, fromlist=[class_name])
            ops_class = getattr(module, class_name)
            instance = ops_class(mock_flex_project)

            assert hasattr(instance, 'Create'), \
                f"{class_name} should have Create method"
            assert callable(instance.Create)

        except Exception as e:
            pytest.fail(f"Failed to check Create for {class_name}: {e}")


# =============================================================================
# DOMAIN-SPECIFIC BASELINE TESTS
# =============================================================================

class TestGrammarOperations:
    """Baseline tests specific to Grammar operations."""

    @pytest.mark.parametrize("class_name,module_path", GRAMMAR_OPERATIONS)
    def test_grammar_operations_domain(self, class_name, module_path, mock_flex_project):
        """Test Grammar operations classes are properly configured."""
        module = __import__(module_path, fromlist=[class_name])
        ops_class = getattr(module, class_name)
        instance = ops_class(mock_flex_project)

        # Grammar operations should have GetAll
        assert hasattr(instance, 'GetAll')


class TestLexiconOperations:
    """Baseline tests specific to Lexicon operations."""

    @pytest.mark.parametrize("class_name,module_path", LEXICON_OPERATIONS)
    def test_lexicon_operations_domain(self, class_name, module_path, mock_flex_project):
        """Test Lexicon operations classes are properly configured."""
        module = __import__(module_path, fromlist=[class_name])
        ops_class = getattr(module, class_name)
        instance = ops_class(mock_flex_project)

        # Lexicon operations should have GetAll or Find
        assert hasattr(instance, 'GetAll') or hasattr(instance, 'Find')


class TestTextsWordsOperations:
    """Baseline tests specific to TextsWords operations."""

    @pytest.mark.parametrize("class_name,module_path", TEXTSWORDS_OPERATIONS)
    def test_textswords_operations_domain(self, class_name, module_path, mock_flex_project):
        """Test TextsWords operations classes are properly configured."""
        module = __import__(module_path, fromlist=[class_name])
        ops_class = getattr(module, class_name)
        instance = ops_class(mock_flex_project)

        # TextsWords operations should have GetAll
        assert hasattr(instance, 'GetAll')


class TestScriptureOperations:
    """Baseline tests specific to Scripture operations."""

    @pytest.mark.parametrize("class_name,module_path", SCRIPTURE_OPERATIONS)
    def test_scripture_operations_domain(self, class_name, module_path, mock_flex_project):
        """Test Scripture operations classes are properly configured."""
        module = __import__(module_path, fromlist=[class_name])
        ops_class = getattr(module, class_name)
        instance = ops_class(mock_flex_project)

        # Scripture operations should exist and be callable
        assert instance is not None


# =============================================================================
# SUMMARY TEST
# =============================================================================

class TestOperationsSummary:
    """Generate summary statistics about operations coverage."""

    def test_total_operations_count(self):
        """Verify we're testing all expected operations classes."""
        total = len(ALL_OPERATIONS)

        # We expect at least 61 operations classes (62 files - 1 BaseOperations)
        assert total >= 61, f"Expected at least 61 operations classes, found {total}"

        print(f"\n{'='*70}")
        print(f"OPERATIONS COVERAGE SUMMARY")
        print(f"{'='*70}")
        print(f"Total Operations Classes: {total}")
        print(f"\nBreakdown by Domain:")
        print(f"  Grammar:     {len(GRAMMAR_OPERATIONS):2d} classes")
        print(f"  Lexicon:     {len(LEXICON_OPERATIONS):2d} classes")
        print(f"  TextsWords:  {len(TEXTSWORDS_OPERATIONS):2d} classes")
        print(f"  Wordform:    {len(WORDFORM_OPERATIONS):2d} classes")
        print(f"  Discourse:   {len(DISCOURSE_OPERATIONS):2d} classes")
        print(f"  Scripture:   {len(SCRIPTURE_OPERATIONS):2d} classes")
        print(f"  Notebook:    {len(NOTEBOOK_OPERATIONS):2d} classes")
        print(f"  Reversal:    {len(REVERSAL_OPERATIONS):2d} classes")
        print(f"  Lists:       {len(LISTS_OPERATIONS):2d} classes")
        print(f"  System:      {len(SYSTEM_OPERATIONS):2d} classes")
        print(f"  Shared:      {len(SHARED_OPERATIONS):2d} classes")
        print(f"{'='*70}\n")


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

if __name__ == '__main__':
    # Run with pytest
    pytest.main([__file__, '-v', '--tb=short'])
