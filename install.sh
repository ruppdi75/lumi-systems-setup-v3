#!/bin/bash
#
# Lumi-Setup v2.0 Universal Installation Script
# Compatible with AnduinOS, Ubuntu Desktop, and other Debian-based systems
#

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Error handling
set -e
trap 'log_error "Installation failed at line $LINENO. Exit code: $?"' ERR

log_info "Installing Lumi-Setup v2.0..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root (use sudo)"
    exit 1
fi

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION=$VERSION_ID
    log_info "Detected distribution: $PRETTY_NAME"
else
    log_warning "Cannot detect distribution, assuming Ubuntu/Debian"
    DISTRO="ubuntu"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install package with error handling
install_package() {
    local package="$1"
    local description="$2"
    
    log_info "Installing $description ($package)..."
    
    if apt install -y "$package" 2>/dev/null; then
        log_success "$description installed successfully"
        return 0
    else
        log_warning "Failed to install $package via apt"
        return 1
    fi
}

# Update package lists
log_info "Updating package lists..."
if apt update; then
    log_success "Package lists updated"
else
    log_warning "Failed to update package lists, continuing anyway..."
fi

# Install Python 3 and pip
log_info "Installing Python dependencies..."
install_package "python3" "Python 3"
install_package "python3-pip" "Python pip"
install_package "python3-venv" "Python virtual environment"

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
log_info "Python version: $PYTHON_VERSION"

if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    log_success "Python version is compatible (3.8+)"
else
    log_error "Python 3.8 or higher is required"
    exit 1
fi

# Install PyQt6 - Try multiple methods
log_info "Installing PyQt6 GUI framework..."

PYQT6_INSTALLED=false

# Method 1: Try system package
if install_package "python3-pyqt6" "PyQt6 system package"; then
    # Test if PyQt6 works
    if python3 -c "import PyQt6.QtWidgets; import PyQt6.QtCore; import PyQt6.QtGui" 2>/dev/null; then
        log_success "PyQt6 system package works correctly"
        PYQT6_INSTALLED=true
    else
        log_warning "PyQt6 system package installed but not working properly"
    fi
fi

# Method 2: Install via pip if system package failed or incomplete
if [ "$PYQT6_INSTALLED" = false ]; then
    log_info "Installing PyQt6 via pip..."
    
    # Install build dependencies for PyQt6
    install_package "build-essential" "Build tools" || true
    install_package "python3-dev" "Python development headers" || true
    install_package "qt6-base-dev" "Qt6 development files" || true
    
    if pip3 install PyQt6; then
        if python3 -c "import PyQt6.QtWidgets; import PyQt6.QtCore; import PyQt6.QtGui" 2>/dev/null; then
            log_success "PyQt6 installed successfully via pip"
            PYQT6_INSTALLED=true
        else
            log_error "PyQt6 pip installation failed verification"
        fi
    else
        log_error "Failed to install PyQt6 via pip"
    fi
fi

# Final PyQt6 check
if [ "$PYQT6_INSTALLED" = false ]; then
    log_error "Could not install PyQt6. Please install it manually:"
    echo "  sudo apt install python3-pyqt6"
    echo "  OR"
    echo "  pip3 install PyQt6"
    exit 1
fi

# Install additional Python dependencies
log_info "Installing additional Python packages..."
if [ -f "requirements.txt" ]; then
    if pip3 install -r requirements.txt; then
        log_success "Python packages installed successfully"
    else
        log_warning "Some Python packages failed to install, but continuing..."
    fi
else
    log_warning "requirements.txt not found, skipping additional packages"
fi

# Make main script executable
log_info "Making application executable..."
chmod +x main.py
log_success "Main script made executable"

# Test the application
log_info "Testing application startup..."
if python3 -c "import sys; sys.path.insert(0, '.'); from main import *" 2>/dev/null; then
    log_success "Application imports work correctly"
else
    log_warning "Application test failed, but installation continues"
fi

# Create desktop entry
log_info "Creating desktop entry..."
DESKTOP_FILE="/usr/share/applications/lumi-setup.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Lumi-Setup v2.0
Comment=Modern AnduinOS Software Installer
Exec=python3 $(pwd)/main.py
Icon=$(pwd)/resources/icons/lumi-setup.svg
Terminal=false
Type=Application
Categories=System;Settings;PackageManager;
StartupNotify=true
Keywords=installer;software;packages;anduinos;
EOF

if [ -f "$DESKTOP_FILE" ]; then
    log_success "Desktop entry created successfully"
else
    log_warning "Failed to create desktop entry"
fi

# Create symbolic link for command line access
log_info "Creating command line shortcut..."
SYMLINK_PATH="/usr/local/bin/lumi-setup"

# Remove existing symlink if it exists
[ -L "$SYMLINK_PATH" ] && rm "$SYMLINK_PATH"

# Create wrapper script instead of direct symlink for better compatibility
cat > "$SYMLINK_PATH" << EOF
#!/bin/bash
# Lumi-Setup v2.0 Launcher
cd "$(pwd)"
exec python3 main.py "\$@"
EOF

chmod +x "$SYMLINK_PATH"

if [ -x "$SYMLINK_PATH" ]; then
    log_success "Command line shortcut created successfully"
else
    log_warning "Failed to create command line shortcut"
fi

# Create application directory in user's home (for config and logs)
log_info "Setting up application directories..."
APP_DIR="/home/$SUDO_USER/.lumi-setup" 2>/dev/null || APP_DIR="/root/.lumi-setup"
mkdir -p "$APP_DIR/logs"
chown -R "$SUDO_USER:$SUDO_USER" "$APP_DIR" 2>/dev/null || true
log_success "Application directories created"

# Final verification
log_info "Performing final verification..."
VERIFICATION_PASSED=true

# Check Python
if ! command_exists python3; then
    log_error "Python 3 not found"
    VERIFICATION_PASSED=false
fi

# Check PyQt6
if ! python3 -c "import PyQt6.QtWidgets" 2>/dev/null; then
    log_error "PyQt6 not working"
    VERIFICATION_PASSED=false
fi

# Check main application file
if [ ! -f "main.py" ]; then
    log_error "Main application file not found"
    VERIFICATION_PASSED=false
fi

if [ "$VERIFICATION_PASSED" = true ]; then
    log_success "All verification checks passed!"
else
    log_error "Some verification checks failed"
    exit 1
fi

# Installation completed successfully
echo ""
log_success "Lumi-Setup v2.0 installation completed successfully!"
echo ""
log_info "You can now run Lumi-Setup v2.0 in the following ways:"
echo "  🖥️  From applications menu: Search for 'Lumi-Setup v2.0'"
echo "  💻 From command line: lumi-setup"
echo "  🐍 Directly: python3 $(pwd)/main.py"
echo ""
log_warning "Important Notes:"
echo "  • The application requires root privileges for system installations"
echo "  • Run with: sudo lumi-setup (or sudo python3 main.py)"
echo "  • Configuration and logs are stored in ~/.lumi-setup/"
echo "  • For issues, check: https://github.com/ruppdi75/lumi-systems-setup-V2"
echo ""
log_info "Installation log saved to: /var/log/lumi-setup-install.log" || true
