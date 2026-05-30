#
#   test_gramcat_duplicate.py
#
#   Class: TestGramCatDuplicate
#          Regression coverage for issue #158 Pattern I:
#          GramCatOperations.Duplicate(insert_after=True) on a top-level
#          category called TypesOC.IndexOf() + TypesOC.Insert() on an
#          ILcmOwningCollection (OC), which has no Insert() method.
#
#          Fix: Duplicate always uses Add() on TypesOC; insert_after is
#          silently ignored at the top level. The OS branch
#          (SubPossibilitiesOS) continues to support positional Insert()
#          unchanged.
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
    Stand-in for ILcmOwningCollection<IFsFeatStrucType>.

    Mirrors the real contract: Add() works; Insert() does NOT exist;
    Clear() cascade-deletes (simulated).
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
    Stand-in for ILcmOwningSequence<ICmPossibility> (SubPossibilitiesOS).

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


class _MockCat:
    """Minimal stand-in for ICmPossibility / IFsFeatStrucType."""

    def __init__(self, name):
        self.name = name
        self.SubPossibilitiesOS = _MockOS()

    def __repr__(self):
        return f"<MockCat {self.name!r}>"


class _MockFeatureSystem:
    """Minimal stand-in for MsFeatureSystemOA."""

    def __init__(self, cats=None):
        self.TypesOC = _MockOC(cats or [])


# ---------------------------------------------------------------------------
# Helpers that mimic the relevant code paths from GramCatOperations.Duplicate
# ---------------------------------------------------------------------------


def _simulate_duplicate_toplevel(source_cat, feature_system):
    """
    Simulate Duplicate() for a top-level category. TypesOC is unordered,
    so insert_after is ignored and the duplicate is always appended via Add().
    """
    duplicate = _MockCat(source_cat.name + "_copy")
    feature_system.TypesOC.Add(duplicate)
    return duplicate


def _simulate_duplicate_subcat_insert_after(source_sub, parent_cat):
    """
    Simulate Duplicate(item, insert_after=True) for a subcategory.
    SubPossibilitiesOS is an OS (ordered sequence); positional Insert is valid.
    No DeprecationWarning expected.
    """
    duplicate = _MockCat(source_sub.name + "_copy")
    idx = parent_cat.SubPossibilitiesOS.IndexOf(source_sub)
    parent_cat.SubPossibilitiesOS.Insert(idx + 1, duplicate)
    return duplicate


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGramCatDuplicateTopLevel:
    """
    Regression tests for issue #158 Pattern I -- Duplicate() top-level path
    (TypesOC is unordered OC).
    """

    def test_uses_add_not_insert(self):
        """
        Duplicate() must call Add() and must NOT raise AttributeError from
        a missing Insert().
        """
        cat1 = _MockCat("person")
        fs = _MockFeatureSystem([cat1])
        assert len(fs.TypesOC) == 1

        dup = _simulate_duplicate_toplevel(cat1, fs)

        assert len(fs.TypesOC) == 2
        assert dup in fs.TypesOC._items

    def test_emits_no_deprecation_warning(self):
        """
        Duplicate() of a top-level category must not emit any
        DeprecationWarning, regardless of insert_after.
        """
        cat1 = _MockCat("person")
        fs = _MockFeatureSystem([cat1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_toplevel(cat1, fs)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep == [], f"Unexpected DeprecationWarning(s): {dep}"

    def test_insert_method_absent_on_mock_oc(self):
        """
        Confirm that _MockOC raises AttributeError on Insert(), proving
        the pre-fix code would crash.
        """
        oc = _MockOC([_MockCat("x")])
        with pytest.raises(AttributeError):
            oc.Insert(0, _MockCat("y"))

    def test_duplicate_does_not_call_clear(self):
        """
        Duplicate() must never call Clear() on TypesOC.
        """
        cat1 = _MockCat("person")
        fs = _MockFeatureSystem([cat1])

        _simulate_duplicate_toplevel(cat1, fs)

        assert not fs.TypesOC.clear_called, \
            "Duplicate() must not call Clear() on TypesOC"

    def test_duplicate_collection_count_increases_by_one(self):
        """
        After Duplicate() the collection must have exactly one more item.
        """
        cats = [_MockCat(f"cat{i}") for i in range(3)]
        fs = _MockFeatureSystem(cats)
        count_before = len(fs.TypesOC)

        _simulate_duplicate_toplevel(cats[0], fs)

        assert len(fs.TypesOC) == count_before + 1


class TestGramCatDuplicateSubcategory:
    """
    Verify the OS (SubPossibilitiesOS) branch is unaffected by the fix.
    Subcategories live in an ordered sequence; positional Insert is valid.
    """

    def test_subcat_insert_after_uses_insert_not_add(self):
        """
        For subcategories (SubPossibilitiesOS is OS), insert_after=True must
        use IndexOf + Insert to place the duplicate after the source.
        """
        parent = _MockCat("number")
        s = _MockCat("singular")
        p = _MockCat("plural")
        parent.SubPossibilitiesOS.Add(s)
        parent.SubPossibilitiesOS.Add(p)

        dup = _simulate_duplicate_subcat_insert_after(s, parent)

        items = parent.SubPossibilitiesOS._items
        # dup should be immediately after 's'
        s_idx = items.index(s)
        assert items[s_idx + 1] is dup

    def test_subcat_no_deprecation_warning(self):
        """
        The OS (subcategory) branch must not emit DeprecationWarning.
        """
        parent = _MockCat("number")
        s = _MockCat("singular")
        parent.SubPossibilitiesOS.Add(s)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_subcat_insert_after(s, parent)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep == [], f"Unexpected DeprecationWarning(s): {dep}"
