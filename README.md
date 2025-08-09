# Lumi-Setup v2.0

Modern PyQt6 GUI Application for AnduinOS Software Installation

## Overview

Lumi-Setup v2.0 is a complete rewrite of the original shell-based installation scripts, now featuring a modern graphical user interface built with PyQt6. This application provides a user-friendly way to install and configure software packages on AnduinOS systems.

## Features

- 🎨 **Modern GUI Interface** - Clean, intuitive PyQt6-based interface
- 📊 **Real-time Progress Tracking** - Live progress bars and status updates
- 📝 **Comprehensive Logging** - Detailed installation logs with filtering
- ✅ **Installation Checklist** - Complete summary of successful/failed installations
- 🔄 **Resume Capability** - Pause and resume installations
- 📋 **Selective Installation** - Choose which applications to install
- 📄 **Report Generation** - Export installation results to PDF/HTML

## Requirements

- Python 3.8+
- PyQt6
- AnduinOS (or compatible Linux distribution)
- Root privileges for system installations

## Installation

```bash
# Clone the repository
git clone https://github.com/ruppdi75/lumi-setup-v2.git
cd lumi-setup-v2

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Project Structure

```
lumi-setup-v2/
├── main.py                 # Application entry point
├── gui/                    # GUI components
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── progress_widget.py # Progress tracking widget
│   ├── log_widget.py      # Log display widget
│   └── results_widget.py  # Results summary widget
├── backend/               # Backend logic
│   ├── __init__.py
│   ├── installer.py       # Installation manager
│   ├── script_runner.py   # Shell script execution
│   └── progress_tracker.py # Progress tracking
├── scripts/               # Original shell scripts (adapted)
│   ├── software_install.sh
│   ├── system_config.sh
│   └── cleanup.sh
├── resources/             # UI resources
│   ├── icons/
│   └── styles/
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── logger.py
│   └── config.py
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Usage

1. Launch the application with `python main.py`
2. Select the applications you want to install
3. Click "Start Installation" to begin
4. Monitor progress in real-time
5. Review the installation summary when complete

## License

MIT License - see LICENSE file for details

## Author

Dimitri Rupp (dimitri.rupp@icloud.com)

## Version History

- **v2.0.0** - Complete GUI rewrite with PyQt6
- **v1.x** - Original shell script version
