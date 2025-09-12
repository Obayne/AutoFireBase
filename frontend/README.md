# Frontend

Qt/PySide6 UI: windows, scenes, tools wiring, command handling, and input events.

Guidelines
- Keep business logic out of the UI where possible.
- Call into `cad_core` for geometry; call `backend` for I/O/services.

