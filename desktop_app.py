import os
import sys
import json
import glob
import shutil
import sqlite3
import subprocess
import traceback 
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

# Theme names
STANDARD_THEME = "blue"
MIDNIGHT_THEME_NAME = "midnight"

# Midnight OLED theme definition using the proper CustomTkinter theme format
MIDNIGHT_THEME = {
  "CTk": {
    "fg_color": ["gray95", "#000000"]
  },
  "CTkToplevel": {
    "fg_color": ["gray95", "#000000"]
  },
  "CTkFrame": {
    "corner_radius": 6,
    "border_width": 0,
    "fg_color": ["gray90", "#0a0a0a"],
    "top_fg_color": ["gray85", "#101010"],
    "border_color": ["gray65", "#181818"]
  },
  "CTkButton": {
    "corner_radius": 6,
    "border_width": 0,
    "fg_color": ["#3a7ebf", "#101010"],
    "hover_color": ["#325882", "#0a0a0a"],
    "border_color": ["#3E454A", "#141414"],
    "text_color": ["#DCE4EE", "#DCE4EE"],
    "text_color_disabled": ["gray74", "#6B6B6B"]
  },
  "CTkLabel": {
    "corner_radius": 0,
    "fg_color": "transparent",
    "text_color": ["gray14", "#DCE4EE"]
  },
  "CTkEntry": {
    "corner_radius": 6,
    "border_width": 2,
    "fg_color": ["#F9F9FA", "#060606"],
    "border_color": ["#979DA2", "#151515"],
    "text_color": ["gray14", "#DCE4EE"],
    "placeholder_text_color": ["gray52", "#6B6B6B"]
  },
  "CTkCheckBox": {
    "corner_radius": 6,
    "border_width": 3,
    "fg_color": ["#3a7ebf", "#101010"],
    "border_color": ["#3E454A", "#151515"],
    "hover_color": ["#325882", "#0a0a0a"],
    "checkmark_color": ["#DCE4EE", "#DCE4EE"],
    "text_color": ["gray14", "#DCE4EE"],
    "text_color_disabled": ["gray60", "#6B6B6B"]
  },
  "CTkSwitch": {
    "corner_radius": 1000,
    "border_width": 3,
    "button_length": 0,
    "fg_color": ["#939BA2", "#3A3A3A"],
    "progress_color": ["#3a7ebf", "#101010"],
    "button_color": ["gray36", "#151515"],
    "button_hover_color": ["gray20", "#202020"],
    "text_color": ["gray14", "#DCE4EE"],
    "text_color_disabled": ["gray60", "#6B6B6B"]
  },
  "CTkRadioButton": {
    "corner_radius": 1000,
    "border_width_checked": 6,
    "border_width_unchecked": 3,
    "fg_color": ["#3a7ebf", "#101010"],
    "border_color": ["#3E454A", "#151515"],
    "hover_color": ["#325882", "#0a0a0a"],
    "text_color": ["gray14", "#DCE4EE"],
    "text_color_disabled": ["gray60", "#6B6B6B"]
  },
  "CTkProgressBar": {
    "corner_radius": 1000,
    "border_width": 0,
    "fg_color": ["#939BA2", "#252525"],
    "progress_color": ["#3a7ebf", "#101010"],
    "border_color": ["gray", "#151515"]
  },
  "CTkSlider": {
    "corner_radius": 1000,
    "button_corner_radius": 1000,
    "border_width": 6,
    "button_length": 0,
    "fg_color": ["#939BA2", "#252525"],
    "progress_color": ["gray40", "#151515"],
    "button_color": ["#3a7ebf", "#101010"],
    "button_hover_color": ["#325882", "#0a0a0a"]
  },
  "CTkOptionMenu": {
    "corner_radius": 6,
    "fg_color": ["#3a7ebf", "#101010"],
    "button_color": ["#325882", "#0a0a0a"],
    "button_hover_color": ["#234567", "#050505"],
    "text_color": ["#DCE4EE", "#DCE4EE"],
    "text_color_disabled": ["gray74", "#6B6B6B"]
  },
  "CTkComboBox": {
    "corner_radius": 6,
    "border_width": 2,
    "fg_color": ["#F9F9FA", "#060606"],
    "border_color": ["#979DA2", "#151515"],
    "button_color": ["#979DA2", "#151515"],
    "button_hover_color": ["#6E7174", "#202020"],
    "text_color": ["gray14", "#DCE4EE"],
    "text_color_disabled": ["gray50", "#6B6B6B"]
  },
  "CTkScrollbar": {
    "corner_radius": 1000,
    "border_spacing": 4,
    "fg_color": "transparent",
    "button_color": ["gray55", "#151515"],
    "button_hover_color": ["gray40", "#222222"]
  },
  "CTkSegmentedButton": {
    "corner_radius": 6,
    "border_width": 2,
    "fg_color": ["#979DA2", "#151515"],
    "selected_color": ["#3a7ebf", "#101010"],
    "selected_hover_color": ["#325882", "#0a0a0a"],
    "unselected_color": ["#979DA2", "#151515"],
    "unselected_hover_color": ["gray70", "#222222"],
    "text_color": ["#DCE4EE", "#DCE4EE"],
    "text_color_disabled": ["gray74", "#6B6B6B"]
  },
  "CTkTextbox": {
    "corner_radius": 6,
    "border_width": 0,
    "fg_color": ["gray100", "#060606"],
    "border_color": ["#979DA2", "#151515"],
    "text_color": ["gray14", "#DCE4EE"],
    "scrollbar_button_color": ["gray55", "#151515"],
    "scrollbar_button_hover_color": ["gray40", "#222222"]
  },
  "CTkScrollableFrame": {
    "label_fg_color": ["gray80", "#0a0a0a"]
  },
  "DropdownMenu": {
    "fg_color": ["gray90", "#0a0a0a"],
    "hover_color": ["gray75", "#151515"],
    "text_color": ["gray14", "#DCE4EE"]
  },
  "CTkFont": {
    "macOS": {
      "family": "SF Display",
      "size": 13,
      "weight": "normal"
    },
    "Windows": {
      "family": "Roboto",
      "size": 13,
      "weight": "normal"
    },
    "Linux": {
      "family": "Roboto",
      "size": 13,
      "weight": "normal"
    }
  }
}

