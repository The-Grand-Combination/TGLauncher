# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.win32.versioninfo import VSVersionInfo, FixedFileInfo, StringFileInfo, StringTable, StringStruct

a = Analysis(
    ['launcher.py'],
    pathex=['', '/scr', '/scr/icon.ico'],
    binaries=[],
    datas=[],
    hiddenimports=['PyQt6'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='The Greater Launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='scr/icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=VSVersionInfo(
        ffi=FixedFileInfo(
            filevers=(1, 0, 0, 0),
            prodvers=(1, 0, 0, 0),
            mask=0x3f,
            flags=0x0,
            OS=0x40004,
            fileType=0x1,
            subtype=0x0,
            date=(0, 0)
        ),
        kids=[
            StringFileInfo(
                [
                    StringTable(
                        u'040904B0',
                        [StringStruct(u'CompanyName', u'TGC Modding Team'),
                         StringStruct(u'FileDescription', u'The Greater Launcher'),
                         StringStruct(u'FileVersion', u'1.2.1'),
                         StringStruct(u'InternalName', u'TGLauncher'),
                         StringStruct(u'OriginalFilename', u'The Greater Launcher.exe'),
                         StringStruct(u'ProductName', u'The Greater Launcher'),
                         StringStruct(u'ProductVersion', u'1.2.1')])
                ]
            ),
        ]
    ),
    uac_admin=False,
)