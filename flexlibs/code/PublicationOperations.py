#
#   PublicationOperations.py
#
#   Class: PublicationOperations
#          Publication and publishing workflow operations for FieldWorks Language
#          Explorer projects via SIL Language and Culture Model (LCM) API.
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
    ICmPossibilityRepository,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils
from System import DateTime

# Import flexlibs exceptions
from .FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class PublicationOperations:
    """
    This class provides operations for managing publications and publishing
    workflows in a FieldWorks project.

    Publications in FLEx define output formats for dictionary and text publishing.
    They specify page layouts, formatting options, divisions (e.g., main entries,
    minor entries), header/footer settings, and default publication types. These
    are used when exporting dictionaries or texts to various formats.

    This class should be accessed via FLExProject.Publications property.

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get all publications
        for pub in project.Publications.GetAll():
            name = project.Publications.GetName(pub)
            is_default = project.Publications.GetIsDefault(pub)
            print(f"{name} (Default: {is_default})")

        # Create a new publication
        pub = project.Publications.Create("Web Dictionary", "en")

        # Set page layout and formatting
        project.Publications.SetPageWidth(pub, 8.5)
        project.Publications.SetPageHeight(pub, 11.0)
        project.Publications.SetDescription(pub,
            "Dictionary layout for web publication")

        # Set as default publication
        project.Publications.SetIsDefault(pub, True)

        # Find a publication by name
        main_pub = project.Publications.Find("Main Dictionary")
        if main_pub:
            width = project.Publications.GetPageWidth(main_pub)
            height = project.Publications.GetPageHeight(main_pub)
            print(f"Page size: {width} x {height} inches")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize PublicationOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    # --- Core CRUD Operations ---

    def GetAll(self, flat=True):
        """
        Get all publications in the project.

        Args:
            flat (bool): If True, returns a flat list of all publications including
                sub-publications. If False, returns only top-level publications.
                Defaults to True.

        Returns:
            list: List of ICmPossibility objects representing publications.

        Example:
            >>> # Get all publications
            >>> for pub in project.Publications.GetAll():
            ...     name = project.Publications.GetName(pub)
            ...     desc = project.Publications.GetDescription(pub)
            ...     is_default = project.Publications.GetIsDefault(pub)
            ...     default_str = " [DEFAULT]" if is_default else ""
            ...     print(f"{name}{default_str}: {desc}")
            Main Dictionary [DEFAULT]: Primary publication for dictionary
            Root-based Dictionary: Dictionary organized by roots
            Thematic Dictionary: Dictionary organized by semantic domains

            >>> # Get only top-level publications
            >>> top_pubs = project.Publications.GetAll(flat=False)
            >>> for pub in top_pubs:
            ...     name = project.Publications.GetName(pub)
            ...     subs = project.Publications.GetSubPublications(pub)
            ...     print(f"{name} ({len(subs)} variants)")

        Notes:
            - Returns empty list if no publications exist
            - Publications are ordered by creation order
            - Each publication can have page layout and formatting settings
            - Default publication is used when no specific publication is selected
            - Publications are stored as ICmPossibility objects

        See Also:
            Find, Create, Exists
        """
        pub_list = self.project.lexDB.PublicationTypesOA
        if not pub_list:
            return []

        return list(self.project.UnpackNestedPossibilityList(
            pub_list.PossibilitiesOS,
            ICmPossibility,
            flat
        ))


    def Create(self, name, wsHandle=None):
        """
        Create a new publication.

        Args:
            name (str): The name of the publication (e.g., "Main Dictionary").
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ICmPossibility: The newly created publication object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If name is None.
            FP_ParameterError: If name is empty or publication already exists.

        Example:
            >>> # Create a simple publication
            >>> pub = project.Publications.Create("Web Dictionary")
            >>> print(project.Publications.GetName(pub))
            Web Dictionary

            >>> # Create with specific writing system
            >>> pub = project.Publications.Create("Diccionario Web",
            ...                                    project.WSHandle('es'))

            >>> # Create and configure
            >>> pub = project.Publications.Create("Print Dictionary")
            >>> project.Publications.SetPageWidth(pub, 8.5)
            >>> project.Publications.SetPageHeight(pub, 11.0)
            >>> project.Publications.SetDescription(pub,
            ...     "Standard letter-size print layout")

        Notes:
            - Name should be descriptive of the publication purpose
            - Name must be unique within the project
            - Publication is created but not set as default
            - Use Set* methods to configure page layout and formatting
            - GUID is auto-generated
            - DateCreated is set automatically

        See Also:
            Delete, Find, Exists, SetIsDefault
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        # Check if publication already exists
        if self.Exists(name):
            raise FP_ParameterError(f"Publication '{name}' already exists")

        wsHandle = self.__WSHandle(wsHandle)

        # Get the publication types list
        pub_list = self.project.lexDB.PublicationTypesOA
        if not pub_list:
            raise FP_ParameterError("Publication types list not found in project")

        # Create the new publication using the factory
        factory = self.project.project.ServiceLocator.GetInstance(
            ICmPossibilityFactory
        )
        new_pub = factory.Create()

        # Set name
        mkstr_name = TsStringUtils.MakeString(name, wsHandle)
        new_pub.Name.set_String(wsHandle, mkstr_name)

        # Set creation date
        new_pub.DateCreated = DateTime.Now

        # Add to publications list
        pub_list.PossibilitiesOS.Add(new_pub)

        return new_pub


    def Delete(self, publication_or_hvo):
        """
        Delete a publication from the project.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If publication_or_hvo is None.
            FP_ParameterError: If trying to delete the default publication.

        Example:
            >>> # Delete a publication
            >>> pub = project.Publications.Find("Old Publication")
            >>> if pub and not project.Publications.GetIsDefault(pub):
            ...     project.Publications.Delete(pub)

            >>> # Delete by HVO
            >>> project.Publications.Delete(12345)

        Warning:
            - This is a destructive operation
            - Deletion is permanent and cannot be undone
            - Cannot delete the default publication
            - Any references to this publication will be removed
            - Lexical entries using this publication may lose formatting info

        Notes:
            - Check if publication is default before deleting
            - Set a different default before deleting current default
            - Sub-publications are deleted recursively
            - Use with caution on shared projects

        See Also:
            Create, GetIsDefault, SetIsDefault
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)

        # Check if this is the default publication
        if self.GetIsDefault(publication):
            raise FP_ParameterError(
                "Cannot delete the default publication. "
                "Set a different default first."
            )

        # Get the parent or top-level list
        parent = self.GetParent(publication)

        if parent:
            # Remove from parent's sub-publications
            parent.SubPossibilitiesOS.Remove(publication)
        else:
            # Remove from top-level list
            pub_list = self.project.lexDB.PublicationTypesOA
            if pub_list:
                pub_list.PossibilitiesOS.Remove(publication)


    def Find(self, name):
        """
        Find a publication by its name.

        Args:
            name (str): The publication name to search for (case-sensitive).

        Returns:
            ICmPossibility or None: The publication object if found, None otherwise.

        Raises:
            FP_NullParameterError: If name is None.

        Example:
            >>> # Find by name
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> if pub:
            ...     width = project.Publications.GetPageWidth(pub)
            ...     height = project.Publications.GetPageHeight(pub)
            ...     print(f"Page size: {width}\" x {height}\"")
            Page size: 8.5" x 11.0"

            >>> # Check if publication exists before using
            >>> pub = project.Publications.Find("Web Dictionary")
            >>> if pub:
            ...     project.Publications.SetPageWidth(pub, 10)
            ... else:
            ...     pub = project.Publications.Create("Web Dictionary")

        Notes:
            - Search is case-sensitive
            - Searches in default analysis writing system
            - Returns first match only
            - Returns None if not found (doesn't raise exception)
            - Searches both top-level and nested publications

        See Also:
            Exists, GetAll, GetName
        """
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            return None

        name_search = name.strip()
        wsHandle = self.project.project.DefaultAnalWs

        # Search through all publications
        for pub in self.GetAll(flat=True):
            pub_name = ITsString(pub.Name.get_String(wsHandle)).Text
            if pub_name and pub_name == name_search:
                return pub

        return None


    def Exists(self, name):
        """
        Check if a publication with the given name exists.

        Args:
            name (str): The publication name to check.

        Returns:
            bool: True if publication exists, False otherwise.

        Example:
            >>> if project.Publications.Exists("Main Dictionary"):
            ...     print("Main Dictionary publication exists")
            Main Dictionary publication exists

            >>> if not project.Publications.Exists("New Publication"):
            ...     pub = project.Publications.Create("New Publication")

        Notes:
            - Search is case-sensitive
            - Returns False for empty or whitespace-only names
            - More efficient than Find() when you only need existence check
            - Use Find() if you need the actual publication object

        See Also:
            Find, Create
        """
        if not name or (isinstance(name, str) and not name.strip()):
            return False

        return self.Find(name) is not None


    # --- Name and Description Operations ---

    def GetName(self, publication_or_hvo, wsHandle=None):
        """
        Get the name of a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The publication name, or empty string if not set.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> name = project.Publications.GetName(pub)
            >>> print(name)
            Main Dictionary

            >>> # Get name in specific writing system
            >>> name_es = project.Publications.GetName(pub,
            ...                                        project.WSHandle('es'))

        Notes:
            - Returns empty string if name not set in specified writing system
            - Names can be set in multiple writing systems
            - Default writing system is the default analysis WS

        See Also:
            SetName, GetDescription
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        name = ITsString(publication.Name.get_String(wsHandle)).Text
        return name or ""


    def SetName(self, publication_or_hvo, name, wsHandle=None):
        """
        Set the name of a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.
            name (str): The new name.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If publication_or_hvo or name is None.
            FP_ParameterError: If name is empty.

        Example:
            >>> pub = project.Publications.Find("Old Name")
            >>> project.Publications.SetName(pub, "New Name")
            >>> print(project.Publications.GetName(pub))
            New Name

            >>> # Set name in multiple writing systems
            >>> project.Publications.SetName(pub, "Dictionary", "en")
            >>> project.Publications.SetName(pub, "Diccionario", "es")

        Notes:
            - Empty string is not allowed
            - Name is stored in the specified writing system
            - Does not affect other writing systems
            - Use different writing systems for multilingual names

        See Also:
            GetName, SetDescription
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if publication_or_hvo is None:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Name cannot be empty")

        publication = self.__ResolveObject(publication_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        publication.Name.set_String(wsHandle, mkstr)

        # Update modification date
        publication.DateModified = DateTime.Now


    def GetDescription(self, publication_or_hvo, wsHandle=None):
        """
        Get the description of a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The publication description, or empty string if not set.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> desc = project.Publications.GetDescription(pub)
            >>> print(desc)
            Primary publication format for comprehensive dictionary.
            Letter-size pages, two-column layout.

        Notes:
            - Returns empty string if description not set
            - Description can be lengthy (multiple paragraphs)
            - Useful for documenting publication purpose and settings
            - Can be multilingual (different description per writing system)

        See Also:
            SetDescription, GetName
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        if hasattr(publication, 'Description'):
            desc = ITsString(publication.Description.get_String(wsHandle)).Text
            return desc or ""

        return ""


    def SetDescription(self, publication_or_hvo, description, wsHandle=None):
        """
        Set the description of a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.
            description (str): The new description text.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If publication_or_hvo or description is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> desc = ("Primary publication format.\\n"
            ...         "Letter-size pages, two-column layout.\\n"
            ...         "Includes main entries and subentries.")
            >>> project.Publications.SetDescription(pub, desc)

            >>> # Clear description
            >>> project.Publications.SetDescription(pub, "")

        Notes:
            - Empty string is allowed (clears the description)
            - Description is stored in the specified writing system
            - Use newlines for formatting if needed
            - Good place for publication settings documentation

        See Also:
            GetDescription, SetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if publication_or_hvo is None:
            raise FP_NullParameterError()
        if description is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        if hasattr(publication, 'Description'):
            mkstr = TsStringUtils.MakeString(description, wsHandle)
            publication.Description.set_String(wsHandle, mkstr)

            # Update modification date
            publication.DateModified = DateTime.Now


    # --- Publishing Properties ---

    def GetPageLayout(self, publication_or_hvo, wsHandle=None):
        """
        Get the page layout description for a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: Page layout description, or empty string if not set.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> layout = project.Publications.GetPageLayout(pub)
            >>> print(layout)
            Two-column layout with headers and footers

        Notes:
            - Returns empty string if page layout not set
            - Layout description is free-form text
            - Can describe columns, margins, orientation, etc.
            - Different from page dimensions (width/height)

        See Also:
            SetPageLayout, GetPageWidth, GetPageHeight
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Use Abbreviation field for page layout description
        if hasattr(publication, 'Abbreviation'):
            layout = ITsString(publication.Abbreviation.get_String(wsHandle)).Text
            return layout or ""

        return ""


    def SetPageLayout(self, publication_or_hvo, layout, wsHandle=None):
        """
        Set the page layout description for a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.
            layout (str): Page layout description.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If publication_or_hvo or layout is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> project.Publications.SetPageLayout(pub,
            ...     "Two-column layout with running headers")

            >>> # Clear layout description
            >>> project.Publications.SetPageLayout(pub, "")

        Notes:
            - Empty string is allowed (clears the layout description)
            - Layout description is stored in the specified writing system
            - Use to describe columns, margins, orientation, etc.
            - Actual page dimensions set with SetPageWidth/SetPageHeight

        See Also:
            GetPageLayout, SetPageWidth, SetPageHeight
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if publication_or_hvo is None:
            raise FP_NullParameterError()
        if layout is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        if hasattr(publication, 'Abbreviation'):
            mkstr = TsStringUtils.MakeString(layout, wsHandle)
            publication.Abbreviation.set_String(wsHandle, mkstr)

            # Update modification date
            publication.DateModified = DateTime.Now


    def GetIsDefault(self, publication_or_hvo):
        """
        Check if a publication is the default publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.

        Returns:
            bool: True if this is the default publication, False otherwise.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> for pub in project.Publications.GetAll():
            ...     name = project.Publications.GetName(pub)
            ...     is_default = project.Publications.GetIsDefault(pub)
            ...     default_marker = " [DEFAULT]" if is_default else ""
            ...     print(f"{name}{default_marker}")
            Main Dictionary [DEFAULT]
            Root-based Dictionary
            Thematic Dictionary

            >>> # Find the default publication
            >>> default_pub = None
            >>> for pub in project.Publications.GetAll():
            ...     if project.Publications.GetIsDefault(pub):
            ...         default_pub = pub
            ...         break

        Notes:
            - Only one publication can be the default
            - Default publication is used when no specific publication is selected
            - Returns False if publication is not default
            - If no default is set, all publications return False

        See Also:
            SetIsDefault, Find
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)

        # Check if this publication is the default
        # Default is typically the first publication or marked by IsDefault property
        pub_list = self.project.lexDB.PublicationTypesOA
        if pub_list and pub_list.PossibilitiesOS.Count > 0:
            # The default publication is typically the first one
            default_pub = pub_list.PossibilitiesOS[0]
            return publication.Hvo == default_pub.Hvo

        return False


    def SetIsDefault(self, publication_or_hvo, is_default):
        """
        Set whether a publication is the default publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.
            is_default (bool): True to make this the default, False otherwise.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If publication_or_hvo or is_default is None.

        Example:
            >>> # Set a publication as default
            >>> pub = project.Publications.Find("Web Dictionary")
            >>> project.Publications.SetIsDefault(pub, True)

            >>> # Remove default status (sets first publication as default)
            >>> project.Publications.SetIsDefault(pub, False)

        Notes:
            - Only one publication can be default at a time
            - Setting a publication as default makes it the first in the list
            - If is_default is False, publication is moved from first position
            - Default publication is used when no specific publication is selected

        See Also:
            GetIsDefault, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if publication_or_hvo is None:
            raise FP_NullParameterError()
        if is_default is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)

        pub_list = self.project.lexDB.PublicationTypesOA
        if not pub_list:
            return

        # To make a publication default, move it to the first position
        if is_default:
            # Remove from current position
            if publication in pub_list.PossibilitiesOS:
                pub_list.PossibilitiesOS.Remove(publication)
            # Insert at first position
            pub_list.PossibilitiesOS.Insert(0, publication)
        else:
            # If removing default status, move to end
            if publication in pub_list.PossibilitiesOS:
                current_index = pub_list.PossibilitiesOS.IndexOf(publication)
                if current_index == 0:  # Is currently default
                    pub_list.PossibilitiesOS.Remove(publication)
                    pub_list.PossibilitiesOS.Add(publication)


    # --- Formatting Properties ---

    def GetPageHeight(self, publication_or_hvo):
        """
        Get the page height for a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.

        Returns:
            float or None: Page height in inches, or None if not set.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> height = project.Publications.GetPageHeight(pub)
            >>> if height:
            ...     print(f"Page height: {height} inches")
            Page height: 11.0 inches

            >>> # Get both dimensions
            >>> width = project.Publications.GetPageWidth(pub)
            >>> height = project.Publications.GetPageHeight(pub)
            >>> if width and height:
            ...     print(f"Page size: {width}\" x {height}\"")

        Notes:
            - Returns None if page height is not set
            - Height is in inches (standard US measurement)
            - Common sizes: 11.0 (Letter), 11.69 (A4), 14.0 (Legal)
            - Use with GetPageWidth() to get full page dimensions

        See Also:
            SetPageHeight, GetPageWidth
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)

        # Store in SortKey2 field (encoded as integer, divide by 1000 for inches)
        if hasattr(publication, 'SortKey2') and publication.SortKey2 != 0:
            return float(publication.SortKey2) / 1000.0

        return None


    def SetPageHeight(self, publication_or_hvo, height):
        """
        Set the page height for a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.
            height (float): Page height in inches.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If publication_or_hvo or height is None.
            FP_ParameterError: If height is not positive.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> # Set letter-size height
            >>> project.Publications.SetPageHeight(pub, 11.0)

            >>> # Set A4 height
            >>> project.Publications.SetPageHeight(pub, 11.69)

            >>> # Set legal-size height
            >>> project.Publications.SetPageHeight(pub, 14.0)

        Notes:
            - Height must be positive
            - Height is stored in inches
            - Common heights: 11.0 (Letter), 11.69 (A4), 14.0 (Legal)
            - Set both width and height for complete page dimensions

        See Also:
            GetPageHeight, SetPageWidth
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if publication_or_hvo is None:
            raise FP_NullParameterError()
        if height is None:
            raise FP_NullParameterError()

        try:
            h = float(height)
        except (TypeError, ValueError):
            raise FP_ParameterError("Height must be numeric")

        if h <= 0:
            raise FP_ParameterError("Height must be positive")

        publication = self.__ResolveObject(publication_or_hvo)

        # Store in SortKey2 field (multiply by 1000 to store as integer)
        if hasattr(publication, 'SortKey2'):
            publication.SortKey2 = int(h * 1000)

            # Update modification date
            publication.DateModified = DateTime.Now


    def GetPageWidth(self, publication_or_hvo):
        """
        Get the page width for a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.

        Returns:
            float or None: Page width in inches, or None if not set.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> width = project.Publications.GetPageWidth(pub)
            >>> if width:
            ...     print(f"Page width: {width} inches")
            Page width: 8.5 inches

            >>> # Check if dimensions are set
            >>> width = project.Publications.GetPageWidth(pub)
            >>> height = project.Publications.GetPageHeight(pub)
            >>> if width and height:
            ...     aspect = width / height
            ...     print(f"Aspect ratio: {aspect:.2f}")

        Notes:
            - Returns None if page width is not set
            - Width is in inches (standard US measurement)
            - Common sizes: 8.5 (Letter), 8.27 (A4), 8.5 (Legal)
            - Use with GetPageHeight() to get full page dimensions

        See Also:
            SetPageWidth, GetPageHeight
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)

        # Store in SortKey field (encoded as integer, divide by 1000 for inches)
        if hasattr(publication, 'SortKey') and publication.SortKey != 0:
            return float(publication.SortKey) / 1000.0

        return None


    def SetPageWidth(self, publication_or_hvo, width):
        """
        Set the page width for a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.
            width (float): Page width in inches.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If publication_or_hvo or width is None.
            FP_ParameterError: If width is not positive.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> # Set letter-size width
            >>> project.Publications.SetPageWidth(pub, 8.5)

            >>> # Set A4 width
            >>> project.Publications.SetPageWidth(pub, 8.27)

            >>> # Set custom width
            >>> project.Publications.SetPageWidth(pub, 7.0)

        Notes:
            - Width must be positive
            - Width is stored in inches
            - Common widths: 8.5 (Letter/Legal), 8.27 (A4)
            - Set both width and height for complete page dimensions

        See Also:
            GetPageWidth, SetPageHeight
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if publication_or_hvo is None:
            raise FP_NullParameterError()
        if width is None:
            raise FP_NullParameterError()

        try:
            w = float(width)
        except (TypeError, ValueError):
            raise FP_ParameterError("Width must be numeric")

        if w <= 0:
            raise FP_ParameterError("Width must be positive")

        publication = self.__ResolveObject(publication_or_hvo)

        # Store in SortKey field (multiply by 1000 to store as integer)
        if hasattr(publication, 'SortKey'):
            publication.SortKey = int(w * 1000)

            # Update modification date
            publication.DateModified = DateTime.Now


    # --- Divisions and Structure ---

    def GetDivisions(self, publication_or_hvo):
        """
        Get the publication divisions (e.g., main entries, minor entries).

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.

        Returns:
            list: List of ICmPossibility objects representing divisions.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> divisions = project.Publications.GetDivisions(pub)
            >>> for div in divisions:
            ...     name = ITsString(div.Name.BestAnalysisAlternative).Text
            ...     print(f"Division: {name}")
            Division: Main Entries
            Division: Minor Entries
            Division: Back Matter

        Notes:
            - Returns empty list if no divisions
            - Divisions organize content into sections
            - Common divisions: Main Entries, Minor Entries, Subentries
            - Divisions are represented as sub-possibilities

        See Also:
            AddDivision, GetSubPublications
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)

        # Divisions are stored as sub-possibilities
        if hasattr(publication, 'SubPossibilitiesOS'):
            return list(publication.SubPossibilitiesOS)

        return []


    def AddDivision(self, publication_or_hvo, division_name, wsHandle=None):
        """
        Add a division to a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.
            division_name (str): Name of the division (e.g., "Main Entries").
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            ICmPossibility: The newly created division object.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If publication_or_hvo or division_name is None.
            FP_ParameterError: If division_name is empty.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> # Add standard divisions
            >>> main = project.Publications.AddDivision(pub, "Main Entries")
            >>> minor = project.Publications.AddDivision(pub, "Minor Entries")
            >>> back = project.Publications.AddDivision(pub, "Back Matter")

            >>> # Verify divisions were added
            >>> divisions = project.Publications.GetDivisions(pub)
            >>> print(f"Publication has {len(divisions)} divisions")

        Notes:
            - Division name should be descriptive
            - Common divisions: Main Entries, Minor Entries, Subentries
            - Divisions organize publication content
            - Multiple divisions can be added to one publication

        See Also:
            GetDivisions, Create
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if publication_or_hvo is None:
            raise FP_NullParameterError()
        if division_name is None:
            raise FP_NullParameterError()

        if not division_name or not division_name.strip():
            raise FP_ParameterError("Division name cannot be empty")

        publication = self.__ResolveObject(publication_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Create the new division using the factory
        factory = self.project.project.ServiceLocator.GetInstance(
            ICmPossibilityFactory
        )
        new_division = factory.Create()

        # Set name
        mkstr_name = TsStringUtils.MakeString(division_name, wsHandle)
        new_division.Name.set_String(wsHandle, mkstr_name)

        # Set creation date
        new_division.DateCreated = DateTime.Now

        # Add to publication's sub-possibilities
        if hasattr(publication, 'SubPossibilitiesOS'):
            publication.SubPossibilitiesOS.Add(new_division)

        return new_division


    def GetHeaderFooter(self, publication_or_hvo, wsHandle=None):
        """
        Get the header/footer configuration for a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.
            wsHandle: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: Header/footer configuration text, or empty string if not set.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> header = project.Publications.GetHeaderFooter(pub)
            >>> print(header)
            Header: Dictionary title | Page number
            Footer: Copyright notice

        Notes:
            - Returns empty string if header/footer not set
            - Can describe header and footer content
            - Free-form text description
            - Actual header/footer rendering depends on export format

        See Also:
            GetPageLayout, GetDescription
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Use Comment field for header/footer information
        if hasattr(publication, 'Comment'):
            header = ITsString(publication.Comment.get_String(wsHandle)).Text
            return header or ""

        return ""


    # --- Hierarchical Operations ---

    def GetSubPublications(self, publication_or_hvo):
        """
        Get all sub-publications of a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.

        Returns:
            list: List of ICmPossibility sub-publication objects.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> subs = project.Publications.GetSubPublications(pub)
            >>> for sub in subs:
            ...     name = project.Publications.GetName(sub)
            ...     print(f"Variant: {name}")

        Notes:
            - Returns empty list if no sub-publications
            - Sub-publications can represent variants or divisions
            - Different from GetDivisions() which is content-based

        See Also:
            GetParent, GetDivisions
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)

        if hasattr(publication, 'SubPossibilitiesOS'):
            return list(publication.SubPossibilitiesOS)

        return []


    def GetParent(self, publication_or_hvo):
        """
        Get the parent publication of a sub-publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.

        Returns:
            ICmPossibility or None: The parent publication, or None if top-level.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> pub = project.Publications.Find("Web Dictionary Variant")
            >>> parent = project.Publications.GetParent(pub)
            >>> if parent:
            ...     parent_name = project.Publications.GetName(parent)
            ...     print(f"Parent: {parent_name}")

        Notes:
            - Returns None for top-level publications
            - Parent is determined by ownership hierarchy
            - Use for building breadcrumb navigation

        See Also:
            GetSubPublications
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)
        owner = publication.Owner

        # Check if owner is a publication (sub-publication) or the list (top-level)
        if owner and hasattr(owner, 'ClassName'):
            if owner.ClassName == 'CmPossibility':
                return ICmPossibility(owner)

        return None


    # --- Metadata Operations ---

    def GetGuid(self, publication_or_hvo):
        """
        Get the GUID (Globally Unique Identifier) of a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.

        Returns:
            System.Guid: The publication's GUID.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> guid = project.Publications.GetGuid(pub)
            >>> print(guid)
            a1b2c3d4-e5f6-7890-abcd-ef1234567890

            >>> # Use GUID to retrieve publication later
            >>> pub2 = project.Object(guid)
            >>> print(project.Publications.GetName(pub2))
            Main Dictionary

        Notes:
            - GUIDs are unique across all FLEx projects
            - GUIDs are persistent (don't change)
            - Useful for linking publications across projects
            - Can be used with FLExProject.Object() to retrieve publication

        See Also:
            FLExProject.Object
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)
        return publication.Guid


    def GetDateCreated(self, publication_or_hvo):
        """
        Get the creation date of a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.

        Returns:
            System.DateTime or None: The creation date/time, or None if not set.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> date = project.Publications.GetDateCreated(pub)
            >>> if date:
            ...     print(f"Created: {date}")
            Created: 11/23/2025 10:30:45 AM

            >>> # Sort publications by creation date
            >>> pubs = project.Publications.GetAll()
            >>> sorted_pubs = sorted(pubs,
            ...     key=lambda p: project.Publications.GetDateCreated(p) or DateTime.MinValue)

        Notes:
            - DateCreated is set automatically when publication is created
            - Returns System.DateTime object
            - Can be None for publications without creation date
            - Use for tracking when publications were added to project

        See Also:
            GetDateModified, Create
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)

        if hasattr(publication, 'DateCreated'):
            return publication.DateCreated

        return None


    def GetDateModified(self, publication_or_hvo):
        """
        Get the last modification date of a publication.

        Args:
            publication_or_hvo: Either an ICmPossibility publication object or its HVO.

        Returns:
            System.DateTime or None: The modification date/time, or None if not set.

        Raises:
            FP_NullParameterError: If publication_or_hvo is None.

        Example:
            >>> pub = project.Publications.Find("Main Dictionary")
            >>> modified = project.Publications.GetDateModified(pub)
            >>> if modified:
            ...     print(f"Last modified: {modified}")
            Last modified: 11/23/2025 2:15:30 PM

            >>> # Find recently modified publications
            >>> from System import DateTime
            >>> one_week_ago = DateTime.Now.AddDays(-7)
            >>> pubs = project.Publications.GetAll()
            >>> recent = [p for p in pubs
            ...     if project.Publications.GetDateModified(p) and
            ...        project.Publications.GetDateModified(p) > one_week_ago]

        Notes:
            - DateModified is updated when properties change
            - Returns System.DateTime object
            - May be None if publication has never been modified
            - Useful for tracking publication updates

        See Also:
            GetDateCreated, SetName, SetDescription
        """
        if publication_or_hvo is None:
            raise FP_NullParameterError()

        publication = self.__ResolveObject(publication_or_hvo)

        if hasattr(publication, 'DateModified'):
            return publication.DateModified

        return None


    # --- Private Helper Methods ---

    def __ResolveObject(self, publication_or_hvo):
        """
        Resolve HVO or object to ICmPossibility.

        Args:
            publication_or_hvo: Either an ICmPossibility object or an HVO (int).

        Returns:
            ICmPossibility: The resolved publication object.

        Raises:
            FP_ParameterError: If HVO doesn't refer to a publication.
        """
        if isinstance(publication_or_hvo, int):
            obj = self.project.Object(publication_or_hvo)
            if not isinstance(obj, ICmPossibility):
                raise FP_ParameterError("HVO does not refer to a publication")
            return obj
        return publication_or_hvo


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
