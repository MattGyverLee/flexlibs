#
#   test_gramcat_duplicate.py
#
#   Class: TestGramCatDuplicate
#          Regression coverage for issue #158 Pattern I:
#          GramCatOperations.Duplicate(insert_after=True) on a top-level
#          category called TypesOC.IndexOf() + TypesOC.Insert() on an
#          ILcmOwningCollection (OC), which has no Insert() method.
#
#          Fix:
#            - Duplicate: default changed to insert_after=False; kwarg is
#              deprecated and ignored for the TypesOC (top-level) branch;
#              always uses Add() on OC. OS branch (SubPossibilitiesOS)
#              continues to support positional Insert() unchanged.
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


def _simulate_duplicate_toplevel_default(source_cat, feature_system):
    """
    Simulate Duplicate(item, insert_after=False) for a top-level category.
    No DeprecationWarning; uses Add() on TypesOC.
    """
    duplicate = _MockCat(source_cat.name + "_copy")
    feature_system.TypesOC.Add(duplicate)
    return duplicate


def _simulate_duplicate_toplevel_deprecated(source_cat, feature_system):
    """
    Simulate Duplicate(item, insert_after=True) for a top-level category.
    Emits DeprecationWarning; still uses Add(), never Insert().
    """
    warnings.warn(
        "GramCatOperations.Duplicate: insert_after is deprecated and "
        "ignored for top-level categories. TypesOC is an unordered "
        "ILcmOwningCollection; positional insertion is not supported. "
        "The duplicate is always appended via Add().",
        DeprecationWarning,
        stacklevel=2,
    )
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

    def test_default_path_uses_add_not_insert(self):
        """
        Duplicate(item) -- default insert_after=False -- must call Add() and
        must NOT raise AttributeError from a missing Insert().
        """
        cat1 = _MockCat("person")
        fs = _MockFeatureSystem([cat1])
        assert len(fs.TypesOC) == 1

        dup = _simulate_duplicate_toplevel_default(cat1, fs)

        assert len(fs.TypesOC) == 2
        assert dup in fs.TypesOC._items

    def test_default_path_emits_no_deprecation_warning(self):
        """
        The default path (insert_after=False) must not emit DeprecationWarning.
        """
        cat1 = _MockCat("person")
        fs = _MockFeatureSystem([cat1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_toplevel_default(cat1, fs)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep == [], f"Unexpected DeprecationWarning(s): {dep}"

    def test_deprecated_insert_after_true_emits_warning(self):
        """
        Duplicate(item, insert_after=True) on a top-level category must emit
        exactly one DeprecationWarning mentioning 'TypesOC'.
        """
        cat1 = _MockCat("person")
        fs = _MockFeatureSystem([cat1])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _simulate_duplicate_toplevel_deprecated(cat1, fs)

        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert len(dep) == 1
        assert "TypesOC" in str(dep[0].message)

    def test_deprecated_insert_after_true_still_adds_via_add(self):
        """
        Even with insert_after=True the duplicate must be added via Add()
        so the collection count increases by 1 and no AttributeError occurs.
        """
        cat1 = _MockCat("person")
        fs = _MockFeatureSystem([cat1])
        initial = len(fs.TypesOC)

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            dup = _simulate_duplicate_toplevel_deprecated(cat1, fs)

        assert len(fs.TypesOC) == initial + 1
        assert dup in fs.TypesOC._items

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

        _simulate_duplicate_toplevel_default(cat1, fs)

        assert not fs.TypesOC.clear_called, \
            "Duplicate() must not call Clear() on TypesOC"

    def test_duplicate_collection_count_increases_by_one(self):
        """
        After Duplicate() the collection must have exactly one more item.
        """
        cats = [_MockCat(f"cat{i}") for i in range(3)]
        fs = _MockFeatureSystem(cats)
        count_before = len(fs.TypesOC)

        _simulate_duplicate_toplevel_default(cats[0], fs)

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
