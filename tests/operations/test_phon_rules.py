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


class TestPhonRulesFindDeleteRegression:
    """
    Regression coverage for issue #5: PhonologicalRule wrapper / PhonRules
    operations. Two bugs were fixed:

    Bug 1 — PhonologicalRule.name always returned "":
        wrapper used self._obj.OwnerOfClass.project.DefaultAnalWs which
        raised AttributeError (no .project on OwnerOfClass). A bare
        `except` swallowed the error and returned "". Cascading effect:
        PhonRules.Find always returned None because it compared against
        wrapper.name.
        Fix: use self._obj.Cache.DefaultAnalWs.

    Bug 2 — PhonRules.Delete(wrapper) raised TypeError:
        __ResolveObject did not unwrap PhonologicalRule wrappers, so
        ICollection.Contains was handed a Python object instead of an
        IPhSegmentRule and threw TypeError. Fix: __ResolveObject now
        duck-types on _obj/_concrete and returns the raw LCM object.

    Cleanup pattern: unique rule names per test + try/finally Delete on
    the raw LCM rule (looked up by iterating PhonRulesOS and matching on
    GetName, which doesn't depend on the wrapper.name code path). This
    mirrors how TestPhonologicalRuleAddOutputSegmentRegression handles
    cleanup since the writable_project fixture is not transactional.
    """

    _RULE_NAMES = (
        "Phase4RegressionRule_NameNotEmpty",
        "Phase4RegressionRule_FindAfterCreate",
        "Phase4RegressionRule_DeleteWrapper",
    )

    def _cleanup_rule_by_name(self, project, rule_name):
        """
        Find the raw LCM rule by name (using GetName, NOT wrapper.name —
        wrapper.name is the very thing under test here) and Delete it.
        Safe to call even if the rule doesn't exist.
        """
        phon_data = project.lp.PhonologicalDataOA
        if not phon_data or not hasattr(phon_data, "PhonRulesOS"):
            return
        targets = []
        for raw_rule in list(phon_data.PhonRulesOS):
            try:
                if project.PhonRules.GetName(raw_rule) == rule_name:
                    targets.append(raw_rule)
            except Exception:
                pass
        for raw_rule in targets:
            try:
                project.PhonRules.Delete(raw_rule)
            except Exception:
                pass

    def test_wrapper_name_returns_actual_rule_name_not_empty(self, writable_project):
        """
        Issue #5 Bug 1 reproducer: wrapper.name was always returning ""
        due to a swallowed AttributeError on OwnerOfClass.project. After
        the fix (Cache.DefaultAnalWs), the wrapper should expose the
        actual rule name.
        """
        rule_name = self._RULE_NAMES[0]
        self._cleanup_rule_by_name(writable_project, rule_name)
        try:
            writable_project.PhonRules.Create(rule_name)
            # Find the wrapped version via GetAll(). Identify it WITHOUT
            # relying on wrapper.name (since that's under test) — use
            # GetName on the underlying raw object.
            wrappers = list(writable_project.PhonRules.GetAll())
            wrapped = None
            for w in wrappers:
                try:
                    if writable_project.PhonRules.GetName(w._obj) == rule_name:
                        wrapped = w
                        break
                except Exception:
                    continue
            assert wrapped is not None, (
                "Could not locate created rule via GetAll()"
            )
            assert wrapped.name == rule_name, (
                f"wrapper.name returned {wrapped.name!r}, "
                f"expected {rule_name!r}"
            )
        finally:
            self._cleanup_rule_by_name(writable_project, rule_name)

    def test_find_returns_rule_after_create(self, writable_project):
        """
        Issue #5 Bug 1 cascading consequence: Find iterates GetAll() and
        compares against wrapper.name. If wrapper.name returned "", Find
        always returned None. After the fix, Find must locate a freshly
        created rule.
        """
        rule_name = self._RULE_NAMES[1]
        self._cleanup_rule_by_name(writable_project, rule_name)
        try:
            writable_project.PhonRules.Create(rule_name)
            found = writable_project.PhonRules.Find(rule_name)
            assert found is not None, (
                "Find returned None for a rule that was just created — "
                "wrapper.name regression is back"
            )
            assert found.name == rule_name
        finally:
            self._cleanup_rule_by_name(writable_project, rule_name)

    def test_delete_accepts_wrapper_from_getall(self, writable_project):
        """
        Issue #5 Bug 2 reproducer: Delete(wrapper) used to TypeError on
        ICollection.Contains because __ResolveObject did not unwrap the
        PhonologicalRule wrapper. After the fix, passing a wrapper
        straight from GetAll() must work and the rule must be gone
        afterwards.
        """
        rule_name = self._RULE_NAMES[2]
        self._cleanup_rule_by_name(writable_project, rule_name)
        rule_created = False
        try:
            writable_project.PhonRules.Create(rule_name)
            rule_created = True

            # Locate the wrapper via GetAll() without using wrapper.name
            # (defensive — even if Bug 1 ever resurfaces, this test is
            # specifically about Bug 2 and shouldn't be tangled with it).
            wrappers = list(writable_project.PhonRules.GetAll())
            target = None
            for w in wrappers:
                try:
                    if writable_project.PhonRules.GetName(w._obj) == rule_name:
                        target = w
                        break
                except Exception:
                    continue
            assert target is not None, (
                "Could not find the created rule's wrapper in GetAll()"
            )

            # This call previously raised TypeError on ICollection.Contains.
            writable_project.PhonRules.Delete(target)
            rule_created = False  # successful delete — no further cleanup

            # Confirm the rule was actually removed.
            phon_data = writable_project.lp.PhonologicalDataOA
            remaining_names = []
            if phon_data and hasattr(phon_data, "PhonRulesOS"):
                for raw_rule in phon_data.PhonRulesOS:
                    try:
                        remaining_names.append(
                            writable_project.PhonRules.GetName(raw_rule)
                        )
                    except Exception:
                        pass
            assert rule_name not in remaining_names, (
                f"Delete(wrapper) returned without error but rule "
                f"{rule_name!r} is still present"
            )
        finally:
            if rule_created:
                self._cleanup_rule_by_name(writable_project, rule_name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
