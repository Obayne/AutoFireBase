# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\boot.py'],
    pathex=['.'],
    binaries=[],
    datas=[('VERSION.txt', '.')],
    hiddenimports=['app', 'app.main', 'app.minwin', 'app.scene', 'app.device', 'app.catalog', 'app.tools', 'app.tools.draw', 'core.logger', 'core.logger_bridge', 'core.error_hook', 'updater.auto_update'],
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
    name='AutoFire_Debug',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='AutoFire_Debug',
)
