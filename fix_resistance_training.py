#!/usr/bin/env python
"""
fix_resistance_training.py - Add resistance training question to settings
"""

import re
import shutil

def add_resistance_training_question():
    """
    Add resistance training question to the settings section
    """
    file_path = 'enhanced_desktop_app.py'
    backup_path = f'{file_path}.resistance.bak'

    # Create backup first
    print(f"Creating backup of {file_path} as {backup_path}")
    shutil.copy2(file_path, backup_path)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the activity level section
        activity_level_section = """        # Activity Level
        ctk.CTkLabel(activity_frame, text="Activity Level:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.settings_activity_level_var = ctk.StringVar()
        activity_options = [f"{i}: {desc}" for i, desc in {1: "Sedentary", 2: "Light", 3: "Moderate", 4: "Active", 5: "Very Active"}.items()]
        self.settings_activity_level_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_activity_level_var, values=activity_options)
        self.settings_activity_level_options.grid(row=1, column=1, padx=10, pady=5, sticky="ew")"""

        # Add resistance training question right after activity level
        resistance_training_section = """        # Activity Level
        ctk.CTkLabel(activity_frame, text="Activity Level:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.settings_activity_level_var = ctk.StringVar()
        activity_options = [f"{i}: {desc}" for i, desc in {1: "Sedentary", 2: "Light", 3: "Moderate", 4: "Active", 5: "Very Active"}.items()]
        self.settings_activity_level_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_activity_level_var, values=activity_options)
        self.settings_activity_level_options.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Resistance Training
        ctk.CTkLabel(activity_frame, text="Resistance Training:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.settings_resistance_training_var = ctk.StringVar()
        self.settings_resistance_training_options = ctk.CTkOptionMenu(activity_frame, variable=self.settings_resistance_training_var, values=["Yes", "No"])
        self.settings_resistance_training_options.grid(row=2, column=1, padx=10, pady=5, sticky="ew")"""

        # Replace activity level section with activity level + resistance training
        content = content.replace(activity_level_section, resistance_training_section)

        # Adjust the row numbers for subsequent fields
        content = re.sub(r'row=2, column=0', 'row=3, column=0', content)
        content = re.sub(r'row=2, column=1', 'row=3, column=1', content)
        content = re.sub(r'row=3, column=0', 'row=4, column=0', content)
        content = re.sub(r'row=3, column=1', 'row=4, column=1', content)
        content = re.sub(r'row=4, column=0', 'row=5, column=0', content)
        content = re.sub(r'row=4, column=1', 'row=5, column=1', content)
        content = re.sub(r'row=5, column=0', 'row=6, column=0', content)
        content = re.sub(r'row=5, column=1', 'row=6, column=1', content)

        # Add resistance training field to load_settings method
        load_settings_pattern = """        # Populate Activity & Experience fields
        activity_level_db = user_data.get('activity_level', 1) # Get numeric value
        if hasattr(self, 'settings_activity_level_options'):
            activity_options = self.settings_activity_level_options.cget("values")
            matching_activity = next((opt for opt in activity_options if opt.startswith(str(activity_level_db))), activity_options[0])
            self.settings_activity_level_var.set(matching_activity)"""

        load_settings_replacement = """        # Populate Activity & Experience fields
        activity_level_db = user_data.get('activity_level', 1) # Get numeric value
        if hasattr(self, 'settings_activity_level_options'):
            activity_options = self.settings_activity_level_options.cget("values")
            matching_activity = next((opt for opt in activity_options if opt.startswith(str(activity_level_db))), activity_options[0])
            self.settings_activity_level_var.set(matching_activity)

        # Load resistance training
        if hasattr(self, 'settings_resistance_training_var'):
            self.settings_resistance_training_var.set("Yes" if user_data.get('resistance_training', False) else "No")"""

        content = content.replace(load_settings_pattern, load_settings_replacement)

        # Add resistance training field to save_settings method
        save_settings_pattern = """            # Read values from fields
            name = self.settings_name_entry.get()
            email = self.settings_email_entry.get() if hasattr(self, 'settings_email_entry') else ''
            age_str = self.settings_age_entry.get()
            gender = self.settings_gender_var.get()
            height_ft_str = self.settings_height_ft_entry.get()
            height_in_str = self.settings_height_in_entry.get()
            dob = self.settings_dob_entry.get() if hasattr(self, 'settings_dob_entry') else None

            activity_level_str = self.settings_activity_level_var.get() if hasattr(self, 'settings_activity_level_var') else ''
            experience_level_str = self.settings_experience_level_var.get() if hasattr(self, 'settings_experience_level_var') else ''
            workout_type_str = self.settings_workout_type_var.get() if hasattr(self, 'settings_workout_type_var') else ''
            workout_days_str = self.settings_workout_days_entry.get() if hasattr(self, 'settings_workout_days_entry') else ''
            athlete_status_str = self.settings_athlete_status_var.get() if hasattr(self, 'settings_athlete_status_var') else 'No'
            job_activity_str = self.settings_job_activity_var.get() if hasattr(self, 'settings_job_activity_var') else ''
            leisure_activity_str = self.settings_leisure_activity_var.get() if hasattr(self, 'settings_leisure_activity_var') else ''
            protein_intake_str = self.settings_protein_intake_entry.get() if hasattr(self, 'settings_protein_intake_entry') else ''

            goal_weight_str = self.settings_goal_weight_entry.get()
            goal_bf_str = self.settings_goal_bf_entry.get()
            goal_timeframe = self.settings_goal_timeframe_var.get() if hasattr(self, 'settings_goal_timeframe_var') else None # Added
            selected_theme = self.settings_theme_var.get()"""

        save_settings_replacement = """            # Read values from fields
            name = self.settings_name_entry.get()
            email = self.settings_email_entry.get() if hasattr(self, 'settings_email_entry') else ''
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
            selected_theme = self.settings_theme_var.get()"""

        content = content.replace(save_settings_pattern, save_settings_replacement)

        # Add resistance training to the settings dictionary
        settings_dict_pattern = """            settings_to_update = {
                'name': name,
                'email': email,
                'age': age,
                'gender': gender,
                'height': total_height_inches,
                'dob': dob,
                'activity_level': activity_level,
                'experience_level': experience_level,
                'workout_type': workout_type,
                'workout_days': workout_days,
                'is_athlete': is_athlete,
                'job_activity': job_activity,
                'leisure_activity': leisure_activity,
                'protein_intake': protein_intake,
                'goal_weight': goal_weight,
                'goal_bf': goal_bf,
                'goal_timeframe': goal_timeframe if goal_timeframe != "Not Set" else None, # Save None if "Not Set"
                'preferred_theme': selected_theme
            }"""

        settings_dict_replacement = """            settings_to_update = {
                'name': name,
                'email': email,
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
            }"""

        content = content.replace(settings_dict_pattern, settings_dict_replacement)

        # Save the changes
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("Successfully added resistance training question!")
        print(f"If the changes didn't work correctly, you can restore from the backup: {backup_path}")
        return True

    except Exception as e:
        print(f"Error updating file: {str(e)}")
        print(f"You can restore from the backup: {backup_path}")
        return False

if __name__ == "__main__":
    add_resistance_training_question()
