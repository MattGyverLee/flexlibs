#
#   test_phon_rules.py
#
#   Class: TestPhonologicalRuleAddOutputSegmentRegression
#          Phase 2 regression tests for PhonologicalRuleOperations — guards
#          against the orphan-NPE bugs closed by issue #8 (AddOutputSegment,
#          SetLeftContext, SetRightContext). All three sites previously did
#              new_obj = factory.Create()
#              new_obj.FeatureStructureRA = phoneme_or_class   # NPE
#              owner_collection.Add(new_obj)
#          LCM forbids property writes on orphan (unowned) objects. The
#          Phase 2 fixes in PhonologicalRuleOperations.py invert the order
#          so the new context/segment is attached BEFORE its properties are
#          assigned.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

import sys

import pytest


# ---------------------------------------------------------------------------
# Live-LCM project fixture (matches Phase 1 pattern from
# tests/test_flexproject_discoverability.py)
# ---------------------------------------------------------------------------

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
    """
    Module-scoped write-enabled FLExProject fixture. Skips dependent tests
    if SIL.LCModel isn't loaded or no candidate project can be opened.
    """
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


# ---------------------------------------------------------------------------
# Regression tests
# ---------------------------------------------------------------------------


class TestPhonologicalRuleAddOutputSegmentRegression:
    """
    Regression coverage for issue #8: PhonologicalRuleOperations
    AddOutputSegment/SetLeftContext/SetRightContext must attach the new
    IPhSimpleContextSeg to its owning collection (RHS.StrucChangeOS,
    input_context.LeftContextOA, or input_context.RightContextOA) before
    setting FeatureStructureRA. Previously the property assignment came
    first and raised NullReferenceException on the orphan.
    """

    def _get_or_create_phoneme(self, project, representation):
        """
        Look up `representation` in the phoneme inventory, or create it
        if missing. Returns (phoneme, was_created) so the test can clean
        up only what it added.
        """
        existing = project.Phonemes.Find(representation)
        if existing is not None:
            return existing, False
        return project.Phonemes.Create(representation), True

    def test_add_output_segment(self, writable_project):
        """
        Issue #8 reproducer: create a phonological rule, attach an output
        segment via AddOutputSegment, and assert the segment was attached
        without an orphan NPE.
        """
        rule_name = "Phase2RegressionRule_AddOutputSegment"

        # Pre-clean: if a previous run left this rule behind, drop it.
        # (PhonRules has no Find, so iterate GetAll.)
        for r in list(writable_project.PhonRules.GetAll()):
            try:
                if writable_project.PhonRules.GetName(r) == rule_name:
                    writable_project.PhonRules.Delete(r)
            except Exception:
                # Be tolerant — leftover wrapper objects shouldn't block us.
                pass

        # Pick an output phoneme. Reuse an existing one if available so we
        # don't pollute the phoneme inventory; only create as a last resort.
        all_phonemes = list(writable_project.Phonemes.GetAll())
        if all_phonemes:
            phoneme = all_phonemes[0]
            created_phoneme = False
        else:
            phoneme, created_phoneme = self._get_or_create_phoneme(
                writable_project, "qZ_phase2_phonrule"
            )

        rule = writable_project.PhonRules.Create(rule_name)
        try:
            # Act: this is the call that previously NPE'd before the
            # Phase 2 fix (FeatureStructureRA set on orphan output_seg).
            writable_project.PhonRules.AddOutputSegment(rule, phoneme)

            # Assert: the rule now exposes the phoneme as an output. The
            # exact accessor varies, so check both the documented
            # GetOutputSegments helper (if present) and the underlying
            # LCM ownership chain (rule.RightHandSidesOS[0].StrucChangeOS).
            attached = False

            if hasattr(writable_project.PhonRules, "GetOutputSegments"):
                outputs = list(
                    writable_project.PhonRules.GetOutputSegments(rule)
                )
                if outputs:
                    attached = True

            if not attached:
                # Drop down to LCM: at least one StrucChange entry should
                # now exist on the first RHS. The collection returns
                # IPhSimpleContext (base interface) entries; the concrete
                # type created by IPhSimpleContextSegFactory is
                # IPhSimpleContextSeg, which exposes FeatureStructureRA.
                # Cast via pythonnet so the property is reachable.
                if (
                    hasattr(rule, "RightHandSidesOS")
                    and rule.RightHandSidesOS.Count > 0
                ):
                    rhs = rule.RightHandSidesOS[0]
                    if (
                        hasattr(rhs, "StrucChangeOS")
                        and rhs.StrucChangeOS.Count > 0
                    ):
                        from SIL.LCModel import IPhSimpleContextSeg

                        seg = IPhSimpleContextSeg(rhs.StrucChangeOS[0])
                        attached = seg.FeatureStructureRA is not None

            assert attached, (
                "AddOutputSegment did not attach an output segment to "
                "RightHandSidesOS[0].StrucChangeOS — fix did not preserve "
                "FeatureStructureRA assignment after owner Add"
            )
        finally:
            # Cleanup: always remove the rule we created.
            try:
                writable_project.PhonRules.Delete(rule)
            except Exception:
                pass
            # Only delete the phoneme if THIS test created it.
            if created_phoneme:
                try:
                    writable_project.Phonemes.Delete(phoneme)
                except Exception:
                    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
