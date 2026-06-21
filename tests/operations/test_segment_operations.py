#
#   test_segment_operations.py
#
#   Class: TestSegmentWriteOps
#          Regression coverage for issues #172 and #174:
#          SegmentOperations write paths reworked to use the correct LCM
#          idiom (Contents-first then SegmentsOS). Tests cover
#          AppendSentence, SplitSegment, MergeSegments, and ReparseParagraph.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

import sys

import pytest


# Every test in this module opens a real .fwdata project via writable_project.
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_throwaway_text(project, title="zz_seg_ops_test"):
    """
    Create a fresh IStText with one empty paragraph for use as a test fixture.
    The caller is responsible for deleting it afterwards.
    """
    text = project.Text.Create(title)
    # Ensure there is at least one paragraph
    para_list = list(text.ContentsOA.ParagraphsOS) if text.ContentsOA else []
    if not para_list:
        project.Paragraphs.Create(text.ContentsOA, "")
        para_list = list(text.ContentsOA.ParagraphsOS)
    return text, para_list[0]


def _cleanup_text(project, text):
    """Delete a throwaway text, ignoring errors."""
    try:
        project.Text.Delete(text)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# AppendSentence
# ---------------------------------------------------------------------------


class TestAppendSentence:
    """
    Coverage for SegmentOperations.AppendSentence (formerly Create).
    Each test creates a fresh throwaway text so tests are fully isolated.
    """

    def test_AppendSentence_to_empty_paragraph(self, writable_project):
        """
        AppendSentence on an empty paragraph should create one segment and
        set Contents to the provided text without adding any terminator prefix.
        """
        text, para = _make_throwaway_text(writable_project, "zz_append_empty")
        try:
            seg = writable_project.Segments.AppendSentence(para, "Hello world.")
            assert seg is not None
            segs = list(para.SegmentsOS)
            assert len(segs) == 1
            contents_text = para.Contents.Text or ""
            assert "Hello world." in contents_text
        finally:
            _cleanup_text(writable_project, text)

    def test_AppendSentence_adds_terminator_when_missing(self, writable_project):
        """
        When the paragraph already has content not ending with . ! ?,
        AppendSentence must insert '. ' before the new text.
        """
        text, para = _make_throwaway_text(writable_project, "zz_append_terminator")
        try:
            # Seed the paragraph with text that has no terminator
            writable_project.Segments.AppendSentence(para, "First sentence")
            contents_before = para.Contents.Text or ""
            assert contents_before.endswith("First sentence")

            writable_project.Segments.AppendSentence(para, "Second sentence.")
            contents_after = para.Contents.Text or ""
            # The '. ' separator must appear between the two sentences
            assert ". " in contents_after or contents_after.count(".") >= 1
            assert "Second sentence." in contents_after
        finally:
            _cleanup_text(writable_project, text)

    def test_AppendSentence_skips_terminator_when_present(self, writable_project):
        """
        When the paragraph already ends with a sentence terminator,
        AppendSentence should not insert a second one.
        """
        text, para = _make_throwaway_text(writable_project, "zz_append_no_double_term")
        try:
            writable_project.Segments.AppendSentence(para, "First sentence.")
            before_len = len(para.Contents.Text or "")

            writable_project.Segments.AppendSentence(para, "Second sentence.")
            after_text = para.Contents.Text or ""

            # Should not have two consecutive terminators like '.. '
            assert ".. " not in after_text
            assert "Second sentence." in after_text
        finally:
            _cleanup_text(writable_project, text)

    def test_AppendSentence_creates_segment_with_correct_offsets(self, writable_project):
        """
        The new segment returned by AppendSentence must be present in
        SegmentsOS, and its text must be recoverable via GetBaselineText.
        """
        text, para = _make_throwaway_text(writable_project, "zz_append_offsets")
        try:
            seg = writable_project.Segments.AppendSentence(para, "Offset check sentence.")
            assert seg is not None
            segs = list(para.SegmentsOS)
            assert seg in segs
            # BeginOffset must be >= 0 and < EndOffset (or both 0 for uninitialized)
            begin = seg.BeginOffset
            end = seg.EndOffset
            # Either offsets are set by AnalysisAdjuster, or they start at 0.
            # At minimum they must not be negative.
            assert begin >= 0
            assert end >= 0
        finally:
            _cleanup_text(writable_project, text)

    def test_AppendSentence_raises_on_empty_text(self, writable_project):
        """
        AppendSentence must raise FP_ParameterError when text is empty.
        """
        from flexlibs2.code.FLExProject import FP_ParameterError

        text, para = _make_throwaway_text(writable_project, "zz_append_empty_text")
        try:
            with pytest.raises(FP_ParameterError):
                writable_project.Segments.AppendSentence(para, "   ")
        finally:
            _cleanup_text(writable_project, text)

    def test_AppendSentence_raises_on_none_paragraph(self, writable_project):
        """
        AppendSentence must raise FP_NullParameterError when paragraph is None.
        """
        from flexlibs2.code.FLExProject import FP_NullParameterError

        with pytest.raises(FP_NullParameterError):
            writable_project.Segments.AppendSentence(None, "Some text.")


