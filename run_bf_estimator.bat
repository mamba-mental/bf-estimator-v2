@echo off
echo ====================================================
echo       Body Fat Estimator Application Launcher
echo ====================================================
echo.

rem Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in your PATH.
    echo Please install Python 3.8 or newer from python.org
    echo.
    pause
    exit /b 1
)

rem Run the launcher
echo Starting the BF Estimator launcher...
echo.
python app_launcher.py

rem If the application exits with an error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code %errorlevel%
    echo.
    pause
) else (
    echo.
    echo Application closed successfully.
    echo.
)
