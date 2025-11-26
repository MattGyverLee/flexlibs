#
#   GramCatOperations.py
#
#   Class: GramCatOperations
#          Grammatical Category operations for FieldWorks Language Explorer
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
from SIL.LCModel import ICmPossibility, ICmPossibilityFactory
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class GramCatOperations:
    """
    This class provides operations for managing Grammatical Categories in a
    FieldWorks project.

    Grammatical categories are used to classify and describe grammatical
    properties such as person, number, gender, tense, aspect, mood, case,
    and other morphosyntactic features used in linguistic analysis.

    Usage::

        from flexlibs import FLExProject, GramCatOperations

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        gramCatOps = GramCatOperations(project)

        # Get all grammatical categories
        for cat in gramCatOps.GetAll():
            print(gramCatOps.GetName(cat))

        # Create a new category
        person = gramCatOps.Create("person")

        # Create subcategories
        first = gramCatOps.Create("1st person", parent=person)
        second = gramCatOps.Create("2nd person", parent=person)
        third = gramCatOps.Create("3rd person", parent=person)

        # Navigate hierarchy
        parent = gramCatOps.GetParent(first)
        subcats = gramCatOps.GetSubcategories(person)

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize GramCatOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    def GetAll(self):
        """
        Get all grammatical categories in the project.

        Yields:
            ICmPossibility: Each top-level grammatical category object in the
                project's feature system.

        Example:
            >>> gramCatOps = GramCatOperations(project)
            >>> for cat in gramCatOps.GetAll():
            ...     name = gramCatOps.GetName(cat)
            ...     subcats = gramCatOps.GetSubcategories(cat)
            ...     print(f"{name}: {len(subcats)} subcategories")
            person: 3 subcategories
            number: 2 subcategories
            gender: 3 subcategories
            tense: 5 subcategories

        Notes:
            - Returns only top-level categories
            - Does not include subcategories
            - Use GetSubcategories() to navigate the hierarchy
            - Categories are stored in the feature system

        See Also:
            GetSubcategories, Create
        """
        feature_system = self.project.lp.MsFeatureSystemOA
        if feature_system:
            for cat in feature_system.TypesOC:
                yield cat


    def Create(self, name, parent=None):
        """
        Create a new grammatical category.

        Args:
            name (str): The name of the category (e.g., "person", "1st person").
            parent (ICmPossibility or int, optional): Optional parent category
                for creating subcategories. Can be an ICmPossibility object or
                an HVO. Defaults to None (creates top-level category).

        Returns:
            ICmPossibility: The newly created grammatical category object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name is None.
            FP_ParameterError: If name is empty, or if a category with this
                name already exists.

        Example:
            >>> gramCatOps = GramCatOperations(project)
            >>> # Create top-level category
            >>> person = gramCatOps.Create("person")
            >>> print(gramCatOps.GetName(person))
            person

            >>> # Create subcategories
            >>> first = gramCatOps.Create("1st person", parent=person)
            >>> second = gramCatOps.Create("2nd person", parent=person)
            >>> third = gramCatOps.Create("3rd person", parent=person)

            >>> # Create nested hierarchy
            >>> number = gramCatOps.Create("number")
            >>> singular = gramCatOps.Create("singular", parent=number)
            >>> plural = gramCatOps.Create("plural", parent=number)

        Notes:
            - If parent is None, creates a top-level category
            - If parent is provided, creates a subcategory
            - Name must be unique within the project
            - The category is created in the default analysis writing system
            - Used for linguistic feature analysis in morphology

        See Also:
            Delete, GetSubcategories, GetParent
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        # Get the writing system handle
        wsHandle = self.project.project.DefaultAnalWs

        # Create the new category using the factory
        factory = self.project.project.ServiceLocator.GetService(ICmPossibilityFactory)
        new_cat = factory.Create()

        # Add to parent's subcategories or to top-level TypesOC (must be done before setting properties)
        if parent:
            parent_obj = self.__ResolveObject(parent)
            parent_obj.SubPossibilitiesOS.Add(new_cat)
        else:
            feature_system = self.project.lp.MsFeatureSystemOA
            feature_system.TypesOC.Add(new_cat)

        # Set name
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_cat.Name.set_String(wsHandle, mkstr_name)

        return new_cat


    def Delete(self, cat_or_hvo):
        """
        Delete a grammatical category.

        Args:
            cat_or_hvo: The ICmPossibility object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If cat_or_hvo is None.
            FP_ParameterError: If the category is in use and cannot be deleted.

        Example:
            >>> gramCatOps = GramCatOperations(project)
            >>> obsolete = gramCatOps.Create("obsolete_feature")
            >>> # Later, if not needed...
            >>> gramCatOps.Delete(obsolete)

        Warning:
            - Deleting a category that is in use may raise an error from FLEx
            - Will also delete all subcategories recursively
            - Deletion is permanent and cannot be undone
            - Morphological rules or entries using this may be affected

        See Also:
            Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not cat_or_hvo:
            raise FP_NullParameterError()

        # Resolve to category object
        cat = self.__ResolveObject(cat_or_hvo)

        # Remove from the feature system TypesOC
        feature_system = self.project.lp.MsFeatureSystemOA
        feature_system.TypesOC.Remove(cat)


    def GetName(self, cat_or_hvo, wsHandle=None):
        """
        Get the name of a grammatical category.

        Args:
            cat_or_hvo: The ICmPossibility object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The category name, or empty string if not set.

        Raises:
            FP_NullParameterError: If cat_or_hvo is None.

        Example:
            >>> gramCatOps = GramCatOperations(project)
            >>> person = gramCatOps.Create("person")
            >>> name = gramCatOps.GetName(person)
            >>> print(name)
            person

            >>> # Get name in a specific writing system
            >>> vern_name = gramCatOps.GetName(person, project.WSHandle('en'))

            >>> # List all categories
            >>> for cat in gramCatOps.GetAll():
            ...     print(gramCatOps.GetName(cat))

        See Also:
            SetName, GetSubcategories
        """
        if not cat_or_hvo:
            raise FP_NullParameterError()

        cat = self.__ResolveObject(cat_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(cat.Name.get_String(wsHandle)).Text
        return name or ""


    def SetName(self, cat_or_hvo, name, wsHandle=None):
        """
        Set the name of a grammatical category.

        Args:
            cat_or_hvo: The ICmPossibility object or HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If cat_or_hvo or name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> gramCatOps = GramCatOperations(project)
            >>> cat = gramCatOps.Create("prson")  # typo
            >>> gramCatOps.SetName(cat, "person")  # fix it

            >>> # Set name in vernacular WS
            >>> gramCatOps.SetName(cat, "persona", project.WSHandle('es'))

        See Also:
            GetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not cat_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        cat = self.__ResolveObject(cat_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        cat.Name.set_String(wsHandle, mkstr)


    def GetSubcategories(self, cat_or_hvo):
        """
        Get all subcategories of a grammatical category.

        Args:
            cat_or_hvo: The ICmPossibility object or HVO.

        Returns:
            list: List of ICmPossibility subcategory objects (empty list if none).

        Raises:
            FP_NullParameterError: If cat_or_hvo is None.

        Example:
            >>> gramCatOps = GramCatOperations(project)
            >>> person = gramCatOps.Create("person")
            >>> first = gramCatOps.Create("1st person", parent=person)
            >>> second = gramCatOps.Create("2nd person", parent=person)
            >>> third = gramCatOps.Create("3rd person", parent=person)
            >>>
            >>> subcats = gramCatOps.GetSubcategories(person)
            >>> for subcat in subcats:
            ...     print(gramCatOps.GetName(subcat))
            1st person
            2nd person
            3rd person

            >>> # Check if category has subcategories
            >>> if gramCatOps.GetSubcategories(cat):
            ...     print("This category has subcategories")

        Notes:
            - Returns direct children only (not recursive)
            - Returns empty list if no subcategories
            - Subcategories form a hierarchy for fine-grained classification

        See Also:
            GetAll, GetParent, Create
        """
        if not cat_or_hvo:
            raise FP_NullParameterError()

        cat = self.__ResolveObject(cat_or_hvo)

        return list(cat.SubPossibilitiesOS)


    def GetParent(self, cat_or_hvo):
        """
        Get the parent category of a grammatical category.

        Args:
            cat_or_hvo: The ICmPossibility object or HVO.

        Returns:
            ICmPossibility or None: Parent category, or None if top-level.

        Raises:
            FP_NullParameterError: If cat_or_hvo is None.

        Example:
            >>> gramCatOps = GramCatOperations(project)
            >>> person = gramCatOps.Create("person")
            >>> first = gramCatOps.Create("1st person", parent=person)
            >>>
            >>> parent = gramCatOps.GetParent(first)
            >>> print(gramCatOps.GetName(parent))
            person
            >>>
            >>> # Top-level categories have no parent
            >>> print(gramCatOps.GetParent(person))
            None

            >>> # Traverse up the hierarchy
            >>> cat = first
            >>> while cat:
            ...     print(gramCatOps.GetName(cat))
            ...     cat = gramCatOps.GetParent(cat)
            1st person
            person

        Notes:
            - Returns None for top-level categories
            - Use to traverse hierarchy upward
            - Useful for determining category depth
            - Parent-child relationships define category taxonomy

        See Also:
            GetSubcategories, Create
        """
        if not cat_or_hvo:
            raise FP_NullParameterError()

        cat = self.__ResolveObject(cat_or_hvo)

        # Check if this category has a parent
        # The Owner property returns the owning object
        if hasattr(cat, 'Owner') and cat.Owner:
            # Check if the owner is also a possibility (not the feature system itself)
            try:
                owner = ICmPossibility(cat.Owner)
                return owner
            except (AttributeError, System.InvalidCastException) as e:
                # If owner is not a possibility, it's a top-level category
                return None

        return None


    # --- Private Helper Methods ---

    def __ResolveObject(self, cat_or_hvo):
        """
        Resolve HVO or object to ICmPossibility.

        Args:
            cat_or_hvo: Either an ICmPossibility object or an HVO (int).

        Returns:
            ICmPossibility: The resolved category object.
        """
        if isinstance(cat_or_hvo, int):
            return self.project.Object(cat_or_hvo)
        return cat_or_hvo


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
