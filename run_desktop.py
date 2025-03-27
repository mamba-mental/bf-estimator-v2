#!/usr/bin/env python
"""
Launcher script for Body Fat Estimator Application

This script provides a simple way to launch the Body Fat Estimator application
in either web mode (Flask) or desktop mode (CustomTkinter).
"""

import os
import sys
import traceback
import subprocess
import importlib.util

def check_dependencies(mode):
    """Check if all required dependencies are installed based on mode"""
    missing_deps = []
    
    # Common dependencies
    try:
        import PIL
        import matplotlib
    except ImportError as e:
        missing_deps.append(str(e).split("'")[1])
        
    # Mode-specific dependencies
    if mode == "desktop":
        try:
            import customtkinter
        except ImportError:
            missing_deps.append("customtkinter")
    elif mode == "web":
        try:
            import flask
            import werkzeug
        except ImportError as e:
            missing_deps.append(str(e).split("'")[1])
    
    if missing_deps:
        print("Missing dependencies:", ", ".join(missing_deps))
        if mode == "desktop":
            print("\nPlease install them with:")
            print("pip install customtkinter pillow matplotlib")
        else:
            print("\nPlease install them with:")
            print("pip install flask pillow matplotlib")
        return False
    
    return True

def get_user_choice():
    """Ask the user which mode they want to run"""
    print("\nBody Fat Estimator Launcher")
    print("===========================")
    print("1: Desktop Application (CustomTkinter GUI)")
    print("2: Web Application (Flask web server)")
    
    while True:
        choice = input("\nEnter your choice (1-2): ").strip()
        if choice == "1":
            return "desktop"
        elif choice == "2":
            return "web"
        else:
            print("Invalid choice. Please enter 1 or 2.")

def run_desktop_app():
    """Run the desktop application using CustomTkinter"""
    try:
        # Try to import the desktop_app module directly
        if os.path.exists("desktop_app.py"):
            # Check if desktop_app.py has a valid class ready to use
            try:
                import desktop_app
                if hasattr(desktop_app, "BodyFatEstimatorApp"):
                    print("Starting desktop application...")
                    app = desktop_app.BodyFatEstimatorApp()
                    app.run()
                    return 0
            except (ImportError, AttributeError):
                pass
            
        # If that fails, try the complete_desktop_app.py
        if os.path.exists("complete_desktop_app.py"):
            print("Using complete_desktop_app.py instead...")
            import complete_desktop_app
            if hasattr(complete_desktop_app, "BodyFatEstimatorApp"):
                app = complete_desktop_app.BodyFatEstimatorApp()
                app.run()
                return 0
                
        # As a last resort, create a simple app using the existing code
        print("Creating basic desktop interface...")
        import customtkinter as ctk
        from main import process_test_data
        from test_data import TEST_DATA
        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        app = ctk.CTk()
        app.title("Body Fat Estimator")
        app.geometry("800x600")
        
        title = ctk.CTkLabel(app, text="Body Fat Estimator", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        
        btn = ctk.CTkButton(
            app, 
            text="Generate Test Report", 
            command=lambda: process_test_data(TEST_DATA)
        )
        btn.pack(pady=20)
        
        app.mainloop()
        return 0
    
    except Exception as e:
        print(f"Error launching desktop application: {str(e)}")
        print("\nDetailed error information:")
        traceback.print_exc()
        return 1

def run_web_app():
    """Run the web application using Flask"""
    try:
        # Use subprocess to start the web application
        print("Starting web application...")
        process = subprocess.Popen(
            ["python", "run.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send "web" to the input prompt
        stdout, stderr = process.communicate(input="web\n")
        
        # Check for errors
        if process.returncode != 0:
            print("Error starting web application:")
            print(stderr)
            return 1
            
        print("Web application started successfully!")
        print("Navigate to http://127.0.0.1:5000 in your browser.")
        
        # Keep the process running
        process.wait()
        return 0
    
    except Exception as e:
        print(f"Error launching web application: {str(e)}")
        print("\nDetailed error information:")
        traceback.print_exc()
        return 1

def main():
    """Main entry point for the application launcher"""
    print("Welcome to Body Fat Estimator!\n")
    
    # Get user's choice for application mode
    mode = get_user_choice()
    
    # Check if dependencies are installed
    if not check_dependencies(mode):
        input("Press Enter to exit...")
        return 1
    
    # Run the appropriate application
    if mode == "desktop":
        return run_desktop_app()
    else:
        return run_web_app()

if __name__ == "__main__":
    sys.exit(main())
