#!/usr/bin/env python
# enhanced_desktop_app.py - Enhanced Body Fat Estimator Desktop Application
# Created: 03/27/25

import os
import sys
import json
import sqlite3
import datetime
import tkinter as tk
import subprocess
import io
import base64
from tkinter import messagebox, ttk, simpledialog # Added simpledialog
import customtkinter as ctk
import speech_recognition as sr
from PIL import Image, ImageTk
import traceback # Added traceback

# Import custom modules
from theme_manager import ThemeManager
from user_auth import UserAuth
from login_interface import create_login_window
import additional_measurements # Added
import voice_input # Added
import smart_analysis # Added
from tutorial_system import TutorialSystem, show_welcome_tutorial # Added
from report_generation import generate_comprehensive_report, save_report # Ensure report functions are imported
from complete_report_functions import get_body_fat_info # Ensure helper is imported
from utils import calculate_rmr # Import calculate_rmr

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"

# Database file
DB_FILE = 'history.db'
RESULTS_FOLDER = "results" # Added

class WidgetFrame(ctk.CTkFrame):
    """Base class for draggable dashboard widgets."""
    def __init__(self, master, title, **kwargs):
        super().__init__(master, **kwargs)

        # Widget title
        self.title_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.title_bar.pack(fill="x", side="top")

        self.title_label = ctk.CTkLabel(self.title_bar, text=title, font=("Roboto", 12, "bold"))
        self.title_label.pack(side="left", padx=10)

        # Make widget draggable (Only works with place geometry manager)
        # self.title_bar.bind("<ButtonPress-1>", self.start_drag)
        # self.title_bar.bind("<ButtonRelease-1>", self.stop_drag)
        # self.title_bar.bind("<B1-Motion>", self.do_drag)
        # self.title_label.bind("<ButtonPress-1>", self.start_drag)
        # self.title_label.bind("<ButtonRelease-1>", self.stop_drag)
        # self.title_label.bind("<B1-Motion>", self.do_drag)

        # Dragging state (Kept for potential future use)
        self.x = 0
        self.y = 0
        self.is_dragging = False

    # Drag methods kept for potential future use with place()
    def start_drag(self, event):
        if not hasattr(self.master.master, 'edit_mode') or not self.master.master.edit_mode: 
             return
        self.x = event.x
        self.y = event.y
        self.is_dragging = True
        self.lift()

    def stop_drag(self, event):
        if not hasattr(self.master.master, 'edit_mode') or not self.master.master.edit_mode:
             return
        self.is_dragging = False

    def do_drag(self, event):
        if not self.is_dragging or not hasattr(self.master.master, 'edit_mode') or not self.master.master.edit_mode:
            return
        x = self.winfo_x() - self.x + event.x
        y = self.winfo_y() - self.y + event.y
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        widget_width = self.winfo_width()
        widget_height = self.winfo_height()
        x = max(0, min(x, parent_width - widget_width))
        y = max(0, min(y, parent_height - widget_height))
        self.place(x=x, y=y)

class WeightWidget(WidgetFrame):
    """Weight tracking widget for the dashboard."""
    def __init__(self, master, db_conn, user_id, **kwargs):
        super().__init__(master, title="Weight Tracking", **kwargs)
        self.db_conn = db_conn
        self.user_id = user_id

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Last weight entry
        self.last_weight_label = ctk.CTkLabel(self.content_frame, text="Current Weight:")
        self.last_weight_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.last_weight_value = ctk.CTkLabel(self.content_frame, text="--", font=("Roboto", 24))
        self.last_weight_value.pack(anchor="w", padx=10)

        # Weight change
        self.weight_change_label = ctk.CTkLabel(self.content_frame, text="Change:")
        self.weight_change_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.weight_change_value = ctk.CTkLabel(self.content_frame, text="--", font=("Roboto", 18))
        self.weight_change_value.pack(anchor="w", padx=10)

        # Refresh button
        self.refresh_button = ctk.CTkButton(self.content_frame, text="Refresh", command=self.refresh_data)
        self.refresh_button.pack(anchor="center", padx=10, pady=10)

        # Initially load data
        self.refresh_data()

    def refresh_data(self):
        """Refresh weight data from the database."""
        if not self.user_id: return
        cursor = self.db_conn.cursor()

        # Get last two weight entries for the specific user
        cursor.execute(
            "SELECT weight FROM weekly_progress WHERE user_id = ? ORDER BY date DESC LIMIT 2",
            (self.user_id,)
        )
        weights = cursor.fetchall()

        if weights and len(weights) > 0:
            # Update current weight
            current_weight = weights[0][0]
            self.last_weight_value.configure(text=f"{current_weight:.1f} lbs")

            # Calculate change if we have at least two entries
            if len(weights) > 1:
                previous_weight = weights[1][0]
                change = current_weight - previous_weight

                # Format change with color and sign
                sign = "+" if change > 0 else ""
                color = "#FF5555" if change > 0 else "#33CC33" if change < 0 else None

                self.weight_change_value.configure(
                    text=f"{sign}{change:.1f} lbs",
                    text_color=color
                )
            else:
                self.weight_change_value.configure(text="No change data", text_color=None)
        else:
            self.last_weight_value.configure(text="No data")
            self.weight_change_value.configure(text="--", text_color=None)

class BodyFatWidget(WidgetFrame):
    """Body fat percentage tracking widget for the dashboard."""
    def __init__(self, master, db_conn, user_id, **kwargs):
        super().__init__(master, title="Body Fat %", **kwargs)
        self.db_conn = db_conn
        self.user_id = user_id

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Last body fat entry
        self.last_bf_label = ctk.CTkLabel(self.content_frame, text="Current Body Fat:")
        self.last_bf_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.last_bf_value = ctk.CTkLabel(self.content_frame, text="--", font=("Roboto", 24))
        self.last_bf_value.pack(anchor="w", padx=10)

        # Body fat change
        self.bf_change_label = ctk.CTkLabel(self.content_frame, text="Change:")
        self.bf_change_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.bf_change_value = ctk.CTkLabel(self.content_frame, text="--", font=("Roboto", 18))
        self.bf_change_value.pack(anchor="w", padx=10)

        # Body fat category
        self.bf_category_label = ctk.CTkLabel(self.content_frame, text="Category:")
        self.bf_category_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.bf_category_value = ctk.CTkLabel(self.content_frame, text="--")
        self.bf_category_value.pack(anchor="w", padx=10)

        # Refresh button
        self.refresh_button = ctk.CTkButton(self.content_frame, text="Refresh", command=self.refresh_data)
        self.refresh_button.pack(anchor="center", padx=10, pady=10)

        # Initially load data
        self.refresh_data()

    def refresh_data(self):
        """Refresh body fat data from the database."""
        if not self.user_id: return
        cursor = self.db_conn.cursor()

        # Get last two body fat entries for the specific user
        cursor.execute(
            """SELECT wp.bodyfat AS body_fat_percentage, p.gender
               FROM weekly_progress wp
               JOIN user_profiles p ON wp.user_id = p.user_id
               WHERE wp.user_id = ?
               ORDER BY wp.date DESC LIMIT 2""",
            (self.user_id,)
        )
        entries = cursor.fetchall()

        if entries and len(entries) > 0:
            # Update current body fat
            current_bf = entries[0][0]
            gender = entries[0][1] if entries[0][1] else 'm'

            self.last_bf_value.configure(text=f"{current_bf:.1f}%")

            # Calculate change if we have at least two entries
            if len(entries) > 1:
                previous_bf = entries[1][0]
                change = current_bf - previous_bf

                # Format change with color and sign
                sign = "+" if change > 0 else ""
                color = "#FF5555" if change > 0 else "#33CC33" if change < 0 else None

                self.bf_change_value.configure(
                    text=f"{sign}{change:.1f}%",
                    text_color=color
                )
            else:
                self.bf_change_value.configure(text="No change data", text_color=None)

            # Get body fat category
            category, _, _ = get_body_fat_info(gender, current_bf)
            self.bf_category_value.configure(text=category)

        else:
            self.last_bf_value.configure(text="No data")
            self.bf_change_value.configure(text="--", text_color=None)
            self.bf_category_value.configure(text="--")

class MeasurementsWidget(WidgetFrame):
    """Body measurements tracking widget for the dashboard."""
    def __init__(self, master, db_conn, user_id, **kwargs):
        super().__init__(master, title="Measurements", **kwargs)
        self.db_conn = db_conn
        self.user_id = user_id

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Create scrollable frame for measurements
        self.scrollable_frame = ctk.CTkScrollableFrame(self.content_frame, height=120)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Refresh button
        self.refresh_button = ctk.CTkButton(self.content_frame, text="Refresh", command=self.refresh_data)
        self.refresh_button.pack(anchor="center", padx=10, pady=(0, 10))

        # Initially load data
        self.refresh_data()

    def refresh_data(self):
        """Refresh measurements data from the database."""
        if not self.user_id: return
        cursor = self.db_conn.cursor()

        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        try:
            # First make sure the additional_measurements tables are set up
            additional_measurements.setup_database()
            
            # Get latest measurement for each type for the specific user
            cursor.execute(
                """SELECT m.measurement_type, m.value, m.date, t.units
                FROM additional_measurements m
                JOIN (
                    SELECT measurement_type, MAX(date) as max_date
                    FROM additional_measurements
                    WHERE user_id = ?
                    GROUP BY measurement_type
                ) latest ON m.measurement_type = latest.measurement_type AND m.date = latest.max_date
                JOIN measurement_types t ON m.user_id = t.user_id AND m.measurement_type = t.measurement_type
                WHERE m.user_id = ?
                ORDER BY m.measurement_type""",
                (self.user_id, self.user_id)
            )
        except sqlite3.OperationalError:
            # If tables or columns don't exist, just show an empty widget
            no_data_label = ctk.CTkLabel(self.scrollable_frame, text="Measurement data tables not yet set up.")
            no_data_label.pack(padx=10, pady=10)
            return
        measurements = cursor.fetchall()

        if measurements:
            for i, (mtype, value, date, units) in enumerate(measurements):
                # Create frame for each measurement
                frame = ctk.CTkFrame(self.scrollable_frame)
                frame.pack(fill="x", padx=5, pady=2)

                # Measurement type
                type_label = ctk.CTkLabel(frame, text=f"{mtype.replace('_', ' ').capitalize()}")
                type_label.pack(side="left", padx=5)

                # Measurement value
                value_label = ctk.CTkLabel(frame, text=f"{value:.1f} {units}")
                value_label.pack(side="right", padx=5)
        else:
            no_data_label = ctk.CTkLabel(self.scrollable_frame, text="No measurement data available")
            no_data_label.pack(padx=10, pady=10)

