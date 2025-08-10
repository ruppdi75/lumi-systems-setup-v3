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
    
    def __init__(self, selected_apps, config, sudo_password=None):
        super().__init__()
        self.selected_apps = selected_apps
        self.config = config
        self.sudo_password = sudo_password
        self.logger = logging.getLogger(__name__)
        
        self.script_runner = ScriptRunner(sudo_password)
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
            
            # Force immediate progress update
            self.update_progress_display()
            
            # Check if application is already installed
            is_already_installed = self.check_if_installed(app_name)
            
            if is_already_installed:
                # Mark as already installed
                app_result = {
                    'name': app_name,
                    'status': 'already_installed',
                    'time': '00:00',
                    'error': None,
                    'details': 'Application is already installed'
                }
                self.results['applications'].append(app_result)
                
                # Update progress tracker
                self.progress_tracker.complete_app_installation(app_name, True, "Already installed")
                self.log_message.emit("INFO", f"ℹ️ {app_name} is already installed - skipping")
                
                # Force progress update
                self.update_progress_display()
                continue
            
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
                
            # Force progress update after completion
            self.update_progress_display()
                
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
            
            for i, (step_name, command) in enumerate(commands):
                if self.should_stop:
                    return False, "Installation stopped by user", self.format_time(time.time() - start_time)
                    
                # Wait if paused
                while self.is_paused and not self.should_stop:
                    time.sleep(0.1)
                    
                # Update progress tracker with current step
                step_progress = int((i / len(commands)) * 100)
                self.progress_tracker.update_app_step(step_name, step_progress)
                
                # Force progress update to display current step
                self.update_progress_display()
                
                self.log_message.emit("DEBUG", f"Executing: {step_name}")
                self.status_updated.emit(f"Installing {app_name}: {step_name}")
                
                # Execute command
                success, output, error = self.script_runner.run_command(command)
                
                if not success:
                    # Check if this is a repository-related failure that we can recover from
                    if self.is_recoverable_error(step_name, error):
                        self.log_message.emit("WARNING", f"⚠️ {step_name} failed but continuing: {error}")
                        # Try to clean up any problematic repositories
                        # COMMENTED OUT: Spotify-related cleanup
                        # if "apt update" in command.lower() and "spotify" in error.lower():
                        #     self.cleanup_spotify_repository()
                        continue
                    else:
                        install_time = self.format_time(time.time() - start_time)
                        return False, f"{step_name} failed: {error}", install_time
                    
            install_time = self.format_time(time.time() - start_time)
            return True, None, install_time
            
        except Exception as e:
            install_time = self.format_time(time.time() - start_time)
            return False, str(e), install_time
    
    def is_recoverable_error(self, step_name, error):
        """Check if an error is recoverable and installation can continue"""
        recoverable_patterns = [
            "Update package lists",
            "apt update",
            "OpenPGP",
            "NO_PUBKEY",
            "not signed",
            "repository",
            "GPG"
        ]
        
        # Only consider repository/update related steps as recoverable
        if any(pattern.lower() in step_name.lower() for pattern in ["update", "repository", "gpg", "key"]):
            return any(pattern.lower() in error.lower() for pattern in recoverable_patterns)
        
        return False
    
    # COMMENTED OUT: Spotify repository cleanup method
    # def cleanup_spotify_repository(self):
    #     """Clean up problematic Spotify repository"""
    #     try:
    #         self.log_message.emit("INFO", "🔧 Cleaning up Spotify repository...")
    #         
    #         # Remove problematic Spotify sources
    #         cleanup_commands = [
    #             'sudo rm -f /etc/apt/sources.list.d/spotify.list',
    #             'sudo rm -f /etc/apt/trusted.gpg.d/spotify.gpg',
    #             'sudo apt update'
    #         ]
    #         
    #         for cmd in cleanup_commands:
    #             success, output, error = self.script_runner.run_command(cmd)
    #             if not success and "apt update" not in cmd:
    #                 self.log_message.emit("WARNING", f"Cleanup command failed: {cmd}")
    #                 
    #         self.log_message.emit("INFO", "✅ Spotify repository cleanup completed")
    #         
    #     except Exception as e:
    #         self.log_message.emit("ERROR", f"Failed to cleanup Spotify repository: {e}")
    
    def check_if_installed(self, app_name):
        """Check if an application is already installed"""
        try:
            # Define check commands for each application
            check_commands = {
                'firefox': 'which firefox',
                'thunderbird': 'which thunderbird',
                'libreoffice': 'which libreoffice',
                'gimp': 'which gimp',
                'vlc': 'which vlc',
                'code': 'which code',
                'git': 'which git',
                'python3': 'which python3',
                'nodejs': 'which node',
                'docker': 'which docker',
                'rustdesk': 'which rustdesk',
                'steam': 'which steam',
                'discord': 'flatpak list | grep -i discord',
                # COMMENTED OUT: Spotify check
                # 'spotify': 'flatpak list | grep -i spotify',
                'htop': 'which htop',
                'curl': 'which curl',
                'wget': 'which wget',
                'zip': 'which zip'
            }
            
            if app_name not in check_commands:
                # If we don't have a check command, assume it's not installed
                return False
            
            command = check_commands[app_name]
            success, output, error = self.script_runner.run_command(command)
            
            # If command succeeds and has output, the application is likely installed
            return success and output.strip() != ""
            
        except Exception as e:
            self.logger.warning(f"Could not check if {app_name} is installed: {e}")
            # If we can't check, assume it's not installed to be safe
            return False
            
    def get_installation_steps(self):
        """Get installation steps for each application"""
        return {
            'firefox': [
                ('Update package lists', 'sudo apt update'),
                ('Install Firefox', 'sudo apt install -y firefox'),
            ],
            'thunderbird': [
                ('Update package lists', 'sudo apt update'),
                ('Install Thunderbird', 'sudo apt install -y thunderbird'),
            ],
            'libreoffice': [
                ('Update package lists', 'sudo apt update'),
                ('Install LibreOffice', 'sudo apt install -y libreoffice'),
            ],
            'gimp': [
                ('Update package lists', 'sudo apt update'),
                ('Install GIMP', 'sudo apt install -y gimp'),
            ],
            'vlc': [
                ('Update package lists', 'sudo apt update'),
                ('Install VLC', 'sudo apt install -y vlc'),
            ],
            'code': [
                ('Add Microsoft GPG key', 'wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg'),
                ('Install GPG key', 'sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/'),
                ('Add VS Code repository', 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list'),
                ('Update package lists', 'sudo apt update'),
                ('Install VS Code', 'sudo apt install -y code'),
            ],
            'git': [
                ('Update package lists', 'sudo apt update'),
                ('Install Git', 'sudo apt install -y git'),
            ],
            'python3': [
                ('Update package lists', 'sudo apt update'),
                ('Install Python 3', 'sudo apt install -y python3 python3-pip'),
            ],
            'nodejs': [
                ('Update package lists', 'sudo apt update'),
                ('Install Node.js', 'sudo apt install -y nodejs npm'),
            ],
            'docker': [
                ('Update package lists', 'sudo apt update'),
                ('Install prerequisites', 'sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release'),
                ('Add Docker GPG key', 'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg'),
                ('Add Docker repository', 'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null'),
                ('Update package lists', 'sudo apt update'),
                ('Install Docker', 'sudo apt install -y docker-ce docker-ce-cli containerd.io'),
            ],
            'rustdesk': [
                ('Download RustDesk', 'wget -O /tmp/rustdesk.deb https://github.com/rustdesk/rustdesk/releases/download/1.2.3/rustdesk-1.2.3-x86_64.deb'),
                ('Install RustDesk', 'sudo dpkg -i /tmp/rustdesk.deb || sudo apt-get install -f -y'),
            ],
            'steam': [
                ('Enable multiverse repository', 'sudo add-apt-repository multiverse -y'),
                ('Update package lists', 'sudo apt update'),
                ('Install Steam', 'sudo apt install -y steam'),
            ],
            'discord': [
                ('Download Discord', 'wget -O /tmp/discord.deb "https://discordapp.com/api/download?platform=linux&format=deb"'),
                ('Install Discord', 'sudo dpkg -i /tmp/discord.deb || sudo apt-get install -f -y'),
            ],
            # COMMENTED OUT: Spotify installation steps
            # 'spotify': [
            #     ('Install Flatpak if needed', 'sudo apt update && sudo apt install -y flatpak'),
            #     ('Add Flathub repository', 'flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo'),
            #     ('Install Spotify via Flatpak', 'flatpak install -y flathub com.spotify.Client'),
            # ],
            'htop': [
                ('Update package lists', 'sudo apt update'),
                ('Install htop', 'sudo apt install -y htop'),
            ],
            'curl': [
                ('Update package lists', 'sudo apt update'),
                ('Install curl', 'sudo apt install -y curl'),
            ],
            'wget': [
                ('Update package lists', 'sudo apt update'),
                ('Install wget', 'sudo apt install -y wget'),
            ],
            'zip': [
                ('Update package lists', 'sudo apt update'),
                ('Install zip utilities', 'sudo apt install -y zip unzip'),
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
