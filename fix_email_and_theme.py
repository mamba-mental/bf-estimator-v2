#!/usr/bin/env python
"""
fix_email_and_theme.py - A utility script to add an email field
and fix theme application issues in enhanced_desktop_app.py
"""

import re
import shutil
import json
import os

def fix_email_and_theme():
    """
    Add an email field to the settings section
    and fix theme application in the enhanced_desktop_app.py file
    """
    file_path = 'enhanced_desktop_app.py'
    backup_path = f'{file_path}.email_theme.bak'
    
    # Create backup first
    print(f"Creating backup of {file_path} as {backup_path}")
    shutil.copy2(file_path, backup_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix 1: Add email field
        # Find the profile section in setup_settings_tab() where name is added
        name_field_pattern = r"""        # Name
        ctk\.CTkLabel\(profile_frame, text="Name:"\)\.grid\(row=1, column=0, padx=10, pady=5, sticky="w"\)
        self\.settings_name_entry = ctk\.CTkEntry\(profile_frame\)
        self\.settings_name_entry\.grid\(row=1, column=1, padx=10, pady=5, sticky="ew"\)

"""
        
        # Add email field right after name field
        email_field_replacement = """        # Name
        ctk.CTkLabel(profile_frame, text="Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.settings_name_entry = ctk.CTkEntry(profile_frame)
        self.settings_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Email
        ctk.CTkLabel(profile_frame, text="Email:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.settings_email_entry = ctk.CTkEntry(profile_frame)
        self.settings_email_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

"""

        # Replace name field with name+email fields
        content = content.replace(name_field_pattern, email_field_replacement)
        
        # Adjust the row numbers for subsequent profile fields (age and others)
        content = re.sub(r'row=2, column=0', 'row=3, column=0', content)
        content = re.sub(r'row=2, column=1', 'row=3, column=1', content)
        content = re.sub(r'row=3, column=0', 'row=4, column=0', content)
        content = re.sub(r'row=3, column=1', 'row=4, column=1', content)
        content = re.sub(r'row=4, column=0', 'row=5, column=0', content)
        content = re.sub(r'row=4, column=1', 'row=5, column=1', content)
        content = re.sub(r'row=5, column=0', 'row=6, column=0', content)
        content = re.sub(r'row=5, column=1', 'row=6, column=1', content)
        
        # Add email field to load_settings method
        load_settings_pattern = r"""        self\.settings_name_entry\.delete\(0, "end"\)
        self\.settings_name_entry\.insert\(0, user_data\.get\('name', ''\)\)

"""
        
        load_settings_replacement = """        self.settings_name_entry.delete(0, "end")
        self.settings_name_entry.insert(0, user_data.get('name', ''))

        # Load email
        if hasattr(self, 'settings_email_entry'):
            self.settings_email_entry.delete(0, "end")
            self.settings_email_entry.insert(0, user_data.get('email', ''))

"""
        
        content = content.replace(load_settings_pattern, load_settings_replacement)
        
        # Add email field to save_settings method
        save_settings_pattern = r"""            # Read values from fields
            name = self\.settings_name_entry\.get\(\)"""
        
        save_settings_replacement = """            # Read values from fields
            name = self.settings_name_entry.get()
            email = self.settings_email_entry.get() if hasattr(self, 'settings_email_entry') else ''"""
        
        content = content.replace(save_settings_pattern, save_settings_replacement)
        
        # Add email to the settings dictionary
        settings_dict_pattern = r"""            settings_to_update = \{
                'name': name,"""
        
        settings_dict_replacement = """            settings_to_update = {
                'name': name,
                'email': email,"""
        
        content = content.replace(settings_dict_pattern, settings_dict_replacement)
        
        # Fix 2: Theme Application
        # Modify apply_theme in ThemeManager class to ensure appropriate contrast and force-repaint
        # We'll do this in a separate file to not make this script too complex
        
        # Save the changes
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Successfully added email field!")
        
        # Now let's ensure the theme_manager.py file applies themes correctly
        fix_theme_manager()
        
        print(f"If the changes didn't work correctly, you can restore from the backup: {backup_path}")
        return True
    
    except Exception as e:
        print(f"Error updating file: {str(e)}")
        print(f"You can restore from the backup: {backup_path}")
        return False

def fix_theme_manager():
    """Fix theme application in the theme_manager.py file"""
    
    file_path = 'theme_manager.py'
    backup_path = f'{file_path}.bak'
    
    # Create backup first
    print(f"Creating backup of {file_path} as {backup_path}")
    shutil.copy2(file_path, backup_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find apply_theme method
        apply_theme_pattern = r"""    def apply_theme\(self, theme_name\):
        """
        
        # Looking for where it loads the theme data
        if "with open(theme_path, 'r') as file:" in content:
            # Insert debug prints and force widget updates
            # Find the section where theme is applied to widgets
            theme_application_pattern = r"""        # Apply theme to all widgets
        count = 0  # Initialize count
        for widget in self.get_all_widgets\(self.root\):
            # Apply theme to appropriate widget types
            try:
                self.apply_widget_theme\(widget, theme_data\)
                count \+= 1  # Increment count
            except Exception as e:
                print\(f"\[WARNING\] Error applying theme to widget: {e}"\)
"""
            
            theme_application_replacement = """        # Apply theme to all widgets
        count = 0  # Initialize count
        
        # Force a complete redraw of the application
        self.root.update_idletasks()
        
        for widget in self.get_all_widgets(self.root):
            # Apply theme to appropriate widget types
            try:
                # Apply with stronger styling to ensure changes take effect
                self.apply_widget_theme(widget, theme_data)
                
                # Force widget update
                if hasattr(widget, 'update'):
                    widget.update()
                count += 1  # Increment count
            except Exception as e:
                print(f"[WARNING] Error applying theme to widget: {e}")
                
        # Force another update after all widgets are themed
        self.root.update_idletasks()
"""
            
            content = content.replace(theme_application_pattern, theme_application_replacement)
            
            # Enhance apply_widget_theme for stronger styling
            apply_widget_pattern = r"""    def apply_widget_theme\(self, widget, theme_data\):
        """
            
            if apply_widget_pattern in content:
                # Find the closing of the method
                apply_widget_end_pattern = r"""            # Apply any other theme values based on widget type
            # ...

            # Apply any widget-specific custom configurations if needed
            # ...
"""
                
                apply_widget_end_replacement = """            # Apply any other theme values based on widget type
            # Ensure higher contrast for text elements
            if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton, ctk.CTkCheckBox, ctk.CTkRadioButton)):
                if 'text_color' in theme_data:
                    widget.configure(text_color=theme_data['text_color'])
            
            # Force button highlights to be more visible
            if isinstance(widget, ctk.CTkButton):
                if 'button_hover_color' in theme_data:
                    # Make hover color more distinct
                    widget.configure(hover_color=theme_data['button_hover_color'])
                    
            # Ensure entry and text fields have good contrast
            if isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
                if 'entry_text_color' in theme_data:
                    widget.configure(text_color=theme_data['entry_text_color'])
                if 'entry_background_color' in theme_data:
                    widget.configure(fg_color=theme_data['entry_background_color'])
                    
            # Update progress bars to be more visible
            if isinstance(widget, ctk.CTkProgressBar):
                if 'progressbar_progress_color' in theme_data:
                    widget.configure(progress_color=theme_data['progressbar_progress_color'])

            # Apply any widget-specific custom configurations if needed
            # ...
"""
                
                content = content.replace(apply_widget_end_pattern, apply_widget_end_replacement)
        
        # Save the changes
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Successfully fixed theme manager!")
        
        # Now let's enhance all theme files with better contrast settings
        enhance_theme_files()
        
        return True
    
    except Exception as e:
        print(f"Error updating theme manager: {str(e)}")
        print(f"You can restore from the backup: {backup_path}")
        return False

def enhance_theme_files():
    """Enhance all theme files with better contrast settings"""
    
    theme_files = [
        'enhanced_blue.json',
        'midnight_oled_theme.json',
        'forest_theme.json',
        'lavender_theme.json',
        'sunset_theme.json',
        'batman_theme.json',
        'ocean_theme.json'
    ]
    
    for theme_file in theme_files:
        if not os.path.exists(theme_file):
            print(f"Theme file {theme_file} not found, skipping")
            continue
            
        try:
            # Create backup
            backup_path = f'{theme_file}.bak'
            print(f"Creating backup of {theme_file} as {backup_path}")
            shutil.copy2(theme_file, backup_path)
            
            # Load theme data
            with open(theme_file, 'r') as f:
                theme_data = json.load(f)
            
            # Enhance contrast
            if 'text_color' in theme_data:
                # Make text more vivid/contrasting
                if theme_data.get('appearance_mode', '').lower() == 'dark':
                    theme_data['text_color'] = "#FFFFFF"  # Bright white for dark mode
                else:
                    theme_data['text_color'] = "#000000"  # Black for light mode
            
            # Add critical missing properties if they don't exist
            if 'button_hover_color' not in theme_data:
                # Use a distinct hover color based on theme primary
                theme_data['button_hover_color'] = "#3B8ED0"  # Default blue hover
                
            if 'entry_text_color' not in theme_data:
                theme_data['entry_text_color'] = theme_data.get('text_color', "#000000")
                
            if 'entry_background_color' not in theme_data:
                theme_data['entry_background_color'] = "#EEEEEE"  # Light gray background
                
            if 'progressbar_progress_color' not in theme_data:
                theme_data['progressbar_progress_color'] = "#1F6AA5"  # Blue progress
            
            # Save enhanced theme
            with open(theme_file, 'w') as f:
                json.dump(theme_data, f, indent=4)
                
            print(f"Enhanced theme file: {theme_file}")
            
        except Exception as e:
            print(f"Error enhancing theme file {theme_file}: {str(e)}")
            print(f"You can restore from the backup: {backup_path}")

if __name__ == "__main__":
    fix_email_and_theme()