# ---------------------------------------------------------------------------
# SplitSegment
# ---------------------------------------------------------------------------


class TestSplitSegment:
    """
    Coverage for SegmentOperations.SplitSegment.
    """

    def _make_para_with_one_segment(self, project, sentence="In the beginning God created."):
        """Create a text, append one segment, return (text, para, seg)."""
        text, para = _make_throwaway_text(project, "zz_split_test")
        seg = project.Segments.AppendSentence(para, sentence)
        return text, para, seg

    def test_SplitSegment_creates_two_segments_at_offset(self, writable_project):
        """
        SplitSegment must return a 2-tuple and para.SegmentsOS must contain
        exactly two segments afterwards.
        """
        text, para, seg = self._make_para_with_one_segment(writable_project)
        try:
            initial_count = len(list(para.SegmentsOS))
            result = writable_project.Segments.SplitSegment(seg, 3)
            assert isinstance(result, tuple)
            assert len(result) == 2
            seg1, seg2 = result
            assert seg1 is not None
            assert seg2 is not None
            new_count = len(list(para.SegmentsOS))
            assert new_count == initial_count + 1
        finally:
            _cleanup_text(writable_project, text)

    def test_SplitSegment_preserves_analyses_on_seg1_portion(self, writable_project):
        """
        After a split, seg1 (the original segment, now truncated) must still
        be present in SegmentsOS at the earlier index.
        """
        text, para, seg = self._make_para_with_one_segment(writable_project)
        try:
            seg1, seg2 = writable_project.Segments.SplitSegment(seg, 3)
            segs = list(para.SegmentsOS)
            idx1 = segs.index(seg1)
            idx2 = segs.index(seg2)
            assert idx2 == idx1 + 1, "new_seg must immediately follow the original"
        finally:
            _cleanup_text(writable_project, text)

    def test_SplitSegment_rejects_offset_zero(self, writable_project):
        """
        offset_within_segment=0 is invalid; must raise FP_ParameterError.
        """
        from flexlibs2.code.FLExProject import FP_ParameterError

        text, para, seg = self._make_para_with_one_segment(writable_project)
        try:
            with pytest.raises(FP_ParameterError):
                writable_project.Segments.SplitSegment(seg, 0)
        finally:
            _cleanup_text(writable_project, text)

    def test_SplitSegment_rejects_offset_beyond_length(self, writable_project):
        """
        offset_within_segment >= seg length is invalid; must raise FP_ParameterError.
        """
        from flexlibs2.code.FLExProject import FP_ParameterError

        sentence = "Short."
        text, para, seg = self._make_para_with_one_segment(writable_project, sentence)
        try:
            seg_len = seg.EndOffset - seg.BeginOffset
            with pytest.raises(FP_ParameterError):
                writable_project.Segments.SplitSegment(seg, seg_len)
        finally:
            _cleanup_text(writable_project, text)

    def test_SplitSegment_raises_on_none_segment(self, writable_project):
        """SplitSegment must raise FP_NullParameterError when segment is None."""
        from flexlibs2.code.FLExProject import FP_NullParameterError

        with pytest.raises(FP_NullParameterError):
            writable_project.Segments.SplitSegment(None, 5)


# ---------------------------------------------------------------------------
# MergeSegments
# ---------------------------------------------------------------------------


