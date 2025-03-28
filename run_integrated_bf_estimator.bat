@echo off
echo ============================================================================
echo Enhanced BF Estimator v2.1 with Dashboard and Settings
echo ============================================================================
echo.
echo This will run the fully integrated version with:
echo  - Dashboard with real-time metrics
echo  - Enhanced user profile with gender, height and more
echo  - Diet-based calculations and projections
echo  - Settings tab for customization
echo.
echo Press Ctrl+C to cancel or any key to continue...
pause > nul

echo Checking required packages...
pip install --upgrade pip
pip install customtkinter

echo.
echo Preparing database...
python "%~dp0update_database_enhanced_profile.py"

echo.
echo Creating database backup...
copy "%~dp0history.db" "%~dp0history.db.bak_integrated_app"
echo Database backup created as history.db.bak_integrated_app

echo.
echo Starting Enhanced BF Estimator with Dashboard and Settings...
echo.
python "%~dp0integrated_app.py"

echo.
echo ============================================================================
echo Thank you for using the Enhanced BF Estimator!
echo Check out the Dashboard tab to see your progress visually.
echo ============================================================================
echo.
pause
