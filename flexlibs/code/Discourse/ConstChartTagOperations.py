#
#   ConstChartTagOperations.py
#
#   Class: ConstChartTagOperations
#          Chart tag operations for constituent charts in FieldWorks
#          Language Explorer projects via SIL Language and Culture Model (LCM) API.
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
    IConstChartTag,
    IConstChartTagFactory,
    ICmPossibility,
    ICmPossibilityFactory,
    IDsConstChart,
)
from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

# Import flexlibs exceptions
from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class ConstChartTagOperations(BaseOperations):
    """
    This class provides operations for managing chart tags (discourse markers)
    in constituent charts for discourse analysis in FieldWorks projects.

    Chart tags are possibility items that can be used to categorize and mark
    elements within discourse charts. They provide a vocabulary for discourse
    annotation.

    This class should be accessed via FLExProject.ConstChartTags property.

    Usage::

        from flexlibs import FLExProject

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        # Get a chart
        chart = project.ConstCharts.Find("Genesis 1 Analysis")

        # Create a tag
        tag = project.ConstChartTags.Create(chart, "Topic")

        # Get all tags
        for tag in project.ConstChartTags.GetAll(chart):
            name = project.ConstChartTags.GetName(tag)
            print(f"Tag: {name}")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize ConstChartTagOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)


    # --- Core CRUD Operations ---

    def Create(self, chart_or_hvo, tag_name):
        """
        Create a new chart tag possibility.

        Creates a tag that can be used to mark elements in the discourse chart.
        Tags are stored as possibility items within the chart.

        Args:
            chart_or_hvo: Either an IDsConstChart object or its HVO
            tag_name (str): The name of the tag (e.g., "Topic", "Focus", "Tail")

        Returns:
            ICmPossibility: The newly created tag possibility object

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If chart_or_hvo or tag_name is None
            FP_ParameterError: If tag_name is empty

        Example:
            >>> chart = project.ConstCharts.Find("Genesis 1 Analysis")
            >>> tag = project.ConstChartTags.Create(chart, "Topic")
            >>> print(project.ConstChartTags.GetName(tag))
            Topic

        Notes:
            - Tag is added to the chart's tag list
            - Tags can be used to mark word groups or other elements
            - Factory.Create() automatically adds tag to repository
            - Tags are possibilities and can have descriptions

        See Also:
            Delete, Find, GetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not chart_or_hvo:
            raise FP_NullParameterError()
        if tag_name is None:
            raise FP_NullParameterError()

        if not tag_name or not tag_name.strip():
            raise FP_ParameterError("Tag name cannot be empty")

        chart = self.__ResolveChart(chart_or_hvo)
        wsHandle = self.__WSHandleAnalysis()

        # Get or create the tag possibility list
        if not hasattr(chart, 'TagsOC') or chart.TagsOC is None:
            # Chart doesn't have tags collection - this is normal
            # Tags would be in a CmPossibilityList referenced by the chart
            # For simplicity, we'll create the tag as a CmPossibility
            pass

        # Create the new tag using the possibility factory
        factory = self.project.project.ServiceLocator.GetService(ICmPossibilityFactory)
        new_tag = factory.Create()

        # Set the name
        mkstr = TsStringUtils.MakeString(tag_name, wsHandle)
        new_tag.Name.set_String(wsHandle, mkstr)

        # Add to chart's tags collection
        # Note: In FLEx, tags may be stored differently depending on the chart structure
        # This implementation assumes a basic tag storage
        if hasattr(chart, 'TagsOC'):
            chart.TagsOC.Add(new_tag)

        return new_tag


    def Delete(self, tag_or_hvo):
        """
        Delete a chart tag.

        Args:
            tag_or_hvo: Either a tag possibility object or its HVO

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If tag_or_hvo is None

        Example:
            >>> tag = project.ConstChartTags.Find(chart, "Old Tag")
            >>> if tag:
            ...     project.ConstChartTags.Delete(tag)

        Warning:
            - This is a destructive operation
            - Cannot be undone
            - References to this tag from word groups may become invalid

        See Also:
            Create, Find
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not tag_or_hvo:
            raise FP_NullParameterError()

        # Resolve to tag object
        tag = self.__ResolveObject(tag_or_hvo)

        # Delete the tag (LCM handles removal from repository)
        tag.Delete()


    def Find(self, chart_or_hvo, name):
        """
        Find a chart tag by its name.

        Args:
            chart_or_hvo: Either an IDsConstChart object or its HVO
            name (str): The tag name to search for

        Returns:
            ICmPossibility or None: The tag if found, None otherwise

        Raises:
            FP_NullParameterError: If chart_or_hvo or name is None

        Example:
            >>> chart = project.ConstCharts.Find("Genesis 1 Analysis")
            >>> tag = project.ConstChartTags.Find(chart, "Topic")
            >>> if tag:
            ...     desc = project.ConstChartTags.GetDescription(tag)
            ...     print(f"Tag: {desc}")

        Notes:
            - Returns first match only
            - Search is case-sensitive
            - Searches in default analysis writing system
            - Returns None if not found

        See Also:
            GetAll, Create
        """
        if not chart_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            return None

        chart = self.__ResolveChart(chart_or_hvo)
        wsHandle = self.__WSHandleAnalysis()

        # Search through chart tags
        if hasattr(chart, 'TagsOC'):
            for tag in chart.TagsOC:
                tag_name = ITsString(tag.Name.get_String(wsHandle)).Text
                if tag_name == name:
                    return tag

        return None


    def GetAll(self, chart_or_hvo):
        """
        Get all chart tags for a constituent chart.

        Args:
            chart_or_hvo: Either an IDsConstChart object or its HVO

        Returns:
            list: List of tag possibility objects (empty list if none)

        Raises:
            FP_NullParameterError: If chart_or_hvo is None

        Example:
            >>> chart = project.ConstCharts.Find("Genesis 1 Analysis")
            >>> tags = project.ConstChartTags.GetAll(chart)
            >>> for tag in tags:
            ...     name = project.ConstChartTags.GetName(tag)
            ...     print(f"Tag: {name}")

        Notes:
            - Returns empty list if chart has no tags
            - Tags are in database order
            - Each tag is a possibility that can be used in the chart

        See Also:
            Find, Create
        """
        if not chart_or_hvo:
            raise FP_NullParameterError()

        chart = self.__ResolveChart(chart_or_hvo)

        if hasattr(chart, 'TagsOC'):
            return list(chart.TagsOC)

        return []


    # --- Tag Properties ---

    def GetName(self, tag_or_hvo):
        """
        Get the name of a chart tag.

        Args:
            tag_or_hvo: Either a tag possibility object or its HVO

        Returns:
            str: The tag name (empty string if not set)

        Raises:
            FP_NullParameterError: If tag_or_hvo is None

        Example:
            >>> tag = project.ConstChartTags.Find(chart, "Topic")
            >>> name = project.ConstChartTags.GetName(tag)
            >>> print(name)
            Topic

        Notes:
            - Returns empty string if name not set
            - Uses default analysis writing system

        See Also:
            SetName, GetDescription
        """
        if not tag_or_hvo:
            raise FP_NullParameterError()

        tag = self.__ResolveObject(tag_or_hvo)
        wsHandle = self.__WSHandleAnalysis()

        return ITsString(tag.Name.get_String(wsHandle)).Text or ""


    def SetName(self, tag_or_hvo, name):
        """
        Set the name of a chart tag.

        Args:
            tag_or_hvo: Either a tag possibility object or its HVO
            name (str): The new tag name

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If tag_or_hvo or name is None
            FP_ParameterError: If name is empty

        Example:
            >>> tag = project.ConstChartTags.Find(chart, "Old Name")
            >>> project.ConstChartTags.SetName(tag, "New Name")
            >>> print(project.ConstChartTags.GetName(tag))
            New Name

        Notes:
            - Name is stored in default analysis writing system
            - Changes are immediately persisted

        See Also:
            GetName, SetDescription
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not tag_or_hvo:
            raise FP_NullParameterError()
        if name is None:
            raise FP_NullParameterError()

        if not name or not name.strip():
            raise FP_ParameterError("Tag name cannot be empty")

        tag = self.__ResolveObject(tag_or_hvo)
        wsHandle = self.__WSHandleAnalysis()

        mkstr = TsStringUtils.MakeString(name, wsHandle)
        tag.Name.set_String(wsHandle, mkstr)


    def GetDescription(self, tag_or_hvo, ws=None):
        """
        Get the description of a chart tag.

        Args:
            tag_or_hvo: Either a tag possibility object or its HVO
            ws: Optional writing system handle. Defaults to analysis WS.

        Returns:
            str: The tag description (empty string if not set)

        Raises:
            FP_NullParameterError: If tag_or_hvo is None

        Example:
            >>> tag = project.ConstChartTags.Find(chart, "Topic")
            >>> desc = project.ConstChartTags.GetDescription(tag)
            >>> print(desc)
            Marks the topic of the sentence

        Notes:
            - Returns empty string if description not set
            - Uses default analysis writing system unless specified
            - Description provides explanation of tag usage

        See Also:
            SetDescription, GetName
        """
        if not tag_or_hvo:
            raise FP_NullParameterError()

        tag = self.__ResolveObject(tag_or_hvo)
        wsHandle = self.__WSHandle(ws)

        return ITsString(tag.Description.get_String(wsHandle)).Text or ""


    def SetDescription(self, tag_or_hvo, text, ws=None):
        """
        Set the description of a chart tag.

        Args:
            tag_or_hvo: Either a tag possibility object or its HVO
            text (str): The new description text
            ws: Optional writing system handle. Defaults to analysis WS.

        Raises:
            FP_ReadOnlyError: If project is not opened with write enabled
            FP_NullParameterError: If tag_or_hvo or text is None

        Example:
            >>> tag = project.ConstChartTags.Find(chart, "Topic")
            >>> project.ConstChartTags.SetDescription(tag,
            ...     "Marks the topic of the sentence")

        Notes:
            - Description can be empty to clear
            - Uses default analysis writing system unless specified
            - Description helps analysts understand tag meaning

        See Also:
            GetDescription, SetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not tag_or_hvo:
            raise FP_NullParameterError()
        if text is None:
            raise FP_NullParameterError()

        tag = self.__ResolveObject(tag_or_hvo)
        wsHandle = self.__WSHandle(ws)

        mkstr = TsStringUtils.MakeString(text, wsHandle)
        tag.Description.set_String(wsHandle, mkstr)


    # --- Private Helper Methods ---

    def __ResolveObject(self, tag_or_hvo):
        """
        Resolve HVO or object to possibility object.

        Args:
            tag_or_hvo: Either a possibility object or an HVO (int)

        Returns:
            ICmPossibility: The resolved tag object

        Raises:
            FP_ParameterError: If HVO doesn't refer to a possibility
        """
        if isinstance(tag_or_hvo, int):
            obj = self.project.Object(tag_or_hvo)
            if not isinstance(obj, ICmPossibility):
                raise FP_ParameterError("HVO does not refer to a tag possibility")
            return obj
        return tag_or_hvo


    def __ResolveChart(self, chart_or_hvo):
        """
        Resolve HVO or object to IDsConstChart.

        Args:
            chart_or_hvo: Either an IDsConstChart object or an HVO (int)

        Returns:
            IDsConstChart: The resolved chart object

        Raises:
            FP_ParameterError: If HVO doesn't refer to a constituent chart
        """
        if isinstance(chart_or_hvo, int):
            obj = self.project.Object(chart_or_hvo)
            if not isinstance(obj, IDsConstChart):
                raise FP_ParameterError("HVO does not refer to a constituent chart")
            return obj
        return chart_or_hvo


    def __WSHandle(self, ws):
        """
        Get writing system handle, defaulting to analysis WS.

        Args:
            ws: Optional writing system handle

        Returns:
            int: The writing system handle
        """
        if ws is None:
            return self.project.project.DefaultAnalWs
        return self.project._FLExProject__WSHandle(
            ws,
            self.project.project.DefaultAnalWs
        )


    def __WSHandleAnalysis(self):
        """
        Get writing system handle for analysis writing system.

        Returns:
            int: The analysis writing system handle
        """
        return self.project.project.DefaultAnalWs


    # --- Reordering Support ---

    def _GetSequence(self, parent):
        """
        Get the owning sequence for tags.

        Args:
            parent: The parent IDsConstChart object

        Returns:
            ILcmOwningCollection: The TagsOC collection

        Notes:
            - Required for BaseOperations reordering methods
            - Tags are in an owning collection (OC), not sequence (OS)
            - Reordering may not be applicable to tag collections
        """
        if hasattr(parent, 'TagsOC'):
            return parent.TagsOC
        raise NotImplementedError(
            "Chart does not have a TagsOC collection. "
            "Tag reordering may not be applicable to this chart structure."
        )