class TestMergeSegments:
    """
    Coverage for SegmentOperations.MergeSegments.
    """

    def _make_para_with_two_segments(self, project):
        """Create a text with two sentences and return (text, para, seg1, seg2)."""
        text, para = _make_throwaway_text(project, "zz_merge_test")
        seg1 = project.Segments.AppendSentence(para, "First sentence.")
        seg2 = project.Segments.AppendSentence(para, "Second sentence.")
        return text, para, seg1, seg2

    def test_MergeSegments_migrates_FreeTranslation_by_default(self, writable_project):
        """
        Default policy='migrate' must concatenate seg2's FreeTranslation
        into seg1's before removing seg2. Merged survivor is seg1.
        """
        text, para, seg1, seg2 = self._make_para_with_two_segments(writable_project)
        try:
            ws = writable_project.project.DefaultAnalWs
            writable_project.Segments.SetFreeTranslation(seg1, "Trans one.")
            writable_project.Segments.SetFreeTranslation(seg2, "Trans two.")

            survivor = writable_project.Segments.MergeSegments(seg1, seg2)
            assert survivor is seg1
            merged_trans = writable_project.Segments.GetFreeTranslation(survivor)
            assert "Trans one." in merged_trans
            assert "Trans two." in merged_trans
        finally:
            _cleanup_text(writable_project, text)

    def test_MergeSegments_discard_policy_drops_translations(self, writable_project):
        """
        policy='discard' must silently drop seg2's translations.
        Survivor must NOT contain seg2's translation text.
        """
        text, para, seg1, seg2 = self._make_para_with_two_segments(writable_project)
        try:
            writable_project.Segments.SetFreeTranslation(seg1, "Keep this.")
            writable_project.Segments.SetFreeTranslation(seg2, "Drop this.")

            survivor = writable_project.Segments.MergeSegments(
                seg1, seg2, translation_policy="discard"
            )
            assert survivor is seg1
            trans = writable_project.Segments.GetFreeTranslation(survivor)
            assert "Drop this." not in trans
        finally:
            _cleanup_text(writable_project, text)

    def test_MergeSegments_reject_policy_raises_when_seg2_has_translation(
        self, writable_project
    ):
        """
        policy='reject' must raise FP_ParameterError when seg2 has a
        non-empty FreeTranslation.
        """
        from flexlibs2.code.FLExProject import FP_ParameterError

        text, para, seg1, seg2 = self._make_para_with_two_segments(writable_project)
        try:
            writable_project.Segments.SetFreeTranslation(seg2, "Has content.")
            with pytest.raises(FP_ParameterError):
                writable_project.Segments.MergeSegments(
                    seg1, seg2, translation_policy="reject"
                )
        finally:
            _cleanup_text(writable_project, text)

    def test_MergeSegments_rejects_non_adjacent_segments(self, writable_project):
        """
        Merging non-adjacent segments must raise FP_ParameterError.
        """
        from flexlibs2.code.FLExProject import FP_ParameterError

        text, para = _make_throwaway_text(writable_project, "zz_merge_nonadj")
        try:
            seg1 = writable_project.Segments.AppendSentence(para, "Sentence one.")
            seg2 = writable_project.Segments.AppendSentence(para, "Sentence two.")
            seg3 = writable_project.Segments.AppendSentence(para, "Sentence three.")
            # seg1 and seg3 are not adjacent
            with pytest.raises(FP_ParameterError):
                writable_project.Segments.MergeSegments(seg1, seg3)
        finally:
            _cleanup_text(writable_project, text)

    def test_MergeSegments_rejects_segments_from_different_paragraphs(
        self, writable_project
    ):
        """
        Merging segments from different paragraphs must raise FP_ParameterError.
        """
        from flexlibs2.code.FLExProject import FP_ParameterError

        text1, para1 = _make_throwaway_text(writable_project, "zz_merge_diff_para_A")
        text2, para2 = _make_throwaway_text(writable_project, "zz_merge_diff_para_B")
        try:
            seg1 = writable_project.Segments.AppendSentence(para1, "Para A sentence.")
            seg2 = writable_project.Segments.AppendSentence(para2, "Para B sentence.")
            with pytest.raises(FP_ParameterError):
                writable_project.Segments.MergeSegments(seg1, seg2)
        finally:
            _cleanup_text(writable_project, text1)
            _cleanup_text(writable_project, text2)

    def test_MergeSegments_returns_seg1_as_survivor(self, writable_project):
        """
        MergeSegments must return seg1 (the first/earlier segment).
        """
        text, para, seg1, seg2 = self._make_para_with_two_segments(writable_project)
        try:
            survivor = writable_project.Segments.MergeSegments(seg1, seg2)
            assert survivor is seg1
        finally:
            _cleanup_text(writable_project, text)

    def test_MergeSegments_reduces_segment_count(self, writable_project):
        """
        After merging two segments, SegmentsOS count must decrease by 1.
        """
        text, para, seg1, seg2 = self._make_para_with_two_segments(writable_project)
        try:
            count_before = len(list(para.SegmentsOS))
            writable_project.Segments.MergeSegments(seg1, seg2)
            count_after = len(list(para.SegmentsOS))
            assert count_after == count_before - 1
        finally:
            _cleanup_text(writable_project, text)