# Set initial appearance mode and default color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme(STANDARD_THEME)

# Constants
DB_FILE = "history.db"
RESULTS_FOLDER = "results"

class SimpleMessageBox:
    @staticmethod
    def show_info(title, message):
        """Show an information message"""
        dialog = ctk.CTkToplevel()
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.grab_set()
        dialog.attributes("-topmost", True) # Keep on top
        
        label = ctk.CTkLabel(dialog, text=message, wraplength=350)
        label.pack(pady=(30, 20), padx=20, fill="both", expand=True)
        
        button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy, width=100)
        button.pack(pady=10)
        
        # Center the dialog
        dialog.update_idletasks()
        x = dialog.winfo_screenwidth() // 2 - dialog.winfo_width() // 2
        y = dialog.winfo_screenheight() // 2 - dialog.winfo_height() // 2
        dialog.geometry(f"+{x}+{y}")
        
        dialog.wait_window() # Wait until destroyed
        return dialog
    
    @staticmethod
    def show_question(title, message, option_1="Yes", option_2="No"):
        """Show a question dialog with two options"""
        dialog = ctk.CTkToplevel()
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.grab_set()
        dialog.attributes("-topmost", True) # Keep on top
        
        # Set a class attribute to store the result
        dialog.result = None
        
        label = ctk.CTkLabel(dialog, text=message, wraplength=350)
        label.pack(pady=(30, 20), padx=20, fill="both", expand=True)
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)
        
        def set_result(value):
            dialog.result = value
            dialog.destroy()
        
        button1 = ctk.CTkButton(button_frame, text=option_1, command=lambda: set_result(option_1), width=100)
        button1.grid(row=0, column=0, padx=10)
        
        button2 = ctk.CTkButton(button_frame, text=option_2, command=lambda: set_result(option_2), width=100)
        button2.grid(row=0, column=1, padx=10)
        
        # Center the dialog
        dialog.update_idletasks()
        x = dialog.winfo_screenwidth() // 2 - dialog.winfo_width() // 2
        y = dialog.winfo_screenheight() // 2 - dialog.winfo_height() // 2
        dialog.geometry(f"+{x}+{y}")

        # Wait for the dialog to be destroyed
        dialog.wait_window()
        
        return dialog.result

