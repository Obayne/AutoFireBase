from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class AppSettings:
    version: int = 1
    theme: str = "light"
    recent_projects: list[str] = field(default_factory=list)
    db_path: str = "db/catalog.sqlite3"


DEFAULT_SETTINGS = AppSettings()


def load_settings(path: str | Path, defaults: Optional[AppSettings] = None) -> AppSettings:
    p = Path(path)
    if not p.exists():
        return defaults or AppSettings()
    data = json.loads(p.read_text(encoding="utf-8"))
    base = asdict(defaults or AppSettings())
    base.update({k: v for k, v in data.items() if k in base})
    return AppSettings(**base)


def save_settings(settings: AppSettings, path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(asdict(settings), indent=2, sort_keys=True), encoding="utf-8")


def add_recent_project(settings: AppSettings, project_path: str, max_items: int = 10) -> AppSettings:
    items = [project_path] + [p for p in settings.recent_projects if p != project_path]
    settings.recent_projects = items[:max_items]
    return settings

