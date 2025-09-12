# .autofire Project Schema (v1)

Top-level fields
- `version` (int): schema version (1)
- `name` (string): project name
- `units` (string): e.g., `ft`
- `elements` (array): list of drawing/model elements

Element
- `type` (string): semantic type (e.g., `line`, `device`, `underlay`)
- `data` (object): type-specific payload

Notes
- Unknown fields must be preserved by loaders.
- Future versions may add fields; loaders should default missing fields.
- Binary underlays (e.g., DXF/PDF) are referenced by path; not embedded.
