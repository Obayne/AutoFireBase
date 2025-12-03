"""Regression tests for UI workflows.

These tests verify end-to-end user workflows that have broken.
"""

import pytest


class TestProjectWorkflow:
    """Test project creation/loading workflows - POTENTIAL ISSUES."""

    @pytest.mark.xfail(reason="Project workflow needs end-to-end verification")
    def test_new_project_creation(self):
        """Test creating a new project from UI.

        Workflow:
        1. File > New Project
        2. Enter project details
        3. Create drawing
        4. Save project
        5. Reload project
        6. Verify all data persisted
        """
        pytest.skip("Needs UI automation or manual test protocol")

    @pytest.mark.xfail(reason="Import/export workflows uncovered by tests")
    def test_dxf_import_export(self):
        """Test DXF import/export round-trip.

        Workflow:
        1. Import DXF
        2. Verify geometry loaded
        3. Make modifications
        4. Export DXF
        5. Re-import and verify
        """
        pytest.skip("Needs real DXF test fixtures")


class TestDesignWorkflow:
    """Test AI-assisted design workflows - KNOWN BROKEN."""

    @pytest.mark.xfail(reason="SystemBuilder interface broken (occupancy_type)")
    def test_automated_design_workflow(self):
        """Test AI system design from UI.

        Workflow:
        1. Open design dialog
        2. Enter building parameters
        3. Run AI design
        4. Verify devices placed
        5. Verify coverage calculated
        """
        pytest.skip("Blocked by SystemBuilder.design_system() error")

    @pytest.mark.xfail(reason="Coverage calculation needs verification")
    def test_coverage_analysis(self):
        """Test that coverage analysis runs and displays correctly.

        Check strobe coverage, speaker coverage, heat detector coverage.
        """
        pytest.skip("Need coverage calculation test data")


class TestToolWorkflows:
    """Test interactive tool workflows - NEEDS VERIFICATION."""

    @pytest.mark.xfail(reason="Tool state management uncovered")
    def test_tool_switching(self):
        """Test switching between tools maintains state correctly.

        Verify:
        - Previous tool deactivates
        - New tool activates
        - Settings preserved
        - No memory leaks
        """
        pytest.skip("Needs tool state verification strategy")

    @pytest.mark.xfail(reason="Undo/redo broken or incomplete")
    def test_undo_redo_workflow(self):
        """Test undo/redo for various operations.

        Operations to test:
        - Draw operations
        - Edit operations
        - Delete operations
        - Property changes
        """
        pytest.skip("Needs undo stack implementation details")
