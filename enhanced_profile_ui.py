#!/usr/bin/env python
# enhanced_profile_ui.py
# Created: 03/28/25
# Description: Enhanced user profile data collection with critical fields for proper RMR calculation

import os
import sys
import json
import sqlite3
import traceback
from datetime import datetime
import customtkinter as ctk
from PIL import Image, ImageTk

# Import RMR calculations module for validation
from rmr_calculations import get_rmr_and_tdee, ValidationError

# Constants
DB_FILE = "history.db"

class SimpleMessageBox:
    @staticmethod
    def show_info(title, message):
        """Show an information message"""
        dialog = ctk.CTkToplevel()
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.grab_set()
        dialog.attributes("-topmost", True)
        
        label = ctk.CTkLabel(dialog, text=message, wraplength=350)
        label.pack(pady=(30, 20), padx=20, fill="both", expand=True)
        
        button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy, width=100)
        button.pack(pady=10)
        
        # Center the dialog
        dialog.update_idletasks()
        x = dialog.winfo_screenwidth() // 2 - dialog.winfo_width() // 2
        y = dialog.winfo_screenheight() // 2 - dialog.winfo_height() // 2
        dialog.geometry(f"+{x}+{y}")
        
        dialog.wait_window()
        return dialog
    
    @staticmethod
    def show_question(title, message, option_1="Yes", option_2="No"):
        """Show a question dialog with two options"""
        dialog = ctk.CTkToplevel()
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.grab_set()
        dialog.attributes("-topmost", True)
        
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

        dialog.wait_window()
        return dialog.result

