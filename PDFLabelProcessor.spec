# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all required modules
hiddenimports = []
hiddenimports += collect_submodules('customtkinter')
hiddenimports += ['fitz', 'PyMuPDF']  # Explicitly include PyMuPDF modules
hiddenimports += ['openpyxl']
hiddenimports += ['PIL', 'PIL._tkinter_finder', 'PIL.Image']  # Include Pillow modules

# Define the analysis
a = Analysis(
    ['pdf_processor_app.py'],  # Main script
    pathex=[],
    binaries=[],
    datas=[
        ('logo.png', '.'),  # App logo
        ('app_icon.png', '.'),  # App icon
        ('hazmat.png', '.'),  # Hazmat image for labels
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# Create the PYZ archive
pyz = PYZ(a.pure)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PDFLabelProcessor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want a console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',  # Windows icon
)

# macOS bundle
import sys
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='PDFLabelProcessor.app',
        icon='app_icon.icns',  # macOS icon
        bundle_identifier=None,
    )