class GoalsWidget(WidgetFrame):
    """Goals and progress tracking widget for the dashboard."""
    def __init__(self, master, db_conn, user_id, **kwargs):
        super().__init__(master, title="Goals & Progress", **kwargs)
        self.db_conn = db_conn
        self.user_id = user_id

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Weight goal
        self.weight_goal_label = ctk.CTkLabel(self.content_frame, text="Weight Goal:")
        self.weight_goal_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.weight_goal_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.weight_goal_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.weight_goal_value = ctk.CTkLabel(self.weight_goal_frame, text="--")
        self.weight_goal_value.pack(side="left")

        self.weight_goal_progress = ctk.CTkProgressBar(self.weight_goal_frame, width=150)
        self.weight_goal_progress.pack(side="right", padx=10)
        self.weight_goal_progress.set(0) # Initialize progress bar

        # Body fat goal
        self.bf_goal_label = ctk.CTkLabel(self.content_frame, text="Body Fat Goal:")
        self.bf_goal_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.bf_goal_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.bf_goal_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.bf_goal_value = ctk.CTkLabel(self.bf_goal_frame, text="--")
        self.bf_goal_value.pack(side="left")

        self.bf_goal_progress = ctk.CTkProgressBar(self.bf_goal_frame, width=150)
        self.bf_goal_progress.pack(side="right", padx=10)
        self.bf_goal_progress.set(0) # Initialize progress bar

        # Estimated completion
        self.completion_label = ctk.CTkLabel(self.content_frame, text="Estimated Completion:")
        self.completion_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.completion_value = ctk.CTkLabel(self.content_frame, text="--")
        self.completion_value.pack(anchor="w", padx=10)

        # Refresh button
        self.refresh_button = ctk.CTkButton(self.content_frame, text="Refresh", command=self.refresh_data)
        self.refresh_button.pack(anchor="center", padx=10, pady=10)

        # Initially load data
        self.refresh_data()

    def refresh_data(self):
        """Refresh goals data from the database."""
        if not self.user_id: return
        cursor = self.db_conn.cursor()

        # Get current weight, body fat, and goals for the specific user
        cursor.execute(
            """SELECT wp.weight, wp.bodyfat AS body_fat_percentage, p.goal_weight, p.goal_bf
               FROM weekly_progress wp
               JOIN user_profiles p ON wp.user_id = p.user_id
               WHERE wp.user_id = ?
               ORDER BY wp.date DESC LIMIT 1""",
            (self.user_id,)
        )
        result = cursor.fetchone()

        if result and result['goal_weight'] is not None and result['goal_bf'] is not None:
            current_weight = result['weight']
            current_bf = result['body_fat_percentage']
            goal_weight = result['goal_weight']
            goal_bf = result['goal_bf']

            # Get starting weight and BF for progress calculation
            cursor.execute(
                "SELECT weight, bodyfat AS body_fat_percentage FROM weekly_progress WHERE user_id = ? ORDER BY date ASC LIMIT 1",
                (self.user_id,)
            )
            start_result = cursor.fetchone()
            start_weight = start_result['weight'] if start_result else current_weight
            start_bf = start_result['body_fat_percentage'] if start_result else current_bf

            # Weight goal progress
            if goal_weight is not None and start_weight != goal_weight:
                 weight_progress = (start_weight - current_weight) / (start_weight - goal_weight)
                 weight_progress = max(0, min(weight_progress, 1)) # Clamp
                 self.weight_goal_value.configure(text=f"{current_weight:.1f} / {goal_weight:.1f} lbs")
                 self.weight_goal_progress.set(weight_progress)
            else:
                 self.weight_goal_value.configure(text=f"{current_weight:.1f} lbs (No goal set)")
                 self.weight_goal_progress.set(0)


            # Body fat goal progress
            if goal_bf is not None and start_bf != goal_bf:
                 bf_progress = (start_bf - current_bf) / (start_bf - goal_bf)
                 bf_progress = max(0, min(bf_progress, 1)) # Clamp
                 self.bf_goal_value.configure(text=f"{current_bf:.1f}% / {goal_bf:.1f}%")
                 self.bf_goal_progress.set(bf_progress)
            else:
                 self.bf_goal_value.configure(text=f"{current_bf:.1f}% (No goal set)")
                 self.bf_goal_progress.set(0)


            # Estimate completion date (simplified)
            cursor.execute(
                """SELECT AVG(weight_diff) as avg_weight_change, AVG(bf_diff) as avg_bf_change FROM (
                   SELECT date,
                          weight - LAG(weight, 1, weight) OVER (ORDER BY date) as weight_diff,
                          bodyfat - LAG(bodyfat, 1, bodyfat) OVER (ORDER BY date) as bf_diff
                   FROM weekly_progress
                   WHERE user_id = ?
                   ORDER BY date DESC
                   LIMIT 10
                ) as changes""", (self.user_id,)
            )
            avg_changes = cursor.fetchone()

            weeks_to_goal = float('inf')
            if avg_changes and avg_changes['avg_weight_change'] is not None and avg_changes['avg_bf_change'] is not None:
                avg_weight_change = avg_changes['avg_weight_change']
                avg_bf_change = avg_changes['avg_bf_change']

                weight_diff = current_weight - goal_weight
                bf_diff = current_bf - goal_bf

                weight_weeks = weight_diff / (-avg_weight_change) if avg_weight_change < 0 else float('inf')
                bf_weeks = bf_diff / (-avg_bf_change) if avg_bf_change < 0 else float('inf')

                # Use the longer estimate, only if progress is in the right direction
                valid_weeks = [w for w in [weight_weeks, bf_weeks] if w > 0]
                if valid_weeks:
                    weeks_to_goal = max(valid_weeks)

            if weeks_to_goal < float('inf') and weeks_to_goal > 0:
                completion_date = datetime.datetime.now() + datetime.timedelta(weeks=weeks_to_goal)
                self.completion_value.configure(text=completion_date.strftime("%B %d, %Y"))
            elif goal_weight is None or goal_bf is None:
                 self.completion_value.configure(text="Set goals first")
            else:
                self.completion_value.configure(text="Not enough data or no progress")
        else:
            self.weight_goal_value.configure(text="No data")
            self.weight_goal_progress.set(0)
            self.bf_goal_value.configure(text="No data")
            self.bf_goal_progress.set(0)
            self.completion_value.configure(text="No data")

class AnalysisWidget(WidgetFrame):
    """Smart analysis widget for the dashboard."""
    def __init__(self, master, db_conn, user_id, **kwargs):
        super().__init__(master, title="Smart Analysis", **kwargs)
        self.db_conn = db_conn
        self.user_id = user_id

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Analysis text area
        self.analysis_text = ctk.CTkTextbox(self.content_frame, height=120, width=250)
        self.analysis_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.analysis_text.insert("1.0", "Login to see analysis.") # Initial text

        # Refresh button
        self.refresh_button = ctk.CTkButton(self.content_frame, text="Refresh Analysis", command=self.refresh_data)
        self.refresh_button.pack(anchor="center", padx=10, pady=(0, 10))

        # Initially load data
        self.refresh_data()

    def refresh_data(self):
        """Generate and display smart analysis."""
        if not self.user_id:
             self.analysis_text.delete("1.0", "end")
             self.analysis_text.insert("1.0", "Login to see analysis.")
             return

        try:
            # Clear existing text
            self.analysis_text.delete("1.0", "end")
            self.analysis_text.insert("1.0", "Generating analysis...")
            self.update() # Force UI update

            # Get analysis
            analysis_result = smart_analysis.analyze_progress(self.db_conn) # Pass connection

            self.analysis_text.delete("1.0", "end")
            if analysis_result:
                # Display analysis
                self.analysis_text.insert("1.0", analysis_result)
            else:
                self.analysis_text.insert("1.0", "Not enough data for analysis. Continue tracking your progress regularly.")
        except Exception as e:
            self.analysis_text.delete("1.0", "end")
            self.analysis_text.insert("1.0", f"Error generating analysis: {str(e)}\n\nPlease continue tracking your progress.")

