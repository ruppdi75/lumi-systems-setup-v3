#!/usr/bin/env python3
"""
Source Checker Module - Checks for updates to software sources
"""

import json
import re
import requests
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class SourceChecker:
    """Checks software sources for updates"""
    
    def __init__(self, manifest_dir: Path):
        self.manifest_dir = manifest_dir
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        self.sources_file = manifest_dir / "sources.json"
        self.current_sources = self._load_current_sources()
        
    def _load_current_sources(self) -> Dict:
        """Load current sources from manifest"""
        if self.sources_file.exists():
            with open(self.sources_file, 'r') as f:
                return json.load(f)
        return self._initialize_sources()
    
    def _initialize_sources(self) -> Dict:
        """Initialize sources with current known versions"""
        return {
            "rustdesk": {
                "type": "github",
                "repo": "rustdesk/rustdesk",
                "current_version": None,
                "latest_version": None,
                "download_urls": {},
                "last_checked": None
            },
            "microsoft-edge": {
                "type": "apt",
                "repo_url": "https://packages.microsoft.com/repos/edge",
                "key_url": "https://packages.microsoft.com/keys/microsoft.asc",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "onlyoffice": {
                "type": "flatpak",
                "flatpak_id": "org.onlyoffice.desktopeditors",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "thunderbird": {
                "type": "flatpak",
                "flatpak_id": "org.mozilla.Thunderbird",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "vlc": {
                "type": "apt",
                "package": "vlc",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "firefox": {
                "type": "apt",
                "package": "firefox",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "vscode": {
                "type": "deb",
                "download_url": "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "chrome": {
                "type": "deb",
                "repo_url": "https://dl.google.com/linux/chrome/deb/",
                "package": "google-chrome-stable",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "teams": {
                "type": "deb",
                "repo_url": "https://packages.microsoft.com/repos/ms-teams",
                "package": "teams",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "discord": {
                "type": "deb",
                "download_url": "https://discord.com/api/download?platform=linux&format=deb",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "signal": {
                "type": "apt",
                "repo_url": "https://updates.signal.org/desktop/apt",
                "package": "signal-desktop",
                "key_url": "https://updates.signal.org/desktop/apt/keys.asc",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "telegram": {
                "type": "flatpak",
                "flatpak_id": "org.telegram.desktop",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "spotify": {
                "type": "snap",
                "snap_name": "spotify",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "zoom": {
                "type": "deb",
                "download_url": "https://zoom.us/client/latest/zoom_amd64.deb",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "anydesk": {
                "type": "deb",
                "repo_url": "http://deb.anydesk.com/",
                "package": "anydesk",
                "key_url": "https://keys.anydesk.com/repos/DEB-GPG-KEY",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "teamviewer": {
                "type": "deb",
                "download_url": "https://download.teamviewer.com/download/linux/teamviewer_amd64.deb",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "brave": {
                "type": "apt",
                "repo_url": "https://brave-browser-apt-release.s3.brave.com/",
                "package": "brave-browser",
                "key_url": "https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "opera": {
                "type": "apt",
                "repo_url": "https://deb.opera.com/opera-stable/",
                "package": "opera-stable",
                "key_url": "https://deb.opera.com/archive.key",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "vivaldi": {
                "type": "apt",
                "repo_url": "https://repo.vivaldi.com/archive/deb/",
                "package": "vivaldi-stable",
                "key_url": "https://repo.vivaldi.com/archive/linux_signing_key.pub",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "sublime-text": {
                "type": "apt",
                "repo_url": "https://download.sublimetext.com/",
                "package": "sublime-text",
                "key_url": "https://download.sublimetext.com/sublimehq-pub.gpg",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "atom": {
                "type": "github",
                "repo": "atom/atom",
                "current_version": None,
                "latest_version": None,
                "download_urls": {},
                "last_checked": None
            },
            "gitkraken": {
                "type": "deb",
                "download_url": "https://release.gitkraken.com/linux/gitkraken-amd64.deb",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "postman": {
                "type": "snap",
                "snap_name": "postman",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "docker": {
                "type": "apt",
                "repo_url": "https://download.docker.com/linux/ubuntu",
                "package": "docker-ce",
                "key_url": "https://download.docker.com/linux/ubuntu/gpg",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            },
            "nodejs": {
                "type": "nodesource",
                "version": "20",  # LTS version
                "repo_url": "https://deb.nodesource.com/node_20.x",
                "package": "nodejs",
                "current_version": None,
                "latest_version": None,
                "last_checked": None
            }
        }
    
    def check_github_release(self, repo: str) -> Optional[Dict]:
        """Check latest release from GitHub"""
        try:
            url = f"https://api.github.com/repos/{repo}/releases/latest"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                version = data.get('tag_name', '').lstrip('v')
                assets = {}
                for asset in data.get('assets', []):
                    name = asset['name']
                    if name.endswith('.deb') or name.endswith('.flatpak'):
                        assets[name] = asset['browser_download_url']
                return {
                    'version': version,
                    'assets': assets,
                    'release_url': data.get('html_url')
                }
        except Exception as e:
            logger.error(f"Error checking GitHub release for {repo}: {e}")
        return None
    
    def check_apt_package(self, package: str) -> Optional[str]:
        """Check latest version of APT package"""
        try:
            import subprocess
            result = subprocess.run(
                ['apt-cache', 'policy', package],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Candidate:' in line:
                        version = line.split(':', 1)[1].strip()
                        return version
        except Exception as e:
            logger.error(f"Error checking APT package {package}: {e}")
        return None
    
    def check_flatpak_app(self, app_id: str) -> Optional[str]:
        """Check latest version of Flatpak app"""
        try:
            import subprocess
            result = subprocess.run(
                ['flatpak', 'remote-info', 'flathub', app_id],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Version:' in line:
                        version = line.split(':', 1)[1].strip()
                        return version
        except Exception as e:
            logger.error(f"Error checking Flatpak app {app_id}: {e}")
        return None
    
    def check_snap_package(self, snap_name: str) -> Optional[str]:
        """Check latest version of Snap package"""
        try:
            import subprocess
            result = subprocess.run(
                ['snap', 'info', snap_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'latest/stable:' in line:
                        # Extract version from format like "latest/stable: 1.2.3 2024-01-01"
                        parts = line.split(':', 1)[1].strip().split()
                        if parts:
                            return parts[0]
        except Exception as e:
            logger.error(f"Error checking Snap package {snap_name}: {e}")
        return None
    
    def check_all_sources(self) -> Dict[str, Dict]:
        """Check all sources for updates"""
        updates = {}
        timestamp = datetime.now().isoformat()
        
        for app_name, source_info in self.current_sources.items():
            logger.info(f"Checking {app_name}...")
            source_type = source_info.get('type')
            latest_version = None
            additional_info = {}
            
            if source_type == 'github':
                repo = source_info.get('repo')
                if repo:
                    release_info = self.check_github_release(repo)
                    if release_info:
                        latest_version = release_info['version']
                        additional_info = {
                            'download_urls': release_info['assets'],
                            'release_url': release_info['release_url']
                        }
            
            elif source_type == 'apt':
                package = source_info.get('package')
                if package:
                    latest_version = self.check_apt_package(package)
            
            elif source_type == 'flatpak':
                app_id = source_info.get('flatpak_id')
                if app_id:
                    latest_version = self.check_flatpak_app(app_id)
            
            elif source_type == 'snap':
                snap_name = source_info.get('snap_name')
                if snap_name:
                    latest_version = self.check_snap_package(snap_name)
            
            elif source_type == 'deb':
                # For direct download URLs, we'll need to check headers or download page
                logger.info(f"Direct DEB download for {app_name} - manual check required")
                latest_version = "manual_check_required"
            
            elif source_type == 'nodesource':
                # NodeSource repos have specific versioning
                version = source_info.get('version')
                latest_version = f"Node.js {version}.x LTS"
            
            # Check if there's an update
            if latest_version and latest_version != source_info.get('current_version'):
                updates[app_name] = {
                    'current_version': source_info.get('current_version'),
                    'latest_version': latest_version,
                    'type': source_type,
                    **additional_info
                }
                
                # Update the source info
                self.current_sources[app_name]['latest_version'] = latest_version
                self.current_sources[app_name]['last_checked'] = timestamp
                if additional_info:
                    self.current_sources[app_name].update(additional_info)
        
        # Save updated sources
        self._save_sources()
        
        return updates
    
    def _save_sources(self):
        """Save current sources to manifest"""
        with open(self.sources_file, 'w') as f:
            json.dump(self.current_sources, f, indent=2)
    
    def get_update_summary(self, updates: Dict) -> str:
        """Generate a summary of available updates"""
        if not updates:
            return "All software sources are up to date."
        
        summary = f"Found {len(updates)} updates:\n\n"
        for app, info in updates.items():
            current = info.get('current_version', 'not installed')
            latest = info.get('latest_version', 'unknown')
            summary += f"📦 {app}:\n"
            summary += f"   Current: {current}\n"
            summary += f"   Latest: {latest}\n"
            if 'download_urls' in info:
                summary += f"   Downloads: {len(info['download_urls'])} files available\n"
            summary += "\n"
        
        return summary
