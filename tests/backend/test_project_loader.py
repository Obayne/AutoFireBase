"""Tests for backend schema and project loader functionality."""

import json
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime

import pytest
from jsonschema import ValidationError

# Import backend modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.schema import (
    validate_autofire_project,
    upgrade_project_data,
    get_schema_version,
    get_schema_info,
    AUTOFIRE_SCHEMA_V1
)

from backend.project_loader import (
    ProjectLoader,
    ProjectSaver,
    ProjectManager,
    load_project,
    save_project,
    new_project,
    validate_project
)


class TestSchema:
    """Test the AutoFire project schema."""
    
    def test_schema_version(self):
        """Test schema version is correctly set."""
        assert get_schema_version() == "1.0"
        
        info = get_schema_info()
        assert info["version"] == "1.0"
        assert "required_fields" in info
        assert "optional_fields" in info
    
    def test_minimal_valid_project(self):
        """Test minimal valid project passes validation."""
        minimal_project = {
            "schema_version": "1.0",
            "grid": 50,
            "snap": True,
            "px_per_ft": 12.0,
            "devices": []
        }
        
        # Should not raise exception
        assert validate_autofire_project(minimal_project) is True
    
    def test_complete_valid_project(self):
        """Test complete project with all fields passes validation."""
        complete_project = {
            "schema_version": "1.0",
            "app_version": "0.6.8-cad-base",
            "created": "2024-01-01T12:00:00",
            "modified": "2024-01-01T12:00:00",
            "metadata": {
                "title": "Test Project",
                "author": "Test User"
            },
            "grid": 50,
            "snap": True,
            "px_per_ft": 12.0,
            "snap_step_in": 6.0,
            "grid_opacity": 0.25,
            "grid_width_px": 1.0,
            "grid_major_every": 5,
            "devices": [
                {
                    "x": 100.0,
                    "y": 200.0,
                    "symbol": "STR",
                    "name": "Strobe",
                    "manufacturer": "Test Mfg",
                    "part_number": "STR-001",
                    "label_text": "S1",
                    "label_offset": {"x": 10.0, "y": -5.0},
                    "coverage": {
                        "mode": "strobe",
                        "mount": "ceiling",
                        "computed_radius_ft": 25.0,
                        "px_per_ft": 12.0,
                        "params": {
                            "candela": 95.0
                        }
                    }
                }
            ],
            "underlay_transform": {
                "m11": 1.0, "m12": 0.0, "m13": 0.0,
                "m21": 0.0, "m22": 1.0, "m23": 0.0,
                "m31": 0.0, "m32": 0.0, "m33": 1.0
            },
            "dxf_layers": {
                "Layer1": {
                    "visible": True,
                    "locked": False,
                    "print": True,
                    "color": "#FF0000",
                    "orig_color": "#FF0000"
                }
            },
            "sketch": [
                {
                    "type": "line",
                    "x1": 0.0, "y1": 0.0,
                    "x2": 100.0, "y2": 100.0
                },
                {
                    "type": "circle",
                    "x": 50.0, "y": 50.0, "r": 25.0
                }
            ],
            "wires": [
                {
                    "ax": 10.0, "ay": 10.0,
                    "bx": 50.0, "by": 50.0
                }
            ]
        }
        
        assert validate_autofire_project(complete_project) is True
    
    def test_invalid_schema_version(self):
        """Test invalid schema version raises validation error."""
        invalid_project = {
            "schema_version": "2.0",  # Invalid version
            "grid": 50,
            "snap": True,
            "px_per_ft": 12.0,
            "devices": []
        }
        
        with pytest.raises(ValidationError):
            validate_autofire_project(invalid_project)
    
    def test_missing_required_fields(self):
        """Test missing required fields raise validation errors."""
        # Missing grid
        with pytest.raises(ValidationError):
            validate_autofire_project({
                "schema_version": "1.0",
                "snap": True,
                "px_per_ft": 12.0,
                "devices": []
            })
        
        # Missing devices
        with pytest.raises(ValidationError):
            validate_autofire_project({
                "schema_version": "1.0",
                "grid": 50,
                "snap": True,
                "px_per_ft": 12.0
            })
    
    def test_device_validation(self):
        """Test device object validation."""
        project_with_invalid_device = {
            "schema_version": "1.0",
            "grid": 50,
            "snap": True,
            "px_per_ft": 12.0,
            "devices": [
                {
                    "x": 100.0,
                    "y": 200.0,
                    # Missing required 'symbol' and 'name'
                }
            ]
        }
        
        with pytest.raises(ValidationError):
            validate_autofire_project(project_with_invalid_device)
    
    def test_sketch_validation(self):
        """Test sketch geometry validation."""
        # Valid sketch items
        project_with_sketch = {
            "schema_version": "1.0",
            "grid": 50,
            "snap": True,
            "px_per_ft": 12.0,
            "devices": [],
            "sketch": [
                {"type": "line", "x1": 0, "y1": 0, "x2": 10, "y2": 10},
                {"type": "rect", "x": 0, "y": 0, "w": 50, "h": 30},
                {"type": "circle", "x": 25, "y": 25, "r": 10},
                {"type": "text", "x": 10, "y": 10, "text": "Label"},
                {"type": "poly", "pts": [{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 5, "y": 10}]}
            ]
        }
        
        assert validate_autofire_project(project_with_sketch) is True
        
        # Invalid sketch item
        project_with_invalid_sketch = {
            "schema_version": "1.0",
            "grid": 50,
            "snap": True,
            "px_per_ft": 12.0,
            "devices": [],
            "sketch": [
                {"type": "invalid_type"}  # Invalid type
            ]
        }
        
        with pytest.raises(ValidationError):
            validate_autofire_project(project_with_invalid_sketch)
    
    def test_upgrade_project_data(self):
        """Test upgrading older project data."""
        old_project = {
            "grid": 50,
            "snap": True,
            "px_per_ft": 12.0
            # Missing schema_version and devices
        }
        
        upgraded = upgrade_project_data(old_project)
        
        assert upgraded["schema_version"] == "1.0"
        assert "devices" in upgraded
        assert upgraded["devices"] == []
        assert validate_autofire_project(upgraded) is True


