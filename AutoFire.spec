# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\boot.py'],
    pathex=['.'],
    binaries=[],
    datas=[('app', 'app'), ('core', 'core'), ('updater', 'updater')],
    hiddenimports=['app.main', 'app.minwin', 'app.tools.array', 'app.tools.draw', 'app.tools.dimension'],
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
