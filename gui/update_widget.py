#!/usr/bin/env python3
"""
Update Widget for displaying software update information
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QTextEdit,
                            QGroupBox, QProgressBar, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor
from pathlib import Path
import json
import logging
from datetime import datetime

from src.updater import SourceChecker, ManifestGenerator

logger = logging.getLogger(__name__)

class UpdateCheckWorker(QThread):
    """Worker thread for checking updates"""
    progress = pyqtSignal(str)
    result = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, project_root):
        super().__init__()
        self.project_root = project_root
        
    def run(self):
        try:
            self.progress.emit("Initializing update checker...")
            
            manifest_dir = self.project_root / "manifests"
            log_dir = self.project_root / "logs" / "updates"
            
            self.progress.emit("Checking software sources...")
            checker = SourceChecker(manifest_dir)
            
            self.progress.emit("Analyzing updates...")
            updates = checker.check_all_sources()
            
            if updates:
                self.progress.emit("Generating manifest...")
                manifest_gen = ManifestGenerator(manifest_dir, log_dir)
                manifest = manifest_gen.generate_manifest(updates, checker.current_sources)
                self.result.emit(manifest)
            else:
                self.result.emit({"updates_found": 0, "updates": {}})
                
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            self.error.emit(str(e))

class UpdateWidget(QWidget):
    """Widget for managing and displaying software updates"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_root = Path(__file__).parent.parent
        self.init_ui()
        self.load_last_manifest()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Software Update Manager")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.check_button = QPushButton("Check for Updates")
        self.check_button.clicked.connect(self.check_updates)
        header_layout.addWidget(self.check_button)
        
        layout.addLayout(header_layout)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("QLabel { color: #0d7377; }")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Updates table
        updates_group = QGroupBox("Available Updates")
        updates_layout = QVBoxLayout()
        
        self.updates_table = QTableWidget()
        self.updates_table.setColumnCount(5)
        self.updates_table.setHorizontalHeaderLabels([
            "Application", "Current Version", "Latest Version", "Type", "Status"
        ])
        
        # Configure table
        header = self.updates_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.updates_table.setAlternatingRowColors(True)
        self.updates_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        updates_layout.addWidget(self.updates_table)
        updates_group.setLayout(updates_layout)
        layout.addWidget(updates_group)
        
        # Details section
        details_group = QGroupBox("Update Details")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_button = QPushButton("Apply Updates to Scripts")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply_updates)
        button_layout.addWidget(self.apply_button)
        
        self.export_button = QPushButton("Export Manifest")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.export_manifest)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def load_last_manifest(self):
        """Load the last update manifest if available"""
        manifest_file = self.project_root / "manifests" / "current_manifest.json"
        
        if manifest_file.exists():
            try:
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                self.display_manifest(manifest)
                self.status_label.setText(f"Last checked: {manifest.get('timestamp', 'Unknown')}")
            except Exception as e:
                logger.error(f"Failed to load manifest: {e}")
                
    def check_updates(self):
        """Start update check in background thread"""
        self.check_button.setEnabled(False)
        self.apply_button.setEnabled(False)
        self.export_button.setEnabled(False)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        self.status_label.setText("Checking for updates...")
        
        # Start worker thread
        self.worker = UpdateCheckWorker(self.project_root)
        self.worker.progress.connect(self.on_progress)
        self.worker.result.connect(self.on_result)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_progress(self, message):
        """Handle progress updates"""
        self.status_label.setText(message)
        
    def on_result(self, manifest):
        """Handle update check results"""
        self.progress_bar.setVisible(False)
        self.check_button.setEnabled(True)
        
        self.current_manifest = manifest
        self.display_manifest(manifest)
        
        updates_count = manifest.get("updates_found", 0)
        if updates_count > 0:
            self.status_label.setText(f"✅ Found {updates_count} updates")
            self.status_label.setStyleSheet("QLabel { color: #14a085; }")
            self.apply_button.setEnabled(True)
            self.export_button.setEnabled(True)
        else:
            self.status_label.setText("✅ All software sources are up to date")
            self.status_label.setStyleSheet("QLabel { color: #0d7377; }")
            
    def on_error(self, error_msg):
        """Handle errors"""
        self.progress_bar.setVisible(False)
        self.check_button.setEnabled(True)
        
        self.status_label.setText(f"❌ Error: {error_msg}")
        self.status_label.setStyleSheet("QLabel { color: #d32f2f; }")
        
    def display_manifest(self, manifest):
        """Display manifest in the table"""
        updates = manifest.get("updates", {})
        
        self.updates_table.setRowCount(len(updates))
        
        for row, (app_name, update_info) in enumerate(updates.items()):
            # Application name
            self.updates_table.setItem(row, 0, QTableWidgetItem(app_name))
            
            # Current version
            current = update_info.get("current_version", "Not installed")
            self.updates_table.setItem(row, 1, QTableWidgetItem(current))
            
            # Latest version
            latest = update_info.get("latest_version", "Unknown")
            item = QTableWidgetItem(latest)
            item.setForeground(QColor("#14a085"))  # Green for new version
            self.updates_table.setItem(row, 2, item)
            
            # Type
            update_type = update_info.get("type", "Unknown")
            self.updates_table.setItem(row, 3, QTableWidgetItem(update_type))
            
            # Status
            status = "Update Available"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("#ff9800"))  # Orange
            self.updates_table.setItem(row, 4, status_item)
            
        # Update details
        if updates:
            details = f"Update Summary\n"
            details += f"{'=' * 50}\n"
            details += f"Total updates found: {len(updates)}\n\n"
            
            for app_name, info in updates.items():
                details += f"• {app_name}: {info.get('current_version', 'N/A')} → {info.get('latest_version', 'N/A')}\n"
                
            self.details_text.setPlainText(details)
        else:
            self.details_text.setPlainText("No updates available. All software is up to date.")
            
    def apply_updates(self):
        """Apply updates to installation scripts"""
        if hasattr(self, 'current_manifest'):
            try:
                manifest_gen = ManifestGenerator(
                    self.project_root / "manifests",
                    self.project_root / "logs" / "updates"
                )
                
                success = manifest_gen.apply_updates_to_scripts(self.current_manifest)
                
                if success:
                    self.status_label.setText("✅ Updates applied successfully")
                    self.status_label.setStyleSheet("QLabel { color: #4caf50; }")
                else:
                    self.status_label.setText("⚠️ Some updates could not be applied")
                    self.status_label.setStyleSheet("QLabel { color: #ff9800; }")
                    
            except Exception as e:
                logger.error(f"Failed to apply updates: {e}")
                self.status_label.setText(f"❌ Failed to apply updates: {e}")
                self.status_label.setStyleSheet("QLabel { color: #d32f2f; }")
                
    def export_manifest(self):
        """Export current manifest to file"""
        if hasattr(self, 'current_manifest'):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_file = self.project_root / f"manifest_export_{timestamp}.json"
                
                with open(export_file, 'w') as f:
                    json.dump(self.current_manifest, f, indent=2)
                    
                self.status_label.setText(f"✅ Manifest exported to {export_file.name}")
                self.status_label.setStyleSheet("QLabel { color: #4caf50; }")
                
            except Exception as e:
                logger.error(f"Failed to export manifest: {e}")
                self.status_label.setText(f"❌ Failed to export: {e}")
                self.status_label.setStyleSheet("QLabel { color: #d32f2f; }")
