#
#   test_const_chart_tags.py
#
#   Class: TestConstChartTagsHarness
#          Regression coverage for the issue #26 ConstChartTag fix:
#          Create / Find / GetAll previously routed through
#          hasattr(chart, "TagsOC") which silently no-op'd because
#          IDsConstChart has no TagsOC. Chart markers actually live
#          project-wide in DiscourseDataOA.ChartMarkersOA.
#
#          We exercise the static contract (method shape) and the
#          private __GetChartMarkers resolver. We do NOT trigger
#          a live Create here -- creating a marker mutates the
#          shared test project's marker list, and the burndown ground
#          rule is to avoid cumulative pollution.
#
#   Platform: Python.NET
#             FieldWorks Version 9+
#
#   Copyright 2026
#

import inspect

import pytest


class TestConstChartTagsStaticContract:
    """
    Static introspection of the ConstChartTagOperations public
    surface after the issue #26 part 3 refactor.
    """

    def test_class_imports(self):
        from flexlibs2.code.Discourse.ConstChartTagOperations import (
            ConstChartTagOperations,
        )

        assert ConstChartTagOperations is not None

    def test_get_chart_markers_helper_resolves_via_discourse_data(self):
        """
        The private __GetChartMarkers helper must read
        DiscourseDataOA.ChartMarkersOA.PossibilitiesOS, not anything
        chart-local. We verify by inspecting the source of the
        underlying function (the helper is name-mangled).
        """
        from flexlibs2.code.Discourse.ConstChartTagOperations import (
            ConstChartTagOperations,
        )

        helper = inspect.getattr_static(
            ConstChartTagOperations,
            "_ConstChartTagOperations__GetChartMarkers",
        )
        src = inspect.getsource(helper)
        # Source should reference DiscourseDataOA and ChartMarkersOA.
        assert "DiscourseDataOA" in src, (
            "__GetChartMarkers should read DiscourseDataOA"
        )
        assert "ChartMarkersOA" in src, (
            "__GetChartMarkers should read ChartMarkersOA"
        )

    def test_module_no_longer_uses_hasattr_tagsoc_guard(self):
        """
        Confirm the previous hasattr(chart, "TagsOC")-guarded Add /
        iteration is gone from the entire module. The guard silently
        dropped the new tag (or returned empty results from Find /
        GetAll) whenever chart.TagsOC didn't exist (always, since
        IDsConstChart has no TagsOC). After the fix, all three
        methods route through DiscourseDataOA.ChartMarkersOA. We
        verify by reading the module source directly.
        """
        from flexlibs2.code.Discourse import ConstChartTagOperations as mod

        with open(mod.__file__, "r", encoding="utf-8") as fp:
            source = fp.read()

        # The whole-module check is conservative -- we just want to
        # know "no Create/Find/GetAll path still uses the broken
        # guard". If a future test wants finer-grained scoping it can
        # parse the AST.
        assert 'hasattr(chart, "TagsOC")' not in source, (
            "hasattr(chart, \"TagsOC\") guard still present in "
            "ConstChartTagOperations -- issue #26 fix did not land "
            "cleanly on all paths."
        )
        assert "ChartMarkersOA" in source, (
            "ChartMarkersOA reference missing -- expected at least "
            "one route through DiscourseDataOA.ChartMarkersOA "
            "after the issue #26 fix."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
