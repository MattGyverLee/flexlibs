"""
Core Text Operations - Cluster 1.1

This module provides core CRUD operations for FLEx Text objects.
Implements 8 fundamental methods for creating, reading, updating, and deleting texts.

Author: FlexTools Development Team
Date: 2025-11-22
"""

from typing import Optional, Generator

from ..core import (
    IText,
    resolve_text,
    validate_non_empty_string,
    validate_object_exists,
    ObjectNotFoundError,
    DuplicateObjectError,
    NotImplementedYetError,
)


class TextCoreOperations:
    """
    Core operations for managing FLEx Text objects.

    This class provides the fundamental CRUD operations needed to work with
    texts in a FieldWorks Language Explorer project.
    """

    def __init__(self, project):
        """
        Initialize TextCoreOperations with a FLEx project.

        Args:
            project: The FLExProject instance to operate on
        """
        self.project = project
        # TODO: Initialize FLEx API connection
        # self.db = project.GetDatabase()

    def text_create(self, name: str, genre: Optional[str] = None) -> IText:
        """
        Create a new text in the FLEx project.

        Args:
            name (str): The name of the text to create
            genre (str, optional): The genre classification for the text. Defaults to None.

        Returns:
            IText: The newly created text object

        Raises:
            ValueError: If a text with the given name already exists
            RuntimeError: If the text cannot be created

        Example:
            >>> ops = TextCoreOperations(project)
            >>> new_text = ops.text_create("Story 1", genre="Narrative")
        """
        # TODO: Integrate with FLEx API
        validate_non_empty_string(name, "name")

        # Check if text already exists
        if self.text_exists(name):
            raise DuplicateObjectError("Text", name)

        # TODO: Create text using FLEx API
        # text = self.project.LangProject.TextsOC.Add()
        # text.Name.SetAlternative(name, self.project.DefaultAnalysisWs)
        # if genre:
        #     self.text_set_genre(text, genre)
        # return text

        raise NotImplementedYetError("FLEx API integration pending")

    def text_delete(self, text_or_hvo) -> None:
        """
        Delete a text from the FLEx project.

        Args:
            text_or_hvo: Either an IText object or its HVO (integer identifier)

        Raises:
            ValueError: If the text does not exist
            RuntimeError: If the text cannot be deleted

        Example:
            >>> ops = TextCoreOperations(project)
            >>> ops.text_delete(my_text)
        """
        # TODO: Integrate with FLEx API
        # text_obj = resolve_text(text_or_hvo, self.project)
        # validate_object_exists(text_obj, text_or_hvo, "Text")
        # self.project.LangProject.TextsOC.Remove(text_obj)

        raise NotImplementedYetError("FLEx API integration pending")

    def text_exists(self, name: str) -> bool:
        """
        Check if a text with the given name exists in the project.

        Args:
            name (str): The name of the text to check

        Returns:
            bool: True if a text with the given name exists, False otherwise

        Example:
            >>> ops = TextCoreOperations(project)
            >>> if ops.text_exists("Story 1"):
            ...     print("Text exists")
        """
        # TODO: Integrate with FLEx API
        # for text in self.project.LangProject.TextsOC:
        #     text_name = text.Name.BestAnalysisAlternative.Text
        #     if text_name == name:
        #         return True
        # return False

        raise NotImplementedYetError("FLEx API integration pending")

    def text_get_all(self) -> Generator[IText, None, None]:
        """
        Get all texts in the FLEx project.

        Yields:
            IText: Each text object in the project

        Example:
            >>> ops = TextCoreOperations(project)
            >>> for text in ops.text_get_all():
            ...     print(text.Name)
        """
        # TODO: Integrate with FLEx API
        # for text in self.project.LangProject.TextsOC:
        #     yield text

        raise NotImplementedYetError("FLEx API integration pending")
        # Make this a generator even in stub implementation
        yield  # This line will never execute but makes it a generator

    def text_get_name(self, text_or_hvo, ws_handle: Optional[int] = None) -> str:
        """
        Get the name of a text.

        Args:
            text_or_hvo: Either an IText object or its HVO (integer identifier)
            ws_handle (int, optional): Writing system handle. If None, uses default analysis WS.

        Returns:
            str: The name of the text

        Raises:
            ValueError: If the text does not exist

        Example:
            >>> ops = TextCoreOperations(project)
            >>> name = ops.text_get_name(my_text)
        """
        # TODO: Integrate with FLEx API
        # text_obj = resolve_text(text_or_hvo, self.project)
        # validate_object_exists(text_obj, text_or_hvo, "Text")
        #
        # if ws_handle is None:
        #     ws_handle = self.project.DefaultAnalysisWs
        #
        # return text_obj.Name.get_String(ws_handle).Text

        raise NotImplementedYetError("FLEx API integration pending")

    def text_set_name(self, text_or_hvo, name: str, ws_handle: Optional[int] = None) -> None:
        """
        Set the name of a text.

        Args:
            text_or_hvo: Either an IText object or its HVO (integer identifier)
            name (str): The new name for the text
            ws_handle (int, optional): Writing system handle. If None, uses default analysis WS.

        Raises:
            ValueError: If the text does not exist

        Example:
            >>> ops = TextCoreOperations(project)
            >>> ops.text_set_name(my_text, "Updated Story")
        """
        # TODO: Integrate with FLEx API
        validate_non_empty_string(name, "name")
        # text_obj = resolve_text(text_or_hvo, self.project)
        # validate_object_exists(text_obj, text_or_hvo, "Text")
        #
        # if ws_handle is None:
        #     ws_handle = self.project.DefaultAnalysisWs
        #
        # text_obj.Name.set_String(ws_handle, name)

        raise NotImplementedYetError("FLEx API integration pending")

    def text_get_genre(self, text_or_hvo) -> str:
        """
        Get the genre of a text.

        Args:
            text_or_hvo: Either an IText object or its HVO (integer identifier)

        Returns:
            str: The genre name, or empty string if no genre is set

        Raises:
            ValueError: If the text does not exist

        Example:
            >>> ops = TextCoreOperations(project)
            >>> genre = ops.text_get_genre(my_text)
        """
        # TODO: Integrate with FLEx API
        # text_obj = resolve_text(text_or_hvo, self.project)
        # validate_object_exists(text_obj, text_or_hvo, "Text")
        #
        # if text_obj.GenresRC.Count > 0:
        #     return text_obj.GenresRC[0].Name.BestAnalysisAlternative.Text
        # return ""

        raise NotImplementedYetError("FLEx API integration pending")

    def text_set_genre(self, text_or_hvo, genre: str) -> None:
        """
        Set the genre of a text.

        Args:
            text_or_hvo: Either an IText object or its HVO (integer identifier)
            genre (str): The genre name to set

        Raises:
            ObjectNotFoundError: If the text or genre does not exist

        Example:
            >>> ops = TextCoreOperations(project)
            >>> ops.text_set_genre(my_text, "Narrative")
        """
        # TODO: Integrate with FLEx API
        validate_non_empty_string(genre, "genre")
        # text_obj = resolve_text(text_or_hvo, self.project)
        # validate_object_exists(text_obj, text_or_hvo, "Text")
        #
        # # Find genre in the project's genre list
        # genre_obj = self._find_genre(genre)
        # if genre_obj is None:
        #     raise ObjectNotFoundError("Genre", genre)
        #
        # text_obj.GenresRC.Clear()
        # text_obj.GenresRC.Add(genre_obj)

        raise NotImplementedYetError("FLEx API integration pending")
