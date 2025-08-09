#!/bin/bash

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the main setup.sh to get all required functions
source "$SCRIPT_DIR/setup.sh"

# Set weather location
WEATHER_LOCATION="Vienna"

# Run just the weather location configuration
configure_weather_location

# Print result
if [ $? -eq 0 ]; then
    echo "Weather location successfully configured!"
else
    echo "Weather location configuration failed."
fi
