# 🚀 Lumi-Systems Setup V2

**Modern PyQt6 GUI Application for AnduinOS Software Installation**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)]()

## 📋 Overview

Lumi-Systems Setup V2 is a **complete rewrite** of the original shell-based installation scripts, now featuring a **modern graphical user interface** built with PyQt6. This application provides an intuitive, user-friendly way to install and configure software packages on AnduinOS and compatible Linux systems.

### 🎯 From Command Line to GUI

This version transforms the powerful but terminal-based installation process into a beautiful, modern desktop application with real-time feedback and professional reporting.

## ✨ Key Features

### 🎨 **Modern User Interface**
- **Dark Theme Design** - Professional, eye-friendly interface
- **Tabbed Layout** - Progress, Logs, and Results in organized tabs
- **Responsive Design** - Adapts to different screen sizes
- **Intuitive Controls** - Easy-to-use buttons and checkboxes

### 📊 **Real-time Progress Tracking**
- **Live Progress Bars** - Overall and per-application progress
- **Status Updates** - Current installation step display
- **Time Tracking** - Installation duration and estimates
- **Statistics Dashboard** - Success/failure counts and rates

### 📝 **Advanced Logging System**
- **Multi-level Logging** - Debug, Info, Warning, Error levels
- **Log Filtering** - View specific log levels
- **Real-time Display** - Live log updates during installation
- **Export Functionality** - Save logs to file

### 🛠️ **Installation Management**
- **25+ Applications** - Pre-configured popular software
- **Categorized Selection** - Desktop, Development, Entertainment, System tools
- **Pause/Resume/Stop** - Full control over installation process
- **Error Recovery** - Continue installation despite individual failures
- **Dependency Handling** - Automatic prerequisite installation

### 📄 **Professional Reporting**
- **Installation Summary** - Complete results overview
- **HTML Export** - Professional installation reports
- **Success/Failure Analysis** - Detailed error information
- **Time Statistics** - Installation duration tracking

## 🖥️ Supported Applications

### 🖥️ Desktop Applications
- **Firefox** - Web Browser
- **Thunderbird** - Email Client  
- **LibreOffice** - Office Suite
- **GIMP** - Image Editor
- **VLC** - Media Player
- **Visual Studio Code** - Code Editor

### 🛠️ Development Tools
- **Git** - Version Control
- **Python 3** - Programming Language
- **Node.js** - JavaScript Runtime
- **Docker** - Containerization
- **RustDesk** - Remote Desktop

### 🎮 Entertainment
- **Steam** - Gaming Platform
- **Discord** - Communication
- **Spotify** - Music Streaming

### 🔧 System Tools
- **htop** - System Monitor
- **curl** - HTTP Client
- **wget** - File Downloader
- **zip/unzip** - Archive Tools

## 🔧 System Requirements

- **Operating System**: AnduinOS or compatible Linux distribution
- **Python**: 3.8 or higher
- **GUI Framework**: PyQt6
- **Privileges**: Root access for system installations
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB free space

## 📦 Quick Installation

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

## 📁 Project Structure

```
lumi-systems-setup-V2/
├── main.py                 # 🚀 Application entry point
├── gui/                    # 🎨 GUI components
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── progress_widget.py # Progress tracking widget
│   ├── log_widget.py      # Log display widget
│   └── results_widget.py  # Results summary widget
├── backend/               # ⚙️ Backend logic
│   ├── __init__.py
│   ├── installer.py       # Installation manager
│   ├── script_runner.py   # Shell script execution
│   └── progress_tracker.py # Progress tracking
├── scripts/               # 📜 Original shell scripts (adapted)
│   ├── software_install.sh
│   ├── system_config.sh
│   └── cleanup.sh
├── resources/             # 🎨 UI resources
│   ├── icons/
│   └── styles/
├── utils/                 # 🔧 Utility functions
│   ├── __init__.py
│   ├── logger.py
│   └── config.py
├── install.sh             # 📦 Automated installation script
├── requirements.txt       # 📋 Python dependencies
├── LICENSE               # ⚖️ MIT License
└── README.md             # 📖 This documentation
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
