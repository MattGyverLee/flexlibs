#
#   test_catalog.py
#
#   Class: TestCatalog
#          Phase 5a (issue #14) unit tests for the GOLDEtic catalog parser
#          in flexlibs2.code.Shared.catalog. These exercise the pure-Python
#          parsing path: file discovery, XML parsing, tree navigation. No
#          live LCM/FieldWorks operations are required, but find_catalog_file
#          needs FLExGlobals.FWCodeDir to be initialised (which happens via
#          the session-scoped fixture in conftest.py when FieldWorks is
#          installed). Tests that depend on FWCodeDir skip gracefully when
#          FieldWorks isn't reachable.
#
#   Platform: Python (stdlib only for the module under test;
#             FieldWorks needed only for FWCodeDir resolution)
#             FieldWorks Version 9+
#
#   Copyright 2026
#

import os
import sys

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fw_available():
    """
    Return True iff FieldWorks is reachable: SIL.LCModel loaded AND
    FLExGlobals.FWCodeDir is set to an existing Templates directory.
    Matches the FW-availability skip pattern in
    tests/test_flexproject_discoverability.py / tests/operations/test_phonemes.py.
    """
    if "SIL.LCModel" not in sys.modules:
        return False
    try:
        from flexlibs2.code import FLExGlobals
    except Exception:
        return False
    if not FLExGlobals.FWCodeDir:
        return False
    return os.path.isdir(os.path.join(FLExGlobals.FWCodeDir, "Templates"))


