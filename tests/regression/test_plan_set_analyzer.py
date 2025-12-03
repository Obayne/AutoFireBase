"""Regression tests for plan set analyzer functionality.

This feature should enable AI to analyze multiple DXF files simultaneously
for comprehensive project analysis.
"""

import pytest

# Skip Qt-dependent tests in non-GUI environment
pytestmark = pytest.mark.skipif(
    "not config.getoption('--run-gui-tests', default=False)",
    reason="GUI tests require --run-gui-tests flag",
)


class TestPlanSetAnalyzer:
    """Test plan set analyzer (multi-file DXF analysis)."""

    def test_plan_set_analyzer_exists(self):
        """Verify plan set analyzer module exists."""
        # Module now exists - test passes
        from app import plan_set_analyzer  # noqa: F401

        assert plan_set_analyzer is not None

    @pytest.mark.xfail(reason="Multi-file import integration pending")
    def test_import_multiple_dxf_files(self):
        """Test importing multiple DXF files as a plan set."""
        from app.plan_set_analyzer import import_plan_set

        # Should be able to import multiple DXF files
        files = ["floor_plan.dxf", "electrical.dxf", "fire_protection.dxf"]
        plan_set = import_plan_set(files)
        assert plan_set is not None
        assert plan_set.sheet_count == 3

    def test_batch_layer_analysis_exists(self):
        """Test that batch layer analysis function exists."""
        from app.plan_set_analyzer import analyze_layers_batch

        # Function exists
        assert analyze_layers_batch is not None

    def test_plan_set_analyzer_class_exists(self):
        """Test that PlanSetAnalyzer class exists."""
        from app.plan_set_analyzer import PlanSetAnalyzer

        analyzer = PlanSetAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, "analyze_plan_set")
        assert hasattr(analyzer, "format_analysis_report")
