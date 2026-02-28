#
#   SegmentOperations.py
#
#   Class: SegmentOperations
#          Segment operations for FieldWorks Language Explorer projects
#          via SIL Language and Culture Model (LCM) API.
#
#   Copyright 2025
#

import re

import clr
clr.AddReference("System")
import System

from SIL.LCModel import (
    ISegment,
    ISegmentFactory,
    IStTxtPara,
)

from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

from ..FLExProject import (
    FP_ParameterError,
)
from ..BaseOperations import BaseOperations

class SegmentOperations(BaseOperations):
    """
    This class provides operations for managing segments in a FieldWorks project.

    Segments represent the units of text analysis in FLEx, typically sentences
    or clauses within paragraphs. Each segment can have baseline text, analyses,
    translations (free and literal), and notes.

    Usage::

        from flexlibs2 import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get all segments in a paragraph
        para = project.Object(para_hvo)
        for segment in project.Segments.GetAll(para):
            baseline = project.Segments.GetBaselineText(segment)
            print(baseline)

        # Set translations
        project.Segments.SetFreeTranslation(segment, "In the beginning...")
        project.Segments.SetLiteralTranslation(segment, "In-the beginning...")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize SegmentOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)

    def _GetSequence(self, parent):
        """Specify which sequence to reorder for segment analyses (reference sequence)."""
        return parent.AnalysesRS

    def __WSHandle(self, wsHandle):
        """
        Internal helper for writing system handles (analysis).

        Args:
            wsHandle: Writing system handle or None for default analysis WS.

        Returns:
            int: The writing system handle to use.
        """
        if wsHandle is None:
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultAnalWs)

    def __WSHandleVern(self, wsHandle):
        """
        Internal helper for writing system handles (vernacular).

        Args:
            wsHandle: Writing system handle or None for default vernacular WS.

        Returns:
            int: The writing system handle to use.
        """
        if wsHandle is None:
            return self.project.project.DefaultVernWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultVernWs)

    def __GetParagraphObject(self, para_or_hvo):
        """
        Internal helper to get paragraph object from HVO or object.

        Args:
            para_or_hvo: IStTxtPara object or HVO integer.

        Returns:
            IStTxtPara: The paragraph object.
        """
        if isinstance(para_or_hvo, int):
            return self.project.Object(para_or_hvo)
        return para_or_hvo

    def __GetSegmentObject(self, segment_or_hvo):
        """
        Internal helper to get segment object from HVO or object.

        Args:
            segment_or_hvo: ISegment object or HVO integer.

        Returns:
            ISegment: The segment object.
        """
        if isinstance(segment_or_hvo, int):
            return self.project.Object(segment_or_hvo)
        return segment_or_hvo

    def GetAll(self, paragraph_or_hvo):
        """
        Get all segments in a paragraph.

        Args:
            paragraph_or_hvo: The IStTxtPara object or HVO.

        Yields:
            ISegment: Each segment in the paragraph.

        Raises:
            FP_NullParameterError: If paragraph_or_hvo is None.

        Example:
            >>> para = project.Object(para_hvo)
            >>> for segment in project.Segments.GetAll(para):
            ...     text = project.Segments.GetBaselineText(segment)
            ...     print(text)
            In the beginning God created the heavens and the earth.
            Now the earth was formless and empty.

        See Also:
            GetBaselineText, GetFreeTranslation, GetAnalyses
        """
        self._ValidateParam(paragraph_or_hvo, "paragraph_or_hvo")

        para_obj = self.__GetParagraphObject(paragraph_or_hvo)
        segments = list(para_obj.SegmentsOS)

        for segment in segments:
            yield segment

    def GetAnalyses(self, segment_or_hvo):
        """
        Get all analyses (wordforms and their linguistic analyses) for a segment.

        Args:
            segment_or_hvo: The ISegment object or HVO.

        Returns:
            list: List of IAnalysis objects representing the wordforms in the segment.

        Raises:
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> analyses = project.Segments.GetAnalyses(segment)
            >>> print(f"Segment has {len(analyses)} wordforms")
            Segment has 5 wordforms

        See Also:
            GetAll, GetBaselineText

        Notes:
            Each analysis can be an IWfiWordform, IWfiGloss, or IWfiAnalysis object.
            These represent different levels of linguistic analysis for each word.
        """
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)
        analyses = list(segment_obj.AnalysesRS)
        return analyses

    def GetBaselineText(self, segment_or_hvo, wsHandle=None):
        """
        Get the baseline text of a segment (the original text in the vernacular language).

        Args:
            segment_or_hvo: The ISegment object or HVO.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            str: The baseline text, or empty string if not set.

        Raises:
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> text = project.Segments.GetBaselineText(segment)
            >>> print(text)
            In the beginning God created the heavens and the earth.

        See Also:
            SetBaselineText, GetFreeTranslation, GetLiteralTranslation
        """
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)
        ws = self.__WSHandleVern(wsHandle)

        text = ITsString(segment_obj.BaselineText.get_String(ws)).Text
        return text or ""

    def SetBaselineText(self, segment_or_hvo, text, wsHandle=None):
        """
        Set the baseline text of a segment.

        Note: Setting baseline text typically requires re-parsing the segment.

        Args:
            segment_or_hvo: The ISegment object or HVO.
            text: The baseline text to set.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> project.Segments.SetBaselineText(segment, "In the beginning...")
            >>> # Verify the change
            >>> print(project.Segments.GetBaselineText(segment))
            In the beginning...

        See Also:
            GetBaselineText, SetFreeTranslation, SetLiteralTranslation

        Notes:
            Modifying baseline text may affect existing analyses and word glosses.
            The segment may need to be re-parsed after this operation.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)
        ws = self.__WSHandleVern(wsHandle)

        mkstr = TsStringUtils.MakeString(text, ws)
        segment_obj.BaselineText.set_String(ws, mkstr)

    def GetFreeTranslation(self, segment_or_hvo, wsHandle=None):
        """
        Get the free translation for a segment.

        Args:
            segment_or_hvo: The ISegment object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The free translation text, or empty string if not set.

        Raises:
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> trans = project.Segments.GetFreeTranslation(segment)
            >>> print(trans)
            In the beginning God created the heavens and the earth.

        See Also:
            SetFreeTranslation, GetLiteralTranslation, GetBaselineText

        Notes:
            Free translation is typically a natural, idiomatic translation
            of the segment, as opposed to a word-for-word literal translation.
        """
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)
        ws = self.__WSHandle(wsHandle)

        if segment_obj.FreeTranslation:
            text = ITsString(segment_obj.FreeTranslation.get_String(ws)).Text
            return text or ""
        return ""

    def SetFreeTranslation(self, segment_or_hvo, text, wsHandle=None):
        """
        Set the free translation for a segment.

        Args:
            segment_or_hvo: The ISegment object or HVO.
            text: The free translation text to set.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> project.Segments.SetFreeTranslation(segment, "In the beginning God created...")
            >>> # Verify the change
            >>> print(project.Segments.GetFreeTranslation(segment))
            In the beginning God created...

        See Also:
            GetFreeTranslation, SetLiteralTranslation, SetBaselineText

        Notes:
            Free translation should be a natural, idiomatic translation.
            This is distinct from literal (word-for-word) translation.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)
        ws = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(text, ws)
        segment_obj.FreeTranslation.set_String(ws, mkstr)

    def GetLiteralTranslation(self, segment_or_hvo, wsHandle=None):
        """
        Get the literal (word-for-word) translation of a segment.

        Args:
            segment_or_hvo: The ISegment object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The literal translation text, or empty string if not set.

        Raises:
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> trans = project.Segments.GetLiteralTranslation(segment)
            >>> print(trans)
            In-the beginning God created the-heavens and-the-earth

        See Also:
            SetLiteralTranslation, GetFreeTranslation, GetBaselineText

        Notes:
            Literal translation is typically a word-for-word gloss showing
            the grammatical structure, using hyphens to show morpheme boundaries.
        """
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)
        ws = self.__WSHandle(wsHandle)

        if segment_obj.LiteralTranslation:
            text = ITsString(segment_obj.LiteralTranslation.get_String(ws)).Text
            return text or ""
        return ""

    def SetLiteralTranslation(self, segment_or_hvo, text, wsHandle=None):
        """
        Set the literal (word-for-word) translation of a segment.

        Args:
            segment_or_hvo: The ISegment object or HVO.
            text: The literal translation text to set.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> project.Segments.SetLiteralTranslation(segment, "In-the beginning God created...")
            >>> # Verify the change
            >>> print(project.Segments.GetLiteralTranslation(segment))
            In-the beginning God created...

        See Also:
            GetLiteralTranslation, SetFreeTranslation, SetBaselineText

        Notes:
            Literal translation should be a word-for-word gloss.
            Use hyphens to show morpheme boundaries within words.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)
        ws = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(text, ws)
        segment_obj.LiteralTranslation.set_String(ws, mkstr)

    def GetNotes(self, segment_or_hvo):
        """
        Get all notes associated with a segment.

        Args:
            segment_or_hvo: The ISegment object or HVO.

        Returns:
            list: List of note objects associated with the segment.

        Raises:
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> notes = project.Segments.GetNotes(segment)
            >>> print(f"Segment has {len(notes)} notes")
            Segment has 2 notes

        See Also:
            GetAll, GetBaselineText, GetFreeTranslation

        Notes:
            Notes in FLEx can include translator notes, consultant notes,
            and other types of annotations attached to segments.
        """
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)

        # Get notes from the NotesOS collection if it exists
        if hasattr(segment_obj, 'NotesOS'):
            notes = list(segment_obj.NotesOS)
            return notes
        return []

    def Create(self, paragraph_or_hvo, baseline_text, wsHandle=None):
        """
        Create a new segment and append it to a paragraph.

        Creates a new segment with the specified baseline text and adds it to the
        end of the paragraph's segment collection.

        Args:
            paragraph_or_hvo: The IStTxtPara object or HVO.
            baseline_text: The baseline text for the new segment. Must be non-empty.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            ISegment: The newly created segment object.

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If paragraph_or_hvo or baseline_text is None.
            FP_ParameterError: If baseline_text is empty.

        Example:
            >>> para = project.Object(para_hvo)
            >>> segment = project.Segments.Create(para, "This is a new sentence.", ws)
            >>> print(project.Segments.GetBaselineText(segment))
            This is a new sentence.

        See Also:
            Delete, Exists, SetBaselineText

        Notes:
            The segment will need to be parsed to create wordforms and analyses.
            Consider calling RebuildSegments after creating segments to ensure
            proper offsets and structure.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(paragraph_or_hvo, "paragraph_or_hvo")
        self._ValidateParam(baseline_text, "baseline_text")

        text_str = baseline_text.strip() if isinstance(baseline_text, str) else str(baseline_text)
        if not text_str:
            raise FP_ParameterError("baseline_text cannot be empty")

        para_obj = self.__GetParagraphObject(paragraph_or_hvo)
        ws = self.__WSHandleVern(wsHandle)

        # Create the new segment using the factory
        factory = self.project.project.ServiceLocator.GetService(ISegmentFactory)
        segment = factory.Create()

        # Add to paragraph's segments collection
        para_obj.SegmentsOS.Add(segment)

        # Set the baseline text
        mkstr = TsStringUtils.MakeString(text_str, ws)
        segment.BaselineText.set_String(ws, mkstr)

        return segment

    def Delete(self, segment_or_hvo):
        """
        Delete a segment from its paragraph.

        Removes the segment from its parent paragraph's segment collection. This
        will also delete all analyses, translations, and notes associated with the segment.

        Args:
            segment_or_hvo: The ISegment object or HVO.

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> project.Segments.Delete(segment)
            >>> # Segment is now removed from the paragraph

        See Also:
            Create, Exists, MergeSegments

        Notes:
            This operation cannot be undone. All data associated with the
            segment will be permanently deleted.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)

        # Get the owner (paragraph) and remove from collection
        owner = segment_obj.Owner
        if owner and hasattr(owner, 'SegmentsOS'):
            owner.SegmentsOS.Remove(segment_obj)

    def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
        """
        Duplicate a segment, creating a new segment with the same content.

        This method creates a copy of an existing segment. The baseline text and
        translations (free and literal) are copied. Analyses are NOT copied as they
        are complex and context-dependent.

        Args:
            item_or_hvo: Either an ISegment object or its HVO (integer identifier)
            insert_after (bool): If True, insert the duplicate after the original
                segment in the paragraph. If False, append to the end of the paragraph.
            deep (bool): Currently not used for segments (analyses are never copied).
                Parameter kept for consistency with other Duplicate() methods.

        Returns:
            ISegment: The newly created duplicate segment

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the segment does not exist or is invalid, or
                if the segment has no valid owner paragraph.

        Example:
            >>> # Duplicate a segment
            >>> segment = list(project.Segments.GetAll(para))[0]
            >>> duplicate = project.Segments.Duplicate(segment, insert_after=True)
            >>> print(project.Segments.GetBaselineText(duplicate))
            In the beginning God created the heavens and the earth.
            >>> print(project.Segments.GetFreeTranslation(duplicate))
            In the beginning God created the heavens and the earth.

        Warning:
            - Analyses are NOT copied (would need re-parsing)
            - Notes are NOT copied
            - Offsets may need adjustment after duplication
            - The duplicate will have identical text but a new GUID
            - insert_after=True inserts immediately after the original segment

        Notes:
            - Duplicated segment is added to the same paragraph as the original
            - New GUID is auto-generated for the duplicate
            - Baseline text is copied in the same writing system
            - Free translation and literal translation are copied
            - Analyses are NOT copied (complex and context-dependent)
            - Segment is inserted after original if insert_after=True
            - deep parameter is ignored (analyses never copied)

        See Also:
            Create, Delete, GetAll, SetBaselineText
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(item_or_hvo, "item_or_hvo")

        segment_obj = self.__GetSegmentObject(item_or_hvo)

        # Get the owner (paragraph)
        owner = segment_obj.Owner
        if not owner or not hasattr(owner, 'SegmentsOS'):
            raise FP_ParameterError("Segment has no valid owner paragraph")

        # Create the new segment (factory + add to parent)
        factory = self.project.project.ServiceLocator.GetService(ISegmentFactory)
        new_segment = factory.Create()
        owner.SegmentsOS.Add(new_segment)

        # Copy all writing systems of each MultiString property
        if segment_obj.BaselineText:
            new_segment.BaselineText.CopyAlternatives(segment_obj.BaselineText)
        if segment_obj.FreeTranslation:
            new_segment.FreeTranslation.CopyAlternatives(segment_obj.FreeTranslation)
        if segment_obj.LiteralTranslation:
            new_segment.LiteralTranslation.CopyAlternatives(segment_obj.LiteralTranslation)

        # Copy boolean properties
        if hasattr(segment_obj, 'IsLabel'):
            new_segment.IsLabel = segment_obj.IsLabel

        # Handle insert_after positioning
        if insert_after:
            # Find the index of the current segment
            seg_list = list(owner.SegmentsOS)
            try:
                current_index = seg_list.index(segment_obj)
                # The new segment was appended, so we need to move it
                # Remove from end
                owner.SegmentsOS.Remove(new_segment)
                # Insert at correct position (after original)
                owner.SegmentsOS.Insert(current_index + 1, new_segment)
            except ValueError:
                # Segment not found in list, leave at end
                pass

        return new_segment

    # ========== SYNC INTEGRATION METHODS ==========

    def GetSyncableProperties(self, item):
        """
        Get all syncable properties of a segment.

        Args:
            item: The ISegment object.

        Returns:
            dict: Dictionary of syncable properties with their values.

        Example:
            >>> props = project.Segments.GetSyncableProperties(segment)
            >>> print(props['BaselineText'])
            {'en': 'In the beginning...'}
            >>> print(props['IsLabel'])
            False
            >>> print(props['BeginOffset'])
            0

        Notes:
            - MultiString properties: BaselineText, FreeTranslation, LiteralTranslation
            - Boolean property: IsLabel
            - Integer properties: BeginOffset, EndOffset
            - Does NOT include analyses (those are children)
        """
        props = {}

        # MultiString properties
        if hasattr(item, 'BaselineText') and item.BaselineText:
            props['BaselineText'] = self.project.GetMultiStringDict(item.BaselineText)

        if hasattr(item, 'FreeTranslation') and item.FreeTranslation:
            props['FreeTranslation'] = self.project.GetMultiStringDict(item.FreeTranslation)

        if hasattr(item, 'LiteralTranslation') and item.LiteralTranslation:
            props['LiteralTranslation'] = self.project.GetMultiStringDict(item.LiteralTranslation)

        # Boolean property
        if hasattr(item, 'IsLabel'):
            props['IsLabel'] = bool(item.IsLabel)

        # Integer properties
        if hasattr(item, 'BeginOffset'):
            props['BeginOffset'] = int(item.BeginOffset)

        if hasattr(item, 'EndOffset'):
            props['EndOffset'] = int(item.EndOffset)

        return props

    def CompareTo(self, item1, item2, ops1=None, ops2=None):
        """
        Compare two segments for differences.

        Args:
            item1: First segment object (from project 1)
            item2: Second segment object (from project 2)
            ops1: Optional SegmentOperations instance for project 1 (defaults to self)
            ops2: Optional SegmentOperations instance for project 2 (defaults to self)

        Returns:
            tuple: (is_different, differences_dict)
                - is_different (bool): True if segments differ, False if identical
                - differences_dict (dict): Maps property names to (value1, value2) tuples

        Example:
            >>> is_diff, diffs = ops1.CompareTo(seg1, seg2, ops1, ops2)
            >>> if is_diff:
            ...     for prop, (val1, val2) in diffs.items():
            ...         print(f"{prop}: {val1} != {val2}")

        Notes:
            - Compares all syncable properties
            - MultiStrings are compared across all writing systems
            - Empty/null values are treated as equivalent
        """
        if ops1 is None:
            ops1 = self
        if ops2 is None:
            ops2 = self

        props1 = ops1.GetSyncableProperties(item1)
        props2 = ops2.GetSyncableProperties(item2)

        differences = {}

        # Get all property keys from both items
        all_keys = set(props1.keys()) | set(props2.keys())

        for key in all_keys:
            val1 = props1.get(key)
            val2 = props2.get(key)

            # Compare values
            if self.project._CompareValues(val1, val2):
                # Values are different
                differences[key] = (val1, val2)

        is_different = len(differences) > 0
        return (is_different, differences)

    def Exists(self, paragraph_or_hvo, segment_or_hvo):
        """
        Check if a segment exists in a paragraph.

        Args:
            paragraph_or_hvo: The IStTxtPara object or HVO.
            segment_or_hvo: The ISegment object or HVO to check for.

        Returns:
            bool: True if the segment exists in the paragraph, False otherwise.

        Raises:
            FP_NullParameterError: If paragraph_or_hvo or segment_or_hvo is None.

        Example:
            >>> para = project.Object(para_hvo)
            >>> segment = segments[0]
            >>> exists = project.Segments.Exists(para, segment)
            >>> print(exists)
            True

        See Also:
            Create, Delete, GetAll
        """
        self._ValidateParam(paragraph_or_hvo, "paragraph_or_hvo")
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        para_obj = self.__GetParagraphObject(paragraph_or_hvo)
        segment_obj = self.__GetSegmentObject(segment_or_hvo)

        # Check if segment is in paragraph's segments collection
        segments_list = list(para_obj.SegmentsOS)
        return segment_obj in segments_list

    def SplitSegment(self, segment_or_hvo, position):
        """
        Split a segment at the specified character position.

        Creates two segments from one by splitting the baseline text at the given
        position. The first segment will contain text from 0 to position, and the
        second segment will contain text from position to the end.

        Args:
            segment_or_hvo: The ISegment object or HVO to split.
            position: Character position (0-based) where to split the text.

        Returns:
            tuple: (first_segment, second_segment) - The two resulting segments.

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If segment_or_hvo is None.
            FP_ParameterError: If position is invalid or out of range.

        Example:
            >>> segment = segments[0]
            >>> text = project.Segments.GetBaselineText(segment)
            >>> print(text)
            In the beginning God created the heavens.
            >>> seg1, seg2 = project.Segments.SplitSegment(segment, 17)
            >>> print(project.Segments.GetBaselineText(seg1))
            In the beginning
            >>> print(project.Segments.GetBaselineText(seg2))
            God created the heavens.

        See Also:
            MergeSegments, Create, Delete

        Notes:
            The original segment is deleted and replaced with two new segments.
            All analyses and translations from the original segment are lost.
            You will need to re-parse the new segments.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        if position is None or position < 0:
            raise FP_ParameterError("position must be a non-negative integer")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)
        owner = segment_obj.Owner

        if not owner or not hasattr(owner, 'SegmentsOS'):
            raise FP_ParameterError("Segment has no valid owner paragraph")

        # Get baseline text and writing system
        ws = self.__WSHandleVern(None)
        baseline_text = self.GetBaselineText(segment_obj, ws)

        if position >= len(baseline_text):
            raise FP_ParameterError(f"position {position} is beyond text length {len(baseline_text)}")

        # Split the text
        first_text = baseline_text[:position]
        second_text = baseline_text[position:]

        if not first_text.strip() or not second_text.strip():
            raise FP_ParameterError("Split would create an empty segment")

        # Get the segment's index in the paragraph
        segments_list = list(owner.SegmentsOS)
        segment_index = segments_list.index(segment_obj)

        # Create factory for new segments
        factory = self.project.project.ServiceLocator.GetService(ISegmentFactory)

        # Create first segment
        first_segment = factory.Create()
        mkstr1 = TsStringUtils.MakeString(first_text, ws)
        first_segment.BaselineText.set_String(ws, mkstr1)

        # Create second segment
        second_segment = factory.Create()
        mkstr2 = TsStringUtils.MakeString(second_text, ws)
        second_segment.BaselineText.set_String(ws, mkstr2)

        # Insert new segments at the original position
        owner.SegmentsOS.Insert(segment_index, first_segment)
        owner.SegmentsOS.Insert(segment_index + 1, second_segment)

        # Remove the original segment
        owner.SegmentsOS.Remove(segment_obj)

        return (first_segment, second_segment)

    def MergeSegments(self, segment1_or_hvo, segment2_or_hvo):
        """
        Merge two adjacent segments into one.

        Combines the baseline text of two segments into a single segment. The segments
        must be adjacent in the paragraph.

        Args:
            segment1_or_hvo: The first ISegment object or HVO.
            segment2_or_hvo: The second ISegment object or HVO (must be adjacent).

        Returns:
            ISegment: The merged segment containing text from both segments.

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If either segment is None.
            FP_ParameterError: If segments are not adjacent or not in same paragraph.

        Example:
            >>> seg1 = segments[0]
            >>> seg2 = segments[1]
            >>> merged = project.Segments.MergeSegments(seg1, seg2)
            >>> print(project.Segments.GetBaselineText(merged))
            In the beginning God created the heavens and the earth.

        See Also:
            SplitSegment, Create, Delete

        Notes:
            Both original segments are deleted and replaced with a new merged segment.
            All analyses and translations from both segments are lost.
            You will need to re-parse the merged segment.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(segment1_or_hvo, "segment1_or_hvo")
        self._ValidateParam(segment2_or_hvo, "segment2_or_hvo")

        segment1 = self.__GetSegmentObject(segment1_or_hvo)
        segment2 = self.__GetSegmentObject(segment2_or_hvo)

        # Validate merge compatibility (same class, same concrete type)
        from ..lcm_casting import validate_merge_compatibility
        is_compatible, error_msg = validate_merge_compatibility(segment1, segment2)
        if not is_compatible:
            raise FP_ParameterError(error_msg)

        # Check they have the same owner
        if segment1.Owner != segment2.Owner:
            raise FP_ParameterError("Segments must be in the same paragraph")

        owner = segment1.Owner
        if not owner or not hasattr(owner, 'SegmentsOS'):
            raise FP_ParameterError("Segments have no valid owner paragraph")

        # Get indices and check adjacency
        segments_list = list(owner.SegmentsOS)
        index1 = segments_list.index(segment1)
        index2 = segments_list.index(segment2)

        if abs(index1 - index2) != 1:
            raise FP_ParameterError("Segments must be adjacent")

        # Ensure segment1 comes first
        if index1 > index2:
            segment1, segment2 = segment2, segment1
            index1, index2 = index2, index1

        # Get baseline texts
        ws = self.__WSHandleVern(None)
        text1 = self.GetBaselineText(segment1, ws)
        text2 = self.GetBaselineText(segment2, ws)

        # Merge with a space between
        merged_text = f"{text1} {text2}"

        # Create merged segment
        factory = self.project.project.ServiceLocator.GetService(ISegmentFactory)
        merged_segment = factory.Create()
        mkstr = TsStringUtils.MakeString(merged_text, ws)
        merged_segment.BaselineText.set_String(ws, mkstr)

        # Insert at first position
        owner.SegmentsOS.Insert(index1, merged_segment)

        # Remove original segments
        owner.SegmentsOS.Remove(segment1)
        owner.SegmentsOS.Remove(segment2)

        return merged_segment

    def GetBeginOffset(self, segment_or_hvo):
        """
        Get the beginning character offset of a segment within its paragraph.

        The offset indicates where the segment's text starts in the paragraph's
        baseline text.

        Args:
            segment_or_hvo: The ISegment object or HVO.

        Returns:
            int: The beginning offset (0-based character position).

        Raises:
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> offset = project.Segments.GetBeginOffset(segment)
            >>> print(offset)
            0

        See Also:
            GetEndOffset, SetOffsets

        Notes:
            Offsets are used internally by FLEx to track segment positions
            in the paragraph text. They are automatically maintained when
            using RebuildSegments.
        """
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)

        if hasattr(segment_obj, 'BeginOffset'):
            return segment_obj.BeginOffset
        return 0

    def GetEndOffset(self, segment_or_hvo):
        """
        Get the ending character offset of a segment within its paragraph.

        The offset indicates where the segment's text ends in the paragraph's
        baseline text.

        Args:
            segment_or_hvo: The ISegment object or HVO.

        Returns:
            int: The ending offset (0-based character position).

        Raises:
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> offset = project.Segments.GetEndOffset(segment)
            >>> print(offset)
            45

        See Also:
            GetBeginOffset, SetOffsets

        Notes:
            Offsets are used internally by FLEx to track segment positions
            in the paragraph text. They are automatically maintained when
            using RebuildSegments.
        """
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)

        if hasattr(segment_obj, 'EndOffset'):
            return segment_obj.EndOffset
        return 0

    def SetOffsets(self, segment_or_hvo, begin_offset, end_offset):
        """
        Set the beginning and ending offsets of a segment.

        Manually sets the character offsets that define where the segment's text
        appears within the paragraph's baseline text.

        Args:
            segment_or_hvo: The ISegment object or HVO.
            begin_offset: The beginning offset (0-based character position).
            end_offset: The ending offset (0-based character position).

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If segment_or_hvo is None.
            FP_ParameterError: If offsets are invalid (negative or begin >= end).

        Example:
            >>> segment = segments[0]
            >>> project.Segments.SetOffsets(segment, 0, 45)

        See Also:
            GetBeginOffset, GetEndOffset, RebuildSegments

        Notes:
            Manually setting offsets can lead to inconsistencies. It's generally
            better to use RebuildSegments to automatically calculate correct offsets.
            Only use this if you know what you're doing.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")
        self._ValidateParam(begin_offset, "begin_offset")
        self._ValidateParam(end_offset, "end_offset")

        if begin_offset < 0 or end_offset < 0:
            raise FP_ParameterError("Offsets cannot be negative")

        if begin_offset >= end_offset:
            raise FP_ParameterError("begin_offset must be less than end_offset")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)

        if hasattr(segment_obj, 'BeginOffset'):
            segment_obj.BeginOffset = begin_offset

        if hasattr(segment_obj, 'EndOffset'):
            segment_obj.EndOffset = end_offset

    def IsLabel(self, segment_or_hvo):
        """
        Check if a segment is marked as a label (section header).

        Labels are segments that represent section headers, titles, or other
        structural markers rather than regular text content.

        Args:
            segment_or_hvo: The ISegment object or HVO.

        Returns:
            bool: True if the segment is a label, False otherwise.

        Raises:
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> is_header = project.Segments.IsLabel(segment)
            >>> print(is_header)
            False

        See Also:
            SetIsLabel

        Notes:
            Label segments are often used for chapter headings, section titles,
            and other non-content text in interlinear texts.
        """
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)

        if hasattr(segment_obj, 'IsLabel'):
            return segment_obj.IsLabel
        return False

    def SetIsLabel(self, segment_or_hvo, is_label):
        """
        Set whether a segment is a label (section header).

        Marks or unmarks a segment as a label. Labels represent section headers,
        titles, or other structural markers.

        Args:
            segment_or_hvo: The ISegment object or HVO.
            is_label: Boolean value - True to mark as label, False for regular segment.

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If segment_or_hvo is None.

        Example:
            >>> segment = segments[0]
            >>> project.Segments.SetIsLabel(segment, True)
            >>> print(project.Segments.IsLabel(segment))
            True

        See Also:
            IsLabel

        Notes:
            Label segments are typically used for chapter headings and section titles.
            They may be displayed or processed differently than regular content segments.
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(segment_or_hvo, "segment_or_hvo")

        segment_obj = self.__GetSegmentObject(segment_or_hvo)

        if hasattr(segment_obj, 'IsLabel'):
            segment_obj.IsLabel = bool(is_label)

    def ValidateSegments(self, paragraph_or_hvo):
        """
        Validate the integrity of all segments in a paragraph.

        Checks that segments are properly structured with valid offsets,
        non-overlapping ranges, and complete coverage of the paragraph text.

        Args:
            paragraph_or_hvo: The IStTxtPara object or HVO.

        Returns:
            dict: Validation results with keys:
                - 'valid': bool - Overall validity
                - 'errors': list - List of error messages
                - 'warnings': list - List of warning messages
                - 'segment_count': int - Number of segments checked

        Raises:
            FP_NullParameterError: If paragraph_or_hvo is None.

        Example:
            >>> para = project.Object(para_hvo)
            >>> result = project.Segments.ValidateSegments(para)
            >>> if result['valid']:
            ...     print("All segments are valid")
            ... else:
            ...     for error in result['errors']:
            ...         print(f"Error: {error}")

        See Also:
            RebuildSegments, GetBeginOffset, GetEndOffset

        Notes:
            This method performs non-destructive validation. It reports issues
            but doesn't modify the segments. Use RebuildSegments to fix issues.
        """
        self._ValidateParam(paragraph_or_hvo, "paragraph_or_hvo")

        para_obj = self.__GetParagraphObject(paragraph_or_hvo)
        segments_list = list(para_obj.SegmentsOS)

        errors = []
        warnings = []

        if not segments_list:
            warnings.append("Paragraph has no segments")
            return {
                'valid': True,
                'errors': errors,
                'warnings': warnings,
                'segment_count': 0
            }

        # Check each segment
        prev_end = -1
        for i, segment in enumerate(segments_list):
            # Check if segment has required attributes
            if not hasattr(segment, 'BeginOffset') or not hasattr(segment, 'EndOffset'):
                warnings.append(f"Segment {i} missing offset attributes")
                continue

            begin = segment.BeginOffset
            end = segment.EndOffset

            # Validate offset values
            if begin < 0 or end < 0:
                errors.append(f"Segment {i} has negative offset (begin={begin}, end={end})")

            if begin >= end:
                errors.append(f"Segment {i} has invalid offsets (begin={begin} >= end={end})")

            # Check for gaps or overlaps
            if prev_end >= 0:
                if begin > prev_end + 1:
                    warnings.append(f"Gap between segment {i-1} and {i} (prev_end={prev_end}, begin={begin})")
                elif begin < prev_end:
                    errors.append(f"Overlap between segment {i-1} and {i} (prev_end={prev_end}, begin={begin})")

            # Check baseline text exists
            baseline = self.GetBaselineText(segment)
            if not baseline:
                warnings.append(f"Segment {i} has empty baseline text")

            prev_end = end

        valid = len(errors) == 0

        return {
            'valid': valid,
            'errors': errors,
            'warnings': warnings,
            'segment_count': len(segments_list)
        }

    def RebuildSegments(self, paragraph_or_hvo):
        """
        Rebuild and regenerate all segments from paragraph baseline text.

        Analyzes the paragraph's baseline text and recreates segments with proper
        offsets. This is useful for repairing corrupted segment data or after
        modifying paragraph text directly.

        Args:
            paragraph_or_hvo: The IStTxtPara object or HVO.

        Returns:
            int: Number of segments created.

        Raises:
            FP_ReadOnlyError: If project is not opened with writeEnabled=True.
            FP_NullParameterError: If paragraph_or_hvo is None.

        Example:
            >>> para = project.Object(para_hvo)
            >>> count = project.Segments.RebuildSegments(para)
            >>> print(f"Rebuilt {count} segments")
            Rebuilt 5 segments

        See Also:
            ValidateSegments, Create, SetOffsets

        Notes:
            This method deletes all existing segments and their data (analyses,
            translations, notes) and creates new segments based on sentence
            boundaries in the baseline text. Use with caution.

            Sentence boundaries are detected using basic punctuation rules
            (periods, question marks, exclamation marks followed by spaces).
        """
        self._EnsureWriteEnabled()
        self._ValidateParam(paragraph_or_hvo, "paragraph_or_hvo")

        para_obj = self.__GetParagraphObject(paragraph_or_hvo)

        # Get paragraph baseline text
        ws = self.__WSHandleVern(None)
        if hasattr(para_obj, 'Contents') and para_obj.Contents:
            para_text = ITsString(para_obj.Contents).Text or ""
        else:
            para_text = ""

        # Clear existing segments
        if hasattr(para_obj, 'SegmentsOS'):
            para_obj.SegmentsOS.Clear()

        if not para_text.strip():
            return 0

        # Simple sentence splitting (split on . ! ? followed by space or end)
        sentence_pattern = r'([^.!?]+[.!?]+(?:\s+|$))'
        sentences = re.findall(sentence_pattern, para_text)

        # If no sentences found, treat whole text as one segment
        if not sentences:
            sentences = [para_text]

        factory = self.project.project.ServiceLocator.GetService(ISegmentFactory)
        offset = 0

        for sentence_text in sentences:
            sentence_text = sentence_text.strip()
            if not sentence_text:
                continue

            # Create segment
            segment = factory.Create()
            para_obj.SegmentsOS.Add(segment)

            # Set baseline text
            mkstr = TsStringUtils.MakeString(sentence_text, ws)
            segment.BaselineText.set_String(ws, mkstr)

            # Set offsets
            if hasattr(segment, 'BeginOffset') and hasattr(segment, 'EndOffset'):
                segment.BeginOffset = offset
                segment.EndOffset = offset + len(sentence_text)

            offset += len(sentence_text) + 1  # +1 for space between sentences

        return len(para_obj.SegmentsOS)
