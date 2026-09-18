# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

sys.setrecursionlimit(5000)

block_cipher = None

# Collect static files and package data files
datas = [
    ('app/static', 'app/static'),
]

datas += collect_data_files('presidio_analyzer', include_py_files=True)
datas += collect_data_files('presidio_anonymizer', include_py_files=True)
datas += collect_data_files('uk_core_news_sm', include_py_files=True)
datas += collect_data_files('uk_core_news_trf', include_py_files=True)
datas += collect_data_files('spacy', include_py_files=True)
datas += collect_data_files('spacy_curated_transformers', include_py_files=True)
datas += collect_data_files('curated_transformers', include_py_files=True)
datas += collect_data_files('curated_tokenizers', include_py_files=True)

# Copy package metadata (including entry_points.txt for spacy plugins & architectures)
datas += copy_metadata('spacy_curated_transformers')
datas += copy_metadata('curated_transformers')
datas += copy_metadata('curated_tokenizers')
datas += copy_metadata('uk_core_news_trf')
datas += copy_metadata('uk_core_news_sm')
datas += copy_metadata('spacy')

# Hidden imports for FastAPI, Uvicorn, Presidio, spaCy, Pydantic, etc.
hiddenimports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'starlette',
    'starlette.responses',
    'starlette.staticfiles',
    'starlette.routing',
    'pydantic',
    'pydantic_core',
    'presidio_analyzer',
    'presidio_anonymizer',
    'spacy',
    'spacy.pipeline',
    'spacy.lang.uk',
    'spacy.lang.en',
    'spacy_curated_transformers',
    'spacy_curated_transformers.pipeline',
    'spacy_curated_transformers.pipeline.transformer',
    'spacy_curated_transformers.models',
    'spacy_curated_transformers.models.listeners',
    'spacy_curated_transformers.models.architectures',
    'spacy_curated_transformers.tokenization',
    'spacy_legacy',
    'spacy_loggers',
    'curated_transformers',
    'curated_tokenizers',
    'uk_core_news_sm',
    'uk_core_news_trf',
    'torch',
    'thinc',
    'pymorphy3',
    'phonenumbers',
    'regex',
]

hiddenimports += collect_submodules('app')
hiddenimports += collect_submodules('presidio_analyzer')
hiddenimports += collect_submodules('presidio_anonymizer')
hiddenimports += collect_submodules('uk_core_news_sm')
hiddenimports += collect_submodules('uk_core_news_trf')
hiddenimports += collect_submodules('spacy_curated_transformers')
hiddenimports += collect_submodules('curated_transformers')
hiddenimports += collect_submodules('curated_tokenizers')

a = Analysis(
    ['run_server.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
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
    [],
    exclude_binaries=True,
    name='PIIUA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PIIUA',
)
