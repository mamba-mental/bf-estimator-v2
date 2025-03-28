#!/usr/bin/env python
# integrated_profile_app.py - Integration of Enhanced User Profile for Body Fat Estimator
# Created: 03/28/25
# Description: Integrates enhanced user profile fields into the main Body Fat Estimator app

import os
import sys
import sqlite3
from datetime import datetime
import customtkinter as ctk
import traceback

# Import existing functionality
from desktop_app import BodyFatEstimatorApp, SimpleMessageBox
from enhanced_profile_ui import EnhancedProfileUI
from weekly_updates_ui import WeeklyUpdatesUI
from progress_dashboard import ProgressDashboard
from settings_tab import SettingsTab
from update_database_enhanced_profile import update_database_schema

class IntegratedProfileApp(BodyFatEstimatorApp):
    """Extended Body Fat Estimator app with enhanced profile capabilities"""

    def __init__(self):
        # Initialize the parent class
        super().__init__()

        # Make sure database schema is updated
        update_database_schema()

        # Initialize the enhanced profile UI handler
        self.enhanced_profile = EnhancedProfileUI(self, self.input_frame, self.variables)

        # Initialize the weekly updates UI handler
        self.weekly_updates = WeeklyUpdatesUI(self, self.input_frame, self.variables)

        # Add Progress Dashboard tab
        self.setup_progress_dashboard()

        # Modify the existing setup_input_form method to add our additional fields
        self.setup_enhanced_input_form()

        # Add RMR calculation after form submission
        self.original_generate_report = self.generate_report
        self.generate_report = self.enhanced_generate_report
        
    def setup_progress_dashboard(self):
        """Set up the progress dashboard and settings tabs"""
        # Add Progress Dashboard tab
        self.progress_tab = self.tabview.add("Progress Dashboard")
        self.progress_dashboard = ProgressDashboard(self.progress_tab, app_instance=self)
        
        # Initialize Settings tab with app reference
        self.settings_tab = self.tabview.add("Settings")
        self.settings_interface = SettingsTab(self.settings_tab, self)

    def setup_enhanced_input_form(self):
        """Set up enhanced input form fields"""
        # Get the current maximum row in the input form
        max_row = 26
        for child in self.input_frame.winfo_children():
            try:
                grid_info = child.grid_info()
                if 'row' in grid_info:
                    max_row = max(max_row, grid_info['row'])
            except:
                continue

        # Set up the enhanced profile fields starting after the existing fields
        self.enhanced_profile.setup_all_enhanced_fields(max_row + 1)

        # Set up the weekly updates form
        self.weekly_updates.setup_weekly_updates_form(max_row + 20)

    def enhanced_generate_report(self):
        """Enhanced version of generate_report that includes RMR calculation"""
        try:
            # Get form data
            initial_data = self.get_form_data()
            if not initial_data:
                return  # Stop if validation failed

            # Add RMR and TDEE calculations to the data
            rmr, tdee = self.enhanced_profile.get_rmr_and_tdee(initial_data)

            # Only add if the values are valid
            if rmr > 0 and tdee > 0:
                initial_data['rmr'] = rmr
                initial_data['tdee'] = tdee

                # Build weekly progression data
                # Add calculated values to each week if present
                conn = sqlite3.connect("history.db")
                cursor = conn.cursor()
                cursor.execute("SELECT date, weight, bodyfat FROM weekly_progress ORDER BY date ASC")
                progression_rows = cursor.fetchall()
                conn.close()

                progression_data = []

                # If we have progress data
                if progression_rows:
                    # Convert to expected format
                    for date_str, weight, bf in progression_rows:
                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                            entry = {
                                "date": date_obj.strftime("%m/%d/%Y"),
                                "weight": weight,
                                "body_fat_percentage": bf
                            }

                            # Calculate RMR and TDEE based on this week's weight
                            if weight > 0:
                                # Get basic info from initial_data
                                height_feet = initial_data.get('height_feet', 0)
                                height_inches = initial_data.get('height_inches', 0)
                                height_cm = (height_feet * 12 + height_inches) * 2.54

                                gender = initial_data.get('gender', 'm')

                                # Calculate age from DOB
                                dob = initial_data.get('dob', '')
                                age = 30  # Default

                                if dob:
                                    try:
                                        if len(dob) == 6:  # MMDDYY
                                            dob_date = datetime.strptime(dob, "%m%d%y")
                                        elif '/' in dob:  # MM/DD/YYYY
                                            dob_date = datetime.strptime(dob, "%m/%d/%Y")
                                        else:
                                            dob_date = None

                                        if dob_date:
                                            # Calculate age as of this entry's date
                                            age = date_obj.year - dob_date.year - ((date_obj.month, date_obj.day) < (dob_date.month, dob_date.day))
                                    except:
                                        pass

                                # Convert weight to kg
                                weight_kg = weight * 0.453592

                                # Calculate RMR
                                weekly_rmr = self.enhanced_profile.calculate_rmr(weight_kg, height_cm, age, gender)

                                # Get activity factor
                                activity_factor_str = initial_data.get('activity_factor', '')
                                activity_factor = 1.2  # Default: sedentary

                                if activity_factor_str:
                                    try:
                                        activity_factor = float(activity_factor_str.split(":")[0])
                                    except:
                                        pass

                                # Calculate TDEE
                                weekly_tdee = weekly_rmr * activity_factor

                                # Add to entry
                                entry['rmr'] = weekly_rmr
                                entry['tdee'] = weekly_tdee

                            progression_data.append(entry)
                        except Exception as e:
                            print(f"Error processing weekly data: {e}")
                            continue

                # If no weekly data or as a fallback, add current data
                if not progression_data:
                    current_date_str = initial_data.get('start_date', datetime.now().strftime("%m/%d/%Y"))
                    current_entry = {
                        "date": current_date_str,
                        "weight": initial_data.get('current_weight', 0),
                        "body_fat_percentage": initial_data.get('current_bf', 0),
                        "rmr": rmr,
                        "tdee": tdee
                    }
                    progression_data.append(current_entry)

            # Call the original generate_report with our enhanced data
            self.original_generate_report()

            # Save profile data to user_profiles table
            user_id = self.save_user_profile(initial_data)

            # Save initial measurements
            self.save_initial_measurements(initial_data)

            # Save weekly updates
            self.weekly_updates.save_weekly_updates(user_id)
            
            # Refresh progress dashboard with the updated data
            if hasattr(self, 'progress_dashboard'):
                self.progress_dashboard.refresh(user_id)
                
            # Display a success message
            SimpleMessageBox.show_info("Success", "Data saved successfully!\nProgress dashboard has been updated.")

        except Exception as e:
            SimpleMessageBox.show_info("Error", f"Error in enhanced report generation: {str(e)}")
            traceback.print_exc()

    def save_user_profile(self, profile_data):
        """Save user profile data to database"""
        try:
            # Connect to database
            conn = sqlite3.connect("history.db")
            cursor = conn.cursor()

            # Get user name
            user_name = profile_data.get('name', 'User')

            # Check if user exists
            cursor.execute("SELECT id FROM user_profiles WHERE user_name = ?", (user_name,))
            user_id = cursor.fetchone()

            # Extract enhanced profile fields
            enhanced_data = self.enhanced_profile.get_enhanced_profile_data()

            # Combine with profile_data
            combined_data = {**profile_data, **enhanced_data}

            # Set current time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if user_id:
                # Update existing user
                user_id = user_id[0]  # Extract id from tuple
                cursor.execute("""
                    UPDATE user_profiles SET
                    email = ?, phone = ?, gender = ?, dob = ?,
                    height_feet = ?, height_inches = ?, initial_weight = ?,
                    initial_bf = ?, current_weight = ?, current_bf = ?,
                    goal_weight = ?, goal_bf = ?, activity_factor = ?,
                    rmr = ?, tdee = ?, protein_intake = ?, carb_intake = ?,
                    fat_intake = ?, diet_type = ?, workout_type = ?,
                    workout_days = ?, resistance_training = ?, experience_level = ?,
                    is_athlete = ?, last_updated = ?
                    WHERE id = ?
                """, (
                    combined_data.get('email', ''),
                    combined_data.get('phone', ''),
                    combined_data.get('gender', ''),
                    combined_data.get('dob', ''),
                    combined_data.get('height_feet', 0),
                    combined_data.get('height_inches', 0),
                    combined_data.get('initial_weight', 0.0),
                    combined_data.get('initial_bf', 0.0),
                    combined_data.get('current_weight', 0.0),
                    combined_data.get('current_bf', 0.0),
                    combined_data.get('goal_weight', 0.0),
                    combined_data.get('goal_bf', 0.0),
                    combined_data.get('activity_factor', ''),
                    combined_data.get('rmr', 0.0),
                    combined_data.get('tdee', 0.0),
                    combined_data.get('protein_intake', 0.0),
                    combined_data.get('carb_intake', 0.0),
                    combined_data.get('fat_intake', 0.0),
                    combined_data.get('diet_type', ''),
                    combined_data.get('workout_type', ''),
                    combined_data.get('workout_days', 0),
                    combined_data.get('resistance_training', ''),
                    combined_data.get('experience_level', ''),
                    combined_data.get('is_athlete', ''),
                    current_time,
                    user_id
                ))
                print(f"Updated user profile for {user_name}")
            else:
                # Insert new user
                cursor.execute("""
                    INSERT INTO user_profiles (
                    user_name, email, phone, gender, dob,
                    height_feet, height_inches, initial_weight,
                    initial_bf, current_weight, current_bf,
                    goal_weight, goal_bf, activity_factor,
                    rmr, tdee, protein_intake, carb_intake,
                    fat_intake, diet_type, workout_type,
                    workout_days, resistance_training, experience_level,
                    is_athlete, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_name,
                    combined_data.get('email', ''),
                    combined_data.get('phone', ''),
                    combined_data.get('gender', ''),
                    combined_data.get('dob', ''),
                    combined_data.get('height_feet', 0),
                    combined_data.get('height_inches', 0),
                    combined_data.get('initial_weight', 0.0),
                    combined_data.get('initial_bf', 0.0),
                    combined_data.get('current_weight', 0.0),
                    combined_data.get('current_bf', 0.0),
                    combined_data.get('goal_weight', 0.0),
                    combined_data.get('goal_bf', 0.0),
                    combined_data.get('activity_factor', ''),
                    combined_data.get('rmr', 0.0),
                    combined_data.get('tdee', 0.0),
                    combined_data.get('protein_intake', 0.0),
                    combined_data.get('carb_intake', 0.0),
                    combined_data.get('fat_intake', 0.0),
                    combined_data.get('diet_type', ''),
                    combined_data.get('workout_type', ''),
                    combined_data.get('workout_days', 0),
                    combined_data.get('resistance_training', ''),
                    combined_data.get('experience_level', ''),
                    combined_data.get('is_athlete', ''),
                    current_time
                ))
                user_id = cursor.lastrowid
                print(f"Created new user profile for {user_name}")

            conn.commit()
            conn.close()
            return user_id

        except Exception as e:
            print(f"Error saving user profile: {e}")
            traceback.print_exc()
            return None

    def save_initial_measurements(self, profile_data):
        """Save initial measurements to database"""
        try:
            # Only save if we have initial weight or body fat
            initial_weight = profile_data.get('initial_weight')
            initial_bf = profile_data.get('initial_bf')

            if not (initial_weight or initial_bf):
                return  # No initial data to save

            # Connect to database
            conn = sqlite3.connect("history.db")
            cursor = conn.cursor()

            # Get user ID
            user_name = profile_data.get('name', 'User')
            cursor.execute("SELECT id FROM user_profiles WHERE user_name = ?", (user_name,))
            user_id_result = cursor.fetchone()

            if not user_id_result:
                print(f"Warning: No user profile found for {user_name}, can't save initial measurements")
                conn.close()
                return

            user_id = user_id_result[0]

            # Get formatted start date
            start_date = profile_data.get('start_date', '')
            if start_date:
                try:
                    if len(start_date) == 6:  # MMDDYY
                        date_obj = datetime.strptime(start_date, "%m%d%y")
                    elif '/' in start_date:  # MM/DD/YYYY
                        date_obj = datetime.strptime(start_date, "%m/%d/%Y")
                    else:
                        date_obj = datetime.now()

                    formatted_date = date_obj.strftime("%Y-%m-%d")
                except:
                    formatted_date = datetime.now().strftime("%Y-%m-%d")
            else:
                formatted_date = datetime.now().strftime("%Y-%m-%d")

            # Calculate lean mass and fat mass if we have both weight and BF
            lean_mass = None
            fat_mass = None

            if initial_weight and initial_bf:
                fat_mass = initial_weight * (initial_bf / 100.0)
                lean_mass = initial_weight - fat_mass

            # Check if entry already exists for this user on this date
            cursor.execute(
                "SELECT id FROM initial_measurements WHERE user_id = ? AND date = ?",
                (user_id, formatted_date)
            )
            existing_entry = cursor.fetchone()

            if existing_entry:
                # Update existing entry
                cursor.execute("""
                    UPDATE initial_measurements SET
                    weight = ?, body_fat = ?, lean_mass = ?, fat_mass = ?,
                    rmr = ?, tdee = ?, notes = ?
                    WHERE id = ?
                """, (
                    initial_weight or 0.0,
                    initial_bf or 0.0,
                    lean_mass or 0.0,
                    fat_mass or 0.0,
                    profile_data.get('rmr', 0.0),
                    profile_data.get('tdee', 0.0),
                    f"Updated initial measurements on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    existing_entry[0]
                ))
                print(f"Updated initial measurements for {user_name}")
            else:
                # Insert new entry
                cursor.execute("""
                    INSERT INTO initial_measurements (
                    user_id, date, weight, body_fat, lean_mass, fat_mass,
                    rmr, tdee, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    formatted_date,
                    initial_weight or 0.0,
                    initial_bf or 0.0,
                    lean_mass or 0.0,
                    fat_mass or 0.0,
                    profile_data.get('rmr', 0.0),
                    profile_data.get('tdee', 0.0),
                    f"Initial measurements recorded on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                ))
                print(f"Added initial measurements for {user_name}")

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error saving initial measurements: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    try:
        app = IntegratedProfileApp()
        app.run()
    except Exception as e:
        print("Unhandled exception in main execution:")
        traceback.print_exc()
        # Keep console open on Windows if run directly
        if sys.platform == 'win32':
            input("Press Enter to exit...")
