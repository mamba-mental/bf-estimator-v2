@echo off
cd /d "%~dp0"

echo Updating pip...
python -m pip install --upgrade pip --user --quiet

echo Installing dependencies...
python -m pip install --user numpy pandas matplotlib Flask Flask-WTF Flask-Session Flask-Login WTForms Jinja2 WeasyPrint pdfkit mistune lxml cairocffi tinycss2 cssselect2 werkzeug --quiet
if errorlevel 1 (
    echo Error installing main dependencies. Please make sure Python is installed correctly.
    pause
    exit /b 1
)

echo Installing test dependencies...
python -m pip install --user pytest --quiet
if errorlevel 1 (
    echo Note: Test dependencies could not be installed. This won't affect normal program operation.
)

echo.
echo BF Estimator
echo ============
echo 1. Web Interface
echo 2. Command Line Interface
echo.
set /p choice="Enter your choice (1 or 2): "

echo Cleaning up old session files...
if exist "flask_session" rmdir /s /q "flask_session"

if "%choice%"=="1" (
    echo Starting web interface...
    mkdir flask_session
    start http://127.0.0.1:5000
    python run.py web
) else if "%choice%"=="2" (
    echo Starting terminal interface...
    python run.py terminal
    pause
) else (
    echo Invalid choice. Please run again and select 1 or 2.
    pause
)
