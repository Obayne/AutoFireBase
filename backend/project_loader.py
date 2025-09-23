# AutoFire Project Loader/Saver API
# Provides high-level save/load functionality for .autofire projects

import json
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from jsonschema import ValidationError

from .schema import (
    validate_autofire_project, 
    upgrade_project_data, 
    get_schema_version,
    AUTOFIRE_SCHEMA_V1
)


class ProjectLoader:
    """Handles loading and validation of .autofire project files."""
    
    def __init__(self):
        self.last_error = None
    
    def load_project(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Load an .autofire project file.
        
        Args:
            file_path: Path to the .autofire file
            
        Returns:
            Project data dictionary if successful, None if failed
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.last_error = f"File not found: {file_path}"
                return None
            
            if not file_path.suffix.lower() == '.autofire':
                self.last_error = f"Invalid file extension. Expected .autofire, got: {file_path.suffix}"
                return None
            
            # Read the ZIP file
            with zipfile.ZipFile(file_path, 'r') as zf:
                # Check for required project.json
                if 'project.json' not in zf.namelist():
                    self.last_error = "Invalid .autofire file: missing project.json"
                    return None
                
                # Load project data
                project_data = json.loads(zf.read('project.json').decode('utf-8'))
            
            # Upgrade data if from older version
            project_data = upgrade_project_data(project_data)
            
            # Validate against schema
            try:
                validate_autofire_project(project_data)
            except ValidationError as e:
                self.last_error = f"Project validation failed: {e.message}"
                return None
            
            self.last_error = None
            return project_data
            
        except zipfile.BadZipFile:
            self.last_error = "Invalid or corrupted .autofire file"
            return None
        except json.JSONDecodeError as e:
            self.last_error = f"Invalid JSON in project file: {e}"
            return None
        except Exception as e:
            self.last_error = f"Unexpected error loading project: {e}"
            return None
    
    def validate_project_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate project data against schema without loading from file.
        
        Args:
            data: Project data dictionary
            
        Returns:
            True if valid, False otherwise
        """
        try:
            validate_autofire_project(data)
            self.last_error = None
            return True
        except ValidationError as e:
            self.last_error = f"Validation failed: {e.message}"
            return False
        except Exception as e:
            self.last_error = f"Validation error: {e}"
            return False


class ProjectSaver:
    """Handles saving .autofire project files."""
    
    def __init__(self):
        self.last_error = None
    
    def save_project(self, project_data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
        """
        Save project data to an .autofire file.
        
        Args:
            project_data: Project data dictionary
            file_path: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            # Ensure .autofire extension
            if file_path.suffix.lower() != '.autofire':
                file_path = file_path.with_suffix('.autofire')
            
            # Prepare project data
            enhanced_data = self._enhance_project_data(project_data)
            
            # Validate before saving
            try:
                validate_autofire_project(enhanced_data)
            except ValidationError as e:
                self.last_error = f"Project data validation failed: {e.message}"
                return False
            
            # Create parent directory if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to ZIP file
            with zipfile.ZipFile(file_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                # Write project.json
                project_json = json.dumps(enhanced_data, indent=2, ensure_ascii=False)
                zf.writestr('project.json', project_json.encode('utf-8'))
                
                # TODO: Add support for embedded assets (images, PDFs) in future versions
            
            self.last_error = None
            return True
            
        except Exception as e:
            self.last_error = f"Error saving project: {e}"
            return False
    
    def _enhance_project_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance project data with metadata and schema information.
        
        Args:
            data: Original project data
            
        Returns:
            Enhanced project data
        """
        enhanced = data.copy()
        
        # Add schema version
        enhanced["schema_version"] = get_schema_version()
        
        # Add timestamps
        now = datetime.now().isoformat()
        if "created" not in enhanced:
            enhanced["created"] = now
        enhanced["modified"] = now
        
        # Add app version (TODO: get from app constants)
        enhanced["app_version"] = "0.6.8-cad-base"
        
        return enhanced


class ProjectManager:
    """High-level project management API."""
    
    def __init__(self):
        self.loader = ProjectLoader()
        self.saver = ProjectSaver()
        self.current_project_path = None
        self.current_project_data = None
    
    def new_project(self) -> Dict[str, Any]:
        """
        Create a new empty project.
        
        Returns:
            Empty project data dictionary
        """
        self.current_project_path = None
        self.current_project_data = {
            "schema_version": get_schema_version(),
            "grid": 50,
            "snap": True,
            "px_per_ft": 12.0,
            "snap_step_in": 0.0,
            "grid_opacity": 0.25,
            "grid_width_px": 0.0,
            "grid_major_every": 5,
            "devices": [],
            "underlay_transform": {
                "m11": 1.0, "m12": 0.0, "m13": 0.0,
                "m21": 0.0, "m22": 1.0, "m23": 0.0,
                "m31": 0.0, "m32": 0.0, "m33": 1.0
            },
            "dxf_layers": {},
            "sketch": [],
            "wires": []
        }
        return self.current_project_data.copy()
    
    def load_project(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Load a project from file.
        
        Args:
            file_path: Path to .autofire file
            
        Returns:
            Project data if successful, None otherwise
        """
        data = self.loader.load_project(file_path)
        if data:
            self.current_project_path = Path(file_path)
            self.current_project_data = data
        return data
    
    def save_project(self, project_data: Dict[str, Any], file_path: Optional[Union[str, Path]] = None) -> bool:
        """
        Save project data.
        
        Args:
            project_data: Project data to save
            file_path: Output path (uses current path if None)
            
        Returns:
            True if successful
        """
        if file_path:
            save_path = Path(file_path)
        elif self.current_project_path:
            save_path = self.current_project_path
        else:
            self.saver.last_error = "No file path specified and no current project path"
            return False
        
        success = self.saver.save_project(project_data, save_path)
        if success:
            self.current_project_path = save_path
            self.current_project_data = project_data.copy()
        return success
    
    def save_project_as(self, project_data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
        """
        Save project to a new file.
        
        Args:
            project_data: Project data to save
            file_path: New file path
            
        Returns:
            True if successful
        """
        return self.save_project(project_data, file_path)
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error message from loader or saver."""
        return self.loader.last_error or self.saver.last_error
    
    def is_project_modified(self, current_data: Dict[str, Any]) -> bool:
        """
        Check if current project data differs from saved version.
        
        Args:
            current_data: Current project state
            
        Returns:
            True if modified
        """
        if not self.current_project_data:
            return True
        
        # Simple comparison - exclude timestamps
        saved = self.current_project_data.copy()
        current = current_data.copy()
        
        # Remove timestamps for comparison
        for data in [saved, current]:
            data.pop('created', None)
            data.pop('modified', None)
        
        return saved != current


# Global project manager instance
project_manager = ProjectManager()


# Convenience functions
def load_project(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """Load an .autofire project file."""
    return project_manager.load_project(file_path)


def save_project(project_data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
    """Save project data to an .autofire file."""
    return project_manager.save_project(project_data, file_path)


def new_project() -> Dict[str, Any]:
    """Create a new empty project."""
    return project_manager.new_project()


def validate_project(data: Dict[str, Any]) -> bool:
    """Validate project data against schema."""
    loader = ProjectLoader()
    return loader.validate_project_data(data)


def get_last_error() -> Optional[str]:
    """Get the last error message."""
    return project_manager.get_last_error()