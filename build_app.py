# build_app.py
# Script to build ZENIA PDF Processor application with proper icon support

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_app():
    print("Starting ZENIA PDF Processor build process...")
    
    # Ensure all required packages are installed
    print("Installing required packages...")
    packages = [
        "pyinstaller",
        "customtkinter",
        "pillow",
        "PyMuPDF",
        "openpyxl"
    ]
    
    for package in packages:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package])
    
    print("Packages installed successfully.")
    
    # Create a spec file with proper configuration
    spec_content = """# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = []
hiddenimports += collect_submodules('customtkinter')
hiddenimports += ['fitz', 'PyMuPDF']  # Explicitly include PyMuPDF modules
hiddenimports += ['openpyxl']

a = Analysis(
    ['pdf_processor_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.png', '.'), 
        ('app_icon.png', '.'), 
        ('hazmat.png', '.')
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',  # Specify icon here
)

# For macOS
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='PDFLabelProcessor.app',
        icon='app_icon.icns',  # macOS icon
        bundle_identifier=None,
    )
"""
    
    # Write the spec file
    with open("ZENIA_PDF_Processor.spec", "w") as f:
        f.write(spec_content)
    
    print("Spec file created.")
    
    # Check if icon files exist, and create/convert if not
    check_and_create_icons()
    
    # Run PyInstaller
    print("Building application with PyInstaller...")
    subprocess.run(["pyinstaller", "--clean", "ZENIA_PDF_Processor.spec"])
    
    print("Build completed. Check the 'dist' folder for the application.")
    
    # Create Inno Setup script for Windows installer
    if sys.platform == 'win32':
        create_inno_setup_script()
        print("Inno Setup script (ZeniaSetup.iss) has been created.")
        print("You can now run Inno Setup Compiler to create the installer.")

def check_and_create_icons():
    # Check for Windows icon
    if not os.path.exists("app_icon.ico"):
        print("Icon file app_icon.ico not found.")
        if os.path.exists("app_icon.png"):
            try:
                # Try to convert PNG to ICO if PIL is available
                from PIL import Image
                print("Converting PNG to ICO...")
                img = Image.open("app_icon.png")
                img.save("app_icon.ico")
                print("Icon created: app_icon.ico")
            except:
                print("Warning: Could not convert app_icon.png to ICO format.")
                print("Please create app_icon.ico manually for Windows builds.")
    
    # Check for macOS icon
    if sys.platform == 'darwin' and not os.path.exists("app_icon.icns"):
        print("Icon file app_icon.icns not found.")
        if os.path.exists("app_icon.png"):
            try:
                # Try to convert PNG to ICNS if on macOS
                print("Attempting to convert PNG to ICNS...")
                os.makedirs("icon.iconset", exist_ok=True)
                
                # Generate different icon sizes
                sizes = [16, 32, 64, 128, 256, 512, 1024]
                for size in sizes:
                    subprocess.run([
                        "sips", "-z", str(size), str(size),
                        "app_icon.png", "--out", f"icon.iconset/icon_{size}x{size}.png"
                    ])
                    subprocess.run([
                        "sips", "-z", str(size*2), str(size*2),
                        "app_icon.png", "--out", f"icon.iconset/icon_{size}x{size}@2x.png"
                    ])
                
                # Create icns file
                subprocess.run(["iconutil", "-c", "icns", "icon.iconset"])
                
                # Cleanup
                shutil.rmtree("icon.iconset")
                print("Icon created: app_icon.icns")
            except:
                print("Warning: Could not convert app_icon.png to ICNS format.")
                print("Please create app_icon.icns manually for macOS builds.")

def create_inno_setup_script():
    inno_script = """#define MyAppName "ZENIA PDF Processor"
#define MyAppVersion "1.4"
#define MyAppPublisher "ZENIA"
#define MyAppURL "https://www.zenia.com"
#define MyAppExeName "PDFLabelProcessor.exe"

[Setup]
AppId={{15C9D640-0B94-42A1-8F35-F3A7C8A1D5A3}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=ZENIA_PDF_Processor_Setup_v1.4
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\\{#MyAppExeName}
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\PDFLabelProcessor.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{group}\\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
"""
    
    with open("ZeniaSetup.iss", "w") as f:
        f.write(inno_script)

if __name__ == "__main__":
    build_app()