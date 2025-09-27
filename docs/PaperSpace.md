# Paper Space (Current State + Plan)

This is not a mock-up — there is a minimal, working Paper Space implementation in the app, and we will evolve it toward a CAD‑style layout workspace with true separation from ModelSpace, per‑window scale, layer overrides, and high‑fidelity exports.

What exists today
- Page frame: `app/layout.py:PageFrame` draws sheet border and printable area using real page sizes (Letter, A‑series, Arch) and margins.
- Title block: `app/layout.py:TitleBlock` renders a simple metadata box (project, address, sheet, date, by) in the lower-right.
- Viewport item: `app/layout.py:ViewportItem` renders the Model scene into a rectangle on the page. Features:
  - Context menu: set scale factor, center on current model view, fit model to viewport, lock/unlock.
  - Drag to position; lock to prevent edits.
- Menu hooks (in `app/main.py`): Add Page Frame, Add/Update Title Block, Page Setup (stub), Add Viewport, Switch to Paper/Model Space.

Design principles
- Separate workspaces: ModelSpace for modeling; PaperSpace for layout only.
- Keep UI uncluttered: a slide‑out “Layout Drawer” provides layout controls without crowding the canvas.
- Smooth flow: single‑key toggles; sensible defaults; export from the same place you lay out.

Planned PaperSpace features (incremental)
- Workspace separation
  - Explicit workspace state and tool gating: modeling tools disabled in PaperSpace; layout tools active.
  - Keep current Model/Paper font indicator and status messages.
- Layout Drawer (slick, lightweight)
  - Sheet: page size/orientation (Architectural and Engineering), margins, title block metadata.
  - Windows (CAD viewports): list with lock/visible toggles, scale presets (architectural and engineering), fit/center, per‑window layer overrides.
  - Reports: insert/update Device Legend, BOM, Riser Diagram, Operational Matrix as PaperSpace items.
  - Export: PDF (vector), DXF (true paperspace + VIEWPORT), PNG; “Flatten layers” toggle.
- Per‑window layer overrides
  - Visibility overrides applied during window rendering only (no global side effects).
- Exports
  - DXF: paperspace layout via ezdxf with VIEWPORT entities; preserve layers by default; optional flatten (single layer).
  - PDF: vector output; scaled to page; flattened by default.
  - PNG: page raster at chosen DPI.
- Persistence
  - `LayoutDTO`, `ViewportDTO` including per‑window layer state; round‑trip in project saves; safe migration.

Paper & scale presets
- Architectural sizes: Arch A–E, Letter/Tabloid; Engineering: ANSI A–E.
- Architectural scales: 1/8"=1', 3/16"=1', 1/4"=1', 3/8"=1', 1/2"=1', 3/4"=1', 1"=1', 1½"=1', 3"=1'.
- Engineering scales: 1"=10', 20', 30', 40', 50', 60'.

How to try it (today)
- Add a page frame: Layouts > Add Page Frame.
- Add a viewport: Switch to Paper Space, then Layouts > Add Viewport. Right‑click the viewport to set scale, center, or fit.
- Add/update title block: Layouts > Add/Update Title Block.

Code entry points
- `app/layout.py` (PageFrame, TitleBlock, ViewportItem)
- `app/main.py` layout actions (search for: Add Page Frame, Add Viewport, Title Block, Page Setup)

Notes
- This doc tracks the evolving feature; it will be updated as behavior stabilizes.
