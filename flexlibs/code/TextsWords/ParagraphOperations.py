#
#   ParagraphOperations.py
#
#   Class: ParagraphOperations
#          Paragraph CRUD operations for FieldWorks Language Explorer projects
#          via SIL Language and Culture Model (LCM) API.
#
#   Copyright Craig Farrow, 2008 - 2025
#

import logging
logger = logging.getLogger(__name__)

import clr
clr.AddReference("System")
import System

from SIL.LCModel import (
    IText,
    IStTxtPara,
    IStTxtParaFactory,
)

from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class ParagraphOperations:
    """
    Paragraph CRUD operations for managing FLEx paragraph objects.

    This class provides methods for creating, reading, updating, and deleting
    paragraphs within texts in a FieldWorks Language Explorer project.

    Usage:
        project = FLExProject()
        project.OpenProject("MyProject", writeEnabled=True)

        # Access through the Paragraphs property
        para_ops = ParagraphOperations(project)

        # Or if integrated into FLExProject:
        # text = project.Texts.Create("Genesis")
        # para = project.Paragraphs.Create(text, "In the beginning...")
    """

    def __init__(self, project):
        """
        Initialize ParagraphOperations with a FLEx project.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project

    def __WSHandle(self, wsHandle):
        """
        Internal helper for writing system handles.

        Args:
            wsHandle: Writing system handle or None for default vernacular WS.

        Returns:
            int: The writing system handle to use.
        """
        if wsHandle is None:
            return self.project.project.DefaultVernWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultVernWs)

    def __GetTextObject(self, text_or_hvo):
        """
        Resolve text_or_hvo to IText object.

        Args:
            text_or_hvo: Either an IText object or its HVO (integer).

        Returns:
            IText: The text object.

        Raises:
            FP_NullParameterError: If text_or_hvo is None.
            FP_ParameterError: If the object doesn't exist or isn't a valid text.
        """
        if not text_or_hvo:
            raise FP_NullParameterError()

        if isinstance(text_or_hvo, int):
            try:
                obj = self.project.Object(text_or_hvo)
                return IText(obj)
            except (AttributeError, System.InvalidCastException) as e:
                raise FP_ParameterError(f"Invalid text HVO: {text_or_hvo}") from e
        return text_or_hvo

    def __GetParagraphObject(self, para_or_hvo):
        """
        Resolve para_or_hvo to IStTxtPara object.

        Args:
            para_or_hvo: Either an IStTxtPara object or its HVO (integer).

        Returns:
            IStTxtPara: The paragraph object.

        Raises:
            FP_NullParameterError: If para_or_hvo is None.
            FP_ParameterError: If the object doesn't exist or isn't a valid paragraph.
        """
        if not para_or_hvo:
            raise FP_NullParameterError()

        if isinstance(para_or_hvo, int):
            try:
                obj = self.project.Object(para_or_hvo)
                return IStTxtPara(obj)
            except (AttributeError, System.InvalidCastException) as e:
                raise FP_ParameterError(f"Invalid paragraph HVO: {para_or_hvo}") from e
        return para_or_hvo

    # --- Core CRUD Operations ---

    def Create(self, text_or_hvo, content, wsHandle=None):
        """
        Create a new paragraph and append it to a text.

        Creates a new paragraph with the specified content and adds it to the end
        of the text's paragraph collection. The paragraph will be created in the
        specified writing system or the default vernacular writing system.

        Args:
            text_or_hvo: Either an IText object or its HVO (integer identifier).
            content (str): The text content for the new paragraph. Must be non-empty.
            wsHandle (int, optional): Writing system handle. If None, uses the
                default vernacular writing system. Can also be a language tag string.

        Returns:
            IStTxtPara: The newly created paragraph object.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If text_or_hvo or content is None.
            FP_ParameterError: If text has no StText contents, or content is empty.

        Example:
            >>> # Create a paragraph in a text
            >>> text = project.Texts.Create("Genesis")
            >>> para = project.Paragraphs.Create(text, "In the beginning...")
            >>> print(project.Paragraphs.GetText(para))
            In the beginning...

            >>> # Create with specific writing system
            >>> ws_handle = project.WSHandle('en')
            >>> para2 = project.Paragraphs.Create(text, "Chapter 2", ws_handle)

        See Also:
            Delete, InsertAt, GetAll, SetText
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if content is None:
            raise FP_NullParameterError()

        content_str = content.strip() if isinstance(content, str) else str(content)
        if not content_str:
            raise FP_ParameterError("Content cannot be empty")

        text_obj = self.__GetTextObject(text_or_hvo)

        # Validate text has ContentsOA
        if not text_obj.ContentsOA:
            raise FP_ParameterError("Text has no StText contents")

        # Get the writing system handle
        wsHandle = self.__WSHandle(wsHandle)

        # Create the new paragraph using the factory
        factory = self.project.project.ServiceLocator.GetInstance(IStTxtParaFactory)
        para = factory.Create()

        # Add to text's paragraphs collection
        text_obj.ContentsOA.ParagraphsOS.Add(para)

        # Set the content
        mkstr = TsStringUtils.MakeString(content_str, wsHandle)
        para.Contents = mkstr

        return para

    def Delete(self, paragraph_or_hvo):
        """
        Delete a paragraph from its text.

        Removes the paragraph from its parent text's paragraph collection. This
        will also delete all segments and other data associated with the paragraph.

        Args:
            paragraph_or_hvo: Either an IStTxtPara object or its HVO (integer identifier).

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If paragraph_or_hvo is None.
            FP_ParameterError: If the paragraph does not exist or is invalid.

        Example:
            >>> # Delete a paragraph
            >>> para = list(project.Paragraphs.GetAll(text))[0]
            >>> project.Paragraphs.Delete(para)

            >>> # Delete by HVO
            >>> project.Paragraphs.Delete(para_hvo)

        Warning:
            - Deletion is permanent and cannot be undone
            - All segments in the paragraph will also be deleted
            - References to the paragraph from other objects may become invalid

        See Also:
            Create, GetAll, InsertAt
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        para_obj = self.__GetParagraphObject(paragraph_or_hvo)

        # Get the owner (StText) and remove the paragraph
        owner = para_obj.Owner
        if owner and hasattr(owner, 'ParagraphsOS'):
            owner.ParagraphsOS.Remove(para_obj)
        else:
            raise FP_ParameterError("Paragraph has no valid owner or cannot be removed")

    def GetAll(self, text_or_hvo):
        """
        Get all paragraphs in a text.

        Returns a generator that yields all paragraph objects in the text's
        paragraph collection in order.

        Args:
            text_or_hvo: Either an IText object or its HVO (integer identifier).

        Yields:
            IStTxtPara: Each paragraph object in the text.

        Raises:
            FP_NullParameterError: If text_or_hvo is None.
            FP_ParameterError: If the text does not exist or is invalid.

        Example:
            >>> # Iterate over all paragraphs
            >>> text = project.Texts.Find("Genesis")
            >>> for para in project.Paragraphs.GetAll(text):
            ...     text = project.Paragraphs.GetText(para)
            ...     print(f"Paragraph: {text[:50]}...")

            >>> # Get as list
            >>> all_paras = list(project.Paragraphs.GetAll(text))
            >>> print(f"Total paragraphs: {len(all_paras)}")

        Notes:
            - If the text has no contents, yields nothing
            - Paragraphs are yielded in the order they appear in the text
            - Use list() to convert to a list if you need random access

        See Also:
            Create, Delete, GetSegmentCount
        """
        text_obj = self.__GetTextObject(text_or_hvo)

        # If text has no contents, return empty
        if not text_obj.ContentsOA:
            return

        # Yield each paragraph
        for para in text_obj.ContentsOA.ParagraphsOS:
            yield para

    def GetText(self, paragraph_or_hvo, wsHandle=None):
        """
        Get the text content of a paragraph.

        Retrieves the text content in the specified writing system, or the default
        vernacular writing system if not specified.

        Args:
            paragraph_or_hvo: Either an IStTxtPara object or its HVO (integer identifier).
            wsHandle (int, optional): Writing system handle. If None, uses the
                default vernacular writing system. Can also be a language tag string.

        Returns:
            str: The text content of the paragraph. Returns empty string if no
                content is set for that writing system.

        Raises:
            FP_NullParameterError: If paragraph_or_hvo is None.
            FP_ParameterError: If the paragraph does not exist or is invalid.

        Example:
            >>> para = list(project.Paragraphs.GetAll(text))[0]
            >>>
            >>> # Get text in default vernacular WS
            >>> text = project.Paragraphs.GetText(para)
            >>> print(text)
            In the beginning...
            >>>
            >>> # Get text in specific WS
            >>> ws_handle = project.WSHandle('en')
            >>> text_en = project.Paragraphs.GetText(para, ws_handle)

        See Also:
            SetText, Create, GetSegments
        """
        para_obj = self.__GetParagraphObject(paragraph_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Get the text content
        text = ITsString(para_obj.Contents).Text
        return text or ""

    def SetText(self, paragraph_or_hvo, content, wsHandle=None):
        """
        Set the text content of a paragraph.

        Updates the paragraph's text content in the specified writing system, or
        the default vernacular writing system if not specified.

        Args:
            paragraph_or_hvo: Either an IStTxtPara object or its HVO (integer identifier).
            content (str): The new text content for the paragraph. Must be non-empty.
            wsHandle (int, optional): Writing system handle. If None, uses the
                default vernacular writing system. Can also be a language tag string.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If paragraph_or_hvo or content is None.
            FP_ParameterError: If the paragraph does not exist, is invalid, or
                content is empty.

        Example:
            >>> para = list(project.Paragraphs.GetAll(text))[0]
            >>>
            >>> # Set text in default vernacular WS
            >>> project.Paragraphs.SetText(para, "Updated paragraph text.")
            >>>
            >>> # Set text in specific WS
            >>> ws_handle = project.WSHandle('en')
            >>> project.Paragraphs.SetText(para, "English text", ws_handle)

        Warning:
            - This will replace all existing content in the paragraph
            - Existing segments may be invalidated and need re-analysis
            - Use with caution on analyzed texts

        See Also:
            GetText, Create, InsertAt
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if content is None:
            raise FP_NullParameterError()

        content_str = content.strip() if isinstance(content, str) else str(content)
        if not content_str:
            raise FP_ParameterError("Content cannot be empty")

        para_obj = self.__GetParagraphObject(paragraph_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Set the content
        mkstr = TsStringUtils.MakeString(content_str, wsHandle)
        para_obj.Contents = mkstr

    def GetSegments(self, paragraph_or_hvo):
        """
        Get all segments in a paragraph.

        Segments are the individual units (typically sentences) within a paragraph
        that can have their own analyses and translations.

        Args:
            paragraph_or_hvo: Either an IStTxtPara object or its HVO (integer identifier).

        Returns:
            list: A list of ISegment objects in the paragraph.

        Raises:
            FP_NullParameterError: If paragraph_or_hvo is None.
            FP_ParameterError: If the paragraph does not exist or is invalid.

        Example:
            >>> para = list(project.Paragraphs.GetAll(text))[0]
            >>> segments = project.Paragraphs.GetSegments(para)
            >>> print(f"Paragraph has {len(segments)} segments")
            Paragraph has 3 segments
            >>>
            >>> # Iterate over segments
            >>> for seg in segments:
            ...     print(seg.BaselineText.Text)

        Notes:
            - Returns empty list if the paragraph has no segments
            - Segments are created during text analysis
            - Use GetSegmentCount() for a quick count without creating a list

        See Also:
            GetSegmentCount, GetText, Create
        """
        para_obj = self.__GetParagraphObject(paragraph_or_hvo)

        # Return list of segments
        return list(para_obj.SegmentsOS)

    def GetSegmentCount(self, paragraph_or_hvo):
        """
        Get the number of segments in a paragraph.

        This is more efficient than calling len(GetSegments()) when you only
        need the count.

        Args:
            paragraph_or_hvo: Either an IStTxtPara object or its HVO (integer identifier).

        Returns:
            int: The number of segments in the paragraph.

        Raises:
            FP_NullParameterError: If paragraph_or_hvo is None.
            FP_ParameterError: If the paragraph does not exist or is invalid.

        Example:
            >>> para = list(project.Paragraphs.GetAll(text))[0]
            >>> count = project.Paragraphs.GetSegmentCount(para)
            >>> print(f"Paragraph has {count} segments")
            Paragraph has 3 segments

        Notes:
            - Returns 0 if the paragraph has no segments
            - More efficient than getting all segments when you only need the count
            - Segments are created during text analysis

        See Also:
            GetSegments, GetText
        """
        para_obj = self.__GetParagraphObject(paragraph_or_hvo)

        # Return segment count
        return para_obj.SegmentsOS.Count

    def InsertAt(self, text_or_hvo, index, content, wsHandle=None):
        """
        Insert a new paragraph at a specific position in a text.

        Creates a new paragraph with the specified content and inserts it at the
        given index in the text's paragraph collection. Existing paragraphs at
        that index and after will be shifted down.

        Args:
            text_or_hvo: Either an IText object or its HVO (integer identifier).
            index (int): The position at which to insert the paragraph (0-based).
                Must be between 0 and the current paragraph count (inclusive).
            content (str): The text content for the new paragraph. Must be non-empty.
            wsHandle (int, optional): Writing system handle. If None, uses the
                default vernacular writing system. Can also be a language tag string.

        Returns:
            IStTxtPara: The newly created paragraph object.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If text_or_hvo or content is None.
            FP_ParameterError: If text has no StText contents, content is empty,
                or index is out of range.

        Example:
            >>> text = project.Texts.Find("Genesis")
            >>>
            >>> # Insert at beginning
            >>> para = project.Paragraphs.InsertAt(text, 0, "Title: Genesis")
            >>>
            >>> # Insert at end (equivalent to Create)
            >>> count = len(list(project.Paragraphs.GetAll(text)))
            >>> para2 = project.Paragraphs.InsertAt(text, count, "The end")
            >>>
            >>> # Insert in middle
            >>> para3 = project.Paragraphs.InsertAt(text, 5, "Chapter 3")

        Notes:
            - Index must be in range [0, current_paragraph_count]
            - Index equal to paragraph count appends to the end
            - Existing paragraphs are shifted, not replaced
            - Use Create() to always append to the end

        See Also:
            Create, Delete, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if content is None:
            raise FP_NullParameterError()

        content_str = content.strip() if isinstance(content, str) else str(content)
        if not content_str:
            raise FP_ParameterError("Content cannot be empty")

        text_obj = self.__GetTextObject(text_or_hvo)

        # Validate text has ContentsOA
        if not text_obj.ContentsOA:
            raise FP_ParameterError("Text has no StText contents")

        # Validate index range
        para_count = text_obj.ContentsOA.ParagraphsOS.Count
        if index < 0 or index > para_count:
            raise FP_ParameterError(f"Index {index} out of range (0-{para_count})")

        # Get the writing system handle
        wsHandle = self.__WSHandle(wsHandle)

        # Create the new paragraph using the factory
        factory = self.project.project.ServiceLocator.GetInstance(IStTxtParaFactory)
        para = factory.Create()

        # Insert at the specified index
        text_obj.ContentsOA.ParagraphsOS.Insert(index, para)

        # Set the content
        mkstr = TsStringUtils.MakeString(content_str, wsHandle)
        para.Contents = mkstr

        return para
