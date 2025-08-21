"""
Progress tracker for Lumi-Setup v2.0
"""

import time
from datetime import datetime

class ProgressTracker:
    """Tracks installation progress and statistics"""
    
    def __init__(self):
        self.total_apps = 0
        self.completed_apps = 0
        self.failed_apps = 0
        self.already_installed_apps = 0
        self.current_app = ""
        self.current_step = ""
        self.current_app_progress = 0
        self.overall_progress = 0
        
        self.installation_steps = []
        self.app_results = {}
        
        self.start_time = None
        self.current_app_start_time = None
        
    def set_total_apps(self, total):
        """Set the total number of applications to install"""
        self.total_apps = total
        self.overall_progress = 0
        
    def start_app_installation(self, app_name):
        """Start installation of a specific application"""
        self.current_app = app_name
        self.current_step = "Preparing installation..."
        self.current_app_progress = 0
        self.current_app_start_time = time.time()
        
        # Add step to installation steps
        step = {
            'app': app_name,
            'description': f"Installing {app_name}",
            'status': 'running',
            'time': datetime.now().strftime("%H:%M:%S")
        }
        self.installation_steps.append(step)
        
    def update_app_step(self, step_description, progress=None):
        """Update the current installation step"""
        self.current_step = step_description
        
        if progress is not None:
            self.current_app_progress = progress
            
        # Update the last step in installation_steps
        if self.installation_steps:
            self.installation_steps[-1]['description'] = f"{self.current_app}: {step_description}"
            
    def complete_app_installation(self, app_name, success, error_message=None):
        """Complete installation of an application"""
        install_time = 0
        if self.current_app_start_time:
            install_time = time.time() - self.current_app_start_time
            
        # Handle different completion statuses
        if success:
            if error_message == "Already installed":
                status = 'already_installed'
                self.already_installed_apps += 1
            else:
                status = 'completed'
                self.completed_apps += 1
        else:
            self.failed_apps += 1
            status = 'failed'
            
        # Update app results
        self.app_results[app_name] = {
            'status': status,
            'time': install_time,
            'error': error_message
        }
        
        # Update overall progress
        total_processed = self.completed_apps + self.failed_apps + self.already_installed_apps
        self.overall_progress = int(total_processed / self.total_apps * 100)
        
        # Update installation steps
        if self.installation_steps:
            self.installation_steps[-1]['status'] = status
            self.installation_steps[-1]['time'] = f"{int(install_time//60):02d}:{int(install_time%60):02d}"
            
        # Reset current app info
        self.current_app = ""
        self.current_step = ""
        self.current_app_progress = 0
        
    def get_progress_data(self):
        """Get current progress data for UI updates"""
        total_processed = self.completed_apps + self.failed_apps + self.already_installed_apps
        return {
            'overall_progress': self.overall_progress,
            'overall_label': f"Installing applications... ({total_processed}/{self.total_apps})",
            'current_app': self.current_app,
            'current_step': self.current_step,
            'current_progress': self.current_app_progress,
            'completed_apps': self.completed_apps,
            'failed_apps': self.failed_apps,
            'already_installed_apps': self.already_installed_apps,
            'total_apps': self.total_apps,
            'installation_steps': self.installation_steps[-10:]  # Show last 10 steps
        }
        
    def get_statistics(self):
        """Get installation statistics"""
        # Success rate includes both completed and already installed
        successful_apps = self.completed_apps + self.already_installed_apps
        return {
            'total_apps': self.total_apps,
            'completed_apps': self.completed_apps,
            'failed_apps': self.failed_apps,
            'already_installed_apps': self.already_installed_apps,
            'success_rate': (successful_apps / self.total_apps * 100) if self.total_apps > 0 else 0,
            'app_results': self.app_results
        }
