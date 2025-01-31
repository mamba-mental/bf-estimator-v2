@echo off
echo Setting up Python environment for BF Estimator Terminal...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.x and try again.
    pause
    exit /b 1
)

REM Install requirements
echo Installing required packages...
pip install -r requirements.txt

REM Run the application
echo Starting BF Estimator...
python main.py

REM Keep the window open
pause
