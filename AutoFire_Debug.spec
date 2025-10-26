# -*- mode: python ; coding: utf-8 -*-

try:
    from backend import branding as _branding
    _product = getattr(_branding, 'PRODUCT_NAME', 'AutoFire')
except Exception:
    _product = 'AutoFire'

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('VERSION.txt', '.'), ('frontend', 'frontend'), ('backend', 'backend'), ('cad_core', 'cad_core'), ('db', 'db'), ('core', 'core'), ('updater', 'updater')],
    hiddenimports=['frontend.app', 'frontend.controller', 'frontend.windows.model_space', 'frontend.windows.paperspace', 'frontend.panels.panel_system_builder', 'frontend.panels.panel_device_palette', 'backend.catalog', 'backend.persistence', 'cad_core.geometry', 'cad_core.tools', 'db.loader', 'core.logger', 'core.logger_bridge', 'core.error_hook', 'updater.auto_update'],
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
    name=f"{_product}_Debug",
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
    name=f"{_product}_Debug",
)
