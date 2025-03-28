@echo off
echo Running Comprehensive Tests for Enhanced Profile System...
python test_enhanced_profile_system.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================
    echo All tests passed successfully!
    echo Enhanced profile system is working correctly.
    echo ======================================
) else (
    echo.
    echo ======================================
    echo Some tests failed. Please review the output above.
    echo ======================================
)
pause
