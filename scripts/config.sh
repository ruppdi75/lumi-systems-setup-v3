#!/bin/bash
#
# Configuration File for Lumi-Systems Setup
# Edit this file to customize the installation
#

# System configuration
SYSTEM_LANGUAGE="de_AT.UTF-8"
# SYSTEM_TIMEZONE="Europe/Vienna"  # Removed - not working in this script
# WEATHER_LOCATION="Vienna"        # Removed - not working in this script

# RustDesk configuration
# Version: set to "latest" to automatically use the latest available version
RUSTDESK_VERSION="latest"
# Installation method: "deb" or "flatpak"
RUSTDESK_INSTALL_METHOD="flatpak"

# Software lists
# APT GUI applications
APT_GUI_APPS=(
    "gimp"
    "inkscape"
    "krita"
    "vlc"
    "gnome-tweaks"

    "microsoft-edge-stable"
    "firefox"
    "evolution"
    "thunderbird"
)

# APT CLI tools
APT_CLI_TOOLS=(
    "wget"
    "curl"
    "git"
    "htop"
    "neofetch"
    "btop"
    "p7zip-full"
)

# Flatpak applications
FLATPAK_APPS=(
    "org.onlyoffice.desktopeditors"
    "chat.revolt.RevoltDesktop"
    "com.obsproject.Studio"
    "org.videolan.VLC"
)

# RustDesk dependencies
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
