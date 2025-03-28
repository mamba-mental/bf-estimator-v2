@echo off
echo Running Enhanced Profile System Tests...
python test_enhanced_profile.py
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
