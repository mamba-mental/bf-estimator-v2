#!/usr/bin/env python
# dashboard_widgets.py - Dashboard Widgets for Body Fat Estimator
# Created: 03/28/25
# Description: Widget components for the progress dashboard

import os
import sys
import sqlite3
import customtkinter as ctk
from datetime import datetime, timedelta
import traceback
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
from weekly_updates_ui import WeeklyUpdatesUI

class DashboardWidgets:
    """Class to provide dashboard widgets for the progress dashboard"""
    
    def __init__(self, parent_frame, app_instance=None):
        """
        Initialize the dashboard widgets
        
        Args:
            parent_frame: The frame where the widgets will be displayed
            app_instance: The parent app instance
        """
        self.parent_frame = parent_frame
        self.app_instance = app_instance
        self.user_id = None
        self.user_data = None
        self.initial_measurements = None
        self.weekly_updates = None
        self.goal_date = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI elements for the dashboard widgets"""
        # Create main container
        self.container = ctk.CTkFrame(self.parent_frame)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create widgets grid (2x2 layout)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)
        
        # 1. Current vs Goal widget (top left)
        self.current_goal_frame = ctk.CTkFrame(self.container)
        self.current_goal_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.current_goal_label = ctk.CTkLabel(
            self.current_goal_frame, 
            text="Current vs Goal", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.current_goal_label.pack(pady=(10, 5))
        
        # Container for metrics
        self.metrics_container = ctk.CTkFrame(self.current_goal_frame)
        self.metrics_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 2. Weekly progress sparklines (top right)
        self.sparklines_frame = ctk.CTkFrame(self.container)
        self.sparklines_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.sparklines_label = ctk.CTkLabel(
            self.sparklines_frame, 
            text="Weekly Progress", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.sparklines_label.pack(pady=(10, 5))
        
        # Container for sparklines
        self.sparklines_container = ctk.CTkFrame(self.sparklines_frame)
        self.sparklines_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 3. Program timeline countdown (bottom left)
        self.timeline_frame = ctk.CTkFrame(self.container)
        self.timeline_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.timeline_label = ctk.CTkLabel(
            self.timeline_frame, 
            text="Program Timeline", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.timeline_label.pack(pady=(10, 5))
        
        # Container for timeline
        self.timeline_container = ctk.CTkFrame(self.timeline_frame)
        self.timeline_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 4. Quick entry buttons (bottom right)
        self.quick_entry_frame = ctk.CTkFrame(self.container)
        self.quick_entry_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        self.quick_entry_label = ctk.CTkLabel(
            self.quick_entry_frame, 
            text="Quick Entry", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.quick_entry_label.pack(pady=(10, 5))
        
        # Container for quick entry buttons
        self.quick_entry_container = ctk.CTkFrame(self.quick_entry_frame)
        self.quick_entry_container.pack(fill="both", expand=True, padx=10, pady=5)
    
    def load_data(self, user_id):
        """
        Load user data for the widgets
        
        Args:
            user_id: The user ID to load data for
        """
        if user_id is None:
            print("No user ID provided, cannot load widget data")
            return
            
        self.user_id = user_id
            
        try:
            # Connect to database
            conn = sqlite3.connect("history.db")
            
            # Load user profile
            profile_query = """
                SELECT 
                    user_name, email, gender, dob, height_feet, height_inches,
                    current_weight, current_bf, goal_weight, goal_bf,
                    rmr, tdee, protein_intake, carb_intake, fat_intake,
                    diet_type, workout_type, workout_days, resistance_training,
                    experience_level, is_athlete, last_updated
                FROM 
                    user_profiles
                WHERE 
                    id = ?
            """
            user_df = pd.read_sql_query(profile_query, conn, params=(user_id,))
            
            # Load initial measurements
            initial_query = """
                SELECT 
                    date, weight, body_fat, lean_mass, fat_mass, rmr, tdee
                FROM 
                    initial_measurements
                WHERE 
                    user_id = ?
                ORDER BY 
                    date DESC
                LIMIT 1
            """
            initial_df = pd.read_sql_query(initial_query, conn, params=(user_id,))
            
            # Load weekly updates
            weekly_query = """
                SELECT 
                    date, weight, body_fat, protein_intake, carb_intake, fat_intake
                FROM 
                    weekly_updates
                WHERE 
                    user_id = ?
                ORDER BY 
                    date ASC
            """
            weekly_df = pd.read_sql_query(weekly_query, conn, params=(user_id,))
            
            # Close connection
            conn.close()
            
            # Store data
            self.user_data = user_df
            self.initial_measurements = initial_df
            self.weekly_updates = weekly_df
            
            # Calculate goal date
            # Try to get the end date from user profile
            if not user_df.empty:
                try:
                    # Look for end_date field
                    end_date = None
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA table_info(user_profiles)")
                    columns = [column[1] for column in cursor.fetchall()]
                    
                    if 'end_date' in columns:
                        cursor.execute("SELECT end_date FROM user_profiles WHERE id = ?", (user_id,))
                        result = cursor.fetchone()
                        if result and result[0]:
                            end_date_str = result[0]
                            
                            # Parse end date
                            if len(end_date_str) == 6:  # MMDDYY
                                self.goal_date = datetime.strptime(end_date_str, "%m%d%y")
                            elif '/' in end_date_str:  # MM/DD/YYYY
                                self.goal_date = datetime.strptime(end_date_str, "%m/%d/%Y")
                        
                except Exception as e:
                    print(f"Error parsing goal date: {e}")
                    traceback.print_exc()
            
            # Update UI with new data
            self.update_widgets()
            
        except Exception as e:
            print(f"Error loading widget data: {e}")
            traceback.print_exc()
    
    def update_widgets(self):
        """Update all dashboard widgets with current data"""
        self.update_current_goal_widget()
        self.update_sparklines_widget()
        self.update_timeline_widget()
        self.update_quick_entry_widget()
    
    def update_current_goal_widget(self):
        """Update the Current vs Goal comparison widget"""
        # Clear existing widgets
        for widget in self.metrics_container.winfo_children():
            widget.destroy()
            
        # Configure grid layout
        self.metrics_container.grid_columnconfigure(0, weight=1)
        self.metrics_container.grid_columnconfigure(1, weight=1)
        self.metrics_container.grid_columnconfigure(2, weight=1)
        
        # Headers
        headers = ["Metric", "Current", "Goal"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.metrics_container,
                text=header,
                font=ctk.CTkFont(weight="bold")
            )
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        # Check if we have user data
        if self.user_data is None or self.user_data.empty:
            # Show placeholder
            placeholder = ctk.CTkLabel(
                self.metrics_container,
                text="No user data available",
                text_color="gray"
            )
            placeholder.grid(row=1, column=0, columnspan=3, padx=5, pady=20)
            return
        
        # Get current values
        try:
            current_weight = self.user_data.iloc[0]['current_weight']
            current_bf = self.user_data.iloc[0]['current_bf']
            goal_weight = self.user_data.iloc[0]['goal_weight']
            goal_bf = self.user_data.iloc[0]['goal_bf']
            
            # If we have latest weekly update, use those values instead
            if self.weekly_updates is not None and not self.weekly_updates.empty:
                latest_update = self.weekly_updates.iloc[-1]
                current_weight = latest_update['weight']
                current_bf = latest_update['body_fat']
                
            # Calculate progress percentages
            weight_progress = 0
            bf_progress = 0
            
            if self.initial_measurements is not None and not self.initial_measurements.empty:
                initial_weight = self.initial_measurements.iloc[0]['weight']
                initial_bf = self.initial_measurements.iloc[0]['body_fat']
                
                if goal_weight != initial_weight:
                    weight_progress = ((initial_weight - current_weight) / 
                                      (initial_weight - goal_weight)) * 100
                    weight_progress = min(max(weight_progress, 0), 100)  # Clamp to 0-100%
                    
                if goal_bf != initial_bf:
                    bf_progress = ((initial_bf - current_bf) / 
                                  (initial_bf - goal_bf)) * 100
                    bf_progress = min(max(bf_progress, 0), 100)  # Clamp to 0-100%
            
            # Create metrics list
            metrics = [
                {
                    "name": "Weight (lbs)", 
                    "current": f"{current_weight:.1f}", 
                    "goal": f"{goal_weight:.1f}",
                    "progress": weight_progress
                },
                {
                    "name": "Body Fat (%)", 
                    "current": f"{current_bf:.1f}", 
                    "goal": f"{goal_bf:.1f}",
                    "progress": bf_progress
                }
            ]
            
            # Add protein, carbs and fats if available
            if 'protein_intake' in self.user_data.columns and 'protein_intake' in self.weekly_updates.columns:
                # Get target protein based on body weight (use 1g/lb as default target)
                target_protein = current_weight
                current_protein = self.weekly_updates.iloc[-1]['protein_intake'] if not self.weekly_updates.empty else 0
                protein_progress = min((current_protein / target_protein) * 100, 100) if target_protein > 0 else 0
                
                metrics.append({
                    "name": "Protein (g)", 
                    "current": f"{current_protein:.1f}", 
                    "goal": f"{target_protein:.1f}",
                    "progress": protein_progress
                })
            
            # Add metrics to grid
            for i, metric in enumerate(metrics):
                # Metric name
                name_label = ctk.CTkLabel(
                    self.metrics_container,
                    text=metric["name"]
                )
                name_label.grid(row=i+1, column=0, padx=5, pady=5, sticky="w")
                
                # Current value with progress bar
                current_frame = ctk.CTkFrame(self.metrics_container)
                current_frame.grid(row=i+1, column=1, padx=5, pady=5, sticky="ew")
                
                current_value = ctk.CTkLabel(
                    current_frame,
                    text=metric["current"]
                )
                current_value.pack(side="left", padx=5)
                
                # Progress bar (if progress is available)
                if "progress" in metric:
                    progress_bar = ctk.CTkProgressBar(current_frame, width=50, height=8)
                    progress_bar.pack(side="right", padx=5)
                    progress_bar.set(metric["progress"] / 100)
                
                # Goal value
                goal_label = ctk.CTkLabel(
                    self.metrics_container,
                    text=metric["goal"]
                )
                goal_label.grid(row=i+1, column=2, padx=5, pady=5, sticky="w")
                
        except Exception as e:
            print(f"Error updating current vs goal widget: {e}")
            traceback.print_exc()
            
            # Show error message
            error_label = ctk.CTkLabel(
                self.metrics_container,
                text=f"Error loading metrics: {str(e)}",
                text_color="red"
            )
            error_label.grid(row=1, column=0, columnspan=3, padx=5, pady=20)
    
    def update_sparklines_widget(self):
        """Update the weekly progress sparklines widget"""
        # Clear existing widgets
        for widget in self.sparklines_container.winfo_children():
            widget.destroy()
            
        # Check if we have weekly updates
        if self.weekly_updates is None or self.weekly_updates.empty:
            # Show placeholder
            placeholder = ctk.CTkLabel(
                self.sparklines_container,
                text="No weekly data available",
                text_color="gray"
            )
            placeholder.pack(padx=5, pady=20)
            return
        
        try:
            # Create matplotlib figure
            fig = plt.figure(figsize=(4, 4), dpi=100)
            fig.patch.set_facecolor('#2b2b2b')  # Match CTk dark mode
            
            # Prepare data
            dates = pd.to_datetime(self.weekly_updates['date'])
            weights = self.weekly_updates['weight']
            body_fats = self.weekly_updates['body_fat']
            
            # Calculate lean mass and fat mass
            fat_masses = weights * (body_fats / 100.0)
            lean_masses = weights - fat_masses
            
            # Ensure macro columns exist
            for col in ['protein_intake', 'carb_intake', 'fat_intake']:
                if col not in self.weekly_updates.columns:
                    self.weekly_updates[col] = 0
            
            # Weight sparkline
            ax1 = fig.add_subplot(221)
            ax1.set_title("Weight (lbs)", color='white', fontsize=8)
            ax1.set_facecolor('#2b2b2b')
            ax1.tick_params(colors='white', labelsize=6)
            for spine in ax1.spines.values():
                spine.set_color('white')
                
            ax1.plot(dates, weights, 'b-', linewidth=1)
            ax1.set_xticklabels([])  # Hide x tick labels for cleaner look
            
            # Body fat sparkline
            ax2 = fig.add_subplot(222)
            ax2.set_title("Body Fat %", color='white', fontsize=8)
            ax2.set_facecolor('#2b2b2b')
            ax2.tick_params(colors='white', labelsize=6)
            for spine in ax2.spines.values():
                spine.set_color('white')
                
            ax2.plot(dates, body_fats, 'r-', linewidth=1)
            ax2.set_xticklabels([])  # Hide x tick labels
            
            # Lean mass sparkline
            ax3 = fig.add_subplot(223)
            ax3.set_title("Lean Mass (lbs)", color='white', fontsize=8)
            ax3.set_facecolor('#2b2b2b')
            ax3.tick_params(colors='white', labelsize=6)
            for spine in ax3.spines.values():
                spine.set_color('white')
                
            ax3.plot(dates, lean_masses, 'g-', linewidth=1)
            ax3.set_xticklabels([])  # Hide x tick labels
            
            # Macros sparkline
            ax4 = fig.add_subplot(224)
            ax4.set_title("Macros (g)", color='white', fontsize=8)
            ax4.set_facecolor('#2b2b2b')
            ax4.tick_params(colors='white', labelsize=6)
            for spine in ax4.spines.values():
                spine.set_color('white')
                
            # Plot available macros
            if 'protein_intake' in self.weekly_updates.columns:
                ax4.plot(dates, self.weekly_updates['protein_intake'], 'g-', linewidth=1, label='Protein')
            if 'carb_intake' in self.weekly_updates.columns:
                ax4.plot(dates, self.weekly_updates['carb_intake'], 'b-', linewidth=1, label='Carbs')
            if 'fat_intake' in self.weekly_updates.columns:
                ax4.plot(dates, self.weekly_updates['fat_intake'], 'r-', linewidth=1, label='Fats')
                
            ax4.set_xticklabels([])  # Hide x tick labels
            
            # Adjust layout
            plt.tight_layout(pad=0.5)
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, master=self.sparklines_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            print(f"Error updating sparklines widget: {e}")
            traceback.print_exc()
            
            # Show error message
            error_label = ctk.CTkLabel(
                self.sparklines_container,
                text=f"Error creating sparklines: {str(e)}",
                text_color="red"
            )
            error_label.pack(padx=5, pady=20)
    
    def update_timeline_widget(self):
        """Update the program timeline countdown widget"""
        # Clear existing widgets
        for widget in self.timeline_container.winfo_children():
            widget.destroy()
            
        # Check if we have a goal date
        if self.goal_date is None:
            # Try to calculate a reasonable goal date from the data
            if self.user_data is not None and not self.user_data.empty:
                try:
                    # If we have initial measurements and a goal weight
                    if (self.initial_measurements is not None and not self.initial_measurements.empty and
                        'goal_weight' in self.user_data.columns):
                        
                        # Assume a reasonable rate of weight loss (1-2 lbs per week)
                        initial_weight = self.initial_measurements.iloc[0]['weight']
                        goal_weight = self.user_data.iloc[0]['goal_weight']
                        weight_to_lose = initial_weight - goal_weight
                        
                        if weight_to_lose > 0:
                            # Calculate weeks needed (at 1.5 lbs per week)
                            weeks_needed = int(weight_to_lose / 1.5)
                            
                            # Get initial date
                            initial_date = pd.to_datetime(self.initial_measurements.iloc[0]['date'])
                            
                            # Calculate projected end date
                            self.goal_date = initial_date + timedelta(weeks=weeks_needed)
                except Exception as e:
                    print(f"Error calculating projected goal date: {e}")
                    self.goal_date = None
                    
        # If still no goal date, show placeholder
        if self.goal_date is None:
            placeholder = ctk.CTkLabel(
                self.timeline_container,
                text="No goal date set",
                text_color="gray"
            )
            placeholder.pack(padx=5, pady=20)
            return
        
        try:
            # Calculate days remaining
            today = datetime.now()
            days_remaining = (self.goal_date - today).days
            
            if days_remaining < 0:
                # Goal date has passed
                status_text = "Goal date has passed"
                progress = 1.0  # Full progress
                days_text = f"0 days remaining (ended {abs(days_remaining)} days ago)"
                color = "orange"
            else:
                # Goal date is in the future
                # Calculate progress (need start date for this)
                progress = 0.0
                
                if self.initial_measurements is not None and not self.initial_measurements.empty:
                    try:
                        start_date = pd.to_datetime(self.initial_measurements.iloc[0]['date'])
                        total_days = (self.goal_date - start_date).days
                        days_elapsed = (today - start_date).days
                        
                        if total_days > 0:
                            progress = days_elapsed / total_days
                            progress = min(max(progress, 0), 1.0)  # Clamp to 0-1
                    except:
                        pass
                
                # Status text based on remaining time
                if days_remaining <= 7:
                    status_text = "Final Week!"
                    color = "orange"
                elif days_remaining <= 14:
                    status_text = "Almost There!"
                    color = "#1f6aa5"  # Blue
                else:
                    status_text = "In Progress"
                    color = "#37a447"  # Green
                    
                # Days remaining text
                weeks_remaining = days_remaining // 7
                remaining_days = days_remaining % 7
                
                if weeks_remaining > 0:
                    days_text = f"{weeks_remaining} weeks, {remaining_days} days remaining"
                else:
                    days_text = f"{days_remaining} days remaining"
            
            # Create status label
            status_label = ctk.CTkLabel(
                self.timeline_container,
                text=status_text,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=color
            )
            status_label.pack(pady=(20, 5))
            
            # Create days remaining label
            days_label = ctk.CTkLabel(
                self.timeline_container,
                text=days_text,
                font=ctk.CTkFont(size=16)
            )
            days_label.pack(pady=5)
            
            # Create goal date label
            date_label = ctk.CTkLabel(
                self.timeline_container,
                text=f"Goal Date: {self.goal_date.strftime('%B %d, %Y')}",
                font=ctk.CTkFont(size=14)
            )
            date_label.pack(pady=5)
            
            # Create progress bar
            progress_frame = ctk.CTkFrame(self.timeline_container)
            progress_frame.pack(fill="x", padx=20, pady=15)
            
            progress_bar = ctk.CTkProgressBar(progress_frame)
            progress_bar.pack(fill="x", padx=10, pady=5)
            progress_bar.set(progress)
            
            # Create percentage label
            percentage = int(progress * 100)
            percentage_label = ctk.CTkLabel(
                progress_frame,
                text=f"{percentage}% Complete",
                font=ctk.CTkFont(size=12)
            )
            percentage_label.pack(pady=5)
            
        except Exception as e:
            print(f"Error updating timeline widget: {e}")
            traceback.print_exc()
            
            # Show error message
            error_label = ctk.CTkLabel(
                self.timeline_container,
                text=f"Error creating timeline: {str(e)}",
                text_color="red"
            )
            error_label.pack(padx=5, pady=20)
    
    def update_quick_entry_widget(self):
        """Update the quick entry buttons widget"""
        # Clear existing widgets
        for widget in self.quick_entry_container.winfo_children():
            widget.destroy()
            
        # Create instruction label
        instruction = ctk.CTkLabel(
            self.quick_entry_container,
            text="Add weekly update with one click:",
            font=ctk.CTkFont(size=12)
        )
        instruction.pack(pady=(10, 15), anchor="w")
        
        # Create buttons frame
        buttons_frame = ctk.CTkFrame(self.quick_entry_container)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        # Create quick entry buttons
        # 1. Log today's weight
        weight_frame = ctk.CTkFrame(buttons_frame)
        weight_frame.pack(fill="x", pady=5)
        
        weight_label = ctk.CTkLabel(weight_frame, text="Weight:", width=60)
        weight_label.pack(side="left", padx=5)
        
        weight_var = ctk.DoubleVar(value=0.0)
        weight_entry = ctk.CTkEntry(weight_frame, textvariable=weight_var, width=80)
        weight_entry.pack(side="left", padx=5)
        
        lbs_label = ctk.CTkLabel(weight_frame, text="lbs", width=30)
        lbs_label.pack(side="left")
        
        weight_button = ctk.CTkButton(
            weight_frame, 
            text="Log Weight", 
            command=lambda: self.quick_log_weight(weight_var.get()),
            width=100
        )
        weight_button.pack(side="right", padx=10)
        
        # 2. Log body fat
        bf_frame = ctk.CTkFrame(buttons_frame)
        bf_frame.pack(fill="x", pady=5)
        
        bf_label = ctk.CTkLabel(bf_frame, text="Body Fat:", width=60)
        bf_label.pack(side="left", padx=5)
        
        bf_var = ctk.DoubleVar(value=0.0)
        bf_entry = ctk.CTkEntry(bf_frame, textvariable=bf_var, width=80)
        bf_entry.pack(side="left", padx=5)
        
        pct_label = ctk.CTkLabel(bf_frame, text="%", width=30)
        pct_label.pack(side="left")
        
        bf_button = ctk.CTkButton(
            bf_frame, 
            text="Log Body Fat", 
            command=lambda: self.quick_log_body_fat(bf_var.get()),
            width=100
        )
        bf_button.pack(side="right", padx=10)
        
        # 3. Log full update button
        full_update_button = ctk.CTkButton(
            buttons_frame,
            text="Log Full Weekly Update",
            command=self.open_weekly_update_form,
            height=35
        )
        full_update_button.pack(fill="x", pady=15)
        
        # If we have current values, set them as defaults
        if self.weekly_updates is not None and not self.weekly_updates.empty:
            latest = self.weekly_updates.iloc[-1]
            weight_var.set(latest['weight'])
            bf_var.set(latest['body_fat'])
    
    def quick_log_weight(self, weight):
        """Log a weight update quickly"""
        if weight <= 0:
            print("Invalid weight value")
            return
            
        if self.user_id is None:
            print("No user ID available")
            return
            
        try:
            # Connect to database
            conn = sqlite3.connect("history.db")
            cursor = conn.cursor()
            
            # Get current date/time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get latest body fat value (if available)
            body_fat = 0.0
            if self.weekly_updates is not None and not self.weekly_updates.empty:
                body_fat = self.weekly_updates.iloc[-1]['body_fat']
            
            # Insert new entry
            cursor.execute("""
                INSERT INTO weekly_updates (
                user_id, date, weight, body_fat, protein_intake, carb_intake, fat_intake, notes, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.user_id,
                current_time,
                weight,
                body_fat,
                0.0,  # protein
                0.0,  # carbs
                0.0,  # fats
                "Quick weight entry",
                current_time
            ))
            
            conn.commit()
            conn.close()
            
            # Reload data to update widgets
            self.load_data(self.user_id)
            
            print(f"Weight of {weight} lbs logged successfully")
            
        except Exception as e:
            print(f"Error logging weight: {e}")
            traceback.print_exc()
    
    def quick_log_body_fat(self, body_fat):
        """Log a body fat update quickly"""
        if body_fat <= 0 or body_fat >= 100:
            print("Invalid body fat value")
            return
            
        if self.user_id is None:
            print("No user ID available")
            return
            
        try:
            # Connect to database
            conn = sqlite3.connect("history.db")
            cursor = conn.cursor()
            
            # Get current date/time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get latest weight value (if available)
            weight = 0.0
            if self.weekly_updates is not None and not self.weekly_updates.empty:
                weight = self.weekly_updates.iloc[-1]['weight']
            
            # Insert new entry
            cursor.execute("""
                INSERT INTO weekly_updates (
                user_id, date, weight, body_fat, protein_intake, carb_intake, fat_intake, notes, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.user_id,
                current_time,
                weight,
                body_fat,
                0.0,  # protein
                0.0,  # carbs
                0.0,  # fats
                "Quick body fat entry",
                current_time
            ))
            
            conn.commit()
            conn.close()
            
            # Reload data to update widgets
            self.load_data(self.user_id)
            
            print(f"Body fat of {body_fat}% logged successfully")
            
        except Exception as e:
            print(f"Error logging body fat: {e}")
            traceback.print_exc()
    
    def open_weekly_update_form(self):
        """Open the weekly updates form for a full update"""
        if self.app_instance is None:
            print("No app instance available, cannot open weekly update form")
            return
            
        try:
            # Create a popup window for the update form
            popup = ctk.CTkToplevel()
            popup.title("Weekly Update")
            popup.geometry("600x500")
            popup.grab_set()  # Make window modal
            
            # Create a frame for the form
            form_frame = ctk.CTkScrollableFrame(popup)
            form_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create variables dict for the form
            variables = {}
            
            # Initialize the weekly updates UI handler
            weekly_updates = WeeklyUpdatesUI(self.app_instance, form_frame, variables)
            
            # Set up the weekly updates form
            weekly_updates.setup_weekly_updates_form()
            
            # Set default values if available
            if self.weekly_updates is not None and not self.weekly_updates.empty:
                latest = self.weekly_updates.iloc[-1]
                if 'current_weight' in variables:
                    variables['current_weight'].set(latest['weight'])
                if 'current_bf' in variables:
                    variables['current_bf'].set(latest['body_fat'])
                if 'protein_intake' in variables and 'protein_intake' in latest:
                    variables['protein_intake'].set(latest['protein_intake'])
                if 'carb_intake' in variables and 'carb_intake' in latest:
                    variables['carb_intake'].set(latest['carb_intake'])
                if 'fat_intake' in variables and 'fat_intake' in latest:
                    variables['fat_intake'].set(latest['fat_intake'])
                    
            # Set current date
            if 'update_date' in variables:
                variables['update_date'].set(datetime.now().strftime("%m/%d/%Y"))
            
            # Create button frame
            button_frame = ctk.CTkFrame(popup)
            button_frame.pack(fill="x", padx=10, pady=10)
            
            # Add save button
            def save_weekly_update():
                weekly_updates.save_weekly_updates(self.user_id)
                self.load_data(self.user_id)  # Refresh widgets
                popup.destroy()
                
            save_button = ctk.CTkButton(
                button_frame,
                text="Save Weekly Update",
                command=save_weekly_update,
                width=200,
                height=40
            )
            save_button.pack(side="right", padx=10, pady=10)
            
            # Add cancel button
            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel",
                command=popup.destroy,
                width=100,
                height=40
            )
            cancel_button.pack(side="left", padx=10, pady=10)
            
        except Exception as e:
            print(f"Error opening weekly update form: {e}")
            traceback.print_exc()
    
    def refresh(self, user_id=None):
        """Refresh all widgets with latest data"""
        self.load_data(user_id or self.user_id)
