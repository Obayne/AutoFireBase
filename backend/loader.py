from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Union


SCHEMA_VERSION = 1


@dataclass
class Element:
    type: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Project:
    name: str = "Untitled"
    units: str = "ft"
    elements: List[Element] = field(default_factory=list)


def to_dict(project: Project) -> Dict[str, Any]:
    return {
        "version": SCHEMA_VERSION,
        "name": project.name,
        "units": project.units,
        "elements": [asdict(e) for e in project.elements],
    }


def save(project: Union[Project, Dict[str, Any]]) -> str:
    """Serialize a Project (or compatible dict) to a JSON string.

    Ensures a schema version field is present at the top level.
    """

    if isinstance(project, Project):
        data = to_dict(project)
    else:
        data = dict(project)
        data.setdefault("version", SCHEMA_VERSION)
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def save_to_path(path: Union[str, Path], project: Union[Project, Dict[str, Any]]) -> None:
    path = Path(path)
    text = save(project)
    path.write_text(text, encoding="utf-8")


def _loads(text: str) -> Dict[str, Any]:
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Invalid project: root must be an object")
    if "version" not in data:
        # Treat as legacy; assign version 1
        data["version"] = 1
    return data


def load(obj: Union[str, Path]) -> Dict[str, Any]:
    """Load a project from a path or JSON string.

    Returns a dict with at least: version, name, units, elements.
    """

    if isinstance(obj, (str, Path)) and Path(obj).exists():
        text = Path(obj).read_text(encoding="utf-8")
        return _loads(text)
    # Assume string content
    return _loads(str(obj))


__all__ = [
    "SCHEMA_VERSION",
    "Element",
    "Project",
    "save",
    "save_to_path",
    "load",
]

