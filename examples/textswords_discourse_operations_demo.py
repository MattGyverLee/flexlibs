#!/usr/bin/env python3
"""
Demonstration of DiscourseOperations for flexlibs
"""
from flexlibs import FLExProject, FLExInitialize, FLExCleanup

def demo_discourse():
    """Demonstrate DiscourseOperations functionality."""
    FLExInitialize()

    project = FLExProject()
    try:
        project.OpenProject("Kenyang-M", writeEnabled=True)
    except Exception as e:
        print(f"Cannot run demo - FLEx project not available: {e}")
        FLExCleanup()
        return

    print("=" * 60)
    print("DiscourseOperations Demonstration")
    print("=" * 60)

    # Test Read operations (GetAll, GetAllCharts, GetChartName, GetChartType)
    print("\n1. Testing Read operations:")
    try:
        # Get a text to work with
        texts = list(project.Texts.GetAll())
        if texts:
            text = texts[0]
            try:
                text_name = text.Name.BestAnalysisAlternative.Text
                print(f"   Working with text: {text_name}")
            except UnicodeEncodeError:
                print(f"   Working with text: [Unicode]")

            # Get all charts for the text
            charts = list(project.Discourse.GetAllCharts(text))
            print(f"   Found {len(charts)} chart(s) in text")

            # Display chart info
            count = 0
            for chart in charts:
                try:
                    name = project.Discourse.GetChartName(chart)
                    chart_type = project.Discourse.GetChartType(chart)
                    print(f"   Chart: {name} ({chart_type})")
                except UnicodeEncodeError:
                    print(f"   Chart: [Unicode] (chart_type)")
                count += 1
                if count >= 3:
                    break

            # Get rows if chart exists
            if charts:
                chart = charts[0]
                rows = project.Discourse.GetRows(chart)
                row_count = project.Discourse.GetRowCount(chart)
                print(f"   Chart has {row_count} row(s)")
        else:
            print("   No texts found in project")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Test Create operations (CreateChart - check existence first)
    print("\n2. Testing Create operations:")
    print("   NOTE: Not creating charts to preserve data")
    print("   CreateChart() would create a new constituent or discourse chart")
    print("   AddRow() would add rows to the chart structure")

    # Test Update operations (SetChartName)
    print("\n3. Testing Update operations:")
    print("   NOTE: Not modifying charts to preserve data")
    print("   SetChartName() would update chart names")
    print("   SetCellContent() would update chart cell content")

    # Test Delete operations (NOT demonstrated to preserve data)
    print("\n4. Delete operations available but not demonstrated")
    print("   DeleteChart() and DeleteRow() available but skipped for safety")

    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)

    project.CloseProject()
    FLExCleanup()

if __name__ == "__main__":
    demo_discourse()
