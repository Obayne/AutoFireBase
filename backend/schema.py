# AutoFire Project Schema Definition (v1.0)
# Defines the JSON schema and validation for .autofire project files

import json
from typing import Dict, Any, List, Optional, Union
from jsonschema import validate, ValidationError


# AutoFire Project Schema v1.0
AUTOFIRE_SCHEMA_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "AutoFire Project Format",
    "description": "Schema for .autofire project files",
    "type": "object",
    "properties": {
        "schema_version": {
            "type": "string",
            "description": "Version of the schema",
            "enum": ["1.0"]
        },
        "app_version": {
            "type": "string",
            "description": "Version of AutoFire that saved this file"
        },
        "created": {
            "type": "string",
            "format": "date-time",
            "description": "ISO timestamp when the project was created"
        },
        "modified": {
            "type": "string", 
            "format": "date-time",
            "description": "ISO timestamp when the project was last modified"
        },
        "metadata": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "author": {"type": "string"},
                "project_number": {"type": "string"},
                "client": {"type": "string"}
            },
            "additionalProperties": True
        },
        "grid": {
            "type": "integer",
            "minimum": 2,
            "description": "Grid size in pixels"
        },
        "snap": {
            "type": "boolean",
            "description": "Whether snap is enabled"
        },
        "px_per_ft": {
            "type": "number",
            "minimum": 1.0,
            "description": "Scale factor: pixels per foot"
        },
        "snap_step_in": {
            "type": "number",
            "minimum": 0.0,
            "description": "Snap step in inches"
        },
        "grid_opacity": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Grid opacity (0.0-1.0)"
        },
        "grid_width_px": {
            "type": "number",
            "minimum": 0.0,
            "description": "Grid line width in pixels"
        },
        "grid_major_every": {
            "type": "integer",
            "minimum": 1,
            "description": "Major grid line frequency"
        },
        "devices": {
            "type": "array",
            "items": {
                "$ref": "#/definitions/device"
            },
            "description": "Array of placed devices"
        },
        "underlay_transform": {
            "$ref": "#/definitions/transform_matrix",
            "description": "Transformation matrix for underlay"
        },
        "dxf_layers": {
            "type": "object",
            "patternProperties": {
                ".*": {
                    "$ref": "#/definitions/dxf_layer"
                }
            },
            "description": "DXF layer states"
        },
        "sketch": {
            "type": "array",
            "items": {
                "$ref": "#/definitions/sketch_item"
            },
            "description": "Sketch geometry"
        },
        "wires": {
            "type": "array",
            "items": {
                "$ref": "#/definitions/wire"
            },
            "description": "Wire connections"
        }
    },
    "required": ["schema_version", "grid", "snap", "px_per_ft", "devices"],
    "additionalProperties": True,
    "definitions": {
        "device": {
            "type": "object",
            "properties": {
                "x": {"type": "number"},
                "y": {"type": "number"},
                "symbol": {"type": "string"},
                "name": {"type": "string"},
                "manufacturer": {"type": "string"},
                "part_number": {"type": "string"},
                "label_text": {"type": "string"},
                "label_offset": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "number"},
                        "y": {"type": "number"}
                    },
                    "required": ["x", "y"]
                },
                "coverage": {
                    "$ref": "#/definitions/coverage"
                }
            },
            "required": ["x", "y", "symbol", "name"]
        },
        "coverage": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["none", "strobe", "speaker", "smoke"]
                },
                "mount": {
                    "type": "string", 
                    "enum": ["ceiling", "wall"]
                },
                "computed_radius_ft": {"type": "number"},
                "px_per_ft": {"type": "number"},
                "params": {
                    "type": "object",
                    "properties": {
                        "candela": {"type": "number"},
                        "spacing_ft": {"type": "number"},
                        "db_ref": {"type": "number"},
                        "target_db": {"type": "number"}
                    }
                }
            }
        },
        "transform_matrix": {
            "type": "object",
            "properties": {
                "m11": {"type": "number"},
                "m12": {"type": "number"},
                "m13": {"type": "number"},
                "m21": {"type": "number"},
                "m22": {"type": "number"},
                "m23": {"type": "number"},
                "m31": {"type": "number"},
                "m32": {"type": "number"},
                "m33": {"type": "number"}
            },
            "required": ["m11", "m12", "m13", "m21", "m22", "m23", "m31", "m32", "m33"]
        },
        "dxf_layer": {
            "type": "object",
            "properties": {
                "visible": {"type": "boolean"},
                "locked": {"type": "boolean"},
                "print": {"type": "boolean"},
                "color": {"type": ["string", "null"]},
                "orig_color": {"type": ["string", "null"]}
            },
            "required": ["visible", "locked", "print"]
        },
        "sketch_item": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["line", "rect", "circle", "poly", "text"]
                }
            },
            "required": ["type"],
            "oneOf": [
                {
                    "properties": {
                        "type": {"const": "line"},
                        "x1": {"type": "number"},
                        "y1": {"type": "number"},
                        "x2": {"type": "number"},
                        "y2": {"type": "number"}
                    },
                    "required": ["type", "x1", "y1", "x2", "y2"]
                },
                {
                    "properties": {
                        "type": {"const": "rect"},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "w": {"type": "number"},
                        "h": {"type": "number"}
                    },
                    "required": ["type", "x", "y", "w", "h"]
                },
                {
                    "properties": {
                        "type": {"const": "circle"},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "r": {"type": "number"}
                    },
                    "required": ["type", "x", "y", "r"]
                },
                {
                    "properties": {
                        "type": {"const": "poly"},
                        "pts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"}
                                },
                                "required": ["x", "y"]
                            },
                            "minItems": 2
                        }
                    },
                    "required": ["type", "pts"]
                },
                {
                    "properties": {
                        "type": {"const": "text"},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "text": {"type": "string"}
                    },
                    "required": ["type", "x", "y", "text"]
                }
            ]
        },
        "wire": {
            "type": "object",
            "properties": {
                "ax": {"type": "number"},
                "ay": {"type": "number"},
                "bx": {"type": "number"},
                "by": {"type": "number"}
            },
            "required": ["ax", "ay", "bx", "by"]
        }
    }
}


def validate_autofire_project(data: Dict[str, Any]) -> bool:
    """
    Validate a project data dictionary against the AutoFire schema.
    
    Args:
        data: Project data dictionary
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If validation fails
    """
    validate(data, AUTOFIRE_SCHEMA_V1)
    return True


def get_schema_version() -> str:
    """Get the current schema version."""
    return "1.0"


def upgrade_project_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upgrade project data from older versions to current schema.
    
    Args:
        data: Project data dictionary (may be older version)
        
    Returns:
        Upgraded project data dictionary
    """
    # For now, just ensure schema_version is set
    if "schema_version" not in data:
        data["schema_version"] = "1.0"
    
    # Add missing required fields with defaults
    if "devices" not in data:
        data["devices"] = []
    
    return data


def get_schema_info() -> Dict[str, Any]:
    """Get information about the current schema."""
    return {
        "version": "1.0",
        "description": "AutoFire Project Format Schema",
        "required_fields": ["schema_version", "grid", "snap", "px_per_ft", "devices"],
        "optional_fields": [
            "app_version", "created", "modified", "metadata",
            "snap_step_in", "grid_opacity", "grid_width_px", "grid_major_every",
            "underlay_transform", "dxf_layers", "sketch", "wires"
        ]
    }