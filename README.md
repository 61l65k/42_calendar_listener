## 42 Calendar listener

### Important Notes:

- **Security Warning**: Running scripts directly from `curl` can be dangerous, especially if the script has not been reviewed by the user. It's a good practice to encourage users to first review the script before executing it, especially if it's being piped directly into `bash`.
- **Permissions**: The user running the script will need appropriate permissions to install software and write to the system directories involved.
- **Dependencies**: Ensure that users know they need `curl`, `git`, and `python3` installed on their system before running the script.


## Installation

To install this project and all dependencies, run the following command:

```bash
curl -s https://raw.githubusercontent.com/4l3xHive/42_calendar_listener/main/install.sh | bash
```


### Full `install.sh` Script:

Ensure your `install.sh` script is complete and robust enough to handle errors and is accessible as a raw file from GitHub. Here's the script for clarity:

```bash
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
