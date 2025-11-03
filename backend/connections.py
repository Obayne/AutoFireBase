from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class ConnectionMethod(str, Enum):
    """Methods to connect NAC panels to FACPs and similar links.

    Mirrors common FireCAD patterns:
    - REVERSE_POLARITY: FACP NAC drives NAC panel input (DC reverse polarity)
    - VENDOR_BUS: Proprietary bus (e.g., P-LINK, RUI, V-LINK)
    - REMOTE_SYNC: Remote sync terminals used as activation signal
    - RELAY_CONTACT: Dry relay output to input, plus monitor zone for troubles
    """

    REVERSE_POLARITY = "reverse_polarity"
    VENDOR_BUS = "vendor_bus"
    REMOTE_SYNC = "remote_sync"
    RELAY_CONTACT = "relay_contact"


@dataclass(frozen=True)
class Connection:
    """A logical connection between a source circuit and a target endpoint.

    The minimal common data we need to drive riser exports and validation.
    """

    method: ConnectionMethod
    source_panel: str
    source_circuit: str
    target_id: str  # panel id or device id
    target_kind: Literal["panel", "device"] = "panel"
    vendor_bus_name: str | None = None  # e.g., "P-LINK", "RUI", "V-LINK"

    def label(self) -> str:
        if self.method == ConnectionMethod.VENDOR_BUS and self.vendor_bus_name:
            return (
                f"{self.source_panel}:{self.source_circuit} → "
                f"{self.target_kind}:{self.target_id} ({self.vendor_bus_name})"
            )
        return (
            f"{self.source_panel}:{self.source_circuit} → "
            f"{self.target_kind}:{self.target_id} ({self.method.value})"
        )
