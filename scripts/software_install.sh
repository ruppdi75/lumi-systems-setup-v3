#!/bin/bash
#
# Software Installation Functions for Lumi-Systems Setup
#

# Installation tracking arrays
declare -A INSTALL_STATUS
declare -A INSTALL_REASON
SUCCESSFUL_APPS=()
FAILED_APPS=()

# Helper function to mark app as successfully installed
mark_app_success() {
    local app_name="$1"
    INSTALL_STATUS["$app_name"]="SUCCESS"
    SUCCESSFUL_APPS+=("$app_name")
    SUCCESSFUL_INSTALLS=$((SUCCESSFUL_INSTALLS + 1))
}

# Helper function to mark app as failed with reason
mark_app_failed() {
    local app_name="$1"
    local reason="${2:-Unknown error}"
    INSTALL_STATUS["$app_name"]="FAILED"
    INSTALL_REASON["$app_name"]="$reason"
    FAILED_APPS+=("$app_name")
    FAILED_INSTALLS=$((FAILED_INSTALLS + 1))
}

# Function to display installation checklist
show_installation_checklist() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "                    INSTALLATION CHECKLIST"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    # Count totals
    local total_apps=$((${#SUCCESSFUL_APPS[@]} + ${#FAILED_APPS[@]}))
    local success_count=${#SUCCESSFUL_APPS[@]}
    local failed_count=${#FAILED_APPS[@]}
    
    echo "📊 SUMMARY:"
    echo "   Total applications processed: $total_apps"
    echo "   ✅ Successfully installed: $success_count"
    echo "   ❌ Failed installations: $failed_count"
    echo ""
    
    # Show successful installations
    if [ ${#SUCCESSFUL_APPS[@]} -gt 0 ]; then
        echo "✅ SUCCESSFULLY INSTALLED:"
        for app in "${SUCCESSFUL_APPS[@]}"; do
            echo "   ✓ $app"
        done
        echo ""
    fi
    
    # Show failed installations with reasons
    if [ ${#FAILED_APPS[@]} -gt 0 ]; then
        echo "❌ FAILED INSTALLATIONS:"
        for app in "${FAILED_APPS[@]}"; do
            local reason="${INSTALL_REASON[$app]}"
            echo "   ✗ $app - Reason: $reason"
        done
        echo ""
    fi
    
    # Show completion percentage
    if [ $total_apps -gt 0 ]; then
        local success_percentage=$((success_count * 100 / total_apps))
        echo "📈 Installation Success Rate: $success_percentage%"
    fi
    
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
}

# Function to add Microsoft Edge repository
add_edge_repository() {
    log_message "INFO" "Adding Microsoft Edge repository"
    
    # Download and install the Microsoft signing key
    if wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg; then
        if mv microsoft.gpg /usr/share/keyrings/microsoft-edge-archive-keyring.gpg; then
            log_message "INFO" "Microsoft signing key installed"
        else
            log_message "ERROR" "Failed to install Microsoft signing key"
            return 1
        fi
    else
        log_message "ERROR" "Failed to download Microsoft signing key"
        return 1
    fi
    
    # Add the Edge repository with signed-by option
    if echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-edge-archive-keyring.gpg] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge.list; then
        log_message "INFO" "Microsoft Edge repository added"
        return 0
    else
        log_message "ERROR" "Failed to add Microsoft Edge repository"
        return 1
    fi
}

# Function to install OnlyOffice
install_onlyoffice() {
    log_message "INFO" "Starting OnlyOffice installation"
    show_progress "onlyoffice" "Installing OnlyOffice Desktop Editors"
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    log_message "INFO" "Created temporary directory: $temp_dir"
    
    # Try .deb installation first
    log_message "INFO" "Attempting to install OnlyOffice via .deb package"
    
    # Get the latest .deb download URL
    local deb_url="https://download.onlyoffice.com/install/desktop/editors/linux/onlyoffice-desktopeditors_amd64.deb"
    
    log_message "INFO" "Downloading OnlyOffice .deb package from: $deb_url"
    if wget -q --timeout=60 "$deb_url" -O "$temp_dir/onlyoffice.deb"; then
        log_message "INFO" "OnlyOffice .deb package downloaded successfully"
        
        # Install the .deb package
        log_message "INFO" "Installing OnlyOffice .deb package"
        if dpkg -i "$temp_dir/onlyoffice.deb" 2>/dev/null; then
            log_message "INFO" "OnlyOffice installed successfully via .deb package"
            mark_app_success "OnlyOffice (.deb)"
            rm -rf "$temp_dir"
            return 0
        else
            log_message "WARNING" "Failed to install OnlyOffice .deb package, trying to fix dependencies"
            
            # Try to fix dependencies and retry
            apt-get -f install -y >/dev/null 2>&1
            if dpkg -i "$temp_dir/onlyoffice.deb" 2>/dev/null; then
                log_message "INFO" "OnlyOffice installed successfully after fixing dependencies"
                mark_app_success "OnlyOffice (.deb)"
                rm -rf "$temp_dir"
                return 0
            else
                log_message "WARNING" "Failed to install OnlyOffice .deb package after fixing dependencies"
            fi
        fi
    else
        log_message "WARNING" "Failed to download OnlyOffice .deb package"
    fi
    
    # If .deb installation failed, try Flatpak
    log_message "INFO" "Falling back to Flatpak installation for OnlyOffice"
    
    # Check if Flatpak is installed
    if ! command -v flatpak &>/dev/null; then
        log_message "WARNING" "Flatpak is not installed, installing it first"
        apt-get update >/dev/null 2>&1
        apt-get install -y flatpak >/dev/null 2>&1
        
        # Add Flathub repository
        flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo >/dev/null 2>&1
    fi
    
    # Install OnlyOffice via Flatpak
    log_message "INFO" "Installing OnlyOffice via Flatpak from Flathub"
    if flatpak install -y flathub org.onlyoffice.desktopeditors 2>/dev/null; then
        log_message "INFO" "OnlyOffice installed successfully via Flatpak"
        mark_app_success "OnlyOffice (Flatpak)"
        rm -rf "$temp_dir"
        return 0
    else
        log_message "ERROR" "Failed to install OnlyOffice via Flatpak"
        mark_app_failure "OnlyOffice"
        rm -rf "$temp_dir"
        return 1
    fi
}

# Function to install RustDesk
install_rustdesk() {
    # Check if a specific version is requested or use 'latest'
    local version_to_install=${RUSTDESK_VERSION:-"latest"}
    local installation_method=${RUSTDESK_INSTALL_METHOD:-"deb"}
    
    if [ "$version_to_install" = "latest" ]; then
        show_progress "rustdesk" "Finding latest RustDesk version"
        log_message "INFO" "Finding latest RustDesk version"
    else
        show_progress "rustdesk" "Installing RustDesk $version_to_install"
        log_message "INFO" "Installing RustDesk version $version_to_install"
    fi
    
    log_message "INFO" "Installation method: $installation_method"
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    log_message "INFO" "Created temporary directory: $temp_dir"
    
    # Get system architecture
    local architecture=$(dpkg --print-architecture)
    local download_success=false
    local download_url=""
    local actual_version=""
    
    # If latest version is requested, get it from GitHub API
    if [ "$version_to_install" = "latest" ]; then
        log_message "INFO" "Fetching latest RustDesk release information from GitHub"
        
        # Download the latest release info
        if ! curl -s -L "https://api.github.com/repos/rustdesk/rustdesk/releases/latest" -o "$temp_dir/release.json"; then
            log_message "ERROR" "Failed to fetch release information from GitHub"
            rm -rf "$temp_dir"
            return 1
        fi
        
        # Extract the latest version tag
        if command -v jq &>/dev/null; then
            # Use jq if available
            actual_version=$(jq -r .tag_name "$temp_dir/release.json" | sed 's/^v//')
        else
            # Fallback to grep and sed if jq is not available
            actual_version=$(grep -o '"tag_name":"[^"]*"' "$temp_dir/release.json" | head -1 | sed 's/"tag_name":"\(.*\)"/\1/' | sed 's/^v//')
        fi
        
        if [ -z "$actual_version" ]; then
            log_message "ERROR" "Failed to extract latest version from GitHub API response"
            rm -rf "$temp_dir"
            return 1
        fi
        
        log_message "INFO" "Latest RustDesk version: $actual_version"
    else
        actual_version="$version_to_install"
    fi
    
    # Find the correct download URL for the deb package
    if [ "$version_to_install" = "latest" ]; then
        # Try to find the correct asset URL from the release info
        log_message "INFO" "System architecture: $architecture"
        
        # Define architecture patterns to look for
        local arch_patterns=()
        if [ "$architecture" = "amd64" ]; then
            arch_patterns=("x86_64" "amd64" "x64")
        elif [ "$architecture" = "arm64" ]; then
            arch_patterns=("arm64" "aarch64")
        else
            arch_patterns=("$architecture")
        fi
        
        log_message "INFO" "Looking for packages matching architectures: ${arch_patterns[*]}"
        
        if command -v jq &>/dev/null; then
            # Use jq for better parsing if available
            # First try to find exact architecture match
            for arch in "${arch_patterns[@]}"; do
                if [ -z "$download_url" ]; then
                    download_url=$(jq -r ".assets[] | select(.name | test(\"${arch}.deb$\")) | .browser_download_url" "$temp_dir/release.json" | head -1)
                    if [ -n "$download_url" ]; then
                        log_message "INFO" "Found package for architecture $arch: $download_url"
                    fi
                fi
            done
            
            # If still not found, look for any .deb file that might be architecture-independent
            if [ -z "$download_url" ]; then
                download_url=$(jq -r ".assets[] | select(.name | test(\".deb$\")) | .browser_download_url" "$temp_dir/release.json" | head -1)
                if [ -n "$download_url" ]; then
                    log_message "INFO" "Found generic .deb package: $download_url"
                fi
            fi
        else
            # Fallback method if jq is not available
            for arch in "${arch_patterns[@]}"; do
                if [ -z "$download_url" ]; then
                    download_url=$(grep -o '"browser_download_url":"[^"]*'"$arch"'.deb"' "$temp_dir/release.json" | head -1 | sed 's/"browser_download_url":"\(.*\)"/\1/')
                    if [ -n "$download_url" ]; then
                        log_message "INFO" "Found package for architecture $arch: $download_url"
                    fi
                fi
            done
            
            # If still not found, look for any .deb file
            if [ -z "$download_url" ]; then
                download_url=$(grep -o '"browser_download_url":"[^"]*\.deb"' "$temp_dir/release.json" | head -1 | sed 's/"browser_download_url":"\(.*\)"/\1/')
                if [ -n "$download_url" ]; then
                    log_message "INFO" "Found generic .deb package: $download_url"
                fi
            fi
        fi
    else
        # Try different URL patterns for a specific version
        local url_patterns=(
            "https://github.com/rustdesk/rustdesk/releases/download/$actual_version/rustdesk-$actual_version-$architecture.deb"
            "https://github.com/rustdesk/rustdesk/releases/download/$actual_version/rustdesk-$actual_version.deb"
            "https://github.com/rustdesk/rustdesk/releases/download/$actual_version/rustdesk_$actual_version-1_$architecture.deb"
            "https://github.com/rustdesk/rustdesk/releases/download/$actual_version/rustdesk_$actual_version-1.deb"
            "https://github.com/rustdesk/rustdesk/releases/download/$actual_version/rustdesk-$actual_version-x86_64.deb"
        )
        
        for url in "${url_patterns[@]}"; do
            log_message "INFO" "Checking URL: $url"
            if wget --spider -q "$url" 2>/dev/null; then
                download_url="$url"
                log_message "INFO" "Found valid download URL: $download_url"
                break
            fi
        done
    fi
    
    # Download the package if URL was found
    if [ -n "$download_url" ]; then
        log_message "INFO" "Downloading RustDesk from: $download_url"
        if wget -q "$download_url" -O "$temp_dir/rustdesk.deb"; then
            log_message "INFO" "RustDesk downloaded successfully"
            download_success=true
        else
            log_message "ERROR" "Failed to download RustDesk from: $download_url"
        fi
    else
        log_message "ERROR" "Could not find a valid download URL for RustDesk $actual_version"
    fi
    
    # If using Flatpak installation method or if DEB download fails, try Flatpak
    if [ "$installation_method" = "flatpak" ] || [ "$download_success" = false ]; then
        if [ "$installation_method" = "flatpak" ]; then
            log_message "INFO" "Using Flatpak installation method for RustDesk"
        else
            log_message "WARNING" "DEB download failed, trying Flatpak installation method"
        fi
        
        # Check if Flatpak is installed
        if ! command -v flatpak &>/dev/null; then
            log_message "INFO" "Flatpak not installed, installing it now"
            if ! setup_flatpak; then
                log_message "ERROR" "Failed to install Flatpak, cannot continue with Flatpak installation"
                if [ "$installation_method" = "flatpak" ]; then
                    rm -rf "$temp_dir"
                    return 1
                fi
            fi
        fi
        
        # If Flatpak is now available, try to install RustDesk
        if command -v flatpak &>/dev/null; then
            # First try installing from Flathub (most reliable method)
            log_message "INFO" "Attempting to install RustDesk from Flathub"
            if flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo; then
                if flatpak install -y flathub com.rustdesk.RustDesk; then
                    log_message "INFO" "RustDesk installed successfully from Flathub"
                    mark_app_success "RustDesk (Flatpak)"
                    rm -rf "$temp_dir"
                    return 0
                else
                    log_message "WARNING" "RustDesk not available on Flathub or installation failed, trying direct download"
                fi
            else
                log_message "WARNING" "Failed to add Flathub repository, trying direct download"
            fi
            
            # If Flathub fails, try direct download from GitHub
            local flatpak_url=""
            
            # Try to find Flatpak URL if using latest version
            if [ "$version_to_install" = "latest" ] && [ -f "$temp_dir/release.json" ]; then
                # Get system architecture
                local arch=$(dpkg --print-architecture)
                local arch_patterns=()
                
                # Map system architecture to possible Flatpak architecture patterns
                if [ "$arch" = "amd64" ]; then
                    arch_patterns=("x86_64" "amd64" "x64")
                elif [ "$arch" = "arm64" ]; then
                    arch_patterns=("arm64" "aarch64")
                else
                    arch_patterns=("$arch")
                fi
                
                log_message "INFO" "Looking for Flatpak packages matching architectures: ${arch_patterns[*]}"
                
                # Try to find a matching Flatpak for our architecture
                if command -v jq &>/dev/null; then
                    for arch_pattern in "${arch_patterns[@]}"; do
                        flatpak_url=$(jq -r ".assets[] | select(.name | test(\".flatpak$\")) | select(.name | test(\"$arch_pattern\")) | .browser_download_url" "$temp_dir/release.json" | head -1)
                        if [ -n "$flatpak_url" ]; then
                            log_message "INFO" "Found Flatpak for architecture $arch_pattern: $flatpak_url"
                            break
                        fi
                    done
                    
                    # If no architecture-specific Flatpak found, try any Flatpak as last resort
                    if [ -z "$flatpak_url" ]; then
                        flatpak_url=$(jq -r ".assets[] | select(.name | test(\".flatpak$\")) | .browser_download_url" "$temp_dir/release.json" | head -1)
                        if [ -n "$flatpak_url" ]; then
                            log_message "WARNING" "No architecture-specific Flatpak found, using: $flatpak_url"
                        fi
                    fi
                else
                    # Fallback if jq is not available
                    for arch_pattern in "${arch_patterns[@]}"; do
                        flatpak_url=$(grep -o "\"browser_download_url\":\"[^\"]*$arch_pattern[^\"]*\.flatpak\"" "$temp_dir/release.json" | head -1 | sed 's/"browser_download_url":"\(.*\)"/\1/')
                        if [ -n "$flatpak_url" ]; then
                            log_message "INFO" "Found Flatpak for architecture $arch_pattern: $flatpak_url"
                            break
                        fi
                    done
                    
                    # If no architecture-specific Flatpak found, try any Flatpak as last resort
                    if [ -z "$flatpak_url" ]; then
                        flatpak_url=$(grep -o '"browser_download_url":"[^"]*\.flatpak"' "$temp_dir/release.json" | head -1 | sed 's/"browser_download_url":"\(.*\)"/\1/')
                        if [ -n "$flatpak_url" ]; then
                            log_message "WARNING" "No architecture-specific Flatpak found, using: $flatpak_url"
                        fi
                    fi
                fi
            fi
            
            # If no Flatpak URL found from API, try standard URL patterns
            if [ -z "$flatpak_url" ]; then
                # Get system architecture
                local arch=$(dpkg --print-architecture)
                local arch_patterns=()
                
                # Map system architecture to possible Flatpak architecture patterns
                if [ "$arch" = "amd64" ]; then
                    arch_patterns=("x86_64" "amd64" "x64")
                elif [ "$arch" = "arm64" ]; then
                    arch_patterns=("arm64" "aarch64")
                else
                    arch_patterns=("$arch")
                fi
                
                log_message "INFO" "Looking for Flatpak packages matching architectures: ${arch_patterns[*]}"
                
                local flatpak_patterns=()
                
                # Generate URL patterns for each architecture
                for arch_pattern in "${arch_patterns[@]}"; do
                    flatpak_patterns+=("https://github.com/rustdesk/rustdesk/releases/download/$actual_version/rustdesk-$actual_version-$arch_pattern.flatpak")
                done
                
                # Add generic patterns as fallback
                flatpak_patterns+=("https://github.com/rustdesk/rustdesk/releases/download/$actual_version/rustdesk-$actual_version.flatpak")
                flatpak_patterns+=("https://github.com/rustdesk/rustdesk/releases/download/$actual_version/rustdesk_$actual_version.flatpak")
                
                for url in "${flatpak_patterns[@]}"; do
                    log_message "INFO" "Checking Flatpak URL: $url"
                    if wget --spider -q "$url" 2>/dev/null; then
                        flatpak_url="$url"
                        log_message "INFO" "Found valid Flatpak URL: $flatpak_url"
                        break
                    fi
                done
            fi
            
            # If we found a Flatpak URL, download and install it
            if [ -n "$flatpak_url" ]; then
                log_message "INFO" "Downloading RustDesk Flatpak from: $flatpak_url"
                if wget -q "$flatpak_url" -O "$temp_dir/rustdesk.flatpak"; then
                    log_message "INFO" "RustDesk Flatpak downloaded successfully"
                    
                    log_message "INFO" "Installing RustDesk via Flatpak"
                    if flatpak install --user -y "$temp_dir/rustdesk.flatpak"; then
                        log_message "INFO" "RustDesk installed successfully via Flatpak"
                        mark_app_success "RustDesk (Flatpak)"
                        rm -rf "$temp_dir"
                        return 0
                    else
                        log_message "ERROR" "Failed to install RustDesk via Flatpak"
                    fi
                else
                    log_message "ERROR" "Failed to download RustDesk Flatpak"
                fi
            else
                log_message "WARNING" "No valid Flatpak download URL found"
            fi
        fi
    fi
    
    # If we're still here and using Flatpak method, try falling back to .deb installation
    if [ "$installation_method" = "flatpak" ]; then
        log_message "WARNING" "All Flatpak installation attempts for RustDesk failed, falling back to .deb installation"
        
        # If we already have a .deb file downloaded, try to install it
        if [ -f "$temp_dir/rustdesk.deb" ] && [ "$download_success" = true ]; then
            log_message "INFO" "Attempting to install RustDesk using downloaded .deb package"
            
            # Install RustDesk using the .deb package
            if dpkg -i "$temp_dir/rustdesk.deb"; then
                log_message "INFO" "RustDesk installed successfully via .deb package"
                mark_app_success "RustDesk (.deb)"
                rm -rf "$temp_dir"
                return 0
            else
                log_message "WARNING" "Failed to install RustDesk .deb package, trying to fix dependencies"
                
                # Try to fix dependencies and retry
                apt-get -f install -y
                if dpkg -i "$temp_dir/rustdesk.deb"; then
                    log_message "INFO" "RustDesk installed successfully after fixing dependencies"
                    mark_app_success "RustDesk (.deb)"
                    rm -rf "$temp_dir"
                    return 0
                else
                    log_message "ERROR" "Failed to install RustDesk .deb package after fixing dependencies"
                fi
            fi
        else 
            log_message "ERROR" "No valid .deb package available for fallback installation"
        fi
        
        # If we get here, all installation methods failed
        log_message "ERROR" "All installation attempts for RustDesk failed"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # If we're still here and using DEB method but download failed, try apt
    if [ "$download_success" = false ]; then
        log_message "WARNING" "Direct download failed, trying package manager"
        
        # Try to install via apt
        log_message "INFO" "Attempting to install RustDesk via package manager"
        if apt-get install -y rustdesk; then
            log_message "INFO" "RustDesk installed successfully from repositories"
            mark_app_success "RustDesk (APT)"
            rm -rf "$temp_dir"
            return 0
        else
            log_message "WARNING" "RustDesk not available in standard repositories"
        fi
        
        # If we get here, all download attempts failed
        log_message "ERROR" "All download attempts for RustDesk failed"
        mark_app_failed "RustDesk" "All download attempts failed"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Install RustDesk
    log_message "INFO" "Installing RustDesk package"
    if dpkg -i "$temp_dir/rustdesk.deb"; then
        log_message "INFO" "RustDesk installed successfully"
        mark_app_success "RustDesk (.deb)"
    else
        log_message "ERROR" "Failed to install RustDesk package"
        # Try to fix dependencies and retry
        log_message "INFO" "Attempting to fix dependencies and retry installation"
        apt-get -f install -y
        if dpkg -i "$temp_dir/rustdesk.deb"; then
            log_message "INFO" "RustDesk installed successfully after fixing dependencies"
            mark_app_success "RustDesk (.deb)"
        else
            log_message "ERROR" "Failed to install RustDesk package after fixing dependencies"
            mark_app_failed "RustDesk" "Failed to install .deb package"
            rm -rf "$temp_dir"
            return 1
        fi
    fi
    
    # Clean up
    rm -rf "$temp_dir"
    log_message "INFO" "Temporary directory removed"
    
    return 0
}

# Function to install a single APT package
install_apt_package() {
    local package="$1"
    
    log_message "INFO" "Installing package: $package"
    
    # First try normal installation
    if apt-get install -y "$package"; then
        log_message "INFO" "Package installed successfully: $package"
        mark_app_success "$package"
        return 0
    else
        # Try with --allow-unauthenticated if normal installation fails
        log_message "WARNING" "Standard installation failed for $package. Trying with --allow-unauthenticated"
        if apt-get install -y --allow-unauthenticated "$package"; then
            log_message "INFO" "Package installed successfully with --allow-unauthenticated: $package"
            mark_app_success "$package"
            return 0
        else
            # Check if it's a virtual package
            local apt_cache_output=$(apt-cache policy "$package" 2>&1)
            
            if echo "$apt_cache_output" | grep -q "is a virtual package"; then
                log_message "WARNING" "$package is a virtual package. Attempting to find a suitable provider."
                
                # Try to extract the first provider
                local provider=$(echo "$apt_cache_output" | grep -oP '\s+\K[^\s]+(?=\s+[0-9])' | head -1)
                
                if [ -n "$provider" ]; then
                    log_message "INFO" "Trying to install $provider as a replacement for $package"
                    
                    if apt-get install -y "$provider" || apt-get install -y --allow-unauthenticated "$provider"; then
                        log_message "SUCCESS" "Successfully installed $provider as a replacement for $package"
                        mark_app_success "$package (via $provider)"
                        return 0
                    else
                        log_message "ERROR" "Failed to install $provider as a replacement for $package"
                    fi
                else
                    log_message "ERROR" "Could not determine a provider for virtual package $package"
                fi
            fi
            
            log_message "ERROR" "Failed to install package: $package"
            mark_app_failed "$package" "Package not found or installation failed"
            return 1
        fi
    fi
}

# Function to install APT GUI applications
install_apt_gui_apps() {
    log_message "INFO" "Installing APT GUI applications"
    
    # Configure debconf to automatically accept license agreements and prompts
    log_message "INFO" "Configuring automatic acceptance for package installations"
    echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula boolean true" | debconf-set-selections
    echo "msttcorefonts msttcorefonts/accepted-mscorefonts-eula boolean true" | debconf-set-selections
    export DEBIAN_FRONTEND=noninteractive
    
    # Add repositories for special packages
    add_edge_repository
    # OnlyOffice will be installed via Flatpak instead of APT
    
    # Update package lists after adding repositories
    update_package_lists
    
    # Install each GUI application
    for app in "${APT_GUI_APPS[@]}"; do
        show_progress "apt_gui_$app" "Installing $app"
        
        # Normal installation for all packages
        if ! install_apt_package "$app"; then
            handle_error "Failed to install $app" "install_apt_package $app"
        fi
    done
    
    # Reset DEBIAN_FRONTEND
    export DEBIAN_FRONTEND=dialog
    
    log_message "INFO" "APT GUI applications installation completed"
}

# Function to install APT CLI tools
install_apt_cli_tools() {
    log_message "INFO" "Installing APT CLI tools"
    
    # Install each CLI tool
    for tool in "${APT_CLI_TOOLS[@]}"; do
        show_progress "apt_cli_$tool" "Installing $tool"
        if ! install_apt_package "$tool"; then
            handle_error "Failed to install $tool" "install_apt_package $tool"
        fi
    done
    
    log_message "INFO" "APT CLI tools installation completed"
}

# Function to install RustDesk dependencies
install_rustdesk_dependencies() {
    log_message "INFO" "Installing RustDesk dependencies"
    
    # Install each dependency
    for dep in "${RUSTDESK_DEPENDENCIES[@]}"; do
        show_progress "dep_$dep" "Installing dependency: $dep"
        if ! install_apt_package "$dep"; then
            handle_error "Failed to install dependency: $dep" "install_apt_package $dep"
        fi
    done
    
    log_message "INFO" "RustDesk dependencies installation completed"
}

# Function to setup Flatpak
setup_flatpak() {
    show_progress "flatpak_setup" "Setting up Flatpak"
    
    log_message "INFO" "Installing Flatpak and GNOME Software plugin"
    
    # Install Flatpak and GNOME Software plugin
    if apt-get install -y flatpak gnome-software-plugin-flatpak; then
        log_message "INFO" "Flatpak and GNOME Software plugin installed successfully"
        mark_app_success "Flatpak Setup"
    else
        log_message "ERROR" "Failed to install Flatpak and GNOME Software plugin"
        mark_app_failed "Flatpak Setup" "Failed to install Flatpak packages"
        return 1
    fi
    
    # Add Flathub repository
    log_message "INFO" "Adding Flathub repository"
    if flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo; then
        log_message "INFO" "Flathub repository added successfully"
        return 0
    else
        log_message "ERROR" "Failed to add Flathub repository"
        return 1
    fi
}

# Function to install Flatpak applications
install_flatpak_apps() {
    log_message "INFO" "Installing Flatpak applications"
    
    # Install each Flatpak application
    for app in "${FLATPAK_APPS[@]}"; do
        # Skip OnlyOffice as it's installed separately
        if [ "$app" = "org.onlyoffice.desktopeditors" ]; then
            log_message "INFO" "Skipping OnlyOffice Flatpak installation as it's handled separately"
            continue
        fi
        
        # Skip VLC if it's already installed via APT to avoid duplicate icons
        if [ "$app" = "org.videolan.VLC" ] && dpkg -l | grep -q "^ii\s\+vlc\s\+"; then
            log_message "INFO" "Skipping Flatpak VLC installation as it's already installed via APT"
            continue
        fi
        
        show_progress "flatpak_$app" "Installing Flatpak app: $app"
        
        log_message "INFO" "Installing Flatpak application: $app"
        if flatpak install -y flathub "$app"; then
            log_message "INFO" "Flatpak application installed successfully: $app"
            mark_app_success "$app (Flatpak)"
            # Optionally launch Thunderbird after install
            if [ "$app" = "org.mozilla.Thunderbird" ] && [ "${LAUNCH_THUNDERBIRD:-false}" = true ]; then
                log_message "INFO" "Launching Thunderbird via Flatpak as requested."
                flatpak run org.mozilla.Thunderbird &
            fi
        else
            log_message "ERROR" "Failed to install Flatpak application: $app"
            mark_app_failed "$app (Flatpak)" "Flatpak installation failed"
        fi
    done
    
    log_message "INFO" "Flatpak applications installation completed"
}

# Main software installation function
# Function to clean up repository files that might cause issues
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
    
    # Update package lists after cleanup
    log_message "INFO" "Updating package lists after repository cleanup"
    apt-get update -o Acquire::AllowInsecureRepositories=true
}

install_software() {
    log_message "INFO" "Starting software installation"
    
    # Clean up problematic repository files first
    cleanup_repository_files
    
    # Install RustDesk dependencies first
    install_rustdesk_dependencies
    
    # Install RustDesk (with error handling - continues on failure)
    if ! install_rustdesk; then
        log_message "WARNING" "RustDesk installation failed, continuing with other applications"
        mark_app_failed "RustDesk" "Installation failed - continuing with other apps"
    fi
    
    # Install OnlyOffice (with error handling - continues on failure)
    if ! install_onlyoffice; then
        log_message "WARNING" "OnlyOffice installation failed, continuing with other applications"
        mark_app_failed "OnlyOffice" "Installation failed - continuing with other apps"
    fi
    
    # Install APT GUI applications
    install_apt_gui_apps
    
    # Install APT CLI tools
    install_apt_cli_tools
    
    # Setup Flatpak (with error handling - continues on failure)
    if ! setup_flatpak; then
        log_message "WARNING" "Flatpak setup failed, skipping Flatpak applications"
        mark_app_failed "Flatpak Setup" "Setup failed - skipping Flatpak apps"
    else
        # Install Flatpak applications only if setup succeeded
        install_flatpak_apps
    fi
    
    log_message "INFO" "Software installation completed"
    
    # Display comprehensive installation checklist
    show_installation_checklist
}
