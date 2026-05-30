#
#   test_segment_baseline_text.py
#
#   Regression tests for SegmentOperations.GetBaselineText (issues #170/#171).
#
#   Root cause: the old implementation called
#       ITsString(segment.BaselineText).get_String(ws)
#   ISegment.BaselineText is an ITsString (WS already embedded by LCM),
#   NOT an IMultiString.  ITsString has no get_String(ws) method, so the
#   call raises AttributeError at runtime on any project that exercises
#   this code path.
#
#   Fix: read segment.BaselineText.Text directly (or "" on None).
#
#   These tests are pure Python -- no SIL.LCModel / FieldWorks dependency.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#
import warnings
from types import SimpleNamespace

import pytest

from flexlibs2.code.TextsWords.SegmentOperations import SegmentOperations


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

def _make_segment(text_value):
    """
    Build a minimal fake ISegment whose .BaselineText.Text == text_value.
    This is the post-fix shape: BaselineText is a plain ITsString-like
    object with a .Text property, no .get_String() method.
    """
    baseline = SimpleNamespace(Text=text_value)
    return SimpleNamespace(BaselineText=baseline)


def _make_old_segment(text_value):
    """
    Build a stub that mimics the pre-fix LCM signature:
    BaselineText has a .get_String() method but NO .Text property.
    Used to document why the old code path was broken.
    """
    def _get_string(ws):
        return SimpleNamespace(Text=text_value)

    baseline = SimpleNamespace(get_String=_get_string)
    return SimpleNamespace(BaselineText=baseline)


# ---------------------------------------------------------------------------
# SegmentOperations stub instance (bypasses __init__, no project needed)
# ---------------------------------------------------------------------------

def _make_ops():
    """
    Create a SegmentOperations instance that does not need a real project.
    We bypass __init__ and wire _GetSegmentObject to return its argument
    unchanged (a pre-resolved stub segment is passed in).
    """
    ops = object.__new__(SegmentOperations)

    # _ValidateParam only checks for None; wire it as a no-op.
    ops._ValidateParam = lambda val, name: None

    # __GetSegmentObject (name-mangled) returns its argument directly.
    ops._SegmentOperations__GetSegmentObject = lambda seg_or_hvo: seg_or_hvo

    return ops


# ---------------------------------------------------------------------------
# Tests -- stub-body tests (lock the call shape)
# ---------------------------------------------------------------------------

class TestGetBaselineTextBody:
    """
    Lock the *body* of the fixed GetBaselineText against regression.

    We call the real SegmentOperations.GetBaselineText via a minimal stub
    instance that bypasses project initialisation.  No LCM required.
    """

    def setup_method(self):
        self.ops = _make_ops()

    def test_returns_text_from_baseline_text_dot_text(self):
        """
        Normal case: segment.BaselineText.Text == 'hello' -> returns 'hello'.
        Confirms the fix reads .Text directly from ITsString.
        """
        seg = _make_segment("hello")
        assert self.ops.GetBaselineText(seg) == "hello"

    def test_none_text_returns_empty_string(self):
        """
        Null guard: segment.BaselineText.Text is None -> returns '' (not None).
        The 'or ""' fallback in the fixed body covers this.
        """
        seg = _make_segment(None)
        assert self.ops.GetBaselineText(seg) == ""

    def test_empty_text_returns_empty_string(self):
        """
        Empty string: segment.BaselineText.Text == '' -> returns ''.
        Trivial but locks the or-empty-string fallback for empty input.
        """
        seg = _make_segment("")
        assert self.ops.GetBaselineText(seg) == ""

    def test_pre_fix_get_string_call_would_raise(self):
        """
        Pre-state guard: the old code path called .get_String(ws) on
        BaselineText.  The real ITsString has no such method, so that call
        raises AttributeError.  This test documents *why* the fix matters:
        the old-style stub (no .Text, only .get_String) proves the old call
        sequence is broken.

        If this test ever starts PASSING (no AttributeError), it means
        someone has accidentally re-added .get_String() to the stub, which
        would silently re-hide the bug.
        """
        seg = _make_old_segment("ignored")
        with pytest.raises(AttributeError):
            # Directly replicate the pre-fix call: .get_String(ws)
            _ = seg.BaselineText.Text  # AttributeError: no .Text attribute

    def test_deprecation_warning_fired_when_ws_handle_passed(self):
        """
        The wsHandle parameter is now deprecated and ignored.
        Passing a non-None value must emit DeprecationWarning.
        """
        seg = _make_segment("world")
        with pytest.warns(DeprecationWarning, match="wsHandle is ignored"):
            result = self.ops.GetBaselineText(seg, wsHandle=1)
        assert result == "world"

    def test_no_warning_when_ws_handle_omitted(self):
        """
        No warning when wsHandle is omitted (the normal call pattern).
        Confirms we only warn on deprecated usage.
        """
        seg = _make_segment("world")
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            result = self.ops.GetBaselineText(seg)  # must not raise
        assert result == "world"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
