"""
Test Suite for LexSenseOperations

Tests operations for lexical senses (meanings):
- Create: Create senses with gloss and definition
- Read: GetAll, Find, GetGloss, GetDefinition
- Update: SetGloss, SetDefinition, SetPartOfSpeech
- Delete: Delete senses
- Examples: AddExample, GetExamples
- Reordering: Inherited BaseOperations methods
- Sequence: _GetSequence returns parent.SensesOS

Uses mocking for unit tests that don't require FLEx connection.

Author: Programmer Team 3 - Test Infrastructure
Date: 2025-12-05
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
_test_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_test_dir))
sys.path.insert(0, _project_root)

# Import test fixtures
from tests.operations import (
    mock_flex_project,
    mock_lex_entry,
    mock_lex_sense,
    assert_has_reordering_methods,
    MockLCMObject,
    MockMultiString,
    MockOwningSequence,
    generate_test_senses,
)


# =============================================================================
# UNIT TESTS - Using Mocks
# =============================================================================


class TestLexSenseOperationsImport:
    """Test that LexSenseOperations can be imported and instantiated."""

    def test_import_lexsense_operations(self):
        """Test importing LexSenseOperations class."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        assert LexSenseOperations is not None

    def test_instantiate_with_mock_project(self, mock_flex_project):
        """Test instantiating LexSenseOperations with mock project."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert ops is not None
        assert ops.project == mock_flex_project


class TestLexSenseOperationsInheritance:
    """Test BaseOperations inheritance."""

    def test_inherits_from_base_operations(self):
        """Test that LexSenseOperations inherits from BaseOperations."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations
        from flexlibs2.code.BaseOperations import BaseOperations

        assert issubclass(LexSenseOperations, BaseOperations)

    def test_has_all_reordering_methods(self, mock_flex_project):
        """Test that LexSenseOperations has all reordering methods."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert_has_reordering_methods(ops)

    def test_has_getsequence_implementation(self, mock_flex_project):
        """Test that _GetSequence is implemented for senses."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert hasattr(ops, "_GetSequence")

        # Test with mock entry
        mock_entry = MockLCMObject()
        mock_entry.SensesOS = MockOwningSequence()

        # Should return SensesOS
        sequence = ops._GetSequence(mock_entry)
        assert sequence is mock_entry.SensesOS


class TestLexSenseOperationsCRUDMethods:
    """Test that CRUD methods exist and are callable."""

    def test_has_create_method(self, mock_flex_project):
        """Test that Create method exists and is callable."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert hasattr(ops, "Create")
        assert callable(ops.Create)

    def test_has_delete_method(self, mock_flex_project):
        """Test that Delete method exists and is callable."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert hasattr(ops, "Delete")
        assert callable(ops.Delete)

    def test_has_find_method(self, mock_flex_project):
        """Test that Find method exists and is callable."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert hasattr(ops, "Find")
        assert callable(ops.Find)


class TestLexSenseOperationsPropertyGetters:
    """Test property getter methods."""

    def test_has_getgloss_method(self, mock_flex_project):
        """Test that GetGloss method exists."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert hasattr(ops, "GetGloss")
        assert callable(ops.GetGloss)

    def test_has_getdefinition_method(self, mock_flex_project):
        """Test that GetDefinition method exists."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert hasattr(ops, "GetDefinition")
        assert callable(ops.GetDefinition)

    def test_has_getpartofspeech_method(self, mock_flex_project):
        """Test that GetPartOfSpeech method exists."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert hasattr(ops, "GetPartOfSpeech")
        assert callable(ops.GetPartOfSpeech)


