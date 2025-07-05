#!/usr/bin/env python3
"""
ZENIA PDF Processor - Setup and Deployment Script
This script helps set up the complete Streamlit web application.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_directory_structure():
    """Create the required directory structure"""
    print("📁 Creating directory structure...")
    
    directories = [
        '.streamlit',
        'assets',
        'temp',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✓ Created: {directory}/")

def create_config_files():
    """Create configuration files"""
    print("⚙️ Creating configuration files...")
    
    # Create .streamlit/config.toml
    config_toml = """
[global]
developmentMode = false

[server]
port = 8501
maxUploadSize = 200
enableCORS = false

[theme]
primaryColor = "#FF0050"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[browser]
gatherUsageStats = false
"""
    
    with open('.streamlit/config.toml', 'w') as f:
        f.write(config_toml.strip())
    print("   ✓ Created: .streamlit/config.toml")
    
    # Create .gitignore
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Streamlit
.streamlit/secrets.toml

# Temporary files
temp/
*.tmp
*.log

# OS
.DS_Store
Thumbs.db

# Output files
Output/
DISCARD/
*.pdf
*.xlsx
*.csv
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    print("   ✓ Created: .gitignore")

def create_requirements_file():
    """Create requirements.txt file"""
    print("📦 Creating requirements.txt...")
    
    requirements = """
streamlit>=1.28.0
pandas>=1.5.0
pillow>=9.0.0
PyMuPDF>=1.23.0
openpyxl>=3.1.0
python-dateutil>=2.8.0
watchdog>=3.0.0
altair>=4.2.0
numpy>=1.24.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements.strip())
    print("   ✓ Created: requirements.txt")

def create_dockerfile():
    """Create Dockerfile for containerized deployment"""
    print("🐳 Creating Dockerfile...")
    
    dockerfile_content = """
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p temp logs assets

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content.strip())
    print("   ✓ Created: Dockerfile")

def create_docker_compose():
    """Create docker-compose.yml for easy deployment"""
    print("🐳 Creating docker-compose.yml...")
    
    docker_compose_content = """
version: '3.8'

services:
  zenia-pdf-processor:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./temp:/app/temp
      - ./logs:/app/logs
    environment:
      - STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
      - STREAMLIT_THEME_PRIMARY_COLOR=#FF0050
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
"""
    
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose_content.strip())
    print("   ✓ Created: docker-compose.yml")

def create_launch_scripts():
    """Create platform-specific launch scripts"""
    print("🚀 Creating launch scripts...")
    
    # Windows batch file
    windows_script = """
@echo off
echo Starting ZENIA PDF Processor Web App...
echo.
echo Opening browser at http://localhost:8501
echo Press Ctrl+C to stop the application
echo.
python -m streamlit run streamlit_app.py --server.address localhost --server.port 8501
pause
"""
    
    with open('start_app.bat', 'w') as f:
        f.write(windows_script.strip())
    print("   ✓ Created: start_app.bat (Windows)")
    
    # Unix shell script
    unix_script = """#!/bin/bash
echo "Starting ZENIA PDF Processor Web App..."
echo ""
echo "Opening browser at http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo ""
python3 -m streamlit run streamlit_app.py --server.address localhost --server.port 8501
"""
    
    with open('start_app.sh', 'w') as f:
        f.write(unix_script.strip())
    
    # Make shell script executable
    try:
        os.chmod('start_app.sh', 0o755)
        print("   ✓ Created: start_app.sh (Linux/macOS)")
    except:
        print("   ⚠ Created: start_app.sh (you may need to make it executable)")

def create_readme():
    """Create a comprehensive README file"""
    print("📖 Creating README.md...")
    
    readme_content = """
# ZENIA PDF Label Processor - Web Edition

A modern web application for processing PDF shipping labels and packing slips, built with Streamlit.

## Features

- 📦 Batch PDF processing
- 🏷️ Automatic hazmat detection
- 📊 Real-time statistics dashboard
- 📱 Responsive web interface
- 🌙 Dark/light theme support
- 📥 Direct file downloads
- 🚀 Fast processing with progress tracking

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Open your browser:**
   Navigate to `http://localhost:8501`

### Using Launch Scripts

- **Windows:** Double-click `start_app.bat`
- **Linux/macOS:** Run `./start_app.sh`

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Or build manually:**
   ```bash
   docker build -t zenia-pdf-processor .
   docker run -p 8501:8501 zenia-pdf-processor
   ```

## File Structure

```
zenia-pdf-processor/
├── streamlit_app.py      # Main web application
├── order_processor.py    # Core processing logic
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-container setup
├── start_app.bat        # Windows launcher
├── start_app.sh         # Unix launcher
├── .streamlit/
│   └── config.toml      # Streamlit configuration
├── assets/              # Static assets
├── temp/                # Temporary files
└── logs/                # Application logs
```

## Usage

1. **Upload PDF files** containing shipping labels and packing slips
2. **Configure hazmat keywords** for automatic detection
3. **Click "Process"** to start batch processing
4. **Download results** including:
   - Sorted warehouse labels
   - Packingroom labels
   - Pick lists (Excel/CSV)

## Configuration

Edit `.streamlit/config.toml` to customize:
- Upload size limits
- Theme colors
- Server settings

## Deployment

### Streamlit Community Cloud

1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Deploy automatically

### Self-hosted

Use the provided Docker configuration for production deployment.

## Support

For issues or questions, check the processing log in the web interface.

---

**ZENIA PDF Processor** - Streamlining your shipping operations
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content.strip())
    print("   ✓ Created: README.md")

def install_dependencies():
    """Install Python dependencies"""
    print("🔧 Installing Python dependencies...")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("   ✓ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("   ❌ Failed to install dependencies")
        return False

def check_existing_files():
    """Check for existing core files"""
    required_files = ['streamlit_app.py', 'order_processor.py']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    return missing_files

def main():
    """Main setup function"""
    print("=" * 60)
    print("🏢 ZENIA PDF PROCESSOR - SETUP SCRIPT")
    print("=" * 60)
    print()
    
    # Check for existing core files
    missing_files = check_existing_files()
    if missing_files:
        print(f"❌ Missing core files: {', '.join(missing_files)}")
        print("Please ensure you have:")
        print("- streamlit_app.py (main application)")
        print("- order_processor.py (processing logic)")
        print()
        print("Copy these files to the current directory and run the setup again.")
        return
    
    print("✅ Core application files found!")
    print()
    
    # Create directory structure
    create_directory_structure()
    print()
    
    # Create configuration files
    create_config_files()
    print()
    
    # Create requirements file
    create_requirements_file()
    print()
    
    # Create Docker files
    create_dockerfile()
    create_docker_compose()
    print()
    
    # Create launch scripts
    create_launch_scripts()
    print()
    
    # Create README
    create_readme()
    print()
    
    # Install dependencies
    install_choice = input("Install Python dependencies now? (y/n): ").lower().strip()
    if install_choice == 'y':
        if install_dependencies():
            print()
            print("🎉 Setup completed successfully!")
            print()
            print("Next steps:")
            print("1. Run 'streamlit run streamlit_app.py' to start the app")
            print("2. Or use the launch scripts (start_app.bat/start_app.sh)")
            print("3. Open http://localhost:8501 in your browser")
        else:
            print("⚠️ Setup completed but dependencies failed to install")
            print("Please run 'pip install -r requirements.txt' manually")
    else:
        print("🎉 Setup completed!")
        print("Remember to install dependencies: pip install -r requirements.txt")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()