class TestProjectLoader:
    """Test the ProjectLoader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.loader = ProjectLoader()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_valid_project(self):
        """Test loading a valid .autofire file."""
        # Create test project data
        project_data = {
            "schema_version": "1.0",
            "grid": 50,
            "snap": True,
            "px_per_ft": 12.0,
            "devices": []
        }
        
        # Create .autofire file
        autofire_path = self.temp_dir / "test.autofire"
        with zipfile.ZipFile(autofire_path, 'w') as zf:
            zf.writestr('project.json', json.dumps(project_data))
        
        # Load and validate
        loaded_data = self.loader.load_project(autofire_path)
        assert loaded_data is not None
        assert loaded_data["schema_version"] == "1.0"
        assert loaded_data["grid"] == 50
        assert self.loader.last_error is None
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file returns None."""
        nonexistent_path = self.temp_dir / "nonexistent.autofire"
        result = self.loader.load_project(nonexistent_path)
        
        assert result is None
        assert "not found" in self.loader.last_error.lower()
    
    def test_load_invalid_extension(self):
        """Test loading file with wrong extension."""
        txt_path = self.temp_dir / "test.txt"
        txt_path.write_text("dummy content")
        
        result = self.loader.load_project(txt_path)
        assert result is None
        assert "invalid file extension" in self.loader.last_error.lower()
    
    def test_load_corrupted_zip(self):
        """Test loading corrupted ZIP file."""
        corrupted_path = self.temp_dir / "corrupted.autofire"
        corrupted_path.write_text("This is not a ZIP file")
        
        result = self.loader.load_project(corrupted_path)
        assert result is None
        assert "invalid or corrupted" in self.loader.last_error.lower()
    
    def test_load_missing_project_json(self):
        """Test loading .autofire without project.json."""
        autofire_path = self.temp_dir / "no_project.autofire"
        with zipfile.ZipFile(autofire_path, 'w') as zf:
            zf.writestr('other.txt', 'dummy content')
        
        result = self.loader.load_project(autofire_path)
        assert result is None
        assert "missing project.json" in self.loader.last_error.lower()
    
    def test_validate_project_data(self):
        """Test project data validation method."""
        valid_data = {
            "schema_version": "1.0",
            "grid": 50,
            "snap": True,
            "px_per_ft": 12.0,
            "devices": []
        }
        
        assert self.loader.validate_project_data(valid_data) is True
        assert self.loader.last_error is None
        
        invalid_data = {"invalid": "data"}
        assert self.loader.validate_project_data(invalid_data) is False
        assert self.loader.last_error is not None


