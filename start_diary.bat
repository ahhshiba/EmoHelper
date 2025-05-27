@echo off
setlocal

:: Change to the script's directory
cd /d "%~dp0"

:: Check if Python environment is set up
if not exist "venv" (
    echo Setting up Python environment...
    python environment.py
    if errorlevel 1 (
        echo Failed to set up environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Run the Streamlit app
echo Starting Diary Application...
streamlit run app.py

:: Deactivate virtual environment on exit
deactivate
endlocal 