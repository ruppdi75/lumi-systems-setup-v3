"""
Script runner for Lumi-Setup v2.0
Handles execution of shell commands and scripts
"""

import subprocess
import logging
import threading
import queue
import os
from PyQt6.QtCore import QObject, pyqtSignal

class ScriptRunner(QObject):
    """Handles execution of shell scripts and commands"""
    
    # Signals
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    command_completed = pyqtSignal(bool, int)  # success, exit_code
    
    def __init__(self, sudo_password=None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.sudo_password = sudo_password
        self.current_process = None
        
    def run_command(self, command, cwd=None, timeout=300):
        """
        Run a shell command and return the result
        
        Args:
            command: Command to execute
            cwd: Working directory
            timeout: Timeout in seconds
            
        Returns:
            tuple: (success, stdout, stderr)
        """
        self.logger.debug(f"Executing command: {command}")
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env['DEBIAN_FRONTEND'] = 'noninteractive'
            
            # Handle sudo commands with password
            stdin_input = None
            if command.strip().startswith('sudo') and self.sudo_password:
                # For sudo commands, provide password via stdin
                stdin_input = self.sudo_password + '\n'
            
            # Start process
            self.process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE if stdin_input else None,
                text=False,  # Use binary mode for better compatibility
                cwd=cwd,
                env=env,
                bufsize=1
            )
            
            # Read output in real-time
            threading.Thread(target=self._read_output).start()
            
            # Send password to stdin if needed for sudo commands
            if stdin_input and self.process and self.process.stdin:
                try:
                    self.process.stdin.write(stdin_input.encode('utf-8'))
                    self.process.stdin.flush()
                    self.process.stdin.close()
                except Exception as e:
                    self.logger.warning(f"Failed to send password to stdin: {e}")
            
            # Wait for process to complete
            try:
                exit_code = self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.logger.error(f"Command timed out after {timeout} seconds")
                self.kill_process()
                return False, "", f"Command timed out after {timeout} seconds"
                
            success = exit_code == 0
            self.command_completed.emit(success, exit_code)
            
            if success:
                self.logger.debug(f"Command completed successfully")
            else:
                self.logger.error(f"Command failed with exit code {exit_code}")
                
            return success, '\n'.join(self.output_lines), '\n'.join(self.error_lines)
            
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            self.error_received.emit(str(e))
            self.command_completed.emit(False, -1)
            return False, "", str(e)
            
        finally:
            self.process = None
    
    def _read_output(self):
        """Read output from process"""
        try:
            while self.process and self.process.poll() is None:
                try:
                    # Read stdout
                    if self.process and self.process.stdout:
                        line = self.process.stdout.readline()
                        if line:
                            decoded_line = line.decode('utf-8', errors='replace').rstrip()
                            self.output_received.emit(decoded_line)
                            self.output_lines.append(decoded_line)
                    
                    # Read stderr
                    if self.process and self.process.stderr:
                        line = self.process.stderr.readline()
                        if line:
                            decoded_line = line.decode('utf-8', errors='replace').rstrip()
                            self.error_received.emit(decoded_line)
                            self.error_lines.append(decoded_line)
                    
                    # Small delay to prevent CPU spinning
                    time.sleep(0.01)
                except (IOError, OSError) as e:
                    # Handle pipe errors gracefully
                    if self.process and self.process.poll() is None:
                        self.error_received.emit(f"Read error: {str(e)}")
                    break
        except Exception as e:
            self.logger.error(f"Error reading output: {e}")
            
    def run_script(self, script_path, args=None, cwd=None):
        """
        Run a shell script
        
        Args:
            script_path: Path to the script
            args: Arguments to pass to the script
            cwd: Working directory
            
        Returns:
            tuple: (success, stdout, stderr)
        """
        if not os.path.exists(script_path):
            error_msg = f"Script not found: {script_path}"
            self.logger.error(error_msg)
            return False, "", error_msg
            
        # Make script executable
        os.chmod(script_path, 0o755)
        
        # Build command
        command = f"bash {script_path}"
        if args:
            command += f" {' '.join(args)}"
            
        return self.run_command(command, cwd=cwd)
        
    def kill_process(self):
        """Kill the running process"""
        if self.process:
            try:
                # Try SIGTERM first
                self.process.terminate()
                time.sleep(0.5)
                
                # If still running, use SIGKILL
                if self.process.poll() is None:
                    self.process.kill()
                    try:
                        self.process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        # Force kill if timeout
                        import os
                        import signal
                        os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                
                self.process = None
                return True
            except Exception as e:
                self.error_received.emit(f"Failed to kill process: {str(e)}")
                # Try to clean up anyway
                self.process = None
                return False
        return True
        
    def is_running(self):
        """Check if a process is currently running"""
        return self.process is not None and self.process.poll() is None
