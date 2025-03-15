#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create gpx directory if it doesn't exist
mkdir -p gpx

# Run the parser script
echo "Starting Park4Night parser..."
python3 get_bookmarks.py

# Deactivate virtual environment
deactivate