@pytest.fixture(scope="module")
def goldetic_entries():
    """
    Parse GOLDEtic.xml once per module and share the result across all
    tests that need a parsed tree. Skips if FieldWorks is not available.
    """
    if not _fw_available():
        pytest.skip("FieldWorks (with Templates/GOLDEtic.xml) not available")

    from flexlibs2.code.Shared.catalog import (
        find_catalog_file,
        parse_etic_catalog,
    )

    path = find_catalog_file("GOLDEtic.xml")
    return parse_etic_catalog(path)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCatalog:
    """
    Pure-Python coverage for catalog.py: file discovery, parsing, lookup.
    """

    # --- find_catalog_file ----------------------------------------------

    def test_find_catalog_file_returns_existing_goldetic_path(self):
        """
        find_catalog_file('GOLDEtic.xml') must resolve to an existing file
        whose basename is 'GOLDEtic.xml'. Requires a FieldWorks install.
        """
        if not _fw_available():
            pytest.skip("FieldWorks (with Templates/GOLDEtic.xml) not available")

        from flexlibs2.code.Shared.catalog import find_catalog_file

        path = find_catalog_file("GOLDEtic.xml")
        assert os.path.isfile(path), (
            f"find_catalog_file returned non-existent path: {path}"
        )
        assert path.endswith("GOLDEtic.xml"), (
            f"Expected path ending with 'GOLDEtic.xml', got: {path}"
        )

    def test_find_catalog_file_raises_for_nonexistent(self):
        """
        find_catalog_file with a bogus filename must raise. Per the source,
        the helper raises FileNotFoundError when the file is missing under
        FWCodeDir/Templates. (If FWCodeDir is None it would raise
        RuntimeError; we only run this test when FW is available so we get
        the FileNotFoundError branch.)
        """
        if not _fw_available():
            pytest.skip("FieldWorks (with Templates/) not available")

        from flexlibs2.code.Shared.catalog import find_catalog_file

        # Use a unique, almost-certainly-not-present filename.
        with pytest.raises(FileNotFoundError):
            find_catalog_file("DoesNotExist_Phase5aVerificationAgent.xml")

    # --- parse_etic_catalog ---------------------------------------------

    def test_parse_etic_catalog_top_level_count(self, goldetic_entries):
        """
        GOLDEtic.xml has 16 top-level <item type="category"> children
        under <eticPOSList>. Confirmed by Programmer's smoke test.
        """
        assert len(goldetic_entries) == 16, (
            f"Expected 16 top-level catalog entries, got {len(goldetic_entries)}"
        )

    def test_parse_etic_catalog_total_count_with_nesting(self, goldetic_entries):
        """
        Walking nested children produces 58 entries total. Confirmed by
        Programmer's smoke test.
        """
        from flexlibs2.code.Shared.catalog import count_catalog_entries

        total = count_catalog_entries(goldetic_entries)
        assert total == 58, (
            f"Expected 58 total catalog entries (including nested), got {total}"
        )

    def test_parse_etic_catalog_first_entry_is_adjective(self, goldetic_entries):
        """
        First top-level entry is 'Adjective' with its canonical FW GUID.
        Confirmed by Programmer's smoke test.
        """
        first = goldetic_entries[0]
        assert first.id == "Adjective", (
            f"Expected first entry id 'Adjective', got '{first.id}'"
        )
        assert first.guid.lower() == "30d07580-5052-4d91-bc24-469b8b2d7df9", (
            f"Expected canonical Adjective GUID, got '{first.guid}'"
        )

    def test_parse_etic_catalog_adjective_has_localized_term(self, goldetic_entries):
        """
        The Adjective entry has at least an English term; in the shipped
        GOLDEtic.xml that value is exactly 'Adjective'.
        """
        first = goldetic_entries[0]
        assert "en" in first.term, (
            f"Adjective entry missing 'en' term; available WSes: {list(first.term)}"
        )
        assert first.term["en"] == "Adjective", (
            f"Adjective.term['en'] = {first.term['en']!r}, expected 'Adjective'"
        )

    # --- find_catalog_entry ---------------------------------------------

    def test_find_catalog_entry_accepts_gold_prefix(self, goldetic_entries):
        """
        find_catalog_entry must strip a 'GOLD:' prefix and find the entry.
        """
        from flexlibs2.code.Shared.catalog import find_catalog_entry

        entry = find_catalog_entry(goldetic_entries, "GOLD:Adjective")
        assert entry is not None, (
            "find_catalog_entry returned None for 'GOLD:Adjective'"
        )
        assert entry.id == "Adjective"

    def test_find_catalog_entry_accepts_bare_id(self, goldetic_entries):
        """
        find_catalog_entry must accept a bare id (no 'GOLD:' prefix).
        """
        from flexlibs2.code.Shared.catalog import find_catalog_entry

        entry = find_catalog_entry(goldetic_entries, "Adjective")
        assert entry is not None, (
            "find_catalog_entry returned None for bare 'Adjective'"
        )
        assert entry.id == "Adjective"
        assert entry.guid.lower() == "30d07580-5052-4d91-bc24-469b8b2d7df9"

    def test_find_catalog_entry_returns_none_for_missing(self, goldetic_entries):
        """
        Unknown ids must return None (not raise).
        """
        from flexlibs2.code.Shared.catalog import find_catalog_entry

        result = find_catalog_entry(
            goldetic_entries, "Phase5aBogusCategory_NotInCatalog"
        )
        assert result is None, (
            f"Expected None for unknown id, got {result!r}"
        )

    def test_find_catalog_entry_walks_nested(self, goldetic_entries):
        """
        find_catalog_entry must descend into .children. 'Postposition' is a
        sub-category of 'Adposition' in GOLDEtic.xml, so a successful look-up
        proves the depth-first walk works.
        """
        from flexlibs2.code.Shared.catalog import find_catalog_entry

        # Sanity: Postposition is NOT a top-level id.
        top_ids = {e.id for e in goldetic_entries}
        assert "Postposition" not in top_ids, (
            "Test assumption violated: Postposition is now top-level; "
            "pick a different nested id."
        )

        nested = find_catalog_entry(goldetic_entries, "Postposition")
        assert nested is not None, (
            "find_catalog_entry did not descend into children to find "
            "'Postposition' (expected under 'Adposition')"
        )
        assert nested.id == "Postposition"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
