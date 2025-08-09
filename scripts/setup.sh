#!/bin/bash
#
# Lumi-Systems Setup Script
# This script installs and configures all required software for Lumi-Systems
#

# Set script to exit on error
set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse command line arguments
DEBUG_MODE=false
for arg in "$@"; do
    case $arg in
        --debug)
            DEBUG_MODE=true
            ;;
        --view-logs)
            if [ -d "$SCRIPT_DIR/logs" ]; then
                echo "Available logs:"
                ls -lh "$SCRIPT_DIR/logs" | grep -v "^d"
                echo ""
                echo "To view a specific log: less $SCRIPT_DIR/logs/[log_filename]"
                echo "To view the latest summary: less $SCRIPT_DIR/logs/latest_summary.log"
            else
                echo "No logs directory found."
            fi
            exit 0
            ;;
    esac
done

# Source configuration file
if [ -f "$SCRIPT_DIR/config.sh" ]; then
    source "$SCRIPT_DIR/config.sh"
else
    echo "Configuration file not found. Using default settings."
    # Default configuration will be set below
fi

# Log file setup
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/setup_$TIMESTAMP.log"
SUMMARY_FILE="$LOG_DIR/summary_$TIMESTAMP.log"

# State file for resuming interrupted installations
STATE_FILE="$LOG_DIR/setup_state.dat"

# Initialize counters
SUCCESSFUL_INSTALLS=0
FAILED_INSTALLS=0
TOTAL_STEPS=0
CURRENT_STEP=0
LAST_COMPLETED_STEP=""

# State loading will be done after function definitions

# Function to log messages
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local function_name="${FUNCNAME[1]:-main}"
    local line_number="${BASH_LINENO[0]:-unknown}"
    local current_user=$(whoami)
    local memory_usage=$(free -m | awk '/Mem/{printf "%.1f%%", $3*100/$2}')
    
    # Format for detailed logging
    local log_entry="[$timestamp] [$level] [$function_name:$line_number] [$current_user] [$memory_usage] $message"
    
    # Always write to log file with detailed format
    echo "$log_entry" >> "$LOG_FILE"
    
    # For terminal output, use colored and simplified format
    case "$level" in
        ERROR)
            # Red text for errors
            echo -e "\e[1;31m[$timestamp] [$level] $message\e[0m"
            # For critical errors, also print a visible separator
            echo -e "\e[1;31m====================================\e[0m" >&2
            echo -e "\e[1;31m   ERROR: $message\e[0m" >&2
            echo -e "\e[1;31m====================================\e[0m" >&2
            ;;
        WARNING)
            # Yellow text for warnings
            echo -e "\e[1;33m[$timestamp] [$level] $message\e[0m"
            ;;
        SUCCESS)
            # Green text for success
            echo -e "\e[1;32m[$timestamp] [$level] $message\e[0m"
            ;;
        DEBUG)
            # Only log to file, don't display in terminal unless DEBUG_MODE is enabled
            if [ "${DEBUG_MODE:-false}" = "true" ]; then
                echo -e "\e[1;34m[$timestamp] [$level] $message\e[0m"
            fi
            ;;
        *)
            # Normal text for info and other levels
            echo "[$timestamp] [$level] $message"
            ;;
    esac
    
    # If log file exceeds 10MB, rotate it
    if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE") -gt 10485760 ]; then
        local rotated_log="${LOG_FILE}.old"
        mv "$LOG_FILE" "$rotated_log"
        touch "$LOG_FILE"
        echo "[$timestamp] [INFO] Log file rotated to $rotated_log due to size" >> "$LOG_FILE"
    fi
}

