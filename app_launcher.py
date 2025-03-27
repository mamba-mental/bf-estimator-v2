#!/usr/bin/env python
"""
BF Estimator Launcher

A unified launcher for the Body Fat Estimator application.
Supports both web mode (Flask) and desktop mode (CustomTkinter GUI).
"""

import os
import sys
import traceback
import subprocess
import importlib.util
from datetime import datetime

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

from datetime import datetime # Added for date parsing

def create_minimal_gui():
    """Create a simple GUI using customtkinter"""
    import customtkinter as ctk
    from test_data import TEST_DATA
    from main import process_test_data
    from report_generation import generate_comprehensive_report, save_report
    
    # Configure the app
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    # Create the app
    app = ctk.CTk()
    app.title("Body Fat Estimator (Basic Mode)")
    app.geometry("800x600")
    app.minsize(800, 600)
    
    # Create frames
    main_frame = ctk.CTkFrame(app)
    main_frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    # Title
    title_label = ctk.CTkLabel(
        main_frame, 
        text="Body Fat Estimator", 
        font=ctk.CTkFont(size=24, weight="bold")
    )
    title_label.pack(pady=(20, 30))
    
    # Info label
    info_label = ctk.CTkLabel(
        main_frame,
        text="This is a simplified version of the Body Fat Estimator app.\n"
             "You can generate a test report using the button below.",
        wraplength=600,
        font=ctk.CTkFont(size=14)
    )
    info_label.pack(pady=(0, 30))
    
    result_text = ctk.CTkTextbox(main_frame, width=700, height=300)
    result_text.pack(padx=20, pady=10, fill="both", expand=True)
    result_text.insert("1.0", "Click the button below to generate a test report...")
    result_text.configure(state="disabled")
    
    def generate_test_report():
        try:
            result_text.configure(state="normal")
            result_text.delete("1.0", "end")
            result_text.insert("1.0", "Generating report...\n")
            result_text.configure(state="disabled")
            app.update()
            
            # Generate report
            progression, initial_data = process_test_data(TEST_DATA)
            report_data = generate_comprehensive_report(progression, initial_data)
            saved_files = save_report(report_data, initial_data["name"], "both")
            
            # Update text
            result_text.configure(state="normal")
            result_text.delete("1.0", "end")
            result_text.insert("1.0", "Report generated successfully!\n\n") # Corrected indentation

            # Convert date strings to datetime objects if they are strings (Corrected Indentation)
            start_date_obj = report_data['start_date']
            if isinstance(start_date_obj, str):
                try:
                    # Try ISO format first (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
                    start_date_obj = datetime.fromisoformat(start_date_obj.split(' ')[0])
                except ValueError:
                    # Fallback to other common formats
                    try:
                        # Try YYYY-MM-DD
                        start_date_obj = datetime.strptime(start_date_obj, '%Y-%m-%d')
                    except ValueError:
                        try:
                            # Try MM/DD/YYYY
                            start_date_obj = datetime.strptime(start_date_obj, '%m/%d/%Y')
                        except ValueError:
                            # Add more formats or raise an error if parsing fails
                            raise ValueError(f"Could not parse start date: {start_date_obj}")

            end_date_obj = report_data['end_date']
            if isinstance(end_date_obj, str):
                try:
                    # Try ISO format first
                    end_date_obj = datetime.fromisoformat(end_date_obj.split(' ')[0])
                except ValueError:
                    # Fallback to other common formats
                    try:
                        # Try YYYY-MM-DD
                        end_date_obj = datetime.strptime(end_date_obj, '%Y-%m-%d')
                    except ValueError:
                        try:
                            # Try MM/DD/YYYY
                            end_date_obj = datetime.strptime(end_date_obj, '%m/%d/%Y')
                        except ValueError:
                            raise ValueError(f"Could not parse end date: {end_date_obj}")

            # Display summary (Corrected Indentation)
            result_text.insert("end", f"Name: {report_data['name']}\n")
            # Use the converted datetime objects for formatting
            result_text.insert("end", f"Period: {start_date_obj.strftime('%m/%d/%Y')} to {end_date_obj.strftime('%m/%d/%Y')}\n")
            result_text.insert("end", f"Age: {report_data['age']} years\n")
            result_text.insert("end", f"Initial Weight: {report_data['initial_weight']:.1f} lbs\n")
            result_text.insert("end", f"Goal Weight: {report_data['goal_weight']:.1f} lbs\n")
            result_text.insert("end", f"Initial Body Fat: {report_data['initial_body_fat']:.1f}%\n")
            result_text.insert("end", f"Goal Body Fat: {report_data['goal_body_fat']:.1f}%\n\n")
            
            result_text.insert("end", f"Files saved to:\n")
            for key, path in saved_files.items():
                if path:
                    result_text.insert("end", f"- {key.capitalize()}: {path}\n")
            
            result_text.configure(state="disabled")
            
            # Enable buttons
            if saved_files.get("pdf"):
                open_pdf_btn.configure(state="normal", command=lambda: open_file(saved_files.get("pdf")))
            if saved_files.get("markdown"):
                open_md_btn.configure(state="normal", command=lambda: open_file(saved_files.get("markdown")))
                
        except Exception as e:
            result_text.configure(state="normal")
            result_text.delete("1.0", "end")
            result_text.insert("1.0", f"Error generating report: {str(e)}\n\n")
            result_text.insert("end", traceback.format_exc())
            result_text.configure(state="disabled")
    
    def open_file(file_path):
        try:
            if sys.platform == 'win32':
                os.startfile(file_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
        except Exception as e:
            result_text.configure(state="normal")
            result_text.insert("end", f"\nError opening file: {str(e)}\n")
            result_text.configure(state="disabled")
    
    # Buttons frame
    button_frame = ctk.CTkFrame(main_frame)
    button_frame.pack(pady=20, fill="x")
    
    # Generate button  
    generate_btn = ctk.CTkButton(
        button_frame,
        text="Generate Test Report",
        font=ctk.CTkFont(size=14),
        command=generate_test_report
    )
    generate_btn.grid(row=0, column=0, padx=10, pady=10)
    
    # Open PDF button (initially disabled)
    open_pdf_btn = ctk.CTkButton(
        button_frame,
        text="Open PDF Report",
        state="disabled",
        font=ctk.CTkFont(size=14)
    )
    open_pdf_btn.grid(row=0, column=1, padx=10, pady=10)
    
    # Open MD button (initially disabled)
    open_md_btn = ctk.CTkButton(
        button_frame,
        text="Open Markdown Report",
        state="disabled",
        font=ctk.CTkFont(size=14)
    )
    open_md_btn.grid(row=0, column=2, padx=10, pady=10)
    
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)
    
    app.mainloop()
    return 0

