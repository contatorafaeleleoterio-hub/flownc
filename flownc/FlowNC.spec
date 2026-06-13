# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\USUARIO\\Desktop\\Projetos\\Sistema_verificador_codigos_cnc\\flownc\\main.py'],
    pathex=['C:\\Users\\USUARIO\\Desktop\\Projetos\\Sistema_verificador_codigos_cnc\\flownc'],
    binaries=[],
    datas=[
        ('ui/style.qss', 'ui'),
        ('assets/fonts', 'assets/fonts'),
        ('assets/logo', 'assets/logo'),
        ('data_default', 'data_default'),
    ],
    hiddenimports=[],
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
    name='FlowNC',
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
    icon='assets\\logo\\flownc.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FlowNC',
)
