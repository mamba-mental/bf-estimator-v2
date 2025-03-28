@echo off
echo ============================================================================
echo BF Estimator Enhanced with Diet Calculations - Comprehensive Setup & Launch
echo ============================================================================
echo.
echo This script will:
echo  1. Update the database schema for enhanced user profiles
echo  2. Install required modules for diet calculations
echo  3. Configure report generation with diet-based calculations
echo  4. Launch the enhanced app with diet features
echo.
echo Press Ctrl+C to cancel or any key to continue...
pause > nul

REM Create a temporary directory for setup files
mkdir temp_setup 2>nul

REM Install required packages if needed
echo Checking required packages...
python -m pip install --upgrade pip
python -m pip install customtkinter weasyprint matplotlib

REM Update database schema for enhanced profile
echo.
echo Updating database schema for enhanced profile...
python update_database_enhanced_profile.py
if %ERRORLEVEL% NEQ 0 (
    echo Error updating database schema! Aborting.
    pause
    exit /b 1
)
echo Database schema updated successfully.

REM Backup existing database
echo.
echo Creating database backup...
copy history.db history.db.bak_diet_update 2>nul
echo Database backup created as history.db.bak_diet_update

REM Setup report configuration to use the enhanced report generation
echo.
echo Configuring enhanced report generation with diet calculations...
echo import fixed_report_generation_enhanced as report_module > temp_setup\report_config.py
echo report_generate = report_module.generate_comprehensive_report >> temp_setup\report_config.py
echo report_save = report_module.save_report >> temp_setup\report_config.py

REM Run the enhanced application
echo.
echo Starting Enhanced BF Estimator with Diet Calculations...
echo.
python -c "import sys; import os; sys.path.append(os.path.abspath('temp_setup')); import diet_calculations; import enhanced_profile_ui; from run_enhanced_app import main; main()"

REM Clean up
echo.
rmdir /s /q temp_setup 2>nul

echo.
echo Application session complete.
echo Remember to check the 'results' folder for your generated reports with diet-based projections.
echo.
pause
