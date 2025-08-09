#!/usr/bin/env python3
"""
Lumi-Setup v2.0 - Modern PyQt6 GUI Application
Main application entry point
"""

import sys
import os
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QIcon

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow
from utils.logger import setup_logging
from utils.config import Config

def setup_application():
    """Setup the Qt application with proper styling and configuration"""
    app = QApplication(sys.argv)
    app.setApplicationName("Lumi-Setup v2.0")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Lumi-Systems")
    app.setOrganizationDomain("lumi-systems.com")
    
    # Set application icon
    icon_path = project_root / "resources" / "icons" / "lumi-setup.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Apply modern styling
    apply_modern_style(app)
    
    return app

def apply_modern_style(app):
    """Apply modern dark theme styling to the application"""
    style = """
    QMainWindow {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-family: 'Segoe UI', 'Ubuntu', sans-serif;
        font-size: 10pt;
    }
    
    QPushButton {
        background-color: #0d7377;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #14a085;
    }
    
    QPushButton:pressed {
        background-color: #0a5d61;
    }
    
    QPushButton:disabled {
        background-color: #555555;
        color: #888888;
    }
    
    QProgressBar {
        border: 2px solid #555555;
        border-radius: 5px;
        text-align: center;
        background-color: #3b3b3b;
    }
    
    QProgressBar::chunk {
        background-color: #0d7377;
        border-radius: 3px;
    }
    
    QTextEdit, QPlainTextEdit {
        background-color: #1e1e1e;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px;
        color: #ffffff;
    }
    
    QLabel {
        color: #ffffff;
    }
    
    QGroupBox {
        font-weight: bold;
        border: 2px solid #555555;
        border-radius: 5px;
        margin-top: 1ex;
        padding-top: 10px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }
    
    QCheckBox {
        spacing: 5px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
    }
    
    QCheckBox::indicator:unchecked {
        border: 2px solid #555555;
        background-color: #2b2b2b;
        border-radius: 3px;
    }
    
    QCheckBox::indicator:checked {
        border: 2px solid #0d7377;
        background-color: #0d7377;
        border-radius: 3px;
    }
    
    QTabWidget::pane {
        border: 1px solid #555555;
        background-color: #2b2b2b;
    }
    
    QTabBar::tab {
        background-color: #3b3b3b;
        color: #ffffff;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #0d7377;
    }
    
    QTabBar::tab:hover {
        background-color: #555555;
    }
    """
    app.setStyleSheet(style)

def check_requirements():
    """Check if all requirements are met to run the application"""
    # Check if running on Linux
    if sys.platform != 'linux':
        QMessageBox.warning(None, "Platform Warning", 
                          "Lumi-Setup is designed for Linux systems. "
                          "Some features may not work correctly on other platforms.")
    
    # Check Python version
    if sys.version_info < (3, 8):
        QMessageBox.critical(None, "Python Version Error",
                           "Python 3.8 or higher is required to run Lumi-Setup v2.0")
        return False
    
    # Check if running as root (for installations)
    if os.geteuid() != 0:
        reply = QMessageBox.question(None, "Root Privileges",
                                   "Lumi-Setup requires root privileges for system installations.\n"
                                   "Some features may be limited without root access.\n\n"
                                   "Continue anyway?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return False
    
    return True

def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting Lumi-Setup v2.0")
        
        # Create Qt application
        app = setup_application()
        
        # Check requirements
        if not check_requirements():
            sys.exit(1)
        
        # Load configuration
        config = Config()
        
        # Create and show main window
        main_window = MainWindow(config)
        main_window.show()
        
        logger.info("Application started successfully")
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        if 'app' in locals():
            QMessageBox.critical(None, "Application Error",
                               f"Failed to start Lumi-Setup v2.0:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
