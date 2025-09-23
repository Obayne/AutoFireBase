"""Backend package (logic, I/O, services).

Hosts loaders, configuration, and headless logic extracted from legacy `db/` and `core/`.
"""

# Project loader API
from .project_loader import (
    ProjectLoader,
    ProjectSaver,
    ProjectManager,
    load_project,
    save_project,
    new_project,
    validate_project,
    get_last_error,
    project_manager
)

# Schema definitions
from .schema import (
    validate_autofire_project,
    upgrade_project_data,
    get_schema_version,
    get_schema_info,
    AUTOFIRE_SCHEMA_V1
)

# Catalog store (existing)
from .catalog_store import (
    get_catalog_path,
    seed_defaults,
    add_device,
    list_devices,
    get_device_specs
)

__all__ = [
    # Project management
    'ProjectLoader', 'ProjectSaver', 'ProjectManager',
    'load_project', 'save_project', 'new_project', 'validate_project', 'get_last_error',
    'project_manager',
    
    # Schema
    'validate_autofire_project', 'upgrade_project_data', 'get_schema_version',
    'get_schema_info', 'AUTOFIRE_SCHEMA_V1',
    
    # Catalog
    'get_catalog_path', 'seed_defaults', 'add_device', 'list_devices', 'get_device_specs'
]

