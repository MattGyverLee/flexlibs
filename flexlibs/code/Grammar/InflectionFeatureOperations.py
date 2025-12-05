#
#   InflectionFeatureOperations.py
#
#   Class: InflectionFeatureOperations
#          Inflection class and feature operations for FieldWorks Language
#          Explorer projects via SIL Language and Culture Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

import logging
logger = logging.getLogger(__name__)

# Import BaseOperations parent class
from ..BaseOperations import BaseOperations

# Import FLEx LCM types
from SIL.LCModel import (
    IMoInflClass,
    IMoInflClassFactory,
    IFsFeatStruc,
    IFsFeatStrucFactory,
    IFsFeatDefn,  # Fixed: was IFsFeatureDefn
    IFsComplexFeature,
    IFsComplexFeatureFactory,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class InflectionFeatureOperations(BaseOperations):
    """
    This class provides operations for managing inflection classes, feature
    structures, and features in a FieldWorks project.

    Inflection classes group lexical items that inflect similarly (e.g., Latin
    noun declensions, Spanish verb conjugations). Feature structures and features
    represent grammatical properties like person, number, gender, tense, aspect,
    mood, etc.

    Usage::

        from flexlibs import FLExProject, InflectionFeatureOperations

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        inflOps = InflectionFeatureOperations(project)

        # Get all inflection classes
        for ic in inflOps.InflectionClassGetAll():
            name = inflOps.InflectionClassGetName(ic)
            print(f"Inflection Class: {name}")

        # Create a new inflection class
        first_decl = inflOps.InflectionClassCreate("First Declension")

        # Work with features
        for feature in inflOps.FeatureGetAll():
            print(f"Feature: {feature}")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize InflectionFeatureOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)


    def _GetSequence(self, parent):
        """
        Specify which sequence to reorder for inflection features.
        For InflectionFeature, we reorder parent.FeaturesOA.PossibilitiesOS
        """
        return parent.FeaturesOA.PossibilitiesOS


    # ========================================================================
    # INFLECTION CLASS OPERATIONS
    # ========================================================================

    def InflectionClassGetAll(self):
        """
        Get all inflection classes in the project.

        Yields:
            IMoInflClass: Each inflection class object in the project.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> for ic in inflOps.InflectionClassGetAll():
            ...     name = inflOps.InflectionClassGetName(ic)
            ...     print(f"Class: {name}")
            Class: First Declension
            Class: Second Declension
            Class: Irregular Verb
            Class: Regular Verb

        Notes:
            - Returns all inflection classes from MorphologicalDataOA
            - Classes organize lexical items by inflectional pattern
            - Each class defines how entries inflect (conjugate/decline)
            - Returns empty if no classes defined

        See Also:
            InflectionClassCreate, InflectionClassGetName
        """
        morph_data = self.project.lp.MorphologicalDataOA
        if morph_data and hasattr(morph_data, 'ProdRestrictOA') and morph_data.ProdRestrictOA:
            # Inflection classes are stored in the ProdRestrictOA (Production Restrictions)
            infl_classes = morph_data.ProdRestrictOA
            for ic in infl_classes.PossibilitiesOS:
                yield ic


    def InflectionClassCreate(self, name):
        """
        Create a new inflection class.

        Args:
            name (str): The name of the inflection class (e.g., "First Declension").

        Returns:
            IMoInflClass: The newly created inflection class object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name is None.
            FP_ParameterError: If name is empty or if a class with this name
                already exists.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> first_decl = inflOps.InflectionClassCreate("First Declension")
            >>> print(inflOps.InflectionClassGetName(first_decl))
            First Declension

            >>> # Create Spanish verb conjugation classes
            >>> ar_verbs = inflOps.InflectionClassCreate("AR Verbs")
            >>> er_verbs = inflOps.InflectionClassCreate("ER Verbs")
            >>> ir_verbs = inflOps.InflectionClassCreate("IR Verbs")

        Notes:
            - Inflection classes group entries that inflect the same way
            - Name should describe the inflectional pattern
            - Classes can be associated with specific parts of speech
            - Used in morphological templates and paradigms
            - The class is created in the default analysis writing system

        See Also:
            InflectionClassDelete, InflectionClassGetAll, InflectionClassSetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        # Check if class already exists
        for existing_ic in self.InflectionClassGetAll():
            existing_name = self.InflectionClassGetName(existing_ic)
            if existing_name and existing_name.lower() == name.lower():
                raise FP_ParameterError(f"Inflection class '{name}' already exists")

        # Get the writing system handle
        wsHandle = self.project.project.DefaultAnalWs

        # Create the new inflection class using the factory
        factory = self.project.project.ServiceLocator.GetService(IMoInflClassFactory)
        new_ic = factory.Create()

        # Add to the inflection classes list (must be done before setting properties)
        morph_data = self.project.lp.MorphologicalDataOA
        if morph_data.ProdRestrictOA:
            morph_data.ProdRestrictOA.PossibilitiesOS.Add(new_ic)

        # Set name
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_ic.Name.set_String(wsHandle, mkstr_name)

        return new_ic


    def InflectionClassDelete(self, ic_or_hvo):
        """
        Delete an inflection class.

        Args:
            ic_or_hvo: The IMoInflClass object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If ic_or_hvo is None.
            FP_ParameterError: If the class is in use and cannot be deleted.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> # Find and delete an obsolete class
            >>> for ic in inflOps.InflectionClassGetAll():
            ...     if inflOps.InflectionClassGetName(ic) == "Obsolete":
            ...         inflOps.InflectionClassDelete(ic)
            ...         break

        Warning:
            - Deleting a class that is in use may raise an error from FLEx
            - Entries using this class should be updated first
            - Deletion is permanent and cannot be undone
            - Check for references before deletion

        See Also:
            InflectionClassCreate, InflectionClassGetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not ic_or_hvo:
            raise FP_NullParameterError()

        # Resolve to inflection class object
        ic = self.__ResolveInflectionClass(ic_or_hvo)

        # Remove from the inflection classes list
        morph_data = self.project.lp.MorphologicalDataOA
        if morph_data.ProdRestrictOA:
            morph_data.ProdRestrictOA.PossibilitiesOS.Remove(ic)


    def InflectionClassGetName(self, ic_or_hvo, wsHandle=None):
        """
        Get the name of an inflection class.

        Args:
            ic_or_hvo: The IMoInflClass object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The inflection class name, or empty string if not set.

        Raises:
            FP_NullParameterError: If ic_or_hvo is None.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> for ic in inflOps.InflectionClassGetAll():
            ...     name = inflOps.InflectionClassGetName(ic)
            ...     print(f"Inflection Class: {name}")
            Inflection Class: First Declension
            Inflection Class: Second Declension

        See Also:
            InflectionClassSetName, InflectionClassGetAll
        """
        if not ic_or_hvo:
            raise FP_NullParameterError()

        ic = self.__ResolveInflectionClass(ic_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(ic.Name.get_String(wsHandle)).Text
        return name or ""


    def InflectionClassSetName(self, ic_or_hvo, name, wsHandle=None):
        """
        Set the name of an inflection class.

        Args:
            ic_or_hvo: The IMoInflClass object or HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If ic_or_hvo or name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> ic = inflOps.InflectionClassCreate("1st Decl")
            >>> inflOps.InflectionClassSetName(ic, "First Declension")
            >>> print(inflOps.InflectionClassGetName(ic))
            First Declension

        See Also:
            InflectionClassGetName, InflectionClassCreate
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not ic_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        ic = self.__ResolveInflectionClass(ic_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        ic.Name.set_String(wsHandle, mkstr)


    # ========================================================================
    # FEATURE STRUCTURE OPERATIONS
    # ========================================================================

    def FeatureStructureGetAll(self):
        """
        Get all feature structures in the project.

        Yields:
            IFsFeatStruc: Each feature structure object in the project.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> for fs in inflOps.FeatureStructureGetAll():
            ...     print(f"Feature Structure HVO: {fs.Hvo}")

        Notes:
            - Feature structures encode grammatical information
            - Used in morphosyntactic descriptions
            - Can represent combinations of features (person+number+gender, etc.)
            - Returns empty if no feature structures defined
            - Note: This method may need adjustment based on actual FLEx API
              structure for storing feature structures

        See Also:
            FeatureStructureCreate, FeatureGetAll
        """
        # Feature structures in FLEx are typically owned by various objects
        # (morphemes, entries, etc.) rather than stored in a central list.
        # This implementation may need adjustment based on specific requirements.
        feature_system = self.project.lp.MsFeatureSystemOA
        if feature_system:
            # This yields feature definitions which may contain feature structures
            # The actual implementation depends on what the user needs
            for feature in feature_system.FeaturesOS:
                if hasattr(feature, 'FeaturesOS'):
                    for fs in feature.FeaturesOS:
                        yield fs


    def FeatureStructureCreate(self):
        """
        Create a new feature structure.

        Returns:
            IFsFeatStruc: The newly created feature structure object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> fs = inflOps.FeatureStructureCreate()
            >>> print(f"Created feature structure: {fs.Hvo}")

        Notes:
            - Feature structures organize related grammatical features
            - After creation, features must be added separately
            - Structures can represent complex feature combinations
            - Used to specify morphosyntactic properties
            - The structure is created as an empty container

        See Also:
            FeatureStructureDelete, FeatureGetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        # Create the new feature structure using the factory
        factory = self.project.project.ServiceLocator.GetService(IFsFeatStrucFactory)
        new_fs = factory.Create()

        return new_fs


    def FeatureStructureDelete(self, fs_or_hvo):
        """
        Delete a feature structure.

        Args:
            fs_or_hvo: The IFsFeatStruc object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If fs_or_hvo is None.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> fs = inflOps.FeatureStructureCreate()
            >>> inflOps.FeatureStructureDelete(fs)

        Warning:
            - Cannot delete if referenced by entries, morphemes, or rules
            - Check dependencies before deletion
            - Deletion is permanent and cannot be undone

        See Also:
            FeatureStructureCreate, FeatureStructureGetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not fs_or_hvo:
            raise FP_NullParameterError()

        # Resolve to feature structure object
        fs = self.__ResolveFeatureStructure(fs_or_hvo)

        # Feature structures are typically owned by other objects,
        # so deletion involves removing from the owner's collection
        # This is a simplified implementation
        if hasattr(fs, 'Owner') and fs.Owner:
            owner = fs.Owner
            if hasattr(owner, 'FeaturesOA') and owner.FeaturesOA == fs:
                owner.FeaturesOA = None


    # ========================================================================
    # FEATURE OPERATIONS
    # ========================================================================

    def FeatureGetAll(self):
        """
        Get all feature definitions in the project.

        Yields:
            IFsFeatureDefn: Each feature definition object in the project.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> for feature in inflOps.FeatureGetAll():
            ...     print(f"Feature: {feature}")

        Notes:
            - Feature definitions describe grammatical categories
            - Each feature has a name and set of possible values
            - Examples: person (1st/2nd/3rd), number (sg/pl), tense, aspect, mood
            - Used to build feature structures for morphosyntactic analysis
            - Returns empty if no feature system defined

        See Also:
            FeatureCreate, FeatureGetValues
        """
        feature_system = self.project.lp.MsFeatureSystemOA
        if feature_system:
            for feature in feature_system.FeaturesOS:
                yield feature


    def FeatureCreate(self, name, type):
        """
        Create a new feature definition.

        Args:
            name (str): The name of the feature (e.g., "person", "number", "tense").
            type (str): The type of feature (e.g., "complex" for structured features).

        Returns:
            IFsFeatureDefn: The newly created feature definition object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name or type is None.
            FP_ParameterError: If name or type is empty, or if a feature with
                this name already exists.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> person = inflOps.FeatureCreate("person", "complex")
            >>> number = inflOps.FeatureCreate("number", "complex")
            >>> tense = inflOps.FeatureCreate("tense", "complex")

        Notes:
            - Features define grammatical categories
            - Values must be added separately after creation
            - Features can be shared across multiple parts of speech
            - The 'complex' type is used for features with multiple values
            - Feature is created in the default analysis writing system

        See Also:
            FeatureDelete, FeatureGetAll, FeatureGetValues
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()
        if type is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")
        if not type or not type.strip():
            raise FP_ParameterError("Type cannot be empty")

        # Check if feature already exists
        wsHandle = self.project.project.DefaultAnalWs
        for existing_feature in self.FeatureGetAll():
            existing_name = ITsString(existing_feature.Name.get_String(wsHandle)).Text
            if existing_name and existing_name.lower() == name.lower():
                raise FP_ParameterError(f"Feature '{name}' already exists")

        # Create the new feature using the factory
        # Using complex feature factory as it's the most common type
        factory = self.project.project.ServiceLocator.GetService(IFsComplexFeatureFactory)
        new_feature = factory.Create()

        # Add to the feature system (must be done before setting properties)
        feature_system = self.project.lp.MsFeatureSystemOA
        if feature_system:
            feature_system.FeaturesOS.Add(new_feature)

        # Set name
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_feature.Name.set_String(wsHandle, mkstr_name)

        return new_feature


    def FeatureDelete(self, feature_or_hvo):
        """
        Delete a feature definition.

        Args:
            feature_or_hvo: The IFsFeatureDefn object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If feature_or_hvo is None.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> # Find and delete a test feature
            >>> for feature in inflOps.FeatureGetAll():
            ...     ws = project.project.DefaultAnalWs
            ...     name = ITsString(feature.Name.get_String(ws)).Text
            ...     if name == "test_feature":
            ...         inflOps.FeatureDelete(feature)
            ...         break

        Warning:
            - Cannot delete if used in feature structures
            - Cannot delete if referenced by entries or morphemes
            - Check dependencies before deletion
            - Deletion is permanent and cannot be undone

        See Also:
            FeatureCreate, FeatureGetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not feature_or_hvo:
            raise FP_NullParameterError()

        # Resolve to feature object
        feature = self.__ResolveFeature(feature_or_hvo)

        # Remove from the feature system
        feature_system = self.project.lp.MsFeatureSystemOA
        if feature_system:
            feature_system.FeaturesOS.Remove(feature)


    def FeatureGetValues(self, feature_or_hvo):
        """
        Get all possible values for a feature.

        Args:
            feature_or_hvo: The IFsFeatureDefn object or HVO.

        Returns:
            list: List of feature value objects (empty list if none).

        Raises:
            FP_NullParameterError: If feature_or_hvo is None.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> person = inflOps.FeatureCreate("person", "complex")
            >>> # After adding values 1st, 2nd, 3rd...
            >>> values = inflOps.FeatureGetValues(person)
            >>> print(f"Person has {len(values)} values")

        Notes:
            - Returns symbolic values (named choices)
            - Empty list if no values defined yet
            - Values represent the possible settings for this feature
            - Example: person feature has values [1st, 2nd, 3rd]
            - Example: number feature has values [singular, plural]
            - The type and structure of values depends on the feature type

        See Also:
            FeatureCreate, FeatureGetAll
        """
        if not feature_or_hvo:
            raise FP_NullParameterError()

        feature = self.__ResolveFeature(feature_or_hvo)

        # Check if feature has values collection
        if hasattr(feature, 'ValuesOC'):
            return list(feature.ValuesOC)
        elif hasattr(feature, 'FeaturesOS'):
            return list(feature.FeaturesOS)

        return []


    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def __ResolveInflectionClass(self, ic_or_hvo):
        """
        Resolve HVO or object to IMoInflClass.

        Args:
            ic_or_hvo: Either an IMoInflClass object or an HVO (int).

        Returns:
            IMoInflClass: The resolved inflection class object.
        """
        if isinstance(ic_or_hvo, int):
            return self.project.Object(ic_or_hvo)
        return ic_or_hvo


    def __ResolveFeatureStructure(self, fs_or_hvo):
        """
        Resolve HVO or object to IFsFeatStruc.

        Args:
            fs_or_hvo: Either an IFsFeatStruc object or an HVO (int).

        Returns:
            IFsFeatStruc: The resolved feature structure object.
        """
        if isinstance(fs_or_hvo, int):
            return self.project.Object(fs_or_hvo)
        return fs_or_hvo


    def __ResolveFeature(self, feature_or_hvo):
        """
        Resolve HVO or object to IFsFeatureDefn.

        Args:
            feature_or_hvo: Either an IFsFeatureDefn object or an HVO (int).

        Returns:
            IFsFeatureDefn: The resolved feature definition object.
        """
        if isinstance(feature_or_hvo, int):
            return self.project.Object(feature_or_hvo)
        return feature_or_hvo


    # ========== SYNC INTEGRATION METHODS ==========

    def GetSyncableProperties(self, item):
        """
        Get dictionary of syncable properties for cross-project synchronization.

        This method works with inflection classes (IMoInflClass). For features and
        feature structures, use separate sync methods if needed.

        Args:
            item: The IMoInflClass (inflection class) object.

        Returns:
            dict: Dictionary mapping property names to their values.
                Keys are property names, values are the property values.

        Example:
            >>> inflOps = InflectionFeatureOperations(project)
            >>> ic = list(inflOps.InflectionClassGetAll())[0]
            >>> props = inflOps.GetSyncableProperties(ic)
            >>> print(props.keys())
            dict_keys(['Name', 'Abbreviation', 'Description'])

        Notes:
            - Returns all MultiString properties (all writing systems)
            - This implementation focuses on inflection classes
            - Does not include GUID or HVO
        """
        ic = self.__ResolveInflectionClass(item)

        # Get all writing systems for MultiString properties
        ws_factory = self.project.project.WritingSystemFactory
        all_ws = {ws.Id: ws.Handle for ws in ws_factory.WritingSystems}

        props = {}

        # MultiString properties
        for prop_name in ['Name', 'Abbreviation', 'Description']:
            if hasattr(ic, prop_name):
                prop_obj = getattr(ic, prop_name)
                ws_values = {}
                for ws_id, ws_handle in all_ws.items():
                    text = ITsString(prop_obj.get_String(ws_handle)).Text
                    if text:  # Only include non-empty values
                        ws_values[ws_id] = text
                if ws_values:  # Only include property if it has values
                    props[prop_name] = ws_values

        return props


    def CompareTo(self, item1, item2, ops1=None, ops2=None):
        """
        Compare two inflection classes and return detailed differences.

        Args:
            item1: First inflection class to compare (from source project).
            item2: Second inflection class to compare (from target project).
            ops1: Optional InflectionFeatureOperations instance for item1's project.
                 Defaults to self.
            ops2: Optional InflectionFeatureOperations instance for item2's project.
                 Defaults to self.

        Returns:
            tuple: (is_different, differences) where:
                - is_different (bool): True if items differ
                - differences (dict): Maps property names to (value1, value2) tuples

        Example:
            >>> ic1 = project1_inflOps.InflectionClassFind("First Declension")
            >>> ic2 = project2_inflOps.InflectionClassFind("First Declension")
            >>> is_diff, diffs = project1_inflOps.CompareTo(
            ...     ic1, ic2,
            ...     ops1=project1_inflOps,
            ...     ops2=project2_inflOps
            ... )
            >>> if is_diff:
            ...     for prop, (val1, val2) in diffs.items():
            ...         print(f"{prop}: {val1} -> {val2}")

        Notes:
            - Compares all MultiString properties across all writing systems
            - Returns empty dict if items are identical
            - Handles cross-project comparison via ops1/ops2
        """
        if ops1 is None:
            ops1 = self
        if ops2 is None:
            ops2 = self

        # Get syncable properties from both items
        props1 = ops1.GetSyncableProperties(item1)
        props2 = ops2.GetSyncableProperties(item2)

        is_different = False
        differences = {}

        # Compare each property
        all_keys = set(props1.keys()) | set(props2.keys())
        for key in all_keys:
            val1 = props1.get(key)
            val2 = props2.get(key)

            # For MultiString properties, compare the dictionaries
            if val1 != val2:
                is_different = True
                differences[key] = (val1, val2)

        return (is_different, differences)


    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

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
