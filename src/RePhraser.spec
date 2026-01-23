# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
      ("rephraser/images", "rephraser/images"),
      ("rephraser/dark.qss", "rephraser"),
      ("rephraser/Rephraser.ico", "rephraser"),
      ("rephraser/Rephraser.png", "rephraser")
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
# ---------------------------------------------------------
# IN ONE-FILE MODE, WE ADD BINARIES AND DATA HERE
# ---------------------------------------------------------
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
# ---------------------------------------------------------
    exclude_binaries=False,
    name='RePhraser',
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
