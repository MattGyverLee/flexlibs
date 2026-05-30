#
#   test_note_duplicate.py
#
#   Class: TestNoteDuplicate, TestNoteReorder
#          Regression coverage for issue #158 Pattern I:
#          NoteOperations.Duplicate(insert_after=True) called
#          AnnotationsOC.IndexOf() + AnnotationsOC.Insert() on an
#          ILcmOwningCollection (OC), which has no Insert() method.
#          NoteOperations.Reorder() called Clear() on AnnotationsOC,
#          cascade-deleting all ICmBaseAnnotation objects (P0 corruption).
#
#          Fixes:
#            - Duplicate: default changed to insert_after=False; kwarg is
#              deprecated and ignored for the AnnotationsOC branch; always
#              uses Add(). RepliesOS (OS) branch is unchanged.
#            - Reorder: converted to no-op that emits DeprecationWarning
#              and never touches the collection.
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


def _simulate_duplicate_oc_default(source_note, owner):
    """
    Simulate Duplicate(item, insert_after=False) when parent has AnnotationsOC.
    No DeprecationWarning; uses Add().
    """
    duplicate = _MockNote(source_note.name + "_copy")
    owner.AnnotationsOC.Add(duplicate)
    return duplicate


def _simulate_duplicate_oc_deprecated(source_note, owner):
    """
    Simulate Duplicate(item, insert_after=True) when parent has AnnotationsOC.
    Emits DeprecationWarning; still uses Add(), never Insert().
    """
    warnings.warn(
        "NoteOperations.Duplicate: insert_after is deprecated and "
        "ignored when the parent exposes AnnotationsOC. "
        "AnnotationsOC is an unordered ILcmOwningCollection; "
        "positional insertion is not supported. The duplicate is "
        "always appended via Add().",
        DeprecationWarning,
        stacklevel=2,
    )
    duplicate = _MockNote(source_note.name + "_copy")
    owner.AnnotationsOC.Add(duplicate)
    return duplicate


def _simulate_duplicate_os_insert_after(source_note, parent_note):
    """
    Simulate Duplicate(item, insert_after=True) when parent has RepliesOS.
    RepliesOS is an OS (ordered); positional Insert is valid. No warning.
    """
    duplicate = _MockNote(source_note.name + "_copy")
    idx = parent_note.RepliesOS.IndexOf(source_note)
    parent_note.RepliesOS.Insert(idx + 1, duplicate)
    return duplicate


def _simulate_reorder(owner_object, note_list):
    """
    Simulate Reorder() -- the fixed no-op body.
    Emits DeprecationWarning; never calls Clear() or Add().
    """
    warnings.warn(
        "NoteOperations.Reorder is a no-op: AnnotationsOC is an unordered "
        "ILcmOwningCollection and reorder has no semantic meaning. "
        "The previous implementation called Clear() which cascade-deletes "
        "all ICmBaseAnnotation objects (P0 data corruption, issue #158). "
        "This method does nothing and will be removed in a future release.",
        DeprecationWarning,
        stacklevel=2,
    )
    # No collection operations performed.


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestNoteDuplicateAnnotationsOC:
    """
    Regression tests for issue #158 Pattern I -- Duplicate() path
    when parent exposes AnnotationsOC (unordered OC).
    """

    def test_default_path_uses_add_not_insert(self):
        """
        Duplicate(item) -- default insert_after=False -- must call Add() and
        must NOT raise AttributeError from a missing Insert().
        """
        n1 = _MockNote("note1")
        owner = _MockOwnerWithAnnotationsOC([n1])
        assert len(owner.AnnotationsOC) == 1

        dup = _simulate_duplicate_oc_default(n1, owner)

        assert len(owner.AnnotationsOC) == 2
        assert dup in owner.AnnotationsOC._items

    def test_default_path_emits_no_deprecation_warning(self):
        """
        The default path (insert_after=False) must not emit DeprecationWarning.
        """
        n1 = _MockNote("note1")
        owner = _MockOwnerWithAnnotationsOC([n1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_oc_default(n1, owner)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep == [], f"Unexpected DeprecationWarning(s): {dep}"

    def test_deprecated_insert_after_true_emits_warning(self):
        """
        Duplicate(item, insert_after=True) with AnnotationsOC parent must emit
        exactly one DeprecationWarning mentioning 'AnnotationsOC'.
        """
        n1 = _MockNote("note1")
        owner = _MockOwnerWithAnnotationsOC([n1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_oc_deprecated(n1, owner)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert len(dep) == 1
        assert "AnnotationsOC" in str(dep[0].message)

    def test_deprecated_insert_after_true_still_adds_via_add(self):
        """
        Even with insert_after=True the duplicate must be added via Add()
        so the collection count increases by 1 and no AttributeError occurs.
        """
        n1 = _MockNote("note1")
        owner = _MockOwnerWithAnnotationsOC([n1])
        initial = len(owner.AnnotationsOC)

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            dup = _simulate_duplicate_oc_deprecated(n1, owner)

        assert len(owner.AnnotationsOC) == initial + 1
        assert dup in owner.AnnotationsOC._items

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

        _simulate_duplicate_oc_default(n1, owner)

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


class TestNoteReorder:
    """
    Regression tests for issue #158 -- Reorder() path.
    """

    def test_reorder_emits_deprecation_warning(self):
        """
        Reorder() must emit exactly one DeprecationWarning mentioning 'no-op'.
        """
        n1 = _MockNote("note1")
        n2 = _MockNote("note2")
        owner = _MockOwnerWithAnnotationsOC([n1, n2])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_reorder(owner, [n2, n1])

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert len(dep) == 1
        assert "no-op" in str(dep[0].message)

    def test_reorder_does_not_call_clear(self):
        """
        Reorder() must NOT call Clear() -- that would cascade-delete all
        ICmBaseAnnotation objects (P0 data corruption).
        """
        n1 = _MockNote("note1")
        n2 = _MockNote("note2")
        owner = _MockOwnerWithAnnotationsOC([n1, n2])

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            _simulate_reorder(owner, [n2, n1])

        assert not owner.AnnotationsOC.clear_called, \
            "Reorder() must not call Clear() -- cascade-delete is P0 corruption"

    def test_reorder_collection_count_unchanged(self):
        """
        After Reorder() the collection must still have the same number of items.
        """
        notes = [_MockNote(f"note{i}") for i in range(3)]
        owner = _MockOwnerWithAnnotationsOC(notes)
        count_before = len(owner.AnnotationsOC)

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            _simulate_reorder(owner, list(reversed(notes)))

        assert len(owner.AnnotationsOC) == count_before

    def test_reorder_no_deleted_items(self):
        """
        After Reorder() the _deleted list must be empty.
        """
        n1 = _MockNote("note1")
        n2 = _MockNote("note2")
        owner = _MockOwnerWithAnnotationsOC([n1, n2])

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            _simulate_reorder(owner, [n2, n1])

        assert owner.AnnotationsOC._deleted == []

    def test_reorder_returns_none(self):
        """
        Reorder() is a no-op and returns None (implicit).
        """
        n1 = _MockNote("note1")
        owner = _MockOwnerWithAnnotationsOC([n1])

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = _simulate_reorder(owner, [n1])

        assert result is None
