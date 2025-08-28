"""
Script runner for Lumi-Setup v2.0
Handles execution of shell commands and scripts
"""

import subprocess
import logging
import threading
import queue
import os
import time
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
        self.process = None  # Initialize process attribute
        
    def run_command(self, command, cwd=None, timeout=120):
        """
        Run a shell command and return the result
        
        Args:
            command: Command to execute
            cwd: Working directory
            timeout: Timeout in seconds
            
        Returns:
            tuple: (success, stdout, stderr)
        """
        # Extract timeout from command if present
        if command.strip().startswith('timeout '):
            parts = command.split(None, 2)
            if len(parts) >= 3:
                try:
                    timeout = int(parts[1])
                    command = parts[2]  # Remove 'timeout X' from command
                    self.logger.debug(f"Extracted timeout {timeout}s from command")
                except (ValueError, IndexError):
                    pass
        
        self.logger.debug(f"Executing command: {command} (timeout: {timeout}s)")
        
        # Initialize output storage
        self.output_lines = []
        self.error_lines = []
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env['DEBIAN_FRONTEND'] = 'noninteractive'
            
            # Handle sudo commands with password
            stdin_input = None
            original_command = command
            
            # Modify sudo commands to use -S flag for password input
            if command.strip().startswith('sudo') and self.sudo_password:
                # Check if -S flag is already present
                if ' -S ' not in command:
                    # Insert -S flag after sudo
                    command = command.replace('sudo ', 'sudo -S ', 1)
                stdin_input = self.sudo_password + '\n'
                self.logger.debug(f"Modified command for sudo: {command[:50]}...")
            
            # Start process
            self.current_process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE if stdin_input else subprocess.DEVNULL,
                text=False,  # Use binary mode for better compatibility
                cwd=cwd,
                env=env,
                bufsize=1
            )
            self.process = self.current_process  # Keep both references for compatibility
            
            # Read output in real-time
            threading.Thread(target=self._read_output).start()
            
            # Send password to stdin if needed for sudo commands
            if stdin_input and self.current_process and self.current_process.stdin:
                try:
                    # Write password and keep stdin open for potential prompts
                    self.current_process.stdin.write(stdin_input.encode('utf-8'))
                    self.current_process.stdin.flush()
                    # Don't close stdin immediately - let the process close it
                except Exception as e:
                    self.logger.warning(f"Failed to send password to stdin: {e}")
            
            # Wait for process to complete
            try:
                exit_code = self.current_process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.logger.error(f"Command timed out after {timeout} seconds")
                self.kill_process()
                return False, "", f"Command timed out after {timeout} seconds"
                
            # Close stdin after process completes
            if stdin_input and self.current_process and self.current_process.stdin:
                try:
                    self.current_process.stdin.close()
                except:
                    pass
            
            success = exit_code == 0
            self.command_completed.emit(success, exit_code)
            
            if success:
                self.logger.debug(f"Command completed successfully")
            else:
                self.logger.warning(f"Command failed with exit code {exit_code}")
                # Log stderr for debugging
                if self.error_lines:
                    self.logger.warning(f"Error output: {' '.join(self.error_lines[:5])}")
                
            return success, '\n'.join(self.output_lines), '\n'.join(self.error_lines)
            
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            self.error_received.emit(str(e))
            self.command_completed.emit(False, -1)
            return False, "", str(e)
            
        finally:
            self.process = None
            self.current_process = None
    
    def _read_output(self):
        """Read output from process"""
        try:
            process = self.current_process  # Get local reference for thread safety
            if not process:
                return
                
            while process.poll() is None:
                try:
                    # Use select to read from both stdout and stderr without blocking
                    import select
                    ready_to_read = []
                    if process.stdout:
                        ready_to_read.append(process.stdout)
                    if process.stderr:
                        ready_to_read.append(process.stderr)
                    
                    if ready_to_read:
                        readable, _, _ = select.select(ready_to_read, [], [], 0.1)
                        
                        for stream in readable:
                            line = stream.readline()
                            if line:
                                decoded_line = line.decode('utf-8', errors='replace').rstrip()
                                if stream == process.stdout:
                                    self.output_received.emit(decoded_line)
                                    self.output_lines.append(decoded_line)
                                else:
                                    # Filter out sudo password prompts from stderr
                                    if '[sudo] password' not in decoded_line:
                                        self.error_received.emit(decoded_line)
                                        self.error_lines.append(decoded_line)
                    
                    # Small delay to prevent CPU spinning
                    time.sleep(0.01)
                except (IOError, OSError) as e:
                    # Handle pipe errors gracefully
                    if process.poll() is None:
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
        process = self.current_process or self.process
        if process:
            try:
                # Try SIGTERM first
                process.terminate()
                time.sleep(0.5)
                
                # If still running, use SIGKILL
                if process.poll() is None:
                    process.kill()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        # Force kill if timeout
                        import os
                        import signal
                        try:
                            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                        except ProcessLookupError:
                            pass  # Process already dead
                
                self.process = None
                self.current_process = None
                return True
            except Exception as e:
                self.error_received.emit(f"Failed to kill process: {str(e)}")
                # Try to clean up anyway
                self.process = None
                self.current_process = None
                return False
        return True
        
    def is_running(self):
        """Check if a process is currently running"""
        process = self.current_process or self.process
        return process is not None and process.poll() is None
