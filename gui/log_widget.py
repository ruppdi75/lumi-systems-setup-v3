"""
Log display widget for Lumi-Setup v2.0
"""

import logging
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QPushButton, QComboBox, QLabel, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QTextCursor, QFont

class LogWidget(QWidget):
    """Widget for displaying installation logs"""
    
    def __init__(self):
        super().__init__()
        self.log_levels = {
            'DEBUG': '#888888',
            'INFO': '#ffffff',
            'WARNING': '#ff9500',
            'ERROR': '#ff3333',
            'CRITICAL': '#ff0000'
        }
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Log controls
        controls_layout = QHBoxLayout()
        
        # Log level filter
        level_label = QLabel("Level:")
        self.level_combo = QComboBox()
        self.level_combo.addItems(['ALL', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        self.level_combo.setCurrentText('INFO')
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        
        # Auto-scroll checkbox
        self.auto_scroll_cb = QCheckBox("Auto-scroll")
        self.auto_scroll_cb.setChecked(True)
        
        # Clear button
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        
        # Export button
        export_btn = QPushButton("Export Logs")
        export_btn.clicked.connect(self.export_logs)
        
        controls_layout.addWidget(level_label)
        controls_layout.addWidget(self.level_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(self.auto_scroll_cb)
        controls_layout.addWidget(clear_btn)
        controls_layout.addWidget(export_btn)
        
        layout.addLayout(controls_layout)
        
        # Log display area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        
        layout.addWidget(self.log_display)
        
        # Log statistics
        stats_layout = QHBoxLayout()
        
        self.total_messages_label = QLabel("Messages: 0")
        self.errors_label = QLabel("Errors: 0")
        self.warnings_label = QLabel("Warnings: 0")
        
        stats_layout.addWidget(self.total_messages_label)
        stats_layout.addWidget(self.errors_label)
        stats_layout.addWidget(self.warnings_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # Initialize counters
        self.message_counts = {
            'total': 0,
            'DEBUG': 0,
            'INFO': 0,
            'WARNING': 0,
            'ERROR': 0,
            'CRITICAL': 0
        }
        
        self.all_messages = []  # Store all messages for filtering
        
    @pyqtSlot(str, str)
    def add_log_message(self, level, message):
        """Add a new log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create log entry
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'full_text': f"[{timestamp}] {level}: {message}"
        }
        
        # Store message
        self.all_messages.append(log_entry)
        
        # Update counters
        self.message_counts['total'] += 1
        if level in self.message_counts:
            self.message_counts[level] += 1
            
        # Update statistics display
        self.update_statistics()
        
        # Apply current filter and display
        self.filter_logs()
        
    def filter_logs(self):
        """Filter logs based on selected level"""
        selected_level = self.level_combo.currentText()
        
        # Clear display
        self.log_display.clear()
        
        # Filter and display messages
        for entry in self.all_messages:
            if selected_level == 'ALL' or entry['level'] == selected_level:
                self.append_formatted_message(entry)
                
        # Auto-scroll to bottom if enabled
        if self.auto_scroll_cb.isChecked():
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_display.setTextCursor(cursor)
            
    def append_formatted_message(self, entry):
        """Append a formatted message to the display"""
        level = entry['level']
        color = self.log_levels.get(level, '#ffffff')
        
        # Format message with color
        formatted_message = f'<span style="color: {color};">{entry["full_text"]}</span><br>'
        
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(formatted_message)
        
    def update_statistics(self):
        """Update the statistics display"""
        total = self.message_counts['total']
        errors = self.message_counts['ERROR'] + self.message_counts['CRITICAL']
        warnings = self.message_counts['WARNING']
        
        self.total_messages_label.setText(f"Messages: {total}")
        self.errors_label.setText(f"Errors: {errors}")
        self.warnings_label.setText(f"Warnings: {warnings}")
        
        # Update label colors based on counts
        if errors > 0:
            self.errors_label.setStyleSheet("color: #ff3333; font-weight: bold;")
        else:
            self.errors_label.setStyleSheet("color: #ffffff;")
            
        if warnings > 0:
            self.warnings_label.setStyleSheet("color: #ff9500; font-weight: bold;")
        else:
            self.warnings_label.setStyleSheet("color: #ffffff;")
            
    def clear_logs(self):
        """Clear all log messages"""
        self.log_display.clear()
        self.all_messages.clear()
        
        # Reset counters
        for key in self.message_counts:
            self.message_counts[key] = 0
            
        self.update_statistics()
        
    def export_logs(self):
        """Export logs to file"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Logs", 
            f"lumi-setup-logs-{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Lumi-Setup v2.0 Installation Logs\n")
                    f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for entry in self.all_messages:
                        f.write(f"{entry['full_text']}\n")
                        
                    f.write(f"\n" + "=" * 50 + "\n")
                    f.write(f"Statistics:\n")
                    f.write(f"Total Messages: {self.message_counts['total']}\n")
                    f.write(f"Debug: {self.message_counts['DEBUG']}\n")
                    f.write(f"Info: {self.message_counts['INFO']}\n")
                    f.write(f"Warning: {self.message_counts['WARNING']}\n")
                    f.write(f"Error: {self.message_counts['ERROR']}\n")
                    f.write(f"Critical: {self.message_counts['CRITICAL']}\n")
                    
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Export Complete", 
                                      f"Logs exported successfully to:\n{filename}")
                                      
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Export Failed", 
                                   f"Failed to export logs:\n{str(e)}")
                                   
    def get_log_text(self):
        """Get all log text as plain text"""
        return '\n'.join([entry['full_text'] for entry in self.all_messages])
