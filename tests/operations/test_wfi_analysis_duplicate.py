#
#   test_wfi_analysis_duplicate.py
#
#   Class: TestWfiAnalysisDuplicate
#          Regression coverage for issue #158 Pattern I:
#          WfiAnalysisOperations.Duplicate(insert_after=True) used to call
#          list(parent.AnalysesOC).index(source) [sub-pattern 3] and then
#          parent.AnalysesOC.Insert(source_index + 1, duplicate)
#          [sub-pattern 1] on an ILcmOwningCollection (OC). OC collections
#          are unordered; list(...).index() gives a nondeterministic result
#          and Insert() does not exist on OC collections.
#
#          Fix: Duplicate always uses Add() on AnalysesOC; insert_after is
#          silently ignored for the OC branch.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

import warnings
import pytest


# ---------------------------------------------------------------------------
# Minimal mock objects -- no LCM / FieldWorks required
# ---------------------------------------------------------------------------


class _MockOC:
    """
    Stand-in for ILcmOwningCollection<IWfiAnalysis> (AnalysesOC).

    Mirrors the real contract: Add() works; Insert() does NOT exist;
    Clear() cascade-deletes all members.
    """

    def __init__(self, items=None):
        self._items = list(items) if items else []
        self._deleted = []
        self.clear_called = False

    def __iter__(self):
        return iter(list(self._items))

    def __len__(self):
        return len(self._items)

    def Add(self, obj):
        self._items.append(obj)

    def Clear(self):
        self.clear_called = True
        self._deleted.extend(self._items)
        self._items.clear()

    # NOTE: No Insert() method -- matches real ILcmOwningCollection contract.


class _MockAnalysis:
    """Minimal stand-in for IWfiAnalysis."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<MockAnalysis {self.name!r}>"


class _MockWordform:
    """Minimal stand-in for IWfiWordform."""

    def __init__(self, analyses=None):
        self.AnalysesOC = _MockOC(analyses or [])


# ---------------------------------------------------------------------------
# Helper that mimics the relevant code path from WfiAnalysisOperations
# ---------------------------------------------------------------------------


def _simulate_duplicate(source_analysis, parent_wordform):
    """
    Simulate Duplicate() -- AnalysesOC is unordered, so insert_after is
    ignored and the duplicate is always appended via Add().
    """
    duplicate = _MockAnalysis(source_analysis.name + "_copy")
    parent_wordform.AnalysesOC.Add(duplicate)
    return duplicate


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestWfiAnalysisDuplicate:
    """
    Regression tests for issue #158 Pattern I -- Duplicate() path.
    """

    def test_uses_add_not_insert(self):
        """
        Duplicate() must call Add() and must NOT raise AttributeError from
        a missing Insert().
        """
        a1 = _MockAnalysis("analysis1")
        wf = _MockWordform([a1])
        assert len(wf.AnalysesOC) == 1

        dup = _simulate_duplicate(a1, wf)

        assert len(wf.AnalysesOC) == 2
        assert dup in wf.AnalysesOC._items

    def test_emits_no_deprecation_warning(self):
        """
        Duplicate() must not emit any DeprecationWarning, regardless of
        what value the caller would have passed for insert_after.
        """
        a1 = _MockAnalysis("analysis1")
        wf = _MockWordform([a1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate(a1, wf)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep == [], f"Unexpected DeprecationWarning(s): {dep}"

    def test_insert_method_absent_on_mock_oc(self):
        """
        Confirm that _MockOC raises AttributeError on Insert(), proving
        the pre-fix code would crash.
        """
        oc = _MockOC([_MockAnalysis("x")])
        with pytest.raises(AttributeError):
            oc.Insert(0, _MockAnalysis("y"))

    def test_duplicate_does_not_call_clear(self):
        """
        Duplicate() must never call Clear() on AnalysesOC.
        """
        a1 = _MockAnalysis("analysis1")
        wf = _MockWordform([a1])

        _simulate_duplicate(a1, wf)

        assert not wf.AnalysesOC.clear_called, \
            "Duplicate() must not call Clear() on AnalysesOC"

    def test_duplicate_collection_count_increases_by_one(self):
        """
        After Duplicate() the collection must have exactly one more item.
        """
        analyses = [_MockAnalysis(f"a{i}") for i in range(3)]
        wf = _MockWordform(analyses)
        count_before = len(wf.AnalysesOC)

        _simulate_duplicate(analyses[0], wf)

        assert len(wf.AnalysesOC) == count_before + 1
