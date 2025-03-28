@echo off
echo Running RMR Calculator Tests...
python test_rmr_calculation.py
echo.
echo Press any key to run interactive mode
pause
python test_rmr_calculation.py --manual
pause