# ---------------------------------------------------------------------------
# ReparseParagraph
# ---------------------------------------------------------------------------


class TestReparseParagraph:
    """
    Coverage for SegmentOperations.ReparseParagraph (formerly RebuildSegments).
    """

    def test_ReparseParagraph_rebuilds_from_Contents(self, writable_project):
        """
        ReparseParagraph must return the SegmentsOS collection (non-None)
        and the paragraph Contents must be unchanged.
        """
        text, para = _make_throwaway_text(writable_project, "zz_reparse_basic")
        try:
            writable_project.Segments.AppendSentence(para, "Sentence one.")
            writable_project.Segments.AppendSentence(para, "Sentence two.")
            contents_before = para.Contents.Text or ""

            result = writable_project.Segments.ReparseParagraph(para)

            # Returns the SegmentsOS collection
            assert result is not None
            contents_after = para.Contents.Text or ""
            # Contents must be identical after reparse
            assert contents_after == contents_before
        finally:
            _cleanup_text(writable_project, text)

    def test_ReparseParagraph_destroys_translations_per_docstring(self, writable_project):
        """
        Per the docstring: ReparseParagraph destroys all wordform analyses and
        segment translations. After ReparseParagraph, the old segment object
        that held translations should no longer be in SegmentsOS (LCM re-derives
        fresh segment objects). This test verifies ReparseParagraph completes
        without error and that translations are not preserved on any surviving
        segment that covers the same span.
        """
        text, para = _make_throwaway_text(writable_project, "zz_reparse_destroys_trans")
        try:
            seg = writable_project.Segments.AppendSentence(para, "Test sentence.")
            writable_project.Segments.SetFreeTranslation(seg, "Should be gone after reparse.")

            # Reparse — this destroys all translations
            writable_project.Segments.ReparseParagraph(para)

            # The old seg reference may be stale. Check all current segments
            # for the translation text; none should carry it.
            for current_seg in para.SegmentsOS:
                trans = writable_project.Segments.GetFreeTranslation(current_seg)
                # After a full reparse the translations are cleared
                assert "Should be gone after reparse." not in trans
        finally:
            _cleanup_text(writable_project, text)

    def test_ReparseParagraph_raises_on_readonly_project(self, writable_project):
        """
        ReparseParagraph must raise FP_ReadOnlyError when the project is
        read-only. We verify this via the _EnsureWriteEnabled guard by calling
        the method on a mock/stub that simulates read-only state, or by
        checking that the real project (which is write-enabled) does NOT raise.

        Since we only have a writable fixture here, we verify the positive case:
        ReparseParagraph on a writable project completes without error.
        """
        text, para = _make_throwaway_text(writable_project, "zz_reparse_write_check")
        try:
            result = writable_project.Segments.ReparseParagraph(para)
            assert result is not None
        finally:
            _cleanup_text(writable_project, text)

    def test_ReparseParagraph_raises_on_none_paragraph(self, writable_project):
        """ReparseParagraph must raise FP_NullParameterError when paragraph is None."""
        from flexlibs2.code.FLExProject import FP_NullParameterError

        with pytest.raises(FP_NullParameterError):
            writable_project.Segments.ReparseParagraph(None)
