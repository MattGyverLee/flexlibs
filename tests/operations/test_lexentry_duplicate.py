#
#   test_lexentry_duplicate.py
#
#   Class: TestLexEntryDuplicateDeep
#          Regression coverage for issue #31:
#          LexEntryOperations.Duplicate(entry, deep=True) raised
#          AttributeError because _copy_sense_content in
#          LexSenseOperations called `.CopyAlternatives` on
#          duplicate.Source -- a single-string ITsString field that
#          has no multistring methods. The fix replaces the multistring
#          copy with a direct ITsString assignment.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

import sys

import pytest


# Every test in this module opens a real .fwdata project via the
# writable_project fixture.
pytestmark = pytest.mark.requires_live_project


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


class TestLexEntryDuplicateDeep:
    """
    Coverage for the deep-Duplicate path through _copy_sense_content
    after the issue #31 fix. The bug surfaced specifically when the
    duplicate code reached the Source field, which is ITsString and
    has no CopyAlternatives. The test creates an entry with a Source
    value set, duplicates it deep=True, and asserts no AttributeError.
    """

    def test_duplicate_deep_does_not_raise_on_source_field(
        self, writable_project
    ):
        """
        Direct reproducer from #31's stack trace:
            entry = leops.Find("some-stem")
            new_entry = leops.Duplicate(entry, deep=True)  # crashed here

        After the fix, Duplicate must complete without AttributeError
        even when the source sense has a non-empty Source field.
        """
        lexeme = "qZ_dup_source_regression"

        # Pre-clean: remove any leftover from a previous run.
        existing = writable_project.LexEntry.Find(lexeme)
        if existing is not None:
            writable_project.LexEntry.Delete(existing)

        entry = writable_project.LexEntry.Create(lexeme)
        duplicate = None
        try:
            senses = list(entry.SensesOS)
            assert len(senses) >= 1, (
                "Create with create_blank_sense=True should yield 1 sense"
            )
            sense = senses[0]

            # Set Source so the _copy_sense_content path under test
            # actually copies a non-empty ITsString. SetSource itself
            # has a pre-existing bug (assigns a Python str to an
            # ITsString field and crashes), so build the ITsString
            # directly via TsStringUtils to make this test independent
            # of that other issue.
            from SIL.LCModel.Core.Text import TsStringUtils

            ws = writable_project.project.DefaultVernWs
            sense.Source = TsStringUtils.MakeString(
                "qZ-regression-source", ws
            )

            # The call that previously crashed with:
            #   AttributeError: 'ITsString' object has no attribute
            #   'CopyAlternatives'
            duplicate = writable_project.LexEntry.Duplicate(entry, deep=True)

            assert duplicate is not None, "Duplicate returned None"
            dup_senses = list(duplicate.SensesOS)
            assert len(dup_senses) >= 1, (
                "Deep duplicate did not propagate senses to the new entry"
            )
            # Source must round-trip. Read the ITsString text via the
            # raw LCM .Text property to avoid SetSource/GetSource's
            # multi-string handling (they have pre-existing quirks
            # independent of #31).
            from SIL.LCModel.Core.KernelInterfaces import ITsString

            dup_source_tss = dup_senses[0].Source
            assert dup_source_tss is not None, (
                "Duplicate's Source is None; the fix did not assign it"
            )
            dup_source_text = ITsString(dup_source_tss).Text
            assert dup_source_text == "qZ-regression-source", (
                "Source did not round-trip through deep duplicate: "
                f"got {dup_source_text!r}"
            )
        finally:
            if duplicate is not None:
                try:
                    writable_project.LexEntry.Delete(duplicate)
                except Exception:
                    pass
            try:
                writable_project.LexEntry.Delete(entry)
            except Exception:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