class EnhancedBodyFatEstimator(ctk.CTk):
    """Enhanced Body Fat Estimator Desktop Application with all enhanced features."""
    def __init__(self):
        super().__init__()

        # Set up window
        self.title("Enhanced Body Fat Estimator v2.0")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # Initialize auth system (still needed for settings)
        self.auth = UserAuth() 
        self.current_user_data = None
        self.current_user_id = 1 # Default to user ID 1, bypassing login

        # Initialize theme manager
        self.theme_manager = ThemeManager(self)

        # Connect to database
        self.db_conn = sqlite3.connect(DB_FILE, check_same_thread=False) # Allow multithreading access if needed
        self.db_conn.row_factory = sqlite3.Row

        # Ensure additional measurements table exists
        additional_measurements.setup_database()

        # Check if required packages are installed
        self.check_required_packages()
        
        # --- Bypass Login ---
        # Simulate login for user 1 to populate self.auth.current_user
        # Fetch data directly and set necessary attributes
        self.current_user_data = self._get_user_data_directly(self.current_user_id)
        if self.current_user_data:
             self.auth.current_user = self.current_user_data # Manually set current user in auth object
             self.auth.is_authenticated = True # Mark as authenticated
        else:
            print(f"[WARNING] Could not load data for default user ID {self.current_user_id}. App might not function correctly.")
            messagebox.showerror("Error", f"Default user (ID {self.current_user_id}) not found. Please register a user first.")
            self.destroy()
            return

        # Apply theme (use default or user's preference if loaded)
        preferred_theme = self.current_user_data.get('preferred_theme', 'enhanced_blue') if self.current_user_data else 'enhanced_blue'
        try:
            self.theme_manager.apply_theme(preferred_theme)
        except Exception as e:
            print(f"[DEBUG] Error applying theme: {e}")
            self.theme_manager.apply_theme("enhanced_blue") # Fallback

        # Initialize the UI
        self.setup_ui()
        self.load_settings() # Load settings after UI is built
        self.refresh_dashboard_widgets() # Refresh dashboard with user data
        self.populate_measurement_fields() # Populate measurements for the user
        # --- End Bypass Login ---

        # self.show_login_window() # Removed login window call

    def _get_user_data_directly(self, user_id):
        """Internal helper to fetch user data directly from DB."""
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE, timeout=10.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Ensure related records exist
            cursor.execute("INSERT OR IGNORE INTO user_profiles (user_id) VALUES (?)", (user_id,))
            cursor.execute("INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)", (user_id,))
            conn.commit() # Commit insertions before fetching

            cursor.execute("""
                SELECT u.*, p.*, s.*
                FROM users u
                LEFT JOIN user_profiles p ON u.user_id = p.user_id
                LEFT JOIN user_settings s ON u.user_id = s.user_id
                WHERE u.user_id = ?
            """, (user_id,))
            user_data = cursor.fetchone()
            conn.close()
            return dict(user_data) if user_data else None
        except Exception as e:
            print(f"Error fetching user data directly for ID {user_id}: {e}")
            if conn:
                try: conn.close()
                except: pass
            return None


    def check_required_packages(self):
        """Check and install required packages."""
        try:
            import speech_recognition
        except ImportError:
            messagebox.showinfo("Info", "SpeechRecognition package not found. Attempting to install...")
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "SpeechRecognition", "pyaudio"])
                messagebox.showinfo("Success", "Successfully installed SpeechRecognition and PyAudio.")
            except Exception as e:
                 messagebox.showerror("Error", f"Failed to install packages: {e}\nVoice input may not work.")

    def show_login_window(self):
        """Show login window."""
        # Call create_login_window with only the callback
        create_login_window(on_login_success=self.handle_login_success)

    def handle_login_success(self, auth_obj):
        """Handle successful login."""
        # This function is no longer called directly in the bypass scenario,
        # but kept for potential future re-enabling of login.
        self.auth = auth_obj if auth_obj else self.auth
        
        if self.auth and self.auth.is_logged_in():
            self.current_user_data = self.auth.get_user_data()
            self.current_user_id = self.current_user_data.get('user_id') if self.current_user_data else None

            # Set theme from user preferences
            preferred_theme = self.auth.get_preferred_theme()
            try:
                self.theme_manager.apply_theme(preferred_theme)
            except Exception as e:
                print(f"[DEBUG] Error applying theme on login: {e}")
                self.theme_manager.apply_theme("enhanced_blue") # Fallback

            # Initialize the UI only after successful login
            self.setup_ui()
            self.load_settings() # Load settings after UI is built
            self.refresh_dashboard_widgets() # Refresh dashboard with user data
            self.populate_measurement_fields() # Populate measurements for the user
            # self.check_show_tutorial() # Check if tutorial should run

        else:
             # Handle login failure or window close without login
             self.destroy() # Close the main app if login fails

    def setup_ui(self):
        """Set up the user interface."""
        # Destroy previous main_frame if exists (e.g., on re-login)
        if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
             self.main_frame.destroy()

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
        self.setup_input_tab() # Contains weekly and measurements input
        self.setup_progress_tab() # Contains charts and history
        self.setup_report_tab() # For generating reports
        self.setup_settings_tab() # For profile, themes, etc.
        self.setup_about_tab() # Basic info

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

        # Initialize tutorial system
        self.tutorial_system = TutorialSystem(self, callback=self._on_tutorial_complete)

        # Check if tutorial needs to be shown
        # self.check_show_tutorial() # Add this later if needed

    def setup_dashboard_tab(self):
        """Set up the dashboard tab with customizable widgets."""
        # Clear previous widgets if any
        for widget in self.dashboard_tab.winfo_children():
            widget.destroy()

        # Configure grid for dashboard
        self.dashboard_tab.grid_columnconfigure(0, weight=1)
        self.dashboard_tab.grid_rowconfigure(0, weight=1)

        # Create a frame to hold the widgets
        self.dashboard_frame = ctk.CTkFrame(self.dashboard_tab)
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure grid layout for the dashboard frame
        self.dashboard_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="dashboard") # Adjust weights as needed
        self.dashboard_frame.grid_rowconfigure((0, 1), weight=1, uniform="dashboard")

        # Create widgets
        self.dashboard_widgets = {}
        user_id = self.current_user_id

        # Create and grid widgets, passing user_id
        # Adjust row/column placement as desired
        self.dashboard_widgets["weight"] = WeightWidget(self.dashboard_frame, self.db_conn, user_id)
        self.dashboard_widgets["weight"].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.dashboard_widgets["body_fat"] = BodyFatWidget(self.dashboard_frame, self.db_conn, user_id)
        self.dashboard_widgets["body_fat"].grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.dashboard_widgets["measurements"] = MeasurementsWidget(self.dashboard_frame, self.db_conn, user_id)
        self.dashboard_widgets["measurements"].grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.dashboard_widgets["goals"] = GoalsWidget(self.dashboard_frame, self.db_conn, user_id)
        self.dashboard_widgets["goals"].grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.dashboard_widgets["analysis"] = AnalysisWidget(self.dashboard_frame, self.db_conn, user_id)
        self.dashboard_widgets["analysis"].grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Removed edit mode button and related logic for now
        # self.edit_mode = False 

    # Removed load_dashboard_layout, save_dashboard_layout, and toggle_edit_mode methods
    # as they were tied to the place() geometry manager.

    def setup_input_tab(self):
        """Set up the input data tab with additional measurements."""
         # Clear previous widgets if any
        for widget in self.input_tab.winfo_children():
            widget.destroy()

        # Configure grid for input tab
        self.input_tab.grid_columnconfigure(0, weight=1)
        self.input_tab.grid_columnconfigure(1, weight=1)
        self.input_tab.grid_rowconfigure(0, weight=1) # Allow frames to expand

        # Left column - Weekly data input
        self.weekly_frame = ctk.CTkFrame(self.input_tab)
        self.weekly_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.weekly_frame.grid_rowconfigure(1, weight=1) # Allow form frame to expand

        ctk.CTkLabel(
            self.weekly_frame,
            text="Weekly Progress Data",
            font=("Roboto", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Weekly data form
        form_frame = ctk.CTkFrame(self.weekly_frame)
        form_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        form_frame.grid_columnconfigure(1, weight=1) # Allow entries to expand

        # Date field
        ctk.CTkLabel(form_frame, text="Date:").grid(row=0, column=0, padx=10, pady=(5, 5), sticky="w")
        self.date_entry = ctk.CTkEntry(form_frame)
        self.date_entry.grid(row=0, column=1, padx=10, pady=(5, 5), sticky="ew")
        self.date_entry.insert(0, datetime.datetime.now().strftime("%m/%d/%Y"))

        # Weight field
        ctk.CTkLabel(form_frame, text="Weight (lbs):").grid(row=1, column=0, padx=10, pady=(5, 5), sticky="w")
        self.weight_entry = ctk.CTkEntry(form_frame)
        self.weight_entry.grid(row=1, column=1, padx=10, pady=(5, 5), sticky="ew")

        # Body fat field
        ctk.CTkLabel(form_frame, text="Body Fat %:").grid(row=6, column=0, padx=10, pady=(5, 5), sticky="w")
        self.bf_entry = ctk.CTkEntry(form_frame)
        self.bf_entry.grid(row=6, column=1, padx=10, pady=(5, 5), sticky="ew")

        # Save button for weekly data
        save_weekly_btn = ctk.CTkButton(
            self.weekly_frame,
            text="Save Weekly Data",
            command=self.save_weekly_data
        )
        save_weekly_btn.grid(row=6, column=0, padx=10, pady=10, sticky="ew")

        # Right column - Additional Measurements
        self.measurements_section = ctk.CTkFrame(self.input_tab)
        self.measurements_section.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.measurements_section.grid_rowconfigure(1, weight=1) # Allow scrollable frame to expand

        ctk.CTkLabel(
            self.measurements_section,
            text="Additional Measurements",
            font=("Roboto", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Frame for measurement entries
        self.measurements_entry_frame = ctk.CTkScrollableFrame(self.measurements_section)
        self.measurements_entry_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        # No need to configure columns here, pack inside

        # Dictionary to hold measurement entry widgets
        self.measurement_entries = {}

        # Populate measurement fields
        self.populate_measurement_fields()

        # Add custom measurement button
        self.custom_measurement_button = ctk.CTkButton(
            self.measurements_section,
            text="Add Custom Measurement",
            command=self.add_custom_measurement_dialog
        )
        self.custom_measurement_button.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        # Save button for measurements
        save_measurements_btn = ctk.CTkButton(
            self.measurements_section,
            text="Save Measurements",
            command=self.save_measurements_data
        )
        save_measurements_btn.grid(row=6, column=0, padx=10, pady=10, sticky="ew")

    def populate_measurement_fields(self):
        """Populate the measurement entry fields based on available types."""
        # Clear existing fields
        for widget in self.measurements_entry_frame.winfo_children():
            widget.destroy()
        self.measurement_entries.clear()

        user_id = self.current_user_id
        if not user_id:
             ctk.CTkLabel(self.measurements_entry_frame, text="Error: User ID not set.").pack(pady=10)
             return

        measurement_types = additional_measurements.get_measurement_types(user_id)

        if not measurement_types:
             # Add default types if none exist for the user yet
             additional_measurements.setup_database() # Ensure defaults are added
             measurement_types = additional_measurements.get_measurement_types(user_id)

        if not measurement_types:
             ctk.CTkLabel(self.measurements_entry_frame, text="No measurement types defined.").pack(pady=10)
             return

        for i, (m_type, units, is_custom) in enumerate(measurement_types):
            frame = ctk.CTkFrame(self.measurements_entry_frame)
            frame.pack(fill="x", pady=2, padx=5)
            frame.grid_columnconfigure(1, weight=1) # Allow entry to expand

            label_text = f"{m_type.replace('_', ' ').capitalize()} ({units}):"
            label = ctk.CTkLabel(frame, text=label_text, width=120, anchor="w")
            label.grid(row=0, column=0, padx=(0, 5), pady=2, sticky="w")

            entry = ctk.CTkEntry(frame)
            entry.grid(row=0, column=1, padx=(0, 5), pady=2, sticky="ew")

            self.measurement_entries[m_type] = entry

    def add_custom_measurement_dialog(self):
        """Show dialog to add a custom measurement type."""
        user_id = self.current_user_id
        if not user_id:
             messagebox.showerror("Error", "User ID not set.")
             return

        dialog = ctk.CTkInputDialog(
            text="Enter new measurement type name (e.g., 'forearm'):",
            title="Add Custom Measurement"
        )
        measurement_name = dialog.get_input()

        if measurement_name:
            if additional_measurements.add_custom_measurement_type(user_id, measurement_name):
                messagebox.showinfo("Success", f"Added custom measurement: {measurement_name}")
                self.populate_measurement_fields() # Refresh fields
            else:
                messagebox.showerror("Error", "Failed to add custom measurement type (it might already exist).")

    def save_weekly_data(self):
        """Save the weekly progress data."""
        user_id = self.current_user_id
        if not user_id:
            messagebox.showerror("Error", "User ID not set. Cannot save data.")
            return

        try:
            date_str = self.date_entry.get()
            weight_str = self.weight_entry.get()
            body_fat_str = self.bf_entry.get()
            # muscle_gain_str = self.muscle_entry.get() # Removed reading muscle gain

            if not date_str or not weight_str or not body_fat_str:
                 messagebox.showerror("Error", "Date, Weight, and Body Fat are required.")
                 return

            weight = float(weight_str)
            body_fat = float(body_fat_str)
            muscle_gain = 0.0 # Set muscle_gain to 0.0 as it's no longer entered

            # Validate date format (MM/DD/YYYY)
            try:
                date_obj = datetime.datetime.strptime(date_str, "%m/%d/%Y")
                db_date_str = date_obj.strftime("%Y-%m-%d") # Store in YYYY-MM-DD format
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use MM/DD/YYYY.")
                return

            # Add to weekly_progress table
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            # Use INSERT OR REPLACE to update if entry for that date exists
            cursor.execute(
                """
                INSERT OR REPLACE INTO weekly_progress (user_id, date, weight, bodyfat, muscle_gain) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, db_date_str, weight, body_fat, muscle_gain) # Pass the calculated/default muscle_gain
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Weekly data saved successfully.")

            # Refresh relevant widgets/tabs
            self.refresh_dashboard_widgets()
            self.setup_progress_tab() # Refresh progress tab

        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter numeric values for weight, body fat, and muscle gain.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save weekly data: {str(e)}")
            traceback.print_exc()


    def save_measurements_data(self):
        """Save the additional measurements data."""
        user_id = self.current_user_id
        if not user_id:
            messagebox.showerror("Error", "User ID not set. Cannot save measurements.")
            return

        date_str = self.date_entry.get() # Use the date from the weekly section

        try:
            # Validate date format (MM/DD/YYYY)
            date_obj = datetime.datetime.strptime(date_str, "%m/%d/%Y")
            db_date_str = date_obj.strftime("%Y-%m-%d") # Store in YYYY-MM-DD format
        except ValueError:
            messagebox.showerror("Error", "Invalid date format in weekly section. Please use MM/DD/YYYY.")
            return

        saved_count = 0
        errors = []

        for m_type, entry_widget in self.measurement_entries.items():
            value_str = entry_widget.get()
            if value_str: # Only save if a value is entered
                try:
                    value = float(value_str)
                    # Add measurement (will handle insert/update logic if needed)
                    if additional_measurements.add_measurement(user_id, m_type, value, date=db_date_str):
                        saved_count += 1
                    else:
                        errors.append(f"Failed to save {m_type}")
                except ValueError:
                    errors.append(f"Invalid numeric value for {m_type}")
                except Exception as e:
                    errors.append(f"Error saving {m_type}: {str(e)}")
                    traceback.print_exc()


        if saved_count > 0:
            message = f"Successfully saved {saved_count} measurements."
            if errors:
                message += "\nErrors occurred for: " + ", ".join(errors)
            messagebox.showinfo("Save Measurements", message)
            self.refresh_dashboard_widgets() # Refresh dashboard
        elif errors:
            messagebox.showerror("Save Measurements Error", "\n".join(errors))
        else:
            messagebox.showinfo("Save Measurements", "No new measurement values entered.")

    def refresh_dashboard_widgets(self):
        """Refresh data in all dashboard widgets."""
        if hasattr(self, 'dashboard_widgets'):
             print("Refreshing dashboard widgets...")
             for widget_name, widget in self.dashboard_widgets.items():
                 if hasattr(widget, 'refresh_data'):
                     print(f"Refreshing {widget_name} widget")
                     try:
                         widget.refresh_data()
                         # Force update
                         widget.update()
                     except Exception as e:
                         print(f"Error refreshing {widget_name}: {e}")
             
             # Force UI update
             self.update_idletasks()

    def setup_progress_tab(self):
        """Set up the weekly progress charts and history tab."""
         # Clear previous widgets if any
        for widget in self.progress_tab.winfo_children():
            widget.destroy()

        # Placeholder - Needs implementation to show charts and history table
        label = ctk.CTkLabel(self.progress_tab, text="Weekly Progress Charts & History (To be implemented)")
        label.pack(pady=20)
        # TODO: Add chart generation and history table display here later

    def setup_report_tab(self):
        """Set up the report generation tab."""
         # Clear previous widgets if any
        for widget in self.report_tab.winfo_children():
            widget.destroy()

        # Placeholder - Needs implementation for report generation options
        frame = ctk.CTkFrame(self.report_tab)
        frame.pack(expand=True, padx=20, pady=20)

        label = ctk.CTkLabel(frame, text="Generate Reports", font=("Roboto", 18, "bold"))
        label.pack(pady=10)

        # Button to trigger report generation using data from the Input Tab
        # Note: This uses the *current* state of the Input Tab, not historical data
        generate_now_btn = ctk.CTkButton(
            frame,
            text="Generate Report from Current Input Data",
            command=self.generate_report_from_input_tab # Link to a new method
        )
        generate_now_btn.pack(pady=20)

        # Placeholder for future report options (e.g., date range)
        options_label = ctk.CTkLabel(frame, text="(More report options coming soon)")
        options_label.pack(pady=10)

    def generate_report_from_input_tab(self):
         """Generates a report using the current data entered in the Input Data tab."""
         messagebox.showinfo("Info", "Generating report based on current data in the 'Input Data' tab...")
         # This reuses the logic that reads from the input fields
         self.generate_report() # Call the existing report generation method

    def setup_settings_tab(self):
        """Set up the settings tab with profile, goals, and appearance options."""
         # Clear previous widgets if any
        for widget in self.settings_tab.winfo_children():
            widget.destroy()

        settings_scroll_frame = ctk.CTkScrollableFrame(self.settings_tab)
        settings_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        settings_scroll_frame.grid_columnconfigure(0, weight=1)

        row_idx = 0

        # --- Profile Section ---
        profile_frame = ctk.CTkFrame(settings_scroll_frame)
        profile_frame.grid(row=row_idx, column=0, padx=10, pady=10, sticky="ew")
        profile_frame.grid_columnconfigure(1, weight=1)
        row_idx += 1

        ctk.CTkLabel(profile_frame, text="User Profile", font=("Roboto", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(5, 10), sticky="w")

        # Name
        ctk.CTkLabel(profile_frame, text="Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.settings_name_entry = ctk.CTkEntry(profile_frame)
        self.settings_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Email
        ctk.CTkLabel(profile_frame, text="Email:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_email_entry = ctk.CTkEntry(profile_frame)
        self.settings_email_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Email
        ctk.CTkLabel(profile_frame, text="Email:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_email_entry = ctk.CTkEntry(profile_frame)
        self.settings_email_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Email
        ctk.CTkLabel(profile_frame, text="Email:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_email_entry = ctk.CTkEntry(profile_frame)
        self.settings_email_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Email
        ctk.CTkLabel(profile_frame, text="Email:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_email_entry = ctk.CTkEntry(profile_frame)
        self.settings_email_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Email
        ctk.CTkLabel(profile_frame, text="Email:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_email_entry = ctk.CTkEntry(profile_frame)
        self.settings_email_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Age (DOB might be better, but keeping simple for now)
        ctk.CTkLabel(profile_frame, text="Age:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_age_entry = ctk.CTkEntry(profile_frame)
        self.settings_age_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Gender
        ctk.CTkLabel(profile_frame, text="Gender:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_gender_var = ctk.StringVar()
        self.settings_gender_options = ctk.CTkOptionMenu(profile_frame, variable=self.settings_gender_var, values=["m", "f"])
        self.settings_gender_options.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Height
        ctk.CTkLabel(profile_frame, text="Height:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        height_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        height_frame.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
        self.settings_height_ft_entry = ctk.CTkEntry(height_frame, width=60)
        self.settings_height_ft_entry.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(height_frame, text="ft").pack(side="left", padx=(0, 10))
        self.settings_height_in_entry = ctk.CTkEntry(height_frame, width=60)
        self.settings_height_in_entry.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(height_frame, text="in").pack(side="left")

        # DOB
        ctk.CTkLabel(profile_frame, text="Date of Birth (MMDDYY):").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_dob_entry = ctk.CTkEntry(profile_frame)
        self.settings_dob_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")


        # --- Activity & Experience Section ---
        activity_frame = ctk.CTkFrame(settings_scroll_frame)
        activity_frame.grid(row=row_idx, column=0, padx=10, pady=10, sticky="ew")
        activity_frame.grid_columnconfigure(1, weight=1)
        row_idx += 1

        ctk.CTkLabel(activity_frame, text="Activity & Experience", font=("Roboto", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(5, 10), sticky="w")

        # Activity Level
        ctk.CTkLabel(activity_frame, text="Activity Level:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.settings_activity_level_var = ctk.StringVar()
        activity_options = [f"{i}: {desc}" for i, desc in {1: "Sedentary", 2: "Light", 3: "Moderate", 4: "Active", 5: "Very Active"}.items()]
        self.settings_activity_level_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_activity_level_var, values=activity_options)
        self.settings_activity_level_options.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Resistance Training
        ctk.CTkLabel(activity_frame, text="Resistance Training:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_resistance_training_var = ctk.StringVar()
        self.settings_resistance_training_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_resistance_training_var, values=["Yes", "No"])
        self.settings_resistance_training_options.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Resistance Training
        ctk.CTkLabel(activity_frame, text="Resistance Training:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_resistance_training_var = ctk.StringVar()
        self.settings_resistance_training_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_resistance_training_var, values=["Yes", "No"])
        self.settings_resistance_training_options.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Resistance Training
        ctk.CTkLabel(activity_frame, text="Resistance Training:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_resistance_training_var = ctk.StringVar()
        self.settings_resistance_training_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_resistance_training_var, values=["Yes", "No"])
        self.settings_resistance_training_options.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Resistance Training
        ctk.CTkLabel(activity_frame, text="Resistance Training:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_resistance_training_var = ctk.StringVar()
        self.settings_resistance_training_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_resistance_training_var, values=["Yes", "No"])
        self.settings_resistance_training_options.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Experience Level
        ctk.CTkLabel(activity_frame, text="Experience Level:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_experience_level_var = ctk.StringVar()
        experience_options = ["Beginner (0-1 yr)", "Novice (1-2 yrs)", "Intermediate (2-4 yrs)", "Advanced (4-10 yrs)", "Elite (10+ yrs)"]
        self.settings_experience_level_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_experience_level_var, values=experience_options)
        self.settings_experience_level_options.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Workout Type
        ctk.CTkLabel(activity_frame, text="Workout Type:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_workout_type_var = ctk.StringVar()
        workout_options = ["Bodybuilding", "Strength", "Powerlifting", "Weightlifting", "Crossfit", "Calisthenics", "General Fitness"] # Match descriptions/keys used elsewhere
        self.settings_workout_type_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_workout_type_var, values=workout_options)
        self.settings_workout_type_options.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Workout Days
        ctk.CTkLabel(activity_frame, text="Workout Days/Week:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_workout_days_entry = ctk.CTkEntry(activity_frame)
        self.settings_workout_days_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Resistance Training
        ctk.CTkLabel(activity_frame, text="Resistance Training:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_resistance_training_var = ctk.StringVar()
        self.settings_resistance_training_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_resistance_training_var, values=["Yes", "No"])
        self.settings_resistance_training_options.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Athlete Status
        ctk.CTkLabel(activity_frame, text="Athlete Status:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_athlete_status_var = ctk.StringVar()
        self.settings_athlete_status_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_athlete_status_var, values=["Yes", "No"])
        self.settings_athlete_status_options.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Job Activity
        ctk.CTkLabel(activity_frame, text="Job Activity:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.settings_job_activity_var = ctk.StringVar()
        job_options = ["sedentary: Desk job", "light: Teacher, Sales", "moderate: Construction", "active: Courier, Farmer"]
        self.settings_job_activity_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_job_activity_var, values=job_options)
        self.settings_job_activity_options.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

        # Leisure Activity
        ctk.CTkLabel(activity_frame, text="Leisure Activity:").grid(row=8, column=0, padx=10, pady=5, sticky="w")
        self.settings_leisure_activity_var = ctk.StringVar()
        leisure_options = ["sedentary: Little activity", "light: Walking, gardening", "moderate: Hiking, dancing", "active: Sports, intense exercise"]
        self.settings_leisure_activity_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_leisure_activity_var, values=leisure_options)
        self.settings_leisure_activity_options.grid(row=8, column=1, padx=10, pady=5, sticky="ew")


        # --- Nutrition Section ---
        nutrition_frame = ctk.CTkFrame(settings_scroll_frame)
        nutrition_frame.grid(row=row_idx, column=0, padx=10, pady=10, sticky="ew")
        nutrition_frame.grid_columnconfigure(1, weight=1)
        row_idx += 1

        ctk.CTkLabel(nutrition_frame, text="Nutrition", font=("Roboto", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(5, 10), sticky="w")

        # Protein Intake
        ctk.CTkLabel(nutrition_frame, text="Avg Protein Intake (g):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.settings_protein_intake_entry = ctk.CTkEntry(nutrition_frame)
        self.settings_protein_intake_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")


        # --- Goals Section ---
        goals_frame = ctk.CTkFrame(settings_scroll_frame)
        goals_frame.grid(row=row_idx, column=0, padx=10, pady=10, sticky="ew")
        goals_frame.grid_columnconfigure(1, weight=1)
        row_idx += 1

        ctk.CTkLabel(goals_frame, text="Goals", font=("Roboto", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(5, 10), sticky="w")

        # Goal Weight
        ctk.CTkLabel(goals_frame, text="Goal Weight (lbs):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.settings_goal_weight_entry = ctk.CTkEntry(goals_frame)
        self.settings_goal_weight_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Goal Body Fat
        ctk.CTkLabel(goals_frame, text="Goal Body Fat (%):").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_goal_bf_entry = ctk.CTkEntry(goals_frame)
        self.settings_goal_bf_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Goal Timeframe
        ctk.CTkLabel(goals_frame, text="Goal Timeframe:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.settings_goal_timeframe_var = ctk.StringVar()
        timeframe_options = ["Not Set", "8 Weeks", "10 Weeks", "12 Weeks", "16 Weeks", "Custom Weeks", "Custom Date"] # Added Options
        self.settings_goal_timeframe_options = ctk.CTkOptionMenu(goals_frame, variable=self.settings_goal_timeframe_var, values=timeframe_options)
        self.settings_goal_timeframe_options.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
        # TODO: Add entry/datepicker for Custom options if selected

        # --- Appearance Section ---
        appearance_frame = ctk.CTkFrame(settings_scroll_frame)
        appearance_frame.grid(row=row_idx, column=0, padx=10, pady=10, sticky="ew")
        appearance_frame.grid_columnconfigure(1, weight=1)
        row_idx += 1

        ctk.CTkLabel(appearance_frame, text="Appearance", font=("Roboto", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(5, 10), sticky="w")

        # Theme Selection
        ctk.CTkLabel(appearance_frame, text="Theme:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        available_themes = self.theme_manager.get_theme_names() # Corrected method name
        self.settings_theme_var = ctk.StringVar()
        self.settings_theme_options = ctk.CTkOptionMenu(
            appearance_frame,
            variable=self.settings_theme_var,
            values=available_themes,
            command=self.apply_selected_theme # Apply immediately on change
        )
        self.settings_theme_options.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # --- Save Button ---
        save_button = ctk.CTkButton(settings_scroll_frame, text="Save Settings", command=self.save_settings)
        save_button.grid(row=row_idx, column=0, padx=10, pady=20, sticky="ew")
        row_idx += 1

        # Load current settings into fields
        self.load_settings()

    def load_settings(self):
        """Load current user settings into the settings tab fields."""
        user_id_to_load = self.current_user_id
        if not user_id_to_load:
            print("Cannot load settings: User ID not set.")
            return

        # Use the existing get_user_data method from the auth object
        # which should be populated correctly in __init__ now
        user_data = self.auth.get_user_data() 
        if not user_data:
            print(f"Cannot load settings: Failed to retrieve user data for user ID {user_id_to_load}.")
            # Clear fields or set defaults if user data is missing
            self.settings_name_entry.delete(0, "end")
            self.settings_age_entry.delete(0, "end")
            self.settings_gender_var.set("m")
            self.settings_height_ft_entry.delete(0, "end")
            self.settings_height_in_entry.delete(0, "end")
            self.settings_goal_weight_entry.delete(0, "end")
            self.settings_goal_bf_entry.delete(0, "end")
            if hasattr(self, 'settings_goal_timeframe_var'):
                self.settings_goal_timeframe_var.set("Not Set")
            # ... clear other fields ...
            if hasattr(self, 'settings_theme_var'):
                available_themes = self.theme_manager.get_theme_names()
                self.settings_theme_var.set(available_themes[0] if available_themes else "")
            return

        self.current_user_data = user_data # Update local cache

        # Populate Profile fields
        self.settings_name_entry.delete(0, "end")
        self.settings_name_entry.insert(0, user_data.get('name', ''))

        self.settings_age_entry.delete(0, "end")
        self.settings_age_entry.insert(0, str(user_data.get('age', '')))

        self.settings_gender_var.set(user_data.get('gender', 'm'))

        # Height
        total_height_inches = user_data.get('height', 0)
        feet = int(total_height_inches // 12) if total_height_inches else 0
        inches = int(total_height_inches % 12) if total_height_inches else 0
        self.settings_height_ft_entry.delete(0, "end")
        self.settings_height_ft_entry.insert(0, str(feet))
        self.settings_height_in_entry.delete(0, "end")
        self.settings_height_in_entry.insert(0, str(inches))

        # Populate Goals fields
        self.settings_goal_weight_entry.delete(0, "end")
        self.settings_goal_weight_entry.insert(0, str(user_data.get('goal_weight', '')))

        self.settings_goal_bf_entry.delete(0, "end")
        self.settings_goal_bf_entry.insert(0, str(user_data.get('goal_bf', '') or '')) # Handle None

        # Goal Timeframe
        if hasattr(self, 'settings_goal_timeframe_var'):
            self.settings_goal_timeframe_var.set(user_data.get('goal_timeframe', 'Not Set')) # Default to "Not Set"

        # Populate Activity & Experience fields
        activity_level_db = user_data.get('activity_level', 1) # Get numeric value
        if hasattr(self, 'settings_activity_level_options'):
            activity_options = self.settings_activity_level_options.cget("values")
            matching_activity = next((opt for opt in activity_options if opt.startswith(str(activity_level_db))), activity_options[0])
            self.settings_activity_level_var.set(matching_activity)

        # Load resistance training
        if hasattr(self, 'settings_resistance_training_var'):
            self.settings_resistance_training_var.set("Yes" if user_data.get('resistance_training', False) else "No")

        # Load resistance training
        if hasattr(self, 'settings_resistance_training_var'):
            self.settings_resistance_training_var.set("Yes" if user_data.get('resistance_training', False) else "No")

        # Load resistance training
        if hasattr(self, 'settings_resistance_training_var'):
            self.settings_resistance_training_var.set("Yes" if user_data.get('resistance_training', False) else "No")

        # Load resistance training
        if hasattr(self, 'settings_resistance_training_var'):
            self.settings_resistance_training_var.set("Yes" if user_data.get('resistance_training', False) else "No")

        experience_db = user_data.get('experience_level') # Get value, might be None
        experience_default = 'Beginner' # Define default
        if hasattr(self, 'settings_experience_level_options'):
            experience_options = self.settings_experience_level_options.cget("values")
            # Use default if DB value is None, otherwise use DB value
            experience_to_match = experience_db if experience_db is not None else experience_default
            matching_experience = next((opt for opt in experience_options if opt.startswith(experience_to_match)), experience_options[0])
            self.settings_experience_level_var.set(matching_experience)

        if hasattr(self, 'settings_workout_type_var'):
            self.settings_workout_type_var.set(user_data.get('workout_type', 'General Fitness'))

        if hasattr(self, 'settings_workout_days_entry'):
            self.settings_workout_days_entry.delete(0, "end")
            self.settings_workout_days_entry.insert(0, str(user_data.get('workout_days', '') or '')) # Handle None

        if hasattr(self, 'settings_resistance_training_var'):
            self.settings_resistance_training_var.set("Yes" if user_data.get('resistance_training', False) else "No")
        if hasattr(self, 'settings_athlete_status_var'):
            self.settings_athlete_status_var.set("Yes" if user_data.get('is_athlete', False) else "No")

        if hasattr(self, 'settings_job_activity_var'):
             job_activity_db = user_data.get('job_activity') # Get value, might be None
             job_default = 'sedentary'
             job_options = self.settings_job_activity_options.cget("values")
             job_to_match = job_activity_db if job_activity_db is not None else job_default
             matching_job = next((opt for opt in job_options if opt.startswith(job_to_match)), job_options[0])
             self.settings_job_activity_var.set(matching_job)

        if hasattr(self, 'settings_leisure_activity_var'):
             leisure_activity_db = user_data.get('leisure_activity') # Get value, might be None
             leisure_default = 'sedentary'
             leisure_options = self.settings_leisure_activity_options.cget("values")
             leisure_to_match = leisure_activity_db if leisure_activity_db is not None else leisure_default
             matching_leisure = next((opt for opt in leisure_options if opt.startswith(leisure_to_match)), leisure_options[0])
             self.settings_leisure_activity_var.set(matching_leisure)

        if hasattr(self, 'settings_protein_intake_entry'):
             self.settings_protein_intake_entry.delete(0, "end")
             self.settings_protein_intake_entry.insert(0, str(user_data.get('protein_intake', '') or '')) # Handle None

        if hasattr(self, 'settings_dob_entry'):
            self.settings_dob_entry.delete(0, "end")
            self.settings_dob_entry.insert(0, user_data.get('dob', '') or '') # Handle None

        # Populate Appearance fields
        preferred_theme = user_data.get('preferred_theme', 'enhanced_blue')
        available_themes = self.theme_manager.get_theme_names() # Corrected method name
        if preferred_theme in available_themes:
             self.settings_theme_var.set(preferred_theme)
        elif available_themes:
             self.settings_theme_var.set(available_themes[0]) # Fallback to first available

    def save_settings(self):
        """Save the settings from the settings tab to the database."""
        user_id_to_save = self.current_user_id # Use the default user ID
        if not user_id_to_save:
            messagebox.showerror("Error", "User ID not set. Cannot save settings.")
            return

        try:
            # Read values from fields
            name = self.settings_name_entry.get()
            age_str = self.settings_age_entry.get()
            gender = self.settings_gender_var.get()
            height_ft_str = self.settings_height_ft_entry.get()
            height_in_str = self.settings_height_in_entry.get()
            dob = self.settings_dob_entry.get() if hasattr(self, 'settings_dob_entry') else None

            activity_level_str = self.settings_activity_level_var.get() if hasattr(self, 'settings_activity_level_var') else ''
            experience_level_str = self.settings_experience_level_var.get() if hasattr(self, 'settings_experience_level_var') else ''
            workout_type_str = self.settings_workout_type_var.get() if hasattr(self, 'settings_workout_type_var') else ''
            workout_days_str = self.settings_workout_days_entry.get() if hasattr(self, 'settings_workout_days_entry') else ''
            resistance_training_str = self.settings_resistance_training_var.get() if hasattr(self, 'settings_resistance_training_var') else 'No'
            athlete_status_str = self.settings_athlete_status_var.get() if hasattr(self, 'settings_athlete_status_var') else 'No'
            job_activity_str = self.settings_job_activity_var.get() if hasattr(self, 'settings_job_activity_var') else ''
            leisure_activity_str = self.settings_leisure_activity_var.get() if hasattr(self, 'settings_leisure_activity_var') else ''
            protein_intake_str = self.settings_protein_intake_entry.get() if hasattr(self, 'settings_protein_intake_entry') else ''

            goal_weight_str = self.settings_goal_weight_entry.get()
            goal_bf_str = self.settings_goal_bf_entry.get()
            goal_timeframe = self.settings_goal_timeframe_var.get() if hasattr(self, 'settings_goal_timeframe_var') else None # Added
            selected_theme = self.settings_theme_var.get()

            # Validate and convert
            age = int(age_str) if age_str and age_str.isdigit() else None 
            height_ft = int(height_ft_str) if height_ft_str and height_ft_str.isdigit() else 0
            height_in = int(height_in_str) if height_in_str and height_in_str.isdigit() else 0
            total_height_inches = (height_ft * 12) + height_in

            if dob and dob.strip(): 
                try:
                    datetime.datetime.strptime(dob, "%m%d%y")
                except ValueError:
                    messagebox.showerror("Input Error", "Invalid Date of Birth format. Use MMDDYY.")
                    return
            else:
                dob = None 

            activity_level = int(activity_level_str.split(":")[0]) if activity_level_str else 1
            experience_level = experience_level_str.split(" ")[0] if experience_level_str else "Beginner"
            workout_type = workout_type_str if workout_type_str else "General Fitness"
            workout_days = int(workout_days_str) if workout_days_str and workout_days_str.isdigit() else 0
            resistance_training = True if resistance_training_str == "Yes" else False
            is_athlete = True if athlete_status_str == "Yes" else False
            job_activity = job_activity_str.split(":")[0] if job_activity_str else 'sedentary'
            leisure_activity = leisure_activity_str.split(":")[0] if leisure_activity_str else 'sedentary'
            protein_intake = float(protein_intake_str) if protein_intake_str else 0.0

            goal_weight = float(goal_weight_str) if goal_weight_str else None
            goal_bf = float(goal_bf_str) if goal_bf_str else None

            # Prepare settings dictionary
            settings_to_update = {
                'name': name,
                'age': age,
                'gender': gender,
                'height': total_height_inches,
                'dob': dob,
                'activity_level': activity_level,
                'experience_level': experience_level,
                'workout_type': workout_type,
                'workout_days': workout_days,
                'resistance_training': resistance_training,
                'is_athlete': is_athlete,
                'job_activity': job_activity, 
                'leisure_activity': leisure_activity, 
                'protein_intake': protein_intake, 
                'goal_weight': goal_weight,
                'goal_bf': goal_bf,
                'goal_timeframe': goal_timeframe if goal_timeframe != "Not Set" else None, # Save None if "Not Set"
                'preferred_theme': selected_theme
            }

            # Update database via auth module using the specific user ID
            # Use the existing update_settings method, ensuring self.auth.current_user is set
            if self.auth.current_user and self.auth.current_user.get('user_id') == user_id_to_save:
                 self.auth.is_authenticated = True # Ensure it's marked as logged in for update_settings
                 success, message = self.auth.update_settings(settings_to_update)
            else:
                 success = False
                 message = "Internal error: Auth context mismatch."


            if success:
                messagebox.showinfo("Success", "Settings saved successfully.")
                # Update local user data cache
                self.current_user_data = self.auth.get_user_data() # Re-fetch using the logged-in context
                # Apply theme immediately
                self.apply_selected_theme(selected_theme)
                # Refresh dashboard goals widget
                self.refresh_dashboard_widgets()
            else:
                messagebox.showerror("Error", f"Failed to save settings: {message}")

        except ValueError as ve:
             messagebox.showerror("Input Error", f"Invalid numeric value entered: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving settings: {str(e)}")
            traceback.print_exc()

    def apply_selected_theme(self, theme_name):
         """Applies the selected theme and saves it."""
         try:
             print(f"Applying theme: {theme_name}")
             self.theme_manager.apply_theme(theme_name)
             
             # Force update of all widgets
             self.update_idletasks()
             
             # Save the theme preference persistently for the current user
             user_id_to_save = self.current_user_id
             if user_id_to_save:
                 # Use the existing set_preferred_theme method
                 if self.auth.current_user and self.auth.current_user.get('user_id') == user_id_to_save:
                     self.auth.is_authenticated = True # Ensure logged-in state for method
                     self.auth.set_preferred_theme(theme_name) 
                     print(f"Saved theme preference: {theme_name}")
                 else:
                      print("[WARNING] Auth context mismatch when setting theme.")
                      
             # Explicitly update all frames and widgets to ensure theme is applied
             for widget in self.winfo_children():
                 if hasattr(widget, 'update'):
                     widget.update()

         except Exception as e:
              messagebox.showerror("Theme Error", f"Failed to apply theme '{theme_name}': {e}")
              # Optionally revert to a default theme
              self.theme_manager.apply_theme("enhanced_blue")
              user_id_to_save = self.current_user_id
              if user_id_to_save and self.auth.current_user and self.auth.current_user.get('user_id') == user_id_to_save:
                  self.auth.is_authenticated = True
                  self.auth.set_preferred_theme("enhanced_blue")


    def setup_about_tab(self):
        """Set up the about tab with application information."""
         # Clear previous widgets if any
        for widget in self.about_tab.winfo_children():
            widget.destroy()

        about_frame = ctk.CTkFrame(self.about_tab)
        about_frame.pack(expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(about_frame, text="Enhanced Body Fat Estimator", font=("Roboto", 20, "bold"))
        title.pack(pady=10)

        version = ctk.CTkLabel(about_frame, text="Version 2.0 (Enhanced)", font=("Roboto", 14))
        version.pack(pady=5)

        description = ctk.CTkLabel(
            about_frame,
            text="This application helps you estimate body fat percentage, track progress, "
                 "and provides insights into your fitness journey using advanced calculations and AI analysis.",
            wraplength=500,
            justify="center"
        )
        description.pack(pady=10)

        # Add more info like author, license, etc. if desired
        author = ctk.CTkLabel(about_frame, text="Developed by: Tiran Winston & AI Assistant")
        author.pack(pady=5)

    def start_voice_input(self):
        """Handle the voice input button click."""
        user_id = self.current_user_id
        if not user_id:
             messagebox.showerror("Error", "User ID not set. Cannot use voice input.")
             return

        try:
            result = voice_input.show_voice_input_dialog(self)
            if result:
                # Process the result data
                print("Voice Input Result:", result) # Debug print
                # Populate fields based on result
                if result.get('date'):
                    try:
                        # Convert YYYY-MM-DD back to MM/DD/YYYY for the entry field
                        date_obj = datetime.datetime.strptime(result['date'], "%Y-%m-%d")
                        self.date_entry.delete(0, "end")
                        self.date_entry.insert(0, date_obj.strftime("%m/%d/%Y"))
                    except ValueError:
                        print(f"Error parsing date from voice input: {result['date']}")

                if result.get('weight') is not None:
                    self.weight_entry.delete(0, "end")
                    self.weight_entry.insert(0, str(result['weight']))

                if result.get('body_fat') is not None:
                    self.bf_entry.delete(0, "end")
                    self.bf_entry.insert(0, str(result['body_fat']))

                for m_type, value in result.get('measurements', {}).items():
                    if m_type in self.measurement_entries:
                        self.measurement_entries[m_type].delete(0, "end")
                        self.measurement_entries[m_type].insert(0, str(value))

                # Ask user if they want to save now
                if messagebox.askyesno("Save Data?", "Voice input received. Save this data now?"):
                     self.save_weekly_data()
                     self.save_measurements_data()

        except Exception as e:
            messagebox.showerror("Voice Input Error", f"Failed to process voice input: {str(e)}")
            traceback.print_exc()


    def _on_tutorial_complete(self, completed):
        """Callback when tutorial finishes."""
        print(f"Tutorial completed status: {completed}")
        # Update user setting if tutorial was completed
        user_id_to_save = self.current_user_id
        if completed and user_id_to_save:
             # Use the existing update_settings method
             if self.auth.current_user and self.auth.current_user.get('user_id') == user_id_to_save:
                 self.auth.is_authenticated = True
                 self.auth.update_settings({'tutorial_completed': 1})
             else:
                  print("[WARNING] Auth context mismatch when saving tutorial status.")


    def check_show_tutorial(self):
         """Check if the welcome tutorial should be shown."""
         user_id_to_check = self.current_user_id
         if user_id_to_check:
             # Use the existing get_user_data method
             user_data = self.auth.get_user_data()
             if user_data and not user_data.get('tutorial_completed', 0):
                  # Use after to delay showing the tutorial slightly
                  self.after(500, lambda: show_welcome_tutorial(self, on_complete=self._on_tutorial_complete))

    # --- Report Generation & Display ---
    def generate_report(self):
        """Generate report from form data in the Input tab."""
        initial_data = self.get_input_data_for_report() # New helper method
        if not initial_data:
            return # Stop if validation failed

        try:
            # Get progression data from DB
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT date, weight, bodyfat AS body_fat_percentage FROM weekly_progress WHERE user_id = ? ORDER BY date ASC", (self.current_user_id,))
            progression_rows = cursor.fetchall()
            conn.close()

            progression_data = []
            if progression_rows:
                 for date_str, weight, bf in progression_rows:
                     try:
                         date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                         progression_data.append({
                             "date": date_obj.strftime("%m/%d/%Y"),
                             "weight": weight,
                             "body_fat_percentage": bf 
                         })
                     except ValueError:
                         print(f"Skipping invalid date in progress data: {date_str}")
            else:
                 try:
                      start_date_obj = datetime.datetime.strptime(initial_data['start_date'], "%m/%d/%Y") 
                      progression_data = [{
                          "date": start_date_obj.strftime("%m/%d/%Y"),
                          "weight": initial_data['current_weight'],
                          "body_fat_percentage": initial_data['current_bf']
                      }]
                 except KeyError:
                      messagebox.showerror("Error", "Missing start date, current weight, or current body fat in input data.")
                      return
                 except ValueError:
                      messagebox.showerror("Error", "Invalid start date format. Use MM/DD/YYYY.")
                      return

            if not progression_data:
                 messagebox.showerror("Error", "No progress data available to generate a report.")
                 return

            try:
                height_ft = initial_data.get('height_feet', 0)
                height_in = initial_data.get('height_inches', 0)
                initial_data['height_cm'] = (height_ft * 12 + height_in) * 2.54
            except Exception as hc_err:
                 messagebox.showerror("Error", f"Could not calculate height in cm: {hc_err}")
                 return

            self.current_report = generate_comprehensive_report(progression_data, initial_data)

            report_name = initial_data.get("name", "UserReport")
            self.saved_files = save_report(self.current_report, report_name, "both") 

            try:
                 with open("last_report_data.json", "w") as f:
                     json.dump(initial_data, f, indent=4, default=str) 
            except Exception as e:
                 print(f"Warning: Could not save last report data: {e}")

            self.add_report_to_history(report_name, self.saved_files)

            self.display_results()
            self.tab_view.set("Reports") 
            messagebox.showinfo("Success", "Report generated successfully!")

        except KeyError as ke:
             messagebox.showerror("Error", f"Failed to generate report: Missing key {ke}")
             traceback.print_exc()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            traceback.print_exc()

    def get_input_data_for_report(self):
         """Helper to gather data from Settings and Input Tab fields for report generation."""
         data = {}
         errors = []

         if not hasattr(self, 'settings_name_entry'):
              messagebox.showerror("Error", "Settings tab not fully initialized. Cannot generate report.")
              return None

         try:
            # Read from Settings Tab 
            data['name'] = self.settings_name_entry.get() or "User"
            data['gender'] = self.settings_gender_var.get() or "m"
            data['dob'] = self.settings_dob_entry.get() or None

            height_ft_str = self.settings_height_ft_entry.get() or '0'
            height_in_str = self.settings_height_in_entry.get() or '0'
            data['height_feet'] = int(height_ft_str) if height_ft_str.isdigit() else 0
            data['height_inches'] = int(height_in_str) if height_in_str.isdigit() else 0

            goal_weight_str = self.settings_goal_weight_entry.get() or ''
            data['goal_weight'] = float(goal_weight_str) if goal_weight_str else 0.0

            goal_bf_str = self.settings_goal_bf_entry.get() or ''
            data['goal_bf'] = float(goal_bf_str) if goal_bf_str else 0.0
            
            # Get goal timeframe from settings
            data['goal_timeframe'] = self.settings_goal_timeframe_var.get() if hasattr(self, 'settings_goal_timeframe_var') else None


            activity_level_str = self.settings_activity_level_var.get() or ''
            data['activity_level'] = int(activity_level_str.split(":")[0]) if activity_level_str else 1

            experience_level_str = self.settings_experience_level_var.get() or ''
            data['experience_level'] = experience_level_str.split(" ")[0] if experience_level_str else "Beginner"

            workout_type_str = self.settings_workout_type_var.get() or ''
            data['workout_type'] = workout_type_str if workout_type_str else "General Fitness"

            workout_days_str = self.settings_workout_days_entry.get() or ''
            data['workout_days'] = int(workout_days_str) if workout_days_str and workout_days_str.isdigit() else 0

            resistance_training_str = self.settings_resistance_training_var.get() or 'No'
            data['resistance_training'] = True if resistance_training_str == "Yes" else False

            athlete_status_str = self.settings_athlete_status_var.get() or 'No'
            data['is_athlete'] = True if athlete_status_str == "Yes" else False

            job_activity_str = self.settings_job_activity_var.get() or ''
            data['job_activity'] = job_activity_str.split(":")[0] if job_activity_str else 'sedentary'

            leisure_activity_str = self.settings_leisure_activity_var.get() or ''
            data['leisure_activity'] = leisure_activity_str.split(":")[0] if leisure_activity_str else 'sedentary'

            protein_intake_str = self.settings_protein_intake_entry.get() or ''
            data['protein_intake'] = float(protein_intake_str) if protein_intake_str else 0.0

            # Read from Input Tab 
            data['start_date'] = self.date_entry.get() 
            data['end_date'] = self.date_entry.get()   

            current_weight_str = self.weight_entry.get()
            if not current_weight_str: errors.append("Current Weight (Input Tab) is required.")
            else: data['current_weight'] = float(current_weight_str)

            current_bf_str = self.bf_entry.get()
            if not current_bf_str: errors.append("Current Body Fat (Input Tab) is required.")
            else: data['current_bf'] = float(current_bf_str)

            # Validate date format (MM/DD/YYYY) from Input Tab
            try:
                date_obj = datetime.datetime.strptime(data['start_date'], "%m/%d/%Y")
            except ValueError:
                errors.append(f"Invalid date format for Start/End Date: {data['start_date']}. Use MM/DD/YYYY.")

            # DOB validation (MMDDYY format)
            if data['dob']:
                try:
                    datetime.datetime.strptime(data['dob'], "%m%d%y")
                except ValueError:
                    errors.append(f"Invalid date format for DOB: {data['dob']}. Use MMDDYY.")
                    data['dob'] = None 
            else:
                 pass 

         except ValueError as ve:
              errors.append(f"Invalid numeric value entered: {ve}")
         except AttributeError as ae:
              errors.append(f"A required UI element might be missing: {ae}")
              traceback.print_exc()
         except Exception as e:
              errors.append(f"Error reading input data: {e}")
              traceback.print_exc()

         if errors:
              messagebox.showerror("Input Error", "Please correct the following errors:\n\n" + "\n".join(errors))
              return None

         # Add derived fields 
         data['activity_level_description'] = next((opt.split(": ")[1] for opt in self.settings_activity_level_options.cget("values") if opt.startswith(str(data['activity_level']))), "Unknown")
         
         # Calculate and add RMR
         try:
             # Get age from data, defaulting to 30 if not available
             age_for_rmr = data.get('age', 30)  # Use age from data or default to 30
             
             # Calculate height in cm from data height_feet and height_inches
             height_feet = data.get('height_feet', 0)
             height_inches = data.get('height_inches', 0)
             total_height_in_inches = (height_feet * 12) + height_inches
             height_cm_for_rmr = total_height_in_inches * 2.54
             
             weight_kg_for_rmr = data['current_weight'] / 2.20462 # Convert lbs to kg
             is_athlete_for_rmr = data.get('is_athlete', False)
             
             data['rmr'] = calculate_rmr(weight_kg_for_rmr, age_for_rmr, data['gender'], height_cm_for_rmr, is_athlete_for_rmr)
         except Exception as rmr_err:
             errors.append(f"Could not calculate RMR: {rmr_err}")
             data['rmr'] = None # Ensure key exists even if calculation fails

         if errors: # Re-check errors after RMR calculation attempt
              messagebox.showerror("Input Error", "Please correct the following errors:\n\n" + "\n".join(errors))
              return None

         return data

    def add_report_to_history(self, report_name, saved_files_dict):
         """Adds a generated report to the database history."""
         try:
             conn = sqlite3.connect(DB_FILE)
             cursor = conn.cursor()
             cursor.execute(
                 """INSERT INTO report_history (name, date, json_path, md_path, pdf_path)
                    VALUES (?, ?, ?, ?, ?)""",
                 (
                     report_name,
                     datetime.datetime.now().strftime("%Y-%m-%d"),
                     saved_files_dict.get("json"),
                     saved_files_dict.get("markdown"),
                     saved_files_dict.get("pdf"),
                 ),
             )
             conn.commit()
             conn.close()
         except Exception as e:
             print(f"Error saving report to history DB: {e}")
             traceback.print_exc()


    def display_results(self):
        """Display the generated report results in the Results tab"""
        # Ensure results_frame exists (might need to be created in setup_report_tab or similar)
        if not hasattr(self, 'results_frame'):
             # Create it if it doesn't exist (example placement)
             self.results_frame = ctk.CTkScrollableFrame(self.report_tab)
             self.results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
             print("[WARNING] results_frame created dynamically in display_results.")

        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not hasattr(self, 'current_report') or not self.current_report:
            ctk.CTkLabel(self.results_frame, text="No report generated yet.").pack(pady=20)
            return

        # Display key results 
        ctk.CTkLabel(self.results_frame, text=f"Report for: {self.current_report.get('name', 'N/A')}", font=("Roboto", 18, "bold")).pack(pady=10, anchor="w")
        ctk.CTkLabel(self.results_frame, text=f"Generated on: {self.current_report.get('report_date', 'N/A')}").pack(pady=2, anchor="w")

        summary_frame = ctk.CTkFrame(self.results_frame)
        summary_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(summary_frame, text="Summary:", font=("Roboto", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")
        ctk.CTkLabel(summary_frame, text=f"Duration: {self.current_report.get('total_weeks', 'N/A')} weeks").grid(row=1, column=0, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(summary_frame, text=f"Total Weight Loss: {self.current_report.get('total_weight_loss', 'N/A')} lbs").grid(row=1, column=1, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(summary_frame, text=f"Final Weight: {self.current_report.get('final_weight', 'N/A')} lbs").grid(row=6, column=0, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(summary_frame, text=f"Total Body Fat Reduction: {self.current_report.get('total_bf_loss', 'N/A')}%").grid(row=6, column=1, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(summary_frame, text=f"Final Body Fat: {self.current_report.get('final_body_fat', 'N/A')}%").grid(row=6, column=0, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(summary_frame, text=f"Total Muscle Gain: {self.current_report.get('total_muscle_gain', 'N/A')} lbs").grid(row=6, column=1, padx=10, pady=2, sticky="w")

        # Display charts 
        chart_frame = ctk.CTkFrame(self.results_frame)
        chart_frame.pack(fill="both", expand=True, pady=10)
        chart_frame.grid_columnconfigure((0, 1), weight=1)
        chart_frame.grid_rowconfigure(0, weight=1)

        try:
            if 'weight_progress_chart' in self.current_report:
                 img_data = base64.b64decode(self.current_report['weight_progress_chart'])
                 img = Image.open(io.BytesIO(img_data))
                 ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 300)) 
                 img_label = ctk.CTkLabel(chart_frame, image=ctk_img, text="")
                 img_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

            if 'body_composition_chart' in self.current_report:
                 img_data = base64.b64decode(self.current_report['body_composition_chart'])
                 img = Image.open(io.BytesIO(img_data))
                 ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 300)) 
                 img_label = ctk.CTkLabel(chart_frame, image=ctk_img, text="")
                 img_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        except Exception as e:
             ctk.CTkLabel(chart_frame, text=f"Error displaying charts: {e}").grid(row=0, column=0, columnspan=2)


        # Buttons to open saved files
        button_frame = ctk.CTkFrame(self.results_frame)
        button_frame.pack(fill="x", pady=10)

        if hasattr(self, 'saved_files') and self.saved_files and self.saved_files.get("pdf"):
            pdf_path = self.saved_files["pdf"]
            pdf_btn = ctk.CTkButton(button_frame, text="Open PDF Report", command=lambda p=pdf_path: self.open_file(p))
            pdf_btn.pack(side="left", padx=10, pady=10)

        if hasattr(self, 'saved_files') and self.saved_files and self.saved_files.get("markdown"):
            md_path = self.saved_files["markdown"]
            md_btn = ctk.CTkButton(button_frame, text="Open Markdown Report", command=lambda p=md_path: self.open_file(p))
            md_btn.pack(side="left", padx=10, pady=10)

    def open_file(self, file_path):
        """Open a file using the default system application."""
        try:
            if os.path.exists(file_path):
                if sys.platform == "win32":
                    os.startfile(os.path.abspath(file_path))
                elif sys.platform == "darwin": # macOS
                    subprocess.call(["open", os.path.abspath(file_path)])
                else: # Linux
                    subprocess.call(["xdg-open", os.path.abspath(file_path)])
            else:
                messagebox.showerror("Error", f"File not found: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")


# --- Main Execution ---
if __name__ == "__main__":
    app = EnhancedBodyFatEstimator()
    app.mainloop()
