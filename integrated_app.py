#!/usr/bin/env python
# integrated_app.py - Integrated BF Estimator app with enhanced profile and dashboard
# Created: 03/27/25

import os
import sys
import tkinter as tk
import customtkinter as ctk
import sqlite3
import datetime
import traceback
from tkinter import messagebox, filedialog

# Import components
from enhanced_profile_ui import EnhancedProfileFrame
from dashboard_widgets import (
    WeightTrackingWidget, BodyFatWidget, MeasurementsWidget, 
    GoalsProgressWidget, SmartAnalysisWidget, DietAnalysisWidget
)
from smart_analysis_engine import SmartAnalysisEngine

# Constants
APP_VERSION = "2.1"
APP_TITLE = f"Enhanced Body Fat Estimator v{APP_VERSION} with Dashboard"
DB_FILE = 'history.db'
THEME_JSON = "batman_theme.json"  # Default theme

class IntegratedApp:
    """Integrated BF Estimator app with enhanced profile and dashboard"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1000x650")
        self.root.minsize(850, 600)
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Try to load custom theme
        self.load_theme()
        
        self.setup_db()
        self.setup_ui()
        
        # Smart analysis engine
        self.analysis_engine = SmartAnalysisEngine(DB_FILE)
    
    def load_theme(self):
        """Load custom theme if available"""
        try:
            if os.path.exists(THEME_JSON):
                ctk.set_default_color_theme(THEME_JSON)
        except Exception as e:
            print(f"Error loading theme: {e}")
    
    def setup_db(self):
        """Set up database connection"""
        try:
            # Ensure the database exists
            if not os.path.exists(DB_FILE):
                conn = sqlite3.connect(DB_FILE)
                
                # Create necessary tables
                cursor = conn.cursor()
                
                # Weekly progress table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS weekly_progress (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER DEFAULT 1,
                        date TEXT,
                        weight REAL,
                        bodyfat REAL
                    )
                ''')
                
                # Commit changes and close connection
                conn.commit()
                conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error setting up database: {e}")
    
    def setup_ui(self):
        """Set up the main UI layout with tabs"""
        # Main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabview
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True)
        
        # Create tabs
        self.input_tab = self.tabview.add("Input Data")
        self.progress_tab = self.tabview.add("Weekly Progress")
        self.reports_tab = self.tabview.add("Reports History")
        self.results_tab = self.tabview.add("Results")
        self.about_tab = self.tabview.add("About")
        self.dashboard_tab = self.tabview.add("Dashboard")
        self.settings_tab = self.tabview.add("Settings")
        
        # Setup each tab
        self.setup_input_tab()
        self.setup_progress_tab()
        self.setup_reports_tab()
        self.setup_results_tab()
        self.setup_about_tab()
        self.setup_dashboard_tab()
        self.setup_settings_tab()
        
        # Footer
        self.footer = ctk.CTkFrame(self.root, height=20)
        self.footer.pack(fill="x", side="bottom")
        
        self.status_label = ctk.CTkLabel(self.footer, text="Welcome to Enhanced BF Estimator!")
        self.status_label.pack(side="left", padx=10)
        
        self.version_label = ctk.CTkLabel(self.footer, text=f"This version includes Dashboard, Enhanced Profile, Diet Calculations and Settings")
        self.version_label.pack(side="right", padx=10)
    
    def setup_input_tab(self):
        """Set up the input data tab with enhanced profile UI"""
        # Add enhanced profile frame to input tab
        self.profile_frame = EnhancedProfileFrame(self.input_tab)
        self.profile_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def setup_progress_tab(self):
        """Set up the weekly progress tab"""
        # Weekly progress frame
        progress_frame = ctk.CTkFrame(self.progress_tab)
        progress_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add weekly progress UI components here
        # (This is a simplified implementation)
        top_frame = ctk.CTkFrame(progress_frame)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        # Date entry
        date_label = ctk.CTkLabel(top_frame, text="Date (YYYY-MM-DD):")
        date_label.pack(side="left", padx=(10, 5))
        
        # Get current date in YYYY-MM-DD format
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.date_entry = ctk.CTkEntry(top_frame, width=150)
        self.date_entry.insert(0, current_date)
        self.date_entry.pack(side="left", padx=5)
        
        # Weight and body fat entries
        weight_frame = ctk.CTkFrame(progress_frame)
        weight_frame.pack(fill="x", padx=10, pady=10)
        
        weight_label = ctk.CTkLabel(weight_frame, text="Weight (lbs):")
        weight_label.pack(side="left", padx=(10, 5))
        
        self.weight_entry = ctk.CTkEntry(weight_frame, width=150)
        self.weight_entry.pack(side="left", padx=5)
        
        bf_label = ctk.CTkLabel(weight_frame, text="Body Fat %:")
        bf_label.pack(side="left", padx=(20, 5))
        
        self.bf_entry = ctk.CTkEntry(weight_frame, width=150)
        self.bf_entry.pack(side="left", padx=5)
        
        # Save button
        save_frame = ctk.CTkFrame(progress_frame)
        save_frame.pack(fill="x", padx=10, pady=10)
        
        save_button = ctk.CTkButton(
            save_frame, 
            text="Save Weekly Progress", 
            command=self.save_weekly_progress
        )
        save_button.pack(pady=10)
        
        # Progress history
        history_frame = ctk.CTkFrame(progress_frame)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        history_label = ctk.CTkLabel(history_frame, text="Weekly Progress History:", font=("Roboto", 14, "bold"))
        history_label.pack(anchor="w", padx=10, pady=5)
        
        # Create scrollable frame for history
        self.history_scroll = ctk.CTkScrollableFrame(history_frame, height=200)
        self.history_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load history data
        self.load_progress_history()
    
    def load_progress_history(self):
        """Load weekly progress history from database"""
        # Clear existing widgets
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
        
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get progress entries sorted by date (newest first)
            cursor.execute(
                "SELECT date, weight, bodyfat FROM weekly_progress WHERE user_id = ? ORDER BY date DESC",
                (1,)  # Default user_id is 1
            )
            entries = cursor.fetchall()
            
            if entries:
                # Header row
                header_frame = ctk.CTkFrame(self.history_scroll)
                header_frame.pack(fill="x", padx=5, pady=2)
                
                date_header = ctk.CTkLabel(header_frame, text="Date", font=("Roboto", 12, "bold"), width=120)
                date_header.pack(side="left", padx=5)
                
                weight_header = ctk.CTkLabel(header_frame, text="Weight (lbs)", font=("Roboto", 12, "bold"), width=120)
                weight_header.pack(side="left", padx=5)
                
                bf_header = ctk.CTkLabel(header_frame, text="Body Fat %", font=("Roboto", 12, "bold"), width=120)
                bf_header.pack(side="left", padx=5)
                
                # Separator
                separator = ctk.CTkFrame(self.history_scroll, height=1, fg_color="gray")
                separator.pack(fill="x", padx=5, pady=5)
                
                # Data rows
                for entry in entries:
                    row_frame = ctk.CTkFrame(self.history_scroll)
                    row_frame.pack(fill="x", padx=5, pady=2)
                    
                    date_label = ctk.CTkLabel(row_frame, text=entry['date'], width=120)
                    date_label.pack(side="left", padx=5)
                    
                    weight_label = ctk.CTkLabel(row_frame, text=f"{entry['weight']:.1f}", width=120)
                    weight_label.pack(side="left", padx=5)
                    
                    bf_label = ctk.CTkLabel(row_frame, text=f"{entry['bodyfat']:.1f}%", width=120)
                    bf_label.pack(side="left", padx=5)
            else:
                no_data_label = ctk.CTkLabel(self.history_scroll, text="No progress data available")
                no_data_label.pack(padx=10, pady=10)
            
            conn.close()
            
        except Exception as e:
            print(f"Error loading progress history: {e}")
            error_label = ctk.CTkLabel(
                self.history_scroll, 
                text=f"Error loading progress history: {str(e)}"
            )
            error_label.pack(padx=10, pady=10)
    
    def save_weekly_progress(self):
        """Save weekly progress to database"""
        try:
            date_str = self.date_entry.get().strip()
            weight_str = self.weight_entry.get().strip()
            bf_str = self.bf_entry.get().strip()
            
            # Validate inputs
            if not date_str or not weight_str or not bf_str:
                messagebox.showerror("Input Error", "All fields are required")
                return
            
            # Convert to appropriate types
            try:
                weight = float(weight_str)
                bodyfat = float(bf_str)
            except ValueError:
                messagebox.showerror("Input Error", "Weight and Body Fat must be numeric values")
                return
            
            # Validate date format (YYYY-MM-DD)
            try:
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Input Error", "Date must be in YYYY-MM-DD format")
                return
            
            # Save to database
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Check if entry for this date already exists
            cursor.execute(
                "SELECT id FROM weekly_progress WHERE user_id = ? AND date = ?",
                (1, date_str)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing entry
                cursor.execute(
                    "UPDATE weekly_progress SET weight = ?, bodyfat = ? WHERE user_id = ? AND date = ?",
                    (weight, bodyfat, 1, date_str)
                )
                action = "updated"
            else:
                # Insert new entry
                cursor.execute(
                    "INSERT INTO weekly_progress (user_id, date, weight, bodyfat) VALUES (?, ?, ?, ?)",
                    (1, date_str, weight, bodyfat)
                )
                action = "added"
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Weekly progress {action} successfully")
            
            # Clear entry fields
            self.weight_entry.delete(0, tk.END)
            self.bf_entry.delete(0, tk.END)
            
            # Refresh history
            self.load_progress_history()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving progress: {str(e)}")
    
    def setup_reports_tab(self):
        """Set up the reports history tab"""
        # Reports frame
        reports_frame = ctk.CTkFrame(self.reports_tab)
        reports_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add reports UI components here
        # (Simplified implementation)
        label = ctk.CTkLabel(reports_frame, text="Reports History", font=("Roboto", 16, "bold"))
        label.pack(pady=20)
        
        description = ctk.CTkLabel(
            reports_frame, 
            text="This tab displays your saved reports history.\nGenerate reports from the Results tab."
        )
        description.pack(pady=10)
    
    def setup_results_tab(self):
        """Set up the results tab"""
        # Results frame
        results_frame = ctk.CTkFrame(self.results_tab)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add results UI components here
        # (Simplified implementation)
        label = ctk.CTkLabel(results_frame, text="Results", font=("Roboto", 16, "bold"))
        label.pack(pady=20)
        
        description = ctk.CTkLabel(
            results_frame, 
            text="This tab will generate detailed body composition results and reports.\nEnter your data in the Input tab and Weekly Progress tab first."
        )
        description.pack(pady=10)
    
    def setup_about_tab(self):
        """Set up the about tab"""
        # About frame
        about_frame = ctk.CTkFrame(self.about_tab)
        about_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add about information
        title_label = ctk.CTkLabel(about_frame, text=f"Enhanced Body Fat Estimator v{APP_VERSION}", font=("Roboto", 24, "bold"))
        title_label.pack(pady=(30, 10))
        
        description = ctk.CTkLabel(
            about_frame,
            text="A comprehensive fitness and body composition tracking application.\n" +
                 "This application helps you track your progress, set goals, and analyze your results.\n\n" +
                 "Features:\n" +
                 "- Enhanced user profile with comprehensive fitness data collection\n" +
                 "- Weekly progress tracking with body fat percentage calculations\n" +
                 "- Diet and nutrition tracking with macronutrient analysis\n" +
                 "- Smart analysis of your progress and trends\n" +
                 "- Interactive dashboard with visual metrics\n" +
                 "- Customizable settings and themes\n\n" +
                 "Created: March 2025",
            font=("Roboto", 12),
            justify="left"
        )
        description.pack(pady=20)
    
    def setup_dashboard_tab(self):
        """Set up the dashboard tab with widgets"""
        # Dashboard frame with scrollable content
        self.dashboard_frame = ctk.CTkFrame(self.dashboard_tab)
        self.dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Top controls
        controls_frame = ctk.CTkFrame(self.dashboard_frame)
        controls_frame.pack(fill="x", pady=10)
        
        refresh_button = ctk.CTkButton(
            controls_frame, 
            text="Refresh All", 
            command=self.refresh_dashboard,
            width=120
        )
        refresh_button.pack(side="right", padx=10)
        
        # Widget layout - using grid for better organization
        # We'll have 2 rows of 3 widgets each
        widgets_frame = ctk.CTkFrame(self.dashboard_frame)
        widgets_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid - 3 columns of equal width
        widgets_frame.columnconfigure((0, 1, 2), weight=1, uniform="column")
        widgets_frame.rowconfigure((0, 1), weight=1, uniform="row")
        
        # Create widgets
        self.weight_widget = WeightTrackingWidget(widgets_frame)
        self.weight_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.bf_widget = BodyFatWidget(widgets_frame)
        self.bf_widget.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.analysis_widget = SmartAnalysisWidget(widgets_frame, self.analysis_engine)
        self.analysis_widget.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        
        self.measurements_widget = MeasurementsWidget(widgets_frame)
        self.measurements_widget.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.goals_widget = GoalsProgressWidget(widgets_frame)
        self.goals_widget.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        self.diet_widget = DietAnalysisWidget(widgets_frame)
        self.diet_widget.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
    
    def refresh_dashboard(self):
        """Refresh all dashboard widgets"""
        try:
            self.weight_widget.refresh_data()
            self.bf_widget.refresh_data()
            self.analysis_widget.refresh_data()
            self.measurements_widget.refresh_data()
            self.goals_widget.refresh_data()
            self.diet_widget.refresh_data()
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
            traceback.print_exc()
    
    def setup_settings_tab(self):
        """Set up the settings tab"""
        # Settings frame
        settings_frame = ctk.CTkFrame(self.settings_tab)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add settings UI components here
        # (Simplified implementation)
        title_label = ctk.CTkLabel(settings_frame, text="Application Settings", font=("Roboto", 16, "bold"))
        title_label.pack(pady=(20, 30))
        
        # Theme settings
        theme_frame = ctk.CTkFrame(settings_frame)
        theme_frame.pack(fill="x", padx=20, pady=10)
        
        theme_label = ctk.CTkLabel(theme_frame, text="Theme:", font=("Roboto", 14))
        theme_label.pack(side="left", padx=10)
        
        self.theme_var = ctk.StringVar(value="dark")
        
        # Theme radio buttons
        theme_options = ctk.CTkFrame(theme_frame)
        theme_options.pack(side="left", padx=10)
        
        dark_radio = ctk.CTkRadioButton(theme_options, text="Dark", variable=self.theme_var, value="dark", command=self.change_theme)
        dark_radio.pack(side="left", padx=10)
        
        light_radio = ctk.CTkRadioButton(theme_options, text="Light", variable=self.theme_var, value="light", command=self.change_theme)
        light_radio.pack(side="left", padx=10)
        
        # Theme files dropdown
        theme_files_frame = ctk.CTkFrame(settings_frame)
        theme_files_frame.pack(fill="x", padx=20, pady=10)
        
        theme_file_label = ctk.CTkLabel(theme_files_frame, text="Theme File:", font=("Roboto", 14))
        theme_file_label.pack(side="left", padx=10)
        
        # Get available theme files
        theme_files = self.get_theme_files()
        
        self.theme_file_var = ctk.StringVar(value=THEME_JSON)
        self.theme_file_dropdown = ctk.CTkOptionMenu(
            theme_files_frame,
            values=theme_files,
            variable=self.theme_file_var,
            command=self.change_theme_file
        )
        self.theme_file_dropdown.pack(side="left", padx=10)
        
        # Dashboard settings
        dashboard_frame = ctk.CTkFrame(settings_frame)
        dashboard_frame.pack(fill="x", padx=20, pady=20)
        
        dashboard_label = ctk.CTkLabel(dashboard_frame, text="Dashboard:", font=("Roboto", 14))
        dashboard_label.pack(anchor="w", padx=10, pady=5)
        
        self.dashboard_enabled_var = ctk.BooleanVar(value=True)
        dashboard_checkbox = ctk.CTkCheckBox(
            dashboard_frame, 
            text="Enable Dashboard on Startup",
            variable=self.dashboard_enabled_var
        )
        dashboard_checkbox.pack(anchor="w", padx=30, pady=5)
        
        # Save settings button
        save_button = ctk.CTkButton(
            settings_frame,
            text="Save Settings",
            command=self.save_settings
        )
        save_button.pack(pady=30)
        
        # Load settings
        self.load_settings()
    
    def get_theme_files(self):
        """Get list of theme JSON files"""
        theme_files = ["blue"]  # Default theme
        
        for file in os.listdir("."):
            if file.endswith(".json") and file != "package.json":
                theme_files.append(file)
        
        return theme_files
    
    def change_theme(self, *args):
        """Change the appearance mode"""
        mode = self.theme_var.get()
        ctk.set_appearance_mode(mode)
    
    def change_theme_file(self, *args):
        """Change the theme file"""
        theme_file = self.theme_file_var.get()
        
        try:
            ctk.set_default_color_theme(theme_file)
            messagebox.showinfo("Theme Changed", f"Theme changed to {theme_file}. Some changes will take effect after restart.")
        except Exception as e:
            messagebox.showerror("Theme Error", f"Error changing theme: {str(e)}")
    
    def save_settings(self):
        """Save settings to database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Create settings table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    id INTEGER PRIMARY KEY,
                    theme_mode TEXT,
                    theme_file TEXT,
                    dashboard_enabled INTEGER
                )
            """)
            
            # Check if settings exist
            cursor.execute("SELECT COUNT(*) FROM app_settings")
            count = cursor.fetchone()[0]
            
            # Prepare settings
            theme_mode = self.theme_var.get()
            theme_file = self.theme_file_var.get()
            dashboard_enabled = 1 if self.dashboard_enabled_var.get() else 0
            
            if count > 0:
                # Update existing settings
                cursor.execute("""
                    UPDATE app_settings 
                    SET theme_mode = ?, theme_file = ?, dashboard_enabled = ?
                    WHERE id = 1
                """, (theme_mode, theme_file, dashboard_enabled))
            else:
                # Insert new settings
                cursor.execute("""
                    INSERT INTO app_settings 
                    (theme_mode, theme_file, dashboard_enabled)
                    VALUES (?, ?, ?)
                """, (theme_mode, theme_file, dashboard_enabled))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Settings Saved", "Settings saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")
    
    def load_settings(self):
        """Load settings from database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Check if settings table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='app_settings'")
            if not cursor.fetchone():
                conn.close()
                return
            
            # Get settings
            cursor.execute("SELECT theme_mode, theme_file, dashboard_enabled FROM app_settings WHERE id = 1")
            settings = cursor.fetchone()
            
            if settings:
                # Apply settings
                theme_mode, theme_file, dashboard_enabled = settings
                
                # Set theme mode
                if theme_mode in ["dark", "light"]:
                    self.theme_var.set(theme_mode)
                    ctk.set_appearance_mode(theme_mode)
                
                # Set theme file
                if theme_file and theme_file in self.get_theme_files():
                    self.theme_file_var.set(theme_file)
                    try:
                        ctk.set_default_color_theme(theme_file)
                    except Exception as e:
                        print(f"Error setting theme file: {e}")
                
                # Set dashboard enabled
                self.dashboard_enabled_var.set(bool(dashboard_enabled))
            
            conn.close()
            
        except Exception as e:
            print(f"Error loading settings: {e}")

def main():
    # Set up the root window
    root = ctk.CTk()
    
    try:
        # Create the messagebox wrapper for CTk
        try:
            from CTkMessagebox import CTkMessagebox
            messagebox.showinfo = lambda title, message: CTkMessagebox(title=title, message=message).get()
            messagebox.showerror = lambda title, message: CTkMessagebox(title=title, message=message, icon="cancel").get()
            messagebox.showwarning = lambda title, message: CTkMessagebox(title=title, message=message, icon="warning").get()
            messagebox.askyesno = lambda title, message: CTkMessagebox(title=title, message=message, option_1="Yes", option_2="No").get()
        except ImportError:
            print("CTkMessagebox not found, using standard message boxes.")
        
        # Create the app
        print(f"Starting {APP_TITLE}")
        app = IntegratedApp(root)
        
        # Run the app
        root.mainloop()
    except Exception as e:
        print(f"Error running app: {e}")
        traceback.print_exc()
        
        # Attempt to show error message
        try:
            messagebox.showerror("Application Error", f"Error starting application: {str(e)}")
        except:
            # If even that fails, just print to console
            print(f"Critical error: {str(e)}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
