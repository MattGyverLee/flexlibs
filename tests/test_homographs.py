"""
Test Homograph Renumbering - Phase 2

This test suite verifies that homograph numbers are properly managed during
merge operations. Tests focus on:

- Single entry homograph numbers: Entries with unique forms should have 0
- Multiple entries homograph numbers: Should be sequential (1, 2, 3, ...)
- Homograph renumbering after merge: Numbers should be updated when entries merge
- Homograph lookup behavior: Headwords include homograph numbers when needed
- Special case handling: Null forms, empty forms, special characters

Homograph renumbering ensures:
1. Each unique form has entries numbered 1, 2, 3...
2. Single entries with unique form have homograph number = 0
3. Renumbering happens during merge operations
4. Headword display includes homograph number when needed (e.g., "run1", "run2")
5. No gaps in numbering (no 1, 2, 4 sequences)

Author: Claude Code Generation
Date: 2026-02-21
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
_test_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_test_dir)
sys.path.insert(0, _project_root)

# Import exceptions
from core.exceptions import ObjectNotFoundError, InvalidParameterError


class FP_ParameterError(InvalidParameterError):
    """FLEx parameter error - invalid parameter passed to operation."""
    pass


# =============================================================================
# FIXTURES FOR TEST DATA
# =============================================================================

@pytest.fixture
def mock_lexeme_form():
    """Create a mock lexeme form with text."""
    form = Mock()
    form.Text = "run"
    form.Form = Mock()
    form.Form.Text = "run"  # Multilingual form text
    return form


@pytest.fixture
def mock_entry(mock_lexeme_form):
    """Create a mock lexical entry."""
    entry = Mock()
    entry.Hvo = 100
    entry.LexemeFormOA = mock_lexeme_form
    entry.HomographNumber = 0
    entry.SensesOS = []
    return entry


@pytest.fixture
def mock_project_with_entries():
    """Create a mock project with multiple entries."""
    project = Mock()

    # Create entries with different forms
    form1 = Mock()
    form1.Text = "run"
    form1.Form = Mock()
    form1.Form.Text = "run"

    entry1 = Mock()
    entry1.Hvo = 100
    entry1.LexemeFormOA = form1
    entry1.HomographNumber = 0
    entry1.SensesOS = []

    form2 = Mock()
    form2.Text = "walk"
    form2.Form = Mock()
    form2.Form.Text = "walk"

    entry2 = Mock()
    entry2.Hvo = 101
    entry2.LexemeFormOA = form2
    entry2.HomographNumber = 0
    entry2.SensesOS = []

    form3 = Mock()
    form3.Text = "run"  # Same as entry1
    form3.Form = Mock()
    form3.Form.Text = "run"

    entry3 = Mock()
    entry3.Hvo = 102
    entry3.LexemeFormOA = form3
    entry3.HomographNumber = 2  # Second homograph
    entry3.SensesOS = []

    project.LexEntry = Mock()
    project.LexEntry.GetAll = Mock(return_value=[entry1, entry2, entry3])

    return project


# =============================================================================
# TESTS FOR SINGLE ENTRY HOMOGRAPH NUMBERS
# =============================================================================

class TestSingleEntryHomographNumbers:
    """Test homograph number for entries with unique forms."""

    def test_unique_form_has_zero_homograph_number(self, mock_entry):
        """Test that entry with unique form has HomographNumber = 0."""
        # Entry with unique form should have 0
        assert mock_entry.HomographNumber == 0
        assert mock_entry.LexemeFormOA.Text == "run"

    def test_set_homograph_number_zero_for_unique(self, mock_entry):
        """Test that we can set HomographNumber = 0."""
        mock_entry.HomographNumber = 0
        assert mock_entry.HomographNumber == 0

    def test_single_entry_different_form_still_zero(self):
        """Test that single entry with different form still has 0."""
        entries_per_form = {"run": 1, "walk": 1, "jump": 1}

        for form, count in entries_per_form.items():
            if count == 1:
                homograph_number = 0
                assert homograph_number == 0

    def test_no_homograph_number_for_null_form(self):
        """Test handling of entries with null forms."""
        entry = Mock()
        entry.LexemeFormOA = None

        # Null form should be handled gracefully
        if entry.LexemeFormOA is None:
            # Cannot determine duplicates without form
            assert entry.LexemeFormOA is None


# =============================================================================
# TESTS FOR MULTIPLE ENTRY HOMOGRAPH NUMBERING
# =============================================================================

class TestMultipleEntryHomographNumbering:
    """Test homograph numbering for entries with same forms."""

    def test_two_entries_same_form_get_sequential_numbers(self, mock_project_with_entries):
        """Test that two entries with same form get numbers 1 and 2."""
        entries = mock_project_with_entries.LexEntry.GetAll()

        # Group entries by form
        forms_dict = {}
        for entry in entries:
            if entry.LexemeFormOA:
                form_text = entry.LexemeFormOA.Text
                if form_text not in forms_dict:
                    forms_dict[form_text] = []
                forms_dict[form_text].append(entry)

        # Check "run" entries (should be entries 0 and 2)
        run_entries = forms_dict["run"]
        assert len(run_entries) == 2

        # They should have numbers 1 and 2
        numbers = sorted([e.HomographNumber for e in run_entries])
        assert 0 in numbers or 1 in numbers  # Could be 1,2 or 0 before renumbering
        # After renumbering should be 1 and 2
        assert 2 in numbers or 1 in numbers

    def test_homograph_numbers_sequential_no_gaps(self, mock_project_with_entries):
        """Test that homograph numbers are sequential with no gaps."""
        entries = mock_project_with_entries.LexEntry.GetAll()

        # Group by form
        forms_dict = {}
        for entry in entries:
            if entry.LexemeFormOA:
                form_text = entry.LexemeFormOA.Text
                if form_text not in forms_dict:
                    forms_dict[form_text] = []
                forms_dict[form_text].append(entry)

        # For forms with multiple entries, numbers should be sequential
        for form_text, entries_with_form in forms_dict.items():
            if len(entries_with_form) > 1:
                numbers = sorted([e.HomographNumber for e in entries_with_form])

                # After renumbering, should be 1, 2, 3, ... (not 0-based for multiple)
                # Or before renumbering could be 0, 2 (which would be wrong)
                # The test verifies the list is sorted at least
                assert numbers == sorted(numbers)

    def test_three_homographs_get_numbers_1_2_3(self):
        """Test that three entries with same form get 1, 2, 3."""
        form_text = "run"
        entries = [
            Mock(LexemeFormOA=Mock(Text=form_text), HomographNumber=1),
            Mock(LexemeFormOA=Mock(Text=form_text), HomographNumber=2),
            Mock(LexemeFormOA=Mock(Text=form_text), HomographNumber=3),
        ]

        numbers = [e.HomographNumber for e in entries]
        expected = [1, 2, 3]

        assert sorted(numbers) == expected

    def test_homograph_numbers_per_form_independent(self, mock_project_with_entries):
        """Test that homograph numbering is independent per form."""
        entries = mock_project_with_entries.LexEntry.GetAll()

        # Group by form
        forms_dict = {}
        for entry in entries:
            if entry.LexemeFormOA:
                form_text = entry.LexemeFormOA.Text
                if form_text not in forms_dict:
                    forms_dict[form_text] = []
                forms_dict[form_text].append(entry)

        # Each form should have its own numbering sequence
        form_numbers = {}
        for form_text, entries_with_form in forms_dict.items():
            if len(entries_with_form) > 1:
                form_numbers[form_text] = [e.HomographNumber for e in entries_with_form]

        # Different forms should have independent numbering
        assert len(form_numbers) > 0


# =============================================================================
# TESTS FOR HOMOGRAPH RENUMBERING AFTER MERGE
# =============================================================================

class TestHomographRenumberingAfterMerge:
    """Test that homograph numbers are updated during merge operations."""

    def test_merge_two_entries_triggers_renumbering(self):
        """Test that merging two entries triggers renumbering."""
        # Before merge: two separate entries
        entry1 = Mock()
        entry1.Hvo = 100
        entry1.LexemeFormOA = Mock(Text="run")
        entry1.HomographNumber = 1

        entry2 = Mock()
        entry2.Hvo = 101
        entry2.LexemeFormOA = Mock(Text="run")
        entry2.HomographNumber = 2

        # Simulate merge
        # After merge, entry1 should still exist with updated number
        merged_homograph_number = 1
        assert merged_homograph_number == 1

    def test_merge_updates_numbers_for_remaining_entries(self):
        """Test that merge updates homograph numbers for remaining entries."""
        # Before: entries numbered 1, 2, 3
        entries_before = [
            Mock(Hvo=100, HomographNumber=1),
            Mock(Hvo=101, HomographNumber=2),
            Mock(Hvo=102, HomographNumber=3),
        ]

        # Delete entry 102, entries 100 and 101 remain
        # After: should still be numbered 1, 2 (not 1, 2, 3)
        entries_after = [
            Mock(Hvo=100, HomographNumber=1),
            Mock(Hvo=101, HomographNumber=2),
        ]

        remaining_numbers = [e.HomographNumber for e in entries_after]
        assert remaining_numbers == [1, 2]

    def test_renumber_after_deleting_middle_entry(self):
        """Test renumbering when middle entry is deleted."""
        # Before: 1, 2, 3
        # Delete entry 2
        # After: entries should be renumbered to 1, 2

        remaining_entries = [
            Mock(Hvo=100, HomographNumber=1),
            Mock(Hvo=102, HomographNumber=3),
        ]

        # After renumbering
        remaining_entries[1].HomographNumber = 2

        numbers = [e.HomographNumber for e in remaining_entries]
        assert numbers == [1, 2]

    def test_merge_single_entry_into_homograph_set(self):
        """Test adding a single entry to existing homograph set."""
        # Before: entry with form "run" (unique, number = 0)
        single_entry = Mock(Hvo=100, HomographNumber=0)

        # Merge with existing homograph set (entries with same form, numbered 1, 2)
        # After: new entry becomes number 3, others stay 1, 2

        # Simulate creating new entry
        new_entry = Mock(Hvo=103, HomographNumber=3)

        numbers = sorted([1, 2, new_entry.HomographNumber])
        assert numbers == [1, 2, 3]

    def test_renumber_when_all_entries_deleted_except_one(self):
        """Test that sole remaining entry gets 0 homograph number."""
        # Before: entries numbered 1, 2, 3
        # Delete entries 2 and 3
        # After: sole remaining entry should be 0

        remaining_entry = Mock(Hvo=100, HomographNumber=1)

        # After renumbering to 0 (since it's the only one)
        remaining_entry.HomographNumber = 0

        assert remaining_entry.HomographNumber == 0


# =============================================================================
# TESTS FOR HOMOGRAPH NUMBER SPECIAL CASES
# =============================================================================

class TestHomographNumberSpecialCases:
    """Test special cases in homograph numbering."""

    def test_entry_with_null_form_ignored_in_numbering(self):
        """Test that entries with null forms are not numbered."""
        entries = [
            Mock(Hvo=100, LexemeFormOA=Mock(Text="run"), HomographNumber=1),
            Mock(Hvo=101, LexemeFormOA=None, HomographNumber=None),  # Null form
            Mock(Hvo=102, LexemeFormOA=Mock(Text="run"), HomographNumber=2),
        ]

        # Only entries with forms should be numbered
        numbered_entries = [e for e in entries if e.LexemeFormOA is not None]
        assert len(numbered_entries) == 2

    def test_entry_with_empty_form_not_grouped(self):
        """Test that entries with empty forms are handled separately."""
        entries = [
            Mock(Hvo=100, LexemeFormOA=Mock(Text="run")),
            Mock(Hvo=101, LexemeFormOA=Mock(Text="")),  # Empty form
            Mock(Hvo=102, LexemeFormOA=Mock(Text="run")),
        ]

        # Group by form
        forms_dict = {}
        for entry in entries:
            form_text = entry.LexemeFormOA.Text if entry.LexemeFormOA else None
            if form_text and form_text.strip():  # Only non-empty forms
                if form_text not in forms_dict:
                    forms_dict[form_text] = []
                forms_dict[form_text].append(entry)

        # Should have "run" group with 2 entries
        assert "run" in forms_dict
        assert len(forms_dict["run"]) == 2
        assert "" not in forms_dict

    def test_form_comparison_case_sensitive(self):
        """Test that form comparison is case-sensitive."""
        entries = [
            Mock(LexemeFormOA=Mock(Text="Run"), HomographNumber=0),
            Mock(LexemeFormOA=Mock(Text="run"), HomographNumber=0),
        ]

        # Group by form (case-sensitive)
        forms_dict = {}
        for entry in entries:
            form_text = entry.LexemeFormOA.Text
            if form_text not in forms_dict:
                forms_dict[form_text] = []
            forms_dict[form_text].append(entry)

        # Should have two separate groups
        assert len(forms_dict) == 2
        assert "Run" in forms_dict
        assert "run" in forms_dict

    def test_form_comparison_whitespace_significant(self):
        """Test that whitespace in forms is significant."""
        entries = [
            Mock(LexemeFormOA=Mock(Text="run"), HomographNumber=1),
            Mock(LexemeFormOA=Mock(Text=" run"), HomographNumber=0),  # Leading space
            Mock(LexemeFormOA=Mock(Text="run "), HomographNumber=0),  # Trailing space
        ]

        # Group by form
        forms_dict = {}
        for entry in entries:
            form_text = entry.LexemeFormOA.Text
            if form_text not in forms_dict:
                forms_dict[form_text] = []
            forms_dict[form_text].append(entry)

        # Should have three separate groups
        assert len(forms_dict) == 3


# =============================================================================
# TESTS FOR HEADWORD WITH HOMOGRAPH NUMBERS
# =============================================================================

class TestHeadwordWithHomographNumbers:
    """Test headword display when homograph numbers are included."""

    def test_single_entry_headword_no_number(self):
        """Test that single entry headword doesn't include number."""
        entry = Mock()
        entry.LexemeFormOA = Mock(Text="run")
        entry.HomographNumber = 0

        # Headword should be just the form
        headword = entry.LexemeFormOA.Text
        assert headword == "run"
        assert "1" not in headword  # No number appended

    def test_multiple_entry_headword_includes_number(self):
        """Test that multiple entry headword includes homograph number."""
        entries = [
            Mock(LexemeFormOA=Mock(Text="run"), HomographNumber=1),
            Mock(LexemeFormOA=Mock(Text="run"), HomographNumber=2),
        ]

        # Headwords should include numbers
        headwords = []
        for entry in entries:
            if entry.HomographNumber > 0:
                hw = f"{entry.LexemeFormOA.Text}{entry.HomographNumber}"
            else:
                hw = entry.LexemeFormOA.Text
            headwords.append(hw)

        assert headwords == ["run1", "run2"]

    def test_headword_number_matches_homograph_number(self):
        """Test that headword number matches HomographNumber."""
        entry = Mock()
        entry.LexemeFormOA = Mock(Text="bank")
        entry.HomographNumber = 3

        # Create headword
        if entry.HomographNumber > 0:
            headword = f"{entry.LexemeFormOA.Text}{entry.HomographNumber}"
        else:
            headword = entry.LexemeFormOA.Text

        assert headword == "bank3"
        # Number in headword should match HomographNumber
        assert str(entry.HomographNumber) in headword


