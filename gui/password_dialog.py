"""
Password dialog for sudo authentication in Lumi-Setup v2.0
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
import subprocess
import os

class PasswordDialog(QDialog):
    """Dialog for entering sudo password"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.password = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Administrator Authentication Required")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        # Center the dialog
        if self.parent():
            parent_geo = self.parent().geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        # Icon (using system lock icon or emoji)
        icon_label = QLabel("🔒")
        icon_label.setStyleSheet("font-size: 24pt;")
        header_layout.addWidget(icon_label)
        
        # Title and description
        title_layout = QVBoxLayout()
        title_label = QLabel("Administrator Authentication Required")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        
        desc_label = QLabel("Please enter your password to install system packages:")
        desc_label.setStyleSheet("font-size: 10pt; color: #888888;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(desc_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Password input
        password_layout = QVBoxLayout()
        
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-weight: bold;")
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 12pt;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #2b2b2b;
                color: white;
            }
            QLineEdit:focus {
                border-color: #0d7377;
            }
        """)
        self.password_input.returnPressed.connect(self.accept)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        layout.addLayout(password_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                font-size: 11pt;
                background-color: #6c757d;
                border: none;
                border-radius: 4px;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        ok_button = QPushButton("Authenticate")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        ok_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                font-size: 11pt;
                font-weight: bold;
                background-color: #0d7377;
                border: none;
                border-radius: 4px;
                color: white;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        # Focus on password input
        self.password_input.setFocus()
        
    def accept(self):
        """Handle OK button click"""
        password = self.password_input.text()
        
        if not password:
            QMessageBox.warning(self, "Error", "Please enter your password.")
            return
            
        # Test the password by running a simple sudo command
        if self.verify_password(password):
            self.password = password
            super().accept()
        else:
            QMessageBox.critical(self, "Authentication Failed", 
                               "Incorrect password. Please try again.")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def verify_password(self, password):
        """Verify the sudo password"""
        try:
            # Test with a simple sudo command
            process = subprocess.Popen(
                ['sudo', '-S', 'echo', 'test'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=password + '\n', timeout=10)
            return process.returncode == 0
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
    
    def get_password(self):
        """Get the entered password"""
        return self.password

def get_sudo_password(parent=None):
    """Show password dialog and return the password if successful"""
    dialog = PasswordDialog(parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_password()
    return None
