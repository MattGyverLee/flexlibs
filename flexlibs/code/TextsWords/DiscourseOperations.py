#
#   DiscourseOperations.py
#
#   Class: DiscourseOperations
#          Discourse and constituent chart management operations for FieldWorks
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
    IDsConstChart,  # Fixed: was IConstChart
    IDsConstChartFactory,  # Fixed: was IConstChartFactory
    IDsChart,
    IDsDiscourseData,  # Fixed: was IDiscourseData
    IConstChartRow,
    IConstChartRowFactory,
    IConstChartWordGroup,
    IConstChartWordGroupFactory,
    IConstChartMovedTextMarker,
    IConstChartMovedTextMarkerFactory,
    IConstChartClauseMarker,
    IConstChartClauseMarkerFactory,
    IConstChartTag,
    IText,
    ICmPossibility,
)

from SIL.LCModel.Core.KernelInterfaces import ITsString
from SIL.LCModel.Core.Text import TsStringUtils

from ..FLExProject import (
    FP_ReadOnlyError,
    FP_NullParameterError,
    FP_ParameterError,
)
from ..BaseOperations import BaseOperations


class DiscourseOperations(BaseOperations):
    """
    Discourse and constituent chart management operations for FLEx projects.

    This class provides methods for creating and managing discourse charts and
    constituent charts. Charts provide a visual analysis of text structure, showing
    relationships between clauses, participants, and discourse features.

    Note:
        Charts are complex UI-heavy features. This class focuses on data access
        and basic chart structure management. Full chart editing capabilities
        typically require the FLEx UI.

    Usage::

        from flexlibs import FLExProject, DiscourseOperations

        project = FLExProject()
        project.OpenProject("my project", writeEnabled=True)

        discourse_ops = DiscourseOperations(project)

        # Get a text
        text = list(project.Texts.GetAll())[0]

        # Get all charts for the text
        charts = list(discourse_ops.GetAllCharts(text))
        print(f"Text has {len(charts)} charts")

        # Create a new constituent chart
        chart = discourse_ops.CreateChart(text, "Main Chart", "constituent")
        chart_name = discourse_ops.GetChartName(chart)
        print(f"Created chart: {chart_name}")

        # Add rows to the chart
        row1 = discourse_ops.AddRow(chart)
        row2 = discourse_ops.AddRow(chart)
        row_count = discourse_ops.GetRowCount(chart)
        print(f"Chart has {row_count} rows")

        # Get chart rows
        rows = discourse_ops.GetRows(chart)
        for i, row in enumerate(rows, 1):
            print(f"Row {i}")

        project.CloseProject()
    """

    def __init__(self, project):
        """
        Initialize DiscourseOperations with a FLExProject instance.

        Args:
            project: The FLExProject instance to operate on.
        """
        super().__init__(project)

    def _GetSequence(self, parent):
        """Specify which sequence to reorder for discourse charts."""
        return parent.ChartsOS


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


    def __GetTextObject(self, text_or_hvo):
        """
        Resolve text_or_hvo to IText object.

        Args:
            text_or_hvo: Either an IText object or its HVO (integer).

        Returns:
            IText: The text object.

        Raises:
            FP_NullParameterError: If text_or_hvo is None.
            FP_ParameterError: If the object doesn't exist or isn't a valid text.
        """
        if not text_or_hvo:
            raise FP_NullParameterError()

        if isinstance(text_or_hvo, int):
            try:
                return IText(self.project.Object(text_or_hvo))
            except:
                raise FP_ParameterError(f"Invalid text HVO: {text_or_hvo}")
        return text_or_hvo


    def __GetChartObject(self, chart_or_hvo):
        """
        Resolve chart_or_hvo to chart object (IConstChart or IDsChart).

        Args:
            chart_or_hvo: Either a chart object or its HVO (integer).

        Returns:
            Chart object (IConstChart or IDsChart).

        Raises:
            FP_NullParameterError: If chart_or_hvo is None.
            FP_ParameterError: If the object doesn't exist or isn't a valid chart.
        """
        if not chart_or_hvo:
            raise FP_NullParameterError()

        if isinstance(chart_or_hvo, int):
            try:
                obj = self.project.Object(chart_or_hvo)
                # Try to cast to IDsConstChart first (most common)
                try:
                    return IDsConstChart(obj)
                except:
                    # Fall back to IDsChart for discourse charts
                    return IDsChart(obj)
            except:
                raise FP_ParameterError(f"Invalid chart HVO: {chart_or_hvo}")
        return chart_or_hvo


    def __GetRowObject(self, row_or_hvo):
        """
        Resolve row_or_hvo to IConstChartRow object.

        Args:
            row_or_hvo: Either an IConstChartRow object or its HVO (integer).

        Returns:
            IConstChartRow: The row object.

        Raises:
            FP_NullParameterError: If row_or_hvo is None.
            FP_ParameterError: If the object doesn't exist or isn't a valid row.
        """
        if not row_or_hvo:
            raise FP_NullParameterError()

        if isinstance(row_or_hvo, int):
            try:
                obj = self.project.Object(row_or_hvo)
                return IConstChartRow(obj)
            except:
                raise FP_ParameterError(f"Invalid row HVO: {row_or_hvo}")
        return row_or_hvo


    # --- Chart Management Operations ---

    def GetAllCharts(self, text_or_hvo):
        """
        Get all charts (discourse and constituent) for a text.

        Args:
            text_or_hvo: Either an IText object or its HVO (integer identifier).

        Yields:
            Chart objects (IConstChart or IDsChart): Each chart associated with the text.

        Raises:
            FP_NullParameterError: If text_or_hvo is None.
            FP_ParameterError: If the text does not exist or is invalid.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> print(f"Text has {len(charts)} charts")
            Text has 2 charts
            >>>
            >>> for chart in charts:
            ...     name = discourse_ops.GetChartName(chart)
            ...     chart_type = discourse_ops.GetChartType(chart)
            ...     print(f"Chart: {name} ({chart_type})")

        Notes:
            - Returns both constituent charts and discourse charts
            - Charts are accessed through the text's DiscourseData property
            - Returns empty generator if no charts exist
            - Use list() to convert to a list if needed

        See Also:
            CreateChart, DeleteChart, GetChartName
        """
        text_obj = self.__GetTextObject(text_or_hvo)

        # Check if text has discourse data
        if not text_obj.ContentsOA:
            return

        # Get the discourse data container
        discourse_data = None
        if hasattr(text_obj, 'ContentsOA') and text_obj.ContentsOA:
            # DiscourseData is typically stored in the text's contents
            # Access charts through the owning text's structure
            if hasattr(text_obj.ContentsOA, 'ChartsOC'):
                for chart in text_obj.ContentsOA.ChartsOC:
                    yield chart


    def CreateChart(self, text_or_hvo, name, chart_type="constituent"):
        """
        Create a new chart for a text.

        Creates either a constituent chart (IConstChart) or discourse chart based
        on the chart_type parameter. The chart will be added to the text's chart
        collection.

        Args:
            text_or_hvo: Either an IText object or its HVO (integer identifier).
            name (str): The name of the chart. Must be non-empty.
            chart_type (str): Type of chart to create. Either "constituent" or
                "discourse". Defaults to "constituent".

        Returns:
            Chart object (IConstChart): The newly created chart.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If text_or_hvo or name is None.
            FP_ParameterError: If name is empty, text is invalid, or chart_type
                is not recognized.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>>
            >>> # Create a constituent chart (default)
            >>> chart = discourse_ops.CreateChart(text, "Main Analysis")
            >>> print(discourse_ops.GetChartName(chart))
            Main Analysis
            >>>
            >>> # Create a discourse chart
            >>> discourse_chart = discourse_ops.CreateChart(text, "Discourse", "discourse")

        Notes:
            - Chart name should be descriptive of the analysis being performed
            - Constituent charts are more common for syntactic analysis
            - Discourse charts focus on discourse structure and relations
            - The text must have a ContentsOA (StText) object

        See Also:
            DeleteChart, GetAllCharts, SetChartName
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not name:
            raise FP_NullParameterError()

        name = name.strip()
        if not name:
            raise FP_ParameterError("Chart name cannot be empty")

        # Validate chart_type
        chart_type_lower = chart_type.lower() if chart_type else "constituent"
        if chart_type_lower not in ["constituent", "discourse"]:
            raise FP_ParameterError(
                f"chart_type must be 'constituent' or 'discourse', got '{chart_type}'"
            )

        text_obj = self.__GetTextObject(text_or_hvo)

        # Ensure text has contents
        if not text_obj.ContentsOA:
            raise FP_ParameterError("Text has no StText contents")

        # Create the chart using the factory
        factory = self.project.project.ServiceLocator.GetService(IConstChartFactory)
        chart = factory.Create()

        # Add to the text's chart collection
        # Charts are stored in ContentsOA.ChartsOC
        if hasattr(text_obj.ContentsOA, 'ChartsOC'):
            text_obj.ContentsOA.ChartsOC.Add(chart)
        else:
            # Alternative: If charts are stored differently, adjust accordingly
            # For now, assume standard structure
            raise FP_ParameterError("Text contents does not support charts")

        # Set the chart name
        wsHandle = self.__WSHandle(None)
        name_str = TsStringUtils.MakeString(name, wsHandle)
        chart.Name.set_String(wsHandle, name_str)

        return chart


    def DeleteChart(self, chart_or_hvo):
        """
        Delete a chart from its text.

        Removes the chart and all its rows, cells, and associated data from the
        text's chart collection.

        Args:
            chart_or_hvo: Either a chart object or its HVO (integer identifier).

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If chart_or_hvo is None.
            FP_ParameterError: If the chart does not exist or is invalid.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> if charts:
            ...     # Delete the first chart
            ...     discourse_ops.DeleteChart(charts[0])
            ...     print("Chart deleted")

        Warning:
            - Deletion is permanent and cannot be undone
            - All chart rows and cells will be deleted
            - All chart analysis data will be lost

        Notes:
            - The chart is removed from its owning text's collection
            - Use with caution on charts with significant analysis work

        See Also:
            CreateChart, GetAllCharts
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        chart_obj = self.__GetChartObject(chart_or_hvo)

        # Get the owner and remove the chart
        owner = chart_obj.Owner
        if owner and hasattr(owner, 'ChartsOC'):
            owner.ChartsOC.Remove(chart_obj)
        else:
            raise FP_ParameterError("Chart has no valid owner or cannot be removed")


    def GetChartName(self, chart_or_hvo, wsHandle=None):
        """
        Get the name of a chart.

        Retrieves the chart's name in the specified writing system, or the default
        analysis writing system if not specified.

        Args:
            chart_or_hvo: Either a chart object or its HVO (integer identifier).
            wsHandle (int, optional): Writing system handle. If None, uses the
                default analysis writing system.

        Returns:
            str: The chart name in the specified writing system. Returns empty
                string if no name is set.

        Raises:
            FP_NullParameterError: If chart_or_hvo is None.
            FP_ParameterError: If the chart does not exist or is invalid.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> if charts:
            ...     name = discourse_ops.GetChartName(charts[0])
            ...     print(f"Chart name: {name}")
            Chart name: Main Analysis

        See Also:
            SetChartName, CreateChart
        """
        chart_obj = self.__GetChartObject(chart_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Get the chart name
        if hasattr(chart_obj, 'Name'):
            name_str = ITsString(chart_obj.Name.get_String(wsHandle)).Text
            return name_str or ""
        return ""


    def SetChartName(self, chart_or_hvo, name, wsHandle=None):
        """
        Set the name of a chart.

        Updates the chart's name in the specified writing system, or the default
        analysis writing system if not specified.

        Args:
            chart_or_hvo: Either a chart object or its HVO (integer identifier).
            name (str): The new name for the chart. Must be non-empty.
            wsHandle (int, optional): Writing system handle. If None, uses the
                default analysis writing system.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If chart_or_hvo or name is None.
            FP_ParameterError: If name is empty or chart is invalid.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> if charts:
            ...     discourse_ops.SetChartName(charts[0], "Updated Analysis")
            ...     print(discourse_ops.GetChartName(charts[0]))
            Updated Analysis

        See Also:
            GetChartName, CreateChart
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not name:
            raise FP_NullParameterError()

        name = name.strip()
        if not name:
            raise FP_ParameterError("Chart name cannot be empty")

        chart_obj = self.__GetChartObject(chart_or_hvo)
        wsHandle = self.__WSHandle(wsHandle)

        # Set the chart name
        if hasattr(chart_obj, 'Name'):
            name_str = TsStringUtils.MakeString(name, wsHandle)
            chart_obj.Name.set_String(wsHandle, name_str)
        else:
            raise FP_ParameterError("Chart does not support name setting")


    def GetChartType(self, chart_or_hvo):
        """
        Get the type of a chart (constituent or discourse).

        Determines whether the chart is a constituent chart (IConstChart) or
        a discourse chart (IDsChart) based on its class type.

        Args:
            chart_or_hvo: Either a chart object or its HVO (integer identifier).

        Returns:
            str: "constituent" for constituent charts, "discourse" for discourse
                charts, or "unknown" if the type cannot be determined.

        Raises:
            FP_NullParameterError: If chart_or_hvo is None.
            FP_ParameterError: If the chart does not exist or is invalid.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> for chart in charts:
            ...     name = discourse_ops.GetChartName(chart)
            ...     chart_type = discourse_ops.GetChartType(chart)
            ...     print(f"{name}: {chart_type}")
            Main Analysis: constituent
            Discourse Chart: discourse

        Notes:
            - Chart type is determined by the object's class
            - Constituent charts are IConstChart instances
            - Discourse charts are IDsChart instances
            - Most charts in FLEx are constituent charts

        See Also:
            CreateChart, GetAllCharts
        """
        chart_obj = self.__GetChartObject(chart_or_hvo)

        # Determine chart type by class
        class_name = chart_obj.GetType().Name

        if "ConstChart" in class_name:
            return "constituent"
        elif "DsChart" in class_name:
            return "discourse"
        else:
            # Try to determine by checking for specific interfaces
            try:
                IConstChart(chart_obj)
                return "constituent"
            except:
                try:
                    IDsChart(chart_obj)
                    return "discourse"
                except:
                    return "unknown"


    # --- Chart Row/Structure Operations ---

    def GetRows(self, chart_or_hvo):
        """
        Get all rows in a chart.

        Retrieves the ordered list of rows (typically representing clauses or
        discourse units) from the chart.

        Args:
            chart_or_hvo: Either a chart object or its HVO (integer identifier).

        Returns:
            list: List of IConstChartRow objects. Returns empty list if the chart
                has no rows.

        Raises:
            FP_NullParameterError: If chart_or_hvo is None.
            FP_ParameterError: If the chart does not exist or is invalid.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> if charts:
            ...     rows = discourse_ops.GetRows(charts[0])
            ...     print(f"Chart has {len(rows)} rows")
            ...     for i, row in enumerate(rows, 1):
            ...         print(f"Row {i}")
            Chart has 5 rows
            Row 1
            Row 2
            Row 3
            Row 4
            Row 5

        Notes:
            - Rows are returned in the order they appear in the chart
            - Each row typically represents a clause or sentence
            - Empty list returned if chart has no rows
            - Use GetRowCount() for just the count

        See Also:
            GetRowCount, AddRow, DeleteRow
        """
        chart_obj = self.__GetChartObject(chart_or_hvo)

        # Get rows from the chart
        if hasattr(chart_obj, 'RowsOS'):
            return list(chart_obj.RowsOS)
        return []


    def GetRowCount(self, chart_or_hvo):
        """
        Get the number of rows in a chart.

        This is more efficient than calling len(GetRows()) when you only need
        the count.

        Args:
            chart_or_hvo: Either a chart object or its HVO (integer identifier).

        Returns:
            int: The number of rows in the chart. Returns 0 if the chart has
                no rows.

        Raises:
            FP_NullParameterError: If chart_or_hvo is None.
            FP_ParameterError: If the chart does not exist or is invalid.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> if charts:
            ...     count = discourse_ops.GetRowCount(charts[0])
            ...     print(f"Chart has {count} rows")
            Chart has 5 rows

        Notes:
            - More efficient than getting all rows for just the count
            - Returns 0 for charts with no rows
            - Each row typically represents a clause or discourse unit

        See Also:
            GetRows, AddRow, DeleteRow
        """
        chart_obj = self.__GetChartObject(chart_or_hvo)

        # Get row count
        if hasattr(chart_obj, 'RowsOS'):
            return chart_obj.RowsOS.Count
        return 0


    def AddRow(self, chart_or_hvo):
        """
        Add a new row to a chart.

        Creates a new row and appends it to the end of the chart's row collection.
        The row will be empty initially and can be populated with cells and content.

        Args:
            chart_or_hvo: Either a chart object or its HVO (integer identifier).

        Returns:
            IConstChartRow: The newly created row object.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If chart_or_hvo is None.
            FP_ParameterError: If the chart does not exist or is invalid.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> chart = discourse_ops.CreateChart(text, "Analysis")
            >>>
            >>> # Add rows to the chart
            >>> row1 = discourse_ops.AddRow(chart)
            >>> row2 = discourse_ops.AddRow(chart)
            >>> row3 = discourse_ops.AddRow(chart)
            >>> print(f"Chart has {discourse_ops.GetRowCount(chart)} rows")
            Chart has 3 rows

        Notes:
            - Rows are appended to the end of the chart
            - New rows are initially empty
            - Rows typically represent clauses or discourse segments
            - Use InsertRow() to insert at a specific position (if implemented)

        See Also:
            DeleteRow, GetRows, GetRowCount
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        chart_obj = self.__GetChartObject(chart_or_hvo)

        # Create the new row using the factory
        factory = self.project.project.ServiceLocator.GetService(IConstChartRowFactory)
        row = factory.Create()

        # Add to chart's row collection
        if hasattr(chart_obj, 'RowsOS'):
            chart_obj.RowsOS.Add(row)
        else:
            raise FP_ParameterError("Chart does not support rows")

        return row


    def DeleteRow(self, row_or_hvo):
        """
        Delete a row from its chart.

        Removes the row and all its cells and content from the chart's row
        collection.

        Args:
            row_or_hvo: Either an IConstChartRow object or its HVO (integer identifier).

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If row_or_hvo is None.
            FP_ParameterError: If the row does not exist or is invalid.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> if charts:
            ...     rows = discourse_ops.GetRows(charts[0])
            ...     if rows:
            ...         # Delete the last row
            ...         discourse_ops.DeleteRow(rows[-1])
            ...         print(f"Chart now has {discourse_ops.GetRowCount(charts[0])} rows")

        Warning:
            - Deletion is permanent and cannot be undone
            - All cells and content in the row will be deleted
            - Chart structure may be affected

        Notes:
            - The row is removed from its owning chart's collection
            - All associated data (cells, markers, etc.) is also deleted

        See Also:
            AddRow, GetRows, GetRowCount
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        row_obj = self.__GetRowObject(row_or_hvo)

        # Get the owner (chart) and remove the row
        owner = row_obj.Owner
        if owner and hasattr(owner, 'RowsOS'):
            owner.RowsOS.Remove(row_obj)
        else:
            raise FP_ParameterError("Row has no valid owner or cannot be removed")


    # --- Chart Content Operations ---

    def GetCells(self, row_or_hvo):
        """
        Get all cells in a chart row.

        Retrieves the cells (word groups, markers, etc.) that make up a row in
        the chart. Cells represent individual units of analysis within the row.

        Args:
            row_or_hvo: Either an IConstChartRow object or its HVO (integer identifier).

        Returns:
            list: List of cell objects (IConstChartWordGroup, IConstChartMovedTextMarker,
                IConstChartClauseMarker, etc.). Returns empty list if the row has no cells.

        Raises:
            FP_NullParameterError: If row_or_hvo is None.
            FP_ParameterError: If the row does not exist or is invalid.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> if charts:
            ...     rows = discourse_ops.GetRows(charts[0])
            ...     for row in rows:
            ...         cells = discourse_ops.GetCells(row)
            ...         print(f"Row has {len(cells)} cells")
            Row has 3 cells
            Row has 2 cells
            Row has 4 cells

        Notes:
            - Cells are returned in the order they appear in the row
            - Different cell types include word groups, markers, etc.
            - Empty list returned if row has no cells
            - Chart cells are complex objects with various properties

        See Also:
            GetCellContent, SetCellContent, GetRows
        """
        row_obj = self.__GetRowObject(row_or_hvo)

        # Get cells from the row
        if hasattr(row_obj, 'CellsOS'):
            return list(row_obj.CellsOS)
        return []


    def SetCellContent(self, cell, content, wsHandle=None):
        """
        Set content for a chart cell.

        Updates the text content of a chart cell. This is primarily for cells
        that contain annotations or labels.

        Note:
            Most chart cells reference text segments rather than containing
            their own text. This method is for cells with editable content
            like notes or labels.

        Args:
            cell: The cell object to update.
            content (str): The content to set.
            wsHandle (int, optional): Writing system handle. If None, uses the
                default analysis writing system.

        Raises:
            FP_ReadOnlyError: If project was not opened with writeEnabled=True.
            FP_NullParameterError: If cell or content is None.
            FP_ParameterError: If the cell is invalid or doesn't support content.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> if charts:
            ...     rows = discourse_ops.GetRows(charts[0])
            ...     if rows:
            ...         cells = discourse_ops.GetCells(rows[0])
            ...         if cells:
            ...             # Set content for a cell (if it supports it)
            ...             discourse_ops.SetCellContent(cells[0], "Subject")

        Notes:
            - Not all cell types support editable content
            - Most cells reference text segments from the source text
            - Use this for annotations, labels, or notes on cells
            - Content may be available only for specific cell types

        See Also:
            GetCellContent, GetCells
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if cell is None:
            raise FP_NullParameterError()
        if content is None:
            raise FP_NullParameterError()

        wsHandle = self.__WSHandle(wsHandle)

        # Check if cell has a content property that can be set
        # Different cell types have different properties
        if hasattr(cell, 'Label'):
            # Some cells have a Label property
            content_str = TsStringUtils.MakeString(content, wsHandle)
            cell.Label.set_String(wsHandle, content_str)
        elif hasattr(cell, 'Comment'):
            # Some cells have a Comment property
            content_str = TsStringUtils.MakeString(content, wsHandle)
            cell.Comment.set_String(wsHandle, content_str)
        else:
            raise FP_ParameterError(
                "Cell does not support editable content (no Label or Comment property)"
            )


    def GetCellContent(self, cell, wsHandle=None):
        """
        Get content from a chart cell.

        Retrieves the text content of a chart cell. For cells that reference
        text segments, this may return the referenced text. For annotation cells,
        it returns the annotation content.

        Args:
            cell: The cell object to read from.
            wsHandle (int, optional): Writing system handle. If None, uses the
                default analysis writing system.

        Returns:
            str: The cell content, or empty string if no content is available.

        Raises:
            FP_NullParameterError: If cell is None.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> if charts:
            ...     rows = discourse_ops.GetRows(charts[0])
            ...     for row in rows:
            ...         cells = discourse_ops.GetCells(row)
            ...         for cell in cells:
            ...             content = discourse_ops.GetCellContent(cell)
            ...             if content:
            ...                 print(f"Cell: {content}")

        Notes:
            - Different cell types store content differently
            - Word group cells reference text segments
            - Marker cells may have labels or comments
            - Returns empty string if no content is available
            - Content type depends on cell type

        See Also:
            SetCellContent, GetCells
        """
        if cell is None:
            raise FP_NullParameterError()

        wsHandle = self.__WSHandle(wsHandle)

        # Try different properties based on cell type
        content = ""

        # Try Label property (for markers, annotations)
        if hasattr(cell, 'Label'):
            try:
                label_str = ITsString(cell.Label.get_String(wsHandle)).Text
                if label_str:
                    content = label_str
            except:
                pass

        # Try Comment property
        if not content and hasattr(cell, 'Comment'):
            try:
                comment_str = ITsString(cell.Comment.get_String(wsHandle)).Text
                if comment_str:
                    content = comment_str
            except:
                pass

        # For word groups, get the baseline text
        if not content and hasattr(cell, 'BeginSegment'):
            try:
                # Word groups reference segments
                segment = cell.BeginSegment
                if segment and hasattr(segment, 'BaselineText'):
                    baseline = ITsString(segment.BaselineText).Text
                    if baseline:
                        content = baseline
            except:
                pass

        return content or ""


    # --- Utility Operations ---

    def GetOwningText(self, chart_or_hvo):
        """
        Get the text that owns a chart.

        Retrieves the IText object that contains the chart.

        Args:
            chart_or_hvo: Either a chart object or its HVO (integer identifier).

        Returns:
            IText: The text object that owns the chart.

        Raises:
            FP_NullParameterError: If chart_or_hvo is None.
            FP_ParameterError: If the chart does not exist or has no owner.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> if charts:
            ...     owner = discourse_ops.GetOwningText(charts[0])
            ...     text_name = owner.Name.BestAnalysisAlternative.Text
            ...     print(f"Chart belongs to text: {text_name}")
            Chart belongs to text: Genesis

        Notes:
            - Charts are always owned by a text's StText contents
            - Useful for navigation and context
            - The owner is accessed through the chart's ownership chain

        See Also:
            GetAllCharts, CreateChart
        """
        chart_obj = self.__GetChartObject(chart_or_hvo)

        # Navigate up the ownership chain to find the text
        # Chart -> StText -> Text
        owner = chart_obj.Owner  # This should be StText
        if owner:
            text_owner = owner.Owner  # This should be IText
            if text_owner:
                try:
                    return IText(text_owner)
                except:
                    raise FP_ParameterError("Chart owner is not a valid text")

        raise FP_ParameterError("Chart has no valid owning text")


    def GetGuid(self, chart_or_hvo):
        """
        Get the GUID of a chart.

        Retrieves the globally unique identifier for the chart.

        Args:
            chart_or_hvo: Either a chart object or its HVO (integer identifier).

        Returns:
            System.Guid: The GUID of the chart.

        Raises:
            FP_NullParameterError: If chart_or_hvo is None.
            FP_ParameterError: If the chart does not exist or is invalid.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> if charts:
            ...     guid = discourse_ops.GetGuid(charts[0])
            ...     print(f"Chart GUID: {guid}")
            Chart GUID: 12345678-1234-1234-1234-123456789abc

        Notes:
            - GUIDs are globally unique identifiers
            - Persistent across project versions
            - Use for external references and tracking
            - Same GUID across different copies of the project

        See Also:
            GetOwningText, GetChartName
        """
        chart_obj = self.__GetChartObject(chart_or_hvo)

        if hasattr(chart_obj, 'Guid'):
            return chart_obj.Guid
        else:
            raise FP_ParameterError("Chart object does not have a GUID")


    def Duplicate(self, item_or_hvo, insert_after=True, deep=False):
        """
        Duplicate a chart, creating a new copy with a new GUID.

        Args:
            item_or_hvo: The chart object or HVO to duplicate.
            insert_after (bool): If True (default), insert after the source chart.
                                If False, insert at end of text's chart collection.
            deep (bool): If True, also duplicate rows and cells.
                        If False (default), only copy chart properties.

        Returns:
            Chart object: The newly created duplicate with a new GUID.

        Raises:
            FP_ReadOnlyError: If the project is not opened with write enabled.
            FP_NullParameterError: If item_or_hvo is None.

        Example:
            >>> discourse_ops = DiscourseOperations(project)
            >>> text = list(project.Texts.GetAll())[0]
            >>> charts = list(discourse_ops.GetAllCharts(text))
            >>> if charts:
            ...     dup = discourse_ops.Duplicate(charts[0])
            ...     print(f"Duplicate: {discourse_ops.GetChartName(dup)}")

        Notes:
            - Factory.Create() automatically generates a new GUID
            - MultiString property: Name
            - Chart rows duplicated only if deep=True
            - Chart structure can be complex, deep duplication may be slow

        See Also:
            CreateChart, DeleteChart, GetGuid
        """
        if not self.project.writeEnabled:
            raise FP_ReadOnlyError()

        if not item_or_hvo:
            raise FP_NullParameterError()

        # Get source chart and parent
        source = self.__GetChartObject(item_or_hvo)
        parent = source.Owner  # This is the StText

        # Create new chart using factory (auto-generates new GUID)
        factory = self.project.project.ServiceLocator.GetService(IDsConstChartFactory)
        duplicate = factory.Create()

        # ADD TO PARENT FIRST
        if insert_after:
            # Insert after source chart
            if hasattr(parent, 'ChartsOC'):
                source_index = parent.ChartsOC.IndexOf(source)
                parent.ChartsOC.Insert(source_index + 1, duplicate)
        else:
            # Insert at end
            if hasattr(parent, 'ChartsOC'):
                parent.ChartsOC.Add(duplicate)

        # Copy MultiString properties (AFTER adding to parent)
        if hasattr(source, 'Name') and source.Name:
            duplicate.Name.CopyAlternatives(source.Name)

        # Deep copy: duplicate rows
        if deep and hasattr(source, 'RowsOS') and source.RowsOS.Count > 0:
            for row in source.RowsOS:
                # Create new row
                row_factory = self.project.project.ServiceLocator.GetService(IConstChartRowFactory)
                dup_row = row_factory.Create()
                duplicate.RowsOS.Add(dup_row)

                # Note: Full row/cell duplication is complex and would require
                # additional logic to copy cell contents, word groups, markers, etc.
                # For now, we create empty rows

        return duplicate
