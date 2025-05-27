#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed! Please install Python 3.8 or later."
    exit 1
fi

# Create and activate virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install or update dependencies
python -c "from environment import EnvironmentManager; env = EnvironmentManager(); env.setup_environment()"
if [ $? -ne 0 ]; then
    echo "Failed to setup environment!"
    exit 1
fi

# Check API key configuration
python -c "from environment import EnvironmentManager; env = EnvironmentManager(); env.check_api_key()"
if [ $? -ne 0 ]; then
    echo "Failed to verify API key!"
    exit 1
fi

# Start the application
echo "Starting Diary Application..."
streamlit run app.py

# Deactivate virtual environment
deactivate 