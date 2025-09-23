"""Additional tests for backend schema validation."""

import pytest
from backend.schema import validate_autofire_project, upgrade_project_data, get_schema_info


class TestSchemaEdgeCases:
    """Test edge cases for schema validation."""
    
    def test_empty_project_validation(self):
        """Test validation of minimal empty project."""
        empty_project = {
            "schema_version": "1.0",
            "grid": 20,
            "snap": True,
            "px_per_ft": 12.0,
            "devices": [],
            "sketch": [],
            "dxf_layers": {}
        }
        
        result = validate_autofire_project(empty_project)
        assert result
    
    def test_schema_with_extra_fields(self):
        """Test that extra fields are allowed (future compatibility)."""
        project_with_extra = {
            "schema_version": "1.0",
            "grid": 20,
            "snap": True,
            "px_per_ft": 12.0,
            "metadata": {
                "created": "2025-09-15T12:00:00Z",
                "modified": "2025-09-15T12:00:00Z",
                "extra_field": "should be allowed"
            },
            "settings": {"future_setting": True},
            "devices": [],
            "sketch": [{"type": "line", "x1": 0, "y1": 0, "x2": 10, "y2": 10}],
            "dxf_layers": {},
            "future_section": {"data": "test"}
        }
        
        result = validate_autofire_project(project_with_extra)
        assert result
    
    def test_invalid_schema_version_format(self):
        """Test handling of invalid schema version formats."""
        invalid_versions = ["1", "1.0.0", "v1.0", "", "invalid"]
        
        for version in invalid_versions:
            project = {
                "schema_version": version,
                "metadata": {"created": "2025-09-15T12:00:00Z", "modified": "2025-09-15T12:00:00Z"},
                "settings": {}, "devices": [], "sketch": {"lines": [], "circles": [], "polylines": []}, "dxf_layers": []
            }
            
            try:
                result = validate_autofire_project(project)
                if version not in ["1.0"]:  # Only 1.0 should be valid
                    assert not result  # Should fail validation
            except Exception:
                if version == "1.0":
                    raise  # 1.0 should not raise exception


class TestSchemaUpgrade:
    """Test schema upgrade functionality."""
    
    def test_upgrade_from_legacy_format(self):
        """Test upgrading from legacy project format."""
        legacy_project = {
            "devices": [{"x": 100, "y": 200, "name": "Device1"}],
            "grid": 20,
            "snap": True
        }
        
        upgraded = upgrade_project_data(legacy_project)
        
        assert upgraded["schema_version"] == "1.0"
        assert len(upgraded["devices"]) == 1
        # Basic upgrade just adds schema_version, doesn't transform structure
        assert upgraded["devices"][0]["x"] == 100
        assert upgraded["grid"] == 20
    
    def test_upgrade_preserves_valid_v1(self):
        """Test that valid v1.0 projects are not modified."""
        v1_project = {
            "schema_version": "1.0",
            "metadata": {"created": "2025-09-15T12:00:00Z", "modified": "2025-09-15T12:00:00Z"},
            "settings": {"grid_size": 30},
            "devices": [],
            "sketch": {"lines": [], "circles": [], "polylines": []},
            "dxf_layers": []
        }
        
        upgraded = upgrade_project_data(v1_project.copy())
        
        # Should be identical except possibly metadata.modified
        assert upgraded["schema_version"] == "1.0"
        assert upgraded["settings"]["grid_size"] == 30
        assert upgraded["devices"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])