#!/bin/bash
#
# Cleanup Functions for Lumi-Systems Setup
#

# Function to remove unused packages
remove_unused_packages() {
    show_progress "cleanup_unused" "Removing unused packages"
    
    log_message "INFO" "Removing unused packages"
    
    if apt-get autoremove -y; then
        log_message "INFO" "Unused packages removed successfully"
        SUCCESSFUL_INSTALLS=$((SUCCESSFUL_INSTALLS + 1))
        return 0
    else
        log_message "ERROR" "Failed to remove unused packages"
        return 1
    fi
}

# Function to clean APT cache
clean_apt_cache() {
    show_progress "cleanup_apt" "Cleaning APT cache"
    
    log_message "INFO" "Cleaning APT cache"
    
    if apt-get clean && apt-get autoclean; then
        log_message "INFO" "APT cache cleaned successfully"
        SUCCESSFUL_INSTALLS=$((SUCCESSFUL_INSTALLS + 1))
        return 0
    else
        log_message "ERROR" "Failed to clean APT cache"
        return 1
    fi
}

# Function to remove temporary files
remove_temp_files() {
    show_progress "cleanup_temp" "Removing temporary files"
    
    log_message "INFO" "Removing temporary files"
    
    # Remove any temporary files created during installation
    local temp_files=(
        "/tmp/rustdesk_*"
        "/tmp/apt_*"
        "/tmp/flatpak_*"
    )
    
    for pattern in "${temp_files[@]}"; do
        rm -rf $pattern 2>/dev/null || true
    done
    
    log_message "INFO" "Temporary files removed successfully"
    SUCCESSFUL_INSTALLS=$((SUCCESSFUL_INSTALLS + 1))
    return 0
}

# Function to generate installation summary
generate_summary() {
    show_progress "generate_summary" "Generating detailed installation summary"
    log_message "INFO" "Generating detailed installation summary for QA purposes"
    
    # Create summary header with more system information
    cat > "$SUMMARY_FILE" << EOF
=================================================
Lumi-Systems Setup Summary (QA Report)
=================================================
Date: $(date)
Hostname: $(hostname)
Kernel: $(uname -r)
Ubuntu Version: $(lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME | cut -d '"' -f2)
Architecture: $(dpkg --print-architecture)
=================================================

Installation Statistics:
- Total Steps: $TOTAL_STEPS
- Steps Completed: $CURRENT_STEP
- Successful Installations: $SUCCESSFUL_INSTALLS
- Failed Installations: $FAILED_INSTALLS
- Installation Duration: $(( ($(date +%s) - $(date -d "$(head -n 1 "$LOG_FILE" | cut -d '[' -f2 | cut -d ']' -f1)" +%s) ) / 60 )) minutes
=================================================

System Configuration:
- Language: $SYSTEM_LANGUAGE
- Timezone: $SYSTEM_TIMEZONE
- Weather Location: $WEATHER_LOCATION
=================================================

Installed Software:
EOF
    
    # Add successful installations to summary with versions where possible
    echo "Successful Installations:" >> "$SUMMARY_FILE"
    grep -E "INFO.*installed successfully" "$LOG_FILE" | sed 's/.*INFO\] /- /' >> "$SUMMARY_FILE"
    
    # Add package versions for key software
    echo -e "\nSoftware Versions:" >> "$SUMMARY_FILE"
    for pkg in vlc firefox rustdesk btop neofetch; do
        if dpkg -l | grep -q "^ii\s\+$pkg\s\+"; then
            version=$(dpkg -l | grep "^ii\s\+$pkg\s\+" | awk '{print $3}')
            echo "- $pkg: $version" >> "$SUMMARY_FILE"
        fi
    done
    
    # Add Flatpak application versions
    if command -v flatpak &>/dev/null; then
        echo -e "\nFlatpak Applications:" >> "$SUMMARY_FILE"
        flatpak list --columns=application,version 2>/dev/null | grep -v "^Application" | while read -r line; do
            echo "- $line" >> "$SUMMARY_FILE"
        done
    fi
    
    # Add failed installations to summary
    echo -e "\nFailed Installations:" >> "$SUMMARY_FILE"
    grep -E "ERROR.*Failed to install" "$LOG_FILE" | sed 's/.*ERROR\] /- /' >> "$SUMMARY_FILE"
    
    # Add warnings section
    echo -e "\nWarnings:" >> "$SUMMARY_FILE"
    grep -E "\[WARNING\]" "$LOG_FILE" | sed 's/.*WARNING\] /- /' >> "$SUMMARY_FILE"
    
    # Add retry attempts section
    echo -e "\nRetry Attempts:" >> "$SUMMARY_FILE"
    grep -E "Retrying" "$LOG_FILE" | sed 's/.*INFO\] /- /' >> "$SUMMARY_FILE"
    
    # Add system resource information
    echo -e "\nSystem Resources:" >> "$SUMMARY_FILE"
    echo "- CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')%" >> "$SUMMARY_FILE"
    echo "- Memory Usage: $(free -m | awk '/Mem/{printf "%.1f%%", $3*100/$2}')" >> "$SUMMARY_FILE"
    echo "- Disk Usage: $(df -h / | awk '/\// {print $5}')" >> "$SUMMARY_FILE"
    
    # Create a copy of the summary file with a fixed name for easy access
    cp "$SUMMARY_FILE" "$LOG_DIR/latest_summary.log"
    
    # Add footer with links to both log files
    cat >> "$SUMMARY_FILE" << EOF
=================================================
Detailed Log: $LOG_FILE
Latest Summary: $LOG_DIR/latest_summary.log
=================================================
EOF
    
    log_message "SUCCESS" "Detailed installation summary generated: $SUMMARY_FILE"
    log_message "INFO" "A copy of the summary is available at: $LOG_DIR/latest_summary.log"
    
    # Display summary
    echo -e "\n\e[1;36m=== INSTALLATION SUMMARY ===\e[0m"
    cat "$SUMMARY_FILE"
}

