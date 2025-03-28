@echo off
echo ===================================================
echo Enhanced Body Fat Estimator v2.0 - FINAL FIX SCRIPT
echo ===================================================
echo.
echo This script applies ALL fixes in the correct order
echo.

echo Step 1: Creating database backup...
copy history.db history.db_backup_%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2% > nul 2>&1
echo Database backup created.
echo.

echo Step 2: Fixing database schema...
echo 2.1: Running schema updates...
python update_database_schema_v3.py
echo 2.2: Adding email column to user profiles...
python update_user_profiles.py
echo.

echo Step 3: Fixing application code...
echo 3.1: Fixing muscle gain field...
python fix_muscle_gain.py
echo 3.2: Fixing RMR calculation...
python fix_report_generation.py
echo 3.3: Adding email field and fixing themes...
python fix_email_and_theme.py
echo 3.4: Applying final fixes for report generation and UI...
python fix_final_issues.py
echo.

echo Step 4: Starting Enhanced Body Fat Estimator v2.0...
echo.
echo Application starting with all fixes applied.
echo If you experience any issues, restore from the backups created during the fix process.
echo Backup files have .bak extensions (multiple backups were created).
echo.
pause
echo.

start pythonw enhanced_desktop_app.py

echo.
echo Application launched! Please check BUGFIX_DOCUMENTATION.md for details about all fixes.
echo.
pause
