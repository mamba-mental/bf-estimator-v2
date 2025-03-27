# run.py
import sys
import os
import warnings
import contextlib

# Set environment variables for WeasyPrint
os.environ['WEASYPRINT_VERBOSE'] = '1'  # Enable verbose logging
os.environ['GDK_BACKEND'] = 'cairo'  # Use Cairo backend
os.environ['GIO_USE_VFS'] = 'local'
os.environ['GSETTINGS_BACKEND'] = 'memory'
os.environ['G_MESSAGES_DEBUG'] = 'none'
os.environ['G_DEBUG'] = 'fatal-warnings'

# Suppress all warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Disable Flask debug mode
os.environ['FLASK_DEBUG'] = '0'

# Add these lines to suppress more warnings and debug messages
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('matplotlib').setLevel(logging.ERROR)

@contextlib.contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(os.devnull, 'w') as fnull:
        with contextlib.redirect_stderr(fnull) as err, contextlib.redirect_stdout(fnull) as out:
            yield (err, out)

def run_terminal_mode(use_test_data=False):
    from main import run_user_interaction, print_summary
    progression, initial_data = run_user_interaction(use_test_data=use_test_data)
    saved_files = print_summary(progression, initial_data)
    # No extra prompting here

def run_web_mode():
    from app import app
    print("Starting web server...")
    print("Navigate to http://127.0.0.1:5000 in your web browser.")
    print("Press CTRL+C to stop the server.")
    with suppress_stdout_stderr():
        app.run(debug=False, host='127.0.0.1', port=5000)

if __name__ == "__main__":
    mode = input("Choose mode (terminal/web): ").lower()

    if mode == "terminal":
        use_test = input("Use test data? (y/n): ").lower() == 'y'
        run_terminal_mode(use_test_data=use_test)
    elif mode == "web":
        run_web_mode()
    else:
        print("Invalid mode. Please choose 'terminal' or 'web'.")
        sys.exit(1)
