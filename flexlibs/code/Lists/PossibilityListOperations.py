#
#   PossibilityListOperations.py
#
#   Class: PossibilityListOperations
#          Generic possibility list operations for FieldWorks Language Explorer
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
    ICmPossibility,
    ICmPossibilityFactory,
    ICmPossibilityList,
    ICmPossibilityListFactory,
    ICmPossibilityRepository,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils
import System

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class PossibilityListOperations:
    """
    This class provides generic operations for managing possibility lists
    in a FieldWorks project.

    Possibility lists are hierarchical categorization systems used throughout
    FLEx for various purposes (e.g., semantic domains, parts of speech,
    grammatical categories, locations, people, text genres, etc.).

    This class provides generic operations that work with any possibility list,
    regardless of its specific purpose.

    This class should be accessed via FLExProject.PossibilityLists property.

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get all possibility lists in the project
        for poss_list in project.PossibilityLists.GetAllLists():
            name = project.PossibilityLists.GetListName(poss_list)
            print(f"List: {name}")

            # Get items in each list
            items = project.PossibilityLists.GetItems(poss_list, flat=True)
            print(f"  Contains {len(items)} items")

        # Work with a specific list
        genre_list = project.PossibilityLists.FindList("Text Genres")
        if genre_list:
            # Create a new genre
            narrative = project.PossibilityLists.CreateItem(
                genre_list, "Narrative", "en")

            # Create a sub-genre
            folktale = project.PossibilityLists.CreateItem(
                genre_list, "Folktale", "en", parent=narrative)

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize PossibilityListOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    # --- List Management ---

    def GetAllLists(self):
        """
        Get all possibility lists in the project.

        Returns:
            list: List of ICmPossibilityList objects representing all
                possibility lists in the project.

        Example:
            >>> for poss_list in project.PossibilityLists.GetAllLists():
            ...     name = project.PossibilityLists.GetListName(poss_list)
            ...     guid = project.PossibilityLists.GetListGuid(poss_list)
            ...     print(f"{name}: {guid}")
            Semantic Domains: 63403699-07c1-43f3-a47c-069d6e4316e5
            Parts of Speech: d1b6f191-6664-4f28-b2cc-5c37e24f69f1
            Text Genres: 3f99fdad-19c9-44e7-8d04-4b0f284137f9
            ...

        Notes:
            - Returns all possibility lists accessible in the LangProject
            - Each list serves a different purpose in the project
            - Standard FLEx projects have predefined lists (semantic domains, POS, etc.)
            - Custom lists can also be created for project-specific needs
            - Some lists may be empty if not used in the project

        See Also:
            FindList, CreateList, GetListName
        """
        lists = []

        # Access common possibility lists through LangProject
        lp = self.project.lp

        # Add all major possibility lists
        if lp.SemanticDomainListOA:
            lists.append(lp.SemanticDomainListOA)
        if lp.PartsOfSpeechOA:
            lists.append(lp.PartsOfSpeechOA)
        if lp.LocationsOA:
            lists.append(lp.LocationsOA)
        if lp.PeopleOA:
            lists.append(lp.PeopleOA)
        if lp.EducationOA:
            lists.append(lp.EducationOA)
        if lp.TranslationTagsOA:
            lists.append(lp.TranslationTagsOA)
        if lp.AnthroListOA:
            lists.append(lp.AnthroListOA)
        if lp.ConfidenceLevelsOA:
            lists.append(lp.ConfidenceLevelsOA)
        if lp.RestrictionsOA:
            lists.append(lp.RestrictionsOA)
        if lp.RolesOA:
            lists.append(lp.RolesOA)
        if lp.StatusOA:
            lists.append(lp.StatusOA)
        if lp.TimeOfDayOA:
            lists.append(lp.TimeOfDayOA)

        # Lexicon-specific lists
        if lp.LexDbOA:
            lexdb = lp.LexDbOA
            if lexdb.PublicationTypesOA:
                lists.append(lexdb.PublicationTypesOA)
            if lexdb.UsageTypesOA:
                lists.append(lexdb.UsageTypesOA)
            if lexdb.DomainTypesOA:
                lists.append(lexdb.DomainTypesOA)
            if lexdb.SenseTypesOA:
                lists.append(lexdb.SenseTypesOA)
            if lexdb.DialectLabelsOA:
                lists.append(lexdb.DialectLabelsOA)
            if lexdb.VariantEntryTypesOA:
                lists.append(lexdb.VariantEntryTypesOA)
            if lexdb.ComplexEntryTypesOA:
                lists.append(lexdb.ComplexEntryTypesOA)
            if lexdb.MorphTypesOA:
                lists.append(lexdb.MorphTypesOA)

        # Text/discourse lists
        if lp.TextMarkupTagsOA:
            lists.append(lp.TextMarkupTagsOA)
        if lp.GenreListOA:
            lists.append(lp.GenreListOA)

        return lists


    def CreateList(self, name, wsHandle=None):
        """
        Create a new possibility list.

        Args:
            name (str): The name of the new list.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ICmPossibilityList: The newly created list object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> # Create a custom possibility list
            >>> custom_list = project.PossibilityLists.CreateList("Custom Categories")
            >>> print(project.PossibilityLists.GetListName(custom_list))
            Custom Categories

        Warning:
            - Custom possibility lists may not integrate with all FLEx features
            - Consider using existing lists where possible
            - Created lists are not automatically linked to any field

        Notes:
            - Creates an independent possibility list
            - List is created but not automatically added to any field
            - To use the list, it must be associated with a custom field
            - Name is set in specified writing system

        See Also:
            DeleteList, GetAllLists, FindList
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        wsHandle = self.__WSHandle(wsHandle)

        # Create the new list using the factory
        factory = self.project.project.ServiceLocator.GetInstance(
            ICmPossibilityListFactory
        )
        new_list = factory.Create()

        # Set name
        mkstr = TsStringUtils.MakeString(name, wsHandle)
        new_list.Name.set_String(wsHandle, mkstr)

        return new_list


    def DeleteList(self, list_or_hvo):
        """
        Delete a possibility list.

        Args:
            list_or_hvo: The ICmPossibilityList object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If list_or_hvo is None.
            FP_ParameterError: If trying to delete a system list.

        Example:
            >>> # Delete a custom list
            >>> custom = project.PossibilityLists.FindList("Old Custom List")
            >>> if custom:
            ...     project.PossibilityLists.DeleteList(custom)

        Warning:
            - DO NOT delete standard FLEx lists (semantic domains, POS, etc.)
            - Deletion is permanent and cannot be undone
            - Deletes all items in the list recursively
            - Any fields referencing this list will be broken
            - Only delete custom lists that are no longer needed

        Notes:
            - Best practice: only delete custom lists you created
            - Deletion cascades to all items in the list
            - Use with extreme caution on shared projects

        See Also:
            CreateList, GetAllLists
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not list_or_hvo:
            raise FP_NullParameterError()

        poss_list = self.__ResolveList(list_or_hvo)

        # Note: Actual deletion of system lists is dangerous and not implemented
        # Only custom lists should be deleted, and they need special handling
        raise FP_ParameterError(
            "DeleteList: Direct deletion of possibility lists is not safe. "
            "Please delete items individually or consult FLEx documentation."
        )


    def FindList(self, name):
        """
        Find a possibility list by its name.

        Args:
            name (str): The list name to search for (case-insensitive).

        Returns:
            ICmPossibilityList or None: The list object if found, None otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> # Find the semantic domains list
            >>> sd_list = project.PossibilityLists.FindList("Semantic Domains")
            >>> if sd_list:
            ...     items = project.PossibilityLists.GetItems(sd_list, flat=True)
            ...     print(f"Found {len(items)} semantic domains")

            >>> # Find text genres list
            >>> genre_list = project.PossibilityLists.FindList("Text Genres")

        Notes:
            - Search is case-insensitive
            - Searches in default analysis writing system
            - Returns first match only
            - Returns None if not found (doesn't raise exception)
            - Common list names: "Semantic Domains", "Parts of Speech",
              "Text Genres", "Locations", "People", etc.

        See Also:
            GetAllLists, GetListName
        """
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            return None

        name_lower = name.strip().lower()
        wsHandle = self.project.project.DefaultAnalWs

        # Search through all lists
        for poss_list in self.GetAllLists():
            list_name = ITsString(poss_list.Name.get_String(wsHandle)).Text
            if list_name and list_name.lower() == name_lower:
                return poss_list

        return None


    def GetListName(self, list_or_hvo, wsHandle=None):
        """
        Get the name of a possibility list.

        Args:
            list_or_hvo: The ICmPossibilityList object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The list name, or empty string if not set.

        Raises:
            FP_NullParameterError: If list_or_hvo is None.

        Example:
            >>> lists = project.PossibilityLists.GetAllLists()
            >>> for poss_list in lists:
            ...     name = project.PossibilityLists.GetListName(poss_list)
            ...     print(f"List: {name}")
            List: Semantic Domains
            List: Parts of Speech
            List: Text Genres
            ...

        See Also:
            SetListName, FindList
        """
        if not list_or_hvo:
            raise FP_NullParameterError()

        poss_list = self.__ResolveList(list_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(poss_list.Name.get_String(wsHandle)).Text
        return name or ""


    def SetListName(self, list_or_hvo, name, wsHandle=None):
        """
        Set the name of a possibility list.

        Args:
            list_or_hvo: The ICmPossibilityList object or HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If list_or_hvo or name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> custom_list = project.PossibilityLists.CreateList("Temp")
            >>> project.PossibilityLists.SetListName(custom_list, "Custom List")

        Warning:
            - Renaming standard FLEx lists is not recommended
            - Only rename custom lists you created
            - Changes affect how the list appears throughout the UI

        See Also:
            GetListName, CreateList
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not list_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        poss_list = self.__ResolveList(list_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        poss_list.Name.set_String(wsHandle, mkstr)


    # --- Item Management ---

    def GetItems(self, list_or_hvo, flat=False):
        """
        Get items from a possibility list.

        Args:
            list_or_hvo: The ICmPossibilityList object or HVO.
            flat (bool): If True, returns a flat list of all items including
                nested items. If False, returns only top-level items.
                Defaults to False.

        Returns:
            list: List of ICmPossibility objects.

        Raises:
            FP_NullParameterError: If list_or_hvo is None.

        Example:
            >>> # Get top-level items only
            >>> genre_list = project.PossibilityLists.FindList("Text Genres")
            >>> top_items = project.PossibilityLists.GetItems(genre_list)
            >>> for item in top_items:
            ...     name = project.PossibilityLists.GetItemName(item)
            ...     print(name)
            Narrative
            Procedural
            Expository
            ...

            >>> # Get all items including nested ones
            >>> all_items = project.PossibilityLists.GetItems(genre_list, flat=True)
            >>> print(f"Total items: {len(all_items)}")
            Total items: 25

        Notes:
            - flat=False returns only top-level items (direct children of list)
            - flat=True recursively includes all nested subitems
            - Returns empty list if no items in the list
            - Use GetSubitems() to navigate hierarchy manually

        See Also:
            GetSubitems, CreateItem, FindItem
        """
        if not list_or_hvo:
            raise FP_NullParameterError()

        poss_list = self.__ResolveList(list_or_hvo)

        if not flat:
            return list(poss_list.PossibilitiesOS)
        else:
            return list(self.project.UnpackNestedPossibilityList(
                poss_list.PossibilitiesOS,
                ICmPossibility,
                flat
            ))


    def CreateItem(self, list_or_hvo, name, wsHandle=None, parent=None):
        """
        Create a new item in a possibility list.

        Args:
            list_or_hvo: The ICmPossibilityList object or HVO.
            name (str): The name of the new item.
            wsHandle: Optional writing system handle. Defaults to analysis WS.
            parent: Optional parent ICmPossibility object or HVO. If None,
                creates a top-level item. If provided, creates a subitem.

        Returns:
            ICmPossibility: The newly created item object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If list_or_hvo or name is None.
            FP_ParameterError: If name is empty or parent is invalid.

        Example:
            >>> # Create a top-level item
            >>> genre_list = project.PossibilityLists.FindList("Text Genres")
            >>> narrative = project.PossibilityLists.CreateItem(
            ...     genre_list, "Narrative", "en")
            >>> print(project.PossibilityLists.GetItemName(narrative))
            Narrative

            >>> # Create a subitem
            >>> folktale = project.PossibilityLists.CreateItem(
            ...     genre_list, "Folktale", "en", parent=narrative)
            >>> parent = project.PossibilityLists.GetParentItem(folktale)
            >>> print(project.PossibilityLists.GetItemName(parent))
            Narrative

        Notes:
            - Item is added to parent's subitems or to list's top level
            - Name is set in specified writing system
            - Use SetItemName() to add names in other writing systems
            - New items have no abbreviation by default

        See Also:
            DeleteItem, GetItems, FindItem, GetSubitems
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not list_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        poss_list = self.__ResolveList(list_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Create the new possibility using the factory
        factory = self.project.project.ServiceLocator.GetInstance(
            ICmPossibilityFactory
        )
        new_item = factory.Create()

        # Set name
        mkstr = TsStringUtils.MakeString(name, wsHandle)
        new_item.Name.set_String(wsHandle, mkstr)

        # Add to parent or top-level list
        if parent:
            parent_obj = self.__ResolveItem(parent)
            # Verify parent belongs to the same list
            parent_list = self.__GetListOwner(parent_obj)
            if parent_list.Guid != poss_list.Guid:
                raise FP_ParameterError(
                    "Parent item does not belong to the specified list"
                )
            parent_obj.SubPossibilitiesOS.Add(new_item)
        else:
            poss_list.PossibilitiesOS.Add(new_item)

        return new_item


    def DeleteItem(self, item_or_hvo):
        """
        Delete an item from a possibility list.

        Args:
            item_or_hvo: The ICmPossibility object or HVO to delete.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> # Delete an item
            >>> genre_list = project.PossibilityLists.FindList("Text Genres")
            >>> obsolete = project.PossibilityLists.FindItem(genre_list, "Obsolete")
            >>> if obsolete:
            ...     project.PossibilityLists.DeleteItem(obsolete)

        Warning:
            - Deletion is permanent and cannot be undone
            - Deletes all subitems recursively
            - Objects referencing this item will lose the reference
            - Consider removing references first
            - DO NOT delete standard list items unless you know what you're doing

        Notes:
            - Deletion cascades to all subitems
            - Item is removed from parent's SubPossibilitiesOS or list's PossibilitiesOS
            - References to this item are automatically cleaned up

        See Also:
            CreateItem, GetItems, FindItem
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not item_or_hvo:
            raise FP_NullParameterError()

        item = self.__ResolveItem(item_or_hvo)

        # Get the parent or owning list
        parent = self.GetParentItem(item)

        if parent:
            # Remove from parent's subitems
            parent.SubPossibilitiesOS.Remove(item)
        else:
            # Remove from top-level list
            owner = self.__GetListOwner(item)
            owner.PossibilitiesOS.Remove(item)


    def FindItem(self, list_or_hvo, name):
        """
        Find an item in a possibility list by name.

        Args:
            list_or_hvo: The ICmPossibilityList object or HVO to search in.
            name (str): The item name to search for (case-insensitive).

        Returns:
            ICmPossibility or None: The item object if found, None otherwise.

        Raises:
            FP_NullParameterError: If list_or_hvo or name is None.

        Example:
            >>> # Find an item
            >>> genre_list = project.PossibilityLists.FindList("Text Genres")
            >>> narrative = project.PossibilityLists.FindItem(genre_list, "Narrative")
            >>> if narrative:
            ...     subitems = project.PossibilityLists.GetSubitems(narrative)
            ...     print(f"Found {len(subitems)} sub-genres")

            >>> # Case-insensitive search
            >>> item = project.PossibilityLists.FindItem(genre_list, "narrative")
            >>> print(item is not None)
            True

        Notes:
            - Search is case-insensitive
            - Searches recursively through all items including nested ones
            - Searches in default analysis writing system
            - Returns first match only
            - Returns None if not found (doesn't raise exception)

        See Also:
            GetItems, CreateItem, GetItemName
        """
        if not list_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            return None

        name_lower = name.strip().lower()
        wsHandle = self.project.project.DefaultAnalWs

        # Search through all items (flat)
        for item in self.GetItems(list_or_hvo, flat=True):
            item_name = ITsString(item.Name.get_String(wsHandle)).Text
            if item_name and item_name.lower() == name_lower:
                return item

        return None


    def GetItemName(self, item_or_hvo, wsHandle=None):
        """
        Get the name of a possibility item.

        Args:
            item_or_hvo: The ICmPossibility object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The item name, or empty string if not set.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> genre_list = project.PossibilityLists.FindList("Text Genres")
            >>> items = project.PossibilityLists.GetItems(genre_list)
            >>> for item in items:
            ...     name = project.PossibilityLists.GetItemName(item)
            ...     print(f"Genre: {name}")
            Genre: Narrative
            Genre: Procedural
            Genre: Expository

            >>> # Get name in a specific writing system
            >>> name_fr = project.PossibilityLists.GetItemName(
            ...     item, project.WSHandle('fr'))

        See Also:
            SetItemName, GetItemAbbreviation, FindItem
        """
        if not item_or_hvo:
            raise FP_NullParameterError()

        item = self.__ResolveItem(item_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(item.Name.get_String(wsHandle)).Text
        return name or ""


    def SetItemName(self, item_or_hvo, name, wsHandle=None):
        """
        Set the name of a possibility item.

        Args:
            item_or_hvo: The ICmPossibility object or HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo or name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> genre_list = project.PossibilityLists.FindList("Text Genres")
            >>> item = project.PossibilityLists.FindItem(genre_list, "Old Name")
            >>> if item:
            ...     project.PossibilityLists.SetItemName(item, "New Name")

        See Also:
            GetItemName, SetItemAbbreviation
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not item_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        item = self.__ResolveItem(item_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        item.Name.set_String(wsHandle, mkstr)


    def GetItemAbbreviation(self, item_or_hvo, wsHandle=None):
        """
        Get the abbreviation of a possibility item.

        Args:
            item_or_hvo: The ICmPossibility object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The item abbreviation, or empty string if not set.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> pos_list = project.PossibilityLists.FindList("Parts of Speech")
            >>> noun = project.PossibilityLists.FindItem(pos_list, "Noun")
            >>> abbr = project.PossibilityLists.GetItemAbbreviation(noun)
            >>> print(abbr)
            N

        See Also:
            SetItemAbbreviation, GetItemName
        """
        if not item_or_hvo:
            raise FP_NullParameterError()

        item = self.__ResolveItem(item_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        abbr = ITsString(item.Abbreviation.get_String(wsHandle)).Text
        return abbr or ""


    def SetItemAbbreviation(self, item_or_hvo, abbr, wsHandle=None):
        """
        Set the abbreviation of a possibility item.

        Args:
            item_or_hvo: The ICmPossibility object or HVO.
            abbr (str): The new abbreviation.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo or abbr is None.

        Example:
            >>> pos_list = project.PossibilityLists.FindList("Parts of Speech")
            >>> noun = project.PossibilityLists.FindItem(pos_list, "Noun")
            >>> project.PossibilityLists.SetItemAbbreviation(noun, "N")

        Notes:
            - Abbreviation can be empty string if not needed
            - Abbreviations are often used in interlinear displays
            - Common in POS lists and semantic domain lists

        See Also:
            GetItemAbbreviation, SetItemName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not item_or_hvo:
            raise FP_NullParameterError()
        if abbr is None:
            raise FP_NullParameterError()

        item = self.__ResolveItem(item_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(abbr, wsHandle)
        item.Abbreviation.set_String(wsHandle, mkstr)


    def GetItemDescription(self, item_or_hvo, wsHandle=None):
        """
        Get the description of a possibility item.

        Args:
            item_or_hvo: The ICmPossibility object or HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The item description, or empty string if not set.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> sd_list = project.PossibilityLists.FindList("Semantic Domains")
            >>> walk = project.PossibilityLists.FindItem(sd_list, "Walk")
            >>> desc = project.PossibilityLists.GetItemDescription(walk)
            >>> print(desc)
            Use this domain for words related to walking.

        See Also:
            SetItemDescription, GetItemName
        """
        if not item_or_hvo:
            raise FP_NullParameterError()

        item = self.__ResolveItem(item_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Description is a MultiString
        desc = ITsString(item.Description.get_String(wsHandle)).Text
        return desc or ""


    def SetItemDescription(self, item_or_hvo, description, wsHandle=None):
        """
        Set the description of a possibility item.

        Args:
            item_or_hvo: The ICmPossibility object or HVO.
            description (str): The new description text.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo or description is None.

        Example:
            >>> genre_list = project.PossibilityLists.FindList("Text Genres")
            >>> narrative = project.PossibilityLists.FindItem(genre_list, "Narrative")
            >>> project.PossibilityLists.SetItemDescription(
            ...     narrative, "Stories that tell about events in sequence")

        See Also:
            GetItemDescription, SetItemName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not item_or_hvo:
            raise FP_NullParameterError()
        if description is None:
            raise FP_NullParameterError()

        item = self.__ResolveItem(item_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Description is a MultiString
        item.Description.set_String(wsHandle, description)


    # --- Hierarchy Operations ---

    def GetSubitems(self, item_or_hvo):
        """
        Get all direct child subitems of a possibility item.

        Args:
            item_or_hvo: The ICmPossibility object or HVO.

        Returns:
            list: List of ICmPossibility child objects (empty list if none).

        Raises:
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> # Get subitems
            >>> pos_list = project.PossibilityLists.FindList("Parts of Speech")
            >>> noun = project.PossibilityLists.FindItem(pos_list, "Noun")
            >>> subcats = project.PossibilityLists.GetSubitems(noun)
            >>> for subcat in subcats:
            ...     name = project.PossibilityLists.GetItemName(subcat)
            ...     print(f"  {name}")
              Proper Noun
              Common Noun
              Count Noun

        Notes:
            - Returns direct children only (not recursive)
            - Returns empty list if item has no subitems
            - Subitems are ordered as they appear in the list
            - For all descendants, use GetItems(list, flat=True)

        See Also:
            GetParentItem, GetItems, CreateItem
        """
        if not item_or_hvo:
            raise FP_NullParameterError()

        item = self.__ResolveItem(item_or_hvo)

        return list(item.SubPossibilitiesOS)


    def GetParentItem(self, item_or_hvo):
        """
        Get the parent item of a possibility item.

        Args:
            item_or_hvo: The ICmPossibility object or HVO.

        Returns:
            ICmPossibility or None: The parent item, or None if top-level.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> # Get parent
            >>> pos_list = project.PossibilityLists.FindList("Parts of Speech")
            >>> proper_noun = project.PossibilityLists.FindItem(
            ...     pos_list, "Proper Noun")
            >>> parent = project.PossibilityLists.GetParentItem(proper_noun)
            >>> if parent:
            ...     name = project.PossibilityLists.GetItemName(parent)
            ...     print(f"Parent: {name}")
            Parent: Noun

            >>> # Top-level items have no parent
            >>> noun = project.PossibilityLists.FindItem(pos_list, "Noun")
            >>> parent = project.PossibilityLists.GetParentItem(noun)
            >>> print(parent)
            None

        Notes:
            - Returns None for top-level items
            - Parent is determined by ownership hierarchy
            - Parent-child relationships form a tree structure

        See Also:
            GetSubitems, GetDepth, MoveItem
        """
        if not item_or_hvo:
            raise FP_NullParameterError()

        item = self.__ResolveItem(item_or_hvo)
        owner = item.Owner

        # Check if owner is a possibility (subitem) or a list (top-level)
        if owner and hasattr(owner, 'ClassName'):
            if owner.ClassName == 'CmPossibility':
                return ICmPossibility(owner)

        return None


    def MoveItem(self, item_or_hvo, new_parent_or_hvo=None):
        """
        Move an item to a different parent or to top level.

        Args:
            item_or_hvo: The ICmPossibility object or HVO to move.
            new_parent_or_hvo: The new parent ICmPossibility object or HVO.
                If None, moves item to top level of its list.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.
            FP_ParameterError: If new parent is in a different list or
                if trying to make an item its own descendant.

        Example:
            >>> # Move item to a different parent
            >>> pos_list = project.PossibilityLists.FindList("Parts of Speech")
            >>> common_noun = project.PossibilityLists.FindItem(
            ...     pos_list, "Common Noun")
            >>> noun = project.PossibilityLists.FindItem(pos_list, "Noun")
            >>> project.PossibilityLists.MoveItem(common_noun, noun)

            >>> # Move item to top level
            >>> project.PossibilityLists.MoveItem(common_noun, None)

        Warning:
            - Cannot move item to its own descendant (would create cycle)
            - Cannot move item between different lists
            - Moving changes the item's hierarchical position

        Notes:
            - Item is removed from old location and added to new location
            - All subitems move with the item
            - Item remains in the same list

        See Also:
            GetParentItem, GetSubitems, CreateItem
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not item_or_hvo:
            raise FP_NullParameterError()

        item = self.__ResolveItem(item_or_hvo)
        item_list = self.__GetListOwner(item)

        # Resolve new parent if provided
        if new_parent_or_hvo:
            new_parent = self.__ResolveItem(new_parent_or_hvo)
            new_parent_list = self.__GetListOwner(new_parent)

            # Verify both items are in the same list
            if item_list.Guid != new_parent_list.Guid:
                raise FP_ParameterError(
                    "Cannot move item to a different list"
                )

            # Verify not moving to own descendant
            if self.__IsDescendant(new_parent, item):
                raise FP_ParameterError(
                    "Cannot move item to its own descendant"
                )
        else:
            new_parent = None

        # Remove from current location
        old_parent = self.GetParentItem(item)
        if old_parent:
            old_parent.SubPossibilitiesOS.Remove(item)
        else:
            item_list.PossibilitiesOS.Remove(item)

        # Add to new location
        if new_parent:
            new_parent.SubPossibilitiesOS.Add(item)
        else:
            item_list.PossibilitiesOS.Add(item)


    def GetDepth(self, item_or_hvo):
        """
        Get the depth of an item in the hierarchy.

        Args:
            item_or_hvo: The ICmPossibility object or HVO.

        Returns:
            int: The depth (0 for top-level, 1 for first level subitems, etc.).

        Raises:
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> # Top-level item
            >>> pos_list = project.PossibilityLists.FindList("Parts of Speech")
            >>> noun = project.PossibilityLists.FindItem(pos_list, "Noun")
            >>> depth = project.PossibilityLists.GetDepth(noun)
            >>> print(depth)
            0

            >>> # Second-level item
            >>> proper = project.PossibilityLists.FindItem(pos_list, "Proper Noun")
            >>> depth = project.PossibilityLists.GetDepth(proper)
            >>> print(depth)
            1

        Notes:
            - Depth is 0-based (top-level = 0)
            - Calculated by traversing parent chain
            - Useful for indentation in tree displays
            - Efficient operation (doesn't scan entire tree)

        See Also:
            GetParentItem, GetSubitems
        """
        if not item_or_hvo:
            raise FP_NullParameterError()

        item = self.__ResolveItem(item_or_hvo)

        # Count parents by traversing ownership chain
        depth = 0
        current = item
        while True:
            parent = self.GetParentItem(current)
            if parent is None:
                break
            depth += 1
            current = parent

        return depth


    # --- Utilities ---

    def GetListGuid(self, list_or_hvo):
        """
        Get the GUID of a possibility list.

        Args:
            list_or_hvo: The ICmPossibilityList object or HVO.

        Returns:
            System.Guid: The list's globally unique identifier.

        Raises:
            FP_NullParameterError: If list_or_hvo is None.

        Example:
            >>> genre_list = project.PossibilityLists.FindList("Text Genres")
            >>> guid = project.PossibilityLists.GetListGuid(genre_list)
            >>> print(guid)
            3f99fdad-19c9-44e7-8d04-4b0f284137f9

        Notes:
            - GUID is stable across sessions
            - GUID is unique across all projects
            - Use GUID for persistent references
            - GUID can be used with project.Object(guid) to retrieve the list

        See Also:
            GetItemGuid, FindList
        """
        if not list_or_hvo:
            raise FP_NullParameterError()

        poss_list = self.__ResolveList(list_or_hvo)
        return poss_list.Guid


    def GetItemGuid(self, item_or_hvo):
        """
        Get the GUID of a possibility item.

        Args:
            item_or_hvo: The ICmPossibility object or HVO.

        Returns:
            System.Guid: The item's globally unique identifier.

        Raises:
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> pos_list = project.PossibilityLists.FindList("Parts of Speech")
            >>> noun = project.PossibilityLists.FindItem(pos_list, "Noun")
            >>> guid = project.PossibilityLists.GetItemGuid(noun)
            >>> print(guid)
            a23b6fcc-654c-4983-a11c-5e4e15e1f6e9

            >>> # Use GUID to retrieve item later
            >>> retrieved = project.Object(guid)
            >>> name = project.PossibilityLists.GetItemName(retrieved)
            >>> print(name)
            Noun

        Notes:
            - GUID is stable across sessions
            - GUID is unique across all projects
            - Use GUID for persistent references
            - GUID can be used with project.Object(guid) to retrieve the item

        See Also:
            GetListGuid, FindItem
        """
        if not item_or_hvo:
            raise FP_NullParameterError()

        item = self.__ResolveItem(item_or_hvo)
        return item.Guid


    def GetItemHvo(self, item):
        """
        Get the HVO (handle value) of a possibility item.

        Args:
            item: The ICmPossibility object.

        Returns:
            int: The item's HVO.

        Raises:
            FP_NullParameterError: If item is None.

        Example:
            >>> pos_list = project.PossibilityLists.FindList("Parts of Speech")
            >>> noun = project.PossibilityLists.FindItem(pos_list, "Noun")
            >>> hvo = project.PossibilityLists.GetItemHvo(noun)
            >>> print(hvo)
            123456

        Notes:
            - HVO is only valid for current session
            - HVO changes between sessions
            - Use GUID for persistent references
            - HVO can be used with project.Object(hvo) to retrieve the item

        See Also:
            GetItemGuid, GetListGuid
        """
        if not item:
            raise FP_NullParameterError()

        return item.Hvo


    def GetListHvo(self, poss_list):
        """
        Get the HVO (handle value) of a possibility list.

        Args:
            poss_list: The ICmPossibilityList object.

        Returns:
            int: The list's HVO.

        Raises:
            FP_NullParameterError: If poss_list is None.

        Example:
            >>> genre_list = project.PossibilityLists.FindList("Text Genres")
            >>> hvo = project.PossibilityLists.GetListHvo(genre_list)
            >>> print(hvo)
            789012

        Notes:
            - HVO is only valid for current session
            - HVO changes between sessions
            - Use GUID for persistent references
            - HVO can be used with project.Object(hvo) to retrieve the list

        See Also:
            GetListGuid, GetItemHvo
        """
        if not poss_list:
            raise FP_NullParameterError()

        return poss_list.Hvo


    # --- Private Helper Methods ---

    def __ResolveList(self, list_or_hvo):
        """
        Resolve HVO or object to ICmPossibilityList.

        Args:
            list_or_hvo: Either an ICmPossibilityList object or an HVO (int).

        Returns:
            ICmPossibilityList: The resolved list object.

        Raises:
            FP_ParameterError: If HVO doesn't refer to a possibility list.
        """
        if isinstance(list_or_hvo, int):
            obj = self.project.Object(list_or_hvo)
            if not isinstance(obj, ICmPossibilityList):
                raise FP_ParameterError(
                    "HVO does not refer to a possibility list"
                )
            return obj
        return list_or_hvo


    def __ResolveItem(self, item_or_hvo):
        """
        Resolve HVO or object to ICmPossibility.

        Args:
            item_or_hvo: Either an ICmPossibility object or an HVO (int).

        Returns:
            ICmPossibility: The resolved item object.

        Raises:
            FP_ParameterError: If HVO doesn't refer to a possibility item.
        """
        if isinstance(item_or_hvo, int):
            obj = self.project.Object(item_or_hvo)
            if not isinstance(obj, ICmPossibility):
                raise FP_ParameterError(
                    "HVO does not refer to a possibility item"
                )
            return obj
        return item_or_hvo


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
        return self.project._FLExProject__WSHandle(
            wsHandle,
            self.project.project.DefaultAnalWs
        )


    def __GetListOwner(self, item):
        """
        Get the possibility list that owns an item.

        Args:
            item: The ICmPossibility object.

        Returns:
            ICmPossibilityList: The owning list.
        """
        # Traverse up the ownership chain to find the list
        current = item
        while current:
            owner = current.Owner
            if isinstance(owner, ICmPossibilityList):
                return owner
            elif hasattr(owner, 'ClassName') and owner.ClassName == 'CmPossibility':
                current = ICmPossibility(owner)
            else:
                break
        return None


    def __IsDescendant(self, potential_descendant, potential_ancestor):
        """
        Check if an item is a descendant of another item.

        Args:
            potential_descendant: The ICmPossibility that might be a descendant.
            potential_ancestor: The ICmPossibility that might be an ancestor.

        Returns:
            bool: True if potential_descendant is a descendant of potential_ancestor.
        """
        if potential_descendant.Guid == potential_ancestor.Guid:
            return True

        parent = self.GetParentItem(potential_descendant)
        while parent:
            if parent.Guid == potential_ancestor.Guid:
                return True
            parent = self.GetParentItem(parent)

        return False
