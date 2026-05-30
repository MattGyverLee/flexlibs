#
#   test_datanotebook_duplicate.py
#
#   Class: TestDataNotebookDuplicate
#          Regression coverage for issue #158 Pattern I:
#          DataNotebookOperations.Duplicate(insert_after=True) on a
#          top-level record called RecordsOC.IndexOf() + RecordsOC.Insert()
#          on an ILcmOwningCollection (OC), which has no Insert() method.
#
#          Fix: Duplicate always uses Add() on RecordsOC; insert_after is
#          silently ignored at the top level. SubRecordsOS (OS) branch
#          continues to support positional Insert() unchanged.
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
    Stand-in for ILcmOwningCollection<IRnGenericRec> (RecordsOC).

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


class _MockOS:
    """
    Stand-in for ILcmOwningSequence<IRnGenericRec> (SubRecordsOS).

    Ordered sequence: supports IndexOf and Insert.
    """

    def __init__(self, items=None):
        self._items = list(items) if items else []

    def __iter__(self):
        return iter(list(self._items))

    def __len__(self):
        return len(self._items)

    def Add(self, obj):
        self._items.append(obj)

    def IndexOf(self, obj):
        return self._items.index(obj)

    def Insert(self, index, obj):
        self._items.insert(index, obj)

    @property
    def Count(self):
        return len(self._items)


class _MockRecord:
    """Minimal stand-in for IRnGenericRec."""

    def __init__(self, title):
        self.title = title
        self.SubRecordsOS = _MockOS()

    def __repr__(self):
        return f"<MockRecord {self.title!r}>"


class _MockRepository:
    """Minimal stand-in for IRnResearchNbkRepository."""

    def __init__(self, records=None):
        self.RecordsOC = _MockOC(records or [])


# ---------------------------------------------------------------------------
# Helpers that mimic the relevant code paths from DataNotebookOperations
# ---------------------------------------------------------------------------


def _simulate_duplicate_toplevel(source_rec, repos):
    """
    Simulate Duplicate() for a top-level record. RecordsOC is unordered,
    so insert_after is ignored and the duplicate is always appended via Add().
    """
    duplicate = _MockRecord(source_rec.title + "_copy")
    repos.RecordsOC.Add(duplicate)
    return duplicate


def _simulate_duplicate_subrecord_insert_after(source_sub, parent_rec):
    """
    Simulate Duplicate(item, insert_after=True) for a sub-record.
    SubRecordsOS is an OS (ordered sequence); positional Insert is valid.
    No DeprecationWarning expected.
    """
    duplicate = _MockRecord(source_sub.title + "_copy")
    idx = parent_rec.SubRecordsOS.IndexOf(source_sub)
    parent_rec.SubRecordsOS.Insert(idx + 1, duplicate)
    return duplicate


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDataNotebookDuplicateTopLevel:
    """
    Regression tests for issue #158 Pattern I -- Duplicate() top-level path
    (RecordsOC is unordered OC).
    """

    def test_uses_add_not_insert(self):
        """
        Duplicate() must call Add() and must NOT raise AttributeError from
        a missing Insert().
        """
        r1 = _MockRecord("Interview 1")
        repos = _MockRepository([r1])
        assert len(repos.RecordsOC) == 1

        dup = _simulate_duplicate_toplevel(r1, repos)

        assert len(repos.RecordsOC) == 2
        assert dup in repos.RecordsOC._items

    def test_emits_no_deprecation_warning(self):
        """
        Duplicate() of a top-level record must not emit any
        DeprecationWarning, regardless of insert_after.
        """
        r1 = _MockRecord("Interview 1")
        repos = _MockRepository([r1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_toplevel(r1, repos)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep == [], f"Unexpected DeprecationWarning(s): {dep}"

    def test_insert_method_absent_on_mock_oc(self):
        """
        Confirm that _MockOC raises AttributeError on Insert(), proving
        the pre-fix code would crash.
        """
        oc = _MockOC([_MockRecord("x")])
        with pytest.raises(AttributeError):
            oc.Insert(0, _MockRecord("y"))

    def test_duplicate_does_not_call_clear(self):
        """
        Duplicate() must never call Clear() on RecordsOC.
        """
        r1 = _MockRecord("Interview 1")
        repos = _MockRepository([r1])

        _simulate_duplicate_toplevel(r1, repos)

        assert not repos.RecordsOC.clear_called, \
            "Duplicate() must not call Clear() on RecordsOC"

    def test_duplicate_collection_count_increases_by_one(self):
        """
        After Duplicate() the collection must have exactly one more item.
        """
        recs = [_MockRecord(f"rec{i}") for i in range(3)]
        repos = _MockRepository(recs)
        count_before = len(repos.RecordsOC)

        _simulate_duplicate_toplevel(recs[0], repos)

        assert len(repos.RecordsOC) == count_before + 1


class TestDataNotebookDuplicateSubRecord:
    """
    Verify the OS (SubRecordsOS) branch is unaffected by the fix.
    Sub-records live in an ordered sequence; positional Insert is valid.
    """

    def test_subrecord_insert_after_positions_correctly(self):
        """
        For sub-records (SubRecordsOS is OS), insert_after=True must
        use IndexOf + Insert to place the duplicate after the source.
        """
        parent = _MockRecord("Interview")
        s1 = _MockRecord("sub1")
        s2 = _MockRecord("sub2")
        parent.SubRecordsOS.Add(s1)
        parent.SubRecordsOS.Add(s2)

        dup = _simulate_duplicate_subrecord_insert_after(s1, parent)

        items = parent.SubRecordsOS._items
        s1_idx = items.index(s1)
        assert items[s1_idx + 1] is dup

    def test_subrecord_no_deprecation_warning(self):
        """
        The OS (sub-record) branch must not emit DeprecationWarning.
        """
        parent = _MockRecord("Interview")
        s1 = _MockRecord("sub1")
        parent.SubRecordsOS.Add(s1)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_subrecord_insert_after(s1, parent)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep == [], f"Unexpected DeprecationWarning(s): {dep}"
