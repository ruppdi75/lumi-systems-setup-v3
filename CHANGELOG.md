# Changelog

All notable changes to Lumi-Setup will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.2] - 2025-08-28

### Fixed
- **OnlyOffice Installation**: Implemented dedicated installation function with .deb package priority
  - Downloads official .deb package from OnlyOffice servers
  - Automatic fallback to Flatpak if .deb installation fails
  - Added proper timeout handling (60s) for downloads
- **Script Runner**: Fixed missing `time` module import causing crashes in kill_process() method
- **Steam Installation**: Replaced obsolete libgl1-mesa-glx:i386 with libgl1:i386 and libgl1-mesa-dri:i386
- **Discord Installation**: Added explicit timeout to prevent hanging during download

### Changed
- Removed OnlyOffice from FLATPAK_APPS arrays to prevent duplicate installation attempts
- OnlyOffice now installs separately with intelligent fallback mechanism

### Added
- Test script for OnlyOffice installation verification
- Improved error handling for package installations

## [3.0.1] - 2025-08-21

### Added
- Professional phased progress reporting in update dialog
- Source-specific status messages for different package types
- Gradient progress bar with Lumi-Systems branding colors
- Package list display in final update status
- Context-aware completion messages
- Enhanced error handling with user-friendly messages

### Changed
- Update dialog now shows 5 distinct phases of verification
- Improved dialog size to 600x180px for better readability
- Enhanced status messages with professional terminology
- Better visual feedback with emoji indicators

### Improved
- User experience during update checking process
- Transparency of update verification steps
- Visual consistency with Lumi-Systems design language

## [3.0.0] - 2025-01-21

### Added
- Automatic source version checking on startup
- Update manifest generation system
- GitHub integration for releases
- CI/CD pipeline configuration
- Enhanced logging system with dedicated update logs
- Script auto-update capability
- Comprehensive update reporting
- Source checker for 25+ applications
- Version manager with semantic versioning
- Manifest generator for tracking all changes

### Changed
- Updated from version 2.0.0 to 3.0.0
- Enhanced application startup with update checks
- Improved error handling and logging
- Restructured project with new `src/updater` module

### Fixed
- Repository cleanup for problematic sources
- Dependency resolution improvements

---

## [2.0.0] - 2025-01-20

### Added
- Complete PyQt6 GUI implementation
- Real-time progress tracking
- Advanced logging system
- Professional installation reporting
- Support for 25+ pre-configured applications

### Changed
- Complete rewrite from shell scripts to Python/PyQt6
- Modern dark theme UI
- Modular architecture

---

## [1.0.0] - 2025-01-15

### Added
- Initial release with shell script implementation
- Basic software installation capabilities
- System configuration scripts
