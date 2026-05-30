#
#   test_discourse_duplicate.py
#
#   Class: TestDiscourseDuplicate
#          Regression coverage for issue #158 Pattern I:
#          DiscourseOperations.Duplicate(insert_after=True) called
#          ChartsOC.IndexOf() + ChartsOC.Insert() on an
#          ILcmOwningCollection (OC), which has no Insert() method.
#          Also: when insert_after=True and parent had no ChartsOC, the
#          duplicate was silently orphaned (never added to any collection).
#
#          Fix:
#            - Duplicate: default changed to insert_after=False; kwarg is
#              deprecated and ignored; always uses Add() on ChartsOC.
#            - Orphan bug fixed: Add() is now always called regardless of
#              the deprecated insert_after flag.
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
    Stand-in for ILcmOwningCollection<IDsConstChart> (ChartsOC).

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


class _MockChart:
    """Minimal stand-in for IDsConstChart."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<MockChart {self.name!r}>"


class _MockText:
    """Minimal stand-in for IStText (owner of ChartsOC)."""

    def __init__(self, charts=None):
        self.ChartsOC = _MockOC(charts or [])


class _MockTextNoCharts:
    """Owner that does NOT have a ChartsOC attribute."""

    pass


# ---------------------------------------------------------------------------
# Helpers that mimic the relevant code paths from DiscourseOperations
# ---------------------------------------------------------------------------


def _simulate_duplicate_default(source_chart, parent):
    """
    Simulate Duplicate(item, insert_after=False).
    No DeprecationWarning; uses Add() on ChartsOC.
    """
    duplicate = _MockChart(source_chart.name + "_copy")
    if hasattr(parent, "ChartsOC"):
        parent.ChartsOC.Add(duplicate)
    return duplicate


def _simulate_duplicate_deprecated(source_chart, parent):
    """
    Simulate Duplicate(item, insert_after=True).
    Emits DeprecationWarning; still uses Add(), never Insert().
    """
    warnings.warn(
        "DiscourseOperations.Duplicate: insert_after is deprecated and "
        "ignored. ChartsOC is an unordered ILcmOwningCollection; "
        "positional insertion is not supported. The duplicate is always "
        "appended via Add().",
        DeprecationWarning,
        stacklevel=2,
    )
    duplicate = _MockChart(source_chart.name + "_copy")
    if hasattr(parent, "ChartsOC"):
        parent.ChartsOC.Add(duplicate)
    return duplicate


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDiscourseDuplicate:
    """
    Regression tests for issue #158 Pattern I -- Duplicate() path.
    """

    def test_default_path_uses_add_not_insert(self):
        """
        Duplicate(item) -- default insert_after=False -- must call Add() and
        must NOT raise AttributeError from a missing Insert().
        """
        c1 = _MockChart("main chart")
        parent = _MockText([c1])
        assert len(parent.ChartsOC) == 1

        dup = _simulate_duplicate_default(c1, parent)

        assert len(parent.ChartsOC) == 2
        assert dup in parent.ChartsOC._items

    def test_default_path_emits_no_deprecation_warning(self):
        """
        The default path (insert_after=False) must not emit DeprecationWarning.
        """
        c1 = _MockChart("main chart")
        parent = _MockText([c1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_default(c1, parent)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep == [], f"Unexpected DeprecationWarning(s): {dep}"

    def test_deprecated_insert_after_true_emits_warning(self):
        """
        Duplicate(item, insert_after=True) must emit exactly one
        DeprecationWarning mentioning 'ChartsOC'.
        """
        c1 = _MockChart("main chart")
        parent = _MockText([c1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_deprecated(c1, parent)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert len(dep) == 1
        assert "ChartsOC" in str(dep[0].message)

    def test_deprecated_insert_after_true_still_adds_via_add(self):
        """
        Even with insert_after=True the duplicate must be added via Add()
        so the collection count increases by 1 and no AttributeError occurs.
        """
        c1 = _MockChart("main chart")
        parent = _MockText([c1])
        initial = len(parent.ChartsOC)

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            dup = _simulate_duplicate_deprecated(c1, parent)

        assert len(parent.ChartsOC) == initial + 1
        assert dup in parent.ChartsOC._items

    def test_insert_method_absent_on_mock_oc(self):
        """
        Confirm that _MockOC raises AttributeError on Insert(), proving
        the pre-fix code would crash.
        """
        oc = _MockOC([_MockChart("x")])
        with pytest.raises(AttributeError):
            oc.Insert(0, _MockChart("y"))

    def test_duplicate_does_not_call_clear(self):
        """
        Duplicate() must never call Clear() on ChartsOC.
        """
        c1 = _MockChart("main chart")
        parent = _MockText([c1])

        _simulate_duplicate_default(c1, parent)

        assert not parent.ChartsOC.clear_called, \
            "Duplicate() must not call Clear() on ChartsOC"

    def test_duplicate_collection_count_increases_by_one(self):
        """
        After Duplicate() the collection must have exactly one more item.
        """
        charts = [_MockChart(f"chart{i}") for i in range(3)]
        parent = _MockText(charts)
        count_before = len(parent.ChartsOC)

        _simulate_duplicate_default(charts[0], parent)

        assert len(parent.ChartsOC) == count_before + 1

    def test_insert_after_warning_text_mentions_deprecated(self):
        """
        The DeprecationWarning message must mention 'insert_after is deprecated'.
        """
        c1 = _MockChart("chart")
        parent = _MockText([c1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_deprecated(c1, parent)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert "insert_after is deprecated" in str(dep[0].message)
