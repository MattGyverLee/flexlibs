#
#   ExampleOperations.py
#
#   Class: ExampleOperations
#          Example sentence operations for FieldWorks Language Explorer
#          projects via SIL Language and Culture Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

import logging
logger = logging.getLogger(__name__)

# Import FLEx LCM types
from SIL.LCModel import (
    ILexExampleSentence,
    ILexExampleSentenceFactory,
    ILexSense,
    ICmTranslation,
    ICmTranslationFactory,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class ExampleOperations:
    """
    This class provides operations for managing example sentences in a FieldWorks project.

    Example sentences illustrate the usage of lexical senses in context. Each example
    can have vernacular text, translations in multiple analysis languages, references
    to source texts, and associated media files.

    Usage::

        from flexlibs import FLExProject, ExampleOperations

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        exampleOps = ExampleOperations(project)

        # Get first entry and sense
        entry = project.LexiconAllEntries().__next__()
        sense = entry.SensesOS[0] if entry.SensesOS.Count > 0 else None

        # Get all examples for a sense
        for example in exampleOps.GetAll(sense):
            text = exampleOps.GetExample(example)
            trans = exampleOps.GetTranslation(example)
            print(f"Example: {text}")
            print(f"Translation: {trans}")

        # Create a new example
        example = exampleOps.Create(sense, "The cat sat on the mat.")
        exampleOps.SetTranslation(example, "Le chat s'est assis sur le tapis.")
        exampleOps.SetReference(example, "Example Corpus 1.23")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize ExampleOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    def GetAll(self, sense_or_hvo):
        """
        Get all example sentences for a lexical sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.

        Yields:
            ILexExampleSentence: Each example sentence for the sense.

        Raises:
            FP_NullParameterError: If sense_or_hvo is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> for example in exampleOps.GetAll(sense):
            ...     text = exampleOps.GetExample(example)
            ...     print(f"Example: {text}")
            Example: The dog ran quickly.
            Example: Dogs run faster than cats.

        Notes:
            - Returns examples in the order they appear in FLEx
            - Returns empty generator if sense has no examples
            - Examples are ordered collections (can be reordered)

        See Also:
            Create, Delete, Reorder
        """
        if not sense_or_hvo:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)

        for example in sense.ExamplesOS:
            yield example


    def Create(self, sense_or_hvo, example_text, wsHandle=None):
        """
        Create a new example sentence for a lexical sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            example_text (str): The example sentence text.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            ILexExampleSentence: The newly created example object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo or example_text is None.
            FP_ParameterError: If example_text is empty.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> example = exampleOps.Create(sense, "The cat slept.")
            >>> print(exampleOps.GetExample(example))
            The cat slept.

            >>> # Create with specific writing system
            >>> example = exampleOps.Create(sense, "Le chat dort.",
            ...                              project.WSHandle('fr'))

        Notes:
            - The example is added to the end of the sense's examples list
            - You can add translations after creation using SetTranslation()
            - References and media can also be added separately
            - Use vernacular writing system for the example text

        See Also:
            Delete, SetExample, SetTranslation
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not sense_or_hvo:
            raise FP_NullParameterError()
        if example_text is None:
            raise FP_NullParameterError()

        if not example_text or not example_text.strip():
            raise FP_ParameterError("Example text cannot be empty")

        sense = self.__GetSenseObject(sense_or_hvo)
        wsHandle = self.__WSHandleVern(wsHandle)

        # Create the new example using the factory
        factory = self.project.project.ServiceLocator.GetInstance(ILexExampleSentenceFactory)
        example = factory.Create()

        # Set example text
        mkstr = TsStringUtils.MakeString(example_text, wsHandle)
        example.Example.set_String(wsHandle, mkstr)

        # Add to sense's examples collection
        sense.ExamplesOS.Add(example)

        return example


    def Delete(self, example_or_hvo):
        """
        Delete an example sentence.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If example_or_hvo is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> examples = list(exampleOps.GetAll(sense))
            >>> if len(examples) > 0:
            ...     exampleOps.Delete(examples[-1])

        Warning:
            - Deletion is permanent and cannot be undone
            - All translations and associated data are also deleted
            - Media file links are removed (but files themselves remain)

        Notes:
            - Removes the example from the owning sense's collection
            - Automatically removes all translations

        See Also:
            Create, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not example_or_hvo:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)

        # Get the owning sense and remove the example
        owner = example.Owner
        if hasattr(owner, 'ExamplesOS'):
            owner.ExamplesOS.Remove(example)


    def Reorder(self, sense_or_hvo, example_list):
        """
        Reorder the examples for a sense.

        Args:
            sense_or_hvo: The ILexSense object or HVO.
            example_list: List of ILexExampleSentence objects or HVOs in desired order.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If sense_or_hvo or example_list is None.
            FP_ParameterError: If example_list doesn't contain all examples or
                contains examples not belonging to this sense.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> examples = list(exampleOps.GetAll(sense))
            >>> # Reverse the order
            >>> exampleOps.Reorder(sense, reversed(examples))

        Notes:
            - All examples must be provided in the new order
            - Examples not in the list will be removed
            - All examples must belong to the specified sense
            - This is useful for organizing examples by frequency or importance

        See Also:
            GetAll, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not sense_or_hvo:
            raise FP_NullParameterError()
        if example_list is None:
            raise FP_NullParameterError()

        sense = self.__GetSenseObject(sense_or_hvo)

        # Convert to list if it's an iterator
        example_list = list(example_list)

        # Resolve all to objects
        examples = [self.__GetExampleObject(ex) for ex in example_list]

        # Verify all examples belong to this sense
        current_examples = set(sense.ExamplesOS)
        new_examples = set(examples)

        if current_examples != new_examples:
            raise FP_ParameterError(
                "Example list must contain exactly the same examples as the sense"
            )

        # Clear and re-add in new order
        sense.ExamplesOS.Clear()
        for example in examples:
            sense.ExamplesOS.Add(example)


    def GetExample(self, example_or_hvo, wsHandle=None):
        """
        Get the example text of an example sentence.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            str: The example text, or empty string if not set.

        Raises:
            FP_NullParameterError: If example_or_hvo is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> examples = list(exampleOps.GetAll(sense))
            >>> if examples:
            ...     text = exampleOps.GetExample(examples[0])
            ...     print(text)
            The dog ran quickly.

            >>> # Get in specific writing system
            >>> text_fr = exampleOps.GetExample(examples[0],
            ...                                   project.WSHandle('fr'))

        Notes:
            - Returns empty string if text not set in specified writing system
            - Use vernacular writing system for example sentences
            - Different writing systems can contain different text

        See Also:
            SetExample, Create
        """
        if not example_or_hvo:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)
        wsHandle = self.__WSHandleVern(wsHandle)

        text = ITsString(example.Example.get_String(wsHandle)).Text
        return text or ""


    def SetExample(self, example_or_hvo, text, wsHandle=None):
        """
        Set the example text of an example sentence.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.
            text (str): The new example text.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If example_or_hvo or text is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> examples = list(exampleOps.GetAll(sense))
            >>> if examples:
            ...     exampleOps.SetExample(examples[0], "The cat ran quickly.")
            ...     print(exampleOps.GetExample(examples[0]))
            The cat ran quickly.

        Notes:
            - Empty string is allowed (clears the text)
            - Use different writing systems for different representations
            - Does not affect translations (update those separately)

        See Also:
            GetExample, Create, SetTranslation
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not example_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)
        wsHandle = self.__WSHandleVern(wsHandle)

        mkstr = TsStringUtils.MakeString(text, wsHandle)
        example.Example.set_String(wsHandle, mkstr)


    def GetTranslations(self, example_or_hvo):
        """
        Get all translation objects for an example sentence.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.

        Returns:
            list: List of ICmTranslation objects (empty list if none).

        Raises:
            FP_NullParameterError: If example_or_hvo is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> examples = list(exampleOps.GetAll(sense))
            >>> if examples:
            ...     translations = exampleOps.GetTranslations(examples[0])
            ...     for trans in translations:
            ...         wsHandle = project.project.DefaultAnalWs
            ...         text = ITsString(trans.Translation.get_String(wsHandle)).Text
            ...         print(f"Translation: {text}")
            Translation: The dog ran quickly.
            Translation: El perro corrió rápidamente.

        Notes:
            - Returns ICmTranslation objects, not strings
            - To get text, use GetTranslation() for a specific WS
            - Translations are in analysis writing systems
            - Multiple translations can exist for different languages

        See Also:
            GetTranslation, SetTranslation, AddTranslation
        """
        if not example_or_hvo:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)
        return list(example.TranslationsOC)


    def GetTranslation(self, example_or_hvo, wsHandle=None):
        """
        Get the translation text for a specific writing system.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The translation text, or empty string if not set.

        Raises:
            FP_NullParameterError: If example_or_hvo is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> examples = list(exampleOps.GetAll(sense))
            >>> if examples:
            ...     trans = exampleOps.GetTranslation(examples[0])
            ...     print(trans)
            The dog ran quickly.

            >>> # Get Spanish translation
            >>> trans_es = exampleOps.GetTranslation(examples[0],
            ...                                       project.WSHandle('es'))
            >>> print(trans_es)
            El perro corrió rápidamente.

        Notes:
            - Returns empty string if no translation in specified WS
            - Use analysis writing system for translations
            - Searches through all translation objects for matching WS
            - Returns the first match found

        See Also:
            SetTranslation, GetTranslations, GetExample
        """
        if not example_or_hvo:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Search through translations for this writing system
        for translation in example.TranslationsOC:
            text = ITsString(translation.Translation.get_String(wsHandle)).Text
            if text:
                return text

        return ""


    def SetTranslation(self, example_or_hvo, text, wsHandle=None):
        """
        Set the translation text for a specific writing system.

        Creates a translation object if one doesn't exist for the writing system.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.
            text (str): The translation text.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If example_or_hvo or text is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> example = exampleOps.Create(sense, "El gato durmió.")
            >>> exampleOps.SetTranslation(example, "The cat slept.")
            >>> print(exampleOps.GetTranslation(example))
            The cat slept.

            >>> # Set French translation
            >>> exampleOps.SetTranslation(example, "Le chat a dormi.",
            ...                            project.WSHandle('fr'))

        Notes:
            - Creates new translation object if needed
            - Updates existing translation if already present
            - Use analysis writing system for translations
            - Empty string is allowed (clears the translation)

        See Also:
            GetTranslation, AddTranslation, RemoveTranslation
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not example_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Find existing translation for this WS or create new one
        translation = None
        for trans in example.TranslationsOC:
            existing_text = ITsString(trans.Translation.get_String(wsHandle)).Text
            if existing_text:  # This translation has content in our WS
                translation = trans
                break

        if translation is None:
            # Create new translation
            factory = self.project.project.ServiceLocator.GetInstance(ICmTranslationFactory)
            translation = factory.Create()
            example.TranslationsOC.Add(translation)

        # Set the translation text
        mkstr = TsStringUtils.MakeString(text, wsHandle)
        translation.Translation.set_String(wsHandle, mkstr)


    def AddTranslation(self, example_or_hvo, text, wsHandle=None):
        """
        Add a new translation to an example sentence.

        This is an alias for SetTranslation() - both create or update translations.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.
            text (str): The translation text.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If example_or_hvo or text is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> example = exampleOps.Create(sense, "Le chien a couru.")
            >>> exampleOps.AddTranslation(example, "The dog ran.")
            >>> exampleOps.AddTranslation(example, "El perro corrió.",
            ...                            project.WSHandle('es'))

        Notes:
            - Identical to SetTranslation() in functionality
            - Creates new translation if needed, updates if exists
            - Use for semantic clarity when adding first translation

        See Also:
            SetTranslation, GetTranslation, RemoveTranslation
        """
        self.SetTranslation(example_or_hvo, text, wsHandle)


    def RemoveTranslation(self, example_or_hvo, wsHandle=None):
        """
        Remove the translation for a specific writing system.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If example_or_hvo is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> examples = list(exampleOps.GetAll(sense))
            >>> if examples:
            ...     # Remove English translation
            ...     exampleOps.RemoveTranslation(examples[0])
            ...     # Remove Spanish translation
            ...     exampleOps.RemoveTranslation(examples[0],
            ...                                   project.WSHandle('es'))

        Notes:
            - Sets translation text to empty string for the WS
            - Does not remove the translation object itself
            - If translation has content in other WSs, those are preserved
            - No error if translation doesn't exist

        See Also:
            SetTranslation, AddTranslation, GetTranslation
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not example_or_hvo:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Find and clear translation for this WS
        for translation in example.TranslationsOC:
            text = ITsString(translation.Translation.get_String(wsHandle)).Text
            if text:
                translation.Translation.set_String(wsHandle, None)
                break


    def GetReference(self, example_or_hvo):
        """
        Get the reference (source citation) for an example sentence.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.

        Returns:
            str: The reference text, or empty string if not set.

        Raises:
            FP_NullParameterError: If example_or_hvo is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> examples = list(exampleOps.GetAll(sense))
            >>> if examples:
            ...     ref = exampleOps.GetReference(examples[0])
            ...     print(f"Reference: {ref}")
            Reference: Genesis 1:1

        Notes:
            - Reference can be a corpus citation, biblical reference, etc.
            - Format is free-form text
            - Commonly used formats: "Book Chapter:Verse", "Corpus ID"
            - Returns empty string if no reference set

        See Also:
            SetReference
        """
        if not example_or_hvo:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)

        if hasattr(example, 'Reference') and example.Reference:
            ref = ITsString(example.Reference).Text
            return ref or ""
        return ""


    def SetReference(self, example_or_hvo, reference_text):
        """
        Set the reference (source citation) for an example sentence.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.
            reference_text (str): The reference text (e.g., "Genesis 1:1").

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If example_or_hvo or reference_text is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> example = exampleOps.Create(sense, "In the beginning...")
            >>> exampleOps.SetReference(example, "Genesis 1:1")
            >>> print(exampleOps.GetReference(example))
            Genesis 1:1

            >>> # Corpus reference
            >>> exampleOps.SetReference(example, "Corpus A, Text 3, Line 12")

        Notes:
            - Reference format is free-form
            - Common formats: biblical citations, corpus IDs, page numbers
            - Empty string is allowed (clears the reference)
            - Use consistent format within a project

        See Also:
            GetReference
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not example_or_hvo:
            raise FP_NullParameterError()
        if reference_text is None:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)
        wsHandle = self.project.project.DefaultAnalWs

        mkstr = TsStringUtils.MakeString(reference_text, wsHandle)
        example.Reference = mkstr


    def GetMediaFiles(self, example_or_hvo):
        """
        Get all media files associated with an example sentence.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.

        Returns:
            list: List of media file objects (empty list if none).

        Raises:
            FP_NullParameterError: If example_or_hvo is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> examples = list(exampleOps.GetAll(sense))
            >>> if examples:
            ...     media = exampleOps.GetMediaFiles(examples[0])
            ...     print(f"Media count: {len(media)}")
            Media count: 2

        Notes:
            - Returns media file objects from MediaFilesOS collection
            - Media files can be audio, video, or image files
            - File objects contain path and metadata information
            - Empty list if no media files attached

        See Also:
            GetMediaCount
        """
        if not example_or_hvo:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)

        if hasattr(example, 'MediaFilesOS'):
            return list(example.MediaFilesOS)
        return []


    def GetMediaCount(self, example_or_hvo):
        """
        Get the count of media files associated with an example sentence.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.

        Returns:
            int: The number of media files.

        Raises:
            FP_NullParameterError: If example_or_hvo is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> examples = list(exampleOps.GetAll(sense))
            >>> if examples:
            ...     count = exampleOps.GetMediaCount(examples[0])
            ...     print(f"This example has {count} media files")
            This example has 2 media files

        Notes:
            - More efficient than len(GetMediaFiles()) for just counting
            - Returns 0 if no media files attached
            - Includes all media types (audio, video, images)

        See Also:
            GetMediaFiles
        """
        if not example_or_hvo:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)

        if hasattr(example, 'MediaFilesOS'):
            return example.MediaFilesOS.Count
        return 0


    def GetOwningSense(self, example_or_hvo):
        """
        Get the lexical sense that owns this example sentence.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.

        Returns:
            ILexSense: The owning sense object.

        Raises:
            FP_NullParameterError: If example_or_hvo is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> examples = list(exampleOps.GetAll(sense))
            >>> if examples:
            ...     owner = exampleOps.GetOwningSense(examples[0])
            ...     gloss = project.LexiconGetSenseGloss(owner)
            ...     print(f"Example belongs to sense: {gloss}")
            Example belongs to sense: run (verb)

        Notes:
            - Returns the ILexSense that contains this example
            - Useful for navigation and context
            - Examples always have exactly one owning sense

        See Also:
            GetAll, Create
        """
        if not example_or_hvo:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)
        return ILexSense(example.Owner)


    def GetGuid(self, example_or_hvo):
        """
        Get the GUID of an example sentence.

        Args:
            example_or_hvo: The ILexExampleSentence object or HVO.

        Returns:
            System.Guid: The GUID of the example.

        Raises:
            FP_NullParameterError: If example_or_hvo is None.

        Example:
            >>> exampleOps = ExampleOperations(project)
            >>> entry = project.LexiconAllEntries().__next__()
            >>> sense = entry.SensesOS[0]
            >>> examples = list(exampleOps.GetAll(sense))
            >>> if examples:
            ...     guid = exampleOps.GetGuid(examples[0])
            ...     print(f"Example GUID: {guid}")
            Example GUID: 12345678-1234-1234-1234-123456789abc

        Notes:
            - GUIDs are globally unique identifiers
            - Persistent across project versions
            - Use for external references and tracking
            - Same GUID across different copies of the project

        See Also:
            GetOwningSense
        """
        if not example_or_hvo:
            raise FP_NullParameterError()

        example = self.__GetExampleObject(example_or_hvo)
        return example.Guid


    # --- Private Helper Methods ---

    def __GetSenseObject(self, sense_or_hvo):
        """
        Resolve HVO or object to ILexSense.

        Args:
            sense_or_hvo: Either an ILexSense object or an HVO (int).

        Returns:
            ILexSense: The resolved sense object.
        """
        if isinstance(sense_or_hvo, int):
            return self.project.Object(sense_or_hvo)
        return sense_or_hvo


    def __GetExampleObject(self, example_or_hvo):
        """
        Resolve HVO or object to ILexExampleSentence.

        Args:
            example_or_hvo: Either an ILexExampleSentence object or an HVO (int).

        Returns:
            ILexExampleSentence: The resolved example object.
        """
        if isinstance(example_or_hvo, int):
            return self.project.Object(example_or_hvo)
        return example_or_hvo


    def __WSHandle(self, wsHandle):
        """
        Get writing system handle, defaulting to analysis WS for translations.

        Args:
            wsHandle: Optional writing system handle.

        Returns:
            int: The writing system handle.
        """
        if wsHandle is None:
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultAnalWs)


    def __WSHandleVern(self, wsHandle):
        """
        Get writing system handle, defaulting to vernacular WS for example text.

        Args:
            wsHandle: Optional writing system handle.

        Returns:
            int: The writing system handle.
        """
        if wsHandle is None:
            return self.project.project.DefaultVernWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultVernWs)
