# backend.spec

# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_submodules

from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo, FixedFileInfo, StringFileInfo, StringTable,
    StringStruct, VarFileInfo, VarStruct
)

# Collect FastAPI / Pydantic dynamic imports
hiddenimports = collect_submodules('astropy') + \
                collect_submodules('motor') + \
                collect_submodules('pymongo') + \
                collect_submodules('fastapi') + \
                collect_submodules('pydantic') + \
                collect_submodules('uvicorn')

block_cipher = None

a = Analysis(
    ['start.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('..\\astro', 'astro'),
        ('common', 'common'),
        ('routers', 'routers'),
        ('schemas', 'schemas'),
        ('tasks', 'tasks'),
        ('main.py', '.'),
    ],
    hiddenimports=hiddenimports,
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

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(0, 1, 0, 0),
        prodvers=(0, 1, 0, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable(
                '040904B0',
                [
                    StringStruct('CompanyName', 'Alessio Negri'),
                    StringStruct('FileDescription', 'Spacecraft Dynamics Lab Backend Service'),
                    StringStruct('FileVersion', '0.1.0'),
                    StringStruct('InternalName', 'SpacecraftDynamicsLabService'),
                    StringStruct('LegalCopyright', '© 2026 Alessio Negri'),
                    StringStruct('OriginalFilename', 'SpacecraftDynamicsLabService.exe'),
                    StringStruct('ProductName', 'Spacecraft Dynamics Lab'),
                    StringStruct('ProductVersion', '0.1.0')
                ]
            )
        ]),
        VarFileInfo([VarStruct('Translation', [1033, 1200])])
    ]
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='SpacecraftDynamicsLabService',
    debug=False,
    strip=False,
    upx=True,
    console=True,
    icon='SpacecraftDynamicsLab.ico',
    version=version_info
)