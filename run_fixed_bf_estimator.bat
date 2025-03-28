@echo off
echo Body Fat Estimator - Enhanced Edition (with Database Fix)
echo =========================================================
echo.
echo Step 1: Fixing the database...
echo.
python fix_database.py

echo.
echo Step 2: Starting the application...
echo.
python run_enhanced_app.py

echo.
echo Application closed.
pause
