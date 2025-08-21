#!/usr/bin/env python3
"""
Manifest Generator Module - Generates update manifests for tracking changes
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ManifestGenerator:
    """Generates and manages update manifests"""
    
    def __init__(self, manifest_dir: Path, log_dir: Path):
        self.manifest_dir = manifest_dir
        self.log_dir = log_dir
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_manifest_file = manifest_dir / "current_manifest.json"
        self.update_log_file = log_dir / f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
    def generate_manifest(self, updates: Dict, source_info: Dict) -> Dict:
        """Generate a comprehensive update manifest"""
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0",
            "updates_found": len(updates),
            "updates": updates,
            "source_information": source_info,
            "actions_required": self._determine_actions(updates),
            "script_updates": self._generate_script_updates(updates)
        }
        
        # Save manifest
        self._save_manifest(manifest)
        
        # Generate update log
        self._generate_update_log(manifest)
        
        return manifest
    
    def _determine_actions(self, updates: Dict) -> List[Dict]:
        """Determine what actions need to be taken for updates"""
        actions = []
        
        for app_name, update_info in updates.items():
            action = {
                "application": app_name,
                "type": update_info.get("type"),
                "current_version": update_info.get("current_version"),
                "new_version": update_info.get("latest_version"),
                "action_type": "update"
            }
            
            # Determine specific actions based on type
            if update_info.get("type") == "github":
                if "download_urls" in update_info:
                    action["download_urls"] = update_info["download_urls"]
                    action["action_details"] = "Update download URLs in installation script"
            
            elif update_info.get("type") == "apt":
                action["action_details"] = "APT package will auto-update via package manager"
            
            elif update_info.get("type") == "flatpak":
                action["action_details"] = "Flatpak will auto-update from Flathub"
            
            elif update_info.get("type") == "deb":
                action["action_details"] = "Update direct download URL if changed"
            
            elif update_info.get("type") == "snap":
                action["action_details"] = "Snap will auto-update"
            
            actions.append(action)
        
        return actions
    
    def _generate_script_updates(self, updates: Dict) -> Dict:
        """Generate specific script updates needed"""
        script_updates = {}
        
        for app_name, update_info in updates.items():
            if update_info.get("type") == "github" and app_name == "rustdesk":
                # Generate RustDesk script update
                script_updates["rustdesk"] = {
                    "file": "scripts/software_install.sh",
                    "function": "install_rustdesk",
                    "updates": {
                        "version": update_info.get("latest_version"),
                        "download_urls": update_info.get("download_urls", {})
                    }
                }
            
            elif update_info.get("type") == "deb":
                # Track direct download URL updates
                script_updates[app_name] = {
                    "file": "scripts/software_install.sh",
                    "type": "download_url",
                    "current_url": self._get_current_download_url(app_name),
                    "check_required": True
                }
        
        return script_updates
    
    def _get_current_download_url(self, app_name: str) -> Optional[str]:
        """Get current download URL from scripts"""
        # This would parse the actual script files
        # For now, returning placeholder
        urls = {
            "vscode": "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64",
            "discord": "https://discord.com/api/download?platform=linux&format=deb",
            "zoom": "https://zoom.us/client/latest/zoom_amd64.deb",
            "teamviewer": "https://download.teamviewer.com/download/linux/teamviewer_amd64.deb",
            "gitkraken": "https://release.gitkraken.com/linux/gitkraken-amd64.deb"
        }
        return urls.get(app_name)
    
    def _save_manifest(self, manifest: Dict):
        """Save manifest to file"""
        with open(self.current_manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        logger.info(f"Manifest saved to {self.current_manifest_file}")
    
    def _generate_update_log(self, manifest: Dict):
        """Generate detailed update log"""
        log_entry = {
            "timestamp": manifest["timestamp"],
            "summary": f"Found {manifest['updates_found']} updates",
            "details": []
        }
        
        for app_name, update_info in manifest["updates"].items():
            detail = {
                "application": app_name,
                "from_version": update_info.get("current_version", "not installed"),
                "to_version": update_info.get("latest_version"),
                "type": update_info.get("type"),
                "timestamp": datetime.now().isoformat()
            }
            log_entry["details"].append(detail)
        
        # Save update log
        with open(self.update_log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        # Also create a human-readable log
        readable_log_file = self.log_dir / f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(readable_log_file, 'w') as f:
            f.write(f"Lumi-Setup Update Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            if manifest["updates_found"] == 0:
                f.write("No updates found. All software sources are up to date.\n")
            else:
                f.write(f"Found {manifest['updates_found']} updates:\n\n")
                
                for app_name, update_info in manifest["updates"].items():
                    f.write(f"📦 {app_name}\n")
                    f.write(f"   Current: {update_info.get('current_version', 'not installed')}\n")
                    f.write(f"   Latest: {update_info.get('latest_version')}\n")
                    f.write(f"   Type: {update_info.get('type')}\n")
                    
                    if "download_urls" in update_info:
                        f.write(f"   Downloads:\n")
                        for file_name, url in update_info["download_urls"].items():
                            f.write(f"      - {file_name}: {url}\n")
                    f.write("\n")
                
                f.write("\nActions Required:\n")
                f.write("-" * 40 + "\n")
                
                for action in manifest["actions_required"]:
                    f.write(f"\n{action['application']}:\n")
                    f.write(f"   Action: {action['action_type']}\n")
                    f.write(f"   Details: {action.get('action_details', 'N/A')}\n")
        
        logger.info(f"Update log saved to {readable_log_file}")
    
    def get_latest_manifest(self) -> Optional[Dict]:
        """Get the latest manifest"""
        if self.current_manifest_file.exists():
            with open(self.current_manifest_file, 'r') as f:
                return json.load(f)
        return None
    
    def generate_github_release_notes(self, manifest: Dict) -> str:
        """Generate release notes for GitHub"""
        notes = f"# Lumi-Setup v3.0.0 - Update Report\n\n"
        notes += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        if manifest["updates_found"] == 0:
            notes += "✅ All software sources are up to date.\n"
        else:
            notes += f"## 📦 Found {manifest['updates_found']} Updates\n\n"
            
            for app_name, update_info in manifest["updates"].items():
                current = update_info.get("current_version", "not installed")
                latest = update_info.get("latest_version")
                notes += f"### {app_name}\n"
                notes += f"- **Current:** {current}\n"
                notes += f"- **Latest:** {latest}\n"
                notes += f"- **Type:** {update_info.get('type')}\n\n"
        
        notes += "\n## 🚀 Features in this Release\n\n"
        notes += "- Automatic source version checking\n"
        notes += "- Update manifest generation\n"
        notes += "- Enhanced logging system\n"
        notes += "- GitHub integration\n"
        notes += "- CI/CD pipeline support\n"
        
        return notes
    
    def apply_updates_to_scripts(self, manifest: Dict) -> bool:
        """Apply updates to installation scripts"""
        try:
            script_updates = manifest.get("script_updates", {})
            
            for app_name, update_info in script_updates.items():
                if app_name == "rustdesk" and "updates" in update_info:
                    self._update_rustdesk_script(update_info["updates"])
                # Add more specific update handlers as needed
            
            return True
        except Exception as e:
            logger.error(f"Failed to apply updates to scripts: {e}")
            return False
    
    def _update_rustdesk_script(self, updates: Dict):
        """Update RustDesk installation script with new version"""
        script_file = self.manifest_dir.parent.parent / "scripts" / "software_install.sh"
        
        if not script_file.exists():
            logger.warning(f"Script file not found: {script_file}")
            return
        
        # Read current script
        with open(script_file, 'r') as f:
            content = f.read()
        
        # Update version references if needed
        new_version = updates.get("version")
        if new_version:
            # This would update specific version references in the script
            # For now, just logging
            logger.info(f"Would update RustDesk to version {new_version}")
        
        # Note: Actual script modification would go here
        # This is a placeholder for the update logic
