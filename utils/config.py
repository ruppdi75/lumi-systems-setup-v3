"""
Configuration management for Lumi-Setup v2.0
"""

import json
import os
from pathlib import Path

class Config:
    """Configuration manager for the application"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".lumi-setup"
        self.config_file = self.config_dir / "config.json"
        self.config_data = {}
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config_data = {}
        
        # Set defaults if not present
        self.set_defaults()
        
    def set_defaults(self):
        """Set default configuration values"""
        defaults = {
            'system': {
                'language': 'en_US.UTF-8',
                'auto_update': True,
                'check_dependencies': True,
                'parallel_installs': False,
                'max_retries': 3,
                'timeout': 300
            },
            'ui': {
                'theme': 'dark',
                'auto_scroll_logs': True,
                'show_debug_logs': False,
                'window_geometry': {
                    'width': 1200,
                    'height': 800,
                    'x': 100,
                    'y': 100
                }
            },
            'installation': {
                'create_backups': True,
                'cleanup_downloads': True,
                'verify_checksums': True,
                'continue_on_error': True
            },
            'logging': {
                'level': 'INFO',
                'max_log_files': 10,
                'max_log_size_mb': 10
            }
        }
        
        # Merge defaults with existing config
        for section, values in defaults.items():
            if section not in self.config_data:
                self.config_data[section] = {}
            for key, value in values.items():
                if key not in self.config_data[section]:
                    self.config_data[section][key] = value
                    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get(self, section, key, default=None):
        """Get configuration value"""
        return self.config_data.get(section, {}).get(key, default)
        
    def set(self, section, key, value):
        """Set configuration value"""
        if section not in self.config_data:
            self.config_data[section] = {}
        self.config_data[section][key] = value
        self.save_config()
        
    def get_section(self, section):
        """Get entire configuration section"""
        return self.config_data.get(section, {})
        
    def update_section(self, section, values):
        """Update entire configuration section"""
        if section not in self.config_data:
            self.config_data[section] = {}
        self.config_data[section].update(values)
        self.save_config()