# Function to update the system
update_system() {
    show_progress "system_update" "Updating system packages"
    
    log_message "INFO" "Updating system packages"
    
    # Update package lists
    log_message "INFO" "Updating package lists"
    if ! apt-get update; then
        log_message "ERROR" "Failed to update package lists"
        return 1
    fi
    
    # Upgrade packages with automatic confirmation
    log_message "INFO" "Upgrading packages"
    export DEBIAN_FRONTEND=noninteractive
    if ! apt-get upgrade -y; then
        export DEBIAN_FRONTEND=dialog
        log_message "ERROR" "Failed to upgrade packages"
        return 1
    fi
    export DEBIAN_FRONTEND=dialog
    
    # Run dist-upgrade for kernel and library updates
    log_message "INFO" "Running distribution upgrade"
    export DEBIAN_FRONTEND=noninteractive
    if ! apt-get dist-upgrade -y; then
        export DEBIAN_FRONTEND=dialog
        log_message "ERROR" "Failed to run distribution upgrade"
        return 1
    fi
    export DEBIAN_FRONTEND=dialog
    
    log_message "SUCCESS" "System update completed successfully"
    return 0
}

# Main cleanup function
perform_cleanup() {
    log_message "INFO" "Starting cleanup"
    
    # Remove unused packages
    if ! remove_unused_packages; then
        handle_error "Failed to remove unused packages" remove_unused_packages
    fi
    
    # Clean APT cache
    if ! clean_apt_cache; then
        handle_error "Failed to clean APT cache" clean_apt_cache
    fi
    
    # Remove temporary files
    if ! remove_temp_files; then
        handle_error "Failed to remove temporary files" remove_temp_files
    fi
    
    # Update the system
    if ! update_system; then
        handle_error "Failed to update system" update_system
    fi
    
    log_message "INFO" "Cleanup and system update completed"
}