class BodyFatEstimatorApp:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Body Fat Estimator")
        self.app.geometry("1200x800")
        self.app.minsize(1000, 700)
        
        # Theme tracking
        self.current_theme = STANDARD_THEME
        self.is_midnight_mode = False
        
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

    def run(self):
        """Run the application"""
        self.app.mainloop()
        
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
            # Use the imported TEST_DATA dictionary
            for key, value in TEST_DATA.items():
                if key in self.variables:
                    var = self.variables[key]
                    try:
                        if isinstance(var, ctk.StringVar):
                            # Handle dropdowns - find matching option if possible
                            if key == "activity_level" and isinstance(value, (int, float)):
                                # Find option starting with the number
                                options = var._values if hasattr(var, '_values') else [] # Get options if available
                                matching_option = next((opt for opt in options if opt.startswith(str(value))), None)
                                if matching_option:
                                    var.set(matching_option)
                                else:
                                    var.set(str(value)) # Fallback
                            elif key in ["gender", "resistance_training", "is_athlete"]:
                                var.set(str(value).lower()) # Ensure lowercase for consistency
                            elif key in ["job_activity", "leisure_activity", "experience_level", "workout_type"]:
                                # Find exact match or first part before ":"
                                options = var._values if hasattr(var, '_values') else []
                                matching_option = next((opt for opt in options if opt.split(":")[0] == str(value).split(":")[0]), None)
                                if matching_option:
                                     var.set(matching_option)
                                else:
                                     var.set(str(value)) # Fallback
                            else:
                                var.set(str(value))
                        elif isinstance(var, ctk.DoubleVar):
                            var.set(float(value))
                        elif isinstance(var, ctk.IntVar):
                            var.set(int(value))
                    except (ValueError, TypeError) as e:
                         print(f"Warning: Could not set test value for {key}: {value}. Error: {e}")
                         # Optionally set to default or skip
                         if isinstance(var, (ctk.DoubleVar, ctk.IntVar)):
                             var.set(0)
                         else:
                             var.set("")
            SimpleMessageBox.show_info("Success", "Form filled with test data.")
        except Exception as e:
            SimpleMessageBox.show_info("Error", f"Failed to fill test data: {str(e)}")
            traceback.print_exc()

    def load_most_recent_data(self):
        """Load the most recent report data into the form"""
        try:
            json_path = "last_report_data.json"
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    data = json.load(f)
                
                # Prefer 'initial_data' if it exists, otherwise use the main dict
                load_data = data # Load the raw data saved previously

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
                                elif key in ["job_activity", "leisure_activity", "experience_level", "workout_type"]:
                                    # Find exact match or first part before ":"
                                    options = var._values if hasattr(var, '_values') else []
                                    matching_option = next((opt for opt in options if opt.split(":")[0] == str(value).split(":")[0]), None)
                                    if matching_option:
                                         var.set(matching_option)
                                    else:
                                         var.set(str(value)) # Fallback
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
                elif name in ["job_activity", "leisure_activity", "experience_level", "workout_type"]:
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
                            try: # Attempt MM/DD/YYYY
                                datetime.strptime(str(value), "%m/%d/%Y")
                                data[name] = datetime.strptime(str(value), "%m/%d/%Y").strftime("%m%d%y") # Convert to MMDDYY
                            except ValueError:
                                errors.append(f"Invalid date format for {name.replace('_', ' ').title()}. Use MMDDYY or MM/DD/YYYY.")
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
            
            # Ensure current data is included if no other progress exists or as the latest point
            current_date_str_mmddyy = initial_data.get('start_date') # Use start_date as current if no progress
            if current_date_str_mmddyy:
                 try:
                     current_date_obj = datetime.strptime(current_date_str_mmddyy, "%m%d%y")
                     current_entry = {
                         "date": current_date_obj.strftime("%m/%d/%Y"),
                         "weight": initial_data.get('current_weight', 0),
                         "bodyfat": initial_data.get('current_bf', 0)
                     }
                     # Add if no progress data or if it's newer than the last entry
                     if not progression_data or current_date_obj > datetime.strptime(progression_data[-1]['date'], "%m/%d/%Y"):
                          progression_data.append(current_entry)
                     # Ensure sorted by date after potentially adding current
                     progression_data.sort(key=lambda x: datetime.strptime(x['date'], "%m/%d/%Y"))
                 except ValueError:
                     print(f"Could not parse current date {current_date_str_mmddyy} for progression data.")


            if not progression_data:
                 SimpleMessageBox.show_info("Error", "No valid progression data available to generate report.")
                 return

            # Generate the report data using imported functions
            self.current_report = generate_comprehensive_report(progression_data, initial_data)
            
            # Save the report files
            self.saved_files = save_report(self.current_report, initial_data["name"], "all") # Save PDF, MD, JSON, Chart
            
            # Save data used for this report to last_report_data.json
            try:
                 # Save the raw input data for easier reloading
                 with open("last_report_data.json", "w") as f:
                     # Convert datetime objects back to strings if necessary before saving
                     save_data = initial_data.copy()
                     # No datetime objects expected in initial_data based on get_form_data
                     json.dump(save_data, f, indent=4)
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
                        self.saved_files.get("json"), 
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
            self.saved_files = save_report(self.current_report, initial_data["name"], "all")

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
        
        # Dropdown - Ensure options are strings
        str_options = [str(opt) for opt in options]
        dropdown = ctk.CTkOptionMenu(frame, variable=var, values=str_options)
        dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        if str_options:
             dropdown.set(str_options[0])  # Set default value
        
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
                elif "-" in date_str: # Allow YYYY-MM-DD
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                else: # Assume MMDDYY
                    date = datetime.strptime(date_str, "%m%d%y")
                date_sql_str = date.strftime("%Y-%m-%d")  # Standardize date format for storage
            except ValueError:
                SimpleMessageBox.show_info("Invalid Date", "Please enter a valid date (MM/DD/YYYY, YYYY-MM-DD, or MMDDYY).")
                return
                
            # Get weight and bodyfat
            try:
                weight = float(self.progress_weight_var.get()) if self.progress_weight_var.get() else 0.0
                bodyfat = float(self.progress_bf_var.get()) if self.progress_bf_var.get() else 0.0
                if weight <= 0:
                     SimpleMessageBox.show_info("Invalid Data", "Weight must be a positive number.")
                     return
                # BF can be 0, but maybe add upper limit?
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
                (date_sql_str, weight, bodyfat, notes)
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
            traceback.print_exc()
    
    def load_progress_data(self):
        """Load and display progress data from database"""
        # Clear existing data
        for widget in self.history_table_frame.winfo_children():
            if widget.grid_info()["row"] > 0:  # Skip headers
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
                display_date = date # Fallback if format is unexpected
                
            # Add data to table
            ctk.CTkLabel(self.history_table_frame, text=display_date).grid(row=row_num, column=0, padx=5, pady=2, sticky="w")
            ctk.CTkLabel(self.history_table_frame, text=f"{weight:.1f}").grid(row=row_num, column=1, padx=5, pady=2, sticky="w")
            ctk.CTkLabel(self.history_table_frame, text=f"{bodyfat:.1f}").grid(row=row_num, column=2, padx=5, pady=2, sticky="w")
            
            notes_text = (notes[:40] + '...') if notes and len(notes) > 40 else notes # Truncate long notes
            ctk.CTkLabel(self.history_table_frame, text=notes_text).grid(row=row_num, column=3, padx=5, pady=2, sticky="w")
            
            # Action button
            delete_btn = ctk.CTkButton(
                self.history_table_frame, 
                text="Delete", 
                width=80,
                fg_color="darkred",
                hover_color="#A00000",
                command=lambda id=entry_id: self.delete_progress_entry(id)
            )
            delete_btn.grid(row=row_num, column=4, padx=5, pady=2)
        
        # Update charts
        self.update_progress_charts(rows)

    def delete_progress_entry(self, entry_id):
        """Delete a progress entry from the database"""
        result = SimpleMessageBox.show_question("Confirm Delete", "Are you sure you want to delete this progress entry?")
        if result == "Yes":
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM weekly_progress WHERE id = ?", (entry_id,))
                conn.commit()
                conn.close()
                self.load_progress_data() # Refresh the list
                SimpleMessageBox.show_info("Success", "Entry deleted successfully.")
            except Exception as e:
                SimpleMessageBox.show_info("Error", f"Failed to delete entry: {str(e)}")
                traceback.print_exc()

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
        
        # Sort by date (YYYY-MM-DD format from DB)
        sorted_data = sorted(data, key=lambda x: x[1]) 
        
        for _, date_str, weight, bodyfat, _ in sorted_data:
            # Convert date string to datetime
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                dates.append(date)
                weights.append(weight)
                bodyfats.append(bodyfat)
            except ValueError:
                print(f"Skipping invalid date format in chart data: {date_str}")
                continue
        
        # Skip if not enough data after filtering
        if len(dates) < 2:
            no_data_label = ctk.CTkLabel(
                self.weight_chart_frame,
                text="Not enough data for chart\n(at least 2 entries needed)",
                wraplength=200,
                justify="center"
            )
            no_data_label.place(relx=0.5, rely=0.5, anchor="center")
            
            no_data_label2 = ctk.CTkLabel(
                self.bf_chart_frame, 
                text="Not enough data for chart\n(at least 2 entries needed)",
                wraplength=200,
                justify="center"
            ) 
            no_data_label2.place(relx=0.5, rely=0.5, anchor="center")
            return

        # Create Weight Chart
        try:
            fig_weight, ax_weight = plt.subplots(figsize=(5, 3)) # Smaller figure size
            ax_weight.plot(dates, weights, marker='o', linestyle='-')
            ax_weight.set_title("Weight (lbs)")
            ax_weight.set_xlabel("Date")
            ax_weight.set_ylabel("Weight")
            ax_weight.grid(True)
            fig_weight.autofmt_xdate() # Auto format dates
            plt.tight_layout() # Adjust layout
            
            canvas_weight = FigureCanvasTkAgg(fig_weight, master=self.weight_chart_frame)
            canvas_widget_weight = canvas_weight.get_tk_widget()
            canvas_widget_weight.pack(fill="both", expand=True)
            canvas_weight.draw()
            plt.close(fig_weight) # Close figure to free memory
        except Exception as e:
             print(f"Error creating weight chart: {e}")
             ctk.CTkLabel(self.weight_chart_frame, text=f"Error: {e}").pack()


        # Create Body Fat Chart
        try:
            fig_bf, ax_bf = plt.subplots(figsize=(5, 3)) # Smaller figure size
            ax_bf.plot(dates, bodyfats, marker='x', linestyle='--', color='r')
            ax_bf.set_title("Body Fat (%)")
            ax_bf.set_xlabel("Date")
            ax_bf.set_ylabel("Body Fat %")
            ax_bf.grid(True)
            fig_bf.autofmt_xdate() # Auto format dates
            plt.tight_layout() # Adjust layout
            
            canvas_bf = FigureCanvasTkAgg(fig_bf, master=self.bf_chart_frame)
            canvas_widget_bf = canvas_bf.get_tk_widget()
            canvas_widget_bf.pack(fill="both", expand=True)
            canvas_bf.draw()
            plt.close(fig_bf) # Close figure to free memory
        except Exception as e:
             print(f"Error creating body fat chart: {e}")
             ctk.CTkLabel(self.bf_chart_frame, text=f"Error: {e}").pack()


    def setup_reports_history(self):
        """Setup the reports history view"""
        # Title
        title = ctk.CTkLabel(
            self.history_frame, 
            text="Report History", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Controls
        controls_frame = ctk.CTkFrame(self.history_frame)
        controls_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        controls_frame.grid_columnconfigure(0, weight=1)
        
        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="Refresh Reports",
            command=self.load_report_history
        )
        refresh_btn.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        # Reports list
        self.reports_list_frame = ctk.CTkScrollableFrame(self.history_frame)
        self.reports_list_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.reports_list_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1) # Added column for delete
        
        # Headers
        header_font = ctk.CTkFont(weight="bold")
        ctk.CTkLabel(self.reports_list_frame, text="Name", font=header_font).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.reports_list_frame, text="Date", font=header_font).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.reports_list_frame, text="PDF", font=header_font).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.reports_list_frame, text="Markdown", font=header_font).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.reports_list_frame, text="Actions", font=header_font).grid(row=0, column=4, padx=5, pady=5, sticky="w") # Delete action header
        
        # Load reports
        self.load_report_history()
    
    def load_report_history(self):
        """Load and display report history from database"""
        # Clear existing data
        for widget in self.reports_list_frame.winfo_children():
            # Check if grid_info exists and row > 0
            try:
                 if widget.grid_info()["row"] > 0: 
                      widget.destroy()
            except: # Handle cases where widget might not have grid_info yet
                 widget.destroy()

        
        # Get data from database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, date, json_path, md_path, pdf_path 
            FROM report_history 
            ORDER BY date DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            no_data_label = ctk.CTkLabel(
                self.reports_list_frame,
                text="No reports found. Generate a report to see it here.",
                font=ctk.CTkFont(size=14)
            )
            # Ensure headers are row 0, data starts row 1
            no_data_label.grid(row=1, column=0, columnspan=5, padx=10, pady=20) 
            return
        
        # Add each report to the list
        for i, (id, name, date, json_path, md_path, pdf_path) in enumerate(rows):
            row_num = i + 1  # +1 for header row
            
            # Format date for display
            try:
                display_date = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
            except ValueError:
                display_date = date # Fallback
                
            # Name and date
            ctk.CTkLabel(self.reports_list_frame, text=name).grid(row=row_num, column=0, padx=5, pady=2, sticky="w")
            ctk.CTkLabel(self.reports_list_frame, text=display_date).grid(row=row_num, column=1, padx=5, pady=2, sticky="w")
            
            # PDF button
            pdf_button_frame = ctk.CTkFrame(self.reports_list_frame, fg_color="transparent")
            pdf_button_frame.grid(row=row_num, column=2, padx=5, pady=2, sticky="w")
            if pdf_path and os.path.exists(pdf_path):
                pdf_btn = ctk.CTkButton(
                    pdf_button_frame,
                    text="Open PDF",
                    width=100,
                    command=lambda path=pdf_path: self.open_file(path)
                )
                pdf_btn.pack()
            else:
                ctk.CTkLabel(pdf_button_frame, text="N/A").pack()
            
            # Markdown button
            md_button_frame = ctk.CTkFrame(self.reports_list_frame, fg_color="transparent")
            md_button_frame.grid(row=row_num, column=3, padx=5, pady=2, sticky="w")
            if md_path and os.path.exists(md_path):
                md_btn = ctk.CTkButton(
                    md_button_frame,
                    text="Open Markdown",
                    width=120,
                    command=lambda path=md_path: self.open_file(path)
                )
                md_btn.pack()
            else:
                ctk.CTkLabel(md_button_frame, text="N/A").pack()

            # Delete button
            delete_btn = ctk.CTkButton(
                self.reports_list_frame,
                text="Delete",
                width=80,
                fg_color="darkred",
                hover_color="#A00000",
                command=lambda report_id=id, pdf=pdf_path, md=md_path, json_p=json_path: self.delete_report_entry(report_id, pdf, md, json_p)
            )
            delete_btn.grid(row=row_num, column=4, padx=5, pady=2)

    def delete_report_entry(self, report_id, pdf_path, md_path, json_path):
        """Delete a report entry from DB and optionally delete files"""
        result = SimpleMessageBox.show_question("Confirm Delete", "Delete this report entry? Also delete associated files (PDF, MD, JSON)?", option_1="Delete All", option_2="Delete Entry Only")
        
        if result == "Delete All" or result == "Delete Entry Only":
            try:
                # Delete from DB
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM report_history WHERE id = ?", (report_id,))
                conn.commit()
                conn.close()
                
                # Delete files if requested
                if result == "Delete All":
                    files_to_delete = [pdf_path, md_path, json_path]
                    deleted_files = []
                    errors = []
                    for f_path in files_to_delete:
                        if f_path and os.path.exists(f_path):
                            try:
                                os.remove(f_path)
                                deleted_files.append(os.path.basename(f_path))
                            except Exception as e:
                                errors.append(f"Could not delete {os.path.basename(f_path)}: {e}")
                    if errors:
                         SimpleMessageBox.show_info("File Deletion Error", "\n".join(errors))
                    # Removed redundant success message for file deletion

                self.load_report_history() # Refresh the list
                SimpleMessageBox.show_info("Success", "Report entry deleted successfully.")

            except Exception as e:
                SimpleMessageBox.show_info("Error", f"Failed to delete report entry: {str(e)}")
                traceback.print_exc()

    def setup_results_view(self):
        """Setup the results view tab"""
        # Initial empty state
        self.results_title = ctk.CTkLabel(
            self.results_frame,
            text="Report Results",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.results_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.no_results_label = ctk.CTkLabel(
            self.results_frame,
            text="Generate a report to see results here",
            font=ctk.CTkFont(size=14)
        )
        self.no_results_label.grid(row=1, column=0, padx=20, pady=20)

        # Frame for buttons
        self.results_button_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        # Grid placement will happen in display_results

        # Frame for text results
        self.results_text_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        # Grid placement will happen in display_results

        # Frame for chart
        self.results_chart_frame = ctk.CTkFrame(self.results_frame)
        # Grid placement will happen in display_results

    def display_results(self):
        """Display the generated report data in the Results tab"""
        # Clear previous results
        for widget in self.results_button_frame.winfo_children():
            widget.destroy()
        for widget in self.results_text_frame.winfo_children():
            widget.destroy()
        for widget in self.results_chart_frame.winfo_children():
            widget.destroy()
            
        self.no_results_label.grid_forget() # Hide the initial message

        if not self.current_report:
            self.no_results_label.grid(row=1, column=0, padx=20, pady=20) # Show again if no report
            return

        # Grid the frames
        self.results_button_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.results_text_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.results_chart_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.results_frame.grid_rowconfigure(2, weight=1) # Allow text frame to expand
        self.results_frame.grid_rowconfigure(3, weight=1) # Allow chart frame to expand

        # --- Buttons ---
        self.results_button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Open PDF button
        pdf_path = self.saved_files.get("pdf")
        pdf_btn = ctk.CTkButton(
            self.results_button_frame,
            text="Open PDF Report",
            state="normal" if pdf_path and os.path.exists(pdf_path) else "disabled",
            command=lambda: self.open_file(pdf_path) if pdf_path else None
        )
        pdf_btn.grid(row=0, column=0, padx=5, pady=5)

        # Open Markdown button
        md_path = self.saved_files.get("markdown")
        md_btn = ctk.CTkButton(
            self.results_button_frame,
            text="Open Markdown Report",
            state="normal" if md_path and os.path.exists(md_path) else "disabled",
            command=lambda: self.open_file(md_path) if md_path else None
        )
        md_btn.grid(row=0, column=1, padx=5, pady=5)

        # Open JSON button
        json_path = self.saved_files.get("json")
        json_btn = ctk.CTkButton(
            self.results_button_frame,
            text="Open JSON Data",
            state="normal" if json_path and os.path.exists(json_path) else "disabled",
            command=lambda: self.open_file(json_path) if json_path else None
        )
        json_btn.grid(row=0, column=2, padx=5, pady=5)

        # --- Text Results ---
        self.results_text_frame.grid_columnconfigure(0, weight=1)
        
        results_textbox = ctk.CTkTextbox(self.results_text_frame, wrap="word", height=300) # Set initial height
        results_textbox.grid(row=0, column=0, sticky="nsew")
        self.results_text_frame.grid_rowconfigure(0, weight=1) # Allow textbox to expand vertically

        # Populate textbox (example fields, adjust as needed based on report_data structure)
        report = self.current_report
        results_textbox.insert("end", f"Report for: {report.get('name', 'N/A')}\n")
        
        # Safely format dates, handling potential missing keys or format issues
        start_date_str = "N/A"
        end_date_str = "N/A"
        try:
             if report.get('start_date'):
                  # Use the date string directly if it's already formatted, else parse MMDDYY
                  date_val = report['start_date']
                  if isinstance(date_val, str) and "/" in date_val: # Check if already MM/DD/YYYY
                       start_date_str = date_val
                  else:
                       start_date_obj = datetime.strptime(str(date_val), "%m%d%y") 
                       start_date_str = start_date_obj.strftime("%m/%d/%Y")
        except (ValueError, TypeError): pass # Keep N/A if parsing fails
        try:
             if report.get('end_date'):
                  date_val = report['end_date']
                  if isinstance(date_val, str) and "/" in date_val:
                       end_date_str = date_val
                  else:
                       end_date_obj = datetime.strptime(str(date_val), "%m%d%y") 
                       end_date_str = end_date_obj.strftime("%m/%d/%Y")
        except (ValueError, TypeError): pass # Keep N/A if parsing fails
        results_textbox.insert("end", f"Date Range: {start_date_str} to {end_date_str}\n\n")
        
        results_textbox.insert("end", f"--- Summary ---\n")
        results_textbox.insert("end", f"Initial Weight: {report.get('initial_weight', 0):.1f} lbs\n")
        results_textbox.insert("end", f"Final Weight: {report.get('final_weight', 0):.1f} lbs\n")
        results_textbox.insert("end", f"Weight Change: {report.get('weight_change', 0):.1f} lbs\n\n")
        
        results_textbox.insert("end", f"Initial Body Fat: {report.get('initial_body_fat', 0):.1f}%\n")
        results_textbox.insert("end", f"Final Body Fat: {report.get('final_body_fat', 0):.1f}%\n")
        results_textbox.insert("end", f"Body Fat Change: {report.get('body_fat_change', 0):.1f}%\n\n")

        results_textbox.insert("end", f"--- Lean Mass ---\n")
        results_textbox.insert("end", f"Initial Lean Mass: {report.get('initial_lean_mass', 0):.1f} lbs\n")
        results_textbox.insert("end", f"Final Lean Mass: {report.get('final_lean_mass', 0):.1f} lbs\n")
        results_textbox.insert("end", f"Lean Mass Change: {report.get('lean_mass_change', 0):.1f} lbs\n")
        lmps = report.get('lean_mass_preservation_score', {})
        results_textbox.insert("end", f"Preservation Score: {lmps.get('score', 'N/A')} ({lmps.get('rating', 'N/A')})\n\n")

        results_textbox.insert("end", f"--- Predictions & Goals ---\n")
        results_textbox.insert("end", f"Goal Weight: {report.get('goal_weight', 0):.1f} lbs\n")
        results_textbox.insert("end", f"Goal Body Fat: {report.get('goal_body_fat', 0):.1f}%\n")
        if 'weight_loss_prediction' in report:
             pred = report['weight_loss_prediction']
             results_textbox.insert("end", f"Predicted time to goal: {pred.get('time_to_goal_weeks', 'N/A')} weeks\n")
             results_textbox.insert("end", f"Required weekly deficit: {pred.get('required_weekly_deficit', 'N/A')} kcal\n")
        
        results_textbox.configure(state="disabled") # Make read-only

        # --- Chart ---
        chart_path = self.saved_files.get("chart") # Get chart path from save_report result
        if chart_path and os.path.exists(chart_path):
            try:
                # Open image and resize if needed
                img = Image.open(chart_path)
                # Optional: Resize image if it's too large for the window
                # max_width = 700 
                # if img.width > max_width:
                #     ratio = max_width / img.width
                #     new_height = int(img.height * ratio)
                #     img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                chart_image = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height)) 
                chart_label = ctk.CTkLabel(self.results_chart_frame, image=chart_image, text="")
                chart_label.pack(pady=10, padx=10, fill="both", expand=True)
            except Exception as e:
                print(f"Error loading chart image: {e}")
                chart_label = ctk.CTkLabel(self.results_chart_frame, text=f"Error loading chart: {e}")
                chart_label.pack(pady=10)
        else:
             chart_label = ctk.CTkLabel(self.results_chart_frame, text="Chart not available.")
             chart_label.pack(pady=10)

    def apply_theme_to_children(self, parent, fg_color, text_color):
        """Apply theme colors to all child widgets recursively"""
        for child in parent.winfo_children():
            try:
                # Apply to different widget types
                if isinstance(child, ctk.CTkFrame):
                    child.configure(fg_color=fg_color)
                    
                # Different handling for scrollable frames
                if isinstance(child, ctk.CTkScrollableFrame):
                    child.configure(fg_color=fg_color)

                # Text widgets
                if isinstance(child, (ctk.CTkLabel, ctk.CTkTextbox)):
                    if hasattr(child, 'configure') and callable(getattr(child, 'configure')):
                        if text_color:
                            child.configure(text_color=text_color)
                
                # Apply to buttons (leave fg_color as is for contrast)
                if isinstance(child, ctk.CTkButton) and not isinstance(child, ctk.CTkSegmentedButton):
                    # Only modify button hover color
                    child.configure(hover_color="#101010" if self.is_midnight_mode else None)
                
                # Recursively process child widgets
                self.apply_theme_to_children(child, fg_color, text_color)
            except Exception as e:
                print(f"Error applying theme to widget {type(child)}: {e}")

    def toggle_theme(self):
        """Toggle between standard theme and midnight OLED theme"""
        try:
            if self.is_midnight_mode:
                # Switch to standard theme
                ctk.set_default_color_theme(STANDARD_THEME)
                self.current_theme = STANDARD_THEME
                self.theme_button.configure(text="Switch to Midnight OLED Theme")
                self.is_midnight_mode = False
                
                # Reset application colors
                self.app.configure(fg_color=None)  # Reset to default
                self.main_frame.configure(fg_color=None)  # Reset to default
                
                # Reset tab colors
                for tab_name in ["Input Data", "Weekly Progress", "Reports History", "Results", "About"]:
                    self.tab_view.tab(tab_name).configure(fg_color=None)
                
                # Reset all child widgets - use None to reset to default theme
                self.apply_theme_to_children(self.app, None, None)
                
            else:
                # Switch to midnight OLED theme - apply directly without file
                ctk.set_appearance_mode("Dark")  # Ensure we're in dark mode
                
                # Apply OLED black theme directly to the application
                pure_black = "#000000"
                near_black = "#030303"  # Just a touch off pure black for some elements
                text_white = "#FFFFFF"  # Pure white text for contrast
                
                # Apply to main containers
                self.app.configure(fg_color=pure_black)
                self.main_frame.configure(fg_color=pure_black)
                self.tab_view.configure(fg_color=pure_black)
                
                # Apply to all tabs
                for tab_name in ["Input Data", "Weekly Progress", "Reports History", "Results", "About"]:
                    self.tab_view.tab(tab_name).configure(fg_color=pure_black)
                
                # Apply to all child widgets recursively
                self.apply_theme_to_children(self.app, near_black, text_white)
                
                # Ensure foreground colors of primary widgets are properly set
                self.input_frame.configure(fg_color=pure_black)
                self.progress_frame.configure(fg_color=pure_black)
                self.history_frame.configure(fg_color=pure_black)
                self.results_frame.configure(fg_color=pure_black)
                self.about_frame.configure(fg_color=pure_black)
                
                # Mark as midnight mode
                self.current_theme = MIDNIGHT_THEME_NAME
                self.theme_button.configure(text="Switch to Standard Theme", fg_color="#101010", text_color=text_white)
                self.is_midnight_mode = True
                
            # Show message about restart
            SimpleMessageBox.show_info("Theme Changed", 
                "Theme changed successfully! Some UI elements may require restarting the application to fully apply the new theme.")
                
        except Exception as e:
            print(f"Error changing theme: {e}")
            SimpleMessageBox.show_info("Error", f"Failed to change theme: {str(e)}")
            traceback.print_exc()

    def setup_about_view(self):
        """Setup the About tab view"""
        self.about_frame.grid_columnconfigure(0, weight=1)
        self.about_frame.grid_rowconfigure(0, weight=0)  # Title
        self.about_frame.grid_rowconfigure(1, weight=0)  # Theme button
        self.about_frame.grid_rowconfigure(2, weight=1)  # About text

        title = ctk.CTkLabel(
            self.about_frame, 
            text="About Body Fat Estimator", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Add theme toggle button
        theme_frame = ctk.CTkFrame(self.about_frame, fg_color="transparent")
        theme_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        theme_label = ctk.CTkLabel(theme_frame, text="UI Theme:")
        theme_label.pack(side="left", padx=(0, 10))
        
        self.theme_button = ctk.CTkButton(
            theme_frame, 
            text="Switch to Midnight OLED Theme" if not self.is_midnight_mode else "Switch to Standard Theme",
            command=self.toggle_theme
        )
        self.theme_button.pack(side="left", padx=5)

        about_text = """
Body Fat Estimator Application
Version: 1.1 (Desktop Mode)

This application helps estimate and track body fat percentage based on user inputs.
Features include:
- Data input for personal metrics and goals
- Weekly progress tracking with charts
- Comprehensive report generation (PDF, Markdown, JSON)
- Report history management with file opening and deletion
- Visualization of results including progress chart

Developed using CustomTkinter and Matplotlib.
        """
        
        textbox = ctk.CTkTextbox(self.about_frame, wrap="word")
        textbox.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        textbox.insert("1.0", about_text)
        textbox.configure(state="disabled", font=("Arial", 12)) # Make read-only, set font

    def open_file(self, file_path):
        """Open a file using the default system application."""
        try:
            abs_path = os.path.abspath(file_path) # Ensure absolute path
            if not file_path or not os.path.exists(abs_path):
                 SimpleMessageBox.show_info("Error", f"File not found: {abs_path}")
                 return

            print(f"Attempting to open file: {abs_path}") # Debug print

            if sys.platform == 'win32':
                os.startfile(abs_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', abs_path])
            else:  # Linux
                subprocess.call(['xdg-open', abs_path])
        except Exception as e:
            SimpleMessageBox.show_info("Error", f"Could not open file '{os.path.basename(file_path)}':\n{str(e)}")
            traceback.print_exc()

# This block should be outside the class definition and correctly indented
if __name__ == "__main__":
    # This allows running the desktop app directly for testing
    try:
        app = BodyFatEstimatorApp()
        app.run()
    except Exception as e:
        print("Unhandled exception in main execution:")
        traceback.print_exc()
        # Keep console open on Windows if run directly
        if sys.platform == 'win32':
             input("Press Enter to exit...")
