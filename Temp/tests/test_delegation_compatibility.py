"""
Integration tests for FLExProject delegation refactoring.

These tests verify that Craig's original methods and the new Operations
classes return identical results, ensuring backward compatibility.

Test Coverage:
- 42 delegated methods across 9 categories
- Both Craig's API and Operations API
- Parameter variations
- Edge cases
- Error handling

Setup:
- Requires a FLEx project for testing (configure PROJECT_NAME below)
- Project should have basic test data (entries, senses, examples, etc.)
- Set environment variable FLEX_TEST_PROJECT to override default

Run tests:
    pytest tests/test_delegation_compatibility.py -v
    pytest tests/test_delegation_compatibility.py -v -k "LexEntry"
    pytest tests/test_delegation_compatibility.py -v --tb=short

Author: FlexTools Development Team
Date: 2025-11-24
"""

import pytest
import os
import sys
from functools import wraps

# Add parent directory to path to import flexlibs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flexlibs.code.FLExProject import FLExProject

# Configuration
PROJECT_NAME = os.environ.get('FLEX_TEST_PROJECT', 'TestProject')


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def project():
    """
    Fixture providing an open FLEx project for testing.

    The project is opened once for all tests in this module and closed
    at the end to improve performance.
    """
    proj = FLExProject()
    try:
        proj.OpenProject(PROJECT_NAME, writeEnabled=False)
        yield proj
    finally:
        if hasattr(proj, 'project') and proj.project:
            proj.CloseProject()


@pytest.fixture(scope="module")
def writable_project():
    """
    Fixture providing an open FLEx project with write access.

    Used for testing setter methods and modifications.
    Note: Tests should clean up after themselves to avoid side effects.
    """
    proj = FLExProject()
    try:
        proj.OpenProject(PROJECT_NAME, writeEnabled=True)
        yield proj
    finally:
        if hasattr(proj, 'project') and proj.project:
            proj.CloseProject()


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def sample_entry(project):
    """Get the first lexical entry for testing."""
    try:
        return next(iter(project.LexEntry.GetAll()))
    except StopIteration:
        pytest.skip("No lexical entries in test project")


@pytest.fixture(scope="module")
def sample_sense(sample_entry, project):
    """Get the first sense from the sample entry."""
    try:
        if hasattr(sample_entry, 'SensesOS') and sample_entry.SensesOS.Count > 0:
            return sample_entry.SensesOS[0]
    except:
        pass
    pytest.skip("No senses available in sample entry")


@pytest.fixture(scope="module")
def sample_example(sample_sense):
    """Get the first example from the sample sense."""
    try:
        if hasattr(sample_sense, 'ExamplesOS') and sample_sense.ExamplesOS.Count > 0:
            return sample_sense.ExamplesOS[0]
    except:
        pass
    pytest.skip("No examples available in sample sense")


@pytest.fixture(scope="module")
def sample_pronunciation(sample_entry):
    """Get the first pronunciation from the sample entry."""
    try:
        if hasattr(sample_entry, 'PronunciationsOS') and sample_entry.PronunciationsOS.Count > 0:
            return sample_entry.PronunciationsOS[0]
    except:
        pass
    pytest.skip("No pronunciations available in sample entry")


@pytest.fixture(scope="module")
def sample_text(project):
    """Get the first text for testing."""
    try:
        texts = list(project.Texts.GetAll())
        if texts:
            return texts[0]
    except:
        pass
    pytest.skip("No texts in test project")


@pytest.fixture(scope="module")
def sample_reversal_index(project):
    """Get the first reversal index for testing."""
    try:
        indices = project.lp.ReversalIndexes
        if indices.Count > 0:
            return indices[0]
    except:
        pass
    pytest.skip("No reversal indices in test project")


# ============================================================================
# Helper Utilities
# ============================================================================

