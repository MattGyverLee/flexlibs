#
#   test_lexsense_single_string_fields.py
#
#   Round-trip coverage for the three ILexSense ITsString fields:
#   Source, ScientificName, ImportResidue.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

import sys

import pytest


_CANDIDATE_PROJECTS = ("Sena 3", "Test", "SampleLexicon", "SampleLexicon3")


def _try_open_writable_project():
    try:
        from flexlibs2.code.FLExProject import FLExProject
    except Exception:
        return None
    project = FLExProject()
    for name in _CANDIDATE_PROJECTS:
        try:
            project.OpenProject(name, writeEnabled=True)
            return project
        except Exception:
            continue
    return None


@pytest.fixture(scope="module")
def writable_project():
    if "SIL.LCModel" not in sys.modules:
        pytest.skip("Requires SIL.LCModel (FieldWorks installed)")
    project = _try_open_writable_project()
    if project is None:
        pytest.skip(
            "No writable FieldWorks project available "
            f"(tried: {', '.join(_CANDIDATE_PROJECTS)})"
        )
    yield project
    try:
        project.CloseProject()
    except Exception:
        pass


class TestLexSenseSingleStringFields:
    """
    Round-trip coverage for the three single-string sense fields after
    the issue #36 fix:
      - Source         (bibliographic source / citation)
      - ScientificName (binomial nomenclature for biological entries)
      - ImportResidue  (carry-over from non-LIFT import)
    All three are ITsString on ILexSense; each had a matching pair of
    broken getter+setter that this test now pins in tree.
    """

    @pytest.mark.parametrize(
        "getter_name,setter_name,sentinel",
        [
            ("GetSource",         "SetSource",         "qZ_source_value"),
            ("GetScientificName", "SetScientificName", "qZ_scientific_name"),
            ("GetImportResidue",  "SetImportResidue",  "qZ_import_residue"),
        ],
    )
    def test_round_trip(
        self, writable_project, getter_name, setter_name, sentinel
    ):
        """
        Create an entry with a blank sense, Set the field, Get it
        back, assert equal. Before the fix, the Set call raised
        TypeError before ever touching the project.
        """
        lexeme = f"qZ_lexsense_{setter_name}_roundtrip"

        existing = writable_project.LexEntry.Find(lexeme)
        if existing is not None:
            writable_project.LexEntry.Delete(existing)

        entry = writable_project.LexEntry.Create(lexeme)
        try:
            sense = list(entry.SensesOS)[0]

            setter = getattr(writable_project.Senses, setter_name)
            getter = getattr(writable_project.Senses, getter_name)

            # The call that previously crashed with:
            #   TypeError: 'str' value cannot be converted to
            #   ...ITsString
            setter(sense, sentinel)

            got = getter(sense)
            assert got == sentinel, (
                f"{setter_name}/{getter_name} did not round-trip: "
                f"wrote {sentinel!r}, read {got!r}"
            )
        finally:
            try:
                writable_project.LexEntry.Delete(entry)
            except Exception:
                pass

    def test_get_returns_empty_string_when_unset(self, writable_project):
        """
        Get* on an unset single-string field must return "" -- not
        None, not the FLEX null marker "***". The fix's __ReadTsString
        helper normalises both None and "***".
        """
        lexeme = "qZ_lexsense_single_string_empty"

        existing = writable_project.LexEntry.Find(lexeme)
        if existing is not None:
            writable_project.LexEntry.Delete(existing)

        entry = writable_project.LexEntry.Create(lexeme)
        try:
            sense = list(entry.SensesOS)[0]
            for getter_name in (
                "GetSource", "GetScientificName", "GetImportResidue"
            ):
                getter = getattr(writable_project.Senses, getter_name)
                value = getter(sense)
                assert isinstance(value, str), (
                    f"{getter_name}() returned {type(value).__name__}; "
                    "expected str"
                )
                assert value == "", (
                    f"{getter_name}() on a fresh sense returned "
                    f"{value!r}; expected empty string"
                )
        finally:
            try:
                writable_project.LexEntry.Delete(entry)
            except Exception:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
