# 🚀 Lumi-Systems# Lumi-Setup v3.0 🚀

**Modern PyQt6-based GUI installer for AnduinOS/Linux systems with automatic update checking, professional features, and comprehensive software management.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)]()

## 📋 Overview

Lumi-Systems# Lumi-Setup v3.0 🚀 is a **complete rewrite** of the original shell-based installation scripts, now featuring a **modern graphical user interface** built with PyQt6. This application provides an intuitive, user-friendly way to install and configure software packages on AnduinOS and compatible Linux systems.

### 🔄 Recent Changes
- **Spotify Temporarily Disabled** (v2.0.1) - Due to installation issues, Spotify has been temporarily excluded from the setup process. All Spotify-related code has been commented out and can be re-enabled in the future.

### 🎯 From Command Line to GUI

This version transforms the powerful but terminal-based installation process into a beautiful, modern desktop application with real-time feedback and professional reporting.

## What's New in Version 3.0.2

### 🐛 Bug Fixes & Improvements
- **OnlyOffice Installation**: Now properly installs via .deb package with automatic Flatpak fallback
- **Script Runner**: Fixed critical import error that caused crashes
- **Steam Dependencies**: Updated to use current package names
- **Discord Download**: Added timeout handling to prevent hanging

## What's New in Version 3.0

### Automatic Source Updates

Lumi-Setup now automatically checks for the latest versions of all software it manages:
- Runs update check on every startup
- Compares current versions with latest available
- Generates detailed manifests of all changes
- Can apply updates directly to installation scripts

### Update Sources Supported

- **GitHub Releases** - Direct API integration
- **APT Packages** - System package manager
- **Flatpak Apps** - Flathub repository
- **Snap Packages** - Snap store
- **Direct Downloads** - DEB files and archives

## Quick Start

### Method 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/ruppdi75/lumi-systems-setup-V2.git
cd lumi-systems-setup-V2

# Run automated installation (requires sudo)
sudo ./install.sh

# Launch from applications menu or command line
lumi-setup
```

### Method 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/ruppdi75/lumi-systems-setup-V2.git
cd lumi-systems-setup-V2

# Install Python dependencies
sudo apt update
sudo apt install python3 python3-pip python3-pyqt6

# Install Python packages
pip3 install -r requirements.txt

# Run the application
python3 main.py
```

## Development

### Project Structure

```
lumi-setup-v3/
├── main.py              # Application entry point
├── gui/                 # PyQt6 GUI components
│   ├── main_window.py   # Main application window
│   ├── progress_widget.py
│   ├── log_widget.py
│   ├── results_widget.py
│   └── update_widget.py # NEW: Update dashboard
├── backend/             # Core logic
│   ├── installer.py     # Installation manager
│   ├── script_runner.py # Shell script executor
│   └── progress_tracker.py
├── src/updater/         # NEW: Update system
│   ├── source_checker.py    # Version checking
│   ├── manifest_generator.py # Manifest creation
│   └── version_manager.py   # Version control
├── scripts/             # Installation scripts
│   ├── setup.sh
│   ├── software_install.sh
│   └── system_config.sh
├── manifests/           # Update manifests
├── logs/updates/        # Update logs
├── .github/workflows/   # CI/CD pipelines
│   ├── release.yml
│   └── update-check.yml
├── utils/               # Utilities
│   ├── logger.py
│   └── config.py
└── resources/           # Assets
    ├── icons/
    └── styles/
```

## 🚀 Usage Guide

### 1. **Launch the Application**

```bash
# From command line (after installation)
lumi-setup

# Or directly
python3 main.py
```

### 2. **Select Applications**

- Browse through categorized application lists
- Use **"Select All"**, **"Select None"**, or **"Recommended"** buttons
- Check individual applications you want to install

### 3. **Start Installation**

- Click **"🚀 Start Installation"** button
- Monitor real-time progress in the **Progress** tab
- View detailed logs in the **Logs** tab
- Use **Pause/Resume/Stop** controls as needed

### 4. **Review Results**

