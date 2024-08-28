#!/bin/bash

# Define the repository URL and the directory name
REPO_URL="https://github.com/61l65k/42_calendar_listener.git"
DIR_NAME="42_calendar_listener"

# Check if the current directory is the target directory
if [ "${PWD##*/}" == "$DIR_NAME" ]; then
    echo "You are already in the $DIR_NAME directory."
else
    # Clone the repository if the directory does not exist
    if [ -d "$DIR_NAME" ]; then
        echo "Directory $DIR_NAME already exists."
        cd $DIR_NAME
    else
        echo "Cloning the repository..."
        git clone $REPO_URL
        cd $DIR_NAME
    fi
fi

# Check if Python 3 is installed
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

# Create a Python virtual environment
if [ ! -d "venv" ]; then
    echo "Setting up the Python virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Install the requirements
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installation is complete."

echo -e "\n\n To start the listener, run the following command: \n"
echo -e "source venv/bin/activate && python3 42_calendar.py \n\n"

echo -e "To deactivate the virtual environment, run: \n"
echo -e "deactivate \n\n"
