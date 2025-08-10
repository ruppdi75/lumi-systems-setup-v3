"""
Main window for Lumi-Setup v2.0
"""

import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QLabel, QPushButton, QProgressBar,
                            QTextEdit, QGroupBox, QCheckBox, QScrollArea,
                            QSplitter, QStatusBar, QMenuBar, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QAction

from .progress_widget import ProgressWidget
from .log_widget import LogWidget
from .results_widget import ResultsWidget
from .password_dialog import get_sudo_password
from backend.installer import InstallationManager

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.installation_manager = None
        self.installation_thread = None
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Lumi-Setup v2.0 - AnduinOS Software Installer")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create header
        self.create_header(main_layout)
        
        # Create main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Application selection
        self.create_selection_panel(splitter)
        
        # Right panel - Progress and logs
        self.create_progress_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
        
        # Create status bar
        self.create_status_bar()
        
        # Create menu bar
        self.create_menu_bar()
        
    def create_header(self, parent_layout):
        """Create the application header"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Logo and title
        title_label = QLabel("🚀 Lumi-Setup v2.0")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Control buttons
        self.start_button = QPushButton("🚀 Start Installation")
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                font-weight: bold;
                padding: 10px 20px;
                background-color: #0d7377;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
        """)
        
        self.pause_button = QPushButton("⏸️ Pause")
        self.pause_button.setEnabled(False)
        
        self.stop_button = QPushButton("⏹️ Stop")
        self.stop_button.setEnabled(False)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        
        header_layout.addLayout(button_layout)
        
        parent_layout.addWidget(header_widget)
        
    def create_selection_panel(self, parent_splitter):
        """Create the application selection panel"""
        selection_widget = QWidget()
        selection_layout = QVBoxLayout(selection_widget)
        
        # Selection header
        selection_header = QLabel("📦 Select Applications to Install")
        selection_header.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 10px;")
        selection_layout.addWidget(selection_header)
        
        # Quick selection buttons - horizontal layout like tabs
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 10)
        buttons_layout.setSpacing(10)
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_applications)
        select_all_btn.setMinimumHeight(30)
        select_all_btn.setStyleSheet("""
            QPushButton {
                font-size: 10pt;
                font-weight: bold;
                padding: 5px 15px;
                background-color: #0d7377;
                border: none;
                border-radius: 4px;
                color: white;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
        """)
        
        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self.select_no_applications)
        select_none_btn.setMinimumHeight(30)
        select_none_btn.setStyleSheet("""
            QPushButton {
                font-size: 10pt;
                font-weight: bold;
                padding: 5px 15px;
                background-color: #6c757d;
                border: none;
                border-radius: 4px;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        select_recommended_btn = QPushButton("Recommended")
        select_recommended_btn.clicked.connect(self.select_recommended_applications)
        select_recommended_btn.setMinimumHeight(30)
        select_recommended_btn.setStyleSheet("""
            QPushButton {
                font-size: 10pt;
                font-weight: bold;
                padding: 5px 15px;
                background-color: #28a745;
                border: none;
                border-radius: 4px;
                color: white;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        buttons_layout.addWidget(select_all_btn)
        buttons_layout.addWidget(select_none_btn)
        buttons_layout.addWidget(select_recommended_btn)
        buttons_layout.addStretch()  # Push buttons to the left
        
        selection_layout.addWidget(buttons_widget)
        
        # Scrollable application list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.apps_widget = QWidget()
        self.apps_layout = QVBoxLayout(self.apps_widget)
        
        # Create application groups
        self.create_application_groups()
        
        scroll_area.setWidget(self.apps_widget)
        selection_layout.addWidget(scroll_area)
        
        # Selection summary
        self.selection_summary = QLabel("0 applications selected")
        self.selection_summary.setStyleSheet("font-weight: bold; color: #0d7377;")
        selection_layout.addWidget(self.selection_summary)
        
        parent_splitter.addWidget(selection_widget)
        
    def create_application_groups(self):
        """Create grouped application checkboxes"""
        # Define application categories
        app_categories = {
            "🖥️ Desktop Applications": [
                ("firefox", "Firefox Web Browser", True),
                ("thunderbird", "Thunderbird Email Client", True),
                ("libreoffice", "LibreOffice Office Suite", True),
                ("gimp", "GIMP Image Editor", False),
                ("vlc", "VLC Media Player", True),
                ("code", "Visual Studio Code", True),
            ],
            "🛠️ Development Tools": [
                ("git", "Git Version Control", True),
                ("python3", "Python 3", True),
                ("nodejs", "Node.js", False),
                ("docker", "Docker", False),
                ("rustdesk", "RustDesk Remote Desktop", True),
            ],
            "🎮 Entertainment": [
                ("steam", "Steam Gaming Platform", False),
                ("discord", "Discord Chat", False),
                # COMMENTED OUT: Spotify option
                # ("spotify", "Spotify Music", False),
            ],
            "🔧 System Tools": [
                ("htop", "System Monitor", True),
                ("curl", "HTTP Client", True),
                ("wget", "File Downloader", True),
                ("zip", "Archive Tools", True),
            ]
        }
        
        self.app_checkboxes = {}
        
        for category, apps in app_categories.items():
            # Create group box
            group_box = QGroupBox(category)
            group_layout = QVBoxLayout(group_box)
            
            for app_id, app_name, recommended in apps:
                checkbox = QCheckBox(app_name)
                checkbox.setChecked(recommended)
                checkbox.stateChanged.connect(self.update_selection_summary)
                
                if recommended:
                    checkbox.setStyleSheet("font-weight: bold;")
                
                self.app_checkboxes[app_id] = checkbox
                group_layout.addWidget(checkbox)
            
            self.apps_layout.addWidget(group_box)
        
        self.apps_layout.addStretch()
        
        # Initialize selection summary after creating checkboxes
        if hasattr(self, 'selection_summary'):
            self.update_selection_summary()
        
    def create_progress_panel(self, parent_splitter):
        """Create the progress and logging panel"""
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        
        # Create horizontal layout for tabs and selection buttons
        top_layout = QHBoxLayout()
        
        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        top_layout.addWidget(self.tab_widget)
        progress_layout.addLayout(top_layout)
        
        # Progress tab
        self.progress_widget = ProgressWidget()
        self.tab_widget.addTab(self.progress_widget, "📊 Progress")
        
        # Log tab
        self.log_widget = LogWidget()
        self.tab_widget.addTab(self.log_widget, "📝 Logs")
        
        # Results tab
        self.results_widget = ResultsWidget()
        self.tab_widget.addTab(self.results_widget, "✅ Results")
        
        parent_splitter.addWidget(progress_widget)
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_bar.showMessage("Ready to install applications")
        
        # Add permanent widgets
        self.status_label = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.status_label)
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        export_action = QAction('Export Results', self)
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        clear_logs_action = QAction('Clear Logs', self)
        clear_logs_action.triggered.connect(self.log_widget.clear_logs)
        tools_menu.addAction(clear_logs_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.start_button.clicked.connect(self.start_installation)
        self.pause_button.clicked.connect(self.pause_installation)
        self.stop_button.clicked.connect(self.stop_installation)
        
    def select_all_applications(self):
        """Select all applications"""
        for checkbox in self.app_checkboxes.values():
            checkbox.setChecked(True)
            
    def select_no_applications(self):
        """Deselect all applications"""
        for checkbox in self.app_checkboxes.values():
            checkbox.setChecked(False)
            
    def select_recommended_applications(self):
        """Select only recommended applications"""
        recommended_apps = ["firefox", "thunderbird", "libreoffice", "vlc", "code", 
                          "git", "python3", "rustdesk", "htop", "curl", "wget", "zip"]
        
        for app_id, checkbox in self.app_checkboxes.items():
            checkbox.setChecked(app_id in recommended_apps)
            
    def update_selection_summary(self):
        """Update the selection summary label"""
        if not hasattr(self, 'selection_summary') or not hasattr(self, 'app_checkboxes'):
            return
            
        selected_count = sum(1 for cb in self.app_checkboxes.values() if cb.isChecked())
        total_count = len(self.app_checkboxes)
        
        self.selection_summary.setText(f"{selected_count} of {total_count} applications selected")
        
    def get_selected_applications(self):
        """Get list of selected applications"""
        return [app_id for app_id, checkbox in self.app_checkboxes.items() 
                if checkbox.isChecked()]
        
    def start_installation(self):
        """Start the installation process"""
        selected_apps = self.get_selected_applications()
        
        if not selected_apps:
            QMessageBox.warning(self, "No Selection", 
                              "Please select at least one application to install.")
            return
        
        # Prompt for sudo password before starting
        sudo_password = get_sudo_password(self)
        if sudo_password is None:
            # User cancelled password dialog
            return
            
        # Store password for use during installation
        self.sudo_password = sudo_password
            
        # Update UI state
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        
        # Switch to progress tab
        self.tab_widget.setCurrentIndex(0)
        
        # Start installation in background thread
        self.installation_manager = InstallationManager(selected_apps, self.config, self.sudo_password)
        self.installation_thread = QThread()
        
        self.installation_manager.moveToThread(self.installation_thread)
        
        # Connect signals
        self.installation_manager.progress_updated.connect(self.progress_widget.update_progress)
        self.installation_manager.status_updated.connect(self.update_status)
        self.installation_manager.log_message.connect(self.log_widget.add_log_message)
        self.installation_manager.installation_completed.connect(self.installation_completed)
        self.installation_manager.installation_failed.connect(self.installation_failed)
        
        self.installation_thread.started.connect(self.installation_manager.start_installation)
        self.installation_thread.start()
        
        self.logger.info(f"Started installation of {len(selected_apps)} applications")
        
    def pause_installation(self):
        """Pause the installation process"""
        if self.installation_manager:
            self.installation_manager.pause_installation()
            self.pause_button.setText("▶️ Resume")
            self.pause_button.clicked.disconnect()
            self.pause_button.clicked.connect(self.resume_installation)
            
    def resume_installation(self):
        """Resume the installation process"""
        if self.installation_manager:
            self.installation_manager.resume_installation()
            self.pause_button.setText("⏸️ Pause")
            self.pause_button.clicked.disconnect()
            self.pause_button.clicked.connect(self.pause_installation)
            
    def stop_installation(self):
        """Stop the installation process"""
        if self.installation_manager:
            self.installation_manager.stop_installation()
            
        self.installation_completed()
        
    def installation_completed(self):
        """Handle installation completion"""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("⏸️ Pause")
        
        # Switch to results tab
        self.tab_widget.setCurrentIndex(2)
        
        if self.installation_manager:
            self.results_widget.display_results(self.installation_manager.get_results())
            
        self.update_status("Installation completed")
        self.logger.info("Installation process completed")
        
    def installation_failed(self, error_message):
        """Handle installation failure"""
        self.installation_completed()
        QMessageBox.critical(self, "Installation Failed", 
                           f"Installation failed with error:\n{error_message}")
        
    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.showMessage(message)
        self.status_label.setText(message.split(':')[0] if ':' in message else message)
        
    def export_results(self):
        """Export installation results"""
        if self.results_widget:
            self.results_widget.export_results()
            
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Lumi-Setup v2.0",
                         "Lumi-Setup v2.0\n\n"
                         "Modern PyQt6 GUI Application for AnduinOS Software Installation\n\n"
                         "Author: Dimitri Rupp\n"
                         "Email: dimitri.rupp@icloud.com\n\n"
                         "© 2024 Lumi-Systems")
        
    def closeEvent(self, event):
        """Handle application close event"""
        if self.installation_thread and self.installation_thread.isRunning():
            reply = QMessageBox.question(self, "Installation Running",
                                       "Installation is currently running. "
                                       "Are you sure you want to exit?",
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
                
            # Stop installation
            if self.installation_manager:
                self.installation_manager.stop_installation()
                
            # Wait for thread to finish
            self.installation_thread.quit()
            self.installation_thread.wait(3000)  # Wait up to 3 seconds
            
        event.accept()
