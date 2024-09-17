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



@contextlib.contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(os.devnull, 'w') as fnull:
        with contextlib.redirect_stderr(fnull) as err, contextlib.redirect_stdout(fnull) as out:
            yield (err, out)

def run_terminal_mode(use_test_data=False):
    from main import run_user_interaction, generate_comprehensive_report
    from report_generation import print_summary, save_report
    
    progression, initial_data = run_user_interaction(use_test_data=use_test_data)
    print_summary(progression, initial_data)
    
    save_option = input("\nDo you want to save the detailed report? (y/n): ").lower()
    if save_option == 'y':
        save_format = input("Choose the format to save (markdown/pdf/both): ").lower()
        if save_format in ['markdown', 'pdf', 'both']:
            report_data = generate_comprehensive_report(progression, initial_data)
            save_report(report_data, initial_data.get('name', 'User'), save_format)
        else:
            print("Invalid format choice. Report will not be saved.")
    else:
        print("Report will not be saved.")

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