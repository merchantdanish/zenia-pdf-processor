#!/usr/bin/env python3
"""
ZENIA PDF Processor - Web App Launcher
This script helps launch the Streamlit web application with proper configuration.
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'pandas', 
        'pillow',
        'pymupdf',
        'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(packages):
    """Install missing dependencies"""
    print(f"Installing missing packages: {', '.join(packages)}")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Please install manually:")
        print(f"pip install {' '.join(packages)}")
        return False

def check_files():
    """Check if required files exist"""
    required_files = [
        'streamlit_app.py',
        'order_processor.py'
    ]
    
    missing_files = []
    current_dir = Path.cwd()
    
    for file in required_files:
        if not (current_dir / file).exists():
            missing_files.append(file)
    
    return missing_files

def launch_streamlit():
    """Launch the Streamlit application"""
    print("🚀 Launching ZENIA PDF Processor Web App...")
    print("📍 The app will open in your default browser")
    print("🔗 Local URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Launch streamlit
        process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
            '--server.address', 'localhost',
            '--server.port', '8501',
            '--browser.gatherUsageStats', 'false'
        ])
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open('http://localhost:8501')
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
        process.terminate()
    except Exception as e:
        print(f"❌ Error launching application: {e}")

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🏢 ZENIA PDF PROCESSOR - WEB APP LAUNCHER")
    print("=" * 60)
    
    # Check if required files exist
    missing_files = check_files()
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all files are in the current directory:")
        print("- streamlit_app.py")
        print("- order_processor.py")
        print("- hazmat.png (optional)")
        print("- logo.png (optional)")
        return
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"📦 Missing packages detected: {', '.join(missing_packages)}")
        install_choice = input("Install missing packages automatically? (y/n): ").lower().strip()
        
        if install_choice == 'y':
            if not install_dependencies(missing_packages):
                return
        else:
            print("Please install missing packages manually and try again.")
            return
    else:
        print("✅ All dependencies are installed!")
    
    # Launch the application
    print("\n" + "=" * 60)
    launch_streamlit()

if __name__ == "__main__":
    main()