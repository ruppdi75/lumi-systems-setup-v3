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
            self.current_process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE if stdin_input else None,
                text=True,
                cwd=cwd,
                env=env,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output in real-time
            stdout_lines = []
            stderr_lines = []
            
            # Create threads to read stdout and stderr
            stdout_queue = queue.Queue()
            stderr_queue = queue.Queue()
            
            def read_stdout():
                for line in iter(self.current_process.stdout.readline, ''):
                    stdout_queue.put(line)
                    self.output_received.emit(line.rstrip())
                self.current_process.stdout.close()
                
            def read_stderr():
                for line in iter(self.current_process.stderr.readline, ''):
                    stderr_queue.put(line)
                    self.error_received.emit(line.rstrip())
                self.current_process.stderr.close()
                
            stdout_thread = threading.Thread(target=read_stdout)
            stderr_thread = threading.Thread(target=read_stderr)
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Send password to stdin if needed for sudo commands
            if stdin_input:
                try:
                    self.current_process.stdin.write(stdin_input)
                    self.current_process.stdin.flush()
                    self.current_process.stdin.close()
                except Exception as e:
                    self.logger.warning(f"Failed to send password to stdin: {e}")
            
            # Wait for process to complete
            try:
                exit_code = self.current_process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.logger.error(f"Command timed out after {timeout} seconds")
                self.current_process.kill()
                self.current_process.wait()
                return False, "", f"Command timed out after {timeout} seconds"
                
            # Wait for threads to finish
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)
            
            # Collect all output
            while not stdout_queue.empty():
                stdout_lines.append(stdout_queue.get())
                
            while not stderr_queue.empty():
                stderr_lines.append(stderr_queue.get())
                
            stdout_text = ''.join(stdout_lines)
            stderr_text = ''.join(stderr_lines)
            
            success = exit_code == 0
            self.command_completed.emit(success, exit_code)
            
            if success:
                self.logger.debug(f"Command completed successfully")
            else:
                self.logger.error(f"Command failed with exit code {exit_code}")
                
            return success, stdout_text, stderr_text
            
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            self.error_received.emit(str(e))
            self.command_completed.emit(False, -1)
            return False, "", str(e)
            
        finally:
            self.current_process = None
            
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
        
    def kill_current_process(self):
        """Kill the currently running process"""
        if self.current_process:
            try:
                self.current_process.kill()
                self.current_process.wait()
                self.logger.info("Current process killed")
            except Exception as e:
                self.logger.error(f"Error killing process: {e}")
                
    def is_running(self):
        """Check if a process is currently running"""
        return self.current_process is not None and self.current_process.poll() is None
