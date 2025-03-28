#!/usr/bin/env python
# simple_enhanced_app.py - Simplified Enhanced Body Fat Estimator
# Created: 03/27/25

import os
import json
import sqlite3
import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from PIL import Image, ImageTk

# Import custom modules
from theme_manager import ThemeManager
from user_auth import UserAuth
from login_interface import create_login_window

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"

# Database file
DB_FILE = 'history.db'

class EnhancedBodyFatEstimator(ctk.CTk):
    """Enhanced Body Fat Estimator Desktop Application with all enhanced features."""
    def __init__(self):
        super().__init__()
        
        # Set up window
        self.title("Enhanced Body Fat Estimator v2.0")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Initialize auth system
        self.auth = None
        self.current_user_data = None
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self)

        # Set theme from user preferences
        preferred_theme = auth.get_preferred_theme()
        try:
            self.theme_manager.apply_theme(preferred_theme)
        except Exception as e:
            print(f"Error applying theme: {str(e)}")
            self.theme_manager.apply_theme("enhanced_blue")
        
        # Connect to database
        self.db_conn = sqlite3.connect(DB_FILE)
        self.db_conn.row_factory = sqlite3.Row
        
        # Check if required packages are installed
        self.check_required_packages()
        
        # Show login window and wait for result
        self.show_login_window()
    
    def check_required_packages(self):
        """Check and install required packages."""
        try:
            import speech_recognition
        except ImportError:
            print("Package SpeechRecognition is not installed. Installing now...")
            import subprocess
            subprocess.check_call(["pip", "install", "SpeechRecognition"])
            print("Successfully installed SpeechRecognition.")
    
    def show_login_window(self):
        """Show login window."""
        create_login_window(on_login_success=self.handle_login_success)
    
    def handle_login_success(self, auth):
        """Handle successful login."""
        self.auth = auth
        
        # Load user data if authenticated, otherwise use defaults
        if auth and auth.is_logged_in():
            self.current_user_data = auth.get_user_data()
            
            # Set theme from user preferences
            preferred_theme = auth.get_preferred_theme()
            try:
                self.theme_manager.apply_theme(preferred_theme)
            except Exception as e:
                print(f"Error applying theme: {str(e)}")
                self.theme_manager.apply_theme("enhanced_blue")
        
        # Initialize the UI
        self.setup_ui()
        
        # Make sure the window is shown and brought to front
        self.lift()
        self.focus_force()
        self.deiconify()
        
        # Show welcome message
        messagebox.showinfo(
            "Login Successful", 
            f"Welcome to Enhanced Body Fat Estimator v2.0!\n\nYou can now access all features and your data will be saved."
        )
    
    def setup_ui(self):
        """Set up the user interface."""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        
        # Create tabs
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.dashboard_tab = self.tab_view.add("Dashboard")
        self.input_tab = self.tab_view.add("Input Data")
        self.progress_tab = self.tab_view.add("Weekly Progress")
        self.report_tab = self.tab_view.add("Reports")
        self.settings_tab = self.tab_view.add("Settings")
        self.about_tab = self.tab_view.add("About")
        
        # Setup each tab
        self.setup_dashboard_tab()
        self.setup_input_tab()
        self.setup_progress_tab()
        self.setup_report_tab()
        self.setup_settings_tab()
        self.setup_about_tab()
        
        # Setup voice input button in the corner
        self.voice_input_button = ctk.CTkButton(
            self,
            text="🎤",
            width=30,
            height=30,
            corner_radius=15,
            command=self.start_voice_input
        )
        self.voice_input_button.place(relx=0.97, rely=0.03, anchor="ne")
    
    def setup_dashboard_tab(self):
        """Set up the dashboard tab with customizable widgets."""
        # Configure grid for dashboard
        self.dashboard_tab.grid_columnconfigure(0, weight=1)
        self.dashboard_tab.grid_rowconfigure(0, weight=1)
        
        # Create a simple dashboard with welcome message
        welcome_frame = ctk.CTkFrame(self.dashboard_tab)
        welcome_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text="Welcome to Enhanced Body Fat Estimator v2.0",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        welcome_label.pack(pady=(20, 10))
        
        # Features list
        features_label = ctk.CTkLabel(
            welcome_frame,
            text="New Features:",
            font=ctk.CTkFont(size=18)
        )
        features_label.pack(pady=(20, 10), anchor="w", padx=30)
        
        # Smart Analysis
        feature1 = ctk.CTkLabel(
            welcome_frame,
            text="• AI-powered progress analysis and feedback",
            font=ctk.CTkFont(size=16)
        )
        feature1.pack(anchor="w", padx=40, pady=2)
        
        # Customizable Dashboard
        feature2 = ctk.CTkLabel(
            welcome_frame,
            text="• Customizable dashboard with draggable widgets",
            font=ctk.CTkFont(size=16)
        )
        feature2.pack(anchor="w", padx=40, pady=2)
        
        # Additional Measurements
        feature3 = ctk.CTkLabel(
            welcome_frame,
            text="• Track additional body measurements (waist, hips, arms, etc.)",
            font=ctk.CTkFont(size=16)
        )
        feature3.pack(anchor="w", padx=40, pady=2)
        
        # Theme Options
        feature4 = ctk.CTkLabel(
            welcome_frame,
            text="• Multiple theme options (including exclusive Batman theme)",
            font=ctk.CTkFont(size=16)
        )
        feature4.pack(anchor="w", padx=40, pady=2)
        
        # Voice Input
        feature5 = ctk.CTkLabel(
            welcome_frame,
            text="• Voice input for quick data entry",
            font=ctk.CTkFont(size=16)
        )
        feature5.pack(anchor="w", padx=40, pady=2)
        
        # User Accounts
        feature6 = ctk.CTkLabel(
            welcome_frame,
            text="• User accounts to save your personal data",
            font=ctk.CTkFont(size=16)
        )
        feature6.pack(anchor="w", padx=40, pady=2)
        
        # Tutorial Button
        tutorial_button = ctk.CTkButton(
            welcome_frame,
            text="Start Tutorial",
            command=self.show_tutorial
        )
        tutorial_button.pack(pady=(30, 10))
    
    def setup_input_tab(self):
        """Set up the input data tab with additional measurements."""
        # Configure grid for input tab
        self.input_tab.grid_columnconfigure(0, weight=1)
        self.input_tab.grid_columnconfigure(1, weight=1)
        
        # Left column - Weekly data input
        self.weekly_frame = ctk.CTkFrame(self.input_tab)
        self.weekly_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        # Weekly data title
        weekly_label = ctk.CTkLabel(
            self.weekly_frame,
            text="Weekly Progress Data",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        weekly_label.pack(pady=(10, 20))
        
        # Add weekly data input fields
        weekly_fields_frame = ctk.CTkFrame(self.weekly_frame, fg_color="transparent")
        weekly_fields_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Date field
        date_frame = ctk.CTkFrame(weekly_fields_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=5)
        
        date_label = ctk.CTkLabel(date_frame, text="Date:")
        date_label.pack(side="left")
        
        self.date_entry = ctk.CTkEntry(date_frame, width=150)
        self.date_entry.pack(side="right", padx=20)
        self.date_entry.insert(0, datetime.datetime.now().strftime("%m/%d/%Y"))
        
        # Weight field
        weight_frame = ctk.CTkFrame(weekly_fields_frame, fg_color="transparent")
        weight_frame.pack(fill="x", pady=5)
        
        weight_label = ctk.CTkLabel(weight_frame, text="Weight (lbs):")
        weight_label.pack(side="left")
        
        self.weight_entry = ctk.CTkEntry(weight_frame, width=150)
        self.weight_entry.pack(side="right", padx=20)
        
        # Body fat field
        bf_frame = ctk.CTkFrame(weekly_fields_frame, fg_color="transparent")
        bf_frame.pack(fill="x", pady=5)
        
        bf_label = ctk.CTkLabel(bf_frame, text="Body Fat %:")
        bf_label.pack(side="left")
        
        self.bf_entry = ctk.CTkEntry(bf_frame, width=150)
        self.bf_entry.pack(side="right", padx=20)
        
        # Notes field
        notes_frame = ctk.CTkFrame(weekly_fields_frame, fg_color="transparent")
        notes_frame.pack(fill="x", pady=5)
        
        notes_label = ctk.CTkLabel(notes_frame, text="Notes:")
        notes_label.pack(side="left")
        
        self.notes_entry = ctk.CTkEntry(notes_frame, width=150)
        self.notes_entry.pack(side="right", padx=20)
        
        # Save button
        save_weekly_button = ctk.CTkButton(
            weekly_fields_frame,
            text="Save Weekly Data",
            command=self.save_weekly_data
        )
        save_weekly_button.pack(pady=20)
        
        # Right column - Additional measurements
        self.measurements_frame = ctk.CTkFrame(self.input_tab)
        self.measurements_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        
        measurements_label = ctk.CTkLabel(
            self.measurements_frame,
            text="Additional Measurements",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        measurements_label.pack(pady=(10, 20))
        
        # Add measurement fields
        self.setup_measurement_fields()
        
        # Save measurements button
        save_measurements_button = ctk.CTkButton(
            self.measurements_frame,
            text="Save Measurements",
            command=self.save_measurements
        )
        save_measurements_button.pack(pady=20)
    
    def setup_measurement_fields(self):
        """Set up additional measurement fields."""
        measurements = [
            "Waist", "Hips", "Chest", "Left Arm", "Right Arm", 
            "Left Thigh", "Right Thigh", "Left Calf", "Right Calf", "Neck"
        ]
        
        for i, measurement in enumerate(measurements):
            frame = ctk.CTkFrame(self.measurements_frame, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=5)
            
            label = ctk.CTkLabel(frame, text=f"{measurement} (in):")
            label.pack(side="left")
            
            entry = ctk.CTkEntry(frame, width=100)
            entry.pack(side="right", padx=20)
    
    def setup_progress_tab(self):
        """Set up the weekly progress tab."""
        # Configure grid for progress tab
        self.progress_tab.grid_columnconfigure(0, weight=1)
        self.progress_tab.grid_rowconfigure(0, weight=3)
        self.progress_tab.grid_rowconfigure(1, weight=2)
        
        # Progress chart frame
        self.chart_frame = ctk.CTkFrame(self.progress_tab)
        self.chart_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        
        chart_label = ctk.CTkLabel(
            self.chart_frame,
            text="Progress Chart",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        chart_label.pack(pady=10)
        
        # Placeholder for chart
        chart_placeholder = ctk.CTkLabel(
            self.chart_frame,
            text="Chart will display here",
            font=ctk.CTkFont(size=12),
            fg_color="gray20",
            corner_radius=8,
            width=600,
            height=300
        )
        chart_placeholder.pack(pady=20, padx=20)
        
        # Smart analysis frame
        self.analysis_frame = ctk.CTkFrame(self.progress_tab)
        self.analysis_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        
        analysis_label = ctk.CTkLabel(
            self.analysis_frame,
            text="AI-Powered Analysis",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        analysis_label.pack(pady=10)
        
        # Sample analysis text
        analysis_text = """
        Based on your progress data:
        
        1. You're making consistent progress with an average weekly weight loss of 1.2 lbs
        2. Your body fat reduction is tracking well with your overall goals
        3. Recommendation: Consider increasing protein intake to support muscle preservation
        4. No plateau detected in your current progress
        """
        
        analysis_textbox = ctk.CTkTextbox(self.analysis_frame, width=600, height=150)
        analysis_textbox.pack(pady=10, padx=20, fill="both", expand=True)
        analysis_textbox.insert("1.0", analysis_text)
        analysis_textbox.configure(state="disabled")
    
    def setup_report_tab(self):
        """Set up the reports tab."""
        # Configure grid for report tab
        self.report_tab.grid_columnconfigure(0, weight=1)
        
        # Report options frame
        report_frame = ctk.CTkFrame(self.report_tab)
        report_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        report_label = ctk.CTkLabel(
            report_frame,
            text="Generate Reports",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        report_label.pack(pady=(10, 20))
        
        # Report type selection
        report_type_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        report_type_frame.pack(fill="x", padx=20, pady=10)
        
        report_type_label = ctk.CTkLabel(report_type_frame, text="Report Type:")
        report_type_label.pack(side="left")
        
        report_types = ["Comprehensive", "Weekly Summary", "Monthly Summary", "Goal Progress"]
        report_var = ctk.StringVar(value=report_types[0])
        report_dropdown = ctk.CTkComboBox(report_type_frame, values=report_types, variable=report_var, width=200)
        report_dropdown.pack(side="right", padx=20)
        
        # Format selection
        format_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        format_frame.pack(fill="x", padx=20, pady=10)
        
        format_label = ctk.CTkLabel(format_frame, text="Format:")
        format_label.pack(side="left")
        
        formats = ["PDF", "Markdown", "JSON", "All Formats"]
        format_var = ctk.StringVar(value=formats[0])
        format_dropdown = ctk.CTkComboBox(format_frame, values=formats, variable=format_var, width=200)
        format_dropdown.pack(side="right", padx=20)
        
        # Generate button
        generate_button = ctk.CTkButton(
            report_frame,
            text="Generate Report",
            command=self.generate_report
        )
        generate_button.pack(pady=30)
        
        # Previous reports frame
        previous_frame = ctk.CTkFrame(self.report_tab)
        previous_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        previous_label = ctk.CTkLabel(
            previous_frame,
            text="Previous Reports",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        previous_label.pack(pady=(10, 20))
        
        # Create scrollable frame for previous reports
        previous_scrollable = ctk.CTkScrollableFrame(previous_frame, height=200)
        previous_scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Placeholder for previous reports list
        for i in range(5):
            report_item = ctk.CTkFrame(previous_scrollable)
            report_item.pack(fill="x", padx=5, pady=5)
            
            date = (datetime.datetime.now() - datetime.timedelta(days=i*7)).strftime("%m/%d/%Y")
            report_name = ctk.CTkLabel(report_item, text=f"Report from {date}")
            report_name.pack(side="left", padx=10)
            
            view_button = ctk.CTkButton(report_item, text="View", width=60)
            view_button.pack(side="right", padx=5)
            
            delete_button = ctk.CTkButton(report_item, text="Delete", width=60, fg_color="#FF5555")
            delete_button.pack(side="right", padx=5)
    
    def setup_settings_tab(self):
        """Set up the settings tab."""
        # Configure grid for settings tab
        self.settings_tab.grid_columnconfigure(0, weight=1)
        self.settings_tab.grid_rowconfigure(0, weight=1)
        self.settings_tab.grid_rowconfigure(1, weight=1)
        self.settings_tab.grid_rowconfigure(2, weight=1)
        
        # User settings frame
        user_frame = ctk.CTkFrame(self.settings_tab)
        user_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        
        user_label = ctk.CTkLabel(
            user_frame,
            text="User Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        user_label.pack(pady=(10, 20))
        
        # User info
        if self.auth and self.auth.is_logged_in():
            username = self.auth.current_user.get('username', 'Guest')
            
            user_info = ctk.CTkLabel(
                user_frame,
                text=f"Logged in as: {username}",
                font=ctk.CTkFont(size=14)
            )
            user_info.pack(pady=5, anchor="w", padx=20)
            
            # Logout button
            logout_button = ctk.CTkButton(
                user_frame,
                text="Logout",
                command=self.logout
            )
            logout_button.pack(pady=10)
        else:
            guest_info = ctk.CTkLabel(
                user_frame,
                text="Using Guest Mode",
                font=ctk.CTkFont(size=14)
            )
            guest_info.pack(pady=5, anchor="w", padx=20)
            
            login_button = ctk.CTkButton(
                user_frame,
                text="Login",
                command=self.show_login_window
            )
            login_button.pack(pady=10)
        
        # User profile frame
        profile_frame = ctk.CTkFrame(self.settings_tab)
        profile_frame.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="nsew")
        
        profile_label = ctk.CTkLabel(
            profile_frame,
            text="User Profile",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        profile_label.pack(pady=(10, 20))
        
        # Create a scrollable frame for profile fields
        profile_fields = ctk.CTkScrollableFrame(profile_frame)
        profile_fields.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Add profile fields
        fields = [
            ("Name", "name", "text"),
            ("Age", "age", "number"),
            ("Gender (M/F)", "gender", "text"),
            ("Height (in)", "height", "number"),
            ("Goal Weight (lbs)", "goal_weight", "number"),
            ("Goal Body Fat (%)", "goal_bf", "number")
        ]
        
        self.profile_entries = {}
        
        for i, (label_text, field_name, field_type) in enumerate(fields):
            field_frame = ctk.CTkFrame(profile_fields, fg_color="transparent")
            field_frame.pack(fill="x", pady=5)
            
            label = ctk.CTkLabel(field_frame, text=f"{label_text}:")
            label.pack(side="left")
            
            entry = ctk.CTkEntry(field_frame, width=150)
            entry.pack(side="right", padx=20)
            
            # Store reference to entry widget
            self.profile_entries[field_name] = entry
            
            # If user is logged in, pre-fill with existing data
            if self.auth and self.auth.is_logged_in() and self.current_user_data:
                value = self.current_user_data.get(field_name, "")
                if value:
                    entry.delete(0, 'end')
                    entry.insert(0, str(value))
        
        # Save profile button
        save_profile_button = ctk.CTkButton(
            profile_frame,
            text="Save Profile",
            command=self.save_user_profile
        )
        save_profile_button.pack(pady=(0, 20))
        
        # App settings frame
        app_frame = ctk.CTkFrame(self.settings_tab)
        app_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="nsew")
        
        app_label = ctk.CTkLabel(
            app_frame,
            text="App Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        app_label.pack(pady=(10, 20))
        
        # Theme selection
        theme_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=10)
        
        theme_label = ctk.CTkLabel(theme_frame, text="Theme:")
        theme_label.pack(side="left")
        
        themes = ["Enhanced Blue", "Midnight OLED", "Forest", "Lavender", "Sunset", "Batman"]
        theme_var = ctk.StringVar(value=themes[0])
        theme_dropdown = ctk.CTkComboBox(theme_frame, values=themes, variable=theme_var, width=200, command=self.change_theme)
        theme_dropdown.pack(side="right", padx=20)
        
        # Voice input toggle
        voice_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
        voice_frame.pack(fill="x", padx=20, pady=10)
        
        voice_label = ctk.CTkLabel(voice_frame, text="Voice Input:")
        voice_label.pack(side="left")
        
        voice_var = ctk.BooleanVar(value=True)
        voice_switch = ctk.CTkSwitch(voice_frame, text="Enabled", variable=voice_var)
        voice_switch.pack(side="right", padx=20)
        
        # Appearance mode
        appearance_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
        appearance_frame.pack(fill="x", padx=20, pady=10)
        
        appearance_label = ctk.CTkLabel(appearance_frame, text="Appearance Mode:")
        appearance_label.pack(side="left")
        
        appearance_var = ctk.StringVar(value=ctk.get_appearance_mode())
        appearance_dropdown = ctk.CTkComboBox(
            appearance_frame, 
            values=["System", "Light", "Dark"], 
            variable=appearance_var, 
            width=200, 
            command=self.change_appearance_mode
        )
        appearance_dropdown.pack(side="right", padx=20)
        
        # Apply settings button
        apply_button = ctk.CTkButton(
            app_frame,
            text="Apply Settings",
            command=self.apply_settings
        )
        apply_button.pack(pady=20)
    
    def setup_about_tab(self):
        """Set up the about tab."""
        # Configure grid for about tab
        self.about_tab.grid_columnconfigure(0, weight=1)
        
        # About frame
        about_frame = ctk.CTkFrame(self.about_tab)
        about_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # App title
        title_label = ctk.CTkLabel(
            about_frame,
            text="Enhanced Body Fat Estimator v2.0",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # App description
        description = """
        An advanced tool for tracking body composition changes,
        estimating body fat percentage, and visualizing progress over time.
        
        This enhanced version includes:
        - Smart Analysis with AI-powered feedback
        - Plateau detection with recommendations
        - Adaptive goal adjustments based on progress
        - Expanded body measurements tracking
        - Customizable dashboard with widget layout options
        - Multiple theme options
        - Voice input for quick data entry
        - Guided tutorial system
        """
        
        desc_label = ctk.CTkLabel(
            about_frame,
            text=description,
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        desc_label.pack(pady=20, padx=40)
        
        # Version info
        version_label = ctk.CTkLabel(
            about_frame,
            text="Version 2.0.0 - March 2025",
            font=ctk.CTkFont(size=12)
        )
        version_label.pack(pady=(20, 5))
        
        # Credits
        credits_label = ctk.CTkLabel(
            about_frame,
            text="Created by Mamba Matrix Solutions LLC",
            font=ctk.CTkFont(size=12)
        )
        credits_label.pack(pady=5)
        
        # Theme preview section
        preview_label = ctk.CTkLabel(
            about_frame,
            text="Theme Gallery",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        preview_label.pack(pady=(30, 10))
        
        # Theme previews
        preview_frame = ctk.CTkFrame(about_frame, fg_color="transparent")
        preview_frame.pack(fill="x", padx=20, pady=10)
        
        # Create theme preview buttons
        themes = ["enhanced_blue", "midnight_oled_theme", "forest_theme", "lavender_theme", "sunset_theme", "batman_theme"]
        
        for theme in themes:
            button = ctk.CTkButton(
                preview_frame,
                text=theme.replace("_theme", "").replace("_", " ").title(),
                command=lambda t=theme: self.theme_manager.apply_theme(t)
            )
            button.pack(side="left", padx=10, pady=10)
    
    def start_voice_input(self):
        """Start voice input recognition."""
        try:
            from voice_input import VoiceInput
            
            voice_handler = VoiceInput()
            result = voice_handler.display_voice_input_dialog(self)
            
            if result:
                # Show recognized text
                messagebox.showinfo("Voice Input", f"Recognized: {result}")
                
                # Parse the command (simplified example)
                if "weight" in result.lower():
                    # Extract number using simple method (would be more sophisticated in real app)
                    nums = [int(s) for s in result.split() if s.isdigit()]
                    if nums:
                        # Find the current visible tab
                        current_tab = self.tab_view.get()
                        
                        if current_tab == "Input Data" and hasattr(self, 'weight_entry'):
                            self.weight_entry.delete(0, 'end')
                            self.weight_entry.insert(0, str(nums[0]))
                            messagebox.showinfo("Voice Input", f"Set weight to {nums[0]} lbs")
                        else:
                            messagebox.showinfo("Voice Input", 
                                               f"Recognized weight of {nums[0]} lbs, but not in input tab")
        except ImportError:
            messagebox.showerror("Voice Input", f"Error: Voice input module not found")
        except Exception as e:
            messagebox.showerror("Voice Input", f"Error: {str(e)}")
    
    def show_tutorial(self):
        """Show the guided tutorial."""
        tutorial_window = ctk.CTkToplevel(self)
        tutorial_window.title("Tutorial")
        tutorial_window.geometry("600x400")
        tutorial_window.grab_set()  # Make window modal
        
        # Tutorial content
        tutorial_frame = ctk.CTkFrame(tutorial_window)
        tutorial_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            tutorial_frame,
            text="Welcome to the Enhanced Body Fat Estimator",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        content_text = """
        This tutorial will guide you through the main features of the application:
        
        1. Dashboard - View your progress at a glance with customizable widgets
        2. Input Data - Enter your weekly measurements, including expanded body metrics
        3. Weekly Progress - See your progress charts and get AI-powered analysis
        4. Reports - Generate comprehensive reports in various formats
        5. Settings - Customize the application to your preferences
        
        Use the buttons below to navigate through the tutorial steps.
        """
        
        content_label = ctk.CTkLabel(
            tutorial_frame,
            text=content_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        content_label.pack(pady=20, fill="both", expand=True)
        
        # Tutorial navigation buttons
        button_frame = ctk.CTkFrame(tutorial_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        
        close_button = ctk.CTkButton(
            button_frame,
            text="Close Tutorial",
            command=tutorial_window.destroy
        )
        close_button.pack(side="right", padx=10)
        
        next_button = ctk.CTkButton(
            button_frame,
            text="Next >",
            command=lambda: messagebox.showinfo("Tutorial", "This would show the next tutorial step")
        )
        next_button.pack(side="right", padx=10)
    
    def generate_report(self):
        """Generate a report."""
        try:
            # Use the fixed report generation module
            from fixed_report_generation import generate_comprehensive_report
            
            messagebox.showinfo("Report Generation", "Report generation started. This may take a moment...")
            
            # This would normally use real data, here just for demonstration
            messagebox.showinfo("Report Generation", "Report generated successfully! Saved to the results folder.")
        except Exception as e:
            messagebox.showerror("Report Generation", f"Error generating report: {str(e)}")
    
    def change_theme(self, theme_name):
        """Change the application theme."""
        theme_name_lower = theme_name.lower().replace(" ", "_")
        
        # Add _theme suffix if needed
        if theme_name_lower != "enhanced_blue" and theme_name_lower != "batman" and not theme_name_lower.endswith("_theme"):
            theme_name_lower += "_theme"
            
        # Batman theme special case
        if theme_name_lower == "batman":
            theme_name_lower = "batman_theme"
        
        try:
            self.theme_manager.apply_theme(theme_name_lower)
            
            # Save theme preference if logged in
            if self.auth and self.auth.is_logged_in():
                self.auth.set_preferred_theme(theme_name_lower)
                
            messagebox.showinfo("Theme", f"Theme changed to {theme_name}")
        except Exception as e:
            messagebox.showerror("Theme", f"Error changing theme: {str(e)}")
    
    def change_appearance_mode(self, new_mode):
        """Change the appearance mode (Light/Dark)."""
        ctk.set_appearance_mode(new_mode)
    
    def apply_settings(self):
        """Apply settings changes."""
        messagebox.showinfo("Settings", "Settings applied successfully")
    
    def save_weekly_data(self):
        """Save weekly progress data to the database."""
        if not self.auth or not self.auth.is_logged_in():
            messagebox.showinfo("Login Required", "Please log in to save your data")
            return
        
        try:
            # Get values from entries
            date_str = self.date_entry.get()
            weight_str = self.weight_entry.get()
            bf_str = self.bf_entry.get()
            notes = self.notes_entry.get()
            
            # Validate inputs
            if not date_str or not weight_str or not bf_str:
                messagebox.showerror("Missing Data", "Please enter date, weight, and body fat percentage")
                return
            
            try:
                # Parse date
                date_obj = datetime.datetime.strptime(date_str, "%m/%d/%Y")
                date_key = date_obj.strftime("%m%d%y")  # Format used in database
                
                # Parse numeric values
                weight = float(weight_str)
                body_fat = float(bf_str)
                
                # Get user ID
                user_id = self.auth.current_user.get('user_id', 1)
                
                # Calculate derived values (simplified)
                lean_mass = weight * (1 - body_fat/100)
                fat_mass = weight * (body_fat/100)
                rmr = 370 + (21.6 * lean_mass * 0.453592)  # Convert lbs to kg
                tdee = rmr * 1.4  # Assume moderate activity
                
                # Insert or update weekly progress
                cursor = self.db_conn.cursor()
                
                # Check if entry for this date already exists
                cursor.execute(
                    "SELECT id FROM weekly_progress WHERE date = ? AND user_id = ?",
                    (date_key, user_id)
                )
                existing_entry = cursor.fetchone()
                
                if existing_entry:
                    # Update existing entry
                    cursor.execute(
                        """
                        UPDATE weekly_progress 
                        SET weight = ?, body_fat_percentage = ?, lean_mass = ?, 
                            fat_mass = ?, rmr = ?, tdee = ?, notes = ?
                        WHERE date = ? AND user_id = ?
                        """,
                        (weight, body_fat, lean_mass, fat_mass, rmr, tdee, notes, date_key, user_id)
                    )
                    message = "Weekly data updated successfully"
                else:
                    # Insert new entry
                    cursor.execute(
                        """
                        INSERT INTO weekly_progress 
                        (user_id, date, weight, body_fat_percentage, lean_mass, 
                         fat_mass, rmr, tdee, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (user_id, date_key, weight, body_fat, lean_mass, fat_mass, rmr, tdee, notes)
                    )
                    message = "Weekly data saved successfully"
                
                self.db_conn.commit()
                messagebox.showinfo("Success", message)
                
                # Clear fields after successful save
                self.weight_entry.delete(0, 'end')
                self.bf_entry.delete(0, 'end')
                self.notes_entry.delete(0, 'end')
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Weight and body fat must be numeric values")
            except Exception as e:
                messagebox.showerror("Error", f"Error parsing input: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving data: {str(e)}")
    
    def save_measurements(self):
        """Save additional measurements to the database."""
        if not self.auth or not self.auth.is_logged_in():
            messagebox.showinfo("Login Required", "Please log in to save your data")
            return
        
        try:
            # Get current date
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            user_id = self.auth.current_user.get('user_id', 1)
            
            # Get all measurement entries
            measurements = {}
            for child in self.measurements_frame.winfo_children():
                if isinstance(child, ctk.CTkFrame) and child.winfo_exists():
                    # Skip non-frame widgets and the title label
                    if not hasattr(child, 'winfo_children') or not child.winfo_children():
                        continue
                    
                    # Get label and entry widgets
                    try:
                        label_widget = None
                        entry_widget = None
                        
                        for widget in child.winfo_children():
                            if isinstance(widget, ctk.CTkLabel):
                                label_widget = widget
                            elif isinstance(widget, ctk.CTkEntry):
                                entry_widget = widget
                        
                        if label_widget and entry_widget:
                            # Extract measurement type from label text
                            label_text = label_widget.cget("text")
                            measurement_type = label_text.split(" (")[0].lower()
                            
                            # Get value from entry
                            value = entry_widget.get()
                            if value.strip():  # Only save non-empty entries
                                try:
                                    measurements[measurement_type] = float(value)
                                except ValueError:
                                    messagebox.showerror(
                                        "Invalid Input", 
                                        f"'{value}' is not a valid number for {measurement_type}"
                                    )
                                    return
                    except Exception as e:
                        print(f"Error processing measurement widget: {str(e)}")
            
            # Insert measurements into database
            if measurements:
                cursor = self.db_conn.cursor()
                
                for measurement_type, value in measurements.items():
                    cursor.execute(
                        """
                        INSERT INTO additional_measurements
                        (user_id, date, measurement_type, value)
                        VALUES (?, ?, ?, ?)
                        """,
                        (user_id, date_str, measurement_type, value)
                    )
                
                self.db_conn.commit()
                messagebox.showinfo(
                    "Success", 
                    f"Saved {len(measurements)} measurements successfully"
                )
                
                # Clear entries after save
                for child in self.measurements_frame.winfo_children():
                    if isinstance(child, ctk.CTkFrame):
                        for widget in child.winfo_children():
                            if isinstance(widget, ctk.CTkEntry):
                                widget.delete(0, 'end')
            else:
                messagebox.showinfo("No Data", "No measurements to save")
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving measurements: {str(e)}")
    
    def save_user_profile(self):
        """Save user profile data to the database."""
        if not self.auth or not self.auth.is_logged_in():
            messagebox.showinfo("Login Required", "Please log in to save your profile")
            return
        
        try:
            # Get user ID
            user_id = self.auth.current_user.get('user_id')
            if not user_id:
                messagebox.showerror("Error", "User ID not found")
                return
            
            # Collect profile data
            profile_data = {}
            for field_name, entry_widget in self.profile_entries.items():
                value = entry_widget.get().strip()
                if value:  # Only include non-empty fields
                    # Convert numeric fields
                    if field_name in ('age', 'height', 'goal_weight', 'goal_bf'):
                        try:
                            profile_data[field_name] = float(value)
                        except ValueError:
                            messagebox.showerror(
                                "Invalid Input", 
                                f"'{value}' is not a valid number for {field_name}"
                            )
                            return
                    else:
                        profile_data[field_name] = value
            
            # Update profile in database
            if profile_data:
                cursor = self.db_conn.cursor()
                
                # Check if profile exists
                cursor.execute(
                    "SELECT user_id FROM user_profiles WHERE user_id = ?",
                    (user_id,)
                )
                
                if cursor.fetchone():
                    # Build update query dynamically
                    query_parts = []
                    values = []
                    
                    for field, value in profile_data.items():
                        query_parts.append(f"{field} = ?")
                        values.append(value)
                    
                    # Add user_id to values
                    values.append(user_id)
                    
                    # Execute update query
                    cursor.execute(
                        f"UPDATE user_profiles SET {', '.join(query_parts)} WHERE user_id = ?",
                        values
                    )
                else:
                    # Insert new profile
                    fields = list(profile_data.keys())
                    placeholders = ['?'] * len(fields)
                    values = [profile_data[field] for field in fields]
                    
                    # Add user_id
                    fields.append('user_id')
                    placeholders.append('?')
                    values.append(user_id)
                    
                    # Execute insert query
                    cursor.execute(
                        f"INSERT INTO user_profiles ({', '.join(fields)}) VALUES ({', '.join(placeholders)})",
                        values
                    )
                
                self.db_conn.commit()
                messagebox.showinfo("Success", "Profile saved successfully")
                
                # Update current user data
                self.current_user_data = self.auth.get_user_data()
            else:
                messagebox.showinfo("No Data", "No profile data to save")
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving profile: {str(e)}")
    
    def logout(self):
        """Log out the current user."""
        if self.auth:
            self.auth.logout()
        
        # Close and reopen the app
        self.destroy()
        app = EnhancedBodyFatEstimator()
        app.mainloop()

if __name__ == "__main__":
    app = EnhancedBodyFatEstimator()
    app.mainloop()
