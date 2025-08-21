#!/usr/bin/env python3
"""
Version Manager Module - Manages version updates and tracking
"""

import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class VersionManager:
    """Manages application versions and updates"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.version_file = project_root / "version.json"
        self.changelog_file = project_root / "CHANGELOG.md"
        self.current_version = self._load_version()
        
    def _load_version(self) -> Dict:
        """Load current version information"""
        if self.version_file.exists():
            with open(self.version_file, 'r') as f:
                return json.load(f)
        return self._initialize_version()
    
    def _initialize_version(self) -> Dict:
        """Initialize version information"""
        return {
            "version": "3.0.0",
            "release_date": datetime.now().isoformat(),
            "build_number": 1,
            "features": [
                "Automatic source version checking",
                "Update manifest generation",
                "GitHub integration",
                "CI/CD pipeline support",
                "Enhanced logging system"
            ]
        }
    
    def update_version(self, major: bool = False, minor: bool = False, patch: bool = True) -> str:
        """Update version number"""
        version_parts = self.current_version["version"].split(".")
        major_num = int(version_parts[0])
        minor_num = int(version_parts[1])
        patch_num = int(version_parts[2])
        
        if major:
            major_num += 1
            minor_num = 0
            patch_num = 0
        elif minor:
            minor_num += 1
            patch_num = 0
        elif patch:
            patch_num += 1
        
        new_version = f"{major_num}.{minor_num}.{patch_num}"
        self.current_version["version"] = new_version
        self.current_version["release_date"] = datetime.now().isoformat()
        self.current_version["build_number"] += 1
        
        self._save_version()
        self._update_changelog(new_version)
        
        return new_version
    
    def _save_version(self):
        """Save version information"""
        with open(self.version_file, 'w') as f:
            json.dump(self.current_version, f, indent=2)
    
    def _update_changelog(self, version: str):
        """Update changelog with new version"""
        changelog_entry = f"""
## [{version}] - {datetime.now().strftime('%Y-%m-%d')}

### Added
- Automatic source version checking on startup
- Update manifest generation system
- GitHub integration for releases
- CI/CD pipeline configuration

### Changed
- Updated to version {version}
- Enhanced logging system
- Improved error handling

### Fixed
- Repository cleanup for problematic sources
- Dependency resolution improvements

---
"""
        
        if self.changelog_file.exists():
            with open(self.changelog_file, 'r') as f:
                existing_content = f.read()
            
            # Insert new entry after the header
            lines = existing_content.split('\n')
            header_end = 0
            for i, line in enumerate(lines):
                if line.startswith('##'):
                    header_end = i
                    break
            
            lines.insert(header_end, changelog_entry)
            new_content = '\n'.join(lines)
        else:
            new_content = f"""# Changelog

All notable changes to Lumi-Setup will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

{changelog_entry}
"""
        
        with open(self.changelog_file, 'w') as f:
            f.write(new_content)
    
    def get_version_string(self) -> str:
        """Get formatted version string"""
        return f"v{self.current_version['version']}"
    
    def get_full_version_info(self) -> Dict:
        """Get complete version information"""
        return self.current_version.copy()
    
    def update_python_files(self):
        """Update version strings in Python files"""
        version = self.current_version["version"]
        
        # Update main.py
        main_file = self.project_root / "main.py"
        if main_file.exists():
            content = main_file.read_text()
            # Update version in setApplicationVersion
            content = content.replace(
                'app.setApplicationVersion("2.0.0")',
                f'app.setApplicationVersion("{version}")'
            )
            # Update version in setApplicationName
            content = content.replace(
                'app.setApplicationName("Lumi-Setup v2.0")',
                f'app.setApplicationName("Lumi-Setup v{version.split(".")[0]}.0")'
            )
            # Update version in window title and logs
            content = content.replace(
                'Lumi-Setup v2.0',
                f'Lumi-Setup v{version.split(".")[0]}.0'
            )
            main_file.write_text(content)
            logger.info(f"Updated main.py to version {version}")
        
        # Update other Python files that might contain version strings
        for py_file in self.project_root.rglob("*.py"):
            if "version" in py_file.name.lower() or py_file.name == "__init__.py":
                try:
                    content = py_file.read_text()
                    if "__version__" in content:
                        content = content.replace(
                            content[content.find('__version__'):content.find('\n', content.find('__version__'))],
                            f'__version__ = "{version}"'
                        )
                        py_file.write_text(content)
                        logger.info(f"Updated {py_file.name} to version {version}")
                except Exception as e:
                    logger.warning(f"Could not update version in {py_file}: {e}")
    
    def create_git_tag(self) -> bool:
        """Create a git tag for the current version"""
        try:
            version_tag = self.get_version_string()
            
            # Check if tag already exists
            result = subprocess.run(
                ["git", "tag", "-l", version_tag],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.stdout.strip():
                logger.warning(f"Tag {version_tag} already exists")
                return False
            
            # Create annotated tag
            message = f"Release {version_tag}\n\nFeatures:\n"
            for feature in self.current_version.get("features", []):
                message += f"- {feature}\n"
            
            subprocess.run(
                ["git", "tag", "-a", version_tag, "-m", message],
                check=True,
                cwd=self.project_root
            )
            
            logger.info(f"Created git tag: {version_tag}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create git tag: {e}")
            return False
    
    def prepare_release(self) -> Dict:
        """Prepare a new release"""
        version = self.get_version_string()
        
        # Update Python files
        self.update_python_files()
        
        # Create git tag
        tag_created = self.create_git_tag()
        
        release_info = {
            "version": version,
            "date": datetime.now().isoformat(),
            "tag_created": tag_created,
            "files_updated": True,
            "changelog_updated": True
        }
        
        return release_info