- Check the **Results** tab for installation summary
- Export results to HTML for documentation
- Review any failed installations and error details

## 📸 Screenshots

*Screenshots will be added once the application is tested on AnduinOS*

## 🔧 Configuration

The application creates a configuration directory at `~/.lumi-setup/` containing:
- `config.json` - Application settings
- `logs/` - Installation logs

### Customizable Settings:

- **UI Theme** - Dark/Light mode
- **Log Levels** - Debug verbosity
- **Installation Options** - Timeouts, retries, parallel installs
- **Window Preferences** - Size, position

## 🐛 Troubleshooting

### Common Issues:

**PyQt6 Import Error:**

```bash
# Install PyQt6 system packages
sudo apt install python3-pyqt6 python3-pyqt6.qtcore python3-pyqt6.qtgui python3-pyqt6.qtwidgets

# Or via pip
pip3 install PyQt6
```

**Permission Denied:**

```bash
# Run with sudo for system installations
sudo python3 main.py
```

**Missing Dependencies:**

```bash
# Install all requirements
pip3 install -r requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup:

```bash
# Clone for development
git clone https://github.com/ruppdi75/lumi-systems-setup-V2.git
cd lumi-systems-setup-V2

# Install in development mode
pip3 install -e .

# Run tests (when available)
python3 -m pytest
```

## 📝 Changelog

### v3.0.1 (2025-08-21)

- 🎨 **Enhanced Update Dialog** - Professional status messages with phased progress reporting
- 📊 **Detailed Progress Tracking** - 5-phase update verification process with clear indicators
- 🔍 **Source-Specific Messages** - Tailored status updates for GitHub, APT, Flatpak, and Snap
- 💎 **Improved UI Styling** - Gradient progress bars and Lumi-Systems branding
- 📦 **Package List Display** - Shows updated packages in final status message
- ⚡ **Better User Feedback** - Context-aware completion messages and error handling

### v3.0.0 (2025-01-21)

- 🔄 **Automatic Update Checking** - Checks all software sources on startup
- 📋 **Update Manifest System** - JSON-based tracking of all changes
- 🎯 **Smart Version Detection** - GitHub API, APT, Flatpak, Snap integration
- 📊 **Update Dashboard** - Visual interface for managing updates
- 🔧 **CI/CD Pipeline** - GitHub Actions for automated releases
- 📝 **Enhanced Logging** - Detailed update and change logs

### v2.0.0 (2024-08-09)

- 🎉 **Complete GUI rewrite** with PyQt6
- ✨ **Modern dark theme** interface
- 📊 **Real-time progress tracking**
- 📝 **Advanced logging system**
- 📄 **Professional reporting** with HTML export
- 🛠️ **25+ pre-configured applications**
- ⏯️ **Pause/Resume/Stop** functionality
- 🔧 **Configuration management**
- 📦 **Automated installation script**
- 🖥️ **Desktop integration**

### v1.x

- 📜 Original shell script-based version
- 🖥️ Terminal-only interface
- ✅ Basic installation tracking

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Dimitri Rupp**
- 📧 Email: dimitri.rupp@icloud.com
- 🐙 GitHub: [@ruppdi75](https://github.com/ruppdi75)
- 🏢 Organization: Lumi-Systems

## 🙏 Acknowledgments

- Built with [PyQt6](https://pypi.org/project/PyQt6/) for the modern GUI framework
- Inspired by the need for user-friendly Linux software installation
- Designed specifically for AnduinOS and compatible distributions

## 📊 Project Stats

- **Language**: Python 3.8+
- **GUI Framework**: PyQt6
- **Lines of Code**: 4000+
- **Files**: 25+
- **Supported Apps**: 25+

---

<div align="center">

**⭐ Star this repository if you find it useful! ⭐**

[Report Bug](https://github.com/ruppdi75/lumi-systems-setup-V2/issues) • [Request Feature](https://github.com/ruppdi75/lumi-systems-setup-V2/issues) • [Documentation](https://github.com/ruppdi75/lumi-systems-setup-V2/wiki)

</div>
