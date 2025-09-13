AutoFire DXF Template

Purpose
- Quick-start DXF with layers and a couple of generic NFPA-style blocks.
- Neutral units: 1 drawing unit = 1 foot (DXF $INSUNITS=2).

Layers (predefined)
- AF-UNDERLAY   (gray)    — architectural underlays (PDF/DXF traces)
- AF-WIRE       (green)   — wiring routes
- AF-ANNO       (white)   — annotations
- AF-DEV-SMOKE  (cyan)    — smoke detectors
- AF-DEV-HEAT   (orange)  — heat detectors
- AF-DEV-PULL   (yellow)  — pull stations
- AF-AV-STROBE  (magenta) — strobes
- AF-AV-HORN    (red)     — horns
- AF-AV-SPKR    (blue)    — speakers

Blocks (predefined)
- AF_BLK_SMOKE — simple circle symbol (insert on AF-DEV-SMOKE)
- AF_BLK_STROBE_WALL — small square with cross (insert on AF-AV-STROBE)

How to use (LibreCAD/QCAD/AutoCAD LT)
1) Open AF_Template_R2013.dxf.
2) Import or trace your underlay on layer AF-UNDERLAY.
3) Place devices by inserting the provided blocks on their device layers.
4) Draw wiring on AF-WIRE. Use ByLayer colors/weights for consistency.
5) Save as DXF R2013 or R2007 to use as underlay in the app.

