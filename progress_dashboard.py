#!/usr/bin/env python
# progress_dashboard.py - Progress tracking and visualization for Body Fat Estimator
# Created: 03/28/25
# Description: Links weekly updates to initial measurements and visualizes progress

import os
import sys
import sqlite3
import customtkinter as ctk
from datetime import datetime
import traceback
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
from dashboard_widgets import DashboardWidgets

class ProgressDashboard:
    """Class to handle progress tracking and visualization"""
    
    def __init__(self, parent_frame, user_id=None, app_instance=None):
        """
        Initialize the progress dashboard
        
        Args:
            parent_frame: The frame where the dashboard will be displayed
            user_id: The user ID for which to display progress
            app_instance: The parent app instance
        """
        self.parent_frame = parent_frame
        self.user_id = user_id
        self.app_instance = app_instance
        self.data_frame = None
        self.initial_measurements = None
        self.weekly_updates = None
        self.comparison_data = None
        
        # Create dashboard widgets
        self.dashboard_widgets = DashboardWidgets(self.parent_frame, app_instance)
        
        # Load data if user ID is provided
        if self.user_id is not None:
            self.refresh(self.user_id)
        
    def setup_ui(self):
        """Set up the UI elements for the progress dashboard"""
        # Main container
        self.container = ctk.CTkFrame(self.parent_frame)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.container, 
            text="Progress Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(10, 20))
        
        # Progress summary section
        self.summary_frame = ctk.CTkFrame(self.container)
        self.summary_frame.pack(fill="x", padx=10, pady=10)
        
        self.summary_title = ctk.CTkLabel(
            self.summary_frame,
            text="Progress Summary",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.summary_title.pack(pady=(10, 5), anchor="w")
        
        # Comparison metrics
        self.metrics_frame = ctk.CTkFrame(self.summary_frame)
        self.metrics_frame.pack(fill="x", padx=10, pady=10)
        
        # Create placeholder for metrics
        self.setup_comparison_metrics()
        
        # Charts section
        self.charts_frame = ctk.CTkFrame(self.container)
        self.charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.charts_title = ctk.CTkLabel(
            self.charts_frame,
            text="Progress Charts",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.charts_title.pack(pady=(10, 5), anchor="w")
        
        # Create placeholder for charts
        self.charts_container = ctk.CTkFrame(self.charts_frame)
        self.charts_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Historical data section
        self.history_frame = ctk.CTkFrame(self.container)
        self.history_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.history_title = ctk.CTkLabel(
            self.history_frame,
            text="Historical Data",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.history_title.pack(pady=(10, 5), anchor="w")
        
        # Create placeholder for table
        self.table_container = ctk.CTkFrame(self.history_frame)
        self.table_container.pack(fill="both", expand=True, padx=10, pady=10)
        
    def setup_comparison_metrics(self):
        """Set up the comparison metrics UI"""
        # Clear existing widgets
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
            
        # Create grid layout for metrics
        self.metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Headers
        headers = ["Metric", "Initial", "Current", "Change"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.metrics_frame,
                text=header,
                font=ctk.CTkFont(weight="bold")
            )
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        # Placeholder metrics (will be populated with actual data later)
        metrics = [
            ["Weight (lbs)", "0.0", "0.0", "0.0"],
            ["Body Fat (%)", "0.0", "0.0", "0.0"],
            ["Lean Mass (lbs)", "0.0", "0.0", "0.0"],
            ["Fat Mass (lbs)", "0.0", "0.0", "0.0"],
            ["RMR (calories)", "0", "0", "0"],
            ["TDEE (calories)", "0", "0", "0"]
        ]
        
        for i, metric in enumerate(metrics):
            for j, value in enumerate(metric):
                label = ctk.CTkLabel(self.metrics_frame, text=value)
                label.grid(row=i+1, column=j, padx=5, pady=5, sticky="w")
    
    def load_data(self, user_id=None):
        """
        Load data for the given user ID
        
        Args:
            user_id: The user ID to load data for
        """
        if user_id is not None:
            self.user_id = user_id
            
        if self.user_id is None:
            print("No user ID provided, cannot load data")
            return
            
        try:
            # Connect to database
            conn = sqlite3.connect("history.db")
            
            # Load initial measurements
            initial_query = """
                SELECT 
                    date, weight, body_fat, lean_mass, fat_mass, rmr, tdee, notes
                FROM 
                    initial_measurements
                WHERE 
                    user_id = ?
                ORDER BY 
                    date ASC
                LIMIT 1
            """
            initial_df = pd.read_sql_query(initial_query, conn, params=(self.user_id,))
            
            # Load weekly updates
            weekly_query = """
                SELECT 
                    date, weight, body_fat, protein_intake, carb_intake, fat_intake, notes, photo_path, last_updated
                FROM 
                    weekly_updates
                WHERE 
                    user_id = ?
                ORDER BY 
                    date ASC
            """
            weekly_df = pd.read_sql_query(weekly_query, conn, params=(self.user_id,))
            
            # Close connection
            conn.close()
            
            # Store data
            self.initial_measurements = initial_df
            self.weekly_updates = weekly_df
            
            # Combine data for visualization
            self.prepare_comparison_data()
            
            # Update UI with new data
            self.update_ui()
            
        except Exception as e:
            print(f"Error loading progress data: {e}")
            traceback.print_exc()
    
    def prepare_comparison_data(self):
        """Prepare comparison data between initial and current measurements"""
        if self.initial_measurements is None or self.initial_measurements.empty:
            print("No initial measurements available")
            return
            
        if self.weekly_updates is None or self.weekly_updates.empty:
            print("No weekly updates available")
            return
            
        try:
            # Get initial values
            initial_weight = self.initial_measurements.iloc[0]['weight']
            initial_bf = self.initial_measurements.iloc[0]['body_fat']
            initial_lean_mass = self.initial_measurements.iloc[0]['lean_mass']
            initial_fat_mass = self.initial_measurements.iloc[0]['fat_mass']
            initial_rmr = self.initial_measurements.iloc[0]['rmr']
            initial_tdee = self.initial_measurements.iloc[0]['tdee']
            
            # Get latest values from weekly updates
            latest_weight = self.weekly_updates.iloc[-1]['weight']
            latest_bf = self.weekly_updates.iloc[-1]['body_fat']
            
            # Calculate latest lean mass and fat mass
            latest_fat_mass = latest_weight * (latest_bf / 100.0)
            latest_lean_mass = latest_weight - latest_fat_mass
            
            # Get user profile to calculate RMR/TDEE based on current weight
            conn = sqlite3.connect("history.db")
            cursor = conn.cursor()
            
            # Get user gender, height, age, activity factor
            cursor.execute("""
                SELECT gender, height_feet, height_inches, dob, activity_factor
                FROM user_profiles
                WHERE id = ?
            """, (self.user_id,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                gender, height_feet, height_inches, dob, activity_factor = user_data
                
                # Calculate height in cm
                height_cm = (height_feet * 12 + height_inches) * 2.54
                
                # Calculate age from DOB
                try:
                    if dob:
                        if len(dob) == 6:  # MMDDYY
                            dob_date = datetime.strptime(dob, "%m%d%y")
                        elif '/' in dob:  # MM/DD/YYYY
                            dob_date = datetime.strptime(dob, "%m/%d/%Y")
                        else:
                            dob_date = None
                            
                        if dob_date:
                            current_date = datetime.now()
                            age = current_date.year - dob_date.year - ((current_date.month, current_date.day) < (dob_date.month, dob_date.day))
                        else:
                            age = 30  # Default age
                    else:
                        age = 30  # Default age
                except Exception as e:
                    print(f"Error calculating age: {e}")
                    age = 30  # Default age
                
                # Calculate RMR using Mifflin-St Jeor equation
                weight_kg = latest_weight * 0.453592  # Convert lbs to kg
                
                if gender.lower() == 'm':
                    # Men: RMR = 88.362 + (13.397 × weight in kg) + (4.799 × height in cm) - (5.677 × age in years)
                    latest_rmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
                else:
                    # Women: RMR = 447.593 + (9.247 × weight in kg) + (3.098 × height in cm) - (4.330 × age in years)
                    latest_rmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
                
                # Calculate TDEE
                try:
                    activity_value = float(activity_factor.split(":")[0]) if isinstance(activity_factor, str) else 1.2
                except Exception as e:
                    print(f"Error parsing activity factor: {e}")
                    activity_value = 1.2  # Default sedentary
                    
                latest_tdee = latest_rmr * activity_value
            else:
                # Default values if user data not found
                latest_rmr = initial_rmr
                latest_tdee = initial_tdee
            
            # Create comparison data
            self.comparison_data = {
                "weight": {"initial": initial_weight, "current": latest_weight, "change": latest_weight - initial_weight},
                "body_fat": {"initial": initial_bf, "current": latest_bf, "change": latest_bf - initial_bf},
                "lean_mass": {"initial": initial_lean_mass, "current": latest_lean_mass, "change": latest_lean_mass - initial_lean_mass},
                "fat_mass": {"initial": initial_fat_mass, "current": latest_fat_mass, "change": latest_fat_mass - initial_fat_mass},
                "rmr": {"initial": initial_rmr, "current": latest_rmr, "change": latest_rmr - initial_rmr},
                "tdee": {"initial": initial_tdee, "current": latest_tdee, "change": latest_tdee - initial_tdee}
            }
            
        except Exception as e:
            print(f"Error preparing comparison data: {e}")
            traceback.print_exc()
    
    def update_ui(self):
        """Update UI elements with loaded data"""
        self.update_comparison_metrics()
        self.update_charts()
        self.update_history_table()
    
    def update_comparison_metrics(self):
        """Update comparison metrics display"""
        if self.comparison_data is None:
            return
            
        # Clear existing widgets
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
            
        # Create grid layout for metrics
        self.metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Headers
        headers = ["Metric", "Initial", "Current", "Change"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.metrics_frame,
                text=header,
                font=ctk.CTkFont(weight="bold")
            )
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        # Format metrics
        metrics = [
            ["Weight (lbs)", 
             f"{self.comparison_data['weight']['initial']:.1f}", 
             f"{self.comparison_data['weight']['current']:.1f}", 
             self.format_change(self.comparison_data['weight']['change'], "lbs")],
            ["Body Fat (%)", 
             f"{self.comparison_data['body_fat']['initial']:.1f}", 
             f"{self.comparison_data['body_fat']['current']:.1f}", 
             self.format_change(self.comparison_data['body_fat']['change'], "%", reverse=True)],
            ["Lean Mass (lbs)", 
             f"{self.comparison_data['lean_mass']['initial']:.1f}", 
             f"{self.comparison_data['lean_mass']['current']:.1f}", 
             self.format_change(self.comparison_data['lean_mass']['change'], "lbs")],
            ["Fat Mass (lbs)", 
             f"{self.comparison_data['fat_mass']['initial']:.1f}", 
             f"{self.comparison_data['fat_mass']['current']:.1f}", 
             self.format_change(self.comparison_data['fat_mass']['change'], "lbs", reverse=True)],
            ["RMR (calories)", 
             f"{self.comparison_data['rmr']['initial']:.0f}", 
             f"{self.comparison_data['rmr']['current']:.0f}", 
             self.format_change(self.comparison_data['rmr']['change'], "cal")],
            ["TDEE (calories)", 
             f"{self.comparison_data['tdee']['initial']:.0f}", 
             f"{self.comparison_data['tdee']['current']:.0f}", 
             self.format_change(self.comparison_data['tdee']['change'], "cal")]
        ]
        
        # Display metrics
        for i, metric in enumerate(metrics):
            for j, value in enumerate(metric):
                # Determine text color for the change column
                if j == 3:  # Change column
                    if "+" in value:
                        if "(better)" in value:
                            text_color = "green"
                        else:
                            text_color = "red"
                    elif "-" in value:
                        if "(better)" in value:
                            text_color = "green"
                        else:
                            text_color = "red"
                    else:
                        text_color = None
                else:
                    text_color = None
                    
                label = ctk.CTkLabel(self.metrics_frame, text=value, text_color=text_color)
                label.grid(row=i+1, column=j, padx=5, pady=5, sticky="w")
    
    def format_change(self, change, unit, reverse=False):
        """Format a change value with appropriate sign and indication of improvement/decline"""
        if abs(change) < 0.01:
            return "No change"
            
        if change > 0:
            prefix = "+"
            is_better = not reverse  # For most metrics, increase is better
        else:
            prefix = ""  # Negative sign will be included in the number
            is_better = reverse  # For body fat and fat mass, decrease is better
            
        if is_better:
            suffix = " (better)"
        else:
            suffix = " (worse)"
            
        return f"{prefix}{change:.1f} {unit}{suffix}"
    
    def update_charts(self):
        """Update charts with progress data"""
        if self.weekly_updates is None or self.weekly_updates.empty:
            return
            
        # Clear existing charts
        for widget in self.charts_container.winfo_children():
            widget.destroy()
            
        # Create chart frame
        chart_frame = ctk.CTkFrame(self.charts_container)
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create matplotlib figure
        fig = plt.figure(figsize=(10, 6), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')  # Match CTk dark mode
        
        # Weight chart
        ax1 = fig.add_subplot(221)
        ax1.set_title("Weight Progress", color='white')
        ax1.set_facecolor('#2b2b2b')
        ax1.tick_params(colors='white')
        for spine in ax1.spines.values():
            spine.set_color('white')
            
        # Convert date to datetime
        dates = pd.to_datetime(self.weekly_updates['date'])
        weights = self.weekly_updates['weight']
        
        ax1.plot(dates, weights, 'b-', marker='o')
        ax1.set_ylabel("Weight (lbs)", color='white')
        
        # Body fat chart
        ax2 = fig.add_subplot(222)
        ax2.set_title("Body Fat Progress", color='white')
        ax2.set_facecolor('#2b2b2b')
        ax2.tick_params(colors='white')
        for spine in ax2.spines.values():
            spine.set_color('white')
            
        body_fats = self.weekly_updates['body_fat']
        
        ax2.plot(dates, body_fats, 'r-', marker='o')
        ax2.set_ylabel("Body Fat (%)", color='white')
        
        # Lean mass vs fat mass chart
        ax3 = fig.add_subplot(223)
        ax3.set_title("Lean Mass vs Fat Mass", color='white')
        ax3.set_facecolor('#2b2b2b')
        ax3.tick_params(colors='white')
        for spine in ax3.spines.values():
            spine.set_color('white')
            
        # Calculate lean mass and fat mass
        fat_masses = self.weekly_updates['weight'] * (self.weekly_updates['body_fat'] / 100.0)
        lean_masses = self.weekly_updates['weight'] - fat_masses
        
        ax3.bar(dates, lean_masses, label="Lean Mass", color='blue', alpha=0.7)
        ax3.bar(dates, fat_masses, bottom=lean_masses, label="Fat Mass", color='red', alpha=0.7)
        ax3.legend(facecolor='#2b2b2b', labelcolor='white')
        ax3.set_ylabel("Weight (lbs)", color='white')
        
        # Nutrition chart
        ax4 = fig.add_subplot(224)
        ax4.set_title("Macronutrient Intake", color='white')
        ax4.set_facecolor('#2b2b2b')
        ax4.tick_params(colors='white')
        for spine in ax4.spines.values():
            spine.set_color('white')
            
        # Ensure all macronutrient columns exist
        macro_columns = ['protein_intake', 'carb_intake', 'fat_intake']
        for col in macro_columns:
            if col not in self.weekly_updates.columns:
                self.weekly_updates[col] = 0
                
        proteins = self.weekly_updates['protein_intake']
        carbs = self.weekly_updates['carb_intake']
        fats = self.weekly_updates['fat_intake']
        
        ax4.plot(dates, proteins, 'g-', marker='o', label="Protein")
        ax4.plot(dates, carbs, 'b-', marker='o', label="Carbs")
        ax4.plot(dates, fats, 'r-', marker='o', label="Fats")
        ax4.legend(facecolor='#2b2b2b', labelcolor='white')
        ax4.set_ylabel("Grams", color='white')
        
        # Adjust layout
        plt.tight_layout(pad=2.0)
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def update_history_table(self):
        """Update history table with weekly data"""
        if self.weekly_updates is None or self.weekly_updates.empty:
            return
            
        # Clear existing table
        for widget in self.table_container.winfo_children():
            widget.destroy()
            
        # Create scrollable frame for table
        table_scroll = ctk.CTkScrollableFrame(self.table_container)
        table_scroll.pack(fill="both", expand=True)
        
        # Define columns
        columns = ["Date", "Weight", "Body Fat", "Protein", "Carbs", "Fats", "Notes"]
        
        # Create header row
        for i, col in enumerate(columns):
            label = ctk.CTkLabel(
                table_scroll, 
                text=col,
                font=ctk.CTkFont(weight="bold")
            )
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
            
        # Ensure all expected columns exist
        required_columns = ['date', 'weight', 'body_fat', 'protein_intake', 'carb_intake', 'fat_intake', 'notes']
        for col in required_columns:
            if col not in self.weekly_updates.columns:
                self.weekly_updates[col] = ""
        
        # Add data rows
        for i, row in self.weekly_updates.iterrows():
            # Format date
            try:
                date_obj = pd.to_datetime(row['date'])
                date_str = date_obj.strftime("%m/%d/%Y")
            except:
                date_str = str(row['date'])
                
            # Create row data
            row_data = [
                date_str,
                f"{row['weight']:.1f} lbs",
                f"{row['body_fat']:.1f}%",
                f"{row['protein_intake']:.1f}g",
                f"{row['carb_intake']:.1f}g",
                f"{row['fat_intake']:.1f}g",
                row['notes'][:30] + "..." if len(str(row['notes'])) > 30 else row['notes']
            ]
            
            # Add to table
            for j, value in enumerate(row_data):
                label = ctk.CTkLabel(table_scroll, text=value)
                label.grid(row=i+1, column=j, padx=5, pady=5, sticky="w")
                
    def refresh(self, user_id=None):
        """Refresh the dashboard with updated data"""
        if user_id is not None:
            self.user_id = user_id
            
        if self.user_id is None:
            print("No user ID provided, cannot refresh dashboard")
            return
            
        # Refresh dashboard widgets
        self.dashboard_widgets.refresh(self.user_id)
        
        # Also load data for the main dashboard charts
        self.load_data(self.user_id)