# Function to display progress
show_progress() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    local step_id="$1"
    local message="$2"
    local percent=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    local progress_bar=""
    local bar_length=30
    local filled_length=$((bar_length * CURRENT_STEP / TOTAL_STEPS))
    
    # Skip if this step was already completed in a previous run
    if [ -n "$LAST_COMPLETED_STEP" ] && [ "$LAST_COMPLETED_STEP" = "$step_id" -o "$LAST_COMPLETED_STEP" \> "$step_id" ]; then
        log_message "INFO" "Skipping already completed step $step_id: $message"
        return 0
    fi
    
    # Create the progress bar
    for ((i=0; i<bar_length; i++)); do
        if [ $i -lt $filled_length ]; then
            progress_bar+="█"
        else
            progress_bar+=" "
        fi
    done
    
    # Display progress with color
    echo -e "\e[1;34m[\e[1;36m$CURRENT_STEP\e[1;34m/\e[1;36m$TOTAL_STEPS\e[1;34m] \e[1;32m[$progress_bar] \e[1;33m$percent%\e[0m"
    echo -e "\e[1;37m$message\e[0m"
    echo ""
    
    log_message "INFO" "Step $CURRENT_STEP/$TOTAL_STEPS: $message"
    
    # Update the state file with the last completed step
    LAST_COMPLETED_STEP="$step_id"
    echo "LAST_COMPLETED_STEP=\"$LAST_COMPLETED_STEP\"" > "$STATE_FILE"
    echo "SUCCESSFUL_INSTALLS=$SUCCESSFUL_INSTALLS" >> "$STATE_FILE"
    echo "FAILED_INSTALLS=$FAILED_INSTALLS" >> "$STATE_FILE"
}

# Function to handle errors
handle_error() {
    local error_message="$1"
    local retry_function="$2"
    local max_retries="${3:-3}"
    local retry_count=0
    
    log_message "ERROR" "$error_message"
    
    echo -e "\e[1;33m⚠️  Attempting to recover from error...\e[0m"
    
    while [ $retry_count -lt $max_retries ]; do
        retry_count=$((retry_count + 1))
        echo -e "\e[1;36m   Retry attempt $retry_count of $max_retries\e[0m"
        log_message "INFO" "Retry attempt $retry_count of $max_retries"
        
        if $retry_function; then
            echo -e "\e[1;32m✓ Retry successful\e[0m"
            log_message "SUCCESS" "Retry successful"
            return 0
        else
            echo -e "\e[1;31m✗ Retry attempt $retry_count failed\e[0m"
            log_message "ERROR" "Retry attempt $retry_count failed"
            sleep 5
        fi
    done
    
    echo -e "\e[1;41m All retry attempts failed! \e[0m"
    log_message "ERROR" "All retry attempts failed for: $error_message"
    FAILED_INSTALLS=$((FAILED_INSTALLS + 1))
    return 1
}

# Function to check internet connection
check_internet_connection() {
    log_message "INFO" "Checking internet connection..."
    if ping -c 3 google.com &> /dev/null; then
        log_message "INFO" "Internet connection is available"
        return 0
    else
        log_message "ERROR" "No internet connection available"
        return 1
    fi
}

# Function to check root privileges
check_root_privileges() {
    log_message "INFO" "Checking root privileges..."
    if [ "$(id -u)" -eq 0 ]; then
        log_message "INFO" "Script is running with root privileges"
        return 0
    else
        log_message "ERROR" "Script must be run with root privileges"
        return 1
    fi
}

# Function to fix package manager locks
fix_package_manager_locks() {
    show_progress "fix_locks" "Fixing package manager locks"
    
    log_message "INFO" "Checking for package manager locks"
    
    # Check for dpkg lock
    if [ -f /var/lib/dpkg/lock ]; then
        log_message "WARNING" "Found dpkg lock file. Attempting to remove."
        rm -f /var/lib/dpkg/lock
    fi
    
    # Check for apt lock
    if [ -f /var/lib/apt/lists/lock ]; then
        log_message "WARNING" "Found apt lists lock file. Attempting to remove."
        rm -f /var/lib/apt/lists/lock
    fi
    
    # Check for apt archives lock
    if [ -f /var/cache/apt/archives/lock ]; then
        log_message "WARNING" "Found apt archives lock file. Attempting to remove."
        rm -f /var/cache/apt/archives/lock
    fi
    
    # Check for PackageKit
    if pidof packagekitd > /dev/null; then
        log_message "WARNING" "PackageKit is running. Attempting to stop it."
        systemctl stop packagekit
    fi
    
    log_message "INFO" "Configuring possibly interrupted packages..."
    dpkg --configure -a
    
    log_message "INFO" "Package manager locks have been cleared"
    return 0
}

