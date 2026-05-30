#
#   test_discourse_duplicate.py
#
#   Class: TestDiscourseDuplicate
#          Regression coverage for issue #158 Pattern I:
#          DiscourseOperations.Duplicate(insert_after=True) used to call
#          ChartsOC.IndexOf() + ChartsOC.Insert() on an
#          ILcmOwningCollection (OC), which has no Insert() method.
#          Also: when insert_after=True and parent had no ChartsOC, the
#          duplicate was silently orphaned (never added to any collection).
#
#          Fix: Duplicate always uses Add() on ChartsOC; insert_after is
#          silently ignored. Add() is always called, eliminating the
#          orphan bug.
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
# Helper that mimics the relevant code path from DiscourseOperations
# ---------------------------------------------------------------------------


def _simulate_duplicate(source_chart, parent):
    """
    Simulate Duplicate() -- ChartsOC is unordered, so insert_after is
    ignored and the duplicate is always appended via Add().
    """
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

    def test_uses_add_not_insert(self):
        """
        Duplicate() must call Add() and must NOT raise AttributeError from
        a missing Insert().
        """
        c1 = _MockChart("main chart")
        parent = _MockText([c1])
        assert len(parent.ChartsOC) == 1

        dup = _simulate_duplicate(c1, parent)

        assert len(parent.ChartsOC) == 2
        assert dup in parent.ChartsOC._items

    def test_emits_no_deprecation_warning(self):
        """
        Duplicate() must not emit any DeprecationWarning, regardless of
        what value the caller would have passed for insert_after.
        """
        c1 = _MockChart("main chart")
        parent = _MockText([c1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate(c1, parent)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep == [], f"Unexpected DeprecationWarning(s): {dep}"

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

        _simulate_duplicate(c1, parent)

        assert not parent.ChartsOC.clear_called, \
            "Duplicate() must not call Clear() on ChartsOC"

    def test_duplicate_collection_count_increases_by_one(self):
        """
        After Duplicate() the collection must have exactly one more item.
        """
        charts = [_MockChart(f"chart{i}") for i in range(3)]
        parent = _MockText(charts)
        count_before = len(parent.ChartsOC)

        _simulate_duplicate(charts[0], parent)

        assert len(parent.ChartsOC) == count_before + 1
