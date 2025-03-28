@echo off
echo Starting Enhanced Body Fat Estimator...

rem Update database schema for enhanced features
python update_database.py

rem Start the enhanced Body Fat Estimator v2.0
echo Starting Enhanced Body Fat Estimator v2.0
python simple_enhanced_app.py

pause