def run_desktop_app():
    """Try to run the desktop application"""
    try:
        # Try advanced desktop app files
        desktop_files = ["desktop_app.py", "finalized_desktop_app.py", "complete_desktop_app.py"]
        
        for file in desktop_files:
            if os.path.exists(file):
                print(f"Trying to load {file}...")
                try:
                    # Try to import and use the file
                    spec = importlib.util.spec_from_file_location("desktop_module", file)
                    desktop_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(desktop_module)
                    
                    # Check if it has the required class
                    if hasattr(desktop_module, "BodyFatEstimatorApp"):
                        app_class = desktop_module.BodyFatEstimatorApp
                        app = app_class()
                        
                        # Check if it has the run method
                        if hasattr(app, "run"):
                            print(f"Starting desktop application from {file}")
                            app.run()
                            return 0
                except Exception as e:
                    print(f"Error loading {file}: {str(e)}")
                    print("Trying next option...")
        
        # If we get here, none of the desktop app files worked
        # Fall back to the minimal GUI
        print("Using basic desktop interface...")
        return create_minimal_gui()
        
    except Exception as e:
        print(f"Error launching desktop application: {str(e)}")
        print("\nDetailed error information:")
        traceback.print_exc()
        input("Press Enter to exit...")
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
    print("Welcome to Body Fat Estimator!")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
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
