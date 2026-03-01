# backend.spec

# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_submodules

# Collect FastAPI / Pydantic dynamic imports
hiddenimports = collect_submodules('hapsira') + \
                collect_submodules('astrora') + \
                collect_submodules('astropy') + \
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
)