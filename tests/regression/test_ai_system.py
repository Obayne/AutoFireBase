"""Regression tests for AI system functionality.

These tests document broken AI features discovered during manual testing.
"""

import pytest


class TestSystemBuilderRegression:
    """Test SystemBuilder AI design functionality - KNOWN BROKEN."""

    @pytest.mark.xfail(reason="occupancy_type argument removed/renamed - needs investigation")
    def test_design_system_with_occupancy_type(self):
        """Test that design_system accepts occupancy_type parameter.

        Error seen in app:
        TypeError: SystemBuilder.design_system() got an unexpected keyword
        argument 'occupancy_type'

        This broke the AI design workflow in the UI.
        """
        # This test documents the interface that SHOULD exist
        # Once we find SystemBuilder, we'll implement the actual test
        pytest.skip("Need to locate SystemBuilder class to write proper test")

    @pytest.mark.xfail(reason="AI system integration needs verification")
    def test_ai_assistant_stiffness(self):
        """Test that AI assistant provides flexible, conversational responses.

        User feedback: AI is very 'stiff' and rigid.
        Need to verify AI model selection, prompt engineering, temperature settings.
        """
        pytest.skip("Need to define metrics for 'stiff' vs 'flexible' AI behavior")


class TestDatabaseIntegration:
    """Test database persistence - KNOWN ISSUES."""

    @pytest.mark.xfail(reason="Database items reported missing")
    def test_project_persistence(self):
        """Test that projects save and load correctly.

        User feedback: Database items missing.
        Need to verify:
        - Project save/load
        - Device catalog persistence
        - Settings persistence
        """
        pytest.skip("Need to identify specific missing database items")

    @pytest.mark.xfail(reason="Data integrity issues reported")
    def test_device_catalog_integrity(self):
        """Test that device catalog maintains data integrity.

        Check for missing devices, corrupt data, failed migrations.
        """
        pytest.skip("Need catalog schema documentation to write test")


class TestCADFunctionalityRegression:
    """Test CAD drawing/editing features - KNOWN ISSUES."""

    @pytest.mark.xfail(reason="CAD portion needs a lot of work per user feedback")
    def test_drawing_tools_complete(self):
        """Test that all drawing tools work correctly.

        User feedback: CAD portion needs a lot of work.
        Need to verify each tool: line, arc, circle, polyline, etc.
        """
        pytest.skip("Need to enumerate all broken CAD tools")

    @pytest.mark.xfail(reason="Editing workflows broken")
    def test_edit_operations(self):
        """Test that edit operations work: trim, extend, fillet, offset, etc.

        Verify that geometry modifications don't corrupt objects.
        """
        pytest.skip("Need to test each edit operation individually")

    @pytest.mark.xfail(reason="Selection and osnap issues")
    def test_object_selection(self):
        """Test that object selection and snapping work reliably.

        Check osnap modes, selection filters, multi-select.
        """
        pytest.skip("Need to define selection test scenarios")