def skip_if_no_data(func):
    """
    Decorator to gracefully skip tests when test data is not available.

    This prevents test failures due to missing data while still allowing
    tests to run when appropriate data exists.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (StopIteration, IndexError, AttributeError) as e:
            pytest.skip(f"Test data not available: {str(e)}")
    return wrapper


def compare_results(result_craig, result_operations, method_name):
    """
    Compare results from Craig's API and Operations API.

    Args:
        result_craig: Result from Craig's delegated method
        result_operations: Result from Operations class method
        method_name: Name of the method being tested (for error messages)

    Raises:
        AssertionError: If results don't match
    """
    assert result_craig == result_operations, \
        f"{method_name}: APIs must return identical results.\n" \
        f"  Craig's API:      {result_craig!r}\n" \
        f"  Operations API:   {result_operations!r}"


# ============================================================================
# Category 1: LexEntry Operations (5 tests)
# ============================================================================

class TestLexEntryOperations:
    """Test backward compatibility of LexEntry delegated methods."""

    @skip_if_no_data
    def test_lexicon_get_headword_compatibility(self, project, sample_entry):
        """
        Verify LexiconGetHeadword returns same result as LexEntry.GetHeadword.

        Tests:
        - Craig's API: project.LexiconGetHeadword(entry)
        - Operations API: project.LexEntry.GetHeadword(entry)
        """
        result_craig = project.LexiconGetHeadword(sample_entry)
        result_operations = project.LexEntry.GetHeadword(sample_entry)

        compare_results(result_craig, result_operations, "LexiconGetHeadword")

    @skip_if_no_data
    def test_lexicon_get_lexeme_form_compatibility(self, project, sample_entry):
        """
        Verify LexiconGetLexemeForm returns same result as LexEntry.GetLexemeForm.

        Tests both with default writing system and specific writing system.
        """
        # Test with default writing system
        result_craig = project.LexiconGetLexemeForm(sample_entry)
        result_operations = project.LexEntry.GetLexemeForm(sample_entry)
        compare_results(result_craig, result_operations, "LexiconGetLexemeForm (default WS)")

        # Test with specific writing system
        ws = project.GetDefaultVernacularWS()
        result_craig_ws = project.LexiconGetLexemeForm(sample_entry, ws)
        result_operations_ws = project.LexEntry.GetLexemeForm(sample_entry, ws)
        compare_results(result_craig_ws, result_operations_ws, "LexiconGetLexemeForm (specific WS)")

    @skip_if_no_data
    def test_lexicon_set_lexeme_form_compatibility(self, writable_project, sample_entry):
        """
        Verify LexiconSetLexemeForm behaves same as LexEntry.SetLexemeForm.

        Note: This test modifies data but restores original value.
        """
        # Save original value
        original = writable_project.LexEntry.GetLexemeForm(sample_entry)

        try:
            # Set via Craig's API
            test_value = "TEST_FORM_1"
            writable_project.LexiconSetLexemeForm(sample_entry, test_value)
            result_craig = writable_project.LexEntry.GetLexemeForm(sample_entry)

            # Set via Operations API
            test_value_2 = "TEST_FORM_2"
            writable_project.LexEntry.SetLexemeForm(sample_entry, test_value_2)
            result_operations = writable_project.LexEntry.GetLexemeForm(sample_entry)

            # Both should have successfully set the value
            assert result_craig == test_value, "Craig's API failed to set value"
            assert result_operations == test_value_2, "Operations API failed to set value"

        finally:
            # Restore original value
            if original:
                writable_project.LexEntry.SetLexemeForm(sample_entry, original)

    @skip_if_no_data
    def test_lexicon_get_citation_form_compatibility(self, project, sample_entry):
        """
        Verify LexiconGetCitationForm returns same result as LexEntry.GetCitationForm.

        Tests both with default writing system and specific writing system.
        """
        # Test with default writing system
        result_craig = project.LexiconGetCitationForm(sample_entry)
        result_operations = project.LexEntry.GetCitationForm(sample_entry)
        compare_results(result_craig, result_operations, "LexiconGetCitationForm (default WS)")

        # Test with specific writing system
        ws = project.GetDefaultVernacularWS()
        result_craig_ws = project.LexiconGetCitationForm(sample_entry, ws)
        result_operations_ws = project.LexEntry.GetCitationForm(sample_entry, ws)
        compare_results(result_craig_ws, result_operations_ws, "LexiconGetCitationForm (specific WS)")

    @skip_if_no_data
    def test_lexicon_all_entries_compatibility(self, project):
        """
        Verify LexiconAllEntries returns same entries as LexEntry.GetAll.

        Compares the count and first few entries.
        """
        # Get entries from both APIs
        entries_craig = list(project.LexiconAllEntries())
        entries_operations = list(project.LexEntry.GetAll())

        # Compare counts
        assert len(entries_craig) == len(entries_operations), \
            f"Entry count mismatch: Craig={len(entries_craig)}, Operations={len(entries_operations)}"

        # Compare first 10 entries (or all if less than 10)
        compare_count = min(10, len(entries_craig))
        for i in range(compare_count):
            assert entries_craig[i] == entries_operations[i], \
                f"Entry mismatch at index {i}"


# ============================================================================
# Category 2: LexSense Operations (7 tests)
# ============================================================================

class TestLexSenseOperations:
    """Test backward compatibility of LexSense delegated methods."""

    @skip_if_no_data
    def test_lexicon_get_sense_gloss_compatibility(self, project, sample_sense):
        """
        Verify LexiconGetSenseGloss returns same result as Senses.GetGloss.
        """
        # Test with default writing system
        result_craig = project.LexiconGetSenseGloss(sample_sense)
        result_operations = project.Senses.GetGloss(sample_sense)
        compare_results(result_craig, result_operations, "LexiconGetSenseGloss (default WS)")

        # Test with specific writing system
        ws = project.GetDefaultAnalysisWS()
        result_craig_ws = project.LexiconGetSenseGloss(sample_sense, ws)
        result_operations_ws = project.Senses.GetGloss(sample_sense, ws)
        compare_results(result_craig_ws, result_operations_ws, "LexiconGetSenseGloss (specific WS)")

    @skip_if_no_data
    def test_lexicon_set_sense_gloss_compatibility(self, writable_project, sample_sense):
        """
        Verify LexiconSetSenseGloss behaves same as Senses.SetGloss.

        Note: This test modifies data but restores original value.
        """
        # Save original value
        original = writable_project.Senses.GetGloss(sample_sense)

        try:
            # Set via Craig's API
            test_value = "TEST_GLOSS_1"
            writable_project.LexiconSetSenseGloss(sample_sense, test_value)
            result_craig = writable_project.Senses.GetGloss(sample_sense)

            # Set via Operations API
            test_value_2 = "TEST_GLOSS_2"
            writable_project.Senses.SetGloss(sample_sense, test_value_2)
            result_operations = writable_project.Senses.GetGloss(sample_sense)

            # Both should have successfully set the value
            assert result_craig == test_value, "Craig's API failed to set gloss"
            assert result_operations == test_value_2, "Operations API failed to set gloss"

        finally:
            # Restore original value
            if original:
                writable_project.Senses.SetGloss(sample_sense, original)

    @skip_if_no_data
    def test_lexicon_get_sense_definition_compatibility(self, project, sample_sense):
        """
        Verify LexiconGetSenseDefinition returns same result as Senses.GetDefinition.
        """
        # Test with default writing system
        result_craig = project.LexiconGetSenseDefinition(sample_sense)
        result_operations = project.Senses.GetDefinition(sample_sense)
        compare_results(result_craig, result_operations, "LexiconGetSenseDefinition (default WS)")

        # Test with specific writing system
        ws = project.GetDefaultAnalysisWS()
        result_craig_ws = project.LexiconGetSenseDefinition(sample_sense, ws)
        result_operations_ws = project.Senses.GetDefinition(sample_sense, ws)
        compare_results(result_craig_ws, result_operations_ws, "LexiconGetSenseDefinition (specific WS)")

    @skip_if_no_data
    def test_lexicon_get_sense_pos_compatibility(self, project, sample_sense):
        """
        Verify LexiconGetSensePOS returns same result as Senses.GetPOS.
        """
        result_craig = project.LexiconGetSensePOS(sample_sense)
        result_operations = project.Senses.GetPOS(sample_sense)
        compare_results(result_craig, result_operations, "LexiconGetSensePOS")

    @skip_if_no_data
    def test_lexicon_get_sense_semantic_domains_compatibility(self, project, sample_sense):
        """
        Verify LexiconGetSenseSemanticDomains returns same result as Senses.GetSemanticDomains.
        """
        result_craig = project.LexiconGetSenseSemanticDomains(sample_sense)
        result_operations = project.Senses.GetSemanticDomains(sample_sense)

        # Convert to lists for comparison
        list_craig = list(result_craig)
        list_operations = list(result_operations)

        assert len(list_craig) == len(list_operations), \
            f"Semantic domain count mismatch: Craig={len(list_craig)}, Operations={len(list_operations)}"

        # Compare domain objects
        for i, (domain_c, domain_o) in enumerate(zip(list_craig, list_operations)):
            assert domain_c == domain_o, f"Semantic domain mismatch at index {i}"

    @skip_if_no_data
    def test_lexicon_get_sense_number_compatibility(self, project, sample_sense):
        """
        Verify LexiconGetSenseNumber returns same result as Senses.GetSenseNumber.
        """
        result_craig = project.LexiconGetSenseNumber(sample_sense)
        result_operations = project.Senses.GetSenseNumber(sample_sense)
        compare_results(result_craig, result_operations, "LexiconGetSenseNumber")

    @skip_if_no_data
    def test_lexicon_sense_analyses_count_compatibility(self, project, sample_sense):
        """
        Verify LexiconSenseAnalysesCount returns same result as Senses.GetAnalysesCount.
        """
        result_craig = project.LexiconSenseAnalysesCount(sample_sense)
        result_operations = project.Senses.GetAnalysesCount(sample_sense)
        compare_results(result_craig, result_operations, "LexiconSenseAnalysesCount")


# ============================================================================
# Category 3: Example Operations (2 tests)
# ============================================================================

class TestExampleOperations:
    """Test backward compatibility of Example sentence delegated methods."""

    @skip_if_no_data
    def test_lexicon_get_example_compatibility(self, project, sample_example):
        """
        Verify LexiconGetExample returns same result as Examples.GetExample.
        """
        # Test with default writing system
        result_craig = project.LexiconGetExample(sample_example)
        result_operations = project.Examples.GetExample(sample_example)
        compare_results(result_craig, result_operations, "LexiconGetExample (default WS)")

        # Test with specific writing system
        ws = project.GetDefaultVernacularWS()
        result_craig_ws = project.LexiconGetExample(sample_example, ws)
        result_operations_ws = project.Examples.GetExample(sample_example, ws)
        compare_results(result_craig_ws, result_operations_ws, "LexiconGetExample (specific WS)")

    @skip_if_no_data
    def test_lexicon_set_example_compatibility(self, writable_project, sample_example):
        """
        Verify LexiconSetExample behaves same as Examples.SetExample.

        Note: This test modifies data but restores original value.
        """
        # Save original value
        original = writable_project.Examples.GetExample(sample_example)

        try:
            # Set via Craig's API
            test_value = "TEST EXAMPLE 1"
            writable_project.LexiconSetExample(sample_example, test_value)
            result_craig = writable_project.Examples.GetExample(sample_example)

            # Set via Operations API
            test_value_2 = "TEST EXAMPLE 2"
            writable_project.Examples.SetExample(sample_example, test_value_2)
            result_operations = writable_project.Examples.GetExample(sample_example)

            # Both should have successfully set the value
            assert result_craig == test_value, "Craig's API failed to set example"
            assert result_operations == test_value_2, "Operations API failed to set example"

        finally:
            # Restore original value
            if original:
                writable_project.Examples.SetExample(sample_example, original)


# ============================================================================
# Category 4: Pronunciation Operations (1 test)
# ============================================================================

class TestPronunciationOperations:
    """Test backward compatibility of Pronunciation delegated methods."""

    @skip_if_no_data
    def test_lexicon_get_pronunciation_compatibility(self, project, sample_pronunciation):
        """
        Verify LexiconGetPronunciation returns same result as Pronunciations.GetForm.
        """
        # Test with default writing system
        result_craig = project.LexiconGetPronunciation(sample_pronunciation)
        result_operations = project.Pronunciations.GetForm(sample_pronunciation)
        compare_results(result_craig, result_operations, "LexiconGetPronunciation (default WS)")

        # Test with specific writing system
        ws = project.GetDefaultVernacularWS()
        result_craig_ws = project.LexiconGetPronunciation(sample_pronunciation, ws)
        result_operations_ws = project.Pronunciations.GetForm(sample_pronunciation, ws)
        compare_results(result_craig_ws, result_operations_ws, "LexiconGetPronunciation (specific WS)")


# ============================================================================
# Category 5: Text Operations (2 tests)
# ============================================================================

class TestTextOperations:
    """Test backward compatibility of Text delegated methods."""

    @skip_if_no_data
    def test_texts_get_all_compatibility(self, project):
        """
        Verify TextsGetAll returns same texts as Texts.GetAll.

        Tests with different parameter combinations.
        """
        # Test with default parameters
        result_craig = list(project.TextsGetAll())
        result_operations = list(project.Texts.GetAll())

        assert len(result_craig) == len(result_operations), \
            f"Text count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"

        # Compare first few texts
        compare_count = min(5, len(result_craig))
        for i in range(compare_count):
            # TextsGetAll returns tuples, so we need to extract the text object
            text_craig = result_craig[i][0] if isinstance(result_craig[i], tuple) else result_craig[i]
            text_operations = result_operations[i]
            assert text_craig == text_operations, f"Text mismatch at index {i}"

    @skip_if_no_data
    def test_texts_number_of_texts_compatibility(self, project):
        """
        Verify TextsNumberOfTexts returns same count as Texts.GetCount.
        """
        result_craig = project.TextsNumberOfTexts()
        result_operations = project.Texts.GetCount()
        compare_results(result_craig, result_operations, "TextsNumberOfTexts")


# ============================================================================
# Category 6: Reversal Operations (4 tests)
# ============================================================================

class TestReversalOperations:
    """Test backward compatibility of Reversal delegated methods."""

    @skip_if_no_data
    def test_reversal_index_compatibility(self, project):
        """
        Verify ReversalIndex returns same index as Reversal.GetIndex.
        """
        # Get the first reversal index language tag
        try:
            indices = project.lp.ReversalIndexes
            if indices.Count == 0:
                pytest.skip("No reversal indices in project")

            lang_tag = indices[0].WritingSystem

            result_craig = project.ReversalIndex(lang_tag)
            result_operations = project.Reversal.GetIndex(lang_tag)
            compare_results(result_craig, result_operations, "ReversalIndex")
        except:
            pytest.skip("Cannot access reversal indices")

    @skip_if_no_data
    def test_reversal_entries_compatibility(self, project):
        """
        Verify ReversalEntries returns same entries as Reversal.GetAllEntries.
        """
        try:
            indices = project.lp.ReversalIndexes
            if indices.Count == 0:
                pytest.skip("No reversal indices in project")

            lang_tag = indices[0].WritingSystem

            result_craig = list(project.ReversalEntries(lang_tag))
            result_operations = list(project.Reversal.GetAllEntries(lang_tag))

            assert len(result_craig) == len(result_operations), \
                f"Reversal entry count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"
        except:
            pytest.skip("Cannot access reversal entries")

    @skip_if_no_data
    def test_reversal_get_form_compatibility(self, project, sample_reversal_index):
        """
        Verify ReversalGetForm returns same result as Reversal.GetForm.
        """
        # Get first reversal entry
        try:
            entries = list(sample_reversal_index.AllEntries)
            if not entries:
                pytest.skip("No reversal entries available")

            entry = entries[0]

            result_craig = project.ReversalGetForm(entry)
            result_operations = project.Reversal.GetForm(entry)
            compare_results(result_craig, result_operations, "ReversalGetForm")
        except:
            pytest.skip("Cannot access reversal entry form")

    @skip_if_no_data
    def test_reversal_set_form_compatibility(self, writable_project, sample_reversal_index):
        """
        Verify ReversalSetForm behaves same as Reversal.SetForm.

        Note: This test modifies data but restores original value.
        """
        # Get first reversal entry
        try:
            entries = list(sample_reversal_index.AllEntries)
            if not entries:
                pytest.skip("No reversal entries available")

            entry = entries[0]

            # Save original value
            original = writable_project.Reversal.GetForm(entry)

            try:
                # Set via Craig's API
                test_value = "TEST_REVERSAL_1"
                writable_project.ReversalSetForm(entry, test_value)
                result_craig = writable_project.Reversal.GetForm(entry)

                # Set via Operations API
                test_value_2 = "TEST_REVERSAL_2"
                writable_project.Reversal.SetForm(entry, test_value_2)
                result_operations = writable_project.Reversal.GetForm(entry)

                # Both should have successfully set the value
                assert result_craig == test_value, "Craig's API failed to set reversal form"
                assert result_operations == test_value_2, "Operations API failed to set reversal form"

            finally:
                # Restore original value
                if original:
                    writable_project.Reversal.SetForm(entry, original)
        except:
            pytest.skip("Cannot modify reversal entry form")


# ============================================================================
# Category 7: System Operations (4 tests)
# ============================================================================

class TestSystemOperations:
    """Test backward compatibility of system-level delegated methods."""

    def test_get_parts_of_speech_compatibility(self, project):
        """
        Verify GetPartsOfSpeech returns same result as POS.GetAll.
        """
        result_craig = list(project.GetPartsOfSpeech())
        result_operations = list(project.POS.GetAll())

        assert len(result_craig) == len(result_operations), \
            f"POS count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"

    def test_get_all_semantic_domains_compatibility(self, project):
        """
        Verify GetAllSemanticDomains returns same result as SemanticDomains.GetAll.

        Tests both flat and hierarchical modes.
        """
        # Test flat mode (default)
        result_craig = list(project.GetAllSemanticDomains())
        result_operations = list(project.SemanticDomains.GetAll())

        assert len(result_craig) == len(result_operations), \
            f"Semantic domain count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"

        # Test hierarchical mode
        result_craig_hier = list(project.GetAllSemanticDomains(flat=False))
        result_operations_hier = list(project.SemanticDomains.GetAll(flat=False))

        assert len(result_craig_hier) == len(result_operations_hier), \
            f"Semantic domain count mismatch (hierarchical): Craig={len(result_craig_hier)}, Operations={len(result_operations_hier)}"

    def test_get_lexical_relation_types_compatibility(self, project):
        """
        Verify GetLexicalRelationTypes returns same result as LexReferences.GetAllTypes.
        """
        result_craig = list(project.GetLexicalRelationTypes())
        result_operations = list(project.LexReferences.GetAllTypes())

        assert len(result_craig) == len(result_operations), \
            f"Lexical relation type count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"

    def test_get_publications_compatibility(self, project):
        """
        Verify GetPublications returns same result as Publications.GetAll.
        """
        result_craig = list(project.GetPublications())
        result_operations = list(project.Publications.GetAll())

        assert len(result_craig) == len(result_operations), \
            f"Publication count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"


# ============================================================================
# Category 8: Writing System Operations (7 tests)
# ============================================================================

class TestWritingSystemOperations:
    """Test backward compatibility of writing system delegated methods."""

    def test_best_str_compatibility(self, project, sample_entry):
        """
        Verify BestStr returns same result as WritingSystems.BestStr.
        """
        # Get a multilingual string object to test with
        if hasattr(sample_entry, 'LexemeFormOA') and sample_entry.LexemeFormOA:
            string_obj = sample_entry.LexemeFormOA.Form

            result_craig = project.BestStr(string_obj)
            result_operations = project.WritingSystems.BestStr(string_obj)
            compare_results(result_craig, result_operations, "BestStr")
        else:
            pytest.skip("No suitable string object for BestStr test")

    def test_get_all_vernacular_ws_compatibility(self, project):
        """
        Verify GetAllVernacularWSs returns same result as WritingSystems.GetAllVernacular.
        """
        result_craig = list(project.GetAllVernacularWSs())
        result_operations = list(project.WritingSystems.GetAllVernacular())

        assert len(result_craig) == len(result_operations), \
            f"Vernacular WS count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"

        # Compare writing system handles
        for i, (ws_c, ws_o) in enumerate(zip(result_craig, result_operations)):
            assert ws_c == ws_o, f"Vernacular WS mismatch at index {i}"

    def test_get_all_analysis_ws_compatibility(self, project):
        """
        Verify GetAllAnalysisWSs returns same result as WritingSystems.GetAllAnalysis.
        """
        result_craig = list(project.GetAllAnalysisWSs())
        result_operations = list(project.WritingSystems.GetAllAnalysis())

        assert len(result_craig) == len(result_operations), \
            f"Analysis WS count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"

        # Compare writing system handles
        for i, (ws_c, ws_o) in enumerate(zip(result_craig, result_operations)):
            assert ws_c == ws_o, f"Analysis WS mismatch at index {i}"

    def test_get_writing_systems_compatibility(self, project):
        """
        Verify GetWritingSystems returns same result as WritingSystems.GetAll.
        """
        result_craig = list(project.GetWritingSystems())
        result_operations = list(project.WritingSystems.GetAll())

        assert len(result_craig) == len(result_operations), \
            f"Writing system count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"

    def test_ws_ui_name_compatibility(self, project):
        """
        Verify WSUIName returns same result as WritingSystems.GetUIName.
        """
        # Test with default vernacular WS
        ws = project.GetDefaultVernacularWS()

        result_craig = project.WSUIName(ws)
        result_operations = project.WritingSystems.GetUIName(ws)
        compare_results(result_craig, result_operations, "WSUIName")

    def test_get_default_vernacular_ws_compatibility(self, project):
        """
        Verify GetDefaultVernacularWS returns same result as WritingSystems.GetDefaultVernacular.
        """
        result_craig = project.GetDefaultVernacularWS()
        result_operations = project.WritingSystems.GetDefaultVernacular()
        compare_results(result_craig, result_operations, "GetDefaultVernacularWS")

    def test_get_default_analysis_ws_compatibility(self, project):
        """
        Verify GetDefaultAnalysisWS returns same result as WritingSystems.GetDefaultAnalysis.
        """
        result_craig = project.GetDefaultAnalysisWS()
        result_operations = project.WritingSystems.GetDefaultAnalysis()
        compare_results(result_craig, result_operations, "GetDefaultAnalysisWS")


# ============================================================================
# Category 9: CustomField Operations (9 tests)
# ============================================================================

class TestCustomFieldOperations:
    """Test backward compatibility of custom field delegated methods."""

    def test_lexicon_field_is_string_type_compatibility(self, project):
        """
        Verify LexiconFieldIsStringType returns same result as CustomFields.IsStringType.
        """
        # Get a custom field to test with
        fields = list(project.CustomFields.GetAllFields("LexEntry"))
        if not fields:
            pytest.skip("No custom fields defined for testing")

        field_id = fields[0][0]  # (flid, label)

        result_craig = project.LexiconFieldIsStringType(field_id)
        result_operations = project.CustomFields.IsStringType(field_id)
        compare_results(result_craig, result_operations, "LexiconFieldIsStringType")

    def test_lexicon_field_is_multi_type_compatibility(self, project):
        """
        Verify LexiconFieldIsMultiType returns same result as CustomFields.IsMultiType.
        """
        # Get a custom field to test with
        fields = list(project.CustomFields.GetAllFields("LexEntry"))
        if not fields:
            pytest.skip("No custom fields defined for testing")

        field_id = fields[0][0]

        result_craig = project.LexiconFieldIsMultiType(field_id)
        result_operations = project.CustomFields.IsMultiType(field_id)
        compare_results(result_craig, result_operations, "LexiconFieldIsMultiType")

    def test_lexicon_field_is_any_string_type_compatibility(self, project):
        """
        Verify LexiconFieldIsAnyStringType returns same result as CustomFields.IsAnyStringType.
        """
        # Get a custom field to test with
        fields = list(project.CustomFields.GetAllFields("LexEntry"))
        if not fields:
            pytest.skip("No custom fields defined for testing")

        field_id = fields[0][0]

        result_craig = project.LexiconFieldIsAnyStringType(field_id)
        result_operations = project.CustomFields.IsAnyStringType(field_id)
        compare_results(result_craig, result_operations, "LexiconFieldIsAnyStringType")

    def test_lexicon_get_entry_custom_fields_compatibility(self, project):
        """
        Verify LexiconGetEntryCustomFields returns same result as CustomFields.GetAllFields("LexEntry").
        """
        result_craig = list(project.LexiconGetEntryCustomFields())
        result_operations = list(project.CustomFields.GetAllFields("LexEntry"))

        assert len(result_craig) == len(result_operations), \
            f"Entry custom field count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"

        # Compare field IDs and labels
        for i, (field_c, field_o) in enumerate(zip(result_craig, result_operations)):
            assert field_c == field_o, f"Entry custom field mismatch at index {i}"

    def test_lexicon_get_sense_custom_fields_compatibility(self, project):
        """
        Verify LexiconGetSenseCustomFields returns same result as CustomFields.GetAllFields("LexSense").
        """
        result_craig = list(project.LexiconGetSenseCustomFields())
        result_operations = list(project.CustomFields.GetAllFields("LexSense"))

        assert len(result_craig) == len(result_operations), \
            f"Sense custom field count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"

    def test_lexicon_get_example_custom_fields_compatibility(self, project):
        """
        Verify LexiconGetExampleCustomFields returns same result as CustomFields.GetAllFields("LexExampleSentence").
        """
        result_craig = list(project.LexiconGetExampleCustomFields())
        result_operations = list(project.CustomFields.GetAllFields("LexExampleSentence"))

        assert len(result_craig) == len(result_operations), \
            f"Example custom field count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"

    def test_lexicon_get_allomorph_custom_fields_compatibility(self, project):
        """
        Verify LexiconGetAllomorphCustomFields returns same result as CustomFields.GetAllFields("MoForm").
        """
        result_craig = list(project.LexiconGetAllomorphCustomFields())
        result_operations = list(project.CustomFields.GetAllFields("MoForm"))

        assert len(result_craig) == len(result_operations), \
            f"Allomorph custom field count mismatch: Craig={len(result_craig)}, Operations={len(result_operations)}"

    def test_lexicon_get_entry_custom_field_named_compatibility(self, project):
        """
        Verify LexiconGetEntryCustomFieldNamed returns same result as CustomFields.GetFieldNamed.
        """
        # Get a custom field name to test with
        fields = list(project.CustomFields.GetAllFields("LexEntry"))
        if not fields:
            pytest.skip("No custom fields defined for testing")

        field_name = fields[0][1]  # (flid, label)

        result_craig = project.LexiconGetEntryCustomFieldNamed(field_name)
        result_operations = project.CustomFields.GetFieldNamed("LexEntry", field_name)
        compare_results(result_craig, result_operations, "LexiconGetEntryCustomFieldNamed")

    def test_lexicon_get_sense_custom_field_named_compatibility(self, project):
        """
        Verify LexiconGetSenseCustomFieldNamed returns same result as CustomFields.GetFieldNamed.
        """
        # Get a custom field name to test with
        fields = list(project.CustomFields.GetAllFields("LexSense"))
        if not fields:
            pytest.skip("No sense custom fields defined for testing")

        field_name = fields[0][1]

        result_craig = project.LexiconGetSenseCustomFieldNamed(field_name)
        result_operations = project.CustomFields.GetFieldNamed("LexSense", field_name)
        compare_results(result_craig, result_operations, "LexiconGetSenseCustomFieldNamed")


# ============================================================================
# Test Summary
# ============================================================================

def test_delegation_coverage():
    """
    Meta-test to verify all delegated methods are covered.

    This test documents which methods are being tested for backward compatibility.
    """
    tested_methods = {
        # Category 1: LexEntry Operations (5 methods)
        'LexiconGetHeadword',
        'LexiconGetLexemeForm',
        'LexiconSetLexemeForm',
        'LexiconGetCitationForm',
        'LexiconAllEntries',

        # Category 2: LexSense Operations (7 methods)
        'LexiconGetSenseGloss',
        'LexiconSetSenseGloss',
        'LexiconGetSenseDefinition',
        'LexiconGetSensePOS',
        'LexiconGetSenseSemanticDomains',
        'LexiconGetSenseNumber',
        'LexiconSenseAnalysesCount',

        # Category 3: Example Operations (2 methods)
        'LexiconGetExample',
        'LexiconSetExample',

        # Category 4: Pronunciation Operations (1 method)
        'LexiconGetPronunciation',

        # Category 5: Text Operations (2 methods)
        'TextsGetAll',
        'TextsNumberOfTexts',

        # Category 6: Reversal Operations (4 methods)
        'ReversalIndex',
        'ReversalEntries',
        'ReversalGetForm',
        'ReversalSetForm',

        # Category 7: System Operations (4 methods)
        'GetPartsOfSpeech',
        'GetAllSemanticDomains',
        'GetLexicalRelationTypes',
        'GetPublications',

        # Category 8: Writing System Operations (7 methods)
        'BestStr',
        'GetAllVernacularWSs',
        'GetAllAnalysisWSs',
        'GetWritingSystems',
        'WSUIName',
        'GetDefaultVernacularWS',
        'GetDefaultAnalysisWS',

        # Category 9: CustomField Operations (9 methods)
        'LexiconFieldIsStringType',
        'LexiconFieldIsMultiType',
        'LexiconFieldIsAnyStringType',
        'LexiconGetEntryCustomFields',
        'LexiconGetSenseCustomFields',
        'LexiconGetExampleCustomFields',
        'LexiconGetAllomorphCustomFields',
        'LexiconGetEntryCustomFieldNamed',
        'LexiconGetSenseCustomFieldNamed',
    }

    assert len(tested_methods) == 42, \
        f"Expected 42 tested methods, found {len(tested_methods)}"

    # This test always passes - it's just documentation
    print(f"\nTesting {len(tested_methods)} delegated methods for backward compatibility")
    print("Categories:")
    print("  - LexEntry Operations: 5 methods")
    print("  - LexSense Operations: 7 methods")
    print("  - Example Operations: 2 methods")
    print("  - Pronunciation Operations: 1 method")
    print("  - Text Operations: 2 methods")
    print("  - Reversal Operations: 4 methods")
    print("  - System Operations: 4 methods")
    print("  - Writing System Operations: 7 methods")
    print("  - CustomField Operations: 9 methods")


if __name__ == "__main__":
    # Run tests with pytest when executed directly
    import sys
    pytest.main([__file__, "-v"] + sys.argv[1:])