class TestProjectSaver:
    """Test the ProjectSaver class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.saver = ProjectSaver()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_valid_project(self):
        """Test saving a valid project."""
        project_data = {
            "grid": 50,
            "snap": True,
            "px_per_ft": 12.0,
            "devices": []
        }
        
        save_path = self.temp_dir / "saved_project.autofire"
        result = self.saver.save_project(project_data, save_path)
        
        assert result is True
        assert save_path.exists()
        assert self.saver.last_error is None
        
        # Verify saved content
        with zipfile.ZipFile(save_path, 'r') as zf:
            assert 'project.json' in zf.namelist()
            saved_data = json.loads(zf.read('project.json').decode('utf-8'))
            assert saved_data["schema_version"] == "1.0"
            assert saved_data["grid"] == 50
            assert "created" in saved_data
            assert "modified" in saved_data
    
    def test_save_auto_add_extension(self):
        """Test that .autofire extension is added automatically."""
        project_data = {
            "grid": 50,
            "snap": True,
            "px_per_ft": 12.0,
            "devices": []
        }
        
        save_path = self.temp_dir / "no_extension"
        result = self.saver.save_project(project_data, save_path)
        
        assert result is True
        expected_path = self.temp_dir / "no_extension.autofire"
        assert expected_path.exists()
    
    def test_save_invalid_project(self):
        """Test saving invalid project data fails."""
        invalid_data = {"invalid": "data"}  # Missing required fields
        
        save_path = self.temp_dir / "invalid.autofire"
        result = self.saver.save_project(invalid_data, save_path)
        
        assert result is False
        assert not save_path.exists()
        assert "validation failed" in self.saver.last_error.lower()


class TestProjectManager:
    """Test the ProjectManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ProjectManager()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_new_project(self):
        """Test creating a new project."""
        project_data = self.manager.new_project()
        
        assert project_data["schema_version"] == "1.0"
        assert "devices" in project_data
        assert project_data["devices"] == []
        assert validate_autofire_project(project_data) is True
    
    def test_load_save_roundtrip(self):
        """Test loading and saving a project preserves data."""
        # Create and save project
        original_data = self.manager.new_project()
        original_data["metadata"] = {"title": "Test Project"}
        
        save_path = self.temp_dir / "roundtrip.autofire"
        save_success = self.manager.save_project(original_data, save_path)
        assert save_success is True
        
        # Load project
        loaded_data = self.manager.load_project(save_path)
        assert loaded_data is not None
        
        # Compare (excluding timestamps)
        for key in ["schema_version", "grid", "snap", "px_per_ft", "devices"]:
            assert loaded_data[key] == original_data[key]
        
        assert loaded_data["metadata"]["title"] == "Test Project"
    
    def test_is_project_modified(self):
        """Test project modification detection."""
        original_data = self.manager.new_project()
        
        # Initially not modified (same data)
        assert not self.manager.is_project_modified(original_data)
        
        # Modify data
        modified_data = original_data.copy()
        modified_data["grid"] = 100
        
        assert self.manager.is_project_modified(modified_data)


class TestConvenienceFunctions:
    """Test the convenience functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_new_project_function(self):
        """Test new_project convenience function."""
        project_data = new_project()
        assert validate_project(project_data) is True
    
    def test_save_load_functions(self):
        """Test save_project and load_project convenience functions."""
        project_data = new_project()
        project_data["metadata"] = {"title": "Convenience Test"}
        
        save_path = self.temp_dir / "convenience.autofire"
        
        # Save
        save_result = save_project(project_data, save_path)
        assert save_result is True
        
        # Load
        loaded_data = load_project(save_path)
        assert loaded_data is not None
        assert loaded_data["metadata"]["title"] == "Convenience Test"


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])