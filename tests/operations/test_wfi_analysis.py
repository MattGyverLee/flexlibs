#
#   test_wfi_analysis.py
#
#   Class: TestWfiAnalysisDelete
#          Regression coverage for issue #32:
#          WfiAnalysisOperations.Delete raised AttributeError
#          ("'ICmObject' object has no attribute 'AnalysesOC'") for
#          every input. The fix casts analysis.Owner -- which pythonnet
#          types as the base ICmObject -- to IWfiWordform before
#          touching AnalysesOC.
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
    """Open one of the standard test projects in write mode, or None."""
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
    """Module-scoped writable FLExProject; skip if LCM or project unavailable."""
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


class TestWfiAnalysisDelete:
    """
    Regression coverage for issue #32: WfiAnalysisOperations.Delete
    previously crashed with AttributeError because it accessed
    AnalysesOC on `analysis.Owner` which pythonnet returns as the
    base ICmObject (no AnalysesOC). The fix casts to IWfiWordform.
    """

    def test_delete_round_trips_on_existing_wordform(self, writable_project):
        """
        Create a temporary analysis on an existing wordform, then
        delete it. Before the fix, Delete raised AttributeError on
        every input -- this test would have failed during the Delete
        call. After the fix, the round-trip succeeds and the
        wordform's AnalysesOC count returns to its starting value.
        """
        # Find any wordform with no analyses (preferred -- minimizes
        # disturbance) or fall back to one with analyses. We then
        # create our own throw-away analysis and delete it.
        candidate_wf = None
        starting_count = 0
        for wf in writable_project.Wordforms.GetAll():
            count = wf.AnalysesOC.Count
            if count == 0:
                candidate_wf = wf
                starting_count = 0
                break
        if candidate_wf is None:
            # Fall back to the first wordform; record its analysis
            # count so we can assert the delta returns to zero.
            for wf in writable_project.Wordforms.GetAll():
                candidate_wf = wf
                starting_count = wf.AnalysesOC.Count
                break

        if candidate_wf is None:
            pytest.skip("Project has no wordforms to test against")

        # Create an analysis we own and can safely delete.
        analysis = writable_project.WfiAnalyses.Create(candidate_wf)
        assert analysis is not None, "WfiAnalyses.Create returned None"
        assert candidate_wf.AnalysesOC.Count == starting_count + 1, (
            f"AnalysesOC count did not increase after Create: "
            f"{candidate_wf.AnalysesOC.Count} vs expected "
            f"{starting_count + 1}"
        )

        # The fix under test: Delete must not raise AttributeError.
        writable_project.WfiAnalyses.Delete(analysis)

        assert candidate_wf.AnalysesOC.Count == starting_count, (
            f"AnalysesOC count did not return to starting value after "
            f"Delete: {candidate_wf.AnalysesOC.Count} vs expected "
            f"{starting_count}. The Remove() call may have hit a "
            f"different cast path."
        )


class TestWfiAnalysisSetApprovalStatus:
    """
    Regression coverage for issue #26 (the WfiAnalysis EvaluationsRC
    ownership-ordering bug). The previous implementation created an
    ICmAgentEvaluation, set evaluation.Agent on the unowned object,
    and added it to analysis.EvaluationsRC -- but EvaluationsRC is a
    reference collection that does not confer ownership. Property
    writes on the unowned evaluation would NPE.

    The fix delegates to LCM's purpose-built
    ICmAgent.SetEvaluation(target, Opinions) which handles ownership
    and bookkeeping internally. These tests exercise the three valid
    status transitions to confirm the new path doesn't raise.
    """

    def test_set_approval_status_does_not_raise(self, writable_project):
        """
        Issue #26 part 2: SetApprovalStatus previously trampled on the
        Phase 2 ownership-ordering rule by setting evaluation.Agent on
        an unowned ICmAgentEvaluation and adding it to a REFERENCE
        collection (EvaluationsRC). After the fix, SetApprovalStatus
        delegates to ICmAgent.SetEvaluation(target, Opinions) which
        handles ownership internally.

        We verify only the no-raise contract for each of the three
        status values. The reverse direction (GetApprovalStatus
        reading the new state correctly) is a separate concern:
        GetApprovalStatus has a pre-existing bug that treats every
        non-empty EvaluationsRC as APPROVED regardless of whether
        the evaluation is an approve or disapprove. Filing that is
        out of scope here -- this test pins the SetApprovalStatus
        side of the contract.
        """
        from flexlibs2.code.TextsWords.WfiAnalysisOperations import (
            ApprovalStatusTypes,
        )

        # Need at least one human agent. Read AnalyzingAgentsOC directly
        # to stay independent of the AgentOperations wrapper.
        has_human_agent = False
        for raw in writable_project.lp.AnalyzingAgentsOC:
            if getattr(raw, "Human", False):
                has_human_agent = True
                break
        if not has_human_agent:
            pytest.skip(
                "Project has no human agents; SetApprovalStatus "
                "refuses without one. Create via "
                "AgentOperations.CreateHumanAgent first."
            )

        # Find a wordform to attach a throw-away analysis to.
        candidate_wf = None
        for wf in writable_project.Wordforms.GetAll():
            candidate_wf = wf
            break
        if candidate_wf is None:
            pytest.skip("Project has no wordforms")

        analysis = writable_project.WfiAnalyses.Create(candidate_wf)
        try:
            # Each transition must complete without raising. Before the
            # fix, each call would NPE on the unowned-evaluation
            # property setter.
            for status in (
                ApprovalStatusTypes.APPROVED,
                ApprovalStatusTypes.DISAPPROVED,
                ApprovalStatusTypes.UNAPPROVED,
                ApprovalStatusTypes.APPROVED,  # re-apply
            ):
                writable_project.WfiAnalyses.SetApprovalStatus(
                    analysis, status
                )
        finally:
            try:
                writable_project.WfiAnalyses.Delete(analysis)
            except Exception:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