# Function to update package lists
update_package_lists() {
    show_progress "update_packages" "Updating package lists"
    
    log_message "INFO" "Updating package lists"
    
    # First, make sure we don't have any problematic repositories
    cleanup_repository_files
    
    # Try with allowing insecure repositories and ignoring missing keys
    if apt-get update -o Acquire::AllowInsecureRepositories=true -o Acquire::AllowDowngradeToInsecureRepositories=true --allow-insecure-repositories; then
        log_message "INFO" "Package lists updated successfully"
        return 0
    else
        # If that fails, try with --allow-unauthenticated
        log_message "WARNING" "Standard update failed. Trying with --allow-unauthenticated"
        if apt-get update --allow-unauthenticated; then
            log_message "INFO" "Package lists updated with --allow-unauthenticated"
            return 0
        else
            # Last resort: try with -o APT::Get::AllowUnauthenticated=true
            log_message "WARNING" "Update with --allow-unauthenticated failed. Trying with APT::Get::AllowUnauthenticated=true"
            if apt-get -o APT::Get::AllowUnauthenticated=true update; then
                log_message "INFO" "Package lists updated with APT::Get::AllowUnauthenticated=true"
                return 0
            else
                log_message "ERROR" "Failed to update package lists"
                return 1
            fi
        fi
    fi
}

# Function to repair package database
repair_package_database() {
    log_message "INFO" "Repairing package database..."
    
    # Fix broken packages
    if apt-get -f install -y; then
        log_message "INFO" "Fixed broken packages"
    else
        log_message "ERROR" "Failed to fix broken packages"
        return 1
    fi
    
    # Clean apt cache
    if apt-get clean && apt-get autoclean; then
        log_message "INFO" "Cleaned apt cache"
    else
        log_message "ERROR" "Failed to clean apt cache"
        return 1
    fi
    
    log_message "INFO" "Package database repaired"
    return 0
}

