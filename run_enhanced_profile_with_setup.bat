@echo off
echo ====================================================
echo Enhanced Profile Setup and Launcher
echo ====================================================
echo.

echo Step 1: Updating database schema for enhanced profile...
python update_database_enhanced_profile.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error updating database schema. Please check the output above for details.
    echo Press any key to continue anyway...
    pause > nul
) else (
    echo Database update completed successfully!
)

echo.
echo Step 2: Launching Enhanced Profile UI...
echo.
echo IMPORTANT: Please ensure you fill in all required fields:
echo - Gender (male/female)
echo - Height (feet and inches)
echo - Date of Birth (MMDDYY format)
echo - Start Date (MMDDYY format)
echo - Initial Weight
echo - Resistance Training status
echo - Workout Type
echo - Weekly Workout Frequency
echo - Experience Level
echo.
echo These fields are critical for proper RMR calculation!
echo.
echo Starting Profile UI...
echo.
python enhanced_profile_ui.py

echo.
echo Enhanced Profile session completed.
echo.
pause
