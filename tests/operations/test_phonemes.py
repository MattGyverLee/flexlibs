#
#   test_phonemes.py
#
#   Class: TestPhonemeOperationsCreateRegression
#          Phase 2 regression tests for PhonemeOperations.Create — guards
#          against the orphan-NPE bug closed by issue #6 where a freshly
#          created IPhPhoneme had `.Name.set_String(...)` called on it
#          before the phoneme was attached to its owning collection. LCM
#          forbids setting properties on an orphan object; the fix in
#          PhonemeOperations.py moves `phoneme_set.PhonemesOC.Add(...)`
#          ahead of the Name assignment.
#
#          Reproducer:
#              phoneme = project.Phonemes.Create("o")    # ASCII; NFD
#                                                        # normalization is
#                                                        # a separate Phase
#                                                        # 3 concern.
#              assert project.Phonemes.GetRepresentation(phoneme) == "o"
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

import sys

import pytest


# ---------------------------------------------------------------------------
# Live-LCM project fixture (matches the Phase 1 pattern from
# tests/test_flexproject_discoverability.py)
# ---------------------------------------------------------------------------

_CANDIDATE_PROJECTS = ("Sena 3", "Test", "SampleLexicon", "SampleLexicon3")


def _try_open_project(write_enabled):
    """
    Attempt to open one of the standard test projects.

    Returns the open FLExProject on success, or None if no FieldWorks
    project is reachable. Caller is responsible for CloseProject().
    """
    try:
        from flexlibs2.code.FLExProject import FLExProject
    except Exception:
        return None

    project = FLExProject()
    for name in _CANDIDATE_PROJECTS:
        try:
            project.OpenProject(name, writeEnabled=write_enabled)
            return project
        except Exception:
            continue
    return None


@pytest.fixture(scope="module")
def writable_project():
    """
    Module-scoped fixture providing an open, write-enabled FLExProject.

    Skips dependent tests if SIL.LCModel isn't loaded or no candidate
    FieldWorks project can be opened in write mode.
    """
    if "SIL.LCModel" not in sys.modules:
        pytest.skip("Requires SIL.LCModel (FieldWorks installed)")

    project = _try_open_project(write_enabled=True)
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


# ---------------------------------------------------------------------------
# Regression tests
# ---------------------------------------------------------------------------


class TestPhonemeOperationsCreateRegression:
    """
    Regression coverage for issue #6: PhonemeOperations.Create() must attach
    the new phoneme to phoneme_set.PhonemesOC before setting Name, otherwise
    LCM raises a NullReferenceException ("orphan NPE") because property
    writes on unowned objects are not permitted.
    """

    def test_create_does_not_npe(self, writable_project):
        """
        Issue #6 reproducer: creating a phoneme with ASCII representation
        must succeed (no NPE) and round-trip its representation.

        Uses an ASCII character so this test is decoupled from NFD/Unicode
        normalization concerns, which belong to Phase 3.
        """
        # Use a representation that's extremely unlikely to clash with
        # existing phoneme inventory. If it does, the Create() call will
        # raise FP_ParameterError("Phoneme '...' already exists") and we
        # adapt by deleting first.
        representation = "qZ_phase2_regression"

        # Pre-clean: if a previous run left this phoneme behind, remove it
        # so the regression test starts from a clean slate.
        existing = writable_project.Phonemes.Find(representation)
        if existing is not None:
            writable_project.Phonemes.Delete(existing)

        # Act: this is the call that previously NPE'd before the Phase 2
        # fix (set_String on an orphan phoneme).
        phoneme = writable_project.Phonemes.Create(representation)

        try:
            # Assert: returned object is non-None and its representation
            # round-trips through GetRepresentation.
            assert phoneme is not None, (
                "Create() returned None instead of an IPhPhoneme"
            )
            assert writable_project.Phonemes.GetRepresentation(phoneme) == (
                representation
            ), (
                "Phoneme representation did not round-trip after Create() — "
                "fix did not preserve Name assignment after owner Add"
            )
        finally:
            # Clean up: delete the phoneme so re-running the suite is
            # idempotent.
            try:
                writable_project.Phonemes.Delete(phoneme)
            except Exception:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
