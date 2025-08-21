#!/usr/bin/env python3
"""
Test script for Lumi-Setup v3 updater functionality
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.updater import SourceChecker, VersionManager, ManifestGenerator

def test_updater():
    """Test the updater components"""
    print("=" * 60)
    print("Lumi-Setup v3.0 - Updater Test")
    print("=" * 60)
    
    # Initialize components
    manifest_dir = project_root / "manifests"
    log_dir = project_root / "logs" / "updates"
    
    print("\n1. Initializing updater components...")
    try:
        checker = SourceChecker(manifest_dir)
        version_mgr = VersionManager(project_root)
        manifest_gen = ManifestGenerator(manifest_dir, log_dir)
        print("✅ Components initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Check current version
    print("\n2. Checking current version...")
    current_version = version_mgr.current_version
    print(f"   Current version: {current_version}")
    
    # Check for updates
    print("\n3. Checking for software updates...")
    print("   This may take a moment...")
    
    try:
        updates = checker.check_all_sources()
        
        if updates:
            print(f"\n✅ Found {len(updates)} updates:")
            for app_name, update_info in updates.items():
                print(f"   • {app_name}: {update_info.get('current_version', 'N/A')} → {update_info.get('latest_version', 'N/A')}")
            
            # Generate manifest
            print("\n4. Generating update manifest...")
            manifest = manifest_gen.generate_manifest(updates, checker.current_sources)
            
            # Save test manifest
            test_manifest_file = project_root / f"test_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(test_manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            print(f"   Manifest saved to: {test_manifest_file}")
            
            # Get summary
            summary = checker.get_update_summary(updates)
            print("\n5. Update Summary:")
            print("-" * 40)
            print(summary)
            
        else:
            print("\n✅ All software sources are up to date!")
            
    except Exception as e:
        print(f"\n❌ Update check failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_updater()
    sys.exit(0 if success else 1)
