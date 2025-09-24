from __future__ import annotations

# Frontend-side adapter for backend OpsService.
# Passive wiring: provides an adapter class and optional tool registration
# without touching the active UI. Import in UI code when ready to expose.
from dataclasses import dataclass

from backend.geom_repo import EntityRef, InMemoryGeomRepo
from backend.models import CircleDTO, PointDTO
from backend.ops_service import OpsService

from .tool_registry import ToolSpec, register


@dataclass
class OpsAdapter:
    repo: InMemoryGeomRepo
    svc: OpsService

    def extend_segment_to_circle(
        self, seg_id: str, center_x: float, center_y: float, r: float, end: str = "b"
    ) -> bool:
        ref = EntityRef("segment", seg_id)
        circle = CircleDTO(center=PointDTO(center_x, center_y), r=float(r))
        return self.svc.extend_segment_to_circle(ref, circle, end=end)


def build_adapter(repo: InMemoryGeomRepo | None = None) -> OpsAdapter:
    repo = repo or InMemoryGeomRepo()
    svc = OpsService(repo=repo)
    return OpsAdapter(repo=repo, svc=svc)


def register_ops_tools(prefix: str = "ops") -> None:
    """Register passive tools for ops; safe to call multiple times."""

    def factory():
        # Factory returns a new adapter instance; UI can bind actions to its methods.
        return build_adapter()

    register(
        ToolSpec(
            name="Extend Segment to Circle",
            command=f"{prefix}.extend_to_circle",
            shortcut=None,
            icon=None,
            factory=factory,
        )
    )


__all__ = ["OpsAdapter", "build_adapter", "register_ops_tools"]
