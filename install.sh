#!/bin/bash

# Define the repository URL and the directory name
REPO_URL="https://github.com/4l3xHive/42_calendar_listener.git"
DIR_NAME="42_calendar_listener"

# Clone the repository
echo "Cloning the repository..."
git clone $REPO_URL
cd $DIR_NAME

# Check if Python 3 is installed
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

# Create a Python virtual environment
echo "Setting up the Python virtual environment..."
python3 -m venv venv

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Install the requirements
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installation is complete."

echo -e "\n\n To start the listener, run the following command: \n"
echo -e "source venv/bin/activate && python3 42_calendar.py \n\n"
 