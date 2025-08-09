"""
Installation manager for Lumi-Setup v2.0
"""

import logging
import time
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from .script_runner import ScriptRunner
from .progress_tracker import ProgressTracker

class InstallationManager(QObject):
    """Manages the installation process"""
    
    # Signals
    progress_updated = pyqtSignal(dict)
    status_updated = pyqtSignal(str)
    log_message = pyqtSignal(str, str)  # level, message
    installation_completed = pyqtSignal()
    installation_failed = pyqtSignal(str)
    
    def __init__(self, selected_apps, config):
        super().__init__()
        self.selected_apps = selected_apps
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.script_runner = ScriptRunner()
        self.progress_tracker = ProgressTracker()
        
        self.is_running = False
        self.is_paused = False
        self.should_stop = False
        
        self.start_time = None
        self.results = {
            'applications': [],
            'total_time': '00:00',
            'start_time': None,
            'end_time': None
        }
        
        # Timer for progress updates
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress_display)
        
        # Connect script runner signals
        self.script_runner.output_received.connect(self.handle_script_output)
        self.script_runner.error_received.connect(self.handle_script_error)
        self.script_runner.command_completed.connect(self.handle_command_completed)
        
    def start_installation(self):
        """Start the installation process"""
        self.logger.info("Starting installation process")
        self.log_message.emit("INFO", "Starting installation process")
        
        self.is_running = True
        self.start_time = datetime.now()
        self.results['start_time'] = self.start_time.isoformat()
        
        # Start progress timer
        self.progress_timer.start(1000)  # Update every second
        
        try:
            self.run_installation()
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            self.installation_failed.emit(str(e))
            
    def run_installation(self):
        """Run the actual installation process"""
        total_apps = len(self.selected_apps)
        self.progress_tracker.set_total_apps(total_apps)
        
        self.log_message.emit("INFO", f"Installing {total_apps} applications")
        
        # Define installation steps for each application
        installation_steps = self.get_installation_steps()
        
        for i, app_name in enumerate(self.selected_apps):
            if self.should_stop:
                self.log_message.emit("WARNING", "Installation stopped by user")
                break
                
            # Wait if paused
            while self.is_paused and not self.should_stop:
                time.sleep(0.1)
                
            if self.should_stop:
                break
                
            self.log_message.emit("INFO", f"Installing {app_name} ({i+1}/{total_apps})")
            self.status_updated.emit(f"Installing {app_name}")
            
            # Update progress
            self.progress_tracker.start_app_installation(app_name)
            
            # Install the application
            success, error_msg, install_time = self.install_application(app_name, installation_steps.get(app_name, []))
            
            # Record result
            app_result = {
                'name': app_name,
                'status': 'success' if success else 'failed',
                'time': install_time,
                'error': error_msg if not success else None,
                'details': f"Installation {'completed successfully' if success else 'failed'}"
            }
            self.results['applications'].append(app_result)
            
            # Update progress tracker
            if success:
                self.progress_tracker.complete_app_installation(app_name, True)
                self.log_message.emit("INFO", f"✅ {app_name} installed successfully")
            else:
                self.progress_tracker.complete_app_installation(app_name, False, error_msg)
                self.log_message.emit("ERROR", f"❌ {app_name} installation failed: {error_msg}")
                
        # Complete installation
        self.complete_installation()
        
    def install_application(self, app_name, steps):
        """Install a single application"""
        start_time = time.time()
        
        try:
            # Map application names to installation commands
            install_commands = self.get_install_commands()
            
            if app_name not in install_commands:
                return False, f"Unknown application: {app_name}", "00:00"
                
            commands = install_commands[app_name]
            
            for step_name, command in commands:
                if self.should_stop:
                    return False, "Installation stopped by user", self.format_time(time.time() - start_time)
                    
                # Wait if paused
                while self.is_paused and not self.should_stop:
                    time.sleep(0.1)
                    
                self.log_message.emit("DEBUG", f"Executing: {step_name}")
                self.status_updated.emit(f"Installing {app_name}: {step_name}")
                
                # Execute command
                success, output, error = self.script_runner.run_command(command)
                
                if not success:
                    install_time = self.format_time(time.time() - start_time)
                    return False, f"{step_name} failed: {error}", install_time
                    
            install_time = self.format_time(time.time() - start_time)
            return True, None, install_time
            
        except Exception as e:
            install_time = self.format_time(time.time() - start_time)
            return False, str(e), install_time
            
    def get_installation_steps(self):
        """Get installation steps for each application"""
        return {
            'firefox': [
                ('Update package lists', 'apt update'),
                ('Install Firefox', 'apt install -y firefox'),
            ],
            'thunderbird': [
                ('Update package lists', 'apt update'),
                ('Install Thunderbird', 'apt install -y thunderbird'),
            ],
            'libreoffice': [
                ('Update package lists', 'apt update'),
                ('Install LibreOffice', 'apt install -y libreoffice'),
            ],
            'gimp': [
                ('Update package lists', 'apt update'),
                ('Install GIMP', 'apt install -y gimp'),
            ],
            'vlc': [
                ('Update package lists', 'apt update'),
                ('Install VLC', 'apt install -y vlc'),
            ],
            'code': [
                ('Add Microsoft GPG key', 'wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg'),
                ('Install GPG key', 'install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/'),
                ('Add VS Code repository', 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'),
                ('Update package lists', 'apt update'),
                ('Install VS Code', 'apt install -y code'),
            ],
            'git': [
                ('Update package lists', 'apt update'),
                ('Install Git', 'apt install -y git'),
            ],
            'python3': [
                ('Update package lists', 'apt update'),
                ('Install Python 3', 'apt install -y python3 python3-pip'),
            ],
            'nodejs': [
                ('Update package lists', 'apt update'),
                ('Install Node.js', 'apt install -y nodejs npm'),
            ],
            'docker': [
                ('Update package lists', 'apt update'),
                ('Install prerequisites', 'apt install -y apt-transport-https ca-certificates curl gnupg lsb-release'),
                ('Add Docker GPG key', 'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg'),
                ('Add Docker repository', 'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null'),
                ('Update package lists', 'apt update'),
                ('Install Docker', 'apt install -y docker-ce docker-ce-cli containerd.io'),
            ],
            'rustdesk': [
                ('Download RustDesk', 'wget -O /tmp/rustdesk.deb https://github.com/rustdesk/rustdesk/releases/download/1.2.3/rustdesk-1.2.3-x86_64.deb'),
                ('Install RustDesk', 'dpkg -i /tmp/rustdesk.deb || apt-get install -f -y'),
            ],
            'steam': [
                ('Enable multiverse repository', 'add-apt-repository multiverse -y'),
                ('Update package lists', 'apt update'),
                ('Install Steam', 'apt install -y steam'),
            ],
            'discord': [
                ('Download Discord', 'wget -O /tmp/discord.deb "https://discordapp.com/api/download?platform=linux&format=deb"'),
                ('Install Discord', 'dpkg -i /tmp/discord.deb || apt-get install -f -y'),
            ],
            'spotify': [
                ('Add Spotify GPG key', 'curl -sS https://download.spotify.com/debian/pubkey_7A3A762FAFD4A51F.gpg | gpg --dearmor --yes -o /etc/apt/trusted.gpg.d/spotify.gpg'),
                ('Add Spotify repository', 'echo "deb http://repository.spotify.com stable non-free" | tee /etc/apt/sources.list.d/spotify.list'),
                ('Update package lists', 'apt update'),
                ('Install Spotify', 'apt install -y spotify-client'),
            ],
            'htop': [
                ('Update package lists', 'apt update'),
                ('Install htop', 'apt install -y htop'),
            ],
            'curl': [
                ('Update package lists', 'apt update'),
                ('Install curl', 'apt install -y curl'),
            ],
            'wget': [
                ('Update package lists', 'apt update'),
                ('Install wget', 'apt install -y wget'),
            ],
            'zip': [
                ('Update package lists', 'apt update'),
                ('Install zip utilities', 'apt install -y zip unzip'),
            ],
        }
        
    def get_install_commands(self):
        """Get installation commands for each application"""
        steps = self.get_installation_steps()
        commands = {}
        
        for app_name, app_steps in steps.items():
            commands[app_name] = app_steps
            
        return commands
        
    def complete_installation(self):
        """Complete the installation process"""
        end_time = datetime.now()
        self.results['end_time'] = end_time.isoformat()
        
        if self.start_time:
            total_time = end_time - self.start_time
            self.results['total_time'] = self.format_timedelta(total_time)
            
        self.is_running = False
        self.progress_timer.stop()
        
        self.log_message.emit("INFO", "Installation process completed")
        self.status_updated.emit("Installation completed")
        self.installation_completed.emit()
        
    def pause_installation(self):
        """Pause the installation process"""
        self.is_paused = True
        self.log_message.emit("INFO", "Installation paused")
        self.status_updated.emit("Installation paused")
        
    def resume_installation(self):
        """Resume the installation process"""
        self.is_paused = False
        self.log_message.emit("INFO", "Installation resumed")
        self.status_updated.emit("Installation resumed")
        
    def stop_installation(self):
        """Stop the installation process"""
        self.should_stop = True
        self.is_paused = False
        self.log_message.emit("WARNING", "Installation stopped by user")
        
    def update_progress_display(self):
        """Update the progress display"""
        if not self.is_running:
            return
            
        progress_data = self.progress_tracker.get_progress_data()
        
        # Add time information
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            progress_data['time_elapsed'] = self.format_timedelta(elapsed)
            
        self.progress_updated.emit(progress_data)
        
    def handle_script_output(self, output):
        """Handle script output"""
        self.log_message.emit("DEBUG", output.strip())
        
    def handle_script_error(self, error):
        """Handle script error"""
        self.log_message.emit("ERROR", error.strip())
        
    def handle_command_completed(self, success, exit_code):
        """Handle command completion"""
        if success:
            self.log_message.emit("DEBUG", f"Command completed successfully (exit code: {exit_code})")
        else:
            self.log_message.emit("ERROR", f"Command failed with exit code: {exit_code}")
            
    def get_results(self):
        """Get installation results"""
        return self.results
        
    def format_time(self, seconds):
        """Format time in seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
        
    def format_timedelta(self, td):
        """Format timedelta to MM:SS format"""
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
