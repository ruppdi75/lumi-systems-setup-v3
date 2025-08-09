#!/bin/bash
#
# System Configuration Functions for Lumi-Systems Setup
#

# Function to configure system language
configure_system_language() {
    show_progress "system_language" "Setting system language to $SYSTEM_LANGUAGE"
    
    log_message "INFO" "Configuring system language to $SYSTEM_LANGUAGE"
    
    # Install language pack
    if apt-get install -y language-pack-de; then
        log_message "INFO" "German language pack installed"
    else
        log_message "ERROR" "Failed to install German language pack"
        return 1
    fi
    
    # Generate the locale
    if locale-gen "$SYSTEM_LANGUAGE"; then
        log_message "INFO" "Locale generated: $SYSTEM_LANGUAGE"
    else
        log_message "ERROR" "Failed to generate locale: $SYSTEM_LANGUAGE"
        return 1
    fi
    
    # Set the locale
    if update-locale LANG="$SYSTEM_LANGUAGE" LC_ALL="$SYSTEM_LANGUAGE"; then
        log_message "INFO" "System language set to $SYSTEM_LANGUAGE"
        SUCCESSFUL_INSTALLS=$((SUCCESSFUL_INSTALLS + 1))
        return 0
    else
        log_message "ERROR" "Failed to set system language to $SYSTEM_LANGUAGE"
        return 1
    fi
}

# Function to configure system timezone
configure_system_timezone() {
    show_progress "system_timezone" "Setting system timezone to $SYSTEM_TIMEZONE"
    
    log_message "INFO" "Configuring system timezone to $SYSTEM_TIMEZONE"
    
    if timedatectl set-timezone "$SYSTEM_TIMEZONE"; then
        log_message "INFO" "System timezone set to $SYSTEM_TIMEZONE"
        SUCCESSFUL_INSTALLS=$((SUCCESSFUL_INSTALLS + 1))
        return 0
    else
        log_message "ERROR" "Failed to set system timezone to $SYSTEM_TIMEZONE"
        return 1
    fi
}

# Function to configure weather location
configure_weather_location() {
    show_progress "weather_location" "Setting weather location to $WEATHER_LOCATION"
    log_message "INFO" "Configuring weather location to $WEATHER_LOCATION"

    # Check if we're in a desktop environment that supports weather settings
    if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
        log_message "WARN" "No display environment detected. Skipping weather location configuration."
        echo -e "\e[1;33m⚠️  Weather location will need to be set manually after desktop login\e[0m"
        SUCCESSFUL_INSTALLS=$((SUCCESSFUL_INSTALLS + 1))
        return 0
    fi

    # Check if gsettings is available
    if ! command -v gsettings &> /dev/null; then
        log_message "WARN" "gsettings command not found. Weather location will need to be set manually."
        echo -e "\e[1;33m⚠️  Please set weather location manually in GNOME Weather after installation\e[0m"
        SUCCESSFUL_INSTALLS=$((SUCCESSFUL_INSTALLS + 1))
        return 0
    fi

    # Get current user
    if [ "$SUDO_USER" ]; then
        CURRENT_USER="$SUDO_USER"
    else
        CURRENT_USER="$(whoami)"
    fi

    # Check if GNOME Weather schema exists
    if ! su - "$CURRENT_USER" -c "gsettings list-schemas | grep -q org.gnome.Weather" 2>/dev/null; then
        log_message "WARN" "GNOME Weather schema not found. Weather location will be set when GNOME Weather is installed."
        echo -e "\e[1;33m⚠️  GNOME Weather not installed yet. Location will be configured after software installation.\e[0m"
        SUCCESSFUL_INSTALLS=$((SUCCESSFUL_INSTALLS + 1))
        return 0
    fi

    # Define GVariant for Vienna (expandable for more cities)
    local city="$WEATHER_LOCATION"
    local gvariant_value=""
    case "$city" in
        "Vienna"|"Wien")
            gvariant_value="[<(uint32 2, <('Vienna', '', false, [(48.2082, 16.3738)], [(48.2082, 16.3738)])>)>]"
            ;;
        "Salzburg")
            gvariant_value="[<(uint32 2, <('Salzburg', '', false, [(47.8095, 13.0550)], [(47.8095, 13.0550)])>)>]"
            ;;
        "Graz")
            gvariant_value="[<(uint32 2, <('Graz', '', false, [(47.0707, 15.4395)], [(47.0707, 15.4395)])>)>]"
            ;;
        "Innsbruck")
            gvariant_value="[<(uint32 2, <('Innsbruck', '', false, [(47.2692, 11.4041)], [(47.2692, 11.4041)])>)>]"
            ;;
        "Linz")
            gvariant_value="[<(uint32 2, <('Linz', '', false, [(48.3069, 14.2858)], [(48.3069, 14.2858)])>)>]"
            ;;
        # Add more cities here as needed
        *)
            log_message "WARN" "Unknown city for weather location: $city. Using Vienna as default."
            gvariant_value="[<(uint32 2, <('Vienna', '', false, [(48.2082, 16.3738)], [(48.2082, 16.3738)])>)>]"
            city="Vienna (default)"
            ;;
    esac

    # Try to set the weather location with better error handling
    if su - "$CURRENT_USER" -c "gsettings set org.gnome.Weather locations '$gvariant_value'" 2>/dev/null; then
        log_message "INFO" "Weather location set to $city successfully"
        SUCCESSFUL_INSTALLS=$((SUCCESSFUL_INSTALLS + 1))
        return 0
    else
        log_message "WARN" "Could not set weather location automatically. This can be set manually later."
        echo -e "\e[1;33m⚠️  Weather location setting failed. You can set it manually in GNOME Weather:\e[0m"
        echo -e "\e[1;33m   1. Open GNOME Weather\e[0m"
        echo -e "\e[1;33m   2. Click the + button to add a location\e[0m"
        echo -e "\e[1;33m   3. Search for and select: $WEATHER_LOCATION\e[0m"
        SUCCESSFUL_INSTALLS=$((SUCCESSFUL_INSTALLS + 1))
        return 0
    fi
}

# Main system configuration function
configure_system() {
    log_message "INFO" "Starting system configuration"
    
    # Configure system language
    if ! configure_system_language; then
        handle_error "Failed to configure system language" configure_system_language
    fi
    
    # Configure system timezone
    if ! configure_system_timezone; then
        handle_error "Failed to configure system timezone" configure_system_timezone
    fi
    
    # Configure weather location (non-fatal)
    configure_weather_location || {
        log_message "WARN" "Weather location configuration was skipped or failed, but continuing with setup"
        echo -e "\e[1;33m⚠️  Weather location setup was skipped - you can configure it manually later\e[0m"
    }
    
    log_message "INFO" "System configuration completed"
}