# Calculate total steps
calculate_total_steps() {
    # System configuration steps
    TOTAL_STEPS=$((TOTAL_STEPS + 3))  # Language, timezone, weather location
    
    # Software installation steps
    TOTAL_STEPS=$((TOTAL_STEPS + 1))  # RustDesk
    TOTAL_STEPS=$((TOTAL_STEPS + ${#APT_GUI_APPS[@]}))  # APT GUI apps
    TOTAL_STEPS=$((TOTAL_STEPS + ${#APT_CLI_TOOLS[@]}))  # APT CLI tools
    TOTAL_STEPS=$((TOTAL_STEPS + 1))  # Flatpak setup
    TOTAL_STEPS=$((TOTAL_STEPS + ${#FLATPAK_APPS[@]}))  # Flatpak apps
    TOTAL_STEPS=$((TOTAL_STEPS + ${#RUSTDESK_DEPENDENCIES[@]}))  # RustDesk dependencies
    
    # Cleanup steps
    TOTAL_STEPS=$((TOTAL_STEPS + 3))  # Remove unused packages, clean apt cache, remove temp files
    
    log_message "INFO" "Total steps calculated: $TOTAL_STEPS"
}

# Load default configuration if not loaded from file
if [ ! -f "$SCRIPT_DIR/config.sh" ]; then
    # System configuration
    SYSTEM_LANGUAGE="de_AT.UTF-8"
    # SYSTEM_TIMEZONE="Europe/Vienna"  # Removed - not working in this script
    # WEATHER_LOCATION="Vienna"        # Removed - not working in this script
    
    # Software lists
    APT_GUI_APPS=(
        "gimp"
        "inkscape"
        "krita"
        "vlc"
        "gnome-tweaks"
        "microsoft-edge-stable"
        "firefox"
        "evolution"
    )
    
    APT_CLI_TOOLS=(
        "wget"
        "curl"
        "git"
        "htop"
        "neofetch"
        "p7zip-full"
    )
    
    FLATPAK_APPS=(
        "chat.revolt.RevoltDesktop"
        "com.obsproject.Studio"
        "org.videolan.VLC"
        "org.onlyoffice.desktopeditors"
    )
    
    RUSTDESK_DEPENDENCIES=(
        "libfuse2"
        "libpulse0"
        "libxcb-randr0"
        "libxdo3"
        "libxfixes3"
        "libxcb-shape0"
        "libxcb-xfixes0"
        "libasound2t64"
        "pipewire"
    )
    
    # RustDesk version
    RUSTDESK_VERSION="1.4.0"
fi

# Function to display a banner
display_banner() {
    echo -e "\e[1;34m"  # Blue color
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║               LUMI-SYSTEMS SETUP SCRIPT                   ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "\e[0m"  # Reset color
    echo -e "\e[1;36mThis script will install and configure all required software\e[0m"
    echo -e "\e[1;33mStarted at: $(date)\e[0m"
    echo ""
}

# Main execution starts here
# Function to clean up problematic repository files
cleanup_repository_files() {
    log_message "INFO" "Cleaning up problematic repository files"
    
    # Remove OnlyOffice repository files
    if [ -f "/etc/apt/sources.list.d/onlyoffice.list" ]; then
        log_message "INFO" "Removing OnlyOffice repository file"
        rm -f /etc/apt/sources.list.d/onlyoffice.list
    fi
    
    if [ -f "/etc/apt/sources.list.d/onlyoffice-fallback.list" ]; then
        log_message "INFO" "Removing OnlyOffice fallback repository file"
        rm -f /etc/apt/sources.list.d/onlyoffice-fallback.list
    fi
    
    if [ -f "/usr/share/keyrings/onlyoffice-archive-keyring.gpg" ]; then
        log_message "INFO" "Removing OnlyOffice keyring file"
        rm -f /usr/share/keyrings/onlyoffice-archive-keyring.gpg
    fi
    
    # Also check for any other OnlyOffice related files
    if [ -f "/etc/apt/trusted.gpg.d/onlyoffice.gpg" ]; then
        log_message "INFO" "Removing OnlyOffice trusted GPG file"
        rm -f /etc/apt/trusted.gpg.d/onlyoffice.gpg
    fi
    
    log_message "INFO" "Repository cleanup completed"
}

main() {
    display_banner
    log_message "INFO" "Lumi-Systems Setup Script started"
    
    # Load state if available
    if [ -f "$STATE_FILE" ]; then
        source "$STATE_FILE"
        log_message "INFO" "Resuming from previous state. Last completed step: $LAST_COMPLETED_STEP"
        echo -e "\e[1;33mResuming installation from previous state. Last completed step: $LAST_COMPLETED_STEP\e[0m"
        echo ""
    fi
    
    # Clean up problematic repository files first - do this before any other operations
    cleanup_repository_files
    
    # Check prerequisites
    if ! check_internet_connection; then
        log_message "ERROR" "Internet connection is required. Exiting."
        exit 1
    fi
    
    if ! check_root_privileges; then
        log_message "ERROR" "Root privileges are required. Please run with sudo. Exiting."
        echo -e "\n\e[1;41m IMPORTANT: This script must be run with root privileges! \e[0m"
        echo -e "\e[1;31mPlease run the script again using: \e[1;37msudo ./setup.sh\e[0m\n"
        exit 1
    fi
    
    # Calculate total steps first - this must be done before any progress is shown
    calculate_total_steps
    
    # Fix package manager issues
    fix_package_manager_locks
    
    # Update package lists
    if ! update_package_lists; then
        handle_error "Failed to update package lists" update_package_lists
    fi
    
    # Configure system
    configure_system
    
    # Install software
    install_software
    
    # Cleanup
    perform_cleanup
    
    # Generate summary
    generate_summary
    
    log_message "SUCCESS" "Lumi-Systems Setup Script completed successfully"
    echo -e "\e[1;32m╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║               SETUP COMPLETED SUCCESSFULLY                ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝\e[0m"
    echo -e "\e[1;36mSummary file: \e[1;33m$SUMMARY_FILE\e[0m"
    echo -e "\e[1;36mLog file: \e[1;33m$LOG_FILE\e[0m"
}

# Source additional script files
source "$SCRIPT_DIR/system_config.sh"
source "$SCRIPT_DIR/software_install.sh"
source "$SCRIPT_DIR/cleanup.sh"

# Run the main function
main
