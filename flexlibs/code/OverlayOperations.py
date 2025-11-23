#
#   OverlayOperations.py
#
#   Class: OverlayOperations
#          Discourse chart overlay and layer management operations for FieldWorks
#          Language Explorer projects via SIL Language and Culture Model (LCM) API.
#
#   Copyright 2025
#

import logging
logger = logging.getLogger(__name__)

import clr
clr.AddReference("System")
import System

from SIL.LCModel import (
    IConstChart,
    IConstChartRow,
    IDsConstChart,
    IDsConstChartFactory,
    ICmPossibility,
    ICmPossibilityFactory,
)

from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

from .FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)


class OverlayOperations:
    """
    Discourse chart overlay and layer management operations for FLEx projects.

    This class provides methods for creating and managing overlays (layers) in
    discourse constituent charts. Overlays allow multiple levels of analysis to
    be displayed in the same chart, with each overlay representing a different
    analytical perspective or feature set.

    Overlays can be toggled on/off for visibility and have customizable display
    order. They are used to organize complex chart analyses by separating different
    aspects of discourse structure into manageable layers.

    Note:
        Overlays are specific to constituent charts (IConstChart). They provide
        a way to layer multiple analytical perspectives in a single chart view.

    Usage::

        from flexlibs import FLExProject, DiscourseOperations, OverlayOperations

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        discourse_ops = DiscourseOperations(project)
        overlay_ops = OverlayOperations(project)

        # Get a chart
        text = list(project.Texts.GetAll())[0]
        charts = list(discourse_ops.GetAllCharts(text))
        chart = charts[0]

        # Get all overlays for the chart
        overlays = list(overlay_ops.GetAll(chart))
        print(f"Chart has {len(overlays)} overlays")

        # Create a new overlay
        overlay = overlay_ops.Create(chart, "Participants")
        overlay_ops.SetDescription(overlay, "Track participant chains")

        # Configure visibility and display order
        overlay_ops.SetVisible(overlay, True)
        overlay_ops.SetDisplayOrder(overlay, 1)

        # Get visible overlays
        visible = list(overlay_ops.GetVisibleOverlays(chart))
        print(f"Chart has {len(visible)} visible overlays")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize OverlayOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        self.project = project


    # --- Helper Methods ---

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


    def __GetChartObject(self, chart_or_hvo):
        """
        Resolve chart_or_hvo to IConstChart object.

        Args:
            chart_or_hvo: Either an IConstChart object or its HVO (integer).

        Returns:
            IConstChart: The chart object.

        Raises:
            FP_NullParameterError: If chart_or_hvo is None.
            FP_ParameterError: If the object doesn't exist or isn't a valid chart.
        """
        if not chart_or_hvo:
            raise FP_NullParameterError()

        if isinstance(chart_or_hvo, int):
            try:
                return IConstChart(self.project.Object(chart_or_hvo))
            except (AttributeError, System.InvalidCastException) as e:
                raise FP_ParameterError(f"Invalid chart HVO: {chart_or_hvo}")
        return chart_or_hvo


    def __GetOverlayObject(self, overlay_or_hvo):
        """
        Resolve overlay_or_hvo to overlay object.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer).

        Returns:
            Overlay object (typically IDsConstChart or ICmPossibility).

        Raises:
            FP_NullParameterError: If overlay_or_hvo is None.
            FP_ParameterError: If the object doesn't exist or isn't a valid overlay.
        """
        if not overlay_or_hvo:
            raise FP_NullParameterError()

        if isinstance(overlay_or_hvo, int):
            try:
                obj = self.project.Object(overlay_or_hvo)
                # Try to cast to the appropriate overlay type
                try:
                    return IDsConstChart(obj)
                except (AttributeError, System.InvalidCastException) as e:
                    try:
                        return ICmPossibility(obj)
                    except (AttributeError, System.InvalidCastException) as e:
                        return obj
            except (AttributeError, System.InvalidCastException) as e:
                raise FP_ParameterError(f"Invalid overlay HVO: {overlay_or_hvo}")
        return overlay_or_hvo


    # --- Core Operations ---

    def GetAll(self, chart_or_hvo):
        """
        Get all overlays (layers) for a discourse chart.

        Retrieves all overlay layers defined for the specified chart, including
        both visible and hidden overlays.

        Args:
            chart_or_hvo: Either an IConstChart object or its HVO (integer identifier).

        Yields:
            Overlay objects: Each overlay/layer associated with the chart.

        Raises:
            FP_NullParameterError: If chart_or_hvo is None.
            FP_ParameterError: If the chart does not exist or is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlays = list(overlay_ops.GetAll(chart))
            >>> print(f"Chart has {len(overlays)} overlays")
            Chart has 3 overlays
            >>>
            >>> for overlay in overlays:
            ...     name = overlay_ops.GetName(overlay)
            ...     visible = overlay_ops.IsVisible(overlay)
            ...     print(f"Overlay: {name} (visible: {visible})")

        Notes:
            - Returns all overlays regardless of visibility status
            - Overlays are returned in their current display order
            - Empty generator if chart has no overlays
            - Use GetVisibleOverlays() to get only visible overlays

        See Also:
            GetVisibleOverlays, Create, FindByChart
        """
        chart_obj = self.__GetChartObject(chart_or_hvo)

        # Access overlays from the chart
        # In FLEx, overlays may be stored in different properties depending on chart type
        if hasattr(chart_obj, 'TemplateRA'):
            template = chart_obj.TemplateRA
            if template and hasattr(template, 'ColumnsPossibilitiesOC'):
                for overlay in template.ColumnsPossibilitiesOC:
                    yield overlay

        # Alternative: Check if chart has direct overlay collection
        if hasattr(chart_obj, 'RowsOS'):
            # Some overlays may be accessed through rows
            for row in chart_obj.RowsOS:
                if hasattr(row, 'ClauseType'):
                    clause_type = row.ClauseType
                    if clause_type:
                        yield clause_type


    def Create(self, chart_or_hvo, name):
        """
        Create a new overlay (layer) for a discourse chart.

        Creates a new overlay that can be used to organize different aspects of
        chart analysis. The overlay is initially visible and added to the end of
        the display order.

        Args:
            chart_or_hvo: Either an IConstChart object or its HVO (integer identifier).
            name (str): The name of the overlay. Must be non-empty.

        Returns:
            Overlay object: The newly created overlay.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If chart_or_hvo or name is None.
            FP_ParameterError: If name is empty or chart is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>>
            >>> # Create overlays for different analytical perspectives
            >>> participants = overlay_ops.Create(chart, "Participants")
            >>> overlay_ops.SetDescription(participants, "Track participant chains")
            >>>
            >>> discourse = overlay_ops.Create(chart, "Discourse Features")
            >>> overlay_ops.SetDescription(discourse, "Discourse markers and structure")
            >>>
            >>> theme = overlay_ops.Create(chart, "Thematic Structure")
            >>> print(f"Created overlay: {overlay_ops.GetName(theme)}")
            Created overlay: Thematic Structure

        Notes:
            - New overlays are visible by default
            - Display order is set to the next available position
            - Name should be descriptive of the analysis perspective
            - Overlays help organize complex multi-layered analyses

        See Also:
            Delete, GetAll, SetName, SetVisible
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not name:
            raise FP_NullParameterError()

        name = name.strip()
        if not name:
            raise FP_ParameterError("Overlay name cannot be empty")

        chart_obj = self.__GetChartObject(chart_or_hvo)
        wsHandle = self.__WSHandle(None)

        # Create the overlay using the appropriate factory
        # Overlays are typically implemented as possibilities in the chart template
        factory = self.project.project.ServiceLocator.GetInstance(ICmPossibilityFactory)
        overlay = factory.Create()

        # Set the overlay name
        name_str = TsStringUtils.MakeString(name, wsHandle)
        overlay.Name.set_String(wsHandle, name_str)

        # Add to the chart's template column possibilities
        if hasattr(chart_obj, 'TemplateRA'):
            template = chart_obj.TemplateRA
            if template and hasattr(template, 'ColumnsPossibilitiesOC'):
                template.ColumnsPossibilitiesOC.Add(overlay)
            else:
                # If no template exists, we may need to create one
                # For now, raise an error
                raise FP_ParameterError("Chart template not configured for overlays")
        else:
            raise FP_ParameterError("Chart does not support overlays")

        return overlay


    def Delete(self, overlay_or_hvo):
        """
        Delete an overlay from its chart.

        Removes the overlay and all its associated elements from the chart. This
        will affect the display of the chart but does not delete the underlying
        chart data.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If overlay_or_hvo is None.
            FP_ParameterError: If the overlay does not exist or is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlays = list(overlay_ops.GetAll(chart))
            >>> if overlays:
            ...     # Delete the last overlay
            ...     overlay_ops.Delete(overlays[-1])
            ...     print(f"Chart now has {len(list(overlay_ops.GetAll(chart)))} overlays")

        Warning:
            - Deletion is permanent and cannot be undone
            - All overlay configuration and associations will be lost
            - Chart elements linked only to this overlay may become orphaned

        Notes:
            - The overlay is removed from the chart's template
            - Does not affect underlying chart data or rows
            - Other overlays are not affected

        See Also:
            Create, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)

        # Remove from the owning collection
        owner = overlay_obj.Owner
        if owner and hasattr(owner, 'ColumnsPossibilitiesOC'):
            owner.ColumnsPossibilitiesOC.Remove(overlay_obj)
        elif owner and hasattr(owner, 'PossibilitiesOS'):
            owner.PossibilitiesOS.Remove(overlay_obj)
        else:
            raise FP_ParameterError("Overlay has no valid owner or cannot be removed")


    def Find(self, chart_or_hvo, name):
        """
        Find an overlay by name within a chart.

        Searches for an overlay with the specified name in the given chart.
        Search is case-sensitive.

        Args:
            chart_or_hvo: Either an IConstChart object or its HVO (integer identifier).
            name (str): The name of the overlay to find.

        Returns:
            Overlay object or None: The overlay if found, None otherwise.

        Raises:
            FP_NullParameterError: If chart_or_hvo or name is None.
            FP_ParameterError: If the chart does not exist or is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>>
            >>> # Find a specific overlay
            >>> participants = overlay_ops.Find(chart, "Participants")
            >>> if participants:
            ...     print(f"Found overlay: {overlay_ops.GetName(participants)}")
            ... else:
            ...     print("Overlay not found")
            Found overlay: Participants
            >>>
            >>> # Search is case-sensitive
            >>> result = overlay_ops.Find(chart, "participants")
            >>> print(result)
            None

        Notes:
            - Search is case-sensitive
            - Returns first match only
            - Returns None if no overlay with the name exists
            - Use GetAll() to search with custom criteria

        See Also:
            GetAll, FindByChart, GetName
        """
        if not name:
            raise FP_NullParameterError()

        wsHandle = self.__WSHandle(None)

        for overlay in self.GetAll(chart_or_hvo):
            if hasattr(overlay, 'Name'):
                overlay_name = ITsString(overlay.Name.get_String(wsHandle)).Text
                if overlay_name == name:
                    return overlay

        return None


    # --- Property Operations ---

    def GetName(self, overlay_or_hvo, wsHandle=None):
        """
        Get the name of an overlay.

        Retrieves the overlay's name in the specified writing system, or the default
        analysis writing system if not specified.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).
            wsHandle (int, optional): Writing system handle. If None, uses the
                default analysis writing system.

        Returns:
            str: The overlay name in the specified writing system. Returns empty
                string if no name is set.

        Raises:
            FP_NullParameterError: If overlay_or_hvo is None.
            FP_ParameterError: If the overlay does not exist or is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlays = list(overlay_ops.GetAll(chart))
            >>> if overlays:
            ...     name = overlay_ops.GetName(overlays[0])
            ...     print(f"Overlay name: {name}")
            Overlay name: Participants

        See Also:
            SetName, GetDescription
        """
        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        if hasattr(overlay_obj, 'Name'):
            name_str = ITsString(overlay_obj.Name.get_String(wsHandle)).Text
            return name_str or ""
        return ""


    def SetName(self, overlay_or_hvo, name, wsHandle=None):
        """
        Set the name of an overlay.

        Updates the overlay's name in the specified writing system, or the default
        analysis writing system if not specified.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).
            name (str): The new name for the overlay. Must be non-empty.
            wsHandle (int, optional): Writing system handle. If None, uses the
                default analysis writing system.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If overlay_or_hvo or name is None.
            FP_ParameterError: If name is empty or overlay is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlays = list(overlay_ops.GetAll(chart))
            >>> if overlays:
            ...     overlay_ops.SetName(overlays[0], "Participant Tracking")
            ...     print(overlay_ops.GetName(overlays[0]))
            Participant Tracking

        See Also:
            GetName, SetDescription
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not name:
            raise FP_NullParameterError()

        name = name.strip()
        if not name:
            raise FP_ParameterError("Overlay name cannot be empty")

        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        if hasattr(overlay_obj, 'Name'):
            name_str = TsStringUtils.MakeString(name, wsHandle)
            overlay_obj.Name.set_String(wsHandle, name_str)
        else:
            raise FP_ParameterError("Overlay does not support name setting")


    def GetDescription(self, overlay_or_hvo, wsHandle=None):
        """
        Get the description of an overlay.

        Retrieves the overlay's description in the specified writing system, or
        the default analysis writing system if not specified.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).
            wsHandle (int, optional): Writing system handle. If None, uses the
                default analysis writing system.

        Returns:
            str: The overlay description in the specified writing system. Returns
                empty string if no description is set.

        Raises:
            FP_NullParameterError: If overlay_or_hvo is None.
            FP_ParameterError: If the overlay does not exist or is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlay = overlay_ops.Find(chart, "Participants")
            >>> if overlay:
            ...     desc = overlay_ops.GetDescription(overlay)
            ...     if desc:
            ...         print(f"Description: {desc}")
            ... else:
            ...     print("No description set")
            Description: Track participant chains throughout the discourse

        See Also:
            SetDescription, GetName
        """
        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        if hasattr(overlay_obj, 'Description'):
            desc_str = ITsString(overlay_obj.Description.get_String(wsHandle)).Text
            return desc_str or ""
        return ""


    def SetDescription(self, overlay_or_hvo, description, wsHandle=None):
        """
        Set the description of an overlay.

        Updates the overlay's description in the specified writing system, or the
        default analysis writing system if not specified.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).
            description (str): The description text. Can be empty to clear.
            wsHandle (int, optional): Writing system handle. If None, uses the
                default analysis writing system.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If overlay_or_hvo or description is None.
            FP_ParameterError: If the overlay is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlay = overlay_ops.Find(chart, "Participants")
            >>> if overlay:
            ...     overlay_ops.SetDescription(
            ...         overlay,
            ...         "Track participant chains and reference throughout the narrative"
            ...     )
            ...     print(overlay_ops.GetDescription(overlay))
            Track participant chains and reference throughout the narrative

        See Also:
            GetDescription, SetName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if description is None:
            raise FP_NullParameterError()

        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        if hasattr(overlay_obj, 'Description'):
            desc_str = TsStringUtils.MakeString(description, wsHandle)
            overlay_obj.Description.set_String(wsHandle, desc_str)
        else:
            raise FP_ParameterError("Overlay does not support description setting")


    # --- Visibility Operations ---

    def IsVisible(self, overlay_or_hvo):
        """
        Check if an overlay is currently visible.

        Determines whether the overlay is set to be displayed in the chart view.
        Hidden overlays are still part of the chart but not shown in the UI.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).

        Returns:
            bool: True if the overlay is visible, False if hidden.

        Raises:
            FP_NullParameterError: If overlay_or_hvo is None.
            FP_ParameterError: If the overlay does not exist or is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlays = list(overlay_ops.GetAll(chart))
            >>> for overlay in overlays:
            ...     name = overlay_ops.GetName(overlay)
            ...     visible = overlay_ops.IsVisible(overlay)
            ...     status = "visible" if visible else "hidden"
            ...     print(f"{name}: {status}")
            Participants: visible
            Discourse Features: hidden
            Theme: visible

        Notes:
            - Visibility controls chart display only
            - Hidden overlays are still part of the chart data
            - Use SetVisible() to toggle visibility
            - Defaults to True for newly created overlays

        See Also:
            SetVisible, GetVisibleOverlays
        """
        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)

        # Check visibility property
        # In FLEx, this might be stored in different ways
        if hasattr(overlay_obj, 'Hidden'):
            return not overlay_obj.Hidden

        # Default to visible if no visibility property exists
        return True


    def SetVisible(self, overlay_or_hvo, visible):
        """
        Set the visibility status of an overlay.

        Controls whether the overlay is displayed in the chart view. Hidden overlays
        remain part of the chart but are not shown in the UI.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).
            visible (bool): True to make visible, False to hide.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If overlay_or_hvo or visible is None.
            FP_ParameterError: If the overlay is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlay = overlay_ops.Find(chart, "Participants")
            >>>
            >>> # Hide an overlay
            >>> overlay_ops.SetVisible(overlay, False)
            >>> print(f"Visible: {overlay_ops.IsVisible(overlay)}")
            Visible: False
            >>>
            >>> # Show it again
            >>> overlay_ops.SetVisible(overlay, True)
            >>> print(f"Visible: {overlay_ops.IsVisible(overlay)}")
            Visible: True

        Notes:
            - Affects chart display only, not data
            - Useful for focusing on specific analytical perspectives
            - Hidden overlays can be re-shown at any time
            - Does not affect display order

        See Also:
            IsVisible, GetVisibleOverlays
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if visible is None:
            raise FP_NullParameterError()

        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)

        # Set visibility property
        if hasattr(overlay_obj, 'Hidden'):
            overlay_obj.Hidden = not visible
        else:
            # If no visibility property, we can't set it
            # This might need to be implemented through custom fields
            logger.warning("Overlay does not have a visibility property")


    def GetDisplayOrder(self, overlay_or_hvo):
        """
        Get the display order of an overlay.

        Retrieves the numeric position that determines the order in which overlays
        are displayed in the chart. Lower numbers appear first.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).

        Returns:
            int: The display order position (0-based). Returns 0 if not set.

        Raises:
            FP_NullParameterError: If overlay_or_hvo is None.
            FP_ParameterError: If the overlay does not exist or is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlays = list(overlay_ops.GetAll(chart))
            >>> for overlay in overlays:
            ...     name = overlay_ops.GetName(overlay)
            ...     order = overlay_ops.GetDisplayOrder(overlay)
            ...     print(f"{order}: {name}")
            0: Participants
            1: Discourse Features
            2: Theme

        Notes:
            - Lower numbers display first
            - Display order is independent of visibility
            - Returns 0 for overlays without explicit ordering
            - Use SetDisplayOrder() to change the position

        See Also:
            SetDisplayOrder, GetVisibleOverlays
        """
        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)

        # Get display order
        # This might be stored in different ways depending on the implementation
        if hasattr(overlay_obj, 'SortSpec'):
            return overlay_obj.SortSpec

        # If part of an owning sequence, get position in sequence
        owner = overlay_obj.Owner
        if owner and hasattr(owner, 'ColumnsPossibilitiesOC'):
            try:
                return owner.ColumnsPossibilitiesOC.ToList().IndexOf(overlay_obj)
            except (IndexError, System.ArgumentException, System.InvalidOperationException) as e:
                pass

        return 0


    def SetDisplayOrder(self, overlay_or_hvo, order):
        """
        Set the display order of an overlay.

        Updates the numeric position that determines the order in which overlays
        are displayed in the chart. Lower numbers appear first.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).
            order (int): The display order position (0-based). Must be non-negative.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If overlay_or_hvo or order is None.
            FP_ParameterError: If order is negative or overlay is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlay = overlay_ops.Find(chart, "Theme")
            >>>
            >>> # Move to first position
            >>> overlay_ops.SetDisplayOrder(overlay, 0)
            >>> print(f"Display order: {overlay_ops.GetDisplayOrder(overlay)}")
            Display order: 0
            >>>
            >>> # Move to third position
            >>> overlay_ops.SetDisplayOrder(overlay, 2)

        Notes:
            - Lower numbers display first
            - Order changes affect visual arrangement only
            - Does not affect data or visibility
            - May need to reorder other overlays to avoid gaps

        See Also:
            GetDisplayOrder, GetAll
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if order is None:
            raise FP_NullParameterError()

        if order < 0:
            raise FP_ParameterError("Display order must be non-negative")

        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)

        # Set display order
        if hasattr(overlay_obj, 'SortSpec'):
            overlay_obj.SortSpec = order
        else:
            # If part of an owning sequence, reorder within sequence
            owner = overlay_obj.Owner
            if owner and hasattr(owner, 'ColumnsPossibilitiesOC'):
                collection = owner.ColumnsPossibilitiesOC
                try:
                    # Remove and re-insert at new position
                    collection.Remove(overlay_obj)
                    if order >= collection.Count:
                        collection.Add(overlay_obj)
                    else:
                        collection.Insert(order, overlay_obj)
                except (IndexError, System.ArgumentException, System.InvalidOperationException) as e:
                    raise FP_ParameterError("Could not reorder overlay")
            else:
                logger.warning("Overlay does not support display order setting")


    # --- Element Operations ---

    def GetElements(self, overlay_or_hvo):
        """
        Get all chart elements associated with an overlay.

        Retrieves the chart elements (cells, markers, word groups, etc.) that are
        displayed in this overlay layer.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).

        Returns:
            list: List of chart element objects. Returns empty list if no elements.

        Raises:
            FP_NullParameterError: If overlay_or_hvo is None.
            FP_ParameterError: If the overlay does not exist or is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlay = overlay_ops.Find(chart, "Participants")
            >>> if overlay:
            ...     elements = overlay_ops.GetElements(overlay)
            ...     print(f"Overlay has {len(elements)} elements")
            Overlay has 12 elements

        Notes:
            - Returns all elements regardless of visibility
            - Element types vary by overlay purpose
            - Empty list if overlay has no elements
            - Elements are shared with the parent chart

        See Also:
            AddElement, RemoveElement, GetChart
        """
        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)

        elements = []

        # Get elements from the overlay
        # This depends on how elements are stored
        if hasattr(overlay_obj, 'CellsOS'):
            elements.extend(list(overlay_obj.CellsOS))

        if hasattr(overlay_obj, 'MarkersRS'):
            elements.extend(list(overlay_obj.MarkersRS))

        return elements


    def AddElement(self, overlay_or_hvo, element):
        """
        Add a chart element to an overlay.

        Associates a chart element with this overlay layer so it will be displayed
        when the overlay is visible.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).
            element: The chart element object to add.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If overlay_or_hvo or element is None.
            FP_ParameterError: If the overlay or element is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlay = overlay_ops.Find(chart, "Participants")
            >>>
            >>> # Add a chart element to the overlay
            >>> # (assuming 'element' is a valid chart element)
            >>> overlay_ops.AddElement(overlay, element)
            >>> elements = overlay_ops.GetElements(overlay)
            >>> print(f"Overlay now has {len(elements)} elements")

        Notes:
            - Element must be compatible with the overlay type
            - Element can be in multiple overlays
            - Does not affect element's chart membership
            - Element visibility follows overlay visibility

        See Also:
            RemoveElement, GetElements
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not element:
            raise FP_NullParameterError()

        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)

        # Add element to overlay's collection
        # The specific collection depends on element type
        if hasattr(overlay_obj, 'CellsOS'):
            try:
                overlay_obj.CellsOS.Add(element)
                return
            except:
                pass

        if hasattr(overlay_obj, 'MarkersRS'):
            try:
                overlay_obj.MarkersRS.Add(element)
                return
            except:
                pass

        raise FP_ParameterError("Could not add element to overlay")


    def RemoveElement(self, overlay_or_hvo, element):
        """
        Remove a chart element from an overlay.

        Removes the association between a chart element and this overlay layer.
        The element remains in the chart but is no longer displayed in this overlay.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).
            element: The chart element object to remove.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If overlay_or_hvo or element is None.
            FP_ParameterError: If the overlay or element is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlay = overlay_ops.Find(chart, "Participants")
            >>> elements = overlay_ops.GetElements(overlay)
            >>> if elements:
            ...     # Remove the first element
            ...     overlay_ops.RemoveElement(overlay, elements[0])
            ...     print(f"Overlay now has {len(overlay_ops.GetElements(overlay))} elements")

        Notes:
            - Does not delete the element from the chart
            - Only removes the overlay association
            - Element may still appear in other overlays
            - No error if element is not in the overlay

        See Also:
            AddElement, GetElements
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not element:
            raise FP_NullParameterError()

        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)

        # Remove element from overlay's collection
        if hasattr(overlay_obj, 'CellsOS'):
            try:
                overlay_obj.CellsOS.Remove(element)
                return
            except:
                pass

        if hasattr(overlay_obj, 'MarkersRS'):
            try:
                overlay_obj.MarkersRS.Remove(element)
                return
            except:
                pass

        # If we get here, element wasn't in any collection
        logger.warning("Element not found in overlay or could not be removed")


    # --- Chart Operations ---

    def GetChart(self, overlay_or_hvo):
        """
        Get the chart that owns an overlay.

        Retrieves the IConstChart object that contains this overlay.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).

        Returns:
            IConstChart: The chart object that owns the overlay.

        Raises:
            FP_NullParameterError: If overlay_or_hvo is None.
            FP_ParameterError: If the overlay does not exist or has no owner.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlays = list(overlay_ops.GetAll(chart))
            >>> if overlays:
            ...     owner_chart = overlay_ops.GetChart(overlays[0])
            ...     chart_name = discourse_ops.GetChartName(owner_chart)
            ...     print(f"Overlay belongs to chart: {chart_name}")
            Overlay belongs to chart: Main Analysis

        Notes:
            - Overlays are always owned by a chart
            - Useful for navigation and context
            - The owner is accessed through the overlay's ownership chain

        See Also:
            GetAll, FindByChart
        """
        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)

        # Navigate up the ownership chain to find the chart
        # Overlay -> Template -> Chart
        owner = overlay_obj.Owner
        if owner:
            # Check if owner is the template
            if hasattr(owner, 'Owner'):
                chart_owner = owner.Owner
                if chart_owner:
                    try:
                        return IConstChart(chart_owner)
                    except:
                        raise FP_ParameterError("Overlay owner is not a valid chart")

        raise FP_ParameterError("Overlay has no valid owning chart")


    def GetPossItems(self, overlay_or_hvo):
        """
        Get the possibility items (column/row labels) for an overlay.

        Retrieves the possibility items that define the structure of this overlay,
        such as column headers or row labels.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).

        Returns:
            list: List of ICmPossibility objects. Returns empty list if none.

        Raises:
            FP_NullParameterError: If overlay_or_hvo is None.
            FP_ParameterError: If the overlay does not exist or is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlay = overlay_ops.Find(chart, "Participants")
            >>> if overlay:
            ...     items = overlay_ops.GetPossItems(overlay)
            ...     print(f"Overlay has {len(items)} possibility items")
            Overlay has 5 possibility items

        Notes:
            - Possibility items define the structure of the overlay
            - Items may represent columns, rows, or other structural elements
            - Empty list if overlay has no structural items
            - Items are typically ICmPossibility objects

        See Also:
            GetElements, GetChart
        """
        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)

        items = []

        # Get possibility items
        if hasattr(overlay_obj, 'SubPossibilitiesOS'):
            items.extend(list(overlay_obj.SubPossibilitiesOS))

        if hasattr(overlay_obj, 'PossItemsRS'):
            items.extend(list(overlay_obj.PossItemsRS))

        return items


    # --- Query Operations ---

    def FindByChart(self, chart_or_hvo, name):
        """
        Find an overlay by name within a specific chart.

        This is an alias for Find() for consistency with other operations classes.

        Args:
            chart_or_hvo: Either an IConstChart object or its HVO (integer identifier).
            name (str): The name of the overlay to find.

        Returns:
            Overlay object or None: The overlay if found, None otherwise.

        Raises:
            FP_NullParameterError: If chart_or_hvo or name is None.
            FP_ParameterError: If the chart does not exist or is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlay = overlay_ops.FindByChart(chart, "Participants")
            >>> if overlay:
            ...     print(f"Found: {overlay_ops.GetName(overlay)}")
            Found: Participants

        See Also:
            Find, GetAll
        """
        return self.Find(chart_or_hvo, name)


    def GetVisibleOverlays(self, chart_or_hvo):
        """
        Get all visible overlays for a chart.

        Retrieves only the overlays that are currently set to be visible in the
        chart view, filtered by their visibility status.

        Args:
            chart_or_hvo: Either an IConstChart object or its HVO (integer identifier).

        Yields:
            Overlay objects: Each visible overlay in the chart.

        Raises:
            FP_NullParameterError: If chart_or_hvo is None.
            FP_ParameterError: If the chart does not exist or is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>>
            >>> # Get only visible overlays
            >>> visible = list(overlay_ops.GetVisibleOverlays(chart))
            >>> print(f"Chart has {len(visible)} visible overlays")
            Chart has 2 visible overlays
            >>>
            >>> for overlay in visible:
            ...     name = overlay_ops.GetName(overlay)
            ...     order = overlay_ops.GetDisplayOrder(overlay)
            ...     print(f"{order}: {name}")
            0: Participants
            2: Theme

        Notes:
            - Returns only overlays with visibility set to True
            - Empty generator if no visible overlays
            - Use GetAll() to get all overlays regardless of visibility
            - Useful for UI display and analysis

        See Also:
            GetAll, IsVisible, SetVisible
        """
        for overlay in self.GetAll(chart_or_hvo):
            if self.IsVisible(overlay):
                yield overlay


    # --- Metadata Operations ---

    def GetGuid(self, overlay_or_hvo):
        """
        Get the GUID of an overlay.

        Retrieves the globally unique identifier for the overlay.

        Args:
            overlay_or_hvo: Either an overlay object or its HVO (integer identifier).

        Returns:
            System.Guid: The GUID of the overlay.

        Raises:
            FP_NullParameterError: If overlay_or_hvo is None.
            FP_ParameterError: If the overlay does not exist or is invalid.

        Example:
            >>> overlay_ops = OverlayOperations(project)
            >>> chart = discourse_ops.GetAllCharts(text)[0]
            >>> overlays = list(overlay_ops.GetAll(chart))
            >>> if overlays:
            ...     guid = overlay_ops.GetGuid(overlays[0])
            ...     print(f"Overlay GUID: {guid}")
            Overlay GUID: 12345678-1234-1234-1234-123456789abc

        Notes:
            - GUIDs are globally unique identifiers
            - Persistent across project versions
            - Use for external references and tracking
            - Same GUID across different copies of the project

        See Also:
            GetChart, GetName
        """
        overlay_obj = self.__GetOverlayObject(overlay_or_hvo)

        if hasattr(overlay_obj, 'Guid'):
            return overlay_obj.Guid
        else:
            raise FP_ParameterError("Overlay object does not have a GUID")
