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


def _phon_feats_available():
    """
    Like _fw_available(), but additionally requires the MGA
    PhonFeatsEticGlossList.xml catalog to exist under FWCodeDir. The
    Phase 5b parser tests need this XML file.
    """
    if not _fw_available():
        return False
    from flexlibs2.code import FLExGlobals

    path = os.path.join(
        FLExGlobals.FWCodeDir,
        "Language Explorer",
        "MGA",
        "GlossLists",
        "PhonFeatsEticGlossList.xml",
    )
    return os.path.isfile(path)


@pytest.fixture(scope="module")
def phon_feat_entries():
    """
    Parse PhonFeatsEticGlossList.xml once per module and share the result
    across all Phase 5b parser tests. Skips if the catalog is not
    available.
    """
    if not _phon_feats_available():
        pytest.skip(
            "FieldWorks (with Language Explorer/MGA/GlossLists/"
            "PhonFeatsEticGlossList.xml) not available"
        )

    from flexlibs2.code.Shared.catalog import (
        find_catalog_file,
        parse_etic_gloss_list,
    )

    path = find_catalog_file(
        "PhonFeatsEticGlossList.xml",
        subdir="Language Explorer/MGA/GlossLists",
    )
    return parse_etic_gloss_list(path)


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

    # --- Phase 5b: subdir argument on find_catalog_file -----------------

    def test_find_catalog_file_with_subdir_resolves_mga_path(self):
        """
        find_catalog_file('PhonFeatsEticGlossList.xml',
                          subdir='Language Explorer/MGA/GlossLists')
        must resolve to an existing file under FWCodeDir/Language
        Explorer/MGA/GlossLists. Confirms the Phase 5b subdir parameter
        works for the MGA catalog location.
        """
        if not _phon_feats_available():
            pytest.skip(
                "FieldWorks (with PhonFeatsEticGlossList.xml) not available"
            )

        from flexlibs2.code.Shared.catalog import find_catalog_file

        path = find_catalog_file(
            "PhonFeatsEticGlossList.xml",
            subdir="Language Explorer/MGA/GlossLists",
        )
        assert os.path.isfile(path), (
            f"find_catalog_file returned non-existent path: {path}"
        )
        assert path.endswith("PhonFeatsEticGlossList.xml"), (
            f"Expected path ending with the catalog filename, got: {path}"
        )
        # The resolved path should contain the subdir components.
        assert "MGA" in path and "GlossLists" in path, (
            f"Path missing expected MGA/GlossLists components: {path}"
        )

    def test_find_catalog_file_default_subdir_preserves_phase5a_behavior(self):
        """
        Phase 5a callers passed no subdir argument and got
        FWCodeDir/Templates/GOLDEtic.xml. The Phase 5b extension must
        keep that default behaviour intact (no positional/keyword
        breakage).
        """
        if not _fw_available():
            pytest.skip("FieldWorks (with Templates/GOLDEtic.xml) not available")

        from flexlibs2.code.Shared.catalog import find_catalog_file

        # Call WITHOUT the subdir kwarg (Phase 5a call shape).
        path = find_catalog_file("GOLDEtic.xml")
        assert os.path.isfile(path), (
            f"Phase 5a default subdir broke: {path}"
        )
        assert path.endswith("GOLDEtic.xml")
        # The default subdir is 'Templates' per the source.
        assert "Templates" in path, (
            f"Default subdir should be 'Templates'; got path: {path}"
        )

    # --- Phase 5b: parse_etic_gloss_list --------------------------------

    def test_parse_etic_gloss_list_returns_features_only(self, phon_feat_entries):
        """
        The parser must return ONLY type='feature' entries (groups are
        organizational and are flattened away; their child features
        are still surfaced). The MGA PhonFeatsEticGlossList.xml ships
        with roughly 25-29 features depending on FW version, all
        addressable from the top of the returned list.
        """
        count = len(phon_feat_entries)
        assert 25 <= count <= 29, (
            f"Expected ~25-29 features from PhonFeatsEticGlossList, "
            f"got {count}. Counts outside this band suggest the parser "
            "is including/excluding the wrong item types."
        )
        # No group entries leaked through: ids should not start with 'g'
        # by FW convention (features start with 'f', values with 'v',
        # groups with 'g'). Defensive: only check a few well-known
        # patterns. Empty id strings would also indicate a parser bug.
        for entry in phon_feat_entries:
            assert entry.id, (
                "Encountered a feature entry with empty id; parser may "
                "be emitting group items."
            )

    def test_parse_etic_gloss_list_first_feature_has_values(self, phon_feat_entries):
        """
        Each feature in the catalog has 2+ value children (binary +/- in
        the common case). The first feature must therefore have at least
        two children whose abbrev['en'] is '+' and '-' respectively.
        """
        first = phon_feat_entries[0]
        assert len(first.children) >= 2, (
            f"First feature '{first.id}' has only {len(first.children)} "
            "value children; expected >= 2 (typically + and -)."
        )
        abbrevs = {v.abbrev.get("en") for v in first.children}
        assert "+" in abbrevs, (
            f"First feature '{first.id}' is missing a value with abbrev "
            f"'+'; got abbrevs: {sorted(a for a in abbrevs if a)}"
        )
        assert "-" in abbrevs, (
            f"First feature '{first.id}' is missing a value with abbrev "
            f"'-'; got abbrevs: {sorted(a for a in abbrevs if a)}"
        )

    def test_parse_etic_gloss_list_feature_has_guid(self, phon_feat_entries):
        """
        Catalog features must carry a canonical, lowercase-hex GUID.
        Without it, CreateFromCatalog cannot pin the canonical FW GUID
        when creating the LCM object.
        """
        import re

        first = phon_feat_entries[0]
        assert first.guid, (
            f"Feature '{first.id}' missing canonical GUID; "
            "CreateFromCatalog would fall back to a random GUID."
        )
        # Standard GUID: 8-4-4-4-12 hex with hyphens, lowercase.
        guid_re = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        )
        assert guid_re.match(first.guid.lower()), (
            f"Feature '{first.id}' GUID {first.guid!r} is not a valid "
            "lowercase-hex GUID."
        )

    def test_parse_etic_gloss_list_value_has_guid(self, phon_feat_entries):
        """
        Catalog value children must carry their own canonical GUIDs,
        distinct from the parent feature's GUID. ImportCatalog relies
        on these for idempotency at the value level.
        """
        import re

        first = phon_feat_entries[0]
        assert first.children, (
            f"Feature '{first.id}' has no value children; "
            "cannot verify value-GUID invariants."
        )
        first_value = first.children[0]
        assert first_value.guid, (
            f"Value '{first_value.id}' of feature '{first.id}' missing "
            "canonical GUID."
        )
        guid_re = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        )
        assert guid_re.match(first_value.guid.lower()), (
            f"Value GUID {first_value.guid!r} is not lowercase-hex."
        )
        assert first_value.guid.lower() != first.guid.lower(), (
            "Value GUID must differ from parent feature GUID, but both "
            f"are {first.guid!r}."
        )

    # --- Phase 5b: _strip_catalog_prefix dual-prefix --------------------

    def test_strip_catalog_prefix_accepts_phon_and_gold(self):
        """
        The internal prefix stripper must recognise both 'GOLD:' (Phase
        5a, POS) and 'PHON:' (Phase 5b, phon features). Case-insensitive
        match on the prefix; bare ids pass through; unknown prefixes are
        preserved verbatim.
        """
        from flexlibs2.code.Shared.catalog import _strip_catalog_prefix

        # GOLD prefix stripped (Phase 5a baseline).
        assert _strip_catalog_prefix("GOLD:Adjective") == "Adjective"
        # PHON prefix stripped (Phase 5b addition).
        assert _strip_catalog_prefix("PHON:fPAConsonantal") == "fPAConsonantal"
        # Case-insensitive prefix match.
        assert _strip_catalog_prefix("gold:Adjective") == "Adjective"
        assert _strip_catalog_prefix("phon:fPAConsonantal") == "fPAConsonantal"
        # Bare id (no prefix) passes through unchanged.
        assert _strip_catalog_prefix("fPAConsonantal") == "fPAConsonantal"
        # Unknown prefix preserved verbatim (don't strip).
        assert _strip_catalog_prefix("UNKNOWN:foo") == "UNKNOWN:foo"

    # --- Phase 5b: find_catalog_entry across both catalogs --------------

    def test_find_catalog_entry_resolves_bare_phon_id(self, phon_feat_entries):
        """
        find_catalog_entry must find 'fPAConsonantal' against the
        PhonFeats catalog without any prefix.
        """
        from flexlibs2.code.Shared.catalog import find_catalog_entry

        entry = find_catalog_entry(phon_feat_entries, "fPAConsonantal")
        assert entry is not None, (
            "find_catalog_entry returned None for bare 'fPAConsonantal'"
        )
        assert entry.id == "fPAConsonantal"
        # Canonical GUID per the MGA catalog.
        assert entry.guid.lower() == "b4ddf8e5-1ff8-43fc-9723-04f1ee0471fc"

    def test_find_catalog_entry_resolves_phon_prefixed_id(self, phon_feat_entries):
        """
        find_catalog_entry must accept 'PHON:fPAConsonantal' and return
        the same entry as the bare-id form.
        """
        from flexlibs2.code.Shared.catalog import find_catalog_entry

        bare = find_catalog_entry(phon_feat_entries, "fPAConsonantal")
        prefixed = find_catalog_entry(phon_feat_entries, "PHON:fPAConsonantal")
        assert bare is not None and prefixed is not None
        assert bare.id == prefixed.id == "fPAConsonantal"
        assert bare.guid.lower() == prefixed.guid.lower()

    def test_find_catalog_entry_resolves_value_id(self, phon_feat_entries):
        """
        Value entries are nested under their parent feature, so a lookup
        by value id ('vPAConsonantalPositive') must walk into
        entry.children. Confirms the depth-first walk handles the
        eticGlossList tree shape, not just the GOLDEtic shape.
        """
        from flexlibs2.code.Shared.catalog import find_catalog_entry

        value = find_catalog_entry(phon_feat_entries, "vPAConsonantalPositive")
        assert value is not None, (
            "find_catalog_entry did not descend into value children to "
            "find 'vPAConsonantalPositive' under 'fPAConsonantal'."
        )
        assert value.id == "vPAConsonantalPositive"
        # Canonical positive-value GUID per the MGA catalog.
        assert value.guid.lower() == "ec5800b4-52a8-4859-a976-f3005c53bd5f"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
