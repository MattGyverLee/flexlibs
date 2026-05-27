#
#   test_wfi_morph_bundle.py
#
#   Class: TestWfiMorphBundleGloss
#          Regression coverage for issue #16 Bug 2: GetGloss/SetGloss
#          previously referenced `bundle.Gloss`, a field that does not
#          exist on IWfiMorphBundle. Calls raised AttributeError on
#          every input.
#
#          The fix routes GetGloss through bundle.SenseRA.Gloss (with
#          a None-guard) and refuses SetGloss outright, since writing
#          via SenseRA would mutate shared lexical-sense state for
#          every bundle that references the sense -- a surprising
#          side effect to attach to a per-bundle setter.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

import inspect
import sys

import pytest


class TestWfiMorphBundleGlossContract:
    """
    Static-contract coverage for WfiMorphBundleOperations.GetGloss and
    SetGloss after the issue #16 fix. These tests do not require a
    live FieldWorks project -- they verify the method shape and the
    unconditional SetGloss raise.
    """

    def test_get_and_set_gloss_remain_public_methods(self):
        """
        GetGloss and SetGloss must remain on the class surface so the
        AttributeError reproducer from issue #16 cannot resurface as
        AttributeError for the wrong reason (e.g. method renamed). A
        callable that explicitly refuses is the documented contract.
        """
        from flexlibs2.code.TextsWords.WfiMorphBundleOperations import (
            WfiMorphBundleOperations,
        )

        for name in ("GetGloss", "SetGloss"):
            assert name in dir(WfiMorphBundleOperations), (
                f"{name} missing from WfiMorphBundleOperations"
            )
            # GetGloss/SetGloss are wrapped by the @OperationsMethod
            # descriptor; retrieve via descriptor protocol on the class
            # (which yields a bound-method-like callable) rather than
            # via inspect.getattr_static (which yields the raw
            # descriptor object).
            attr = getattr(WfiMorphBundleOperations, name)
            assert callable(attr), f"{name} is not callable on class"
            assert not isinstance(attr, property), (
                f"{name} must be a method, not a property"
            )

    def test_set_gloss_raises_unconditionally(self):
        """
        SetGloss must always raise FP_ParameterError with a message
        pointing the caller at LexSenseOperations.SetGloss. Mutating
        a shared lexical sense from a per-bundle setter would be a
        surprising side effect; explicit refusal is the contract.
        """
        from flexlibs2.code.TextsWords.WfiMorphBundleOperations import (
            WfiMorphBundleOperations,
        )
        from flexlibs2.code.FLExProject import FP_ParameterError

        class _MockSelf:
            project = None

        with pytest.raises(FP_ParameterError) as exc_info:
            WfiMorphBundleOperations.SetGloss(
                _MockSelf(), object(), "anything"
            )

        message = str(exc_info.value)
        assert "not supported" in message, (
            "SetGloss raise message should explain it's not supported; "
            f"got: {message!r}"
        )
        assert "LexSenseOperations.SetGloss" in message, (
            "SetGloss raise message should point at the sense-based "
            f"alternative; got: {message!r}"
        )

    def test_get_gloss_returns_empty_for_unlinked_bundle(self):
        """
        GetGloss must return an empty string when the bundle has no
        linked sense (SenseRA is None) -- it must not raise
        AttributeError trying to read sense.Gloss off of None.

        This guards against a partial fix that forwards to SenseRA
        without a None-guard.
        """
        from flexlibs2.code.TextsWords.WfiMorphBundleOperations import (
            WfiMorphBundleOperations,
        )

        # Stand up the smallest possible mock that satisfies the
        # method's dependencies. __GetBundleObject is a private
        # resolver that this test sidesteps by patching with a passthrough.
        class _MockBundle:
            SenseRA = None  # the case under test

        captured = {}

        def _passthrough_get_bundle(self, bundle_or_hvo):
            captured["called"] = True
            return bundle_or_hvo

        def _passthrough_ws(self, ws):
            return 1  # any int; SenseRA is None so it's never used

        # Monkey-patch the private resolvers on the class. These names
        # are mangled because they're double-underscore in the source.
        mangled_get_bundle = (
            "_WfiMorphBundleOperations__GetBundleObject"
        )
        mangled_ws = "_WfiMorphBundleOperations__WSHandleAnal"

        original_get_bundle = getattr(
            WfiMorphBundleOperations, mangled_get_bundle, None
        )
        original_ws = getattr(WfiMorphBundleOperations, mangled_ws, None)
        if original_get_bundle is None or original_ws is None:
            pytest.skip(
                "Private resolver names changed; "
                "test_get_gloss_returns_empty_for_unlinked_bundle "
                "needs updating"
            )

        setattr(
            WfiMorphBundleOperations,
            mangled_get_bundle,
            _passthrough_get_bundle,
        )
        setattr(WfiMorphBundleOperations, mangled_ws, _passthrough_ws)
        try:
            class _MockSelf:
                project = None

            result = WfiMorphBundleOperations.GetGloss(
                _MockSelf(), _MockBundle()
            )
            assert result == "", (
                "GetGloss must return empty string for unlinked bundle, "
                f"got {result!r}"
            )
        finally:
            setattr(
                WfiMorphBundleOperations,
                mangled_get_bundle,
                original_get_bundle,
            )
            setattr(WfiMorphBundleOperations, mangled_ws, original_ws)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