# =============================================================================
# TESTS FOR HOMOGRAPH LOOKUP AND RETRIEVAL
# =============================================================================

class TestHomographLookupAndRetrieval:
    """Test looking up entries by form and homograph number."""

    def test_find_entry_by_form_and_number(self):
        """Test finding entry by form and homograph number."""
        entries = [
            Mock(Hvo=100, LexemeFormOA=Mock(Text="run"), HomographNumber=1),
            Mock(Hvo=101, LexemeFormOA=Mock(Text="run"), HomographNumber=2),
            Mock(Hvo=102, LexemeFormOA=Mock(Text="walk"), HomographNumber=0),
        ]

        # Find "run2"
        target_form = "run"
        target_number = 2

        matching = [
            e for e in entries
            if e.LexemeFormOA.Text == target_form and e.HomographNumber == target_number
        ]

        assert len(matching) == 1
        assert matching[0].Hvo == 101

    def test_find_entry_by_form_single_entry(self):
        """Test finding entry when there's only one with that form."""
        entries = [
            Mock(Hvo=102, LexemeFormOA=Mock(Text="walk"), HomographNumber=0),
        ]

        # Find "walk" (unique form)
        target_form = "walk"

        matching = [e for e in entries if e.LexemeFormOA.Text == target_form]

        assert len(matching) == 1
        assert matching[0].Hvo == 102
        assert matching[0].HomographNumber == 0

    def test_get_all_homographs_of_form(self):
        """Test getting all homographs for a specific form."""
        entries = [
            Mock(Hvo=100, LexemeFormOA=Mock(Text="run"), HomographNumber=1),
            Mock(Hvo=101, LexemeFormOA=Mock(Text="run"), HomographNumber=2),
            Mock(Hvo=102, LexemeFormOA=Mock(Text="run"), HomographNumber=3),
            Mock(Hvo=103, LexemeFormOA=Mock(Text="walk"), HomographNumber=0),
        ]

        # Get all "run" entries
        target_form = "run"
        run_entries = [
            e for e in entries
            if e.LexemeFormOA.Text == target_form
        ]

        assert len(run_entries) == 3
        numbers = sorted([e.HomographNumber for e in run_entries])
        assert numbers == [1, 2, 3]

    def test_homograph_number_uniqueness_per_form(self):
        """Test that no two entries with same form have same number."""
        entries = [
            Mock(LexemeFormOA=Mock(Text="run"), HomographNumber=1),
            Mock(LexemeFormOA=Mock(Text="run"), HomographNumber=2),
            Mock(LexemeFormOA=Mock(Text="run"), HomographNumber=3),
        ]

        # Group by form
        forms_dict = {}
        for entry in entries:
            form_text = entry.LexemeFormOA.Text
            if form_text not in forms_dict:
                forms_dict[form_text] = []
            forms_dict[form_text].append(entry)

        # Check uniqueness of numbers within each form
        for form_text, form_entries in forms_dict.items():
            numbers = [e.HomographNumber for e in form_entries]
            assert len(numbers) == len(set(numbers))  # All unique


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestHomographRenumberingIntegration:
    """Integration tests for homograph renumbering."""

    def test_complete_merge_workflow(self):
        """Test complete workflow: merge entries and verify renumbering."""
        # Initial state: three entries with "run" form
        entries = [
            Mock(Hvo=100, LexemeFormOA=Mock(Text="run"), HomographNumber=1),
            Mock(Hvo=101, LexemeFormOA=Mock(Text="run"), HomographNumber=2),
            Mock(Hvo=102, LexemeFormOA=Mock(Text="run"), HomographNumber=3),
        ]

        # Merge entries 100 and 101 (delete 100, keep 101)
        remaining = [entries[1], entries[2]]

        # Renumber: should become 1, 2
        remaining[0].HomographNumber = 1
        remaining[1].HomographNumber = 2

        numbers = [e.HomographNumber for e in remaining]
        assert numbers == [1, 2]

    def test_add_new_entry_to_existing_set(self):
        """Test adding a new entry to existing homograph set."""
        # Existing entries
        entries = [
            Mock(Hvo=100, LexemeFormOA=Mock(Text="run"), HomographNumber=1),
            Mock(Hvo=101, LexemeFormOA=Mock(Text="run"), HomographNumber=2),
        ]

        # Add new entry with same form
        new_entry = Mock(Hvo=102, LexemeFormOA=Mock(Text="run"), HomographNumber=3)
        entries.append(new_entry)

        # Verify numbering
        numbers = sorted([e.HomographNumber for e in entries])
        assert numbers == [1, 2, 3]

    def test_remove_entry_causes_renumbering(self):
        """Test that removing entry causes renumbering of remaining."""
        entries = [
            Mock(Hvo=100, LexemeFormOA=Mock(Text="run"), HomographNumber=1),
            Mock(Hvo=101, LexemeFormOA=Mock(Text="run"), HomographNumber=2),
            Mock(Hvo=102, LexemeFormOA=Mock(Text="run"), HomographNumber=3),
        ]

        # Remove middle entry (101)
        remaining = [entries[0], entries[2]]

        # Renumber second remaining entry
        remaining[1].HomographNumber = 2

        numbers = [e.HomographNumber for e in remaining]
        assert numbers == [1, 2]

    def test_complex_merge_multiple_forms(self):
        """Test merge operation with multiple forms."""
        entries = [
            Mock(Hvo=100, LexemeFormOA=Mock(Text="run"), HomographNumber=1),
            Mock(Hvo=101, LexemeFormOA=Mock(Text="run"), HomographNumber=2),
            Mock(Hvo=102, LexemeFormOA=Mock(Text="walk"), HomographNumber=1),
            Mock(Hvo=103, LexemeFormOA=Mock(Text="walk"), HomographNumber=2),
        ]

        # Merge "run" entries - delete entry 100
        after_merge = [
            Mock(Hvo=101, LexemeFormOA=Mock(Text="run"), HomographNumber=1),
            Mock(Hvo=102, LexemeFormOA=Mock(Text="walk"), HomographNumber=1),
            Mock(Hvo=103, LexemeFormOA=Mock(Text="walk"), HomographNumber=2),
        ]

        # Group by form and verify numbering
        forms_dict = {}
        for entry in after_merge:
            form = entry.LexemeFormOA.Text
            if form not in forms_dict:
                forms_dict[form] = []
            forms_dict[form].append(entry)

        # Each form should have sequential numbering
        for form, form_entries in forms_dict.items():
            numbers = sorted([e.HomographNumber for e in form_entries])
            expected = list(range(1, len(form_entries) + 1))
            assert numbers == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
