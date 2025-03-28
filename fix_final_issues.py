#!/usr/bin/env python
"""
fix_final_issues.py - Final fixes for Body Fat Estimator app
- Fixes report RMR calculation (total_height_inches issue)
- Ensures email field displays properly
- Adds missing input fields
- Fixes theme switching
- Ensures widget refreshing works
"""

import re
import shutil
import os
import json

def fix_rmr_calculation_final():
    """Fix the total_height_inches reference in the RMR calculation"""
    file_path = 'enhanced_desktop_app.py'
    backup_path = f'{file_path}.final.bak'
    
    # Create backup first
    print(f"Creating backup of {file_path} as {backup_path}")
    shutil.copy2(file_path, backup_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the total_height_inches reference
        rmr_pattern = r"""         # Calculate and add RMR
         try:
             # Get age from data, defaulting to 30 if not available
             age_for_rmr = data\.get\('age', 30\)  # Use age from data or default to 30
             height_cm_for_rmr = total_height_inches \* 2\.54
             weight_kg_for_rmr = data\['current_weight'\] / 2\.20462 # Convert lbs to kg
             is_athlete_for_rmr = data\.get\('is_athlete', False\)
             
             data\['rmr'\] = calculate_rmr\(weight_kg_for_rmr, age_for_rmr, data\['gender'\], height_cm_for_rmr, is_athlete_for_rmr\)"""
        
        rmr_replacement = """         # Calculate and add RMR
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
             
             data['rmr'] = calculate_rmr(weight_kg_for_rmr, age_for_rmr, data['gender'], height_cm_for_rmr, is_athlete_for_rmr)"""
        
        # Replace the RMR calculation
        content = re.sub(rmr_pattern, rmr_replacement, content)
        
        # Fix the email field display
        # The regex might not have matched properly, so let's try a different approach
        name_field_section = """        # Name
        ctk.CTkLabel(profile_frame, text="Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.settings_name_entry = ctk.CTkEntry(profile_frame)
        self.settings_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")"""
        
        email_field_section = """        # Name
        ctk.CTkLabel(profile_frame, text="Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.settings_name_entry = ctk.CTkEntry(profile_frame)
        self.settings_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Email
        ctk.CTkLabel(profile_frame, text="Email:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.settings_email_entry = ctk.CTkEntry(profile_frame)
        self.settings_email_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")"""
        
        # Replace name field with name+email fields
        content = content.replace(name_field_section, email_field_section)
        
        # Fix setup_dashboard_tab to ensure widget refreshing works
        refresh_pattern = """    def refresh_dashboard_widgets(self):
        \"\"\"Refresh data in all dashboard widgets.\"\"\"
        if hasattr(self, 'dashboard_widgets'):
             for widget in self.dashboard_widgets.values():
                 if hasattr(widget, 'refresh_data'):
                     widget.refresh_data()"""
        
        refresh_replacement = """    def refresh_dashboard_widgets(self):
        \"\"\"Refresh data in all dashboard widgets.\"\"\"
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
             self.update_idletasks()"""
        
        # Replace refresh method
        content = content.replace(refresh_pattern, refresh_replacement)
        
        # Fix theme application
        apply_theme_pattern = """    def apply_selected_theme(self, theme_name):
         \"\"\"Applies the selected theme and saves it.\"\"\"
         try:
             self.theme_manager.apply_theme(theme_name)
             # Save the theme preference persistently for the current user
             user_id_to_save = self.current_user_id
             if user_id_to_save:
                 # Use the existing set_preferred_theme method
                 if self.auth.current_user and self.auth.current_user.get('user_id') == user_id_to_save:
                     self.auth.is_authenticated = True # Ensure logged-in state for method
                     self.auth.set_preferred_theme(theme_name) 
                 else:
                      print("[WARNING] Auth context mismatch when setting theme.")"""
        
        apply_theme_replacement = """    def apply_selected_theme(self, theme_name):
         \"\"\"Applies the selected theme and saves it.\"\"\"
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
                     widget.update()"""
        
        # Replace apply theme method
        content = content.replace(apply_theme_pattern, apply_theme_replacement)
        
        # Save the changes
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Successfully fixed RMR calculation, email field, and widget refreshing!")
        
        # Fix theme manager
        fix_theme_manager_final()
        
        return True
    
    except Exception as e:
        print(f"Error updating file: {str(e)}")
        print(f"You can restore from the backup: {backup_path}")
        return False

def fix_theme_manager_final():
    """Fix theme application in the theme_manager.py file"""
    
    file_path = 'theme_manager.py'
    backup_path = f'{file_path}.final.bak'
    
    # Create backup first
    print(f"Creating backup of {file_path} as {backup_path}")
    shutil.copy2(file_path, backup_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the apply_theme method
        apply_theme_pattern = r"""    def apply_theme\(self, theme_name\):
        \"\"\"Apply a theme to the application.\"\"\"
        theme_path = self._get_theme_path\(theme_name\)
        if not theme_path:
            print\(f"Theme '{theme_name}' not found."\)
            return False

        # Load theme data
        try:
            with open\(theme_path, 'r'\) as file:
                theme_data = json\.load\(file\)
        except Exception as e:
            print\(f"Error loading theme file: {e}"\)
            return False"""
        
        apply_theme_replacement = """    def apply_theme(self, theme_name):
        \"\"\"Apply a theme to the application.\"\"\"
        print(f"Applying theme: {theme_name}")
        theme_path = self._get_theme_path(theme_name)
        if not theme_path:
            print(f"Theme '{theme_name}' not found.")
            return False

        # Load theme data
        try:
            with open(theme_path, 'r') as file:
                theme_data = json.load(file)
                print(f"Loaded theme data: {theme_name}")
                # Print some theme properties for debugging
                print(f"Theme properties: {', '.join(list(theme_data.keys())[:5])}")
        except Exception as e:
            print(f"Error loading theme file: {e}")
            return False"""
        
        # Replace the apply_theme method introduction
        content = content.replace(apply_theme_pattern, apply_theme_replacement)
        
        # Fix the get_all_widgets method for more thorough widget collection
        get_widgets_pattern = r"""    def get_all_widgets\(self, parent\):
        \"\"\"Recursively get all widgets in the application.\"\"\"
        widgets = \[\]
        for child in parent.winfo_children\(\):
            widgets.append\(child\)
            widgets.extend\(self.get_all_widgets\(child\)\)
        return widgets"""
        
        get_widgets_replacement = """    def get_all_widgets(self, parent):
        \"\"\"Recursively get all widgets in the application.\"\"\"
        widgets = []
        try:
            for child in parent.winfo_children():
                widgets.append(child)
                if hasattr(child, 'winfo_children'):
                    widgets.extend(self.get_all_widgets(child))
        except Exception as e:
            print(f"Error getting widgets for {parent}: {e}")
        return widgets"""
        
        # Replace the get_all_widgets method
        content = content.replace(get_widgets_pattern, get_widgets_replacement)
        
        # Save the fixed theme manager
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Successfully fixed theme manager!")
        return True
    
    except Exception as e:
        print(f"Error updating theme manager: {str(e)}")
        print(f"You can restore from the backup: {backup_path}")
        return False

if __name__ == "__main__":
    fix_rmr_calculation_final()
