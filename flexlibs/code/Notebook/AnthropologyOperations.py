#
#   AnthropologyOperations.py
#
#   Class: AnthropologyOperations
#          Anthropological/cultural item operations for FieldWorks Language
#          Explorer projects via SIL Language and Culture Model (LCM) API.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2025
#

# Import FLEx LCM types
from SIL.LCModel import (
    ICmAnthroItem,
    ICmAnthroItemFactory,
    IText,
    ICmPerson,
    ICmPossibility,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils
from System import Guid, DateTime

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)
from ..BaseOperations import BaseOperations

class AnthropologyOperations(BaseOperations):
    """
    This class provides operations for managing anthropological and cultural
    items in a FieldWorks project.

    Anthropological items (ICmAnthroItem) are used to categorize and organize
    cultural information collected during fieldwork. They support hierarchical
    organization, OCM (Outline of Cultural Materials) codes, and linking to
    texts and researchers. These items help linguists document cultural context
    alongside linguistic data.

    This class should be accessed via FLExProject.Anthropology property.

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Create a new anthropology item
        item = project.Anthropology.Create("Marriage Customs", "MAR")

        # Set OCM code
        project.Anthropology.SetAnthroCode(item, "586")

        # Set description
        project.Anthropology.SetDescription(item,
            "Traditional marriage practices and ceremonies")

        # Create hierarchical structure
        subitem = project.Anthropology.CreateSubitem(item,
            "Wedding Ceremony", "WED")

        # Link to texts
        text = project.Texts.Find("Wedding Story 1")
        if text:
            project.Anthropology.AddText(item, text)

        # Get all items linked to a specific text
        for anthro_item in project.Anthropology.GetItemsForText(text):
            name = project.Anthropology.GetName(anthro_item)
            code = project.Anthropology.GetAnthroCode(anthro_item)
            print(f"{name} ({code})")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize AnthropologyOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)

    def __WSHandle(self, wsHandle):
        """
        Internal helper for writing system handles.

        Args:
            wsHandle: Writing system handle or None for default analysis WS.

        Returns:
            int: The writing system handle to use.
        """
        if wsHandle is None:
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(wsHandle, self.project.project.DefaultAnalWs)

    def __ValidatedItemHvo(self, item_or_hvo):
        """
        Internal function to validate and convert item_or_hvo to HVO.

        Args:
            item_or_hvo: Either an ICmAnthroItem object or its HVO (integer).

        Returns:
            int: The HVO of the anthropology item.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
        """
        if not item_or_hvo:
            raise FP_NullParameterError()

        try:
            hvo = item_or_hvo.Hvo
        except AttributeError:
            hvo = item_or_hvo

        return hvo

    def __GetItemObject(self, item_or_hvo):
        """
        Internal function to get ICmAnthroItem object from item_or_hvo.

        Args:
            item_or_hvo: Either an ICmAnthroItem object or its HVO (integer).

        Returns:
            ICmAnthroItem: The anthropology item object.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the object doesn't exist or isn't valid.
        """
        hvo = self.__ValidatedItemHvo(item_or_hvo)

        try:
            obj = self.project.Object(hvo)
            return ICmAnthroItem(obj)
        except Exception:
            raise FP_ParameterError(f"Invalid anthropology item object or HVO: {item_or_hvo}")

    # --- Core CRUD Operations ---

    def GetAll(self, flat=True):
        """
        Get all anthropology items in the project.

        Args:
            flat (bool): If True, returns a flat list of all items including
                subitems. If False, returns only top-level items (use
                GetSubitems to navigate hierarchy). Defaults to True.

        Returns:
            list: List of ICmAnthroItem objects.

        Example:
            >>> # Get all items in a flat list
            >>> for item in project.Anthropology.GetAll(flat=True):
            ...     name = project.Anthropology.GetName(item)
            ...     code = project.Anthropology.GetAnthroCode(item)
            ...     print(f"{name} - {code}")
            Marriage Customs - 586
            Wedding Ceremony - 586.1
            Divorce - 587
            ...

            >>> # Get only top-level items
            >>> top_level = project.Anthropology.GetAll(flat=False)
            >>> for item in top_level:
            ...     name = project.Anthropology.GetName(item)
            ...     print(f"Parent: {name}")
            ...     for subitem in project.Anthropology.GetSubitems(item):
            ...         sub_name = project.Anthropology.GetName(subitem)
            ...         print(f"  - {sub_name}")
            Parent: Marriage Customs
              - Wedding Ceremony
              - Marriage Gifts
            ...

        Notes:
            - Returns list, not iterator
            - Flat list is useful for searching and iteration
            - Hierarchical list is useful for tree display
            - Items can use OCM (Outline of Cultural Materials) codes
            - Items are ordered by their position in the database

        See Also:
            Find, FindByCode, GetSubitems
        """
        anthro_list = self.project.lp.AnthroListOA
        if not anthro_list:
            return []

        return list(self.project.UnpackNestedPossibilityList(
            anthro_list.PossibilitiesOS,
            ICmAnthroItem,
            flat
        ))

    def Create(self, name, abbreviation=None, anthro_code=None):
        """
        Create a new anthropology item.

        Creates a new top-level ICmAnthroItem in the project's anthropology list.
        Use CreateSubitem() to create hierarchical items.

        Args:
            name (str): The name of the item (e.g., "Marriage Customs").
            abbreviation (str, optional): Short abbreviation (e.g., "MAR").
                If None, no abbreviation is set. Defaults to None.
            anthro_code (str, optional): OCM (Outline of Cultural Materials) code
                (e.g., "586" for marriage). If None, no code is set. Defaults to None.

        Returns:
            ICmAnthroItem: The newly created anthropology item object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name is None or empty.
            FP_ParameterError: If an item with this name already exists.

        Example:
            >>> # Create a simple item
            >>> item = project.Anthropology.Create("Marriage Customs")
            >>> print(project.Anthropology.GetName(item))
            Marriage Customs

            >>> # Create with abbreviation and OCM code
            >>> item = project.Anthropology.Create(
            ...     "Marriage Customs",
            ...     abbreviation="MAR",
            ...     anthro_code="586"
            ... )
            >>> print(project.Anthropology.GetAnthroCode(item))
            586

            >>> # Create multiple items
            >>> kinship = project.Anthropology.Create("Kinship", "KIN", "600")
            >>> religion = project.Anthropology.Create("Religion", "REL", "770")

        Notes:
            - Name must be unique within the project
            - Abbreviations don't need to be unique but should be distinct
            - OCM codes follow the Outline of Cultural Materials standard
            - The item is created in the default analysis writing system
            - Use CreateSubitem() for hierarchical items

        See Also:
            CreateSubitem, Delete, Exists, Find
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        name = name.strip()
        if not name:
            raise FP_NullParameterError()

        # Check if item already exists
        if self.Exists(name):
            raise FP_ParameterError(f"Anthropology item '{name}' already exists")

        # Ensure anthropology list exists
        if not self.project.lp.AnthroListOA:
            from SIL.LCModel import ICmPossibilityListFactory
            list_factory = self.project.project.ServiceLocator.GetService(ICmPossibilityListFactory)
            anthro_list = list_factory.Create()
            self.project.lp.AnthroListOA = anthro_list
        else:
            anthro_list = self.project.lp.AnthroListOA

        # Get the writing system handle
        wsHandle = self.project.project.DefaultAnalWs

        # Create the new item using the factory
        factory = self.project.project.ServiceLocator.GetService(ICmAnthroItemFactory)
        new_item = factory.Create()

        # Add to the anthropology list (must be done before setting properties)
        anthro_list.PossibilitiesOS.Add(new_item)

        # Set name
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_item.Name.set_String(wsHandle, mkstr_name)

        # Set abbreviation if provided
        if abbreviation:
            mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
            new_item.Abbreviation.set_String(wsHandle, mkstr_abbr)

        # Set OCM code if provided
        if anthro_code:
            new_item.AnthroCode = anthro_code

        return new_item

    def CreateSubitem(self, parent_item, name, abbreviation=None, anthro_code=None):
        """
        Create a new anthropology item as a child of an existing item.

        Creates a hierarchical relationship where the new item is a subcategory
        or more specific aspect of the parent item.

        Args:
            parent_item: The parent ICmAnthroItem object or HVO.
            name (str): The name of the subitem (e.g., "Wedding Ceremony").
            abbreviation (str, optional): Short abbreviation. Defaults to None.
            anthro_code (str, optional): OCM code for the subitem. Defaults to None.

        Returns:
            ICmAnthroItem: The newly created subitem object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If parent_item or name is None/empty.
            FP_ParameterError: If parent_item is invalid.

        Example:
            >>> # Create parent item
            >>> marriage = project.Anthropology.Create("Marriage Customs", "MAR", "586")
            >>>
            >>> # Create subitems
            >>> wedding = project.Anthropology.CreateSubitem(
            ...     marriage, "Wedding Ceremony", "WED", "586.1"
            ... )
            >>> gifts = project.Anthropology.CreateSubitem(
            ...     marriage, "Marriage Gifts", "GIFT", "586.2"
            ... )
            >>>
            >>> # Verify hierarchy
            >>> parent = project.Anthropology.GetParent(wedding)
            >>> print(project.Anthropology.GetName(parent))
            Marriage Customs
            >>>
            >>> # Get all subitems
            >>> for sub in project.Anthropology.GetSubitems(marriage):
            ...     print(project.Anthropology.GetName(sub))
            Wedding Ceremony
            Marriage Gifts

        Notes:
            - Creates hierarchical organization of cultural data
            - Subitems inherit context from parent
            - OCM codes typically use decimal notation (e.g., 586.1, 586.2)
            - Multiple levels of nesting are supported
            - Parent item must exist before creating subitems

        See Also:
            Create, GetSubitems, GetParent, Delete
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        name = name.strip()
        if not name:
            raise FP_NullParameterError()

        parent = self.__GetItemObject(parent_item)

        # Get the writing system handle
        wsHandle = self.project.project.DefaultAnalWs

        # Create the new item using the factory
        factory = self.project.project.ServiceLocator.GetService(ICmAnthroItemFactory)
        new_item = factory.Create()

        # Add to parent's subitems (must be done before setting properties)
        parent.SubPossibilitiesOS.Add(new_item)

        # Set name
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_item.Name.set_String(wsHandle, mkstr_name)

        # Set abbreviation if provided
        if abbreviation:
            mkstr_abbr = TsStringUtils.MakeString(abbreviation, wsHandle)
            new_item.Abbreviation.set_String(wsHandle, mkstr_abbr)

        # Set OCM code if provided
        if anthro_code:
            new_item.AnthroCode = anthro_code

        return new_item

    def Delete(self, item_or_hvo):
        """
        Delete an anthropology item.

        Removes the item from the project. If the item has subitems, they
        will also be deleted. Removes all links to texts and researchers.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> # Delete a specific item
            >>> item = project.Anthropology.Find("Obsolete Item")
            >>> if item:
            ...     project.Anthropology.Delete(item)

            >>> # Delete by HVO
            >>> project.Anthropology.Delete(item_hvo)

        Warning:
            - Deleting an item also deletes all its subitems
            - This operation cannot be undone (unless using UndoActionSequence)
            - Text and researcher links are removed, but the texts and
              researchers themselves are not deleted

        See Also:
            Create, CreateSubitem, Exists
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        item = self.__GetItemObject(item_or_hvo)

        # Get the anthropology list
        anthro_list = self.project.lp.AnthroListOA
        if anthro_list:
            # Check if it's a top-level item
            if anthro_list.PossibilitiesOS.Contains(item):
                anthro_list.PossibilitiesOS.Remove(item)
            else:
                # It's a subitem, remove from parent
                if hasattr(item, 'Owner') and item.Owner:
                    try:
                        parent = ICmPossibility(item.Owner)
                        if hasattr(parent, 'SubPossibilitiesOS'):
                            parent.SubPossibilitiesOS.Remove(item)
                    except Exception:
                        pass

    def Exists(self, name):
        """
        Check if an anthropology item with the given name exists.

        Performs a case-sensitive comparison of item names in the default
        analysis writing system.

        Args:
            name (str): The name of the item to check.

        Returns:
            bool: True if an item with the given name exists, False otherwise.

        Raises:
            FP_NullParameterError: If name is None or empty.

        Example:
            >>> if project.Anthropology.Exists("Marriage Customs"):
            ...     print("Item already exists")
            ... else:
            ...     item = project.Anthropology.Create("Marriage Customs")

            >>> # Case-sensitive check
            >>> print(project.Anthropology.Exists("marriage customs"))
            False

        Notes:
            - Search is case-sensitive
            - Searches through all items (including subitems)
            - Returns False for empty or whitespace-only names
            - More efficient than Find() when you only need existence check

        See Also:
            Find, FindByCode, Create
        """
        if name is None:
            raise FP_NullParameterError()

        name = name.strip()
        if not name:
            raise FP_NullParameterError()

        return self.Find(name) is not None

    def Find(self, name):
        """
        Find an anthropology item by its name.

        Searches through all anthropology items (including subitems) and
        returns the first item with a matching name.

        Args:
            name (str): The name to search for.

        Returns:
            ICmAnthroItem or None: The item object if found, None otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> # Find by name
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> if item:
            ...     code = project.Anthropology.GetAnthroCode(item)
            ...     print(f"Found item with code: {code}")
            Found item with code: 586

            >>> # Handle not found
            >>> item = project.Anthropology.Find("Nonexistent Item")
            >>> if not item:
            ...     print("Item not found")
            Item not found

        Notes:
            - Search is case-sensitive
            - Searches in default analysis writing system
            - Returns first match only
            - Returns None if not found (doesn't raise exception)
            - For OCM code search, use FindByCode()

        See Also:
            FindByCode, Exists, GetAll
        """
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            return None

        name = name.strip()
        wsHandle = self.project.project.DefaultAnalWs

        # Search through all items
        for item in self.GetAll(flat=True):
            item_name = ITsString(item.Name.get_String(wsHandle)).Text
            if item_name == name:
                return item

        return None

    def FindByCode(self, anthro_code):
        """
        Find an anthropology item by its OCM code.

        Searches through all anthropology items and returns the first item
        with a matching AnthroCode (Outline of Cultural Materials code).

        Args:
            anthro_code (str): The OCM code to search for (e.g., "586").

        Returns:
            ICmAnthroItem or None: The item object if found, None otherwise.

        Raises:
            FP_NullParameterError: If anthro_code is None.

        Example:
            >>> # Find by OCM code
            >>> item = project.Anthropology.FindByCode("586")
            >>> if item:
            ...     name = project.Anthropology.GetName(item)
            ...     print(f"Code 586 is: {name}")
            Code 586 is: Marriage Customs

            >>> # Find hierarchical codes
            >>> item = project.Anthropology.FindByCode("586.1")
            >>> if item:
            ...     name = project.Anthropology.GetName(item)
            ...     parent = project.Anthropology.GetParent(item)
            ...     parent_name = project.Anthropology.GetName(parent)
            ...     print(f"{name} is subcategory of {parent_name}")
            Wedding Ceremony is subcategory of Marriage Customs

        Notes:
            - Search is case-sensitive
            - Returns first match only
            - Returns None if not found
            - OCM codes are standard anthropological classification system
            - Common OCM code ranges:
              - 100-199: Orientation
              - 200-299: Food and Clothing
              - 300-399: Housing
              - 400-499: Economy
              - 500-599: Kinship and Family
              - 600-699: Political Behavior
              - 700-799: Religion
              - 800-899: Social Structure

        See Also:
            Find, GetAnthroCode, SetAnthroCode
        """
        if anthro_code is None:
            raise FP_NullParameterError()

        if not anthro_code or not anthro_code.strip():
            return None

        anthro_code = anthro_code.strip()

        # Search through all items
        for item in self.GetAll(flat=True):
            if hasattr(item, 'AnthroCode') and item.AnthroCode:
                if item.AnthroCode == anthro_code:
                    return item

        return None

    def FindByCategory(self, category):
        """
        Find all anthropology items in a specific category.

        Searches for items that have been assigned to a particular category
        possibility.

        Args:
            category: ICmPossibility object representing the category.

        Returns:
            list: List of ICmAnthroItem objects in that category.

        Raises:
            FP_NullParameterError: If category is None.

        Example:
            >>> # Get a category from the categories list
            >>> categories = project.lp.AnthroListOA
            >>> if categories and categories.PossibilitiesOS.Count > 0:
            ...     category = categories.PossibilitiesOS[0]
            ...     items = project.Anthropology.FindByCategory(category)
            ...     for item in items:
            ...         name = project.Anthropology.GetName(item)
            ...         print(f"Item: {name}")

        Notes:
            - Returns empty list if no items found
            - Category must be a valid ICmPossibility
            - Items can belong to multiple categories
            - This searches the item's category reference

        See Also:
            Find, FindByCode, GetCategory, SetCategory
        """
        if not category:
            raise FP_NullParameterError()

        results = []

        # Search through all items
        for item in self.GetAll(flat=True):
            # Check if item has this category
            if hasattr(item, 'CategoryRA') and item.CategoryRA:
                if item.CategoryRA == category:
                    results.append(item)

        return results

    # --- Property Access Methods ---

    def GetName(self, item_or_hvo, wsHandle=None):
        """
        Get the name of an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The item name, or empty string if not set.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> name = project.Anthropology.GetName(item)
            >>> print(name)
            Marriage Customs

            >>> # Get name in a specific writing system
            >>> name_fr = project.Anthropology.GetName(item,
            ...                                         project.WSHandle('fr'))
            >>> print(name_fr)
            Coutumes matrimoniales

        Notes:
            - Returns empty string if name not set in specified writing system
            - Names are typically set in multiple writing systems
            - Default writing system is the default analysis WS

        See Also:
            SetName, GetAbbreviation, GetDescription
        """
        item = self.__GetItemObject(item_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(item.Name.get_String(wsHandle)).Text
        return name or ""

    def SetName(self, item_or_hvo, name, wsHandle=None):
        """
        Set the name of an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo or name is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage")
            >>> project.Anthropology.SetName(item, "Marriage Customs")
            >>> print(project.Anthropology.GetName(item))
            Marriage Customs

            >>> # Set in multiple writing systems
            >>> project.Anthropology.SetName(item, "Marriage Customs", "en")
            >>> project.Anthropology.SetName(item, "Coutumes matrimoniales",
            ...                               project.WSHandle('fr'))

        Notes:
            - Name is stored in the specified writing system
            - Can set different names for different writing systems
            - Empty string clears the name in that writing system

        See Also:
            GetName, SetAbbreviation, SetDescription
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        item = self.__GetItemObject(item_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        item.Name.set_String(wsHandle, mkstr)

    def GetAbbreviation(self, item_or_hvo, wsHandle=None):
        """
        Get the abbreviation of an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The abbreviation, or empty string if not set.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> abbr = project.Anthropology.GetAbbreviation(item)
            >>> print(abbr)
            MAR

            >>> # Use in display
            >>> for item in project.Anthropology.GetAll():
            ...     name = project.Anthropology.GetName(item)
            ...     abbr = project.Anthropology.GetAbbreviation(item)
            ...     if abbr:
            ...         print(f"{abbr}: {name}")
            ...     else:
            ...         print(name)
            MAR: Marriage Customs
            WED: Wedding Ceremony
            KIN: Kinship

        Notes:
            - Returns empty string if abbreviation not set
            - Abbreviations are shorter identifiers for display
            - Typically 2-5 characters

        See Also:
            SetAbbreviation, GetName, GetAnthroCode
        """
        item = self.__GetItemObject(item_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        abbr = ITsString(item.Abbreviation.get_String(wsHandle)).Text
        return abbr or ""

    def SetAbbreviation(self, item_or_hvo, abbreviation, wsHandle=None):
        """
        Set the abbreviation of an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.
            abbreviation (str): The new abbreviation.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo or abbreviation is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> project.Anthropology.SetAbbreviation(item, "MAR")
            >>> print(project.Anthropology.GetAbbreviation(item))
            MAR

            >>> # Clear abbreviation
            >>> project.Anthropology.SetAbbreviation(item, "")

        Notes:
            - Abbreviation is stored in the specified writing system
            - Can set different abbreviations for different writing systems
            - Empty string clears the abbreviation

        See Also:
            GetAbbreviation, SetName, SetAnthroCode
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if abbreviation is None:
            raise FP_NullParameterError()

        item = self.__GetItemObject(item_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(abbreviation, wsHandle)
        item.Abbreviation.set_String(wsHandle, mkstr)

    def GetDescription(self, item_or_hvo, wsHandle=None):
        """
        Get the description of an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The description, or empty string if not set.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> desc = project.Anthropology.GetDescription(item)
            >>> print(desc)
            Traditional marriage practices, including courtship,
            betrothal, wedding ceremonies, and gift exchanges.

            >>> # Display full item information
            >>> name = project.Anthropology.GetName(item)
            >>> code = project.Anthropology.GetAnthroCode(item)
            >>> desc = project.Anthropology.GetDescription(item)
            >>> print(f"{name} ({code})")
            >>> print(f"Description: {desc}")

        Notes:
            - Returns empty string if description not set
            - Descriptions can be multi-paragraph text
            - Use descriptions to document cultural context

        See Also:
            SetDescription, GetName, GetAnthroCode
        """
        item = self.__GetItemObject(item_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        desc = ITsString(item.Description.get_String(wsHandle)).Text
        return desc or ""

    def SetDescription(self, item_or_hvo, description, wsHandle=None):
        """
        Set the description of an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.
            description (str): The new description.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo or description is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> project.Anthropology.SetDescription(item,
            ...     "Traditional marriage practices, including courtship, "
            ...     "betrothal, wedding ceremonies, and gift exchanges."
            ... )

            >>> # Set in multiple languages
            >>> project.Anthropology.SetDescription(item,
            ...     "Traditional marriage practices...", "en")
            >>> project.Anthropology.SetDescription(item,
            ...     "Pratiques matrimoniales traditionnelles...",
            ...     project.WSHandle('fr'))

            >>> # Clear description
            >>> project.Anthropology.SetDescription(item, "")

        Notes:
            - Description is stored in the specified writing system
            - Can set different descriptions for different writing systems
            - Empty string clears the description
            - Descriptions support multi-paragraph text

        See Also:
            GetDescription, SetName, SetAnthroCode
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if description is None:
            raise FP_NullParameterError()

        item = self.__GetItemObject(item_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(description, wsHandle)
        item.Description.set_String(wsHandle, mkstr)

    def GetAnthroCode(self, item_or_hvo):
        """
        Get the OCM (Outline of Cultural Materials) code of an item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.

        Returns:
            str: The OCM code, or empty string if not set.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> code = project.Anthropology.GetAnthroCode(item)
            >>> print(code)
            586

            >>> # Display all items with their codes
            >>> for item in project.Anthropology.GetAll():
            ...     name = project.Anthropology.GetName(item)
            ...     code = project.Anthropology.GetAnthroCode(item)
            ...     if code:
            ...         print(f"{code}: {name}")
            ...     else:
            ...         print(f"No code: {name}")
            586: Marriage Customs
            586.1: Wedding Ceremony
            587: Divorce
            No code: Custom Category

        Notes:
            - OCM (Outline of Cultural Materials) is a standard classification
            - Returns empty string if no code is set
            - Codes typically use decimal notation for hierarchy
            - Common OCM code ranges documented in FindByCode()

        See Also:
            SetAnthroCode, FindByCode, GetName
        """
        item = self.__GetItemObject(item_or_hvo)

        if hasattr(item, 'AnthroCode') and item.AnthroCode:
            return item.AnthroCode
        return ""

    def SetAnthroCode(self, item_or_hvo, anthro_code):
        """
        Set the OCM (Outline of Cultural Materials) code of an item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.
            anthro_code (str): The OCM code to set.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo or anthro_code is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> project.Anthropology.SetAnthroCode(item, "586")
            >>> print(project.Anthropology.GetAnthroCode(item))
            586

            >>> # Set hierarchical codes
            >>> subitem = project.Anthropology.Find("Wedding Ceremony")
            >>> project.Anthropology.SetAnthroCode(subitem, "586.1")

            >>> # Clear code
            >>> project.Anthropology.SetAnthroCode(item, "")

        Notes:
            - OCM codes follow standard anthropological classification
            - Empty string clears the code
            - Codes are stored as strings, not validated
            - Use decimal notation for hierarchical codes (e.g., 586.1)

        See Also:
            GetAnthroCode, FindByCode, SetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if anthro_code is None:
            raise FP_NullParameterError()

        item = self.__GetItemObject(item_or_hvo)
        item.AnthroCode = anthro_code

    def GetCategory(self, item_or_hvo):
        """
        Get the category of an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.

        Returns:
            ICmPossibility or None: The category object if set, None otherwise.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> category = project.Anthropology.GetCategory(item)
            >>> if category:
            ...     cat_name = category.Name.BestAnalysisAlternative.Text
            ...     print(f"Category: {cat_name}")
            ... else:
            ...     print("No category assigned")

        Notes:
            - Returns None if no category is assigned
            - Category is a reference to a possibility item
            - Categories help organize anthropology items

        See Also:
            SetCategory, FindByCategory
        """
        item = self.__GetItemObject(item_or_hvo)

        if hasattr(item, 'CategoryRA') and item.CategoryRA:
            return item.CategoryRA
        return None

    def SetCategory(self, item_or_hvo, category):
        """
        Set the category of an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.
            category: ICmPossibility object or None to clear.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item or category is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>>
            >>> # Set category from a possibility list
            >>> # (assuming categories are defined in a list)
            >>> category = project.lp.AnthroListOA.PossibilitiesOS[0]
            >>> project.Anthropology.SetCategory(item, category)
            >>>
            >>> # Clear category
            >>> project.Anthropology.SetCategory(item, None)

        Notes:
            - Category must be a valid ICmPossibility object
            - Setting to None clears the category
            - Categories help organize and filter items

        See Also:
            GetCategory, FindByCategory
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        item = self.__GetItemObject(item_or_hvo)

        if category is None:
            item.CategoryRA = None
        else:
            try:
                cat_poss = ICmPossibility(category)
                item.CategoryRA = cat_poss
            except Exception:
                raise FP_ParameterError("category must be a valid ICmPossibility object")

    # --- Hierarchy Operations ---

    def GetSubitems(self, item_or_hvo):
        """
        Get all direct subitems of an anthropology item.

        Returns only immediate children, not all descendants. For a full
        hierarchical view, use GetAll(flat=True).

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.

        Returns:
            list: List of ICmAnthroItem objects that are direct children.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> # Get subitems of a parent
            >>> marriage = project.Anthropology.Find("Marriage Customs")
            >>> subitems = project.Anthropology.GetSubitems(marriage)
            >>> for sub in subitems:
            ...     name = project.Anthropology.GetName(sub)
            ...     print(f"  - {name}")
              - Wedding Ceremony
              - Marriage Gifts
              - Bride Price

            >>> # Check if item has subitems
            >>> if project.Anthropology.GetSubitems(marriage):
            ...     print("Has subitems")
            ... else:
            ...     print("No subitems")
            Has subitems

            >>> # Build hierarchical display
            >>> def display_hierarchy(item, indent=0):
            ...     name = project.Anthropology.GetName(item)
            ...     print("  " * indent + name)
            ...     for sub in project.Anthropology.GetSubitems(item):
            ...         display_hierarchy(sub, indent + 1)
            >>> for top in project.Anthropology.GetAll(flat=False):
            ...     display_hierarchy(top)

        Notes:
            - Returns empty list if item has no subitems
            - Returns only direct children, not grandchildren
            - Use GetAll(flat=True) to get all items in hierarchy
            - Subitems maintain their database order

        See Also:
            CreateSubitem, GetParent, GetAll
        """
        item = self.__GetItemObject(item_or_hvo)

        if hasattr(item, 'SubPossibilitiesOS'):
            return list(item.SubPossibilitiesOS)
        return []

    def GetParent(self, item_or_hvo):
        """
        Get the parent item of an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.

        Returns:
            ICmAnthroItem or None: The parent item if this is a subitem,
                None if this is a top-level item.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> # Get parent of a subitem
            >>> wedding = project.Anthropology.Find("Wedding Ceremony")
            >>> parent = project.Anthropology.GetParent(wedding)
            >>> if parent:
            ...     parent_name = project.Anthropology.GetName(parent)
            ...     print(f"Parent: {parent_name}")
            ... else:
            ...     print("This is a top-level item")
            Parent: Marriage Customs

            >>> # Build breadcrumb trail
            >>> def get_path(item):
            ...     path = []
            ...     current = item
            ...     while current:
            ...         name = project.Anthropology.GetName(current)
            ...         path.insert(0, name)
            ...         current = project.Anthropology.GetParent(current)
            ...     return " > ".join(path)
            >>> print(get_path(wedding))
            Marriage Customs > Wedding Ceremony

        Notes:
            - Returns None for top-level items
            - Parent is always an ICmAnthroItem or the AnthroList
            - Useful for navigation and breadcrumb displays

        See Also:
            GetSubitems, CreateSubitem, GetAll
        """
        item = self.__GetItemObject(item_or_hvo)

        if hasattr(item, 'Owner') and item.Owner:
            try:
                # Check if owner is an ICmAnthroItem (not the list)
                parent = ICmAnthroItem(item.Owner)
                return parent
            except Exception:
                # Owner is the AnthroListOA, so this is a top-level item
                return None
        return None

    # --- Text Linking Operations ---

    def GetTexts(self, item_or_hvo):
        """
        Get all texts linked to an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.

        Returns:
            list: List of IText objects linked to this item.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> texts = project.Anthropology.GetTexts(item)
            >>> print(f"Found {len(texts)} texts")
            Found 3 texts
            >>>
            >>> for text in texts:
            ...     name = text.Name.BestAnalysisAlternative.Text
            ...     print(f"  - {name}")
              - Wedding Story 1
              - Wedding Story 2
              - Marriage Interview

        Notes:
            - Returns empty list if no texts are linked
            - Texts can be linked to multiple anthropology items
            - Use AddText() to create links
            - Use RemoveText() to remove links

        See Also:
            AddText, RemoveText, GetTextCount, GetItemsForText
        """
        item = self.__GetItemObject(item_or_hvo)

        if hasattr(item, 'TextsRC'):
            return list(item.TextsRC)
        return []

    def AddText(self, item_or_hvo, text):
        """
        Link a text to an anthropology item.

        Creates a bidirectional link between the item and the text. The same
        text can be linked to multiple anthropology items.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.
            text: The IText object to link.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo or text is None.
            FP_ParameterError: If the item or text is invalid, or if the
                text is already linked to this item.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> text = project.Texts.Find("Wedding Story 1")
            >>>
            >>> # Link text to item
            >>> project.Anthropology.AddText(item, text)
            >>>
            >>> # Verify link
            >>> texts = project.Anthropology.GetTexts(item)
            >>> print(f"Item now has {len(texts)} text(s)")
            Item now has 1 text(s)

            >>> # Link same text to multiple items
            >>> wedding = project.Anthropology.Find("Wedding Ceremony")
            >>> project.Anthropology.AddText(wedding, text)

        Notes:
            - Text can be linked to multiple items
            - Item can have multiple texts
            - Link is bidirectional (stored in both objects)
            - Raises error if text is already linked to this item
            - Use RemoveText() to remove the link

        See Also:
            RemoveText, GetTexts, GetItemsForText
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not text:
            raise FP_NullParameterError()

        item = self.__GetItemObject(item_or_hvo)

        try:
            text_obj = IText(text)
        except Exception:
            raise FP_ParameterError("text must be a valid IText object")

        # Check if already linked
        if hasattr(item, 'TextsRC') and item.TextsRC.Contains(text_obj):
            raise FP_ParameterError("Text is already linked to this item")

        # Add the text to the item's collection
        if hasattr(item, 'TextsRC'):
            item.TextsRC.Add(text_obj)

    def RemoveText(self, item_or_hvo, text):
        """
        Remove a text link from an anthropology item.

        Removes the bidirectional link between the item and the text. The
        text itself is not deleted, only the link.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.
            text: The IText object to unlink.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo or text is None.
            FP_ParameterError: If the item or text is invalid, or if the
                text is not linked to this item.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> text = project.Texts.Find("Wedding Story 1")
            >>>
            >>> # Remove text link
            >>> project.Anthropology.RemoveText(item, text)
            >>>
            >>> # Verify removal
            >>> texts = project.Anthropology.GetTexts(item)
            >>> print(f"Item now has {len(texts)} text(s)")
            Item now has 0 text(s)

        Notes:
            - Only removes the link, not the text itself
            - Text may still be linked to other items
            - Raises error if text is not linked to this item

        See Also:
            AddText, GetTexts, GetItemsForText
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not text:
            raise FP_NullParameterError()

        item = self.__GetItemObject(item_or_hvo)

        try:
            text_obj = IText(text)
        except Exception:
            raise FP_ParameterError("text must be a valid IText object")

        # Check if linked
        if hasattr(item, 'TextsRC') and not item.TextsRC.Contains(text_obj):
            raise FP_ParameterError("Text is not linked to this item")

        # Remove the text from the item's collection
        if hasattr(item, 'TextsRC'):
            item.TextsRC.Remove(text_obj)

    def GetTextCount(self, item_or_hvo):
        """
        Get the count of texts linked to an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.

        Returns:
            int: The number of texts linked to this item.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> count = project.Anthropology.GetTextCount(item)
            >>> print(f"Item has {count} linked text(s)")
            Item has 3 linked text(s)

            >>> # Find items with linked texts
            >>> for item in project.Anthropology.GetAll():
            ...     count = project.Anthropology.GetTextCount(item)
            ...     if count > 0:
            ...         name = project.Anthropology.GetName(item)
            ...         print(f"{name}: {count} text(s)")
            Marriage Customs: 3 text(s)
            Kinship: 5 text(s)

        Notes:
            - Returns 0 if no texts are linked
            - More efficient than len(GetTexts()) for counting only

        See Also:
            GetTexts, AddText, RemoveText
        """
        item = self.__GetItemObject(item_or_hvo)

        if hasattr(item, 'TextsRC'):
            return item.TextsRC.Count
        return 0

    def GetItemsForText(self, text):
        """
        Get all anthropology items linked to a specific text.

        Searches through all anthropology items to find which ones are
        linked to the specified text.

        Args:
            text: The IText object to search for.

        Returns:
            list: List of ICmAnthroItem objects linked to this text.

        Raises:
            FP_NullParameterError: If text is None.

        Example:
            >>> text = project.Texts.Find("Wedding Story 1")
            >>> items = project.Anthropology.GetItemsForText(text)
            >>> print(f"Text is linked to {len(items)} item(s)")
            Text is linked to 2 item(s)
            >>>
            >>> for item in items:
            ...     name = project.Anthropology.GetName(item)
            ...     code = project.Anthropology.GetAnthroCode(item)
            ...     print(f"  {code}: {name}")
              586: Marriage Customs
              586.1: Wedding Ceremony

            >>> # Find texts not linked to any items
            >>> for text in project.Texts.GetAll():
            ...     items = project.Anthropology.GetItemsForText(text)
            ...     if not items:
            ...         name = text.Name.BestAnalysisAlternative.Text
            ...         print(f"Unlinked text: {name}")

        Notes:
            - Returns empty list if text is not linked to any items
            - Text can be linked to multiple items
            - Useful for finding cultural context of a text

        See Also:
            GetTexts, AddText, RemoveText
        """
        if not text:
            raise FP_NullParameterError()

        try:
            text_obj = IText(text)
        except Exception:
            raise FP_ParameterError("text must be a valid IText object")

        results = []

        # Search through all items
        for item in self.GetAll(flat=True):
            if hasattr(item, 'TextsRC') and item.TextsRC.Contains(text_obj):
                results.append(item)

        return results

    # --- Researcher/People Linking Operations ---

    def GetResearchers(self, item_or_hvo):
        """
        Get all researchers (people) linked to an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.

        Returns:
            list: List of ICmPerson objects linked to this item.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> researchers = project.Anthropology.GetResearchers(item)
            >>> for person in researchers:
            ...     name = person.Name.BestAnalysisAlternative.Text
            ...     print(f"Researcher: {name}")
            Researcher: John Smith
            Researcher: Jane Doe

        Notes:
            - Returns empty list if no researchers are linked
            - Researchers are ICmPerson objects from the project
            - Use AddResearcher() to create links

        See Also:
            AddResearcher, RemoveResearcher
        """
        item = self.__GetItemObject(item_or_hvo)

        if hasattr(item, 'ResearchersRC'):
            return list(item.ResearchersRC)
        return []

    def AddResearcher(self, item_or_hvo, person):
        """
        Link a researcher (person) to an anthropology item.

        Creates a link between the item and a person object, typically used
        to track which researchers are responsible for documenting particular
        cultural items.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.
            person: The ICmPerson object to link.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo or person is None.
            FP_ParameterError: If the item or person is invalid, or if the
                person is already linked to this item.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>>
            >>> # Get or create a person
            >>> # (assuming people are in project.lp.PeopleOA)
            >>> person = project.lp.PeopleOA.PossibilitiesOS[0]
            >>>
            >>> # Link person to item
            >>> project.Anthropology.AddResearcher(item, person)
            >>>
            >>> # Verify link
            >>> researchers = project.Anthropology.GetResearchers(item)
            >>> print(f"Item has {len(researchers)} researcher(s)")
            Item has 1 researcher(s)

        Notes:
            - Person must be a valid ICmPerson object
            - Same person can be linked to multiple items
            - Item can have multiple researchers
            - Raises error if person is already linked

        See Also:
            RemoveResearcher, GetResearchers
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not person:
            raise FP_NullParameterError()

        item = self.__GetItemObject(item_or_hvo)

        try:
            person_obj = ICmPerson(person)
        except Exception:
            raise FP_ParameterError("person must be a valid ICmPerson object")

        # Check if already linked
        if hasattr(item, 'ResearchersRC') and item.ResearchersRC.Contains(person_obj):
            raise FP_ParameterError("Person is already linked to this item")

        # Add the person to the item's collection
        if hasattr(item, 'ResearchersRC'):
            item.ResearchersRC.Add(person_obj)

    def RemoveResearcher(self, item_or_hvo, person):
        """
        Remove a researcher link from an anthropology item.

        Removes the link between the item and the person. The person object
        itself is not deleted, only the link.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.
            person: The ICmPerson object to unlink.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo or person is None.
            FP_ParameterError: If the item or person is invalid, or if the
                person is not linked to this item.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> person = project.lp.PeopleOA.PossibilitiesOS[0]
            >>>
            >>> # Remove person link
            >>> project.Anthropology.RemoveResearcher(item, person)
            >>>
            >>> # Verify removal
            >>> researchers = project.Anthropology.GetResearchers(item)
            >>> print(f"Item has {len(researchers)} researcher(s)")
            Item has 0 researcher(s)

        Notes:
            - Only removes the link, not the person object
            - Person may still be linked to other items
            - Raises error if person is not linked to this item

        See Also:
            AddResearcher, GetResearchers
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not person:
            raise FP_NullParameterError()

        item = self.__GetItemObject(item_or_hvo)

        try:
            person_obj = ICmPerson(person)
        except Exception:
            raise FP_ParameterError("person must be a valid ICmPerson object")

        # Check if linked
        if hasattr(item, 'ResearchersRC') and not item.ResearchersRC.Contains(person_obj):
            raise FP_ParameterError("Person is not linked to this item")

        # Remove the person from the item's collection
        if hasattr(item, 'ResearchersRC'):
            item.ResearchersRC.Remove(person_obj)

    def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
        """
        Duplicate an anthropology item, creating a new copy with a new GUID.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO to duplicate.
            insert_after (bool): If True (default), insert after the source item.
                                If False, insert at end of parent's subitems list.
            deep (bool): If True, also duplicate owned objects (subitems).
                        If False (default), only copy simple properties and references.

        Returns:
            ICmAnthroItem: The newly created duplicate item with a new GUID.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> # Shallow duplicate (no subitems)
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> dup = project.Anthropology.Duplicate(item)
            >>> print(f"Original: {project.Anthropology.GetGuid(item)}")
            >>> print(f"Duplicate: {project.Anthropology.GetGuid(dup)}")
            Original: 12345678-1234-1234-1234-123456789abc
            Duplicate: 87654321-4321-4321-4321-cba987654321

            >>> # Deep duplicate (includes all subitems)
            >>> deep_dup = project.Anthropology.Duplicate(item, deep=True)
            >>> print(f"Subitems: {len(project.Anthropology.GetSubitems(deep_dup))}")

        Notes:
            - Factory.Create() automatically generates a new GUID
            - insert_after=True preserves the original item's position
            - Simple properties copied: Name, Abbreviation, Description, AnthroCode
            - Reference properties copied: CategoryRA
            - Owned objects (deep=True): SubPossibilitiesOS (subitems)
            - TextsRC and ResearchersRC collections are NOT duplicated
            - DateCreated and DateModified are NOT copied (set to current time)

        See Also:
            Create, Delete, GetGuid, GetSubitems
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not item_or_hvo:
            raise FP_NullParameterError()

        # Get source item and parent
        source = self.__GetItemObject(item_or_hvo)

        # Determine parent (owner)
        owner = source.Owner

        # Create new item using factory (auto-generates new GUID)
        factory = self.project.project.ServiceLocator.GetService(ICmAnthroItemFactory)
        duplicate = factory.Create()

        # Determine insertion position and add to parent FIRST
        if hasattr(owner, 'SubPossibilitiesOS'):
            # Parent is another anthropology item
            if insert_after:
                source_index = owner.SubPossibilitiesOS.IndexOf(source)
                owner.SubPossibilitiesOS.Insert(source_index + 1, duplicate)
            else:
                owner.SubPossibilitiesOS.Add(duplicate)
        else:
            # Parent is the top-level list
            anthro_list = self.project.lp.AnthroListOA
            if anthro_list:
                if insert_after:
                    source_index = anthro_list.PossibilitiesOS.IndexOf(source)
                    anthro_list.PossibilitiesOS.Insert(source_index + 1, duplicate)
                else:
                    anthro_list.PossibilitiesOS.Add(duplicate)

        # Copy simple MultiString properties
        duplicate.Name.CopyAlternatives(source.Name)
        duplicate.Abbreviation.CopyAlternatives(source.Abbreviation)
        duplicate.Description.CopyAlternatives(source.Description)

        # Copy simple string property
        if hasattr(source, 'AnthroCode') and source.AnthroCode:
            duplicate.AnthroCode = source.AnthroCode

        # Copy Reference Atomic (RA) properties
        if hasattr(source, 'CategoryRA') and source.CategoryRA:
            duplicate.CategoryRA = source.CategoryRA

        # Handle owned objects if deep=True
        if deep:
            # Duplicate subitems
            if hasattr(source, 'SubPossibilitiesOS'):
                for subitem in source.SubPossibilitiesOS:
                    self.Duplicate(subitem, insert_after=False, deep=True)

        return duplicate

    # ========== SYNC INTEGRATION METHODS ==========

    def GetSyncableProperties(self, item):
        """Get syncable properties for cross-project synchronization."""
        if not item:
            raise FP_NullParameterError()

        anthro_item = self.__ResolveObject(item)
        wsHandle = self.project.project.DefaultAnalWs

        props = {}
        props['Name'] = ITsString(anthro_item.Name.get_String(wsHandle)).Text or ""
        props['Abbreviation'] = ITsString(anthro_item.Abbreviation.get_String(wsHandle)).Text or ""
        props['Description'] = ITsString(anthro_item.Description.get_String(wsHandle)).Text or ""

        if hasattr(anthro_item, 'AnthroCode') and anthro_item.AnthroCode:
            props['AnthroCode'] = anthro_item.AnthroCode
        else:
            props['AnthroCode'] = None

        if hasattr(anthro_item, 'CategoryRA') and anthro_item.CategoryRA:
            props['Category'] = str(anthro_item.CategoryRA.Guid)
        else:
            props['Category'] = None

        return props

    def CompareTo(self, item1, item2, ops1=None, ops2=None):
        """Compare two anthropology items and return detailed differences."""
        if ops1 is None:
            ops1 = self
        if ops2 is None:
            ops2 = self

        is_different = False
        differences = {'properties': {}}

        props1 = ops1.GetSyncableProperties(item1)
        props2 = ops2.GetSyncableProperties(item2)

        for key in set(props1.keys()) | set(props2.keys()):
            val1 = props1.get(key)
            val2 = props2.get(key)
            if val1 != val2:
                is_different = True
                differences['properties'][key] = {
                    'source': val1,
                    'target': val2,
                    'type': 'modified'
                }

        return is_different, differences

    # --- Metadata Operations ---

    def GetGuid(self, item_or_hvo):
        """
        Get the GUID (Globally Unique Identifier) of an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.

        Returns:
            System.Guid: The GUID of the item.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> guid = project.Anthropology.GetGuid(item)
            >>> print(f"GUID: {guid}")
            GUID: 12345678-1234-1234-1234-123456789abc

            >>> # Use GUID for stable cross-references
            >>> guid_str = str(guid)
            >>> # Store guid_str in external database...

        Notes:
            - GUID is unique across all FLEx databases
            - GUID is permanent and never changes
            - Use GUIDs for stable references in external systems
            - Returns System.Guid object (use str() to convert to string)

        See Also:
            GetDateCreated, GetDateModified
        """
        item = self.__GetItemObject(item_or_hvo)
        return item.Guid

    def GetDateCreated(self, item_or_hvo):
        """
        Get the creation date of an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.

        Returns:
            System.DateTime or None: The creation date, or None if not available.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> date = project.Anthropology.GetDateCreated(item)
            >>> if date:
            ...     print(f"Created: {date}")
            Created: 2024-01-15 10:30:00

            >>> # Find recently created items
            >>> from System import DateTime, TimeSpan
            >>> week_ago = DateTime.Now - TimeSpan.FromDays(7)
            >>> recent = []
            >>> for item in project.Anthropology.GetAll():
            ...     date = project.Anthropology.GetDateCreated(item)
            ...     if date and date > week_ago:
            ...         name = project.Anthropology.GetName(item)
            ...         recent.append(name)
            >>> print(f"Items created in last week: {recent}")

        Notes:
            - Returns System.DateTime object
            - May return None if date is not set or available
            - Date is set automatically when item is created
            - Dates are in UTC

        See Also:
            GetDateModified, GetGuid
        """
        item = self.__GetItemObject(item_or_hvo)

        if hasattr(item, 'DateCreated'):
            return item.DateCreated
        return None

    def GetDateModified(self, item_or_hvo):
        """
        Get the last modification date of an anthropology item.

        Args:
            item_or_hvo: The ICmAnthroItem object or HVO.

        Returns:
            System.DateTime or None: The modification date, or None if not available.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If the item is invalid.

        Example:
            >>> item = project.Anthropology.Find("Marriage Customs")
            >>> date = project.Anthropology.GetDateModified(item)
            >>> if date:
            ...     print(f"Last modified: {date}")
            Last modified: 2024-03-20 14:45:00

            >>> # Find recently modified items
            >>> from System import DateTime, TimeSpan
            >>> day_ago = DateTime.Now - TimeSpan.FromDays(1)
            >>> modified = []
            >>> for item in project.Anthropology.GetAll():
            ...     date = project.Anthropology.GetDateModified(item)
            ...     if date and date > day_ago:
            ...         name = project.Anthropology.GetName(item)
            ...         modified.append(name)
            >>> print(f"Modified today: {modified}")

        Notes:
            - Returns System.DateTime object
            - May return None if date is not set or available
            - Date is updated automatically when item is modified
            - Dates are in UTC
            - Tracks all modifications (name, description, links, etc.)

        See Also:
            GetDateCreated, GetGuid
        """
        item = self.__GetItemObject(item_or_hvo)

        if hasattr(item, 'DateModified'):
            return item.DateModified
        return None
