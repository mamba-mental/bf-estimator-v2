# run.py
import sys
import os
import warnings
import contextlib

os.environ['GIO_USE_VFS'] = 'local'
os.environ['GSETTINGS_BACKEND'] = 'memory'

# Suppress all warnings
warnings.filterwarnings("ignore", category=UserWarning, module="gi.repository")

# Suppress GLib-GIO warnings
os.environ['G_MESSAGES_DEBUG'] = 'none'
os.environ['G_ENABLE_DIAGNOSTIC'] = '0'

# Disable Flask debug mode
os.environ['FLASK_DEBUG'] = '0'

# Suppress UWP app warnings
os.environ['SUPPRESS_UWP_WARNINGS'] = '1'

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
    print("Starting BF Estimator...")
    
    # Check if mode is provided as command line argument
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "web":
            print("Initializing web interface...")
            run_web_mode()
        elif mode == "terminal":
            use_test = input("Use test data? (y/n): ").lower() == 'y'
            run_terminal_mode(use_test_data=use_test)
        else:
            print("Invalid mode. Please use 'web' or 'terminal'.")
            sys.exit(1)
    else:
        # Default to web mode if no argument provided
        print("Initializing web interface...")
        run_web_mode()
