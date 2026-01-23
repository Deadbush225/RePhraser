# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for RePhraser portable executable

block_cipher = None

a = Analysis(
    ['src/rephraser/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/rephraser/dark.qss', 'rephraser'),
        ('src/rephraser/login.qss', 'rephraser'),
        ('src/rephraser/Rephraser.ico', 'rephraser'),
        ('src/rephraser/Rephraser.png', 'rephraser'),
        ('src/rephraser/images', 'rephraser/images'),
    ],
    hiddenimports=[
        'PyQt5.sip',
        'rephraser.lib.DarkPallete',
        'rephraser.lib.AuthorComboBox',
        'rephraser.lib.RibbonWidget',
        'rephraser.lib.TextEdit',
        'rephraser.RePhraser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RePhraser-Portable',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/rephraser/Rephraser.ico',
)