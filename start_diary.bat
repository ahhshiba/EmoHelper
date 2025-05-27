@echo off
setlocal

:: Change to the script's directory
cd /d "%~dp0"

:: Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

:: Check Python version
python -c "import sys; sys.exit(0) if sys.version_info >= (3,8) else sys.exit(1)"
if errorlevel 1 (
    echo Python 3.8 or later is required
    echo Current Python version:
    python --version
    pause
    exit /b 1
)

:: Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    echo GOOGLE_API_KEY=your_api_key_here > .env
    echo Please edit the .env file and add your Google API key
    notepad .env
)

:: Check if Python environment is set up
if not exist "venv" (
    echo Setting up Python environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
    
    :: Activate and install requirements
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install requirements
        pause
        exit /b 1
    )
) else (
    :: Activate existing environment
    call venv\Scripts\activate.bat
)

:: Run the Streamlit app
echo Starting Diary Application...
streamlit run app.py

:: Deactivate virtual environment on exit
deactivate
endlocal 