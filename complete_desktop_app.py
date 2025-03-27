import os
import sys
import json
import glob
import shutil
import sqlite3
import subprocess
import traceback # Added for traceback printing in load_most_recent_data
from datetime import datetime, timedelta
import customtkinter as ctk
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Import existing functionality
from calculations import calculate_lean_mass_preservation_scores, predict_weight_loss
from report_generation import generate_comprehensive_report, save_report
from test_data import TEST_DATA
from main import process_test_data

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Constants
DB_FILE = "history.db"
RESULTS_FOLDER = "results"

# Simple message box replacement since CTkMessagebox might not be available
class SimpleMessageBox:
    @staticmethod
    def show_info(title, message):
        """Show an information message"""
        dialog = ctk.CTkToplevel()
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.grab_set()
        
        label = ctk.CTkLabel(dialog, text=message, wraplength=350)
        label.pack(pady=(30, 20))
        
        button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
        button.pack(pady=10)
        
        return dialog
    
    @staticmethod
    def show_question(title, message, option_1="Yes", option_2="No"):
        """Show a question dialog with two options"""
        dialog = ctk.CTkToplevel()
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.grab_set()
        
        # Set a class attribute to store the result
        dialog.result = None
        
        label = ctk.CTkLabel(dialog, text=message, wraplength=350)
        label.pack(pady=(30, 20))
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)
        
        def set_result(value):
            dialog.result = value
            dialog.destroy()
        
        button1 = ctk.CTkButton(button_frame, text=option_1, command=lambda: set_result(option_1))
        button1.grid(row=0, column=0, padx=10)
        
        button2 = ctk.CTkButton(button_frame, text=option_2, command=lambda: set_result(option_2))
        button2.grid(row=0, column=1, padx=10)
        
        # Wait for the dialog to be destroyed
        dialog.wait_window()
        
        return dialog.result

