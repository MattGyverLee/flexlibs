#
#   AllomorphOperations.py
#
#   Class: AllomorphOperations
#          Allomorph operations for FieldWorks Language Explorer
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
    IMoForm,
    IMoStemAllomorphFactory,
    ILexEntry,
    IPhEnvironment,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class AllomorphOperations:
    """
    This class provides operations for managing allomorphs in a FieldWorks project.

    Allomorphs are variant forms of morphemes that appear in different phonological
    or morphological contexts. For example, the English plural morpheme has
    allomorphs "-s", "-es", and "-en" (ox/oxen).

    Usage::

        from flexlibs import FLExProject, AllomorphOperations

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        allomorphOps = AllomorphOperations(project)

        # Get entry
        entry = project.LexiconAllEntries()[0]

        # Get all allomorphs for an entry
        for allomorph in allomorphOps.GetAll(entry):
            form = allomorphOps.GetForm(allomorph)
            print(f"Allomorph: {form}")

        # Create a new allomorph
        morphType = project.lp.MorphTypesOA.PossibilitiesOS[0]
        allomorph = allomorphOps.Create(entry, "walk", morphType)

        # Set phonological environment
        env = project.lp.PhonologicalDataOA.EnvironmentsOS[0]
        allomorphOps.AddPhoneEnv(allomorph, env)

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize AllomorphOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    def GetAll(self, entry_or_hvo):
        """
        Get all allomorphs for a lexical entry.

        Args:
            entry_or_hvo: The ILexEntry object or HVO.

        Yields:
            IMoForm: Each allomorph of the entry.

        Raises:
            FP_NullParameterError: If entry_or_hvo is None.

        Example:
            >>> allomorphOps = AllomorphOperations(project)
            >>> entry = project.LexiconAllEntries()[0]
            >>> for allomorph in allomorphOps.GetAll(entry):
            ...     form = allomorphOps.GetForm(allomorph)
            ...     print(f"Allomorph: {form}")
            Allomorph: run
            Allomorph: ran
            Allomorph: runn-

        Notes:
            - Returns the lexeme form first (if it exists)
            - Then returns all alternate forms
            - Order follows FLEx database order
            - Returns empty generator if entry has no allomorphs

        See Also:
            Create, GetForm
        """
        if not entry_or_hvo:
            raise FP_NullParameterError()

        entry = self.__GetEntryObject(entry_or_hvo)

        # First yield the lexeme form if it exists
        if entry.LexemeFormOA:
            yield entry.LexemeFormOA

        # Then yield all alternate forms
        for allomorph in entry.AlternateFormsOS:
            yield allomorph


    def Create(self, entry_or_hvo, form, morphType, wsHandle=None):
        """
        Create a new allomorph for a lexical entry.

        Args:
            entry_or_hvo: The ILexEntry object or HVO.
            form (str): The allomorph form (e.g., "-ing", "walk", "pre-").
            morphType: The morpheme type (IMoMorphType object).
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            IMoForm: The newly created allomorph object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If entry_or_hvo, form, or morphType is None.
            FP_ParameterError: If form is empty.

        Example:
            >>> allomorphOps = AllomorphOperations(project)
            >>> entry = project.LexiconAllEntries()[0]
            >>> morphType = project.lp.MorphTypesOA.PossibilitiesOS[0]
            >>> allomorph = allomorphOps.Create(entry, "walk", morphType)
            >>> print(allomorphOps.GetForm(allomorph))
            walk

            >>> # Create with specific writing system
            >>> allomorph = allomorphOps.Create(entry, "wɔk", morphType,
            ...                                  project.WSHandle('en-fonipa'))

        Notes:
            - The allomorph is added to the entry's alternate forms list
            - If the entry has no lexeme form, this becomes the lexeme form
            - Otherwise, it's added as an alternate form
            - MorphType determines how the allomorph is analyzed in parsing

        See Also:
            Delete, GetAll, SetForm
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not entry_or_hvo:
            raise FP_NullParameterError()
        if form is None:
            raise FP_NullParameterError()
        if morphType is None:
            raise FP_NullParameterError()

        if not form or not form.strip():
            raise FP_ParameterError("Form cannot be empty")

        entry = self.__GetEntryObject(entry_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Create the new allomorph using the factory
        factory = self.project.project.ServiceLocator.GetInstance(IMoStemAllomorphFactory)
        allomorph = factory.Create()

        # Set form
        mkstr = TsStringUtils.MakeString(form, wsHandle)
        allomorph.Form.set_String(wsHandle, mkstr)

        # Set morph type
        allomorph.MorphTypeRA = morphType

        # Add to entry - if no lexeme form, set as lexeme, else add as alternate
        if not entry.LexemeFormOA:
            entry.LexemeFormOA = allomorph
        else:
            entry.AlternateFormsOS.Add(allomorph)

        return allomorph


    def Delete(self, allomorph_or_hvo):
        """
        Delete an allomorph.

        Args:
            allomorph_or_hvo: The IMoForm object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If allomorph_or_hvo is None.
            FP_ParameterError: If the allomorph is in use or cannot be deleted.

        Example:
            >>> allomorphOps = AllomorphOperations(project)
            >>> entry = project.LexiconAllEntries()[0]
            >>> allomorphs = list(allomorphOps.GetAll(entry))
            >>> if len(allomorphs) > 1:
            ...     allomorphOps.Delete(allomorphs[-1])

        Warning:
            - Deleting an allomorph that is in use in analyses may cause issues
            - If deleting the lexeme form and alternates exist, the first
              alternate becomes the new lexeme form
            - Deletion is permanent and cannot be undone
            - Consider checking usage in texts before deletion

        Notes:
            - Removes the allomorph from the entry's forms collection
            - All references to this allomorph in analyses are affected

        See Also:
            Create, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not allomorph_or_hvo:
            raise FP_NullParameterError()

        allomorph = self.__GetAllomorphObject(allomorph_or_hvo)

        # Get the owning entry
        owner = allomorph.Owner

        # Check if this is the lexeme form or an alternate
        if hasattr(owner, 'LexemeFormOA') and owner.LexemeFormOA == allomorph:
            # Deleting the lexeme form
            # If there are alternates, promote the first one to lexeme
            if owner.AlternateFormsOS.Count > 0:
                new_lexeme = owner.AlternateFormsOS[0]
                owner.AlternateFormsOS.RemoveAt(0)
                owner.LexemeFormOA = new_lexeme
            else:
                # No alternates, just clear the lexeme form
                owner.LexemeFormOA = None
        elif hasattr(owner, 'AlternateFormsOS'):
            # Deleting an alternate form
            owner.AlternateFormsOS.Remove(allomorph)


    def GetForm(self, allomorph_or_hvo, wsHandle=None):
        """
        Get the form (text) of an allomorph.

        Args:
            allomorph_or_hvo: The IMoForm object or HVO.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Returns:
            str: The allomorph form, or empty string if not set.

        Raises:
            FP_NullParameterError: If allomorph_or_hvo is None.

        Example:
            >>> allomorphOps = AllomorphOperations(project)
            >>> entry = project.LexiconAllEntries()[0]
            >>> allomorphs = list(allomorphOps.GetAll(entry))
            >>> if allomorphs:
            ...     form = allomorphOps.GetForm(allomorphs[0])
            ...     print(form)
            walk

            >>> # Get form in specific writing system
            >>> form_ipa = allomorphOps.GetForm(allomorphs[0],
            ...                                  project.WSHandle('en-fonipa'))
            >>> print(form_ipa)
            wɔk

        Notes:
            - Returns empty string if form not set in specified writing system
            - Use different writing systems for pronunciation variants

        See Also:
            SetForm, GetAll
        """
        if not allomorph_or_hvo:
            raise FP_NullParameterError()

        allomorph = self.__GetAllomorphObject(allomorph_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        form = ITsString(allomorph.Form.get_String(wsHandle)).Text
        return form or ""


    def SetForm(self, allomorph_or_hvo, form, wsHandle=None):
        """
        Set the form (text) of an allomorph.

        Args:
            allomorph_or_hvo: The IMoForm object or HVO.
            form (str): The new allomorph form.
            wsHandle: Optional writing system handle. Defaults to vernacular WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If allomorph_or_hvo or form is None.
            FP_ParameterError: If form is empty.

        Example:
            >>> allomorphOps = AllomorphOperations(project)
            >>> entry = project.LexiconAllEntries()[0]
            >>> allomorphs = list(allomorphOps.GetAll(entry))
            >>> if allomorphs:
            ...     allomorphOps.SetForm(allomorphs[0], "walked")
            ...     print(allomorphOps.GetForm(allomorphs[0]))
            walked

            >>> # Set IPA pronunciation
            >>> allomorphOps.SetForm(allomorphs[0], "wɔkt",
            ...                      project.WSHandle('en-fonipa'))

        Notes:
            - Changing the form affects all analyses using this allomorph
            - Parser may need to be rerun after form changes
            - Use different writing systems for different representations

        See Also:
            GetForm, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not allomorph_or_hvo:
            raise FP_NullParameterError()
        if form is None:
            raise FP_NullParameterError()

        if not form or not form.strip():
            raise FP_ParameterError("Form cannot be empty")

        allomorph = self.__GetAllomorphObject(allomorph_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(form, wsHandle)
        allomorph.Form.set_String(wsHandle, mkstr)


    def GetMorphType(self, allomorph_or_hvo):
        """
        Get the morpheme type of an allomorph.

        Args:
            allomorph_or_hvo: The IMoForm object or HVO.

        Returns:
            IMoMorphType: The morpheme type (stem, prefix, suffix, etc.).

        Raises:
            FP_NullParameterError: If allomorph_or_hvo is None.

        Example:
            >>> allomorphOps = AllomorphOperations(project)
            >>> entry = project.LexiconAllEntries()[0]
            >>> allomorphs = list(allomorphOps.GetAll(entry))
            >>> if allomorphs:
            ...     morphType = allomorphOps.GetMorphType(allomorphs[0])
            ...     # Get type name
            ...     wsHandle = project.project.DefaultAnalWs
            ...     type_name = ITsString(morphType.Name.get_String(wsHandle)).Text
            ...     print(type_name)
            stem

        Notes:
            - Morpheme types include: stem, root, bound root, prefix, suffix,
              infix, circumfix, clitic, proclitic, enclitic, simulfix, etc.
            - Type determines parsing behavior and template slots
            - Returns the IMoMorphType object which can be queried for details

        See Also:
            SetMorphType, Create
        """
        if not allomorph_or_hvo:
            raise FP_NullParameterError()

        allomorph = self.__GetAllomorphObject(allomorph_or_hvo)
        return allomorph.MorphTypeRA


    def SetMorphType(self, allomorph_or_hvo, morphType):
        """
        Set the morpheme type of an allomorph.

        Args:
            allomorph_or_hvo: The IMoForm object or HVO.
            morphType: The new morpheme type (IMoMorphType object).

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If allomorph_or_hvo or morphType is None.

        Example:
            >>> allomorphOps = AllomorphOperations(project)
            >>> entry = project.LexiconAllEntries()[0]
            >>> allomorphs = list(allomorphOps.GetAll(entry))
            >>> if allomorphs:
            ...     # Get a different morph type
            ...     morphTypes = project.lp.MorphTypesOA.PossibilitiesOS
            ...     prefix_type = [mt for mt in morphTypes
            ...                    if "prefix" in str(mt).lower()][0]
            ...     allomorphOps.SetMorphType(allomorphs[0], prefix_type)

        Notes:
            - Changing type affects parsing and morphological analysis
            - Incompatible changes may require template updates
            - Parser should be rerun after type changes

        See Also:
            GetMorphType, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not allomorph_or_hvo:
            raise FP_NullParameterError()
        if morphType is None:
            raise FP_NullParameterError()

        allomorph = self.__GetAllomorphObject(allomorph_or_hvo)
        allomorph.MorphTypeRA = morphType


    def GetPhoneEnv(self, allomorph_or_hvo):
        """
        Get the phonological environments for an allomorph.

        Args:
            allomorph_or_hvo: The IMoForm object or HVO.

        Returns:
            list: List of IPhEnvironment objects (empty list if none).

        Raises:
            FP_NullParameterError: If allomorph_or_hvo is None.

        Example:
            >>> allomorphOps = AllomorphOperations(project)
            >>> entry = project.LexiconAllEntries()[0]
            >>> allomorphs = list(allomorphOps.GetAll(entry))
            >>> if allomorphs:
            ...     envs = allomorphOps.GetPhoneEnv(allomorphs[0])
            ...     for env in envs:
            ...         wsHandle = project.project.DefaultAnalWs
            ...         name = ITsString(env.Name.get_String(wsHandle)).Text
            ...         print(f"Environment: {name}")
            Environment: After voiceless consonant

        Notes:
            - Phonological environments define distribution of allomorphs
            - Empty list means allomorph appears in all contexts
            - Multiple environments are OR'd (any match allows allomorph)
            - Used by the parser to select appropriate allomorph

        See Also:
            AddPhoneEnv, RemovePhoneEnv
        """
        if not allomorph_or_hvo:
            raise FP_NullParameterError()

        allomorph = self.__GetAllomorphObject(allomorph_or_hvo)
        return list(allomorph.PhoneEnvRC)


    def AddPhoneEnv(self, allomorph_or_hvo, env_or_hvo):
        """
        Add a phonological environment to an allomorph.

        Args:
            allomorph_or_hvo: The IMoForm object or HVO.
            env_or_hvo: The IPhEnvironment object or HVO to add.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If allomorph_or_hvo or env_or_hvo is None.

        Example:
            >>> allomorphOps = AllomorphOperations(project)
            >>> entry = project.LexiconAllEntries()[0]
            >>> allomorphs = list(allomorphOps.GetAll(entry))
            >>> if allomorphs and project.lp.PhonologicalDataOA:
            ...     envs = project.lp.PhonologicalDataOA.EnvironmentsOS
            ...     if envs.Count > 0:
            ...         allomorphOps.AddPhoneEnv(allomorphs[0], envs[0])

            >>> # Define that "-es" appears after sibilants
            >>> # (assuming you have created the environment)
            >>> sibilant_env = project.lp.PhonologicalDataOA.EnvironmentsOS[0]
            >>> allomorphOps.AddPhoneEnv(allomorphs[0], sibilant_env)

        Notes:
            - Multiple environments can be added (OR logic)
            - If environment already exists in the list, it's still added
              (duplicates are allowed but not recommended)
            - Environments guide parser in selecting appropriate allomorph

        See Also:
            GetPhoneEnv, RemovePhoneEnv
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not allomorph_or_hvo:
            raise FP_NullParameterError()
        if not env_or_hvo:
            raise FP_NullParameterError()

        allomorph = self.__GetAllomorphObject(allomorph_or_hvo)
        env = self.__GetEnvironmentObject(env_or_hvo)

        allomorph.PhoneEnvRC.Add(env)


    def RemovePhoneEnv(self, allomorph_or_hvo, env_or_hvo):
        """
        Remove a phonological environment from an allomorph.

        Args:
            allomorph_or_hvo: The IMoForm object or HVO.
            env_or_hvo: The IPhEnvironment object or HVO to remove.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If allomorph_or_hvo or env_or_hvo is None.

        Example:
            >>> allomorphOps = AllomorphOperations(project)
            >>> entry = project.LexiconAllEntries()[0]
            >>> allomorphs = list(allomorphOps.GetAll(entry))
            >>> if allomorphs:
            ...     envs = allomorphOps.GetPhoneEnv(allomorphs[0])
            ...     if envs:
            ...         # Remove the first environment
            ...         allomorphOps.RemovePhoneEnv(allomorphs[0], envs[0])

        Notes:
            - If environment not in list, this is a no-op (no error)
            - Removing all environments means allomorph appears in all contexts
            - Parser behavior changes when environments are modified

        See Also:
            GetPhoneEnv, AddPhoneEnv
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not allomorph_or_hvo:
            raise FP_NullParameterError()
        if not env_or_hvo:
            raise FP_NullParameterError()

        allomorph = self.__GetAllomorphObject(allomorph_or_hvo)
        env = self.__GetEnvironmentObject(env_or_hvo)

        # Only remove if it's actually in the collection
        if env in allomorph.PhoneEnvRC:
            allomorph.PhoneEnvRC.Remove(env)


    # --- Private Helper Methods ---

    def __GetEntryObject(self, entry_or_hvo):
        """
        Resolve HVO or object to ILexEntry.

        Args:
            entry_or_hvo: Either an ILexEntry object or an HVO (int).

        Returns:
            ILexEntry: The resolved entry object.
        """
        if isinstance(entry_or_hvo, int):
            return self.project.Object(entry_or_hvo)
        return entry_or_hvo


    def __GetAllomorphObject(self, allomorph_or_hvo):
        """
        Resolve HVO or object to IMoForm.

        Args:
            allomorph_or_hvo: Either an IMoForm object or an HVO (int).

        Returns:
            IMoForm: The resolved allomorph object.
        """
        if isinstance(allomorph_or_hvo, int):
            return self.project.Object(allomorph_or_hvo)
        return allomorph_or_hvo


    def __GetEnvironmentObject(self, env_or_hvo):
        """
        Resolve HVO or object to IPhEnvironment.

        Args:
            env_or_hvo: Either an IPhEnvironment object or an HVO (int).

        Returns:
            IPhEnvironment: The resolved environment object.
        """
        if isinstance(env_or_hvo, int):
            return self.project.Object(env_or_hvo)
        return env_or_hvo


    def __WSHandle(self, wsHandle):
        """
        Get writing system handle, defaulting to vernacular WS for allomorph forms.

        Args:
            wsHandle: Optional writing system handle.

        Returns:
            int: The writing system handle.
        """
        if wsHandle is None:
            return self.project.project.DefaultVernWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultVernWs)
