#
#   EnvironmentOperations.py
#
#   Class: EnvironmentOperations
#          Phonological environment operations for FieldWorks Language Explorer
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
from SIL.LCModel import IPhEnvironmentFactory, IPhEnvironment
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class EnvironmentOperations:
    """
    This class provides operations for managing phonological environments in a
    FieldWorks project.

    Phonological environments specify the context in which phonological rules
    apply. They describe what precedes and follows a segment, using notation
    like V_V (between vowels), #_ (word-initially), _# (word-finally), etc.

    Usage::

        from flexlibs import FLExProject, EnvironmentOperations

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        envOps = EnvironmentOperations(project)

        # Get all environments
        for env in envOps.GetAll():
            name = envOps.GetName(env)
            notation = envOps.GetStringRepresentation(env)
            print(f"{name}: {notation}")

        # Create a new environment
        word_initial = envOps.Create("Word Initial", "At the beginning of a word")
        envOps.SetStringRepresentation(word_initial, "#_")

        # Create more environments
        between_vowels = envOps.Create("Between Vowels")
        envOps.SetStringRepresentation(between_vowels, "V_V")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize EnvironmentOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    def GetAll(self):
        """
        Get all phonological environments in the project.

        Yields:
            IPhEnvironment: Each environment object in the project's environment list.

        Example:
            >>> envOps = EnvironmentOperations(project)
            >>> for env in envOps.GetAll():
            ...     name = envOps.GetName(env)
            ...     notation = envOps.GetStringRepresentation(env)
            ...     print(f"{name}: {notation}")
            Word Initial: #_
            Word Final: _#
            Between Vowels: V_V
            Before Consonant: _C

        Notes:
            - Returns environments in their defined order
            - Environments are reusable across phonological rules
            - Returns empty if no phonological data defined

        See Also:
            Create, GetName, GetStringRepresentation
        """
        phon_data = self.project.lp.PhonologicalDataOA
        if phon_data:
            for env in phon_data.EnvironmentsOS:
                yield env


    def Create(self, name, description=None):
        """
        Create a new phonological environment.

        Args:
            name (str): The name of the environment (e.g., "Word Initial",
                "Between Vowels").
            description (str, optional): Optional description of when this
                environment applies. Defaults to None.

        Returns:
            IPhEnvironment: The newly created environment object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> envOps = EnvironmentOperations(project)
            >>> word_initial = envOps.Create("Word Initial", "At word start")
            >>> envOps.SetStringRepresentation(word_initial, "#_")
            >>> print(envOps.GetName(word_initial))
            Word Initial

            >>> between_vowels = envOps.Create("Between Vowels")
            >>> envOps.SetStringRepresentation(between_vowels, "V_V")

        Notes:
            - Name should be descriptive of the phonological context
            - Use SetStringRepresentation() to set formal notation (e.g., "V_V")
            - Description is optional but helpful for documentation
            - Environment is created in the default analysis writing system

        See Also:
            Delete, GetName, SetStringRepresentation
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        # Get the writing system handle
        wsHandle = self.project.project.DefaultAnalWs

        # Create the new environment using the factory
        factory = self.project.project.ServiceLocator.GetInstance(IPhEnvironmentFactory)
        new_env = factory.Create()

        # Set name
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_env.Name.set_String(wsHandle, mkstr_name)

        # Set description if provided
        if description:
            mkstr_desc = TsStringUtils.MakeString(description, wsHandle)
            new_env.Description.set_String(wsHandle, mkstr_desc)

        # Add to the environments list
        phon_data = self.project.lp.PhonologicalDataOA
        phon_data.EnvironmentsOS.Add(new_env)

        return new_env


    def Delete(self, env_or_hvo):
        """
        Delete a phonological environment.

        Args:
            env_or_hvo: The IPhEnvironment object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If env_or_hvo is None.
            FP_ParameterError: If the environment is in use and cannot be deleted.

        Example:
            >>> envOps = EnvironmentOperations(project)
            >>> obsolete = envOps.Create("Obsolete Environment")
            >>> # ... realize it's not needed
            >>> envOps.Delete(obsolete)

        Warning:
            - Deleting an environment that is in use may raise an error from FLEx
            - This includes environments used in phonological rules and allomorph
              conditions
            - Deletion is permanent and cannot be undone
            - Consider checking usage before deletion

        See Also:
            Create, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not env_or_hvo:
            raise FP_NullParameterError()

        # Resolve to environment object
        env = self.__ResolveObject(env_or_hvo)

        # Remove from the environments list
        phon_data = self.project.lp.PhonologicalDataOA
        phon_data.EnvironmentsOS.Remove(env)


    def GetName(self, env_or_hvo, wsHandle=None):
        """
        Get the name of a phonological environment.

        Args:
            env_or_hvo: The IPhEnvironment object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The environment name, or empty string if not set.

        Raises:
            FP_NullParameterError: If env_or_hvo is None.

        Example:
            >>> envOps = EnvironmentOperations(project)
            >>> for env in envOps.GetAll():
            ...     name = envOps.GetName(env)
            ...     print(name)
            Word Initial
            Word Final
            Between Vowels

            >>> # Get name in a specific writing system
            >>> env = list(envOps.GetAll())[0]
            >>> name = envOps.GetName(env, project.WSHandle('en'))

        See Also:
            SetName, GetStringRepresentation
        """
        if not env_or_hvo:
            raise FP_NullParameterError()

        env = self.__ResolveObject(env_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(env.Name.get_String(wsHandle)).Text
        return name or ""


    def SetName(self, env_or_hvo, name, wsHandle=None):
        """
        Set the name of a phonological environment.

        Args:
            env_or_hvo: The IPhEnvironment object or HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If env_or_hvo or name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> envOps = EnvironmentOperations(project)
            >>> env = list(envOps.GetAll())[0]
            >>> envOps.SetName(env, "Word Initial Position")

            >>> # Use standard terminology
            >>> envOps.SetName(env, "Intervocalic")  # Better than custom names

        Notes:
            - Use clear, descriptive names
            - Standard terminology aids cross-linguistic comparison

        See Also:
            GetName, SetStringRepresentation
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not env_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        env = self.__ResolveObject(env_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        env.Name.set_String(wsHandle, mkstr)


    def GetStringRepresentation(self, env_or_hvo, wsHandle=None):
        """
        Get the string representation (notation) of a phonological environment.

        Args:
            env_or_hvo: The IPhEnvironment object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The environment's string representation (e.g., "V_V", "#_", "_#"),
                or empty string if not set.

        Raises:
            FP_NullParameterError: If env_or_hvo is None.

        Example:
            >>> envOps = EnvironmentOperations(project)
            >>> for env in envOps.GetAll():
            ...     name = envOps.GetName(env)
            ...     notation = envOps.GetStringRepresentation(env)
            ...     print(f"{name:20} {notation}")
            Word Initial         #_
            Word Final           _#
            Between Vowels       V_V
            After Nasal          N_
            Before Stop          _P

            >>> # Use in rule description
            >>> env = list(envOps.GetAll())[0]
            >>> notation = envOps.GetStringRepresentation(env)
            >>> print(f"Rule applies in: {notation}")
            Rule applies in: V_V

        Notes:
            - String representation uses formal phonological notation
            - Underscore (_) marks the position of the target segment
            - # marks word boundaries
            - $ marks syllable boundaries
            - Capital letters (V, C, N, etc.) reference natural classes

        Common Environment Notation:
            #_      - Word-initial (e.g., #_at)
            _#      - Word-final (e.g., ca_#)
            V_V     - Between vowels (intervocalic)
            C_C     - Between consonants
            N_      - After nasal
            _P      - Before stop
            $._     - Syllable-initial
            _.$     - Syllable-final

        See Also:
            SetStringRepresentation, GetName
        """
        if not env_or_hvo:
            raise FP_NullParameterError()

        env = self.__ResolveObject(env_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        notation = ITsString(env.StringRepresentation.get_String(wsHandle)).Text
        return notation or ""


    def SetStringRepresentation(self, env_or_hvo, notation, wsHandle=None):
        """
        Set the string representation (notation) of a phonological environment.

        Args:
            env_or_hvo: The IPhEnvironment object or HVO.
            notation (str): The environment representation (e.g., "V_V", "#_", "_#").
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If env_or_hvo or notation is None.

        Example:
            >>> envOps = EnvironmentOperations(project)
            >>> # Create and define common environments
            >>> word_initial = envOps.Create("Word Initial")
            >>> envOps.SetStringRepresentation(word_initial, "#_")

            >>> word_final = envOps.Create("Word Final")
            >>> envOps.SetStringRepresentation(word_final, "_#")

            >>> between_vowels = envOps.Create("Between Vowels")
            >>> envOps.SetStringRepresentation(between_vowels, "V_V")

            >>> # Complex environment: after nasal, before stop
            >>> env = envOps.Create("Nasal-Stop Cluster")
            >>> envOps.SetStringRepresentation(env, "N_P")

        Notes:
            - Use standard phonological environment notation
            - Underscore (_) marks the target position
            - Reference natural classes using their abbreviations (V, C, N, P)
            - Can specify complex environments with multiple contexts
            - Empty string is allowed for unrestricted environment

        Notation Guide:
            _       - Target position (required)
            #       - Word boundary
            $       - Syllable boundary
            V       - Vowel (natural class)
            C       - Consonant (natural class)
            N       - Nasal (natural class)
            P       - Stop (natural class)
            |       - Disjunction (or)

        See Also:
            GetStringRepresentation, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not env_or_hvo:
            raise FP_NullParameterError()
        if notation is None:
            raise FP_NullParameterError()

        env = self.__ResolveObject(env_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(notation, wsHandle)
        env.StringRepresentation.set_String(wsHandle, mkstr)


    # --- Private Helper Methods ---

    def __ResolveObject(self, env_or_hvo):
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
        Get writing system handle, defaulting to analysis WS.

        Args:
            wsHandle: Optional writing system handle.

        Returns:
            int: The writing system handle.
        """
        if wsHandle is None:
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultAnalWs)
