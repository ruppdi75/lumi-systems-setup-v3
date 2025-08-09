"""
Results display widget for Lumi-Setup v2.0
"""

from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QGroupBox, QTextEdit, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class ResultsWidget(QWidget):
    """Widget for displaying installation results"""
    
    def __init__(self):
        super().__init__()
        self.results_data = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Results header
        header_layout = QHBoxLayout()
        
        header_label = QLabel("📊 Installation Results")
        header_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        
        # Export buttons
        export_pdf_btn = QPushButton("📄 Export PDF")
        export_pdf_btn.clicked.connect(self.export_pdf)
        
        export_html_btn = QPushButton("🌐 Export HTML")
        export_html_btn.clicked.connect(self.export_html)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(export_pdf_btn)
        header_layout.addWidget(export_html_btn)
        
        layout.addLayout(header_layout)
        
        # Summary section
        self.create_summary_section(layout)
        
        # Results table
        self.create_results_table(layout)
        
        # Details section
        self.create_details_section(layout)
        
    def create_summary_section(self, parent_layout):
        """Create the summary section"""
        summary_group = QGroupBox("📈 Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        # Summary statistics
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: 0")
        self.success_label = QLabel("✅ Success: 0")
        self.failed_label = QLabel("❌ Failed: 0")
        self.skipped_label = QLabel("⏭️ Skipped: 0")
        self.time_label = QLabel("⏱️ Time: 00:00")
        
        # Style labels
        self.total_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        self.success_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #0d7377;")
        self.failed_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #ff3333;")
        self.skipped_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #ff9500;")
        self.time_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.success_label)
        stats_layout.addWidget(self.failed_label)
        stats_layout.addWidget(self.skipped_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.time_label)
        
        summary_layout.addLayout(stats_layout)
        
        # Success rate bar
        self.success_rate_label = QLabel("Success Rate: 0%")
        self.success_rate_label.setStyleSheet("font-size: 11pt; margin-top: 5px;")
        summary_layout.addWidget(self.success_rate_label)
        
        parent_layout.addWidget(summary_group)
        
    def create_results_table(self, parent_layout):
        """Create the results table"""
        table_group = QGroupBox("📋 Detailed Results")
        table_layout = QVBoxLayout(table_group)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Application", "Status", "Time", "Details"])
        
        # Configure table
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #555555;
                background-color: #2b2b2b;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #555555;
            }
            QTableWidget::item:selected {
                background-color: #0d7377;
            }
        """)
        
        table_layout.addWidget(self.results_table)
        parent_layout.addWidget(table_group)
        
    def create_details_section(self, parent_layout):
        """Create the details section"""
        details_group = QGroupBox("🔍 Installation Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        self.details_text.setPlainText("Select an application from the table above to view detailed information.")
        
        details_layout.addWidget(self.details_text)
        parent_layout.addWidget(details_group)
        
        # Connect table selection to details update
        self.results_table.itemSelectionChanged.connect(self.update_details)
        
    def display_results(self, results_data):
        """Display installation results"""
        self.results_data = results_data
        
        if not results_data:
            return
            
        # Update summary
        self.update_summary(results_data)
        
        # Update table
        self.update_results_table(results_data)
        
    def update_summary(self, results_data):
        """Update the summary section"""
        total = len(results_data.get('applications', []))
        success_count = len([app for app in results_data.get('applications', []) 
                           if app.get('status') == 'success'])
        failed_count = len([app for app in results_data.get('applications', []) 
                          if app.get('status') == 'failed'])
        already_installed_count = len([app for app in results_data.get('applications', []) 
                                     if app.get('status') == 'already_installed'])
        skipped_count = len([app for app in results_data.get('applications', []) 
                           if app.get('status') == 'skipped'])
        
        # Update labels
        self.total_label.setText(f"Total: {total}")
        self.success_label.setText(f"✅ Success: {success_count}")
        self.failed_label.setText(f"❌ Failed: {failed_count}")
        self.skipped_label.setText(f"ℹ️ Already Installed: {already_installed_count}")
        
        # Calculate and display success rate (including already installed as successful)
        total_successful = success_count + already_installed_count
        success_rate = (total_successful / total * 100) if total > 0 else 0
        self.success_rate_label.setText(f"Success Rate: {success_rate:.1f}%")
        
        # Update time
        total_time = results_data.get('total_time', '00:00')
        self.time_label.setText(f"⏱️ Time: {total_time}")
        
    def update_results_table(self, results_data):
        """Update the results table"""
        applications = results_data.get('applications', [])
        
        self.results_table.setRowCount(len(applications))
        
        for row, app in enumerate(applications):
            # Application name
            name_item = QTableWidgetItem(app.get('name', 'Unknown'))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # Status with icon
            status = app.get('status', 'unknown')
            if status == 'success':
                status_text = "✅ Success"
                status_color = "#0d7377"
            elif status == 'failed':
                status_text = "❌ Failed"
                status_color = "#ff3333"
            elif status == 'already_installed':
                status_text = "ℹ️ Already Installed"
                status_color = "#17a2b8"
            elif status == 'skipped':
                status_text = "⏭️ Skipped"
                status_color = "#ff9500"
            else:
                status_text = "❓ Unknown"
                status_color = "#888888"
                
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor(status_color))
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # Installation time
            time_item = QTableWidgetItem(app.get('time', 'N/A'))
            time_item.setFlags(time_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # Details/Error message
            details = app.get('error', app.get('details', 'No additional details'))
            details_item = QTableWidgetItem(details[:100] + "..." if len(details) > 100 else details)
            details_item.setFlags(details_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # Add items to table
            self.results_table.setItem(row, 0, name_item)
            self.results_table.setItem(row, 1, status_item)
            self.results_table.setItem(row, 2, time_item)
            self.results_table.setItem(row, 3, details_item)
            
    def update_details(self):
        """Update details section based on selected row"""
        current_row = self.results_table.currentRow()
        
        if current_row >= 0 and self.results_data:
            applications = self.results_data.get('applications', [])
            if current_row < len(applications):
                app = applications[current_row]
                
                details_text = f"Application: {app.get('name', 'Unknown')}\n"
                details_text += f"Status: {app.get('status', 'Unknown')}\n"
                details_text += f"Installation Time: {app.get('time', 'N/A')}\n"
                details_text += f"Package Manager: {app.get('package_manager', 'N/A')}\n\n"
                
                if app.get('status') == 'failed':
                    details_text += f"Error Details:\n{app.get('error', 'No error details available')}\n\n"
                    
                if app.get('log'):
                    details_text += f"Installation Log:\n{app.get('log', 'No log available')}"
                else:
                    details_text += "Installation completed successfully."
                    
                self.details_text.setPlainText(details_text)
            else:
                self.details_text.setPlainText("No details available for selected application.")
        else:
            self.details_text.setPlainText("Select an application from the table above to view detailed information.")
            
    def export_pdf(self):
        """Export results to PDF"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        if not self.results_data:
            QMessageBox.warning(self, "No Data", "No installation results to export.")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Results to PDF", 
            f"lumi-setup-results-{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if filename:
            try:
                # This would require reportlab or similar PDF library
                # For now, show a message about the feature
                QMessageBox.information(self, "PDF Export", 
                                      "PDF export feature will be implemented in a future version.\n"
                                      "Please use HTML export for now.")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export PDF:\n{str(e)}")
                
    def export_html(self):
        """Export results to HTML"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        if not self.results_data:
            QMessageBox.warning(self, "No Data", "No installation results to export.")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Results to HTML", 
            f"lumi-setup-results-{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML Files (*.html);;All Files (*)"
        )
        
        if filename:
            try:
                html_content = self.generate_html_report()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                    
                QMessageBox.information(self, "Export Complete", 
                                      f"Results exported successfully to:\n{filename}")
                                      
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export HTML:\n{str(e)}")
                
    def generate_html_report(self):
        """Generate HTML report content"""
        if not self.results_data:
            return ""
            
        applications = self.results_data.get('applications', [])
        total = len(applications)
        success_count = len([app for app in applications if app.get('status') == 'success'])
        failed_count = len([app for app in applications if app.get('status') == 'failed'])
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Lumi-Setup v2.0 Installation Results</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .header {{ background-color: #0d7377; color: white; padding: 20px; border-radius: 5px; }}
                .summary {{ background-color: white; padding: 15px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .results-table {{ width: 100%; border-collapse: collapse; background-color: white; border-radius: 5px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .results-table th {{ background-color: #0d7377; color: white; padding: 12px; text-align: left; }}
                .results-table td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                .success {{ color: #0d7377; font-weight: bold; }}
                .failed {{ color: #ff3333; font-weight: bold; }}
                .skipped {{ color: #ff9500; font-weight: bold; }}
                .footer {{ margin-top: 20px; text-align: center; color: #888; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Lumi-Setup v2.0 Installation Results</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>📈 Summary</h2>
                <p><strong>Total Applications:</strong> {total}</p>
                <p><strong>Successfully Installed:</strong> <span class="success">{success_count}</span></p>
                <p><strong>Failed Installations:</strong> <span class="failed">{failed_count}</span></p>
                <p><strong>Success Rate:</strong> {success_rate:.1f}%</p>
                <p><strong>Total Time:</strong> {self.results_data.get('total_time', 'N/A')}</p>
            </div>
            
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Application</th>
                        <th>Status</th>
                        <th>Time</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for app in applications:
            status = app.get('status', 'unknown')
            status_class = status if status in ['success', 'failed', 'skipped'] else 'unknown'
            status_text = {
                'success': '✅ Success',
                'failed': '❌ Failed',
                'skipped': '⏭️ Skipped'
            }.get(status, '❓ Unknown')
            
            html += f"""
                    <tr>
                        <td>{app.get('name', 'Unknown')}</td>
                        <td class="{status_class}">{status_text}</td>
                        <td>{app.get('time', 'N/A')}</td>
                        <td>{app.get('error', app.get('details', 'No details'))}</td>
                    </tr>
            """
            
        html += """
                </tbody>
            </table>
            
            <div class="footer">
                <p>Generated by Lumi-Setup v2.0 - Modern AnduinOS Software Installer</p>
                <p>© 2024 Lumi-Systems</p>
            </div>
        </body>
        </html>
        """
        
        return html
        
    def export_results(self):
        """Export results (called from main window)"""
        self.export_html()
        
    def clear_results(self):
        """Clear all results"""
        self.results_data = None
        self.results_table.setRowCount(0)
        self.details_text.setPlainText("No installation results available.")
        
        # Reset summary
        self.total_label.setText("Total: 0")
        self.success_label.setText("✅ Success: 0")
        self.failed_label.setText("❌ Failed: 0")
        self.skipped_label.setText("⏭️ Skipped: 0")
        self.time_label.setText("⏱️ Time: 00:00")
        self.success_rate_label.setText("Success Rate: 0%")