class TestLexSenseOperationsPropertySetters:
    """Test property setter methods."""

    def test_has_setgloss_method(self, mock_flex_project):
        """Test that SetGloss method exists."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert hasattr(ops, "SetGloss")
        assert callable(ops.SetGloss)

    def test_has_setdefinition_method(self, mock_flex_project):
        """Test that SetDefinition method exists."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert hasattr(ops, "SetDefinition")
        assert callable(ops.SetDefinition)

    def test_has_setpartofspeech_method(self, mock_flex_project):
        """Test that SetPartOfSpeech method exists."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert hasattr(ops, "SetPartOfSpeech")
        assert callable(ops.SetPartOfSpeech)


class TestLexSenseOperationsExampleMethods:
    """Test example-related methods."""

    def test_has_addexample_method(self, mock_flex_project):
        """Test that AddExample method exists."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        assert hasattr(ops, "AddExample")
        assert callable(ops.AddExample)

    def test_has_getexamples_method(self, mock_flex_project):
        """Test that GetExamples or similar method exists."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        ops = LexSenseOperations(mock_flex_project)
        # Check for GetExamples or GetExampleCount
        assert hasattr(ops, "GetExamples") or hasattr(ops, "GetExampleCount")


class TestLexSenseOperationsReordering:
    """Test reordering functionality with mock senses."""

    def test_sort_senses_by_gloss(self, mock_flex_project, mock_lex_entry):
        """Test sorting senses by gloss (mock behavior)."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        # Generate test senses with different glosses
        senses = generate_test_senses(mock_lex_entry, count=3)

        # Update glosses to test sorting
        senses[0].Gloss = MockMultiString({"en": "zebra"})
        senses[1].Gloss = MockMultiString({"en": "apple"})
        senses[2].Gloss = MockMultiString({"en": "banana"})

        ops = LexSenseOperations(mock_flex_project)

        # Sort method exists
        assert hasattr(ops, "Sort")
        assert callable(ops.Sort)

    def test_moveup_sense(self, mock_flex_project, mock_lex_entry):
        """Test moving a sense up in the sequence."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations

        # Generate test senses
        senses = generate_test_senses(mock_lex_entry, count=3)

        ops = LexSenseOperations(mock_flex_project)

        # MoveUp method exists
        assert hasattr(ops, "MoveUp")
        assert callable(ops.MoveUp)

        # Test actual move (using mock sequence)
        result = ops.MoveUp(mock_lex_entry, senses[2], positions=1)

        # Should return number of positions moved
        assert result == 1

        # Sense should now be at index 1
        assert mock_lex_entry.SensesOS[1] == senses[2]


class TestLexSenseOperationsValidation:
    """Test validation and error handling."""

    def test_create_requires_write_enabled(self, mock_flex_project, mock_lex_entry):
        """Test that Create raises error when project is read-only."""
        from flexlibs2.code.Lexicon.LexSenseOperations import LexSenseOperations
        from flexlibs2.code.FLExProject import FP_ReadOnlyError

        # Set project to read-only
        mock_flex_project.writeEnabled = False

        ops = LexSenseOperations(mock_flex_project)

        # Should raise FP_ReadOnlyError
        with pytest.raises(FP_ReadOnlyError):
            ops.Create(mock_lex_entry, "test gloss")


# =============================================================================
# INTEGRATION TESTS - Require Real FLEx Project
# =============================================================================


@pytest.mark.integration
@pytest.mark.requires_live_project
class TestLexSenseOperationsIntegration:
    """
    Integration tests that require a real FLEx project.

    Run with: pytest -m integration
    """

    @pytest.fixture(scope="class")
    def flex_project(self):
        """Setup real FLEx project for integration testing."""
        pytest.importorskip("flexlibs")

        from flexlibs2 import FLExInitialize, FLExCleanup, FLExProject, AllProjectNames

        FLExInitialize()
        projects = AllProjectNames()
        if not projects:
            pytest.skip("No FLEx projects available")

        project = FLExProject()
        project.OpenProject(projects[0], writeEnabled=True)

        yield project

        project.CloseProject()
        FLExCleanup()

    def test_create_and_delete_sense(self, flex_project):
        """Integration test: Create and delete a sense."""
        # Get or create test entry
        entries = list(flex_project.LexEntry.GetAll())
        if not entries:
            pytest.skip("No entries available for testing")

        entry = entries[0]

        # Create sense
        sense = flex_project.Senses.Create(entry, "test_gloss_123")
        assert sense is not None

        # Verify gloss
        gloss = flex_project.Senses.GetGloss(sense)
        assert "test_gloss_123" in gloss

        # Delete sense
        flex_project.Senses.Delete(sense)


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test (requires real FLEx)")


# =============================================================================
# PHASE 2 REGRESSION TESTS - Issue #7
# =============================================================================
#
# Issue #7 (orphan-NPE in LexSenseOperations.SetPartOfSpeech): when a sense
# had no existing MSA, the code did
#       new_msa = factory.Create()
#       new_msa.PartOfSpeechRA = pos_obj      # NPE here — MSA was orphan
#       sense.MorphoSyntaxAnalysisRA = new_msa
# LCM forbids property writes on unowned objects. The Phase 2 fix attaches
# the MSA to entry.MorphoSyntaxAnalysesOC FIRST, then sets its properties.
#
# These tests require a live FLEx project — see writable_project fixture.

_CANDIDATE_PROJECTS = ("Sena 3", "Test", "SampleLexicon", "SampleLexicon3")


def _try_open_writable_project():
    """Open a candidate FLEx project in write-enabled mode, or None."""
    try:
        from flexlibs2.code.FLExProject import FLExProject
    except Exception:
        return None

    project = FLExProject()
    for name in _CANDIDATE_PROJECTS:
        try:
            project.OpenProject(name, writeEnabled=True)
            return project
        except Exception:
            continue
    return None


@pytest.fixture(scope="module")
def writable_project():
    """
    Module-scoped fixture providing a write-enabled FLExProject.

    Skips dependent tests if SIL.LCModel isn't loaded or no candidate
    FieldWorks project can be opened. Matches the Phase 1 fixture style
    from tests/test_flexproject_discoverability.py.
    """
    if "SIL.LCModel" not in sys.modules:
        pytest.skip("Requires SIL.LCModel (FieldWorks installed)")

    project = _try_open_writable_project()
    if project is None:
        pytest.skip(
            "No writable FieldWorks project available "
            f"(tried: {', '.join(_CANDIDATE_PROJECTS)})"
        )

    yield project

    try:
        project.CloseProject()
    except Exception:
        pass


@pytest.mark.requires_live_project
class TestLexSenseSetPartOfSpeechRegression:
    """
    Regression coverage for issue #7: LexSenseOperations.SetPartOfSpeech()
    must attach a freshly created MSA to entry.MorphoSyntaxAnalysesOC before
    assigning PartOfSpeechRA on it. Previously the MSA was an orphan when
    PartOfSpeechRA was set, which raised a NullReferenceException.
    """

    def test_set_part_of_speech_on_new_sense(self, writable_project):
        """
        Issue #7 reproducer: a new entry's blank sense has no MSA, so
        SetPartOfSpeech() must create a new IMoStemMsa, attach it to the
        entry, set PartOfSpeechRA, and link sense.MorphoSyntaxAnalysisRA —
        all without an orphan NPE.
        """
        # Use a unique lexeme form so the test is idempotent and doesn't
        # collide with whatever is already in the sample project.
        lexeme = "phase2regrentry"

        # Pre-clean: if a previous run left this entry behind, delete it.
        existing = writable_project.LexEntry.Find(lexeme)
        if existing is not None:
            writable_project.LexEntry.Delete(existing)

        # Find or fall back to creating a target POS. Most sample projects
        # ship with "Noun" preloaded; we don't insist on a particular name.
        pos = writable_project.POS.Find("Noun")
        if pos is None:
            # Pick any existing POS so we don't introduce taxonomy noise.
            all_pos = list(writable_project.POS.GetAll())
            if not all_pos:
                pytest.skip("Project has no Parts of Speech to assign")
            pos = all_pos[0]
        pos_name = writable_project.POS.GetName(pos)

        # Create blank entry (auto-creates one blank sense with no MSA).
        entry = writable_project.LexEntry.Create(lexeme)
        try:
            senses = list(writable_project.Senses.GetAll(entry))
            assert senses, "LexEntry.Create did not create a blank sense"
            sense = senses[0]

            # Act: this is the call that previously NPE'd.
            writable_project.Senses.SetPartOfSpeech(sense, pos)

            # Assert: GetPartOfSpeech now returns a non-empty abbreviation
            # for this sense (proves the MSA was attached and linked).
            result = writable_project.Senses.GetPartOfSpeech(sense)
            assert result, (
                "GetPartOfSpeech returned empty/None after SetPartOfSpeech "
                f"— expected POS abbreviation for '{pos_name}'"
            )
        finally:
            # Cleanup: delete the entry (also drops its sense + MSA).
            try:
                writable_project.LexEntry.Delete(entry)
            except Exception:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not integration"])
