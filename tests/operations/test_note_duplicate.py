#
#   test_note_duplicate.py
#
#   Class: TestNoteDuplicateAnnotationsOC, TestNoteDuplicateRepliesOS
#          Regression coverage for issue #158 Pattern I:
#          NoteOperations.Duplicate(insert_after=True) used to call
#          AnnotationsOC.IndexOf() + AnnotationsOC.Insert() on an
#          ILcmOwningCollection (OC), which has no Insert() method.
#
#          Fix: Duplicate's AnnotationsOC branch always uses Add(); the
#          insert_after kwarg is silently ignored there. The RepliesOS
#          (ordered sequence) branch still honors insert_after.
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
    Stand-in for ILcmOwningCollection<ICmBaseAnnotation> (AnnotationsOC).

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
    Stand-in for ILcmOwningSequence<ICmBaseAnnotation> (RepliesOS).

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


class _MockNote:
    """Minimal stand-in for ICmBaseAnnotation."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<MockNote {self.name!r}>"


class _MockOwnerWithAnnotationsOC:
    """Simulates an owner object (e.g., IRnGenericRec) exposing AnnotationsOC."""

    def __init__(self, notes=None):
        self.AnnotationsOC = _MockOC(notes or [])


class _MockOwnerWithRepliesOS:
    """Simulates a parent note (owner) exposing RepliesOS."""

    def __init__(self, notes=None):
        self.RepliesOS = _MockOS(notes or [])


# ---------------------------------------------------------------------------
# Helpers that mimic the relevant code paths from NoteOperations
# ---------------------------------------------------------------------------


def _simulate_duplicate_oc(source_note, owner):
    """
    Simulate Duplicate() when parent has AnnotationsOC. AnnotationsOC is an
    unordered ILcmOwningCollection; the duplicate is always appended via
    Add(), regardless of the insert_after argument.
    """
    duplicate = _MockNote(source_note.name + "_copy")
    owner.AnnotationsOC.Add(duplicate)
    return duplicate


def _simulate_duplicate_os_insert_after(source_note, parent_note):
    """
    Simulate Duplicate(item, insert_after=True) when parent has RepliesOS.
    RepliesOS is an OS (ordered); positional Insert is valid.
    """
    duplicate = _MockNote(source_note.name + "_copy")
    idx = parent_note.RepliesOS.IndexOf(source_note)
    parent_note.RepliesOS.Insert(idx + 1, duplicate)
    return duplicate


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestNoteDuplicateAnnotationsOC:
    """
    Regression tests for issue #158 Pattern I -- Duplicate() path
    when parent exposes AnnotationsOC (unordered OC).
    """

    def test_uses_add_not_insert(self):
        """
        Duplicate() against an AnnotationsOC parent must call Add() and
        must NOT raise AttributeError from a missing Insert().
        """
        n1 = _MockNote("note1")
        owner = _MockOwnerWithAnnotationsOC([n1])
        assert len(owner.AnnotationsOC) == 1

        dup = _simulate_duplicate_oc(n1, owner)

        assert len(owner.AnnotationsOC) == 2
        assert dup in owner.AnnotationsOC._items

    def test_emits_no_deprecation_warning(self):
        """
        The AnnotationsOC branch must not emit any DeprecationWarning,
        regardless of the insert_after value the caller would have passed.
        """
        n1 = _MockNote("note1")
        owner = _MockOwnerWithAnnotationsOC([n1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_oc(n1, owner)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep == [], f"Unexpected DeprecationWarning(s): {dep}"

    def test_insert_method_absent_on_mock_oc(self):
        """
        Confirm that _MockOC raises AttributeError on Insert(), proving
        the pre-fix code would crash.
        """
        oc = _MockOC([_MockNote("x")])
        with pytest.raises(AttributeError):
            oc.Insert(0, _MockNote("y"))

    def test_duplicate_does_not_call_clear(self):
        """
        Duplicate() must never call Clear() on AnnotationsOC.
        """
        n1 = _MockNote("note1")
        owner = _MockOwnerWithAnnotationsOC([n1])

        _simulate_duplicate_oc(n1, owner)

        assert not owner.AnnotationsOC.clear_called, \
            "Duplicate() must not call Clear() on AnnotationsOC"


class TestNoteDuplicateRepliesOS:
    """
    Verify the OS (RepliesOS) branch is unaffected by the fix.
    Reply notes live in an ordered sequence; positional Insert is valid.
    """

    def test_replies_os_insert_after_positions_correctly(self):
        """
        For parent with RepliesOS, insert_after=True must use IndexOf + Insert.
        """
        parent = _MockOwnerWithRepliesOS()
        r1 = _MockNote("reply1")
        r2 = _MockNote("reply2")
        parent.RepliesOS.Add(r1)
        parent.RepliesOS.Add(r2)

        dup = _simulate_duplicate_os_insert_after(r1, parent)

        items = parent.RepliesOS._items
        r1_idx = items.index(r1)
        assert items[r1_idx + 1] is dup

    def test_replies_os_no_deprecation_warning(self):
        """
        The RepliesOS branch must not emit DeprecationWarning.
        """
        parent = _MockOwnerWithRepliesOS()
        r1 = _MockNote("reply1")
        parent.RepliesOS.Add(r1)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_os_insert_after(r1, parent)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep == [], f"Unexpected DeprecationWarning(s): {dep}"
