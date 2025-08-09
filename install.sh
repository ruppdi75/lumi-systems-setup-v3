#!/bin/bash
#
# Lumi-Setup v2.0 Installation Script
#

set -e

echo "🚀 Installing Lumi-Setup v2.0..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

# Update package lists
echo "📦 Updating package lists..."
apt update

# Install Python 3 and pip if not already installed
echo "🐍 Installing Python dependencies..."
apt install -y python3 python3-pip python3-venv

# Install system dependencies for PyQt6
echo "🖥️ Installing GUI dependencies..."
apt install -y python3-pyqt6 python3-pyqt6.qtcore python3-pyqt6.qtgui python3-pyqt6.qtwidgets

# Alternative: Install via pip if system packages not available
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "📥 Installing PyQt6 via pip..."
    pip3 install PyQt6
fi

# Install additional Python dependencies
echo "📚 Installing Python packages..."
pip3 install -r requirements.txt

# Make main script executable
chmod +x main.py

# Create desktop entry
echo "🖥️ Creating desktop entry..."
cat > /usr/share/applications/lumi-setup.desktop << EOF
[Desktop Entry]
Name=Lumi-Setup v2.0
Comment=AnduinOS Software Installer
Exec=python3 $(pwd)/main.py
Icon=$(pwd)/resources/icons/lumi-setup.png
Terminal=false
Type=Application
Categories=System;Settings;
StartupNotify=true
EOF

# Create symbolic link for command line access
echo "🔗 Creating command line shortcut..."
ln -sf "$(pwd)/main.py" /usr/local/bin/lumi-setup

echo "✅ Installation completed!"
echo ""
echo "You can now run Lumi-Setup v2.0:"
echo "  • From applications menu: Search for 'Lumi-Setup'"
echo "  • From command line: lumi-setup"
echo "  • Directly: python3 $(pwd)/main.py"
echo ""
echo "⚠️  Note: The application requires root privileges for system installations."
