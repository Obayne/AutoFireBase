# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\boot.py'],
    pathex=['.'],
    binaries=[],
    datas=[('app', 'app'), ('core', 'core'), ('updater', 'updater')],
    hiddenimports=['shapely','shapely.geometry','app.main', 'app.minwin', 'app.tools.array', 'app.tools.draw', 'app.tools.dimension', 'app.tools.text_tool', 'app.tools.trim_tool', 'app.tools.measure_tool', 'app.tools.extend_tool', 'app.tools.fillet_tool', 'app.tools.fillet_radius_tool', 'app.tools.rotate_tool', 'app.tools.mirror_tool', 'app.tools.scale_tool', 'app.tools.chamfer_tool', 'app.layout', 'app.dxf_import'],
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
    name='AutoFire',
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
    name='AutoFire',
)

