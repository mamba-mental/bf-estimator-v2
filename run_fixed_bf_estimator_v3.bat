@echo off
echo ===================================================
echo Enhanced Body Fat Estimator v2.0 - Fix and Run Tool
echo ===================================================
echo.

echo Step 1: Creating database backup...
copy history.db history.db_backup_%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2% > nul 2>&1
echo Database backup created.
echo.

echo Step 2: Running fixes...
echo.
echo 2.1: Fixing muscle gain field in UI...
python fix_muscle_gain.py
if %ERRORLEVEL% NEQ 0 (
    echo Error fixing muscle gain field. Continuing with other fixes...
) else (
    echo Muscle gain field fix completed successfully.
)
echo.

echo 2.2: Fixing RMR calculation for reports...
python fix_report_generation.py
if %ERRORLEVEL% NEQ 0 (
    echo Error fixing RMR calculation. Continuing with other fixes...
) else (
    echo RMR calculation fix completed successfully.
)
echo.

echo 2.3: Adding email field and improving themes...
python fix_email_and_theme.py
if %ERRORLEVEL% NEQ 0 (
    echo Error adding email field and fixing themes. Continuing...
) else (
    echo Email field and theme fixes completed successfully.
)
echo.

echo 2.4: Updating user profile database schema...
python update_user_profiles.py
if %ERRORLEVEL% NEQ 0 (
    echo Error updating user profile schema. Continuing...
) else (
    echo User profile schema updated successfully.
)
echo.

echo Step 3: Starting Enhanced Body Fat Estimator v2.0...
echo.
echo Application starting...
echo If you experience any issues, restore from the backups created during the fix process.
echo Backup files have .bak extensions.
echo.
pause
echo.

start pythonw enhanced_desktop_app.py

echo.
echo Application launched!
echo.
pause
