# -*- mode: python ; coding: utf-8 -*-
# LV CAD Unified Build Configuration


a = Analysis(
    ['lvcad.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('app', 'app'),
        ('frontend', 'frontend'),
        ('backend', 'backend'),
        ('cad_core', 'cad_core'),
        ('core', 'core'),
        ('updater', 'updater'),
        ('db', 'db'),
        ('autofire_layer_intelligence.py', '.'),
        ('fire_pilot.py', '.'),
        ('lvcad_pro.py', '.'),
        ('VERSION.txt', '.')
    ],
    hiddenimports=[
        'shapely','shapely.geometry',
        'app.main', 'app.minwin', 'app.boot',
        'frontend.app', 'frontend.controller',
        'autofire_layer_intelligence', 'fire_pilot',
        'app.tools.array', 'app.tools.draw', 'app.tools.dimension',
        'app.tools.text_tool', 'app.tools.trim_tool', 'app.tools.measure_tool',
        'app.tools.extend_tool', 'app.tools.fillet_tool', 'app.tools.fillet_radius_tool',
        'app.tools.rotate_tool', 'app.tools.mirror_tool', 'app.tools.scale_tool',
        'app.tools.chamfer_tool', 'app.layout', 'app.dxf_import',
        'PySide6', 'ezdxf', 'fitz', 'tkinter'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LV_CAD',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LV_CAD',
)
