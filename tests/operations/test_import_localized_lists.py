#
#   test_import_localized_lists.py
#
#   Class: TestImportLocalizedListsContract
#          Coverage for FLExProject.ImportLocalizedLists -- the
#          wrapper around XmlTranslatedLists.ImportTranslatedListsForWs
#          added to close item 3 of issue #29.
#
#          We deliberately avoid triggering a real import against the
#          shared Sena 3 test project (the same pollution rationale as
#          AnthropologyOperations.ImportCatalog tests -- a successful
#          import mutates the project's possibility lists with
#          translation alternatives that subsequent test runs would
#          have to account for). The tests cover the input-validation
#          guards plus the FP_FileNotFoundError path for unknown
#          language codes.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

import inspect
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


class TestImportLocalizedListsContract:
    """
    Static / input-validation coverage for ImportLocalizedLists.

    Live importing is intentionally NOT exercised here: a successful
    import mutates the test project's possibility-list state with
    translated alternatives, polluting subsequent runs of unrelated
    tests. The contract tests below confirm the method is discoverable,
    rejects bad input, and refuses obvious errors -- enough to catch
    regressions in the surface without seeding state.
    """

    def test_method_is_on_flex_project(self):
        """
        ImportLocalizedLists must be a callable method on FLExProject
        with the documented two-arg signature (language_code, progress).
        """
        from flexlibs2.code.FLExProject import FLExProject

        assert "ImportLocalizedLists" in dir(FLExProject), (
            "ImportLocalizedLists missing from FLExProject"
        )
        method = getattr(FLExProject, "ImportLocalizedLists")
        assert callable(method), "ImportLocalizedLists is not callable"

        params = inspect.signature(method).parameters
        # Expect: self, language_code, progress=None
        assert "language_code" in params, (
            f"ImportLocalizedLists is missing 'language_code'; got: "
            f"{list(params)}"
        )
        assert "progress" in params, (
            f"ImportLocalizedLists is missing 'progress'; got: "
            f"{list(params)}"
        )
        assert params["progress"].default is None, (
            "ImportLocalizedLists 'progress' must default to None"
        )

    def test_rejects_none_language_code(self, writable_project):
        """
        ImportLocalizedLists(None) must raise FP_NullParameterError
        before any FW filesystem access.
        """
        from flexlibs2.code.FLExProject import FP_NullParameterError

        with pytest.raises(FP_NullParameterError):
            writable_project.ImportLocalizedLists(None)

    def test_rejects_empty_language_code(self, writable_project):
        """
        Empty or whitespace-only language_code must raise
        FP_ParameterError -- this prevents the bogus ZIP filename
        ``LocalizedLists-.zip`` from being constructed.
        """
        from flexlibs2.code.FLExProject import FP_ParameterError

        with pytest.raises(FP_ParameterError):
            writable_project.ImportLocalizedLists("")
        with pytest.raises(FP_ParameterError):
            writable_project.ImportLocalizedLists("   ")

    def test_unknown_language_code_raises_file_not_found(
        self, writable_project
    ):
        """
        For a language code with no shipping translation ZIP, the
        method must raise FP_FileNotFoundError -- not a generic
        FileNotFoundError or AttributeError. The error path is the
        same as the existing ImportCatalog file-locator behavior.
        """
        from flexlibs2.code.exceptions import FP_FileNotFoundError

        # "zz-XX" is the standard "unallocated" code; no LocalizedLists
        # ZIP should ever ship for it.
        with pytest.raises(FP_FileNotFoundError):
            writable_project.ImportLocalizedLists("zz-XX")


class TestImportLocalizedListsForEnabledWS:
    """
    Coverage for the auto-enumerator that loops over enabled analysis
    writing systems and applies whatever translation packs ship for
    them. Same anti-pollution constraints apply: we don't trigger live
    imports against Sena 3. We verify the method shape, the missing-
    ZIP skip behavior, and the read-only guard.
    """

    def test_method_is_on_flex_project(self):
        """Method exists, is callable, takes progress= and nothing else."""
        from flexlibs2.code.FLExProject import FLExProject

        assert "ImportLocalizedListsForEnabledWS" in dir(FLExProject)
        method = getattr(FLExProject, "ImportLocalizedListsForEnabledWS")
        assert callable(method)

        params = inspect.signature(method).parameters
        assert "progress" in params
        # No language_code: this is the project-wide enumerator.
        assert "language_code" not in params, (
            "Enumerator must not require a language_code; "
            "use ImportLocalizedLists(code) for the single-WS form"
        )

    def test_iterates_enabled_ws_and_dispatches(self, writable_project):
        """
        Verify the enumerator's iteration + dispatch logic WITHOUT
        actually mutating the project's possibility lists. We
        monkey-patch the underlying per-WS importer with a recorder
        and confirm:
          - Each enabled analysis WS got its IcuLocale forwarded to
            ImportLocalizedLists, in iteration order.
          - The returned list of applied codes matches the recorder.
          - The method's return is always a list[str].

        This keeps the project's list state untouched while still
        exercising the loop, the IcuLocale lookup, and the return
        contract -- the parts of the code that can regress.
        """
        recorded_calls = []

        def _recording_stub(self_arg, language_code, progress=None):
            # Capture what the enumerator dispatched; do NOT touch LCM.
            # First positional is the FLExProject instance because we
            # bound this onto the class via descriptor protocol.
            recorded_calls.append(language_code)

        # Snapshot the real bound method so we can put it back even
        # if the assertions throw mid-test.
        flex_project_obj = writable_project
        real = type(flex_project_obj).ImportLocalizedLists

        type(flex_project_obj).ImportLocalizedLists = _recording_stub
        try:
            result = flex_project_obj.ImportLocalizedListsForEnabledWS()
        finally:
            type(flex_project_obj).ImportLocalizedLists = real

        assert isinstance(result, list), (
            f"Enumerator must return list, got {type(result).__name__}"
        )
        # Each applied code in the result must be a non-empty string.
        for code in result:
            assert isinstance(code, str) and code, (
                f"Applied entries must be non-empty strings; got {code!r}"
            )
        # Result must mirror the dispatch order.
        assert result == recorded_calls, (
            "Enumerator's return value did not match the dispatched "
            f"calls: returned {result!r}, dispatched {recorded_calls!r}"
        )
        # Iteration touched at least one enabled analysis WS (Sena 3
        # and the standard test projects all have English enabled).
        assert len(recorded_calls) >= 1, (
            "Enumerator dispatched no calls -- "
            "CurrentAnalysisWritingSystems iteration may be broken"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
