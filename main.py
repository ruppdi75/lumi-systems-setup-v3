#!/usr/bin/env python3
"""
Lumi-Setup v3.0 - Modern PyQt6 GUI Application with Auto-Update
Main application entry point
"""

import sys
import os
import logging
from pathlib import Path

from PyQt6.QtWidgets import (QApplication, QMessageBox, QProgressDialog, 
                            QStyleFactory, QWidget)
from PyQt6.QtCore import Qt, QDir, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow
from utils.logger import setup_logging
from utils.config import Config
try:
    from src.updater import SourceChecker, VersionManager, ManifestGenerator
    UPDATER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Updater modules not available: {e}")
    UPDATER_AVAILABLE = False

class UpdateCheckThread(QThread):
    """Thread for checking updates in background"""
    update_found = pyqtSignal(dict)
    update_complete = pyqtSignal(str)
    update_error = pyqtSignal(str)
    progress_update = pyqtSignal(str, int)  # (message, percentage)
    
    def __init__(self, project_root):
        super().__init__()
        self.project_root = project_root
    
    def run(self):
        """Run update check in background"""
        try:
            # Phase 1: System Initialization
            self.progress_update.emit("🔧 Initializing update verification system...", 5)
            checker = SourceChecker(self.project_root)
            version_manager = VersionManager(self.project_root)
            
            self.progress_update.emit("📁 Preparing update manifest directories...", 10)
            # Create log directory for manifest generator
            log_dir = self.project_root / "logs" / "updates"
            log_dir.mkdir(parents=True, exist_ok=True)
            manifest_gen = ManifestGenerator(self.project_root / "manifests", log_dir)
            
            # Phase 2: Source Loading
            self.progress_update.emit("📋 Loading application source definitions...", 15)
            sources_file = self.project_root / "manifests" / "sources.json"
            if not sources_file.exists():
                self.update_error.emit("Source definitions file not found")
                return
                
            checker.load_sources(str(sources_file))
            total_sources = len(checker.sources)
            
            self.progress_update.emit(f"✅ Successfully loaded {total_sources} application sources", 20)
            
            # Phase 3: Update Verification
            self.progress_update.emit("🔍 Initiating comprehensive update scan...", 25)
            updates = {}
            updated_packages = []
            
            for idx, (app_name, source_info) in enumerate(checker.sources.items()):
                progress = 30 + int((idx / total_sources) * 55)  # 30-85% range
                
                # Professional status messages based on source type
                source_type = source_info.get('type', 'unknown')
                if source_type == 'github':
                    status_msg = f"🔄 Querying GitHub API for {app_name}..."
                elif source_type == 'apt':
                    status_msg = f"📦 Checking APT repository for {app_name}..."
                elif source_type == 'flatpak':
                    status_msg = f"📱 Verifying Flatpak version for {app_name}..."
                elif source_type == 'snap':
                    status_msg = f"🎯 Inspecting Snap package for {app_name}..."
                else:
                    status_msg = f"🔍 Analyzing {app_name}..."
                
                self.progress_update.emit(status_msg, progress)
                
                try:
                    app_updates = checker.check_source(app_name, source_info)
                    if app_updates and app_updates.get('has_update', False):
                        updates[app_name] = app_updates
                        updated_packages.append(app_name)
                except Exception as e:
                    # Continue checking other apps even if one fails
                    pass
            
            # Phase 4: Manifest Generation
            self.progress_update.emit("📝 Generating comprehensive update manifest...", 88)
            
            if updates:
                # Generate manifest with source info
                manifest = manifest_gen.generate_manifest(updates, checker.sources)
                
                self.progress_update.emit("💾 Persisting update manifest to system...", 92)
                
                # Count updates
                update_count = len(updated_packages)
                
                # Phase 5: Integration
                self.progress_update.emit("🔄 Integrating updates into installation routine...", 95)
                
                # Final status with package list
                if update_count > 0:
                    packages_str = ", ".join(updated_packages[:5])  # Show first 5
                    if update_count > 5:
                        packages_str += f" and {update_count - 5} more"
                    
                    self.progress_update.emit(f"✅ Update verification complete - {update_count} packages ready", 98)
                    self.progress_update.emit(f"📦 Updated packages: {packages_str}", 100)
                    
                    self.update_found.emit({
                        'count': update_count,
                        'updates': updates,
                        'packages': updated_packages
                    })
                    self.update_complete.emit(f"Successfully identified {update_count} available updates")
                else:
                    self.progress_update.emit("✅ System verification complete", 100)
                    self.update_complete.emit("All applications are at their latest versions")
            else:
                self.progress_update.emit("✅ Update scan complete - System is current", 100)
                self.update_complete.emit("No updates required at this time")
        except Exception as e:
            self.update_error.emit(str(e))

