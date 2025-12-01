"""Database interface scaffolding.
We keep the app running without any DB by default.
Later we can implement a SQLite store or remote API.
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class DeviceRecord:
    id: int | None
    name: str
    symbol: str
    manufacturer: str
    part_number: str
    type: str
    attributes: dict[str, Any]


class CatalogStore:
    """Read-only catalog interface."""

    def list_devices(self) -> list[DeviceRecord]:
        ...

    def search(self, text: str) -> list[DeviceRecord]:
        ...


class ProjectStore:
    """Per-project persistence interface (devices, wires, metadata)."""

    def save_snapshot(self, data: dict) -> None:
        ...

    def load_snapshot(self) -> dict:
        ...
