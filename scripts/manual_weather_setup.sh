#!/bin/bash
#
# Manual Weather Location Setup Script
# Use this script to manually configure weather location if automatic setup failed
#

echo -e "\e[1;34m🌤️  Manual Weather Location Setup\e[0m"
echo "This script helps you set up weather location for GNOME Weather"
echo ""

# Check if GNOME Weather is installed
if ! command -v gnome-weather &> /dev/null; then
    echo -e "\e[1;31m❌ GNOME Weather is not installed\e[0m"
    echo "Please install it first: sudo apt install gnome-weather"
    exit 1
fi

# Check if gsettings is available
if ! command -v gsettings &> /dev/null; then
    echo -e "\e[1;31m❌ gsettings is not available\e[0m"
    echo "Please install it first: sudo apt install glib2.0-bin"
    exit 1
fi

# Check if schema exists
if ! gsettings list-schemas | grep -q org.gnome.Weather; then
    echo -e "\e[1;31m❌ GNOME Weather schema not found\e[0m"
    echo "Please run GNOME Weather at least once to initialize it"
    exit 1
fi

echo -e "\e[1;32m✓ GNOME Weather is ready for configuration\e[0m"
echo ""

# Available cities
echo "Available predefined cities:"
echo "1) Vienna/Wien"
echo "2) Salzburg" 
echo "3) Graz"
echo "4) Innsbruck"
echo "5) Linz"
echo "6) Custom (you'll need to provide coordinates)"
echo ""

read -p "Select a city (1-6): " choice

case $choice in
    1)
        city="Vienna"
        gvariant="[<(uint32 2, <('Vienna', '', false, [(48.2082, 16.3738)], [(48.2082, 16.3738)])>)>]"
        ;;
    2)
        city="Salzburg"
        gvariant="[<(uint32 2, <('Salzburg', '', false, [(47.8095, 13.0550)], [(47.8095, 13.0550)])>)>]"
        ;;
    3)
        city="Graz"
        gvariant="[<(uint32 2, <('Graz', '', false, [(47.0707, 15.4395)], [(47.0707, 15.4395)])>)>]"
        ;;
    4)
        city="Innsbruck"
        gvariant="[<(uint32 2, <('Innsbruck', '', false, [(47.2692, 11.4041)], [(47.2692, 11.4041)])>)>]"
        ;;
    5)
        city="Linz"
        gvariant="[<(uint32 2, <('Linz', '', false, [(48.3069, 14.2858)], [(48.3069, 14.2858)])>)>]"
        ;;
    6)
        echo ""
        read -p "Enter city name: " city
        read -p "Enter latitude: " lat
        read -p "Enter longitude: " lon
        gvariant="[<(uint32 2, <('$city', '', false, [($lat, $lon)], [($lat, $lon)])>)>]"
        ;;
    *)
        echo "Invalid choice. Using Vienna as default."
        city="Vienna"
        gvariant="[<(uint32 2, <('Vienna', '', false, [(48.2082, 16.3738)], [(48.2082, 16.3738)])>)>]"
        ;;
esac

echo ""
echo -e "\e[1;36m🔧 Setting weather location to: $city\e[0m"

if gsettings set org.gnome.Weather locations "$gvariant"; then
    echo -e "\e[1;32m✅ Weather location set successfully!\e[0m"
    echo "You can now open GNOME Weather to see the weather for $city"
else
    echo -e "\e[1;31m❌ Failed to set weather location\e[0m"
    echo "You can try setting it manually in GNOME Weather:"
    echo "1. Open GNOME Weather"
    echo "2. Click the + button"
    echo "3. Search for and add: $city"
fi
