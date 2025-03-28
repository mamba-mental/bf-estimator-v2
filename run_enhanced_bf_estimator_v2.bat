@echo off
echo Starting Enhanced Body Fat Estimator v2.0...

REM Install any required packages if they're missing
pip install -q customtkinter Pillow SpeechRecognition pyaudio matplotlib numpy

REM Run the enhanced application
python enhanced_desktop_app.py

echo Application closed.
pause