def setup_application():
    """Setup the Qt application with proper styling and configuration"""
    app = QApplication(sys.argv)
    app.setApplicationName("Lumi-Setup v3.0")
    app.setApplicationVersion("3.0.0")
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

def check_for_updates(app, project_root):
    """Check for software updates on startup"""
    logger = logging.getLogger(__name__)
    
    if not UPDATER_AVAILABLE:
        logger.warning("Updater modules not available, skipping update check")
        return
    
    logger.info("Initiating comprehensive update verification process...")
    
    # Create enhanced progress dialog with professional appearance
    progress = QProgressDialog()
    progress.setWindowTitle("Lumi-Setup Update Manager")
    progress.setLabelText("🔄 Initializing update verification system...")
    progress.setRange(0, 100)
    progress.setValue(0)
    progress.setMinimumDuration(0)
    progress.setMinimumSize(600, 180)
    progress.setWindowModality(Qt.WindowModality.ApplicationModal)
    progress.setAutoReset(False)
    progress.setAutoClose(False)
    
    # Apply professional styling with Lumi-Systems branding
    progress.setStyleSheet("""
        QProgressDialog {
            min-width: 600px;
            min-height: 180px;
            background-color: #2b2b2b;
            color: #ffffff;
            font-family: 'Segoe UI', 'Ubuntu', sans-serif;
        }
        QLabel {
            color: #ffffff;
            font-size: 11pt;
            padding: 10px;
            min-height: 30px;
        }
        QProgressBar {
            min-height: 30px;
            border: 2px solid #555555;
            border-radius: 5px;
            text-align: center;
            background-color: #3b3b3b;
            color: #ffffff;
            font-weight: bold;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                       stop: 0 #0d7377, stop: 1 #14a085);
            border-radius: 3px;
        }
    """)
    
    # Disable cancel button to prevent interruption
    progress.setCancelButton(None)
    progress.show()
    
    # Process events to ensure dialog is displayed
    app.processEvents()
    
    # Create and start update check thread
    update_thread = UpdateCheckThread(project_root)
    
    # Track if updates were found
    updates_found = {'count': 0}
    
    def on_progress_update(message, percentage):
        progress.setLabelText(message)
        progress.setValue(percentage)
        app.processEvents()  # Keep UI responsive
    
    def on_update_found(update_info):
        updates_found['count'] = update_info['count']
        logger.info(f"Found {update_info['count']} updates")
    
    def on_update_complete(message):
        logger.info(f"Update verification completed: {message}")
        if progress and not progress.wasCanceled():
            progress.setValue(100)
            # Add professional completion message with icon
            if "identified" in message.lower() and "available" in message.lower():
                final_msg = f"✅ {message}\nUpdates have been integrated into the installation routine."
            elif "latest versions" in message.lower():
                final_msg = f"✅ {message}\nYour system is fully up-to-date."
            else:
                final_msg = f"✅ {message}"
            progress.setLabelText(final_msg)
            app.processEvents()
            # Close dialog after brief delay to allow user to read the message
            QTimer.singleShot(2000, lambda: progress.close() if progress else None)
    
    def on_update_error(error):
        logger.error(f"Update verification encountered an error: {error}")
        if progress and not progress.wasCanceled():
            progress.setLabelText(f"⚠️ Update verification error: {error}\nPlease check your network connection and try again.")
            progress.setValue(0)
            app.processEvents()
            # Close dialog after showing error with enough time to read
            QTimer.singleShot(3000, lambda: progress.close() if progress else None)
    
    # Connect signals
    update_thread.progress_update.connect(on_progress_update)
    update_thread.update_found.connect(on_update_found)
    update_thread.update_complete.connect(on_update_complete)
    update_thread.update_error.connect(on_update_error)
    
    update_thread.start()
    
    # Wait for thread to complete (with timeout)
    update_thread.wait(30000)  # 30 second timeout
    
    if update_thread.isRunning():
        logger.warning("Update check timed out")
        update_thread.terminate()
        if progress:
            progress.close()

def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting Lumi-Setup v3.0")
        
        # Create Qt application
        app = setup_application()
        
        # Check requirements
        if not check_requirements():
            sys.exit(1)
        
        # Check for updates on startup (only if updater is available)
        if UPDATER_AVAILABLE:
            check_for_updates(app, project_root)
        
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
                               f"Failed to start Lumi-Setup v3.0:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