class EnhancedProfileApp:
    def __init__(self, user_id=1):
        self.user_id = user_id
        self.app = ctk.CTk()
        self.app.title("Enhanced User Profile")
        self.app.geometry("1000x800")
        self.app.minsize(900, 700)
        
        # Configure window
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_rowconfigure(0, weight=1)
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self.app)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configure main frame
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create tab view
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.grid(row=0, column=0, sticky="nsew")
        
        # Create tabs
        self.tab_view.add("Personal Information")
        self.tab_view.add("Initial Measurements")
        self.tab_view.add("Goals & Training")
        self.tab_view.add("Nutrition & Lifestyle")
        self.tab_view.add("Summary")
        
        # Configure tab grids
        for tab in ["Personal Information", "Initial Measurements", "Goals & Training", "Nutrition & Lifestyle", "Summary"]:
            self.tab_view.tab(tab).grid_columnconfigure(0, weight=1)
            self.tab_view.tab(tab).grid_rowconfigure(0, weight=1)
        
        # Create scrollable frames for tabs
        self.personal_frame = ctk.CTkScrollableFrame(self.tab_view.tab("Personal Information"))
        self.personal_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.personal_frame.grid_columnconfigure(0, weight=1)
        
        self.initial_frame = ctk.CTkScrollableFrame(self.tab_view.tab("Initial Measurements"))
        self.initial_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.initial_frame.grid_columnconfigure(0, weight=1)
        
        self.goals_frame = ctk.CTkScrollableFrame(self.tab_view.tab("Goals & Training"))
        self.goals_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.goals_frame.grid_columnconfigure(0, weight=1)
        
        self.nutrition_frame = ctk.CTkScrollableFrame(self.tab_view.tab("Nutrition & Lifestyle"))
        self.nutrition_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.nutrition_frame.grid_columnconfigure(0, weight=1)
        
        self.summary_frame = ctk.CTkScrollableFrame(self.tab_view.tab("Summary"))
        self.summary_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.summary_frame.grid_columnconfigure(0, weight=1)
        
        # Setup form variables
        self.variables = {}
        
        # Ensure database exists and create tables
        self.init_database()
        
        # Create UI elements
        self.setup_personal_info()
        self.setup_initial_measurements()
        self.setup_goals_training()
        self.setup_nutrition_lifestyle()
        self.setup_summary()
        
        # Try to load existing data
        self.load_user_data()

    def run(self):
        """Run the application"""
        self.app.mainloop()
        
    def init_database(self):
        """Initialize the database with enhanced tables"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create user_profiles table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY,
            user_name TEXT,
            gender TEXT,
            dob TEXT,
            height_feet INTEGER,
            height_inches INTEGER,
            email TEXT,
            phone TEXT,
            start_date TEXT,
            end_date TEXT,
            
            goal_weight REAL,
            goal_bf REAL,
            
            resistance_training INTEGER,
            workout_type TEXT,
            workout_days INTEGER,
            experience_level TEXT,
            
            activity_level TEXT,
            job_activity TEXT,
            leisure_activity TEXT,
            is_athlete INTEGER,
            
            diet_type TEXT
        )
        ''')
        
        # Create initial_measurements table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS initial_measurements (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            date TEXT,
            weight REAL,
            body_fat REAL,
            waist REAL,
            hips REAL,
            chest REAL,
            neck REAL,
            left_arm REAL,
            right_arm REAL,
            left_thigh REAL,
            right_thigh REAL,
            lean_mass REAL,
            fat_mass REAL,
            rmr REAL,
            tdee REAL,
            FOREIGN KEY (user_id) REFERENCES user_profiles(id)
        )
        ''')
        
        # Create weekly_updates table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_updates (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            date TEXT,
            weight REAL,
            body_fat REAL,
            waist REAL,
            hips REAL,
            protein_intake REAL,
            carb_intake REAL,
            fat_intake REAL,
            rmr REAL,
            tdee REAL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES user_profiles(id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_section_header(self, parent, text, row):
        """Create a section header with title and separator"""
        # Title
        header = ctk.CTkLabel(
            parent, 
            text=text, 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.grid(row=row, column=0, padx=10, pady=(15, 5), sticky="w")
        
        # Separator
        separator = ctk.CTkFrame(parent, height=2, fg_color="gray70")
        separator.grid(row=row+1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        return row + 2  # Return next available row
    
    def create_form_field(self, parent, name, label, data_type, row, tooltip=None):
        """Create a form field with label and entry"""
        field_frame = ctk.CTkFrame(parent)
        field_frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        field_frame.grid_columnconfigure(0, weight=0)
        field_frame.grid_columnconfigure(1, weight=1)
        
        # Label with optional tooltip
        label_frame = ctk.CTkFrame(field_frame, fg_color="transparent")
        label_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        lbl = ctk.CTkLabel(label_frame, text=label, width=180, anchor="w")
        lbl.pack(side="left")
        
        # Add tooltip if provided
        if tooltip:
            # Simple tooltip implementation - hover effect
            tooltip_icon = ctk.CTkLabel(label_frame, text="?", font=("Arial", 12, "bold"), 
                                        width=16, height=16, fg_color="gray70", corner_radius=8,
                                        text_color="white")
            tooltip_icon.pack(side="left", padx=(5, 0))
            
            # Show tooltip on hover
            def show_tooltip(event):
                tooltip_popup = ctk.CTkToplevel()
                tooltip_popup.wm_overrideredirect(True)
                tooltip_popup.attributes("-topmost", True)
                
                # Position tooltip near the mouse pointer
                x, y = event.x_root, event.y_root
                tooltip_popup.geometry(f"+{x+10}+{y+10}")
                
                # Add tooltip text
                tip_label = ctk.CTkLabel(tooltip_popup, text=tooltip, wraplength=200, justify="left",
                                        corner_radius=6, fg_color="#3a7ebf", text_color="white",
                                        font=("Arial", 12))
                tip_label.pack(padx=5, pady=5)
                
                # Hide tooltip when mouse leaves
                def hide_tooltip(e):
                    tooltip_popup.destroy()
                
                tooltip_icon.bind("<Leave>", hide_tooltip)
                tooltip_popup.bind("<Leave>", hide_tooltip)
            
            tooltip_icon.bind("<Enter>", show_tooltip)
        
        # Create variable of appropriate type
        if data_type == "float":
            var = ctk.DoubleVar()
        elif data_type == "int":
            var = ctk.IntVar()
        elif data_type == "bool":
            var = ctk.BooleanVar()
        else:
            var = ctk.StringVar()
        
        # Entry field or checkbox based on data type
        if data_type == "bool":
            entry = ctk.CTkCheckBox(field_frame, text="", variable=var)
        else:
            entry = ctk.CTkEntry(field_frame, textvariable=var, width=250)
        
        entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # Store variable
        self.variables[name] = var
        
        return row + 1  # Return next available row
    
    def create_dropdown(self, parent, name, label, options, row, tooltip=None):
        """Create a dropdown field with label"""
        field_frame = ctk.CTkFrame(parent)
        field_frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        field_frame.grid_columnconfigure(0, weight=0)
        field_frame.grid_columnconfigure(1, weight=1)
        
        # Label with optional tooltip
        label_frame = ctk.CTkFrame(field_frame, fg_color="transparent")
        label_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        lbl = ctk.CTkLabel(label_frame, text=label, width=180, anchor="w")
        lbl.pack(side="left")
        
        # Add tooltip if provided
        if tooltip:
            tooltip_icon = ctk.CTkLabel(label_frame, text="?", font=("Arial", 12, "bold"), 
                                        width=16, height=16, fg_color="gray70", corner_radius=8,
                                        text_color="white")
            tooltip_icon.pack(side="left", padx=(5, 0))
            
            # Show tooltip on hover
            def show_tooltip(event):
                tooltip_popup = ctk.CTkToplevel()
                tooltip_popup.wm_overrideredirect(True)
                tooltip_popup.attributes("-topmost", True)
                
                x, y = event.x_root, event.y_root
                tooltip_popup.geometry(f"+{x+10}+{y+10}")
                
                tip_label = ctk.CTkLabel(tooltip_popup, text=tooltip, wraplength=200, justify="left",
                                        corner_radius=6, fg_color="#3a7ebf", text_color="white",
                                        font=("Arial", 12))
                tip_label.pack(padx=5, pady=5)
                
                def hide_tooltip(e):
                    tooltip_popup.destroy()
                
                tooltip_icon.bind("<Leave>", hide_tooltip)
                tooltip_popup.bind("<Leave>", hide_tooltip)
            
            tooltip_icon.bind("<Enter>", show_tooltip)
        
        # Variable
        var = ctk.StringVar()
        
        # Dropdown - Ensure options are strings
        str_options = [str(opt) for opt in options]
        dropdown = ctk.CTkOptionMenu(field_frame, variable=var, values=str_options, width=250)
        dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        if str_options:
             dropdown.set(str_options[0])  # Set default value
        
        # Store variable
        self.variables[name] = var
        
        return row + 1  # Return next available row
    
    def setup_personal_info(self):
        """Setup the personal information tab"""
        row = 0
        
        # Title label
        title = ctk.CTkLabel(
            self.personal_frame, 
            text="Personal Information", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=row, column=0, padx=10, pady=(10, 20), sticky="w")
        row += 1
        
        # Basic Information section
        row = self.create_section_header(self.personal_frame, "Basic Information", row)
        
        row = self.create_form_field(self.personal_frame, "user_name", "Name", "str", row)
        
        gender_options = ["Male", "Female"]
        row = self.create_dropdown(self.personal_frame, "gender", "Gender", gender_options, row, 
                                  tooltip="Required for accurate body fat and RMR calculations")
        
        row = self.create_form_field(self.personal_frame, "dob", "Date of Birth (MMDDYY)", "str", row,
                                    tooltip="Required for age calculation in metabolic formulas")
        
        # Height section (separate fields for feet and inches as required)
        row = self.create_form_field(self.personal_frame, "height_feet", "Height - Feet", "int", row)
        row = self.create_form_field(self.personal_frame, "height_inches", "Height - Inches", "int", row)
        
        # Contact information section
        row = self.create_section_header(self.personal_frame, "Contact Information", row)
        
        row = self.create_form_field(self.personal_frame, "email", "Email Address", "str", row)
        row = self.create_form_field(self.personal_frame, "phone", "Phone Number", "str", row)
        
        # Start and end dates
        row = self.create_section_header(self.personal_frame, "Program Dates", row)
        
        row = self.create_form_field(self.personal_frame, "start_date", "Start Date (MMDDYY)", "str", row,
                                   tooltip="Beginning date of your fitness program")
        row = self.create_form_field(self.personal_frame, "end_date", "End Date (MMDDYY or leave blank)", "str", row,
                                   tooltip="Optional target end date of your fitness program")
        
        # Navigation buttons
        button_frame = ctk.CTkFrame(self.personal_frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, padx=10, pady=20, sticky="ew")
        
        next_btn = ctk.CTkButton(
            button_frame, 
            text="Next: Initial Measurements", 
            command=lambda: self.tab_view.set("Initial Measurements")
        )
        next_btn.pack(side="right", padx=10)
    
    def setup_initial_measurements(self):
        """Setup the initial measurements tab"""
        row = 0
        
        # Title label
        title = ctk.CTkLabel(
            self.initial_frame, 
            text="Initial Measurements", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=row, column=0, padx=10, pady=(10, 20), sticky="w")
        row += 1
        
        # Key measurements section
        row = self.create_section_header(self.initial_frame, "Key Measurements", row)
        
        row = self.create_form_field(self.initial_frame, "initial_weight", "Starting Weight (lbs)", "float", row,
                                   tooltip="Your current body weight at the start of your program")
        row = self.create_form_field(self.initial_frame, "initial_bf", "Starting Body Fat (%)", "float", row,
                                   tooltip="Your current body fat percentage at the start")
        
        # Additional measurements section
        row = self.create_section_header(self.initial_frame, "Body Measurements (optional)", row)
        
        row = self.create_form_field(self.initial_frame, "waist", "Waist Circumference (inches)", "float", row)
        row = self.create_form_field(self.initial_frame, "hips", "Hip Circumference (inches)", "float", row)
        row = self.create_form_field(self.initial_frame, "chest", "Chest Circumference (inches)", "float", row)
        row = self.create_form_field(self.initial_frame, "neck", "Neck Circumference (inches)", "float", row)
        
        # Arm and leg measurements
        row = self.create_form_field(self.initial_frame, "left_arm", "Left Arm (inches)", "float", row)
        row = self.create_form_field(self.initial_frame, "right_arm", "Right Arm (inches)", "float", row)
        row = self.create_form_field(self.initial_frame, "left_thigh", "Left Thigh (inches)", "float", row)
        row = self.create_form_field(self.initial_frame, "right_thigh", "Right Thigh (inches)", "float", row)
        
        # Navigation buttons
        button_frame = ctk.CTkFrame(self.initial_frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, padx=10, pady=20, sticky="ew")
        
        back_btn = ctk.CTkButton(
            button_frame, 
            text="Back: Personal Info", 
            command=lambda: self.tab_view.set("Personal Information")
        )
        back_btn.pack(side="left", padx=10)
        
        next_btn = ctk.CTkButton(
            button_frame, 
            text="Next: Goals & Training", 
            command=lambda: self.tab_view.set("Goals & Training")
        )
        next_btn.pack(side="right", padx=10)
    
    def setup_goals_training(self):
        """Setup the goals and training tab"""
        row = 0
        
        # Title label
        title = ctk.CTkLabel(
            self.goals_frame, 
            text="Goals & Training", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=row, column=0, padx=10, pady=(10, 20), sticky="w")
        row += 1
        
        # Goals section
        row = self.create_section_header(self.goals_frame, "Fitness Goals", row)
        
        row = self.create_form_field(self.goals_frame, "goal_weight", "Goal Weight (lbs)", "float", row)
        row = self.create_form_field(self.goals_frame, "goal_bf", "Goal Body Fat (%)", "float", row,
                                   tooltip="Target body fat percentage you want to achieve")
        
        # Training Info section
        row = self.create_section_header(self.goals_frame, "Training Information", row)
        
        # Resistance training status toggle
        row = self.create_form_field(self.goals_frame, "resistance_training", "Resistance Training", "bool", row,
                                   tooltip="Do you incorporate weight training?")
        
        # Workout type selection
        workout_types = ["Bodybuilding", "Cardio", "General Fitness", "Sports-Specific", "Strength Training"]
        row = self.create_dropdown(self.goals_frame, "workout_type", "Workout Type", workout_types, row,
                                 tooltip="Primary style of your workouts")
        
        # Weekly workout frequency
        row = self.create_form_field(self.goals_frame, "workout_days", "Workouts per Week", "int", row,
                                   tooltip="How many days per week do you work out?")
        
        # Experience level selection with tooltips
        experience_levels = [
            "1: Beginner (0-1 year)", 
            "2: Novice (1-2 years)", 
            "3: Intermediate (2-4 years)", 
            "4: Advanced (4-10 years)", 
            "5: Elite (10+ years)"
        ]
        row = self.create_dropdown(self.goals_frame, "experience_level", "Experience Level", experience_levels, row,
                                 tooltip="Your experience level affects recovery needs and muscle gain potential")
        
        # Athlete status
        row = self.create_form_field(self.goals_frame, "is_athlete", "Competitive Athlete", "bool", row,
                                   tooltip="Are you currently competing in a sport?")
        
        # Navigation buttons
        button_frame = ctk.CTkFrame(self.goals_frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, padx=10, pady=20, sticky="ew")
        
        back_btn = ctk.CTkButton(
            button_frame, 
            text="Back: Initial Measurements", 
            command=lambda: self.tab_view.set("Initial Measurements")
        )
        back_btn.pack(side="left", padx=10)
        
        next_btn = ctk.CTkButton(
            button_frame, 
            text="Next: Nutrition & Lifestyle", 
            command=lambda: self.tab_view.set("Nutrition & Lifestyle")
        )
        next_btn.pack(side="right", padx=10)
    
    def setup_nutrition_lifestyle(self):
        """Setup the nutrition and lifestyle tab"""
        row = 0
        
        # Title label
        title = ctk.CTkLabel(
            self.nutrition_frame, 
            text="Nutrition & Lifestyle", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=row, column=0, padx=10, pady=(10, 20), sticky="w")
        row += 1
        
        # Nutrition section
        row = self.create_section_header(self.nutrition_frame, "Nutrition Information", row)
        
        row = self.create_form_field(self.nutrition_frame, "protein_intake", "Protein Intake (g/day)", "float", row)
        row = self.create_form_field(self.nutrition_frame, "carb_intake", "Carbohydrate Intake (g/day)", "float", row)
        row = self.create_form_field(self.nutrition_frame, "fat_intake", "Fat Intake (g/day)", "float", row)
        
        # Diet type dropdown
        diet_types = [
            "Standard", 
            "Keto", 
            "Low-Carb", 
            "Paleo", 
            "Vegetarian", 
            "Vegan", 
            "Mediterranean",
            "Intermittent Fasting"
        ]
        row = self.create_dropdown(self.nutrition_frame, "diet_type", "Diet Type", diet_types, row)
        
        # Activity section
        row = self.create_section_header(self.nutrition_frame, "Activity Levels", row)
        
        activity_levels = [
            "1: Sedentary (little or no exercise)",
            "2: Lightly active (light exercise/sports 1-3 days/week)",
            "3: Moderately active (moderate exercise/sports 3-5 days/week)",
            "4: Very active (hard exercise/sports 6-7 days a week)",
            "5: Extremely active (very hard exercise & physical job)"
        ]
        row = self.create_dropdown(self.nutrition_frame, "activity_level", "Activity Level", activity_levels, row,
                                 tooltip="General activity level affects your calorie needs")
        
        job_activities = [
            "Sedentary: Desk job, minimal movement",
            "Light: Standing, light activity",
            "Moderate: Regular movement, lifting",
            "Active: Very physical, constant movement"
        ]
        row = self.create_dropdown(self.nutrition_frame, "job_activity", "Job Activity", job_activities, row)
        
        leisure_activities = [
            "Sedentary: TV, reading, minimal movement",
            "Light: Walking, casual activities",
            "Moderate: Recreational sports, hiking",
            "Active: Intense hobbies, frequent workouts"
        ]
        row = self.create_dropdown(self.nutrition_frame, "leisure_activity", "Leisure Activity", leisure_activities, row)
        
        # Navigation buttons
        button_frame = ctk.CTkFrame(self.nutrition_frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, padx=10, pady=20, sticky="ew")
        
        back_btn = ctk.CTkButton(
            button_frame, 
            text="Back: Goals & Training", 
            command=lambda: self.tab_view.set("Goals & Training")
        )
        back_btn.pack(side="left", padx=10)
        
        next_btn = ctk.CTkButton(
            button_frame, 
            text="Next: Summary", 
            command=lambda: self.tab_view.set("Summary")
        )
        next_btn.pack(side="right", padx=10)
    
    def setup_summary(self):
        """Setup the summary tab with calculated values and save buttons"""
        row = 0
        
        # Title label
        title = ctk.CTkLabel(
            self.summary_frame, 
            text="Profile Summary", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=row, column=0, padx=10, pady=(10, 20), sticky="w")
        row += 1
        
        # Calculated metrics section
        row = self.create_section_header(self.summary_frame, "Calculated Metrics", row)
        
        # Create calculated fields (read-only)
        self.rmr_var = ctk.StringVar()
        self.rmr_var.set("Not calculated")
        rmr_frame = ctk.CTkFrame(self.summary_frame)
        rmr_frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        rmr_frame.grid_columnconfigure(0, weight=0)
        rmr_frame.grid_columnconfigure(1, weight=1)
        
        rmr_label = ctk.CTkLabel(rmr_frame, text="Resting Metabolic Rate (RMR):", width=250, anchor="w")
        rmr_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        rmr_value = ctk.CTkLabel(rmr_frame, textvariable=self.rmr_var, font=ctk.CTkFont(weight="bold"))
        rmr_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        row += 1
        
        # TDEE display
        self.tdee_var = ctk.StringVar()
        self.tdee_var.set("Not calculated")
        tdee_frame = ctk.CTkFrame(self.summary_frame)
        tdee_frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        tdee_frame.grid_columnconfigure(0, weight=0)
        tdee_frame.grid_columnconfigure(1, weight=1)
        
        tdee_label = ctk.CTkLabel(tdee_frame, text="Total Daily Energy Expenditure (TDEE):", width=250, anchor="w")
        tdee_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        tdee_value = ctk.CTkLabel(tdee_frame, textvariable=self.tdee_var, font=ctk.CTkFont(weight="bold"))
        tdee_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        row += 1
        
        # Lean mass and fat mass displays
        self.lean_mass_var = ctk.StringVar()
        self.lean_mass_var.set("Not calculated")
        lean_mass_frame = ctk.CTkFrame(self.summary_frame)
        lean_mass_frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        lean_mass_frame.grid_columnconfigure(0, weight=0)
        lean_mass_frame.grid_columnconfigure(1, weight=1)
        
        lean_mass_label = ctk.CTkLabel(lean_mass_frame, text="Lean Body Mass:", width=250, anchor="w")
        lean_mass_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        lean_mass_value = ctk.CTkLabel(lean_mass_frame, textvariable=self.lean_mass_var, font=ctk.CTkFont(weight="bold"))
        lean_mass_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        row += 1
        
        self.fat_mass_var = ctk.StringVar()
        self.fat_mass_var.set("Not calculated")
        fat_mass_frame = ctk.CTkFrame(self.summary_frame)
        fat_mass_frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        fat_mass_frame.grid_columnconfigure(0, weight=0)
        fat_mass_frame.grid_columnconfigure(1, weight=1)
        
        fat_mass_label = ctk.CTkLabel(fat_mass_frame, text="Fat Mass:", width=250, anchor="w")
        fat_mass_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        fat_mass_value = ctk.CTkLabel(fat_mass_frame, textvariable=self.fat_mass_var, font=ctk.CTkFont(weight="bold"))
        fat_mass_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        row += 1
        
        # Missing fields section 
        self.missing_fields_var = ctk.StringVar()
        self.missing_fields_var.set("")
        
        missing_fields_frame = ctk.CTkFrame(self.summary_frame)
        missing_fields_frame.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        missing_fields_frame.grid_columnconfigure(0, weight=1)
        missing_fields_frame.grid_rowconfigure(0, weight=0)
        missing_fields_frame.grid_rowconfigure(1, weight=0)
        
        missing_fields_label = ctk.CTkLabel(
            missing_fields_frame, 
            text="Missing Required Fields:", 
            font=ctk.CTkFont(weight="bold"),
            text_color="red"
        )
        missing_fields_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        missing_fields_value = ctk.CTkLabel(
            missing_fields_frame, 
            textvariable=self.missing_fields_var,
            wraplength=500,
            justify="left",
            text_color="red"
        )
        missing_fields_value.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        row += 1
        
        # Add calculate button
        calc_button_frame = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        calc_button_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
        
        calculate_btn = ctk.CTkButton(
            calc_button_frame, 
            text="Calculate Metrics", 
            command=self.calculate_metrics
        )
        calculate_btn.pack(pady=10)
        row += 1
        
        # Save/Update section
        row = self.create_section_header(self.summary_frame, "Save Profile Data", row)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, padx=10, pady=20, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Update profile button
        update_btn = ctk.CTkButton(
            button_frame, 
            text="Update User Profile", 
            command=self.save_user_profile
        )
        update_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # Save initial measurements button
        save_initial_btn = ctk.CTkButton(
            button_frame, 
            text="Save Initial Measurements", 
            command=self.save_initial_measurements
        )
        save_initial_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Back button
        back_btn = ctk.CTkButton(
            self.summary_frame, 
            text="Back: Nutrition & Lifestyle", 
            command=lambda: self.tab_view.set("Nutrition & Lifestyle")
        )
        back_btn.grid(row=row+1, column=0, padx=10, pady=10, sticky="w")
    
    def get_form_data(self):
        """Retrieve and validate data from the form"""
        data = {}
        missing_required = []
        
        # Required fields for RMR calculation
        required_fields = {
            "gender": "Gender",
            "dob": "Date of Birth",
            "height_feet": "Height (feet)",
            "height_inches": "Height (inches)",
            "initial_weight": "Starting Weight"
        }
        
        # Get all variables
        for name, var in self.variables.items():
            # Convert values based on variable type
            if isinstance(var, ctk.DoubleVar):
                try:
                    value = var.get()
                    data[name] = value if value != 0 else None  # Convert 0 to None for optional fields
                except:
                    data[name] = None
            elif isinstance(var, ctk.IntVar):
                try:
                    value = var.get()
                    data[name] = value if value != 0 else None  # Convert 0 to None for optional fields
                except:
                    data[name] = None
            elif isinstance(var, ctk.BooleanVar):
                try:
                    data[name] = var.get()
                except:
                    data[name] = False  # Default to False
            else:  # StringVar
                value = var.get()
                data[name] = value if value.strip() != "" else None
            
            # Check if required field is missing
            if name in required_fields and (data[name] is None or data[name] == ""):
                missing_required.append(required_fields[name])
        
        # Format missing fields
        if missing_required:
            missing_str = "Missing required fields: " + ", ".join(missing_required)
            self.missing_fields_var.set(missing_str)
        else:
            self.missing_fields_var.set("")
        
        return data, missing_required
    
    def calculate_metrics(self):
        """Calculate RMR, TDEE, lean mass, and fat mass"""
        data, missing_required = self.get_form_data()
        
        if missing_required:
            SimpleMessageBox.show_info("Missing Data", 
                                      "Cannot calculate metrics. Please fill in all required fields.")
            return
        
        try:
            # Normalize gender for calculation
            gender = data.get('gender', '').lower()
            if gender.startswith('m'):
                gender = 'm'
            elif gender.startswith('f'):
                gender = 'f'
            else:
                SimpleMessageBox.show_info("Invalid Data", "Please select Male or Female for gender.")
                return
            
            # Calculate RMR and TDEE
            profile_data = {
                'gender': gender,
                'dob': data.get('dob'),
                'current_weight': data.get('initial_weight'),
                'height_feet': data.get('height_feet'),
                'height_inches': data.get('height_inches'),
                'activity_factor': self.get_activity_factor(data.get('activity_level'))
            }
            
            try:
                rmr, tdee = get_rmr_and_tdee(profile_data)
                
                # Update display
                self.rmr_var.set(f"{rmr:.0f} calories/day")
                self.tdee_var.set(f"{tdee:.0f} calories/day")
                
                # Calculate lean mass and fat mass
                weight = data.get('initial_weight')
                bf_percent = data.get('initial_bf')
                
                if weight and bf_percent is not None:
                    fat_mass = weight * (bf_percent / 100)
                    lean_mass = weight - fat_mass
                    
                    self.lean_mass_var.set(f"{lean_mass:.1f} lbs")
                    self.fat_mass_var.set(f"{fat_mass:.1f} lbs")
                else:
                    self.lean_mass_var.set("Need weight and body fat %")
                    self.fat_mass_var.set("Need weight and body fat %")
                
            except ValidationError as e:
                SimpleMessageBox.show_info("Calculation Error", str(e))
                
        except Exception as e:
            SimpleMessageBox.show_info("Error", f"Failed to calculate metrics: {str(e)}")
            traceback.print_exc()
    
    def get_activity_factor(self, activity_level):
        """Convert activity level selection to activity factor"""
        # Extract numeric level from the string "1: Description"
        if not activity_level:
            return 1.2  # Default to sedentary
        
        try:
            if isinstance(activity_level, str) and ":" in activity_level:
                level = int(activity_level.split(":")[0].strip())
            else:
                level = int(float(activity_level))
            
            # Map level to activity factor
            activity_factors = {
                1: 1.2,   # Sedentary
                2: 1.375, # Lightly active
                3: 1.55,  # Moderately active
                4: 1.725, # Very active
                5: 1.9    # Extremely active
            }
            
            return activity_factors.get(level, 1.2)
            
        except (ValueError, TypeError):
            return 1.2  # Default to sedentary
    
    def save_user_profile(self):
        """Save user profile data to database"""
        data, missing_required = self.get_form_data()
        
        if missing_required:
            choice = SimpleMessageBox.show_question(
                "Missing Data", 
                "Some required fields are missing. Save anyway?",
                option_1="Save Anyway",
                option_2="Cancel"
            )
            if choice != "Save Anyway":
                return
        
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM user_profiles WHERE id = ?", (self.user_id,))
            user_exists = cursor.fetchone()
            
            if user_exists:
                # Update existing user
                update_cols = []
                values = []
                
                for field in [
                    "user_name", "gender", "dob", "height_feet", "height_inches", 
                    "email", "phone", "start_date", "end_date", "goal_weight", 
                    "goal_bf", "workout_type", "workout_days", "experience_level", 
                    "activity_level", "job_activity", "leisure_activity", "diet_type"
                ]:
                    if field in data:
                        update_cols.append(f"{field} = ?")
                        values.append(data.get(field))
                
                # Handle boolean fields
                for field in ["resistance_training", "is_athlete"]:
                    update_cols.append(f"{field} = ?")
                    values.append(1 if data.get(field) else 0)
                
                # Add user_id to values
                values.append(self.user_id)
                
                query = f"UPDATE user_profiles SET {', '.join(update_cols)} WHERE id = ?"
                cursor.execute(query, values)
                
            else:
                # Insert new user
                fields = [
                    "id", "user_name", "gender", "dob", "height_feet", "height_inches", 
                    "email", "phone", "start_date", "end_date", "goal_weight", 
                    "goal_bf", "resistance_training", "workout_type", "workout_days", 
                    "experience_level", "activity_level", "job_activity", 
                    "leisure_activity", "is_athlete", "diet_type"
                ]
                
                placeholders = ["?"] * len(fields)
                
                values = [
                    self.user_id,
                    data.get("user_name"),
                    data.get("gender"),
                    data.get("dob"),
                    data.get("height_feet"),
                    data.get("height_inches"),
                    data.get("email"),
                    data.get("phone"),
                    data.get("start_date"),
                    data.get("end_date"),
                    data.get("goal_weight"),
                    data.get("goal_bf"),
                    1 if data.get("resistance_training") else 0,
                    data.get("workout_type"),
                    data.get("workout_days"),
                    data.get("experience_level"),
                    data.get("activity_level"),
                    data.get("job_activity"),
                    data.get("leisure_activity"),
                    1 if data.get("is_athlete") else 0,
                    data.get("diet_type")
                ]
                
                query = f"INSERT INTO user_profiles ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(query, values)
            
            conn.commit()
            SimpleMessageBox.show_info("Success", "User profile saved successfully!")
            
        except Exception as e:
            SimpleMessageBox.show_info("Error", f"Failed to save user profile: {str(e)}")
            traceback.print_exc()
        finally:
            if conn:
                conn.close()
    
    def save_initial_measurements(self):
        """Save initial measurements to database"""
        data, missing_required = self.get_form_data()
        
        # Specific validation for initial measurements
        if not data.get("initial_weight"):
            SimpleMessageBox.show_info("Missing Data", "Initial weight is required.")
            return
        
        try:
            # Calculate derived values if possible
            weight = data.get("initial_weight")
            body_fat = data.get("initial_bf")
            
            # Calculate lean mass and fat mass
            lean_mass = None
            fat_mass = None
            
            if weight and body_fat is not None:
                fat_mass = weight * (body_fat / 100)
                lean_mass = weight - fat_mass
            
            # Try to calculate RMR and TDEE if we have the required data
            rmr = None
            tdee = None
            
            if all(data.get(field) for field in ["gender", "dob", "height_feet", "height_inches"]):
                try:
                    gender = data.get('gender', '').lower()
                    if gender.startswith('m'):
                        gender = 'm'
                    elif gender.startswith('f'):
                        gender = 'f'
                    
                    profile_data = {
                        'gender': gender,
                        'dob': data.get('dob'),
                        'current_weight': weight,
                        'height_feet': data.get('height_feet'),
                        'height_inches': data.get('height_inches'),
                        'activity_factor': self.get_activity_factor(data.get('activity_level'))
                    }
                    
                    rmr, tdee = get_rmr_and_tdee(profile_data)
                except:
                    pass
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Get the date - use start_date if available, otherwise today
            measurement_date = data.get("start_date")
            if not measurement_date:
                measurement_date = datetime.now().strftime("%Y-%m-%d")
            else:
                # Try to standardize MMDDYY to YYYY-MM-DD
                try:
                    date_obj = datetime.strptime(measurement_date, "%m%d%y")
                    measurement_date = date_obj.strftime("%Y-%m-%d")
                except:
                    measurement_date = datetime.now().strftime("%Y-%m-%d")
            
            # Check if initial measurements exist for this user
            cursor.execute(
                "SELECT id FROM initial_measurements WHERE user_id = ?", 
                (self.user_id,)
            )
            
            exists = cursor.fetchone()
            
            if exists:
                # Update existing record
                query = """
                UPDATE initial_measurements SET
                date = ?, weight = ?, body_fat = ?, waist = ?, hips = ?,
                chest = ?, neck = ?, left_arm = ?, right_arm = ?,
                left_thigh = ?, right_thigh = ?, lean_mass = ?, fat_mass = ?,
                rmr = ?, tdee = ?
                WHERE user_id = ?
                """
                
                cursor.execute(query, (
                    measurement_date, weight, body_fat,
                    data.get("waist"), data.get("hips"),
                    data.get("chest"), data.get("neck"),
                    data.get("left_arm"), data.get("right_arm"),
                    data.get("left_thigh"), data.get("right_thigh"),
                    lean_mass, fat_mass, rmr, tdee, 
                    self.user_id
                ))
                
            else:
                # Insert new record
                query = """
                INSERT INTO initial_measurements (
                    user_id, date, weight, body_fat, waist, hips,
                    chest, neck, left_arm, right_arm,
                    left_thigh, right_thigh, lean_mass, fat_mass,
                    rmr, tdee
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(query, (
                    self.user_id, measurement_date, weight, body_fat,
                    data.get("waist"), data.get("hips"),
                    data.get("chest"), data.get("neck"),
                    data.get("left_arm"), data.get("right_arm"),
                    data.get("left_thigh"), data.get("right_thigh"),
                    lean_mass, fat_mass, rmr, tdee
                ))
            
            conn.commit()
            SimpleMessageBox.show_info("Success", "Initial measurements saved successfully!")
            
            # Update the calculated metrics display
            if rmr:
                self.rmr_var.set(f"{rmr:.0f} calories/day")
            if tdee:
                self.tdee_var.set(f"{tdee:.0f} calories/day")
            if lean_mass:
                self.lean_mass_var.set(f"{lean_mass:.1f} lbs")
            if fat_mass:
                self.fat_mass_var.set(f"{fat_mass:.1f} lbs")
            
        except Exception as e:
            SimpleMessageBox.show_info("Error", f"Failed to save initial measurements: {str(e)}")
            traceback.print_exc()
        finally:
            if conn:
                conn.close()
    
    def load_user_data(self):
        """Load existing user data from database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Load user profile data
            cursor.execute("SELECT * FROM user_profiles WHERE id = ?", (self.user_id,))
            user_data = cursor.fetchone()
            
            if user_data:
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                user_dict = dict(zip(columns, user_data))
                
                # Set form variables
                for field, value in user_dict.items():
                    if field in self.variables:
                        var = self.variables[field]
                        
                        # Handle different variable types
                        if isinstance(var, ctk.BooleanVar):
                            var.set(bool(value))
                        elif isinstance(var, ctk.DoubleVar):
                            var.set(float(value) if value is not None else 0.0)
                        elif isinstance(var, ctk.IntVar):
                            var.set(int(value) if value is not None else 0)
                        else:  # StringVar
                            var.set(str(value) if value is not None else "")
            
            # Load initial measurements
            cursor.execute(
                "SELECT * FROM initial_measurements WHERE user_id = ?", 
                (self.user_id,)
            )
            
            initial_data = cursor.fetchone()
            
            if initial_data:
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                initial_dict = dict(zip(columns, initial_data))
                
                # Set initial measurement fields
                if "weight" in initial_dict and "initial_weight" in self.variables:
                    self.variables["initial_weight"].set(float(initial_dict["weight"]) if initial_dict["weight"] else 0.0)
                
                if "body_fat" in initial_dict and "initial_bf" in self.variables:
                    self.variables["initial_bf"].set(float(initial_dict["body_fat"]) if initial_dict["body_fat"] else 0.0)
                
                # Additional measurements
                for field in ["waist", "hips", "chest", "neck", "left_arm", "right_arm", "left_thigh", "right_thigh"]:
                    if field in initial_dict and field in self.variables:
                        self.variables[field].set(float(initial_dict[field]) if initial_dict[field] else 0.0)
                
                # Update calculated fields
                if "rmr" in initial_dict and initial_dict["rmr"]:
                    self.rmr_var.set(f"{float(initial_dict['rmr']):.0f} calories/day")
                
                if "tdee" in initial_dict and initial_dict["tdee"]:
                    self.tdee_var.set(f"{float(initial_dict['tdee']):.0f} calories/day")
                
                if "lean_mass" in initial_dict and initial_dict["lean_mass"]:
                    self.lean_mass_var.set(f"{float(initial_dict['lean_mass']):.1f} lbs")
                
                if "fat_mass" in initial_dict and initial_dict["fat_mass"]:
                    self.fat_mass_var.set(f"{float(initial_dict['fat_mass']):.1f} lbs")
            
            conn.close()
            
        except Exception as e:
            print(f"Error loading user data: {e}")
            traceback.print_exc()

# If run directly, start the application
if __name__ == "__main__":
    app = EnhancedProfileApp()
    app.run()
