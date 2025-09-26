# Paper Space (Current State)

This is not just a mock-up — there is a minimal, working Paper Space implementation in the app. It is intentionally small and evolving.

What exists today
- Page frame: `app/layout.py:PageFrame` draws sheet border and printable area using real page sizes (Letter, A-series, Arch) and margins.
- Title block: `app/layout.py:TitleBlock` draws a simple metadata box (project, address, sheet, date, by) in the lower-right.
- Viewport item: `app/layout.py:ViewportItem` renders the Model scene into a rectangle on the page. Features:
  - Context menu: set scale factor, center on current model view, fit model to viewport, lock/unlock.
  - Drag to position; lock to prevent edits.
- Menu hooks (in `app/main.py`):
  - Layouts menu entries: Add Page Frame, Add/Update Title Block, Page Setup (stub), Add Viewport, Switch to Paper/Model Space.

Gaps and TODOs
- Page setup dialog is a placeholder.
- TitleBlock API alignment: use `set_meta()` (current) vs. `update_content()` used in some paths.
- Persistence: saving/loading of layouts and viewports is limited; define `LayoutDTO` and `ViewportDTO` for project round-trips.
- Multi-viewport support and locked scale validation are basic.
- Export: PDF/PNG output from Paper Space needs polish (DPI/scale verification).

How to try it
- Add a page frame: Layouts > Add Page Frame.
- Add a viewport: Switch to Paper Space, then Layouts > Add Viewport. Right-click the viewport to set scale, center, or fit.
- Add/update title block: Layouts > Add/Update Title Block.

Code entry points
- `app/layout.py` (PageFrame, TitleBlock, ViewportItem)
- `app/main.py` layout actions (search for: Add Page Frame, Add Viewport, Title Block, Page Setup)

Notes
- This doc tracks the evolving feature; update as behavior changes or stabilizes.
