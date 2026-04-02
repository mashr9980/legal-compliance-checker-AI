# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Get all Python files in services and models directories
def get_all_py_files(directory):
    py_files = []
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    rel_path = os.path.relpath(os.path.join(root, file))
                    py_files.append(rel_path.replace('\\', '/'))
    return py_files

# Collect all data files
datas = [
    ('static', 'static'),
    ('services', 'services'),
    ('models', 'models'),
    ('main.py', '.'),
    ('config.py', '.'),
]

# Add requirements.txt if it exists
if os.path.exists('requirements.txt'):
    datas.append(('requirements.txt', '.'))

# Add any additional directories that might exist
for dir_name in ['templates', 'assets', 'reports', 'temp_files']:
    if os.path.exists(dir_name):
        datas.append((dir_name, dir_name))

a = Analysis(
    ['raia_app.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # FastAPI and Uvicorn dependencies
        'uvicorn',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.websockets',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'fastapi',
        'fastapi.responses',
        'fastapi.staticfiles',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'starlette',
        'starlette.applications',
        'starlette.middleware',
        'starlette.responses',
        'starlette.routing',
        'starlette.staticfiles',
        
        # Pydantic
        'pydantic',
        'pydantic.fields',
        'pydantic.main',
        'pydantic.types',
        'pydantic.validators',
        
        # HTTP and networking
        'aiohttp',
        'aiohttp.client',
        'aiohttp.connector',
        'requests',
        'urllib3',
        
        # PDF processing
        'pdfplumber',
        'pdfplumber.pdf',
        'pdfplumber.page',
        'pdfplumber.utils',
        
        # Report generation
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.units',
        'reportlab.lib.colors',
        'reportlab.platypus',
        'reportlab.graphics',
        
        # Standard library modules that might be missed
        'asyncio',
        'concurrent.futures',
        'multiprocessing',
        'threading',
        'queue',
        'socket',
        'webbrowser',
        'subprocess',
        'tempfile',
        'pathlib',
        'json',
        'uuid',
        'datetime',
        're',
        'logging',
        'traceback',
        
        # Our custom modules
        'config',
        'services',
        'services.document_processor',
        'services.compliance_checker',
        'services.report_generator',
        'services.intelligent_analyzer',
        'models',
        'models.schemas',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
    ],
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
    name='RAIA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/raia_icon.ico' if os.path.exists('assets/raia_icon.ico') else None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RAIA'
)