class BodyFatEstimatorApp:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Body Fat Estimator")
        self.app.geometry("1200x800")
        self.app.minsize(1000, 700)
        
        # Configure window
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_rowconfigure(0, weight=1)
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self.app)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create tab view
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.grid(row=0, column=0, sticky="nsew")
        
        # Create tabs
        self.tab_view.add("Input Data")
        self.tab_view.add("Weekly Progress")
        self.tab_view.add("Reports History")
        self.tab_view.add("Results")
        self.tab_view.add("About")
        
        # Configure tab grids
        for tab in ["Input Data", "Weekly Progress", "Reports History", "Results", "About"]:
            self.tab_view.tab(tab).grid_columnconfigure(0, weight=1)
            self.tab_view.tab(tab).grid_rowconfigure(0, weight=1)
        
        # Create scrollable frames for tabs
        self.input_frame = ctk.CTkScrollableFrame(self.tab_view.tab("Input Data"))
        self.input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=1)
        
        self.progress_frame = ctk.CTkFrame(self.tab_view.tab("Weekly Progress"))
        self.progress_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_rowconfigure(0, weight=0)  # Title
        self.progress_frame.grid_rowconfigure(1, weight=0)  # Input area
        self.progress_frame.grid_rowconfigure(2, weight=1)  # Chart area
        self.progress_frame.grid_rowconfigure(3, weight=1)  # History area
        
        self.history_frame = ctk.CTkFrame(self.tab_view.tab("Reports History"))
        self.history_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.history_frame.grid_rowconfigure(0, weight=0)  # Title
        self.history_frame.grid_rowconfigure(1, weight=0)  # Controls
        self.history_frame.grid_rowconfigure(2, weight=1)  # List
        
        self.results_frame = ctk.CTkScrollableFrame(self.tab_view.tab("Results"))
        self.results_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        self.about_frame = ctk.CTkFrame(self.tab_view.tab("About"))
        self.about_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Setup form variables
        self.variables = {}
        
        # Store report data
        self.current_report = None
        self.saved_files = None
        
        # Ensure database and folders exist
        self.init_database()
        
        # Create UI elements
        self.setup_input_form()
        self.setup_weekly_progress()
        self.setup_reports_history()
        self.setup_results_view()
        self.setup_about_view()
    
    def init_database(self):
        """Initialize the database for tracking history"""
        os.makedirs(RESULTS_FOLDER, exist_ok=True)
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_progress (
            id INTEGER PRIMARY KEY,
            date TEXT,
            weight REAL,
            bodyfat REAL,
            notes TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS report_history (
            id INTEGER PRIMARY KEY,
            name TEXT,
            date TEXT,
            json_path TEXT,
            md_path TEXT,
            pdf_path TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_input_form(self):
        """Create the input form with all fields"""
        # Title label
        title = ctk.CTkLabel(
            self.input_frame, 
            text="Body Fat Estimator", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 20), sticky="w")
        
        # Test data buttons
        button_frame = ctk.CTkFrame(self.input_frame)
        button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        test_data_btn = ctk.CTkButton(
            button_frame, 
            text="Fill with Test Data", 
            command=self.fill_test_data
        )
        test_data_btn.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        load_recent_btn = ctk.CTkButton(
            button_frame, 
            text="Load Most Recent Data", 
            command=self.load_most_recent_data
        )
        load_recent_btn.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # Section headers
        self.create_section_header(self.input_frame, "Personal Information", 2, 0, 2)
        self.create_section_header(self.input_frame, "Body Measurements", 10, 0, 2)
        self.create_section_header(self.input_frame, "Activity & Exercise", 16, 0, 2)
        
        # Left column fields
        left_fields = [
            ("name", "Name", "str", 3, 0),
            ("gender", "Gender", ["m", "f"], 4, 0),
            ("dob", "Date of Birth (MMDDYY)", "str", 5, 0),
            ("height_feet", "Height (feet)", "int", 6, 0),
            ("height_inches", "Height (inches)", "int", 7, 0),
            ("current_weight", "Current Weight (lbs)", "float", 11, 0),
            ("current_bf", "Current Body Fat (%)", "float", 12, 0),
            ("protein_intake", "Protein Intake (g)", "float", 13, 0),
            ("activity_level", "Activity Level", [f"{i}: {desc}" for i, desc in {
                1: "Little to no exercise",
                2: "Light exercise/sports 1-3 days/week",
                3: "Moderate exercise/sports 3-5 days/week",
                4: "Hard exercise/sports 6-7 days a week",
                5: "Very hard exercise/sports & a physical job"
            }.items()], 17, 0),
            ("job_activity", "Job Activity", [
                "sedentary: Mostly sitting (e.g., desk job)",
                "light: Light activity (e.g., teacher, salesperson)",
                "moderate: Moderate activity (e.g., construction worker)",
                "active: Very active (e.g., courier, agriculture)"
            ], 18, 0),
            ("leisure_activity", "Leisure Activity", [
                "sedentary: Little to no physical activity",
                "light: Light physical activity (e.g., walking, gardening)",
                "moderate: Moderate physical activity (e.g., hiking, dancing)",
                "active: High physical activity (e.g., sports, intense exercise)"
            ], 19, 0),
        ]
        
        # Right column fields
        right_fields = [
            ("start_date", "Start Date (MMDDYY)", "str", 3, 1),
            ("end_date", "End Date (MMDDYY)", "str", 4, 1),
            ("goal_weight", "Goal Weight (lbs)", "float", 11, 1),
            ("goal_bf", "Goal Body Fat (%)", "float", 12, 1),
            ("workout_type", "Workout Type", [
                "Bodybuilding", 
                "Cardio", 
                "General Fitness"
            ], 17, 1),
            ("workout_days", "Workout Days per Week", "int", 18, 1),
            ("experience_level", "Experience Level", [
                "Beginner (0-1 year)",
                "Novice (1-2 years)",
                "Intermediate (2-4 years)",
                "Advanced (4-10 years)",
                "Elite (10+ years)"
            ], 19, 1),
            ("resistance_training", "Resistance Training", ["y", "n"], 20, 1),
            ("is_athlete", "Athlete", ["y", "n"], 21, 1),
        ]
        
        # Create fields
        for name, label, data_type, row, col in left_fields:
            if isinstance(data_type, list):
                self.create_dropdown(name, label, data_type, row, col)
            else:
                self.create_form_field(name, label, data_type, row, col)
        
        for name, label, data_type, row, col in right_fields:
            if isinstance(data_type, list):
                self.create_dropdown(name, label, data_type, row, col)
            else:
                self.create_form_field(name, label, data_type, row, col)
        
        # Generate report button
        generate_btn = ctk.CTkButton(
            self.input_frame, 
            text="Generate Report", 
            font=ctk.CTkFont(size=16),
            height=40,
            command=self.generate_report
        )
        generate_btn.grid(row=24, column=0, columnspan=2, padx=10, pady=(20, 10))
        
        # Test report button
        test_btn = ctk.CTkButton(
            self.input_frame, 
            text="Generate Test Report", 
            command=self.generate_test_report
        )
        test_btn.grid(row=25, column=0, columnspan=2, padx=10, pady=(0, 20))

    def fill_test_data(self):
        """Fill the form with test data"""
        try:
            for key, value in TEST_DATA.items():
                if key in self.variables:
                    var = self.variables[key]
                    if isinstance(var, ctk.StringVar):
                        # Handle dropdowns - find matching option
                        if isinstance(value, (int, float)):
                            # Find option starting with the number for activity level
                            if key == "activity_level":
                                # Assuming dropdown options are stored in var._values or similar
                                options = var._values if hasattr(var, '_values') else [] 
                                matching_option = next((opt for opt in options if opt.startswith(str(value))), None)
                                if matching_option:
                                    var.set(matching_option)
                                else:
                                    var.set(str(value)) # Fallback
                            elif key in ["gender", "resistance_training", "is_athlete"]:
                                var.set(str(value).lower())
                            else:
                                var.set(str(value))
                        else:
                            var.set(str(value))
                    elif isinstance(var, ctk.DoubleVar):
                        var.set(float(value))
                    elif isinstance(var, ctk.IntVar):
                        var.set(int(value))
            SimpleMessageBox.show_info("Success", "Form filled with test data.")
        except Exception as e:
            SimpleMessageBox.show_info("Error", f"Failed to fill test data: {str(e)}")
            # traceback.print_exc() # Removed traceback for brevity in this version

    def load_most_recent_data(self):
        """Load the most recent report data into the form"""
        try:
            json_path = "last_report_data.json"
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    data = json.load(f)
                
                # Prefer 'initial_data' if it exists, otherwise use the main dict
                load_data = data.get("initial_data", data) 

                for key, value in load_data.items():
                    if key in self.variables:
                        var = self.variables[key]
                        try:
                            if isinstance(var, ctk.StringVar):
                                # Handle dropdowns - find matching option if possible
                                if key == "activity_level" and isinstance(value, (int, float)):
                                    options = var._values if hasattr(var, '_values') else []
                                    matching_option = next((opt for opt in options if opt.startswith(str(value))), None)
                                    if matching_option:
                                        var.set(matching_option)
                                    else:
                                        var.set(str(value)) # Fallback
                                elif key in ["gender", "resistance_training", "is_athlete"]:
                                     var.set(str(value).lower())
                                else:
                                    var.set(str(value))
                            elif isinstance(var, ctk.DoubleVar):
                                var.set(float(value))
                            elif isinstance(var, ctk.IntVar):
                                var.set(int(value))
                        except (ValueError, TypeError) as e:
                            print(f"Warning: Could not set recent value for {key}: {value}. Error: {e}")
                            if isinstance(var, (ctk.DoubleVar, ctk.IntVar)):
                                var.set(0)
                            else:
                                var.set("")
                SimpleMessageBox.show_info("Success", "Loaded most recent data.")
            else:
                SimpleMessageBox.show_info("Info", f"No recent data file found ({json_path}).")
        except Exception as e:
            SimpleMessageBox.show_info("Error", f"Failed to load recent data: {str(e)}")
            traceback.print_exc()

    def get_form_data(self):
        """Retrieve and validate data from the input form"""
        data = {}
        errors = []
        
        for name, var in self.variables.items():
            value = var.get()
            
            # Basic validation (can be expanded)
            if not value and name not in ["protein_intake", "current_bf", "goal_bf"]: # Allow some fields to be optional/zero
                 # Skip date validation here, handle later
                if name not in ["start_date", "end_date", "dob"]:
                    errors.append(f"Field '{name.replace('_', ' ').title()}' cannot be empty.")
                    continue # Skip further processing for this field

            # Type conversion and specific validation
            try:
                if name in ["height_feet", "height_inches", "workout_days"]:
                    data[name] = int(value) if value else 0
                elif name in ["current_weight", "current_bf", "goal_weight", "goal_bf", "protein_intake"]:
                    data[name] = float(value) if value else 0.0
                elif name in ["gender", "resistance_training", "is_athlete"]:
                    data[name] = str(value).lower() if value else None
                elif name == "activity_level":
                    # Extract the number from "X: Description"
                    data[name] = int(str(value).split(":")[0]) if value else 1
                elif name in ["job_activity", "leisure_activity", "experience_level"]:
                     # Extract the key part before ":" if present
                    data[name] = str(value).split(":")[0] if value else None
                elif name in ["dob", "start_date", "end_date"]:
                     # Basic format check, more robust validation can be added
                    if value:
                        try:
                            # Attempt to parse MMDDYY
                            datetime.strptime(str(value), "%m%d%y")
                            data[name] = str(value)
                        except ValueError:
                            errors.append(f"Invalid date format for {name.replace('_', ' ').title()}. Use MMDDYY.")
                    else:
                         errors.append(f"Date field '{name.replace('_', ' ').title()}' cannot be empty.")
                else:
                    data[name] = str(value) # Default to string
            except ValueError:
                errors.append(f"Invalid value for {name.replace('_', ' ').title()}. Expected numeric.")
            except Exception as e:
                 errors.append(f"Error processing field {name}: {e}")

        if errors:
            SimpleMessageBox.show_info("Input Error", "\n".join(errors))
            return None
            
        # Combine height
        data["height"] = data.get("height_feet", 0) * 12 + data.get("height_inches", 0)
        
        return data

    def generate_report(self):
        """Generate report from form data"""
        initial_data = self.get_form_data()
        if not initial_data:
            return # Stop if validation failed

        try:
            # Simulate progression data if needed, or use weekly progress tab data
            # For now, assume a simple case or use test data structure
            # Ideally, fetch from self.load_progress_data() results
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT date, weight, bodyfat FROM weekly_progress ORDER BY date ASC")
            progression_rows = cursor.fetchall()
            conn.close()

            progression_data = []
            if progression_rows:
                 # Convert DB rows to the expected dictionary format
                 for date_str, weight, bf in progression_rows:
                     try:
                         date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                         progression_data.append({
                             "date": date_obj.strftime("%m/%d/%Y"), # Match expected format if needed by calculations
                             "weight": weight,
                             "bodyfat": bf
                         })
                     except ValueError:
                         print(f"Skipping invalid date in progress data: {date_str}")
            else:
                 # Fallback if no progress data: use current values as single point
                 progression_data = [{
                     "date": datetime.strptime(initial_data['start_date'], "%m%d%y").strftime("%m/%d/%Y"),
                     "weight": initial_data['current_weight'],
                     "bodyfat": initial_data['current_bf']
                 }]


            # Generate the report data using imported functions
            self.current_report = generate_comprehensive_report(progression_data, initial_data)
            
            # Save the report files
            self.saved_files = save_report(self.current_report, initial_data["name"], "both") # Save PDF and MD
            
            # Save data used for this report to last_report_data.json
            try:
                 # Save the raw input data for easier reloading
                 with open("last_report_data.json", "w") as f:
                     json.dump(initial_data, f, indent=4)
            except Exception as e:
                 print(f"Warning: Could not save last report data: {e}")

            # Add to report history database
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO report_history (name, date, json_path, md_path, pdf_path) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        self.current_report.get("name", "Unknown"),
                        datetime.now().strftime("%Y-%m-%d"),
                        self.saved_files.get("json"), # save_report now returns json path too
                        self.saved_files.get("markdown"),
                        self.saved_files.get("pdf"),
                    ),
                )
                conn.commit()
                conn.close()
                self.load_report_history() # Refresh history tab
            except Exception as e:
                print(f"Error saving report to history DB: {e}")


            # Display results
            self.display_results()
            self.tab_view.set("Results") # Switch to results tab
            SimpleMessageBox.show_info("Success", "Report generated successfully!")

        except Exception as e:
            SimpleMessageBox.show_info("Error", f"Failed to generate report: {str(e)}")
            traceback.print_exc()

    def generate_test_report(self):
        """Generate a report using test data"""
        try:
            # Process test data using the imported function
            progression, initial_data = process_test_data(TEST_DATA)
            
            # Generate the report data
            self.current_report = generate_comprehensive_report(progression, initial_data)
            
            # Save the report files
            self.saved_files = save_report(self.current_report, initial_data["name"], "both")

             # Save test data used for this report to last_report_data.json
            try:
                 with open("last_report_data.json", "w") as f:
                     # Save the initial_data part derived from TEST_DATA
                     json.dump(initial_data, f, indent=4)
            except Exception as e:
                 print(f"Warning: Could not save last test report data: {e}")

            # Add to report history database
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO report_history (name, date, json_path, md_path, pdf_path) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        self.current_report.get("name", "Test Report"),
                        datetime.now().strftime("%Y-%m-%d"),
                        self.saved_files.get("json"), 
                        self.saved_files.get("markdown"),
                        self.saved_files.get("pdf"),
                    ),
                )
                conn.commit()
                conn.close()
                self.load_report_history() # Refresh history tab
            except Exception as e:
                print(f"Error saving test report to history DB: {e}")

            # Display results
            self.display_results()
            self.tab_view.set("Results") # Switch to results tab
            SimpleMessageBox.show_info("Success", "Test report generated successfully!")

        except Exception as e:
            SimpleMessageBox.show_info("Error", f"Failed to generate test report: {str(e)}")
            traceback.print_exc()

    def create_section_header(self, parent, text, row, col, colspan=1):
        """Create a section header with title and separator"""
        # Title
        header = ctk.CTkLabel(
            parent, 
            text=text, 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.grid(row=row, column=col, columnspan=colspan, padx=10, pady=(15, 5), sticky="w")
        
        # Separator
        separator = ctk.CTkFrame(parent, height=2, fg_color="gray70")
        separator.grid(row=row+1, column=col, columnspan=colspan, padx=10, pady=(0, 10), sticky="ew")
    
    def create_form_field(self, name, label, data_type, row, col):
        """Create a form field with label and entry"""
        frame = ctk.CTkFrame(self.input_frame)
        frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        
        # Label
        lbl = ctk.CTkLabel(frame, text=label, width=150, anchor="w")
        lbl.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Create variable of appropriate type
        if data_type == "float":
            var = ctk.DoubleVar()
        elif data_type == "int":
            var = ctk.IntVar()
        else:
            var = ctk.StringVar()
        
        # Entry field
        entry = ctk.CTkEntry(frame, textvariable=var, width=200)
        entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # Store variable
        self.variables[name] = var
    
    def create_dropdown(self, name, label, options, row, col):
        """Create a dropdown field with label"""
        frame = ctk.CTkFrame(self.input_frame)
        frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        
        # Label
        lbl = ctk.CTkLabel(frame, text=label, width=150, anchor="w")
        lbl.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Variable
        var = ctk.StringVar()
        
        # Dropdown
        dropdown = ctk.CTkOptionMenu(frame, variable=var, values=options)
        dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        dropdown.set(options[0])  # Set default value
        
        # Store variable
        self.variables[name] = var
    
    def setup_weekly_progress(self):
        """Setup the weekly progress tracking view"""
        # Title
        title = ctk.CTkLabel(
            self.progress_frame, 
            text="Weekly Progress Tracking", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Input area
        input_container = ctk.CTkFrame(self.progress_frame)
        input_container.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        input_container.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Date input
        date_label = ctk.CTkLabel(input_container, text="Date:")
        date_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        self.progress_date_var = ctk.StringVar()
        today = datetime.now().strftime("%m/%d/%Y")
        self.progress_date_var.set(today)
        date_entry = ctk.CTkEntry(input_container, textvariable=self.progress_date_var, width=120)
        date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Weight input
        weight_label = ctk.CTkLabel(input_container, text="Weight (lbs):")
        weight_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        self.progress_weight_var = ctk.DoubleVar()
        weight_entry = ctk.CTkEntry(input_container, textvariable=self.progress_weight_var, width=80)
        weight_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Body fat input
        bf_label = ctk.CTkLabel(input_container, text="Body Fat (%):")
        bf_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        
        self.progress_bf_var = ctk.DoubleVar()
        bf_entry = ctk.CTkEntry(input_container, textvariable=self.progress_bf_var, width=80)
        bf_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Notes input
        notes_label = ctk.CTkLabel(input_container, text="Notes:")
        notes_label.grid(row=1, column=2, padx=5, pady=5, sticky="e")
        
        self.progress_notes_var = ctk.StringVar()
        notes_entry = ctk.CTkEntry(input_container, textvariable=self.progress_notes_var, width=200)
        notes_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # Add button
        add_button = ctk.CTkButton(input_container, text="Add Entry", command=self.add_progress_entry)
        add_button.grid(row=0, column=4, rowspan=2, padx=10, pady=10)
        
        # Create frames for charts and history table
        self.chart_frame = ctk.CTkFrame(self.progress_frame)
        self.chart_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(1, weight=1)
        self.chart_frame.grid_rowconfigure(0, weight=0)  # Title
        self.chart_frame.grid_rowconfigure(1, weight=1)  # Chart
        
        # Chart titles
        weight_title = ctk.CTkLabel(
            self.chart_frame, 
            text="Weight Progress", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        weight_title.grid(row=0, column=0, padx=10, pady=5, sticky="n")
        
        bf_title = ctk.CTkLabel(
            self.chart_frame, 
            text="Body Fat Progress", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        bf_title.grid(row=0, column=1, padx=10, pady=5, sticky="n")
        
        # Add chart frames
        self.weight_chart_frame = ctk.CTkFrame(self.chart_frame)
        self.weight_chart_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        self.bf_chart_frame = ctk.CTkFrame(self.chart_frame)
        self.bf_chart_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        
        # History table
        history_container = ctk.CTkFrame(self.progress_frame)
        history_container.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        history_container.grid_columnconfigure(0, weight=1)
        history_container.grid_rowconfigure(0, weight=0)  # Title
        history_container.grid_rowconfigure(1, weight=1)  # Table
        
        # History table title
        history_title = ctk.CTkLabel(
            history_container, 
            text="Progress History", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        history_title.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Create scrollable frame for history
        self.history_table_frame = ctk.CTkScrollableFrame(history_container)
        self.history_table_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.history_table_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Add headers
        header_font = ctk.CTkFont(weight="bold")
        ctk.CTkLabel(self.history_table_frame, text="Date", font=header_font).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.history_table_frame, text="Weight (lbs)", font=header_font).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.history_table_frame, text="Body Fat (%)", font=header_font).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.history_table_frame, text="Notes", font=header_font).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.history_table_frame, text="Actions", font=header_font).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        
        # Load progress data
        self.load_progress_data()
    
    def add_progress_entry(self):
        """Add a new weekly progress entry"""
        try:
            # Validate and parse date
            date_str = self.progress_date_var.get()
            try:
                if "/" in date_str:
                    date = datetime.strptime(date_str, "%m/%d/%Y")
                else:
                    date = datetime.strptime(date_str, "%m%d%y")
                date_str = date.strftime("%Y-%m-%d")  # Standardize date format for storage
            except ValueError:
                SimpleMessageBox.show_info("Invalid Date", "Please enter a valid date in MM/DD/YYYY format.")
                return
                
            # Get weight and bodyfat
            try:
                weight = float(self.progress_weight_var.get())
                bodyfat = float(self.progress_bf_var.get())
            except ValueError:
                SimpleMessageBox.show_info("Invalid Data", "Weight and Body Fat must be numeric values.")
                return
                
            # Get notes
            notes = self.progress_notes_var.get()
            
            # Add to database
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO weekly_progress (date, weight, bodyfat, notes) VALUES (?, ?, ?, ?)",
                (date_str, weight, bodyfat, notes)
            )
            conn.commit()
            conn.close()
            
            # Clear the input fields
            self.progress_date_var.set(datetime.now().strftime("%m/%d/%Y"))
            self.progress_weight_var.set(0.0)
            self.progress_bf_var.set(0.0)
            self.progress_notes_var.set("")
            
            # Reload progress data
            self.load_progress_data()
            
            # Show success message
            SimpleMessageBox.show_info("Success", "Progress entry added successfully!")
            
        except Exception as e:
            SimpleMessageBox.show_info("Error", f"Failed to add progress entry: {str(e)}")
    
    def load_progress_data(self):
        """Load and display progress data from database"""
        # Clear existing data
        for widget in self.history_table_frame.winfo_children():
            if int(widget.grid_info()["row"]) > 0:  # Skip headers
                widget.destroy()
        
        # Get data from database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, weight, bodyfat, notes FROM weekly_progress ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()
        
        # Display data in table
        for i, (entry_id, date, weight, bodyfat, notes) in enumerate(rows):
            row_num = i + 1  # +1 for header row
            
            # Format date for display
            try:
                display_date = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
            except ValueError:
                display_date = date
                
            # Add data to table
            ctk.CTkLabel(self.history_table_frame, text=display_date).grid(row=row_num, column=0, padx=5, pady=2, sticky="w")
            ctk.CTkLabel(self.history_table_frame, text=f"{weight:.1f}").grid(row=row_num, column=1, padx=5, pady=2, sticky="w")
            ctk.CTkLabel(self.history_table_frame, text=f"{bodyfat:.1f}").grid(row=row_num, column=2, padx=5, pady=2, sticky="w")
            ctk.CTkLabel(self.history_table_frame, text=notes).grid(row=row_num, column=3, padx=5, pady=2, sticky="w")
            
            # Action button
            delete_btn = ctk.CTkButton(
                self.history_table_frame, 
                text="Delete", 
                width=80,
                fg_color="darkred",
                command=lambda id=entry_id: self.delete_progress_entry(id)
            )
            delete_btn.grid(row=row_num, column=4, padx=5, pady=2)
        
        # Update charts
        self.update_progress_charts(rows)

    def update_progress_charts(self, data):
        """Update the progress charts with the given data"""
        # Clear previous charts
        for widget in self.weight_chart_frame.winfo_children():
            widget.destroy()
        for widget in self.bf_chart_frame.winfo_children():
            widget.destroy()
            
        # Skip if no data
        if not data:
            no_data_label = ctk.CTkLabel(
                self.weight_chart_frame,
                text="No progress data available\nAdd entries to see charts",
                wraplength=200,
                justify="center"
            )
            no_data_label.place(relx=0.5, rely=0.5, anchor="center")
            
            no_data_label2 = ctk.CTkLabel(
                self.bf_chart_frame,
                text="No progress data available\nAdd entries to see charts",
                wraplength=200,
                justify="center"
            )
            no_data_label2.place(relx=0.5, rely=0.5, anchor="center")
            return
            
        # Format data for plotting
        dates = []
        weights = []
        bodyfats = []
        
        # Sort by date
        sorted_data = sorted(data, key=lambda x: x[1])  # Sort by date
        
        for _, date_str, weight, bodyfat, _ in sorted_data:
            # Convert date string to datetime
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                dates.append(date)
                weights.append(weight)
                bodyfats.append(bodyfat)
            except ValueError:
                continue
        
        # Skip if not enough data after filtering
        if len(dates) < 2:
            no_data_label = ctk.CTk
