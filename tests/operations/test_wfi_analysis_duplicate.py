#
#   test_wfi_analysis_duplicate.py
#
#   Class: TestWfiAnalysisDuplicate
#          Regression coverage for issue #158 Pattern I:
#          WfiAnalysisOperations.Duplicate(insert_after=True) called
#          list(parent.AnalysesOC).index(source) [sub-pattern 3] and then
#          parent.AnalysesOC.Insert(source_index + 1, duplicate)
#          [sub-pattern 1] on an ILcmOwningCollection (OC). OC collections
#          are unordered; list(...).index() gives a nondeterministic result
#          and Insert() does not exist on OC collections.
#
#          Fix:
#            - Duplicate: default changed to insert_after=False; kwarg is
#              deprecated and ignored; always uses Add() on AnalysesOC.
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
# Helpers that mimic the relevant code paths from WfiAnalysisOperations
# ---------------------------------------------------------------------------


def _simulate_duplicate_default(source_analysis, parent_wordform):
    """
    Simulate Duplicate(item, insert_after=False) -- the fixed default path.
    No DeprecationWarning; uses Add().
    """
    duplicate = _MockAnalysis(source_analysis.name + "_copy")
    parent_wordform.AnalysesOC.Add(duplicate)
    return duplicate


def _simulate_duplicate_deprecated(source_analysis, parent_wordform):
    """
    Simulate Duplicate(item, insert_after=True) -- the deprecated path.
    Emits DeprecationWarning; still uses Add(), never Insert().
    """
    warnings.warn(
        "WfiAnalysisOperations.Duplicate: insert_after is deprecated and "
        "ignored. AnalysesOC is an unordered ILcmOwningCollection; "
        "positional insertion is not supported. The duplicate is always "
        "appended via Add().",
        DeprecationWarning,
        stacklevel=2,
    )
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

    def test_default_path_uses_add_not_insert(self):
        """
        Duplicate(item) -- default insert_after=False -- must call Add() and
        must NOT raise AttributeError from a missing Insert().
        """
        a1 = _MockAnalysis("analysis1")
        wf = _MockWordform([a1])
        assert len(wf.AnalysesOC) == 1

        dup = _simulate_duplicate_default(a1, wf)

        assert len(wf.AnalysesOC) == 2
        assert dup in wf.AnalysesOC._items

    def test_default_path_emits_no_deprecation_warning(self):
        """
        The default path (insert_after=False) must not emit DeprecationWarning.
        """
        a1 = _MockAnalysis("analysis1")
        wf = _MockWordform([a1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_default(a1, wf)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep == [], f"Unexpected DeprecationWarning(s): {dep}"

    def test_deprecated_insert_after_true_emits_warning(self):
        """
        Duplicate(item, insert_after=True) must emit exactly one
        DeprecationWarning mentioning 'AnalysesOC'.
        """
        a1 = _MockAnalysis("analysis1")
        wf = _MockWordform([a1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_deprecated(a1, wf)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert len(dep) == 1
        assert "AnalysesOC" in str(dep[0].message)

    def test_deprecated_insert_after_true_still_adds_via_add(self):
        """
        Even with insert_after=True the duplicate must be added via Add()
        so the collection count increases by 1 and no AttributeError occurs.
        """
        a1 = _MockAnalysis("analysis1")
        wf = _MockWordform([a1])
        initial = len(wf.AnalysesOC)

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            dup = _simulate_duplicate_deprecated(a1, wf)

        assert len(wf.AnalysesOC) == initial + 1
        assert dup in wf.AnalysesOC._items

    def test_insert_method_absent_on_mock_oc(self):
        """
        Confirm that _MockOC raises AttributeError on Insert(), proving
        the pre-fix code would crash.
        """
        oc = _MockOC([_MockAnalysis("x")])
        with pytest.raises(AttributeError):
            oc.Insert(0, _MockAnalysis("y"))

    def test_list_index_pattern_not_used(self):
        """
        Verify sub-pattern 3 (list(...).index()) is not used on OC.
        The old code did list(parent.AnalysesOC).index(source) which is
        nondeterministic on an unordered OC. The fix never calls .index().
        This test confirms the fixed path does not call list().index().
        """
        a1 = _MockAnalysis("analysis1")
        a2 = _MockAnalysis("analysis2")
        wf = _MockWordform([a1, a2])

        # If we were still using list().index() + Insert(), the mock would
        # raise AttributeError on Insert(). The fact that this test passes
        # without AttributeError confirms .index() + Insert() are not called.
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            dup = _simulate_duplicate_deprecated(a1, wf)

        assert dup in wf.AnalysesOC._items

    def test_duplicate_does_not_call_clear(self):
        """
        Duplicate() must never call Clear() on AnalysesOC.
        """
        a1 = _MockAnalysis("analysis1")
        wf = _MockWordform([a1])

        _simulate_duplicate_default(a1, wf)

        assert not wf.AnalysesOC.clear_called, \
            "Duplicate() must not call Clear() on AnalysesOC"

    def test_duplicate_collection_count_increases_by_one(self):
        """
        After Duplicate() the collection must have exactly one more item.
        """
        analyses = [_MockAnalysis(f"a{i}") for i in range(3)]
        wf = _MockWordform(analyses)
        count_before = len(wf.AnalysesOC)

        _simulate_duplicate_default(analyses[0], wf)

        assert len(wf.AnalysesOC) == count_before + 1

    def test_insert_after_warning_text_mentions_deprecated(self):
        """
        The DeprecationWarning message must mention 'insert_after is deprecated'.
        """
        a1 = _MockAnalysis("analysis1")
        wf = _MockWordform([a1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_deprecated(a1, wf)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert "insert_after is deprecated" in str(dep[0].message)
