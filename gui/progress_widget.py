"""
Progress tracking widget for Lumi-Setup v2.0
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QTextEdit, QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont

class ProgressWidget(QWidget):
    """Widget for displaying installation progress"""
    
    def __init__(self):
        super().__init__()
        self.current_app = ""
        self.current_step = ""
        self.total_apps = 0
        self.completed_apps = 0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Overall progress section
        overall_group = QGroupBox("📊 Overall Progress")
        overall_layout = QVBoxLayout(overall_group)
        
        # Overall progress bar
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        self.overall_progress.setValue(0)
        self.overall_progress.setTextVisible(True)
        self.overall_progress.setMinimumHeight(30)
        
        # Overall progress label
        self.overall_label = QLabel("Ready to start installation...")
        self.overall_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        
        overall_layout.addWidget(self.overall_label)
        overall_layout.addWidget(self.overall_progress)
        
        layout.addWidget(overall_group)
        
        # Current application section
        current_group = QGroupBox("🔧 Current Application")
        current_layout = QVBoxLayout(current_group)
        
        # Current app info
        self.current_app_label = QLabel("No application currently being installed")
        self.current_app_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #0d7377;")
        
        self.current_step_label = QLabel("Waiting to start...")
        self.current_step_label.setStyleSheet("font-size: 11pt; color: #888888;")
        
        # Current app progress bar
        self.current_progress = QProgressBar()
        self.current_progress.setMinimum(0)
        self.current_progress.setMaximum(100)
        self.current_progress.setValue(0)
        self.current_progress.setTextVisible(True)
        self.current_progress.setMinimumHeight(25)
        
        current_layout.addWidget(self.current_app_label)
        current_layout.addWidget(self.current_step_label)
        current_layout.addWidget(self.current_progress)
        
        layout.addWidget(current_group)
        
        # Installation steps section
        steps_group = QGroupBox("📋 Installation Steps")
        steps_layout = QVBoxLayout(steps_group)
        
        # Scrollable area for steps
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        
        self.steps_widget = QWidget()
        self.steps_layout = QVBoxLayout(self.steps_widget)
        self.steps_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.steps_widget)
        steps_layout.addWidget(scroll_area)
        
        layout.addWidget(steps_group)
        
        # Statistics section
        stats_group = QGroupBox("📈 Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        stats_info_layout = QHBoxLayout()
        
        self.apps_completed_label = QLabel("Completed: 0")
        self.apps_failed_label = QLabel("Failed: 0")
        self.apps_already_installed_label = QLabel("Already Installed: 0")
        self.apps_remaining_label = QLabel("Remaining: 0")
        self.time_elapsed_label = QLabel("Time: 00:00")
        
        stats_info_layout.addWidget(self.apps_completed_label)
        stats_info_layout.addWidget(self.apps_failed_label)
        stats_info_layout.addWidget(self.apps_already_installed_label)
        stats_info_layout.addWidget(self.apps_remaining_label)
        stats_info_layout.addStretch()
        stats_info_layout.addWidget(self.time_elapsed_label)
        
        stats_layout.addLayout(stats_info_layout)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
    @pyqtSlot(dict)
    def update_progress(self, progress_data):
        """Update progress display with new data"""
        # Update overall progress
        if 'overall_progress' in progress_data:
            self.overall_progress.setValue(progress_data['overall_progress'])
            
        if 'overall_label' in progress_data:
            self.overall_label.setText(progress_data['overall_label'])
            
        # Update current application
        if 'current_app' in progress_data:
            self.current_app = progress_data['current_app']
            self.current_app_label.setText(f"Installing: {self.current_app}")
            
        if 'current_step' in progress_data:
            self.current_step = progress_data['current_step']
            self.current_step_label.setText(self.current_step)
            
        if 'current_progress' in progress_data:
            self.current_progress.setValue(progress_data['current_progress'])
            
        # Update statistics
        if 'completed_apps' in progress_data:
            self.completed_apps = progress_data['completed_apps']
            self.apps_completed_label.setText(f"Completed: {self.completed_apps}")
            
        if 'failed_apps' in progress_data:
            failed_count = progress_data['failed_apps']
            self.apps_failed_label.setText(f"Failed: {failed_count}")
            
        if 'already_installed_apps' in progress_data:
            already_installed_count = progress_data['already_installed_apps']
            self.apps_already_installed_label.setText(f"Already Installed: {already_installed_count}")
            
        if 'total_apps' in progress_data:
            self.total_apps = progress_data['total_apps']
            # Calculate remaining based on all processed apps
            completed = progress_data.get('completed_apps', 0)
            failed = progress_data.get('failed_apps', 0)
            already_installed = progress_data.get('already_installed_apps', 0)
            processed = completed + failed + already_installed
            remaining = self.total_apps - processed
            self.apps_remaining_label.setText(f"Remaining: {remaining}")
            
        if 'time_elapsed' in progress_data:
            self.time_elapsed_label.setText(f"Time: {progress_data['time_elapsed']}")
            
        # Update installation steps
        if 'installation_steps' in progress_data:
            self.update_installation_steps(progress_data['installation_steps'])
            
    def update_installation_steps(self, steps):
        """Update the installation steps display"""
        try:
            # Clear existing steps
            for i in reversed(range(self.steps_layout.count())):
                child = self.steps_layout.itemAt(i).widget()
                if child:
                    child.deleteLater()
                    
            # Add new steps
            for step in steps:
                step_widget = self.create_step_widget(step)
                self.steps_layout.addWidget(step_widget)
        except Exception as e:
            print(f"Error updating installation steps: {e}")
            
    def create_step_widget(self, step_data):
        """Create a widget for displaying a single installation step"""
        step_widget = QWidget()
        step_layout = QHBoxLayout(step_widget)
        step_layout.setContentsMargins(5, 2, 5, 2)
        
        # Status icon
        status = step_data.get('status', 'pending')
        if status == 'completed':
            icon = "✅"
            color = "#0d7377"
        elif status == 'already_installed':
            icon = "ℹ️"
            color = "#17a2b8"  # Info blue for already installed
        elif status == 'running':
            icon = "🔄"
            color = "#ff9500"
        elif status == 'failed':
            icon = "❌"
            color = "#ff3333"
        else:
            icon = "⏳"
            color = "#888888"
            
        icon_label = QLabel(icon)
        icon_label.setMinimumWidth(30)
        
        # Step description
        step_label = QLabel(step_data.get('description', 'Unknown step'))
        step_label.setStyleSheet(f"color: {color};")
        
        # Time info
        time_info = step_data.get('time', '')
        time_label = QLabel(time_info)
        time_label.setStyleSheet("color: #888888; font-size: 9pt;")
        time_label.setMinimumWidth(60)
        
        step_layout.addWidget(icon_label)
        step_layout.addWidget(step_label)
        step_layout.addStretch()
        step_layout.addWidget(time_label)
        
        return step_widget
        
    def reset_progress(self):
        """Reset all progress indicators"""
        try:
            self.overall_progress.setValue(0)
            self.current_progress.setValue(0)
            self.overall_label.setText("Ready to start installation...")
            self.current_app_label.setText("No application currently being installed")
            self.current_step_label.setText("Waiting to start...")
            self.apps_completed_label.setText("Completed: 0")
            self.apps_failed_label.setText("Failed: 0")
            self.apps_already_installed_label.setText("Already Installed: 0")
            self.apps_remaining_label.setText("Remaining: 0")
            self.time_elapsed_label.setText("Time: 00:00")
            
            # Clear steps
            for i in reversed(range(self.steps_layout.count())):
                child = self.steps_layout.itemAt(i).widget()
                if child:
                    child.deleteLater()
        except Exception as e:
            print(f"Error resetting progress: {e}")
